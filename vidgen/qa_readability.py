#!/usr/bin/env python3
"""TKK Scene Readability Checker — Pre-render QA tool.

Checks preview PNGs for:
1. Text/background contrast ratio (WCAG AA = 4.5:1, AAA = 7:1)
2. Grid-based luminance mapping to detect low-contrast zones
3. Edge margin safety (TikTok safe zone: 10% inset)

Usage:
    python qa_readability.py /path/to/preview.png
    python qa_readability.py /path/to/previews/     # check all PNGs in dir
    python qa_readability.py --grid /path/to/preview.png  # output contrast grid image

Returns exit code 1 if any scene fails minimum contrast threshold.
"""

import sys
import os
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
except ImportError:
    print("ERROR: pip install Pillow numpy")
    sys.exit(1)


# --- WCAG contrast ratio ---

def relative_luminance(rgb):
    """WCAG 2.0 relative luminance from sRGB."""
    r, g, b = [c / 255.0 for c in rgb[:3]]
    r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(l1, l2):
    """WCAG contrast ratio between two luminance values."""
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


# --- Grid analysis ---

def analyze_grid(img, rows=12, cols=8):
    """Divide image into grid cells, compute avg luminance per cell.

    Returns:
        grid: 2D array of average luminance values (0-1)
        cell_size: (cell_w, cell_h)
    """
    arr = np.array(img.convert("RGB"))
    h, w = arr.shape[:2]
    cell_h = h // rows
    cell_w = w // cols

    grid = np.zeros((rows, cols))
    for r in range(rows):
        for c in range(cols):
            y0, y1 = r * cell_h, (r + 1) * cell_h
            x0, x1 = c * cell_w, (c + 1) * cell_w
            cell = arr[y0:y1, x0:x1]
            avg_rgb = cell.mean(axis=(0, 1))
            grid[r, c] = relative_luminance(avg_rgb)

    return grid, (cell_w, cell_h)


def find_text_regions(img, luminance_threshold=0.15):
    """Detect likely text regions by finding high-variance horizontal bands.

    Text regions have high luminance variance (bright text on dark bg or vice versa).
    Returns list of (y_start, y_end, avg_text_luminance, avg_bg_luminance, contrast).
    """
    arr = np.array(img.convert("RGB"))
    h, w = arr.shape[:2]

    # Compute per-row luminance
    row_lum = np.zeros(h)
    for y in range(h):
        row_rgb = arr[y].mean(axis=0)
        row_lum[y] = relative_luminance(row_rgb)

    # Compute per-row variance (sliding window)
    window = 20
    row_var = np.zeros(h)
    for y in range(window, h - window):
        row_var[y] = np.std(row_lum[y-window:y+window])

    # Find high-variance bands (likely text)
    threshold = np.percentile(row_var[row_var > 0], 75) if np.any(row_var > 0) else 0.01
    text_bands = []
    in_band = False
    band_start = 0

    for y in range(h):
        if row_var[y] > threshold and not in_band:
            band_start = y
            in_band = True
        elif (row_var[y] <= threshold or y == h - 1) and in_band:
            if y - band_start > 15:  # minimum band height
                # Sample text vs background luminance
                band = arr[band_start:y]
                band_lum = np.array([relative_luminance(px) for px in band.reshape(-1, 3)])

                # Split into bright (text) and dark (bg) pixels
                median_lum = np.median(band_lum)
                bright = band_lum[band_lum > median_lum]
                dark = band_lum[band_lum <= median_lum]

                if len(bright) > 0 and len(dark) > 0:
                    text_lum = np.mean(bright)
                    bg_lum = np.mean(dark)
                    cr = contrast_ratio(text_lum, bg_lum)
                    text_bands.append((band_start, y, text_lum, bg_lum, cr))
            in_band = False

    return text_bands


def check_margins(img, margin_pct=0.10):
    """Check if content exists in the TikTok unsafe zone (outer 10%).

    Returns list of issues.
    """
    arr = np.array(img.convert("RGB"))
    h, w = arr.shape[:2]

    margin_x = int(w * margin_pct)
    margin_y = int(h * margin_pct)

    issues = []

    # Check each margin strip for non-background content
    # (content = significantly different luminance from corners)
    corner_rgb = arr[5:15, 5:15].mean(axis=(0, 1))
    corner_lum = relative_luminance(corner_rgb)

    zones = {
        "left": arr[margin_y:h-margin_y, :margin_x],
        "right": arr[margin_y:h-margin_y, w-margin_x:],
        "top": arr[:margin_y, margin_x:w-margin_x],
        "bottom": arr[h-margin_y:, margin_x:w-margin_x],
    }

    for zone_name, zone in zones.items():
        zone_lum = np.mean([relative_luminance(px) for px in zone.reshape(-1, 3)[::50]])
        diff = abs(zone_lum - corner_lum)
        if diff > 0.15:
            issues.append(f"Content near {zone_name} edge (lum diff: {diff:.2f})")

    return issues


def generate_contrast_grid(img, output_path, rows=12, cols=8):
    """Generate a visual contrast grid overlay image for QA."""
    grid, (cell_w, cell_h) = analyze_grid(img, rows, cols)

    overlay = img.convert("RGB").copy()
    draw = ImageDraw.Draw(overlay)

    for r in range(rows):
        for c in range(cols):
            x0, y0 = c * cell_w, r * cell_h
            x1, y1 = x0 + cell_w, y0 + cell_h
            lum = grid[r, c]

            # Color code: red = very dark (hard to read light text on),
            #              yellow = mid, green = good contrast possible
            if lum < 0.05:
                color = (255, 0, 0, 80)  # very dark - red
            elif lum < 0.15:
                color = (255, 165, 0, 60)  # dark - orange
            elif lum > 0.7:
                color = (255, 255, 0, 60)  # very bright - yellow (dark text needed)
            else:
                color = (0, 255, 0, 40)  # mid - green

            # Draw cell border and label
            draw.rectangle([x0, y0, x1, y1], outline=(255, 255, 255, 100))
            label = f"{lum:.2f}"
            draw.text((x0 + 4, y0 + 4), label, fill=(255, 255, 255))

    overlay.save(output_path)
    return output_path


def check_scene(image_path, verbose=True):
    """Run full QA check on a single scene preview PNG.

    Returns (passed: bool, report: str)
    """
    img = Image.open(image_path)
    name = Path(image_path).stem

    report = []
    report.append(f"=== QA: {name} ({img.width}x{img.height}) ===")

    passed = True

    # 1. Text region contrast
    bands = find_text_regions(img)
    report.append(f"\nText regions detected: {len(bands)}")

    for i, (y0, y1, text_lum, bg_lum, cr) in enumerate(bands):
        status = "PASS" if cr >= 4.5 else "WARN" if cr >= 3.0 else "FAIL"
        if status == "FAIL":
            passed = False
        wcag = "AAA" if cr >= 7.0 else "AA" if cr >= 4.5 else "BELOW AA"
        report.append(f"  Band {i+1} (y:{y0}-{y1}): contrast {cr:.1f}:1 [{wcag}] {status}")
        if cr < 4.5:
            report.append(f"    -> Text lum: {text_lum:.3f}, BG lum: {bg_lum:.3f}")

    # 2. Grid luminance
    grid, _ = analyze_grid(img)
    min_lum = grid.min()
    max_lum = grid.max()
    report.append(f"\nLuminance range: {min_lum:.3f} - {max_lum:.3f}")

    # Flag cells in the middle 60% that are very uniform (text might blend)
    mid_rows = grid[3:9]  # middle 6 of 12 rows
    mid_range = mid_rows.max() - mid_rows.min()
    if mid_range < 0.03:
        report.append(f"  WARN: Center zone very uniform (range {mid_range:.3f}) — text may blend")

    # 3. Margin safety
    margin_issues = check_margins(img)
    if margin_issues:
        for issue in margin_issues:
            report.append(f"  WARN: {issue}")
    else:
        report.append("  Margins: OK (10% safe zone clear)")

    # Overall
    report.append(f"\n{'PASS' if passed else 'FAIL'}: {name}")
    report.append("")

    return passed, "\n".join(report)


def main():
    args = sys.argv[1:]
    generate_grid = "--grid" in args
    args = [a for a in args if not a.startswith("--")]

    if not args:
        print(__doc__)
        sys.exit(0)

    target = args[0]

    if os.path.isdir(target):
        files = sorted(Path(target).glob("*.png"))
    else:
        files = [Path(target)]

    all_passed = True
    for f in files:
        passed, report = check_scene(str(f))
        print(report)
        if not passed:
            all_passed = False

        if generate_grid:
            grid_path = f.parent / f"{f.stem}_contrast_grid.png"
            generate_contrast_grid(Image.open(str(f)), str(grid_path))
            print(f"  Grid saved: {grid_path}")

    if not all_passed:
        print("\n!!! SOME SCENES FAILED CONTRAST CHECK — FIX BEFORE RENDERING !!!")
        sys.exit(1)
    else:
        print("\nAll scenes passed readability check.")
        sys.exit(0)


if __name__ == "__main__":
    main()
