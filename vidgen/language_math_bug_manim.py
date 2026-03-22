#!/usr/bin/env python3
"""Your Language Is a Math Bug — Manim screenplay.

6 scenes, ~30.1s (synced to TTS audio).

VTT cues (from tts_language_math_bug_timings.json):
  Scene 1 THE HOOK (0.0–4.6s = 4.55s):
    0.10 Chinese four-year-olds count to forty.
    1.50 American four-year-olds count to fifteen.
    2.80 Same brains. Different language.
  Scene 2 THE BUG (4.6–10.9s = 6.34s):
    4.70 In Chinese, eleven is ten-one.
    6.50 Twelve is ten-two.
    8.00 The math is visible in the words.
  Scene 3 ENGLISH PROBLEM (10.9–21.2s = 10.29s):
    11.00 In English, eleven makes no sense.
    14.00 Thirteen is three-ten, backwards.
    18.00 (hides the math)
  Scene 4 THE DATA (21.2–23.9s = 2.73s):
    21.30 Up to twelve, both groups perform the same.
    22.50 Then American kids fall off a cliff.
  Scene 5 THE EXTREME (23.9–26.5s = 2.57s):
    24.00 (Pirahã — no exact numbers — ceiling of 3)
  Scene 6 THE PUNCH (26.5–30.1s = 3.66s):
    26.60 Your brain is born ready to count.
    28.00 Whether you can depends on the words your language gave you.
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """Chinese four-year-olds count to forty. American four-year-olds count to fifteen. Same brains. Different language. In Chinese, eleven is ten-one. Twelve is ten-two. The math is visible in the words. In English, eleven makes no sense. Thirteen is three-ten, backwards. Up to twelve, both groups perform the same. Then American kids fall off a cliff. Your brain is born ready to count. Whether you can depends on the words your language gave you."""

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
BORDER = "#2A2A3A"
GRID = "#1A2030"
CHINA_RED = "#DE2910"
CHINA_GOLD = "#FFDE00"
USA_BLUE = "#002868"
USA_RED = "#BF0A30"
BRAIN_PINK = "#E88B9C"
BRAIN_CORAL = "#D06070"
LANG_CYAN = "#22CCFF"
LANG_GREEN = "#44CC66"
AMAZON_GREEN = "#1A5A2A"
FOREST_DARK = "#0D3318"
CRISIS_RED = "#FF3333"
WARM_GOLD = "#FFD700"
WHITE_SOFT = "#F0F0F0"
MUTED = "#7B8DA0"
DIM = "#404050"
DEAD_GRAY = "#4A5568"
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

def label_pill(txt, color=LANG_CYAN, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W:
        t.scale(SAFE_W / t.width)
    p = RoundedRectangle(width=t.width+0.5, height=t.height+0.3, corner_radius=0.18,
                         fill_color=bg, fill_opacity=0.95, stroke_color=color, stroke_width=1.5).move_to(t)
    return VGroup(p, t)

def section_div(width=5, color=LANG_CYAN):
    l = Line(LEFT*width/2, LEFT*0.12, color=color, stroke_width=1.5)
    r = Line(RIGHT*0.12, RIGHT*width/2, color=color, stroke_width=1.5)
    d = Square(side_length=0.1, color=color, fill_color=color, fill_opacity=1).rotate(45*DEGREES)
    return VGroup(l, d, r)


# ── Domain shapes ──────────────────────────────────────────────

def brain_shape(height=2.5, color=BRAIN_PINK, outline=BRAIN_CORAL):
    """Brain — two hemisphere blobs + stem + sulci wrinkles."""
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
    sulc1 = Line(LEFT*0.6*s + UP*0.2*s, LEFT*0.2*s + UP*0.4*s,
                 color=outline, stroke_width=1).set_opacity(0.5)
    sulc2 = Line(RIGHT*0.2*s + UP*0.15*s, RIGHT*0.55*s + UP*0.35*s,
                 color=outline, stroke_width=1).set_opacity(0.5)
    stem = Polygon(
        np.array([-0.15*s, -0.5*s, 0]), np.array([0.15*s, -0.5*s, 0]),
        np.array([0.1*s, -0.9*s, 0]), np.array([-0.1*s, -0.9*s, 0]),
        fill_color=outline, fill_opacity=0.7, stroke_width=0,
    )
    return VGroup(left_h, right_h, fissure, bump1, bump2, sulc1, sulc2, stem)

def child_shape(height=1.5, color=WHITE_SOFT):
    """Simple stick figure child with round head and limbs."""
    s = height / 1.5
    head = Circle(radius=0.14*s, fill_color=color, fill_opacity=0.9,
                  stroke_color=color, stroke_width=1).move_to(UP * 0.45*s)
    body = Line(UP * 0.31*s, DOWN * 0.1*s, color=color, stroke_width=2.5)
    l_leg = Line(DOWN * 0.1*s, DOWN * 0.48*s + LEFT * 0.14*s, color=color, stroke_width=1.5)
    r_leg = Line(DOWN * 0.1*s, DOWN * 0.48*s + RIGHT * 0.14*s, color=color, stroke_width=1.5)
    l_arm = Line(UP * 0.2*s, UP * 0.05*s + LEFT * 0.2*s, color=color, stroke_width=1.5)
    r_arm = Line(UP * 0.2*s, UP * 0.05*s + RIGHT * 0.2*s, color=color, stroke_width=1.5)
    return VGroup(head, body, l_leg, r_leg, l_arm, r_arm)

def number_block_shape(n, size=0.8, color=LANG_CYAN, text_color=WHITE_SOFT):
    """Square block with number inside — like a toy counting block."""
    sq = RoundedRectangle(width=size, height=size, corner_radius=size*0.15,
                          fill_color=color, fill_opacity=0.15,
                          stroke_color=color, stroke_width=2)
    num = Text(str(n), font="Bebas Neue", font_size=int(35 * size / 0.8), color=text_color)
    num.move_to(sq.get_center())
    return VGroup(sq, num)

def tree_silhouette(height=2.0, color=AMAZON_GREEN):
    """Simple tree silhouette — trunk + layered canopy blob."""
    s = height / 2.0
    trunk = Rectangle(width=0.15*s, height=0.6*s, fill_color="#3A2A1A", fill_opacity=0.8,
                      stroke_width=0).move_to(DOWN * 0.3*s)
    canopy = Ellipse(width=1.0*s, height=0.9*s, fill_color=color, fill_opacity=0.7,
                     stroke_width=0).move_to(UP * 0.35*s)
    canopy_top = Circle(radius=0.35*s, fill_color=color, fill_opacity=0.5,
                        stroke_width=0).move_to(UP * 0.65*s)
    return VGroup(trunk, canopy, canopy_top)

def speech_bubble_shape(width=2.5, height=1.5, color=SURFACE2, border=MUTED):
    """Rounded rectangle with triangular tail."""
    s = width / 2.5
    body = RoundedRectangle(width=width, height=height, corner_radius=0.25*s,
                            fill_color=color, fill_opacity=0.9,
                            stroke_color=border, stroke_width=1.5)
    tail = Polygon(
        np.array([-0.3*s, -height/2, 0]),
        np.array([-0.5*s, -height/2 - 0.4*s, 0]),
        np.array([0.1*s, -height/2, 0]),
        fill_color=color, fill_opacity=0.9, stroke_color=border, stroke_width=1,
    )
    return VGroup(body, tail)


# ================================================================
# SCENE 1: THE HOOK (0.0–4.6s = 4.55s)
# Two children, 40 vs 15, SAME BRAINS, DIFFERENT LANGUAGE
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 4.55
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # TITLE zone — pill
        pill = label_pill("THE LANGUAGE BUG", color=LANG_CYAN, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # UPPER zone — two children side by side with numbers
        child_cn = child_shape(2.0, CHINA_GOLD)
        child_cn.move_to(LEFT * 2.2 + UP * ZONE_UPPER)
        child_us = child_shape(2.0, USA_BLUE)
        child_us.move_to(RIGHT * 2.2 + UP * ZONE_UPPER)

        num_40 = safe_text("40", font="Bebas Neue", font_size=110, color=CHINA_GOLD)
        num_40.move_to(LEFT * 2.2 + UP * 5.0)
        num_15 = safe_text("15", font="Bebas Neue", font_size=110, color=CRISIS_RED)
        num_15.move_to(RIGHT * 2.2 + UP * 5.0)

        age_cn = safe_text("AGE 4", font="Inter", font_size=22, color=MUTED, weight="BOLD")
        age_cn.move_to(LEFT * 2.2 + UP * 2.0)
        age_us = safe_text("AGE 4", font="Inter", font_size=22, color=MUTED, weight="BOLD")
        age_us.move_to(RIGHT * 2.2 + UP * 2.0)

        v_div = DashedLine(UP * 5.2, UP * 1.8, color=MUTED, stroke_width=1, dash_length=0.15)

        # MID zone — brain shape with "SAME BRAINS"
        brain = brain_shape(2.0, BRAIN_PINK, BRAIN_CORAL)
        brain.move_to(UP * ZONE_MID)
        same_lbl = safe_text("SAME BRAINS.", font="Bebas Neue", font_size=70, color=WHITE_SOFT)
        same_lbl.move_to(DOWN * 1.5)

        # LOWER zone — "DIFFERENT LANGUAGE" dramatic reveal
        diff_lang = safe_text("DIFFERENT", font="Bebas Neue", font_size=90, color=CRISIS_RED)
        diff_lang.move_to(UP * ZONE_LOWER + UP * 0.5)
        language = safe_text("LANGUAGE.", font="Bebas Neue", font_size=90, color=CRISIS_RED)
        language.move_to(UP * ZONE_LOWER + DOWN * 0.8)
        glow_lower = Circle(radius=2.5, fill_color=CRISIS_RED, fill_opacity=0.04,
                            stroke_width=0).move_to(UP * ZONE_LOWER)

        footer_div = section_div(4, MUTED).move_to(UP * ZONE_FOOTER)

        # ── Timing: 4.55s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # Chinese child + 40
        self.play(FadeIn(child_cn, shift=UP*0.15), FadeIn(num_40, scale=1.2),
                  run_time=0.4); t += 0.4
        self.play(FadeIn(age_cn, shift=UP*0.05), FadeIn(v_div), run_time=0.2); t += 0.2

        # American child + 15
        self.play(FadeIn(child_us, shift=UP*0.15), FadeIn(num_15, scale=1.2),
                  run_time=0.4); t += 0.4
        self.play(FadeIn(age_us, shift=UP*0.05), run_time=0.2); t += 0.2

        # Same brains
        self.play(GrowFromCenter(brain), FadeIn(same_lbl, scale=1.05),
                  run_time=0.5); t += 0.5

        # Different language
        self.play(FadeIn(glow_lower), FadeIn(diff_lang, scale=1.1),
                  FadeIn(language, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(language.get_center(), color=CRISIS_RED,
                        line_length=0.4, num_lines=8, run_time=0.3),
                  Create(footer_div, run_time=0.3)); t += 0.3

        target = getattr(self.__class__, 'DURATION', 4.55)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:])), run_time=0.3)


# ================================================================
# SCENE 2: THE BUG (4.6–10.9s = 6.34s)
# Chinese number blocks: structured grid showing transparency
# ================================================================
class Scene2_Bug(Scene):
    DURATION = 6.34
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # TITLE zone
        pill = label_pill("THE BUG", color=CHINA_GOLD, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # UPPER zone: 十一 = 11
        block_10a = number_block_shape(10, 0.9, CHINA_GOLD, WHITE_SOFT)
        block_10a.move_to(LEFT * 2.5 + UP * 4.2)
        plus1 = safe_text("+", font="Bebas Neue", font_size=50, color=MUTED)
        plus1.move_to(LEFT * 1.2 + UP * 4.2)
        block_1a = number_block_shape(1, 0.9, CHINA_GOLD, WHITE_SOFT)
        block_1a.move_to(LEFT * 0.0 + UP * 4.2)
        eq1 = safe_text("=", font="Bebas Neue", font_size=55, color=MUTED)
        eq1.move_to(RIGHT * 1.2 + UP * 4.2)
        result_11 = safe_text("11", font="Bebas Neue", font_size=65, color=LANG_CYAN)
        result_11.move_to(RIGHT * 2.8 + UP * 4.2)
        lbl_tenone = safe_text("TEN-ONE", font="Inter", font_size=22, color=CHINA_GOLD, weight="BOLD")
        lbl_tenone.move_to(UP * 3.2)
        row1_line = Line(LEFT * 3.8 + UP * 2.8, RIGHT * 3.8 + UP * 2.8,
                         color=BORDER, stroke_width=0.8)

        # MID zone: 十二 = 12
        block_10b = number_block_shape(10, 0.9, CHINA_GOLD, WHITE_SOFT)
        block_10b.move_to(LEFT * 2.5 + UP * 1.2)
        plus2 = safe_text("+", font="Bebas Neue", font_size=50, color=MUTED)
        plus2.move_to(LEFT * 1.2 + UP * 1.2)
        block_2b = number_block_shape(2, 0.9, CHINA_GOLD, WHITE_SOFT)
        block_2b.move_to(LEFT * 0.0 + UP * 1.2)
        eq2 = safe_text("=", font="Bebas Neue", font_size=55, color=MUTED)
        eq2.move_to(RIGHT * 1.2 + UP * 1.2)
        result_12 = safe_text("12", font="Bebas Neue", font_size=65, color=LANG_CYAN)
        result_12.move_to(RIGHT * 2.8 + UP * 1.2)
        lbl_tentwo = safe_text("TEN-TWO", font="Inter", font_size=22, color=CHINA_GOLD, weight="BOLD")
        lbl_tentwo.move_to(UP * 0.2)
        row2_line = Line(LEFT * 3.8 + DOWN * 0.3, RIGHT * 3.8 + DOWN * 0.3,
                         color=BORDER, stroke_width=0.8)

        # LOWER zone: 二十五 = 25
        block_2c = number_block_shape(2, 1.0, CHINA_GOLD, WHITE_SOFT)
        block_2c.move_to(LEFT * 3.0 + DOWN * 2.0)
        times_lbl = safe_text("x", font="Bebas Neue", font_size=45, color=MUTED)
        times_lbl.move_to(LEFT * 1.8 + DOWN * 2.0)
        block_10c = number_block_shape(10, 1.0, CHINA_GOLD, WHITE_SOFT)
        block_10c.move_to(LEFT * 0.5 + DOWN * 2.0)
        plus3 = safe_text("+", font="Bebas Neue", font_size=50, color=MUTED)
        plus3.move_to(RIGHT * 0.8 + DOWN * 2.0)
        block_5c = number_block_shape(5, 1.0, CHINA_GOLD, WHITE_SOFT)
        block_5c.move_to(RIGHT * 2.0 + DOWN * 2.0)
        eq3 = safe_text("=", font="Bebas Neue", font_size=55, color=MUTED)
        eq3.move_to(RIGHT * 3.2 + DOWN * 2.0)
        result_25 = safe_text("25", font="Bebas Neue", font_size=75, color=LANG_CYAN)
        result_25.move_to(RIGHT * 3.2 + DOWN * 3.2)
        lbl_25 = safe_text("TWO-TEN-FIVE", font="Inter", font_size=22, color=CHINA_GOLD, weight="BOLD")
        lbl_25.move_to(DOWN * 3.2 + LEFT * 0.5)

        div = section_div(5, LANG_GREEN).move_to(DOWN * 4.2)

        # FOOTER zone
        visible = safe_text("VISIBLE SYSTEM.", font="Bebas Neue", font_size=55, color=LANG_GREEN)
        visible.move_to(DOWN * 5.0)
        logic = safe_text("MATH IN THE WORDS", font="Inter", font_size=22,
                          color=MUTED, weight="BOLD")
        logic.move_to(UP * ZONE_FOOTER)

        # ── Timing: 6.34s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # Row 1: 10+1=11 TEN-ONE
        self.play(FadeIn(block_10a, scale=1.1), FadeIn(plus1),
                  FadeIn(block_1a, scale=1.1), run_time=0.3); t += 0.3
        self.play(FadeIn(eq1), FadeIn(result_11, scale=1.15),
                  FadeIn(lbl_tenone, shift=UP*0.05), run_time=0.3); t += 0.3
        self.play(Create(row1_line), run_time=0.2); t += 0.2

        # Row 2: 10+2=12 TEN-TWO
        self.play(FadeIn(block_10b, scale=1.1), FadeIn(plus2),
                  FadeIn(block_2b, scale=1.1), run_time=0.3); t += 0.3
        self.play(FadeIn(eq2), FadeIn(result_12, scale=1.15),
                  FadeIn(lbl_tentwo, shift=UP*0.05), run_time=0.3); t += 0.3
        self.play(Create(row2_line), run_time=0.2); t += 0.2

        # Row 3: 2x10+5=25 TWO-TEN-FIVE
        self.play(
            LaggedStart(
                FadeIn(block_2c, scale=1.1), FadeIn(times_lbl),
                FadeIn(block_10c, scale=1.1), FadeIn(plus3),
                FadeIn(block_5c, scale=1.1),
                lag_ratio=0.08,
            ), run_time=0.6); t += 0.6
        self.play(FadeIn(eq3), FadeIn(result_25, scale=1.2),
                  FadeIn(lbl_25, shift=UP*0.05), run_time=0.3); t += 0.3

        # VISIBLE SYSTEM footer
        self.play(Create(div), run_time=0.2); t += 0.2
        self.play(FadeIn(visible, scale=1.05), FadeIn(logic, shift=UP*0.05),
                  run_time=0.4); t += 0.4
        self.play(Flash(visible.get_center(), color=LANG_GREEN,
                        line_length=0.3, num_lines=6, run_time=0.3)); t += 0.3

        target = getattr(self.__class__, 'DURATION', 6.34)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:])), run_time=0.3)


# ================================================================
# SCENE 3: ENGLISH PROBLEM (10.9–21.2s = 10.29s)
# ELEVEN ?, THIRTEEN backwards, confused bubble, HIDES THE MATH
# ================================================================
class Scene3_English(Scene):
    DURATION = 10.29
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # TITLE zone
        pill = label_pill("ENGLISH PROBLEM", color=CRISIS_RED, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # UPPER zone — ELEVEN with ? and broken number blocks
        eleven = safe_text("ELEVEN", font="Bebas Neue", font_size=90, color=WHITE_SOFT)
        eleven.move_to(LEFT * 0.8 + UP * 4.2)
        q_mark = safe_text("?", font="Bebas Neue", font_size=130, color=CRISIS_RED)
        q_mark.move_to(RIGHT * 2.8 + UP * 4.2)
        broken_block = number_block_shape(11, 1.0, CRISIS_RED, WHITE_SOFT)
        broken_block.move_to(UP * 2.6)
        cross1 = Line(UL * 0.5, DR * 0.5, color=CRISIS_RED, stroke_width=3).move_to(broken_block)
        cross2 = Line(UR * 0.5, DL * 0.5, color=CRISIS_RED, stroke_width=3).move_to(broken_block)

        # MID zone — THIRTEEN with reversal arrow
        thirteen = safe_text("THIRTEEN", font="Bebas Neue", font_size=80, color=WHITE_SOFT)
        thirteen.move_to(LEFT * 0.5 + UP * 0.8)
        three_lbl = safe_text("3", font="Bebas Neue", font_size=60, color=CRISIS_RED)
        three_lbl.move_to(LEFT * 2.0 + DOWN * 0.5)
        ten_lbl = safe_text("10", font="Bebas Neue", font_size=60, color=CRISIS_RED)
        ten_lbl.move_to(RIGHT * 2.0 + DOWN * 0.5)
        back_arrow = Arrow(RIGHT * 1.2 + DOWN * 0.5, LEFT * 1.2 + DOWN * 0.5,
                           color=CRISIS_RED, stroke_width=3, buff=0.1)
        backwards = safe_text("BACKWARDS", font="Inter", font_size=22, color=MUTED, weight="BOLD")
        backwards.move_to(DOWN * 1.3)

        # LOWER zone — speech bubble with confused symbols
        bubble = speech_bubble_shape(5.0, 2.2, SURFACE2, MUTED)
        bubble.move_to(DOWN * ZONE_LOWER + DOWN * 0.2)
        confused_nums = VGroup()
        conf_data = [("11?", LEFT*1.8), ("13?", LEFT*0.0), ("20?", RIGHT*1.8)]
        for txt, pos in conf_data:
            n = safe_text(txt, font="Bebas Neue", font_size=50, color=MUTED)
            n.move_to(pos + DOWN * 3.3)
            confused_nums.add(n)

        div = section_div(5, CRISIS_RED).move_to(DOWN * 4.8)

        # FOOTER zone
        hides = safe_text("HIDES THE MATH.", font="Bebas Neue", font_size=55, color=CRISIS_RED)
        hides.move_to(DOWN * 5.6)

        # ── Timing: 10.29s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # "In English, eleven makes no sense."
        self.play(FadeIn(eleven, shift=RIGHT*0.15), run_time=0.5); t += 0.5
        self.play(FadeIn(q_mark, scale=1.4), run_time=0.4); t += 0.4
        self.play(Flash(q_mark.get_center(), color=CRISIS_RED,
                        line_length=0.3, num_lines=6, run_time=0.3)); t += 0.3
        self.play(FadeIn(broken_block, scale=0.9), run_time=0.3); t += 0.3
        self.play(Create(cross1), Create(cross2), run_time=0.3); t += 0.3
        self.wait(0.8); t += 0.8

        # "Thirteen is three-ten, backwards."
        self.play(FadeIn(thirteen, shift=RIGHT*0.15), run_time=0.4); t += 0.4
        self.play(FadeIn(three_lbl, shift=DOWN*0.1),
                  FadeIn(ten_lbl, shift=DOWN*0.1), run_time=0.4); t += 0.4
        self.play(GrowArrow(back_arrow), run_time=0.4); t += 0.4
        self.play(FadeIn(backwards, shift=UP*0.05), run_time=0.3); t += 0.3
        self.wait(1.0); t += 1.0

        # Confused bubble
        self.play(FadeIn(bubble, scale=0.95), run_time=0.4); t += 0.4
        self.play(LaggedStart(*[FadeIn(n, scale=1.1) for n in confused_nums],
                              lag_ratio=0.15), run_time=0.5); t += 0.5
        # Shake
        self.play(*[n.animate.shift(RIGHT*0.08) for n in confused_nums], run_time=0.1); t += 0.1
        self.play(*[n.animate.shift(LEFT*0.16) for n in confused_nums], run_time=0.1); t += 0.1
        self.play(*[n.animate.shift(RIGHT*0.08) for n in confused_nums], run_time=0.1); t += 0.1
        self.wait(0.5); t += 0.5

        # "Hides the math"
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(hides, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(hides.get_center(), color=CRISIS_RED,
                        line_length=0.4, num_lines=8, run_time=0.3)); t += 0.3

        target = getattr(self.__class__, 'DURATION', 10.29)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:])), run_time=0.3)


# ================================================================
# SCENE 4: THE DATA (21.2–23.9s = 2.73s)
# Line chart: equal to 12, then diverge. CLIFF.
# Redesigned for 2.7s — chart appears fast, divergence is the beat.
# ================================================================
class Scene4_Data(Scene):
    DURATION = 2.73
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # TITLE zone
        pill = label_pill("THE DATA", color=LANG_CYAN, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # Chart axes
        chart_left = -3.5
        chart_right = 3.5
        chart_bot = -0.5
        chart_top = 5.0
        x_axis = Arrow(np.array([chart_left, chart_bot, 0]),
                       np.array([chart_right + 0.3, chart_bot, 0]),
                       color=MUTED, stroke_width=2, buff=0)
        y_axis = Arrow(np.array([chart_left, chart_bot, 0]),
                       np.array([chart_left, chart_top + 0.3, 0]),
                       color=MUTED, stroke_width=2, buff=0)

        # Marker line at 12
        twelve_line = DashedLine(
            np.array([chart_left + 2.6, chart_bot, 0]),
            np.array([chart_left + 2.6, chart_top, 0]),
            color=MUTED, stroke_width=1, dash_length=0.1,
        )
        twelve_label = safe_text("12", font="Bebas Neue", font_size=28, color=MUTED)
        twelve_label.move_to(np.array([chart_left + 2.6, chart_top + 0.4, 0]))

        # Chinese line — goes up steadily
        cn_points = [
            np.array([chart_left + 0.5, chart_bot + 0.5, 0]),
            np.array([chart_left + 1.5, chart_bot + 1.5, 0]),
            np.array([chart_left + 2.6, chart_bot + 2.5, 0]),
            np.array([chart_left + 3.8, chart_bot + 3.8, 0]),
            np.array([chart_left + 5.5, chart_bot + 4.5, 0]),
        ]
        cn_line = VGroup()
        for i in range(len(cn_points) - 1):
            seg = Line(cn_points[i], cn_points[i+1], color=CHINA_GOLD, stroke_width=3)
            cn_line.add(seg)

        # US line — matches to 12, then drops
        us_points = [
            np.array([chart_left + 0.5, chart_bot + 0.5, 0]),
            np.array([chart_left + 1.5, chart_bot + 1.5, 0]),
            np.array([chart_left + 2.6, chart_bot + 2.5, 0]),
            np.array([chart_left + 3.8, chart_bot + 1.2, 0]),
            np.array([chart_left + 5.5, chart_bot + 0.8, 0]),
        ]
        us_line = VGroup()
        for i in range(len(us_points) - 1):
            seg = Line(us_points[i], us_points[i+1], color=CRISIS_RED, stroke_width=3)
            us_line.add(seg)

        cn_dots = VGroup(*[Dot(p, radius=0.06, color=CHINA_GOLD) for p in cn_points])
        us_dots = VGroup(*[Dot(p, radius=0.06, color=CRISIS_RED) for p in us_points])

        # Legend
        cn_dot_leg = Dot(radius=0.08, color=CHINA_GOLD).move_to(RIGHT * 1.5 + UP * 4.8)
        cn_lbl = safe_text("CHINESE", font="Inter", font_size=20, color=CHINA_GOLD, weight="BOLD")
        cn_lbl.move_to(RIGHT * 2.8 + UP * 4.8)
        us_dot_leg = Dot(radius=0.08, color=CRISIS_RED).move_to(RIGHT * 1.5 + UP * 4.3)
        us_lbl = safe_text("ENGLISH", font="Inter", font_size=20, color=CRISIS_RED, weight="BOLD")
        us_lbl.move_to(RIGHT * 2.8 + UP * 4.3)

        # LOWER zone — CLIFF
        cliff = safe_text("CLIFF.", font="Bebas Neue", font_size=130, color=CRISIS_RED)
        cliff.move_to(DOWN * ZONE_LOWER)

        footer_div = section_div(3, MUTED).move_to(UP * ZONE_FOOTER)

        # ── Timing: 2.73s — fast chart build, divergence as the single beat ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.2); t += 0.2

        # Axes + legend + matching lines (all at once)
        self.play(
            Create(x_axis), Create(y_axis),
            FadeIn(cn_dot_leg), FadeIn(cn_lbl),
            FadeIn(us_dot_leg), FadeIn(us_lbl),
            FadeIn(twelve_line), FadeIn(twelve_label),
            run_time=0.3); t += 0.3

        # Both lines up to 12 — matching (batched)
        self.play(
            Create(cn_line[0]), Create(cn_line[1]),
            Create(us_line[0]), Create(us_line[1]),
            FadeIn(cn_dots[0]), FadeIn(cn_dots[1]), FadeIn(cn_dots[2]),
            FadeIn(us_dots[0]), FadeIn(us_dots[1]), FadeIn(us_dots[2]),
            run_time=0.4); t += 0.4

        # Divergence — the key visual beat
        self.play(
            Create(cn_line[2]), Create(cn_line[3]),
            Create(us_line[2]), Create(us_line[3]),
            FadeIn(cn_dots[3]), FadeIn(cn_dots[4]),
            FadeIn(us_dots[3]), FadeIn(us_dots[4]),
            run_time=0.4); t += 0.4

        # CLIFF
        self.play(FadeIn(cliff, scale=1.2), run_time=0.3); t += 0.3
        self.play(Flash(cliff.get_center(), color=CRISIS_RED,
                        line_length=0.5, num_lines=10, run_time=0.3),
                  Create(footer_div, run_time=0.3)); t += 0.3

        target = getattr(self.__class__, 'DURATION', 2.73)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:])), run_time=0.3)


# ================================================================
# SCENE 5: THE EXTREME (23.9–26.5s = 2.57s)
# Pirahã — trees, ~ONE ~TWO MANY, brain ceiling at 3
# Redesigned for 2.6s — batched visuals, single impact moment.
# ================================================================
class Scene5_Extreme(Scene):
    DURATION = 2.57
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # TITLE zone
        pill = label_pill("THE EXTREME", color=AMAZON_GREEN, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # UPPER zone — Amazon forest silhouette (3 trees instead of 6 for speed)
        trees = VGroup()
        tree_positions = [LEFT*2.5, ORIGIN, RIGHT*2.5]
        tree_heights = [2.8, 3.2, 2.5]
        for pos_x, h in zip(tree_positions, tree_heights):
            tr = tree_silhouette(h, AMAZON_GREEN)
            tr.move_to(np.array([pos_x[0], ZONE_UPPER + 0.5, 0]))
            trees.add(tr)

        pirahã = safe_text("PIRAHÃ", font="Bebas Neue", font_size=55, color=AMAZON_GREEN)
        pirahã.move_to(UP * 1.8)

        # MID zone — three counting concepts with dots
        dots_group = VGroup()
        dot_data = [
            (LEFT * 2.5, "~ONE", 1, LANG_GREEN),
            (ORIGIN, "~TWO", 2, LANG_GREEN),
            (RIGHT * 2.5, "MANY", 0, CRISIS_RED),
        ]
        for pos, label, count, color in dot_data:
            col_group = VGroup()
            if count > 0:
                for j in range(count):
                    d = Dot(radius=0.2, color=color).move_to(pos + UP * 0.5 + RIGHT * j * 0.5)
                    col_group.add(d)
            else:
                for j in range(5):
                    d = Dot(radius=0.12, color=color).set_opacity(0.5)
                    d.move_to(pos + UP * 0.5 + LEFT * 0.4 + RIGHT * j * 0.25)
                    col_group.add(d)
            lbl = safe_text(label, font="Bebas Neue", font_size=40, color=color)
            lbl.move_to(pos + DOWN * 0.2)
            col_group.add(lbl)
            dots_group.add(col_group)

        # LOWER zone — brain with ceiling at 3
        br = brain_shape(2.5, BRAIN_PINK, BRAIN_CORAL)
        br.move_to(LEFT * 1.5 + DOWN * 3.3)

        ceiling_3 = safe_text("3", font="Bebas Neue", font_size=120, color=CRISIS_RED)
        ceiling_3.move_to(RIGHT * 2.0 + DOWN * 3.3)
        ceiling_lbl = safe_text("CEILING", font="Inter", font_size=22,
                                color=CRISIS_RED, weight="BOLD")
        ceiling_lbl.move_to(RIGHT * 2.0 + DOWN * 4.4)

        footer = safe_text("WORDS SHAPE COUNTING.", font="Bebas Neue", font_size=42,
                           color=LANG_GREEN)
        footer.move_to(DOWN * 5.5)

        # ── Timing: 2.57s — everything batched ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.2); t += 0.2

        # Trees + Pirahã label together
        self.play(
            LaggedStart(*[FadeIn(tr, shift=UP*0.15) for tr in trees], lag_ratio=0.05),
            FadeIn(pirahã, scale=1.05),
            run_time=0.4); t += 0.4

        # Dot groups all at once
        self.play(
            LaggedStart(*[FadeIn(dg, scale=0.9) for dg in dots_group], lag_ratio=0.1),
            run_time=0.4); t += 0.4

        # Brain + ceiling 3 — the impact beat
        self.play(GrowFromCenter(br), FadeIn(ceiling_3, scale=1.3),
                  FadeIn(ceiling_lbl, shift=UP*0.05), run_time=0.4); t += 0.4
        self.play(Flash(ceiling_3.get_center(), color=CRISIS_RED,
                        line_length=0.4, num_lines=8, run_time=0.3),
                  FadeIn(footer, shift=UP*0.05, run_time=0.3)); t += 0.3

        target = getattr(self.__class__, 'DURATION', 2.57)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:])), run_time=0.3)


# ================================================================
# SCENE 6: THE PUNCH (26.5–30.1s = 3.66s)
# Brain UPPER, speech bubbles MID, YOUR WORDS DECIDE LOWER
# Redesigned for 3.7s — brain + bubbles fast, hold on punch line.
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 3.66
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

        # Ghost brain barely visible
        ghost = brain_shape(7, BRAIN_PINK, BRAIN_CORAL)
        ghost.move_to(DOWN * 0.5)
        ghost.set_opacity(0.03)
        self.add(ghost)

        # UPPER zone — brain
        br = brain_shape(3.0, BRAIN_PINK, BRAIN_CORAL)
        br.move_to(UP * ZONE_UPPER)

        ready = safe_text("BORN READY.", font="Bebas Neue", font_size=55, color=BRAIN_PINK)
        ready.move_to(UP * 1.5)

        # MID zone — two speech bubbles (reduced from 4 for timing)
        bubbles = VGroup()
        bub_data = [
            ("TEN-ONE", LEFT * 2.0 + DOWN * 0.3, CHINA_GOLD),
            ("ELEVEN", RIGHT * 2.0 + DOWN * 0.3, CRISIS_RED),
        ]
        for txt, pos, col in bub_data:
            bub = speech_bubble_shape(2.2, 0.9, SURFACE2, col)
            bub.move_to(pos)
            lbl = safe_text(txt, font="Bebas Neue", font_size=28, color=col)
            lbl.move_to(pos + UP * 0.05)
            bubbles.add(VGroup(bub, lbl))

        # LOWER zone — YOUR WORDS DECIDE
        your_words = safe_text("YOUR WORDS", font="Bebas Neue", font_size=80, color=WHITE_SOFT)
        your_words.move_to(DOWN * 3.2)
        decide = safe_text("DECIDE.", font="Bebas Neue", font_size=100, color=LANG_CYAN)
        decide.move_to(DOWN * 4.5)

        glow = Circle(radius=2.5, fill_color=LANG_CYAN, fill_opacity=0.05,
                      stroke_width=0).move_to(decide)

        footer_div = section_div(3, MUTED).move_to(UP * ZONE_FOOTER)

        # ── Timing: 3.66s ──
        # "Your brain is born ready to count."
        self.play(GrowFromCenter(br), FadeIn(ready, scale=1.05),
                  run_time=0.5); t += 0.5

        # Bubbles — language contrast
        self.play(LaggedStart(*[FadeIn(b, scale=0.9) for b in bubbles],
                              lag_ratio=0.15), run_time=0.5); t += 0.5

        # "Whether you can depends on the words your language gave you."
        self.play(FadeIn(your_words, shift=UP*0.1), run_time=0.4); t += 0.4
        self.play(FadeIn(glow), FadeIn(decide, scale=1.15), run_time=0.5); t += 0.5
        self.play(Flash(decide.get_center(), color=LANG_CYAN,
                        line_length=0.4, num_lines=8, run_time=0.3),
                  Create(footer_div, run_time=0.3)); t += 0.3

        # Hold + fade to black
        target = getattr(self.__class__, 'DURATION', 3.66)
        remaining = max(0.1, target - t - 0.5)
        self.wait(remaining)
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=0.5)


# ── Infra ─────────────────────────────────────────────────────

SCENES = [Scene1_Hook, Scene2_Bug, Scene3_English,
          Scene4_Data, Scene5_Extreme, Scene6_Punch]

def render_single_scene(idx):
    config.output_file = f"language_math_bug_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    SCENES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"language_math_bug_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"
    d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENES):
        n = f"language_math_bug_scene_{i + 1}"
        print(f"  Preview {n}...")
        config.output_file     = n
        config.save_last_frame = True
        config.format          = "png"
        S().render()
        for p in Path(config.media_dir).rglob(f"{n}*"):
            if p.suffix == ".png":
                dst = d / f"{n}.png"
                shutil.copy2(str(p), str(dst))
                print(f"  OK: {dst} ({dst.stat().st_size // 1024} KB)")
                break
    config.save_last_frame = False
    config.format          = None
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
        idx = int(sys.argv[sys.argv.index("--scene") + 1])
        timings_json = os.environ.get("TKK_SCENE_TIMINGS")
        if timings_json:
            SCENES[idx].DURATION = json.loads(timings_json)[idx]
        render_single_scene(idx)
        sys.exit(0)

    names = ["Scene1_Hook","Scene2_Bug","Scene3_English",
             "Scene4_Data","Scene5_Extreme","Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_language_math_bug.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="language_math_bug", audio_path=str(audio))
    final = od / "language_math_bug_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
