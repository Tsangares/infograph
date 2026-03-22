"""Database layer for tkk — TikTok ad intelligence."""
import sqlite3
import json
import os
from datetime import datetime
from contextlib import contextmanager

DB_PATH = os.environ.get("TKK_DB", "tkk.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def db_session():
    conn = get_db()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with db_session() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                display_name TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                token TEXT UNIQUE NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                expires_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS magic_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                expires_at TEXT NOT NULL,
                used INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                tiktok_id TEXT,
                author TEXT,
                author_id TEXT,
                description TEXT,
                duration REAL,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments_count INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                saves INTEGER DEFAULT 0,
                video_path TEXT,
                audio_path TEXT,
                transcript TEXT,
                analysis TEXT,  -- JSON: GPT analysis result
                metrics_history TEXT,  -- JSON: [{date, views, likes, ...}]
                tags TEXT,  -- JSON array
                status TEXT DEFAULT 'pending',  -- pending, downloading, analyzing, done, error
                error TEXT,
                added_by INTEGER REFERENCES users(id),
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS frames (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
                timestamp REAL NOT NULL,
                image_path TEXT NOT NULL,
                description TEXT,  -- GPT vision description
                dhash TEXT,  -- perceptual hash for dedup
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
                tiktok_user TEXT,
                text TEXT NOT NULL,
                likes INTEGER DEFAULT 0,
                reply_count INTEGER DEFAULT 0,
                sentiment TEXT,  -- positive, negative, neutral
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                concept TEXT NOT NULL,  -- full generated concept
                hook TEXT,
                structure TEXT,  -- JSON: scene breakdown
                target_length INTEGER,  -- seconds
                based_on TEXT,  -- JSON: list of video IDs used as inspiration
                score REAL,  -- predicted engagement score
                status TEXT DEFAULT 'idea',  -- idea, scripted, filmed, posted
                added_by INTEGER REFERENCES users(id),
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                source_type TEXT NOT NULL,  -- podcast, article, text, youtube
                url TEXT,
                raw_text TEXT,  -- original text or transcript
                transcript TEXT,  -- whisper transcript (for audio)
                status TEXT DEFAULT 'pending',  -- pending, transcribing, extracting, done, error
                error TEXT,
                added_by INTEGER REFERENCES users(id),
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS segments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                narration TEXT NOT NULL,  -- the actual text/script for this segment
                start_time REAL,  -- timestamp in source audio (if applicable)
                end_time REAL,
                duration INTEGER,  -- target video length in seconds
                hook TEXT,  -- opening hook for TikTok
                visual_blueprint TEXT,  -- JSON: scene-by-scene visual plan
                assets TEXT,  -- JSON: list of fetched image URLs/paths
                audio_path TEXT,  -- extracted audio clip
                video_path TEXT,  -- final assembled video
                tiktok_score REAL,  -- predicted engagement score
                status TEXT DEFAULT 'pending',  -- pending, planning, assembling, done, posted
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);
            CREATE INDEX IF NOT EXISTS idx_videos_views ON videos(views DESC);
            CREATE INDEX IF NOT EXISTS idx_frames_video ON frames(video_id);
            CREATE INDEX IF NOT EXISTS idx_comments_video ON comments(video_id);
            CREATE INDEX IF NOT EXISTS idx_segments_source ON segments(source_id);
        """)


# --- Video CRUD ---

def add_video(url, added_by=None):
    with db_session() as conn:
        try:
            conn.execute(
                "INSERT INTO videos (url, added_by) VALUES (?, ?)",
                (url, added_by)
            )
            return conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        except sqlite3.IntegrityError:
            row = conn.execute("SELECT id FROM videos WHERE url = ?", (url,)).fetchone()
            return row["id"] if row else None


def get_video(video_id):
    with db_session() as conn:
        return conn.execute("SELECT * FROM videos WHERE id = ?", (video_id,)).fetchone()


def get_video_by_url(url):
    with db_session() as conn:
        return conn.execute("SELECT * FROM videos WHERE url = ?", (url,)).fetchone()


def list_videos(limit=50, offset=0, status=None):
    with db_session() as conn:
        if status:
            return conn.execute(
                "SELECT * FROM videos WHERE status = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (status, limit, offset)
            ).fetchall()
        return conn.execute(
            "SELECT * FROM videos ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        ).fetchall()


def update_video(video_id, **kwargs):
    kwargs["updated_at"] = datetime.utcnow().isoformat()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [video_id]
    with db_session() as conn:
        conn.execute(f"UPDATE videos SET {sets} WHERE id = ?", vals)


def video_count():
    with db_session() as conn:
        return conn.execute("SELECT COUNT(*) FROM videos").fetchone()[0]


# --- Frames ---

def add_frame(video_id, timestamp, image_path, dhash=None, description=None):
    with db_session() as conn:
        conn.execute(
            "INSERT INTO frames (video_id, timestamp, image_path, dhash, description) VALUES (?, ?, ?, ?, ?)",
            (video_id, timestamp, image_path, dhash, description)
        )


def get_frames(video_id):
    with db_session() as conn:
        return conn.execute(
            "SELECT * FROM frames WHERE video_id = ? ORDER BY timestamp",
            (video_id,)
        ).fetchall()


# --- Comments ---

def add_comment(video_id, tiktok_user, text, likes=0, reply_count=0, sentiment=None):
    with db_session() as conn:
        conn.execute(
            "INSERT INTO comments (video_id, tiktok_user, text, likes, reply_count, sentiment) VALUES (?, ?, ?, ?, ?, ?)",
            (video_id, tiktok_user, text, likes, reply_count, sentiment)
        )


def get_comments(video_id):
    with db_session() as conn:
        return conn.execute(
            "SELECT * FROM comments WHERE video_id = ? ORDER BY likes DESC",
            (video_id,)
        ).fetchall()


# --- Drafts ---

def add_draft(title, concept, hook=None, structure=None, target_length=None, based_on=None, score=None, added_by=None):
    with db_session() as conn:
        conn.execute(
            """INSERT INTO drafts (title, concept, hook, structure, target_length, based_on, score, added_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (title, concept, hook, json.dumps(structure) if structure else None,
             target_length, json.dumps(based_on) if based_on else None, score, added_by)
        )
        return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def get_draft(draft_id):
    with db_session() as conn:
        return conn.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,)).fetchone()


def list_drafts(limit=50):
    with db_session() as conn:
        return conn.execute(
            "SELECT * FROM drafts ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()


def update_draft(draft_id, **kwargs):
    kwargs["updated_at"] = datetime.utcnow().isoformat()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [draft_id]
    with db_session() as conn:
        conn.execute(f"UPDATE drafts SET {sets} WHERE id = ?", vals)


# --- Sources ---

def add_source(title, source_type, url=None, raw_text=None, added_by=None):
    with db_session() as conn:
        conn.execute(
            "INSERT INTO sources (title, source_type, url, raw_text, added_by) VALUES (?, ?, ?, ?, ?)",
            (title, source_type, url, raw_text, added_by)
        )
        return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def get_source(source_id):
    with db_session() as conn:
        return conn.execute("SELECT * FROM sources WHERE id = ?", (source_id,)).fetchone()


def list_sources(limit=50):
    with db_session() as conn:
        return conn.execute(
            "SELECT * FROM sources ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()


def update_source(source_id, **kwargs):
    kwargs["updated_at"] = datetime.utcnow().isoformat()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [source_id]
    with db_session() as conn:
        conn.execute(f"UPDATE sources SET {sets} WHERE id = ?", vals)


# --- Segments ---

def add_segment(source_id, title, narration, **kwargs):
    with db_session() as conn:
        cols = ["source_id", "title", "narration"]
        vals = [source_id, title, narration]
        for k, v in kwargs.items():
            cols.append(k)
            vals.append(json.dumps(v) if isinstance(v, (dict, list)) else v)
        placeholders = ", ".join("?" for _ in vals)
        col_str = ", ".join(cols)
        conn.execute(f"INSERT INTO segments ({col_str}) VALUES ({placeholders})", vals)
        return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def get_segment(segment_id):
    with db_session() as conn:
        return conn.execute("SELECT * FROM segments WHERE id = ?", (segment_id,)).fetchone()


def list_segments(source_id=None, limit=50):
    with db_session() as conn:
        if source_id:
            return conn.execute(
                "SELECT * FROM segments WHERE source_id = ? ORDER BY tiktok_score DESC LIMIT ?",
                (source_id, limit)
            ).fetchall()
        return conn.execute(
            "SELECT * FROM segments ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()


def update_segment(segment_id, **kwargs):
    kwargs["updated_at"] = datetime.utcnow().isoformat()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [segment_id]
    with db_session() as conn:
        conn.execute(f"UPDATE segments SET {sets} WHERE id = ?", vals)


# --- Users ---

def get_or_create_user(email):
    with db_session() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if row:
            return dict(row)
        conn.execute("INSERT INTO users (email) VALUES (?)", (email,))
        return dict(conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone())


# --- Stats ---

def get_stats():
    with db_session() as conn:
        total = conn.execute("SELECT COUNT(*) FROM videos").fetchone()[0]
        analyzed = conn.execute("SELECT COUNT(*) FROM videos WHERE status = 'done'").fetchone()[0]
        total_views = conn.execute("SELECT COALESCE(SUM(views), 0) FROM videos").fetchone()[0]
        total_drafts = conn.execute("SELECT COUNT(*) FROM drafts").fetchone()[0]
        return {
            "total_videos": total,
            "analyzed": analyzed,
            "total_views": total_views,
            "total_drafts": total_drafts,
        }
