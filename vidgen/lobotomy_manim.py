#!/usr/bin/env python3
"""Lobotomies Won a Nobel Prize (Manim).

6 scenes, ~40.7s (37.7s audio + 3s hold).

VTT cues (absolute → relative):
  Scene 1 THE HOOK (0.0–6.8s = 6.80s):
    0.100 (0.10) A Nobel Prize winner drove an ice pick
    2.500 (2.50) through 3,500 human brains.
  Scene 2 THE METHOD (6.8–13.5s = 6.70s):
    6.900 (0.10) Walter Freeman called it a cure.
    8.500 (1.70) He didn't use an operating room. He used a van.
    11.500 (4.70) Patients called it the lobotomobile.
  Scene 3 THE VICTIM (13.5–20.3s = 6.80s):
    13.600 (0.10) Rosemary Kennedy was 23. Intelligent. Rebellious.
    16.500 (3.00) Her father had her lobotomized.
    18.500 (5.00) She couldn't walk or speak for the rest of her life.
  Scene 4 THE SCALE (20.3–27.0s = 6.70s):
    20.400 (0.10) Freeman performed lobotomies on housewives, veterans, children.
    24.000 (3.70) His youngest patient was four years old.
  Scene 5 THE INSTITUTION (27.0–33.8s = 6.80s):
    27.100 (0.10) In 1949, the Nobel Committee gave him the Prize.
    30.000 (3.00) They called it a breakthrough.
    32.000 (5.00) The prize has never been revoked.
  Scene 6 THE PUNCH (33.8–40.7s = 6.90s):
    33.900 (0.10) The Nobel Prize for lobotomies still stands.
    37.000 (3.20) No one has ever apologized.
    + 3s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """A Nobel Prize winner drove an ice pick
through 3,500 human brains.
Walter Freeman called it a cure.
He didn't use an operating room. He used a van.
Patients called it the lobotomobile.
Rosemary Kennedy was 23. Intelligent. Rebellious.
Her father had her lobotomized.
She couldn't walk or speak for the rest of her life.
Freeman performed lobotomies on housewives, veterans, children.
His youngest patient was four years old.
In 1949, the Nobel Committee gave him the Prize.
They called it a breakthrough.
The prize has never been revoked.
The Nobel Prize for lobotomies still stands.
No one has ever apologized."""

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
BRAIN_PINK = "#D08090"; BRAIN_DK = "#8A4050"
STEEL_GRAY = "#A0A0B0"; STEEL_DK = "#606070"
NOBEL_GOLD = "#FFD700"; NOBEL_DK = "#B8960F"
BLOOD_RED = "#CC2222"; CRISIS_RED = "#FF3333"
VAN_BLUE = "#2A4A6A"; VAN_DK = "#1A2A3A"
WHITE_SOFT = "#F0F0F0"; MUTED = "#7B8DA0"; DIM = "#404050"
DEAD_GRAY = "#4A5568"
SAFE_W = 8.0

ZONE_TITLE  = 6.2
ZONE_UPPER  = 3.5
ZONE_MID    = 0.0
ZONE_LOWER  = -3.5
ZONE_FOOTER = -6.0


# ── Core helpers ───────────────────────────────────────────────

def gradient_bg(c=BG, g="#0A0A10"):
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

def section_div(width=5, color=BLOOD_RED):
    l = Line(LEFT*width/2, LEFT*0.12, color=color, stroke_width=1.5)
    r = Line(RIGHT*0.12, RIGHT*width/2, color=color, stroke_width=1.5)
    d = Square(side_length=0.1, color=color, fill_color=color, fill_opacity=1).rotate(45*DEGREES)
    return VGroup(l, d, r)

def label_pill(txt, color=BLOOD_RED, bg=SURFACE, fs=28):
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

def brain_shape(height=2.5, color=BRAIN_PINK, outline=BRAIN_DK):
    """Brain — two hemisphere blobs + fissure + stem."""
    s = height / 2.5
    left_h = Ellipse(width=1.1*s, height=1.3*s, fill_color=color, fill_opacity=0.85,
                     stroke_color=outline, stroke_width=1.5).move_to(LEFT * 0.35*s + UP * 0.1*s)
    right_h = Ellipse(width=1.1*s, height=1.3*s, fill_color=color, fill_opacity=0.85,
                      stroke_color=outline, stroke_width=1.5).move_to(RIGHT * 0.35*s + UP * 0.1*s)
    fissure = Line(UP * 0.7*s, DOWN * 0.3*s, color=outline, stroke_width=2)
    bump1 = Circle(radius=0.25*s, fill_color=color, fill_opacity=0.7,
                   stroke_width=0).move_to(LEFT * 0.5*s + UP * 0.5*s)
    bump2 = Circle(radius=0.22*s, fill_color=color, fill_opacity=0.7,
                   stroke_width=0).move_to(RIGHT * 0.45*s + UP * 0.55*s)
    stem = Polygon(
        np.array([-0.15*s, -0.5*s, 0]), np.array([0.15*s, -0.5*s, 0]),
        np.array([0.1*s, -0.9*s, 0]), np.array([-0.1*s, -0.9*s, 0]),
        fill_color=outline, fill_opacity=0.7, stroke_width=0,
    )
    return VGroup(left_h, right_h, fissure, bump1, bump2, stem)

def ice_pick_shape(height=3.0, color=STEEL_GRAY):
    """Long thin ice pick instrument."""
    s = height / 3.0
    # Handle
    handle = RoundedRectangle(width=0.2*s, height=0.8*s, corner_radius=0.05*s,
                              fill_color=STEEL_DK, fill_opacity=0.9,
                              stroke_color=STEEL_GRAY, stroke_width=1).move_to(UP * 1.1*s)
    # Shaft
    shaft = Rectangle(width=0.06*s, height=1.8*s, fill_color=color, fill_opacity=0.9,
                      stroke_width=0).move_to(DOWN * 0.2*s)
    # Tip — pointed
    tip = Polygon(
        np.array([-0.03*s, -1.1*s, 0]), np.array([0.03*s, -1.1*s, 0]),
        np.array([0, -1.4*s, 0]),
        fill_color=color, fill_opacity=1, stroke_width=0,
    )
    return VGroup(handle, shaft, tip)

def nobel_medal_shape(radius=1.5, color=NOBEL_GOLD, ribbon_color=BLOOD_RED):
    """Circular medal with ribbon."""
    s = radius / 1.5
    # Ribbon
    ribbon_l = Polygon(
        np.array([-0.4*s, 1.0*s, 0]), np.array([-0.1*s, 1.0*s, 0]),
        np.array([0, 0.5*s, 0]), np.array([-0.5*s, 0.5*s, 0]),
        fill_color=ribbon_color, fill_opacity=0.7, stroke_width=0,
    )
    ribbon_r = Polygon(
        np.array([0.1*s, 1.0*s, 0]), np.array([0.4*s, 1.0*s, 0]),
        np.array([0.5*s, 0.5*s, 0]), np.array([0, 0.5*s, 0]),
        fill_color=ribbon_color, fill_opacity=0.7, stroke_width=0,
    )
    # Medal disc
    medal = Circle(radius=0.8*s, fill_color=color, fill_opacity=0.9,
                   stroke_color=NOBEL_DK, stroke_width=2)
    medal.move_to(DOWN * 0.2*s)
    # Inner circle detail
    inner = Circle(radius=0.55*s, fill_opacity=0, stroke_color=NOBEL_DK,
                   stroke_width=1.5).move_to(DOWN * 0.2*s)
    # Profile silhouette (simplified)
    profile = Ellipse(width=0.4*s, height=0.5*s, fill_color=NOBEL_DK, fill_opacity=0.4,
                      stroke_width=0).move_to(DOWN * 0.15*s)
    return VGroup(ribbon_l, ribbon_r, medal, inner, profile)

def van_shape(width=4.0, color=VAN_BLUE):
    """Simple van silhouette."""
    s = width / 4.0
    # Body
    body = RoundedRectangle(width=3.0*s, height=1.3*s, corner_radius=0.15*s,
                            fill_color=color, fill_opacity=0.85,
                            stroke_color=VAN_DK, stroke_width=1.5)
    # Cab — front section higher
    cab = Polygon(
        np.array([1.0*s, 0.0, 0]), np.array([1.5*s, 0.0, 0]),
        np.array([1.5*s, 0.4*s, 0]), np.array([1.2*s, 0.65*s, 0]),
        np.array([1.0*s, 0.65*s, 0]),
        fill_color=color, fill_opacity=0.85, stroke_color=VAN_DK, stroke_width=1.5,
    )
    # Windshield
    windshield = Polygon(
        np.array([1.15*s, 0.1*s, 0]), np.array([1.4*s, 0.1*s, 0]),
        np.array([1.4*s, 0.35*s, 0]), np.array([1.2*s, 0.55*s, 0]),
        fill_color="#3A5A7A", fill_opacity=0.5, stroke_width=0,
    )
    # Wheels
    wheel_l = Circle(radius=0.2*s, fill_color="#1A1A1A", fill_opacity=0.9,
                     stroke_color=DIM, stroke_width=1.5).move_to(LEFT * 0.7*s + DOWN * 0.65*s)
    wheel_r = Circle(radius=0.2*s, fill_color="#1A1A1A", fill_opacity=0.9,
                     stroke_color=DIM, stroke_width=1.5).move_to(RIGHT * 0.9*s + DOWN * 0.65*s)
    # Red cross on side
    cross_h = Rectangle(width=0.5*s, height=0.12*s, fill_color=BLOOD_RED, fill_opacity=0.6,
                        stroke_width=0).move_to(LEFT * 0.3*s)
    cross_v = Rectangle(width=0.12*s, height=0.5*s, fill_color=BLOOD_RED, fill_opacity=0.6,
                        stroke_width=0).move_to(LEFT * 0.3*s)
    return VGroup(body, cab, windshield, wheel_l, wheel_r, cross_h, cross_v)

def figure_shape(height=1.5, color=WHITE_SOFT):
    """Simple stick figure."""
    s = height / 1.5
    head = Circle(radius=0.12*s, fill_color=color, fill_opacity=0.9,
                  stroke_color=color, stroke_width=1).move_to(UP * 0.45*s)
    body = Line(UP * 0.33*s, DOWN * 0.1*s, color=color, stroke_width=2)
    l_leg = Line(DOWN * 0.1*s, DOWN * 0.45*s + LEFT * 0.12*s, color=color, stroke_width=1.5)
    r_leg = Line(DOWN * 0.1*s, DOWN * 0.45*s + RIGHT * 0.12*s, color=color, stroke_width=1.5)
    l_arm = Line(UP * 0.2*s, UP * 0.05*s + LEFT * 0.18*s, color=color, stroke_width=1.5)
    r_arm = Line(UP * 0.2*s, UP * 0.05*s + RIGHT * 0.18*s, color=color, stroke_width=1.5)
    return VGroup(head, body, l_leg, r_leg, l_arm, r_arm)


# ================================================================
# SCENE 1: THE HOOK (0.0–6.8s = 6.80s)
# Brain + ice pick UPPER, 3500 LOWER, NOBEL PRIZE FOOTER
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 5.3
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03), star_field(15, seed=1))
        t = 0

        pill = label_pill("THE LOBOTOMY", color=BLOOD_RED, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # Brain at UPPER
        br = brain_shape(3.5, BRAIN_PINK, BRAIN_DK)
        br.move_to(UP * 2.5)

        # Ice pick through brain — angled
        pick = ice_pick_shape(4.0, STEEL_GRAY)
        pick.rotate(-20 * DEGREES)
        pick.move_to(UP * 2.5 + RIGHT * 0.5)

        div = section_div(5, BLOOD_RED).move_to(DOWN * 0.5)

        # 3,500 big at LOWER
        num = safe_text("3,500", font="Bebas Neue", font_size=160, color=BLOOD_RED)
        num.move_to(DOWN * 2.5)

        brains_lbl = safe_text("HUMAN BRAINS.", font="Bebas Neue", font_size=55, color=MUTED)
        brains_lbl.move_to(DOWN * 4.0)

        # NOBEL PRIZE at FOOTER
        nobel_lbl = safe_text("NOBEL PRIZE WINNER.", font="Bebas Neue", font_size=45, color=NOBEL_GOLD)
        nobel_lbl.move_to(DOWN * 5.5)

        footer_div = section_div(3, MUTED).move_to(DOWN * ZONE_FOOTER)

        # ── Timing: 6.80s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "A Nobel Prize winner drove an ice pick"
        self.play(GrowFromCenter(br), run_time=0.6); t += 0.6
        self.play(FadeIn(pick, shift=DOWN*0.3), run_time=0.5); t += 0.5
        self.play(Flash(pick.get_center(), color=STEEL_GRAY,
                        line_length=0.3, num_lines=6, run_time=0.3))       # t=1.7
        self.wait(0.5); t += 0.5

        # VTT 2.50: "through 3,500 human brains."
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(num, scale=1.3), run_time=0.6); t += 0.6
        self.play(Flash(num.get_center(), color=BLOOD_RED,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=3.4
        self.play(FadeIn(brains_lbl, shift=UP*0.1), run_time=0.4); t += 0.4
        self.play(FadeIn(nobel_lbl, shift=UP*0.1), run_time=0.4); t += 0.4
        self.play(Create(footer_div), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 5.3)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 2: THE METHOD (6.8–13.5s = 6.70s)
# Van UPPER, NO OPERATING ROOM MID, ice pick LOWER, LOBOTOMOBILE FOOTER
# ================================================================
class Scene2_Method(Scene):
    DURATION = 5.2
    def construct(self):
        self.add(gradient_bg("#0A080A"), grid_lines(0.03), star_field(10, seed=7))
        t = 0

        pill = label_pill("THE METHOD", color=MUTED, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # Van at UPPER
        van = van_shape(5.0, VAN_BLUE)
        van.move_to(UP * 3.0)

        # "CURE" label near van
        cure = safe_text("A CURE.", font="Bebas Neue", font_size=55, color=MUTED)
        cure.move_to(UP * 1.2)

        div1 = section_div(5, STEEL_GRAY).move_to(UP * 0.3)

        # NO OPERATING ROOM at MID
        no_room = safe_text("NO OPERATING ROOM.", font="Bebas Neue", font_size=60, color=WHITE_SOFT)
        no_room.move_to(DOWN * 0.7)

        # Ice pick at LOWER
        pick = ice_pick_shape(3.0, STEEL_GRAY)
        pick.move_to(DOWN * 2.8)

        div2 = section_div(5, BLOOD_RED).move_to(DOWN * 4.5)

        # LOBOTOMOBILE at FOOTER
        lobo = safe_text("LOBOTOMOBILE.", font="Bebas Neue", font_size=60, color=BLOOD_RED)
        lobo.move_to(DOWN * 5.5)

        # ── Timing: 6.70s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "Walter Freeman called it a cure."
        self.play(FadeIn(van, scale=0.9), run_time=0.6); t += 0.6
        self.play(FadeIn(cure, shift=UP*0.1), run_time=0.4); t += 0.4
        self.wait(0.1); t += 0.1

        # VTT 1.70: "He didn't use an operating room. He used a van."
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(no_room, scale=1.05), run_time=0.5); t += 0.5
        self.play(FadeIn(pick, shift=DOWN*0.1), run_time=0.5); t += 0.5
        self.wait(1.7); t += 1.7

        # VTT 4.70: "Patients called it the lobotomobile."
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(lobo, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(lobo.get_center(), color=BLOOD_RED,
                        line_length=0.3, num_lines=6, run_time=0.3))       # t=5.5
        target = getattr(self.__class__, 'DURATION', 5.2)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 3: THE VICTIM (13.5–20.3s = 6.80s)
# Figure UPPER, AGE 23 MID, brain+X LOWER, COULDN'T WALK FOOTER
# ================================================================
class Scene3_Victim(Scene):
    DURATION = 6.5
    def construct(self):
        self.add(gradient_bg("#0A0A0E"), grid_lines(0.03), star_field(10, seed=13))
        t = 0

        pill = label_pill("ROSEMARY KENNEDY", color=WHITE_SOFT, fs=24)
        pill.move_to(UP * ZONE_TITLE)

        # Woman figure at UPPER
        woman = figure_shape(2.5, WHITE_SOFT)
        woman.move_to(UP * 3.5)

        traits = safe_text("INTELLIGENT. REBELLIOUS.", font="Inter", font_size=24,
                           color=MUTED, weight="BOLD")
        traits.move_to(UP * 1.8)

        # AGE 23 at MID
        age = safe_text("AGE 23", font="Bebas Neue", font_size=100, color=WHITE_SOFT)
        age.move_to(UP * 0.3)

        div = section_div(5, BLOOD_RED).move_to(DOWN * 1.0)

        # Brain with X at LOWER
        br = brain_shape(2.5, BRAIN_PINK, BRAIN_DK)
        br.move_to(DOWN * 2.8)
        x1 = Line(LEFT*1.2 + UP*0.8, RIGHT*1.2 + DOWN*0.8, color=BLOOD_RED, stroke_width=6)
        x2 = Line(RIGHT*1.2 + UP*0.8, LEFT*1.2 + DOWN*0.8, color=BLOOD_RED, stroke_width=6)
        brain_x = VGroup(x1, x2).move_to(DOWN * 2.8)

        # COULDN'T WALK at FOOTER — FadeOut pill first
        couldnt = safe_text("COULDN'T WALK OR SPEAK.", font="Bebas Neue", font_size=42, color=CRISIS_RED)
        couldnt.move_to(DOWN * 4.8)

        footer_div = section_div(3, MUTED).move_to(DOWN * 5.8)

        # ── Timing: 6.80s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "Rosemary Kennedy was 23. Intelligent. Rebellious."
        self.play(FadeIn(woman, shift=UP*0.1), run_time=0.5); t += 0.5
        self.play(FadeIn(traits), run_time=0.3); t += 0.3
        self.play(FadeIn(age, scale=1.1), run_time=0.5); t += 0.5
        self.wait(1.1); t += 1.1

        # VTT 3.00: "Her father had her lobotomized."
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(GrowFromCenter(br), run_time=0.5); t += 0.5
        self.play(Create(x1), Create(x2), run_time=0.4); t += 0.4
        self.play(Flash(br.get_center(), color=BLOOD_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=4.2
        self.wait(0.5); t += 0.5

        # VTT 5.00: "She couldn't walk or speak"
        self.play(FadeIn(couldnt, scale=1.05), run_time=0.5); t += 0.5
        self.play(Flash(couldnt.get_center(), color=CRISIS_RED,
                        line_length=0.3, num_lines=6, run_time=0.3))       # t=5.5
        self.play(Create(footer_div), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 6.5)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 4: THE SCALE (20.3–27.0s = 6.70s)
# 3 figures UPPER, brain+lines MID, FOUR YEARS OLD LOWER
# ================================================================
class Scene4_Scale(Scene):
    DURATION = 4.7
    def construct(self):
        self.add(gradient_bg("#0A0808"), grid_lines(0.03), star_field(8, seed=22))
        t = 0

        pill = label_pill("THE SCALE", color=BLOOD_RED, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # 3 figures at UPPER — housewife, veteran, child
        fig_woman = figure_shape(2.0, WHITE_SOFT)
        fig_woman.move_to(LEFT * 2.5 + UP * 3.5)
        lbl_w = safe_text("HOUSEWIVES", font="Inter", font_size=18, color=MUTED, weight="BOLD")
        lbl_w.move_to(LEFT * 2.5 + UP * 2.0)

        fig_vet = figure_shape(2.0, MUTED)
        fig_vet.move_to(ORIGIN + UP * 3.5)
        lbl_v = safe_text("VETERANS", font="Inter", font_size=18, color=MUTED, weight="BOLD")
        lbl_v.move_to(ORIGIN + UP * 2.0)

        fig_child = figure_shape(1.3, CRISIS_RED)
        fig_child.move_to(RIGHT * 2.5 + UP * 3.3)
        lbl_c = safe_text("CHILDREN", font="Inter", font_size=18, color=CRISIS_RED, weight="BOLD")
        lbl_c.move_to(RIGHT * 2.5 + UP * 2.0)

        figures = VGroup(fig_woman, fig_vet, fig_child)
        fig_labels = VGroup(lbl_w, lbl_v, lbl_c)

        # Brain at MID with red lines from figures
        br = brain_shape(2.0, BRAIN_PINK, BRAIN_DK)
        br.move_to(DOWN * 0.3)

        red_lines = VGroup()
        for fig in [fig_woman, fig_vet, fig_child]:
            rl = Line(fig.get_bottom() + DOWN * 0.1, br.get_top() + UP * 0.1,
                      color=BLOOD_RED, stroke_width=2)
            red_lines.add(rl)

        div = section_div(5, CRISIS_RED).move_to(DOWN * 2.0)

        # FOUR YEARS OLD at LOWER
        four = safe_text("FOUR YEARS OLD.", font="Bebas Neue", font_size=90, color=CRISIS_RED)
        four.move_to(DOWN * 3.5)

        youngest = safe_text("HIS YOUNGEST PATIENT.", font="Inter", font_size=24,
                             color=MUTED, weight="BOLD")
        youngest.move_to(DOWN * 4.8)

        footer_div = section_div(3, MUTED).move_to(DOWN * 5.8)

        # ── Timing: 6.70s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "Freeman performed lobotomies on housewives, veterans, children."
        self.play(LaggedStart(*[FadeIn(f, shift=UP*0.1) for f in figures],
                              lag_ratio=0.15), run_time=0.6)               # t=0.9
        self.play(FadeIn(fig_labels), run_time=0.3); t += 0.3
        self.play(GrowFromCenter(br), run_time=0.5); t += 0.5
        self.play(LaggedStart(*[Create(rl) for rl in red_lines],
                              lag_ratio=0.1), run_time=0.5)                # t=2.2
        self.wait(1.2); t += 1.2

        # VTT 3.70: "His youngest patient was four years old."
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(four, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(four.get_center(), color=CRISIS_RED,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=4.5
        self.play(FadeIn(youngest, shift=UP*0.05), run_time=0.3); t += 0.3
        self.play(Create(footer_div), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 4.7)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 5: THE INSTITUTION (27.0–33.8s = 6.80s)
# Nobel medal UPPER, 1949 MID, NEVER REVOKED LOWER
# ================================================================
class Scene5_Institution(Scene):
    DURATION = 10.7
    def construct(self):
        self.add(gradient_bg("#0A0A0E"), grid_lines(0.03), star_field(10, seed=33))
        t = 0

        pill = label_pill("THE INSTITUTION", color=NOBEL_GOLD, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # Nobel medal at UPPER
        medal = nobel_medal_shape(2.0, NOBEL_GOLD, BLOOD_RED)
        medal.move_to(UP * 3.0)

        prize_lbl = safe_text("PRIZE FOR MEDICINE", font="Inter", font_size=24,
                              color=NOBEL_GOLD, weight="BOLD")
        prize_lbl.move_to(UP * 1.2)

        # 1949 at MID
        yr = safe_text("1949", font="Bebas Neue", font_size=120, color=NOBEL_GOLD)
        yr.move_to(UP * 0.0)

        breakthrough = safe_text("A BREAKTHROUGH.", font="Bebas Neue", font_size=50, color=MUTED)
        breakthrough.move_to(DOWN * 1.3)

        div = section_div(5, BLOOD_RED).move_to(DOWN * 2.3)

        # NEVER REVOKED at LOWER — FadeOut pill first
        never = safe_text("NEVER REVOKED.", font="Bebas Neue", font_size=85, color=CRISIS_RED)
        never.move_to(DOWN * 3.5)

        still = safe_text("STILL.", font="Bebas Neue", font_size=70, color=BLOOD_RED)
        still.move_to(DOWN * 5.0)

        footer_div = section_div(3, MUTED).move_to(DOWN * 5.8)

        # ── Timing: 6.80s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "In 1949, the Nobel Committee gave him the Prize."
        self.play(GrowFromCenter(medal), run_time=0.6); t += 0.6
        self.play(FadeIn(prize_lbl), run_time=0.3); t += 0.3
        self.play(FadeIn(yr, scale=1.1), run_time=0.5); t += 0.5
        self.wait(1.0); t += 1.0

        # VTT 3.00: "They called it a breakthrough."
        self.play(FadeIn(breakthrough, shift=UP*0.1), run_time=0.4); t += 0.4
        self.wait(1.6); t += 1.6

        # VTT 5.00: "The prize has never been revoked."
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(never, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(never.get_center(), color=CRISIS_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=5.8
        self.play(FadeIn(still), run_time=0.3); t += 0.3
        self.play(Create(footer_div), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 10.7)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 6: THE PUNCH (33.8–40.7s = 6.90s)
# Tarnished medal UPPER, STILL STANDS MID, NO APOLOGY LOWER, letterbox
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 8.3
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
        self.add(star_field(10, seed=99))

        # Ghost brain
        ghost = brain_shape(5, BRAIN_PINK, BRAIN_DK)
        ghost.move_to(DOWN * 1)
        ghost.set_opacity(0.04)
        self.add(ghost)

        # Tarnished medal at UPPER
        medal = nobel_medal_shape(2.0, DEAD_GRAY, BLOOD_RED)
        medal.move_to(UP * 3.0)

        div1 = section_div(4, BLOOD_RED).move_to(UP * 0.8)

        # STILL STANDS at MID
        stands = safe_text("STILL STANDS.", font="Bebas Neue", font_size=80, color=WHITE_SOFT)
        stands.move_to(DOWN * 0.3)

        div2 = section_div(4, MUTED).move_to(DOWN * 1.5)

        # NO APOLOGY at LOWER
        no_apology = safe_text("NO APOLOGY.", font="Bebas Neue", font_size=95, color=CRISIS_RED)
        no_apology.move_to(DOWN * 3.0)

        glow = Circle(radius=2.5, fill_color=BLOOD_RED, fill_opacity=0.04,
                      stroke_width=0).move_to(no_apology)

        ever = safe_text("EVER.", font="Bebas Neue", font_size=70, color=BLOOD_RED)
        ever.move_to(DOWN * 4.5)

        # ── Timing: 6.90s → +3s hold+fade ──
        # VTT 0.10: "The Nobel Prize for lobotomies still stands."
        self.play(FadeIn(medal, scale=0.9), run_time=0.5); t += 0.5
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(stands, scale=1.05), run_time=0.5); t += 0.5
        self.wait(1.5); t += 1.5

        # VTT 3.20: "No one has ever apologized."
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(glow), FadeIn(no_apology, scale=1.15), run_time=0.6); t += 0.6
        self.play(Flash(no_apology.get_center(), color=CRISIS_RED,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=4.0
        self.play(FadeIn(ever, scale=1.05), run_time=0.4); t += 0.4

        # Hold + fade
        target = getattr(self.__class__, 'DURATION', 8.3)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5


# ── Infra ─────────────────────────────────────────────────────
def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_Method, Scene3_Victim,
          Scene4_Scale, Scene5_Institution, Scene6_Punch]
    config.output_file = f"lobotomy_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"lobotomy_scene_{idx+1}.mp4"):
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

    names = ["Scene1_Hook","Scene2_Method","Scene3_Victim",
             "Scene4_Scale","Scene5_Institution","Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_lobotomy.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="lobotomy", audio_path=str(audio))
    final = od / "lobotomy_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
