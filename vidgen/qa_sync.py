#!/usr/bin/env python3
"""QA Sync — Detect narration-animation timing mismatches in TKK screenplays.

Checks:
1. AV DRIFT     — final video duration vs TTS audio duration
2. DEAD TIME    — scene where animations finish early, leaving static frame while narration continues
3. OVERFLOW     — scene where coded animations exceed allocated scene time (will be time-scaled/crushed)
4. NUMBER SYNC  — visual numbers/years shown in a different scene than when they're spoken
5. SCENE BUDGET — scene allocated <1.5s (too short for meaningful animation)

Usage:
    python3 qa_sync.py                          # audit all complete screenplays
    python3 qa_sync.py nihilist_trap_manim.py   # audit one screenplay
    python3 qa_sync.py --json                   # JSON output for dashboard integration
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

VIDGEN = Path(__file__).parent
DEAD_TIME_THRESHOLD = 3.0      # seconds of unaccounted time before flagging
OVERFLOW_THRESHOLD = 2.0       # seconds of excess animation before flagging
DRIFT_WARN = 0.5               # AV drift warn threshold
DRIFT_FAIL = 2.0               # AV drift fail threshold
MIN_SCENE_DURATION = 2.5       # scenes shorter than this are suspicious
SCENE_FAIL_DURATION = 2.0      # scenes shorter than this are unusable
NUMBER_MIN_DIGITS = 2           # minimum digits to count as a "number" (skip single digits)


def _get_duration(filepath: Path) -> float | None:
    """Get media file duration via ffprobe."""
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(filepath)],
            capture_output=True, text=True, timeout=10,
        )
        return float(r.stdout.strip())
    except Exception:
        return None


def _extract_numbers(text: str) -> list[str]:
    """Extract significant numbers from text (years, stats, counts)."""
    # Match numbers with 2+ digits, including comma-separated (e.g. "200,000")
    raw = re.findall(r'\b(\d[\d,]+)\b', text)
    return [n.replace(",", "") for n in raw if len(n.replace(",", "")) >= NUMBER_MIN_DIGITS]


def _parse_docstring_scenes(content: str) -> list[dict]:
    """Parse VTT cues from docstring into scene timing data."""
    m = re.search(r'^"""(.*?)"""', content, re.DOTALL)
    if not m:
        return []
    doc = m.group(1)
    scenes = []
    pattern = r'Scene\s+(\d+)\s+(\w[^(]*)\(([^)]+)\):(.*?)(?=Scene\s+\d+|\Z)'
    for match in re.finditer(pattern, doc, re.DOTALL):
        num, label, timing_str, cues_text = match.groups()
        # Parse duration from timing string: "0.0–5.0s = 5.00s" or "0.0-5.0s = 5.00s"
        dur_match = re.search(r'=\s*([\d.]+)s', timing_str)
        if dur_match:
            duration = float(dur_match.group(1))
        else:
            range_match = re.search(r'([\d.]+)\s*[–-]\s*([\d.]+)', timing_str)
            duration = float(range_match.group(2)) - float(range_match.group(1)) if range_match else 0

        # Parse individual cue lines
        cue_lines = []
        for line in cues_text.strip().split("\n"):
            line = line.strip()
            cue_match = re.match(r'([\d.]+)\s+\(([\d.]+)\)\s+(.+)', line)
            if cue_match:
                abs_time = float(cue_match.group(1))
                rel_time = float(cue_match.group(2))
                text = cue_match.group(3)
                cue_lines.append({"abs": abs_time, "rel": rel_time, "text": text})

        narration_text = " ".join(c["text"] for c in cue_lines)
        scenes.append({
            "num": int(num),
            "label": label.strip(),
            "duration": duration,
            "cues": cue_lines,
            "narration_text": narration_text,
            "narration_numbers": _extract_numbers(narration_text),
        })
    return scenes


def _parse_scene_code(content: str) -> list[dict]:
    """Parse scene class code to extract animation timing and visual text."""
    classes = re.findall(r'class\s+(Scene\d+\w*)\(Scene\):', content)
    sections = re.split(r'class\s+Scene\d+\w*\(Scene\):', content)[1:]
    results = []
    for cls, section in zip(classes, sections):
        # DURATION attribute
        dur_match = re.search(r'DURATION\s*=\s*([\d.]+)', section)
        coded_duration = float(dur_match.group(1)) if dur_match else None

        # Sum run_times from self.play() calls
        run_times = [float(r) for r in re.findall(r'run_time\s*=\s*([\d.]+)', section)]
        # Sum self.wait() calls
        waits = [float(w) for w in re.findall(r'self\.wait\s*\(\s*([\d.]+)', section)]

        anim_time = sum(run_times)
        wait_time = sum(waits)

        # Extract visual text content (numbers shown on screen)
        text_calls = re.findall(
            r'(?:Text|safe_text|MathTex|Tex)\s*\(\s*[f]?["\']([^"\']*)["\']', section
        )
        visual_numbers = []
        for t in text_calls:
            visual_numbers.extend(_extract_numbers(t))

        # Check for dynamic padding pattern
        has_padding = "target - t" in section or "target-t" in section

        results.append({
            "class": cls,
            "coded_duration": coded_duration,
            "anim_time": round(anim_time, 2),
            "wait_time": round(wait_time, 2),
            "total_coded": round(anim_time + wait_time, 2),
            "has_padding": has_padding,
            "visual_numbers": visual_numbers,
            "text_calls": text_calls,
        })
    return results


def _get_scene_durations(stem: str, content: str) -> list[float] | None:
    """Get actual scene durations from timings file, or docstring."""
    # Try timings sidecar first
    timings_file = VIDGEN / f"tts_{stem}_timings.json"
    if timings_file.exists():
        data = json.loads(timings_file.read_text())
        return data.get("scene_durations")

    # Fall back to docstring
    scenes = _parse_docstring_scenes(content)
    if scenes:
        return [s["duration"] for s in scenes]

    return None


def audit_screenplay(screenplay_path: Path) -> dict:
    """Run all sync checks on a screenplay. Returns structured results."""
    content = screenplay_path.read_text()
    stem = screenplay_path.stem.replace("_manim", "")
    final_path = VIDGEN / f"{stem}_final.mp4"
    tts_path = VIDGEN / f"tts_{stem}.mp3"

    result = {
        "screenplay": screenplay_path.name,
        "stem": stem,
        "has_final": final_path.exists(),
        "has_tts": tts_path.exists(),
        "checks": [],
    }

    # -- CHECK 1: AV DRIFT --
    if final_path.exists() and tts_path.exists():
        vid_dur = _get_duration(final_path)
        audio_dur = _get_duration(tts_path)
        if vid_dur and audio_dur:
            drift = abs(vid_dur - audio_dur)
            if drift > DRIFT_FAIL:
                status = "FAIL"
            elif drift > DRIFT_WARN:
                status = "WARN"
            else:
                status = "PASS"
            result["checks"].append({
                "name": "av_drift",
                "status": status,
                "detail": f"video={vid_dur:.1f}s audio={audio_dur:.1f}s drift={drift:.1f}s",
                "drift": round(drift, 2),
                "video_duration": round(vid_dur, 2),
                "audio_duration": round(audio_dur, 2),
            })

    # Get scene durations
    scene_durs = _get_scene_durations(stem, content)
    doc_scenes = _parse_docstring_scenes(content)
    code_scenes = _parse_scene_code(content)

    if not scene_durs or not code_scenes:
        result["checks"].append({
            "name": "parse",
            "status": "SKIP",
            "detail": "Could not parse scene durations or code",
        })
        result["verdict"] = result["checks"][0]["status"] if result["checks"] else "PASS"
        result["fail_count"] = sum(1 for c in result["checks"] if c["status"] == "FAIL")
        result["warn_count"] = sum(1 for c in result["checks"] if c["status"] == "WARN")
        return result

    # -- CHECK 2 & 3: DEAD TIME and OVERFLOW per scene --
    for i, code in enumerate(code_scenes):
        if i >= len(scene_durs):
            break
        target = scene_durs[i]

        # -- CHECK 5: SCENE BUDGET --
        if target < SCENE_FAIL_DURATION and target > 0:
            result["checks"].append({
                "name": "scene_budget",
                "status": "FAIL",
                "detail": f"{code['class']}: only {target:.1f}s allocated — too short to render",
                "scene": i + 1,
                "target": round(target, 2),
            })
        elif target < MIN_SCENE_DURATION and target > 0:
            result["checks"].append({
                "name": "scene_budget",
                "status": "WARN",
                "detail": f"{code['class']}: only {target:.1f}s allocated — too short for meaningful animation",
                "scene": i + 1,
                "target": round(target, 2),
            })

        total_coded = code["total_coded"]

        # Dead time: target much larger than coded animations
        dead = target - total_coded
        if dead > DEAD_TIME_THRESHOLD and target > 2.0:
            result["checks"].append({
                "name": "dead_time",
                "status": "WARN",
                "detail": f"{code['class']}: {dead:.1f}s of static frame (target={target:.1f}s, coded={total_coded:.1f}s)",
                "scene": i + 1,
                "dead_seconds": round(dead, 2),
                "target": round(target, 2),
                "coded": round(total_coded, 2),
            })

        # Overflow: coded animations exceed target
        overflow = total_coded - target
        if overflow > OVERFLOW_THRESHOLD and target > 0:
            result["checks"].append({
                "name": "overflow",
                "status": "WARN",
                "detail": f"{code['class']}: {overflow:.1f}s overflow (target={target:.1f}s, coded={total_coded:.1f}s) — will be time-scaled",
                "scene": i + 1,
                "overflow_seconds": round(overflow, 2),
                "target": round(target, 2),
                "coded": round(total_coded, 2),
            })

    # -- CHECK 4: NUMBER SYNC --
    if doc_scenes and code_scenes:
        for i, code in enumerate(code_scenes):
            if i >= len(doc_scenes):
                break
            doc = doc_scenes[i]
            for vnum in code["visual_numbers"]:
                # Check if this number is mentioned in THIS scene's narration
                if vnum in doc["narration_numbers"]:
                    continue
                # Check if it's mentioned in ANY scene's narration
                for j, other_doc in enumerate(doc_scenes):
                    if j == i:
                        continue
                    if vnum in other_doc["narration_numbers"]:
                        result["checks"].append({
                            "name": "number_sync",
                            "status": "WARN",
                            "detail": f"{code['class']} shows '{vnum}' but narration says it in Scene {j+1} ({other_doc['label']})",
                            "scene": i + 1,
                            "narration_scene": j + 1,
                            "number": vnum,
                        })
                        break

    # -- CHECK 6: BEAT SYNC (word-level alignment) --
    word_timing_path = VIDGEN / f"tts_{stem}.mp3.json"
    if word_timing_path.exists():
        try:
            from qa_beat_sync import check_beat_sync
            beat_checks = check_beat_sync(screenplay_path, word_timing_path)
            for bc in beat_checks:
                if bc["status"] in ("FAIL", "WARN"):
                    result["checks"].append(bc)
        except Exception as e:
            result["checks"].append({
                "name": "beat_sync",
                "status": "SKIP",
                "detail": f"Beat sync error: {e}",
            })

    # Summary
    fails = sum(1 for c in result["checks"] if c["status"] == "FAIL")
    warns = sum(1 for c in result["checks"] if c["status"] == "WARN")
    if fails > 0:
        result["verdict"] = "FAIL"
    elif warns > 0:
        result["verdict"] = "WARN"
    else:
        result["verdict"] = "PASS"
    result["fail_count"] = fails
    result["warn_count"] = warns

    return result


def audit_all(only_complete: bool = True) -> list[dict]:
    """Audit all screenplays."""
    results = []
    for f in sorted(VIDGEN.glob("*_manim.py"), key=lambda p: p.stat().st_mtime, reverse=True):
        stem = f.stem.replace("_manim", "")
        if only_complete and not (VIDGEN / f"{stem}_final.mp4").exists():
            continue
        results.append(audit_screenplay(f))
    return results


def print_report(results: list[dict]):
    """Print human-readable audit report."""
    total = len(results)
    passed = sum(1 for r in results if r["verdict"] == "PASS")
    warned = sum(1 for r in results if r["verdict"] == "WARN")
    failed = sum(1 for r in results if r["verdict"] == "FAIL")

    print(f"\n{'='*60}")
    print(f"  QA SYNC AUDIT — {total} videos")
    print(f"  PASS: {passed}  WARN: {warned}  FAIL: {failed}")
    print(f"{'='*60}\n")

    # Show failures first, then warnings
    for r in sorted(results, key=lambda x: ({"FAIL": 0, "WARN": 1, "PASS": 2, "SKIP": 3}[x["verdict"]], x["stem"])):
        issues = [c for c in r["checks"] if c["status"] in ("FAIL", "WARN")]
        if not issues:
            continue
        icon = "\033[91mFAIL\033[0m" if r["verdict"] == "FAIL" else "\033[93mWARN\033[0m"
        print(f"[{icon}] {r['stem']}")
        for c in issues:
            prefix = "\033[91m  FAIL\033[0m" if c["status"] == "FAIL" else "\033[93m  WARN\033[0m"
            print(f"  {prefix} {c['name']}: {c['detail']}")
        print()

    if passed == total:
        print("All videos passed sync checks.\n")


if __name__ == "__main__":
    os.chdir(VIDGEN)
    args = sys.argv[1:]
    json_mode = "--json" in args
    args = [a for a in args if a != "--json"]

    if args:
        # Audit specific file(s)
        results = []
        for arg in args:
            p = VIDGEN / arg
            if not p.exists():
                p = VIDGEN / f"{arg}_manim.py"
            if p.exists():
                results.append(audit_screenplay(p))
            else:
                print(f"Not found: {arg}", file=sys.stderr)
    else:
        results = audit_all(only_complete=True)

    if json_mode:
        print(json.dumps(results, indent=2))
    else:
        print_report(results)
