#!/usr/bin/env python3
"""
qa_manifest_deep.py — Deep manifest validation for LLM-generated content.

Catches specific failure modes: text overflow, zone capacity, SVG validity,
color contrast, anchor ambiguity, scene timing, element diversity.

Usage:
    python3 qa_manifest_deep.py <topic> [--json] [--verbose]
"""

import argparse
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any

# ── Auto-venv ────────────────────────────────────────────────────────────────
VENV = Path(__file__).parent / ".venv"
if VENV.exists() and "VIRTUAL_ENV" not in os.environ:
    site_packages = next(VENV.glob("lib/python*/site-packages"), None)
    if site_packages:
        sys.path.insert(0, str(site_packages))

# ── Constants ────────────────────────────────────────────────────────────────

BASE = Path(__file__).parent
MANIFEST_DIR = BASE / "remotion" / "src" / "manifests"
SVG_LIBRARY_PATH = BASE / "remotion" / "src" / "lib" / "svgLibrary.tsx"

# Zone definitions: name -> (top_px, bottom_px)
ZONES = {
    "TITLE":  (120, 300),
    "UPPER":  (300, 780),
    "MID":    (780, 1140),
    "LOWER":  (1140, 1620),
    "FOOTER": (1620, 1728),
}
ZONE_HEIGHTS = {k: b - a for k, (a, b) in ZONES.items()}

SAFE_WIDTH = 820  # right=940 - left=120

# Estimated char widths per style (px per character)
CHAR_WIDTHS = {
    "headline": 50,
    "stat":     90,
    "caption":  22,
    "label":    24,
    "body":     28,
}

# Font sizes per style
STYLE_HEIGHTS = {
    "headline": 100,   # 80-120, use midpoint
    "stat":     190,   # 160-220
    "caption":  36,    # 32-40
    "label":    36,    # 32-40
    "body":     48,    # 40-56
}

# Estimated vertical space per element type
ELEMENT_BASE_HEIGHTS = {
    "counter":        280,
    "number_ticker":  200,
    "gauge":          300,
}

# Ambiguous anchor words to warn about
AMBIGUOUS_ANCHORS = {"the", "a", "is", "it", "to", "and", "of", "in", "on"}

# Complex element types that need more time
COMPLEX_ELEMENTS = {"bar_race", "pie_chart", "cause_effect", "flow_diagram"}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _load_manifest(topic: str) -> dict:
    path = MANIFEST_DIR / f"{topic}.json"
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")
    with open(path) as f:
        return json.load(f)


def _load_svg_names() -> set[str]:
    """Parse SVG_LIBRARY keys from svgLibrary.tsx."""
    if not SVG_LIBRARY_PATH.exists():
        return set()
    text = SVG_LIBRARY_PATH.read_text()

    names: set[str] = set()
    # Match keys in _extraIcons and SVG_LIBRARY objects
    # Pattern: leading whitespace, then word followed by colon (object key)
    # Also handle quoted keys like 'someName':
    for m in re.finditer(r"^\s+(\w+)\s*:", text, re.MULTILINE):
        name = m.group(1)
        # Skip non-icon keys (React internals, helper vars)
        if name in ("color", "size", "width", "height", "viewBox", "fill",
                     "stroke", "strokeWidth", "strokeLinecap", "strokeLinejoin",
                     "opacity", "d", "cx", "cy", "r", "x", "y", "x1", "y1",
                     "x2", "y2", "rx", "ry", "points", "transform",
                     "style", "xmlns", "children", "Icon"):
            continue
        names.add(name)
    return names


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int] | None:
    """Convert hex color string to RGB tuple."""
    if not hex_color or not isinstance(hex_color, str):
        return None
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    if len(hex_color) != 6:
        return None
    try:
        return (int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))
    except ValueError:
        return None


def _relative_luminance(r: int, g: int, b: int) -> float:
    """WCAG 2.0 relative luminance."""
    def linearize(v: int) -> float:
        s = v / 255.0
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4
    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)


def _contrast_ratio(lum1: float, lum2: float) -> float:
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    return (lighter + 0.05) / (darker + 0.05)


def _estimate_text_height(content: str, style: str) -> float:
    """Estimate vertical px needed for text content at given style."""
    char_w = CHAR_WIDTHS.get(style, 28)
    line_h = STYLE_HEIGHTS.get(style, 48)
    chars = len(content)
    chars_per_line = max(1, SAFE_WIDTH // char_w)
    num_lines = math.ceil(chars / chars_per_line)
    return num_lines * line_h * 1.2  # 1.2 for line spacing


def _estimate_element_height(el: dict) -> float:
    """Estimate vertical space an element needs."""
    etype = el.get("type", "text")

    if etype == "text":
        content = el.get("content", "")
        style = el.get("style", "body")
        return _estimate_text_height(content, style)

    if etype in ELEMENT_BASE_HEIGHTS:
        return ELEMENT_BASE_HEIGHTS[etype]

    if etype == "bar_race":
        bars = el.get("bars", [])
        return len(bars) * 60 + 40

    if etype == "pie_chart":
        size = el.get("size", 200)
        return size + 60

    if etype == "split_screen":
        return 0  # uses full content area

    if etype == "cause_effect":
        dominoes = el.get("dominoes", [])
        return len(dominoes) * 100

    if etype in ("svg", "illustration", "custom_svg"):
        size = el.get("size", 100)
        return size + 20

    if etype == "map_highlight":
        size = el.get("size", 200)
        return size + 20

    if etype == "flow_diagram":
        nodes = el.get("nodes", [])
        direction = el.get("direction", "vertical")
        if direction == "horizontal":
            return 200
        return len(nodes) * 120

    # Default for unknown types
    return 100


# ── Check Functions ──────────────────────────────────────────────────────────

def check_text_overflow(manifest: dict) -> list[dict]:
    """Check if text elements overflow their zone width or height."""
    results = []
    for scene in manifest.get("scenes", []):
        sid = scene.get("id", "?")
        for el in scene.get("elements", []):
            if el.get("type") != "text":
                continue
            content = el.get("content", "")
            style = el.get("style", "body")
            zone = el.get("zone", "MID")

            char_w = CHAR_WIDTHS.get(style, 28)
            line_h = STYLE_HEIGHTS.get(style, 48)
            chars = len(content)
            chars_per_line = max(1, SAFE_WIDTH // char_w)
            num_lines = math.ceil(chars / chars_per_line)

            zone_h = ZONE_HEIGHTS.get(zone, 360)
            max_lines = max(1, zone_h // int(line_h * 1.2))

            if num_lines > max_lines:
                results.append({
                    "check": "text_overflow",
                    "status": "FAIL",
                    "detail": (f"Scene '{sid}': text \"{content[:40]}...\" style={style} "
                               f"needs ~{num_lines} lines but zone {zone} fits ~{max_lines}"),
                })
            elif num_lines > 2:
                results.append({
                    "check": "text_overflow",
                    "status": "WARN",
                    "detail": (f"Scene '{sid}': text \"{content[:40]}\" style={style} "
                               f"wraps to {num_lines} lines in zone {zone}"),
                })
    if not results:
        results.append({"check": "text_overflow", "status": "PASS", "detail": "All text fits within zones"})
    return results


def check_zone_capacity(manifest: dict) -> list[dict]:
    """Check if elements assigned to a zone exceed its pixel height."""
    results = []
    for scene in manifest.get("scenes", []):
        sid = scene.get("id", "?")
        zone_usage: dict[str, float] = {}

        for el in scene.get("elements", []):
            etype = el.get("type", "text")
            zone = el.get("zone", "MID")
            if etype == "split_screen":
                continue
            h = _estimate_element_height(el)
            zone_usage[zone] = zone_usage.get(zone, 0) + h

        for zone, used in zone_usage.items():
            capacity = ZONE_HEIGHTS.get(zone, 360)
            ratio = used / capacity if capacity > 0 else 999

            if ratio > 1.0:
                results.append({
                    "check": "zone_capacity",
                    "status": "FAIL",
                    "detail": (f"Scene '{sid}' zone {zone}: ~{int(used)}px content "
                               f"in {capacity}px zone ({ratio:.0%} full)"),
                })
            elif ratio > 0.8:
                results.append({
                    "check": "zone_capacity",
                    "status": "WARN",
                    "detail": (f"Scene '{sid}' zone {zone}: ~{int(used)}px content "
                               f"in {capacity}px zone ({ratio:.0%} full)"),
                })
    if not results:
        results.append({"check": "zone_capacity", "status": "PASS", "detail": "All zones have sufficient capacity"})
    return results


def check_svg_names(manifest: dict) -> list[dict]:
    """Validate SVG icon references against the library."""
    known = _load_svg_names()
    if not known:
        return [{"check": "svg_names", "status": "WARN", "detail": "Could not load SVG library"}]

    results = []
    for scene in manifest.get("scenes", []):
        sid = scene.get("id", "?")
        for el in scene.get("elements", []):
            if el.get("type") == "svg":
                svg_name = el.get("svg", "")
                if svg_name and svg_name not in known:
                    results.append({
                        "check": "svg_names",
                        "status": "FAIL",
                        "detail": f"Scene '{sid}': SVG icon '{svg_name}' not found in library",
                    })
            # Also check icon references in flow_diagram nodes, bar_race bars, etc.
            if el.get("type") == "flow_diagram":
                for node in el.get("nodes", []):
                    icon = node.get("icon", "")
                    if icon and icon not in known:
                        results.append({
                            "check": "svg_names",
                            "status": "WARN",
                            "detail": f"Scene '{sid}': flow_diagram icon '{icon}' not in library",
                        })
            if el.get("type") == "cause_effect":
                for domino in el.get("dominoes", []):
                    icon = domino.get("icon", "")
                    if icon and icon not in known:
                        results.append({
                            "check": "svg_names",
                            "status": "WARN",
                            "detail": f"Scene '{sid}': cause_effect icon '{icon}' not in library",
                        })

    if not results:
        results.append({"check": "svg_names", "status": "PASS", "detail": "All SVG references valid"})
    return results


def check_color_contrast(manifest: dict) -> list[dict]:
    """Check foreground colors against background for WCAG contrast."""
    results = []
    bg_hex = manifest.get("colors", {}).get("bg", "#000000")
    bg_rgb = _hex_to_rgb(bg_hex)
    if not bg_rgb:
        return [{"check": "color_contrast", "status": "WARN", "detail": f"Cannot parse bg color: {bg_hex}"}]

    bg_lum = _relative_luminance(*bg_rgb)

    checked = set()
    for scene in manifest.get("scenes", []):
        sid = scene.get("id", "?")
        for el in scene.get("elements", []):
            color = el.get("color")
            if not color or not isinstance(color, str):
                continue
            # Avoid duplicate reports for the same color
            key = (sid, color)
            if key in checked:
                continue
            checked.add(key)

            fg_rgb = _hex_to_rgb(color)
            if not fg_rgb:
                continue

            fg_lum = _relative_luminance(*fg_rgb)
            ratio = _contrast_ratio(fg_lum, bg_lum)

            if ratio < 2.0:
                results.append({
                    "check": "color_contrast",
                    "status": "FAIL",
                    "detail": (f"Scene '{sid}': color {color} on bg {bg_hex} "
                               f"has contrast ratio {ratio:.1f}:1 (invisible)"),
                })
            elif ratio < 3.0:
                results.append({
                    "check": "color_contrast",
                    "status": "WARN",
                    "detail": (f"Scene '{sid}': color {color} on bg {bg_hex} "
                               f"has contrast ratio {ratio:.1f}:1 (hard to read)"),
                })

    if not results:
        results.append({"check": "color_contrast", "status": "PASS", "detail": "All colors have sufficient contrast"})
    return results


def check_anchor_words(manifest: dict) -> list[dict]:
    """Validate anchor words exist in ttsScript and are in order."""
    results = []
    tts = manifest.get("ttsScript", "")
    if not tts:
        return [{"check": "anchor_words", "status": "WARN", "detail": "No ttsScript found"}]

    tts_lower = tts.lower()
    tts_words = tts.split()

    # Check element-level anchors
    for scene in manifest.get("scenes", []):
        sid = scene.get("id", "?")
        for el in scene.get("elements", []):
            anchor = el.get("anchor")
            if not anchor:
                continue
            if anchor.lower() not in tts_lower:
                results.append({
                    "check": "anchor_words",
                    "status": "FAIL",
                    "detail": f"Scene '{sid}': anchor '{anchor}' not found in ttsScript",
                })
            elif anchor.lower() in AMBIGUOUS_ANCHORS:
                results.append({
                    "check": "anchor_words",
                    "status": "WARN",
                    "detail": f"Scene '{sid}': anchor '{anchor}' is ambiguous (common word)",
                })

    # Check scene-level anchors are in order
    scene_anchors = []
    for scene in manifest.get("scenes", []):
        sa = scene.get("scene_anchor")
        if sa:
            scene_anchors.append((scene.get("id", "?"), sa))

    last_pos = -1
    for sid, anchor in scene_anchors:
        # Find position of anchor in script
        pos = tts_lower.find(anchor.lower())
        if pos == -1:
            results.append({
                "check": "anchor_words",
                "status": "FAIL",
                "detail": f"Scene '{sid}': scene_anchor '{anchor}' not found in ttsScript",
            })
        elif pos < last_pos:
            results.append({
                "check": "anchor_words",
                "status": "FAIL",
                "detail": f"Scene '{sid}': scene_anchor '{anchor}' appears out of order in ttsScript",
            })
        else:
            last_pos = pos

        if anchor.lower() in AMBIGUOUS_ANCHORS:
            results.append({
                "check": "anchor_words",
                "status": "WARN",
                "detail": f"Scene '{sid}': scene_anchor '{anchor}' is ambiguous (common word)",
            })

    if not results:
        results.append({"check": "anchor_words", "status": "PASS", "detail": "All anchors valid and in order"})
    return results


def check_scene_duration(manifest: dict) -> list[dict]:
    """Estimate scene durations and flag insufficient time for complex elements."""
    results = []
    tts = manifest.get("ttsScript", "")
    if not tts:
        return [{"check": "scene_duration", "status": "WARN", "detail": "No ttsScript for duration estimation"}]

    scenes = manifest.get("scenes", [])
    tts_words = tts.split()
    tts_lower = tts.lower()

    for scene in scenes:
        sid = scene.get("id", "?")
        sa = scene.get("scene_anchor", "")
        sea = scene.get("scene_end_anchor", "")

        if not sa or not sea:
            continue

        # Find word positions
        start_pos = tts_lower.find(sa.lower())
        end_pos = tts_lower.find(sea.lower())
        if start_pos == -1 or end_pos == -1 or end_pos <= start_pos:
            continue

        # Count words in the segment
        segment = tts[start_pos:end_pos + len(sea)]
        word_count = len(segment.split())
        est_duration = word_count / 2.5  # ~2.5 words/second

        elements = scene.get("elements", [])
        has_complex = any(el.get("type") in COMPLEX_ELEMENTS for el in elements)
        num_elements = len(elements)

        if has_complex and est_duration < 4.0:
            results.append({
                "check": "scene_duration",
                "status": "WARN",
                "detail": (f"Scene '{sid}': complex element with only ~{est_duration:.1f}s "
                           f"({word_count} words) — may feel rushed"),
            })
        if num_elements > 4 and est_duration < 5.0:
            results.append({
                "check": "scene_duration",
                "status": "WARN",
                "detail": (f"Scene '{sid}': {num_elements} elements with only ~{est_duration:.1f}s "
                           f"({word_count} words) — may feel crowded"),
            })

    if not results:
        results.append({"check": "scene_duration", "status": "PASS", "detail": "Scene durations look reasonable"})
    return results


def check_element_diversity(manifest: dict) -> list[dict]:
    """Check for variety in element types and zone usage."""
    results = []
    scenes = manifest.get("scenes", [])

    all_types: set[str] = set()
    all_zones: set[str] = set()
    text_only_scenes = 0

    for scene in scenes:
        scene_types = set()
        for el in scene.get("elements", []):
            etype = el.get("type", "text")
            zone = el.get("zone", "MID")
            all_types.add(etype)
            all_zones.add(zone)
            scene_types.add(etype)
        if scene_types == {"text"}:
            text_only_scenes += 1

    if text_only_scenes == len(scenes) and len(scenes) > 1:
        results.append({
            "check": "element_diversity",
            "status": "WARN",
            "detail": "All scenes use only 'text' elements — no data visualization",
        })

    if "LOWER" not in all_zones and "FOOTER" not in all_zones:
        results.append({
            "check": "element_diversity",
            "status": "WARN",
            "detail": "No elements in LOWER or FOOTER zones — poor vertical distribution",
        })

    if len(all_types) < 3:
        results.append({
            "check": "element_diversity",
            "status": "WARN",
            "detail": f"Only {len(all_types)} unique element type(s) used: {sorted(all_types)}",
        })

    if not results:
        results.append({
            "check": "element_diversity",
            "status": "PASS",
            "detail": f"{len(all_types)} element types across {len(all_zones)} zones",
        })
    return results


# ── Main ─────────────────────────────────────────────────────────────────────

def analyze_manifest(topic: str) -> dict:
    """Run all deep checks on a manifest and return structured results."""
    manifest = _load_manifest(topic)

    checks: list[dict] = []
    checks.extend(check_text_overflow(manifest))
    checks.extend(check_zone_capacity(manifest))
    checks.extend(check_svg_names(manifest))
    checks.extend(check_color_contrast(manifest))
    checks.extend(check_anchor_words(manifest))
    checks.extend(check_scene_duration(manifest))
    checks.extend(check_element_diversity(manifest))

    fail_count = sum(1 for c in checks if c["status"] == "FAIL")
    warn_count = sum(1 for c in checks if c["status"] == "WARN")

    if fail_count > 0:
        status = "FAIL"
    elif warn_count > 0:
        status = "WARN"
    else:
        status = "PASS"

    return {
        "topic": topic,
        "status": status,
        "checks": checks,
        "fail_count": fail_count,
        "warn_count": warn_count,
    }


def _print_report(result: dict, verbose: bool = False) -> None:
    """Pretty-print the analysis result."""
    topic = result["topic"]
    status = result["status"]

    # Status colors
    colors = {"PASS": "\033[32m", "WARN": "\033[33m", "FAIL": "\033[31m"}
    reset = "\033[0m"
    c = colors.get(status, "")

    print(f"\n{'=' * 60}")
    print(f"  Deep QA: {topic}")
    print(f"  Status: {c}{status}{reset}  "
          f"({result['fail_count']} fail, {result['warn_count']} warn)")
    print(f"{'=' * 60}")

    # Group by check name
    by_check: dict[str, list[dict]] = {}
    for ck in result["checks"]:
        by_check.setdefault(ck["check"], []).append(ck)

    for check_name, items in by_check.items():
        worst = "PASS"
        for item in items:
            if item["status"] == "FAIL":
                worst = "FAIL"
            elif item["status"] == "WARN" and worst != "FAIL":
                worst = "WARN"
        ck_color = colors.get(worst, "")
        print(f"\n  [{ck_color}{worst}{reset}] {check_name}")

        for item in items:
            if item["status"] == "PASS" and not verbose:
                print(f"        {item['detail']}")
            else:
                ic = colors.get(item["status"], "")
                print(f"    {ic}{item['status']}{reset}  {item['detail']}")

    print()


def main():
    parser = argparse.ArgumentParser(description="Deep manifest QA for LLM failure modes")
    parser.add_argument("topic", help="Manifest topic name (without .json)")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of formatted report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all checks including PASS details")
    args = parser.parse_args()

    try:
        result = analyze_manifest(args.topic)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        _print_report(result, verbose=args.verbose)

    # Exit code reflects status
    if result["status"] == "FAIL":
        sys.exit(2)
    elif result["status"] == "WARN":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
