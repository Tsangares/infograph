#!/usr/bin/env python3
"""Batch pipeline: generate_assets → generate_tts → render_video → review_render.

Usage:
    python produce.py easter_island.py
    python produce.py easter_island.py --skip-assets --skip-tts
    python produce.py easter_island.py --encoder nvenc --output final.mp4
"""

import argparse
import importlib.util
import os
import subprocess
import sys
import time
from pathlib import Path

VIDGEN_DIR = Path(__file__).parent.resolve()


def load_screenplay(screenplay_path: str) -> dict:
    """Import a screenplay .py file and return its `screenplay` dict."""
    path = Path(screenplay_path).resolve()
    if not path.exists():
        print(f"[produce] ERROR: screenplay not found: {path}", file=sys.stderr)
        sys.exit(1)

    spec = importlib.util.spec_from_file_location("_screenplay_mod", str(path))
    mod = importlib.util.module_from_spec(spec)

    # Screenplays do os.chdir to their own dir — save/restore cwd
    orig_cwd = os.getcwd()
    try:
        spec.loader.exec_module(mod)
    finally:
        os.chdir(orig_cwd)

    if not hasattr(mod, "screenplay"):
        print(f"[produce] ERROR: {path.name} has no 'screenplay' variable", file=sys.stderr)
        sys.exit(1)

    return mod.screenplay


def run_step(label: str, cmd: list[str]) -> subprocess.CompletedProcess:
    """Run a subprocess step, printing header and timing."""
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    t0 = time.time()
    result = subprocess.run(cmd, cwd=str(VIDGEN_DIR))
    elapsed = time.time() - t0
    if result.returncode != 0:
        print(f"[produce] WARNING: {label} exited with code {result.returncode}")
    else:
        print(f"[produce] {label} completed in {elapsed:.1f}s")
    return result


def count_assets(screenplay: dict) -> int:
    """Count how many asset files are referenced and exist."""
    count = 0
    assets_dir = VIDGEN_DIR / "assets"
    for scene in screenplay.get("scenes", []):
        bg = scene.get("background", "")
        if bg and (assets_dir / bg).exists():
            count += 1
        for layer in scene.get("layers", []):
            src = layer.get("src", "")
            if src and (assets_dir / src).exists():
                count += 1
    return count


def get_tts_path(screenplay_path: str) -> Path:
    """Derive the TTS output path matching generate_tts.py convention."""
    sp = Path(screenplay_path)
    return sp.parent / f"tts_{sp.stem}.mp3"


def get_tts_duration(tts_path: Path) -> float:
    """Get audio duration in seconds via ffprobe."""
    if not tts_path.exists():
        return 0.0
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(tts_path)],
            capture_output=True, text=True
        )
        return float(result.stdout.strip())
    except (ValueError, FileNotFoundError):
        return 0.0


def main():
    parser = argparse.ArgumentParser(
        description="Full video production pipeline")
    parser.add_argument("screenplay", help="Path to screenplay .py file")
    parser.add_argument("--skip-assets", action="store_true",
                        help="Skip asset generation step")
    parser.add_argument("--skip-tts", action="store_true",
                        help="Skip TTS generation step")
    parser.add_argument("--skip-review", action="store_true",
                        help="Skip review step")
    parser.add_argument("--skip-enhance", action="store_true",
                        help="Skip animation enhancement analysis")
    parser.add_argument("--encoder", choices=["auto", "nvenc", "cpu"],
                        default="auto", help="Video encoder")
    parser.add_argument("--output", "-o", default=None,
                        help="Output video filename")
    args = parser.parse_args()

    screenplay_path = str(Path(args.screenplay).resolve())
    sp_name = Path(screenplay_path).stem
    output = args.output or f"{sp_name}.mp4"

    print(f"[produce] Pipeline: {sp_name}")
    print(f"[produce] Screenplay: {screenplay_path}")
    print(f"[produce] Output: {output}")

    pipeline_start = time.time()
    py = sys.executable

    # ── Step 1: Generate assets ──
    if not args.skip_assets:
        run_step("Step 1/4 — Generate Assets",
                 [py, str(VIDGEN_DIR / "generate_assets.py"), screenplay_path])
    else:
        print("\n[produce] Skipping asset generation")

    # ── Step 2: Generate TTS ──
    if not args.skip_tts:
        run_step("Step 2/4 — Generate TTS",
                 [py, str(VIDGEN_DIR / "generate_tts.py"), screenplay_path])
    else:
        print("[produce] Skipping TTS generation")

    # ── Step 2.5: Enhancement analysis (optional) ──
    if not args.skip_enhance:
        enhance_script = VIDGEN_DIR / "enhance_animations.py"
        if enhance_script.exists():
            print(f"\n{'='*60}")
            print(f"  Step 2.5 — Analyze dead time & suggest enhancements")
            print(f"{'='*60}")
            t_enh = time.time()
            try:
                from enhance_animations import analyze_dead_time
                sp_path = Path(screenplay_path)
                results = analyze_dead_time(sp_path)
                dead_scenes = [r for r in results if r["dead_seconds"] >= 3.0]
                if dead_scenes:
                    print(f"[produce] {len(dead_scenes)} scene(s) with >3s dead time:")
                    for r in dead_scenes:
                        print(f"  {r['class']}: {r['dead_seconds']:.1f}s dead "
                              f"(coded={r['coded_duration']:.1f}s target={r['target_duration']:.1f}s)")
                        for s in r.get("suggested_enhancements", []):
                            print(f"    -> {s['type']}: {s['reason']}")
                else:
                    print("[produce] No significant dead time detected")
            except Exception as e:
                print(f"[produce] Enhancement analysis skipped: {e}")
            print(f"[produce] Analysis completed in {time.time() - t_enh:.1f}s")
    else:
        print("\n[produce] Skipping enhancement analysis")

    # ── Step 3: Render video ──
    print(f"\n{'='*60}")
    print(f"  Step 3/4 — Render Video")
    print(f"{'='*60}")
    t_render = time.time()

    # Import screenplay module (triggers os.chdir, render_video needs it)
    screenplay = load_screenplay(screenplay_path)

    # For manim screenplays, run the screenplay directly instead of the old vidgen renderer
    screenplay_file = Path(screenplay_path)
    render_cmd = [py, str(screenplay_file)]
    result = subprocess.run(render_cmd, cwd=str(VIDGEN_DIR))
    render_time = time.time() - t_render
    stats = {"encoder_used": "manim+ffmpeg"}
    if result.returncode != 0:
        print(f"[produce] ERROR: render failed with code {result.returncode}", file=sys.stderr)

    # ── Step 4: Review render ──
    review_ok = None
    review_script = VIDGEN_DIR / "review_render.py"
    if not args.skip_review and review_script.exists():
        result = run_step("Step 4/4 — Review Render",
                          [py, str(review_script), output])
        review_ok = result.returncode == 0
    elif args.skip_review:
        print("\n[produce] Skipping review")
    else:
        print("\n[produce] Skipping review (review_render.py not found)")

    # ── Summary ──
    pipeline_time = time.time() - pipeline_start
    asset_count = count_assets(screenplay)
    tts_path = get_tts_path(screenplay_path)
    tts_dur = get_tts_duration(tts_path)
    output_path = Path(output).resolve()
    size_mb = output_path.stat().st_size / (1024 * 1024) if output_path.exists() else 0

    review_str = {True: "PASS", False: "FAIL", None: "skipped"}[review_ok]

    print(f"\n{'='*60}")
    print(f"  PRODUCTION SUMMARY")
    print(f"{'='*60}")
    print(f"  Screenplay:   {sp_name}")
    print(f"  Assets:       {asset_count} files")
    print(f"  TTS duration: {tts_dur:.1f}s")
    print(f"  Render time:  {render_time:.1f}s")
    print(f"  Encoder:      {stats.get('encoder_used', 'unknown')}")
    print(f"  Review:       {review_str}")
    print(f"  Output:       {output_path} ({size_mb:.1f} MB)")
    print(f"  Total time:   {pipeline_time:.1f}s")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
