#!/usr/bin/env python3
"""
qa_animation_coverage.py — Visual complexity and scene similarity analysis.

Detects:
- Adjacent scenes that look identical (render failure)
- Content regions too small/narrow (not using frame)
- Low visual complexity (boring scenes)
- Unbalanced quadrant distribution

Usage:
    python3 qa_animation_coverage.py <topic> [--json] [--verbose]
"""

import sys
import os
import json
import argparse
from pathlib import Path

# Auto-activate venv
VENV = Path(__file__).parent / ".venv"
if VENV.exists() and "VIRTUAL_ENV" not in os.environ:
    site_packages = next(VENV.glob("lib/python*/site-packages"), None)
    if site_packages:
        sys.path.insert(0, str(site_packages))

try:
    from PIL import Image
    import numpy as np
except ImportError:
    print("ERROR: PIL and numpy required. Install: pip install Pillow numpy")
    sys.exit(1)

# Frame constants
WIDTH = 1080
HEIGHT = 1920
SAFE_TOP = 200
SAFE_BOTTOM = 1520
SAFE_LEFT = 120
SAFE_RIGHT = 940

# Thresholds
BG_THRESHOLD = 30
SIMILARITY_WARN_PCT = 5.0   # < 5% pixel diff = WARN
SIMILARITY_FAIL_PCT = 2.0   # < 2% pixel diff = FAIL
MIN_CONTENT_W = 300
MIN_CONTENT_H = 400
MIN_CONTENT_BOX = 100       # content bbox < 100x100 = FAIL
LOW_COMPLEXITY = 10          # complexity score < 10 = WARN
QUADRANT_IMBALANCE = 0.60   # >60% in one quadrant = WARN


def detect_bg_color(img):
    """Detect background color from corners."""
    pixels = [
        img.getpixel((5, 5)),
        img.getpixel((WIDTH - 5, 5)),
        img.getpixel((5, HEIGHT - 5)),
        img.getpixel((WIDTH - 5, HEIGHT - 5)),
    ]
    r = sum(p[0] for p in pixels) // 4
    g = sum(p[1] for p in pixels) // 4
    b = sum(p[2] for p in pixels) // 4
    return (r, g, b)


def get_content_mask(arr, bg_color):
    """Return boolean mask where pixels differ from background by > BG_THRESHOLD."""
    bg = np.array(bg_color, dtype=np.float32)
    diff = np.sqrt(np.sum((arr.astype(np.float32) - bg) ** 2, axis=2))
    return diff > BG_THRESHOLD


# ---------------------------------------------------------------------------
# 1. Scene Similarity Detection
# ---------------------------------------------------------------------------

def check_scene_similarity(img_a, img_b, scene_a, scene_b):
    """Compare two adjacent scene images for pixel-level similarity."""
    arr_a = np.array(img_a.convert("RGB"))[:, :, :3].astype(np.float32)
    arr_b = np.array(img_b.convert("RGB"))[:, :, :3].astype(np.float32)

    # Per-pixel Euclidean distance, then threshold to count "different" pixels
    diff = np.sqrt(np.sum((arr_a - arr_b) ** 2, axis=2))
    different_pixels = np.sum(diff > BG_THRESHOLD)
    total_pixels = diff.size
    diff_pct = (different_pixels / total_pixels) * 100

    label = f"Scenes {scene_a}->{scene_b}"

    if diff_pct < SIMILARITY_FAIL_PCT:
        return {
            "check": "scene_similarity",
            "status": "FAIL",
            "detail": f"{label}: Only {diff_pct:.1f}% pixels differ — scenes appear to be the same frame",
            "diff_pct": round(diff_pct, 2),
        }
    elif diff_pct < SIMILARITY_WARN_PCT:
        return {
            "check": "scene_similarity",
            "status": "WARN",
            "detail": f"{label}: Only {diff_pct:.1f}% pixels differ — scenes look identical",
            "diff_pct": round(diff_pct, 2),
        }
    else:
        return {
            "check": "scene_similarity",
            "status": "PASS",
            "detail": f"{label}: {diff_pct:.1f}% pixels differ",
            "diff_pct": round(diff_pct, 2),
        }


# ---------------------------------------------------------------------------
# 2. Content Region Detection
# ---------------------------------------------------------------------------

def check_content_region(content_mask, scene_num):
    """Find bounding box of non-background content and check dimensions."""
    ys, xs = np.where(content_mask)

    if len(ys) == 0:
        return {
            "check": "content_region",
            "status": "FAIL",
            "detail": f"Scene {scene_num}: No content detected — frame is entirely background",
            "bbox": None,
        }

    y_min, y_max = int(ys.min()), int(ys.max())
    x_min, x_max = int(xs.min()), int(xs.max())
    w = x_max - x_min
    h = y_max - y_min

    bbox = {"x_min": x_min, "y_min": y_min, "x_max": x_max, "y_max": y_max, "w": w, "h": h}

    if w < MIN_CONTENT_BOX and h < MIN_CONTENT_BOX:
        return {
            "check": "content_region",
            "status": "FAIL",
            "detail": f"Scene {scene_num}: Content bbox {w}x{h}px — essentially empty (need >{MIN_CONTENT_BOX}x{MIN_CONTENT_BOX})",
            "bbox": bbox,
        }

    warnings = []
    if w < MIN_CONTENT_W:
        warnings.append(f"width {w}px < {MIN_CONTENT_W}px (too narrow)")
    if h < MIN_CONTENT_H:
        warnings.append(f"height {h}px < {MIN_CONTENT_H}px (not using vertical space)")

    if warnings:
        return {
            "check": "content_region",
            "status": "WARN",
            "detail": f"Scene {scene_num}: Content bbox {w}x{h}px — {'; '.join(warnings)}",
            "bbox": bbox,
        }

    return {
        "check": "content_region",
        "status": "PASS",
        "detail": f"Scene {scene_num}: Content bbox {w}x{h}px at ({x_min},{y_min})-({x_max},{y_max})",
        "bbox": bbox,
    }


# ---------------------------------------------------------------------------
# 3. Visual Complexity Score
# ---------------------------------------------------------------------------

def compute_complexity(arr):
    """Compute a 0-100 complexity score from color variety and edge density."""
    h, w, _ = arr.shape

    # --- Color cluster count (quantize to 16 levels per channel) ---
    quantized = (arr // 16).astype(np.uint8)
    # Pack into single int per pixel for unique counting
    packed = quantized[:, :, 0].astype(np.uint32) * 65536 + \
             quantized[:, :, 1].astype(np.uint32) * 256 + \
             quantized[:, :, 2].astype(np.uint32)
    unique_colors = len(np.unique(packed))
    # Max possible with 16^3 = 4096 quantized colors; normalize
    color_score = min(unique_colors / 200.0, 1.0)  # 200+ distinct clusters = max

    # --- Edge density (simple Sobel-like gradient magnitude) ---
    gray = np.mean(arr.astype(np.float32), axis=2)
    # Horizontal and vertical gradients (avoid edges of image)
    gx = np.abs(gray[:, 2:] - gray[:, :-2])
    gy = np.abs(gray[2:, :] - gray[:-2, :])
    # Trim to same size
    min_h = min(gx.shape[0], gy.shape[0])
    min_w = min(gx.shape[1], gy.shape[1])
    gx = gx[:min_h, :min_w]
    gy = gy[:min_h, :min_w]
    grad_mag = np.sqrt(gx ** 2 + gy ** 2)
    # Fraction of pixels with meaningful edge (threshold > 15)
    edge_frac = np.sum(grad_mag > 15) / grad_mag.size
    edge_score = min(edge_frac / 0.15, 1.0)  # 15%+ edge pixels = max

    # Combined score: 50% color, 50% edges
    score = (color_score * 0.5 + edge_score * 0.5) * 100
    return round(score, 1), unique_colors, round(edge_frac * 100, 2)


def check_visual_complexity(arr, scene_num):
    """Check if a scene has enough visual complexity."""
    score, color_count, edge_pct = compute_complexity(arr)

    if score < LOW_COMPLEXITY:
        return {
            "check": "visual_complexity",
            "status": "WARN",
            "detail": f"Scene {scene_num}: Complexity {score}/100 — too simple ({color_count} color clusters, {edge_pct}% edges)",
            "score": score,
            "color_clusters": color_count,
            "edge_pct": edge_pct,
        }

    return {
        "check": "visual_complexity",
        "status": "PASS",
        "detail": f"Scene {scene_num}: Complexity {score}/100 ({color_count} clusters, {edge_pct}% edges)",
        "score": score,
        "color_clusters": color_count,
        "edge_pct": edge_pct,
    }


# ---------------------------------------------------------------------------
# 4. Symmetry / Balance Score (Quadrant analysis)
# ---------------------------------------------------------------------------

def check_quadrant_balance(content_mask, scene_num):
    """Check content density per quadrant; flag if one quadrant dominates."""
    h, w = content_mask.shape
    mid_y = h // 2
    mid_x = w // 2

    quadrants = {
        "TL": content_mask[:mid_y, :mid_x],
        "TR": content_mask[:mid_y, mid_x:],
        "BL": content_mask[mid_y:, :mid_x],
        "BR": content_mask[mid_y:, mid_x:],
    }

    counts = {name: int(np.sum(q)) for name, q in quadrants.items()}
    total = sum(counts.values())

    if total < 100:
        return {
            "check": "quadrant_balance",
            "status": "PASS",
            "detail": f"Scene {scene_num}: Insufficient content for balance check",
            "quadrants": counts,
        }

    fracs = {name: c / total for name, c in counts.items()}
    dominant = max(fracs, key=fracs.get)
    dominant_pct = fracs[dominant] * 100

    frac_str = ", ".join(f"{n}={f:.0%}" for n, f in fracs.items())

    if dominant_pct > QUADRANT_IMBALANCE * 100:
        return {
            "check": "quadrant_balance",
            "status": "WARN",
            "detail": f"Scene {scene_num}: Unbalanced — {dominant} has {dominant_pct:.0f}% of content ({frac_str})",
            "quadrants": {n: round(f, 3) for n, f in fracs.items()},
            "dominant": dominant,
            "dominant_pct": round(dominant_pct, 1),
        }

    return {
        "check": "quadrant_balance",
        "status": "PASS",
        "detail": f"Scene {scene_num}: Balanced ({frac_str})",
        "quadrants": {n: round(f, 3) for n, f in fracs.items()},
    }


# ---------------------------------------------------------------------------
# Per-scene analysis
# ---------------------------------------------------------------------------

def analyze_scene(img_path, scene_num):
    """Run all per-scene checks on a single preview PNG."""
    img = Image.open(img_path).convert("RGB")
    if img.size != (WIDTH, HEIGHT):
        img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)

    arr = np.array(img)[:, :, :3]
    bg_color = detect_bg_color(img)
    content_mask = get_content_mask(arr, bg_color)

    checks = []
    checks.append(check_content_region(content_mask, scene_num))
    checks.append(check_visual_complexity(arr, scene_num))
    checks.append(check_quadrant_balance(content_mask, scene_num))

    return {
        "scene": scene_num,
        "file": str(img_path),
        "bg_color": f"#{bg_color[0]:02x}{bg_color[1]:02x}{bg_color[2]:02x}",
        "checks": checks,
    }


# ---------------------------------------------------------------------------
# Topic-level analysis (main entry point)
# ---------------------------------------------------------------------------

def analyze_topic(topic: str) -> dict:
    """Analyze all preview PNGs for a topic. Returns structured QA report."""
    preview_dir = Path(__file__).parent / "previews"
    previews = sorted(preview_dir.glob(f"{topic}_scene_*.png"))

    if not previews:
        return {
            "topic": topic,
            "status": "FAIL",
            "total_fails": 1,
            "total_warns": 0,
            "scenes": [],
            "similarity_checks": [],
            "error": f"No previews found for topic \"{topic}\" in {preview_dir}",
        }

    all_checks = []
    scene_results = []
    similarity_checks = []

    # Per-scene analysis
    loaded_images = []
    scene_nums = []
    for preview_path in previews:
        scene_num = int(preview_path.stem.split("_scene_")[1])
        scene_nums.append(scene_num)
        result = analyze_scene(preview_path, scene_num)
        scene_results.append(result)
        all_checks.extend(result["checks"])
        loaded_images.append(Image.open(preview_path).convert("RGB"))

    # Adjacent scene similarity
    for i in range(len(loaded_images) - 1):
        img_a = loaded_images[i]
        img_b = loaded_images[i + 1]
        # Resize if needed
        if img_a.size != (WIDTH, HEIGHT):
            img_a = img_a.resize((WIDTH, HEIGHT), Image.LANCZOS)
        if img_b.size != (WIDTH, HEIGHT):
            img_b = img_b.resize((WIDTH, HEIGHT), Image.LANCZOS)
        sim_check = check_scene_similarity(img_a, img_b, scene_nums[i], scene_nums[i + 1])
        similarity_checks.append(sim_check)
        all_checks.append(sim_check)

    fails = sum(1 for c in all_checks if c["status"] == "FAIL")
    warns = sum(1 for c in all_checks if c["status"] == "WARN")
    status = "FAIL" if fails > 0 else ("WARN" if warns > 0 else "PASS")

    return {
        "topic": topic,
        "status": status,
        "total_fails": fails,
        "total_warns": warns,
        "scene_count": len(previews),
        "scenes": scene_results,
        "similarity_checks": similarity_checks,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def print_report(report: dict, verbose: bool = False):
    """Pretty-print the QA report."""
    topic = report["topic"]
    status = report["status"]
    scene_count = report.get("scene_count", 0)

    print(f"Animation Coverage QA: {scene_count} scenes for \"{topic}\"")
    print("=" * 60)

    if report.get("error"):
        print(f"  ERROR: {report['error']}")
        return

    icon_map = {"PASS": "+", "WARN": "!", "FAIL": "X"}

    # Per-scene results
    for sr in report["scenes"]:
        worst = "PASS"
        for c in sr["checks"]:
            if c["status"] == "FAIL":
                worst = "FAIL"
            elif c["status"] == "WARN" and worst != "FAIL":
                worst = "WARN"

        print(f"\n[{icon_map.get(worst, '?')}] Scene {sr['scene']} (bg: {sr['bg_color']})")
        for c in sr["checks"]:
            s = c["status"]
            print(f"    [{icon_map.get(s, '?')}] {c['check']}: {c['detail']}")

    # Similarity checks
    if report["similarity_checks"]:
        print(f"\n--- Adjacent Scene Similarity ---")
        for c in report["similarity_checks"]:
            s = c["status"]
            print(f"  [{icon_map.get(s, '?')}] {c['detail']}")

    # Summary
    fails = report["total_fails"]
    warns = report["total_warns"]
    print(f"\n{'=' * 60}")
    print(f"  {scene_count} scenes checked", end="")
    if fails:
        print(f" — FAIL ({fails} fails, {warns} warnings)")
    elif warns:
        print(f" — WARN ({warns} warnings)")
    else:
        print(" — PASS")
    print(f"{'=' * 60}")


def main():
    parser = argparse.ArgumentParser(description="Visual complexity and scene similarity QA")
    parser.add_argument("topic", help="Topic name")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    report = analyze_topic(args.topic)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report, verbose=args.verbose)

    sys.exit(1 if report["total_fails"] > 0 else 0)


if __name__ == "__main__":
    main()
