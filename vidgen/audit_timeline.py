#!/usr/bin/env python3
"""
Word-Triggered Animation Auditor

Generates a frame-by-frame audit of what's visible on screen at any given time.
Shows zone occupancy, overlap conflicts, and timing issues.

Usage:
    python audit_timeline.py [topic] [--interval 2.0]
"""

import json
import sys
from pathlib import Path
from dataclasses import dataclass, field

FPS = 30
VIDGEN_DIR = Path(__file__).parent

ZONES = ["TITLE", "UPPER", "MID", "LOWER", "FOOTER"]

# Approximate animation durations (frames) for entrance types
ENTRANCE_FRAMES = {
    "fade": 10,
    "wordByWord": 20,  # depends on word count
    "typewriter": 15,
    "pop": 8,
    "slideLeft": 12,
    "slideRight": 12,
    "slideUp": 12,
    "fadeIn": 12,
    "drop": 10,
}


@dataclass
class VisibleElement:
    """An element that is visible at a given time."""
    elem_type: str
    content: str
    zone: str
    enter_time_s: float
    enter_frame: int
    state: str  # "entering", "visible", "exiting"
    scene_id: str
    scene_label: str
    anchor_word: str


def get_content(elem: dict) -> str:
    """Extract a display name for an element."""
    if elem.get("content"):
        return elem["content"][:30]
    if elem.get("svg"):
        svg = elem["svg"]
        repeat = elem.get("repeat", 1)
        return f"[SVG:{svg}]" + (f" x{repeat}" if repeat > 1 else "")
    if elem["type"] == "counter":
        return f"[Counter {elem.get('start',0)}->{elem.get('end',100)} {elem.get('unit','')}]"
    if elem["type"] == "bar":
        return f"[Bar: {elem.get('label','')} = {elem.get('value',0)}]"
    if elem["type"] == "timeline_marker":
        return f"[TL: {elem.get('year','')} {elem.get('label','')}]"
    return f"[{elem['type']}]"


def audit(resolved_path: Path, interval_s: float = 2.0):
    """Generate an audit report of what's visible at each time interval."""
    data = json.loads(resolved_path.read_text())
    scenes = data["scenes"]
    total_s = data["total_duration_s"]

    print("=" * 80)
    print(f"ANIMATION AUDIT: {data['topic']} ({total_s:.1f}s, {data['total_frames']} frames)")
    print(f"Checking every {interval_s}s")
    print("=" * 80)

    issues = []
    t = 0.0

    while t <= total_s + 0.1:
        # Find which scene is active
        active_scene = None
        for scene in scenes:
            if scene["start_s"] <= t <= scene["end_s"]:
                active_scene = scene
                break
            # Check if we're in a gap between scenes
            if t < scene["start_s"]:
                break

        if not active_scene:
            print(f"\n{'─' * 80}")
            print(f"  t={t:6.2f}s | WARNING: NO ACTIVE SCENE (transition gap)")
            t += interval_s
            continue

        scene_rel_s = t - active_scene["start_s"]
        scene_rel_frame = int(scene_rel_s * FPS)
        scene_dur_frames = active_scene["duration_frames"]

        # Determine what's visible
        zone_contents: dict[str, list[VisibleElement]] = {z: [] for z in ZONES}
        visible_elements: list[VisibleElement] = []

        for elem in active_scene["elements"]:
            resolved = elem["_resolved"]
            elem_start_s = active_scene["start_s"] + resolved["delay_s"]
            elem_start_frame = resolved["delay_frames"]

            # Element hasn't appeared yet
            if t < elem_start_s:
                continue

            # How long since element appeared
            elapsed_frames = scene_rel_frame - elem_start_frame
            remaining_frames = scene_dur_frames - scene_rel_frame

            # Determine state
            enter_type = elem.get("enter", "fade")
            enter_dur = ENTRANCE_FRAMES.get(enter_type, 10)
            if enter_type == "wordByWord":
                word_count = len(elem.get("content", "").split())
                enter_dur = word_count * 3 + 6

            exit_start = int(scene_dur_frames * 0.85)

            if elapsed_frames < enter_dur:
                state = "entering"
            elif scene_rel_frame >= exit_start:
                state = "exiting"
            else:
                state = "visible"

            zone = elem.get("zone", "MID")
            content = get_content(elem)

            ve = VisibleElement(
                elem_type=elem["type"],
                content=content,
                zone=zone,
                enter_time_s=elem_start_s,
                enter_frame=elem_start_frame,
                state=state,
                scene_id=active_scene["id"],
                scene_label=active_scene["label"],
                anchor_word=resolved["anchor_word"],
            )
            visible_elements.append(ve)
            zone_contents[zone].append(ve)

        # Print snapshot
        print(f"\n{'─' * 80}")
        print(f"  t={t:6.2f}s | SCENE: {active_scene['label']} ({active_scene['id']}) "
              f"| scene_rel={scene_rel_s:.2f}s frame={scene_rel_frame}/{scene_dur_frames}")

        if not visible_elements:
            print(f"           | WARNING: EMPTY FRAME -- nothing visible")
            issues.append(f"t={t:.2f}s: Empty frame in scene '{active_scene['id']}'")
        else:
            for zone in ZONES:
                elems = zone_contents[zone]
                if not elems:
                    continue

                if len(elems) == 1:
                    e = elems[0]
                    state_icon = {"entering": "[~]", "visible": "[+]", "exiting": "[v]"}[e.state]
                    print(f"           | {zone:6s} {state_icon} {e.content}")
                else:
                    # Multiple elements in same zone -- potential overlap
                    print(f"           | {zone:6s} [!] {len(elems)} ELEMENTS:")
                    for e in elems:
                        state_icon = {"entering": "[~]", "visible": "[+]", "exiting": "[v]"}[e.state]
                        print(f"           |        {state_icon} {e.content} (anchor=\"{e.anchor_word}\" at {e.enter_time_s:.2f}s)")

                    # Check if this is a real overlap issue
                    types = [e.elem_type for e in elems]
                    # Bars and timeline markers are expected to stack
                    if all(t == "bar" for t in types) or all(t == "timeline_marker" for t in types):
                        pass  # Expected stacking
                    elif any(t == "svg" for t in types):
                        pass  # SVGs can coexist (person + warning)
                    else:
                        issues.append(
                            f"t={t:.2f}s: Zone {zone} overlap in '{active_scene['id']}': "
                            + " + ".join(f'"{e.content}"' for e in elems)
                        )

        t += interval_s

    # Summary
    print(f"\n{'=' * 80}")
    print(f"AUDIT SUMMARY")
    print(f"{'=' * 80}")

    if issues:
        print(f"\n  [!] {len(issues)} ISSUES FOUND:")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print("\n  [+] No issues found")

    # Scene gap analysis
    print(f"\n  SCENE GAPS:")
    has_gaps = False
    for i in range(len(scenes) - 1):
        gap = scenes[i + 1]["start_s"] - scenes[i]["end_s"]
        if gap > 0.3:
            severity = "FAIL" if gap > 1.5 else "WARN"
            print(f"    [{severity}] {gap:.2f}s gap between \"{scenes[i]['label']}\" ({scenes[i]['end_s']:.1f}s) "
                  f"and \"{scenes[i+1]['label']}\" ({scenes[i+1]['start_s']:.1f}s)")
            has_gaps = True
            if severity == "FAIL":
                issues.append(f"Scene gap {gap:.1f}s between '{scenes[i]['label']}' and '{scenes[i+1]['label']}'")
    if not has_gaps:
        print(f"    [+] No significant gaps")

    # Zone utilization per scene
    print(f"\n  ZONE UTILIZATION PER SCENE:")
    for scene in scenes:
        zones_used = set()
        for elem in scene["elements"]:
            zones_used.add(elem.get("zone", "MID"))

        empty_zones = set(ZONES) - zones_used - {"TITLE"}  # TITLE is used by LabelPill
        print(f"    {scene['label']:20s} | used: {', '.join(sorted(zones_used)):30s} | empty: {', '.join(sorted(empty_zones)) or 'none'}")

    # Dead time analysis
    print(f"\n  DEAD TIME ANALYSIS (zones empty for >1.5s within a scene):")
    for scene in scenes:
        zone_first_elem: dict[str, float] = {}
        for elem in scene["elements"]:
            zone = elem.get("zone", "MID")
            elem_time = scene["start_s"] + elem["_resolved"]["delay_s"]
            if zone not in zone_first_elem or elem_time < zone_first_elem[zone]:
                zone_first_elem[zone] = elem_time

        for zone in ["UPPER", "MID", "LOWER", "FOOTER"]:
            if zone in zone_first_elem:
                wait = zone_first_elem[zone] - scene["start_s"]
                if wait > 1.5:
                    print(f"    {scene['label']:20s} | {zone:6s} empty for {wait:.1f}s at start")

    return issues


if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "radium"
    interval = 2.0

    for arg in sys.argv[2:]:
        if arg.startswith("--interval"):
            interval = float(sys.argv[sys.argv.index(arg) + 1])

    resolved_path = VIDGEN_DIR / f"{topic}_resolved.json"
    if not resolved_path.exists():
        print(f"Resolved manifest not found: {resolved_path}")
        print("Run resolve_word_triggers.py first")
        sys.exit(1)

    audit(resolved_path, interval)
