#!/usr/bin/env python3
"""
Word-Trigger Resolver for TKK Video Rendering

Takes a word-triggered manifest + Whisper JSON and resolves all
anchor words to absolute timestamps. Outputs a resolved timeline
that Remotion can consume directly.

Usage:
    python resolve_word_triggers.py [topic]
    python resolve_word_triggers.py radium
"""

import json
import sys
from pathlib import Path
from dataclasses import dataclass, field

FPS = 30
SCENE_TAIL_BUFFER_S = 0.4  # hold scene visuals after final anchor word ends
VIDGEN_DIR = Path(__file__).parent


@dataclass
class WordHit:
    text: str
    offset_s: float
    end_s: float
    index: int  # position in word list


@dataclass
class ResolvedElement:
    element: dict
    trigger_s: float      # absolute time the animation starts
    trigger_frame: int    # absolute frame number
    scene_id: str
    anchor_word: str
    anchor_time_s: float  # when the anchor word is spoken
    attack_s: float       # delay after anchor


@dataclass
class ResolvedScene:
    scene_id: str
    label: str
    scene_type: str
    start_s: float
    end_s: float
    start_frame: int
    end_frame: int
    duration_s: float
    duration_frames: int
    elements: list = field(default_factory=list)


def load_whisper(topic: str) -> list[WordHit]:
    """Load Whisper word-level timestamps."""
    path = VIDGEN_DIR / f"tts_{topic}.mp3.json"
    data = json.loads(path.read_text())
    return [
        WordHit(text=w["text"], offset_s=w["offset_s"], end_s=w["end_s"], index=i)
        for i, w in enumerate(data["words"])
    ]


def load_whisper_from_path(path: Path) -> list[WordHit]:
    """Load Whisper word-level timestamps from a specific path."""
    data = json.loads(Path(path).read_text())
    return [
        WordHit(text=w["text"], offset_s=w["offset_s"], end_s=w["end_s"], index=i)
        for i, w in enumerate(data["words"])
    ]


def load_manifest(topic: str) -> dict:
    """Load word-triggered manifest from remotion/src/manifests/{topic}.json."""
    path = VIDGEN_DIR / "remotion" / "src" / "manifests" / f"{topic}.json"
    return json.loads(path.read_text())


def find_word(words: list[WordHit], anchor: str, after_index: int = 0) -> WordHit | None:
    """
    Find a word in the Whisper data. Matches case-insensitively.
    Strips punctuation for matching but returns the original.

    after_index: only match words at or after this index (for disambiguation).
    """
    anchor_clean = anchor.lower().rstrip(".,!?;:")

    for w in words:
        if w.index < after_index:
            continue
        w_clean = w.text.lower().rstrip(".,!?;:")
        if w_clean == anchor_clean:
            return w
    return None


def find_word_occurrence(words: list[WordHit], anchor: str, occurrence: int = 1) -> WordHit | None:
    """Find the Nth occurrence of a word (1-indexed)."""
    anchor_clean = anchor.lower().rstrip(".,!?;:")
    count = 0
    for w in words:
        w_clean = w.text.lower().rstrip(".,!?;:")
        if w_clean == anchor_clean:
            count += 1
            if count == occurrence:
                return w
    return None


def resolve(manifest: dict, words: list[WordHit]) -> list[ResolvedScene]:
    """
    Resolve all word anchors in the manifest to absolute timestamps.

    Returns a list of ResolvedScene objects with all timing computed.
    """
    scenes = []
    last_scene_end_idx = 0  # Track where we are in the word list

    for scene_def in manifest["scenes"]:
        scene_id = scene_def["id"]

        # Resolve scene boundaries from anchor words
        start_word = find_word(words, scene_def["scene_anchor"], after_index=last_scene_end_idx)
        end_word = find_word(words, scene_def["scene_end_anchor"], after_index=last_scene_end_idx)

        if not start_word:
            print(f"  WARN: scene '{scene_id}' start anchor '{scene_def['scene_anchor']}' not found after index {last_scene_end_idx}")
            continue
        if not end_word:
            print(f"  WARN: scene '{scene_id}' end anchor '{scene_def['scene_end_anchor']}' not found after index {last_scene_end_idx}")
            continue

        scene_start = start_word.offset_s
        scene_end = end_word.end_s + SCENE_TAIL_BUFFER_S

        scene = ResolvedScene(
            scene_id=scene_id,
            label=scene_def["label"],
            scene_type=scene_def["type"],
            start_s=scene_start,
            end_s=scene_end,
            start_frame=int(scene_start * FPS),
            end_frame=int(scene_end * FPS),
            duration_s=scene_end - scene_start,
            duration_frames=int((scene_end - scene_start) * FPS),
        )

        # Resolve each element's anchor
        for elem in scene_def["elements"]:
            anchor = elem.get("anchor")
            attack = elem.get("attack", 0.0)

            if not anchor:
                print(f"  WARN: element in scene '{scene_id}' has no anchor")
                continue

            # Find the anchor word within the scene's word range
            anchor_word = find_word(words, anchor, after_index=start_word.index)
            if not anchor_word or anchor_word.index > end_word.index:
                # Try finding it anywhere (might be slightly before scene start)
                anchor_word = find_word(words, anchor, after_index=max(0, start_word.index - 3))

            if not anchor_word:
                print(f"  WARN: anchor '{anchor}' not found for element in scene '{scene_id}'")
                continue

            # Boundary check: reject anchors that resolved far outside scene
            if anchor_word.index > end_word.index + 2:
                print(f"  WARN: anchor '{anchor}' in scene '{scene_id}' resolved to "
                      f"{anchor_word.offset_s:.2f}s (word index {anchor_word.index}), "
                      f"but scene ends at {end_word.end_s:.2f}s (word index {end_word.index}). "
                      f"Clamping to scene start.")
                trigger_s = scene_start + attack
                resolved = ResolvedElement(
                    element=elem,
                    trigger_s=trigger_s,
                    trigger_frame=int(trigger_s * FPS),
                    scene_id=scene_id,
                    anchor_word=f"[CLAMPED:{anchor}]",
                    anchor_time_s=scene_start,
                    attack_s=attack,
                )
                scene.elements.append(resolved)
                continue

            trigger_s = anchor_word.offset_s + attack

            resolved = ResolvedElement(
                element=elem,
                trigger_s=trigger_s,
                trigger_frame=int(trigger_s * FPS),
                scene_id=scene_id,
                anchor_word=anchor_word.text,
                anchor_time_s=anchor_word.offset_s,
                attack_s=attack,
            )
            scene.elements.append(resolved)

            # Handle counter end anchor
            if elem.get("count_end_anchor"):
                end_anchor = find_word(words, elem["count_end_anchor"], after_index=anchor_word.index)
                if end_anchor:
                    resolved.element["_count_end_s"] = end_anchor.end_s
                    resolved.element["_count_duration_s"] = end_anchor.end_s - trigger_s

        # Sort elements by trigger time
        scene.elements.sort(key=lambda e: e.trigger_s)

        # Post-resolve: check for elements that will never appear
        for elem in scene.elements:
            rel_frame = elem.trigger_frame - scene.start_frame
            if rel_frame > scene.duration_frames:
                print(f"  WARN: element '{elem.anchor_word}' in scene '{scene.scene_id}' "
                      f"has delay_frames={rel_frame} but scene only has "
                      f"{scene.duration_frames} frames — element will never appear")

        scenes.append(scene)
        last_scene_end_idx = end_word.index + 1

    return scenes


def check_overlaps(scenes: list[ResolvedScene]):
    """
    Check for zone overlaps within each scene.
    Two elements in the same zone that are both visible at the same time = overlap.
    """
    issues = []

    for scene in scenes:
        zone_elements: dict[str, list[ResolvedElement]] = {}

        for elem in scene.elements:
            zone = elem.element.get("zone", "MID")
            zone_elements.setdefault(zone, []).append(elem)

        for zone, elems in zone_elements.items():
            if len(elems) <= 1:
                continue

            for i, a in enumerate(elems):
                for b in elems[i+1:]:
                    # If both are text in the same zone and one doesn't replace
                    a_hold = a.element.get("hold", "until_scene_end")

                    if a_hold == "until_replaced" and b.element.get("replaces_zone"):
                        continue  # b explicitly replaces a, no overlap

                    if a_hold == "until_scene_end":
                        gap = b.trigger_s - a.trigger_s
                        if gap < 0.5:
                            issues.append(
                                f"  OVERLAP: scene '{scene.scene_id}' zone {zone}: "
                                f"'{a.element.get('content', a.element.get('svg', '?'))}' "
                                f"(t={a.trigger_s:.2f}s) and "
                                f"'{b.element.get('content', b.element.get('svg', '?'))}' "
                                f"(t={b.trigger_s:.2f}s) — only {gap:.2f}s apart"
                            )

    return issues


GAP_THRESHOLD_S = 0.5  # auto-extend scenes to cover gaps larger than this


def close_gaps(scenes: list[ResolvedScene], words: list[WordHit]):
    """
    Auto-extend scenes to cover narration gaps between them.

    When scene N ends at "poison." but scene N+1 doesn't start until "again.",
    the words "Then he did it" fall in a gap — the viewer sees the scene fading
    out while the narrator is still mid-thought. This extends scene N's end_s
    to cover those gap words, keeping the scene visually alive longer.
    """
    for i in range(len(scenes) - 1):
        gap = scenes[i + 1].start_s - scenes[i].end_s
        if gap > GAP_THRESHOLD_S:
            # Find words spoken during the gap
            gap_words = [w for w in words
                         if w.offset_s >= scenes[i].end_s - 0.1
                         and w.end_s <= scenes[i + 1].start_s + 0.1]
            if gap_words:
                new_end = gap_words[-1].end_s + SCENE_TAIL_BUFFER_S
                # Don't extend past the next scene's start
                new_end = min(new_end, scenes[i + 1].start_s)
                old_end = scenes[i].end_s
                scenes[i].end_s = new_end
                scenes[i].duration_s = new_end - scenes[i].start_s
                scenes[i].duration_frames = int(scenes[i].duration_s * FPS)
                scenes[i].end_frame = int(new_end * FPS)
                print(f"  AUTO-EXTEND: scene '{scenes[i].scene_id}' "
                      f"{old_end:.2f}s → {new_end:.2f}s "
                      f"(+{new_end - old_end:.2f}s, covers {len(gap_words)} gap words)")


def generate_remotion_input(scenes: list[ResolvedScene], manifest: dict, audio_duration: float = None) -> dict:
    """
    Generate the resolved input that Remotion would consume.

    This converts word-triggered timing back into frame-relative delays
    that Remotion components already understand.

    Key: each scene's duration is EXTENDED to cover the gap after it
    (silence between narration sections). This ensures the video timeline
    matches the audio timeline exactly. Without this, gaps get eaten by
    TransitionSeries and the video ends before the narration finishes.
    """
    remotion_scenes = []
    scene_durations = []

    for i, scene in enumerate(scenes):
        # Extend scene duration to cover the gap AFTER it.
        # For intermediate scenes: extend to the start of the next scene.
        # For the last scene: extend to audio end (if known) or use scene end + 1s padding.
        if i < len(scenes) - 1:
            extended_end = scenes[i + 1].start_s
        else:
            # Last scene: extend to audio duration or add 1s tail
            extended_end = audio_duration if audio_duration else scene.end_s + 1.0

        extended_duration_s = extended_end - scene.start_s
        extended_duration_frames = int(extended_duration_s * FPS)

        scene_durations.append(extended_duration_s)

        # Convert absolute triggers to scene-relative frame offsets
        resolved_elements = []
        for elem in scene.elements:
            rel_s = elem.trigger_s - scene.start_s
            rel_frame = int(rel_s * FPS)

            resolved = {
                **elem.element,
                "_resolved": {
                    "delay_frames": rel_frame,
                    "delay_s": round(rel_s, 3),
                    "anchor_word": elem.anchor_word,
                    "anchor_time_s": round(elem.anchor_time_s, 3),
                    "absolute_frame": elem.trigger_frame,
                    "absolute_s": round(elem.trigger_s, 3),
                },
            }
            resolved_elements.append(resolved)

        remotion_scenes.append({
            "id": scene.scene_id,
            "label": scene.label,
            "type": scene.scene_type,
            "start_s": round(scene.start_s, 3),
            "end_s": round(scene.end_s, 3),
            "duration_s": round(extended_duration_s, 3),
            "duration_frames": extended_duration_frames,
            "elements": resolved_elements,
        })

    total_duration = sum(scene_durations)
    total_frames = sum(s["duration_frames"] for s in remotion_scenes)

    return {
        "topic": manifest["topic"],
        "colors": manifest["colors"],
        "fps": FPS,
        "total_duration_s": round(total_duration, 3),
        "total_frames": total_frames,
        "scene_durations": [round(d, 3) for d in scene_durations],
        "scenes": remotion_scenes,
    }


def print_timeline(scenes: list[ResolvedScene]):
    """Print a human-readable timeline of all animations."""
    print("\n" + "=" * 70)
    print("WORD-TRIGGERED ANIMATION TIMELINE")
    print("=" * 70)

    for scene in scenes:
        print(f"\n{'─' * 60}")
        print(f"SCENE: {scene.label} ({scene.scene_id})")
        print(f"  Time: {scene.start_s:.2f}s → {scene.end_s:.2f}s ({scene.duration_s:.2f}s / {scene.duration_frames} frames)")
        print(f"  Elements:")

        for elem in scene.elements:
            etype = elem.element.get("type", "?")
            content = elem.element.get("content", elem.element.get("svg", elem.element.get("label", "?")))
            zone = elem.element.get("zone", "MID")
            enter = elem.element.get("enter", "fade")
            hold = elem.element.get("hold", "until_scene_end")
            rel_s = elem.trigger_s - scene.start_s

            print(f"    [{elem.trigger_s:6.2f}s] (+{rel_s:.2f}s) {etype:18s} | \"{content}\"")
            print(f"             anchor=\"{elem.anchor_word}\" ({elem.anchor_time_s:.2f}s) + attack={elem.attack_s:.2f}s | zone={zone} enter={enter} hold={hold}")

            if elem.element.get("_count_duration_s"):
                print(f"             counter runs for {elem.element['_count_duration_s']:.2f}s (ends at {elem.element['_count_end_s']:.2f}s)")

    print(f"\n{'=' * 70}")


def resolve_word_triggers(manifest_path: str, whisper_path: str = None) -> str:
    """Resolve word triggers for a manifest. Callable from other modules.

    Args:
        manifest_path: Path to the word-triggered manifest JSON
        whisper_path: Path to the Whisper JSON (auto-detected if None)

    Returns:
        Path to the resolved JSON output file
    """
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text())
    topic = manifest["topic"]

    if whisper_path:
        words = load_whisper_from_path(Path(whisper_path))
    else:
        words = load_whisper(topic)

    print(f"  Loaded {len(words)} words from Whisper ({words[0].offset_s:.2f}s -> {words[-1].end_s:.2f}s)")

    scenes = resolve(manifest, words)
    print(f"  Resolved {len(scenes)} scenes, {sum(len(s.elements) for s in scenes)} elements")

    close_gaps(scenes, words)

    issues = check_overlaps(scenes)
    if issues:
        print(f"\n  OVERLAP WARNINGS ({len(issues)}):")
        for issue in issues:
            print(issue)
    else:
        print("  No zone overlaps detected")

    # Get audio duration for last-scene padding
    audio_duration = words[-1].end_s if words else None
    audio_path = VIDGEN_DIR / f"tts_{topic}.mp3"
    if audio_path.exists():
        try:
            import subprocess
            r = subprocess.run(
                ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)],
                capture_output=True, text=True, timeout=10,
            )
            audio_duration = float(r.stdout.strip())
        except Exception:
            pass

    remotion_input = generate_remotion_input(scenes, manifest, audio_duration)

    output_path = VIDGEN_DIR / f"{topic}_resolved.json"
    output_path.write_text(json.dumps(remotion_input, indent=2))
    print(f"\nResolved manifest written to: {output_path}")
    print(f"  Audio duration: {audio_duration:.2f}s, video duration: {remotion_input['total_duration_s']:.2f}s")

    return str(output_path)


def main():
    topic = sys.argv[1] if len(sys.argv) > 1 else "radium"

    print(f"Resolving word triggers for '{topic}'...")

    words = load_whisper(topic)
    print(f"  Loaded {len(words)} words from Whisper ({words[0].offset_s:.2f}s -> {words[-1].end_s:.2f}s)")

    manifest = load_manifest(topic)
    print(f"  Loaded manifest: {len(manifest['scenes'])} scenes")

    scenes = resolve(manifest, words)
    print(f"  Resolved {len(scenes)} scenes, {sum(len(s.elements) for s in scenes)} elements")

    # Check for overlaps
    issues = check_overlaps(scenes)
    if issues:
        print(f"\n  OVERLAP WARNINGS ({len(issues)}):")
        for issue in issues:
            print(issue)
    else:
        print("  No zone overlaps detected")

    # Print timeline
    print_timeline(scenes)

    # Get audio duration
    audio_duration = words[-1].end_s
    audio_path = VIDGEN_DIR / f"tts_{topic}.mp3"
    if audio_path.exists():
        try:
            import subprocess
            r = subprocess.run(
                ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)],
                capture_output=True, text=True, timeout=10,
            )
            audio_duration = float(r.stdout.strip())
        except Exception:
            pass

    # Generate Remotion input
    remotion_input = generate_remotion_input(scenes, manifest, audio_duration)

    output_path = VIDGEN_DIR / f"{topic}_resolved.json"
    output_path.write_text(json.dumps(remotion_input, indent=2))
    print(f"\nResolved manifest written to: {output_path}")
    print(f"  Audio duration: {audio_duration:.2f}s, video duration: {remotion_input['total_duration_s']:.2f}s")


if __name__ == "__main__":
    main()
