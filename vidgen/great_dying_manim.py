#!/usr/bin/env python3
"""The Great Dying — The Extinction That Almost Ended Life (Manim).

6 scenes, ~69.5s (66.5s audio + 3s hold).

VTT cues (absolute → relative):
  Scene 1 THE HOOK (0.0–11.5s = 11.50s):
    0.100 (0.10) 252 million years ago, 96 percent of everything alive died.
    4.500 (4.50) Not the dinosaur extinction. That one was minor.
    7.800 (7.80) This was the one that almost ended life itself.
  Scene 2 THE WRONG ANSWER (11.5–23.0s = 11.50s):
    11.600 (0.10) For decades, scientists thought it was slow.
    14.500 (3.00) A gradual climate shift. Maybe a sea level change.
    18.000 (6.50) Something gentle that took millions of years.
  Scene 3 THE SCALE (23.0–35.0s = 12.00s):
    23.100 (0.10) It wasn't gradual. The oceans turned acidic.
    26.500 (3.50) CO2 hit 8 percent of the atmosphere.
    29.000 (6.00) 20 times today's levels.
    31.500 (8.50) Global temperature rose 10 degrees in under 60,000 years.
  Scene 4 THE CAUSE (35.0–46.0s = 11.00s):
    35.100 (0.10) The Siberian Traps.
    36.800 (1.80) The largest volcanic eruption in Earth's history.
    39.500 (4.50) 3 million cubic kilometers of lava.
    42.500 (7.50) It burned through coal seams for a million years straight.
  Scene 5 THE PROOF (46.0–57.0s = 11.00s):
    46.100 (0.10) The mass extinction happened in under 60,000 years.
    49.500 (3.50) Geologically instantaneous.
    51.500 (5.50) The recovery took 10 million years.
    54.500 (8.50) Some ecosystems never came back.
  Scene 6 THE PUNCH (57.0–69.5s = 12.50s):
    57.100 (0.10) The Great Dying was caused by too much CO2.
    60.500 (3.50) We're currently adding CO2 faster than the Siberian Traps did.
    + 3s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """252 million years ago, 96 percent of everything alive died. Not the dinosaurs. This almost ended life itself. Scientists thought it was gradual. It wasn't. The Siberian Traps — largest eruption in Earth's history. Three million cubic kilometers of lava burning through coal for a million years. CO2 hit twenty times today's levels. The extinction took under 60,000 years. Recovery took ten million. We're adding CO2 faster than the Siberian Traps did."""

from manim import (
    Scene, Text, Group, VGroup, Rectangle, RoundedRectangle, Circle,
    Line, Arrow, DashedLine, Dot, Polygon, Ellipse, Square,
    FadeIn, FadeOut, GrowFromCenter, Write, Create, DrawBorderThenFill,
    AnimationGroup, LaggedStart, Flash, GrowArrow,
    config, UP, DOWN, LEFT, RIGHT, ORIGIN, UL, UR, DL, DR,
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

# ── Color Palette ──────────────────────────────────────────────
BG = "#080A10"
SURFACE = "#15192A"
SURFACE2 = "#1A1A26"
GRID = "#1A2030"
LAVA_RED = "#E63B12"
LAVA_ORANGE = "#FF6B1A"
MAGMA_GLOW = "#FF4500"
EARTH_BLUE = "#1A5276"
EARTH_GREEN = "#2D5A27"
EARTH_BROWN = "#6B4226"
CO2_GRAY = "#4A5568"
CO2_TOXIC = "#7FBA3C"
ACID_GREEN = "#88CC22"
OCEAN_BLUE = "#0E4D6B"
OCEAN_ACID = "#3D7A3C"
BONE_WHITE = "#D4C9B0"
DEATH_RED = "#CC2222"
WHITE_SOFT = "#F0F0F0"
MUTED = "#7B8DA0"
DIM = "#404050"
DEAD_GRAY = "#4A5568"
GOLD = "#FFD700"

SAFE_W = 8.0

ZONE_TITLE  = 6.2
ZONE_UPPER  = 3.5
ZONE_MID    = 0.0
ZONE_LOWER  = -3.5
ZONE_FOOTER = -6.0


# ── Core helpers ───────────────────────────────────────────────

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

def label_pill(txt, color=LAVA_RED, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W:
        t.scale(SAFE_W / t.width)
    p = RoundedRectangle(width=t.width+0.5, height=t.height+0.3, corner_radius=0.18,
                         fill_color=bg, fill_opacity=0.95, stroke_color=color, stroke_width=1.5).move_to(t)
    return VGroup(p, t)

def section_div(width=5, color=LAVA_RED):
    l = Line(LEFT*width/2, LEFT*0.12, color=color, stroke_width=1.5)
    r = Line(RIGHT*0.12, RIGHT*width/2, color=color, stroke_width=1.5)
    d = Square(side_length=0.1, color=color, fill_color=color, fill_opacity=1).rotate(45*DEGREES)
    return VGroup(l, d, r)

def star_field(n=25, seed=42):
    np.random.seed(seed)
    stars = VGroup()
    for _ in range(n):
        x = np.random.uniform(-4.5, 4.5)
        y = np.random.uniform(-8, 8)
        r = np.random.uniform(0.015, 0.035)
        op = np.random.uniform(0.15, 0.45)
        stars.add(Dot(point=np.array([x, y, 0]), radius=r, color=WHITE).set_opacity(op))
    return stars


# ── Domain shapes ──────────────────────────────────────────────

def volcano_shape(height=4.0, color=EARTH_BROWN, lava_color=LAVA_RED):
    """Tall volcano with lava eruption and smoke clouds."""
    s = height / 4.0
    body = Polygon(
        np.array([-2.5*s, -1.5*s, 0]), np.array([2.5*s, -1.5*s, 0]),
        np.array([0.8*s, 1.5*s, 0]), np.array([-0.8*s, 1.5*s, 0]),
        fill_color=color, fill_opacity=0.85, stroke_color="#8B6B4A", stroke_width=1.5,
    )
    crater = Ellipse(width=1.6*s, height=0.4*s, fill_color="#2A1A0A", fill_opacity=0.9,
                     stroke_color=lava_color, stroke_width=2).move_to(UP * 1.5*s)
    eruption1 = Polygon(
        np.array([-0.15*s, 1.5*s, 0]), np.array([0.15*s, 1.5*s, 0]),
        np.array([0.05*s, 3.0*s, 0]), np.array([-0.05*s, 2.8*s, 0]),
        fill_color=lava_color, fill_opacity=0.9, stroke_width=0,
    )
    eruption2 = Polygon(
        np.array([0.2*s, 1.5*s, 0]), np.array([0.45*s, 1.5*s, 0]),
        np.array([0.5*s, 2.5*s, 0]), np.array([0.25*s, 2.6*s, 0]),
        fill_color=LAVA_ORANGE, fill_opacity=0.8, stroke_width=0,
    )
    eruption3 = Polygon(
        np.array([-0.4*s, 1.5*s, 0]), np.array([-0.2*s, 1.5*s, 0]),
        np.array([-0.15*s, 2.4*s, 0]), np.array([-0.35*s, 2.3*s, 0]),
        fill_color=LAVA_ORANGE, fill_opacity=0.7, stroke_width=0,
    )
    glow = Ellipse(width=2.0*s, height=0.8*s, fill_color=MAGMA_GLOW, fill_opacity=0.2,
                   stroke_width=0).move_to(UP * 1.8*s)
    smoke1 = Circle(radius=0.5*s, fill_color=CO2_GRAY, fill_opacity=0.3,
                    stroke_width=0).move_to(UP * 3.2*s + LEFT * 0.3*s)
    smoke2 = Circle(radius=0.4*s, fill_color=CO2_GRAY, fill_opacity=0.25,
                    stroke_width=0).move_to(UP * 3.5*s + RIGHT * 0.4*s)
    smoke3 = Circle(radius=0.6*s, fill_color=CO2_GRAY, fill_opacity=0.2,
                    stroke_width=0).move_to(UP * 3.8*s)
    return VGroup(body, crater, eruption1, eruption2, eruption3, glow, smoke1, smoke2, smoke3)

def skull_shape(height=1.5, color=BONE_WHITE):
    """Animal skull — cranium + jaw + eye sockets."""
    s = height / 1.5
    cranium = Ellipse(width=1.0*s, height=0.8*s, fill_color=color, fill_opacity=0.9,
                      stroke_color=color, stroke_width=1.5).move_to(UP * 0.15*s)
    jaw = Polygon(
        np.array([-0.3*s, -0.2*s, 0]), np.array([0.3*s, -0.2*s, 0]),
        np.array([0.2*s, -0.6*s, 0]), np.array([-0.2*s, -0.6*s, 0]),
        fill_color=color, fill_opacity=0.85, stroke_color=color, stroke_width=1,
    )
    eye_l = Circle(radius=0.12*s, fill_color="#1A1A1A", fill_opacity=1,
                   stroke_width=0).move_to(LEFT * 0.2*s + UP * 0.22*s)
    eye_r = Circle(radius=0.12*s, fill_color="#1A1A1A", fill_opacity=1,
                   stroke_width=0).move_to(RIGHT * 0.2*s + UP * 0.22*s)
    nose = Ellipse(width=0.1*s, height=0.08*s, fill_color="#1A1A1A", fill_opacity=1,
                   stroke_width=0).move_to(DOWN * 0.05*s)
    teeth = VGroup()
    for i in range(4):
        t = Rectangle(width=0.08*s, height=0.1*s, fill_color=color, fill_opacity=0.8, stroke_width=0)
        t.move_to(LEFT * 0.15*s + RIGHT * i * 0.1*s + DOWN * 0.35*s)
        teeth.add(t)
    return VGroup(cranium, jaw, eye_l, eye_r, nose, teeth)

def earth_shape(radius=2.0, color=EARTH_BLUE, land_color=EARTH_GREEN):
    """Planet Earth with Pangaea-era continent."""
    ocean = Circle(radius=radius, fill_color=color, fill_opacity=0.9,
                   stroke_color="#2A6A9A", stroke_width=2)
    continent = Polygon(
        np.array([-0.8*radius, 0.3*radius, 0]), np.array([-0.3*radius, 0.7*radius, 0]),
        np.array([0.4*radius, 0.5*radius, 0]), np.array([0.7*radius, 0.1*radius, 0]),
        np.array([0.5*radius, -0.4*radius, 0]), np.array([0.1*radius, -0.6*radius, 0]),
        np.array([-0.5*radius, -0.3*radius, 0]), np.array([-0.7*radius, 0.0, 0]),
        fill_color=land_color, fill_opacity=0.7, stroke_color="#3E7A34", stroke_width=1,
    )
    atmo = Circle(radius=radius*1.08, fill_opacity=0, stroke_color="#4A8AB0",
                  stroke_width=1.5, stroke_opacity=0.3)
    return VGroup(ocean, continent, atmo)

def co2_cloud_shape(width=3.0, color=CO2_GRAY, label_color=CO2_TOXIC):
    """Toxic cloud with CO2 label."""
    s = width / 3.0
    c1 = Circle(radius=0.6*s, fill_color=color, fill_opacity=0.6, stroke_width=0).move_to(LEFT * 0.5*s)
    c2 = Circle(radius=0.8*s, fill_color=color, fill_opacity=0.5, stroke_width=0)
    c3 = Circle(radius=0.55*s, fill_color=color, fill_opacity=0.55, stroke_width=0).move_to(RIGHT * 0.6*s + UP * 0.1*s)
    c4 = Circle(radius=0.45*s, fill_color=color, fill_opacity=0.5, stroke_width=0).move_to(RIGHT * 0.2*s + UP * 0.4*s)
    c5 = Circle(radius=0.5*s, fill_color=color, fill_opacity=0.45, stroke_width=0).move_to(LEFT * 0.3*s + UP * 0.35*s)
    lbl = Text("CO2", font="Bebas Neue", font_size=int(40*s), color=label_color, weight="BOLD")
    lbl.move_to(DOWN * 0.05*s)
    return VGroup(c1, c2, c3, c4, c5, lbl)

def factory_shape(height=3.0, color=DIM, smoke_color=CO2_GRAY):
    """Factory with smokestacks."""
    s = height / 3.0
    building = Rectangle(width=2.5*s, height=1.5*s, fill_color=color, fill_opacity=0.85,
                         stroke_color="#555566", stroke_width=1.5).move_to(DOWN * 0.25*s)
    stacks = VGroup()
    for i in range(3):
        st = Rectangle(width=0.25*s, height=1.2*s, fill_color="#555566", fill_opacity=0.9,
                        stroke_color="#666677", stroke_width=1)
        st.move_to(LEFT * 0.7*s + RIGHT * i * 0.7*s + UP * 1.1*s)
        stacks.add(st)
    smokes = VGroup()
    for i in range(3):
        x = -0.7*s + i * 0.7*s
        smokes.add(Circle(radius=0.2*s, fill_color=smoke_color, fill_opacity=0.35,
                          stroke_width=0).move_to(np.array([x, 1.9*s, 0])))
        smokes.add(Circle(radius=0.3*s, fill_color=smoke_color, fill_opacity=0.25,
                          stroke_width=0).move_to(np.array([x + 0.1*s, 2.3*s, 0])))
    windows = VGroup()
    for i in range(3):
        w = Square(side_length=0.3*s, fill_color=LAVA_ORANGE, fill_opacity=0.5, stroke_width=0)
        w.move_to(LEFT * 0.7*s + RIGHT * i * 0.7*s + DOWN * 0.1*s)
        windows.add(w)
    return VGroup(building, stacks, smokes, windows)

def sprout_shape(height=1.0, color="#44AA22"):
    """Small plant sprout — stem + two leaves."""
    s = height / 1.0
    stem = Line(DOWN * 0.3*s, UP * 0.3*s, color=color, stroke_width=2.5)
    leaf_l = Ellipse(width=0.35*s, height=0.15*s, fill_color=color, fill_opacity=0.8,
                     stroke_width=0).move_to(UP * 0.15*s + LEFT * 0.2*s).rotate(30*DEGREES)
    leaf_r = Ellipse(width=0.35*s, height=0.15*s, fill_color=color, fill_opacity=0.8,
                     stroke_width=0).move_to(UP * 0.25*s + RIGHT * 0.2*s).rotate(-30*DEGREES)
    return VGroup(stem, leaf_l, leaf_r)


# ================================================================
# SCENE 1: THE HOOK (0.0–11.5s = 11.50s)
# Zones: TITLE (pill), UPPER (earth), MID (skulls), LOWER (96%), FOOTER (label+div)
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 11.5
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("252 MILLION YEARS AGO", color=DEATH_RED, fs=24)
        pill.move_to(UP * ZONE_TITLE)

        # Earth at UPPER
        earth = earth_shape(2.0, EARTH_BLUE, EARTH_GREEN)
        earth.move_to(UP * ZONE_UPPER)

        # Skulls multiply across MID zone
        skulls = VGroup()
        skull_positions = [
            LEFT*2.5 + UP*0.5, LEFT*0.8 + UP*0.8, RIGHT*1.0 + UP*0.3,
            RIGHT*2.8 + UP*0.6, LEFT*1.5 + DOWN*0.5, RIGHT*0.2 + DOWN*0.3,
            RIGHT*2.0 + DOWN*0.7, LEFT*3.0 + DOWN*0.2,
        ]
        for pos in skull_positions:
            sk = skull_shape(1.0, BONE_WHITE)
            sk.move_to(pos)
            skulls.add(sk)

        # 96% big at LOWER
        pct = safe_text("96%", font="Bebas Neue", font_size=180, color=DEATH_RED)
        pct.move_to(UP * ZONE_LOWER + UP * 0.7)

        dead_label = safe_text("OF ALL LIFE.", font="Bebas Neue", font_size=55, color=MUTED)
        dead_label.move_to(UP * ZONE_LOWER - UP * 0.8)

        div = section_div(5, DEATH_RED).move_to(UP * ZONE_FOOTER + UP * 0.5)

        ended = safe_text("ALMOST ENDED LIFE.", font="Bebas Neue", font_size=50, color=DEATH_RED)
        ended.move_to(UP * ZONE_TITLE)

        # ── Timing: 11.50s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "252 million years ago, 96% of everything alive died."
        self.play(FadeIn(earth, scale=0.9), run_time=0.7); t += 0.7
        self.wait(1.0); t += 1.0
        self.play(LaggedStart(*[FadeIn(sk, scale=0.8) for sk in skulls[:4]],
                              lag_ratio=0.1), run_time=0.8)                # t=2.8
        self.play(LaggedStart(*[FadeIn(sk, scale=0.8) for sk in skulls[4:]],
                              lag_ratio=0.1), run_time=0.7)                # t=3.5

        self.play(FadeIn(pct, scale=1.3), run_time=0.7); t += 0.7
        self.play(Flash(pct.get_center(), color=DEATH_RED,
                        line_length=0.6, num_lines=12, run_time=0.4))      # t=4.6

        # VTT 4.50: "Not the dinosaur extinction."
        self.play(FadeIn(dead_label, shift=UP*0.1), run_time=0.4); t += 0.4
        self.wait(2.5); t += 2.5

        # VTT 7.80: "This was the one that almost ended life itself."
        self.play(FadeOut(pill), run_time=0.3); t += 0.3
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(ended, scale=1.05), run_time=0.5); t += 0.5
        self.play(Flash(ended.get_center(), color=DEATH_RED,
                        line_length=0.3, num_lines=8, run_time=0.3))       # t=8.9
        # Earth turns red — life is dying
        self.play(earth.animate.set_color(DEATH_RED).set_opacity(0.4),
                  run_time=1.0)                                             # t=9.9
        # Skulls pulse red
        self.play(*[sk.animate.set_color(DEATH_RED).set_opacity(0.6)
                    for sk in skulls], run_time=0.5)                       # t=10.4
        target = getattr(self.__class__, 'DURATION', 11.5)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE WRONG ANSWER (11.5–23.0s = 11.50s)
# Zones: TITLE (pill), UPPER (waves), MID (hourglass), LOWER (gradual?), FOOTER (div)
# ================================================================
class Scene2_WrongAnswer(Scene):
    DURATION = 11.5
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE WRONG ANSWER", color=MUTED, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # Gentle wavy lines at UPPER
        waves = VGroup()
        for i in range(5):
            pts = []
            y_base = ZONE_UPPER + 1.0 - i * 0.6
            for j in range(20):
                x = -4.0 + j * 0.42
                y = y_base + 0.15 * np.sin(j * 0.5 + i * 0.8)
                pts.append(np.array([x, y, 0]))
            for k in range(len(pts) - 1):
                seg = Line(pts[k], pts[k+1], color=OCEAN_BLUE, stroke_width=1.5)
                seg.set_opacity(0.4 - i * 0.05)
                waves.add(seg)

        # Hourglass at MID
        hour_top = Polygon(
            np.array([-0.6, 0.8, 0]), np.array([0.6, 0.8, 0]), np.array([0, 0, 0]),
            fill_color=DIM, fill_opacity=0.7, stroke_color=MUTED, stroke_width=1.5,
        )
        hour_bot = Polygon(
            np.array([-0.6, -0.8, 0]), np.array([0.6, -0.8, 0]), np.array([0, 0, 0]),
            fill_color=DIM, fill_opacity=0.7, stroke_color=MUTED, stroke_width=1.5,
        )
        sand = Polygon(
            np.array([-0.3, -0.8, 0]), np.array([0.3, -0.8, 0]), np.array([0, -0.4, 0]),
            fill_color=GOLD, fill_opacity=0.5, stroke_width=0,
        )
        hourglass = VGroup(hour_top, hour_bot, sand).scale(1.5).move_to(UP * ZONE_MID)

        gradual = safe_text("GRADUAL?", font="Bebas Neue", font_size=100, color=MUTED)
        gradual.move_to(UP * ZONE_LOWER + UP * 1.0)

        millions = safe_text("MILLIONS OF YEARS?", font="Bebas Neue", font_size=50, color=DIM)
        millions.move_to(UP * ZONE_LOWER - UP * 0.5)

        # Big red X slash
        x_line1 = Line(LEFT*2.5 + UP*2, RIGHT*2.5 + DOWN*2, color=DEATH_RED, stroke_width=8)
        x_line2 = Line(RIGHT*2.5 + UP*2, LEFT*2.5 + DOWN*2, color=DEATH_RED, stroke_width=8)

        wrong = safe_text("WRONG.", font="Bebas Neue", font_size=80, color=DEATH_RED)
        wrong.move_to(UP * ZONE_TITLE)

        div = section_div(5, DEATH_RED).move_to(UP * ZONE_FOOTER)

        # ── Timing: 11.50s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "For decades, scientists thought it was slow."
        self.play(FadeIn(waves), run_time=0.8); t += 0.8
        self.play(GrowFromCenter(hourglass), run_time=0.7); t += 0.7
        self.wait(1.2); t += 1.2

        # VTT 3.00: "A gradual climate shift."
        self.play(FadeIn(gradual, scale=1.05), run_time=0.5); t += 0.5
        self.wait(2.7); t += 2.7

        # VTT 6.50: "Something gentle that took millions of years."
        self.play(FadeIn(millions, shift=UP*0.1), run_time=0.5); t += 0.5
        self.play(Create(div), run_time=0.3); t += 0.3
        self.wait(1.2); t += 1.2

        # X slash through the whole thing
        self.play(FadeOut(pill), run_time=0.3); t += 0.3
        self.play(Create(x_line1), run_time=0.3); t += 0.3
        self.play(Create(x_line2), run_time=0.3); t += 0.3
        self.play(FadeIn(wrong, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(wrong.get_center(), color=DEATH_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=9.9
        # Hourglass shatters red
        self.play(hourglass.animate.set_color(DEATH_RED).set_opacity(0.3),
                  run_time=0.3)                                             # t=10.2
        target = getattr(self.__class__, 'DURATION', 11.5)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: THE SCALE (23.0–35.0s = 12.00s)
# Zones: TITLE (pill), UPPER (co2 cloud), MID (therm+stats), LOWER (20x), FOOTER (acid ocean)
# ================================================================
class Scene3_Scale(Scene):
    DURATION = 12.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE SCALE", color=LAVA_RED, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # CO2 cloud at UPPER
        cloud = co2_cloud_shape(4.0, CO2_GRAY, CO2_TOXIC)
        cloud.move_to(UP * ZONE_UPPER)

        # Thermometer at MID left
        therm_bg = RoundedRectangle(width=0.8, height=5, corner_radius=0.3,
                                     fill_color="#1A1A22", fill_opacity=0.9,
                                     stroke_color=MUTED, stroke_width=1.5).move_to(LEFT * 2.5 + UP * ZONE_MID)
        therm_fill = RoundedRectangle(width=0.6, height=0.5, corner_radius=0.2,
                                       fill_color=LAVA_RED, fill_opacity=0.9,
                                       stroke_width=0).move_to(LEFT * 2.5 + DOWN * 2.0)
        therm_bulb = Circle(radius=0.35, fill_color=LAVA_RED, fill_opacity=0.9,
                            stroke_width=0).move_to(LEFT * 2.5 + DOWN * 2.6)
        ticks = VGroup()
        for i in range(6):
            y = -2.0 + i * 0.8
            ticks.add(Line(LEFT * 2.1, LEFT * 1.9, color=MUTED, stroke_width=1).move_to(UP * y))

        co2_text = safe_text("8% CO2", font="Bebas Neue", font_size=70, color=CO2_TOXIC)
        co2_text.move_to(RIGHT * 1.5 + UP * 1.0)

        temp_text = safe_text("+10\u00b0C", font="Bebas Neue", font_size=80, color=LAVA_RED)
        temp_text.move_to(RIGHT * 1.5 + DOWN * 0.5)

        # 20x TODAY at LOWER
        twenty_x = safe_text("20x TODAY", font="Bebas Neue", font_size=110, color=DEATH_RED)
        twenty_x.move_to(UP * ZONE_LOWER + UP * 0.7)

        time_label = safe_text("IN 60,000 YEARS", font="Bebas Neue", font_size=45, color=MUTED)
        time_label.move_to(UP * ZONE_LOWER - UP * 0.5)

        # Acid ocean at FOOTER
        ocean_pts = []
        for i in range(30):
            x = -4.5 + i * 0.31
            y = ZONE_FOOTER + 0.5 + 0.2 * np.sin(i * 0.5)
            ocean_pts.append(np.array([x, y, 0]))
        ocean_pts.append(np.array([4.5, -7, 0]))
        ocean_pts.append(np.array([-4.5, -7, 0]))
        ocean = Polygon(*ocean_pts, fill_color=OCEAN_ACID, fill_opacity=0.4,
                        stroke_color=ACID_GREEN, stroke_width=1.5)

        acid_label = safe_text("ACIDIC OCEANS", font="Inter", font_size=24,
                               color=ACID_GREEN, weight="BOLD")
        acid_label.move_to(UP * ZONE_FOOTER - UP * 0.3)

        # ── Timing: 12.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "It wasn't gradual. The oceans turned acidic."
        self.play(FadeIn(ocean), run_time=0.6); t += 0.6
        self.play(FadeIn(acid_label, shift=UP*0.05), run_time=0.3); t += 0.3
        self.wait(2.0); t += 2.0

        # VTT 3.50: "CO2 hit 8 percent of the atmosphere."
        self.play(FadeIn(cloud, scale=0.5), run_time=0.8); t += 0.8
        self.play(FadeIn(co2_text, scale=1.1), run_time=0.5); t += 0.5
        # Cloud drifts and expands
        self.play(cloud.animate.shift(RIGHT * 0.3).scale(1.1), run_time=1.2); t += 1.2

        # VTT 6.00: "20 times today's levels."
        self.play(FadeIn(twenty_x, scale=1.3), run_time=0.6); t += 0.6
        self.play(Flash(twenty_x.get_center(), color=DEATH_RED,
                        line_length=0.5, num_lines=10, run_time=0.4))      # t=6.7
        self.wait(1.5); t += 1.5

        # VTT 8.50: "Global temperature rose 10 degrees"
        self.play(FadeIn(therm_bg), FadeIn(therm_bulb), FadeIn(ticks),
                  run_time=0.4)                                             # t=8.6
        therm_fill_full = RoundedRectangle(width=0.6, height=4.0, corner_radius=0.2,
                                            fill_color=LAVA_RED, fill_opacity=0.9,
                                            stroke_width=0).move_to(LEFT * 2.5 + DOWN * 0.3)
        self.play(FadeIn(therm_fill), run_time=0.1); t += 0.1
        self.play(therm_fill.animate.become(therm_fill_full), run_time=0.8); t += 0.8
        self.play(FadeIn(temp_text, scale=1.1), run_time=0.5); t += 0.5
        self.play(FadeIn(time_label, shift=UP*0.1), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 12.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE CAUSE (35.0–46.0s = 11.00s)
# Zones: TITLE (pill), UPPER+MID (volcano), LOWER (stats), FOOTER (div)
# ================================================================
class Scene4_Cause(Scene):
    DURATION = 11.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE CAUSE", color=LAVA_ORANGE, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # Large volcano centered UPPER+MID
        volc = volcano_shape(5.0, EARTH_BROWN, LAVA_RED)
        volc.move_to(UP * 1.0)

        # Lava flow spreading down into LOWER
        lava_flow = VGroup()
        flow_pts = [
            [np.array([-1.0, -1.5, 0]), np.array([-2.5, -3.5, 0]),
             np.array([-1.5, -3.8, 0]), np.array([-0.5, -1.8, 0])],
            [np.array([-0.3, -1.5, 0]), np.array([-0.8, -4.0, 0]),
             np.array([0.8, -4.0, 0]), np.array([0.3, -1.5, 0])],
            [np.array([0.5, -1.8, 0]), np.array([1.5, -3.8, 0]),
             np.array([2.5, -3.5, 0]), np.array([1.0, -1.5, 0])],
        ]
        for pts in flow_pts:
            f = Polygon(*pts, fill_color=LAVA_RED, fill_opacity=0.5,
                        stroke_color=LAVA_ORANGE, stroke_width=1)
            lava_flow.add(f)

        volc_glow = Circle(radius=3.5, fill_color=MAGMA_GLOW, fill_opacity=0.06,
                           stroke_width=0).move_to(UP * 1.0)

        km3 = safe_text("3 MILLION KM\u00b3", font="Bebas Neue", font_size=80, color=LAVA_ORANGE)
        km3.move_to(UP * ZONE_LOWER + UP * 0.5)

        lava_label = safe_text("OF LAVA", font="Bebas Neue", font_size=50, color=MUTED)
        lava_label.move_to(UP * ZONE_LOWER - UP * 0.5)

        div = section_div(5, LAVA_ORANGE).move_to(UP * ZONE_FOOTER + UP * 0.5)

        million_yr = safe_text("A MILLION YEARS.", font="Bebas Neue", font_size=50, color=LAVA_RED)
        million_yr.move_to(UP * ZONE_TITLE)

        # ── Timing: 11.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "The Siberian Traps."
        self.add(volc_glow)
        self.play(GrowFromCenter(volc), run_time=1.0); t += 1.0
        self.wait(0.5); t += 0.5

        # VTT 1.80: "The largest volcanic eruption in Earth's history."
        self.play(Flash(volc.get_top(), color=LAVA_RED,
                        line_length=0.6, num_lines=12, run_time=0.4))      # t=2.2
        # Volcano pulses with glow
        self.play(volc_glow.animate.scale(1.3).set_opacity(0.12),
                  run_time=0.8)                                             # t=3.0
        self.play(volc_glow.animate.scale(1/1.3).set_opacity(0.06),
                  run_time=0.8)                                             # t=3.8
        self.wait(0.4); t += 0.4

        # VTT 4.50: "3 million cubic kilometers of lava."
        self.play(LaggedStart(*[FadeIn(f, scale=0.9) for f in lava_flow],
                              lag_ratio=0.15), run_time=0.8)               # t=5.0
        self.play(FadeIn(km3, scale=1.2), run_time=0.6); t += 0.6
        self.play(Flash(km3.get_center(), color=LAVA_ORANGE,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=5.9
        self.play(FadeIn(lava_label, shift=UP*0.1), run_time=0.4); t += 0.4
        self.wait(1.0); t += 1.0

        # VTT 7.50: "It burned through coal seams for a million years straight."
        self.play(FadeOut(pill), run_time=0.3); t += 0.3
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(million_yr, scale=1.05), run_time=0.5); t += 0.5
        self.play(Flash(million_yr.get_center(), color=LAVA_RED,
                        line_length=0.3, num_lines=6, run_time=0.3))       # t=8.7
        # Lava flow intensifies
        self.play(*[f.animate.set_opacity(0.8).set_color(LAVA_ORANGE)
                    for f in lava_flow], run_time=0.5)                     # t=9.2
        target = getattr(self.__class__, 'DURATION', 11.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE PROOF (46.0–57.0s = 11.00s)
# Zones: TITLE (pill), UPPER (skull+ext bar), MID (instant), LOWER (rec bar), FOOTER (sprout+div)
# ================================================================
class Scene5_Proof(Scene):
    DURATION = 11.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE PROOF", color=DEATH_RED, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # Timeline bar from UPPER to LOWER — centered at x=-1
        tl = Line(UP * 5.0, DOWN * 5.5, color=MUTED, stroke_width=3)
        tl.move_to(LEFT * 1.0)

        # Skull at top of timeline
        sk = skull_shape(1.5, BONE_WHITE)
        sk.move_to(LEFT * 1.0 + UP * ZONE_UPPER + UP * 1.0)

        # Extinction bracket — short red
        ext_bar = Line(LEFT * 0.6 + UP * 5.0, LEFT * 0.6 + UP * 3.5,
                       color=DEATH_RED, stroke_width=6)
        ext_label = safe_text("60,000 YRS", font="Bebas Neue", font_size=45, color=DEATH_RED)
        ext_label.move_to(RIGHT * 2.0 + UP * ZONE_UPPER + UP * 0.5)

        instant = safe_text("INSTANT.", font="Bebas Neue", font_size=70, color=DEATH_RED)
        instant.move_to(RIGHT * 2.2 + UP * ZONE_UPPER - UP * 0.8)

        # Recovery bracket — long green
        rec_bar = Line(LEFT * 0.6 + UP * 3.5, LEFT * 0.6 + DOWN * 5.0,
                       color=EARTH_GREEN, stroke_width=6)
        rec_label = safe_text("10 MILLION YRS", font="Bebas Neue", font_size=45, color=EARTH_GREEN)
        rec_label.move_to(RIGHT * 2.0 + UP * ZONE_MID)

        # Sprout at bottom of timeline
        sp = sprout_shape(1.5, "#44AA22")
        sp.move_to(LEFT * 1.0 + UP * ZONE_FOOTER + UP * 0.5)

        div = section_div(5, DEATH_RED).move_to(UP * ZONE_FOOTER - UP * 0.3)

        never = safe_text("NEVER CAME BACK.", font="Bebas Neue", font_size=55, color=DEATH_RED)
        never.move_to(UP * ZONE_TITLE)

        # ── Timing: 11.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "The mass extinction happened in under 60,000 years."
        self.play(Create(tl), run_time=0.6); t += 0.6
        self.play(GrowFromCenter(sk), run_time=0.5); t += 0.5
        self.play(Create(ext_bar), run_time=0.5); t += 0.5
        self.play(FadeIn(ext_label, shift=RIGHT*0.1), run_time=0.4); t += 0.4
        self.wait(0.9); t += 0.9

        # VTT 3.50: "Geologically instantaneous."
        self.play(FadeIn(instant, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(instant.get_center(), color=DEATH_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=4.0
        # Skull shakes to emphasize violence
        self.play(sk.animate.shift(RIGHT*0.1), run_time=0.08); t += 0.08
        self.play(sk.animate.shift(LEFT*0.2), run_time=0.08); t += 0.08
        self.play(sk.animate.shift(RIGHT*0.1), run_time=0.08); t += 0.08
        self.wait(0.96); t += 0.96

        # VTT 5.50: "The recovery took 10 million years."
        self.play(Create(rec_bar), run_time=1.0); t += 1.0
        self.play(FadeIn(rec_label, shift=RIGHT*0.1), run_time=0.4); t += 0.4
        self.play(GrowFromCenter(sp), run_time=0.5); t += 0.5
        self.wait(1.2); t += 1.2

        # VTT 8.50: "Some ecosystems never came back."
        self.play(FadeOut(pill), run_time=0.3); t += 0.3
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(never, scale=1.05), run_time=0.5); t += 0.5
        self.play(Flash(never.get_center(), color=DEATH_RED,
                        line_length=0.3, num_lines=6, run_time=0.3))       # t=9.7
        # Sprout wilts — fades to gray
        self.play(sp.animate.set_color(DEAD_GRAY).set_opacity(0.3),
                  run_time=0.5)                                             # t=10.2
        target = getattr(self.__class__, 'DURATION', 11.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE PUNCH (57.0–69.5s = 12.50s)
# Zones: TITLE (ghost), UPPER (factory), MID (co2 cloud), LOWER (faster than), FOOTER (div)
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 12.5
    def construct(self):
        self.add(gradient_bg("#050508"), grid_lines(0.02))
        t = 0

        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP * (8 - bh/2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN * (8 - bh/2)),
        )

        # Ghost volcano — subtle background texture
        ghost = volcano_shape(6, EARTH_BROWN, LAVA_RED)
        ghost.move_to(DOWN * 1)
        ghost.set_opacity(0.04)
        self.add(ghost)

        # Factory at UPPER
        fact = factory_shape(3.0, DIM, CO2_GRAY)
        fact.move_to(UP * ZONE_UPPER - UP * 0.5)

        # CO2 cloud at MID — grows menacingly
        cloud = co2_cloud_shape(5.0, CO2_GRAY, CO2_TOXIC)
        cloud.move_to(UP * ZONE_MID)

        div1 = section_div(4, DEATH_RED).move_to(UP * ZONE_LOWER + UP * 1.5)

        faster = safe_text("FASTER THAN", font="Bebas Neue", font_size=80, color=WHITE_SOFT)
        faster.move_to(UP * ZONE_LOWER + UP * 0.5)
        traps = safe_text("THE SIBERIAN TRAPS.", font="Bebas Neue", font_size=70, color=DEATH_RED)
        traps.move_to(UP * ZONE_LOWER - UP * 0.8)

        div2 = section_div(3, MUTED).move_to(UP * ZONE_FOOTER)

        # ── Timing: 12.50s ──
        # VTT 0.10: "The Great Dying was caused by too much CO2."
        self.play(FadeIn(fact, shift=DOWN*0.2), run_time=0.7); t += 0.7
        self.play(FadeIn(cloud, scale=0.5), run_time=0.8); t += 0.8
        # Factory smoke drifts up
        self.play(fact.animate.shift(UP * 0.15), run_time=0.8); t += 0.8
        self.wait(0.9); t += 0.9

        # VTT 3.50: "We're currently adding CO2 faster"
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(faster, shift=UP*0.08), run_time=0.6); t += 0.6
        self.play(FadeIn(traps, scale=1.1), run_time=0.7); t += 0.7
        self.play(Flash(traps.get_center(), color=DEATH_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=5.1
        self.play(Create(div2), run_time=0.3); t += 0.3

        # Cloud expands ominously during hold
        self.play(cloud.animate.scale(1.2).set_opacity(0.7), run_time=2.0); t += 2.0
        self.wait(1.6); t += 1.6

        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5
        target = getattr(self.__class__, 'DURATION', 12.5)
        self.wait(max(0.1, target - t - 0.8))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ── Infra ─────────────────────────────────────────────────────
def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_WrongAnswer, Scene3_Scale,
          Scene4_Cause, Scene5_Proof, Scene6_Punch]
    config.output_file = f"great_dying_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"great_dying_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

if __name__ == "__main__":
    import time, gc
    od = Path(__file__).parent
    if "--scene" in sys.argv:
        timings_json = os.environ.get("TKK_SCENE_TIMINGS")
        if timings_json:
            _idx = int(sys.argv[sys.argv.index("--scene")+1])
            _classes = sorted([v for k,v in globals().items() if k.startswith("Scene") and len(k) > 5 and k[5].isdigit() and isinstance(v, type)], key=lambda c: c.__name__); _classes[_idx].DURATION = json.loads(timings_json)[_idx]
        render_single_scene(int(sys.argv[sys.argv.index("--scene")+1])); sys.exit(0)

    names = ["Scene1_Hook","Scene2_WrongAnswer","Scene3_Scale",
             "Scene4_Cause","Scene5_Proof","Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_great_dying.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="great_dying", audio_path=str(audio))
    final = od / "great_dying_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
