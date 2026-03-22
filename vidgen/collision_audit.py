#!/usr/bin/env python3
"""
Visual Collision Auditor for Word-Triggered TKK Videos

Computes actual pixel bounding boxes for every visible element at each
time step and detects:
  1. Same-zone text overlap (two text elements competing for the same space)
  2. Cross-zone bleed (element too tall, bleeds into adjacent zone)
  3. Counter + description overflow (unit text wrapping)
  4. SVG icon overlap (multiple icons in MID zone)
  5. Bar chart vertical stacking issues

Uses the exact zone coordinates and font sizes from the Remotion source.

Usage:
    python collision_audit.py [topic] [--interval 0.5]
"""

import json
import sys
import math
from pathlib import Path
from dataclasses import dataclass

VIDGEN_DIR = Path(__file__).parent
FPS = 30
CANVAS_W = 1080
CANVAS_H = 1920

# ── Zone pixel coordinates (from zones.ts) ──────────────────
def manim_to_pixel_y(manim_y: float) -> float:
    return ((8 - manim_y) / 16) * CANVAS_H

ZONES = {
    "TITLE":  {"top": manim_to_pixel_y(7.0),  "bottom": manim_to_pixel_y(5.5),  "center": manim_to_pixel_y(6.2)},
    "UPPER":  {"top": manim_to_pixel_y(5.5),  "bottom": manim_to_pixel_y(1.5),  "center": manim_to_pixel_y(3.5)},
    "MID":    {"top": manim_to_pixel_y(1.5),  "bottom": manim_to_pixel_y(-1.5), "center": manim_to_pixel_y(0.0)},
    "LOWER":  {"top": manim_to_pixel_y(-1.5), "bottom": manim_to_pixel_y(-5.5), "center": manim_to_pixel_y(-3.5)},
    "FOOTER": {"top": manim_to_pixel_y(-5.5), "bottom": manim_to_pixel_y(-6.4), "center": manim_to_pixel_y(-6.0)},
}

SAFE_LEFT = 120
SAFE_WIDTH = 820

# ── Font sizes (from typography.ts) ──────────────────────────
FONT_SIZE = {
    "hero": 200,
    "stat": 160,
    "headline": 96,
    "subtitle": 64,
    "body": 48,
    "caption": 36,
    "dataLabel": 36,
    "dataValue": 32,
    "label": 36,
    "pill": 32,
}

LINE_HEIGHT = 1.2
CHAR_WIDTH_RATIO = {"mono": 0.6, "body": 0.5, "headline": 0.55}


@dataclass
class BBox:
    """Axis-aligned bounding box in pixel coordinates."""
    x: float
    y: float  # top edge
    w: float
    h: float
    label: str
    elem_type: str
    zone: str

    @property
    def bottom(self) -> float:
        return self.y + self.h

    @property
    def right(self) -> float:
        return self.x + self.w

    def overlaps(self, other: 'BBox') -> bool:
        if self.x >= other.right or other.x >= self.right:
            return False
        if self.y >= other.bottom or other.y >= self.bottom:
            return False
        return True

    def overlap_area(self, other: 'BBox') -> float:
        x_overlap = max(0, min(self.right, other.right) - max(self.x, other.x))
        y_overlap = max(0, min(self.bottom, other.bottom) - max(self.y, other.y))
        return x_overlap * y_overlap


def estimate_text_bbox(content: str, style: str, zone: str, font_size_override: float | None = None) -> BBox:
    z = ZONES.get(zone, ZONES["MID"])
    fs = font_size_override or FONT_SIZE.get(style, 48)
    line_h = fs * LINE_HEIGHT
    char_w = fs * CHAR_WIDTH_RATIO.get("headline" if style == "headline" else "body", 0.5)
    text_width = len(content) * char_w
    lines = max(1, math.ceil(text_width / SAFE_WIDTH))
    total_h = lines * line_h
    center_y = z["center"]
    top = center_y - total_h / 2
    left = SAFE_LEFT + max(0, (SAFE_WIDTH - min(text_width, SAFE_WIDTH)) / 2)
    width = min(text_width, SAFE_WIDTH)
    return BBox(x=left, y=top, w=width, h=total_h, label=content[:40], elem_type="text", zone=zone)


def estimate_counter_bbox(unit: str, description: str | None, zone: str) -> BBox:
    z = ZONES.get(zone, ZONES["MID"])
    number_h = FONT_SIZE["hero"] * LINE_HEIGHT
    unit_h = FONT_SIZE["subtitle"] * LINE_HEIGHT if unit else 0
    desc_h = FONT_SIZE["body"] * LINE_HEIGHT if description else 0
    total_h = number_h + 12 + desc_h
    unit_char_w = FONT_SIZE["subtitle"] * 0.5
    unit_width = len(unit) * unit_char_w if unit else 0
    if unit_width > SAFE_WIDTH * 0.5:
        total_h += unit_h
    center_y = z["center"]
    top = center_y - total_h / 2
    return BBox(x=SAFE_LEFT, y=top, w=SAFE_WIDTH, h=total_h, label=f"Counter + {unit}", elem_type="counter", zone=zone)


def estimate_svg_bbox(svg_name: str, size: int, zone: str, repeat: int = 1, position: dict | None = None) -> BBox:
    z = ZONES.get(zone, ZONES["MID"])
    pos_x = (position or {}).get("x", 0)
    pos_y = (position or {}).get("y", 0)
    center_y = z["center"] + pos_y
    center_x = SAFE_LEFT + SAFE_WIDTH / 2 + pos_x
    if repeat > 1:
        spacing = size * 1.2
        total_w = repeat * spacing
        left = center_x - total_w / 2
        return BBox(x=left, y=center_y - size/2, w=total_w, h=size, label=f"[SVG:{svg_name}] x{repeat}", elem_type="svg", zone=zone)
    else:
        left = center_x - size / 2
        return BBox(x=left, y=center_y - size/2, w=size, h=size, label=f"[SVG:{svg_name}]", elem_type="svg", zone=zone)


def estimate_bar_bbox(label: str, value: int, index: int, total_bars: int, zone: str) -> BBox:
    z = ZONES.get(zone, ZONES["MID"])
    bar_h = 44
    bar_spacing = bar_h + 16
    total_height = total_bars * bar_spacing
    y_offset = index * bar_spacing - total_height / 2 + bar_h / 2
    center_y = z["center"]
    top = center_y + y_offset - bar_h / 2
    return BBox(x=SAFE_LEFT, y=top, w=SAFE_WIDTH, h=bar_h, label=f"Bar: {label}={value}", elem_type="bar", zone=zone)


def estimate_timeline_marker_bbox(year: str, label: str, index: int, total: int, zone: str) -> BBox:
    z = ZONES.get(zone, ZONES["MID"])
    dot_h = 18
    year_h = FONT_SIZE["dataLabel"] * LINE_HEIGHT
    label_lines = max(1, math.ceil(len(label) * FONT_SIZE["dataValue"] * 0.5 / 200))
    label_h = label_lines * FONT_SIZE["dataValue"] * LINE_HEIGHT
    total_h = dot_h + 8 + year_h + label_h
    pct = 0.5 if total == 1 else index / (total - 1)
    x_center = SAFE_LEFT + pct * (SAFE_WIDTH - 100) + 50
    marker_w = 200
    center_y = z["center"]
    top = center_y - total_h / 2
    return BBox(x=x_center - marker_w/2, y=top, w=marker_w, h=total_h, label=f"TL:{year} {label}", elem_type="timeline", zone=zone)


def get_element_bbox(elem: dict, scene_elements: list, all_bars: list, all_markers: list) -> BBox | None:
    etype = elem.get("type", "")
    zone = elem.get("zone", "MID")

    if etype == "text":
        return estimate_text_bbox(elem.get("content", ""), elem.get("style", "caption"), zone, elem.get("fontSize"))
    elif etype == "counter":
        return estimate_counter_bbox(elem.get("unit", ""), elem.get("description"), zone)
    elif etype == "svg":
        return estimate_svg_bbox(elem.get("svg", ""), elem.get("size", 100), zone, elem.get("repeat", 1), elem.get("position"))
    elif etype == "bar":
        idx = all_bars.index(elem) if elem in all_bars else 0
        return estimate_bar_bbox(elem.get("label", ""), elem.get("value", 0), idx, len(all_bars), zone)
    elif etype == "timeline_marker":
        idx = all_markers.index(elem) if elem in all_markers else 0
        return estimate_timeline_marker_bbox(elem.get("year", ""), elem.get("label", ""), idx, len(all_markers), zone)
    return None


def audit_collisions(resolved_path: Path, interval_s: float = 0.5):
    """Run collision detection at regular intervals."""
    data = json.loads(resolved_path.read_text())
    scenes = data["scenes"]
    total_s = data["total_duration_s"]

    print("=" * 80)
    print(f"COLLISION AUDIT: {data['topic']} ({total_s:.1f}s)")
    print(f"Canvas: {CANVAS_W}x{CANVAS_H}, checking every {interval_s}s")
    print("=" * 80)

    print("\nZone layout (pixel Y ranges, top=0):")
    for name, z in ZONES.items():
        height = z["bottom"] - z["top"]
        print(f"  {name:6s}: {z['top']:7.0f}px -> {z['bottom']:7.0f}px ({height:.0f}px tall)")

    collisions = []
    t = 0.0

    while t <= total_s + 0.01:
        active_scene = None
        for scene in scenes:
            if scene["start_s"] <= t <= scene["end_s"]:
                active_scene = scene
                break
        if not active_scene:
            t += interval_s
            continue

        scene_rel_s = t - active_scene["start_s"]

        visible = []
        all_bars = [e for e in active_scene["elements"] if e["type"] == "bar"]
        all_markers = [e for e in active_scene["elements"] if e["type"] == "timeline_marker"]

        for elem in active_scene["elements"]:
            resolved = elem["_resolved"]
            elem_start_s = active_scene["start_s"] + resolved["delay_s"]
            if t < elem_start_s:
                continue

            elem_end_s = active_scene["end_s"]
            if elem.get("hold") == "until_replaced":
                zone = elem.get("zone", "MID")
                for other in active_scene["elements"]:
                    if other is elem:
                        continue
                    if other.get("zone", "MID") == zone and other.get("replaces_zone"):
                        replacer_start = active_scene["start_s"] + other["_resolved"]["delay_s"]
                        if replacer_start > elem_start_s:
                            elem_end_s = replacer_start + 0.1
                            break

            if t > elem_end_s:
                continue

            bbox = get_element_bbox(elem, active_scene["elements"], all_bars, all_markers)
            if bbox:
                visible.append((elem, bbox))

        for i, (elem_a, bbox_a) in enumerate(visible):
            for j, (elem_b, bbox_b) in enumerate(visible):
                if j <= i:
                    continue

                if bbox_a.overlaps(bbox_b):
                    area = bbox_a.overlap_area(bbox_b)
                    if bbox_a.elem_type == "bar" and bbox_b.elem_type == "bar":
                        continue
                    if bbox_a.elem_type == "timeline" and bbox_b.elem_type == "timeline":
                        if area < 500:
                            continue

                    pct_a = area / (bbox_a.w * bbox_a.h) * 100
                    pct_b = area / (bbox_b.w * bbox_b.h) * 100
                    severity = "CRITICAL" if max(pct_a, pct_b) > 50 else "WARN" if max(pct_a, pct_b) > 20 else "minor"

                    collisions.append({
                        "time": t,
                        "scene": active_scene["id"],
                        "a": bbox_a.label,
                        "b": bbox_b.label,
                        "a_zone": bbox_a.zone,
                        "b_zone": bbox_b.zone,
                        "overlap_px": area,
                        "pct_a": pct_a,
                        "pct_b": pct_b,
                        "severity": severity,
                        "a_bbox": f"({bbox_a.x:.0f},{bbox_a.y:.0f})->({bbox_a.right:.0f},{bbox_a.bottom:.0f})",
                        "b_bbox": f"({bbox_b.x:.0f},{bbox_b.y:.0f})->({bbox_b.right:.0f},{bbox_b.bottom:.0f})",
                    })

        # Check for cross-zone bleed
        for elem, bbox in visible:
            zone = bbox.zone
            z = ZONES.get(zone, ZONES["MID"])
            if bbox.y < z["top"] - 10:
                collisions.append({
                    "time": t, "scene": active_scene["id"],
                    "a": bbox.label, "b": f"{zone} zone top boundary",
                    "a_zone": zone, "b_zone": zone,
                    "overlap_px": z["top"] - bbox.y, "pct_a": 0, "pct_b": 0,
                    "severity": "BLEED",
                    "a_bbox": f"({bbox.x:.0f},{bbox.y:.0f})->({bbox.right:.0f},{bbox.bottom:.0f})",
                    "b_bbox": f"zone top={z['top']:.0f}",
                })
            if bbox.bottom > z["bottom"] + 10:
                collisions.append({
                    "time": t, "scene": active_scene["id"],
                    "a": bbox.label, "b": f"{zone} zone bottom boundary",
                    "a_zone": zone, "b_zone": zone,
                    "overlap_px": bbox.bottom - z["bottom"], "pct_a": 0, "pct_b": 0,
                    "severity": "BLEED",
                    "a_bbox": f"({bbox.x:.0f},{bbox.y:.0f})->({bbox.right:.0f},{bbox.bottom:.0f})",
                    "b_bbox": f"zone bottom={z['bottom']:.0f}",
                })

        # Check for text/counter overflow vs zone height
        for elem, bbox in visible:
            if bbox.elem_type not in ("text", "counter"):
                continue
            zone = bbox.zone
            z = ZONES.get(zone, ZONES["MID"])
            zone_height = z["bottom"] - z["top"]
            if zone_height <= 0:
                continue
            ratio = bbox.h / zone_height
            if ratio > 1.0:
                collisions.append({
                    "time": t, "scene": active_scene["id"],
                    "a": bbox.label, "b": f"{zone} zone ({zone_height:.0f}px)",
                    "a_zone": zone, "b_zone": zone,
                    "overlap_px": bbox.h - zone_height, "pct_a": ratio * 100, "pct_b": 0,
                    "severity": "CRITICAL",
                    "a_bbox": f"({bbox.x:.0f},{bbox.y:.0f})->({bbox.right:.0f},{bbox.bottom:.0f})",
                    "b_bbox": f"zone height={zone_height:.0f}px, text height={bbox.h:.0f}px",
                })
            elif ratio > 0.8:
                collisions.append({
                    "time": t, "scene": active_scene["id"],
                    "a": bbox.label, "b": f"{zone} zone ({zone_height:.0f}px)",
                    "a_zone": zone, "b_zone": zone,
                    "overlap_px": 0, "pct_a": ratio * 100, "pct_b": 0,
                    "severity": "WARN",
                    "a_bbox": f"({bbox.x:.0f},{bbox.y:.0f})->({bbox.right:.0f},{bbox.bottom:.0f})",
                    "b_bbox": f"zone height={zone_height:.0f}px, text height={bbox.h:.0f}px ({ratio:.0%} fill)",
                })

        t += interval_s

    # Deduplicate
    seen = set()
    unique_collisions = []
    for c in collisions:
        key = (c["scene"], c["a"], c["b"], c["severity"])
        if key not in seen:
            seen.add(key)
            unique_collisions.append(c)

    # Report
    print(f"\n{'=' * 80}")
    print(f"COLLISION REPORT: {len(unique_collisions)} unique issues")
    print(f"{'=' * 80}")

    by_severity = {"CRITICAL": [], "WARN": [], "BLEED": [], "minor": []}
    for c in unique_collisions:
        by_severity[c["severity"]].append(c)

    for sev in ["CRITICAL", "WARN", "BLEED", "minor"]:
        items = by_severity[sev]
        if not items:
            continue
        print(f"\n  [{sev}] ({len(items)} issues):")
        for c in items:
            print(f"    t={c['time']:5.1f}s | {c['scene']:15s} | \"{c['a']}\" <-> \"{c['b']}\"")
            print(f"           | zones: {c['a_zone']}<->{c['b_zone']} | overlap: {c['overlap_px']:.0f}px ({c['pct_a']:.0f}%/{c['pct_b']:.0f}%)")
            print(f"           | A: {c['a_bbox']}  B: {c['b_bbox']}")

    if not unique_collisions:
        print("\n  [+] No collisions detected")

    return unique_collisions


if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "radium"
    interval = 0.5
    for i, arg in enumerate(sys.argv):
        if arg == "--interval" and i + 1 < len(sys.argv):
            interval = float(sys.argv[i + 1])

    resolved_path = VIDGEN_DIR / f"{topic}_resolved.json"
    if not resolved_path.exists():
        print(f"Run resolve_word_triggers.py first")
        sys.exit(1)

    audit_collisions(resolved_path, interval)
