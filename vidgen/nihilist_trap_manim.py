#!/usr/bin/env python3
"""Nihilist Trap — Visual-first per PRODUCTION_GUIDE.md.

6 scenes, ~40s total.
Domain shapes: yardstick, cage_bars, ghost_yardstick, pendulum.
Visual throughline: broken yardstick pieces reappear in every scene.

VTT cues (approximate):
  Scene 1 (0.0–7.0s):   Figure measures everything, yardstick snaps, pieces form cage
  Scene 2 (7.0–13.5s):  Figure inside cage, others rush past, "FREEDOM" label
  Scene 3 (13.5–20.0s): Weight lifts, "NOTHING MATTERS" — the appeal of refusal
  Scene 4 (20.0–27.0s): Ghost yardstick, orbit path, reaction is not freedom
  Scene 5 (27.0–34.0s): Split screen — pursuer vs refuser, both orbiting trophy
  Scene 6 (34.0–40.0s): Cage dissolves, pieces become question mark, empty field
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from manim import (
    Scene, Text, Group, VGroup, Rectangle, RoundedRectangle, Circle,
    Line, Arrow, DashedLine, Dot, Polygon, Ellipse, Square, Arc,
    FadeIn, FadeOut, GrowFromCenter, Write, Create, DrawBorderThenFill,
    AnimationGroup, LaggedStart, Flash, GrowArrow, MoveToTarget,
    config, UP, DOWN, LEFT, RIGHT, ORIGIN,
    WHITE, BLACK, rate_functions, DEGREES, PI,
)
import numpy as np

TTS_SCRIPT = """If success is imposed, its metrics inherited, its architecture serving power — what are we chasing? The nihilist refuses to measure at all. Not laziness. A rigged yardstick produces meaningless measurements. From outside it looks like giving up. From inside, like setting down something enormously heavy. But nihilism clears the field and plants nothing. You can't live in negation forever. The nihilist who merely refuses is still defined by what's refused. Reaction is not freedom. It's freedom's shadow."""

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.frame_width = 9
config.frame_height = 16
config.background_color = "#080A10"
config.disable_caching = True

# ── Color palette ──────────────────────────────────────────
BG = "#080A10"
GRID = "#1A2030"
SURFACE = "#15192A"
WHITE_SOFT = "#F0F0F0"
GOLD = "#FFD700"
VOID_BLUE = "#1B2A4A"
MEASURE_AMBER = "#D4A017"
REFUSAL_RED = "#EF4444"
ASH_GRAY = "#6B7280"
GHOST_TEAL = "#2DD4BF"
CAGE_DARK = "#374151"
MUTED = "#475569"

# ── Safe zone / layout constants ──────────────────────────
SAFE_W = 8.0
SAFE_TOP = 7.2
SAFE_BOT = -6.4

# Vertical layout zones — USE THESE for all positioning
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
    if t.width > SAFE_W:
        t.scale(SAFE_W / t.width)
    return t

def label_pill(txt, color=GOLD, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W:
        t.scale(SAFE_W / t.width)
    p = RoundedRectangle(width=t.width+0.5, height=t.height+0.3, corner_radius=0.15,
                         fill_color=bg, fill_opacity=0.9, stroke_width=0).move_to(t)
    return VGroup(p, t)


# ── Domain shapes (4 required) ─────────────────────────────

def yardstick(length=5, color=MEASURE_AMBER, broken=False):
    """Flat measuring ruler with tick marks. If broken=True, returns two halves."""
    if not broken:
        bar = Rectangle(width=length, height=0.25, fill_color=color,
                        fill_opacity=0.9, stroke_color=color, stroke_width=1)
        ticks = VGroup()
        for i in range(int(length * 2) + 1):
            x = -length / 2 + i * 0.5
            h = 0.2 if i % 2 == 0 else 0.12
            tick = Line(UP * h / 2, DOWN * h / 2, color=BG, stroke_width=1.5)
            tick.move_to(bar.get_center() + RIGHT * x + UP * 0.0)
            ticks.add(tick)
        return VGroup(bar, ticks)
    else:
        left = Rectangle(width=length * 0.48, height=0.25, fill_color=color,
                         fill_opacity=0.9, stroke_width=1, stroke_color=color)
        right = Rectangle(width=length * 0.48, height=0.25, fill_color=color,
                          fill_opacity=0.9, stroke_width=1, stroke_color=color)
        left_edge = Line(left.get_right() + LEFT * 0.05 + UP * 0.12,
                         left.get_right() + LEFT * 0.05 + DOWN * 0.12,
                         color=REFUSAL_RED, stroke_width=2)
        right_edge = Line(right.get_left() + RIGHT * 0.05 + UP * 0.12,
                          right.get_left() + RIGHT * 0.05 + DOWN * 0.12,
                          color=REFUSAL_RED, stroke_width=2)
        l_half = VGroup(left, left_edge)
        r_half = VGroup(right, right_edge)
        return l_half, r_half

def cage_bars(width=4, height=6, num_bars=6, color=CAGE_DARK):
    """Vertical cage made from yardstick-like pieces."""
    bars = VGroup()
    for i in range(num_bars):
        x = -width / 2 + i * width / (num_bars - 1)
        bar = Rectangle(width=0.15, height=height, fill_color=color,
                        fill_opacity=0.7, stroke_color=MEASURE_AMBER, stroke_width=0.8)
        bar.move_to(RIGHT * x)
        for j in range(int(height * 2)):
            y = -height / 2 + j * 0.5 + 0.25
            tick = Line(LEFT * 0.06, RIGHT * 0.06, color=MEASURE_AMBER,
                        stroke_width=0.5).move_to(bar.get_center() + UP * y)
            bar.add(tick)
        bars.add(bar)
    return bars

def ghost_yardstick(length=5, color=GHOST_TEAL):
    """Translucent hovering yardstick — the measurement that won't leave."""
    bar = Rectangle(width=length, height=0.25, fill_color=color,
                    fill_opacity=0.15, stroke_color=color, stroke_width=1.5)
    bar.set_stroke(opacity=0.4)
    ticks = VGroup()
    for i in range(int(length * 2) + 1):
        x = -length / 2 + i * 0.5
        h = 0.18 if i % 2 == 0 else 0.1
        tick = Line(UP * h / 2, DOWN * h / 2, color=color, stroke_width=1)
        tick.set_opacity(0.3)
        tick.move_to(bar.get_center() + RIGHT * x)
        ticks.add(tick)
    return VGroup(bar, ticks)

def pendulum(length=4, bob_radius=0.3, color=MEASURE_AMBER):
    """Swinging pendulum — fulcrum, rod, bob."""
    pivot = Dot(radius=0.08, color=MUTED)
    rod = Line(ORIGIN, DOWN * length, color=ASH_GRAY, stroke_width=2)
    bob = Circle(radius=bob_radius, fill_color=color, fill_opacity=0.8,
                 stroke_color=color, stroke_width=1.5)
    bob.move_to(rod.get_end())
    return VGroup(pivot, rod, bob)

def stick_figure(color=WHITE_SOFT, height=1.8):
    """Simple standing person — head + body + legs."""
    head = Circle(radius=height * 0.08, fill_color=color, fill_opacity=0.8, stroke_width=0)
    head.move_to(UP * height * 0.4)
    body = Line(UP * height * 0.32, DOWN * height * 0.05, color=color, stroke_width=2)
    leg_l = Line(DOWN * height * 0.05, DOWN * height * 0.4 + LEFT * height * 0.1,
                 color=color, stroke_width=2)
    leg_r = Line(DOWN * height * 0.05, DOWN * height * 0.4 + RIGHT * height * 0.1,
                 color=color, stroke_width=2)
    arm_l = Line(UP * height * 0.2, LEFT * height * 0.15 + UP * height * 0.05,
                 color=color, stroke_width=2)
    arm_r = Line(UP * height * 0.2, RIGHT * height * 0.15 + UP * height * 0.05,
                 color=color, stroke_width=2)
    return VGroup(head, body, leg_l, leg_r, arm_l, arm_r).scale_to_fit_height(height)

def trophy_shape(height=1.5, color=GOLD):
    """Simple trophy — cup + handles + base."""
    cup = Polygon(
        np.array([-0.4, 0.5, 0]), np.array([0.4, 0.5, 0]),
        np.array([0.3, -0.1, 0]), np.array([-0.3, -0.1, 0]),
        fill_color=color, fill_opacity=0.8, stroke_color=color, stroke_width=1.5,
    )
    stem = Rectangle(width=0.12, height=0.3, fill_color=color,
                     fill_opacity=0.7, stroke_width=0).move_to(DOWN * 0.25)
    base = Rectangle(width=0.5, height=0.1, fill_color=color,
                     fill_opacity=0.7, stroke_width=0).move_to(DOWN * 0.42)
    handle_l = Arc(radius=0.2, start_angle=PI/2, angle=PI, stroke_color=color,
                   stroke_width=1.5).move_to(LEFT * 0.45 + UP * 0.2)
    handle_r = Arc(radius=0.2, start_angle=-PI/2, angle=PI, stroke_color=color,
                   stroke_width=1.5).move_to(RIGHT * 0.45 + UP * 0.2)
    return VGroup(cup, stem, base, handle_l, handle_r).scale_to_fit_height(height)


# ================================================================
# SCENE 1: THE HOOK (0.0–7.0s)
# Figure measures everything -> yardstick snaps -> pieces form cage
# Zones: TITLE (pill), UPPER (numbers), MID (figure+yardstick), LOWER (cage)
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 8.3
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE — pill
        pill = label_pill("STILL A PRISON", color=REFUSAL_RED)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_MID — figure holding a yardstick
        figure = stick_figure(WHITE_SOFT, 2.5)
        figure.move_to(UP * ZONE_MID)

        # Full yardstick near figure
        ys = yardstick(4, MEASURE_AMBER)
        ys.move_to(figure.get_center() + RIGHT * 0.5 + DOWN * 0.3)

        # ZONE_UPPER — floating numbers that turn to ash
        numbers = VGroup()
        num_vals = ["87", "3.2", "61%", "A+"]
        for i, val in enumerate(num_vals):
            n = safe_text(val, font="Bebas Neue", font_size=50, color=MEASURE_AMBER)
            n.move_to(LEFT * 2.5 + RIGHT * i * 1.8 + UP * ZONE_UPPER)
            numbers.add(n)

        # Broken halves for snap animation
        left_half, right_half = yardstick(4, MEASURE_AMBER, broken=True)

        # ZONE_LOWER — cage formed from broken pieces
        cage = cage_bars(3.5, 4, 5, CAGE_DARK)
        cage.move_to(UP * ZONE_LOWER)

        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(figure, scale=0.9), FadeIn(ys), run_time=0.5); t += 0.5

        # Numbers float up in ZONE_UPPER
        self.play(
            LaggedStart(*[FadeIn(n, shift=UP * 0.3) for n in numbers], lag_ratio=0.12),
            run_time=0.6,
        )                                                                # t=1.5

        # Numbers turn to ash (fade gray -> fade out)
        self.play(*[n.animate.set_color(ASH_GRAY) for n in numbers], run_time=0.4); t += 0.4
        self.play(FadeOut(numbers, shift=UP * 0.5), run_time=0.4); t += 0.4

        # Yardstick SNAPS — split into two halves
        self.wait(0.5); t += 0.5
        left_half.move_to(ys.get_center() + LEFT * 1.2 + DOWN * 0.2)
        right_half.move_to(ys.get_center() + RIGHT * 1.2 + DOWN * 0.2)
        left_half.rotate(15 * DEGREES)
        right_half.rotate(-15 * DEGREES)
        self.play(
            FadeOut(ys),
            FadeIn(left_half), FadeIn(right_half),
            Flash(ys.get_center(), color=REFUSAL_RED, line_length=0.3, num_lines=8),
            run_time=0.3,
        )                                                                # t=3.1

        # Pieces fall and form cage around figure
        self.wait(0.5); t += 0.5
        self.play(
            FadeOut(left_half, shift=DOWN * 2),
            FadeOut(right_half, shift=DOWN * 2),
            figure.animate.move_to(UP * ZONE_LOWER),
            run_time=0.8,
        )                                                                # t=4.4
        self.play(FadeIn(cage, scale=0.9), run_time=0.5); t += 0.5

        # Camera reveals — figure is inside a cage
        target = getattr(self.__class__, 'DURATION', 8.3)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE MYSTERY (7.0–13.5s)
# Figure in cage looks superior. Others rush past with yardsticks.
# Zones: TITLE (pill), UPPER (freedom label), MID (cage+figure), LOWER (rushers), FOOTER (broken pieces)
# ================================================================
class Scene2_Mystery(Scene):
    DURATION = 7.7
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE — pill
        pill = label_pill("THE REFUSAL", color=GHOST_TEAL)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_MID — caged figure (center)
        cage = cage_bars(3, 4.5, 5, CAGE_DARK)
        cage.move_to(UP * ZONE_MID)
        figure = stick_figure(WHITE_SOFT, 2.0)
        figure.move_to(UP * ZONE_MID)

        # ZONE_UPPER — "FREEDOM" label
        freedom = safe_text("FREEDOM", font="Bebas Neue", font_size=60, color=GHOST_TEAL)
        freedom.move_to(UP * ZONE_UPPER)

        # ZONE_LOWER — rushing figures holding yardsticks
        rushers = VGroup()
        for i in range(6):
            r = stick_figure(MUTED, 1.2)
            ys_small = yardstick(1.5, MEASURE_AMBER)
            ys_small.scale(0.4)
            side = LEFT if i < 3 else RIGHT
            x_off = (i % 3 + 1) * 1.0
            r.move_to(side * (3.5 + x_off * 0.3) + UP * ZONE_LOWER + RIGHT * (i % 3) * 0.3)
            ys_small.next_to(r, RIGHT, buff=0.1)
            rushers.add(VGroup(r, ys_small))

        # ZONE_FOOTER — broken yardstick pieces
        bp1, bp2 = yardstick(2, CAGE_DARK, broken=True)
        bp1.move_to(UP * ZONE_FOOTER + LEFT * 1.5)
        bp2.move_to(UP * ZONE_FOOTER + RIGHT * 1.5)
        bp1.rotate(10 * DEGREES)
        bp2.rotate(-8 * DEGREES)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(cage), FadeIn(figure), run_time=0.5); t += 0.5
        self.play(FadeIn(freedom, scale=1.1), run_time=0.4); t += 0.4

        # Rushers stream past
        self.play(
            LaggedStart(*[FadeIn(r, shift=RIGHT * 0.5) for r in rushers[:3]], lag_ratio=0.1),
            LaggedStart(*[FadeIn(r, shift=LEFT * 0.5) for r in rushers[3:]], lag_ratio=0.1),
            run_time=0.8,
        )                                                                # t=2.0

        # Rushers shift across (motion blur effect)
        self.play(
            *[r.animate.shift(RIGHT * 1.5) for r in rushers[:3]],
            *[r.animate.shift(LEFT * 1.5) for r in rushers[3:]],
            run_time=1.5,
        )                                                                # t=3.5

        # Broken pieces at footer
        self.play(FadeIn(bp1), FadeIn(bp2), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 7.7)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: THE WRONG ANSWER (13.5–20.0s)
# Weight lifts off figure. "NOTHING MATTERS" — the appeal.
# Zones: TITLE (pill), MID (figure), LOWER (crossed yardstick), FOOTER (nothing matters)
# ================================================================
class Scene3_WrongAnswer(Scene):
    DURATION = 7.7
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE — pill
        pill = label_pill("THE APPEAL", color=WHITE_SOFT)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_MID — figure standing tall
        figure = stick_figure(WHITE_SOFT, 2.5)
        figure.move_to(UP * ZONE_MID)

        # Heavy block on shoulders (weight of measurement) — above figure
        block = Rectangle(width=1.5, height=0.8, fill_color=CAGE_DARK,
                          fill_opacity=0.8, stroke_color=MEASURE_AMBER, stroke_width=1.5)
        block.move_to(figure.get_top() + UP * 0.5)
        block_label = safe_text("METRICS", font="Inter", font_size=20, color=MEASURE_AMBER)
        block_label.move_to(block)
        weight = VGroup(block, block_label)

        # ZONE_LOWER — crossed-out yardstick
        ys = yardstick(4, ASH_GRAY)
        ys.move_to(UP * ZONE_LOWER)
        x_line1 = Line(ys.get_corner(UP + LEFT) + LEFT * 0.2 + UP * 0.3,
                        ys.get_corner(DOWN + RIGHT) + RIGHT * 0.2 + DOWN * 0.3,
                        color=REFUSAL_RED, stroke_width=4)
        x_line2 = Line(ys.get_corner(UP + RIGHT) + RIGHT * 0.2 + UP * 0.3,
                        ys.get_corner(DOWN + LEFT) + LEFT * 0.2 + DOWN * 0.3,
                        color=REFUSAL_RED, stroke_width=4)
        crossed_ys = VGroup(ys, x_line1, x_line2)

        # ZONE_FOOTER — "NOTHING MATTERS" text
        nothing = safe_text("NOTHING MATTERS", font="Bebas Neue", font_size=70, color=WHITE_SOFT)
        nothing.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(figure), FadeIn(weight), run_time=0.5); t += 0.5

        # Weight lifts off — floats away
        self.wait(0.7); t += 0.7
        self.play(
            weight.animate.shift(UP * 3).set_opacity(0),
            run_time=1.2,
        )                                                                # t=2.7

        # Figure stands taller
        self.play(figure.animate.scale(1.1), run_time=0.3); t += 0.3

        # Crossed-out yardstick appears in ZONE_LOWER
        self.play(FadeIn(crossed_ys), run_time=0.5); t += 0.5

        # "NOTHING MATTERS" in ZONE_FOOTER
        self.play(FadeIn(nothing, shift=UP * 0.2), run_time=0.5); t += 0.5

        target = getattr(self.__class__, 'DURATION', 7.7)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE CONTRADICTION (20.0–27.0s)
# Ghost yardstick hovers. Figure orbits what they rejected.
# Zones: TITLE (pill), UPPER (freedom label), MID (figure+trophy+orbit), LOWER (ghost ys), FOOTER (broken pieces)
# ================================================================
class Scene4_Contradiction(Scene):
    DURATION = 8.3
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE — pill
        pill = label_pill("THE SHADOW", color=REFUSAL_RED)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER — "FREEDOM" label that transforms
        freedom = safe_text("FREEDOM", font="Bebas Neue", font_size=50, color=GHOST_TEAL)
        freedom.move_to(UP * ZONE_UPPER)
        shadow_label = safe_text("FREEDOM'S SHADOW", font="Bebas Neue", font_size=50,
                                  color=REFUSAL_RED)
        shadow_label.move_to(UP * ZONE_UPPER)

        # ZONE_MID — figure + trophy + orbit
        figure = stick_figure(WHITE_SOFT, 2.0)
        figure.move_to(LEFT * 1.5 + UP * ZONE_MID)

        trophy = trophy_shape(1.5, GOLD)
        trophy.move_to(RIGHT * 2.5 + UP * ZONE_MID)

        orbit = Ellipse(width=5, height=3.5, color=REFUSAL_RED, stroke_width=1.5)
        orbit.set_stroke(opacity=0.4)
        orbit.move_to(trophy)

        # ZONE_LOWER — ghost yardstick hovering
        ghost = ghost_yardstick(5, GHOST_TEAL)
        ghost.move_to(UP * ZONE_LOWER)

        # ZONE_FOOTER — broken pieces
        bp1, bp2 = yardstick(2.5, CAGE_DARK, broken=True)
        bp1.move_to(UP * ZONE_FOOTER + LEFT * 1.5).rotate(12 * DEGREES)
        bp2.move_to(UP * ZONE_FOOTER + RIGHT * 1.5).rotate(-10 * DEGREES)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(figure, scale=0.9), run_time=0.4); t += 0.4
        self.play(FadeIn(freedom), run_time=0.3); t += 0.3

        # Ghost yardstick fades in — the measurement haunts them
        self.wait(0.5); t += 0.5
        self.play(FadeIn(ghost), run_time=0.6); t += 0.6

        # Trophy appears — they're still oriented toward it
        self.play(FadeIn(trophy, scale=0.8), run_time=0.4); t += 0.4

        # Orbit path draws — they're circling what they rejected
        self.play(Create(orbit), run_time=1.0); t += 1.0

        # "FREEDOM" -> "FREEDOM'S SHADOW"
        self.wait(0.5); t += 0.5
        self.play(
            freedom.animate.set_opacity(0),
            FadeIn(shadow_label),
            run_time=0.5,
        )                                                                # t=4.5

        # Broken pieces at footer
        self.play(FadeIn(bp1), FadeIn(bp2), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 8.3)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE PROOF (27.0–34.0s)
# Split screen: pursuer vs refuser, both defined by trophy
# Zones: TITLE (pill), UPPER (labels+figures), MID (trophy), LOWER (pendulum), FOOTER (dotted lines)
# ================================================================
class Scene5_Proof(Scene):
    DURATION = 8.3
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE — pill
        pill = label_pill("THE PROOF", color=GOLD)
        pill.move_to(UP * ZONE_TITLE)

        # Divider — spans UPPER through LOWER
        divider = DashedLine(UP * 5, DOWN * 4, color=MUTED, stroke_width=1,
                             dash_length=0.15).move_to(ORIGIN + UP * 0.5)

        # ZONE_UPPER — pursuer and refuser with labels
        pursue_label = safe_text("PURSUE", font="Inter", font_size=24,
                                  color=MEASURE_AMBER, weight="BOLD")
        pursue_label.move_to(LEFT * 2.5 + UP * (ZONE_UPPER + 1.0))

        pursuer = stick_figure(MEASURE_AMBER, 1.8)
        pursuer.move_to(LEFT * 2.5 + UP * ZONE_UPPER)
        ys_pursue = yardstick(2.5, MEASURE_AMBER)
        ys_pursue.scale(0.6)
        ys_pursue.next_to(pursuer, RIGHT, buff=0.15)

        refuse_label = safe_text("REFUSE", font="Inter", font_size=24,
                                  color=ASH_GRAY, weight="BOLD")
        refuse_label.move_to(RIGHT * 2.5 + UP * (ZONE_UPPER + 1.0))

        refuser = stick_figure(ASH_GRAY, 1.5)
        refuser.move_to(RIGHT * 2.5 + UP * ZONE_UPPER)
        bp1, bp2 = yardstick(2, ASH_GRAY, broken=True)
        bp1.scale(0.5).move_to(RIGHT * 1.8 + UP * (ZONE_UPPER - 1.2)).rotate(20 * DEGREES)
        bp2.scale(0.5).move_to(RIGHT * 3.2 + UP * (ZONE_UPPER - 1.2)).rotate(-15 * DEGREES)

        # ZONE_MID — central trophy both connect to
        trophy = trophy_shape(1.8, GOLD)
        trophy.move_to(UP * ZONE_MID)

        # Dotted lines from figures to trophy
        dotted_l = DashedLine(pursuer.get_bottom(), trophy.get_top() + LEFT * 0.3,
                              color=MEASURE_AMBER, stroke_width=1.5, dash_length=0.15)
        dotted_r = DashedLine(refuser.get_bottom(), trophy.get_top() + RIGHT * 0.3,
                              color=ASH_GRAY, stroke_width=1.5, dash_length=0.15)

        # ZONE_LOWER — pendulum
        pend = pendulum(2.5, 0.25, MUTED)
        pend.move_to(UP * ZONE_LOWER)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(Create(divider), run_time=0.3); t += 0.3

        # Left side — pursuer
        self.play(
            FadeIn(pursuer), FadeIn(ys_pursue), FadeIn(pursue_label),
            run_time=0.4,
        )                                                                # t=1.0

        # Right side — refuser
        self.play(
            FadeIn(refuser), FadeIn(bp1), FadeIn(bp2), FadeIn(refuse_label),
            run_time=0.4,
        )                                                                # t=1.4

        # Trophy appears at ZONE_MID
        self.play(FadeIn(trophy, scale=0.8), run_time=0.4); t += 0.4

        # Dotted lines connect both to trophy
        self.play(Create(dotted_l), Create(dotted_r), run_time=0.6); t += 0.6

        # Pendulum at ZONE_LOWER
        self.play(FadeIn(pend), run_time=0.3); t += 0.3
        # Swing left
        self.play(pend.animate.rotate(15 * DEGREES, about_point=pend[0].get_center()),
                  run_time=0.5)                                          # t=3.2
        # Swing right
        self.play(pend.animate.rotate(-30 * DEGREES, about_point=pend[0].get_center()),
                  run_time=0.5)                                          # t=3.7
        # Swing back center
        self.play(pend.animate.rotate(15 * DEGREES, about_point=pend[0].get_center()),
                  run_time=0.4)                                          # t=4.1

        # Refuser fades — life hollows out
        self.play(refuser.animate.set_opacity(0.25), run_time=1.0); t += 1.0
        target = getattr(self.__class__, 'DURATION', 8.3)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE PUNCH (34.0–40.0s)
# Cage dissolves. Pieces form question mark. Empty field.
# Zones: TITLE (letterbox), MID (cage+figure+question), LOWER (alone figure), FOOTER (empty field)
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 7.1
    def construct(self):
        self.add(gradient_bg("#0A0E18"))
        t = 0

        # Letterbox bars
        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP*(8-bh/2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN*(8-bh/2)),
        )
        self.add(grid_lines(0.02))

        # ZONE_MID — cage around figure
        cage = cage_bars(3, 4, 5, CAGE_DARK)
        cage.move_to(UP * ZONE_MID)
        figure = stick_figure(WHITE_SOFT, 2.0)
        figure.move_to(UP * ZONE_MID)

        # Question mark built from yardstick pieces — appears at ZONE_MID
        q_curve = Arc(radius=0.8, start_angle=30 * DEGREES, angle=270 * DEGREES,
                      stroke_color=MEASURE_AMBER, stroke_width=6)
        q_stem = Line(DOWN * 0.2, DOWN * 0.7, color=MEASURE_AMBER, stroke_width=6)
        q_dot = Dot(radius=0.1, color=MEASURE_AMBER).move_to(DOWN * 1.1)
        question = VGroup(q_curve, q_stem, q_dot)
        question.move_to(UP * ZONE_MID)
        question.set_opacity(0)

        # ZONE_LOWER — alone figure in empty field
        alone_figure = stick_figure(ASH_GRAY, 2.0)
        alone_figure.move_to(UP * ZONE_LOWER)
        alone_figure.set_opacity(0.5)

        # ZONE_FOOTER — source label
        source = safe_text("REACTION IS NOT FREEDOM", font="Inter", font_size=24,
                           color=MUTED)
        source.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(cage), FadeIn(figure), run_time=0.5); t += 0.5

        # Cage dissolves — bars fade away one by one
        self.play(
            LaggedStart(*[FadeOut(bar, shift=UP * 0.3) for bar in cage], lag_ratio=0.08),
            run_time=0.8,
        )                                                                # t=1.3

        # Question mark assembles from where cage was
        question.set_opacity(1)
        self.play(FadeIn(question, scale=0.5), run_time=0.6); t += 0.6

        # Figure + question mark hold
        self.wait(0.6); t += 0.6

        # Figure drifts to ZONE_LOWER — free but empty
        self.play(
            FadeOut(figure),
            FadeOut(question),
            FadeIn(alone_figure),
            FadeIn(source, shift=UP * 0.2),
            run_time=0.8,
        )                                                                # t=3.3

        # Hold on emptiness
        target = getattr(self.__class__, 'DURATION', 7.1)
        self.wait(max(0.1, target - t - 0.8))

        # Fade to black
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5


# ── Infra ─────────────────────────────────────────────────────
SCENES = [Scene1_Hook, Scene2_Mystery, Scene3_WrongAnswer,
          Scene4_Contradiction, Scene5_Proof, Scene6_Punch]

def render_single_scene(idx):
    config.output_file = f"nihilist_trap_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    SCENES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"nihilist_trap_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENES):
        n = f"nihilist_trap_scene_{i+1}"; print(f"  Preview {n}...")
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
        sys.exit(0)
    if "--scene" in sys.argv:
        timings_json = os.environ.get("TKK_SCENE_TIMINGS")
        if timings_json:
            _idx = int(sys.argv[sys.argv.index("--scene")+1])
            SCENES[_idx].DURATION = json.loads(timings_json)[_idx]
        render_single_scene(int(sys.argv[sys.argv.index("--scene")+1])); sys.exit(0)

    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_nihilist_trap.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="nihilist_trap", audio_path=str(audio))
    final = od / "nihilist_trap_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")

    from render_utils import run_post_render_qa
    run_post_render_qa(str(final), scene_count=6)
