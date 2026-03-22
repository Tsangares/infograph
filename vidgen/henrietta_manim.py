#!/usr/bin/env python3
"""Henrietta Lacks — The Cells That Changed Medicine (Manim).

6 scenes, ~42.8s (39.8s audio + 3s hold).

VTT cues (absolute → relative):
  Scene 1 THE HOOK (0.0–7.0s = 7.00s):
    0.100 (0.10) Henrietta Lacks's cells saved millions of lives.
    4.500 (4.50) She never knew.
  Scene 2 THE TAKING (7.0–14.0s = 7.00s):
    7.100 (0.10) In 1951, doctors at Johns Hopkins took cells from her tumor.
    10.500 (3.50) Without her knowledge.
    12.000 (5.00) Without her consent.
  Scene 3 THE MIRACLE (14.0–21.0s = 7.00s):
    14.100 (0.10) Her cells never stopped dividing.
    16.500 (2.50) Scientists called them HeLa.
    18.500 (4.50) They became the most important cells in medical history.
  Scene 4 THE SCALE (21.0–28.0s = 7.00s):
    21.100 (0.10) HeLa cells helped develop the polio vaccine.
    23.000 (2.00) Gene mapping. Cancer treatments. COVID vaccines.
    26.000 (5.00) They've been to space.
  Scene 5 THE INJUSTICE (28.0–35.0s = 7.00s):
    28.100 (0.10) Companies made billions from her cells.
    30.500 (2.50) Her family couldn't afford health insurance.
    33.000 (5.00) They didn't even know the cells existed until 1975.
  Scene 6 THE PUNCH (35.0–42.8s = 7.80s):
    35.100 (0.10) Her body is in every lab on Earth.
    38.000 (3.00) Her name was almost erased from all of them.
    + 3s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """Henrietta Lacks's cells saved millions of lives.
She never knew.
In 1951, doctors at Johns Hopkins took cells from her tumor.
Without her knowledge.
Without her consent.
Her cells never stopped dividing.
Scientists called them HeLa.
They became the most important cells in medical history.
HeLa cells helped develop the polio vaccine.
Gene mapping. Cancer treatments. COVID vaccines.
They've been to space.
Companies made billions from her cells.
Her family couldn't afford health insurance.
They didn't even know the cells existed until 1975.
Her body is in every lab on Earth.
Her name was almost erased from all of them."""

from manim import (
    Scene, Text, VGroup, Rectangle, RoundedRectangle, Circle,
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
config.background_color = "#0A0A0A"
config.disable_caching = True

# ── Color Palette ──────────────────────────────────────────────
BG = "#0A0A0A"; SURFACE = "#12121C"; SURFACE2 = "#1A1A26"
BORDER = "#2A2A3A"; GRID = "#14141C"
CELL_PINK = "#D45B90"; CELL_MAGENTA = "#AA2266"; CELL_GLOW = "#FF69B4"
NUCLEUS_PURPLE = "#6A1B6A"; MEMBRANE = "#CC4488"
MEDICAL_TEAL = "#1A8A8A"; MEDICAL_GREEN = "#2D7A2D"
HOSPITAL_BLUE = "#2A5A8C"; SYRINGE_GRAY = "#A0A0B0"
MONEY_GREEN = "#44AA44"; DOLLAR_GREEN = "#228B22"
CRISIS_RED = "#CC2222"; DEATH_RED = "#FF3333"
HELA_GOLD = "#FFD700"; WARM_GOLD = "#C9A84C"
WHITE_SOFT = "#F0F0F0"; MUTED = "#7B8DA0"; DIM = "#404050"
DEAD_GRAY = "#4A5568"
SAFE_W = 8.0

ZONE_TITLE  = 6.2
ZONE_UPPER  = 3.5
ZONE_MID    = 0.0
ZONE_LOWER  = -3.5
ZONE_FOOTER = -6.0


# ── Core helpers ───────────────────────────────────────────────

def gradient_bg(c=BG, g="#0A0812"):
    bg = Rectangle(width=12, height=20, fill_color=c, fill_opacity=1, stroke_width=0)
    glow = Circle(radius=5, fill_color=g, fill_opacity=0.10, stroke_width=0).move_to(UP * 2)
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

def star_field(n=25, seed=42):
    np.random.seed(seed)
    stars = VGroup()
    for _ in range(n):
        x = np.random.uniform(-4.5, 4.5); y = np.random.uniform(-8, 8)
        r = np.random.uniform(0.015, 0.035); op = np.random.uniform(0.15, 0.45)
        stars.add(Dot(point=np.array([x, y, 0]), radius=r, color=WHITE).set_opacity(op))
    return stars

def section_div(width=5, color=CELL_PINK):
    l = Line(LEFT*width/2, LEFT*0.12, color=color, stroke_width=1.5)
    r = Line(RIGHT*0.12, RIGHT*width/2, color=color, stroke_width=1.5)
    d = Square(side_length=0.1, color=color, fill_color=color, fill_opacity=1).rotate(45*DEGREES)
    return VGroup(l, d, r)

def label_pill(txt, color=CELL_PINK, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    p = RoundedRectangle(width=t.width+0.5, height=t.height+0.3, corner_radius=0.18,
                         fill_color=bg, fill_opacity=0.95, stroke_color=color, stroke_width=1.5).move_to(t)
    return VGroup(p, t)

def safe_text(content, **kwargs):
    t = Text(content, **kwargs)
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    return t


# ── Domain shapes ──────────────────────────────────────────────

def cell_shape(radius=1.0, color=CELL_PINK, nucleus_color=NUCLEUS_PURPLE):
    """Circular cell with membrane, cytoplasm, nucleus."""
    s = radius
    membrane = Circle(radius=1.0*s, fill_color=color, fill_opacity=0.25,
                      stroke_color=MEMBRANE, stroke_width=2.5)
    cytoplasm = Circle(radius=0.85*s, fill_color=color, fill_opacity=0.12, stroke_width=0)
    nucleus = Circle(radius=0.3*s, fill_color=nucleus_color, fill_opacity=0.85,
                     stroke_color=color, stroke_width=1.5)
    dots = VGroup()
    np.random.seed(77)
    for _ in range(5):
        a = np.random.uniform(0, 2*PI); r = np.random.uniform(0.4, 0.75)*s
        dots.add(Dot(np.array([np.cos(a)*r, np.sin(a)*r, 0]), radius=0.04*s, color=color).set_opacity(0.5))
    glow = Circle(radius=1.15*s, fill_color=CELL_GLOW, fill_opacity=0.06, stroke_width=0)
    return VGroup(glow, membrane, cytoplasm, nucleus, dots)

def microscope_shape(height=3.0, color=SYRINGE_GRAY):
    """Lab microscope silhouette."""
    s = height / 3.0
    base = Rectangle(width=1.5*s, height=0.25*s, fill_color=color, fill_opacity=0.8,
                     stroke_color=DIM, stroke_width=1).move_to(DOWN * 1.2*s)
    arm = Rectangle(width=0.3*s, height=2.0*s, fill_color=color, fill_opacity=0.75,
                    stroke_color=DIM, stroke_width=1).move_to(LEFT * 0.3*s + UP * 0.1*s)
    eyepiece = Polygon(
        np.array([-0.45*s, 1.1*s, 0]), np.array([-0.15*s, 1.1*s, 0]),
        np.array([0.1*s, 1.4*s, 0]), np.array([-0.2*s, 1.4*s, 0]),
        fill_color=color, fill_opacity=0.8, stroke_color=DIM, stroke_width=1,
    )
    objective = Rectangle(width=0.2*s, height=0.4*s, fill_color=color, fill_opacity=0.7,
                          stroke_color=DIM, stroke_width=1).move_to(DOWN * 0.3*s + RIGHT * 0.1*s)
    stage = Rectangle(width=1.0*s, height=0.12*s, fill_color=color, fill_opacity=0.6,
                      stroke_color=DIM, stroke_width=1).move_to(DOWN * 0.7*s)
    return VGroup(base, arm, eyepiece, objective, stage)

def syringe_shape(height=2.5, color=SYRINGE_GRAY):
    """Medical syringe."""
    s = height / 2.5
    barrel = Rectangle(width=0.4*s, height=1.5*s, fill_color=color, fill_opacity=0.8,
                       stroke_color=DIM, stroke_width=1.5)
    plunger = Rectangle(width=0.15*s, height=0.6*s, fill_color=DIM, fill_opacity=0.7,
                        stroke_width=0).move_to(UP * 1.05*s)
    plunger_top = Rectangle(width=0.5*s, height=0.1*s, fill_color=DIM, fill_opacity=0.8,
                            stroke_width=0).move_to(UP * 1.35*s)
    needle = Rectangle(width=0.06*s, height=0.5*s, fill_color="#C0C0C0", fill_opacity=0.9,
                       stroke_width=0).move_to(DOWN * 1.0*s)
    liquid = Rectangle(width=0.35*s, height=0.6*s, fill_color=CELL_PINK, fill_opacity=0.4,
                       stroke_width=0).move_to(DOWN * 0.2*s)
    return VGroup(barrel, liquid, plunger, plunger_top, needle)

def vial_shape(height=1.2, color=MEDICAL_TEAL):
    """Small vaccine vial."""
    s = height / 1.2
    body = RoundedRectangle(width=0.5*s, height=0.8*s, corner_radius=0.08*s,
                            fill_color=color, fill_opacity=0.7,
                            stroke_color=color, stroke_width=1.5).move_to(DOWN * 0.1*s)
    cap = Rectangle(width=0.3*s, height=0.15*s, fill_color=DIM, fill_opacity=0.8,
                    stroke_width=0).move_to(UP * 0.35*s)
    neck = Rectangle(width=0.2*s, height=0.15*s, fill_color=color, fill_opacity=0.5,
                     stroke_width=0).move_to(UP * 0.25*s)
    return VGroup(body, neck, cap)

def dna_helix_shape(height=1.5, color=MEDICAL_TEAL):
    """Simplified DNA double helix."""
    s = height / 1.5
    helix = VGroup()
    for i in range(8):
        y = -0.5*s + i * 0.15*s
        x_off = 0.2*s * np.sin(i * 0.8)
        helix.add(Line(np.array([-x_off - 0.1*s, y, 0]), np.array([x_off + 0.1*s, y, 0]),
                       color=color, stroke_width=1.5))
    strand_l = VGroup()
    strand_r = VGroup()
    for i in range(8):
        y = -0.5*s + i * 0.15*s; x = 0.2*s * np.sin(i * 0.8)
        strand_l.add(Dot(np.array([-x - 0.1*s, y, 0]), radius=0.03*s, color=color))
        strand_r.add(Dot(np.array([x + 0.1*s, y, 0]), radius=0.03*s, color=color))
    return VGroup(helix, strand_l, strand_r)

def pill_capsule_shape(height=0.8, color=CRISIS_RED):
    """Simple pill capsule."""
    s = height / 0.8
    left = Circle(radius=0.2*s, fill_color=color, fill_opacity=0.8, stroke_width=0).move_to(LEFT * 0.2*s)
    right = Circle(radius=0.2*s, fill_color=WHITE_SOFT, fill_opacity=0.6, stroke_width=0).move_to(RIGHT * 0.2*s)
    body = Rectangle(width=0.4*s, height=0.4*s, fill_color=color, fill_opacity=0.7, stroke_width=0)
    return VGroup(body, left, right)

def rocket_shape(height=1.5, color=SYRINGE_GRAY):
    """Simple rocket."""
    s = height / 1.5
    body = Polygon(
        np.array([-0.15*s, -0.4*s, 0]), np.array([0.15*s, -0.4*s, 0]),
        np.array([0.15*s, 0.3*s, 0]), np.array([0, 0.6*s, 0]), np.array([-0.15*s, 0.3*s, 0]),
        fill_color=color, fill_opacity=0.8, stroke_color=DIM, stroke_width=1,
    )
    fin_l = Polygon(np.array([-0.15*s, -0.4*s, 0]), np.array([-0.35*s, -0.5*s, 0]),
                    np.array([-0.15*s, -0.15*s, 0]), fill_color=CRISIS_RED, fill_opacity=0.7, stroke_width=0)
    fin_r = Polygon(np.array([0.15*s, -0.4*s, 0]), np.array([0.35*s, -0.5*s, 0]),
                    np.array([0.15*s, -0.15*s, 0]), fill_color=CRISIS_RED, fill_opacity=0.7, stroke_width=0)
    flame = Ellipse(width=0.15*s, height=0.25*s, fill_color="#FF8C00", fill_opacity=0.7,
                    stroke_width=0).move_to(DOWN * 0.55*s)
    return VGroup(body, fin_l, fin_r, flame)


# ================================================================
# SCENE 1: THE HOOK (0.0–7.0s = 7.00s)
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 7.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03), star_field(20, seed=1))
        t = 0

        pill = label_pill("HENRIETTA LACKS", color=CELL_PINK, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        big_cell = cell_shape(2.5, CELL_PINK, NUCLEUS_PURPLE)
        big_cell.move_to(UP * 1.5)

        small_cells = VGroup()
        for pos in [LEFT*2.5 + UP*3.5, RIGHT*2.8 + UP*3.0, LEFT*3.0 + UP*0.5,
                    RIGHT*3.0 + DOWN*0.5, LEFT*1.5 + DOWN*0.8, RIGHT*1.5 + UP*4.0]:
            small_cells.add(cell_shape(0.5, CELL_PINK, NUCLEUS_PURPLE).move_to(pos))

        div = section_div(5, CELL_PINK).move_to(DOWN * 1.8)

        millions = safe_text("MILLIONS SAVED.", font="Bebas Neue", font_size=90, color=WHITE_SOFT)
        millions.move_to(DOWN * 3.0)

        never_knew = safe_text("SHE NEVER KNEW.", font="Bebas Neue", font_size=70, color=CRISIS_RED)
        never_knew.move_to(DOWN * 4.5)

        footer_div = section_div(3, MUTED).move_to(DOWN * 5.8)

        # ── Timing: 7.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(GrowFromCenter(big_cell), run_time=0.8); t += 0.8
        self.play(LaggedStart(*[FadeIn(sc, scale=0.8) for sc in small_cells],
                              lag_ratio=0.1), run_time=0.8)                # t=1.9
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(millions, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(millions.get_center(), color=WHITE_SOFT,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=3.0
        self.wait(1.2); t += 1.2

        # VTT 4.50: "She never knew."
        self.play(FadeIn(never_knew, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(never_knew.get_center(), color=CRISIS_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=5.0
        self.play(Create(footer_div), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 7.0)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 2: THE TAKING (7.0–14.0s = 7.00s)
# ================================================================
class Scene2_Taking(Scene):
    DURATION = 7.0
    def construct(self):
        self.add(gradient_bg("#0A080A"), grid_lines(0.03), star_field(10, seed=7))
        t = 0

        pill = label_pill("1951", color=HOSPITAL_BLUE, fs=32)
        pill.move_to(UP * ZONE_TITLE)

        micro = microscope_shape(3.5, SYRINGE_GRAY)
        micro.move_to(UP * 3.0)

        hopkins = safe_text("JOHNS HOPKINS", font="Inter", font_size=24, color=MUTED, weight="BOLD")
        hopkins.move_to(UP * 1.0)

        syr = syringe_shape(3.0, SYRINGE_GRAY)
        syr.move_to(DOWN * 0.5)

        taken_cell = cell_shape(0.6, CELL_PINK, NUCLEUS_PURPLE)
        taken_cell.move_to(DOWN * 1.8)

        div = section_div(5, CRISIS_RED).move_to(DOWN * 2.8)

        without = safe_text("WITHOUT", font="Bebas Neue", font_size=80, color=WHITE_SOFT)
        without.move_to(DOWN * 3.8)
        consent = safe_text("CONSENT.", font="Bebas Neue", font_size=90, color=CRISIS_RED)
        consent.move_to(DOWN * 5.0)
        footer_div = section_div(3, MUTED).move_to(DOWN * ZONE_FOOTER)

        # ── Timing: 7.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(micro, scale=0.9), run_time=0.6); t += 0.6
        self.play(FadeIn(hopkins), run_time=0.3); t += 0.3
        self.play(FadeIn(syr, shift=DOWN*0.1), run_time=0.5); t += 0.5
        self.play(GrowFromCenter(taken_cell), run_time=0.4); t += 0.4
        self.wait(1.1); t += 1.1

        # VTT 3.50: "Without her knowledge."
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(without, scale=1.05), run_time=0.5); t += 0.5
        self.wait(0.7); t += 0.7

        # VTT 5.00: "Without her consent."
        self.play(FadeIn(consent, scale=1.15), run_time=0.5); t += 0.5
        self.play(Flash(consent.get_center(), color=CRISIS_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=5.5
        self.play(Create(footer_div), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 7.0)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 3: THE MIRACLE (14.0–21.0s = 7.00s)
# ================================================================
class Scene3_Miracle(Scene):
    DURATION = 7.0
    def construct(self):
        self.add(gradient_bg("#0A0A0E"), grid_lines(0.03), star_field(12, seed=13))
        t = 0

        pill = label_pill("THE MIRACLE", color=CELL_PINK, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        c1 = cell_shape(1.2, CELL_PINK, NUCLEUS_PURPLE)
        c1.move_to(UP * 3.0)

        c2a = cell_shape(0.8, CELL_PINK, NUCLEUS_PURPLE).move_to(LEFT * 1.2 + UP * 3.0)
        c2b = cell_shape(0.8, CELL_PINK, NUCLEUS_PURPLE).move_to(RIGHT * 1.2 + UP * 3.0)

        c4 = VGroup()
        for pos in [LEFT*2 + UP*1.5, LEFT*0.5 + UP*1.5, RIGHT*0.5 + UP*1.5, RIGHT*2 + UP*1.5]:
            c4.add(cell_shape(0.6, CELL_PINK, NUCLEUS_PURPLE).move_to(pos))

        c8 = VGroup()
        np.random.seed(88)
        for i in range(8):
            c8.add(cell_shape(0.45, CELL_PINK, NUCLEUS_PURPLE)
                   .move_to(np.array([-3.0 + i * 0.9, np.random.uniform(-0.5, 0.5), 0])))

        div = section_div(5, HELA_GOLD).move_to(DOWN * 1.5)

        hela = safe_text("HeLa", font="Bebas Neue", font_size=150, color=HELA_GOLD)
        hela.move_to(DOWN * 3.0)

        never_stopped = safe_text("NEVER STOPPED.", font="Bebas Neue", font_size=55, color=CELL_PINK)
        never_stopped.move_to(DOWN * 4.8)
        footer_div = section_div(3, MUTED).move_to(DOWN * 5.8)

        # ── Timing: 7.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(GrowFromCenter(c1), run_time=0.5); t += 0.5
        self.wait(0.4); t += 0.4
        self.play(FadeOut(c1, run_time=0.2)); t += 0.2
        self.play(FadeIn(c2a, scale=0.8), FadeIn(c2b, scale=0.8), run_time=0.3); t += 0.3
        self.play(FadeOut(c2a), FadeOut(c2b), run_time=0.2); t += 0.2
        self.play(LaggedStart(*[FadeIn(c, scale=0.8) for c in c4],
                              lag_ratio=0.05), run_time=0.4)               # t=2.3

        # VTT 2.50: "Scientists called them HeLa."
        self.play(FadeOut(c4), run_time=0.2); t += 0.2
        self.play(LaggedStart(*[FadeIn(c, scale=0.8) for c in c8],
                              lag_ratio=0.04), run_time=0.5)               # t=3.0
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(hela, scale=1.2), run_time=0.6); t += 0.6
        self.play(Flash(hela.get_center(), color=HELA_GOLD,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=4.2
        self.wait(0.3); t += 0.3

        # VTT 4.50: "Most important cells in medical history."
        self.play(FadeIn(never_stopped, shift=UP*0.1), run_time=0.4); t += 0.4
        self.play(Create(footer_div), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 7.0)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 4: THE SCALE (21.0–28.0s = 7.00s)
# ================================================================
class Scene4_Scale(Scene):
    DURATION = 7.0
    def construct(self):
        self.add(gradient_bg("#080A0C"), grid_lines(0.03), star_field(10, seed=22))
        t = 0

        pill = label_pill("THE SCALE", color=MEDICAL_TEAL, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        icons = []
        labels = []
        icon_data = [
            (vial_shape, 1.5, MEDICAL_TEAL, "POLIO VACCINE", UP*3.5),
            (dna_helix_shape, 1.8, MEDICAL_TEAL, "GENE MAPPING", UP*1.5),
            (pill_capsule_shape, 1.0, CRISIS_RED, "CANCER TREATMENT", DOWN*0.3),
            (syringe_shape, 1.8, SYRINGE_GRAY, "COVID VACCINES", DOWN*2.2),
            (rocket_shape, 1.8, SYRINGE_GRAY, "SPACE", DOWN*4.0),
        ]
        for fn, h, col, txt, y_pos in icon_data:
            if fn == pill_capsule_shape:
                ic = fn(h, col)
            elif fn == syringe_shape or fn == rocket_shape:
                ic = fn(h, col)
            else:
                ic = fn(h, col)
            ic.move_to(LEFT * 2.0 + y_pos)
            icons.append(ic)
            lbl = safe_text(txt, font="Inter", font_size=22, color=col, weight="BOLD")
            lbl.move_to(RIGHT * 1.0 + y_pos)
            labels.append(lbl)

        div = section_div(5, HELA_GOLD).move_to(DOWN * 5.0)
        space = safe_text("BEEN TO SPACE.", font="Bebas Neue", font_size=55, color=HELA_GOLD)
        space.move_to(DOWN * 5.8)

        # ── Timing: 7.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(GrowFromCenter(icons[0]), FadeIn(labels[0]), run_time=0.5); t += 0.5
        self.wait(0.9); t += 0.9

        # VTT 2.00
        self.play(GrowFromCenter(icons[1]), FadeIn(labels[1]), run_time=0.4); t += 0.4
        self.play(GrowFromCenter(icons[2]), FadeIn(labels[2]), run_time=0.4); t += 0.4
        self.play(GrowFromCenter(icons[3]), FadeIn(labels[3]), run_time=0.4); t += 0.4
        self.wait(1.8); t += 1.8

        # VTT 5.00: "They've been to space."
        self.play(GrowFromCenter(icons[4]), FadeIn(labels[4]), run_time=0.5); t += 0.5
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(space, scale=1.05), run_time=0.4); t += 0.4
        self.play(Flash(space.get_center(), color=HELA_GOLD,
                        line_length=0.3, num_lines=6, run_time=0.3))       # t=6.2
        target = getattr(self.__class__, 'DURATION', 7.0)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 5: THE INJUSTICE (28.0–35.0s = 7.00s)
# ================================================================
class Scene5_Injustice(Scene):
    DURATION = 7.0
    def construct(self):
        self.add(gradient_bg("#0A0808"), grid_lines(0.03), star_field(8, seed=33))
        t = 0

        pill = label_pill("THE INJUSTICE", color=CRISIS_RED, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        dollars = VGroup()
        for pos, fs in [(LEFT*3 + UP*4.3, 65), (LEFT*1 + UP*3.8, 75), (RIGHT*0.5 + UP*4.5, 60),
                        (RIGHT*2.5 + UP*4.0, 70), (LEFT*2 + UP*3.2, 50), (RIGHT*1.5 + UP*3.5, 55)]:
            dollars.add(safe_text("$", font="Bebas Neue", font_size=fs, color=MONEY_GREEN).move_to(pos))

        billions_lbl = safe_text("BILLIONS.", font="Bebas Neue", font_size=70, color=MONEY_GREEN)
        billions_lbl.move_to(UP * 2.0)

        card = RoundedRectangle(width=4, height=2.2, corner_radius=0.2,
                                fill_color=SURFACE2, fill_opacity=0.9,
                                stroke_color=MUTED, stroke_width=1.5).move_to(DOWN * 0.3)
        card_text = safe_text("INSURANCE", font="Inter", font_size=24, color=MUTED, weight="BOLD")
        card_text.move_to(UP * 0.2)
        x1 = Line(LEFT*1.8 + UP*0.8, RIGHT*1.8 + DOWN*1.4, color=CRISIS_RED, stroke_width=6)
        x2 = Line(RIGHT*1.8 + UP*0.8, LEFT*1.8 + DOWN*1.4, color=CRISIS_RED, stroke_width=6)
        denied = safe_text("DENIED.", font="Bebas Neue", font_size=60, color=CRISIS_RED)
        denied.move_to(DOWN * 0.3)

        div = section_div(5, CRISIS_RED).move_to(DOWN * 2.0)

        companies = safe_text("COMPANIES:", font="Bebas Neue", font_size=40, color=MONEY_GREEN)
        companies.move_to(LEFT * 2.0 + DOWN * 3.0)
        comp_val = safe_text("BILLIONS", font="Bebas Neue", font_size=55, color=MONEY_GREEN)
        comp_val.move_to(LEFT * 2.0 + DOWN * 3.8)
        family = safe_text("HER FAMILY:", font="Bebas Neue", font_size=40, color=CRISIS_RED)
        family.move_to(RIGHT * 2.0 + DOWN * 3.0)
        fam_val = safe_text("NOTHING", font="Bebas Neue", font_size=55, color=CRISIS_RED)
        fam_val.move_to(RIGHT * 2.0 + DOWN * 3.8)
        vs_line = Line(DOWN * 2.5, DOWN * 4.5, color=MUTED, stroke_width=1.5)

        yr = safe_text("UNTIL 1975.", font="Inter", font_size=24, color=MUTED, weight="BOLD")
        yr.move_to(DOWN * 5.5)

        # ── Timing: 7.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(LaggedStart(*[FadeIn(d, shift=DOWN*0.2) for d in dollars],
                              lag_ratio=0.06), run_time=0.5)               # t=0.8
        self.play(FadeIn(billions_lbl, scale=1.05), run_time=0.4); t += 0.4
        self.wait(1.0); t += 1.0

        # VTT 2.50
        self.play(FadeIn(card, scale=0.95), FadeIn(card_text), run_time=0.4); t += 0.4
        self.play(Create(x1), Create(x2), run_time=0.4); t += 0.4
        self.play(FadeIn(denied, scale=1.1), run_time=0.3); t += 0.3
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(Create(vs_line), run_time=0.2); t += 0.2
        self.play(FadeIn(companies), FadeIn(family), run_time=0.3); t += 0.3
        self.play(FadeIn(comp_val, scale=1.05), FadeIn(fam_val, scale=1.05),
                  run_time=0.4)                                             # t=4.5
        self.play(Flash(fam_val.get_center(), color=CRISIS_RED,
                        line_length=0.3, num_lines=6, run_time=0.3))       # t=4.8

        # VTT 5.00
        self.play(FadeIn(yr, shift=UP*0.05), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 7.0)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 6: THE PUNCH (35.0–42.8s = 7.80s)
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 7.8
    def construct(self):
        self.add(gradient_bg("#050508"))
        t = 0

        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP * (8 - bh/2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN * (8 - bh/2)),
        )
        self.add(star_field(12, seed=99))

        ghost_glow = Circle(radius=3, fill_color=CELL_GLOW, fill_opacity=0.03, stroke_width=0)
        ghost_glow.move_to(UP * 0.5)
        self.add(ghost_glow)

        cell_grid = VGroup()
        np.random.seed(42)
        for row in range(6):
            for col in range(5):
                x = -3.0 + col * 1.5 + np.random.uniform(-0.2, 0.2)
                y = 4.5 - row * 1.3 + np.random.uniform(-0.15, 0.15)
                cell_grid.add(cell_shape(0.35, CELL_PINK, NUCLEUS_PURPLE)
                              .move_to(np.array([x, y, 0])).set_opacity(0.4))

        every_lab = safe_text("EVERY LAB.", font="Bebas Neue", font_size=60, color=MUTED)
        every_lab.move_to(DOWN * 0.5)

        div = section_div(4, HELA_GOLD).move_to(DOWN * 1.8)

        henrietta = safe_text("HENRIETTA LACKS.", font="Bebas Neue", font_size=75, color=HELA_GOLD)
        henrietta.move_to(DOWN * 3.0)
        erased = safe_text("ALMOST ERASED.", font="Bebas Neue", font_size=65, color=CRISIS_RED)
        erased.move_to(DOWN * 4.5)
        glow = Circle(radius=2.5, fill_color=HELA_GOLD, fill_opacity=0.04, stroke_width=0)
        glow.move_to(henrietta)

        # ── Timing: 7.80s ──
        self.play(LaggedStart(*[FadeIn(c, scale=0.8) for c in cell_grid],
                              lag_ratio=0.02), run_time=1.2)               # t=1.2
        self.play(FadeIn(every_lab, scale=1.05), run_time=0.5); t += 0.5
        self.wait(1.0); t += 1.0

        # VTT 3.00
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(glow), FadeIn(henrietta, scale=1.1), run_time=0.6); t += 0.6
        self.play(Flash(henrietta.get_center(), color=HELA_GOLD,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=3.9
        self.play(FadeIn(erased, scale=1.05), run_time=0.5); t += 0.5
        self.play(Flash(erased.get_center(), color=CRISIS_RED,
                        line_length=0.3, num_lines=6, run_time=0.3))       # t=4.7

        target = getattr(self.__class__, 'DURATION', 7.8)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5


# ── Infra ─────────────────────────────────────────────────────
def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_Taking, Scene3_Miracle,
          Scene4_Scale, Scene5_Injustice, Scene6_Punch]
    config.output_file = f"henrietta_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"henrietta_scene_{idx+1}.mp4"):
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

    names = ["Scene1_Hook","Scene2_Taking","Scene3_Miracle",
             "Scene4_Scale","Scene5_Injustice","Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_henrietta.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="henrietta", audio_path=str(audio))
    final = od / "henrietta_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
