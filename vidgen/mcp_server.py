#!/usr/bin/env python3
"""TKK Video Pipeline MCP Server.

Exposes the TKK video production pipeline as MCP tools that Claude Code
can call. Handles: screenplay management, TTS generation (Fish Audio),
preview/full rendering, and QA checks.

Usage:
    # Register with Claude Code (one-time):
    claude mcp add tkk-studio /opt/tkk/vidgen/.venv/bin/python3 /opt/tkk/vidgen/mcp_server.py

    # Then in any claude session:
    "List all screenplays and their status"
    "Generate TTS for bronze_age.json"
    "Render previews for tunguska.json and run QA"
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

from mcp.server import FastMCP

# Ensure we can import vidgen modules
VIDGEN_DIR = Path("/opt/tkk/vidgen")
sys.path.insert(0, str(VIDGEN_DIR))

# Load .env
env_path = Path("/opt/tkk/.env")
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

VENV_PYTHON = str(VIDGEN_DIR / ".venv" / "bin" / "python3")

SETTINGS_PATH = Path("/opt/tkk/clips/settings.json")

def _get_settings() -> dict:
    """Read clips settings.json for passing to subprocesses."""
    if SETTINGS_PATH.exists():
        try:
            return json.loads(SETTINGS_PATH.read_text())
        except Exception:
            pass
    return {}

def _render_env() -> dict:
    """Build env dict with TKK_ settings for render/TTS subprocesses."""
    s = _get_settings()
    return {
        **os.environ,
        "TKK_RENDER_CRF": s.get("render_crf", "23"),
        "TKK_RENDER_PRESET": s.get("render_preset", "fast"),
        "TKK_SILENCE_THRESHOLD_DB": s.get("silence_threshold_db", "-30"),
        "TKK_SILENCE_MIN_DURATION": s.get("silence_min_duration", "0.3"),
        "TKK_SHORT_MAX_DURATION": s.get("short_max_duration", "30"),
        "TKK_SHORT_FADE_DURATION": s.get("short_fade_duration", "1.5"),
        "TKK_FISH_BITRATE": s.get("fish_bitrate", "192"),
        "FISH_AUDIO_VOICE_ID": s.get("fish_voice_id", "dc74574cfe664e93bd4179fe28542524"),
    }

mcp = FastMCP("tkk-studio", instructions="""TKK Video Production Pipeline.

You help produce TikTok educational videos using **Remotion** (React/TypeScript).

Manifests live at remotion/src/manifests/{topic}.json. Two formats:
- **Word-triggered (preferred)**: scenes declare anchor words from narration. resolve_word_triggers.py
  computes exact frame timing from Whisper data. Workflow:
  write_remotion_manifest() → generate_tts() → resolve_word_triggers() → audit_word_triggered() → render_preview() → render_full()
- **Legacy**: type-based scenes with derive_timings.py heuristics. Workflow:
  write_remotion_manifest() → generate_tts() → render_preview() → render_full()

Word-triggered manifests have `scene_anchor` and `scene_end_anchor` on each scene, plus `anchor` on each element.
generate_tts() auto-detects the format and runs the appropriate resolver.

Use list_screenplays() to see all manifests and their status.

REMOTION DESIGN RULES (from remotion/REMOTION_DESIGN_GUIDE.md):
- Font sizes must be 3-4× web defaults: hero stats 160-220px, headlines 80-120px, body 40-56px minimum
- Safe zones: top 200px, bottom 400px, right 140px, left 120px (platform UI overlays)
- Full-height layout: content MUST fill the vertical frame, use zone-based distribution
- Animations: use spring() + useCurrentFrame() only, never CSS transitions
- Manifests: agent picks from enums (beat types, layout variants, animation presets), never writes CSS
- Audio-first timing: no frame numbers in manifests, derive all timing from TTS audio duration
- Layered backgrounds: gradient + noise texture + vignette + content (not flat backgrounds)

IMPORTANT: Always use Fish Audio for TTS (it's the default).
Read the PRODUCTION_GUIDE with read_production_guide before writing manifests.
""")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _screenplay_status(py_file: Path) -> dict:
    """Get status of a screenplay file."""
    stem = py_file.stem.replace("_manim", "")
    return {
        "filename": py_file.name,
        "topic": stem,
        "has_tts": (VIDGEN_DIR / f"tts_{stem}.mp3").exists(),
        "has_final": (VIDGEN_DIR / f"{stem}_final.mp4").exists(),
        "has_previews": any((VIDGEN_DIR / "previews").glob(f"{stem}_scene_*.png"))
            if (VIDGEN_DIR / "previews").exists() else False,
        "size_kb": py_file.stat().st_size // 1024,
    }


def _ffprobe_duration(filepath: Path) -> float | None:
    """Get duration of audio/video file."""
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(filepath)],
            capture_output=True, text=True, timeout=10,
        )
        return float(r.stdout.strip())
    except Exception:
        return None


def _extract_tts_script(content: str) -> str:
    """Extract TTS_SCRIPT from screenplay source."""
    match = re.search(r'TTS_SCRIPT\s*=\s*"""(.*?)"""', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"TTS_SCRIPT\s*=\s*'''(.*?)'''", content, re.DOTALL)
    if match:
        return match.group(1).strip()
    # VTT cue lines from docstring
    vtt_lines = re.findall(r'\d+\.\d+\s+\(\d+\.\d+\)\s+(.+)', content)
    if vtt_lines:
        return "\n".join(vtt_lines)
    return ""


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def list_screenplays() -> str:
    """List all screenplays (Remotion manifests) with production status."""
    results = []

    manifest_dir = VIDGEN_DIR / "remotion" / "src" / "manifests"
    if manifest_dir.exists():
        for m in sorted(manifest_dir.glob("*.json")):
            stem = m.stem
            try:
                mdata = json.loads(m.read_text())
                is_wt = bool(mdata.get("scenes") and "scene_anchor" in mdata["scenes"][0])
            except Exception:
                is_wt = False
            entry = {
                "filename": m.name,
                "topic": stem,
                "engine": "remotion",
                "format": "word-triggered" if is_wt else "legacy",
                "has_tts": (VIDGEN_DIR / f"tts_{stem}.mp3").exists(),
                "has_final": (VIDGEN_DIR / f"{stem}_final.mp4").exists(),
                "has_previews": any((VIDGEN_DIR / "previews").glob(f"{stem}_scene_*.png"))
                    if (VIDGEN_DIR / "previews").exists() else False,
                "size_kb": m.stat().st_size // 1024,
            }
            if is_wt:
                entry["has_resolved"] = (VIDGEN_DIR / f"{stem}_resolved.json").exists()
            results.append(entry)

    return json.dumps(results, indent=2)


@mcp.tool()
def read_screenplay(filename: str) -> str:
    """Read a screenplay file's source code and extracted metadata.

    Args:
        filename: The screenplay filename (e.g., "aral_sea.json")
    """
    fp = VIDGEN_DIR / filename
    if not fp.exists():
        return f"Error: {filename} not found in {VIDGEN_DIR}"

    content = fp.read_text()
    tts_script = _extract_tts_script(content)
    scene_classes = re.findall(r'^class\s+(Scene\d+_\w+)', content, re.MULTILINE)

    meta = {
        "filename": filename,
        "lines": content.count("\n") + 1,
        "scene_count": len(scene_classes),
        "scene_classes": scene_classes,
        "has_tts_script": bool(tts_script),
        "tts_script_preview": tts_script[:300] + "..." if len(tts_script) > 300 else tts_script,
        "status": _screenplay_status(fp),
    }

    return f"=== Metadata ===\n{json.dumps(meta, indent=2)}\n\n=== Source ===\n{content}"


@mcp.tool()
def read_production_guide() -> str:
    """Read the TKK Production Guide — required reading before writing screenplays."""
    guide = VIDGEN_DIR / "PRODUCTION_GUIDE.md"
    if not guide.exists():
        return "Error: PRODUCTION_GUIDE.md not found"
    return guide.read_text()


@mcp.tool()
def generate_tts(filename: str) -> str:
    """Generate TTS audio for a manifest using Fish Audio.

    This is the ONLY approved TTS method. Do not use edge-tts, kokoro, or piper.
    Voice is configured in Settings (default: ELITE).

    Args:
        filename: The manifest filename (e.g., "aral_sea.json")
    """
    fp = VIDGEN_DIR / filename
    if not fp.exists():
        return f"Error: {filename} not found"

    env = _render_env()
    voice_id = env.get("FISH_AUDIO_VOICE_ID", "dc74574cfe664e93bd4179fe28542524")
    cmd = [VENV_PYTHON, str(VIDGEN_DIR / "generate_tts.py"), str(fp),
           "--voice", voice_id]

    r = subprocess.run(
        cmd,
        capture_output=True, text=True, timeout=120, cwd=str(VIDGEN_DIR),
        env=env,
    )

    output = r.stdout + r.stderr
    if r.returncode != 0:
        return f"TTS generation failed (rc={r.returncode}):\n{output[-500:]}"

    # Find the output file
    stem = fp.stem.replace("_manim", "")
    tts_path = VIDGEN_DIR / f"tts_{stem}.mp3"
    if tts_path.exists():
        duration = _ffprobe_duration(tts_path)
        size_kb = tts_path.stat().st_size // 1024
        parts = [f"TTS generated: {tts_path.name} ({size_kb} KB, {duration:.1f}s)"]

        # Auto-derive timings for Remotion manifests
        if fp.suffix == '.json':
            manifest_data = json.loads(fp.read_text())
            is_wt = bool(manifest_data.get("scenes") and "scene_anchor" in manifest_data["scenes"][0])
            whisper_json = VIDGEN_DIR / f"tts_{stem}.mp3.json"

            if is_wt and whisper_json.exists():
                try:
                    from resolve_word_triggers import resolve_word_triggers as _resolve
                    resolved = _resolve(str(fp), str(whisper_json))
                    if resolved:
                        parts.append(f"Word triggers resolved: {Path(resolved).name}")
                except Exception as e:
                    parts.append(f"Word-trigger resolution failed: {e}")
            elif whisper_json.exists():
                try:
                    from derive_timings import derive_timings as _derive
                    timings_path = _derive(str(fp), str(whisper_json))
                    if timings_path:
                        parts.append(f"Timings derived: {Path(timings_path).name}")
                except Exception as e:
                    parts.append(f"Timing derivation failed: {e}")

        parts.append(f"\n{output}")
        return "\n".join(parts)

    return f"TTS generation completed but output file not found.\n\n{output}"


@mcp.tool()
def render_preview(filename: str) -> str:
    """Render preview PNGs for a manifest's scenes. Fast (~10s).

    Args:
        filename: The manifest filename (e.g., "aral_sea.json")
    """
    fp = VIDGEN_DIR / filename
    if not fp.exists():
        return f"Error: {filename} not found"

    stem = fp.stem.replace("_manim", "")
    cmd = ["npx", "tsx", "remotion/preview.mts", stem]
    r = subprocess.run(
        cmd,
        capture_output=True, text=True, timeout=300, cwd=str(VIDGEN_DIR),
    )

    output = r.stdout + r.stderr
    if r.returncode != 0:
        return f"Preview render failed (rc={r.returncode}):\n{output[-1000:]}"

    # List generated preview files
    previews = sorted((VIDGEN_DIR / "previews").glob(f"{stem}_scene_*.png"))
    preview_list = "\n".join(f"  {p.name} ({p.stat().st_size // 1024} KB)" for p in previews)

    return f"Previews rendered: {len(previews)} scenes\n{preview_list}\n\n{output[-500:]}"


@mcp.tool()
def render_full(filename: str) -> str:
    """Full render: manifest → final MP4. Takes 1-2 minutes.

    Uses render_remote.sh (tries llama → juno → local fallback).

    Args:
        filename: The manifest filename (e.g., "aral_sea.json")
    """
    fp = VIDGEN_DIR / filename
    if not fp.exists():
        return f"Error: {filename} not found"

    stem = fp.stem.replace("_manim", "")
    cmd = ["bash", str(VIDGEN_DIR / "render_remote.sh"), stem]
    r = subprocess.run(
        cmd,
        capture_output=True, text=True, timeout=600, cwd=str(VIDGEN_DIR),
        env=_render_env(),
    )

    output = r.stdout + r.stderr
    if r.returncode != 0:
        return f"Full render failed (rc={r.returncode}):\n{output[-1500:]}"

    # Find the final file
    final = VIDGEN_DIR / f"{stem}_final.mp4"
    if final.exists():
        duration = _ffprobe_duration(final)
        size_mb = final.stat().st_size / 1024 / 1024
        return (f"Render complete: {final.name} ({size_mb:.1f} MB, {duration:.1f}s)\n\n"
                f"{output[-500:]}")

    return f"Render completed but final MP4 not found.\n\n{output[-1000:]}"


@mcp.tool()
def run_qa(filename: str) -> str:
    """Run all QA checks on a manifest. Returns unified PASS/WARN/FAIL report.

    Runs manifest validation, layout QA, sync checks, and format-specific audits.

    Args:
        filename: The manifest filename (e.g., "aral_sea.json")
    """
    fp = VIDGEN_DIR / filename
    if not fp.exists():
        return f"Error: {filename} not found"

    stem = fp.stem.replace("_manim", "")

    try:
        from qa_all import run_all_qa, format_report
        result = run_all_qa(stem)
        return format_report(result)
    except Exception as e:
        return f"QA error: {e}"


@mcp.tool()
def list_videos() -> str:
    """List all final rendered videos with metadata."""
    videos = sorted(VIDGEN_DIR.glob("*_final.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
    results = []
    for v in videos:
        duration = _ffprobe_duration(v)
        results.append({
            "filename": v.name,
            "size_mb": round(v.stat().st_size / 1024 / 1024, 1),
            "duration": round(duration, 1) if duration else None,
            "date": v.stat().st_mtime,
        })
    return json.dumps(results, indent=2)


@mcp.tool()
def get_queue() -> str:
    """Read the current production queue (QUEUE.md)."""
    queue_path = Path("/opt/tkk/workspaces/QUEUE.md")
    if not queue_path.exists():
        return "No QUEUE.md found"
    return queue_path.read_text()


@mcp.tool()
def update_queue(task_description: str, new_status: str) -> str:
    """Update a task's status in QUEUE.md.

    Args:
        task_description: Part of the task text to match (e.g., "aztec")
        new_status: New status — "active", "done", or "remove"
    """
    queue_path = Path("/opt/tkk/workspaces/QUEUE.md")
    if not queue_path.exists():
        return "No QUEUE.md found"

    content = queue_path.read_text()

    if new_status == "done":
        # Mark checkbox as done
        pattern = rf'(- \[ \] .+{re.escape(task_description)}.+)'
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            old_line = match.group(1)
            new_line = old_line.replace("- [ ]", "- [x]")
            content = content.replace(old_line, new_line)
            queue_path.write_text(content)
            return f"Marked as done: {new_line.strip()}"
        return f"No pending task matching '{task_description}' found"

    return f"Status '{new_status}' not yet implemented. Use 'done' to mark tasks complete."


# ---------------------------------------------------------------------------
# Management / QoL Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def pipeline_status() -> str:
    """Get structured status of all manifests: which have TTS, previews, final MP4, and QA results."""
    manifest_dir = VIDGEN_DIR / "remotion" / "src" / "manifests"
    results = []
    if manifest_dir.exists():
        for m in sorted(manifest_dir.glob("*.json")):
            stem = m.stem
            info = {
                "filename": m.name,
                "topic": stem,
                "has_tts": (VIDGEN_DIR / f"tts_{stem}.mp3").exists(),
                "has_final": (VIDGEN_DIR / f"{stem}_final.mp4").exists(),
                "has_previews": any((VIDGEN_DIR / "previews").glob(f"{stem}_scene_*.png"))
                    if (VIDGEN_DIR / "previews").exists() else False,
                "size_kb": m.stat().st_size // 1024,
            }
            tts_path = VIDGEN_DIR / f"tts_{stem}.mp3"
            if tts_path.exists():
                info["tts_duration"] = _ffprobe_duration(tts_path)
            final_path = VIDGEN_DIR / f"{stem}_final.mp4"
            if final_path.exists():
                info["final_size_mb"] = round(final_path.stat().st_size / 1024 / 1024, 1)
                info["final_duration"] = _ffprobe_duration(final_path)
            results.append(info)
    return json.dumps(results, indent=2)


@mcp.tool()
def save_video_metadata(filename: str, title: str, description: str, tags: str) -> str:
    """Save title/description/tags for a video to video_metadata.json.

    Args:
        filename: The video filename (e.g., "superbug_clock_final.mp4")
        title: TikTok-ready title
        description: TikTok-ready description
        tags: Comma-separated tags (e.g., "science,antibiotics,health")
    """
    meta_path = VIDGEN_DIR / "video_metadata.json"
    data = {}
    if meta_path.exists():
        try:
            data = json.loads(meta_path.read_text())
        except json.JSONDecodeError:
            data = {}

    data[filename] = {
        "title": title,
        "description": description,
        "tags": [t.strip() for t in tags.split(",")],
    }

    meta_path.write_text(json.dumps(data, indent=2))
    return f"Saved metadata for {filename}: title={title!r}, {len(data[filename]['tags'])} tags"


@mcp.tool()
def get_video_metadata(filename: str) -> str:
    """Read title/description/tags for a video. Returns empty if none saved.

    Args:
        filename: The video filename (e.g., "superbug_clock_final.mp4")
    """
    meta_path = VIDGEN_DIR / "video_metadata.json"
    if not meta_path.exists():
        return json.dumps({})
    try:
        data = json.loads(meta_path.read_text())
    except json.JSONDecodeError:
        return json.dumps({})
    return json.dumps(data.get(filename, {}), indent=2)


@mcp.tool()
def list_uploads() -> str:
    """List all uploaded research files with name, size, and date."""
    uploads_dir = Path("/opt/tkk/clips/uploads")
    if not uploads_dir.exists():
        return json.dumps({"error": "uploads directory does not exist", "files": []})
    files = []
    for f in sorted(uploads_dir.iterdir()):
        if f.is_file():
            stat = f.stat()
            files.append({
                "name": f.name,
                "size_kb": round(stat.st_size / 1024, 1),
                "modified": stat.st_mtime,
            })
    return json.dumps(files, indent=2)


@mcp.tool()
def search_screenplays(query: str) -> str:
    """Search all Remotion manifests for a keyword. Returns matching filenames and context.

    Args:
        query: Search term (case-insensitive)
    """
    manifest_dir = VIDGEN_DIR / "remotion" / "src" / "manifests"
    results = []
    if manifest_dir.exists():
        for m in sorted(manifest_dir.glob("*.json")):
            content = m.read_text()
            lines = content.splitlines()
            matches = []
            for i, line in enumerate(lines):
                if query.lower() in line.lower():
                    matches.append({"line": i + 1, "text": line.strip()})
                    if len(matches) >= 5:
                        break
            if matches:
                results.append({"filename": m.name, "matches": matches})
    if not results:
        return f"No manifests contain '{query}'"
    return json.dumps(results, indent=2)


@mcp.tool()
def production_stats() -> str:
    """Get production statistics: total videos, total duration, manifests by status, recent renders."""
    manifest_dir = VIDGEN_DIR / "remotion" / "src" / "manifests"
    manifests = sorted(manifest_dir.glob("*.json")) if manifest_dir.exists() else []
    finals = sorted(VIDGEN_DIR.glob("*_final.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)

    total_duration = 0.0
    total_size_mb = 0.0
    for v in finals:
        d = _ffprobe_duration(v)
        if d:
            total_duration += d
        total_size_mb += v.stat().st_size / 1024 / 1024

    has_tts = sum(1 for m in manifests if (VIDGEN_DIR / f"tts_{m.stem}.mp3").exists())
    has_final = len(finals)

    recent = []
    for v in finals[:5]:
        d = _ffprobe_duration(v)
        recent.append({
            "filename": v.name,
            "duration": round(d, 1) if d else None,
            "date": v.stat().st_mtime,
        })

    stats = {
        "total_manifests": len(manifests),
        "with_tts": has_tts,
        "with_final": has_final,
        "needs_tts": len(manifests) - has_tts,
        "needs_render": has_tts - has_final,
        "total_duration_s": round(total_duration, 1),
        "total_duration_min": round(total_duration / 60, 1),
        "total_size_mb": round(total_size_mb, 1),
        "avg_duration_s": round(total_duration / len(finals), 1) if finals else 0,
        "recent_renders": recent,
    }
    return json.dumps(stats, indent=2)


@mcp.tool()
def batch_check(filenames: str) -> str:
    """Check pipeline status for specific manifests (comma-separated filenames).

    Args:
        filenames: Comma-separated manifest filenames (e.g., "antibiotics.json,chernobyl.json")
    """
    names = [f.strip() for f in filenames.split(",") if f.strip()]
    results = []
    for name in names:
        fp = VIDGEN_DIR / name
        if not fp.exists():
            results.append({"filename": name, "error": "not found"})
        else:
            info = _screenplay_status(fp)
            stem = fp.stem.replace("_manim", "")
            tts_path = VIDGEN_DIR / f"tts_{stem}.mp3"
            if tts_path.exists():
                info["tts_duration"] = _ffprobe_duration(tts_path)
            final_path = VIDGEN_DIR / f"{stem}_final.mp4"
            if final_path.exists():
                info["final_size_mb"] = round(final_path.stat().st_size / 1024 / 1024, 1)
                info["final_duration"] = _ffprobe_duration(final_path)
            results.append(info)
    return json.dumps(results, indent=2)


# ---------------------------------------------------------------------------
# TTS Audit & Enhancement Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def audit_tts(filename: str = None) -> str:
    """Audit TTS script word counts and durations against the 70-word target.

    At 150 WPM (Fish Audio ELITE):
      - Target: 70 words = ~28s
      - WARN: >80 words
      - FAIL: >90 words

    Args:
        filename: Optional manifest filename for detailed single-file audit.
                  If None, audits all manifests and returns fleet summary.
    """
    from audit_tts import audit_one, audit_all, suggest_cuts

    if filename:
        fp = VIDGEN_DIR / filename
        if not fp.exists():
            return f"Error: {filename} not found"
        result = audit_one(fp)
        # Add cut suggestions
        cuts = suggest_cuts(result["tts_script"])
        # Remove raw script from output (too long for MCP)
        out = {k: v for k, v in result.items() if k != "tts_script"}
        out["suggest_cuts"] = cuts
        return json.dumps(out, indent=2)
    else:
        results = audit_all()
        # Strip tts_script from each result
        out = [{k: v for k, v in r.items() if k != "tts_script"} for r in results]

        # Add fleet summary
        total = len(out)
        ok = sum(1 for r in out if r["status"] == "OK")
        warn = sum(1 for r in out if r["status"] == "WARN")
        fail = sum(1 for r in out if r["status"] == "FAIL")
        avg = sum(r["word_count"] for r in out) / max(total, 1)

        summary = {
            "fleet_summary": {
                "total": total, "ok": ok, "warn": warn, "fail": fail,
                "avg_words": round(avg, 1),
                "target_words": 70, "wpm": 150,
            },
            "manifests": out,
        }
        return json.dumps(summary, indent=2)


# ---------------------------------------------------------------------------
# Remotion Tools
# ---------------------------------------------------------------------------

REMOTION_MANIFESTS_DIR = VIDGEN_DIR / "remotion" / "src" / "manifests"


@mcp.tool()
def list_remotion_manifests() -> str:
    """List Remotion JSON manifests with their production status (has TTS, has final MP4)."""
    if not REMOTION_MANIFESTS_DIR.exists():
        return json.dumps({"error": "No remotion/src/manifests/ directory", "manifests": []})
    manifests = sorted(REMOTION_MANIFESTS_DIR.glob("*.json"))
    results = []
    for m in manifests:
        stem = m.stem
        results.append({
            "filename": m.name,
            "topic": stem,
            "has_tts": (VIDGEN_DIR / f"tts_{stem}.mp3").exists(),
            "has_final": (VIDGEN_DIR / f"{stem}_final.mp4").exists(),
            "has_previews": any((VIDGEN_DIR / "previews").glob(f"{stem}_scene_*.png"))
                if (VIDGEN_DIR / "previews").exists() else False,
            "size_kb": m.stat().st_size // 1024,
        })
    return json.dumps(results, indent=2)


@mcp.tool()
def read_remotion_manifest(topic: str) -> str:
    """Read a Remotion manifest JSON file.

    Args:
        topic: Topic slug (e.g., "aral_sea") — reads remotion/src/manifests/{topic}.json
    """
    manifest_path = REMOTION_MANIFESTS_DIR / f"{topic}.json"
    if not manifest_path.exists():
        return f"Error: No manifest found for '{topic}' at {manifest_path}"
    content = manifest_path.read_text()
    try:
        data = json.loads(content)
        meta = {
            "topic": topic,
            "scene_count": len(data.get("scenes", [])),
            "tts_words": len(data.get("ttsScript", "").split()),
            "scene_types": [s.get("type", "unknown") for s in data.get("scenes", [])],
        }
        return f"=== Metadata ===\n{json.dumps(meta, indent=2)}\n\n=== Manifest ===\n{content}"
    except json.JSONDecodeError:
        return f"=== Raw Content (invalid JSON) ===\n{content}"


@mcp.tool()
def write_remotion_manifest(topic: str, content: str) -> str:
    """Write or update a Remotion manifest JSON file.

    Args:
        topic: Topic slug (e.g., "aral_sea") — writes to remotion/src/manifests/{topic}.json
        content: The full JSON manifest content
    """
    REMOTION_MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = REMOTION_MANIFESTS_DIR / f"{topic}.json"

    # Validate JSON
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON — {e}"

    # Basic structure validation
    if "scenes" not in data:
        return "Error: Manifest must have a 'scenes' array"
    if "ttsScript" not in data:
        return "Error: Manifest must have a 'ttsScript' field"

    existed = manifest_path.exists()
    manifest_path.write_text(json.dumps(data, indent=2))
    action = "Updated" if existed else "Created"
    return (f"{action} {manifest_path.name} "
            f"({len(data['scenes'])} scenes, {len(data.get('ttsScript', '').split())} words)")


# ---------------------------------------------------------------------------
# Word-Triggered Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def resolve_word_triggers_tool(topic: str) -> str:
    """Resolve word-triggered anchors to frame-level timing.

    Requires TTS + Whisper alignment to be done first (generate_tts handles this).
    Reads the manifest from remotion/src/manifests/{topic}.json and Whisper data
    from tts_{topic}.mp3.json, outputs {topic}_resolved.json.

    Args:
        topic: Topic slug (e.g., "henrietta")
    """
    manifest_path = VIDGEN_DIR / "remotion" / "src" / "manifests" / f"{topic}.json"
    if not manifest_path.exists():
        return f"Error: Manifest not found: {manifest_path}"

    whisper_path = VIDGEN_DIR / f"tts_{topic}.mp3.json"
    if not whisper_path.exists():
        return f"Error: Whisper data not found: {whisper_path}. Run generate_tts first."

    try:
        from resolve_word_triggers import resolve_word_triggers as _resolve
        result = _resolve(str(manifest_path), str(whisper_path))
        return f"Resolved: {result}"
    except Exception as e:
        return f"Resolution failed: {e}"


@mcp.tool()
def audit_word_triggered(topic: str) -> str:
    """Run timeline + collision audits on a word-triggered resolved manifest.

    Requires {topic}_resolved.json to exist (from resolve_word_triggers).

    Args:
        topic: Topic slug (e.g., "henrietta")
    """
    resolved_path = VIDGEN_DIR / f"{topic}_resolved.json"
    if not resolved_path.exists():
        return f"Error: {resolved_path} not found. Run resolve_word_triggers first."

    parts = []

    # Timeline audit
    try:
        from audit_timeline import audit
        issues = audit(resolved_path)
        if issues:
            parts.append(f"Timeline audit: {len(issues)} issues found")
            for issue in issues:
                parts.append(f"  - {issue}")
        else:
            parts.append("Timeline audit: PASS")
    except Exception as e:
        parts.append(f"Timeline audit error: {e}")

    # Collision audit
    try:
        from collision_audit import audit_collisions
        collisions = audit_collisions(resolved_path)
        critical = [c for c in collisions if c["severity"] == "CRITICAL"]
        warns = [c for c in collisions if c["severity"] == "WARN"]
        bleeds = [c for c in collisions if c["severity"] == "BLEED"]
        if critical:
            parts.append(f"Collision audit: {len(critical)} CRITICAL, {len(warns)} WARN, {len(bleeds)} BLEED")
            for c in critical:
                parts.append(f"  CRITICAL: t={c['time']:.1f}s {c['scene']} \"{c['a']}\" <-> \"{c['b']}\"")
        elif warns or bleeds:
            parts.append(f"Collision audit: {len(warns)} WARN, {len(bleeds)} BLEED")
        else:
            parts.append("Collision audit: PASS")
    except Exception as e:
        parts.append(f"Collision audit error: {e}")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# SVG Asset Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def search_svg(query: str) -> str:
    """Search all SVG icon sources by keyword. Shows what's available in svgLibrary (ready to use)
    and what can be imported from Font Awesome (1,400+ icons).

    Args:
        query: Search term (e.g., "medical", "skull", "building", "person")
    """
    from svg_tools import search, format_search_results
    results = search(query)
    return format_search_results(results)


@mcp.tool()
def list_svg_library() -> str:
    """List all SVG icons currently available in svgLibrary.tsx (ready for use in manifests)."""
    from svg_tools import list_library
    names = list_library()
    return f"svgLibrary.tsx: {len(names)} icons\n\n" + "\n".join(f"  {n}" for n in names)


@mcp.tool()
def import_svg(name: str, source: str = "fa-solid", alias: str = None) -> str:
    """Import an SVG icon into svgLibrary.tsx from any icon library.

    Sources: "fa-solid" (Font Awesome, 1402 icons), "lucide" (1544 icons),
    "feather" (287 icons), "fa-regular", "custom".

    The icon becomes immediately available for use in manifest svg fields.
    Use search_svg() first to find the right icon name.

    Args:
        name: Icon name (e.g., "flask", "skull-crossbones", "activity")
        source: Icon library — "fa-solid" (default), "lucide", "feather", "fa-regular", "custom"
        alias: Optional camelCase alias for the library key
    """
    from svg_tools import import_icon
    return import_icon(source, name, alias)


@mcp.tool()
def add_custom_svg_icon(name: str, svg_markup: str) -> str:
    """Add a custom SVG icon to svgLibrary.tsx from raw SVG markup.

    Use this to create topic-specific illustrations that don't exist in Font Awesome.
    The SVG should use fill="currentColor" for dynamic coloring.
    ViewBox should be square (e.g., "0 0 100 100") for best results.

    Args:
        name: camelCase library key (e.g., "moaiStatue", "radiumJar", "icePick")
        svg_markup: Complete SVG string with viewBox and path/shape elements
    """
    from svg_tools import add_custom_svg
    return add_custom_svg(name, svg_markup)


@mcp.tool()
def compute_envelopes(topic: str) -> str:
    """Compute animation envelopes for a word-triggered manifest.

    Traces every element's transform (entrance, hold motion, exit) across all
    frames and computes the convex hull envelope. Used by debug-QA for
    higher-sensitivity collision detection.

    Args:
        topic: Manifest topic name (e.g., "antibiotics")
    """
    resolved = VIDGEN_DIR / f"{topic}_resolved.json"
    if not resolved.exists():
        return f"ERROR: {topic}_resolved.json not found. Run resolve_word_triggers_tool first."

    try:
        result = subprocess.run(
            ["npx", "tsx", "remotion/computeEnvelopes.mts", topic],
            cwd=str(VIDGEN_DIR), capture_output=True, text=True, timeout=30,
        )
        output = (result.stdout + result.stderr).strip()
        if result.returncode != 0:
            return f"ERROR: {output}"
        return output
    except Exception as e:
        return f"ERROR: {e}"


@mcp.tool()
def debug_render(topic: str, video: bool = False) -> str:
    """Render debug-QA previews or video with envelope overlays.

    Shows convex hull bounding boxes, collision intersection highlights,
    element labels, zone templates, and frame info.

    Args:
        topic: Manifest topic name
        video: If True, render full debug MP4 (slower). Default: preview PNGs only.
    """
    resolved = VIDGEN_DIR / f"{topic}_resolved.json"
    if not resolved.exists():
        return f"ERROR: {topic}_resolved.json not found."

    cmd = ["npx", "tsx", "remotion/renderDebug.mts", topic]
    if video:
        cmd.append("--video")

    try:
        result = subprocess.run(
            cmd, cwd=str(VIDGEN_DIR), capture_output=True, text=True, timeout=300,
        )
        output = (result.stdout + result.stderr).strip()
        if result.returncode != 0:
            return f"ERROR: {output}"
        return output
    except Exception as e:
        return f"ERROR: {e}"


@mcp.tool()
def collision_stats_tool(command: str = "hotspots", topic: str = None, days: int = 30) -> str:
    """Query collision statistics collected across renders.

    Args:
        command: One of "hotspots", "trends", "history"
        topic: Required for "history" command
        days: Number of days for "trends" (default 30)
    """
    try:
        from collision_stats import get_hotspots, get_trends, get_topic_history
        if command == "hotspots":
            return json.dumps(get_hotspots(), indent=2)
        elif command == "trends":
            return json.dumps(get_trends(days), indent=2)
        elif command == "history":
            if not topic:
                return "ERROR: topic required for history command"
            return json.dumps({"topic": topic, "runs": get_topic_history(topic)}, indent=2)
        else:
            return f"ERROR: Unknown command '{command}'. Use hotspots, trends, or history."
    except Exception as e:
        return f"ERROR: {e}"


if __name__ == "__main__":
    mcp.run()
