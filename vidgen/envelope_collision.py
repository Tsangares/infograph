#!/usr/bin/env python3
"""
Envelope-based Collision Detection for Word-Triggered TKK Videos

Reads {topic}_envelopes.json (computed by computeEnvelopes.mts) and detects
collisions using convex hull envelopes that capture each element's full
animation lifecycle — including spring overshoots, hold motions, and exits.

Higher sensitivity than collision_audit.py (which checks static bboxes at
discrete time steps). This is the "debug-QA" pre-render collision checker.

Usage:
    python envelope_collision.py <topic> [--json]
"""

import json
import sys
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timezone

VIDGEN_DIR = Path(__file__).parent
CANVAS_W = 1080
CANVAS_H = 1920

# Zone pixel boundaries (from zones.ts)
def _uty(unit_y: float) -> float:
    """Convert unit y-coordinate (-8 to +8 range) to pixel y (top-down)."""
    return ((8 - unit_y) / 16) * CANVAS_H

ZONES = {
    "TITLE":  {"top": _uty(7.0),  "bottom": _uty(5.5)},
    "UPPER":  {"top": _uty(5.5),  "bottom": _uty(1.5)},
    "MID":    {"top": _uty(1.5),  "bottom": _uty(-1.5)},
    "LOWER":  {"top": _uty(-1.5), "bottom": _uty(-5.5)},
    "FOOTER": {"top": _uty(-5.5), "bottom": _uty(-6.4)},
}

SAFE = {"top": 200, "bottom": 1520, "left": 120, "right": 940}


# ── Geometry helpers ──────────────────────────────────────────

@dataclass
class Polygon:
    """Convex polygon as list of (x, y) vertices in order."""
    pts: list[tuple[float, float]]

    def area(self) -> float:
        """Shoelace formula."""
        n = len(self.pts)
        if n < 3:
            return 0.0
        a = 0.0
        for i in range(n):
            j = (i + 1) % n
            a += self.pts[i][0] * self.pts[j][1]
            a -= self.pts[j][0] * self.pts[i][1]
        return abs(a) / 2.0


def _aabb_overlaps(a: dict, b: dict) -> bool:
    """Fast AABB overlap test."""
    if a["x"] >= b["x"] + b["w"] or b["x"] >= a["x"] + a["w"]:
        return False
    if a["y"] >= b["y"] + b["h"] or b["y"] >= a["y"] + a["h"]:
        return False
    return True


def _clip_polygon_by_edge(poly: list[tuple[float, float]],
                           ex: float, ey: float,
                           nx: float, ny: float) -> list[tuple[float, float]]:
    """Sutherland-Hodgman: clip polygon by one edge defined by point (ex,ey) and inward normal (nx,ny)."""
    if not poly:
        return []
    result = []
    n = len(poly)
    for i in range(n):
        curr = poly[i]
        nxt = poly[(i + 1) % n]
        dc = (curr[0] - ex) * nx + (curr[1] - ey) * ny
        dn = (nxt[0] - ex) * nx + (nxt[1] - ey) * ny
        if dc >= 0:
            result.append(curr)
            if dn < 0:
                t = dc / (dc - dn)
                result.append((curr[0] + t * (nxt[0] - curr[0]),
                               curr[1] + t * (nxt[1] - curr[1])))
        elif dn >= 0:
            t = dc / (dc - dn)
            result.append((curr[0] + t * (nxt[0] - curr[0]),
                           curr[1] + t * (nxt[1] - curr[1])))
    return result


def polygon_intersection_area(hull_a: list[dict], hull_b: list[dict]) -> float:
    """Compute intersection area of two convex polygons using Sutherland-Hodgman clipping."""
    if len(hull_a) < 3 or len(hull_b) < 3:
        return 0.0

    # Convert to tuples
    clip = [(p["x"], p["y"]) for p in hull_b]
    subject = [(p["x"], p["y"]) for p in hull_a]

    result = list(subject)

    for i in range(len(clip)):
        if not result:
            return 0.0
        edge_start = clip[i]
        edge_end = clip[(i + 1) % len(clip)]

        # Inward normal (pointing into the polygon)
        dx = edge_end[0] - edge_start[0]
        dy = edge_end[1] - edge_start[1]
        # For a CCW polygon, inward normal is (-dy, dx). For CW, it's (dy, -dx).
        # We don't know winding, so compute area sign to determine.
        nx, ny = -dy, dx

        result = _clip_polygon_by_edge(result, edge_start[0], edge_start[1], nx, ny)

    return Polygon(result).area()


def polygon_area(hull: list[dict]) -> float:
    pts = [(p["x"], p["y"]) for p in hull]
    return Polygon(pts).area()


# ── Collision types ───────────────────────────────────────────

@dataclass
class Collision:
    scene_id: str
    elem_a: dict
    elem_b: dict
    severity: str  # CRITICAL, WARN, minor
    overlap_pct: float
    overlap_area_px: float
    collision_type: str  # element_overlap, zone_bleed, safe_area_violation

    def to_dict(self) -> dict:
        return {
            "scene_id": self.scene_id,
            "elem_a": self.elem_a,
            "elem_b": self.elem_b,
            "severity": self.severity,
            "overlap_pct": round(self.overlap_pct, 1),
            "overlap_area_px": round(self.overlap_area_px),
            "collision_type": self.collision_type,
        }


def _elem_ref(elem: dict) -> dict:
    return {"index": elem["index"], "type": elem["type"], "zone": elem["zone"]}


# ── Temporal overlap check ────────────────────────────────────

def _frames_overlap(a: list[int], b: list[int]) -> bool:
    return a[0] < b[1] and b[0] < a[1]


# ── Main audit ────────────────────────────────────────────────

def audit_envelope_collisions(envelopes_path: Path) -> list[Collision]:
    data = json.loads(envelopes_path.read_text())
    collisions: list[Collision] = []

    for scene in data["scenes"]:
        elements = scene["elements"]
        scene_id = scene["id"]
        n = len(elements)

        # 1. Pairwise element collision detection
        for i in range(n):
            for j in range(i + 1, n):
                a = elements[i]
                b = elements[j]

                # Skip if not temporally overlapping
                if not _frames_overlap(a["visible_frames"], b["visible_frames"]):
                    continue

                aabb_a = a["envelope"]["aabb"]
                aabb_b = b["envelope"]["aabb"]

                # Fast AABB reject
                if not _aabb_overlaps(aabb_a, aabb_b):
                    continue

                # Full polygon intersection
                hull_a = a["envelope"]["hull"]
                hull_b = b["envelope"]["hull"]
                area = polygon_intersection_area(hull_a, hull_b)

                if area < 1.0:
                    continue  # sub-pixel, ignore

                # Severity based on overlap as % of smaller element
                area_a = polygon_area(hull_a)
                area_b = polygon_area(hull_b)
                smaller = min(area_a, area_b) if min(area_a, area_b) > 0 else 1
                pct = (area / smaller) * 100

                if pct > 50:
                    severity = "CRITICAL"
                elif pct > 20:
                    severity = "WARN"
                else:
                    severity = "minor"

                collisions.append(Collision(
                    scene_id=scene_id,
                    elem_a=_elem_ref(a),
                    elem_b=_elem_ref(b),
                    severity=severity,
                    overlap_pct=pct,
                    overlap_area_px=area,
                    collision_type="element_overlap",
                ))

        # 2. Zone bleed detection
        for elem in elements:
            zone_name = elem["zone"]
            zone = ZONES.get(zone_name)
            if not zone:
                continue
            aabb = elem["envelope"]["aabb"]
            tolerance = 10  # 10px tolerance

            bleed_top = zone["top"] - aabb["y"]
            bleed_bottom = (aabb["y"] + aabb["h"]) - zone["bottom"]

            if bleed_top > tolerance or bleed_bottom > tolerance:
                bleed_px = max(bleed_top, bleed_bottom)
                collisions.append(Collision(
                    scene_id=scene_id,
                    elem_a=_elem_ref(elem),
                    elem_b={"zone": zone_name, "top": round(zone["top"]), "bottom": round(zone["bottom"])},
                    severity="WARN" if bleed_px > 30 else "minor",
                    overlap_pct=0,
                    overlap_area_px=bleed_px * aabb["w"],
                    collision_type="zone_bleed",
                ))

        # 3. Safe area violations
        for elem in elements:
            aabb = elem["envelope"]["aabb"]
            violations = []
            if aabb["y"] < SAFE["top"]:
                violations.append(f"top by {SAFE['top'] - aabb['y']:.0f}px")
            if aabb["y"] + aabb["h"] > SAFE["bottom"]:
                violations.append(f"bottom by {aabb['y'] + aabb['h'] - SAFE['bottom']:.0f}px")
            if aabb["x"] + aabb["w"] > SAFE["right"]:
                violations.append(f"right by {aabb['x'] + aabb['w'] - SAFE['right']:.0f}px")

            if violations:
                collisions.append(Collision(
                    scene_id=scene_id,
                    elem_a=_elem_ref(elem),
                    elem_b={"safe_area": SAFE, "violations": violations},
                    severity="WARN",
                    overlap_pct=0,
                    overlap_area_px=0,
                    collision_type="safe_area_violation",
                ))

    return collisions


def format_report(collisions: list[Collision], topic: str) -> str:
    lines = []
    lines.append("=" * 80)
    lines.append(f"ENVELOPE COLLISION AUDIT (debug-QA): {topic}")
    lines.append("=" * 80)

    if not collisions:
        lines.append("\n  No collisions detected.\n")
        lines.append("RESULT: PASS")
        return "\n".join(lines)

    # Group by severity
    by_severity: dict[str, list[Collision]] = {"CRITICAL": [], "WARN": [], "minor": []}
    for c in collisions:
        by_severity.setdefault(c.severity, []).append(c)

    for sev in ["CRITICAL", "WARN", "minor"]:
        items = by_severity.get(sev, [])
        if not items:
            continue
        lines.append(f"\n{'─' * 40}")
        lines.append(f"  {sev} ({len(items)})")
        lines.append(f"{'─' * 40}")

        for c in items:
            a = c.elem_a
            b = c.elem_b
            if c.collision_type == "element_overlap":
                lines.append(f"  Scene '{c.scene_id}': [{a['index']}] {a['type']} ({a['zone']}) ↔ [{b['index']}] {b['type']} ({b['zone']})")
                lines.append(f"    Overlap: {c.overlap_pct:.1f}% ({c.overlap_area_px:.0f}px²)")
            elif c.collision_type == "zone_bleed":
                lines.append(f"  Scene '{c.scene_id}': [{a['index']}] {a['type']} bleeds outside {b.get('zone', '?')}")
                lines.append(f"    Bleed area: {c.overlap_area_px:.0f}px²")
            elif c.collision_type == "safe_area_violation":
                violations = b.get("violations", [])
                lines.append(f"  Scene '{c.scene_id}': [{a['index']}] {a['type']} in unsafe area: {', '.join(violations)}")

    # Summary
    n_crit = len(by_severity.get("CRITICAL", []))
    n_warn = len(by_severity.get("WARN", []))
    n_minor = len(by_severity.get("minor", []))
    lines.append(f"\nSummary: {n_crit} CRITICAL, {n_warn} WARN, {n_minor} minor")

    if n_crit > 0:
        lines.append("RESULT: FAIL")
    elif n_warn > 0:
        lines.append("RESULT: WARN")
    else:
        lines.append("RESULT: PASS")

    return "\n".join(lines)


def get_summary(collisions: list[Collision]) -> dict:
    by_sev = {}
    for c in collisions:
        by_sev[c.severity] = by_sev.get(c.severity, 0) + 1
    return {
        "critical": by_sev.get("CRITICAL", 0),
        "warn": by_sev.get("WARN", 0),
        "minor": by_sev.get("minor", 0),
    }


if __name__ == "__main__":
    args = sys.argv[1:]
    json_mode = "--json" in args
    args = [a for a in args if not a.startswith("--")]

    if not args:
        print("Usage: python envelope_collision.py <topic> [--json]")
        sys.exit(1)

    topic = args[0]
    env_path = VIDGEN_DIR / f"{topic}_envelopes.json"

    if not env_path.exists():
        print(f"ERROR: {env_path} not found. Run computeEnvelopes.mts first.")
        sys.exit(1)

    collisions = audit_envelope_collisions(env_path)

    if json_mode:
        print(json.dumps({
            "topic": topic,
            "collisions": [c.to_dict() for c in collisions],
            "summary": get_summary(collisions),
        }, indent=2))
    else:
        print(format_report(collisions, topic))
