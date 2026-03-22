#!/usr/bin/env python3
"""Layout quality checker for TKK scene preview PNGs.

Analyzes vertical content distribution to catch common layout bugs:
- Content crammed to top half (empty bottom)
- Excessive empty space
- Content centroid too high

Usage:
    python qa_layout.py previews/math_wars_scene_1.png
    python qa_layout.py previews/                        # check all PNGs in dir
    python qa_layout.py previews/ --json                 # JSON output
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image
    import numpy as np
except ImportError:
    print("ERROR: requires Pillow and numpy — pip install Pillow numpy", file=sys.stderr)
    sys.exit(1)


# Background luminance threshold — pixels darker than this are "empty"
BG_THRESH = 20


def _luminance_array(img: Image.Image) -> np.ndarray:
    """Convert image to grayscale numpy array."""
    return np.array(img.convert("L"), dtype=np.float32)


def _is_letterbox(lum: np.ndarray, bar_frac: float = 0.06) -> bool:
    """Detect letterbox/punch scene (black bars at top and bottom)."""
    h = lum.shape[0]
    bar_h = int(h * bar_frac)
    top_avg = lum[:bar_h, :].mean()
    bot_avg = lum[-bar_h:, :].mean()
    return top_avg < 5 and bot_avg < 5


def check_vertical_coverage(lum: np.ndarray) -> dict:
    """Check content distribution between top and bottom halves."""
    h = lum.shape[0]
    mid = h // 2

    content_mask = lum > BG_THRESH
    total_content = content_mask.sum()

    if total_content < 100:
        return {"status": "skip", "detail": "No significant content detected"}

    top_content = content_mask[:mid, :].sum()
    bot_content = content_mask[mid:, :].sum()

    top_pct = top_content / total_content * 100
    bot_pct = bot_content / total_content * 100

    if bot_pct < 5:
        return {"status": "FAIL", "detail": f"Bottom half has {bot_pct:.0f}% of content (need >5%)",
                "top_pct": round(top_pct, 1), "bot_pct": round(bot_pct, 1)}
    if top_pct < 5:
        return {"status": "FAIL", "detail": f"Top half has {top_pct:.0f}% of content (need >5%)",
                "top_pct": round(top_pct, 1), "bot_pct": round(bot_pct, 1)}
    if bot_pct < 15:
        return {"status": "WARN", "detail": f"Bottom half has only {bot_pct:.0f}% of content (want >15%)",
                "top_pct": round(top_pct, 1), "bot_pct": round(bot_pct, 1)}
    if top_pct < 15:
        return {"status": "WARN", "detail": f"Top half has only {top_pct:.0f}% of content (want >15%)",
                "top_pct": round(top_pct, 1), "bot_pct": round(bot_pct, 1)}

    return {"status": "PASS", "detail": f"Top {top_pct:.0f}% / Bottom {bot_pct:.0f}%",
            "top_pct": round(top_pct, 1), "bot_pct": round(bot_pct, 1)}


def check_empty_space(lum: np.ndarray, grid_rows: int = 8, grid_cols: int = 4) -> dict:
    """Divide image into grid cells, count how many are empty."""
    h, w = lum.shape
    cell_h = h // grid_rows
    cell_w = w // grid_cols

    empty_cells = 0
    total_cells = grid_rows * grid_cols

    for r in range(grid_rows):
        for c in range(grid_cols):
            cell = lum[r * cell_h:(r + 1) * cell_h, c * cell_w:(c + 1) * cell_w]
            if cell.mean() < BG_THRESH and cell.std() < 5:
                empty_cells += 1

    empty_pct = empty_cells / total_cells * 100

    if empty_pct > 60:
        return {"status": "FAIL", "detail": f"{empty_pct:.0f}% of grid cells empty (max 60%)",
                "empty_pct": round(empty_pct, 1), "empty_cells": empty_cells, "total_cells": total_cells}
    if empty_pct > 40:
        return {"status": "WARN", "detail": f"{empty_pct:.0f}% of grid cells empty (want <40%)",
                "empty_pct": round(empty_pct, 1), "empty_cells": empty_cells, "total_cells": total_cells}

    return {"status": "PASS", "detail": f"{empty_pct:.0f}% empty ({empty_cells}/{total_cells} cells)",
            "empty_pct": round(empty_pct, 1), "empty_cells": empty_cells, "total_cells": total_cells}


def check_centroid(lum: np.ndarray) -> dict:
    """Check if content centroid is too high (crammed to top)."""
    content_mask = lum > BG_THRESH
    if content_mask.sum() < 100:
        return {"status": "skip", "detail": "No significant content"}

    ys, _ = np.where(content_mask)
    centroid_y = ys.mean()
    h = lum.shape[0]
    # centroid_y is in pixels from top. Normalize: 0=top, 1=bottom
    centroid_norm = centroid_y / h

    if centroid_norm < 0.35:
        return {"status": "WARN",
                "detail": f"Content centroid at {centroid_norm:.0%} from top — too high, push content lower",
                "centroid_norm": round(centroid_norm, 3)}

    return {"status": "PASS", "detail": f"Content centroid at {centroid_norm:.0%} from top",
            "centroid_norm": round(centroid_norm, 3)}


def analyze_preview(filepath: str) -> dict:
    """Run all layout checks on a preview PNG."""
    img = Image.open(filepath)
    lum = _luminance_array(img)

    result = {"file": str(filepath), "checks": []}

    # Detect letterbox — skip coverage checks for punch scenes
    letterbox = _is_letterbox(lum)
    if letterbox:
        result["checks"].append({"name": "letterbox", "status": "skip",
                                  "detail": "Letterbox scene detected — coverage checks skipped"})
        return result

    result["checks"].append({"name": "vertical_coverage", **check_vertical_coverage(lum)})
    result["checks"].append({"name": "empty_space", **check_empty_space(lum)})
    result["checks"].append({"name": "centroid", **check_centroid(lum)})

    return result


def print_result(result: dict):
    """Pretty-print a single file's results."""
    name = Path(result["file"]).name
    checks = result["checks"]
    worst = "PASS"
    for c in checks:
        if c["status"] == "FAIL":
            worst = "FAIL"
        elif c["status"] == "WARN" and worst != "FAIL":
            worst = "WARN"

    icon = {"PASS": "+", "WARN": "!", "FAIL": "X", "skip": "-"}
    print(f"\n[{icon.get(worst, '?')}] {name}")
    for c in checks:
        s = c["status"]
        print(f"    [{icon.get(s, '?')}] {c['name']}: {c['detail']}")


def main():
    parser = argparse.ArgumentParser(description="TKK layout quality checker")
    parser.add_argument("path", help="PNG file or directory of PNGs")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    p = Path(args.path)
    if p.is_dir():
        files = sorted(p.glob("*.png"))
    elif p.is_file():
        files = [p]
    else:
        print(f"ERROR: {p} not found", file=sys.stderr)
        sys.exit(1)

    if not files:
        print(f"No PNG files found in {p}", file=sys.stderr)
        sys.exit(1)

    results = [analyze_preview(str(f)) for f in files]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        has_fail = False
        has_warn = False
        for r in results:
            print_result(r)
            for c in r["checks"]:
                if c["status"] == "FAIL":
                    has_fail = True
                elif c["status"] == "WARN":
                    has_warn = True

        total = len(results)
        print(f"\n{'='*50}")
        print(f"  {total} scenes checked", end="")
        if has_fail:
            print(" — FAIL (layout issues found)")
        elif has_warn:
            print(" — WARN (minor layout issues)")
        else:
            print(" — PASS")
        print(f"{'='*50}")

    sys.exit(1 if has_fail else 0)


if __name__ == "__main__":
    main()
