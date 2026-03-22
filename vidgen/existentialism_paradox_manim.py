#!/usr/bin/env python3
"""Existentialism Paradox — You Can't Command Freedom.

6 scenes, ~40s total.
Domain shapes: stone_tablet, personal_yardstick, stick_figure, mirror_frame.
Visual throughline: yardstick transforms from gold standard to personal to commandment.

VTT cues (approximate):
  Scene 1 (0.0–7.0s):   Figure draws path, turns to command others, title pill
  Scene 2 (7.0–13.5s):  Clay shaping, personal trophy, "YOU DECIDE" label
  Scene 3 (13.5–20.0s): Gold yardstick replaced by colorful one, same function
  Scene 4 (20.0–27.0s): "DEFINE YOURSELF" on stone tablet, tablet cracks
  Scene 5 (27.0–34.0s): Logic chain — step 3 IS step 1 wearing different clothes
  Scene 6 (34.0–40.0s): Footprints behind, unique path became highway, neon sign
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from manim import (
    Scene, Text, Group, VGroup, Group, Rectangle, RoundedRectangle, Circle,
    Line, Arrow, DashedLine, Dot, Polygon, Ellipse, Square, Arc,
    FadeIn, FadeOut, GrowFromCenter, Write, Create, DrawBorderThenFill,
    AnimationGroup, LaggedStart, Flash, GrowArrow, MoveToTarget,
    config, UP, DOWN, LEFT, RIGHT, ORIGIN,
    WHITE, BLACK, rate_functions, DEGREES, PI,
)
import numpy as np

TTS_SCRIPT = """If success can't be accepted or rejected, maybe it can be reclaimed. Existence precedes essence. You arrive without a script. Meaning is made, not discovered. You define your own success. The liberation is real. But you haven't eliminated measurement. You've personalized it. A private yardstick is still a yardstick. And if you tell others to define success for themselves — that's a commandment against commandments. The moment you say follow me, you've left the path."""

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.frame_width = 9
config.frame_height = 16
config.background_color = "#080A10"
config.disable_caching = True

# ── Color palette ──────────────────────────────────────────
BG = "#080A10"; GRID = "#1A2030"; SURFACE = "#15192A"
WHITE_SOFT = "#F0F0F0"; GOLD = "#FFD700"
PATH_CYAN = "#06B6D4"
FREEDOM_GREEN = "#22C55E"
COMMAND_RED = "#EF4444"
TABLET_GRAY = "#9CA3AF"
CRACK_AMBER = "#F59E0B"
MUTED = "#475569"

# ── Safe zone & layout constants ──────────────────────────
SAFE_W = 8.0
SAFE_TOP = 7.2
SAFE_BOT = -6.4

ZONE_TITLE  = 6.2    # y 5.5–7.0  — scene label pills
ZONE_UPPER  = 3.5    # y 1.5–5.5  — hero visual top portion
ZONE_MID    = 0.0    # y -1.5–1.5 — central focal point, big numbers
ZONE_LOWER  = -3.5   # y -5.5–-1.5 — supporting visuals, bars, icons
ZONE_FOOTER = -6.0   # y -6.4–-5.5 — captions, source labels


# ── Core helpers ───────────────────────────────────────────

def gradient_bg(c=BG, g="#121828"):
    bg = Rectangle(width=12, height=20, fill_color=c, fill_opacity=1, stroke_width=0)
    glow = Circle(radius=5, fill_color=g, fill_opacity=0.08, stroke_width=0).move_to(UP * 2)
    return VGroup(bg, glow)

def grid_lines(opacity=0.04):
    lines = VGroup()
    for i in range(13):
        y = -8 + i * 16 / 12
        lines.add(Line(LEFT*5, RIGHT*5, color=GRID, stroke_width=0.5).move_to(UP*y).set_opacity(opacity))
    for j in range(7):
        x = -4.5 + j * 9 / 6
        lines.add(Line(DOWN*8, UP*8, color=GRID, stroke_width=0.5).move_to(RIGHT*x).set_opacity(opacity))
    return lines

def safe_text(content, **kwargs):
    t = Text(content, **kwargs)
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    return t

def label_pill(txt, color=GOLD, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    p = RoundedRectangle(width=t.width+0.5, height=t.height+0.3, corner_radius=0.15,
                         fill_color=bg, fill_opacity=0.9, stroke_width=0).move_to(t)
    return VGroup(p, t)


# ── Domain shapes (4) ─────────────────────────────────────

def stone_tablet(width=3.5, height=5, color=TABLET_GRAY):
    """Stone tablet — rounded top, flat bottom, slightly tapered."""
    body = Rectangle(width=width, height=height * 0.75, fill_color=color,
                     fill_opacity=0.85, stroke_color=WHITE_SOFT, stroke_width=1.5)
    top_arc = Arc(radius=width / 2, start_angle=0, angle=PI,
                  stroke_color=WHITE_SOFT, stroke_width=1.5)
    top_fill = Arc(radius=width / 2, start_angle=0, angle=PI,
                   fill_color=color, fill_opacity=0.85, stroke_width=0)
    top_arc.move_to(body.get_top())
    top_fill.move_to(body.get_top())
    return VGroup(body, top_fill, top_arc)

def personal_yardstick(length=4, color=CRACK_AMBER, rainbow=False):
    """Measuring yardstick — optionally colorful/rainbow segments."""
    if rainbow:
        colors = ["#EF4444", "#F59E0B", "#22C55E", "#06B6D4", "#8B5CF6"]
        segs = VGroup()
        seg_w = length / len(colors)
        for i, c in enumerate(colors):
            seg = Rectangle(width=seg_w, height=0.3, fill_color=c,
                            fill_opacity=0.9, stroke_width=0)
            seg.move_to(LEFT * (length / 2) + RIGHT * (seg_w / 2 + i * seg_w))
            segs.add(seg)
        ticks = VGroup()
        for i in range(int(length * 2) + 1):
            x = -length / 2 + i * 0.5
            h = 0.2 if i % 2 == 0 else 0.12
            tick = Line(UP * h / 2, DOWN * h / 2, color=BG, stroke_width=1.5)
            tick.move_to(RIGHT * x)
            ticks.add(tick)
        return VGroup(segs, ticks)
    bar = Rectangle(width=length, height=0.25, fill_color=color,
                    fill_opacity=0.9, stroke_color=color, stroke_width=1)
    ticks = VGroup()
    for i in range(int(length * 2) + 1):
        x = -length / 2 + i * 0.5
        h = 0.2 if i % 2 == 0 else 0.12
        tick = Line(UP * h / 2, DOWN * h / 2, color=BG, stroke_width=1.5)
        tick.move_to(RIGHT * x)
        ticks.add(tick)
    return VGroup(bar, ticks)

def stick_figure(color=WHITE_SOFT, height=2.0):
    """Simple stick figure."""
    scale = height / 2.0
    head = Circle(radius=0.2 * scale, color=color, stroke_width=2 * scale)
    body = Line(ORIGIN, DOWN * 0.6 * scale, color=color, stroke_width=2 * scale)
    body.next_to(head, DOWN, buff=0.02)
    l_leg = Line(body.get_bottom(), body.get_bottom() + DOWN * 0.4 * scale + LEFT * 0.2 * scale,
                 color=color, stroke_width=2 * scale)
    r_leg = Line(body.get_bottom(), body.get_bottom() + DOWN * 0.4 * scale + RIGHT * 0.2 * scale,
                 color=color, stroke_width=2 * scale)
    l_arm = Line(body.get_center(), body.get_center() + LEFT * 0.3 * scale + DOWN * 0.15 * scale,
                 color=color, stroke_width=2 * scale)
    r_arm = Line(body.get_center(), body.get_center() + RIGHT * 0.3 * scale + DOWN * 0.15 * scale,
                 color=color, stroke_width=2 * scale)
    return VGroup(head, body, l_leg, r_leg, l_arm, r_arm)

def mirror_frame(width=4, height=5, color=MUTED):
    """Rectangular mirror frame with reflective inner fill."""
    outer = Rectangle(width=width, height=height, stroke_color=color,
                      stroke_width=3, fill_opacity=0)
    inner = Rectangle(width=width - 0.4, height=height - 0.4,
                      fill_color="#1E293B", fill_opacity=0.6, stroke_width=0)
    top_dec = Line(LEFT * (width / 2 - 0.3), RIGHT * (width / 2 - 0.3),
                   color=color, stroke_width=1.5).move_to(UP * (height / 2 - 0.3))
    bot_dec = Line(LEFT * (width / 2 - 0.3), RIGHT * (width / 2 - 0.3),
                   color=color, stroke_width=1.5).move_to(DOWN * (height / 2 - 0.3))
    return VGroup(outer, inner, top_dec, bot_dec)


# ================================================================
# SCENE 1: HOOK (0.0–7.0s)
# Figure draws path on blank stage, then commands others
# Zones: TITLE (pill), MID (figure+spotlight), LOWER (path), FOOTER (watchers)
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 4.4
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE — pill
        pill = label_pill("YOU CAN'T COMMAND FREEDOM", color=COMMAND_RED)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_MID — spotlight + figure (hero at y=0 to y=1)
        spotlight = Circle(radius=2.5, fill_color="#1E293B", fill_opacity=0.3,
                           stroke_color=CRACK_AMBER, stroke_width=1.5)
        spotlight.move_to(UP * 0.5)

        figure = stick_figure(WHITE_SOFT, 2.2)
        figure.move_to(UP * 0.5)

        # ZONE_LOWER — spiraling path drawn by figure
        path_points = []
        for t in np.linspace(0, 4 * PI, 60):
            r = 0.3 + t * 0.08
            x = r * np.cos(t) * 0.5
            y = r * np.sin(t) * 0.3
            path_points.append([x, y, 0])

        path_line = VGroup()
        for i in range(len(path_points) - 1):
            seg = Line(path_points[i], path_points[i + 1],
                       color=PATH_CYAN, stroke_width=2, stroke_opacity=0.7)
            path_line.add(seg)
        path_line.move_to(DOWN * abs(ZONE_LOWER))

        # ZONE_FOOTER — dark figures waiting in shadows
        watchers = VGroup()
        positions = [LEFT * 3.0 + UP * ZONE_FOOTER,
                     LEFT * 1.0 + UP * (ZONE_FOOTER - 0.3),
                     RIGHT * 1.0 + UP * ZONE_FOOTER,
                     RIGHT * 3.0 + UP * (ZONE_FOOTER - 0.3)]
        for pos in positions:
            w = stick_figure(MUTED, 1.2)
            w.move_to(pos).set_opacity(0.3)
            watchers.add(w)

        self.play(FadeIn(spotlight, scale=0.9), run_time=0.4); t += 0.4
        self.play(FadeIn(figure, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # Draw path
        self.play(
            LaggedStart(*[Create(seg) for seg in path_line], lag_ratio=0.02),
            run_time=1.5,
        )                                                                    # t=2.6

        # Watchers appear
        self.play(
            LaggedStart(*[FadeIn(w, shift=UP * 0.2) for w in watchers], lag_ratio=0.1),
            run_time=0.6,
        )                                                                    # t=3.2

        # Command arrow from figure to watchers
        cmd_arrow = Arrow(figure.get_bottom() + DOWN * 0.3,
                          DOWN * 4.5, color=COMMAND_RED, stroke_width=3)
        self.play(GrowArrow(cmd_arrow), run_time=0.5); t += 0.5

        target = getattr(self.__class__, 'DURATION', 4.4)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE MYSTERY (7.0–13.5s)
# Existence precedes essence — clay shaping, personal trophy
# Zones: TITLE (pill), MID (clay→trophy), LOWER (decide label), FOOTER (rings)
# ================================================================
class Scene2_Mystery(Scene):
    DURATION = 15.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE — pill
        pill = label_pill("EXISTENCE FIRST", color=FREEDOM_GREEN)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_MID — clay blob → trophy (hero at y=0 to y=1)
        clay = Ellipse(width=2, height=1.5, fill_color=CRACK_AMBER,
                       fill_opacity=0.7, stroke_color=CRACK_AMBER, stroke_width=1.5)
        clay.move_to(UP * ZONE_MID + UP * 1.0)

        # Hands shaping (two arcs flanking clay)
        l_hand = Arc(radius=1.5, start_angle=30 * DEGREES, angle=120 * DEGREES,
                     stroke_color=WHITE_SOFT, stroke_width=2.5)
        l_hand.move_to(LEFT * 1.8 + UP * 1.0)
        r_hand = Arc(radius=1.5, start_angle=210 * DEGREES, angle=120 * DEGREES,
                     stroke_color=WHITE_SOFT, stroke_width=2.5)
        r_hand.move_to(RIGHT * 1.8 + UP * 1.0)

        # Personal trophy (organic — not standard gold)
        trophy_base = Rectangle(width=1.2, height=0.3, fill_color=CRACK_AMBER,
                                fill_opacity=0.9, stroke_width=0)
        trophy_stem = Rectangle(width=0.3, height=1.0, fill_color=CRACK_AMBER,
                                fill_opacity=0.9, stroke_width=0)
        trophy_top = Circle(radius=0.6, fill_color=CRACK_AMBER,
                            fill_opacity=0.7, stroke_color=FREEDOM_GREEN, stroke_width=2)
        trophy_stem.next_to(trophy_base, UP, buff=0)
        trophy_top.next_to(trophy_stem, UP, buff=0)
        trophy = VGroup(trophy_base, trophy_stem, trophy_top)
        trophy.move_to(UP * ZONE_MID + UP * 1.0)

        # ZONE_LOWER — "YOU DECIDE" label
        decide_label = label_pill("YOU DECIDE WHAT COUNTS", color=FREEDOM_GREEN, fs=24)
        decide_label.move_to(UP * ZONE_LOWER)

        # ZONE_FOOTER — radiating circles showing liberation
        rings = VGroup()
        for i in range(3):
            r = Circle(radius=1.5 + i * 1.2, stroke_color=FREEDOM_GREEN,
                       stroke_width=1, stroke_opacity=0.3 - i * 0.08)
            r.move_to(UP * ZONE_FOOTER)
            rings.add(r)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(clay, scale=0.8), run_time=0.4); t += 0.4
        self.play(FadeIn(l_hand), FadeIn(r_hand), run_time=0.4); t += 0.4

        # Hands close in — shaping
        self.play(
            l_hand.animate.shift(RIGHT * 0.5),
            r_hand.animate.shift(LEFT * 0.5),
            clay.animate.scale(0.7),
            run_time=0.6,
        )                                                                    # t=1.7

        # Clay transforms to trophy
        self.play(
            FadeOut(clay), FadeOut(l_hand), FadeOut(r_hand),
            FadeIn(trophy, scale=0.5),
            run_time=0.6,
        )                                                                    # t=2.3

        self.play(FadeIn(decide_label, shift=UP * 0.2), run_time=0.4); t += 0.4

        # Liberation rings expand
        self.play(
            LaggedStart(*[GrowFromCenter(r) for r in rings], lag_ratio=0.15),
            run_time=1.0,
        )                                                                    # t=3.7

        target = getattr(self.__class__, 'DURATION', 15.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: THE WRONG ANSWER (13.5–20.0s)
# Gold yardstick replaced by colorful one — same function
# Zones: TITLE (pill), UPPER (yardsticks), MID (my label), LOWER (figure), FOOTER (question)
# ================================================================
class Scene3_WrongAnswer(Scene):
    DURATION = 1.4
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE — pill
        pill = label_pill("THE WRONG ANSWER", color=COMMAND_RED)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER — standard gold yardstick
        gold_ys = personal_yardstick(5, GOLD)
        gold_ys.move_to(UP * ZONE_UPPER)

        # Personal rainbow yardstick (replaces gold)
        rainbow_ys = personal_yardstick(5, rainbow=True)
        rainbow_ys.move_to(UP * ZONE_UPPER)

        # ZONE_MID — "MY METRICS" label
        my_label = label_pill("MY METRICS", color=CRACK_AMBER, fs=26)
        my_label.move_to(UP * ZONE_MID)

        # ZONE_LOWER — figure proudly measuring with personal yardstick
        figure = stick_figure(WHITE_SOFT, 2.0)
        figure.move_to(UP * ZONE_LOWER + LEFT * 0.5)

        # Small yardstick copy next to figure
        small_ys = personal_yardstick(2.5, rainbow=True)
        small_ys.scale(0.6).next_to(figure, RIGHT, buff=0.3)

        # ZONE_FOOTER — question
        question = safe_text("SAME FUNCTION?", font="Inter", font_size=28,
                             color=COMMAND_RED, weight="BOLD")
        question.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # Show gold yardstick
        self.play(FadeIn(gold_ys, scale=0.9), run_time=0.5); t += 0.5

        # Red X over gold
        x_mark = VGroup(
            Line(LEFT * 0.4 + UP * 0.4, RIGHT * 0.4 + DOWN * 0.4,
                 color=COMMAND_RED, stroke_width=5),
            Line(RIGHT * 0.4 + UP * 0.4, LEFT * 0.4 + DOWN * 0.4,
                 color=COMMAND_RED, stroke_width=5),
        ).move_to(gold_ys)
        self.play(Create(x_mark[0]), Create(x_mark[1]), run_time=0.3); t += 0.3

        # Replace with rainbow
        self.play(
            FadeOut(gold_ys), FadeOut(x_mark),
            FadeIn(rainbow_ys, scale=1.05),
            run_time=0.5,
        )                                                                    # t=1.6

        self.play(FadeIn(my_label, shift=UP * 0.2), run_time=0.4); t += 0.4

        # Figure appears measuring
        self.play(FadeIn(figure), FadeIn(small_ys), run_time=0.5); t += 0.5

        # Uncomfortable question
        self.play(FadeIn(question, shift=UP * 0.2), run_time=0.4); t += 0.4

        target = getattr(self.__class__, 'DURATION', 1.4)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE CONTRADICTION (20.0–27.0s)
# "DEFINE YOURSELF" on stone tablet — commandment cracks
# Zones: TITLE (pill), MID (tablet+text), LOWER (halves+arrow), FOOTER (caption)
# ================================================================
class Scene4_Contradiction(Scene):
    DURATION = 3.4
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE — pill
        pill = label_pill("THE CONTRADICTION", color=CRACK_AMBER)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_MID — stone tablet with commandment (hero at y=0 to y=1)
        tablet = stone_tablet(3.5, 4.5, TABLET_GRAY)
        tablet.move_to(UP * (ZONE_MID + 1.0))

        # Text on tablet
        cmd_text = safe_text("DEFINE", font="Bebas Neue", font_size=60,
                             color=BG, weight="BOLD")
        cmd_text2 = safe_text("YOURSELF!", font="Bebas Neue", font_size=60,
                              color=BG, weight="BOLD")
        cmd_text.move_to(UP * 1.6)
        cmd_text2.move_to(UP * 0.6)

        # Crack line through tablet
        crack = VGroup()
        crack_points = [UP * 3.2, UP * 2.5 + RIGHT * 0.3, UP * 1.5 + LEFT * 0.2,
                        UP * 0.5 + RIGHT * 0.1, DOWN * 0.3 + LEFT * 0.15, DOWN * 1.0]
        for i in range(len(crack_points) - 1):
            seg = Line(crack_points[i], crack_points[i + 1],
                       color=COMMAND_RED, stroke_width=3)
            crack.add(seg)

        # ZONE_LOWER — two halves labels
        l_half = label_pill("BE FREE", color=FREEDOM_GREEN, fs=22)
        l_half.move_to(LEFT * 2.5 + UP * ZONE_LOWER)
        r_half = label_pill("BECAUSE I SAID SO", color=COMMAND_RED, fs=22)
        r_half.move_to(RIGHT * 2.0 + UP * ZONE_LOWER)

        # Arrow connecting them
        paradox_arrow = Arrow(l_half.get_right(), r_half.get_left(),
                              color=CRACK_AMBER, stroke_width=2, buff=0.2)

        # ZONE_FOOTER — caption
        footer = safe_text("PRESCRIPTION AGAINST PRESCRIPTIONS", font="Inter",
                           font_size=20, color=MUTED)
        footer.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(GrowFromCenter(tablet), run_time=0.6); t += 0.6
        self.play(FadeIn(cmd_text, shift=DOWN * 0.1),
                  FadeIn(cmd_text2, shift=DOWN * 0.1), run_time=0.5)      # t=1.4

        self.wait(1.5); t += 1.5

        # Crack appears
        self.play(
            LaggedStart(*[Create(seg) for seg in crack], lag_ratio=0.08),
            run_time=0.8,
        )                                                                    # t=3.7

        # Flash on crack
        self.play(Flash(UP * 1.0, color=COMMAND_RED, line_length=0.5,
                        num_lines=10, run_time=0.3))                       # t=4.0

        # Two halves appear
        self.play(FadeIn(l_half, shift=LEFT * 0.3),
                  FadeIn(r_half, shift=RIGHT * 0.3), run_time=0.5)        # t=4.5

        self.play(GrowArrow(paradox_arrow), run_time=0.4); t += 0.4

        self.play(FadeIn(footer, shift=UP * 0.1), run_time=0.3); t += 0.3

        target = getattr(self.__class__, 'DURATION', 3.4)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE PROOF (27.0–34.0s)
# Logic chain: step 3 IS step 1 wearing different clothes
# Zones: TITLE (pill), UPPER (step1), MID (step2+3), LOWER (mirror+eq), FOOTER (loop)
# ================================================================
class Scene5_Proof(Scene):
    DURATION = 3.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE — pill
        pill = label_pill("THE PROOF", color=GOLD)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER — logic step 1
        s1_text = safe_text("IMPOSED MEANING", font="Inter", font_size=26,
                            color=WHITE_SOFT, weight="BOLD")
        s1_arrow = Arrow(LEFT * 0.3, RIGHT * 0.3, color=MUTED, stroke_width=2, buff=0.1)
        s1_x = safe_text("X", font="Bebas Neue", font_size=50, color=COMMAND_RED)
        step1 = VGroup(s1_text, s1_arrow, s1_x).arrange(RIGHT, buff=0.3)
        step1.move_to(UP * ZONE_UPPER)

        # ZONE_MID — logic steps 2 & 3
        s2_text = safe_text("MAKE YOUR OWN", font="Inter", font_size=26,
                            color=WHITE_SOFT, weight="BOLD")
        s2_arrow = Arrow(LEFT * 0.3, RIGHT * 0.3, color=MUTED, stroke_width=2, buff=0.1)
        s2_check = safe_text("OK", font="Bebas Neue", font_size=50, color=FREEDOM_GREEN)
        step2 = VGroup(s2_text, s2_arrow, s2_check).arrange(RIGHT, buff=0.3)
        step2.move_to(UP * (ZONE_MID + 1.0))

        s3_text = safe_text("TELL OTHERS TO", font="Inter", font_size=26,
                            color=WHITE_SOFT, weight="BOLD")
        s3_arrow = Arrow(LEFT * 0.3, RIGHT * 0.3, color=MUTED, stroke_width=2, buff=0.1)
        s3_result = safe_text("OK", font="Bebas Neue", font_size=50, color=FREEDOM_GREEN)
        step3 = VGroup(s3_text, s3_arrow, s3_result).arrange(RIGHT, buff=0.3)
        step3.move_to(UP * (ZONE_MID - 1.0))

        # Glitched X that replaces the check
        s3_x = safe_text("X", font="Bebas Neue", font_size=50, color=COMMAND_RED)
        s3_x.move_to(s3_result)

        # ZONE_LOWER — mirror reveals equivalence
        mirror = mirror_frame(3.5, 2.5, MUTED)
        mirror.move_to(UP * ZONE_LOWER)

        # "STEP 3 = STEP 1" inside mirror
        eq_text = safe_text("STEP 3 = STEP 1", font="Inter", font_size=24,
                            color=COMMAND_RED, weight="BOLD")
        eq_text.move_to(UP * ZONE_LOWER)

        # ZONE_FOOTER — feedback loop arrow
        loop = Arc(radius=1.2, start_angle=90 * DEGREES, angle=300 * DEGREES,
                   stroke_color=CRACK_AMBER, stroke_width=2.5)
        loop.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # Step 1
        self.play(FadeIn(step1, shift=DOWN * 0.2), run_time=0.5); t += 0.5

        # Step 2
        self.play(FadeIn(step2, shift=DOWN * 0.2), run_time=0.5); t += 0.5

        # Step 3 — initially green
        self.play(FadeIn(step3, shift=DOWN * 0.2), run_time=0.5); t += 0.5

        self.wait(0.7); t += 0.7

        # Glitch: green check → red X
        self.play(
            FadeOut(s3_result, scale=0.5),
            FadeIn(s3_x, scale=1.5),
            Flash(s3_x.get_center(), color=COMMAND_RED, line_length=0.4,
                  num_lines=8, run_time=0.3),
            run_time=0.4,
        )                                                                    # t=2.9

        # Mirror reveals equivalence
        self.play(FadeIn(mirror, scale=0.9), run_time=0.4); t += 0.4
        self.play(FadeIn(eq_text, shift=UP * 0.1), run_time=0.4); t += 0.4

        # Feedback loop
        self.play(Create(loop), run_time=0.6); t += 0.6

        target = getattr(self.__class__, 'DURATION', 3.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE PUNCH (34.0–40.0s)
# Unique path became a highway — freedom became franchise
# Zones: TITLE (letterbox), UPPER (figure), MID (footprints), LOWER (highway), FOOTER (neon)
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 17.9
    def construct(self):
        self.add(gradient_bg("#0A0E18"), grid_lines(0.02))
        t = 0

        # Letterbox bars (decorative, added to bg layer)
        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP * (8 - bh / 2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN * (8 - bh / 2)),
        )

        # ZONE_UPPER — figure looking back
        figure = stick_figure(WHITE_SOFT, 2.2)
        figure.move_to(UP * ZONE_UPPER)

        # ZONE_MID — footprints behind — others followed
        footprints = VGroup()
        for i in range(8):
            fp = Ellipse(width=0.3, height=0.15, fill_color=MUTED,
                         fill_opacity=0.4 + i * 0.05, stroke_width=0)
            fp.move_to(LEFT * (3.5 - i * 0.8) +
                       UP * (ZONE_MID - 0.5 + i * 0.15) +
                       RIGHT * np.random.uniform(-0.15, 0.15))
            footprints.add(fp)

        # ZONE_LOWER — highway lines — the unique path became a road
        highway = VGroup()
        for i in range(6):
            y = ZONE_LOWER + 1.5 - i * 0.8
            dash = Rectangle(width=0.15, height=0.6, fill_color=CRACK_AMBER,
                             fill_opacity=0.5, stroke_width=0)
            dash.move_to(UP * y)
            highway.add(dash)

        edge_l = Line(UP * (ZONE_MID - 1.0) + LEFT * 1.5,
                      UP * (ZONE_FOOTER - 0.5) + LEFT * 1.5,
                      color=MUTED, stroke_width=1.5, stroke_opacity=0.4)
        edge_r = Line(UP * (ZONE_MID - 1.0) + RIGHT * 1.5,
                      UP * (ZONE_FOOTER - 0.5) + RIGHT * 1.5,
                      color=MUTED, stroke_width=1.5, stroke_opacity=0.4)

        # ZONE_FOOTER — neon sign at bottom
        neon_bg = RoundedRectangle(width=7.5, height=1.2, corner_radius=0.15,
                                   stroke_color=COMMAND_RED, stroke_width=2,
                                   fill_color=SURFACE, fill_opacity=0.9)
        neon_text = safe_text("AUTHENTIC SELF-EXPRESSION", font="Inter",
                              font_size=24, color=COMMAND_RED, weight="BOLD")
        neon_sub = safe_text("(REQUIRED)", font="Inter", font_size=20,
                             color=CRACK_AMBER)
        neon_text.move_to(UP * 0.15)
        neon_sub.move_to(DOWN * 0.3)
        neon_sign = VGroup(neon_bg, neon_text, neon_sub)
        neon_sign.move_to(UP * (ZONE_FOOTER + 0.5))

        self.play(FadeIn(figure, scale=1.05), run_time=0.4); t += 0.4

        # Footprints appear
        self.play(
            LaggedStart(*[FadeIn(fp, scale=0.5) for fp in footprints], lag_ratio=0.06),
            run_time=0.6,
        )                                                                    # t=1.0

        # Highway materializes
        self.play(
            FadeIn(edge_l), FadeIn(edge_r),
            LaggedStart(*[FadeIn(d, shift=DOWN * 0.1) for d in highway], lag_ratio=0.08),
            run_time=0.8,
        )                                                                    # t=1.8

        # Neon sign — the punchline
        self.play(FadeIn(neon_sign, scale=0.9), run_time=0.5); t += 0.5

        # Neon flicker
        self.play(neon_sign.animate.set_opacity(0.3), run_time=0.15); t += 0.15
        self.play(neon_sign.animate.set_opacity(1.0), run_time=0.15); t += 0.15

        target = getattr(self.__class__, 'DURATION', 17.9)
        self.wait(max(0.1, target - t - 0.8))

        # Fade to black
        black = Rectangle(width=12, height=20, fill_color=BLACK,
                           fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=2.0); t += 2.0

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ── Infra ─────────────────────────────────────────────────────
SCENES = [Scene1_Hook, Scene2_Mystery, Scene3_WrongAnswer,
          Scene4_Contradiction, Scene5_Proof, Scene6_Punch]

def render_single_scene(idx):
    config.output_file = f"existentialism_paradox_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    SCENES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"existentialism_paradox_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENES):
        n = f"existentialism_paradox_scene_{i+1}"; print(f"  Preview {n}...")
        config.output_file = n; config.save_last_frame = True; config.format = "png"
        S().render()
        for p in Path(config.media_dir).rglob(f"{n}*"):
            if p.suffix == ".png":
                dst = d / f"{n}.png"; shutil.copy2(str(p), str(dst))
                print(f"  OK: {dst} ({dst.stat().st_size//1024} KB)"); break
    config.save_last_frame = False; config.format = None
    print(f"\nAll 6 previews -> {d}/")

if __name__ == "__main__":
    import time, gc
    od = Path(__file__).parent
    if "--preview" in sys.argv:
        render_previews()
        from render_utils import run_preview_qa
        run_preview_qa(od / "previews")
        sys.exit(0)
    if "--scene" in sys.argv:
        timings_json = os.environ.get("TKK_SCENE_TIMINGS")
        if timings_json:
            _idx = int(sys.argv[sys.argv.index("--scene")+1])
            SCENES[_idx].DURATION = json.loads(timings_json)[_idx]
        render_single_scene(int(sys.argv[sys.argv.index("--scene")+1])); sys.exit(0)

    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_existentialism_paradox.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="existentialism_paradox", audio_path=str(audio))
    final = od / "existentialism_paradox_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")

    from render_utils import run_post_render_qa
    run_post_render_qa(str(final), scene_count=6)
