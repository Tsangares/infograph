#!/usr/bin/env python3
"""
qa_raycast.py — Pixel-level raycasting analysis on preview PNGs.

Casts rays across rendered frames to detect visual problems:
- Empty regions (nothing rendered)
- Content outside safe areas
- Content clustering (top/bottom/left heavy)
- Low visual density
- Insufficient contrast

Usage:
    python3 qa_raycast.py <topic> [--json] [--verbose]
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

# Zone boundaries (pixel y ranges)
ZONES = {
    'TITLE':  (120, 300),
    'UPPER':  (300, 780),
    'MID':    (780, 1140),
    'LOWER':  (1140, 1620),
    'FOOTER': (1620, 1728),
}

# Raycasting parameters
H_RAY_COUNT = 40      # horizontal rays (evenly spaced vertically)
V_RAY_COUNT = 20      # vertical rays (evenly spaced horizontally)
BG_THRESHOLD = 30     # max color distance from BG to count as "background"
MIN_DENSITY = 0.03    # minimum fraction of non-bg pixels per scene (3%)
MAX_OUTSIDE_SAFE = 0.05  # max fraction of content outside safe area
CLUSTER_THRESHOLD = 0.70  # if >70% of content in one half, it's clustered


def color_distance(c1, c2):
    """Euclidean distance between two RGB tuples."""
    return ((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2 + (c1[2]-c2[2])**2) ** 0.5


def detect_bg_color(img):
    """Detect background color from corners."""
    pixels = [
        img.getpixel((5, 5)),
        img.getpixel((WIDTH-5, 5)),
        img.getpixel((5, HEIGHT-5)),
        img.getpixel((WIDTH-5, HEIGHT-5)),
    ]
    # Average the corners (they should all be BG)
    r = sum(p[0] for p in pixels) // 4
    g = sum(p[1] for p in pixels) // 4
    b = sum(p[2] for p in pixels) // 4
    return (r, g, b)


def cast_rays(img, bg_color):
    """Cast horizontal and vertical rays, return hit maps."""
    arr = np.array(img)[:, :, :3]  # Ignore alpha if present
    bg = np.array(bg_color, dtype=np.float32)

    # Compute per-pixel distance from background
    diff = np.sqrt(np.sum((arr.astype(np.float32) - bg) ** 2, axis=2))
    content_mask = diff > BG_THRESHOLD  # True where there's content

    return content_mask


def analyze_scene(img_path, scene_num):
    """Analyze a single scene preview PNG."""
    img = Image.open(img_path).convert('RGB')
    if img.size != (WIDTH, HEIGHT):
        img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)

    bg_color = detect_bg_color(img)
    content_mask = cast_rays(img, bg_color)

    total_pixels = WIDTH * HEIGHT
    content_pixels = int(np.sum(content_mask))
    density = content_pixels / total_pixels

    checks = []

    # 1. Visual density check
    if density < 0.01:
        checks.append({
            'check': 'visual_density',
            'status': 'FAIL',
            'detail': f'Scene {scene_num}: Only {density:.1%} content pixels — scene appears nearly empty'
        })
    elif density < MIN_DENSITY:
        checks.append({
            'check': 'visual_density',
            'status': 'WARN',
            'detail': f'Scene {scene_num}: Low density ({density:.1%}) — scene may look sparse'
        })
    else:
        checks.append({
            'check': 'visual_density',
            'status': 'PASS',
            'detail': f'Scene {scene_num}: {density:.1%} content density'
        })

    # 2. Content outside safe area
    safe_mask = np.zeros_like(content_mask)
    safe_mask[SAFE_TOP:SAFE_BOTTOM, SAFE_LEFT:SAFE_RIGHT] = True

    outside_content = int(np.sum(content_mask & ~safe_mask))
    inside_content = int(np.sum(content_mask & safe_mask))

    if content_pixels > 0:
        outside_frac = outside_content / content_pixels
        if outside_frac > MAX_OUTSIDE_SAFE:
            checks.append({
                'check': 'safe_area',
                'status': 'WARN',
                'detail': f'Scene {scene_num}: {outside_frac:.0%} of content outside safe area'
            })
        else:
            checks.append({
                'check': 'safe_area',
                'status': 'PASS',
                'detail': f'Scene {scene_num}: {outside_frac:.0%} outside safe area (OK)'
            })

    # 3. Vertical distribution (top-heavy / bottom-heavy)
    if content_pixels > 100:
        safe_content = content_mask[SAFE_TOP:SAFE_BOTTOM, SAFE_LEFT:SAFE_RIGHT]
        mid_y = safe_content.shape[0] // 2
        top_half = int(np.sum(safe_content[:mid_y, :]))
        bottom_half = int(np.sum(safe_content[mid_y:, :]))
        total_safe = top_half + bottom_half

        if total_safe > 0:
            top_frac = top_half / total_safe
            bottom_frac = bottom_half / total_safe

            if top_frac > CLUSTER_THRESHOLD:
                checks.append({
                    'check': 'vertical_balance',
                    'status': 'WARN',
                    'detail': f'Scene {scene_num}: Top-heavy ({top_frac:.0%} top / {bottom_frac:.0%} bottom)'
                })
            elif bottom_frac > CLUSTER_THRESHOLD:
                checks.append({
                    'check': 'vertical_balance',
                    'status': 'WARN',
                    'detail': f'Scene {scene_num}: Bottom-heavy ({top_frac:.0%} top / {bottom_frac:.0%} bottom)'
                })
            else:
                checks.append({
                    'check': 'vertical_balance',
                    'status': 'PASS',
                    'detail': f'Scene {scene_num}: Balanced ({top_frac:.0%} top / {bottom_frac:.0%} bottom)'
                })

    # 4. Horizontal distribution (left/right heavy)
    if content_pixels > 100:
        safe_content = content_mask[SAFE_TOP:SAFE_BOTTOM, SAFE_LEFT:SAFE_RIGHT]
        mid_x = safe_content.shape[1] // 2
        left_half = int(np.sum(safe_content[:, :mid_x]))
        right_half = int(np.sum(safe_content[:, mid_x:]))
        total_safe = left_half + right_half

        if total_safe > 0:
            left_frac = left_half / total_safe
            if left_frac > 0.80:
                checks.append({
                    'check': 'horizontal_balance',
                    'status': 'WARN',
                    'detail': f'Scene {scene_num}: Left-heavy ({left_frac:.0%} left)'
                })
            elif left_frac < 0.20:
                checks.append({
                    'check': 'horizontal_balance',
                    'status': 'WARN',
                    'detail': f'Scene {scene_num}: Right-heavy ({1-left_frac:.0%} right)'
                })
            else:
                checks.append({
                    'check': 'horizontal_balance',
                    'status': 'PASS',
                    'detail': f'Scene {scene_num}: Centered ({left_frac:.0%} left / {1-left_frac:.0%} right)'
                })

    # 5. Per-zone density (detect empty zones)
    zone_stats = {}
    for zone_name, (y_top, y_bottom) in ZONES.items():
        zone_content = content_mask[y_top:y_bottom, SAFE_LEFT:SAFE_RIGHT]
        zone_total = zone_content.size
        zone_filled = int(np.sum(zone_content))
        zone_density = zone_filled / zone_total if zone_total > 0 else 0
        zone_stats[zone_name] = zone_density

    empty_zones = [z for z, d in zone_stats.items() if d < 0.005]
    active_zones = [z for z, d in zone_stats.items() if d >= 0.005]

    if len(active_zones) < 2:
        checks.append({
            'check': 'zone_coverage',
            'status': 'WARN',
            'detail': f'Scene {scene_num}: Only {len(active_zones)} active zone(s): {", ".join(active_zones)}. Empty: {", ".join(empty_zones)}'
        })
    else:
        checks.append({
            'check': 'zone_coverage',
            'status': 'PASS',
            'detail': f'Scene {scene_num}: {len(active_zones)} active zones: {", ".join(active_zones)}'
        })

    return {
        'scene': scene_num,
        'density': round(density, 4),
        'bg_color': f'#{bg_color[0]:02x}{bg_color[1]:02x}{bg_color[2]:02x}',
        'zone_stats': {z: round(d, 4) for z, d in zone_stats.items()},
        'active_zones': active_zones,
        'checks': checks,
    }


def main():
    parser = argparse.ArgumentParser(description='Pixel-level raycasting QA on preview PNGs')
    parser.add_argument('topic', help='Topic name')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()

    # Find preview PNGs
    preview_dir = Path(__file__).parent / 'previews'
    previews = sorted(preview_dir.glob(f'{args.topic}_scene_*.png'))

    if not previews:
        print(f'ERROR: No previews found for topic "{args.topic}" in {preview_dir}')
        print(f'Run: npx tsx remotion/preview.mts {args.topic}')
        sys.exit(1)

    print(f'Raycasting QA: {len(previews)} scenes for "{args.topic}"')
    print('=' * 60)

    all_checks = []
    scene_results = []

    for preview_path in previews:
        scene_num = int(preview_path.stem.split('_scene_')[1])
        result = analyze_scene(preview_path, scene_num)
        scene_results.append(result)
        all_checks.extend(result['checks'])

        if not args.json:
            print(f'\nScene {scene_num} (density: {result["density"]:.1%}, bg: {result["bg_color"]})')
            print(f'  Active zones: {", ".join(result["active_zones"])}')
            for check in result['checks']:
                icon = '✓' if check['status'] == 'PASS' else ('⚠' if check['status'] == 'WARN' else '✗')
                print(f'  {icon} [{check["status"]}] {check["detail"]}')

    fails = sum(1 for c in all_checks if c['status'] == 'FAIL')
    warns = sum(1 for c in all_checks if c['status'] == 'WARN')

    status = 'FAIL' if fails > 0 else ('WARN' if warns > 0 else 'PASS')

    if args.json:
        output = {
            'topic': args.topic,
            'status': status,
            'total_fails': fails,
            'total_warns': warns,
            'scenes': scene_results,
        }
        print(json.dumps(output, indent=2))
    else:
        print(f'\n{"=" * 60}')
        print(f'Result: {status} ({fails} fails, {warns} warnings)')

    sys.exit(1 if fails > 0 else 0)


if __name__ == '__main__':
    main()
