#!/usr/bin/env python3
"""The Wrong Element — Phlogiston Theory (Manim). Science's biggest wrong answer.

6 scenes, ~37.0s (34.0s audio + 3s hold).

VTT cues (absolute → relative):
  Scene 1 (0.0–5.5s = 5.50s):
    0.200 (0.20) For 100 years, every chemist in the world believed
    2.200 (2.20) fire was made of an invisible substance called phlogiston.
    4.400 (4.40) They were completely wrong.
  Scene 2 (5.5–11.0s = 5.50s):
    5.700 (0.20) When something burned, phlogiston escaped.
    7.200 (1.70) Wood had it. Metal had it.
    8.800 (3.30) When the phlogiston left, you got ash.
    10.000 (4.50) It explained everything perfectly.
  Scene 3 (11.0–17.0s = 6.00s):
    11.200 (0.20) But metals gained weight when they burned.
    13.000 (2.00) If phlogiston left, the thing should get lighter.
    14.800 (3.80) It got heavier.
    15.800 (4.80) Nobody could explain it.
  Scene 4 (17.0–22.5s = 5.50s):
    17.200 (0.20) Lavoisier figured it out.
    18.500 (1.50) Things don't lose phlogiston when they burn.
    20.000 (3.00) They gain oxygen.
    21.200 (4.20) Fire isn't a substance escaping. It's a substance arriving.
  Scene 5 (22.5–28.0s = 5.50s):
    22.700 (0.20) Lavoisier was executed during the French Revolution.
    24.800 (2.30) The judge said 'The Republic has no need of scientists.'
    27.000 (4.50) He was 50.
  Scene 6 (28.0–37.0s = 9.00s):
    28.200 (0.20) It took a century to kill the wrong idea.
    30.500 (2.50) It took a guillotine to kill the man with the right one.
    + 3s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """For a hundred years, every chemist believed fire was an invisible substance called phlogiston. When something burned, phlogiston escaped. It explained everything. But metals gained weight when burned. If phlogiston left, things should get lighter. Lavoisier figured it out. Things don't lose phlogiston. They gain oxygen. Fire isn't escaping. It's arriving. Lavoisier was guillotined during the Revolution. It took a century to kill the wrong idea. A guillotine killed the man with the right one."""

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
config.background_color = "#0A0A10"
config.disable_caching = True

BG = "#0A0A10"; SURFACE = "#12121C"; SURFACE2 = "#1A1A26"
BORDER = "#2A2A3A"; GRID = "#14141C"
FLAME_ORANGE = "#FF6B35"; FLAME_RED = "#E63946"
ASH_GRAY = "#6B6B6B"; CHEM_BLUE = "#3498DB"
LAVOISIER_GOLD = "#C8962A"; REVOLUTION_RED = "#CC2233"
WHITE_SOFT = "#F0F0F0"; MUTED = "#7B8DA0"
SAFE_W = 8.0

ZONE_TITLE  = 6.2
ZONE_UPPER  = 3.5
ZONE_MID    = 0.0
ZONE_LOWER  = -3.5
ZONE_FOOTER = -6.0


def gradient_bg(c=BG, g="#1A0A08"):
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

def safe_text(content, **kwargs):
    t = Text(content, **kwargs)
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    return t

def label_pill(txt, color=FLAME_ORANGE, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    p = RoundedRectangle(width=t.width+0.5, height=t.height+0.3, corner_radius=0.18,
                         fill_color=bg, fill_opacity=0.95, stroke_color=color, stroke_width=1.5).move_to(t)
    return VGroup(p, t)

def section_div(width=5, color=FLAME_ORANGE):
    l = Line(LEFT*width/2, LEFT*0.12, color=color, stroke_width=1.5)
    r = Line(RIGHT*0.12, RIGHT*width/2, color=color, stroke_width=1.5)
    d = Square(side_length=0.1, color=color, fill_color=color, fill_opacity=1).rotate(45*DEGREES)
    return VGroup(l, d, r)

def ember_particles(n=12, seed=42, x_range=(-3.5, 3.5), y_range=(-2, 4)):
    """Floating ember dots that drift upward — ambient fire feel."""
    np.random.seed(seed)
    embers = VGroup()
    for _ in range(n):
        x = np.random.uniform(*x_range)
        y = np.random.uniform(*y_range)
        r = np.random.uniform(0.02, 0.06)
        op = np.random.uniform(0.15, 0.55)
        c = FLAME_ORANGE if np.random.random() > 0.4 else FLAME_RED
        embers.add(Dot(point=np.array([x, y, 0]), radius=r, color=c).set_opacity(op))
    return embers


# -- Domain Shapes --------------------------------------------------------

def flame_shape(color=FLAME_ORANGE, height=3.0):
    """Stylized flame: 3 overlapping pointed ovals, tapered at top."""
    e1 = Ellipse(width=height*0.4, height=height, fill_color=color, fill_opacity=0.9,
                 stroke_width=0)
    e2 = Ellipse(width=height*0.25, height=height*0.7, fill_color=FLAME_RED, fill_opacity=0.7,
                 stroke_width=0).rotate(15*DEGREES).shift(LEFT*height*0.12 + DOWN*height*0.08)
    e3 = Ellipse(width=height*0.25, height=height*0.7, fill_color=FLAME_RED, fill_opacity=0.7,
                 stroke_width=0).rotate(-15*DEGREES).shift(RIGHT*height*0.12 + DOWN*height*0.08)
    core = Ellipse(width=height*0.18, height=height*0.5, fill_color="#FFD700", fill_opacity=0.5,
                   stroke_width=0)
    flame = VGroup(e2, e3, e1, core)
    flame.move_to(ORIGIN)
    return flame

def balance_scale():
    """Balance scale: triangle fulcrum + beam + 2 pans on lines."""
    fulcrum = Polygon(
        np.array([-0.4, -0.6, 0]), np.array([0.4, -0.6, 0]), np.array([0, 0.3, 0]),
        fill_color=MUTED, fill_opacity=0.8, stroke_color=WHITE_SOFT, stroke_width=1.5
    )
    beam = Line(LEFT*2.2, RIGHT*2.2, color=WHITE_SOFT, stroke_width=3).move_to(UP*0.3)
    l_line1 = Line(UP*0.3 + LEFT*2.0, DOWN*0.8 + LEFT*2.0, color=MUTED, stroke_width=1.5)
    l_line2 = Line(UP*0.3 + LEFT*1.4, DOWN*0.8 + LEFT*1.4, color=MUTED, stroke_width=1.5)
    l_pan = Rectangle(width=1.0, height=0.15, fill_color=ASH_GRAY, fill_opacity=0.8,
                      stroke_color=WHITE_SOFT, stroke_width=1).move_to(DOWN*0.8 + LEFT*1.7)
    r_line1 = Line(UP*0.3 + RIGHT*2.0, DOWN*0.8 + RIGHT*2.0, color=MUTED, stroke_width=1.5)
    r_line2 = Line(UP*0.3 + RIGHT*1.4, DOWN*0.8 + RIGHT*1.4, color=MUTED, stroke_width=1.5)
    r_pan = Rectangle(width=1.0, height=0.15, fill_color=ASH_GRAY, fill_opacity=0.8,
                      stroke_color=WHITE_SOFT, stroke_width=1).move_to(DOWN*0.8 + RIGHT*1.7)
    scale = VGroup(fulcrum, beam, l_line1, l_line2, l_pan, r_line1, r_line2, r_pan)
    return scale

def flask_shape(color=CHEM_BLUE, height=3.0, fill_opacity=0.25):
    """Erlenmeyer flask: trapezoid body + thin neck."""
    bw_top = height * 0.25; bw_bot = height * 0.55; bh = height * 0.55
    body = Polygon(
        np.array([-bw_top/2, bh/2, 0]), np.array([bw_top/2, bh/2, 0]),
        np.array([bw_bot/2, -bh/2, 0]), np.array([-bw_bot/2, -bh/2, 0]),
        fill_color=color, fill_opacity=fill_opacity, stroke_color=color, stroke_width=2
    ).move_to(DOWN * height * 0.15)
    nw = height * 0.08; nh = height * 0.35
    neck = Rectangle(width=nw, height=nh, fill_color=color, fill_opacity=fill_opacity * 0.65,
                     stroke_color=color, stroke_width=2).move_to(UP * height * 0.35)
    rim = Line(LEFT*nw*1.2 + UP*(height*0.35+nh/2), RIGHT*nw*1.2 + UP*(height*0.35+nh/2),
               color=color, stroke_width=2.5)
    flask = VGroup(body, neck, rim)
    flask.move_to(ORIGIN)
    return flask

def guillotine_shape(color=REVOLUTION_RED, height=5.0):
    """Guillotine silhouette: 2 uprights + angled blade + base."""
    w = height * 0.35
    base = Rectangle(width=w*1.8, height=height*0.06, fill_color=color, fill_opacity=0.8,
                     stroke_width=0).move_to(DOWN * height * 0.47)
    l_post = Rectangle(width=height*0.035, height=height*0.85, fill_color=color, fill_opacity=0.7,
                       stroke_width=0).move_to(LEFT*w*0.45 + UP*height*0.02)
    r_post = Rectangle(width=height*0.035, height=height*0.85, fill_color=color, fill_opacity=0.7,
                       stroke_width=0).move_to(RIGHT*w*0.45 + UP*height*0.02)
    crossbar = Rectangle(width=w*1.0, height=height*0.04, fill_color=color, fill_opacity=0.8,
                         stroke_width=0).move_to(UP*height*0.44)
    blade = Rectangle(width=w*0.8, height=height*0.025, fill_color=WHITE_SOFT, fill_opacity=0.9,
                      stroke_width=0).rotate(3*DEGREES).move_to(UP*height*0.30)
    guill = VGroup(base, l_post, r_post, crossbar, blade)
    guill.move_to(ORIGIN)
    return guill


# ================================================================
# SCENE 1: THE HOOK (0.0-5.5s = 5.50s)
# Zones used: TITLE, UPPER, MID, LOWER, FOOTER
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 5.5
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE WRONG ELEMENT", color=FLAME_RED, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # Big flame centered at UPPER zone
        flame = flame_shape(FLAME_ORANGE, height=4.5)
        flame.move_to(UP * ZONE_UPPER)
        flame_glow = Circle(radius=3, fill_color=FLAME_ORANGE, fill_opacity=0.06, stroke_width=0)
        flame_glow.move_to(flame.get_center())

        # Embers drifting around the flame area
        embers = ember_particles(16, seed=1, x_range=(-3.5, 3.5), y_range=(1, 6))

        # PHLOGISTON label at MID
        phlog = safe_text("PHLOGISTON", font="Bebas Neue", font_size=100, color=FLAME_RED)
        phlog.move_to(UP * ZONE_MID)

        div = section_div(5, FLAME_RED).move_to(DOWN * 1.5)

        # 100 YEARS at LOWER
        years = safe_text("100 YEARS", font="Bebas Neue", font_size=90, color=WHITE_SOFT)
        years.move_to(UP * ZONE_LOWER + UP * 0.5)

        # WRONG at FOOTER
        wrong = safe_text("WRONG.", font="Bebas Neue", font_size=80, color=FLAME_RED)
        wrong.move_to(UP * ZONE_FOOTER)

        # -- Timing: 5.50s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(flame_glow), FadeIn(flame, scale=1.1), run_time=0.7); t += 0.7

        # Embers fade in with stagger
        self.play(LaggedStart(*[FadeIn(e, scale=0.5) for e in embers],
                              lag_ratio=0.03), run_time=0.4)               # t=1.4

        # VTT 2.20: "fire was made of an invisible substance called phlogiston."
        self.wait(0.5); t += 0.5
        self.play(FadeIn(phlog, scale=1.15), run_time=0.6); t += 0.6
        self.play(Flash(phlog.get_center(), color=FLAME_RED,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=2.8

        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(years, scale=1.05), run_time=0.5); t += 0.5

        # Embers drift upward during hold
        self.play(embers.animate.shift(UP * 0.6).set_opacity(0.1), run_time=0.5); t += 0.5

        # VTT 4.40: "They were completely wrong."
        self.play(FadeIn(wrong, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(wrong.get_center(), color=FLAME_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=4.9
        target = getattr(self.__class__, 'DURATION', 5.5)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE THEORY (5.5-11.0s = 5.50s)
# Zones used: TITLE, UPPER/MID (diagram), LOWER, FOOTER
# ================================================================
class Scene2_Theory(Scene):
    DURATION = 5.5
    def construct(self):
        self.add(gradient_bg("#0A0808"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE THEORY", color=FLAME_ORANGE, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # -- Diagram at UPPER/MID: wood -> flame -> ash --
        # Wood block on the LEFT
        wood = Rectangle(width=2.2, height=1.4, fill_color="#8B4513", fill_opacity=0.85,
                         stroke_color="#A0522D", stroke_width=2)
        wood_grain1 = Line(LEFT*0.8, RIGHT*0.8, color="#A0522D", stroke_width=1).move_to(wood.get_center() + UP*0.3)
        wood_grain2 = Line(LEFT*0.6, RIGHT*0.6, color="#A0522D", stroke_width=1).move_to(wood.get_center() + DOWN*0.2)
        wood_label = safe_text("WOOD", font="Inter", font_size=28, color=WHITE_SOFT, weight="BOLD")
        wood_label.next_to(wood, DOWN, buff=0.2)
        wood_grp = VGroup(wood, wood_grain1, wood_grain2, wood_label).move_to(LEFT * 3.0 + UP * 0.8)

        # Flame in CENTER at MID zone
        center_flame = flame_shape(FLAME_ORANGE, height=2.8)
        center_flame.move_to(UP * 0.8)

        # Rising embers from the flame
        rising_embers = ember_particles(8, seed=22, x_range=(-1.0, 1.0), y_range=(2.0, 4.5))

        # PHLOGISTON ESCAPES label above flame with upward arrow
        escape_label = safe_text("PHLOGISTON", font="Inter", font_size=24,
                                 color=FLAME_ORANGE, weight="BOLD")
        escape_label.move_to(UP * ZONE_UPPER + UP * 0.5)
        escape_up = Arrow(start=np.array([0, 1.7, 0]), end=np.array([0, 2.5, 0]),
                          color=FLAME_ORANGE, stroke_width=3, max_tip_length_to_length_ratio=0.35)

        # Arrows connecting wood -> flame -> ash
        arrow_wf = Arrow(start=np.array([-1.85, 0.8, 0]), end=np.array([-0.65, 0.8, 0]),
                         color=MUTED, stroke_width=3, max_tip_length_to_length_ratio=0.3)
        arrow_fa = Arrow(start=np.array([0.65, 0.8, 0]), end=np.array([1.85, 0.8, 0]),
                         color=MUTED, stroke_width=3, max_tip_length_to_length_ratio=0.3)

        # Ash on the RIGHT
        ash = Rectangle(width=1.4, height=0.8, fill_color=ASH_GRAY, fill_opacity=0.85,
                        stroke_color=MUTED, stroke_width=1.5)
        ash_label = safe_text("ASH", font="Inter", font_size=28, color=ASH_GRAY, weight="BOLD")
        ash_label.next_to(ash, DOWN, buff=0.2)
        ash_grp = VGroup(ash, ash_label).move_to(RIGHT * 3.0 + UP * 0.8)

        # -- Lower zone --
        div = section_div(5, FLAME_ORANGE).move_to(UP * (ZONE_MID - 1.5))

        explained = safe_text("EXPLAINED", font="Bebas Neue", font_size=90, color=FLAME_ORANGE)
        explained.move_to(DOWN * 2.8)

        everything = safe_text("EVERYTHING.", font="Bebas Neue", font_size=70, color=WHITE_SOFT)
        everything.move_to(DOWN * 4.3)

        perfectly = safe_text("Perfectly.", font="DM Serif Display", font_size=46, color=MUTED)
        perfectly.move_to(UP * ZONE_FOOTER)

        # -- Timing: 5.50s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.20: "When something burned, phlogiston escaped."
        self.play(FadeIn(wood_grp, scale=0.9), run_time=0.4); t += 0.4
        self.play(FadeIn(center_flame, scale=1.1), run_time=0.3); t += 0.3
        self.play(GrowArrow(escape_up), FadeIn(escape_label), run_time=0.5); t += 0.5

        # Embers rise from flame
        self.play(LaggedStart(*[FadeIn(e, scale=0.3) for e in rising_embers],
                              lag_ratio=0.04), run_time=0.3)               # t=1.8

        # VTT 1.70: "Wood had it. Metal had it."
        self.play(GrowArrow(arrow_wf), GrowArrow(arrow_fa), run_time=0.3); t += 0.3

        # VTT 3.30: "When the phlogiston left, you got ash."
        self.wait(0.2); t += 0.2
        self.play(FadeIn(ash_grp, shift=RIGHT*0.2), run_time=0.5); t += 0.5

        # Embers drift upward
        self.play(rising_embers.animate.shift(UP * 1.5).set_opacity(0), run_time=0.5); t += 0.5

        self.play(Create(div), run_time=0.3); t += 0.3

        # VTT 4.50: "It explained everything perfectly."
        self.wait(0.2); t += 0.2
        self.play(FadeIn(explained, scale=1.05), run_time=0.5); t += 0.5
        self.play(FadeIn(everything, shift=UP*0.06), run_time=0.4); t += 0.4
        self.play(FadeIn(perfectly, shift=UP*0.04), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 5.5)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: THE PROBLEM (11.0-17.0s = 6.00s)
# Zones used: TITLE, UPPER (scale), MID (div), LOWER (HEAVIER), FOOTER
# ================================================================
class Scene3_Problem(Scene):
    DURATION = 6.0
    def construct(self):
        self.add(gradient_bg("#080A0A"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE PROBLEM", color=FLAME_RED, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # Balance scale at UPPER zone, larger
        scale = balance_scale()
        scale.scale(1.6).move_to(UP * ZONE_UPPER - UP * 0.5)

        # Small metal block on left pan
        metal = Rectangle(width=0.8, height=0.5, fill_color=MUTED, fill_opacity=0.9,
                          stroke_color=WHITE_SOFT, stroke_width=1.5)
        metal.move_to(scale[4].get_center() + UP * 0.25)
        metal_label = safe_text("METAL", font="Inter", font_size=22, color=WHITE_SOFT, weight="BOLD")
        metal_label.next_to(metal, UP, buff=0.15)

        # Flame on the metal
        burn_flame = flame_shape(FLAME_ORANGE, height=1.2)
        burn_flame.move_to(metal.get_center() + UP * 0.85)

        # Weight indicators — arrows showing the paradox
        weight_up = Arrow(start=np.array([2.5, ZONE_UPPER - 1.5, 0]),
                          end=np.array([2.5, ZONE_UPPER, 0]),
                          color=FLAME_RED, stroke_width=4, max_tip_length_to_length_ratio=0.3)
        weight_label = safe_text("WEIGHT", font="Inter", font_size=22, color=FLAME_RED, weight="BOLD")
        weight_label.next_to(weight_up, RIGHT, buff=0.15)

        div = section_div(5, FLAME_RED).move_to(UP * (ZONE_MID - 0.5))

        # Big confused text -- LOWER zone
        heavier = safe_text("HEAVIER?", font="Bebas Neue", font_size=120, color=FLAME_RED)
        heavier.move_to(UP * ZONE_LOWER + UP * 0.3)

        # Red circle around the contradiction
        contra_circle = Circle(radius=2.2, color=FLAME_RED, stroke_width=4, fill_opacity=0)
        contra_circle.move_to(heavier.get_center())

        no_explain = safe_text("NO EXPLANATION.", font="Bebas Neue", font_size=60, color=MUTED)
        no_explain.move_to(DOWN * 5.3)

        q_mark = safe_text("?", font="Bebas Neue", font_size=140, color=FLAME_RED)
        q_mark.set_opacity(0.15).move_to(UP * ZONE_FOOTER + RIGHT * 2.5)

        # -- Timing: 6.00s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.20: "But metals gained weight when they burned."
        self.play(FadeIn(scale, scale=0.9), run_time=0.5); t += 0.5
        self.play(FadeIn(metal), FadeIn(metal_label), run_time=0.3); t += 0.3
        self.play(FadeIn(burn_flame, scale=1.1), run_time=0.4); t += 0.4

        # Tip the scale -- rotate beam to show heavier on left
        self.play(scale.animate.rotate(-8*DEGREES), run_time=0.5); t += 0.5

        # Weight arrow appears
        self.play(GrowArrow(weight_up), FadeIn(weight_label), run_time=0.4); t += 0.4

        # VTT 2.00: "If phlogiston left, the thing should get lighter."
        self.play(Create(div), run_time=0.3); t += 0.3

        # VTT 3.80: "It got heavier."
        self.wait(0.8); t += 0.8
        self.play(FadeIn(heavier, scale=1.3), run_time=0.6); t += 0.6
        self.play(Flash(heavier.get_center(), color=FLAME_RED,
                        line_length=0.6, num_lines=10, run_time=0.3))      # t=4.4
        self.play(Create(contra_circle), run_time=0.4); t += 0.4

        # VTT 4.80: "Nobody could explain it."
        self.play(FadeIn(no_explain, shift=UP*0.06), run_time=0.4); t += 0.4
        self.add(q_mark)

        # Scale wobbles during hold
        self.play(scale.animate.rotate(3*DEGREES), run_time=0.2); t += 0.2
        self.play(scale.animate.rotate(-3*DEGREES), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 6.0)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE ANSWER (17.0-22.5s = 5.50s)
# Zones used: TITLE, UPPER (flask), MID (div + Lavoisier), LOWER, FOOTER
# ================================================================
class Scene4_Answer(Scene):
    DURATION = 5.5
    def construct(self):
        self.add(gradient_bg(g="#0A1018"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE ANSWER", color=CHEM_BLUE, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # Flask in UPPER zone
        FLASK_COLOR = "#4A80A8"
        flask = flask_shape(FLASK_COLOR, height=4.0, fill_opacity=0.45)
        flask.move_to(UP * (ZONE_UPPER - 0.5))

        flask_glow = Circle(radius=2.5, fill_color=FLASK_COLOR, fill_opacity=0.12, stroke_width=0)
        flask_glow.move_to(flask.get_center())

        # Oxygen particles entering the flask (small dots converging)
        o2_dots = VGroup()
        np.random.seed(77)
        for _ in range(10):
            angle = np.random.uniform(0, 2 * np.pi)
            r = np.random.uniform(2.5, 4.0)
            x = r * np.cos(angle)
            y = ZONE_UPPER - 0.5 + r * np.sin(angle)
            dot = Dot(point=np.array([x, y, 0]), radius=0.06, color=FLASK_COLOR)
            dot.set_opacity(0.6)
            o2_dots.add(dot)

        # Arrow pointing IN to the flask
        in_arrow = Arrow(start=np.array([2.8, ZONE_UPPER, 0]),
                         end=np.array([0.7, ZONE_UPPER, 0]),
                         color=FLASK_COLOR, stroke_width=5,
                         max_tip_length_to_length_ratio=0.2)

        # OXYGEN label
        oxygen_label = safe_text("OXYGEN", font="Bebas Neue", font_size=72, color=FLASK_COLOR)
        oxygen_label.move_to(UP * (ZONE_UPPER - 1.0) + RIGHT * 2.0)

        div = section_div(5, LAVOISIER_GOLD).move_to(UP * (ZONE_MID - 0.5))

        # Lavoisier name pill at MID
        lav_pill = label_pill("LAVOISIER", color=LAVOISIER_GOLD, fs=32)
        lav_pill.move_to(DOWN * 1.5)

        # The reversal at LOWER
        arriving = safe_text("ARRIVING.", font="Bebas Neue", font_size=90, color=CHEM_BLUE)
        arriving.move_to(UP * ZONE_LOWER)

        not_escaping = safe_text("Not escaping.", font="DM Serif Display",
                                 font_size=42, color=MUTED)
        not_escaping.move_to(DOWN * 5.2)

        # -- Timing: 5.50s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.20: "Lavoisier figured it out."
        self.play(FadeIn(flask_glow), FadeIn(flask, scale=0.9), run_time=0.5); t += 0.5

        # VTT 1.50: "Things don't lose phlogiston when they burn."
        self.wait(0.4); t += 0.4
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(lav_pill, scale=1.05), run_time=0.5); t += 0.5

        # VTT 3.00: "They gain oxygen."
        self.wait(0.7); t += 0.7

        # O2 particles appear then converge toward flask
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in o2_dots],
                              lag_ratio=0.03), run_time=0.3)               # t=3.0
        self.play(GrowArrow(in_arrow), run_time=0.3); t += 0.3
        # Particles rush inward
        self.play(*[d.animate.move_to(flask.get_center()).set_opacity(0) for d in o2_dots],
                  run_time=0.4)                                            # t=3.7
        self.play(FadeIn(oxygen_label, shift=LEFT*0.3), run_time=0.4); t += 0.4
        self.play(Flash(oxygen_label.get_center(), color=CHEM_BLUE,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=4.4

        # VTT 4.20: "Fire isn't a substance escaping. It's a substance arriving."
        self.play(FadeIn(arriving, scale=1.1), run_time=0.4); t += 0.4
        self.play(FadeIn(not_escaping, shift=UP*0.04), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 5.5)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE COST (22.5-28.0s = 5.50s)
# Zones used: TITLE, UPPER/MID (guillotine), LOWER (date), FOOTER (age)
# ================================================================
class Scene5_Cost(Scene):
    DURATION = 5.5
    def construct(self):
        self.add(gradient_bg("#050508"), grid_lines(0.02))
        t = 0

        pill = label_pill("THE COST", color=REVOLUTION_RED, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # Guillotine silhouette centered across UPPER/MID
        guill = guillotine_shape(REVOLUTION_RED, height=6.0)
        guill.set_opacity(0.6)
        guill.move_to(UP * 1.0)

        guill_glow = Circle(radius=3, fill_color=REVOLUTION_RED, fill_opacity=0.04, stroke_width=0)
        guill_glow.move_to(guill.get_center())

        # Date at LOWER
        date = safe_text("1794", font="Bebas Neue", font_size=100, color=REVOLUTION_RED)
        date.move_to(UP * ZONE_LOWER + UP * 0.5)

        div = section_div(4, REVOLUTION_RED).move_to(DOWN * 4.2)

        # Age at FOOTER
        age = safe_text("AGE 50", font="Bebas Neue", font_size=80, color=WHITE_SOFT)
        age.move_to(DOWN * 5.5)

        # Add pill + glow at frame 0 so first frame is never empty
        self.add(pill, guill_glow)

        # -- Timing: 5.50s --
        # VTT 0.20: "Lavoisier was executed during the French Revolution."
        self.wait(0.5); t += 0.5
        self.play(FadeIn(guill, scale=0.95), run_time=0.8); t += 0.8

        # Blade drops with impact
        blade = guill[4]
        self.play(blade.animate.move_to(DOWN * 0.5), run_time=0.25); t += 0.25
        self.play(Flash(blade.get_center(), color=WHITE_SOFT,
                        line_length=0.3, num_lines=6, run_time=0.15))      # t=1.7

        # VTT 2.30: "The judge said..."
        self.wait(0.3); t += 0.3
        self.play(FadeIn(date, scale=1.1), run_time=0.6); t += 0.6
        self.play(Flash(date.get_center(), color=REVOLUTION_RED,
                        line_length=0.5, num_lines=8, run_time=0.3))       # t=2.9

        self.play(Create(div), run_time=0.3); t += 0.3

        # Guillotine slow drift during hold
        self.play(guill.animate.shift(DOWN * 0.15), run_time=1.0); t += 1.0

        # VTT 4.50: "He was 50."
        self.play(FadeIn(age, scale=1.05), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 5.5)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE PUNCH (28.0-37.0s = 9.00s)
# Zones used: TITLE area (bars), UPPER (flame+guillotine), MID (div),
#             LOWER (punchlines), FOOTER (div2)
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 9.0
    def construct(self):
        self.add(gradient_bg("#050508"), grid_lines(0.02))
        t = 0

        # Cinematic letterbox bars
        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP * (8 - bh/2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN * (8 - bh/2)),
        )

        # Embers scattered across frame
        embers = ember_particles(10, seed=99, x_range=(-4, 4), y_range=(-5, 5))
        embers.set_opacity(0.15)
        self.add(embers)

        # Flame on left at UPPER
        flame_left = flame_shape(FLAME_ORANGE, height=3.5)
        flame_left.move_to(LEFT * 2.5 + UP * ZONE_UPPER - UP * 1.0)
        flame_glow_l = Circle(radius=2, fill_color=FLAME_ORANGE, fill_opacity=0.05, stroke_width=0)
        flame_glow_l.move_to(flame_left.get_center())

        # Guillotine on right at UPPER
        guill_right = guillotine_shape(REVOLUTION_RED, height=4.0)
        guill_right.move_to(RIGHT * 2.5 + UP * ZONE_UPPER - UP * 1.0)
        guill_right.set_opacity(0.7)

        # "100 YEARS" under flame at MID-ish
        century = safe_text("100 YEARS", font="Bebas Neue", font_size=50, color=FLAME_ORANGE)
        century.move_to(LEFT * 2.5 + DOWN * 1.0)

        div = section_div(6, MUTED).move_to(DOWN * 2.5)

        # Punch lines at LOWER
        punch1 = safe_text("Wrong idea.", font="DM Serif Display", font_size=44, color=MUTED)
        punch1.move_to(LEFT * 2.5 + UP * ZONE_LOWER)

        punch2 = safe_text("Right man.", font="DM Serif Display", font_size=44, color=MUTED)
        punch2.move_to(RIGHT * 2.5 + UP * ZONE_LOWER)

        div2 = section_div(4, FLAME_RED).move_to(DOWN * 5.0)

        # -- Timing: 9.00s --
        # VTT 0.20: "It took a century to kill the wrong idea."
        self.play(FadeIn(flame_glow_l), FadeIn(flame_left, scale=1.05), run_time=0.6); t += 0.6
        self.play(FadeIn(century, shift=UP*0.06), run_time=0.4); t += 0.4

        # VTT 2.50: "It took a guillotine to kill the man with the right one."
        target = getattr(self.__class__, 'DURATION', 9.0)
        self.wait(max(0.1, target - t - 0.8))
        self.play(FadeIn(guill_right, scale=0.95), run_time=0.6); t += 0.6

        # Blade drop on the guillotine
        blade_r = guill_right[4]
        self.play(blade_r.animate.move_to(RIGHT * 2.5 + DOWN * 0.2), run_time=0.2); t += 0.2

        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(punch1, shift=UP*0.06), run_time=0.5); t += 0.5
        self.play(FadeIn(punch2, shift=UP*0.06), run_time=0.5); t += 0.5

        self.play(Create(div2), run_time=0.3); t += 0.3

        # Ambient drift — flame pulses gently, embers rise
        self.play(
            flame_left.animate.scale(1.06),
            embers.animate.shift(UP * 0.5).set_opacity(0.05),
            run_time=1.5
        )                                                                   # t=6.1

        self.play(flame_left.animate.scale(1/1.06), run_time=0.9); t += 0.9

        # Fade to black
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=2.0); t += 2.0


# -- Infra ---------------------------------------------------------
def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_Theory, Scene3_Problem,
          Scene4_Answer, Scene5_Cost, Scene6_Punch]
    config.output_file = f"phlogiston_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"phlogiston_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    sc = [Scene1_Hook, Scene2_Theory, Scene3_Problem,
          Scene4_Answer, Scene5_Cost, Scene6_Punch]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(sc):
        n = f"phlogiston_scene_{i+1}"; print(f"  Preview {n}...")
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
    if "--preview" in sys.argv: render_previews(); sys.exit(0)
    if "--scene" in sys.argv:
        timings_json = os.environ.get("TKK_SCENE_TIMINGS")
        if timings_json:
            _idx = int(sys.argv[sys.argv.index("--scene")+1])
            _classes = sorted([v for k,v in globals().items() if k.startswith("Scene") and len(k) > 5 and k[5].isdigit() and isinstance(v, type)], key=lambda c: c.__name__); _classes[_idx].DURATION = json.loads(timings_json)[_idx]
        render_single_scene(int(sys.argv[sys.argv.index("--scene")+1])); sys.exit(0)

    names = ["Scene1_Hook","Scene2_Theory","Scene3_Problem",
             "Scene4_Answer","Scene5_Cost","Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_phlogiston.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="phlogiston", audio_path=str(audio))
    final = od / "phlogiston_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
