#!/usr/bin/env python3
"""Deterministic narration-animation sync checker for Remotion videos.

Validates that visual numbers, years, and keywords appear on screen
in sync with when the narrator speaks them. No rendering required —
reads manifest JSON + Whisper timestamps + scene timings and does
pure math to compute what each component displays at any frame.

Usage:
    python3 qa_remotion_sync.py atari_buried
    python3 qa_remotion_sync.py --json atari_buried
    python3 qa_remotion_sync.py --all

Requires:
    - remotion/src/manifests/{topic}.json — scene manifest
    - tts_{topic}.mp3.json — Whisper word-level timestamps
    - tts_{topic}_timings.json — scene boundaries/durations
"""

import json
import re
import sys
from pathlib import Path

VIDGEN = Path(__file__).parent
FPS = 30
TRANSITION_FRAMES = 25  # measureSpring(SPRINGS.gentle) at 30fps

WARN_THRESHOLD = 1.5  # seconds
FAIL_THRESHOLD = 3.0  # seconds


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


# ── Number-to-words mapping for Whisper matching ──

_NUMBER_WORDS = {
    "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
    "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine",
    "10": "ten", "11": "eleven", "12": "twelve", "13": "thirteen",
    "14": "fourteen", "15": "fifteen", "16": "sixteen", "17": "seventeen",
    "18": "eighteen", "19": "nineteen", "20": "twenty", "30": "thirty",
    "40": "forty", "50": "fifty", "60": "sixty", "70": "seventy",
    "80": "eighty", "90": "ninety", "100": "hundred", "1000": "thousand",
}


def _number_to_search_terms(n: int, unit: str = "") -> list[str]:
    """Generate search terms for finding a number in Whisper transcript.

    E.g., 2 with unit "BILLION" -> ["two billion", "2 billion", "2"]
    E.g., 1982 -> ["1982", "nineteen eighty two"]
    """
    terms = []
    s = str(n)

    # Number + unit combo
    if unit:
        unit_lower = unit.lower().strip()
        word = _NUMBER_WORDS.get(s)
        if word:
            terms.append(f"{word} {unit_lower}")
        terms.append(f"{s} {unit_lower}")

    # The number as spoken
    word = _NUMBER_WORDS.get(s)
    if word:
        terms.append(word)

    # Raw digits (Whisper sometimes transcribes as digits)
    terms.append(s)

    # For years like 1982, 2014
    if 1000 <= n <= 2100:
        terms.append(s)

    return terms


def _find_all_word_times(words: list[dict], search_terms: list[str]) -> list[float]:
    """Find ALL occurrences of search terms in the Whisper word list.

    Returns list of offset_s values for all matches.
    """
    matches = []
    word_texts = [w["text"].lower().strip().rstrip(".,!?;:") for w in words]

    for term in search_terms:
        term_lower = term.lower().strip()
        term_parts = term_lower.split()

        if len(term_parts) > 1:
            for i in range(len(word_texts) - len(term_parts) + 1):
                match = True
                for j, tp in enumerate(term_parts):
                    wt = re.sub(r'[^\w\d]', '', word_texts[i + j])
                    tp_clean = re.sub(r'[^\w\d]', '', tp)
                    if wt != tp_clean:
                        match = False
                        break
                if match:
                    matches.append(words[i]["offset_s"])
        else:
            term_clean = re.sub(r'[^\w\d]', '', term_lower)
            for i, wt in enumerate(word_texts):
                wt_clean = re.sub(r'[^\w\d]', '', wt)
                if wt_clean == term_clean:
                    matches.append(words[i]["offset_s"])

    return sorted(set(matches))


def _find_word_time(words: list[dict], search_terms: list[str],
                    near: float | None = None) -> float | None:
    """Find when a search term is spoken in the Whisper word list.

    If `near` is provided, returns the occurrence closest to that time.
    Otherwise returns the first occurrence.
    """
    all_times = _find_all_word_times(words, search_terms)
    if not all_times:
        return None
    if near is not None:
        return min(all_times, key=lambda t: abs(t - near))
    return all_times[0]


def _extract_numbers_from_text(text: str) -> list[str]:
    """Extract significant numbers from text content."""
    raw = re.findall(r'\b(\d[\d,]*)\b', text)
    return [n.replace(",", "") for n in raw if len(n.replace(",", "")) >= 2]


# ── Component math replication ──

def _counter_value_at_time(t_in_scene: float, scene_dur_frames: int,
                           start: float, end: float, count_duration: float) -> float:
    """Replicate Counter.tsx interpolation logic.

    Counter.tsx: interpolate(frame, [0, round(durationInFrames * countDuration)], [start, end])
    No hidden delays. countDuration is the exact fraction where target is reached.

    scene_dur_frames: the actual durationInFrames the component sees (includes
    overlap extension for the last scene).
    """
    anim_frames = max(1, round(scene_dur_frames * count_duration))
    frame = round(t_in_scene * FPS)
    progress = clamp(frame / anim_frames)
    return start + progress * (end - start)


def _timeline_marker_visible_time(i: int, scene_dur: float) -> float:
    """Compute when timeline marker i becomes visible (seconds into scene).

    Replicates Timeline.tsx proportional stagger logic.
    """
    dur_frames = round(scene_dur * FPS)
    base_delay = max(4, round(dur_frames * 0.05))
    stagger = max(4, round(dur_frames * 0.06))
    # Marker is "visible" when its spring starts + ~8 frames for opacity fade
    visible_frame = base_delay + i * stagger + 8
    return visible_frame / FPS


def _barchart_label_visible_time(i: int, scene_dur: float) -> float:
    """Compute when bar chart label i becomes readable.

    Replicates BarChart.tsx proportional stagger + label fade logic.
    """
    dur_frames = round(scene_dur * FPS)
    delay = i * max(2, round(dur_frames * 0.03))
    label_fade_end = max(delay + 4, round(dur_frames * 0.1))
    return (delay + label_fade_end) / FPS / 2  # midpoint of fade


def _population_drop_value_at_time(t_in_scene: float, scene_dur: float,
                                   start_val: float, end_val: float) -> float:
    """Replicate PopulationDrop.tsx interpolation logic."""
    dur_frames = round(scene_dur * FPS)
    drop_start = round(dur_frames * 0.15)
    drop_end = round(dur_frames * 0.7)
    frame = round(t_in_scene * FPS)

    progress = clamp((frame - drop_start) / (drop_end - drop_start))
    return start_val + progress * (end_val - start_val)


# ── Check implementations ──

def check_counter_sync(scene_idx: int, props: dict, scene_start: float,
                       scene_dur: float, scene_dur_frames: int,
                       words: list[dict]) -> list[dict]:
    """Check 1: Counter number sync.

    scene_dur_frames: actual durationInFrames the component sees (includes
    overlap extension for the last scene).
    """
    results = []
    start = props.get("start", 0)
    end = props.get("end", 0)
    unit = props.get("unit", "")
    count_duration = props.get("countDuration", 0.6)

    # Counter reaches target at frame round(scene_dur_frames * countDuration)
    anim_frames = max(1, round(scene_dur_frames * count_duration))
    anim_end_s = scene_start + anim_frames / FPS

    # When does the narrator say the target number?
    search_terms = _number_to_search_terms(int(end) if end == int(end) else end, unit)
    scene_mid = scene_start + scene_dur / 2
    narration_time = _find_word_time(words, search_terms, near=scene_mid)

    if narration_time is None:
        results.append({
            "check": "counter_sync",
            "scene": scene_idx + 1,
            "status": "SKIP",
            "detail": f"Could not find '{end}{' ' + unit if unit else ''}' in narration",
        })
        return results

    t_in_scene = narration_time - scene_start
    if t_in_scene < 0:
        results.append({
            "check": "counter_sync",
            "scene": scene_idx + 1,
            "status": "FAIL",
            "detail": (f"Narrator says '{end}' at {narration_time:.1f}s but "
                       f"scene doesn't start until {scene_start:.1f}s"),
            "narration_time": narration_time,
            "scene_start": scene_start,
        })
        return results

    visual_value = _counter_value_at_time(t_in_scene, scene_dur_frames, start, end, count_duration)

    if end == int(end):
        display_value = round(visual_value)
        target_int = int(end)
        if display_value != target_int:
            delta = anim_end_s - narration_time
            status = "FAIL" if abs(delta) > FAIL_THRESHOLD else "WARN" if abs(delta) > WARN_THRESHOLD else "PASS"
            results.append({
                "check": "counter_sync",
                "scene": scene_idx + 1,
                "status": status,
                "detail": (f"Counter shows {display_value} when narrator says "
                           f"'{target_int}{' ' + unit if unit else ''}' at {narration_time:.1f}s "
                           f"(counter reaches {target_int} at {anim_end_s:.1f}s, "
                           f"delta={delta:+.1f}s)"),
                "visual_value": display_value,
                "target_value": target_int,
                "narration_time": narration_time,
                "anim_end_time": anim_end_s,
                "delta": delta,
            })
            return results

    results.append({
        "check": "counter_sync",
        "scene": scene_idx + 1,
        "status": "PASS",
        "detail": (f"Counter shows {round(visual_value)} when narrator says "
                   f"'{int(end)}{' ' + unit if unit else ''}' at {narration_time:.1f}s"),
    })
    return results


def check_timeline_sync(scene_idx: int, props: dict, scene_start: float,
                        scene_dur: float, words: list[dict]) -> list[dict]:
    """Check 2: Timeline year sync.

    Timeline markers are contextual labels — they don't need frame-precise sync
    like counters. Use wider tolerance: FAIL only if narration is >1 scene away.
    """
    results = []
    markers = props.get("markers", [])

    # Timeline markers are reference labels — narrator often doesn't say each date.
    # Only flag if the nearest narration mention is >2 scenes away.
    label_fail = scene_dur * 2 + FAIL_THRESHOLD
    label_warn = scene_dur + WARN_THRESHOLD

    for i, marker in enumerate(markers):
        year_text = marker.get("year", "")
        year_digits = re.findall(r'\d+', year_text)
        if not year_digits:
            continue

        year_str = year_digits[0]
        search_terms = [year_str]
        if len(year_str) == 2 and int(year_str) > 50:
            search_terms.insert(0, f"19{year_str}")
        elif len(year_str) == 2 and int(year_str) <= 50:
            search_terms.insert(0, f"20{year_str}")

        scene_mid = scene_start + scene_dur / 2
        narration_time = _find_word_time(words, search_terms, near=scene_mid)
        if narration_time is None:
            continue

        visible_time = scene_start + _timeline_marker_visible_time(i, scene_dur)
        delta = visible_time - narration_time

        if abs(delta) > label_fail:
            status = "FAIL"
        elif abs(delta) > label_warn:
            status = "WARN"
        else:
            status = "PASS"

        direction = "visual leads" if delta < 0 else "visual lags"
        results.append({
            "check": "timeline_year_sync",
            "scene": scene_idx + 1,
            "marker": year_text,
            "status": status,
            "detail": (f"'{year_text}' visible at {visible_time:.1f}s, "
                       f"narrated at {narration_time:.1f}s "
                       f"(delta={delta:+.1f}s, {direction})"),
            "delta": delta,
        })

    return results


def check_headline_sync(scene_idx: int, props: dict, scene_start: float,
                        scene_dur: float, words: list[dict]) -> list[dict]:
    """Check 3: Headline keyword sync."""
    results = []
    title = props.get("title", "")

    # Extract significant words from title (skip short words)
    title_words = [w for w in re.findall(r'\w+', title) if len(w) > 3]
    if not title_words:
        return results

    # Check if any key title word is spoken during this scene's window
    scene_end = scene_start + scene_dur
    scene_mid = scene_start + scene_dur / 2
    for tw in title_words[:3]:  # Check first 3 significant words
        narration_time = _find_word_time(words, [tw.lower()], near=scene_mid)
        if narration_time is None:
            continue

        # Is the narration within this scene's window?
        if narration_time < scene_start - FAIL_THRESHOLD:
            results.append({
                "check": "headline_sync",
                "scene": scene_idx + 1,
                "status": "WARN",
                "detail": (f"Headline word '{tw}' narrated at {narration_time:.1f}s "
                           f"but scene starts at {scene_start:.1f}s "
                           f"(delta={scene_start - narration_time:+.1f}s)"),
            })
        elif narration_time > scene_end + FAIL_THRESHOLD:
            results.append({
                "check": "headline_sync",
                "scene": scene_idx + 1,
                "status": "WARN",
                "detail": (f"Headline word '{tw}' narrated at {narration_time:.1f}s "
                           f"but scene ends at {scene_end:.1f}s "
                           f"(delta={narration_time - scene_end:+.1f}s)"),
            })
        else:
            results.append({
                "check": "headline_sync",
                "scene": scene_idx + 1,
                "status": "PASS",
                "detail": (f"Headline word '{tw}' narrated at {narration_time:.1f}s "
                           f"within scene window [{scene_start:.1f}-{scene_end:.1f}s]"),
            })
            break  # One PASS is enough

    return results


def check_barchart_sync(scene_idx: int, props: dict, scene_start: float,
                        scene_dur: float, words: list[dict]) -> list[dict]:
    """Check 4: BarChart value sync.

    Bar labels are contextual (like "1982", "1983") — use wider tolerance.
    """
    results = []
    bars = props.get("bars", [])

    # Wider tolerance for static labels
    label_fail = scene_dur + FAIL_THRESHOLD
    label_warn = scene_dur / 2 + WARN_THRESHOLD

    for i, bar in enumerate(bars):
        label = bar.get("label", "")
        value = bar.get("value", 0)

        search_terms = []
        label_digits = re.findall(r'\d+', label)
        if label_digits:
            search_terms.extend(label_digits)
        search_terms.append(label.lower())

        scene_mid = scene_start + scene_dur / 2
        narration_time = _find_word_time(words, search_terms, near=scene_mid)
        if narration_time is None:
            continue

        visible_time = scene_start + _barchart_label_visible_time(i, scene_dur)
        delta = visible_time - narration_time

        if abs(delta) > label_fail:
            status = "FAIL"
        elif abs(delta) > label_warn:
            status = "WARN"
        else:
            status = "PASS"

        results.append({
            "check": "barchart_sync",
            "scene": scene_idx + 1,
            "bar": label,
            "status": status,
            "detail": (f"Bar '{label}' ({value}) visible at {visible_time:.1f}s, "
                       f"narrated at {narration_time:.1f}s (delta={delta:+.1f}s)"),
            "delta": delta,
        })

    return results


def check_scene_alignment(scene_idx: int, scene: dict, scene_start: float,
                          scene_dur: float, words: list[dict]) -> list[dict]:
    """Check 5: Scene-narration alignment via text overlays."""
    results = []
    text_overlays = scene.get("text", [])
    scene_end = scene_start + scene_dur

    for overlay in text_overlays:
        content = overlay.get("content", "")
        # Extract significant numbers from overlay text
        numbers = _extract_numbers_from_text(content)

        for num_str in numbers:
            search_terms = [num_str]
            # Add word form for small numbers
            word = _NUMBER_WORDS.get(num_str)
            if word:
                search_terms.insert(0, word)

            scene_mid = scene_start + scene_dur / 2
            narration_time = _find_word_time(words, search_terms, near=scene_mid)
            if narration_time is None:
                continue

            if narration_time < scene_start - FAIL_THRESHOLD or narration_time > scene_end + FAIL_THRESHOLD:
                results.append({
                    "check": "scene_text_sync",
                    "scene": scene_idx + 1,
                    "status": "FAIL",
                    "detail": (f"Text '{content}' (number {num_str}) narrated at "
                               f"{narration_time:.1f}s but scene window is "
                               f"[{scene_start:.1f}-{scene_end:.1f}s]"),
                })
            else:
                results.append({
                    "check": "scene_text_sync",
                    "scene": scene_idx + 1,
                    "status": "PASS",
                    "detail": (f"Text number '{num_str}' narrated at {narration_time:.1f}s "
                               f"within scene [{scene_start:.1f}-{scene_end:.1f}s]"),
                })

    return results


def check_population_drop_sync(scene_idx: int, props: dict, scene_start: float,
                               scene_dur: float, words: list[dict]) -> list[dict]:
    """Check 6: PopulationDrop number sync."""
    results = []
    start_val = props.get("startValue", 0)
    end_val = props.get("endValue", 0)
    unit = props.get("unit", "")

    for val, label in [(start_val, "start"), (end_val, "end")]:
        search_terms = _number_to_search_terms(int(val) if val == int(val) else val, unit)
        scene_mid = scene_start + scene_dur / 2
        narration_time = _find_word_time(words, search_terms, near=scene_mid)
        if narration_time is None:
            continue

        scene_end = scene_start + scene_dur
        if narration_time < scene_start - FAIL_THRESHOLD or narration_time > scene_end + FAIL_THRESHOLD:
            results.append({
                "check": "population_drop_sync",
                "scene": scene_idx + 1,
                "status": "FAIL",
                "detail": (f"PopulationDrop {label} value {val} narrated at "
                           f"{narration_time:.1f}s but scene is "
                           f"[{scene_start:.1f}-{scene_end:.1f}s]"),
            })
        else:
            results.append({
                "check": "population_drop_sync",
                "scene": scene_idx + 1,
                "status": "PASS",
                "detail": (f"PopulationDrop {label} value {val} narrated at "
                           f"{narration_time:.1f}s within scene"),
            })

    return results


# ── Main runner ──

def run_sync_qa(topic: str) -> dict:
    """Run all sync checks for a Remotion video.

    Returns dict with:
        topic, status (PASS/WARN/FAIL), checks[], fail_count, warn_count
    """
    manifest_path = VIDGEN / "remotion" / "src" / "manifests" / f"{topic}.json"
    whisper_path = VIDGEN / f"tts_{topic}.mp3.json"
    timings_path = VIDGEN / f"tts_{topic}_timings.json"

    # Validate inputs
    missing = []
    if not manifest_path.exists():
        missing.append(f"manifest: {manifest_path}")
    if not whisper_path.exists():
        missing.append(f"whisper: {whisper_path}")
    if not timings_path.exists():
        missing.append(f"timings: {timings_path}")

    if missing:
        return {
            "topic": topic,
            "status": "SKIP",
            "detail": f"Missing files: {', '.join(missing)}",
            "checks": [],
            "fail_count": 0,
            "warn_count": 0,
        }

    manifest = json.loads(manifest_path.read_text())
    whisper_data = json.loads(whisper_path.read_text())
    timings = json.loads(timings_path.read_text())

    words = whisper_data.get("words", [])
    scene_durations = timings.get("scene_durations", [])
    scenes = manifest.get("scenes", [])

    # Apply calibrations from timings (same as render.mts does)
    calibrations = timings.get("calibrations", {})
    for key, cal in calibrations.items():
        idx = int(key.replace("scene_", ""))
        if idx < len(scenes) and "countDuration" in cal:
            scenes[idx].setdefault("props", {})["countDuration"] = cal["countDuration"]

    if len(scene_durations) != len(scenes):
        return {
            "topic": topic,
            "status": "FAIL",
            "detail": f"Scene count mismatch: {len(scenes)} scenes, {len(scene_durations)} durations",
            "checks": [],
            "fail_count": 1,
            "warn_count": 0,
        }

    # Compute scene start times and actual durationInFrames per scene.
    # Video.tsx extends the last scene by totalOverlapFrames to compensate
    # for TransitionSeries eating into visual content.
    num_transitions = max(0, len(scenes) - 1)
    total_overlap_frames = num_transitions * TRANSITION_FRAMES

    scene_starts = []
    t = 0.0
    for d in scene_durations:
        scene_starts.append(t)
        t += d

    # Run all checks
    all_checks = []

    for i, scene in enumerate(scenes):
        scene_type = scene.get("type", "")
        props = scene.get("props", {})
        start = scene_starts[i]
        dur = scene_durations[i]

        # Actual durationInFrames the component sees inside Remotion
        dur_frames = round(dur * FPS)
        if i == len(scenes) - 1:
            dur_frames += total_overlap_frames

        if scene_type == "counter":
            all_checks.extend(check_counter_sync(i, props, start, dur, dur_frames, words))
        elif scene_type == "timeline":
            all_checks.extend(check_timeline_sync(i, props, start, dur, words))
        elif scene_type == "headline":
            all_checks.extend(check_headline_sync(i, props, start, dur, words))
        elif scene_type == "barChart":
            all_checks.extend(check_barchart_sync(i, props, start, dur, words))
        elif scene_type == "populationDrop":
            all_checks.extend(check_population_drop_sync(i, props, start, dur, words))

        # Always check text overlays for any scene type
        all_checks.extend(check_scene_alignment(i, scene, start, dur, words))

    # Check 7: AV duration — visual content vs audio duration
    # Video.tsx extends the last scene by the total transition overlap,
    # so visual content fills the full sum(scene_durations).
    total_scene_s = sum(scene_durations)
    visual_duration = total_scene_s
    last_word_time = words[-1]["end_s"] if words else 0

    if last_word_time > visual_duration + 2.0:
        all_checks.append({
            "check": "av_duration",
            "scene": 0,
            "status": "FAIL",
            "detail": (f"Visual content ends at {visual_duration:.1f}s but narration "
                       f"continues until {last_word_time:.1f}s "
                       f"({last_word_time - visual_duration:.1f}s of black screen)"),
        })
    elif last_word_time > visual_duration + 0.5:
        all_checks.append({
            "check": "av_duration",
            "scene": 0,
            "status": "WARN",
            "detail": (f"Visual content ends at {visual_duration:.1f}s, narration at "
                       f"{last_word_time:.1f}s (delta={last_word_time - visual_duration:.1f}s)"),
        })
    else:
        all_checks.append({
            "check": "av_duration",
            "scene": 0,
            "status": "PASS",
            "detail": (f"Visual duration {visual_duration:.1f}s covers narration "
                       f"ending at {last_word_time:.1f}s"),
        })

    fail_count = sum(1 for c in all_checks if c["status"] == "FAIL")
    warn_count = sum(1 for c in all_checks if c["status"] == "WARN")

    if fail_count > 0:
        status = "FAIL"
    elif warn_count > 0:
        status = "WARN"
    else:
        status = "PASS"

    return {
        "topic": topic,
        "status": status,
        "checks": all_checks,
        "fail_count": fail_count,
        "warn_count": warn_count,
    }


def format_results(result: dict) -> str:
    """Format sync QA results as human-readable text."""
    lines = [f"\n=== Remotion Sync QA: {result['topic']} ===\n"]

    if result["status"] == "SKIP":
        lines.append(f"  SKIP: {result['detail']}")
        return "\n".join(lines)

    if result.get("detail"):
        lines.append(f"  {result['detail']}")

    for check in result["checks"]:
        marker = {"PASS": "+", "WARN": "!", "FAIL": "X", "SKIP": "-"}[check["status"]]
        lines.append(f"  [{marker}] Scene {check['scene']}: {check['detail']}")

    lines.append(f"\n  Overall: {result['status']} "
                 f"({result['fail_count']} fails, {result['warn_count']} warns, "
                 f"{len(result['checks'])} checks)")

    return "\n".join(lines)


# ── CLI ──

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Remotion narration-animation sync QA")
    parser.add_argument("topic", nargs="?", help="Topic name (e.g., atari_buried)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--all", action="store_true", help="Run on all manifests")
    args = parser.parse_args()

    if args.all:
        manifest_dir = VIDGEN / "remotion" / "src" / "manifests"
        topics = [p.stem for p in sorted(manifest_dir.glob("*.json"))]
        all_results = []
        for topic in topics:
            result = run_sync_qa(topic)
            all_results.append(result)
            if not args.json:
                print(format_results(result))

        if args.json:
            print(json.dumps(all_results, indent=2))
        else:
            total_fail = sum(r["fail_count"] for r in all_results)
            total_warn = sum(r["warn_count"] for r in all_results)
            print(f"\n{'='*50}")
            print(f"Total: {len(topics)} videos, {total_fail} fails, {total_warn} warns")
    elif args.topic:
        result = run_sync_qa(args.topic)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(format_results(result))
        sys.exit(1 if result["fail_count"] > 0 else 0)
    else:
        parser.print_help()
