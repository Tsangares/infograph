#!/usr/bin/env python3
"""Aral Sea — 'Vanished in a Single Lifetime' (Manim). Visual-first.

6 scenes, ~54.7s (51.7s audio + 3s hold).
Custom domain shapes: lake_silhouette, ship_silhouette, canal_line, cotton_boll.

VTT cues (absolute → relative):
  Scene 1 (0.0–7.4s = 7.40s):
    0.160 (0.16) The Aral Sea was the fourth largest lake on Earth.
    4.280 (4.28) Then it vanished in a single lifetime.
  Scene 2 (7.4–14.2s = 6.80s):
    7.380 (0.0)  Scientists first blamed the climate.
    9.740 (2.34) Drought.
    10.380 (2.98) Evaporation.
    11.420 (4.02) A natural disaster no one could have stopped.
    14.200 (6.80) It was not nature.
  Scene 3 (14.2–24.4s = 10.20s):
    15.820 (1.62) In 1960,
    17.080 (2.88) Soviet engineers diverted the rivers...
    24.400 (10.20) [end]
  Scene 4 (24.4–33.9s = 9.50s):
    24.400 (0.0)  The lake lost 90 percent of its water.
    27.460 (3.06) Fishing towns ended up 150 km from the shore.
    31.540 (7.14) The fish died.
    32.720 (8.32) Then the economy died.
  Scene 5 (33.9–44.0s = 10.10s):
    33.880 (0.0)  An area the size of Ireland.
    35.940 (2.04) Gone.
    36.800 (2.90) The exposed seabed became a toxic desert.
    39.640 (5.74) The dust carries pesticides...
  Scene 6 (44.0–54.7s = 10.70s):
    44.060 (0.06) Ships rust in the desert...
    47.620 (3.62) The Soviets knew it would die.
    49.440 (5.44) They called it a worthwhile sacrifice.
    + 3s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """The Aral Sea was the fourth largest lake on Earth.
Then it vanished in a single lifetime.
Scientists first blamed the climate.
Drought.
Evaporation.
A natural disaster no one could have stopped.
It was not nature.
In 1960,
Soviet engineers diverted the rivers...
The lake lost 90 percent of its water.
Fishing towns ended up 150 km from the shore.
The fish died.
Then the economy died.
An area the size of Ireland.
Gone.
The exposed seabed became a toxic desert.
The dust carries pesticides...
Ships rust in the desert...
The Soviets knew it would die.
They called it a worthwhile sacrifice."""

from manim import (
    Scene, Text, VGroup, Rectangle, RoundedRectangle, Circle,
    Line, Arrow, DashedLine, Dot, Polygon, Ellipse, Square, Arc,
    FadeIn, FadeOut, GrowFromCenter, Write, Create, DrawBorderThenFill,
    AnimationGroup, LaggedStart, Flash, GrowArrow, MoveToTarget,
    config, UP, DOWN, LEFT, RIGHT, ORIGIN,
    WHITE, BLACK, rate_functions, DEGREES, PI,
)
import numpy as np

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.frame_width = 9
config.frame_height = 16
config.background_color = "#080A10"
config.disable_caching = True

# Palette
BG = "#080A10"; GRID = "#1A2030"; SURFACE = "#15192A"
BLUE = "#3B82F6"; BLUE_DIM = "#1E40AF"; BLUE_DARK = "#0F2560"
TAN = "#D4A574"; TAN_DIM = "#A07848"; SAND = "#C4A06A"
RUST = "#8B4513"; RUST_DIM = "#5C2E0D"
DUST = "#8B7355"; DUST_DIM = "#6B5540"
RED = "#E63946"; GOLD = "#FFD700"; GOLD_DIM = "#B8960F"
WHITE_SOFT = "#F0F0F0"; MUTED = "#7B8DA0"; DEAD_GRAY = "#4A5568"
COTTON = "#F5F0E0"

SAFE_W = 8.0
SAFE_TOP = 7.2
SAFE_BOT = -6.4


# ── Core helpers (per PRODUCTION_GUIDE) ──────────────────────

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


# ── Domain shapes (4 required) ───────────────────────────────

def lake_silhouette(scale=1.0, fill_color=BLUE, fill_opacity=0.7):
    """Aral Sea outline — rounded trapezoid shape, recognizable at any size."""
    pts = [
        np.array([-2.5, 2.5, 0]), np.array([-1.5, 3.2, 0]), np.array([0, 3.5, 0]),
        np.array([1.5, 3.2, 0]), np.array([2.5, 2.5, 0]),
        np.array([2.8, 1, 0]), np.array([2.5, -0.5, 0]),
        np.array([2, -2, 0]), np.array([1, -3, 0]),
        np.array([0, -3.2, 0]), np.array([-1.2, -2.8, 0]),
        np.array([-2, -1.5, 0]), np.array([-2.5, 0, 0]),
        np.array([-2.8, 1.5, 0]),
    ]
    scaled = [p * scale for p in pts]
    lake = Polygon(*scaled, fill_color=fill_color, fill_opacity=fill_opacity,
                   stroke_color=BLUE_DIM, stroke_width=2 * scale)
    return lake

def ship_silhouette(width=1.5, color=MUTED, angle=0):
    """Fishing trawler side profile — hull, cabin, mast."""
    w, h = width, width * 0.4
    hull = Polygon(
        np.array([-w/2, 0, 0]), np.array([-w/2.2, -h*0.4, 0]),
        np.array([w/3, -h*0.4, 0]), np.array([w/2, 0, 0]),
        fill_color=color, fill_opacity=1, stroke_color=color, stroke_width=1.5,
    )
    cabin = Rectangle(width=w*0.25, height=h*0.5, fill_color=color, fill_opacity=0.8,
                      stroke_width=0).move_to(hull.get_top() + UP * h * 0.25 + LEFT * w * 0.1)
    mast = Line(np.array([w*0.15, h*0.1, 0]), np.array([w*0.15, h*0.7, 0]),
                color=color, stroke_width=1.5)
    grp = VGroup(hull, cabin, mast)
    if angle: grp.rotate(angle * DEGREES)
    return grp

def canal_line(length=3, color=RED, x=0, y=0, angle=0):
    """Irrigation canal with flow arrows."""
    line = Line(LEFT * length/2, RIGHT * length/2, color=color, stroke_width=3)
    arrows = VGroup()
    for i in range(3):
        pos = LEFT * length/2 + RIGHT * (i + 1) * length / 4
        arr = Arrow(pos + LEFT * 0.15, pos + RIGHT * 0.15, color=color,
                    stroke_width=1.5, buff=0, max_tip_length_to_length_ratio=0.8)
        arr.scale(0.4)
        arrows.add(arr)
    grp = VGroup(line, arrows)
    grp.move_to(np.array([x, y, 0]))
    if angle: grp.rotate(angle * DEGREES)
    return grp

def cotton_boll(x=0, y=0, size=0.4, color=COTTON):
    """Cotton plant icon — fluffy circles + small stem."""
    center = np.array([x, y, 0])
    bolls = VGroup()
    for dx, dy in [(0, 0.12), (-0.1, -0.05), (0.1, -0.05), (0, -0.12), (-0.08, 0.08), (0.08, 0.08)]:
        c = Circle(radius=size*0.28, fill_color=color, fill_opacity=0.85,
                   stroke_width=0).move_to(center + np.array([dx*size*2, dy*size*2, 0]))
        bolls.add(c)
    stem = Line(center + DOWN * size * 0.5, center + DOWN * size * 1.2,
                color="#5A8A3A", stroke_width=2)
    return VGroup(bolls, stem)


# ================================================================
# SCENE 1: THE HOOK (0.0–7.4s)
# Lake full → ships drift → "vanished" → lake DRAINS
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 7.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # Full lake
        lake = lake_silhouette(scale=1.0, fill_color=BLUE, fill_opacity=0.6)
        lake.move_to(UP * 1.5)

        # Ships drifting
        s1 = ship_silhouette(1.0, MUTED)
        s1.move_to(UP * 1.5 + LEFT * 1)
        s2 = ship_silhouette(0.7, MUTED)
        s2.move_to(UP * 2 + RIGHT * 0.8)

        # Wave overlay
        wave = DashedLine(LEFT * 2, RIGHT * 2, color=BLUE, stroke_width=1,
                          dash_length=0.3).move_to(UP * 1.5).set_opacity(0.3)

        # Text: "4TH LARGEST LAKE"
        big = safe_text("4TH LARGEST LAKE", font="Bebas Neue", font_size=70, color=GOLD)
        big.move_to(DOWN * 3)

        # Sand layer (hidden initially)
        sand = Rectangle(width=7, height=5, fill_color=TAN, fill_opacity=0.0,
                         stroke_width=0).move_to(UP * 1.5)

        self.play(FadeIn(lake, scale=0.9), run_time=0.6); t += 0.6
        self.play(FadeIn(s1, shift=RIGHT * 0.3), FadeIn(s2, shift=LEFT * 0.2),
                  run_time=0.5)                                             # t=1.1
        self.add(wave)
        self.play(FadeIn(big, scale=1.1), run_time=0.5); t += 0.5

        # Ships drift slowly
        self.play(s1.animate.shift(RIGHT * 0.5), s2.animate.shift(LEFT * 0.3),
                  run_time=2.0)                                             # t=3.6

        # VTT 4.28: "Then it vanished" — DRAIN the lake
        self.wait(0.38); t += 0.38
        self.play(
            lake.animate.scale(0.2).set_opacity(0.15).shift(DOWN * 1),
            sand.animate.set_opacity(0.5),
            s1.animate.shift(DOWN * 1.5).rotate(-30 * DEGREES).set_color(RUST),
            s2.animate.shift(DOWN * 1).rotate(20 * DEGREES).set_color(RUST),
            wave.animate.set_opacity(0),
            run_time=2.0,
        )                                                                   # t=5.98
        self.play(Flash(lake.get_center(), color=BLUE,
                        line_length=0.3, num_lines=8, run_time=0.3))       # t=6.28
        target = getattr(self.__class__, 'DURATION', 7.0)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 2: THE WRONG ANSWER (7.4–14.2s)
# Sun pulses, heat shimmer, thermometer — "not nature"
# ================================================================
class Scene2_WrongAnswer(Scene):
    DURATION = 6.4
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE WRONG ANSWER", color=RED)
        pill.move_to(UP * SAFE_TOP)

        # Shrunk lake remnant
        lake = lake_silhouette(scale=0.4, fill_color=BLUE_DIM, fill_opacity=0.3)
        lake.move_to(UP * 2)

        # Sun icon
        sun = Circle(radius=1, fill_color=GOLD, fill_opacity=0.3,
                     stroke_color=GOLD, stroke_width=2)
        sun.move_to(UP * 5.5)
        sun_rays = VGroup()
        for i in range(8):
            a = i * PI / 4
            ray = Line(UP * 5.5 + np.array([np.cos(a)*1.2, np.sin(a)*1.2, 0]),
                       UP * 5.5 + np.array([np.cos(a)*1.6, np.sin(a)*1.6, 0]),
                       color=GOLD, stroke_width=2).set_opacity(0.4)
            sun_rays.add(ray)

        # Heat shimmer lines
        shimmers = VGroup()
        for x in [-1.5, 0, 1.5]:
            shimmer = DashedLine(DOWN * 0.5, UP * 1.5, color=RED,
                                 stroke_width=1, dash_length=0.2).move_to(np.array([x, 0, 0]))
            shimmer.set_opacity(0.2)
            shimmers.add(shimmer)

        # Text: "CLIMATE? DROUGHT?"
        q = safe_text("CLIMATE? DROUGHT?", font="Bebas Neue", font_size=60, color=DEAD_GRAY)
        q.move_to(DOWN * 2.5)

        # "NOT NATURE" reveal
        not_nature = safe_text("NOT NATURE.", font="Bebas Neue", font_size=80, color=RED)
        not_nature.move_to(DOWN * 5)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(lake), FadeIn(sun), FadeIn(sun_rays), run_time=0.5); t += 0.5
        self.play(FadeIn(shimmers), run_time=0.3); t += 0.3

        # Sun pulses
        self.play(sun.animate.scale(1.15), run_time=0.3); t += 0.3
        self.play(sun.animate.scale(1/1.15), run_time=0.3); t += 0.3

        self.play(FadeIn(q), run_time=0.4); t += 0.4
        self.play(shimmers.animate.shift(UP * 0.5).set_opacity(0.1), run_time=1.0); t += 1.0

        # Sun pulses again
        self.play(sun.animate.scale(1.1), run_time=0.3); t += 0.3
        self.play(sun.animate.scale(1/1.1), run_time=0.3); t += 0.3

        target = getattr(self.__class__, 'DURATION', 6.4)
        self.wait(max(0.1, target - t - 0.3))

        # VTT 6.80: "It was not nature."
        self.play(FadeIn(not_nature, scale=1.15), run_time=0.4); t += 0.4
        self.play(Flash(not_nature.get_center(), color=RED,
                        line_length=0.3, num_lines=8, run_time=0.2))       # t=6.8


# ================================================================
# SCENE 3: THE TRUTH (14.2–24.4s)
# Rivers fork into canals, cotton blooms, lake fades
# ================================================================
class Scene3_Truth(Scene):
    DURATION = 9.7
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("1960", color=GOLD)
        pill.move_to(UP * SAFE_TOP)

        # Lake (centered)
        lake = lake_silhouette(scale=0.7, fill_color=BLUE, fill_opacity=0.5)
        lake.move_to(UP * 1)

        # Two river lines flowing into lake
        river_l = Line(LEFT * 3.5 + UP * 5, LEFT * 1 + UP * 2.5,
                       color=BLUE, stroke_width=4)
        river_r = Line(RIGHT * 3 + UP * 5.5, RIGHT * 0.5 + UP * 2.5,
                       color=BLUE, stroke_width=4)

        # Canal lines forking off rivers (red)
        canals = VGroup()
        canal_positions = [
            (LEFT * 2.5 + UP * 3.5, -40),
            (LEFT * 1.5 + UP * 3, -60),
            (RIGHT * 2 + UP * 4, 40),
            (RIGHT * 1.2 + UP * 3.5, 55),
        ]
        for pos, angle in canal_positions:
            c = canal_line(2.5, RED, pos[0], pos[1], angle)
            canals.add(c)

        # Cotton bolls at canal ends
        cottons = VGroup()
        cotton_spots = [LEFT*3.5+UP*1.5, LEFT*2.5+DOWN*0.5, RIGHT*3+UP*2, RIGHT*2+UP*0.5,
                        LEFT*1.5+DOWN*2, RIGHT*1.5+DOWN*1.5]
        for pos in cotton_spots:
            cottons.add(cotton_boll(pos[0], pos[1], 0.3))

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(Create(river_l), Create(river_r), run_time=0.5); t += 0.5
        self.play(FadeIn(lake, scale=0.9), run_time=0.5); t += 0.5

        self.wait(1.28); t += 1.28

        # VTT 2.88: "Soviet engineers diverted the rivers"
        # Canals fork off
        self.play(
            LaggedStart(*[Create(c) for c in canals], lag_ratio=0.15),
            run_time=1.2,
        )                                                                   # t=3.78

        # Cotton blooms
        self.play(
            LaggedStart(*[GrowFromCenter(c) for c in cottons], lag_ratio=0.08),
            run_time=0.8,
        )                                                                   # t=4.58

        # Lake fades as water diverts
        self.play(
            lake.animate.set_opacity(0.15).scale(0.6),
            river_l.animate.set_opacity(0.3),
            river_r.animate.set_opacity(0.3),
            run_time=2.0,
        )                                                                   # t=6.58

        target = getattr(self.__class__, 'DURATION', 9.7)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 4: THE COLLAPSE (24.4–33.9s)
# Lake shrinks in 4 hard snaps, ships tip, fish die
# ================================================================
class Scene4_Collapse(Scene):
    DURATION = 9.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE COLLAPSE", color=RED)
        pill.move_to(UP * SAFE_TOP)

        # Lake at 4 stages
        stages = [
            (1.0, 0.5, "1960"),
            (0.7, 0.4, "1980"),
            (0.35, 0.25, "2000"),
            (0.12, 0.15, "2010"),
        ]

        # Ships
        ships = VGroup()
        for i, x in enumerate([-1.5, 0.5, 2]):
            s = ship_silhouette(0.8, MUTED)
            s.move_to(np.array([x, 2, 0]))
            ships.add(s)

        # "−90%" text
        pct = safe_text("−90%", font="Bebas Neue", font_size=100, color=RED)
        pct.move_to(DOWN * 3)

        # Timeline at bottom
        tl = Line(LEFT * 3.5, RIGHT * 3.5, color=MUTED, stroke_width=2).move_to(DOWN * 5.5)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        lake = lake_silhouette(stages[0][0], BLUE, stages[0][1])
        lake.move_to(UP * 1.5)
        self.play(FadeIn(lake), FadeIn(ships), run_time=0.5); t += 0.5

        # Hard snaps through decades
        for i, (sc, op, yr) in enumerate(stages[1:], 1):
            new_lake = lake_silhouette(sc, BLUE if i < 3 else BLUE_DIM, op)
            new_lake.move_to(UP * 1.5)

            yr_text = safe_text(yr, font="Bebas Neue", font_size=36, color=GOLD)
            yr_text.move_to(DOWN * 5.5 + LEFT * 3.5 + RIGHT * i * 2.3)

            self.play(
                lake.animate.become(new_lake),
                FadeIn(yr_text),
                run_time=0.4,
            )
            self.play(Flash(lake.get_center(), color=RED,
                            line_length=0.2, num_lines=4, run_time=0.15))

            if i == 2:  # Ships tip over
                self.play(
                    ships[0].animate.rotate(-40 * DEGREES).set_color(RUST).shift(DOWN * 0.5),
                    ships[1].animate.rotate(30 * DEGREES).set_color(RUST).shift(DOWN * 0.3),
                    ships[2].animate.rotate(-25 * DEGREES).set_color(RUST).shift(DOWN * 0.4),
                    run_time=0.4,
                )

        # VTT ~7.14: "The fish died. Then the economy died."
        self.wait(3.0); t += 3.0
        self.play(FadeIn(pct, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(pct.get_center(), color=RED,
                        line_length=0.4, num_lines=10, run_time=0.3))
        target = getattr(self.__class__, 'DURATION', 9.0)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 5: THE SCALE (33.9–44.0s)
# Before/after split, Ireland comparison, toxic dust
# ================================================================
class Scene5_Scale(Scene):
    DURATION = 9.6
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE SCALE", color=GOLD)
        pill.move_to(UP * SAFE_TOP)

        # Before lake (left)
        lake_before = lake_silhouette(0.4, BLUE, 0.6).move_to(LEFT * 2.2 + UP * 3)
        lbl_before = safe_text("1960", font="Bebas Neue", font_size=36, color=BLUE)
        lbl_before.next_to(lake_before, DOWN, buff=0.2)

        # After lake (right) — mostly sand
        lake_after_outline = lake_silhouette(0.4, TAN, 0.3).move_to(RIGHT * 2.2 + UP * 3)
        tiny_remnant = lake_silhouette(0.06, BLUE, 0.5).move_to(RIGHT * 2.2 + UP * 3.2)
        lbl_after = safe_text("2020", font="Bebas Neue", font_size=36, color=TAN)
        lbl_after.next_to(lake_after_outline, DOWN, buff=0.2)

        # Ireland outline (scale reference — simple ellipse)
        ireland = Ellipse(width=1.5, height=2.2, color=GOLD, stroke_width=2,
                          fill_opacity=0).move_to(UP * 3)
        ire_lbl = safe_text("IRELAND", font="Inter", font_size=22, color=GOLD, weight="BOLD")
        ire_lbl.next_to(ireland, DOWN, buff=0.1)

        # "GONE" text
        gone = safe_text("GONE.", font="Bebas Neue", font_size=90, color=RED)
        gone.move_to(DOWN * 0.5)

        # Wind lines + dust particles
        wind_lines = VGroup()
        particles = VGroup()
        for i in range(4):
            y = DOWN * 2.5 + DOWN * i * 0.6
            wl = Arrow(LEFT * 3.5 + y, RIGHT * 3.5 + y,
                       color=DUST, stroke_width=1.5, buff=0).set_opacity(0.3)
            wind_lines.add(wl)
            for j in range(6):
                p = Dot(LEFT * 3 + RIGHT * j * 1.2 + y + UP * np.random.uniform(-0.2, 0.2),
                        radius=0.04, color=DUST).set_opacity(0.4)
                particles.add(p)

        toxic = safe_text("TOXIC DESERT", font="Bebas Neue", font_size=50, color=DUST)
        toxic.move_to(DOWN * 6)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(lake_before), FadeIn(lbl_before),
                  FadeIn(lake_after_outline), FadeIn(tiny_remnant), FadeIn(lbl_after),
                  run_time=0.6)                                             # t=0.9

        # Ireland comparison
        self.play(FadeIn(ireland), FadeIn(ire_lbl), run_time=0.5); t += 0.5
        self.wait(0.64); t += 0.64

        # "Gone."
        self.play(FadeOut(ireland), FadeOut(ire_lbl), run_time=0.3); t += 0.3
        self.play(FadeIn(gone, scale=1.15), run_time=0.4); t += 0.4
        self.play(Flash(gone.get_center(), color=RED,
                        line_length=0.3, num_lines=8, run_time=0.2))       # t=2.94

        # Toxic dust
        self.wait(2.5); t += 2.5
        self.play(
            LaggedStart(*[GrowArrow(wl) for wl in wind_lines], lag_ratio=0.1),
            run_time=0.8,
        )                                                                   # t=6.24
        self.play(
            LaggedStart(*[FadeIn(p, shift=RIGHT * 0.5) for p in particles], lag_ratio=0.02),
            run_time=0.6,
        )                                                                   # t=6.84
        # Particles drift right
        self.play(
            *[p.animate.shift(RIGHT * 2).set_opacity(0) for p in particles],
            run_time=1.5,
        )                                                                   # t=8.34
        self.play(FadeIn(toxic), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 9.6)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 6: THE PUNCH (44.0–54.7s)
# Single rusted ship in desert. Stillness. Zoom out. Graveyard.
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 10.1
    def construct(self):
        self.add(gradient_bg("#0A0A08"))
        t = 0

        # Letterbox
        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP*(8-bh/2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN*(8-bh/2)),
        )

        # Sand ground plane
        sand_ground = Rectangle(width=10, height=8, fill_color=TAN_DIM, fill_opacity=0.15,
                                stroke_width=0).move_to(UP * 1)
        self.add(sand_ground)

        # Single rusted ship — center frame, tilted
        main_ship = ship_silhouette(2.5, RUST, angle=-15)
        main_ship.move_to(UP * 2)

        # Sparse wind particles
        dust_p = VGroup()
        np.random.seed(42)
        for _ in range(8):
            p = Dot(np.array([np.random.uniform(-4, 4), np.random.uniform(-1, 5), 0]),
                    radius=0.03, color=DUST_DIM).set_opacity(0.2)
            dust_p.add(p)

        # Additional ships (revealed on zoom out)
        graveyard = VGroup()
        ship_configs = [
            (LEFT * 3 + UP * 3.5, -25, 1.5),
            (RIGHT * 3 + UP * 1.5, 20, 1.2),
            (LEFT * 1.5 + DOWN * 1, -10, 1.8),
            (RIGHT * 1.5 + UP * 4, 35, 1.0),
        ]
        for pos, ang, w in ship_configs:
            s = ship_silhouette(w, RUST_DIM, angle=ang)
            s.move_to(pos).set_opacity(0)
            graveyard.add(s)

        # "A WORTHWHILE SACRIFICE."
        sacrifice = safe_text("A WORTHWHILE SACRIFICE.", font="Bebas Neue",
                             font_size=50, color=DEAD_GRAY)
        sacrifice.move_to(DOWN * 5)

        # ── Timing: 10.70s ──
        self.play(FadeIn(main_ship, scale=0.9), run_time=0.8); t += 0.8
        self.add(dust_p)

        # Dust drifts slowly
        self.play(
            *[p.animate.shift(RIGHT * 1) for p in dust_p],
            run_time=2.0,
        )                                                                   # t=2.8

        # VTT 3.62: "The Soviets knew it would die."
        # Slow zoom out reveals graveyard
        self.play(
            *[s.animate.set_opacity(0.5) for s in graveyard],
            main_ship.animate.scale(0.7).shift(UP * 0.5),
            run_time=2.0,
        )                                                                   # t=4.8

        # VTT 5.44: "They called it a worthwhile sacrifice."
        self.wait(0.34); t += 0.34
        self.play(FadeIn(sacrifice, shift=UP * 0.04), run_time=0.8); t += 0.8

        # Hold — stillness is the point
        target = getattr(self.__class__, 'DURATION', 10.1)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1,
                          stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5


# ── Infra ─────────────────────────────────────────────────────
SCENES = [Scene1_Hook, Scene2_WrongAnswer, Scene3_Truth,
          Scene4_Collapse, Scene5_Scale, Scene6_Punch]

def render_single_scene(idx):
    config.output_file = f"aral_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    SCENES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"aral_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENES):
        n = f"aral_scene_{i+1}"; print(f"  Preview {n}...")
        config.output_file = n; config.save_last_frame = True; config.format = "png"
        S().render()
        for p in Path(config.media_dir).rglob(f"{n}*"):
            if p.suffix == ".png":
                dst = d / f"{n}.png"; shutil.copy2(str(p), str(dst))
                print(f"  OK: {dst} ({dst.stat().st_size//1024} KB)"); break
    config.save_last_frame = False; config.format = None
    print(f"\nAll 6 previews → {d}/")

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
    audio = od / "tts_aral_sea.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="aral", audio_path=str(audio))
    final = od / "aral_sea_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")

    from render_utils import run_post_render_qa
    run_post_render_qa(str(final), scene_count=6)

    from render_utils import make_short
    scene_ends = [7.4, 14.2, 24.4, 33.9, 44.0, 54.7]
    short, dur = make_short(str(final), scene_ends)
    print(f"  SHORT: {short} ({Path(short).stat().st_size/1024/1024:.1f} MB, {dur:.1f}s)")
