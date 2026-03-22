#!/usr/bin/env python3
"""TKK Element Visibility Checker — detects dark-on-dark icons/shapes.

Analyzes preview PNGs for graphic elements that are nearly invisible against
the dark background (#080A10). Catches icons rendered with currentColor
defaulting to black, or detail elements using fill="#000".

Usage:
    python qa_visibility.py previews/test_components_scene_4.png
    python qa_visibility.py previews/   # check all PNGs in dir
"""

import sys
from pathlib import Path

try:
    from PIL import Image
    import numpy as np
except ImportError:
    print("ERROR: pip install Pillow numpy")
    sys.exit(1)

# TKK background color
BG_RGB = np.array([8, 10, 16], dtype=np.float64)

# Pre-compute background luminance
def _srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

BG_LUMINANCE = (0.2126 * _srgb_to_linear(BG_RGB[0]) +
                0.7152 * _srgb_to_linear(BG_RGB[1]) +
                0.0722 * _srgb_to_linear(BG_RGB[2]))

# Thresholds
CONTENT_DISTANCE = 25       # min RGB distance from bg to be "content"
DIM_CONTRAST = 2.0          # contrast ratio below which content is "dim"
FAIL_CONTRAST = 1.5         # contrast ratio below which it's a hard fail
MIN_DIM_PIXELS = 200        # ignore tiny speckles


def relative_luminance_array(rgb_array):
    """Vectorized WCAG relative luminance for an (N, 3) float array."""
    srgb = rgb_array / 255.0
    linear = np.where(srgb <= 0.03928, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4)
    return 0.2126 * linear[:, 0] + 0.7152 * linear[:, 1] + 0.0722 * linear[:, 2]


def contrast_ratio(lum):
    """WCAG contrast ratio of luminance values against BG_LUMINANCE."""
    lighter = np.maximum(lum, BG_LUMINANCE)
    darker = np.minimum(lum, BG_LUMINANCE)
    return (lighter + 0.05) / (darker + 0.05)


def check_visibility(image_path: str) -> dict:
    """Check a single preview PNG for dim/invisible elements.

    Returns dict with status, detail, content_pixels, dim_pixels, worst_contrast.
    """
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img, dtype=np.float64).reshape(-1, 3)

    # Find content pixels (far enough from background)
    dist = np.sqrt(np.sum((arr - BG_RGB) ** 2, axis=1))
    content_mask = dist > CONTENT_DISTANCE
    content_count = int(np.sum(content_mask))

    if content_count == 0:
        return {
            "status": "PASS",
            "detail": "No content pixels detected",
            "content_pixels": 0,
            "dim_pixels": 0,
            "worst_contrast": None,
        }

    # Compute luminance and contrast for content pixels only
    content_rgb = arr[content_mask]
    lum = relative_luminance_array(content_rgb)
    cr = contrast_ratio(lum)

    dim_mask = cr < DIM_CONTRAST
    dim_count = int(np.sum(dim_mask))
    worst = float(cr[dim_mask].min()) if dim_count > 0 else float(cr.min())

    name = Path(image_path).stem

    if dim_count < MIN_DIM_PIXELS:
        return {
            "status": "PASS",
            "detail": f"{name}: {content_count} content px, {dim_count} dim (below threshold)",
            "content_pixels": content_count,
            "dim_pixels": dim_count,
            "worst_contrast": round(worst, 2),
        }

    if worst < FAIL_CONTRAST:
        status = "FAIL"
    else:
        status = "WARN"

    return {
        "status": status,
        "detail": f"{name}: {dim_count:,} dim content pixels (contrast < {DIM_CONTRAST}:1), worst ratio {worst:.2f}:1",
        "content_pixels": content_count,
        "dim_pixels": dim_count,
        "worst_contrast": round(worst, 2),
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(0)

    target = Path(args[0])
    if target.is_dir():
        files = sorted(target.glob("*.png"))
    else:
        files = [target]

    any_fail = False
    for f in files:
        result = check_visibility(str(f))
        status = result["status"]
        print(f"  [{status}] {result['detail']}")
        if status == "FAIL":
            any_fail = True

    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
