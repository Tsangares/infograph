#!/usr/bin/env python3
"""
visual_raycast.py — Renders visual debug overlays on preview PNGs.

Draws zone boundaries, safe area, raycasting rays (colored by hit/miss),
content bounding box, and stats. Output: annotated debug PNGs.

Usage:
    python3 visual_raycast.py <topic>
    python3 visual_raycast.py antibiotics
    python3 visual_raycast.py --all          # process all topics in previews/
"""

import sys
import math
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
FRAME_W, FRAME_H = 1080, 1920
BG_THRESHOLD = 30  # color distance to count as background

# Zone definitions: (name, y_start, y_end, color_rgba)
ZONES = [
    ("TITLE",  120,  300,  (255,  80,  80, 200)),   # red
    ("UPPER",  300,  780,  (  0, 220, 220, 200)),   # cyan
    ("MID",    780, 1140,  (240, 220,  40, 200)),   # yellow
    ("LOWER", 1140, 1620,  ( 60, 220,  60, 200)),   # green
    ("FOOTER",1620, 1728,  (240, 100, 200, 200)),   # pink
]

# Safe area
SAFE_TOP, SAFE_BOT = 200, 1520
SAFE_LEFT, SAFE_RIGHT = 120, 940

# Ray counts
H_RAYS = 20
V_RAYS = 10

# Ray line thickness
RAY_THICKNESS = 2

# Overlay alpha for rays
RAY_ALPHA = 160

# Stats overlay
STATS_BG = (0, 0, 0, 180)
STATS_FG = (255, 255, 255, 255)

PREVIEWS_DIR = Path(__file__).parent / "previews"


# ---------------------------------------------------------------------------
# Pixel analysis helpers
# ---------------------------------------------------------------------------

def detect_background_color(pixels: np.ndarray) -> np.ndarray:
    """Detect the dominant background color by sampling corners."""
    h, w = pixels.shape[:2]
    # Sample 50px squares from each corner
    s = 50
    corners = np.concatenate([
        pixels[:s, :s].reshape(-1, 3),
        pixels[:s, w-s:].reshape(-1, 3),
        pixels[h-s:, :s].reshape(-1, 3),
        pixels[h-s:, w-s:].reshape(-1, 3),
    ], axis=0)
    return np.median(corners, axis=0).astype(np.float64)


def color_distance(pixel: np.ndarray, bg: np.ndarray) -> float:
    """Euclidean distance in RGB space."""
    return float(np.sqrt(np.sum((pixel.astype(np.float64) - bg) ** 2)))


def is_content(pixel: np.ndarray, bg: np.ndarray, threshold: float = BG_THRESHOLD) -> bool:
    return color_distance(pixel, bg) > threshold


def find_content_bbox(pixels: np.ndarray, bg: np.ndarray) -> tuple[int, int, int, int]:
    """Find bounding box of all content pixels. Returns (x1, y1, x2, y2)."""
    diff = np.sqrt(np.sum((pixels.astype(np.float64) - bg[None, None, :]) ** 2, axis=2))
    mask = diff > BG_THRESHOLD
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    if not np.any(rows) or not np.any(cols):
        return (0, 0, 0, 0)
    y1, y2 = int(np.argmax(rows)), int(len(rows) - np.argmax(rows[::-1]) - 1)
    x1, x2 = int(np.argmax(cols)), int(len(cols) - np.argmax(cols[::-1]) - 1)
    return (x1, y1, x2, y2)


def compute_content_density(pixels: np.ndarray, bg: np.ndarray) -> float:
    """Fraction of pixels that are content (not background)."""
    diff = np.sqrt(np.sum((pixels.astype(np.float64) - bg[None, None, :]) ** 2, axis=2))
    return float(np.mean(diff > BG_THRESHOLD))


def compute_active_zones(pixels: np.ndarray, bg: np.ndarray) -> list[str]:
    """Return list of zone names that contain content."""
    active = []
    diff = np.sqrt(np.sum((pixels.astype(np.float64) - bg[None, None, :]) ** 2, axis=2))
    mask = diff > BG_THRESHOLD
    h = pixels.shape[0]
    for name, y1, y2, _ in ZONES:
        y1c = min(y1, h)
        y2c = min(y2, h)
        if y2c > y1c and np.any(mask[y1c:y2c]):
            active.append(name)
    return active


def compute_balance(pixels: np.ndarray, bg: np.ndarray) -> tuple[float, float]:
    """Return (top_pct, bottom_pct) — content density in top half vs bottom half."""
    h = pixels.shape[0]
    mid = h // 2
    diff = np.sqrt(np.sum((pixels.astype(np.float64) - bg[None, None, :]) ** 2, axis=2))
    mask = diff > BG_THRESHOLD
    top_density = float(np.mean(mask[:mid])) if mid > 0 else 0.0
    bot_density = float(np.mean(mask[mid:])) if mid < h else 0.0
    total = top_density + bot_density
    if total == 0:
        return (50.0, 50.0)
    return (top_density / total * 100, bot_density / total * 100)


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def try_load_font(size: int):
    """Try to load a monospace font, fall back to default."""
    candidates = [
        "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/dejavu-sans-mono-fonts/DejaVuSansMono.ttf",
        "/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_zone_boundaries(overlay: Image.Image):
    """Draw horizontal zone boundary lines with labels."""
    draw = ImageDraw.Draw(overlay)
    font = try_load_font(22)

    for name, y_start, y_end, color in ZONES:
        # Top edge of zone
        draw.line([(0, y_start), (FRAME_W, y_start)], fill=color, width=2)
        # Bottom edge of zone
        draw.line([(0, y_end), (FRAME_W, y_end)], fill=color, width=2)
        # Label at left edge, slightly inside zone
        label_y = y_start + 4
        # Background box for label
        bbox = draw.textbbox((8, label_y), name, font=font)
        draw.rectangle([bbox[0]-2, bbox[1]-1, bbox[2]+4, bbox[3]+1], fill=(0, 0, 0, 160))
        draw.text((8, label_y), name, fill=color, font=font)
        # y-coordinate labels
        top_label = str(y_start)
        bot_label = str(y_end)
        draw.text((FRAME_W - 70, y_start + 4), top_label, fill=color, font=try_load_font(16))
        draw.text((FRAME_W - 70, y_end - 22), bot_label, fill=color, font=try_load_font(16))


def draw_safe_area(overlay: Image.Image):
    """Draw dashed rectangle for safe area."""
    draw = ImageDraw.Draw(overlay)
    color = (255, 255, 255, 120)
    dash_len = 12
    gap_len = 8

    def dashed_line(x1, y1, x2, y2):
        length = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        if length == 0:
            return
        dx = (x2 - x1) / length
        dy = (y2 - y1) / length
        pos = 0.0
        drawing = True
        while pos < length:
            seg = dash_len if drawing else gap_len
            end = min(pos + seg, length)
            if drawing:
                sx, sy = x1 + dx * pos, y1 + dy * pos
                ex, ey = x1 + dx * end, y1 + dy * end
                draw.line([(sx, sy), (ex, ey)], fill=color, width=1)
            pos = end
            drawing = not drawing

    # Four edges of safe area
    dashed_line(SAFE_LEFT, SAFE_TOP, SAFE_RIGHT, SAFE_TOP)
    dashed_line(SAFE_RIGHT, SAFE_TOP, SAFE_RIGHT, SAFE_BOT)
    dashed_line(SAFE_RIGHT, SAFE_BOT, SAFE_LEFT, SAFE_BOT)
    dashed_line(SAFE_LEFT, SAFE_BOT, SAFE_LEFT, SAFE_TOP)

    # Label
    font = try_load_font(14)
    draw.text((SAFE_LEFT + 4, SAFE_TOP - 18), "SAFE AREA", fill=color, font=font)


def draw_horizontal_rays(overlay: Image.Image, pixels: np.ndarray, bg: np.ndarray):
    """Cast horizontal rays and color them green (content) or red (background)."""
    h, w = pixels.shape[:2]
    overlay_pixels = np.array(overlay)

    spacing = h // (H_RAYS + 1)
    for i in range(1, H_RAYS + 1):
        y = i * spacing
        if y >= h:
            continue
        for t in range(RAY_THICKNESS):
            yy = y + t
            if yy >= h:
                continue
            for x in range(w):
                hit = is_content(pixels[y, x], bg)
                if hit:
                    ray_color = (0, 255, 80, RAY_ALPHA)
                else:
                    ray_color = (255, 40, 40, RAY_ALPHA)
                # Alpha composite manually
                src = np.array(ray_color[:3], dtype=np.float64)
                src_a = ray_color[3] / 255.0
                dst = overlay_pixels[yy, x, :3].astype(np.float64)
                dst_a = overlay_pixels[yy, x, 3] / 255.0
                out_a = src_a + dst_a * (1 - src_a)
                if out_a > 0:
                    out_rgb = (src * src_a + dst * dst_a * (1 - src_a)) / out_a
                    overlay_pixels[yy, x, :3] = out_rgb.astype(np.uint8)
                    overlay_pixels[yy, x, 3] = int(out_a * 255)

    return Image.fromarray(overlay_pixels, "RGBA")


def draw_horizontal_rays_fast(overlay: Image.Image, pixels: np.ndarray, bg: np.ndarray):
    """Vectorized horizontal ray drawing."""
    h, w = pixels.shape[:2]
    overlay_arr = np.array(overlay)

    diff = np.sqrt(np.sum((pixels.astype(np.float64) - bg[None, None, :]) ** 2, axis=2))
    content_mask = diff > BG_THRESHOLD  # (h, w) bool

    spacing = h // (H_RAYS + 1)
    for i in range(1, H_RAYS + 1):
        y = i * spacing
        if y >= h:
            continue
        row_mask = content_mask[y]  # (w,) bool
        for t in range(RAY_THICKNESS):
            yy = y + t
            if yy >= h:
                continue
            # Green where content, red where background
            # Set overlay pixels directly
            green = np.array([0, 255, 80], dtype=np.uint8)
            red = np.array([255, 40, 40], dtype=np.uint8)
            overlay_arr[yy, row_mask, :3] = green
            overlay_arr[yy, ~row_mask, :3] = red
            overlay_arr[yy, :, 3] = RAY_ALPHA

    return Image.fromarray(overlay_arr, "RGBA")


def draw_vertical_rays_fast(overlay: Image.Image, pixels: np.ndarray, bg: np.ndarray):
    """Vectorized vertical ray drawing."""
    h, w = pixels.shape[:2]
    overlay_arr = np.array(overlay)

    diff = np.sqrt(np.sum((pixels.astype(np.float64) - bg[None, None, :]) ** 2, axis=2))
    content_mask = diff > BG_THRESHOLD

    spacing = w // (V_RAYS + 1)
    for i in range(1, V_RAYS + 1):
        x = i * spacing
        if x >= w:
            continue
        col_mask = content_mask[:, x]  # (h,) bool
        for t in range(RAY_THICKNESS):
            xx = x + t
            if xx >= w:
                continue
            green = np.array([0, 255, 80], dtype=np.uint8)
            red = np.array([255, 40, 40], dtype=np.uint8)
            overlay_arr[col_mask, xx, :3] = green
            overlay_arr[~col_mask, xx, :3] = red
            overlay_arr[:, xx, 3] = RAY_ALPHA

    return Image.fromarray(overlay_arr, "RGBA")


def draw_content_bbox(overlay: Image.Image, bbox: tuple[int, int, int, int]):
    """Draw bright white bounding box around content region."""
    x1, y1, x2, y2 = bbox
    if x1 == x2 == 0:
        return
    draw = ImageDraw.Draw(overlay)
    draw.rectangle([x1, y1, x2, y2], outline=(255, 255, 255, 230), width=3)
    # Corner markers (small squares at each corner for visibility)
    marker = 8
    for cx, cy in [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]:
        draw.rectangle([cx-marker, cy-marker, cx+marker, cy+marker],
                       fill=(255, 255, 255, 200))


def draw_stats_overlay(overlay: Image.Image, density: float, active_zones: list[str],
                       balance: tuple[float, float]):
    """Draw stats text box in the top-right corner."""
    draw = ImageDraw.Draw(overlay)
    font = try_load_font(20)
    font_sm = try_load_font(16)

    lines = [
        f"Density: {density*100:.1f}%",
        f"Zones:   {', '.join(active_zones) if active_zones else 'NONE'}",
        f"Balance: T {balance[0]:.0f}% / B {balance[1]:.0f}%",
    ]

    # Compute box size
    padding = 12
    line_h = 26
    box_w = 380
    box_h = padding * 2 + line_h * len(lines) + 8
    box_x = FRAME_W - box_w - 16
    box_y = 16

    # Background
    draw.rectangle([box_x, box_y, box_x + box_w, box_y + box_h], fill=STATS_BG)

    # Title
    draw.text((box_x + padding, box_y + padding - 4), "RAYCAST DEBUG", fill=(120, 200, 255, 255), font=font)

    # Stats lines
    for i, line in enumerate(lines):
        draw.text((box_x + padding, box_y + padding + 24 + i * line_h), line,
                  fill=STATS_FG, font=font_sm)


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------

def process_image(input_path: Path, output_path: Path):
    """Process a single preview PNG and write the debug overlay version."""
    # Load original image
    img = Image.open(input_path).convert("RGB")
    w, h = img.size
    pixels = np.array(img)

    # Detect background
    bg = detect_background_color(pixels)

    # Compute stats
    density = compute_content_density(pixels, bg)
    active_zones = compute_active_zones(pixels, bg)
    balance = compute_balance(pixels, bg)
    bbox = find_content_bbox(pixels, bg)

    # Create base as RGBA (original image)
    base = img.convert("RGBA")

    # --- Layer 1: Zone boundaries + safe area ---
    zone_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_zone_boundaries(zone_overlay)
    draw_safe_area(zone_overlay)

    # --- Layer 2: Horizontal rays ---
    h_ray_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    h_ray_overlay = draw_horizontal_rays_fast(h_ray_overlay, pixels, bg)

    # --- Layer 3: Vertical rays ---
    v_ray_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    v_ray_overlay = draw_vertical_rays_fast(v_ray_overlay, pixels, bg)

    # --- Layer 4: Content bounding box ---
    bbox_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_content_bbox(bbox_overlay, bbox)

    # --- Layer 5: Stats ---
    stats_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_stats_overlay(stats_overlay, density, active_zones, balance)

    # Composite all layers
    result = base.copy()
    result = Image.alpha_composite(result, h_ray_overlay)
    result = Image.alpha_composite(result, v_ray_overlay)
    result = Image.alpha_composite(result, zone_overlay)
    result = Image.alpha_composite(result, bbox_overlay)
    result = Image.alpha_composite(result, stats_overlay)

    # Save as RGB PNG
    result.convert("RGB").save(output_path, "PNG")
    print(f"  -> {output_path.name}")


def process_topic(topic: str):
    """Find all scene PNGs for a topic and generate debug overlays."""
    pattern = f"{topic}_scene_*.png"
    matches = sorted(PREVIEWS_DIR.glob(pattern))

    if not matches:
        print(f"No previews found for topic '{topic}' in {PREVIEWS_DIR}")
        print(f"  Searched for: {pattern}")
        sys.exit(1)

    print(f"Processing {len(matches)} scenes for '{topic}'...")
    for scene_path in matches:
        # Extract scene number from filename
        stem = scene_path.stem  # e.g. "antibiotics_scene_3"
        debug_name = stem.replace("_scene_", "_debug_scene_") + ".png"
        output_path = PREVIEWS_DIR / debug_name
        print(f"  {scene_path.name}")
        process_image(scene_path, output_path)

    print(f"Done. {len(matches)} debug images written to {PREVIEWS_DIR}/")


def process_all():
    """Process every topic found in previews/."""
    all_files = sorted(PREVIEWS_DIR.glob("*_scene_*.png"))
    # Exclude existing debug files
    all_files = [f for f in all_files if "_debug_scene_" not in f.name]

    # Extract unique topics
    topics = set()
    for f in all_files:
        # topic is everything before _scene_
        parts = f.stem.rsplit("_scene_", 1)
        if len(parts) == 2:
            topics.add(parts[0])

    if not topics:
        print(f"No preview scenes found in {PREVIEWS_DIR}")
        sys.exit(1)

    print(f"Found {len(topics)} topics: {', '.join(sorted(topics))}")
    for topic in sorted(topics):
        process_topic(topic)


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        sys.exit(1)

    topic = sys.argv[1]

    if topic == "--all":
        process_all()
    else:
        process_topic(topic)


if __name__ == "__main__":
    main()
