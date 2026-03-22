#!/usr/bin/env python3
"""
Manifest Validator for TKK Remotion Videos

Pre-render validation that catches problems before TTS/rendering:
- SVG names exist in svgLibrary.tsx
- Scene count is 6
- TTS word count in range
- Anchor words appear in ttsScript (word-triggered)
- Text length vs style
- Zone density (potential overlaps)

Usage:
    python validate_manifest.py <topic>
    python validate_manifest.py --all
    python validate_manifest.py --json <topic>
"""

import json
import re
import sys
from pathlib import Path

VIDGEN_DIR = Path(__file__).parent
MANIFESTS_DIR = VIDGEN_DIR / "remotion" / "src" / "manifests"
SVG_LIBRARY_PATH = VIDGEN_DIR / "remotion" / "src" / "lib" / "svgLibrary.tsx"

# Thresholds
WORD_COUNT_WARN = 90
WORD_COUNT_FAIL = 120
HEADLINE_WARN_LEN = 25
HEADLINE_FAIL_LEN = 40
CAPTION_WARN_LEN = 60


def _parse_svg_names() -> set[str]:
    """Extract valid SVG names from svgLibrary.tsx."""
    if not SVG_LIBRARY_PATH.exists():
        return set()
    content = SVG_LIBRARY_PATH.read_text()
    # Match lines like "  person: icon(" or "  brain: icon("
    return set(re.findall(r'^\s+(\w+):\s*(?:icon|strokeIcon)\(', content, re.MULTILINE))


def _is_word_triggered(data: dict) -> bool:
    return bool(data.get("scenes") and "scene_anchor" in data["scenes"][0])


def validate_manifest(topic: str) -> dict:
    """Validate a Remotion manifest. Returns structured result."""
    manifest_path = MANIFESTS_DIR / f"{topic}.json"
    if not manifest_path.exists():
        return {
            "topic": topic,
            "status": "FAIL",
            "checks": [{"check": "file_exists", "status": "FAIL", "detail": f"Manifest not found: {manifest_path}"}],
            "fail_count": 1,
            "warn_count": 0,
        }

    data = json.loads(manifest_path.read_text())
    checks = []
    wt = _is_word_triggered(data)

    # 1. Scene count
    n_scenes = len(data.get("scenes", []))
    if n_scenes < 4 or n_scenes > 8:
        checks.append({"check": "scene_count", "status": "FAIL", "detail": f"{n_scenes} scenes (expected 4-8)"})
    elif n_scenes != 6:
        checks.append({"check": "scene_count", "status": "WARN", "detail": f"{n_scenes} scenes (convention is 6)"})
    else:
        checks.append({"check": "scene_count", "status": "PASS", "detail": f"{n_scenes} scenes"})

    # 2. TTS word count
    tts = data.get("ttsScript", "")
    word_count = len(tts.split())
    if word_count > WORD_COUNT_FAIL:
        checks.append({"check": "word_count", "status": "FAIL", "detail": f"{word_count} words (max {WORD_COUNT_FAIL})"})
    elif word_count > WORD_COUNT_WARN:
        checks.append({"check": "word_count", "status": "WARN", "detail": f"{word_count} words (target <{WORD_COUNT_WARN})"})
    elif word_count < 30:
        checks.append({"check": "word_count", "status": "WARN", "detail": f"{word_count} words (suspiciously short)"})
    else:
        checks.append({"check": "word_count", "status": "PASS", "detail": f"{word_count} words"})

    # 3. SVG name validation
    valid_svgs = _parse_svg_names()
    if valid_svgs:
        bad_svgs = []
        for si, scene in enumerate(data.get("scenes", [])):
            elements = scene.get("elements", [])
            # Legacy format: elements in props
            if not elements and "props" in scene:
                props = scene["props"]
                elements = props.get("elements", [])
                # Also check top-level icon fields
                for key in ("icon", "from", "to"):
                    if isinstance(props.get(key), dict) and "icon" in props[key]:
                        svg_name = props[key]["icon"]
                        if svg_name and svg_name not in valid_svgs:
                            bad_svgs.append(f"scene {si+1}: '{svg_name}'")

            for elem in elements:
                svg_name = elem.get("svg")
                if svg_name and svg_name not in valid_svgs:
                    bad_svgs.append(f"scene {si+1}: '{svg_name}'")

        if bad_svgs:
            checks.append({"check": "svg_names", "status": "FAIL",
                          "detail": f"Unknown SVGs: {', '.join(bad_svgs)}. Valid: {', '.join(sorted(valid_svgs))}"})
        else:
            checks.append({"check": "svg_names", "status": "PASS", "detail": "All SVG names valid"})

    # 4. Anchor validation (word-triggered only)
    if wt:
        tts_lower = tts.lower()
        # Build word set, stripping punctuation. Also include substring matches
        # (e.g. "Lacks" matches "Lacks's")
        tts_words_raw = [w.lower() for w in tts.split()]
        missing = []

        def _anchor_in_script(anchor: str) -> bool:
            clean = anchor.rstrip(".,!?;:").lower()
            for w in tts_words_raw:
                if w.rstrip(".,!?;:") == clean or w.startswith(clean):
                    return True
            return False

        for si, scene in enumerate(data.get("scenes", [])):
            for anchor_field in ("scene_anchor", "scene_end_anchor"):
                anchor = scene.get(anchor_field, "")
                if anchor and not _anchor_in_script(anchor):
                    missing.append(f"scene {si+1} {anchor_field}: '{anchor}'")

            for elem in scene.get("elements", []):
                anchor = elem.get("anchor", "")
                if anchor and not _anchor_in_script(anchor):
                    missing.append(f"scene {si+1} element anchor: '{anchor}'")

        if missing:
            # Downgrade to WARN if resolved JSON exists (resolver proved anchors work via Whisper)
            resolved_exists = (VIDGEN_DIR / f"{topic}_resolved.json").exists()
            severity = "WARN" if resolved_exists else "FAIL"
            checks.append({"check": "anchor_words", "status": severity,
                          "detail": f"Anchors not in ttsScript text (Whisper may transcribe differently): {', '.join(missing)}"})
        else:
            checks.append({"check": "anchor_words", "status": "PASS", "detail": "All anchors found in ttsScript"})

    # 5. Text length vs style
    text_issues = []
    for si, scene in enumerate(data.get("scenes", [])):
        elements = scene.get("elements", [])
        if not elements and "props" in scene:
            elements = scene["props"].get("elements", [])

        for elem in elements:
            if elem.get("type") != "text":
                continue
            content = elem.get("content", "")
            style = elem.get("style", "caption")

            if style == "headline":
                if len(content) > HEADLINE_FAIL_LEN:
                    text_issues.append({"status": "FAIL", "detail": f"scene {si+1}: headline '{content}' is {len(content)} chars (max {HEADLINE_FAIL_LEN})"})
                elif len(content) > HEADLINE_WARN_LEN:
                    text_issues.append({"status": "WARN", "detail": f"scene {si+1}: headline '{content}' is {len(content)} chars (target <{HEADLINE_WARN_LEN})"})
            elif style == "caption" and len(content) > CAPTION_WARN_LEN:
                text_issues.append({"status": "WARN", "detail": f"scene {si+1}: caption '{content[:30]}...' is {len(content)} chars"})

    if text_issues:
        for issue in text_issues:
            checks.append({"check": "text_length", **issue})
    else:
        checks.append({"check": "text_length", "status": "PASS", "detail": "All text lengths OK"})

    # 6. Zone density
    stacking_types = {"bar", "timeline_marker"}
    density_issues = []
    for si, scene in enumerate(data.get("scenes", [])):
        elements = scene.get("elements", [])
        if not elements and "props" in scene:
            elements = scene["props"].get("elements", [])

        zone_counts: dict[str, int] = {}
        for elem in elements:
            etype = elem.get("type", "")
            if etype in stacking_types:
                continue
            zone = elem.get("zone", "MID")
            zone_counts[zone] = zone_counts.get(zone, 0) + 1

        for zone, count in zone_counts.items():
            if count > 2:
                density_issues.append(f"scene {si+1} zone {zone}: {count} elements (potential overlap)")

    if density_issues:
        for issue in density_issues:
            checks.append({"check": "zone_density", "status": "WARN", "detail": issue})
    else:
        checks.append({"check": "zone_density", "status": "PASS", "detail": "Zone density OK"})

    # Aggregate
    fail_count = sum(1 for c in checks if c["status"] == "FAIL")
    warn_count = sum(1 for c in checks if c["status"] == "WARN")
    status = "FAIL" if fail_count > 0 else "WARN" if warn_count > 0 else "PASS"

    return {
        "topic": topic,
        "format": "word-triggered" if wt else "legacy",
        "status": status,
        "checks": checks,
        "fail_count": fail_count,
        "warn_count": warn_count,
    }


def format_report(result: dict) -> str:
    """Format a validation result as human-readable text."""
    lines = [f"\n[{result['status']}] {result['topic']} ({result.get('format', 'unknown')})"]
    for c in result["checks"]:
        lines.append(f"  [{c['status']}] {c['check']}: {c['detail']}")
    lines.append(f"  Total: {result['fail_count']} fails, {result['warn_count']} warns")
    return "\n".join(lines)


if __name__ == "__main__":
    use_json = "--json" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if "--all" in sys.argv:
        topics = [m.stem for m in sorted(MANIFESTS_DIR.glob("*.json"))]
    elif args:
        topics = args
    else:
        print("Usage: python validate_manifest.py <topic> [--all] [--json]")
        sys.exit(1)

    all_results = []
    for topic in topics:
        result = validate_manifest(topic)
        all_results.append(result)
        if use_json:
            print(json.dumps(result, indent=2))
        else:
            print(format_report(result))

    if not use_json and len(topics) > 1:
        total_f = sum(r["fail_count"] for r in all_results)
        total_w = sum(r["warn_count"] for r in all_results)
        overall = "FAIL" if total_f else "WARN" if total_w else "PASS"
        print(f"\n{'='*50}")
        print(f"Fleet: [{overall}] {len(topics)} manifests, {total_f} fails, {total_w} warns")
