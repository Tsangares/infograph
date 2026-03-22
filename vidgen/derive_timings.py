#!/usr/bin/env python3
"""Auto-derive scene boundaries + calibrate animation params from Whisper data.

Takes a Remotion manifest + Whisper word timestamps → produces a timings JSON
with scene_durations, boundaries, and calibrations (e.g. countDuration for Counter scenes).

Usage:
    python3 derive_timings.py remotion/src/manifests/atari_buried.json
    python3 derive_timings.py remotion/src/manifests/atari_buried.json --whisper tts_atari_buried.mp3.json

Output: tts_{topic}_timings.json (in vidgen root)

The calibrations are *suggestions* written to the timings sidecar, NOT modifications
to the manifest. The render pipeline reads them and overrides defaults.
"""

import json
import logging
import re
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="[derive %(levelname)s] %(message)s")
log = logging.getLogger("derive_timings")

VIDGEN = Path(__file__).parent
FPS = 30
TRANSITION_FRAMES = 25  # measureSpring(SPRINGS.gentle) at 30fps
TAIL_S = 0.5            # visual content extends 0.5s past audio (convention)


# ── Number-to-words (reused from qa_remotion_sync.py) ──

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
    """Generate search terms for finding a number in Whisper transcript."""
    terms = []
    s = str(n)
    if unit:
        unit_lower = unit.lower().strip()
        word = _NUMBER_WORDS.get(s)
        if word:
            terms.append(f"{word} {unit_lower}")
        terms.append(f"{s} {unit_lower}")
    word = _NUMBER_WORDS.get(s)
    if word:
        terms.append(word)
    terms.append(s)
    return terms


def _find_word_time(words: list[dict], search_terms: list[str],
                    near: float | None = None) -> float | None:
    """Find when a search term is spoken in the Whisper word list."""
    word_texts = [w["text"].lower().strip().rstrip(".,!?;:") for w in words]
    matches = []

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

    if not matches:
        return None
    matches = sorted(set(matches))
    if near is not None:
        return min(matches, key=lambda t: abs(t - near))
    return matches[0]


# ── Scene boundary detection ──

def _split_sentences(text: str) -> list[str]:
    """Split text into sentences, preserving sentence boundaries.

    Handles abbreviations like E.T., U.S., etc. by not splitting on
    single-letter-dot patterns.
    """
    # Protect abbreviations like E.T., U.S., etc. by replacing dots temporarily
    PLACEHOLDER = "\u00B7"  # middle dot
    protected = re.sub(r'\b([A-Z])\.([A-Z])\.', rf'\1{PLACEHOLDER}\2{PLACEHOLDER}', text)
    # Also protect Mr., Dr., etc.
    protected = re.sub(r'\b(Mr|Mrs|Ms|Dr|St|vs|etc)\.\s', rf'\1{PLACEHOLDER} ', protected)

    # Split on sentence-ending punctuation followed by space
    parts = re.split(r'(?<=[.!?])\s+', protected.strip())

    # Restore dots
    result = [p.replace(PLACEHOLDER, '.').strip() for p in parts if p.strip()]
    return result


def _split_script_into_scenes(tts_script: str, scenes: list[dict]) -> list[str]:
    """Split the ttsScript into per-scene narration segments.

    Strategy: split script into sentences, then assign sentences to scenes
    based on keyword matching between scene content and sentence text.
    Each scene gets at least one sentence.
    """
    num_scenes = len(scenes)
    if num_scenes <= 1:
        return [tts_script]

    sentences = _split_sentences(tts_script)
    if len(sentences) <= num_scenes:
        # Fewer sentences than scenes — distribute what we have
        segments = []
        for i in range(num_scenes):
            if i < len(sentences):
                segments.append(sentences[i])
            else:
                segments.append("")
        return segments

    # Collect keywords from each scene for matching
    scene_keywords = []
    for scene in scenes:
        keywords = set()
        props = scene.get("props", {})
        texts = scene.get("text", [])

        for key in ("title", "subtitle", "description"):
            if key in props:
                val = str(props[key])
                for w in re.findall(r'[A-Za-z]{4,}', val):
                    keywords.add(w.lower())
                # Extract numbers and their word forms
                for d in re.findall(r'\d+', val):
                    keywords.add(d)
                    word = _NUMBER_WORDS.get(d)
                    if word:
                        keywords.add(word)
                    # Year-like numbers: add "twenty fourteen" etc.
                    if len(d) == 4 and d.startswith(('19', '20')):
                        # Common spoken forms
                        keywords.add(d[:2])  # "20", "19"
                        keywords.add(d[2:])  # "14", "82"

        if "unit" in props:
            for w in re.findall(r'[A-Za-z]{3,}', props["unit"]):
                keywords.add(w.lower())

        if "markers" in props:
            for m in props["markers"]:
                for w in re.findall(r'[A-Za-z]{4,}', m.get("label", "")):
                    keywords.add(w.lower())
                # Year digits from markers
                for d in re.findall(r'\d{2,4}', m.get("year", "")):
                    keywords.add(d)

        if "bars" in props:
            for b in props["bars"]:
                label_text = b.get("label", "")
                for w in re.findall(r'[A-Za-z]{4,}', label_text):
                    keywords.add(w.lower())
                for d in re.findall(r'\d+', label_text):
                    keywords.add(d)

        for t in texts:
            content = t.get("content", "")
            for w in re.findall(r'[A-Za-z]{4,}', content):
                keywords.add(w.lower())
            for d in re.findall(r'\d+', content):
                keywords.add(d)
                if len(d) == 4 and d.startswith(('19', '20')):
                    keywords.add(d[:2])
                    keywords.add(d[2:])

        # Scene label too
        label = scene.get("label", "")
        for w in re.findall(r'[A-Za-z]{4,}', label):
            keywords.add(w.lower())

        scene_keywords.append(keywords)

    # Build reverse map: number words → digits for matching
    _word_to_digit = {v: k for k, v in _NUMBER_WORDS.items()}

    # Score each sentence against each scene
    # Then greedily assign sentences to scenes in order
    sentence_assignments = [0] * len(sentences)

    # Start with proportional assignment
    sentences_per_scene = len(sentences) / num_scenes
    for i, _ in enumerate(sentences):
        sentence_assignments[i] = min(int(i / sentences_per_scene), num_scenes - 1)

    # Refine: for each sentence, check if its keywords match a nearby scene better
    for i, sent in enumerate(sentences):
        sent_lower = sent.lower()
        sent_words = set(re.findall(r'[a-z]{4,}', sent_lower))
        sent_digits = set(re.findall(r'\d{2,4}', sent_lower))
        # Add digit equivalents of number words (e.g., "fourteen" → "14")
        for sw in list(sent_words):
            digit = _word_to_digit.get(sw)
            if digit:
                sent_digits.add(digit)
        sent_tokens = sent_words | sent_digits

        base_scene = sentence_assignments[i]
        best_scene = base_scene
        best_score = len(sent_tokens & scene_keywords[base_scene])

        # Only consider adjacent scenes (don't let a sentence jump far)
        for s in range(max(0, base_scene - 1), min(num_scenes, base_scene + 2)):
            score = len(sent_tokens & scene_keywords[s])
            if score > best_score:
                best_score = score
                best_scene = s

        sentence_assignments[i] = best_scene

    # Enforce monotonic assignment (sentences can't go backwards)
    for i in range(1, len(sentences)):
        if sentence_assignments[i] < sentence_assignments[i - 1]:
            sentence_assignments[i] = sentence_assignments[i - 1]

    # Ensure every scene gets at least one sentence
    # Find scenes with no sentences and steal from neighbors
    scene_has_sentence = [False] * num_scenes
    for s in sentence_assignments:
        scene_has_sentence[s] = True

    for s in range(num_scenes):
        if not scene_has_sentence[s]:
            # Find the next sentence assigned to a later scene and reassign it
            for i, assigned in enumerate(sentence_assignments):
                if assigned > s:
                    sentence_assignments[i] = s
                    scene_has_sentence[s] = True
                    break

    # Build segments
    segments = [""] * num_scenes
    for i, sent in enumerate(sentences):
        s = sentence_assignments[i]
        if segments[s]:
            segments[s] += " " + sent
        else:
            segments[s] = sent

    return segments


def _find_segment_time_range(segment: str, words: list[dict],
                              search_after: float = 0.0) -> tuple[float, float]:
    """Find the start and end time of a narration segment in Whisper data.

    Matches the first few words and last few words of the segment against
    the Whisper word list. search_after hints where to start looking.
    """
    if not words or not segment:
        return (0.0, 0.0)

    segment_words = segment.lower().split()
    if not segment_words:
        return (0.0, 0.0)

    word_texts_clean = [re.sub(r'[^\w\d]', '', w["text"].lower().strip()) for w in words]

    # Find start: match first 2-3 words of segment, searching forward from search_after
    start_time = None
    search_words = [re.sub(r'[^\w\d]', '', sw) for sw in segment_words[:3]]
    # Start searching from the word nearest to search_after
    start_idx = 0
    for idx, w in enumerate(words):
        if w["offset_s"] >= search_after - 0.5:
            start_idx = idx
            break

    for i in range(start_idx, len(word_texts_clean)):
        if word_texts_clean[i] == search_words[0]:
            if len(search_words) > 1:
                match = True
                for j in range(1, min(len(search_words), len(word_texts_clean) - i)):
                    if word_texts_clean[i + j] != search_words[j]:
                        match = False
                        break
                if match:
                    start_time = words[i]["offset_s"]
                    break
            else:
                start_time = words[i]["offset_s"]
                break

    # If multi-word match failed, try matching a distinctive word from search_after
    _COMMON = {"the", "a", "an", "in", "on", "of", "to", "and", "is", "it", "was",
               "for", "but", "not", "with", "this", "that", "from", "they", "had",
               "by", "at", "or", "be", "as", "are", "were", "been", "have", "has",
               "its", "all", "one", "two", "no", "so", "if", "up", "out", "then"}
    if start_time is None:
        # Try ALL words from the segment (not just first 3), preferring distinctive ones
        all_seg_words = [re.sub(r'[^\w\d]', '', sw) for sw in segment_words[:10]]
        distinctive = [sw for sw in all_seg_words if sw and sw not in _COMMON]
        fallback_words = distinctive if distinctive else [w for w in all_seg_words if w][:3]
        for fw in fallback_words:
            for i in range(start_idx, len(word_texts_clean)):
                if word_texts_clean[i] == fw:
                    start_time = words[i]["offset_s"]
                    break
            if start_time is not None:
                break

    # Last resort: try from beginning (shouldn't normally happen)
    if start_time is None:
        for i in range(len(word_texts_clean)):
            if word_texts_clean[i] == search_words[0]:
                start_time = words[i]["offset_s"]
                break

    # Find end: match last 2-3 words of segment, searching forward from start
    end_time = None
    search_end = [re.sub(r'[^\w\d]', '', sw) for sw in segment_words[-3:]]
    # Search forward from start_time position
    search_from = 0
    if start_time is not None:
        for idx, w in enumerate(words):
            if w["offset_s"] >= start_time:
                search_from = idx
                break

    for i in range(search_from, len(word_texts_clean)):
        if word_texts_clean[i] == search_end[-1]:
            if len(search_end) > 1:
                match = True
                for j in range(1, min(len(search_end), i + 1)):
                    if word_texts_clean[i - j] != search_end[-(j + 1)]:
                        match = False
                        break
                if match:
                    end_time = words[i]["end_s"]
                    break
            else:
                end_time = words[i]["end_s"]
                break

    if start_time is None:
        start_time = search_after
    if end_time is None:
        end_time = words[-1]["end_s"] if words else 0.0

    return (start_time, end_time)


def _calibrate_counter(scene_idx: int, props: dict, scene_start: float,
                       scene_dur: float, scene_dur_frames: int,
                       words: list[dict]) -> dict | None:
    """Auto-calibrate countDuration for a Counter scene.

    Counter.tsx: interpolate(frame, [0, round(durationInFrames * countDuration)], [start, end])
    No hidden delays. countDuration = fraction of durationInFrames where target is reached.

    scene_dur_frames: actual durationInFrames the component will see (includes
    overlap extension for the last scene).
    """
    end_val = props.get("end", 0)
    unit = props.get("unit", "")

    if end_val == 0:
        return None

    search_terms = _number_to_search_terms(
        int(end_val) if end_val == int(end_val) else end_val, unit
    )
    scene_mid = scene_start + scene_dur / 2
    narration_time = _find_word_time(words, search_terms, near=scene_mid)

    if narration_time is None:
        log.warning(f"Scene {scene_idx}: could not find '{end_val} {unit}' in narration")
        return None

    # How far into the scene is this moment?
    t_in_scene = narration_time - scene_start
    if t_in_scene <= 0 or t_in_scene >= scene_dur:
        log.warning(f"Scene {scene_idx}: narration of '{end_val}' at {narration_time:.1f}s "
                    f"is outside scene window [{scene_start:.1f}-{scene_start + scene_dur:.1f}s]")
        t_in_scene = max(0.1 * scene_dur, min(t_in_scene, 0.95 * scene_dur))

    # countDuration = target_frame / durationInFrames
    # The component sees durationInFrames = scene_dur_frames (which includes
    # overlap extension for the last scene), so we divide by that.
    target_frame = t_in_scene * FPS
    count_duration = target_frame / scene_dur_frames
    count_duration = max(0.02, min(0.95, count_duration))

    log.info(f"Scene {scene_idx}: '{end_val} {unit}' narrated at {narration_time:.1f}s → "
             f"countDuration={count_duration:.2f}")

    return {"countDuration": round(count_duration, 2)}


# ── Main derivation ──

def derive_timings(manifest_path: str, whisper_path: str = None) -> str:
    """Derive scene timings and calibrations from manifest + Whisper data.

    Args:
        manifest_path: Path to Remotion manifest JSON
        whisper_path: Path to Whisper JSON (auto-detected if omitted)

    Returns:
        Path to the output timings JSON
    """
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text())
    topic = manifest.get("topic", manifest_path.stem)

    # Auto-detect whisper path
    if whisper_path is None:
        whisper_path = VIDGEN / f"tts_{topic}.mp3.json"
    else:
        whisper_path = Path(whisper_path)

    if not whisper_path.exists():
        log.error(f"Whisper data not found: {whisper_path}")
        return ""

    whisper_data = json.loads(whisper_path.read_text())
    words = whisper_data.get("words", [])
    if not words:
        log.error("Whisper data has no words")
        return ""

    tts_script = manifest.get("ttsScript", "")
    scenes = manifest.get("scenes", [])
    num_scenes = len(scenes)
    total_audio = words[-1]["end_s"]

    log.info(f"Deriving timings for '{topic}': {num_scenes} scenes, "
             f"{len(words)} words, {total_audio:.1f}s audio")

    # Step 1: Split script into per-scene segments
    segments = _split_script_into_scenes(tts_script, scenes)
    for i, seg in enumerate(segments):
        log.info(f"  Scene {i}: \"{seg[:60]}...\"" if len(seg) > 60 else f"  Scene {i}: \"{seg}\"")

    # Step 2: Find scene start times using first words of each segment
    scene_start_times = [0.0]  # Scene 0 always starts at 0
    search_after = 0.0
    for i in range(1, num_scenes):
        seg = segments[i]
        start, _ = _find_segment_time_range(seg, words, search_after=search_after)
        scene_start_times.append(start)
        search_after = start
        log.info(f"  Scene {i} starts at {start:.2f}s: \"{seg[:50]}...\"" if len(seg) > 50
                 else f"  Scene {i} starts at {start:.2f}s: \"{seg}\"")

    # Step 3: Compute durations from start times
    boundaries = []
    scene_durations = []

    for i in range(num_scenes):
        scene_start = scene_start_times[i]
        if i == num_scenes - 1:
            scene_end = total_audio
        else:
            scene_end = scene_start_times[i + 1]

        if i > 0:
            boundaries.append(round(scene_start, 2))

        duration = scene_end - scene_start
        duration = max(1.5, duration)
        scene_durations.append(round(duration, 2))

    # Adjust last scene to absorb rounding slack + add 0.5s visual tail
    used = sum(scene_durations[:-1])
    scene_durations[-1] = round(total_audio - used + TAIL_S, 2)
    if scene_durations[-1] < 1.5:
        scene_durations[-1] = 1.5

    log.info(f"  Durations: {scene_durations} "
             f"(sum={sum(scene_durations):.2f}s, audio={total_audio:.2f}s, "
             f"tail={TAIL_S}s)")

    # Step 4: Calibrate animation params
    # Compute actual durationInFrames per scene as the component sees it.
    # Video.tsx extends the last scene by totalOverlapFrames to compensate
    # for TransitionSeries eating visual duration.
    num_transitions = max(0, num_scenes - 1)
    total_overlap_frames = num_transitions * TRANSITION_FRAMES

    calibrations = {}
    scene_starts = []
    t = 0.0
    for d in scene_durations:
        scene_starts.append(t)
        t += d

    for i, scene in enumerate(scenes):
        scene_type = scene.get("type", "")
        props = scene.get("props", {})

        # Actual durationInFrames the component will see
        dur_frames = round(scene_durations[i] * FPS)
        if i == num_scenes - 1:
            dur_frames += total_overlap_frames

        if scene_type == "counter":
            cal = _calibrate_counter(i, props, scene_starts[i], scene_durations[i],
                                     dur_frames, words)
            if cal:
                calibrations[f"scene_{i}"] = cal

    # Step 5: Build notes
    notes = {}
    t = 0.0
    for i, seg in enumerate(segments):
        start = t
        end = start + scene_durations[i]
        preview = seg[:70].replace('\n', ' ')
        notes[f"scene_{i+1}"] = f"{start:.2f}-{end:.2f}: {preview}"
        t = end

    # Step 6: Write output
    output_path = VIDGEN / f"tts_{topic}_timings.json"
    timings = {
        "scene_durations": scene_durations,
        "boundaries": boundaries,
        "total_audio": round(total_audio, 2),
        "tail_s": TAIL_S,
        "transition_frames": TRANSITION_FRAMES,
        "source": "whisper_derived",
        "calibrations": calibrations,
        "notes": notes,
    }
    output_path.write_text(json.dumps(timings, indent=2) + "\n")
    log.info(f"Wrote {output_path}")

    if calibrations:
        log.info(f"Calibrations: {json.dumps(calibrations)}")

    return str(output_path)


# ── CLI ──

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Auto-derive scene timings from Whisper data")
    parser.add_argument("manifest", help="Path to Remotion manifest JSON")
    parser.add_argument("--whisper", help="Path to Whisper JSON (auto-detected if omitted)")
    args = parser.parse_args()

    result = derive_timings(args.manifest, args.whisper)
    if not result:
        sys.exit(1)
