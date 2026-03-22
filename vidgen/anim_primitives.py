"""TKK Animation Primitives Library.

Reusable, tested building blocks for manim scenes.
Each primitive is a function that returns animated mobjects
ready to be used in any scene.

Usage:
    from anim_primitives import counter, bar_chart, timeline, split_compare, map_with_markers

Categories:
    - Numbers: counter, stat_reveal, percentage_bar
    - Charts: bar_chart, horizontal_bars, stacked_compare
    - Layout: split_compare, panel_grid, letterbox_closer
    - Timeline: timeline, date_marker, era_span
    - Maps: map_with_markers (uses geo_utils)
    - Text: headline, caption, quote_block, stamp
    - SVG: load_svg, svg_grid, svg_with_label
"""

import numpy as np
from manim import *


# ============================================================
# COLOR PALETTE (consistent across all videos)
# ============================================================
TKK_BG = "#0a0a12"
TKK_BG_WARM = "#1a1410"
TKK_GOLD = "#FFD700"
TKK_RED = "#FF4444"
TKK_GREEN = "#39FF14"
TKK_WHITE = "#EAEAF0"
TKK_DIM = "#8A8A9A"
TKK_MUTED = "#55556A"
TKK_ACCENT = "#FF2D55"

SAFE_FONTS = {
    "heading": "Bebas Neue",
    "body": "Inter",
    "serif": "DM Serif Display",
    "mono": "Space Mono",
}

# Safe zone constants (TikTok UI clearance)
# Frame: 9 wide x 16 tall, origin at center
SAFE_W = 8.0       # horizontal safe width (60px margin each side)
SAFE_TOP = 7.2     # top 5% clearance (status bar, clock) — y must be <= this
SAFE_BOT = -6.4    # bottom 10% clearance (description, buttons) — y must be >= this

# Vertical layout zones — USE THESE for all positioning
# Every scene MUST have content in at least 3 zones to fill the frame.
ZONE_TITLE  = 6.2    # y 5.5–7.0  — scene label pills
ZONE_UPPER  = 3.5    # y 1.5–5.5  — hero visual top portion
ZONE_MID    = 0.0    # y -1.5–1.5 — central focal point, big numbers
ZONE_LOWER  = -3.5   # y -5.5–-1.5 — supporting visuals, bars, icons
ZONE_FOOTER = -6.0   # y -6.4–-5.5 — captions, source labels

_ZONE_MAP = {
    "TITLE": ZONE_TITLE, "UPPER": ZONE_UPPER, "MID": ZONE_MID,
    "LOWER": ZONE_LOWER, "FOOTER": ZONE_FOOTER,
}

# Data viz defaults — chart area centered low to fill the frame
GRID_COLOR = "#1A2030"
SURFACE_COLOR = "#15192A"
CHART_X_LEN = 7.0
CHART_Y_LEN = 7.0
CHART_CENTER = [0, -0.5, 0]


# ============================================================
# SCENE BACKGROUND HELPERS
# ============================================================

def gradient_bg(bg_color=TKK_BG, glow_color="#121828"):
    """Dark background with subtle center glow — standard for every scene."""
    bg = Rectangle(width=12, height=20, fill_color=bg_color, fill_opacity=1, stroke_width=0)
    glow = Circle(radius=5, fill_color=glow_color, fill_opacity=0.08,
                  stroke_width=0).move_to(UP * 2)
    return VGroup(bg, glow)


def grid_lines(color=GRID_COLOR, opacity=0.04):
    """Subtle grid overlay — standard for every scene."""
    lines = VGroup()
    for i in range(13):
        y = -8 + i * 16 / 12
        lines.add(Line(LEFT * 5, RIGHT * 5, color=color,
                       stroke_width=0.5).move_to(UP * y).set_opacity(opacity))
    for j in range(7):
        x = -4.5 + j * 9 / 6
        lines.add(Line(DOWN * 8, UP * 8, color=color,
                       stroke_width=0.5).move_to(RIGHT * x).set_opacity(opacity))
    return lines


def label_pill(text, color=TKK_GOLD, bg_color=SURFACE_COLOR, font_size=28):
    """Scene label badge — pill-shaped background behind bold text."""
    t = Text(text, font="Inter", font_size=font_size, color=color, weight="BOLD")
    if t.width > SAFE_W:
        t.scale(SAFE_W / t.width)
    p = RoundedRectangle(
        width=t.width + 0.5, height=t.height + 0.3,
        corner_radius=0.15, fill_color=bg_color, fill_opacity=0.9, stroke_width=0
    ).move_to(t)
    return VGroup(p, t)


# ============================================================
# TEXT HELPERS
# ============================================================

def safe_text(content, max_width=None, **kwargs):
    """Create Text with fallback font handling and optional SAFE_W auto-scale.

    If max_width is None (default), auto-scales to SAFE_W.
    Pass max_width=0 to disable auto-scaling.
    """
    font = kwargs.pop("font", "Inter")
    try:
        t = Text(content, font=font, **kwargs)
    except Exception:
        t = Text(content, **kwargs)
    limit = SAFE_W if max_width is None else max_width
    if limit and t.width > limit:
        t.scale(limit / t.width)
    return t


def headline(text, color=TKK_GOLD, size=80):
    """Large impact headline — for hooks and key reveals."""
    return safe_text(text, font="Bebas Neue", font_size=size, color=color,
                     weight="BOLD")


def caption(text, color=TKK_DIM, size=36):
    """Subdued explanatory text."""
    return safe_text(text, font="DM Serif Display", font_size=size, color=color)


def stamp(text, color=TKK_RED, size=48, angle=-0.12):
    """Rubber stamp effect — rotated, bordered text."""
    t = safe_text(text, font="Inter", font_size=size, color=color, weight="BOLD")
    border = SurroundingRectangle(t, color=color, buff=0.15, stroke_width=3)
    group = VGroup(t, border).rotate(angle)
    return group


def quote_block(text, color=TKK_WHITE, size=44):
    """Quoted text with decorative marks."""
    q = safe_text(f'"{text}"', font="DM Serif Display", font_size=size, color=color)
    return q


def scene_label(text, color=TKK_ACCENT):
    """Small scene label badge at top of frame."""
    t = safe_text(text, font="Inter", font_size=22, color=color, weight="BOLD")
    border = SurroundingRectangle(t, color=color, buff=0.12,
                                  stroke_width=1.5, corner_radius=0.08)
    return VGroup(t, border).to_edge(UP, buff=0.4)


def divider(color=TKK_DIM, width=5):
    """Horizontal divider line with diamond center."""
    line = Line(LEFT * width/2, RIGHT * width/2, color=color, stroke_width=1)
    diamond = Square(side_length=0.12, color=color, fill_opacity=1).rotate(PI/4)
    return VGroup(line, diamond)


# ============================================================
# LAYOUT ZONE HELPERS
# ============================================================

def safe_place(mob, zone="MID", x=0):
    """Position a mobject at a named vertical zone, enforcing safe bounds.

    zone: "TITLE", "UPPER", "MID", "LOWER", "FOOTER" (or a float y-value)
    x: horizontal offset (default 0 = center)

    Enforces both horizontal (SAFE_W) and vertical (SAFE_TOP/SAFE_BOT) bounds.
    Auto-scales the mobject if it would overflow.
    """
    if isinstance(zone, str):
        y = _ZONE_MAP[zone]
    else:
        y = float(zone)

    mob.move_to(np.array([float(x), y, 0]))

    # Enforce horizontal bounds
    if mob.width > SAFE_W:
        mob.scale(SAFE_W / mob.width)

    # Enforce vertical bounds — shift first, scale if still overflowing
    top = mob.get_top()[1]
    bot = mob.get_bottom()[1]
    if top > SAFE_TOP:
        mob.shift(DOWN * (top - SAFE_TOP))
    if bot < SAFE_BOT:
        mob.shift(UP * (SAFE_BOT - bot))
    # If both bounds violated (mob too tall), scale to fit
    if mob.get_top()[1] > SAFE_TOP or mob.get_bottom()[1] < SAFE_BOT:
        available = SAFE_TOP - SAFE_BOT
        mob.scale(available / mob.height * 0.95)
        mob.move_to(np.array([float(x), (SAFE_TOP + SAFE_BOT) / 2, 0]))

    return mob


def layout_stack(mobs, top=None, bottom=None):
    """Distribute mobjects evenly across the full vertical safe zone.

    Returns VGroup with mobjects positioned from top to bottom.
    """
    if top is None:
        top = SAFE_TOP - 0.8
    if bottom is None:
        bottom = SAFE_BOT + 0.8
    n = len(mobs)
    if n == 0:
        return VGroup()
    if n == 1:
        mobs[0].move_to(UP * ((top + bottom) / 2))
        return VGroup(*mobs)
    spacing = (top - bottom) / (n - 1)
    for i, mob in enumerate(mobs):
        mob.move_to(UP * (top - i * spacing))
    return VGroup(*mobs)


def validate_layout(scene):
    """Call at end of construct() to warn about layout issues.

    Checks: out-of-bounds mobjects, content only in top half.
    """
    issues = []
    content_ys = []
    for mob in scene.mobjects[2:]:  # skip bg + grid
        try:
            top_y = mob.get_top()[1]
            bot_y = mob.get_bottom()[1]
            center_y = mob.get_center()[1]
        except Exception:
            continue
        if mob.width < 0.01 and mob.height < 0.01:
            continue  # skip invisible/tiny mobs
        content_ys.append(center_y)
        if top_y > SAFE_TOP + 0.5:
            issues.append(f"  ABOVE safe zone: y={top_y:.1f} (max {SAFE_TOP})")
        if bot_y < SAFE_BOT - 0.5:
            issues.append(f"  BELOW safe zone: y={bot_y:.1f} (min {SAFE_BOT})")

    if content_ys:
        avg_y = sum(content_ys) / len(content_ys)
        min_y = min(content_ys)
        if min_y > -1.5:
            issues.append(f"  EMPTY BOTTOM: lowest content at y={min_y:.1f} — push something to ZONE_LOWER (-3.5)")
        if avg_y > 2.0:
            issues.append(f"  TOP-HEAVY: content centroid at y={avg_y:.1f} — redistribute vertically")

    if issues:
        print(f"LAYOUT WARNINGS ({len(issues)}):")
        for issue in issues:
            print(issue)
    return len(issues) == 0


# ============================================================
# NUMBERS
# ============================================================

def counter(start, end, duration=1.5, color=TKK_GOLD, size=100, prefix="", suffix="",
            comma_sep=True):
    """Animated counting number. Returns (DecimalNumber, animation).

    Usage:
        num, anim = counter(0, 12000, prefix="", suffix=" people")
        self.play(anim)
    """
    def format_func(n):
        val = int(n)
        if comma_sep:
            formatted = f"{val:,}"
        else:
            formatted = str(val)
        return f"{prefix}{formatted}{suffix}"

    num = Integer(start, color=color, font_size=size)
    # We'll use ChangeDecimalToValue
    anim = ChangeDecimalToValue(num, end, run_time=duration)
    return num, anim


def stat_reveal(number_text, label_text, number_color=TKK_GOLD, label_color=TKK_DIM,
                number_size=90, label_size=36):
    """Big number with small label underneath. Returns VGroup."""
    num = safe_text(number_text, font="Bebas Neue", font_size=number_size,
                    color=number_color)
    label = safe_text(label_text, font="Inter", font_size=label_size,
                      color=label_color)
    label.next_to(num, DOWN, buff=0.25)
    return VGroup(num, label)


def percentage_bar(value, max_val=100, width=6, height=0.5,
                   fill_color=TKK_GOLD, bg_color=TKK_MUTED, label=None):
    """Horizontal progress bar with optional label. Returns (VGroup, fill_anim).

    Usage:
        bar, anim = percentage_bar(73, label="73%")
        self.play(anim)
    """
    bg = Rectangle(width=width, height=height,
                   fill_color=bg_color, fill_opacity=0.3,
                   stroke_color=bg_color, stroke_width=1,
                   stroke_opacity=0.3)
    target_width = max(0.05, width * (value / max_val))
    fill = Rectangle(width=target_width, height=height * 0.85,
                     fill_color=fill_color, fill_opacity=0.85,
                     stroke_width=0)
    fill.align_to(bg, LEFT)

    group = VGroup(bg, fill)

    if label:
        lbl = safe_text(str(label), font="Inter", font_size=24, color=fill_color)
        lbl.next_to(bg, RIGHT, buff=0.2)
        group.add(lbl)

    # Animation: fill grows from zero width
    fill_start = fill.copy().stretch_to_fit_width(0.01).align_to(bg, LEFT)
    anim = Transform(fill_start, fill)
    return group, anim


# ============================================================
# CHARTS
# ============================================================

def bar_chart_simple(data, labels=None, colors=None, width=6, max_height=5,
                     bar_width=0.8, spacing=0.3):
    """Simple vertical bar chart. Returns (VGroup, list of grow animations).

    data: list of values
    labels: list of strings (optional)
    colors: list of colors (optional, defaults to gold)
    """
    if colors is None:
        colors = [TKK_GOLD] * len(data)
    if labels is None:
        labels = [""] * len(data)

    max_val = max(data) if data else 1
    bars = VGroup()
    anims = []
    total_width = len(data) * (bar_width + spacing) - spacing

    for i, (val, label, color) in enumerate(zip(data, labels, colors)):
        bar_height = (val / max_val) * max_height
        bar = Rectangle(width=bar_width, height=bar_height,
                        fill_color=color, fill_opacity=0.8,
                        stroke_color=color, stroke_width=1)
        bar.move_to(RIGHT * (i * (bar_width + spacing) - total_width / 2))
        bar.align_to(ORIGIN, DOWN)

        # Start from zero height
        bar_copy = bar.copy()
        bar.stretch_to_fit_height(0.01).align_to(ORIGIN, DOWN)

        if label:
            lbl = safe_text(label, font="Inter", font_size=20, color=TKK_DIM)
            lbl.next_to(bar_copy, DOWN, buff=0.15)
            bars.add(lbl)

        # Value on top
        val_text = safe_text(str(val), font="Inter", font_size=22, color=color)
        val_text.next_to(bar_copy, UP, buff=0.1)

        bars.add(bar, val_text)
        anims.append(bar.animate.become(bar_copy))

    return bars, anims


def horizontal_bars(data_dict, width=6, bar_height=0.5, spacing=0.15,
                    color=TKK_GOLD, label_color=TKK_WHITE):
    """Horizontal bar chart from dict. Returns (VGroup, list of animations).

    data_dict: {"Label": value, ...}
    """
    max_val = max(data_dict.values()) if data_dict else 1
    group = VGroup()
    anims = []

    for i, (label, val) in enumerate(data_dict.items()):
        y_pos = -i * (bar_height + spacing + 0.3)
        target_w = (val / max_val) * width

        lbl = safe_text(label, font="Inter", font_size=22, color=label_color)
        lbl.move_to(LEFT * 0.5 + UP * y_pos).align_to(LEFT * (width / 2), LEFT)

        bar = Rectangle(width=0.01, height=bar_height,
                        fill_color=color, fill_opacity=0.7,
                        stroke_width=0)
        bar.next_to(lbl, DOWN, buff=0.08).align_to(lbl, LEFT)

        val_text = safe_text(str(val), font="Inter", font_size=20, color=color)
        val_text.next_to(bar, RIGHT, buff=0.15)

        group.add(lbl, bar, val_text)
        anims.append(bar.animate.stretch_to_fit_width(target_w).align_to(lbl, LEFT))

    return group, anims


# ============================================================
# TIMELINE
# ============================================================

def timeline(start_year, end_year, markers=None, width=7, color=TKK_DIM):
    """Horizontal timeline with date markers. Returns VGroup.

    markers: [{"year": 1863, "label": "The Raid", "color": RED}, ...]
    """
    line = Line(LEFT * width/2, RIGHT * width/2, color=color, stroke_width=2)
    year_range = end_year - start_year

    # Start/end labels
    start_lbl = safe_text(str(start_year), font="Inter", font_size=20, color=TKK_DIM)
    start_lbl.next_to(line, LEFT, buff=0.2)
    end_lbl = safe_text(str(end_year), font="Inter", font_size=20, color=TKK_DIM)
    end_lbl.next_to(line, RIGHT, buff=0.2)

    group = VGroup(line, start_lbl, end_lbl)

    if markers:
        for m in markers:
            x_pos = (m["year"] - start_year) / year_range * width - width / 2
            tick = Line(UP * 0.15, DOWN * 0.15, color=m.get("color", TKK_GOLD),
                        stroke_width=2).move_to(RIGHT * x_pos)
            dot = Dot(point=RIGHT * x_pos, radius=0.08,
                      color=m.get("color", TKK_GOLD))
            label = safe_text(m.get("label", str(m["year"])),
                              font="Inter", font_size=16,
                              color=m.get("color", TKK_GOLD))
            label.next_to(dot, UP, buff=0.2)
            group.add(tick, dot, label)

    return group


# ============================================================
# LAYOUT
# ============================================================

def split_compare(left_content, right_content, left_label="", right_label="",
                  left_color=TKK_DIM, right_color=TKK_RED):
    """Split screen comparison. Returns VGroup.

    left_content, right_content: Mobject or string
    """
    divider_line = DashedLine(UP * 4, DOWN * 4, color=TKK_MUTED,
                               stroke_width=1, dash_length=0.15)

    if isinstance(left_content, str):
        left_content = safe_text(left_content, font="Inter", font_size=36,
                                 color=left_color)
    if isinstance(right_content, str):
        right_content = safe_text(right_content, font="Inter", font_size=36,
                                  color=right_color)

    left_content.move_to(LEFT * 2.5)
    right_content.move_to(RIGHT * 2.5)

    group = VGroup(divider_line, left_content, right_content)

    if left_label:
        ll = safe_text(left_label, font="Inter", font_size=22, color=left_color,
                       weight="BOLD")
        ll.next_to(left_content, DOWN, buff=0.4)
        group.add(ll)
    if right_label:
        rl = safe_text(right_label, font="Inter", font_size=22, color=right_color,
                       weight="BOLD")
        rl.next_to(right_content, DOWN, buff=0.4)
        group.add(rl)

    return group


def letterbox_closer(text_lines, colors=None, sizes=None):
    """Cinematic letterbox closer with stacked text. Returns VGroup.

    text_lines: list of strings
    colors: list of colors (optional)
    sizes: list of font sizes (optional)
    """
    if colors is None:
        colors = [TKK_WHITE] * len(text_lines)
    if sizes is None:
        sizes = [48] * len(text_lines)

    # Letterbox bars
    top_bar = Rectangle(width=12, height=1.2, fill_color=BLACK,
                        fill_opacity=1, stroke_width=0).to_edge(UP, buff=0)
    bot_bar = Rectangle(width=12, height=1.2, fill_color=BLACK,
                        fill_opacity=1, stroke_width=0).to_edge(DOWN, buff=0)

    texts = VGroup()
    for i, (line, color, size) in enumerate(zip(text_lines, colors, sizes)):
        t = safe_text(line, font="DM Serif Display", font_size=size, color=color)
        texts.add(t)

    texts.arrange(DOWN, buff=0.4)

    return VGroup(top_bar, bot_bar, texts)


# ============================================================
# SVG HELPERS
# ============================================================

def load_svg(filename, color=None, height=2.0):
    """Load an SVG from the assets library. Returns SVGMobject."""
    import os
    paths = [
        f"svg_assets/downloaded/{filename}",
        f"svg_assets/{filename}",
        filename,
    ]
    for p in paths:
        if os.path.exists(p):
            svg = SVGMobject(p)
            if color:
                svg.set_color(color)
            svg.scale_to_fit_height(height)
            return svg
    raise FileNotFoundError(f"SVG not found: {filename}")


def svg_with_label(svg_file, label_text, color=TKK_GOLD, svg_height=2.0,
                   label_size=24):
    """SVG icon with a text label underneath."""
    svg = load_svg(svg_file, color=color, height=svg_height)
    label = safe_text(label_text, font="Inter", font_size=label_size,
                      color=TKK_DIM)
    label.next_to(svg, DOWN, buff=0.25)
    return VGroup(svg, label)


# ============================================================
# VISUAL-FIRST HELPERS (v2 patterns)
# ============================================================

def svg_grid(svg_file, rows, cols, color=TKK_WHITE, icon_height=0.7,
             spacing_x=1.0, spacing_y=1.0, opacity=0.5):
    """Grid of repeated SVG icons — for scale scenes (e.g., 48 person icons).

    Returns VGroup of individual SVG mobjects.

    Usage:
        people = svg_grid("person.svg", 6, 8, color=TKK_WHITE, icon_height=0.7)
        people.move_to(UP * 3)
        self.play(LaggedStart(*[FadeIn(p, scale=0.3) for p in people], lag_ratio=0.005), run_time=0.6)
    """
    grid = VGroup()
    total_w = (cols - 1) * spacing_x
    total_h = (rows - 1) * spacing_y
    for r in range(rows):
        for c in range(cols):
            icon = load_svg(svg_file, color=color, height=icon_height)
            icon.move_to(
                LEFT * total_w / 2 + RIGHT * c * spacing_x +
                UP * total_h / 2 + DOWN * r * spacing_y
            )
            icon.set_opacity(opacity)
            grid.add(icon)
    return grid


def icon_state_change(icons, new_color, stagger=0.01):
    """Staggered color change for a group of icons.

    Returns a LaggedStart animation that changes all icons to new_color.

    Usage:
        people = svg_grid("person.svg", 6, 8)
        anim = icon_state_change(people, TKK_RED, stagger=0.02)
        self.play(anim, run_time=0.5)
    """
    anims = [icon.animate.set_color(new_color) for icon in icons]
    return LaggedStart(*anims, lag_ratio=stagger)


def shake_group(group, intensity=0.1, cycles=3):
    """Shake animation sequence for a VGroup. Returns list of animations.

    Each cycle is two moves (right then left). Play sequentially.

    Usage:
        for anim in shake_group(workers, intensity=0.1, cycles=3):
            self.play(anim, run_time=0.1)
    """
    anims = []
    for _ in range(cycles):
        for mob in group:
            mob.generate_target()
            mob.target.shift(RIGHT * intensity + UP * intensity * 0.5)
        anims.append(AnimationGroup(*[MoveToTarget(m) for m in group]))
        for mob in group:
            mob.generate_target()
            mob.target.shift(LEFT * intensity * 2 + DOWN * intensity)
        anims.append(AnimationGroup(*[MoveToTarget(m) for m in group]))
        for mob in group:
            mob.generate_target()
            mob.target.shift(RIGHT * intensity + UP * intensity * 0.5)
        anims.append(AnimationGroup(*[MoveToTarget(m) for m in group]))
    return anims


def disappear_sequence(icons, direction=DOWN, shift_amount=2, stagger_time=0.15):
    """Sequential disappearance animations for a list of icons.

    Returns list of animations to play one at a time.

    Usage:
        for anim in disappear_sequence(workers, direction=DOWN, shift_amount=2):
            self.play(anim, run_time=0.15)
    """
    anims = []
    for icon in icons:
        anims.append(icon.animate.shift(direction * shift_amount).set_opacity(0))
    return anims


# ============================================================
# SCENE-LEVEL PATTERNS
# ============================================================

def cascade_list(items, colors=None, size=44, stagger=0.4, x_align=LEFT * 2):
    """Rapid-fire stacking list — each item slams in below the previous.

    Returns (VGroup, list of FadeIn animations with stagger).
    items: list of strings
    """
    if colors is None:
        colors = [TKK_WHITE] * len(items)

    group = VGroup()
    anims = []
    for i, (item, color) in enumerate(zip(items, colors)):
        mark = safe_text("×", font="Inter", font_size=size, color=TKK_RED)
        text = safe_text(item, font="Inter", font_size=size, color=color)
        row = VGroup(mark, text).arrange(RIGHT, buff=0.3)
        group.add(row)
        anims.append(FadeIn(row, shift=LEFT * 0.3))

    group.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
    group.move_to(x_align + ORIGIN, aligned_edge=LEFT)
    return group, anims


def cascade_form(items, status_items=None, status_colors=None,
                 label_size=36, status_size=44, width=7.5):
    """Enhanced cascade — two-column form layout with separating rules.

    Like a form being stamped: CATEGORY → STATUS
    Returns (VGroup, list of animations).

    items: ["BANK ACCOUNT", "MEDICARE", ...]
    status_items: ["FROZEN", "TERMINATED", ...]
    status_colors: colors for status text
    """
    if status_items is None:
        status_items = items
        items = [""] * len(status_items)
    if status_colors is None:
        status_colors = [TKK_RED] * len(items)

    group = VGroup()
    anims = []

    for i, (label, status, s_color) in enumerate(zip(items, status_items, status_colors)):
        # Category label
        lbl = safe_text(label, font="Inter", font_size=label_size,
                        color=TKK_WHITE, weight="BOLD") if label else VGroup()
        # Status (bigger, colored, italic feel)
        stat = safe_text(status, font="Bebas Neue", font_size=status_size,
                         color=s_color)

        if label:
            row = VGroup(lbl, stat).arrange(RIGHT, buff=0.5)
        else:
            row = stat

        # Red × marker
        mark = safe_text("×", font="Inter", font_size=label_size, color=TKK_RED)
        full_row = VGroup(mark, row).arrange(RIGHT, buff=0.4)

        # Separator line
        sep = Line(LEFT * width/2, RIGHT * width/2,
                   color=TKK_MUTED, stroke_width=0.5, stroke_opacity=0.3)

        item_group = VGroup(full_row, sep).arrange(DOWN, buff=0.25)
        group.add(item_group)
        anims.append(AnimationGroup(
            FadeIn(full_row, shift=LEFT * 0.5),
            Create(sep, run_time=0.2),
        ))

    group.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
    return group, anims


def fact_callout(number, unit, description, number_color=TKK_GOLD,
                 desc_color=TKK_DIM, number_size=80, desc_size=32):
    """Prominent fact: big number + unit on one line, description below.

    Example: fact_callout("887", "statues", "Moved up to 18 km")
    """
    num = safe_text(number, font="Bebas Neue", font_size=number_size,
                    color=number_color)
    un = safe_text(unit, font="Inter", font_size=number_size * 0.45,
                   color=number_color)
    un.next_to(num, RIGHT, buff=0.2, aligned_edge=DOWN)
    top_row = VGroup(num, un)

    desc = safe_text(description, font="Inter", font_size=desc_size,
                     color=desc_color)
    desc.next_to(top_row, DOWN, buff=0.3)
    return VGroup(top_row, desc)


def big_number_reveal(number, label_above="", label_below="",
                      number_color=TKK_RED, number_size=160,
                      label_color=TKK_WHITE, label_size=48):
    """Dominant number with small labels above and below.

    The number takes center stage — massive, colored, commanding.
    Like the original Death Bureau "30" that filled the screen.
    """
    parts = VGroup()

    if label_above:
        above = safe_text(label_above, font="Inter", font_size=label_size * 0.7,
                          color=TKK_MUTED)
        parts.add(above)

    num = safe_text(str(number), font="Bebas Neue", font_size=number_size,
                    color=number_color)
    parts.add(num)

    if label_below:
        below = safe_text(label_below, font="Inter", font_size=label_size,
                          color=label_color, weight="BOLD")
        parts.add(below)

    parts.arrange(DOWN, buff=0.3)
    return parts


def icon_row(svg_files, labels=None, colors=None, icon_height=1.5,
             spacing=0.8):
    """Row of SVG icons with optional labels. Returns VGroup.

    svg_files: list of filenames from svg_assets/downloaded/
    """
    if colors is None:
        colors = [TKK_GOLD] * len(svg_files)
    if labels is None:
        labels = [None] * len(svg_files)

    icons = VGroup()
    for filename, label, color in zip(svg_files, labels, colors):
        try:
            icon = load_svg(filename, color=color, height=icon_height)
        except FileNotFoundError:
            icon = Square(side_length=icon_height, color=color, stroke_width=1)
        item = VGroup(icon)
        if label:
            lbl = safe_text(label, font="Inter", font_size=18, color=TKK_DIM)
            lbl.next_to(icon, DOWN, buff=0.15)
            item.add(lbl)
        icons.add(item)

    icons.arrange(RIGHT, buff=spacing)
    return icons


def population_drop(start_val, end_val, label=None, width=5,
                    start_color=TKK_GOLD, end_color=TKK_RED):
    """Two bars showing a dramatic population/value drop.

    Returns VGroup with start bar, end bar, arrow, and labels.
    """
    max_val = start_val
    start_h = 4.0
    end_h = max(0.15, (end_val / max_val) * start_h)

    bar_w = width * 0.3
    start_bar = Rectangle(width=bar_w, height=start_h,
                          fill_color=start_color, fill_opacity=0.7,
                          stroke_color=start_color, stroke_width=1)
    end_bar = Rectangle(width=bar_w, height=end_h,
                        fill_color=end_color, fill_opacity=0.7,
                        stroke_color=end_color, stroke_width=1)

    start_bar.move_to(LEFT * width * 0.25)
    end_bar.move_to(RIGHT * width * 0.25)
    start_bar.align_to(ORIGIN, DOWN)
    end_bar.align_to(ORIGIN, DOWN)

    # Labels on top
    s_lbl = safe_text(f"{start_val:,}", font="Bebas Neue", font_size=48,
                      color=start_color)
    s_lbl.next_to(start_bar, UP, buff=0.15)
    e_lbl = safe_text(f"{end_val:,}", font="Bebas Neue", font_size=48,
                      color=end_color)
    e_lbl.next_to(end_bar, UP, buff=0.15)

    # Arrow between
    arrow = Arrow(start_bar.get_right() + RIGHT * 0.2 + UP * start_h * 0.4,
                  end_bar.get_left() + LEFT * 0.2 + UP * end_h * 0.4,
                  color=TKK_RED, stroke_width=3, buff=0.1)

    group = VGroup(start_bar, end_bar, s_lbl, e_lbl, arrow)

    if label:
        lbl = safe_text(label, font="Inter", font_size=24, color=TKK_DIM)
        lbl.next_to(group, DOWN, buff=0.3)
        group.add(lbl)

    return group


def checklist(items, checked=None, size=32):
    """Animated checklist. Returns (VGroup, list of animations).

    items: list of strings
    checked: list of bools (default all True)
    """
    if checked is None:
        checked = [True] * len(items)

    group = VGroup()
    anims = []
    for item_text, is_checked in zip(items, checked):
        box = Square(side_length=0.35, color=TKK_DIM, stroke_width=2)
        text = safe_text(item_text, font="Inter", font_size=size, color=TKK_WHITE)
        row = VGroup(box, text).arrange(RIGHT, buff=0.3)

        if is_checked:
            check = safe_text("✓", font="Inter", font_size=28, color=TKK_GREEN)
            check.move_to(box.get_center())
            anims.append(FadeIn(check, scale=1.5))
            row.add(check)

        group.add(row)

    group.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
    return group, anims


def versus(left_text, right_text, left_color=TKK_DIM, right_color=TKK_GOLD,
           size=60):
    """A vs B comparison with 'vs' in the middle."""
    left = safe_text(left_text, font="Bebas Neue", font_size=size,
                     color=left_color)
    vs = safe_text("vs", font="Inter", font_size=size * 0.5, color=TKK_MUTED)
    right = safe_text(right_text, font="Bebas Neue", font_size=size,
                      color=right_color)
    return VGroup(left, vs, right).arrange(DOWN, buff=0.4)


def progress_dots(total, active=0, color=TKK_GOLD, inactive_color=TKK_MUTED,
                  radius=0.08, spacing=0.35):
    """Row of dots showing progress (like page indicators). Returns VGroup."""
    dots = VGroup()
    for i in range(total):
        c = color if i < active else inactive_color
        opacity = 1.0 if i < active else 0.3
        dot = Dot(radius=radius, color=c, fill_opacity=opacity)
        dots.add(dot)
    dots.arrange(RIGHT, buff=spacing)
    return dots


# ============================================================
# SCENE SETUP HELPERS
# ============================================================

def setup_portrait_scene(scene, bg_color=TKK_BG):
    """Standard scene setup for TKK portrait videos."""
    scene.camera.background_color = bg_color


def add_progress_bar(scene, progress, color=TKK_GOLD, height=0.04):
    """Add a thin progress bar at the very top of the frame."""
    bar = Rectangle(
        width=9 * progress, height=height,
        fill_color=color, fill_opacity=0.8,
        stroke_width=0
    )
    bar.to_edge(UP, buff=0).align_to(LEFT * 4.5, LEFT)
    scene.add(bar)
    return bar


# ============================================================
# TRANSITIONS
# ============================================================

def flash_transition(scene, color=WHITE, opacity=0.15, duration=0.1):
    """Quick white flash — for emphasis moments."""
    flash = Rectangle(width=20, height=20, fill_color=color,
                      fill_opacity=opacity, stroke_width=0)
    scene.play(FadeIn(flash, run_time=duration/2))
    scene.play(FadeOut(flash, run_time=duration/2))


def wipe_transition(scene, direction=RIGHT, color=TKK_BG, duration=0.4):
    """Wipe transition between scenes."""
    wipe = Rectangle(width=12, height=20, fill_color=color,
                     fill_opacity=1, stroke_width=0)
    wipe.next_to(scene.camera.frame, direction * -1, buff=0)
    scene.play(wipe.animate.move_to(ORIGIN), run_time=duration)
    scene.remove(wipe)


# ============================================================
# DATA VISUALIZATION PRIMITIVES
# ============================================================

def _make_axes(x_range, y_range, x_label="", y_label="",
               x_length=CHART_X_LEN, y_length=CHART_Y_LEN) -> dict:
    """Shared helper for consistent axis styling across chart types.

    Returns {"axes", "x_label", "y_label"}.
    """
    axes = Axes(
        x_range=x_range,
        y_range=y_range,
        x_length=x_length,
        y_length=y_length,
        axis_config={
            "color": GRID_COLOR,
            "tick_size": 0.05,
            "include_ticks": True,
            "include_tip": False,
            "font_size": 20,
        },
    )
    axes.move_to(CHART_CENTER)

    parts = {"axes": axes, "x_label": None, "y_label": None}

    if x_label:
        xl = Text(x_label, font="Inter", font_size=20, color=TKK_WHITE)
        xl.next_to(axes.x_axis, DOWN, buff=0.3)
        parts["x_label"] = xl

    if y_label:
        yl = Text(y_label, font="Inter", font_size=20, color=TKK_WHITE)
        yl.rotate(90 * np.pi / 180)
        yl.next_to(axes.y_axis, LEFT, buff=0.3)
        parts["y_label"] = yl

    return parts


def bar_graph(values, names, bar_colors=None, show_values=True,
              y_label="", title="", **axes_kw) -> dict:
    """Categorical bar chart using Manim's built-in BarChart.

    Returns {"chart", "bars", "bar_labels", "title"}.

    Animation hint: FadeIn chart, then chart.animate.change_bar_values(values)
    for animated grow.
    """
    if bar_colors is None:
        bar_colors = [TKK_RED if i % 2 == 0 else TKK_GOLD
                      for i in range(len(values))]

    chart = BarChart(
        values,
        bar_names=names,
        bar_colors=bar_colors,
        x_length=axes_kw.get("x_length", CHART_X_LEN),
        y_length=axes_kw.get("y_length", CHART_Y_LEN),
        y_axis_config={"include_tip": False, "font_size": 20, "color": GRID_COLOR},
        x_axis_config={"include_tip": False, "font_size": 20, "color": GRID_COLOR},
        bar_label_scale_val=0.5,
    )
    chart.move_to(CHART_CENTER)

    parts = {"chart": chart, "bars": chart.bars, "bar_labels": None, "title": None}

    if show_values:
        labels = VGroup()
        for bar, val in zip(chart.bars, values):
            lbl = Text(str(val), font="Inter", font_size=18, color=TKK_WHITE)
            lbl.next_to(bar, UP, buff=0.1)
            labels.add(lbl)
        parts["bar_labels"] = labels

    if title:
        t = Text(title, font="Inter", font_size=28, color=TKK_WHITE, weight="BOLD")
        t.next_to(chart, UP, buff=0.4)
        parts["title"] = t

    if y_label:
        yl = Text(y_label, font="Inter", font_size=20, color=TKK_WHITE)
        yl.rotate(90 * np.pi / 180)
        yl.next_to(chart, LEFT, buff=0.3)
        parts["y_label"] = yl

    return parts


def scatter_plot(x_data, y_data, x_label="", y_label="", dot_color=TKK_RED,
                 highlight_indices=None, title="", **axes_kw) -> dict:
    """Dots on axes with auto-ranging.

    Returns {"axes", "x_label", "y_label", "dots", "highlight_dots", "title"}.

    Animation hint: FadeIn axes, then LaggedStart FadeIn dots.
    """
    x_min, x_max = min(x_data), max(x_data)
    y_min, y_max = min(y_data), max(y_data)
    x_pad = max((x_max - x_min) * 0.1, 0.5)
    y_pad = max((y_max - y_min) * 0.1, 0.5)

    ax_parts = _make_axes(
        x_range=[x_min - x_pad, x_max + x_pad, (x_max - x_min) / 5 or 1],
        y_range=[y_min - y_pad, y_max + y_pad, (y_max - y_min) / 5 or 1],
        x_label=x_label, y_label=y_label,
        x_length=axes_kw.get("x_length", CHART_X_LEN),
        y_length=axes_kw.get("y_length", CHART_Y_LEN),
    )
    axes = ax_parts["axes"]

    dots = VGroup()
    highlight_dots = VGroup()
    highlight_set = set(highlight_indices or [])

    for i, (x, y) in enumerate(zip(x_data, y_data)):
        d = Dot(axes.c2p(x, y), radius=0.06, color=dot_color)
        dots.add(d)
        if i in highlight_set:
            h = Dot(axes.c2p(x, y), radius=0.1, color=TKK_GOLD)
            h.set_z_index(5)
            highlight_dots.add(h)

    parts = {**ax_parts, "dots": dots, "highlight_dots": highlight_dots, "title": None}

    if title:
        t = Text(title, font="Inter", font_size=28, color=TKK_WHITE, weight="BOLD")
        t.next_to(axes, UP, buff=0.4)
        parts["title"] = t

    return parts


def linear_plot(x_data, y_data, x_label="", y_label="", line_color=TKK_RED,
                show_dots=False, fill_below=False, title="", **axes_kw) -> dict:
    """Line graph with optional area fill.

    Returns {"axes", "x_label", "y_label", "line", "dots", "fill", "title"}.

    Animation hint: FadeIn axes, Create(line), then FadeIn fill.
    """
    x_min, x_max = min(x_data), max(x_data)
    y_min, y_max = min(y_data), max(y_data)
    x_pad = max((x_max - x_min) * 0.1, 0.5)
    y_pad = max((y_max - y_min) * 0.1, 0.5)

    ax_parts = _make_axes(
        x_range=[x_min - x_pad, x_max + x_pad, (x_max - x_min) / 5 or 1],
        y_range=[min(0, y_min - y_pad), y_max + y_pad, (y_max - y_min) / 5 or 1],
        x_label=x_label, y_label=y_label,
        x_length=axes_kw.get("x_length", CHART_X_LEN),
        y_length=axes_kw.get("y_length", CHART_Y_LEN),
    )
    axes = ax_parts["axes"]

    points = [axes.c2p(x, y) for x, y in zip(x_data, y_data)]
    line = VMobject(color=line_color, stroke_width=3)
    line.set_points_as_corners(points)

    dots_group = VGroup()
    if show_dots:
        for p in points:
            dots_group.add(Dot(p, radius=0.05, color=line_color))

    fill_mob = None
    if fill_below:
        y_bottom = axes.c2p(0, axes.y_range[0])[1]
        fill_points = list(points)
        fill_points.append([points[-1][0], y_bottom, 0])
        fill_points.append([points[0][0], y_bottom, 0])
        fill_mob = Polygon(*fill_points, color=line_color, fill_opacity=0.2,
                           stroke_width=0)

    parts = {**ax_parts, "line": line, "dots": dots_group, "fill": fill_mob, "title": None}

    if title:
        t = Text(title, font="Inter", font_size=28, color=TKK_WHITE, weight="BOLD")
        t.next_to(axes, UP, buff=0.4)
        parts["title"] = t

    return parts


def histogram(values, bins=10, bar_color=TKK_RED, x_label="", y_label="Frequency",
              title="", **axes_kw) -> dict:
    """Frequency distribution using numpy binning + manual rectangles.

    Returns {"axes", "x_label", "y_label", "bars", "title"}.

    Animation hint: FadeIn axes, LaggedStart GrowFromEdge(bar, DOWN).
    """
    counts, bin_edges = np.histogram(values, bins=bins)
    x_min, x_max = bin_edges[0], bin_edges[-1]
    y_max = int(counts.max())

    ax_parts = _make_axes(
        x_range=[x_min, x_max, (x_max - x_min) / bins],
        y_range=[0, y_max * 1.1, max(y_max // 5, 1)],
        x_label=x_label, y_label=y_label,
        x_length=axes_kw.get("x_length", CHART_X_LEN),
        y_length=axes_kw.get("y_length", CHART_Y_LEN),
    )
    axes = ax_parts["axes"]

    bars = VGroup()
    for i in range(len(counts)):
        if counts[i] == 0:
            continue
        left = axes.c2p(bin_edges[i], 0)
        right = axes.c2p(bin_edges[i + 1], counts[i])
        rect = Rectangle(
            width=abs(right[0] - left[0]),
            height=abs(right[1] - left[1]),
            color=bar_color,
            fill_opacity=0.7,
            stroke_width=1,
        )
        rect.move_to([(left[0] + right[0]) / 2, (left[1] + right[1]) / 2, 0])
        bars.add(rect)

    parts = {**ax_parts, "bars": bars, "title": None}

    if title:
        t = Text(title, font="Inter", font_size=28, color=TKK_WHITE, weight="BOLD")
        t.next_to(axes, UP, buff=0.4)
        parts["title"] = t

    return parts


def time_intervals(spans, time_range=None, colors=None, bar_height=0.6,
                   title="") -> dict:
    """Timeline with duration spans on a NumberLine.

    Args:
        spans: list of (start, end, label) tuples.
        time_range: [min, max, step] — auto-derived from spans if None.
        colors: list of colors per span, cycles TKK_RED/TKK_GOLD if None.

    Returns {"number_line", "spans", "span_labels", "title"}.

    Animation hint: FadeIn line, then GrowFromEdge each span LEFT sequentially.
    """
    if time_range is None:
        all_starts = [s[0] for s in spans]
        all_ends = [s[1] for s in spans]
        t_min = min(all_starts)
        t_max = max(all_ends)
        t_pad = max((t_max - t_min) * 0.05, 1)
        step = max((t_max - t_min) / 10, 1)
        time_range = [t_min - t_pad, t_max + t_pad, step]

    if colors is None:
        colors = [TKK_RED if i % 2 == 0 else TKK_GOLD for i in range(len(spans))]

    nl = NumberLine(
        x_range=time_range,
        length=CHART_X_LEN,
        include_numbers=True,
        font_size=20,
        color=GRID_COLOR,
        include_tip=False,
    )
    nl.move_to(CHART_CENTER)

    span_rects = VGroup()
    span_labels = VGroup()

    for i, (start, end, label) in enumerate(spans):
        left = nl.n2p(start)
        right = nl.n2p(end)
        width = abs(right[0] - left[0])
        rect = Rectangle(
            width=width, height=bar_height,
            color=colors[i % len(colors)],
            fill_opacity=0.6, stroke_width=1,
        )
        rect.move_to([(left[0] + right[0]) / 2, left[1] + bar_height / 2 + 0.15, 0])
        span_rects.add(rect)

        if label:
            lbl = Text(label, font="Inter", font_size=16, color=TKK_WHITE)
            lbl.move_to(rect)
            if lbl.width > rect.width - 0.1:
                lbl.next_to(rect, UP, buff=0.1)
            span_labels.add(lbl)

    parts = {"number_line": nl, "spans": span_rects, "span_labels": span_labels, "title": None}

    if title:
        t = Text(title, font="Inter", font_size=28, color=TKK_WHITE, weight="BOLD")
        t.next_to(nl, UP, buff=1.2)
        parts["title"] = t

    return parts
