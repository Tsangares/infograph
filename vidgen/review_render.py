#!/usr/bin/env python3
"""Automated render quality checker for TKK video production.

Validates a rendered MP4 against quality rules using ffprobe for metadata
and PIL for visual frame analysis.

Usage:
    python review_render.py output.mp4                    # Full review
    python review_render.py output.mp4 --extract-frames   # Save frames to review_frames/
    python review_render.py output.mp4 --json              # JSON output for automation
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image
    import numpy as np
except ImportError:
    np = None
    from PIL import Image


# --- ffprobe helpers ---

def ffprobe_json(path: str) -> dict:
    """Run ffprobe and return parsed JSON."""
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


def get_stream(probe: dict, codec_type: str) -> dict | None:
    for s in probe.get("streams", []):
        if s.get("codec_type") == codec_type:
            return s
    return None


def extract_frames(path: str, outdir: str, interval: float = 5.0) -> list[str]:
    """Extract frames at regular intervals. Returns list of image paths."""
    os.makedirs(outdir, exist_ok=True)
    pattern = os.path.join(outdir, "frame_%04d.png")
    cmd = [
        "ffmpeg", "-v", "quiet", "-i", path,
        "-vf", f"fps=1/{interval}",
        "-vsync", "vfr", pattern,
    ]
    subprocess.run(cmd, capture_output=True)
    frames = sorted(Path(outdir).glob("frame_*.png"))
    return [str(f) for f in frames]


# --- Image analysis ---

def is_frame_black(img: Image.Image, threshold: int = 15) -> bool:
    """Check if a frame is effectively pure black."""
    gray = img.convert("L")
    pixels = list(gray.getdata()) if not hasattr(gray, "get_flattened_data") else list(gray.get_flattened_data())
    avg = sum(pixels) / len(pixels)
    return avg < threshold


def check_edge_clipping(img: Image.Image, margin: int = 20, brightness_thresh: int = 60) -> dict:
    """Check if bright content (likely text) touches frame edges.

    Looks for non-dark pixels in the edge margin regions. If significant
    bright content is at the very edge, text may be clipped.
    """
    w, h = img.size
    gray = img.convert("L")

    regions = {
        "top": gray.crop((0, 0, w, margin)),
        "bottom": gray.crop((0, h - margin, w, h)),
        "left": gray.crop((0, 0, margin, h)),
        "right": gray.crop((w - margin, 0, w, h)),
    }

    results = {}
    for name, region in regions.items():
        pixels = list(region.getdata()) if not hasattr(region, "get_flattened_data") else list(region.get_flattened_data())
        bright = sum(1 for p in pixels if p > brightness_thresh)
        ratio = bright / len(pixels) if pixels else 0
        # If more than 5% of edge pixels are bright, possible clipping
        results[name] = {"bright_ratio": round(ratio, 4), "clipped": ratio > 0.05}

    return results


# --- Checks ---

class Check:
    def __init__(self, name: str, status: str, detail: str):
        self.name = name
        self.status = status  # PASS, WARN, FAIL
        self.detail = detail

    def to_dict(self):
        return {"name": self.name, "status": self.status, "detail": self.detail}

    def __str__(self):
        icons = {"PASS": "\033[32mPASS\033[0m", "WARN": "\033[33mWARN\033[0m", "FAIL": "\033[31mFAIL\033[0m"}
        icon = icons.get(self.status, self.status)
        return f"  [{icon}] {self.name}: {self.detail}"

    def plain(self):
        return f"  [{self.status}] {self.name}: {self.detail}"


def run_checks(path: str, frame_dir: str | None = None) -> list[Check]:
    checks = []

    # Probe metadata
    try:
        probe = ffprobe_json(path)
    except RuntimeError as e:
        checks.append(Check("ffprobe", "FAIL", str(e)))
        return checks

    fmt = probe.get("format", {})
    video = get_stream(probe, "video")
    audio = get_stream(probe, "audio")

    # 1. Resolution check (1080x1920 for vertical TikTok)
    if video:
        w = int(video.get("width", 0))
        h = int(video.get("height", 0))
        if w == 1080 and h == 1920:
            checks.append(Check("resolution", "PASS", f"{w}x{h}"))
        else:
            checks.append(Check("resolution", "FAIL", f"{w}x{h} (expected 1080x1920)"))
    else:
        checks.append(Check("resolution", "FAIL", "No video stream found"))

    # 2. Audio presence
    if audio:
        checks.append(Check("audio_track", "PASS", f"codec={audio.get('codec_name', '?')}"))
    else:
        checks.append(Check("audio_track", "FAIL", "No audio stream found"))

    # 3. Audio/video duration match
    vid_dur = float(video.get("duration", 0)) if video else 0
    aud_dur = float(audio.get("duration", 0)) if audio else 0
    fmt_dur = float(fmt.get("duration", 0))
    # Use format duration as fallback
    if vid_dur == 0:
        vid_dur = fmt_dur

    if audio and video:
        diff = abs(vid_dur - aud_dur)
        if diff <= 1.0:
            checks.append(Check("av_sync", "PASS", f"video={vid_dur:.1f}s audio={aud_dur:.1f}s (diff={diff:.2f}s)"))
        elif diff <= 3.0:
            checks.append(Check("av_sync", "WARN", f"video={vid_dur:.1f}s audio={aud_dur:.1f}s (diff={diff:.2f}s)"))
        else:
            checks.append(Check("av_sync", "FAIL", f"video={vid_dur:.1f}s audio={aud_dur:.1f}s (diff={diff:.2f}s)"))

    # 4. Bitrate check (>4 Mbps)
    bitrate_str = fmt.get("bit_rate", "0")
    bitrate = int(bitrate_str) if bitrate_str else 0
    bitrate_mbps = bitrate / 1_000_000
    if bitrate_mbps >= 4.0:
        checks.append(Check("bitrate", "PASS", f"{bitrate_mbps:.1f} Mbps"))
    elif bitrate_mbps >= 2.0:
        checks.append(Check("bitrate", "WARN", f"{bitrate_mbps:.1f} Mbps (recommended >4 Mbps)"))
    else:
        checks.append(Check("bitrate", "FAIL", f"{bitrate_mbps:.1f} Mbps (too low, expected >4 Mbps)"))

    # 5. File size sanity
    file_size = os.path.getsize(path)
    file_mb = file_size / (1024 * 1024)
    duration = vid_dur or fmt_dur
    if duration > 0:
        mb_per_30s = file_mb / (duration / 30)
        if mb_per_30s < 1.0:
            checks.append(Check("file_size", "FAIL",
                f"{file_mb:.1f} MB for {duration:.0f}s ({mb_per_30s:.1f} MB/30s — suspiciously small)"))
        elif mb_per_30s < 3.0:
            checks.append(Check("file_size", "WARN",
                f"{file_mb:.1f} MB for {duration:.0f}s ({mb_per_30s:.1f} MB/30s — low)"))
        else:
            checks.append(Check("file_size", "PASS", f"{file_mb:.1f} MB for {duration:.0f}s"))
    else:
        checks.append(Check("file_size", "WARN", f"{file_mb:.1f} MB (could not determine duration)"))

    # 6 & 7. Frame-based checks (black frame, edge clipping)
    use_tmpdir = frame_dir is None
    if use_tmpdir:
        tmpdir = tempfile.mkdtemp(prefix="review_frames_")
        frame_dir_actual = tmpdir
    else:
        frame_dir_actual = frame_dir

    interval = max(5.0, duration / 20) if duration > 0 else 5.0
    frames = extract_frames(path, frame_dir_actual, interval=interval)

    if not frames:
        checks.append(Check("first_frame_black", "WARN", "Could not extract frames"))
        checks.append(Check("edge_clipping", "WARN", "Could not extract frames"))
    else:
        # 6. First frame black check
        first = Image.open(frames[0])
        if is_frame_black(first):
            checks.append(Check("first_frame_black", "FAIL", "First frame is pure/near-black"))
        else:
            checks.append(Check("first_frame_black", "PASS", "First frame has visible content"))

        # 7. Edge clipping across all frames
        any_clipped = False
        clip_details = []
        for fp in frames:
            img = Image.open(fp)
            edges = check_edge_clipping(img)
            clipped_edges = [e for e, v in edges.items() if v["clipped"]]
            if clipped_edges:
                any_clipped = True
                fname = os.path.basename(fp)
                clip_details.append(f"{fname}: {','.join(clipped_edges)}")

        if any_clipped:
            summary = "; ".join(clip_details[:3])
            if len(clip_details) > 3:
                summary += f" (+{len(clip_details)-3} more)"
            checks.append(Check("edge_clipping", "WARN", f"Content near edges in {len(clip_details)}/{len(frames)} frames: {summary}"))
        else:
            checks.append(Check("edge_clipping", "PASS", f"No content clipping detected across {len(frames)} frames"))

    # Clean up temp frames if we created them
    if use_tmpdir:
        for f in frames:
            try:
                os.unlink(f)
            except OSError:
                pass
        try:
            os.rmdir(frame_dir_actual)
        except OSError:
            pass

    return checks


# --- Report ---

def print_report(checks: list[Check], path: str, use_json: bool = False):
    if use_json:
        report = {
            "file": path,
            "checks": [c.to_dict() for c in checks],
            "summary": {
                "pass": sum(1 for c in checks if c.status == "PASS"),
                "warn": sum(1 for c in checks if c.status == "WARN"),
                "fail": sum(1 for c in checks if c.status == "FAIL"),
            },
            "overall": "FAIL" if any(c.status == "FAIL" for c in checks)
                       else "WARN" if any(c.status == "WARN" for c in checks)
                       else "PASS",
        }
        print(json.dumps(report, indent=2))
        return

    # Pretty terminal output
    print(f"\n  Render Quality Report: {os.path.basename(path)}")
    print(f"  {'=' * 50}")
    for c in checks:
        # Detect if terminal supports color
        if sys.stdout.isatty():
            print(str(c))
        else:
            print(c.plain())
    print(f"  {'=' * 50}")
    n_pass = sum(1 for c in checks if c.status == "PASS")
    n_warn = sum(1 for c in checks if c.status == "WARN")
    n_fail = sum(1 for c in checks if c.status == "FAIL")
    total = len(checks)
    if n_fail > 0:
        overall = "\033[31mFAIL\033[0m" if sys.stdout.isatty() else "FAIL"
    elif n_warn > 0:
        overall = "\033[33mWARN\033[0m" if sys.stdout.isatty() else "WARN"
    else:
        overall = "\033[32mPASS\033[0m" if sys.stdout.isatty() else "PASS"
    print(f"  Overall: {overall}  ({n_pass} pass, {n_warn} warn, {n_fail} fail / {total} checks)\n")


def main():
    parser = argparse.ArgumentParser(description="Review rendered MP4 against TKK quality rules")
    parser.add_argument("video", help="Path to rendered MP4 file")
    parser.add_argument("--extract-frames", action="store_true",
                        help="Save extracted frames to review_frames/ directory")
    parser.add_argument("--json", action="store_true", help="Output JSON report for automation")
    args = parser.parse_args()

    if not os.path.isfile(args.video):
        print(f"Error: file not found: {args.video}", file=sys.stderr)
        sys.exit(1)

    frame_dir = None
    if args.extract_frames:
        frame_dir = os.path.join(os.path.dirname(args.video) or ".", "review_frames")

    checks = run_checks(args.video, frame_dir=frame_dir)
    print_report(checks, args.video, use_json=args.json)

    if args.extract_frames and frame_dir:
        print(f"  Frames saved to: {frame_dir}/")

    # Exit code: 2 for fail, 1 for warn, 0 for pass
    if any(c.status == "FAIL" for c in checks):
        sys.exit(2)
    elif any(c.status == "WARN" for c in checks):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
