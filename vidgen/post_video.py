#!/usr/bin/env python3
"""
Post a rendered video to TikTok via the Content Posting API.

Usage:
    python post_video.py output.mp4 --title "Statues that WALKED?" --privacy SELF_ONLY
    python post_video.py output.mp4 --title "..." --privacy PUBLIC_TO_EVERYONE
    python post_video.py output.mp4 --title "..." --inbox  # Post to creator inbox

Requires TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET env vars.
Auth tokens managed by the tiktok-post skill's auth helper.
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request

AUTH_SCRIPT = "/home/wil/.openclaw/workspace/skills/tiktok-post/scripts/tiktok_auth.py"

API_BASE = "https://open.tiktokapis.com/v2"
CREATOR_INFO_URL = f"{API_BASE}/post/publish/creator_info/query/"
DIRECT_POST_URL = f"{API_BASE}/post/publish/video/init/"
INBOX_POST_URL = f"{API_BASE}/post/publish/inbox/video/init/"

PRIVACY_LEVELS = [
    "PUBLIC_TO_EVERYONE",
    "MUTUAL_FOLLOW_FRIENDS",
    "FOLLOWER_OF_CREATOR",
    "SELF_ONLY",
]


def get_access_token() -> str:
    """Get a valid access token from the auth helper."""
    for var in ("TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET"):
        if not os.environ.get(var):
            print(f"Error: {var} not set.", file=sys.stderr)
            sys.exit(1)

    result = subprocess.run(
        ["python3", AUTH_SCRIPT, "--get-token"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print("Failed to get access token.", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        print(
            "If no tokens exist, run the auth flow first:\n"
            f"  python3 {AUTH_SCRIPT}",
            file=sys.stderr,
        )
        sys.exit(1)

    token = result.stdout.strip()
    if not token:
        print("Auth helper returned empty token.", file=sys.stderr)
        sys.exit(1)
    return token


def api_request(url: str, token: str, body: dict | None = None) -> dict:
    """Make an authenticated POST to the TikTok API. Returns parsed JSON."""
    data = json.dumps(body or {}).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode(errors="replace")
        try:
            err = json.loads(body_text)
        except json.JSONDecodeError:
            err = body_text
        print(f"API error {e.code} from {url}", file=sys.stderr)
        print(json.dumps(err, indent=2) if isinstance(err, dict) else err, file=sys.stderr)
        sys.exit(1)


def query_creator_info(token: str) -> dict:
    """Query creator info (required by TikTok before posting)."""
    print("Querying creator info...", file=sys.stderr)
    info = api_request(CREATOR_INFO_URL, token)
    error = info.get("error", {})
    if error.get("code") != "ok":
        print(f"Creator info query failed (log_id={error.get('log_id', 'N/A')}):", file=sys.stderr)
        print(json.dumps(info, indent=2), file=sys.stderr)
        sys.exit(1)
    data = info.get("data", {})
    print(f"  Creator: privacy options = {data.get('privacy_level_options', [])}", file=sys.stderr)
    print(f"  Max video duration: {data.get('max_video_post_duration_sec', '?')}s", file=sys.stderr)
    return data


def init_video_upload(
    token: str,
    video_path: str,
    title: str,
    privacy: str,
    use_inbox: bool,
    disable_comment: bool,
    disable_duet: bool,
    disable_stitch: bool,
) -> dict:
    """Initialize the video upload and get the upload URL."""
    video_size = os.path.getsize(video_path)
    print(f"Video: {video_path} ({video_size:,} bytes)", file=sys.stderr)

    post_info = {"title": title, "privacy_level": privacy}
    if disable_comment:
        post_info["disable_comment"] = True
    if disable_duet:
        post_info["disable_duet"] = True
    if disable_stitch:
        post_info["disable_stitch"] = True

    body = {
        "post_info": post_info,
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": video_size,
            "chunk_size": video_size,
            "total_chunk_count": 1,
        },
    }

    url = INBOX_POST_URL if use_inbox else DIRECT_POST_URL
    label = "inbox" if use_inbox else "direct"
    print(f"Initializing {label} post upload...", file=sys.stderr)
    resp = api_request(url, token, body)

    error = resp.get("error", {})
    if error.get("code") != "ok":
        log_id = error.get("log_id", "N/A")
        print(f"Upload init failed (log_id={log_id}):", file=sys.stderr)
        print(json.dumps(resp, indent=2), file=sys.stderr)
        sys.exit(1)

    return resp.get("data", {})


def upload_video(upload_url: str, video_path: str):
    """PUT the video binary to TikTok's upload endpoint."""
    video_size = os.path.getsize(video_path)
    print(f"Uploading video to TikTok ({video_size:,} bytes)...", file=sys.stderr)

    with open(video_path, "rb") as f:
        video_data = f.read()

    req = urllib.request.Request(
        upload_url,
        data=video_data,
        headers={
            "Content-Type": "video/mp4",
            "Content-Length": str(video_size),
            "Content-Range": f"bytes 0-{video_size - 1}/{video_size}",
        },
        method="PUT",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            body = resp.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        status = e.code
        body = e.read().decode(errors="replace")

    if status not in (200, 201):
        print(f"Upload failed with status {status}:", file=sys.stderr)
        print(body, file=sys.stderr)
        sys.exit(1)

    print("Upload complete.", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Post a video to TikTok")
    parser.add_argument("video", help="Path to the MP4 file")
    parser.add_argument("--title", required=True, help="Video title/caption")
    parser.add_argument(
        "--privacy", default="SELF_ONLY", choices=PRIVACY_LEVELS,
        help="Privacy level (default: SELF_ONLY)",
    )
    parser.add_argument("--inbox", action="store_true", help="Post to creator inbox instead of direct")
    parser.add_argument("--disable-comment", action="store_true", help="Disable comments")
    parser.add_argument("--disable-duet", action="store_true", help="Disable duets")
    parser.add_argument("--disable-stitch", action="store_true", help="Disable stitches")
    args = parser.parse_args()

    if not os.path.isfile(args.video):
        print(f"Error: Video file not found: {args.video}", file=sys.stderr)
        sys.exit(1)

    # Step 1: Get access token
    token = get_access_token()
    print("Access token obtained.", file=sys.stderr)

    # Step 2: Query creator info (required by TikTok API rules)
    query_creator_info(token)

    # Step 3: Initialize upload
    data = init_video_upload(
        token, args.video, args.title, args.privacy, args.inbox,
        args.disable_comment, args.disable_duet, args.disable_stitch,
    )
    upload_url = data.get("upload_url")
    publish_id = data.get("publish_id", "N/A")

    if not upload_url:
        print("No upload_url in response:", file=sys.stderr)
        print(json.dumps(data, indent=2), file=sys.stderr)
        sys.exit(1)

    print(f"  publish_id: {publish_id}", file=sys.stderr)

    # Step 4: Upload video binary
    upload_video(upload_url, args.video)

    # Step 5: Report result
    print(f"\nPublish ID: {publish_id}")
    print(f"Status: uploaded (TikTok will process and publish)")
    print(f"Privacy: {args.privacy}")
    mode = "inbox" if args.inbox else "direct"
    print(f"Mode: {mode}")


if __name__ == "__main__":
    main()
