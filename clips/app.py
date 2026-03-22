import json
import os
import re
import secrets
import smtplib
import subprocess
import sys
import threading
import time
import uuid
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import db as clips_db

app = FastAPI(title="TKK Clips Dashboard")

SETTINGS_PATH = Path("/opt/tkk/clips/settings.json")
_settings_defaults = {
    "studio_model": "opus",
    "studio_budget": "5.00",
    "meta_model": "sonnet",
    "meta_budget": "0.50",
    # Video Rendering
    "rendering_engine": "remotion",
    "render_crf": "23",
    "render_preset": "fast",
    "max_concurrent_renders": "1",
    # TTS Audio
    "fish_bitrate": "192",
    "fish_voice_id": "dc74574cfe664e93bd4179fe28542524",
    "fish_voice_name": "Him-phm",
    # Shorts
    "short_max_duration": "30",
    "short_fade_duration": "1.5",
    # AV Sync
    "silence_threshold_db": "-30",
    "silence_min_duration": "0.3",
}

def get_settings() -> dict:
    """Read settings.json, falling back to defaults for missing keys."""
    settings = dict(_settings_defaults)
    if SETTINGS_PATH.exists():
        try:
            settings.update(json.loads(SETTINGS_PATH.read_text()))
        except Exception:
            pass
    return settings

VIDGEN_DIR = Path("/opt/tkk/vidgen")
THUMBS_DIR = Path("/opt/tkk/clips/thumbs")
PREVIEWS_DIR = Path("/opt/tkk/vidgen/previews")
TEMPLATES_DIR = Path("/opt/tkk/clips/templates")
REMOTION_MANIFESTS_DIR = VIDGEN_DIR / "remotion" / "src" / "manifests"


def _engine_from_filename(filename: str) -> str:
    """Detect framework from filename: .json → remotion, _manim.py/.py → manim."""
    if filename.endswith(".json"):
        return "remotion"
    return "manim"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/videos", StaticFiles(directory=str(VIDGEN_DIR)), name="videos")
app.mount("/thumbs", StaticFiles(directory=str(THUMBS_DIR)), name="thumbs")
app.mount("/previews", StaticFiles(directory=str(PREVIEWS_DIR)), name="previews")
app.mount("/remotion-player", StaticFiles(directory="static/remotion-player", html=True), name="remotion-player")
app.mount("/remotion-assets", StaticFiles(directory=str(VIDGEN_DIR / "remotion" / "public")), name="remotion-assets")

# In-memory render job tracking
render_jobs: dict = {}
_active_renders: dict = {}

# In-memory pipeline job tracking
pipeline_jobs: dict = {}  # pipeline_id -> {status, step, error, filename, ...}
def _max_concurrent_renders() -> int:
    return max(1, min(4, int(get_settings().get("max_concurrent_renders", "1"))))

# --- Auth config ---
APP_URL = os.environ.get("CLIPS_APP_URL", "https://clips.applesauce.chat")
ADMIN_EMAILS = set(e.strip() for e in os.environ.get(
    "ADMIN_EMAILS", ""
).split(",") if e.strip())
SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
SMTP_FROM = os.environ.get("SMTP_FROM", "")
SESSION_COOKIE = "clips_session"
OPEN_PATHS = {"/login", "/auth/verify", "/api/auth/magic-link", "/logout", "/static",
              "/videos", "/thumbs", "/previews", "/about", "/remotion-player", "/remotion-assets"}


@app.on_event("startup")
def startup():
    clips_db.init_db()
    # Clean up orphaned sessions: user sent a message but service died before assistant responded
    with clips_db.db_session() as conn:
        orphaned = conn.execute("""
            SELECT DISTINCT m.session_id FROM studio_messages m
            WHERE m.role = 'user'
            AND NOT EXISTS (
                SELECT 1 FROM studio_messages m2
                WHERE m2.session_id = m.session_id AND m2.role = 'assistant'
                AND m2.created_at > m.created_at
            )
            AND m.created_at = (
                SELECT MAX(m3.created_at) FROM studio_messages m3 WHERE m3.session_id = m.session_id
            )
        """).fetchall()
        for row in orphaned:
            sid = row[0]
            conn.execute(
                "INSERT INTO studio_messages (session_id, role, content) VALUES (?, 'assistant', ?)",
                (sid, "[Session interrupted — the server restarted before a response was generated. Send another message to continue.]"),
            )


# --- Auth helpers ---

def _send_smtp(to_email: str, subject: str, html: str) -> bool:
    if not SMTP_HOST or not SMTP_USER:
        return False
    try:
        msg = MIMEText(html, "html")
        msg["From"] = SMTP_FROM
        msg["To"] = to_email
        msg["Subject"] = subject
        s = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
        s.ehlo(); s.starttls(); s.ehlo()
        s.login(SMTP_USER, SMTP_PASS)
        s.sendmail(SMTP_FROM, [to_email], msg.as_string())
        s.quit()
        return True
    except Exception:
        return False


def _get_session_user(request: Request) -> dict | None:
    token = request.cookies.get(SESSION_COOKIE, "")
    if not token:
        return None
    with clips_db.db_session() as conn:
        row = conn.execute(
            """SELECT u.id, u.email FROM sessions s
               JOIN users u ON s.user_id = u.id
               WHERE s.token = ? AND s.expires_at > ?""",
            (token, datetime.utcnow().isoformat())
        ).fetchone()
        if row:
            return {"id": row["id"], "email": row["email"]}
    return None


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path
    if any(path.startswith(p) for p in OPEN_PATHS):
        return await call_next(request)
    if _get_session_user(request):
        return await call_next(request)
    if path.startswith("/api/"):
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    return RedirectResponse("/login", status_code=302)


# --- Auth routes ---

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if _get_session_user(request):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/api/auth/magic-link")
async def send_magic_link(request: Request):
    body = await request.json()
    email = body.get("email", "").strip().lower()
    if not email or not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        raise HTTPException(400, "Valid email required")
    if email not in ADMIN_EMAILS:
        raise HTTPException(403, "Access restricted")

    clips_db.get_or_create_user(email)
    token = secrets.token_urlsafe(32)
    expires = (datetime.utcnow() + timedelta(minutes=15)).isoformat()
    with clips_db.db_session() as conn:
        conn.execute(
            "INSERT INTO magic_tokens (email, token, expires_at) VALUES (?, ?, ?)",
            (email, token, expires)
        )

    link = f"{APP_URL}/auth/verify?token={token}"
    html = f"""
    <div style="font-family:Inter,sans-serif;max-width:480px;margin:0 auto;padding:32px;">
        <h1 style="font-family:serif;color:#e8834a;">clips</h1>
        <p>Click below to sign in:</p>
        <a href="{link}" style="display:inline-block;padding:12px 24px;background:#e8834a;color:#fff;
           text-decoration:none;border-radius:6px;font-weight:600;margin:16px 0;">Sign In</a>
        <p style="color:#999;font-size:0.85rem;">This link expires in 15 minutes.</p>
    </div>
    """
    sent = _send_smtp(email, "clips — Sign In", html)
    if not sent:
        raise HTTPException(500, "Failed to send email. Check SMTP config.")
    return {"status": "sent"}


@app.get("/auth/verify")
async def verify_magic_link(request: Request, token: str = ""):
    if not token:
        raise HTTPException(400, "Token required")
    with clips_db.db_session() as conn:
        row = conn.execute(
            "SELECT * FROM magic_tokens WHERE token = ? AND used = 0 AND expires_at > ?",
            (token, datetime.utcnow().isoformat())
        ).fetchone()
        if not row:
            return RedirectResponse("/login?error=expired", status_code=302)
        conn.execute("UPDATE magic_tokens SET used = 1 WHERE id = ?", (row["id"],))
        user = clips_db.get_or_create_user(row["email"])
        session_token = secrets.token_urlsafe(32)
        expires = (datetime.utcnow() + timedelta(days=90)).isoformat()
        conn.execute(
            "INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)",
            (user["id"], session_token, expires)
        )
    resp = RedirectResponse("/", status_code=302)
    resp.set_cookie(SESSION_COOKIE, session_token,
                    httponly=True, secure=False, samesite="lax",
                    max_age=90 * 24 * 3600, path="/")
    return resp


@app.get("/logout")
async def logout(request: Request):
    token = request.cookies.get(SESSION_COOKIE, "")
    if token:
        with clips_db.db_session() as conn:
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
    resp = RedirectResponse("/login", status_code=302)
    resp.delete_cookie(SESSION_COOKIE)
    return resp


# --- Helpers ---

def ffprobe_meta(filepath: Path) -> dict:
    """Get video metadata via ffprobe."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(filepath)],
            capture_output=True, text=True, timeout=15,
        )
        data = json.loads(result.stdout)
        fmt = data.get("format", {})
        video_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
        return {
            "duration": float(fmt.get("duration", 0)),
            "size": int(fmt.get("size", 0)),
            "bitrate": int(fmt.get("bit_rate", 0)),
            "codec": video_stream.get("codec_name", "unknown"),
            "width": video_stream.get("width", 0),
            "height": video_stream.get("height", 0),
            "fps": video_stream.get("r_frame_rate", "0/1"),
        }
    except Exception as e:
        return {"error": str(e)}


def format_duration(seconds: float) -> str:
    """Format seconds as M:SS."""
    m, s = divmod(int(seconds), 60)
    return f"{m}:{s:02d}"


def format_size(size_bytes: int) -> str:
    """Format bytes as human-readable."""
    mb = size_bytes / (1024 * 1024)
    if mb >= 1000:
        return f"{mb / 1024:.1f} GB"
    return f"{mb:.1f} MB"


# Duration cache: {filepath_mtime: duration_seconds}
_duration_cache: dict = {}


def _get_cached_duration(filepath: Path, mtime: float) -> float | None:
    """Get video duration, cached by file mtime."""
    cache_key = f"{filepath.name}:{mtime}"
    if cache_key in _duration_cache:
        return _duration_cache[cache_key]
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(filepath)],
            capture_output=True, text=True, timeout=5,
        )
        dur = float(result.stdout.strip())
        _duration_cache[cache_key] = dur
        return dur
    except Exception:
        return None


def _is_final_video(filename: str) -> bool:
    """Check if a video is a final/shipping version (not a test iteration)."""
    import re
    stem = filename.replace('.mp4', '')
    # Final versions: explicitly marked _final, or latest unique topic without version suffix
    if '_final' in stem:
        return True
    # Exclude: demo, versioned iterations (v3-v16), discord copies, hq/compressed variants
    if re.search(r'_(v\d+|discord|hq|compressed|fixed)$', stem):
        return False
    if stem == 'demo_output':
        return False
    return False  # Default: hide unless marked _final


def get_video_list(show_all: bool = False) -> list[dict]:
    """List .mp4 files with metadata for dashboard template."""
    import re

    # Load video metadata for custom titles and posted status
    meta_json = VIDGEN_DIR / "video_metadata.json"
    video_meta = {}
    if meta_json.exists():
        try:
            video_meta = json.loads(meta_json.read_text())
        except Exception:
            pass

    videos = []
    for f in sorted(VIDGEN_DIR.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True):
        stat = f.stat()
        thumb_path = THUMBS_DIR / f"{f.stem}.jpg"
        has_thumb = thumb_path.exists() and thumb_path.stat().st_mtime >= stat.st_mtime
        dur = _get_cached_duration(f, stat.st_mtime)
        is_final = _is_final_video(f.name)

        # Title: prefer custom title from video_metadata.json, fall back to filename
        file_meta = video_meta.get(f.name, {})
        if file_meta.get("title"):
            title = file_meta["title"]
        else:
            title = f.stem.replace("_", " ").title()
            title = re.sub(r'\s*(V\d+|Final|Render|Output|Manim|S\d+.*)$', '', title, flags=re.IGNORECASE).strip()

        posted = file_meta.get("posted", False)

        # Check for corresponding short
        short_filename = None
        short_duration = None
        if is_final and f.stem.endswith("_final"):
            short_stem = f.stem.replace("_final", "_short")
            short_path = VIDGEN_DIR / f"{short_stem}.mp4"
            if short_path.exists():
                short_filename = short_path.name
                short_dur = _get_cached_duration(short_path, short_path.stat().st_mtime)
                short_duration = format_duration(short_dur) if short_dur else None

        # Check for Remotion manifest and detect format
        clean_stem = re.sub(r'_(final|short|v\d+|s\d+)$', '', f.stem)
        manifest_path = REMOTION_MANIFESTS_DIR / f"{clean_stem}.json"
        has_remotion = manifest_path.exists()
        has_manim = (VIDGEN_DIR / f"{clean_stem}_manim.py").exists()
        engine = "remotion" if has_remotion else ("manim" if has_manim else "unknown")

        # Detect word-triggered vs legacy format
        fmt = None
        if has_remotion:
            try:
                mdata = json.loads(manifest_path.read_text())
                fmt = "word-triggered" if (mdata.get("scenes") and "scene_anchor" in mdata["scenes"][0]) else "legacy"
            except Exception:
                fmt = "legacy"

        # Audio duration
        audio_path = VIDGEN_DIR / f"tts_{clean_stem}.mp3"
        audio_dur = None
        if audio_path.exists():
            audio_dur = _get_cached_duration(audio_path, audio_path.stat().st_mtime)

        # Render timestamp
        mtime = datetime.fromtimestamp(stat.st_mtime)
        rendered_ago = _relative_time(mtime)

        is_new = (datetime.now() - mtime).total_seconds() < 48 * 3600
        description = file_meta.get("description", "")

        videos.append({
            "filename": f.name,
            "title": title,
            "description": description,
            "thumbnail": f"{f.stem}.jpg?v={int(stat.st_mtime)}" if has_thumb else None,
            "duration": format_duration(dur) if dur else None,
            "audio_duration": format_duration(audio_dur) if audio_dur else None,
            "size": format_size(stat.st_size),
            "date": mtime.strftime("%b %d, %H:%M"),
            "date_short": mtime.strftime("%b %d"),
            "rendered_ago": rendered_ago,
            "sort_key": mtime.isoformat(),
            "size_bytes": stat.st_size,
            "modified": mtime.isoformat(),
            "is_final": is_final,
            "is_new": is_new,
            "posted": posted,
            "short_filename": short_filename,
            "short_duration": short_duration,
            "has_remotion": has_remotion,
            "has_manim": has_manim,
            "engine": engine,
            "format": fmt,
        })
    if not show_all:
        videos = [v for v in videos if v["is_final"]]
    return videos


def _relative_time(dt: datetime) -> str:
    """Return a human-readable relative time string."""
    now = datetime.now()
    diff = now - dt
    seconds = int(diff.total_seconds())
    if seconds < 60:
        return "just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    if days < 7:
        return f"{days}d ago"
    return dt.strftime("%b %d")


def extract_thumbnail(filepath: Path) -> Path:
    """Extract a thumbnail frame, cached in thumbs dir. Re-extracts if video is newer."""
    thumb_path = THUMBS_DIR / f"{filepath.stem}.jpg"
    if thumb_path.exists() and thumb_path.stat().st_mtime >= filepath.stat().st_mtime:
        return thumb_path
    THUMBS_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-ss", "2", "-i", str(filepath), "-frames:v", "1", "-q:v", "2", str(thumb_path)],
        capture_output=True, timeout=15,
    )
    return thumb_path


def list_screenplays() -> list[str]:
    """List all .py screenplay files in vidgen, newest first."""
    files = list(VIDGEN_DIR.glob("*.py"))
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return [f.name for f in files]


# --- Page Routes ---

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, all: bool = False):
    videos = get_video_list(show_all=all)
    total = len(list(VIDGEN_DIR.glob("*.mp4")))
    # Remotion migration stats
    total_screenplays = len(list(VIDGEN_DIR.glob("*_manim.py")))
    remotion_dir = REMOTION_MANIFESTS_DIR
    remotion_count = len(list(remotion_dir.glob("*.json"))) if remotion_dir.exists() else 0
    return templates.TemplateResponse("dashboard.html", {
        "request": request, "videos": videos, "show_all": all, "total_count": total,
        "remotion_count": remotion_count, "total_screenplays": total_screenplays,
    })


def _video_meta_from_screenplay(stem: str) -> dict:
    """Try to extract title/description from metadata JSON or screenplay file."""
    import re
    # Method 0: Check video_metadata.json first (authoritative source)
    meta_json = VIDGEN_DIR / "video_metadata.json"
    if meta_json.exists():
        try:
            import json
            all_meta = json.loads(meta_json.read_text())
            # Try exact filename match
            for suffix in ["_final.mp4", ".mp4"]:
                key = stem + suffix
                if key in all_meta:
                    m = all_meta[key]
                    return {
                        "title": m.get("title", ""),
                        "description": m.get("description", ""),
                        "tags": m.get("tags", ""),
                        "screenplay": "video_metadata.json",
                    }
        except Exception:
            pass
    # Strip common suffixes progressively: death_bureau_s1_final -> death_bureau_s1 -> death_bureau
    base = re.sub(r'_(v\d+|final|render|output|compressed|hq|discord|fixed)$', '', stem)
    base2 = re.sub(r'_(s\d+|v\d+|history|walking_statues).*$', '', stem)
    # Build candidate list ordered by specificity
    candidates = [
        f"{stem}.py", f"{stem}_manim.py",
        f"{base}.py", f"{base}_manim.py",
        f"{base2}.py", f"{base2}_manim.py",
    ]
    # Also glob for any .py containing the base topic name
    topic = base2.split('_')[0] if '_' in base2 else base2
    for py in VIDGEN_DIR.glob(f"{topic}*.py"):
        if py.name not in candidates:
            candidates.append(py.name)
    for name in candidates:
        sp = VIDGEN_DIR / name
        if not sp.exists():
            continue
        try:
            content = sp.read_text()
            desc = ""

            # Method 1: TTS_SCRIPT variable
            match = re.search(r'TTS_SCRIPT\s*=\s*"""(.*?)"""', content, re.DOTALL)
            if match:
                lines = [l.strip() for l in match.group(1).strip().split('\n') if l.strip()]
                desc = ' '.join(lines[:3])

            # Method 2: Extract narration from VTT-style comments (timestamps with text)
            if not desc:
                narration_lines = re.findall(r'^\s+[\d.]+\s+\([\d.]+\)\s+(.+)$', content, re.MULTILINE)
                if narration_lines:
                    desc = ' '.join(narration_lines[:4])

            # Method 3: Module docstring
            if not desc:
                match = re.search(r'^"""(.*?)"""', content, re.DOTALL)
                if match:
                    first_line = match.group(1).strip().split('\n')[0].strip()
                    if len(first_line) > 10:
                        desc = first_line

            if desc:
                desc = _humanize_description(desc)
                if len(desc) > 250:
                    desc = desc[:247] + '...'
                return {"description": desc, "screenplay": name}
        except Exception:
            pass
    return {}


def _humanize_description(text: str) -> str:
    """Strip common AI writing patterns from auto-extracted descriptions."""
    import re
    # Replace em-dashes with commas or periods depending on context
    text = re.sub(r'\s*—\s*', ', ', text)
    # Remove doubled-up commas from the replacement
    text = re.sub(r',\s*,', ',', text)
    # Strip "Let me explain" / "Here's the thing" / "Here's what happened" openers
    text = re.sub(r'^(Let me explain[.:]?\s*|Here\'s the thing[.:]?\s*|Here\'s what happened[.:]?\s*)', '', text, flags=re.IGNORECASE)
    # Collapse multiple spaces
    text = re.sub(r'  +', ' ', text)
    return text.strip()


def _generate_tags(stem: str) -> str:
    """Generate relevant hashtags from video filename or metadata."""
    import re, json
    # Check metadata JSON first
    meta_json = VIDGEN_DIR / "video_metadata.json"
    if meta_json.exists():
        try:
            all_meta = json.loads(meta_json.read_text())
            for suffix in ["_final.mp4", ".mp4"]:
                key = stem + suffix
                if key in all_meta and all_meta[key].get("tags"):
                    return all_meta[key]["tags"]
        except Exception:
            pass
    base = re.sub(r'_(v\d+|final|render|output|s\d+.*)$', '', stem)
    # Build topic-specific tag from individual words (e.g. "bronze_age" -> "#bronzeage")
    topic_tag = f"#{base.replace('_', '')}"
    # Also add individual word tags if multi-word (e.g. "#bronze" "#age" aren't useful,
    # but topic-specific compound is)
    tags = [topic_tag, "#historytok", "#darkhistory", "#learnontiktok", "#storytime"]
    return ' '.join(tags)


@app.get("/video/{filename}", response_class=HTMLResponse)
async def video_detail(request: Request, filename: str):
    filepath = VIDGEN_DIR / filename
    if not filepath.exists() or not filename.endswith(".mp4"):
        raise HTTPException(404, "Video not found")
    meta = ffprobe_meta(filepath)
    stat = filepath.stat()
    dur = meta.get("duration", 0)
    stem = filepath.stem
    sp_meta = _video_meta_from_screenplay(stem)
    # Use metadata title if available, fall back to filename
    title = sp_meta.get("title", "")
    if not title:
        title = stem.replace("_", " ").replace("  ", " ").title()
        title = re.sub(r'\s*(V\d+|Final|Render|Output|S\d+.*)$', '', title, flags=re.IGNORECASE).strip()
    # Check for short version
    short_filename = None
    short_duration = None
    if stem.endswith("_final"):
        short_stem = stem.replace("_final", "_short")
        short_path = VIDGEN_DIR / f"{short_stem}.mp4"
        if short_path.exists():
            short_filename = short_path.name
            short_meta = ffprobe_meta(short_path)
            short_dur = short_meta.get("duration", 0)
            short_duration = format_duration(short_dur) if short_dur else None

    # Engine source detection
    clean_stem = re.sub(r'_(final|short|v\d+|s\d+)$', '', stem)
    has_remotion = (REMOTION_MANIFESTS_DIR / f"{clean_stem}.json").exists()
    has_manim = (VIDGEN_DIR / f"{clean_stem}_manim.py").exists()
    engine = "remotion" if has_remotion else ("manim" if has_manim else "unknown")

    # Format detection (word-triggered vs legacy)
    fmt = None
    if has_remotion:
        try:
            mdata = json.loads((REMOTION_MANIFESTS_DIR / f"{clean_stem}.json").read_text())
            fmt = "word-triggered" if (mdata.get("scenes") and "scene_anchor" in mdata["scenes"][0]) else "legacy"
        except Exception:
            fmt = "legacy"

    # Posted status from video_metadata.json
    meta_json = VIDGEN_DIR / "video_metadata.json"
    file_meta = {}
    if meta_json.exists():
        try:
            file_meta = json.loads(meta_json.read_text()).get(filename, {})
        except Exception:
            pass

    mtime = datetime.fromtimestamp(stat.st_mtime)

    video = {
        "filename": filename,
        "title": title,
        "description": sp_meta.get("description", ""),
        "tags": _generate_tags(stem),
        "duration": format_duration(dur) if dur else None,
        "size": format_size(stat.st_size),
        "date": mtime.strftime("%b %d"),
        "rendered_ago": _relative_time(mtime),
        "posted": file_meta.get("posted", False),
        "format": fmt,
        "meta": meta,
        "short_filename": short_filename,
        "short_duration": short_duration,
        "has_remotion": has_remotion,
        "has_manim": has_manim,
        "engine": engine,
        "clean_stem": clean_stem,
    }
    return templates.TemplateResponse("video.html", {
        "request": request, "video": video,
    })


def _parse_screenplay_version(stem):
    """'gobekli_tepe_v3' → ('gobekli_tepe', 'v3'), 'death_bureau_s2' → ('death_bureau', 's2')"""
    m = re.match(r'^(.+?)_(v\d+|s\d+|svg|visual|hybrid|geo)$', stem)
    if m:
        return m.group(1), m.group(2)
    return stem, None


def _get_grouped_screenplays() -> list[dict]:
    """Return screenplay list with status groups and version collapsing.
    Includes both Manim (_manim.py) and Remotion (.json manifest) screenplays.
    """
    # Load posted status from video_metadata.json
    meta_json = VIDGEN_DIR / "video_metadata.json"
    all_meta = {}
    if meta_json.exists():
        try:
            all_meta = json.loads(meta_json.read_text())
        except Exception:
            pass

    seen_stems = set()
    screenplays = []

    # 1. Remotion manifests (primary engine)
    if REMOTION_MANIFESTS_DIR.exists():
        for f in sorted(REMOTION_MANIFESTS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            stem = f.stem
            seen_stems.add(stem)
            base_stem, version = _parse_screenplay_version(stem)
            has_tts = (VIDGEN_DIR / f"tts_{stem}.mp3").exists()
            has_preview = (PREVIEWS_DIR / f"{stem}_scene_1.png").exists()
            has_final = (VIDGEN_DIR / f"{stem}_final.mp4").exists()
            has_short = (VIDGEN_DIR / f"{stem}_short.mp4").exists()

            posted = False
            video_key = f"{stem}_final.mp4"
            if video_key in all_meta:
                posted = bool(all_meta[video_key].get("posted", False))

            if has_final:
                group = "complete"
            elif has_tts or has_preview:
                group = "progress"
            else:
                group = "draft"

            screenplays.append({
                "filename": f.name,
                "name": stem.replace("_", " ").title(),
                "stem": stem,
                "base_stem": base_stem,
                "version": version,
                "group": group,
                "engine": "remotion",
                "has_tts": has_tts,
                "has_preview": has_preview,
                "has_final": has_final,
                "has_short": has_short,
                "posted": posted,
                "has_remotion": True,
            })

    # 2. Manim screenplays (only those without a corresponding Remotion manifest)
    for f in sorted(VIDGEN_DIR.glob("*_manim.py"), key=lambda p: p.stat().st_mtime, reverse=True):
        stem = f.stem.replace("_manim", "")
        if stem in seen_stems:
            continue  # Already listed via Remotion entry
        seen_stems.add(stem)
        base_stem, version = _parse_screenplay_version(stem)
        has_tts = (VIDGEN_DIR / f"tts_{stem}.mp3").exists()
        has_preview = (PREVIEWS_DIR / f"{stem}_scene_1.png").exists()
        has_final = (VIDGEN_DIR / f"{stem}_final.mp4").exists()
        has_short = (VIDGEN_DIR / f"{stem}_short.mp4").exists()

        posted = False
        video_key = f"{stem}_final.mp4"
        if video_key in all_meta:
            posted = bool(all_meta[video_key].get("posted", False))

        if has_final:
            group = "complete"
        elif has_tts or has_preview:
            group = "progress"
        else:
            group = "draft"

        screenplays.append({
            "filename": f.name,
            "name": stem.replace("_", " ").title(),
            "stem": stem,
            "base_stem": base_stem,
            "version": version,
            "group": group,
            "engine": "manim",
            "has_tts": has_tts,
            "has_preview": has_preview,
            "has_final": has_final,
            "has_short": has_short,
            "posted": posted,
            "has_remotion": False,
        })

    return screenplays


@app.get("/workbench", response_class=HTMLResponse)
async def workbench(request: Request):
    return templates.TemplateResponse("workbench.html", {"request": request})


@app.get("/editor", response_class=HTMLResponse)
async def editor(request: Request):
    # Redirect to workbench, preserving ?file= param
    file_param = request.query_params.get("file", "")
    url = "/workbench" + (f"?file={file_param}" if file_param else "")
    return RedirectResponse(url, status_code=302)


@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


def _about_stats():
    """Shared stats dict for all about pages."""
    return {
        "video_count": len(list(VIDGEN_DIR.glob("*_final.mp4"))),
        "screenplay_count": len(list(VIDGEN_DIR.glob("*_manim.py"))),
        "remotion_count": len(list(REMOTION_MANIFESTS_DIR.glob("*.json")))
            if REMOTION_MANIFESTS_DIR.exists() else 0,
    }


@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, **_about_stats()})


@app.get("/about/engines", response_class=HTMLResponse)
async def about_engines(request: Request):
    return templates.TemplateResponse("about_engines.html", {"request": request, **_about_stats()})


@app.get("/about/engines/manim", response_class=HTMLResponse)
async def about_engines_manim(request: Request):
    return templates.TemplateResponse("about_engines_manim.html", {"request": request, **_about_stats()})


@app.get("/about/engines/remotion", response_class=HTMLResponse)
async def about_engines_remotion(request: Request):
    return templates.TemplateResponse("about_engines_remotion.html", {"request": request, **_about_stats()})


@app.get("/about/pipeline", response_class=HTMLResponse)
async def about_pipeline(request: Request):
    return templates.TemplateResponse("about_pipeline.html", {"request": request, **_about_stats()})


@app.get("/about/values", response_class=HTMLResponse)
async def about_values(request: Request):
    return templates.TemplateResponse("about_values.html", {"request": request, **_about_stats()})


@app.get("/about/roadmap", response_class=HTMLResponse)
async def about_roadmap(request: Request):
    return templates.TemplateResponse("about_roadmap.html", {"request": request, **_about_stats()})


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "settings": get_settings(),
    })


@app.get("/api/settings")
async def api_get_settings():
    return get_settings()


@app.put("/api/settings")
async def api_save_settings(request: Request):
    body = await request.json()
    current = get_settings()
    # Only allow known keys
    for key in _settings_defaults:
        if key in body:
            current[key] = body[key]
    tmp = SETTINGS_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(current, indent=2))
    tmp.rename(SETTINGS_PATH)
    return {"saved": True, "settings": current}


@app.get("/writer", response_class=HTMLResponse)
async def writer_page(request: Request):
    return RedirectResponse("/workbench", status_code=302)


# --- API Routes ---

@app.get("/api/videos")
async def api_videos():
    return get_video_list()


@app.get("/api/video/{filename}/meta")
async def api_video_meta(filename: str):
    filepath = VIDGEN_DIR / filename
    if not filepath.exists():
        raise HTTPException(404, "Video not found")
    return ffprobe_meta(filepath)


@app.delete("/api/video/{filename}")
async def api_video_delete(filename: str):
    """Delete a rendered final MP4 so it can be re-rendered."""
    if not filename.endswith("_final.mp4"):
        raise HTTPException(400, "Can only delete *_final.mp4 files")
    filepath = VIDGEN_DIR / filename
    if not filepath.exists():
        raise HTTPException(404, "Video not found")
    filepath.unlink()
    # Also remove the short if it exists
    short = VIDGEN_DIR / filename.replace("_final.mp4", "_short.mp4")
    short.unlink(missing_ok=True)
    return {"ok": True, "deleted": filename}


@app.delete("/api/audio/{filename}")
async def api_audio_delete(filename: str):
    """Delete a TTS MP3 so it can be regenerated."""
    if not filename.endswith(".mp3") or not filename.startswith("tts_"):
        raise HTTPException(400, "Can only delete tts_*.mp3 files")
    filepath = VIDGEN_DIR / filename
    if not filepath.exists():
        raise HTTPException(404, "Audio not found")
    filepath.unlink()
    # Also remove related sidecar files (timings, word timing)
    stem = filename.replace("tts_", "").replace(".mp3", "")
    for sidecar in [
        VIDGEN_DIR / f"tts_{stem}_timings.json",
        VIDGEN_DIR / f"tts_{stem}.mp3.json",
    ]:
        sidecar.unlink(missing_ok=True)
    return {"ok": True, "deleted": filename}


@app.put("/api/video/{filename}/metadata")
async def api_video_metadata_save(filename: str, request: Request):
    """Save title/description/tags to video_metadata.json."""
    filepath = VIDGEN_DIR / filename
    if not filepath.exists() or not filename.endswith(".mp4"):
        raise HTTPException(404, "Video not found")
    body = await request.json()
    meta_json = VIDGEN_DIR / "video_metadata.json"
    all_meta = {}
    if meta_json.exists():
        try:
            all_meta = json.loads(meta_json.read_text())
        except Exception:
            pass
    all_meta[filename] = {
        "title": body.get("title", ""),
        "description": body.get("description", ""),
        "tags": body.get("tags", ""),
    }
    tmp = meta_json.with_suffix(".tmp")
    tmp.write_text(json.dumps(all_meta, indent=2))
    tmp.rename(meta_json)
    return {"saved": True, "filename": filename}


_meta_gen_lock = threading.Lock()
_meta_gen_state: dict = {}  # filename -> {"status": "running"|"done"|"error", "result": dict|None}

def _run_meta_gen(filename: str, stem: str):
    """Background thread: ask Claude to generate title/description/tags from screenplay."""
    try:
        # Find screenplay
        sp = None
        for candidate in [f"{stem}_manim.py", f"{stem}.py"]:
            if (VIDGEN_DIR / candidate).exists():
                sp = VIDGEN_DIR / candidate
                break
        if not sp:
            with _meta_gen_lock:
                _meta_gen_state[filename] = {"status": "error", "result": {"error": "No screenplay found"}}
            return

        # Read existing metadata for examples
        meta_json = VIDGEN_DIR / "video_metadata.json"
        examples = ""
        if meta_json.exists():
            all_meta = json.loads(meta_json.read_text())
            # Grab 2 examples
            sample = [(k, v) for k, v in list(all_meta.items())[:2] if v.get("description")]
            for k, v in sample:
                examples += f'\n"{k}": title={v.get("title","")!r}, tags={v.get("tags","")!r}\n'

        tts_script = ""
        content = sp.read_text()
        m = re.search(r'TTS_SCRIPT\s*=\s*"""(.*?)"""', content, re.DOTALL)
        if m:
            tts_script = m.group(1).strip()

        prompt = f"""Generate TikTok metadata for this video. The screenplay file is {sp.name}.

TTS narration script:
{tts_script}

Write a JSON object with exactly these keys: "title", "description", "tags"

Rules:
- title: Short, punchy, under 60 chars. Hook the viewer. No em-dashes.
- description: 3-4 short paragraphs telling the story from the narration. Written like a human, not AI. No em-dashes, no "Here's the thing", no "Let me explain". Use plain commas and periods. Finish the thought, don't trail off. End with the hashtags on their own line.
- tags: 5-6 popular TikTok hashtags as a space-separated string. First tag should be topic-specific (e.g. #bronzeage). Always include #historytok #learnontiktok #storytime. Pick 1-2 more that are popular and relevant.

Examples of good entries:{examples}

Return ONLY the JSON object. No markdown fences, no explanation."""

        s = get_settings()
        cmd = [
            "/usr/bin/claude", "-p", "--output-format", "text",
            "--model", s["meta_model"],
            "--max-budget-usd", s["meta_budget"],
        ]
        output = ""
        proc = subprocess.run(
            cmd, input=prompt, capture_output=True, text=True,
            timeout=60, cwd=str(VIDGEN_DIR),
        )

        output = proc.stdout.strip()
        # Strip markdown fences if present
        if output.startswith("```"):
            output = re.sub(r'^```\w*\n?', '', output)
            output = re.sub(r'\n?```$', '', output)

        result = json.loads(output)

        # Save to video_metadata.json
        all_meta = {}
        if meta_json.exists():
            try:
                all_meta = json.loads(meta_json.read_text())
            except Exception:
                pass
        all_meta[filename] = {
            "title": result.get("title", ""),
            "description": result.get("description", ""),
            "tags": result.get("tags", ""),
        }
        tmp = meta_json.with_suffix(".tmp")
        tmp.write_text(json.dumps(all_meta, indent=2))
        tmp.rename(meta_json)

        with _meta_gen_lock:
            _meta_gen_state[filename] = {"status": "done", "result": result}

    except json.JSONDecodeError as e:
        with _meta_gen_lock:
            _meta_gen_state[filename] = {"status": "error", "result": {"error": f"Bad JSON from Claude: {e}", "raw": output[:500]}}
    except Exception as e:
        with _meta_gen_lock:
            _meta_gen_state[filename] = {"status": "error", "result": {"error": str(e)}}


@app.post("/api/video/{filename}/generate-metadata")
async def api_generate_metadata(filename: str):
    """Spawn Claude to generate title/description/tags from the screenplay."""
    filepath = VIDGEN_DIR / filename
    if not filepath.exists() or not filename.endswith(".mp4"):
        raise HTTPException(404, "Video not found")

    stem = filepath.stem
    base = re.sub(r'_(v\d+|final|render|output|s\d+.*)$', '', stem)

    with _meta_gen_lock:
        existing = _meta_gen_state.get(filename)
        if existing and existing["status"] == "running":
            return {"status": "running"}
        _meta_gen_state[filename] = {"status": "running", "result": None}

    thread = threading.Thread(target=_run_meta_gen, args=(filename, base), daemon=True)
    thread.start()
    return {"status": "started"}


@app.get("/api/video/{filename}/generate-metadata")
async def api_generate_metadata_poll(filename: str):
    """Poll for metadata generation status."""
    with _meta_gen_lock:
        state = _meta_gen_state.get(filename)
    if not state:
        return {"status": "idle"}
    return state


@app.get("/api/video/{filename}/thumbnail")
async def api_video_thumbnail(filename: str):
    filepath = VIDGEN_DIR / filename
    if not filepath.exists():
        raise HTTPException(404, "Video not found")
    thumb = extract_thumbnail(filepath)
    if not thumb.exists():
        raise HTTPException(500, "Failed to extract thumbnail")
    return FileResponse(str(thumb), media_type="image/jpeg")


@app.post("/api/video/{filename}/review")
async def api_video_review(filename: str):
    filepath = VIDGEN_DIR / filename
    if not filepath.exists():
        raise HTTPException(404, "Video not found")
    review_script = Path("/opt/tkk/vidgen/review_render.py")
    if not review_script.exists():
        raise HTTPException(404, "review_render.py not found")
    try:
        result = subprocess.run(
            ["python3", str(review_script), str(filepath), "--json"],
            capture_output=True, text=True, timeout=120, cwd=str(VIDGEN_DIR),
        )
        # Try to parse structured JSON output from review_render.py
        try:
            data = json.loads(result.stdout)
            if "checks" in data:
                return data
        except (json.JSONDecodeError, ValueError):
            pass
        # Fallback: wrap raw output as a single check
        output = result.stdout or result.stderr or "No output"
        status = "pass" if result.returncode == 0 else "fail"
        return {
            "checks": [{"name": "Review", "status": status, "detail": output.strip()}],
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"checks": [{"name": "Review", "status": "fail", "detail": "Timed out after 120s"}]}


@app.get("/api/screenplays")
async def api_screenplays():
    return list_screenplays()


@app.get("/api/screenplay/{filename}")
async def api_screenplay_read(filename: str):
    filepath = VIDGEN_DIR / filename
    if not filepath.exists() or not filename.endswith(".py"):
        raise HTTPException(404, "Screenplay not found")
    return {"filename": filename, "content": filepath.read_text()}


@app.put("/api/screenplay/{filename}")
async def api_screenplay_write(filename: str, request: Request):
    filepath = VIDGEN_DIR / filename
    if not filename.endswith(".py"):
        raise HTTPException(400, "Must be a .py file")
    body = await request.json()
    content = body.get("content", "")
    filepath.write_text(content)
    return {"filename": filename, "saved": True, "size": len(content)}


def _cleanup_render_jobs():
    """Remove completed jobs older than 10 minutes. Cap at 50 entries."""
    now = time.time()
    to_delete = [jid for jid, j in render_jobs.items()
                 if j["status"] != "running"
                 and now - j.get("completed_at", now) > 600]
    for jid in to_delete:
        del render_jobs[jid]


def _stream_render_output(job_id: str):
    """Background thread: read render stdout line-by-line into job buffer."""
    job = render_jobs.get(job_id)
    if not job:
        return
    proc = job["process"]
    try:
        for line in iter(proc.stdout.readline, ""):
            job["output"] += line
        proc.wait()
    except Exception:
        pass
    finally:
        job["status"] = "done" if proc.returncode == 0 else "failed"
        job["returncode"] = proc.returncode
        job["completed_at"] = time.time()
        job["process"] = None  # release fd


@app.post("/api/render")
async def api_render(request: Request):
    _cleanup_render_jobs()

    body = await request.json()
    screenplay = body.get("screenplay", "")
    if not screenplay:
        raise HTTPException(400, "Provide a valid screenplay filename")

    s = get_settings()
    engine = _engine_from_filename(screenplay)

    # Validate file existence based on engine
    if engine == "remotion":
        stem = screenplay.replace("_manim.py", "").replace(".py", "").replace(".json", "")
        manifest = REMOTION_MANIFESTS_DIR / f"{stem}.json"
        if not manifest.exists():
            raise HTTPException(404, f"No Remotion manifest found: {stem}.json")
    else:
        if not screenplay.endswith(".py"):
            raise HTTPException(400, "Provide a valid screenplay filename")
        filepath = VIDGEN_DIR / screenplay
        if not filepath.exists():
            raise HTTPException(404, "Screenplay not found")

    # Check concurrent renders
    active = sum(1 for j in render_jobs.values() if j["status"] == "running")
    if active >= _max_concurrent_renders():
        return JSONResponse({"error": "A render is already running. Please wait.", "status": "queued"}, status_code=429)

    job_id = str(uuid.uuid4())[:8]
    render_env = {
        **os.environ,
        "TKK_RENDER_CRF": s.get("render_crf", "23"),
        "TKK_RENDER_PRESET": s.get("render_preset", "fast"),
        "TKK_SILENCE_THRESHOLD_DB": s.get("silence_threshold_db", "-30"),
        "TKK_SILENCE_MIN_DURATION": s.get("silence_min_duration", "0.3"),
        "TKK_SHORT_MAX_DURATION": s.get("short_max_duration", "30"),
        "TKK_SHORT_FADE_DURATION": s.get("short_fade_duration", "1.5"),
        "TKK_FISH_BITRATE": s.get("fish_bitrate", "192"),
    }

    if engine == "remotion":
        # Copy TTS audio to remotion public dir if it exists
        tts_src = VIDGEN_DIR / f"tts_{stem}.mp3"
        tts_dst = VIDGEN_DIR / "remotion" / "public" / f"tts_{stem}.mp3"
        if tts_src.exists() and (not tts_dst.exists() or tts_src.stat().st_mtime > tts_dst.stat().st_mtime):
            import shutil
            shutil.copy2(str(tts_src), str(tts_dst))
        proc = subprocess.Popen(
            ["/usr/bin/npx", "tsx", "render.mts", stem],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            cwd=str(VIDGEN_DIR / "remotion"), text=True, env=render_env,
        )
    else:
        proc = subprocess.Popen(
            ["python3", str(filepath)],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            cwd=str(VIDGEN_DIR), text=True, env=render_env,
        )
    render_jobs[job_id] = {
        "process": proc, "status": "running", "screenplay": screenplay,
        "output": "", "started_at": time.time(),
    }
    thread = threading.Thread(target=_stream_render_output, args=(job_id,), daemon=True)
    thread.start()
    return {"job_id": job_id, "status": "running"}


@app.get("/api/render/active")
async def api_render_active():
    """Return the currently running render job, if any."""
    for job_id, job in render_jobs.items():
        if job["status"] == "running":
            elapsed = int(time.time() - job.get("started_at", time.time()))
            scenes_done = job["output"].count("Rendered ")
            return {
                "job_id": job_id,
                "status": "running",
                "screenplay": job["screenplay"],
                "elapsed": elapsed,
                "scenes_done": min(scenes_done, 6),
            }
    return {"job_id": None}


@app.get("/api/render/{job_id}/status")
async def api_render_status(job_id: str):
    job = render_jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")

    elapsed = int(time.time() - job.get("started_at", time.time()))
    scenes_done = job["output"].count("Rendered ")
    progress = min(int(scenes_done / 6 * 100), 99) if job["status"] == "running" else (100 if job["status"] == "done" else 0)

    return {
        "job_id": job_id,
        "status": job["status"],
        "returncode": job.get("returncode"),
        "screenplay": job["screenplay"],
        "output": job["output"][-2000:],
        "progress": progress,
        "elapsed": elapsed,
        "scenes_done": min(scenes_done, 6),
    }


@app.get("/api/render/{job_id}")
async def api_render_status_alias(job_id: str):
    """Alias for render status (editor template uses this path)."""
    job = render_jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")

    elapsed = int(time.time() - job.get("started_at", time.time()))
    scenes_done = job["output"].count("Rendered ")

    if job["status"] == "running":
        progress = min(int(scenes_done / 6 * 100), 99)
        return {
            "job_id": job_id, "state": "running",
            "status": f"Rendering scene {min(scenes_done + 1, 6)}/6",
            "progress": progress, "screenplay": job["screenplay"],
            "elapsed": elapsed, "scenes_done": min(scenes_done, 6),
            "output": job["output"][-2000:],
        }

    state = "complete" if job["status"] == "done" else ("cancelled" if job["status"] == "cancelled" else "failed")

    # Try to find the output filename
    output_filename = None
    if state == "complete":
        sp = job["screenplay"]
        stem = sp.replace("_manim.py", "").replace(".py", "")
        for candidate in [f"{stem}_final.mp4", f"{stem}.mp4"]:
            if (VIDGEN_DIR / candidate).exists():
                output_filename = candidate
                break

    return {
        "job_id": job_id,
        "state": state,
        "status": job["status"],
        "progress": 100 if state == "complete" else 0,
        "returncode": job.get("returncode"),
        "screenplay": job["screenplay"],
        "output": job["output"][-2000:],
        "error": job["output"][-1000:] if state == "failed" else None,
        "filename": output_filename,
        "elapsed": elapsed,
        "scenes_done": min(scenes_done, 6),
    }


@app.post("/api/render/{job_id}/cancel")
async def api_render_cancel(job_id: str):
    """Cancel a running render job."""
    job = render_jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    proc = job.get("process")
    if proc and proc.poll() is None:
        proc.kill()
    job["status"] = "cancelled"
    job["completed_at"] = time.time()
    job["process"] = None
    return {"cancelled": True, "job_id": job_id}


@app.post("/api/video/{filename}/posted")
async def api_toggle_posted(filename: str, request: Request):
    """Toggle or set posted status for a video in video_metadata.json."""
    filepath = VIDGEN_DIR / filename
    if not filepath.exists() or not filename.endswith(".mp4"):
        raise HTTPException(404, "Video not found")
    body = await request.json()
    meta_json = VIDGEN_DIR / "video_metadata.json"
    all_meta = {}
    if meta_json.exists():
        try:
            all_meta = json.loads(meta_json.read_text())
        except Exception:
            pass
    if filename not in all_meta:
        all_meta[filename] = {}
    all_meta[filename]["posted"] = bool(body.get("posted", not all_meta[filename].get("posted", False)))
    tmp = meta_json.with_suffix(".tmp")
    tmp.write_text(json.dumps(all_meta, indent=2))
    tmp.rename(meta_json)
    return {"posted": all_meta[filename]["posted"], "filename": filename}


@app.post("/api/videos/mark-all-posted")
async def api_mark_all_posted():
    """Bulk-mark all videos with existing metadata as posted."""
    meta_json = VIDGEN_DIR / "video_metadata.json"
    all_meta = {}
    if meta_json.exists():
        try:
            all_meta = json.loads(meta_json.read_text())
        except Exception:
            pass
    count = 0
    for key in all_meta:
        if all_meta[key].get("title") or all_meta[key].get("description"):
            all_meta[key]["posted"] = True
            count += 1
    tmp = meta_json.with_suffix(".tmp")
    tmp.write_text(json.dumps(all_meta, indent=2))
    tmp.rename(meta_json)
    return {"marked": count}


@app.post("/api/screenplay/{filename}/auto-pipeline")
async def api_auto_pipeline(filename: str):
    """Chain TTS → Render → Meta sequentially in a background thread."""
    stem = filename.replace("_manim.py", "").replace(".py", "").replace(".json", "")
    engine = _engine_from_filename(filename)
    if engine == "remotion":
        manifest = REMOTION_MANIFESTS_DIR / f"{stem}.json"
        if not manifest.exists():
            raise HTTPException(404, f"No Remotion manifest: {stem}.json")
    else:
        filepath = VIDGEN_DIR / filename
        if not filepath.exists() or not filename.endswith(".py"):
            raise HTTPException(404, "Screenplay not found")

    pipeline_id = str(uuid.uuid4())[:8]
    pipeline_jobs[pipeline_id] = {
        "status": "running", "step": "tts", "error": None,
        "filename": filename, "started_at": time.time(),
        "render_job_id": None, "meta_filename": None,
    }

    thread = threading.Thread(target=_run_auto_pipeline, args=(pipeline_id, filename), daemon=True)
    thread.start()
    return {"pipeline_id": pipeline_id, "status": "running"}


@app.get("/api/pipeline/{pipeline_id}")
async def api_pipeline_status(pipeline_id: str):
    """Poll for auto-pipeline progress."""
    job = pipeline_jobs.get(pipeline_id)
    if not job:
        raise HTTPException(404, "Pipeline job not found")
    result = {
        "pipeline_id": pipeline_id,
        "status": job["status"],
        "step": job["step"],
        "error": job.get("error"),
        "filename": job["filename"],
        "elapsed": int(time.time() - job.get("started_at", time.time())),
    }
    # Include render progress if in render step
    if job.get("render_job_id") and job["step"] == "render":
        rjob = render_jobs.get(job["render_job_id"])
        if rjob:
            scenes_done = rjob["output"].count("Rendered ")
            result["render_progress"] = min(int(scenes_done / 6 * 100), 99) if rjob["status"] == "running" else (100 if rjob["status"] == "done" else 0)
            result["render_scenes_done"] = min(scenes_done, 6)
    return result


def _run_auto_pipeline(pipeline_id: str, filename: str):
    """Background: TTS → Render → Meta, stop on error."""
    job = pipeline_jobs[pipeline_id]
    stem = filename.replace("_manim.py", "").replace(".py", "").replace(".json", "")

    # --- Step 1: TTS ---
    job["step"] = "tts"
    s = get_settings()
    engine = _engine_from_filename(filename)
    try:
        venv_python = VIDGEN_DIR / ".venv" / "bin" / "python3"
        python_cmd = str(venv_python) if venv_python.exists() else "python3"
        tts_script = VIDGEN_DIR / "generate_tts.py"
        tts_env = {**os.environ, "TKK_FISH_BITRATE": s.get("fish_bitrate", "192")}
        mp3_file = VIDGEN_DIR / f"tts_{stem}.mp3"
        mtime_before = mp3_file.stat().st_mtime if mp3_file.exists() else 0

        # For Remotion, pass the manifest JSON to generate_tts.py
        if engine == "remotion":
            tts_input = str(REMOTION_MANIFESTS_DIR / f"{stem}.json")
        else:
            tts_input = str(VIDGEN_DIR / filename)

        result = subprocess.run(
            [python_cmd, str(tts_script), tts_input],
            capture_output=True, text=True, timeout=120, cwd=str(VIDGEN_DIR),
            env=tts_env,
        )
        if result.returncode != 0 or not mp3_file.exists() or mp3_file.stat().st_mtime <= mtime_before:
            job["status"] = "failed"
            job["error"] = result.stderr[-500:] if result.stderr else "TTS failed — no audio produced"
            return
    except Exception as e:
        job["status"] = "failed"
        job["error"] = f"TTS error: {str(e)[:300]}"
        return

    # --- Step 2: Render ---
    job["step"] = "render"
    try:
        render_env = {
            **os.environ,
            "TKK_RENDER_CRF": s.get("render_crf", "23"),
            "TKK_RENDER_PRESET": s.get("render_preset", "fast"),
            "TKK_SILENCE_THRESHOLD_DB": s.get("silence_threshold_db", "-30"),
            "TKK_SILENCE_MIN_DURATION": s.get("silence_min_duration", "0.3"),
            "TKK_SHORT_MAX_DURATION": s.get("short_max_duration", "30"),
            "TKK_SHORT_FADE_DURATION": s.get("short_fade_duration", "1.5"),
            "TKK_FISH_BITRATE": s.get("fish_bitrate", "192"),
        }
        render_job_id = str(uuid.uuid4())[:8]

        if engine == "remotion":
            # Copy TTS audio to remotion public dir
            tts_src = VIDGEN_DIR / f"tts_{stem}.mp3"
            tts_dst = VIDGEN_DIR / "remotion" / "public" / f"tts_{stem}.mp3"
            if tts_src.exists() and (not tts_dst.exists() or tts_src.stat().st_mtime > tts_dst.stat().st_mtime):
                import shutil
                shutil.copy2(str(tts_src), str(tts_dst))
            proc = subprocess.Popen(
                ["/usr/bin/npx", "tsx", "render.mts", stem],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                cwd=str(VIDGEN_DIR / "remotion"), text=True, env=render_env,
            )
        else:
            proc = subprocess.Popen(
                ["python3", str(VIDGEN_DIR / filename)],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                cwd=str(VIDGEN_DIR), text=True, env=render_env,
            )
        render_jobs[render_job_id] = {
            "process": proc, "status": "running", "screenplay": filename,
            "output": "", "started_at": time.time(),
        }
        job["render_job_id"] = render_job_id

        # Stream render output (blocking)
        try:
            for line in iter(proc.stdout.readline, ""):
                render_jobs[render_job_id]["output"] += line
            proc.wait()
        except Exception:
            pass
        finally:
            rjob = render_jobs[render_job_id]
            rjob["status"] = "done" if proc.returncode == 0 else "failed"
            rjob["returncode"] = proc.returncode
            rjob["completed_at"] = time.time()
            rjob["process"] = None

        if proc.returncode != 0:
            job["status"] = "failed"
            job["error"] = f"Render failed (exit {proc.returncode})"
            return
    except Exception as e:
        job["status"] = "failed"
        job["error"] = f"Render error: {str(e)[:300]}"
        return

    # --- Step 2.5: Auto-generate short ---
    try:
        timings_file = VIDGEN_DIR / f"tts_{stem}_timings.json"
        final_path = VIDGEN_DIR / f"{stem}_final.mp4"
        if timings_file.exists() and final_path.exists():
            timings = json.loads(timings_file.read_text())
            scene_ends = [round(sum(timings["scene_durations"][:i+1]), 3)
                          for i in range(len(timings["scene_durations"]))]
            sys.path.insert(0, str(VIDGEN_DIR))
            from render_utils import make_short
            s = get_settings()
            make_short(str(final_path), scene_ends,
                       max_duration=float(s.get("short_max_duration", "30")),
                       fade_dur=float(s.get("short_fade_duration", "1.5")))
    except Exception:
        pass  # Short generation is optional

    # --- Step 3: Meta ---
    job["step"] = "meta"
    video_filename = f"{stem}_final.mp4"
    if not (VIDGEN_DIR / video_filename).exists():
        job["status"] = "failed"
        job["error"] = f"Expected {video_filename} not found after render"
        return

    try:
        base = re.sub(r'_(v\d+|final|render|output|s\d+.*)$', '', stem)
        _run_meta_gen(video_filename, base)
        # _run_meta_gen is synchronous, check result
        with _meta_gen_lock:
            state = _meta_gen_state.get(video_filename)
        if state and state["status"] == "error":
            job["status"] = "failed"
            job["error"] = f"Meta generation failed: {state['result'].get('error', 'unknown')}"
            return
    except Exception as e:
        job["status"] = "failed"
        job["error"] = f"Meta error: {str(e)[:300]}"
        return

    # --- Complete ---
    job["status"] = "complete"
    job["step"] = "done"


@app.post("/api/video/{filename}/layout-qa")
async def api_video_layout_qa(filename: str):
    """Extract frames from video, run layout QA, return JSON results."""
    filepath = VIDGEN_DIR / filename
    if not filepath.exists() or not filename.endswith(".mp4"):
        raise HTTPException(404, "Video not found")

    import tempfile, shutil
    qa_layout = VIDGEN_DIR / "qa_layout.py"
    if not qa_layout.exists():
        raise HTTPException(404, "qa_layout.py not found")

    # Get duration
    try:
        dur_result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(filepath)],
            capture_output=True, text=True, timeout=10,
        )
        duration = float(dur_result.stdout.strip())
    except Exception as e:
        return {"error": f"Could not get duration: {e}", "checks": []}

    # Extract 6 frames at scene midpoints
    frame_dir = Path(tempfile.mkdtemp(prefix="tkk_layout_qa_"))
    scene_count = 6
    interval = duration / scene_count
    for i in range(scene_count):
        t = interval * i + interval / 2
        out = frame_dir / f"frame_{i+1}.png"
        subprocess.run(
            ["ffmpeg", "-y", "-ss", str(t), "-i", str(filepath),
             "-frames:v", "1", "-q:v", "2", str(out)],
            capture_output=True, timeout=15,
        )

    # Run qa_layout.py --json on the frame directory
    try:
        result = subprocess.run(
            ["python3", str(qa_layout), str(frame_dir), "--json"],
            capture_output=True, text=True, timeout=60, cwd=str(VIDGEN_DIR),
        )
        try:
            scenes = json.loads(result.stdout)
        except (json.JSONDecodeError, ValueError):
            scenes = []

        # Flatten into checks format matching review endpoint
        checks = []
        for scene in scenes:
            scene_name = Path(scene.get("file", "")).stem
            for c in scene.get("checks", []):
                checks.append({
                    "name": f"{scene_name} — {c.get('name', '')}",
                    "status": c.get("status", "skip").lower(),
                    "detail": c.get("detail", ""),
                })

        # Add sync checks for the video's screenplay
        try:
            stem = filepath.stem
            base = re.sub(r'_(v\d+|final|render|output|s\d+.*)$', '', stem)
            for candidate in [f"{base}_manim.py", f"{stem}_manim.py"]:
                sp_path = VIDGEN_DIR / candidate
                if sp_path.exists():
                    from qa_sync import audit_screenplay
                    sync_result = audit_screenplay(sp_path)
                    for sc in sync_result.get("checks", []):
                        checks.append({
                            "name": f"sync — {sc['name']}",
                            "status": sc["status"].lower(),
                            "detail": sc["detail"],
                        })
                    break
        except Exception:
            pass

        return {
            "checks": checks,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"checks": [{"name": "Layout QA", "status": "fail", "detail": "Timed out"}]}
    finally:
        shutil.rmtree(frame_dir, ignore_errors=True)


@app.get("/api/screenplay/{filename}/qa")
async def api_screenplay_qa(filename: str):
    """Run layout + readability QA on a screenplay's preview PNGs."""
    # Accept .py files directly; for remotion, the .py key still works (previews use the same stem)
    stem = filename.replace("_manim.py", "").replace(".py", "").replace(".json", "")
    filepath = VIDGEN_DIR / filename
    # Allow if the .py file exists OR a remotion manifest exists for this stem
    manifest = REMOTION_MANIFESTS_DIR / f"{stem}.json"
    if not filepath.exists() and not manifest.exists():
        raise HTTPException(404, "Screenplay not found")
    preview_dir = VIDGEN_DIR / "previews"
    previews = sorted(preview_dir.glob(f"{stem}_scene_*.png")) if preview_dir.exists() else []

    if not previews:
        return {"error": "No previews — render previews first"}

    sys_path_added = str(VIDGEN_DIR) not in sys.path
    if sys_path_added:
        sys.path.insert(0, str(VIDGEN_DIR))
    try:
        from qa_layout import analyze_preview
        from qa_readability import check_scene
    finally:
        if sys_path_added and str(VIDGEN_DIR) in sys.path:
            sys.path.remove(str(VIDGEN_DIR))

    scenes = []
    overall_passed = True
    for png in previews:
        # Extract scene number from filename (e.g., "stem_scene_3.png" -> 3)
        m = re.search(r'_scene_(\d+)', png.stem)
        scene_num = int(m.group(1)) if m else len(scenes) + 1

        checks = []

        # Layout checks
        try:
            layout = analyze_preview(str(png))
            for c in layout.get("checks", []):
                checks.append({"name": c["name"], "status": c["status"], "detail": c["detail"]})
        except Exception as e:
            checks.append({"name": "layout", "status": "FAIL", "detail": str(e)})

        # Readability checks
        try:
            read_passed, report = check_scene(str(png), verbose=False)
            cr_match = re.search(r'contrast ([\d.]+):1 \[(\w+)\]', report)
            if cr_match:
                ratio, wcag = cr_match.group(1), cr_match.group(2)
                status = "PASS" if float(ratio) >= 4.5 else "WARN" if float(ratio) >= 3.0 else "FAIL"
                checks.append({"name": "contrast", "status": status, "detail": f"{ratio}:1 ratio ({wcag})"})
            # Extract margin info
            if "Margins: OK" in report:
                checks.append({"name": "margins", "status": "PASS", "detail": "Safe zone clear"})
            elif "Content near" in report:
                margin_issues = re.findall(r'WARN: (Content near \w+ edge.*)', report)
                detail = "; ".join(margin_issues) if margin_issues else "Content in unsafe zone"
                checks.append({"name": "margins", "status": "WARN", "detail": detail})
            if not read_passed:
                overall_passed = False
        except Exception as e:
            checks.append({"name": "readability", "status": "FAIL", "detail": str(e)})

        # Check if any layout check failed
        for c in checks:
            if c["status"] == "FAIL":
                overall_passed = False

        scenes.append({"scene": scene_num, "checks": checks})

    # Sync checks (narration-animation timing) — only for .py screenplays
    try:
        if filepath.exists() and filename.endswith(".py"):
            if str(VIDGEN_DIR) not in sys.path:
                sys.path.insert(0, str(VIDGEN_DIR))
            from qa_sync import audit_screenplay
            sync_result = audit_screenplay(filepath)
            # Merge per-scene sync checks into existing scene entries
            scene_map = {s["scene"]: s for s in scenes}
            for check in sync_result.get("checks", []):
                sc = check.get("scene")
                status = check["status"]
                if status == "FAIL":
                    overall_passed = False
                if sc and sc in scene_map:
                    scene_map[sc]["checks"].append({
                        "name": check["name"], "status": status, "detail": check["detail"],
                    })
                else:
                    # Global checks (av_drift) — attach to scene 1 or create a global section
                    if scenes:
                        scenes[0]["checks"].append({
                            "name": check["name"], "status": status, "detail": check["detail"],
                        })
    except Exception:
        pass  # sync QA is non-blocking

    return {"passed": overall_passed, "scenes": scenes}


@app.post("/api/screenplay/{filename}/preview")
async def api_screenplay_preview(filename: str):
    """Placeholder for scene preview grid — returns empty for now."""
    stem = filename.replace("_manim.py", "").replace(".py", "").replace(".json", "")
    filepath = VIDGEN_DIR / filename
    manifest = REMOTION_MANIFESTS_DIR / f"{stem}.json"
    if not filepath.exists() and not manifest.exists():
        raise HTTPException(404, "Screenplay not found")
    return {"scenes": []}


@app.get("/api/screenplay/{filename}/parsed")
async def api_screenplay_parsed(filename: str):
    """Parse a screenplay .py/.json file and return the screenplay dict as JSON."""
    stem = filename.replace("_manim.py", "").replace(".py", "").replace(".json", "")
    filepath = VIDGEN_DIR / filename

    # Auto-detect engine from filename
    engine = _engine_from_filename(filename)
    manifest_path = REMOTION_MANIFESTS_DIR / f"{stem}.json"
    manim_path = VIDGEN_DIR / f"{stem}_manim.py"
    if engine == "remotion" and manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        scenes = []
        for i, sc in enumerate(manifest.get("scenes", []), 1):
            scene_entry = {
                "index": i,
                "label": sc.get("label", f"Scene {i}"),
                "type": sc.get("type", "unknown"),
            }
            # Check for preview images
            preview_name = f"{stem}_scene_{i}.png"
            if (PREVIEWS_DIR / preview_name).exists():
                scene_entry["preview"] = preview_name
            scenes.append(scene_entry)
        # Check if manifest was modified after the last render
        final_path = VIDGEN_DIR / f"{stem}_final.mp4"
        manifest_stale = False
        if final_path.exists() and manifest_path.exists():
            manifest_stale = manifest_path.stat().st_mtime > final_path.stat().st_mtime

        return {
            "type": "remotion",
            "filename": filename,
            "tts_script": manifest.get("ttsScript", ""),
            "scenes": scenes,
            "scene_count": len(scenes),
            "manifest_path": str(manifest_path),
            "colors": manifest.get("colors", {}),
            "manim_exists": manim_path.exists(),
            "peer_filename": manim_path.name if manim_path.exists() else None,
            "manifest_stale": manifest_stale,
        }

    if not filepath.exists() or not filename.endswith(".py"):
        raise HTTPException(404, "Screenplay not found")
    content = filepath.read_text()
    import re, ast

    # Detect type
    is_manim = "from manim import" in content or "from manim " in content
    is_vidgen = "screenplay = {" in content or "screenplay={" in content

    result = {
        "filename": filename,
        "type": "manim" if is_manim else "vidgen" if is_vidgen else "unknown",
        "remotion_manifest_exists": manifest_path.exists(),
        "peer_filename": f"{stem}.json" if manifest_path.exists() else None,
    }

    # Extract docstring
    match = re.search(r'^"""(.*?)"""', content, re.DOTALL)
    if match:
        result["docstring"] = match.group(1).strip()

    # Extract TTS_SCRIPT
    match = re.search(r'TTS_SCRIPT\s*=\s*"""(.*?)"""', content, re.DOTALL)
    if match:
        result["tts_script"] = match.group(1).strip()

    # Extract narration from VTT cues
    narration_lines = re.findall(r'^\s+[\d.]+\s+\([\d.]+\)\s+(.+)$', content, re.MULTILINE)
    if narration_lines:
        result["narration"] = narration_lines

    if is_manim:
        # Parse scenes from docstring VTT cues
        doc = result.get("docstring", "")
        scenes = []
        # Pattern: "Scene N LABEL (start-end = duration):" followed by VTT lines
        scene_blocks = re.split(r'Scene\s+(\d+)\s+([^(]*)\(([^)]+)\):', doc)
        # scene_blocks: ['preamble', '1', 'THE HOOK ', '0.0-7.6s = 7.60s', 'cue lines...', '2', ...]
        i = 1
        while i < len(scene_blocks) - 3:
            scene_num = int(scene_blocks[i])
            scene_label = scene_blocks[i+1].strip()
            duration_str = scene_blocks[i+2].strip()
            cues_text = scene_blocks[i+3] if i+3 < len(scene_blocks) else ""

            # Parse duration: try "= Xs" first, then fall back to range "start–ends"
            dur_match = re.search(r'=\s*([\d.]+)s', duration_str)
            if dur_match:
                duration = float(dur_match.group(1))
            else:
                # Range format: "0.0–6.5s" or "0.0-6.5s"
                range_match = re.search(r'([\d.]+)\s*[–-]\s*([\d.]+)s?', duration_str)
                duration = round(float(range_match.group(2)) - float(range_match.group(1)), 3) if range_match else 0

            # Parse cue lines
            cue_lines = []
            for cue_line in cues_text.strip().split('\n'):
                cue_line = cue_line.strip()
                cue_match = re.match(r'[\d.]+\s+\([\d.]+\)\s+(.+)', cue_line)
                if cue_match:
                    cue_lines.append(cue_match.group(1))

            # Human-readable label
            label = scene_label.replace('_', ' ').title() if scene_label else f"Scene {scene_num}"

            scenes.append({
                "index": scene_num,
                "label": label,
                "duration": duration,
                "narration": cue_lines,
            })
            i += 4

        # Extract ZONE_ usage and Text() calls per Scene class
        scene_classes = re.findall(r'class\s+(\w+)\(Scene\):', content)
        # Split content by scene classes to analyze each
        class_sections = re.split(r'class\s+\w+\(Scene\):', content)[1:]  # skip preamble

        for idx, section in enumerate(class_sections):
            if idx >= len(scenes):
                break
            # Find ZONE_ references
            zones_used = list(set(re.findall(r'ZONE_(\w+)', section)))
            scenes[idx]["zones"] = zones_used

            # Find text content from safe_text() and Text() calls
            text_calls = re.findall(r'(?:safe_text|Text)\s*\(\s*["\']([^"\']{3,})["\']', section)
            scenes[idx]["screen_text"] = text_calls[:5]  # limit to 5

        # Check for preview images
        stem = filename.replace('_manim.py', '').replace('.py', '')
        for scene in scenes:
            preview_name = f"{stem}_scene_{scene['index']}.png"
            if (PREVIEWS_DIR / preview_name).exists():
                scene["preview"] = preview_name

        result["scenes"] = scenes
        result["scene_count"] = len(scenes)
        result["total_duration"] = sum(s["duration"] for s in scenes)

    if is_vidgen:
        # Try to extract the screenplay dict
        try:
            # Run the file in a sandbox to get the dict
            sandbox_result = subprocess.run(
                ["python3", "-c", f"""
import json, sys, os
os.chdir('{VIDGEN_DIR}')
sys.path.insert(0, '{VIDGEN_DIR}')
code = open('{filepath}').read()
import re
# Provide __file__ and neutralize render/print calls
code = re.sub(r'render_video\\(.*?\\)', 'None', code, flags=re.DOTALL)
code = re.sub(r'preview_frame\\(.*?\\)', 'None', code, flags=re.DOTALL)
code = re.sub(r'preview_grid\\(.*?\\)', 'None', code, flags=re.DOTALL)
code = re.sub(r'print\\(.*?\\)', 'None', code, flags=re.DOTALL)
ns = {{'__file__': '{filepath}', '__name__': '__parse__'}}
exec(code, ns)
sp = ns.get('screenplay')
if sp:
    print(json.dumps(sp, default=str))
"""],
                capture_output=True, text=True, timeout=10,
                cwd=str(VIDGEN_DIR),
            )
            if sandbox_result.returncode == 0 and sandbox_result.stdout.strip():
                sp = json.loads(sandbox_result.stdout.strip())
                result["screenplay"] = sp
                # Extract scene summaries for the UI
                scenes = sp.get("scenes", [])
                result["scene_count"] = len(scenes)
                result["total_duration"] = sum(s.get("duration", 0) for s in scenes)
                result["scenes_summary"] = []
                for i, scene in enumerate(scenes):
                    texts = [l.get("content", "") for l in scene.get("layers", []) if l.get("type") == "text"]
                    images = [l.get("path", "") for l in scene.get("layers", []) if l.get("type") in ("image", "svg")]
                    result["scenes_summary"].append({
                        "index": i + 1,
                        "duration": scene.get("duration", 0),
                        "background": scene.get("background", ""),
                        "bg_animation": scene.get("bg_animation", "none"),
                        "transition": scene.get("transition", "cut"),
                        "transition_duration": scene.get("transition_duration", 0.3),
                        "layer_count": len(scene.get("layers", [])),
                        "texts": texts,
                        "images": [os.path.basename(p) for p in images],
                        "has_camera": bool(scene.get("camera")),
                        "vignette": scene.get("vignette", False),
                        "grain": scene.get("grain", 0),
                    })
        except Exception as e:
            result["parse_error"] = str(e)

    return result


@app.get("/api/screenplay/{filename}/manifest")
async def api_screenplay_manifest_read(filename: str):
    """Read a Remotion manifest JSON for a screenplay."""
    stem = filename.replace("_manim.py", "").replace(".py", "").replace(".json", "")
    manifest_path = REMOTION_MANIFESTS_DIR / f"{stem}.json"
    if not manifest_path.exists():
        raise HTTPException(404, f"No Remotion manifest for {stem}")
    return JSONResponse(json.loads(manifest_path.read_text()))


@app.put("/api/screenplay/{filename}/manifest")
async def api_screenplay_manifest_write(filename: str, request: Request):
    """Write/update a Remotion manifest JSON for a screenplay."""
    stem = filename.replace("_manim.py", "").replace(".py", "").replace(".json", "")
    manifest_path = REMOTION_MANIFESTS_DIR / f"{stem}.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "Invalid JSON body")
    manifest_path.write_text(json.dumps(body, indent=2))
    return {"success": True, "path": str(manifest_path), "size": manifest_path.stat().st_size}


@app.post("/api/screenplay/{filename}/tts")
async def api_screenplay_tts(filename: str):
    """Generate Fish Audio TTS for a screenplay."""
    s = get_settings()
    engine = _engine_from_filename(filename)
    stem = filename.replace("_manim.py", "").replace(".py", "").replace(".json", "")

    # Determine the input file for generate_tts.py
    if engine == "remotion":
        manifest = REMOTION_MANIFESTS_DIR / f"{stem}.json"
        if not manifest.exists():
            raise HTTPException(404, f"No Remotion manifest: {stem}.json")
        tts_input = str(manifest)
    else:
        filepath = VIDGEN_DIR / filename
        if not filepath.exists() or not filename.endswith(".py"):
            raise HTTPException(404, "Screenplay not found")
        tts_input = str(filepath)

    # Check for render concurrency
    active = sum(1 for j in render_jobs.values() if j["status"] == "running")
    if active >= _max_concurrent_renders():
        return JSONResponse({"error": "A render is already running."}, status_code=429)

    tts_script = VIDGEN_DIR / "generate_tts.py"
    if not tts_script.exists():
        raise HTTPException(404, "generate_tts.py not found")

    try:
        import time as _time
        venv_python = VIDGEN_DIR / ".venv" / "bin" / "python3"
        python_cmd = str(venv_python) if venv_python.exists() else "python3"
        tts_env = {**os.environ, "TKK_FISH_BITRATE": get_settings().get("fish_bitrate", "192")}
        mp3_file = VIDGEN_DIR / f"tts_{stem}.mp3"
        # Record mtime before run so we can tell if the file was actually produced
        mtime_before = mp3_file.stat().st_mtime if mp3_file.exists() else 0
        t_before = _time.time()
        result = subprocess.run(
            [python_cmd, str(tts_script), tts_input],
            capture_output=True, text=True, timeout=120, cwd=str(VIDGEN_DIR),
            env=tts_env,
        )
        # Check that the file exists AND was written during this run
        file_is_new = mp3_file.exists() and mp3_file.stat().st_mtime > mtime_before
        duration = None
        if file_is_new:
            try:
                dur_result = subprocess.run(
                    ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                     "-of", "default=noprint_wrappers=1:nokey=1", str(mp3_file)],
                    capture_output=True, text=True, timeout=5,
                )
                duration = float(dur_result.stdout.strip())
            except Exception:
                pass
        success = result.returncode == 0 and file_is_new
        stderr = result.stderr[-500:] if result.stderr else ""
        if not success and not stderr:
            stderr = "TTS generation failed — no audio file was produced"
        # Auto-generate scene timings from silence detection
        timings_result = None
        if success and duration:
            try:
                sys.path.insert(0, str(VIDGEN_DIR))
                from render_utils import detect_scene_timings
                # Determine number of scenes
                num_scenes = 6
                if engine == "remotion":
                    m = json.loads((REMOTION_MANIFESTS_DIR / f"{stem}.json").read_text())
                    num_scenes = len(m.get("scenes", []))
                timings_result = detect_scene_timings(str(mp3_file), num_scenes)
            except Exception as e:
                stderr += f"\nTimings detection failed: {e}"
        return {
            "success": success,
            "duration": duration,
            "timings": timings_result,
            "stdout": result.stdout[-500:] if result.stdout else "",
            "stderr": stderr,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "TTS generation timed out"}


@app.post("/api/screenplay/{filename}/preview-render")
async def api_screenplay_preview_render(filename: str):
    """Render preview PNGs for a screenplay."""
    s = get_settings()
    engine = _engine_from_filename(filename)
    stem = filename.replace("_manim.py", "").replace(".py", "").replace(".json", "")

    if engine == "remotion":
        manifest = REMOTION_MANIFESTS_DIR / f"{stem}.json"
        if not manifest.exists():
            raise HTTPException(404, f"No Remotion manifest: {stem}.json")
        try:
            # Copy TTS audio to remotion public dir
            tts_src = VIDGEN_DIR / f"tts_{stem}.mp3"
            tts_dst = VIDGEN_DIR / "remotion" / "public" / f"tts_{stem}.mp3"
            if tts_src.exists() and (not tts_dst.exists() or tts_src.stat().st_mtime > tts_dst.stat().st_mtime):
                import shutil
                shutil.copy2(str(tts_src), str(tts_dst))
            result = subprocess.run(
                ["/usr/bin/npx", "tsx", "preview.mts", stem],
                capture_output=True, text=True, timeout=300,
                cwd=str(VIDGEN_DIR / "remotion"),
            )
            previews = []
            for i in range(1, 9):
                preview_name = f"{stem}_scene_{i}.png"
                if (PREVIEWS_DIR / preview_name).exists():
                    previews.append(preview_name)
            return {
                "success": result.returncode == 0,
                "previews": previews,
                "stdout": result.stdout[-500:] if result.stdout else "",
                "stderr": result.stderr[-500:] if result.stderr else "",
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Remotion preview render timed out"}
    else:
        filepath = VIDGEN_DIR / filename
        if not filepath.exists() or not filename.endswith(".py"):
            raise HTTPException(404, "Screenplay not found")
        try:
            result = subprocess.run(
                ["python3", str(filepath), "--preview"],
                capture_output=True, text=True, timeout=180, cwd=str(VIDGEN_DIR),
            )
            previews = []
            for i in range(1, 7):
                preview_name = f"{stem}_scene_{i}.png"
                if (PREVIEWS_DIR / preview_name).exists():
                    previews.append(preview_name)
            return {
                "success": result.returncode == 0,
                "previews": previews,
                "stdout": result.stdout[-500:] if result.stdout else "",
                "stderr": result.stderr[-500:] if result.stderr else "",
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Preview render timed out"}


# --- Studio (AI chat for video production) ---

CLAUDE_BIN = "/usr/bin/claude"
MCP_CONFIG = str(VIDGEN_DIR / "mcp_config.json")
STUDIO_SYSTEM_PROMPT = """You are the TKK video production assistant at clips.applesauce.chat.
You help create TikTok educational videos (28-45s, vertical, 6-scene mystery arc).

## Your Tools
You have TWO sets of tools:
1. **Built-in tools**: Read, Bash, Edit, Write, Grep, Glob — use these to read files, explore the filesystem, run commands
2. **TKK MCP tools** (via tkk-studio):
   - **Pipeline**: list_screenplays, pipeline_status, production_stats, batch_check
   - **Screenplays**: read_screenplay, write_screenplay, write_remotion_manifest, search_screenplays
   - **Production**: read_production_guide, generate_tts, render_preview, render_full, run_qa
   - **Management**: list_videos, save_video_metadata, get_video_metadata, list_uploads, get_queue, update_queue

## Key Paths
- Remotion manifests: /opt/tkk/vidgen/remotion/src/manifests/*.json (primary)
- Manim screenplays: /opt/tkk/vidgen/*_manim.py (legacy)
- Production guide: /opt/tkk/vidgen/PRODUCTION_GUIDE.md (READ THIS before writing screenplays)
- TTS audio: /opt/tkk/vidgen/tts_*.mp3
- Final videos: /opt/tkk/vidgen/*_final.mp4
- Uploaded files: /opt/tkk/clips/uploads/

## Workflow (Remotion — default for new videos)
1. Discuss topic with user. If they attach a file, READ it with your Read tool.
2. Read the production guide (read_production_guide) to understand the format
3. Write a Remotion manifest JSON with 6 scenes, ttsScript, and colors
4. Generate TTS with Fish Audio using generate_tts (ALWAYS use Fish Audio)
5. Render preview PNGs and run QA using render_preview then run_qa
6. If QA passes, full render using render_full

## Remotion Manifest Format
New videos use Remotion JSON manifests at /opt/tkk/vidgen/remotion/src/manifests/{topic}.json.
Each manifest has: topic, ttsScript (full narration), colors (bg/accent/secondary), and scenes array.
Scene types: headline, counter, barChart, timeline, kenburns, map, iconRow, populationDrop, splitCompare, videoClip.
See existing manifests for examples. The ttsScript field contains the full narration for TTS generation.

## Legacy: Manim Screenplays
Manim (_manim.py) screenplays still work but are legacy. For Manim, plan_screenplay() is required
before write_screenplay(). Use Remotion for all new work unless the user specifically asks for Manim.

## Rules
- Be concise. The user sees your response in a chat bubble.
- When the user attaches a file, use your Read tool to read it from the given path.
- Never suggest the user run terminal commands — you can run them yourself with Bash.
- Use MCP tools for pipeline operations (TTS, render, QA, screenplay CRUD).
- If you're working on a long task (multiple screenplays), give progress updates between each one.
- If you hit a budget or time limit, tell the user what's done and what's left."""

# Background studio state (fire-and-forget + poll)
_studio_lock = threading.Lock()
_studio_state: dict | None = None
# Shape when active:
# {
#     "session_id": str,
#     "proc": subprocess.Popen,
#     "buffer": str,            # final text response (from assistant text blocks)
#     "status": "running" | "done" | "error" | "timeout",
#     "started": float,
#     "activities": list,       # [{type, name, status, detail, ts}, ...]
#     "current_tool": dict|None,# {name, detail} while a tool is executing
#     "cost_usd": float,
#     "error": str|None,
# }

# Human-readable labels for MCP tool names
_TOOL_LABELS = {
    "plan_screenplay": ("Planning", "topic"),
    "write_screenplay": ("Writing", "filename"),
    "generate_tts": ("Generating TTS", "filename"),
    "render_preview": ("Rendering previews", "filename"),
    "render_full": ("Full render", "filename"),
    "run_qa": ("Running QA", "filename"),
    "read_production_guide": ("Reading production guide", None),
    "read_screenplay": ("Reading screenplay", "filename"),
    "list_screenplays": ("Listing screenplays", None),
    "pipeline_status": ("Checking pipeline", None),
    "search_screenplays": ("Searching screenplays", None),
    "list_videos": ("Listing videos", None),
    "save_video_metadata": ("Saving metadata", "filename"),
    "get_video_metadata": ("Getting metadata", "filename"),
    "get_queue": ("Checking queue", None),
    "update_queue": ("Updating queue", None),
    "production_stats": ("Getting stats", None),
    "batch_check": ("Batch check", None),
}


def _tool_activity_label(tool_name: str, tool_input: dict | None) -> str:
    """Generate a human-readable label for a tool call."""
    if tool_name in _TOOL_LABELS:
        verb, key = _TOOL_LABELS[tool_name]
        if key and tool_input:
            detail = tool_input.get(key, tool_input.get("topic", ""))
            if detail:
                # Truncate long values
                detail = str(detail)[:60]
                return f"{verb}: {detail}"
        return verb
    # Built-in tools — collapse to generic labels
    if tool_name in ("Read", "Bash", "Grep", "Glob", "Edit", "Write"):
        return f"Using {tool_name}"
    return f"Running: {tool_name}"


_pipeline_cache: dict = {"text": "", "ts": 0}

def _get_pipeline_context() -> str:
    """Summarize pipeline state for Claude's system prompt. Cached for 30s."""
    now = time.time()
    if now - _pipeline_cache["ts"] < 30 and _pipeline_cache["text"]:
        return _pipeline_cache["text"]

    # Count both Remotion manifests and Manim screenplays
    stems = set()
    if REMOTION_MANIFESTS_DIR.exists():
        for f in REMOTION_MANIFESTS_DIR.glob("*.json"):
            stems.add(f.stem)
    for f in VIDGEN_DIR.glob("*_manim.py"):
        stems.add(f.stem.replace("_manim", ""))

    total = len(stems)
    complete = 0
    incomplete_sample = []
    for stem in sorted(stems):
        has_final = any((VIDGEN_DIR / f"{stem}{s}.mp4").exists() for s in ["_final", ""])
        if has_final:
            complete += 1
        elif len(incomplete_sample) < 5:
            incomplete_sample.append(stem)

    result = f"Pipeline: {total} screenplays, {complete} complete."
    if incomplete_sample:
        result += f" Incomplete examples: {', '.join(incomplete_sample)}"

    _pipeline_cache["text"] = result
    _pipeline_cache["ts"] = now
    return result


def _run_claude_bg(session_id: str, cmd: list[str], stdin_message: str = ""):
    """Background thread: run Claude with stream-json, parse events, save to DB when done."""
    global _studio_state
    proc = None
    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=subprocess.PIPE, text=True, cwd=str(VIDGEN_DIR),
        )
        if stdin_message:
            try:
                proc.stdin.write(stdin_message)
                proc.stdin.close()
            except Exception:
                pass
        with _studio_lock:
            if _studio_state:
                _studio_state["proc"] = proc

        start_time = time.time()
        pending_tools: dict = {}  # tool_use_id -> activity index

        for line in iter(proc.stdout.readline, ""):
            if time.time() - start_time > 900:
                proc.kill()
                with _studio_lock:
                    if _studio_state and _studio_state["session_id"] == session_id:
                        _studio_state["error"] = "Timed out after 15 minutes"
                        _studio_state["status"] = "timeout"
                break

            line = line.strip()
            if not line:
                continue

            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            with _studio_lock:
                if not _studio_state or _studio_state["session_id"] != session_id:
                    continue
                state = _studio_state
                state["last_activity"] = time.time()

            event_type = event.get("type", "")

            if event_type == "assistant":
                message = event.get("message", {})
                content_blocks = message.get("content", [])
                for block in content_blocks:
                    block_type = block.get("type", "")
                    if block_type == "tool_use":
                        tool_name = block.get("name", "unknown")
                        tool_input = block.get("input", {})
                        tool_id = block.get("id", "")
                        label = _tool_activity_label(tool_name, tool_input)
                        activity = {
                            "type": "tool_call",
                            "name": tool_name,
                            "label": label,
                            "status": "running",
                            "detail": "",
                            "ts": time.time() - start_time,
                        }
                        with _studio_lock:
                            state["activities"].append(activity)
                            state["current_tool"] = {"name": tool_name, "label": label}
                            if tool_id:
                                pending_tools[tool_id] = len(state["activities"]) - 1

                    elif block_type == "text":
                        text = block.get("text", "")
                        if text:
                            with _studio_lock:
                                state["buffer"] += text

                stop_reason = message.get("stop_reason", "")
                if stop_reason == "end_turn":
                    with _studio_lock:
                        state["current_tool"] = None

            elif event_type == "result":
                cost = event.get("cost_usd") or event.get("cost", 0)
                if cost:
                    with _studio_lock:
                        state["cost_usd"] = float(cost)

                is_error = event.get("is_error", False)
                error_msg = event.get("error", "")
                result_text = event.get("result", "")

                if "cost_usd" in event:
                    if result_text and isinstance(result_text, str):
                        with _studio_lock:
                            if not state["buffer"].strip():
                                state["buffer"] = result_text
                    if is_error or error_msg:
                        with _studio_lock:
                            state["error"] = error_msg or result_text or "Unknown error"

            elif event_type == "tool_result":
                tool_use_id = event.get("tool_use_id", "")
                is_error = event.get("is_error", False)
                with _studio_lock:
                    if tool_use_id in pending_tools:
                        idx = pending_tools.pop(tool_use_id)
                        if idx < len(state["activities"]):
                            state["activities"][idx]["status"] = "error" if is_error else "done"
                    state["current_tool"] = None

        proc.wait(timeout=10)

        with _studio_lock:
            if _studio_state and _studio_state["session_id"] == session_id:
                if _studio_state["status"] == "running":
                    for idx in pending_tools.values():
                        if idx < len(_studio_state["activities"]):
                            _studio_state["activities"][idx]["status"] = "done"
                    if proc.returncode and proc.returncode != 0:
                        try:
                            err = proc.stderr.read()[-500:] if proc.stderr else ""
                        except Exception:
                            err = ""
                        _studio_state["error"] = err or "Process exited with error"
                        _studio_state["status"] = "error"
                    else:
                        _studio_state["status"] = "done"

    except subprocess.TimeoutExpired:
        if proc:
            proc.kill()
        with _studio_lock:
            if _studio_state and _studio_state["session_id"] == session_id:
                _studio_state["error"] = "Process timed out"
                _studio_state["status"] = "timeout"
    except Exception as e:
        with _studio_lock:
            if _studio_state and _studio_state["session_id"] == session_id:
                _studio_state["error"] = str(e)
                _studio_state["status"] = "error"
    finally:
        if proc and proc.poll() is None:
            proc.kill()

        with _studio_lock:
            if _studio_state and _studio_state["session_id"] == session_id:
                response_text = _studio_state["buffer"].strip()
                error = _studio_state.get("error")
            else:
                response_text = ""
                error = None

        db_text = response_text
        if not db_text and error:
            db_text = f"[Error: {error}]"
        elif not db_text:
            db_text = "[No response — Claude may have encountered an error]"

        with clips_db.db_session() as conn:
            conn.execute(
                "INSERT INTO studio_messages (session_id, role, content) VALUES (?, 'assistant', ?)",
                (session_id, db_text),
            )

        with _studio_lock:
            if _studio_state and _studio_state["session_id"] == session_id:
                _studio_state = None


@app.get("/studio", response_class=HTMLResponse)
async def studio_page(request: Request):
    return RedirectResponse("/workbench", status_code=302)


@app.get("/api/workbench/screenplays")
async def api_workbench_screenplays():
    """Return grouped, version-collapsed screenplay list."""
    return _get_grouped_screenplays()


@app.get("/api/workbench/chat/{screenplay_filename}")
async def api_workbench_chat(screenplay_filename: str):
    """Find or create a studio session linked to a screenplay."""
    with clips_db.db_session() as conn:
        row = conn.execute(
            "SELECT id, name FROM studio_sessions WHERE screenplay_filename = ? ORDER BY updated_at DESC LIMIT 1",
            (screenplay_filename,),
        ).fetchone()
        if row:
            session_id = row["id"]
            messages = conn.execute(
                "SELECT role, content, created_at FROM studio_messages WHERE session_id = ? ORDER BY created_at",
                (session_id,),
            ).fetchall()
            return {"session_id": session_id, "messages": [dict(m) for m in messages]}

    # Create new session for this screenplay
    session_id = str(uuid.uuid4())
    stem = screenplay_filename.replace("_manim.py", "").replace(".py", "")
    name = f"Editing: {stem.replace('_', ' ').title()}"
    with clips_db.db_session() as conn:
        conn.execute(
            "INSERT INTO studio_sessions (id, name, screenplay_filename) VALUES (?, ?, ?)",
            (session_id, name, screenplay_filename),
        )
    return {"session_id": session_id, "messages": []}


@app.post("/api/studio/sessions")
async def create_studio_session(request: Request):
    """Create a new studio chat session."""
    session_id = str(uuid.uuid4())
    body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    name = body.get("name", "New session")

    with clips_db.db_session() as conn:
        conn.execute(
            "INSERT INTO studio_sessions (id, name) VALUES (?, ?)",
            (session_id, name),
        )
    return {"id": session_id, "name": name}


@app.get("/api/studio/sessions")
async def list_studio_sessions():
    """List recent studio sessions with message counts."""
    with clips_db.db_session() as conn:
        rows = conn.execute("""
            SELECT s.id, s.name, s.screenplay_filename, s.created_at, s.updated_at,
                   COUNT(m.id) as message_count
            FROM studio_sessions s
            LEFT JOIN studio_messages m ON m.session_id = s.id
            GROUP BY s.id
            ORDER BY s.updated_at DESC
            LIMIT 50
        """).fetchall()
    return {"sessions": [dict(r) for r in rows]}


UPLOADS_DIR = Path("/opt/tkk/clips/uploads")
UPLOADS_DIR.mkdir(exist_ok=True)


@app.post("/api/upload")
async def api_upload(request: Request):
    """Save an uploaded file to disk, return its path for Claude to read."""
    form = await request.form()
    file = form.get("file")
    if not file:
        raise HTTPException(400, "No file provided")
    # Sanitize filename
    safe_name = re.sub(r'[^\w\-.]', '_', file.filename)[:200]
    dest = UPLOADS_DIR / safe_name
    content = await file.read()
    dest.write_bytes(content)
    return {"path": str(dest), "filename": safe_name, "size": len(content)}


@app.delete("/api/studio/sessions/{session_id}")
async def delete_studio_session(session_id: str):
    """Delete a studio session and its messages."""
    with clips_db.db_session() as conn:
        conn.execute("DELETE FROM studio_messages WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM studio_sessions WHERE id = ?", (session_id,))
    return {"deleted": session_id}


@app.get("/api/studio/sessions/{session_id}/messages")
async def get_studio_messages(session_id: str):
    """Get all messages for a session."""
    with clips_db.db_session() as conn:
        rows = conn.execute(
            "SELECT role, content, created_at FROM studio_messages WHERE session_id = ? ORDER BY created_at",
            (session_id,),
        ).fetchall()
    return {"messages": [dict(r) for r in rows]}


@app.post("/api/studio/sessions/{session_id}/message")
async def send_studio_message(session_id: str, request: Request):
    """Send a message to a studio session. Launches Claude in background."""
    global _studio_state

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "Invalid message — file may contain unsupported characters. Try pasting the text instead.")
    message = body.get("message", "").strip()
    screenplay_file = body.get("screenplay", "").strip()
    if not message:
        raise HTTPException(400, "Message required")

    # Check if Claude is already running
    with _studio_lock:
        if _studio_state and _studio_state["status"] == "running":
            return JSONResponse(
                status_code=409,
                content={"error": "Claude is already working"},
            )

    # Link session to screenplay if provided
    if screenplay_file:
        with clips_db.db_session() as conn:
            conn.execute(
                "UPDATE studio_sessions SET screenplay_filename = ? WHERE id = ?",
                (screenplay_file, session_id),
            )

    # Save user message
    with clips_db.db_session() as conn:
        conn.execute(
            "INSERT INTO studio_messages (session_id, role, content) VALUES (?, 'user', ?)",
            (session_id, message),
        )
        msg_count = conn.execute(
            "SELECT COUNT(*) FROM studio_messages WHERE session_id = ?", (session_id,)
        ).fetchone()[0]
        if msg_count == 1:
            name = message[:60] + ("..." if len(message) > 60 else "")
            conn.execute(
                "UPDATE studio_sessions SET name = ? WHERE id = ?", (name, session_id)
            )
        conn.execute(
            "UPDATE studio_sessions SET updated_at = datetime('now') WHERE id = ?",
            (session_id,),
        )

    # Build claude command with pipeline context
    is_first = msg_count == 1
    pipeline_ctx = _get_pipeline_context()
    system_prompt = STUDIO_SYSTEM_PROMPT + f"\n\nCurrent pipeline status:\n{pipeline_ctx}"

    # Only include screenplay content on first message (it's in session context after that)
    if screenplay_file and is_first:
        sp_path = VIDGEN_DIR / screenplay_file
        if sp_path.exists():
            sp_content = sp_path.read_text()[:4000]
            system_prompt += f"\n\nCurrently editing screenplay: {screenplay_file}\n```python\n{sp_content}\n```"
    elif screenplay_file:
        system_prompt += f"\n\nCurrently editing: {screenplay_file}"

    s = get_settings()
    cmd = [CLAUDE_BIN, "-p", "--output-format", "stream-json", "--verbose",
           "--model", s["studio_model"], "--mcp-config", MCP_CONFIG,
           "--permission-mode", "bypassPermissions",
           "--max-budget-usd", s["studio_budget"],
           "--append-system-prompt", system_prompt]

    # Decide whether to resume or start fresh
    # Large sessions (>200KB) hang on --resume, so start fresh with conversation summary
    session_file = Path.home() / ".claude" / "projects" / "-opt-tkk-vidgen" / f"{session_id}.jsonl"
    session_too_large = session_file.exists() and session_file.stat().st_size > 200_000

    if is_first:
        cmd.extend(["--session-id", session_id])
    elif session_too_large:
        # Build conversation summary from DB instead of resuming huge session
        with clips_db.db_session() as conn:
            rows = conn.execute(
                "SELECT role, content FROM studio_messages WHERE session_id = ? ORDER BY created_at",
                (session_id,),
            ).fetchall()
        summary_parts = []
        for r in rows:
            role = r["role"].upper()
            content = r["content"]
            # Truncate long assistant messages (they contain tool output)
            if len(content) > 500:
                content = content[:500] + "... [truncated]"
            summary_parts.append(f"{role}: {content}")
        conv_summary = "\n\n".join(summary_parts[-10:])  # last 10 messages
        system_prompt += f"\n\n## Prior conversation (session too large to resume directly):\n{conv_summary}"
        # Update the command with the expanded system prompt
        cmd = [CLAUDE_BIN, "-p", "--output-format", "stream-json", "--verbose",
               "--model", s["studio_model"], "--mcp-config", MCP_CONFIG,
               "--permission-mode", "bypassPermissions",
               "--max-budget-usd", s["studio_budget"],
               "--append-system-prompt", system_prompt]
        # Use a fresh session ID (so it doesn't conflict with the large one)
        new_sid = str(uuid.uuid4())
        cmd.extend(["--session-id", new_sid])
    else:
        cmd.extend(["--resume", session_id])

    # Initialize state and launch background thread
    with _studio_lock:
        _studio_state = {
            "session_id": session_id,
            "proc": None,
            "buffer": "",
            "status": "running",
            "started": time.time(),
            "last_activity": time.time(),
            "activities": [],
            "current_tool": None,
            "cost_usd": 0.0,
            "error": None,
        }

    thread = threading.Thread(target=_run_claude_bg, args=(session_id, cmd, message), daemon=True)
    thread.start()

    return {"status": "started"}


@app.get("/api/studio/sessions/{session_id}/poll")
async def poll_studio(session_id: str):
    """Poll for Claude's response status and content."""
    with _studio_lock:
        if _studio_state and _studio_state["session_id"] == session_id:
            status = _studio_state["status"]
            # Detect stalled process — no output for 60+ seconds while "running"
            if status == "running":
                idle_secs = time.time() - _studio_state.get("last_activity", _studio_state["started"])
                if idle_secs > 120:
                    status = "stalled"
                    _studio_state["error"] = f"No response for {int(idle_secs)}s — process may have hung"
            return {
                "status": status,
                "content": _studio_state["buffer"],
                "elapsed": int(time.time() - _studio_state["started"]),
                "activities": _studio_state["activities"][-20:],
                "current_tool": _studio_state["current_tool"],
                "cost_usd": _studio_state["cost_usd"],
                "error": _studio_state["error"],
            }

    # Not in memory — check DB for last assistant message
    with clips_db.db_session() as conn:
        row = conn.execute(
            "SELECT content, role FROM studio_messages WHERE session_id = ? ORDER BY created_at DESC LIMIT 1",
            (session_id,),
        ).fetchone()
        # Check if the last message is from the user (meaning assistant never responded)
        last_user = conn.execute(
            "SELECT content FROM studio_messages WHERE session_id = ? AND role = 'user' ORDER BY created_at DESC LIMIT 1",
            (session_id,),
        ).fetchone()
    if row and row["role"] == "assistant":
        return {"status": "done", "content": row["content"], "elapsed": 0,
                "activities": [], "current_tool": None, "cost_usd": 0, "error": None}
    if last_user and (not row or row["role"] != "assistant"):
        # User sent a message but no assistant response — process died
        return {"status": "error", "content": "", "elapsed": 0,
                "activities": [], "current_tool": None, "cost_usd": 0,
                "error": "Session ended unexpectedly. Send another message to retry."}
    return {"status": "idle", "content": "", "elapsed": 0,
            "activities": [], "current_tool": None, "cost_usd": 0, "error": None}


@app.post("/api/studio/sessions/{session_id}/stop")
async def stop_studio_session(session_id: str):
    """Stop a running claude process for a session."""
    global _studio_state
    with _studio_lock:
        if _studio_state and _studio_state["session_id"] == session_id:
            proc = _studio_state.get("proc")
            if proc and proc.poll() is None:
                proc.kill()
                _studio_state["status"] = "done"
                _studio_state["buffer"] += "\n\n[Stopped by user]"
                return {"stopped": True}
    return {"stopped": False, "reason": "No active process"}


@app.post("/api/screenplay/{filename}/short")
async def api_create_short(filename: str):
    """Create a ≤30s TikTok short from a rendered screenplay video."""
    filepath = VIDGEN_DIR / filename
    if not filepath.exists() or not filename.endswith(".py"):
        raise HTTPException(404, "Screenplay not found")

    stem = filename.replace("_manim.py", "").replace(".py", "")
    final_path = VIDGEN_DIR / f"{stem}_final.mp4"
    if not final_path.exists():
        raise HTTPException(400, "No rendered video found. Render the full video first.")

    # Try TTS timings sidecar first (most accurate)
    timings_file = VIDGEN_DIR / f"tts_{stem}_timings.json"
    if timings_file.exists():
        timings = json.loads(timings_file.read_text())
        scene_ends = [round(sum(timings["scene_durations"][:i+1]), 3)
                      for i in range(len(timings["scene_durations"]))]
    else:
        # Fall back to docstring parsing
        try:
            parsed = await api_screenplay_parsed(filename)
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(500, "Failed to parse screenplay for scene durations")

        scenes = parsed.get("scenes", [])
        if not scenes:
            raise HTTPException(400, "No scene data found in screenplay")

        durations = [s.get("duration", 0) for s in scenes]
        if not any(d > 0 for d in durations):
            raise HTTPException(400, "No scene duration data available")

        scene_ends = []
        cumulative = 0
        for d in durations:
            cumulative += d
            scene_ends.append(round(cumulative, 2))

    try:
        sys.path.insert(0, str(VIDGEN_DIR))
        from render_utils import make_short
        s = get_settings()
        short_path, duration = make_short(
            str(final_path), scene_ends,
            max_duration=float(s.get("short_max_duration", "30")),
            fade_dur=float(s.get("short_fade_duration", "1.5")),
        )
        return {"success": True, "short": Path(short_path).name, "duration": round(duration, 1)}
    except ValueError as e:
        raise HTTPException(400, str(e))
    except subprocess.CalledProcessError as e:
        raise HTTPException(500, f"FFmpeg failed: {e.stderr[:200] if e.stderr else 'unknown error'}")


# --- Intake (batch .md → screenplays pipeline) ---

_intake_lock = threading.Lock()
_intake_state: dict = {}  # batch_id -> {status, current_item, current_step, elapsed, error, proc}


def _update_batch_status(batch_id: str, status: str, error: str | None = None, video_count: int | None = None):
    with clips_db.db_session() as conn:
        if video_count is not None:
            conn.execute(
                "UPDATE intake_batches SET status=?, error=?, video_count=?, updated_at=datetime('now') WHERE id=?",
                (status, error, video_count, batch_id),
            )
        else:
            conn.execute(
                "UPDATE intake_batches SET status=?, error=?, updated_at=datetime('now') WHERE id=?",
                (status, error, batch_id),
            )


def _update_item_status(item_id: str, status: str, error: str | None = None, screenplay_file: str | None = None):
    with clips_db.db_session() as conn:
        if screenplay_file:
            conn.execute(
                "UPDATE intake_items SET status=?, error=?, screenplay_file=?, updated_at=datetime('now') WHERE id=?",
                (status, error, screenplay_file, item_id),
            )
        else:
            conn.execute(
                "UPDATE intake_items SET status=?, error=?, updated_at=datetime('now') WHERE id=?",
                (status, error, item_id),
            )


def _run_claude_step(prompt: str, use_mcp: bool = False, timeout: int = 300) -> str:
    """Run a fresh Claude -p session, return text output."""
    s = get_settings()
    cmd = [
        CLAUDE_BIN, "-p", "--output-format", "stream-json", "--verbose",
        "--model", s["studio_model"],
        "--permission-mode", "bypassPermissions",
        "--max-budget-usd", "3.00",
    ]
    if use_mcp:
        cmd.extend(["--mcp-config", MCP_CONFIG])
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        stdin=subprocess.PIPE, text=True, cwd=str(VIDGEN_DIR),
    )
    try:
        proc.stdin.write(prompt)
        proc.stdin.close()
    except Exception:
        pass

    # Store proc for cancellation
    result_text = ""
    for line in iter(proc.stdout.readline, ""):
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "assistant":
            for block in event.get("message", {}).get("content", []):
                if block.get("type") == "text":
                    result_text += block.get("text", "")
        elif event.get("type") == "result":
            r = event.get("result", "")
            if r and isinstance(r, str) and not result_text.strip():
                result_text = r
    proc.wait(timeout=timeout)
    if proc.returncode and proc.returncode != 0:
        err = ""
        try:
            err = proc.stderr.read()[-500:]
        except Exception:
            pass
        raise RuntimeError(f"Claude exited {proc.returncode}: {err}")
    return result_text.strip()


def _extract_json_from_text(text: str) -> str:
    """Strip markdown fences and extract JSON from Claude output."""
    # Try to find JSON array in the text
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r'^```\w*\n?', '', text)
        text = re.sub(r'\n?```$', '', text)
        text = text.strip()
    # Find first [ ... ] block
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
    return text


def _run_intake_batch(batch_id: str):
    """Background orchestrator: analyze .md, plan, write, TTS, preview, QA."""
    try:
        # Load batch info
        with clips_db.db_session() as conn:
            batch = dict(conn.execute("SELECT * FROM intake_batches WHERE id=?", (batch_id,)).fetchone())
        source_path = batch["source_file"]
        source_content = Path(source_path).read_text()

        # Check for cancellation
        def _is_cancelled():
            with _intake_lock:
                st = _intake_state.get(batch_id)
                return not st or st.get("cancelled")

        # --- STEP 1: ANALYZE ---
        with _intake_lock:
            _intake_state[batch_id] = {
                "status": "analyzing", "current_item": None,
                "current_step": "analyze", "started": time.time(),
                "error": None, "cancelled": False,
            }
        _update_batch_status(batch_id, "analyzing")

        analyze_prompt = f"""Analyze this research document and determine how many TikTok videos can be made from it.
Each video should cover a distinct, self-contained topic that can be told in 28-45 seconds.
Look for surprising facts, contradictions, betrayals, or mysteries — those make the best TikTok hooks.

Return a JSON array of objects, each with:
- "topic": a snake_case identifier (e.g. "bronze_age_collapse")
- "title": a short punchy title for the video
- "hook": the mystery/surprise angle in one sentence

Return ONLY the JSON array. No markdown fences, no explanation.

Document:
{source_content[:15000]}"""

        analyze_result = _run_claude_step(analyze_prompt, use_mcp=False, timeout=120)
        if _is_cancelled():
            return

        # Parse topics
        json_text = _extract_json_from_text(analyze_result)
        topics = json.loads(json_text)
        if not isinstance(topics, list) or len(topics) == 0:
            raise ValueError(f"Expected JSON array of topics, got: {analyze_result[:200]}")

        # Create items in DB
        _update_batch_status(batch_id, "planning", video_count=len(topics))
        with clips_db.db_session() as conn:
            for i, t in enumerate(topics):
                item_id = str(uuid.uuid4())
                conn.execute(
                    "INSERT INTO intake_items (id, batch_id, topic, title, sort_order) VALUES (?, ?, ?, ?, ?)",
                    (item_id, batch_id, t["topic"], t.get("title", t["topic"]), i),
                )

        if _is_cancelled():
            return

        # --- STEP 2: PLAN ALL ---
        with _intake_lock:
            st = _intake_state.get(batch_id)
            if st:
                st["status"] = "planning"
                st["current_step"] = "plan"
        _update_batch_status(batch_id, "planning")

        # Build a single Claude call that plans all videos
        topics_summary = "\n".join(f"- {t['topic']}: {t.get('title','')} — {t.get('hook','')}" for t in topics)
        plan_prompt = f"""You are a TikTok video producer. Read the production guide first (call read_production_guide),
then call plan_screenplay() for EACH of these topics. Use the source material below for factual content.

Topics to plan:
{topics_summary}

Source material (first 12000 chars):
{source_content[:12000]}

For each topic, call plan_screenplay with a complete creative brief following the mystery arc structure.
Include specific facts from the source material. Each plan needs real content for all 6 scenes."""

        _run_claude_step(plan_prompt, use_mcp=True, timeout=600)
        if _is_cancelled():
            return

        # --- STEPS 3-6: Per-video pipeline ---
        with clips_db.db_session() as conn:
            items = [dict(r) for r in conn.execute(
                "SELECT * FROM intake_items WHERE batch_id=? ORDER BY sort_order", (batch_id,)
            ).fetchall()]

        _update_batch_status(batch_id, "writing")

        for item in items:
            if _is_cancelled():
                return

            topic = item["topic"]
            item_id = item["id"]
            filename = f"{topic}_manim.py"

            # Skip items that are already past writing (for retries)
            if item["status"] in ("written", "tts", "previewed", "rendered", "complete"):
                continue

            # --- WRITE ---
            with _intake_lock:
                st = _intake_state.get(batch_id)
                if st:
                    st["status"] = "writing"
                    st["current_item"] = topic
                    st["current_step"] = "write"

            _update_item_status(item_id, "writing")

            try:
                write_prompt = f"""Write the screenplay for topic "{topic}".
First call get_plan("{topic}") to retrieve the plan, then call write_screenplay to create the file.
The screenplay MUST include TTS_SCRIPT with the full narration text.
Follow the production guide exactly. The filename should be {filename}."""

                _run_claude_step(write_prompt, use_mcp=True, timeout=600)

                # Verify the file was created
                sp_path = VIDGEN_DIR / filename
                if not sp_path.exists():
                    raise FileNotFoundError(f"{filename} was not created")

                # --- VALIDATE: syntax check + dry-import the screenplay ---
                venv_python = VIDGEN_DIR / ".venv" / "bin" / "python3"
                python_cmd = str(venv_python) if venv_python.exists() else "python3"
                val_result = subprocess.run(
                    [python_cmd, "-c", f"import py_compile; py_compile.compile({str(sp_path)!r}, doraise=True)"],
                    capture_output=True, text=True, timeout=15, cwd=str(VIDGEN_DIR),
                )
                if val_result.returncode != 0:
                    err_msg = val_result.stderr.strip().split('\n')[-1][:300] if val_result.stderr else "Syntax error"
                    # Ask Claude to fix the syntax error
                    fix_prompt = f"""The screenplay {filename} has a syntax error:
{val_result.stderr[:500]}

Fix the syntax error by calling write_screenplay with corrected code. Read the file first to see the full content."""
                    try:
                        _run_claude_step(fix_prompt, use_mcp=True, timeout=300)
                        # Re-check syntax after fix attempt
                        val2 = subprocess.run(
                            [python_cmd, "-c", f"import py_compile; py_compile.compile({str(sp_path)!r}, doraise=True)"],
                            capture_output=True, text=True, timeout=15, cwd=str(VIDGEN_DIR),
                        )
                        if val2.returncode != 0:
                            raise SyntaxError(f"Still has syntax errors after fix attempt: {val2.stderr[-200:]}")
                    except SyntaxError:
                        raise
                    except Exception:
                        raise SyntaxError(f"Syntax error in {filename}: {err_msg}")

                _update_item_status(item_id, "written", screenplay_file=filename)
            except Exception as e:
                _update_item_status(item_id, "error", error=str(e)[:500])
                continue

            if _is_cancelled():
                return

            # --- TTS ---
            with _intake_lock:
                st = _intake_state.get(batch_id)
                if st:
                    st["current_step"] = "tts"
            _update_batch_status(batch_id, "tts")

            try:
                venv_python = VIDGEN_DIR / ".venv" / "bin" / "python3"
                python_cmd = str(venv_python) if venv_python.exists() else "python3"
                tts_script = VIDGEN_DIR / "generate_tts.py"
                sp_path = VIDGEN_DIR / filename
                result = subprocess.run(
                    [python_cmd, str(tts_script), str(sp_path)],
                    capture_output=True, text=True, timeout=120, cwd=str(VIDGEN_DIR),
                )
                if result.returncode != 0:
                    _update_item_status(item_id, "error", error=f"TTS failed: {result.stderr[:300]}")
                    continue
                _update_item_status(item_id, "tts")
            except Exception as e:
                _update_item_status(item_id, "error", error=f"TTS error: {str(e)[:300]}")
                continue

            if _is_cancelled():
                return

            # --- PREVIEW (with auto-fix retry) ---
            with _intake_lock:
                st = _intake_state.get(batch_id)
                if st:
                    st["current_step"] = "preview"
            _update_batch_status(batch_id, "previewing")

            preview_ok = False
            last_err = ""
            for _attempt in range(2):  # Try once, then fix + retry
                try:
                    sp_path = VIDGEN_DIR / filename
                    result = subprocess.run(
                        ["python3", str(sp_path), "--preview"],
                        capture_output=True, text=True, timeout=180, cwd=str(VIDGEN_DIR),
                    )
                    if result.returncode == 0:
                        scene_pngs = sorted((VIDGEN_DIR / "previews").glob(f"{topic}_scene_*.png"))
                        if len(scene_pngs) >= 1:
                            preview_ok = True
                            break
                        last_err = "Preview exited OK but produced no scene PNGs"
                    else:
                        last_err = (result.stderr or result.stdout or "")[-500:]
                except subprocess.TimeoutExpired:
                    last_err = "Preview timed out after 180s"
                except Exception as e:
                    last_err = str(e)[:500]

                # First failure: ask Claude to fix the Manim code, then retry
                if _attempt == 0:
                    try:
                        fix_prompt = f"""The screenplay {filename} failed during Manim preview rendering.

Error output:
{last_err}

Read the file, diagnose the Manim error, and fix it using write_screenplay.
Common issues:
- VGroup() only accepts VMobject — use Group() for mixed mobject types
- FadeOut(VGroup(*self.mobjects[2:])) fails when LaggedStart leaves Group objects — use FadeOut(Group(*self.mobjects[2:])) instead
- Don't call run_preview_qa() from inside --preview (it scans all previews and times out)
- Make sure all mobjects are properly constructed before animating"""
                        _run_claude_step(fix_prompt, use_mcp=True, timeout=300)
                    except Exception:
                        pass

            if not preview_ok:
                _update_item_status(item_id, "error", error=f"Preview failed after auto-fix: {last_err[:300]}")
                continue

            # --- QA ---
            try:
                stem = topic
                preview_dir = VIDGEN_DIR / "previews"
                previews = sorted(preview_dir.glob(f"{stem}_scene_*.png"))
                if previews:
                    qa_script = VIDGEN_DIR / "qa_layout.py"
                    if qa_script.exists():
                        subprocess.run(
                            ["python3", str(qa_script), str(preview_dir), "--json"],
                            capture_output=True, text=True, timeout=60, cwd=str(VIDGEN_DIR),
                        )
            except Exception:
                pass  # QA is non-blocking

            _update_item_status(item_id, "previewed")

            if _is_cancelled():
                return

            # --- FULL RENDER ---
            with _intake_lock:
                st = _intake_state.get(batch_id)
                if st:
                    st["current_step"] = "render"
            _update_batch_status(batch_id, "rendering")

            try:
                s = get_settings()
                render_env = {
                    **os.environ,
                    "TKK_RENDER_CRF": s.get("render_crf", "23"),
                    "TKK_RENDER_PRESET": s.get("render_preset", "fast"),
                    "TKK_SILENCE_THRESHOLD_DB": s.get("silence_threshold_db", "-30"),
                    "TKK_SILENCE_MIN_DURATION": s.get("silence_min_duration", "0.3"),
                    "TKK_SHORT_MAX_DURATION": s.get("short_max_duration", "30"),
                    "TKK_SHORT_FADE_DURATION": s.get("short_fade_duration", "1.5"),
                    "TKK_FISH_BITRATE": s.get("fish_bitrate", "192"),
                }
                sp_path = VIDGEN_DIR / filename
                result = subprocess.run(
                    ["python3", str(sp_path)],
                    capture_output=True, text=True, timeout=600, cwd=str(VIDGEN_DIR),
                    env=render_env,
                )
                if result.returncode != 0:
                    _update_item_status(item_id, "error", error=f"Render failed: {result.stderr[-300:]}")
                    continue
                _update_item_status(item_id, "rendered")

                # Auto-generate short
                try:
                    timings_file = VIDGEN_DIR / f"tts_{topic}_timings.json"
                    final_path = VIDGEN_DIR / f"{topic}_final.mp4"
                    if timings_file.exists() and final_path.exists():
                        timings_data = json.loads(timings_file.read_text())
                        scene_ends = [round(sum(timings_data["scene_durations"][:i+1]), 3)
                                      for i in range(len(timings_data["scene_durations"]))]
                        sys.path.insert(0, str(VIDGEN_DIR))
                        from render_utils import make_short
                        make_short(str(final_path), scene_ends,
                                   max_duration=float(s.get("short_max_duration", "30")),
                                   fade_dur=float(s.get("short_fade_duration", "1.5")))
                except Exception:
                    pass  # Short generation is optional

            except subprocess.TimeoutExpired:
                _update_item_status(item_id, "error", error="Render timed out after 10 minutes")
                continue
            except Exception as e:
                _update_item_status(item_id, "error", error=f"Render error: {str(e)[:300]}")
                continue

            if _is_cancelled():
                return

            # --- METADATA GENERATION ---
            with _intake_lock:
                st = _intake_state.get(batch_id)
                if st:
                    st["current_step"] = "meta"
            _update_batch_status(batch_id, "metadata")

            video_filename = f"{topic}_final.mp4"
            if (VIDGEN_DIR / video_filename).exists():
                try:
                    base = re.sub(r'_(v\d+|final|render|output|s\d+.*)$', '', topic)
                    _run_meta_gen(video_filename, base)
                    _update_item_status(item_id, "complete")
                except Exception as e:
                    # Meta failure is non-blocking — video is still usable
                    _update_item_status(item_id, "complete")
            else:
                _update_item_status(item_id, "complete")

        # --- DONE ---
        _update_batch_status(batch_id, "done")
        with _intake_lock:
            st = _intake_state.get(batch_id)
            if st:
                st["status"] = "done"
                st["current_step"] = None
                st["current_item"] = None

    except Exception as e:
        _update_batch_status(batch_id, "error", error=str(e)[:500])
        with _intake_lock:
            st = _intake_state.get(batch_id)
            if st:
                st["status"] = "error"
                st["error"] = str(e)[:500]
    finally:
        # Clean up state after a delay so polling can see final status
        def _cleanup():
            time.sleep(30)
            with _intake_lock:
                st = _intake_state.get(batch_id)
                if st and st["status"] in ("done", "error"):
                    del _intake_state[batch_id]
        threading.Thread(target=_cleanup, daemon=True).start()


@app.get("/intake", response_class=HTMLResponse)
async def intake_page(request: Request):
    return templates.TemplateResponse("intake.html", {"request": request})


@app.post("/api/intake/upload")
async def api_intake_upload(request: Request):
    """Upload .md file, create batch, start orchestrator."""
    form = await request.form()
    file = form.get("file")
    if not file:
        raise HTTPException(400, "No file provided")
    safe_name = re.sub(r'[^\w\-.]', '_', file.filename)[:200]
    dest = UPLOADS_DIR / safe_name
    content = await file.read()
    dest.write_bytes(content)

    batch_id = str(uuid.uuid4())
    batch_name = safe_name.replace('.md', '').replace('_', ' ').title()
    with clips_db.db_session() as conn:
        conn.execute(
            "INSERT INTO intake_batches (id, name, source_file, status) VALUES (?, ?, ?, 'uploaded')",
            (batch_id, batch_name, str(dest)),
        )

    thread = threading.Thread(target=_run_intake_batch, args=(batch_id,), daemon=True)
    thread.start()
    return {"batch_id": batch_id, "name": batch_name, "status": "uploaded"}


@app.get("/api/intake/batches")
async def api_intake_batches():
    """List all batches with their items."""
    with clips_db.db_session() as conn:
        batches = [dict(r) for r in conn.execute(
            "SELECT * FROM intake_batches ORDER BY created_at DESC"
        ).fetchall()]
        for batch in batches:
            batch["items"] = [dict(r) for r in conn.execute(
                "SELECT * FROM intake_items WHERE batch_id=? ORDER BY sort_order",
                (batch["id"],)
            ).fetchall()]
    return {"batches": batches}


@app.get("/api/intake/batches/{batch_id}/poll")
async def api_intake_poll(batch_id: str):
    """Poll for live progress on a batch."""
    with _intake_lock:
        st = _intake_state.get(batch_id)
        if st:
            return {
                "status": st["status"],
                "current_item": st.get("current_item"),
                "current_step": st.get("current_step"),
                "elapsed": int(time.time() - st["started"]),
                "error": st.get("error"),
                "live": True,
            }
    # Fall back to DB
    with clips_db.db_session() as conn:
        batch = conn.execute("SELECT * FROM intake_batches WHERE id=?", (batch_id,)).fetchone()
        if not batch:
            raise HTTPException(404, "Batch not found")
        items = [dict(r) for r in conn.execute(
            "SELECT * FROM intake_items WHERE batch_id=? ORDER BY sort_order", (batch_id,)
        ).fetchall()]
    return {
        "status": dict(batch)["status"],
        "current_item": None,
        "current_step": None,
        "elapsed": 0,
        "error": dict(batch).get("error"),
        "live": False,
        "items": items,
    }


@app.post("/api/intake/batches/{batch_id}/stop")
async def api_intake_stop(batch_id: str):
    """Cancel a running batch."""
    with _intake_lock:
        st = _intake_state.get(batch_id)
        if st:
            st["cancelled"] = True
            st["status"] = "error"
            st["error"] = "Stopped by user"
    _update_batch_status(batch_id, "error", error="Stopped by user")
    return {"stopped": True}


@app.post("/api/intake/batches/{batch_id}/retry")
async def api_intake_retry(batch_id: str):
    """Resume a batch from where it left off (re-run errored items)."""
    with _intake_lock:
        if batch_id in _intake_state:
            return JSONResponse({"error": "Batch is already running"}, status_code=409)

    # Reset errored items to planned
    with clips_db.db_session() as conn:
        batch = conn.execute("SELECT * FROM intake_batches WHERE id=?", (batch_id,)).fetchone()
        if not batch:
            raise HTTPException(404, "Batch not found")
        conn.execute(
            "UPDATE intake_items SET status='planned', error=NULL WHERE batch_id=? AND status='error'",
            (batch_id,),
        )
        conn.execute(
            "UPDATE intake_batches SET status='writing', error=NULL, updated_at=datetime('now') WHERE id=?",
            (batch_id,),
        )

    thread = threading.Thread(target=_run_intake_batch, args=(batch_id,), daemon=True)
    thread.start()
    return {"retrying": True}


@app.delete("/api/intake/batches/{batch_id}")
async def api_intake_delete(batch_id: str):
    """Delete a batch and its items."""
    with _intake_lock:
        st = _intake_state.get(batch_id)
        if st:
            st["cancelled"] = True
    with clips_db.db_session() as conn:
        conn.execute("DELETE FROM intake_items WHERE batch_id=?", (batch_id,))
        conn.execute("DELETE FROM intake_batches WHERE id=?", (batch_id,))
    return {"deleted": batch_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8020)
