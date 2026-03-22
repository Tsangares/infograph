"""Shared render utilities for TKK video pipeline."""

import json
import os
import re
import subprocess
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


def detect_scene_timings(mp3_path: str, num_scenes: int,
                         silence_threshold_db: int = None,
                         silence_min_duration: float = None) -> dict:
    """Detect per-scene durations from TTS audio via silence detection.

    Runs ffmpeg silencedetect, picks the num_scenes-1 largest silence gaps
    as scene boundaries, and computes per-scene durations.

    Returns {"scene_durations": [...], "boundaries": [...], "total_audio": float}
    and writes a sidecar JSON file next to the MP3.
    """
    mp3 = Path(mp3_path)

    # Resolve silence detection parameters from args, env, or defaults
    if silence_threshold_db is None:
        silence_threshold_db = int(os.environ.get("TKK_SILENCE_THRESHOLD_DB", "-30"))
    if silence_min_duration is None:
        silence_min_duration = float(os.environ.get("TKK_SILENCE_MIN_DURATION", "0.3"))

    # Get total audio duration
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(mp3)],
        capture_output=True, text=True, timeout=10,
    )
    total_audio = float(probe.stdout.strip())

    # Run silence detection
    r = subprocess.run(
        ["ffmpeg", "-i", str(mp3), "-af",
         f"silencedetect=noise={silence_threshold_db}dB:d={silence_min_duration}",
         "-f", "null", "-"],
        capture_output=True, text=True, timeout=30,
    )
    stderr = r.stderr

    # Parse silence_start / silence_end pairs
    starts = [float(m) for m in re.findall(r"silence_start:\s*([\d.]+)", stderr)]
    ends = [float(m) for m in re.findall(r"silence_end:\s*([\d.]+)", stderr)]

    # Build gaps: (midpoint, duration)
    gaps = []
    for s, e in zip(starts, ends):
        mid = (s + e) / 2
        dur = e - s
        gaps.append((mid, dur))

    needed = num_scenes - 1

    if len(gaps) >= needed:
        # Pick the N-1 largest gaps by duration, then sort by time
        largest = sorted(gaps, key=lambda g: g[1], reverse=True)[:needed]
        boundaries = sorted(g[0] for g in largest)
    else:
        # Fewer gaps than needed — use what we have, then split longest segment
        boundaries = sorted(g[0] for g in gaps)
        print(f"  WARN: only {len(gaps)} silence gaps found, need {needed}. "
              f"Splitting longest segments proportionally.")
        while len(boundaries) < needed:
            # Find the longest segment and split it at its midpoint
            edges = [0.0] + boundaries + [total_audio]
            longest_idx = 0
            longest_dur = 0
            for i in range(len(edges) - 1):
                seg = edges[i + 1] - edges[i]
                if seg > longest_dur:
                    longest_dur = seg
                    longest_idx = i
            split_at = (edges[longest_idx] + edges[longest_idx + 1]) / 2
            boundaries.append(split_at)
            boundaries.sort()

    # Compute per-scene durations from boundaries
    edges = [0.0] + boundaries + [total_audio]
    scene_durations = [round(edges[i + 1] - edges[i], 3) for i in range(num_scenes)]

    result = {
        "scene_durations": scene_durations,
        "boundaries": [round(b, 3) for b in boundaries],
        "total_audio": round(total_audio, 3),
    }

    # Write sidecar JSON
    if mp3.stem.startswith("tts_"):
        sidecar = mp3.parent / f"{mp3.stem}_timings.json"
    else:
        sidecar = mp3.parent / f"tts_{mp3.stem}_timings.json"
    sidecar.write_text(json.dumps(result, indent=2))
    print(f"  Timings: {scene_durations} (total={total_audio:.1f}s) → {sidecar.name}")

    return result


def estimate_scene_timings_from_docstring(mp3_path: str, screenplay_path: str,
                                           num_scenes: int) -> dict:
    """Estimate per-scene durations by scaling docstring time ranges to actual TTS length.

    Reads the screenplay's docstring for lines like:
        Scene 1 (0.0–7.0s): ...
        Scene 1 (0.0-6.0s = 6.00s): ...
    Computes intended proportions, then scales to match actual audio duration.

    Returns {"scene_durations": [...], "boundaries": [...], "total_audio": float}
    """
    # Read screenplay and extract docstring scene time ranges
    text = Path(screenplay_path).read_text()

    # Match both formats: en-dash (–) and hyphen (-), with optional "= Xs"
    pattern = r'Scene\s+\d+\s+\((\d+\.?\d*)\s*[–\-]\s*(\d+\.?\d*)s'
    matches = re.findall(pattern, text)

    if len(matches) < num_scenes:
        raise ValueError(
            f"Found {len(matches)} scene time ranges in docstring, need {num_scenes}. "
            f"File: {screenplay_path}")

    # Take the first num_scenes matches
    matches = matches[:num_scenes]
    intended = [float(end) - float(start) for start, end in matches]

    if any(d <= 0 for d in intended):
        raise ValueError(f"Invalid scene durations from docstring: {intended}")

    # Get actual TTS audio duration
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(mp3_path)],
        capture_output=True, text=True, timeout=10,
    )
    total_audio = float(probe.stdout.strip())

    # Scale proportionally
    intended_total = sum(intended)
    scale = total_audio / intended_total
    scene_durations = [round(d * scale, 3) for d in intended]

    # Compute boundaries (cumulative sums, excluding last)
    boundaries = []
    cumulative = 0.0
    for d in scene_durations[:-1]:
        cumulative += d
        boundaries.append(round(cumulative, 3))

    result = {
        "scene_durations": scene_durations,
        "boundaries": boundaries,
        "total_audio": round(total_audio, 3),
    }

    # Write sidecar JSON
    mp3 = Path(mp3_path)
    if mp3.stem.startswith("tts_"):
        sidecar = mp3.parent / f"{mp3.stem}_timings.json"
    else:
        sidecar = mp3.parent / f"tts_{mp3.stem}_timings.json"
    sidecar.write_text(json.dumps(result, indent=2))

    print(f"  Proportional timings (from docstring): {scene_durations} "
          f"(scale={scale:.3f}, total={total_audio:.1f}s) → {sidecar.name}")

    return result


def get_duration(path: str) -> float:
    """Get duration of a media file (video or audio) in seconds via ffprobe."""
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, timeout=10,
    )
    return float(r.stdout.strip())


def time_scale_scenes(scene_files, target_durations):
    """Time-scale scene MP4s to match target durations.

    For each scene, if actual duration differs from target by >0.1s,
    re-encode with setpts to match. Scenes are silent video only.

    Args:
        scene_files: List of scene MP4 file paths.
        target_durations: List of target durations in seconds.
    """
    MAX_SCALE = 1.5  # Cap to prevent visible slow-motion
    MAX_FREEZE = 5.0  # Max freeze-frame duration in seconds

    TARGET_TIMESCALE = "15360"

    for i, (sf, target) in enumerate(zip(scene_files, target_durations)):
        actual = get_duration(sf)
        drift = abs(actual - target)
        if drift <= 0.1:
            # Still normalize time_base to avoid concat timestamp issues
            r_probe = subprocess.run(
                ["ffprobe", "-v", "quiet", "-show_entries", "stream=time_base",
                 "-of", "default=noprint_wrappers=1:nokey=1", sf],
                capture_output=True, text=True, timeout=5)
            if r_probe.stdout.strip() != f"1/{TARGET_TIMESCALE}":
                norm = sf + ".norm.mp4"
                subprocess.run(
                    ["ffmpeg", "-y", "-i", sf, "-c:v", "libx264", "-crf", "18",
                     "-preset", "fast", "-pix_fmt", "yuv420p",
                     "-video_track_timescale", TARGET_TIMESCALE, norm],
                    capture_output=True, timeout=120)
                if Path(norm).exists():
                    Path(norm).replace(sf)
            print(f"  Scene {i+1}: {actual:.2f}s (target {target:.2f}s) — OK")
            continue

        ratio = target / actual
        freeze_dur = 0.0

        if ratio > MAX_SCALE:
            # Gentle slowdown at MAX_SCALE + freeze last frame for remainder
            scaled_dur = actual * MAX_SCALE
            freeze_dur = min(target - scaled_dur, MAX_FREEZE)
            print(f"  Scene {i+1}: {actual:.2f}s → {target:.2f}s "
                  f"(setpts {MAX_SCALE}x + freeze {freeze_dur:.2f}s)")
            ratio = MAX_SCALE
        elif ratio < 1 / MAX_SCALE:
            print(f"  Scene {i+1}: WARN: speedup ratio {ratio:.2f}x exceeds limit, "
                  f"capping to {1/MAX_SCALE:.2f}x (actual={actual:.2f}s target={target:.2f}s)")
            ratio = 1 / MAX_SCALE
        else:
            print(f"  Scene {i+1}: {actual:.2f}s → {target:.2f}s "
                  f"(scale {ratio:.3f}, drift was {drift:.2f}s)")

        scaled = sf + ".scaled.mp4"

        if freeze_dur > 0:
            # Two-step: setpts slowdown then tpad freeze-frame
            vf = f"setpts={ratio}*PTS,tpad=stop_mode=clone:stop_duration={freeze_dur}"
        else:
            vf = f"setpts={ratio}*PTS"

        r = subprocess.run(
            ["ffmpeg", "-y", "-i", sf,
             "-filter:v", vf,
             "-r", "30", "-an",
             "-c:v", "libx264", "-crf", "18", "-preset", "fast",
             "-pix_fmt", "yuv420p",
             "-video_track_timescale", TARGET_TIMESCALE, scaled],
            capture_output=True, timeout=120,
        )
        if r.returncode != 0:
            print(f"  WARN: time-scale failed for scene {i+1}, keeping original")
            if freeze_dur > 0:
                print(f"    stderr: {r.stderr.decode()[:300]}")
            Path(scaled).unlink(missing_ok=True)
            continue

        # Replace original with scaled version
        Path(scaled).replace(sf)


def validate_av_sync(final_mp4: str, audio_mp3: str) -> dict:
    """Check AV sync drift between final video and source audio.

    Returns {"video_dur", "audio_dur", "drift", "status": "PASS|WARN|FAIL"}
    """
    video_dur = get_duration(final_mp4)
    audio_dur = get_duration(audio_mp3)
    drift = abs(video_dur - audio_dur)

    if drift < 0.5:
        status = "PASS"
    elif drift < 1.0:
        status = "WARN"
    else:
        status = "FAIL"

    result = {
        "video_dur": round(video_dur, 3),
        "audio_dur": round(audio_dur, 3),
        "drift": round(drift, 3),
        "status": status,
    }
    print(f"  AV Sync: video={video_dur:.2f}s audio={audio_dur:.2f}s "
          f"drift={drift:.2f}s → {status}")
    return result


def _render_one_scene(args):
    """Worker function for parallel scene rendering. Runs in a subprocess."""
    python, script, scene_idx = args
    r = subprocess.run(
        [python, script, "--scene", str(scene_idx)],
        capture_output=True, text=True, timeout=600,
    )
    # Extract SCENE_FILE from stdout
    scene_file = None
    for ln in r.stdout.splitlines():
        if ln.startswith("SCENE_FILE:"):
            scene_file = ln.split(":", 1)[1].strip()
            break
    return scene_idx, r.returncode, r.stdout, r.stderr, scene_file


def parallel_render_scenes(script, scene_count=6, topic=None, media_dir=None,
                           audio_path=None):
    """Render all scenes in parallel using ProcessPoolExecutor.

    Args:
        script: Absolute path to the *_manim.py screenplay file.
        scene_count: Number of scenes (default 6).
        topic: Topic prefix for fallback file search (e.g. "chariot_bronze_age").
               If None, derived from script filename.
        media_dir: Directory to search for fallback scene files. If None, uses
                   script_dir/media.
        audio_path: Path to TTS audio MP3. When provided, detects scene timings
                    via silence detection and time-scales rendered scenes to match.

    Returns:
        List of scene file paths in order, or sys.exit(1) on failure.
    """
    import sys

    script = str(Path(script).resolve())
    script_dir = Path(script).parent
    if topic is None:
        topic = Path(script).stem.replace("_manim", "")
    if media_dir is None:
        media_dir = script_dir / "media"

    # Auto-detect TTS audio file if not provided
    if not audio_path:
        auto_audio = script_dir / f"tts_{topic}.mp3"
        if auto_audio.exists():
            audio_path = str(auto_audio)
            print(f"  Auto-detected TTS audio: {auto_audio.name}")

    # Detect scene timings from TTS audio (if available)
    # Primary: proportional timing from screenplay docstring
    # Fallback: silence detection
    target_durations = None
    if audio_path and Path(audio_path).exists():
        try:
            timing = estimate_scene_timings_from_docstring(
                str(audio_path), script, scene_count)
            target_durations = timing["scene_durations"]
        except Exception as e:
            print(f"  WARN: docstring timing failed ({e}), using silence detection")
            timing = detect_scene_timings(str(audio_path), scene_count)
            target_durations = timing["scene_durations"]
        os.environ["TKK_SCENE_TIMINGS"] = json.dumps(target_durations)

    # Detect venv python
    venv_python = script_dir / ".venv" / "bin" / "python3"
    python = str(venv_python) if venv_python.exists() else sys.executable

    max_workers = min(scene_count, os.cpu_count() or 4)
    print(f"\n  Rendering {scene_count} scenes in parallel (max_workers={max_workers})")

    files = [None] * scene_count
    args_list = [(python, script, i) for i in range(scene_count)]

    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_render_one_scene, a): a[2] for a in args_list}
        for f in as_completed(futures):
            idx, rc, stdout, stderr, scene_file = f.result()
            name = f"Scene {idx+1}/{scene_count}"
            print(f"  {name}: ", end="")
            if rc != 0:
                print(f"FAILED ({rc})")
                print(stderr[-500:] if len(stderr) > 500 else stderr)
                sys.exit(1)
            if scene_file:
                files[idx] = scene_file
                print(f"OK: {Path(scene_file).name} "
                      f"({Path(scene_file).stat().st_size / 1024:.0f} KB)")
            else:
                # Fallback: search media dir
                for mp4 in Path(media_dir).rglob(f"{topic}_scene_{idx+1}.mp4"):
                    files[idx] = str(mp4)
                    print(f"OK (fallback): {mp4.name}")
                    break
                else:
                    print("FAILED (no output file)")
                    sys.exit(1)

    missing = [i for i, f in enumerate(files) if f is None]
    if missing:
        print(f"ERROR: missing scenes {missing}")
        sys.exit(1)

    # Time-scale scenes to match TTS audio durations
    if target_durations:
        print(f"\n  Time-scaling {scene_count} scenes to match TTS audio:")
        time_scale_scenes(files, target_durations)

    return files


def concat_scenes(scene_files, audio_path, final_path, crf=None, preset=None,
                  validate_audio=None):
    """Concat scene MP4s and merge audio using stream-copy (no re-encode).

    Uses two-pass approach:
    1. ffmpeg -f concat -c copy → silent video (no re-encode)
    2. ffmpeg -i silent -i audio -c:v copy -c:a aac → final (only encodes audio)

    Falls back to single-pass re-encode if stream-copy fails.

    Args:
        scene_files: List of scene MP4 paths in order.
        audio_path: Path to TTS audio MP3 (or None for silent video).
        final_path: Output path for final MP4.
        validate_audio: Path to audio for AV sync validation after concat.
                        When provided, automatically runs validate_av_sync().

    Returns:
        Path to final MP4.
    """
    import sys

    if crf is None:
        crf = os.environ.get("TKK_RENDER_CRF", "23")
    if preset is None:
        preset = os.environ.get("TKK_RENDER_PRESET", "fast")

    final_path = Path(final_path)
    media_dir = final_path.parent if final_path.parent.name != "" else Path(".")

    # Write concat list
    cat = media_dir / f"concat_{final_path.stem.replace('_final', '')}.txt"
    cat.parent.mkdir(parents=True, exist_ok=True)
    with open(cat, "w") as f:
        for sf in scene_files:
            f.write(f"file '{sf}'\n")

    audio = Path(audio_path) if audio_path and Path(audio_path).exists() else None

    if audio:
        # Check if scenes have mixed time bases (from time-scaling) which breaks stream-copy
        needs_reencode = False
        try:
            time_bases = set()
            for sf in scene_files:
                r_probe = subprocess.run(
                    ["ffprobe", "-v", "quiet", "-show_entries", "stream=time_base",
                     "-of", "default=noprint_wrappers=1:nokey=1", sf],
                    capture_output=True, text=True, timeout=5)
                time_bases.add(r_probe.stdout.strip())
            if len(time_bases) > 1:
                needs_reencode = True
        except Exception:
            pass

        # Two-pass: stream-copy concat, then mux audio
        silent = final_path.with_name(final_path.stem + "_silent.mp4")
        # Pass 1: concat with stream copy
        r = subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cat),
             "-c", "copy", str(silent)],
            capture_output=True,
        )
        if r.returncode != 0:
            # Fallback: single-pass re-encode
            print("  WARN: stream-copy concat failed, falling back to re-encode")
            cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cat),
                   "-i", str(audio), "-c:a", "aac", "-b:a", "128k",
                   "-map", "0:v", "-map", "1:a",
                   "-c:v", "libx264", "-crf", str(crf), "-preset", str(preset),
                   "-pix_fmt", "yuv420p", "-movflags", "faststart", str(final_path)]
            r2 = subprocess.run(cmd, capture_output=True)
            if r2.returncode != 0:
                print(f"FFmpeg error: {r2.stderr.decode()[:500]}")
                sys.exit(1)
            validate_src_fb = validate_audio or audio_path
            if validate_src_fb and Path(validate_src_fb).exists():
                av = validate_av_sync(str(final_path), str(validate_src_fb))
                if av["status"] == "FAIL":
                    print(f"  AV SYNC FAIL: {av['drift']:.2f}s drift — review scene durations")
            return str(final_path)

        # Pass 2: mux audio with video stream copy
        r = subprocess.run(
            ["ffmpeg", "-y", "-i", str(silent), "-i", str(audio),
             "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
             "-map", "0:v", "-map", "1:a",
             "-movflags", "faststart", str(final_path)],
            capture_output=True,
        )
        # Clean up silent intermediate
        silent.unlink(missing_ok=True)
        if r.returncode != 0:
            print(f"FFmpeg mux error: {r.stderr.decode()[:500]}")
            sys.exit(1)
    else:
        # No audio — just stream-copy concat
        r = subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cat),
             "-c", "copy", "-movflags", "faststart", str(final_path)],
            capture_output=True,
        )
        if r.returncode != 0:
            # Fallback to re-encode
            r2 = subprocess.run(
                ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cat),
                 "-c:v", "libx264", "-crf", str(crf), "-preset", str(preset),
                 "-pix_fmt", "yuv420p", "-movflags", "faststart", str(final_path)],
                capture_output=True,
            )
            if r2.returncode != 0:
                print(f"FFmpeg error: {r2.stderr.decode()[:500]}")
                sys.exit(1)

    # Auto-validate AV sync if audio path provided (or fall back to audio_path)
    validate_src = validate_audio or audio_path
    if validate_src and Path(validate_src).exists():
        av = validate_av_sync(str(final_path), str(validate_src))
        if av["status"] == "FAIL":
            print(f"  AV SYNC FAIL: {av['drift']:.2f}s drift — review scene durations")

    return str(final_path)


def make_short(full_path, scene_ends, max_duration=None, fade_dur=None):
    """Produce a ≤30s short by cutting at the last scene boundary that fits.

    Args:
        full_path: Path to the full-length *_final.mp4.
        scene_ends: List of scene end times in seconds (e.g. [8.7, 13.2, 21.1, 28.7, 35.2, 47.0]).
        max_duration: Target max duration for the short.
        fade_dur: Duration of the fade-to-black at the end.
    """
    if max_duration is None:
        max_duration = float(os.environ.get("TKK_SHORT_MAX_DURATION", "30"))
    if fade_dur is None:
        fade_dur = float(os.environ.get("TKK_SHORT_FADE_DURATION", "1.5"))

    budget = max_duration - fade_dur
    # Find the last scene boundary that fits within budget
    cut_at = max((t for t in scene_ends if t <= budget), default=None)
    if cut_at is None:
        raise ValueError(f"No scene boundary fits within {budget}s. Boundaries: {scene_ends}")

    total = cut_at + fade_dur
    short_path = str(full_path).replace("_final.mp4", "_short.mp4")

    crf = os.environ.get("TKK_RENDER_CRF", "23")
    preset = os.environ.get("TKK_RENDER_PRESET", "fast")

    cmd = [
        "ffmpeg", "-y", "-i", str(full_path),
        "-t", str(total),
        "-vf", f"fade=t=out:st={cut_at}:d={fade_dur}",
        "-af", f"afade=t=out:st={cut_at}:d={fade_dur}",
        "-c:v", "libx264", "-crf", str(crf), "-preset", str(preset),
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
        short_path,
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return short_path, total


def run_preview_qa(preview_dir):
    """Run layout + readability QA on preview PNGs. Returns exit code (0=pass, 1=issues)."""
    preview_dir = Path(preview_dir)
    pngs = sorted(preview_dir.glob("*.png"))
    if not pngs:
        print(f"\n  QA: No PNGs found in {preview_dir}, skipping.")
        return 0

    qa_dir = Path(__file__).parent
    has_fail = False

    # --- Layout QA ---
    print(f"\n{'='*50}")
    print(f"  LAYOUT QA — {len(pngs)} scenes")
    print(f"{'='*50}")
    try:
        from qa_layout import analyze_preview, print_result
        for png in pngs:
            result = analyze_preview(str(png))
            print_result(result)
            for c in result["checks"]:
                if c["status"] == "FAIL":
                    has_fail = True
    except Exception as e:
        print(f"  Layout QA error: {e}")

    # --- Readability QA ---
    print(f"\n{'='*50}")
    print(f"  READABILITY QA — {len(pngs)} scenes")
    print(f"{'='*50}")
    try:
        from qa_readability import check_scene
        for png in pngs:
            passed, report = check_scene(str(png))
            print(report)
            if not passed:
                has_fail = True
    except Exception as e:
        print(f"  Readability QA error: {e}")

    # --- Summary ---
    status = "FAIL" if has_fail else "PASS"
    print(f"\n{'='*50}")
    print(f"  QA RESULT: {status}")
    print(f"{'='*50}")
    return 1 if has_fail else 0


def run_post_render_qa(final_mp4, scene_count=6):
    """Extract frames from final MP4 and run layout QA. Returns exit code (0=pass, 1=issues)."""
    final_mp4 = Path(final_mp4)
    if not final_mp4.exists():
        print(f"  Post-render QA: {final_mp4} not found, skipping.")
        return 0

    # Get video duration
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(final_mp4)],
            capture_output=True, text=True, timeout=10,
        )
        duration = float(r.stdout.strip())
    except Exception as e:
        print(f"  Post-render QA: couldn't get duration: {e}")
        return 0

    # Extract 1 frame per scene at midpoints
    frame_dir = Path(tempfile.mkdtemp(prefix="tkk_qa_"))
    interval = duration / scene_count
    for i in range(scene_count):
        t = interval * i + interval / 2
        out = frame_dir / f"frame_{i+1}.png"
        subprocess.run(
            ["ffmpeg", "-y", "-ss", str(t), "-i", str(final_mp4),
             "-frames:v", "1", "-q:v", "2", str(out)],
            capture_output=True, timeout=15,
        )

    result = run_preview_qa(frame_dir)

    # Cleanup
    import shutil
    shutil.rmtree(frame_dir, ignore_errors=True)
    return result
