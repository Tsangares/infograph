#!/usr/bin/env python3
"""Göbekli Tepe v3 — Fish Audio ELITE voice re-sync (Manim).

6 scenes, ~41.3s total (38.3s audio + 3s hold), word-level sync to tts_gobekli_fish.vtt.
ELITE voice re-record changes pacing; scene 4 now includes pyramids comparison.

VTT cues (absolute → relative to scene start):
  Scene 1 (0.0–6.8s = 6.80s):
    0.320 (0.32)  Every textbook says the same thing.
    2.940 (2.94)  Humans settled down,
    4.280 (4.28)  learned to farm, then built cities.
  Scene 2 (6.8–12.8s = 6.00s):
    6.800 (0.00)  Göbekli Tepe is 12,000 years old.
    9.720 (2.92)  6,000 years before farming even existed.
  Scene 3 (12.8–19.0s = 6.20s):
    12.820 (0.02) Local shepherds in Turkey always said the hilltop was sacred.
    16.640 (3.84) Archaeologists ignored them for decades.
  Scene 4 (19.0–28.9s = 9.90s):
    19.020 (0.02) In 1994, a German archaeologist started digging.
    23.280 (4.28) Massive carved pillars.
    24.880 (5.88) Built by hunter-gatherers.
    26.680 (7.68) 20 times older than the pyramids.
  Scene 5 (28.9–35.7s = 6.80s):
    28.960 (0.06) And then,
    29.840 (0.94) someone buried Göbekli Tepe on purpose.
    32.680 (3.78) They did not build temples because they had civilization.
  Scene 6 (35.7–41.3s = 5.60s):
    35.680 (0.0)  They built civilization because they had temples.
    + 3s hold + fade to black
"""

import json, os
import sys
import subprocess
import shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """Every textbook says the same thing.
Humans settled down,
learned to farm, then built cities.
Göbekli Tepe is 12,000 years old.
6,000 years before farming even existed.
Local shepherds in Turkey always said the hilltop was sacred.
Archaeologists ignored them for decades.
In 1994, a German archaeologist started digging.
Massive carved pillars.
Built by hunter-gatherers.
20 times older than the pyramids.
And then,
someone buried Göbekli Tepe on purpose.
They did not build temples because they had civilization.
They built civilization because they had temples."""

from manim import (
    Scene, Text, VGroup, VMobject, Group, Rectangle, RoundedRectangle, Circle,
    Line, Arrow, DashedLine, Dot, Polygon, Arc, Ellipse,
    Triangle, Square,
    FadeIn, FadeOut, GrowFromCenter, Write, Create, DrawBorderThenFill,
    AnimationGroup, LaggedStart,
    Flash, GrowArrow,
    config, UP, DOWN, LEFT, RIGHT, ORIGIN, UL, UR, DL, DR,
    WHITE, BLACK,
    rate_functions,
    DEGREES, PI,
)
import numpy as np

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.frame_width = 9
config.frame_height = 16
config.background_color = "#0B0F18"
config.disable_caching = True

# Palette — warm sandstone / archaeological feel
GOLD = "#FFD700"
GOLD_DIM = "#B8960F"
RED = "#E63946"
WHITE_SOFT = "#F0F0F0"
MUTED = "#7B8DA0"
BG = "#0B0F18"
SURFACE = "#141C2B"
SURFACE2 = "#1A2538"
BORDER = "#2A3A50"
TEAL = "#2EC4B6"
AMBER = "#D4920A"
OCEAN = "#1B3A5C"
SAND = "#C4A35A"
SAND_DARK = "#8A7238"
SAND_LIGHT = "#E8D5A0"
EARTH = "#5C3D1A"
EARTH_LIGHT = "#8B6B3D"
STONE_GT = "#A8977B"
STONE_GT_DARK = "#6B5E48"

SAFE_W = 8.0


# ── Helpers ───────────────────────────────────────────────────

def gradient_bg():
    bg = Rectangle(width=12, height=20, fill_color=BG, fill_opacity=1, stroke_width=0)
    glow = Circle(radius=5, fill_color="#1A2A1C", fill_opacity=0.10, stroke_width=0).move_to(UP * 2)
    return VGroup(bg, glow)


def star_field(n=30, seed=42):
    np.random.seed(seed)
    stars = VGroup()
    for _ in range(n):
        x = np.random.uniform(-4.5, 4.5)
        y = np.random.uniform(-8, 8)
        r = np.random.uniform(0.015, 0.035)
        op = np.random.uniform(0.15, 0.45)
        stars.add(Dot(point=np.array([x, y, 0]), radius=r, color=WHITE).set_opacity(op))
    return stars


def section_div(width=5, color=GOLD):
    l = Line(LEFT * width / 2, LEFT * 0.12, color=color, stroke_width=1.5)
    r = Line(RIGHT * 0.12, RIGHT * width / 2, color=color, stroke_width=1.5)
    d = Square(side_length=0.1, color=color, fill_color=color, fill_opacity=1).rotate(45 * DEGREES)
    return VGroup(l, d, r)


def label_pill(txt, color=GOLD, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W:
        t.scale(SAFE_W / t.width)
    p = RoundedRectangle(
        width=t.width + 0.5, height=t.height + 0.3,
        corner_radius=0.18, fill_color=bg, fill_opacity=0.95,
        stroke_color=color, stroke_width=1.5,
    ).move_to(t)
    return VGroup(p, t)


def safe_text(content, **kwargs):
    t = Text(content, **kwargs)
    if t.width > SAFE_W:
        t.scale(SAFE_W / t.width)
    return t


def t_pillar(height=4.0, width=None, color=STONE_GT, stroke_color=None, stroke_w=2):
    """Göbekli Tepe T-shaped pillar — the iconic archaeological symbol."""
    w = width or height * 0.3
    h = height
    cap_w = w * 2.2  # wide cap
    cap_h = h * 0.12

    # Main shaft
    shaft = Rectangle(
        width=w, height=h * 0.88,
        fill_color=color, fill_opacity=1,
        stroke_color=stroke_color or STONE_GT_DARK, stroke_width=stroke_w,
    )
    shaft.move_to(DOWN * cap_h / 2)

    # T-cap (horizontal top)
    cap = Rectangle(
        width=cap_w, height=cap_h,
        fill_color=color, fill_opacity=1,
        stroke_color=stroke_color or STONE_GT_DARK, stroke_width=stroke_w,
    )
    cap.next_to(shaft, UP, buff=0)

    # Carved relief detail — simple V pattern on shaft face
    relief_y = shaft.get_center()[1] + h * 0.15
    arm_l = Line(
        np.array([-w * 0.3, relief_y + h * 0.1, 0]),
        np.array([0, relief_y - h * 0.05, 0]),
        color=STONE_GT_DARK, stroke_width=1.5,
    )
    arm_r = Line(
        np.array([w * 0.3, relief_y + h * 0.1, 0]),
        np.array([0, relief_y - h * 0.05, 0]),
        color=STONE_GT_DARK, stroke_width=1.5,
    )

    return VGroup(shaft, cap, arm_l, arm_r)


def hilltop_silhouette(width=8, height=3, color=EARTH):
    """Gentle hill shape — Göbekli Tepe's mound."""
    pts = []
    for i in range(20):
        x = -width / 2 + i * width / 19
        y = height * np.exp(-0.5 * (x / (width * 0.3)) ** 2)
        pts.append(np.array([x, y, 0]))
    pts.append(np.array([width / 2, 0, 0]))
    pts.append(np.array([-width / 2, 0, 0]))
    return Polygon(*pts, fill_color=color, fill_opacity=1,
                   stroke_color=EARTH_LIGHT, stroke_width=1.5)


def pyramid_shape(height=2.0, base=2.5, color=SAND):
    """Simple pyramid silhouette."""
    return Polygon(
        np.array([-base / 2, 0, 0]),
        np.array([0, height, 0]),
        np.array([base / 2, 0, 0]),
        fill_color=color, fill_opacity=0.8,
        stroke_color=SAND_DARK, stroke_width=1.5,
    )


# ================================================================
# SCENE 1: THE WRONG ANSWER (0.0–6.8s = 6.80s)
# VTT: 0.32 "Every textbook..." / 2.94 "Humans settled..." / 4.28 "learned to farm..."
# Visual: Timeline showing wrong order (farming→cities→temples)
# ================================================================
class Scene1_WrongAnswer(Scene):
    DURATION = 6.8
    def construct(self):
        self.add(gradient_bg(), star_field(15, seed=1))
        t = 0

        pill = label_pill("THE TEXTBOOK STORY", color=MUTED, fs=26)
        pill.move_to(UP * 7)

        timeline = Line(LEFT * 3.5, RIGHT * 3.5, color=MUTED, stroke_width=2.5)
        timeline.move_to(UP * 3)

        steps = [("FARMING", -2.5, TEAL), ("CITIES", 0.0, AMBER), ("TEMPLES", 2.5, GOLD)]
        step_groups = VGroup()
        arrows = VGroup()
        for txt, x, col in steps:
            tick = Line(UP * 0.2, DOWN * 0.2, color=col, stroke_width=2)
            tick.move_to(timeline.get_center() + RIGHT * x)
            icon = Circle(radius=0.25, fill_color=col, fill_opacity=0.3,
                          stroke_color=col, stroke_width=2)
            icon.move_to(tick.get_center() + UP * 0.6)
            lbl = safe_text(txt, font="Inter", font_size=22, color=col, weight="BOLD")
            lbl.next_to(tick, DOWN, buff=0.2)
            step_groups.add(VGroup(tick, icon, lbl))
        for i in range(2):
            arrows.add(Arrow(
                step_groups[i][1].get_right() + RIGHT * 0.1,
                step_groups[i + 1][1].get_left() + LEFT * 0.1,
                color=MUTED, stroke_width=2, buff=0, max_tip_length_to_length_ratio=0.3,
            ))

        taught = safe_text("This is what they taught you.", font="Inter",
                          font_size=36, color=WHITE_SOFT, weight="BOLD")
        taught.move_to(UP * 0.5)

        title = safe_text("SETTLED.", font="Bebas Neue", font_size=80, color=GOLD)
        title.move_to(DOWN * 2)
        title2 = safe_text("FARMED.", font="Bebas Neue", font_size=80, color=GOLD)
        title2.move_to(DOWN * 3.2)
        title3 = safe_text("BUILT.", font="Bebas Neue", font_size=80, color=GOLD)
        title3.move_to(DOWN * 4.4)

        wrong = safe_text("WRONG", font="Bebas Neue", font_size=70, color=RED)
        wrong_border = RoundedRectangle(
            width=wrong.width + 0.5, height=wrong.height + 0.35,
            corner_radius=0.08, stroke_color=RED, stroke_width=5, fill_opacity=0,
        ).move_to(wrong)
        stamp = VGroup(wrong_border, wrong).rotate(12 * DEGREES)
        stamp.move_to(DOWN * 3.2)

        # ── Timing: 6.80s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.5); t += 0.5
        self.play(Create(timeline), run_time=0.4); t += 0.4
        self.play(
            LaggedStart(*[FadeIn(s, scale=0.8) for s in step_groups], lag_ratio=0.15),
            run_time=0.8,
        )                                                                   # t=1.7
        self.play(
            LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.2),
            run_time=0.5,
        )                                                                   # t=2.2

        # VTT 2.94: "Humans settled down,"
        self.wait(0.5); t += 0.5
        self.play(FadeIn(taught, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(title, scale=1.1), run_time=0.6); t += 0.6
        # VTT 4.28: "learned to farm, then built cities."
        self.play(FadeIn(title2, scale=1.1), run_time=0.6); t += 0.6
        self.play(FadeIn(title3, scale=1.1), run_time=0.6); t += 0.6
        self.wait(0.2); t += 0.2
        self.play(FadeIn(stamp, scale=1.4), run_time=0.4); t += 0.4
        self.play(Flash(stamp.get_center(), color=RED,
                        line_length=0.3, num_lines=8, run_time=0.4))        # t=6.1
        target = getattr(self.__class__, 'DURATION', 6.8)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 2: THE CONTRADICTION (6.8–12.8s = 6.00s)
# VTT: 0.00 "Göbekli Tepe is 12,000 years old."
#      2.92 "6,000 years before farming even existed."
# Visual: T-pillar + "GÖBEKLI TEPE" prominent + "12,000 YEARS" + timeline
# ================================================================
class Scene2_Contradiction(Scene):
    DURATION = 6.0
    def construct(self):
        self.add(gradient_bg(), star_field(12, seed=7))
        t = 0

        pill = label_pill("THE CONTRADICTION", color=RED, fs=28)
        pill.move_to(UP * 7)

        gt_name = safe_text("GÖBEKLI TEPE", font="Bebas Neue", font_size=70, color=GOLD)
        gt_name.move_to(UP * 5.5)

        pillar = t_pillar(height=4.5, color=STONE_GT, stroke_w=2)
        pillar.move_to(UP * 2)

        big_num = safe_text("12,000", font="Bebas Neue", font_size=120, color=GOLD)
        big_num.move_to(DOWN * 1.5)
        years = safe_text("YEARS OLD", font="Inter", font_size=36, color=WHITE_SOFT, weight="BOLD")
        years.next_to(big_num, DOWN, buff=0.2)

        tl = Line(LEFT * 3.5, RIGHT * 3.5, color=MUTED, stroke_width=2)
        tl.move_to(DOWN * 4)

        gt_tick = Line(UP * 0.2, DOWN * 0.2, color=GOLD, stroke_width=2.5)
        gt_tick.move_to(tl.get_center() + LEFT * 3)
        gt_lbl = safe_text("10,000 BC", font="Inter", font_size=20, color=GOLD, weight="BOLD")
        gt_lbl.next_to(gt_tick, DOWN, buff=0.15)
        farm_tick = Line(UP * 0.2, DOWN * 0.2, color=TEAL, stroke_width=2)
        farm_tick.move_to(tl.get_center() + RIGHT * 0)
        farm_lbl = safe_text("4,000 BC", font="Inter", font_size=20, color=TEAL)
        farm_lbl.next_to(farm_tick, DOWN, buff=0.15)
        farm_tag = safe_text("FARMING\nSTARTS", font="Inter", font_size=16, color=TEAL)
        farm_tag.next_to(farm_tick, UP, buff=0.15)

        gap_bar = Rectangle(width=3.0, height=0.3, fill_color=RED, fill_opacity=0.3,
                            stroke_color=RED, stroke_width=1.5)
        gap_bar.move_to(tl.get_center() + LEFT * 1.5 + UP * 0.5)
        gap_lbl = safe_text("6,000 YEARS BEFORE FARMING", font="Inter",
                           font_size=18, color=RED, weight="BOLD")
        gap_lbl.next_to(gap_bar, UP, buff=0.1)

        div = section_div(5, RED).move_to(DOWN * 6)
        payoff = safe_text("Before farming even existed.", font="DM Serif Display",
                          font_size=40, color=WHITE_SOFT)
        payoff.move_to(DOWN * 7)

        # ── Timing: 6.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(gt_name, scale=1.1), run_time=0.5); t += 0.5
        self.play(FadeIn(pillar, shift=UP * 0.2), run_time=0.6); t += 0.6
        self.play(FadeIn(big_num, scale=1.2), run_time=0.7); t += 0.7
        self.play(FadeIn(years), run_time=0.3); t += 0.3

        # VTT 2.92: "6,000 years before farming even existed."
        self.play(Create(tl), run_time=0.3); t += 0.3
        self.play(
            FadeIn(gt_tick), FadeIn(gt_lbl),
            FadeIn(farm_tick), FadeIn(farm_lbl), FadeIn(farm_tag),
            run_time=0.4,
        )                                                                   # t=3.2
        self.play(FadeIn(gap_bar), FadeIn(gap_lbl), run_time=0.5); t += 0.5
        self.play(Flash(gap_bar.get_center(), color=RED,
                        line_length=0.3, num_lines=6, run_time=0.3))        # t=4.0
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(payoff, shift=UP * 0.06), run_time=0.7); t += 0.7
        target = getattr(self.__class__, 'DURATION', 6.0)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 3: THE DISMISSED CLUE (12.8–19.0s = 6.20s)
# VTT: 0.02 "Local shepherds in Turkey..."
#      3.84 "Archaeologists ignored them for decades."
# ================================================================
class Scene3_DismissedClue(Scene):
    DURATION = 6.2
    def construct(self):
        self.add(gradient_bg(), star_field(10, seed=13))
        t = 0

        pill = label_pill("THE DISMISSED CLUE", color=AMBER, fs=26)
        pill.move_to(UP * 7)

        loc = safe_text("TURKEY", font="Inter", font_size=26, color=AMBER, weight="BOLD")
        loc.move_to(UP * 5.8)

        hill = hilltop_silhouette(width=8, height=2.5, color=EARTH)
        hill.move_to(UP * 2.5)
        glow = Circle(radius=2, fill_color=GOLD, fill_opacity=0.08, stroke_width=0)
        glow.move_to(UP * 4)
        mini_p1 = t_pillar(height=1.0, color=STONE_GT, stroke_w=1).move_to(LEFT * 0.5 + UP * 4.2)
        mini_p2 = t_pillar(height=0.8, color=STONE_GT, stroke_w=1).move_to(RIGHT * 0.8 + UP * 4.0)

        shep_lbl = safe_text("LOCAL SHEPHERDS", font="Inter", font_size=24, color=GOLD, weight="BOLD")
        shep_lbl.move_to(LEFT * 2.2 + DOWN * 0.5)
        shep_quote = safe_text('"The hilltop\nis sacred."', font="DM Serif Display", font_size=34, color=GOLD)
        shep_quote.move_to(LEFT * 2.2 + DOWN * 2)
        sci_lbl = safe_text("ARCHAEOLOGISTS", font="Inter", font_size=24, color=MUTED, weight="BOLD")
        sci_lbl.move_to(RIGHT * 2.2 + DOWN * 0.5)
        sci_quote = safe_text('"Just a\nmedieval cemetery."', font="DM Serif Display", font_size=30, color=MUTED)
        sci_quote.move_to(RIGHT * 2.2 + DOWN * 2)
        vs_line = DashedLine(UP * 0.2, DOWN * 3.5, color=BORDER, stroke_width=1.5)
        vs_line.move_to(DOWN * 1.5)

        div = section_div(5, AMBER).move_to(DOWN * 4.5)
        ignored = safe_text("Ignored for decades.", font="Bebas Neue", font_size=70, color=RED)
        ignored.move_to(DOWN * 5.8)

        # ── Timing: 6.20s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.5); t += 0.5
        self.play(FadeIn(loc, shift=DOWN * 0.06), run_time=0.4); t += 0.4
        self.add(glow)
        self.play(DrawBorderThenFill(hill), run_time=0.7); t += 0.7
        self.play(FadeIn(mini_p1, shift=UP * 0.1),
                  FadeIn(mini_p2, shift=UP * 0.1), run_time=0.5)          # t=2.1
        self.play(FadeIn(shep_lbl), FadeIn(shep_quote, shift=UP * 0.06),
                  run_time=0.7)                                             # t=2.8
        self.play(Create(vs_line), run_time=0.3); t += 0.3

        # VTT 3.84: "Archaeologists ignored them for decades."
        self.wait(0.44); t += 0.44
        self.play(FadeIn(sci_lbl), FadeIn(sci_quote, shift=UP * 0.06),
                  run_time=0.6)                                             # t=4.14
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(ignored, scale=1.1), run_time=0.7); t += 0.7
        self.play(Flash(ignored.get_center(), color=RED,
                        line_length=0.3, num_lines=8, run_time=0.4))        # t=5.54
        target = getattr(self.__class__, 'DURATION', 6.2)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 4: THE PROOF (19.0–28.9s = 9.90s)
# VTT: 0.02 "In 1994, a German archaeologist started digging."
#      4.28 "Massive carved pillars."
#      5.88 "Built by hunter-gatherers."
#      7.68 "20 times older than the pyramids."
# Visual: Date, pillars, hunter-gatherers, THEN pyramids comparison
# ================================================================
class Scene4_Proof(Scene):
    DURATION = 9.9
    def construct(self):
        self.add(gradient_bg())
        t = 0
        dark = Rectangle(width=12, height=20, fill_color="#050810", fill_opacity=0.3, stroke_width=0)
        self.add(dark, star_field(8, seed=44))

        pill = label_pill("THE PROOF", color=TEAL, fs=28)
        pill.move_to(UP * 7)

        date = safe_text("1994", font="Bebas Neue", font_size=140, color=TEAL)
        date.move_to(UP * 5.8)
        date.set_z_index(10)

        ground = Line(LEFT * 4.5, RIGHT * 4.5, color=EARTH_LIGHT, stroke_width=2.5)
        ground.move_to(UP * 1)
        earth = Rectangle(width=9, height=2.5, fill_color=EARTH, fill_opacity=0.4, stroke_width=0)
        earth.move_to(DOWN * 0.25)

        p1 = t_pillar(height=4.0, color=STONE_GT, stroke_w=2).move_to(LEFT * 2 + UP * 3)
        p2 = t_pillar(height=4.5, color=SAND, stroke_w=2).move_to(RIGHT * 0 + UP * 3.2)
        p3 = t_pillar(height=3.5, color=STONE_GT, stroke_w=2).move_to(RIGHT * 2.2 + UP * 2.8)

        massive = safe_text("MASSIVE CARVED", font="Bebas Neue", font_size=70, color=GOLD)
        massive.move_to(DOWN * 2)
        pillars_txt = safe_text("PILLARS.", font="Bebas Neue", font_size=70, color=GOLD)
        pillars_txt.move_to(DOWN * 3.2)

        div1 = section_div(5, TEAL).move_to(DOWN * 4.3)
        hunters = safe_text("HUNTER-GATHERERS.", font="Bebas Neue", font_size=70, color=WHITE_SOFT)
        hunters.move_to(DOWN * 5.4)

        # Pyramids comparison (now in scene 4)
        div2 = section_div(5, GOLD).move_to(DOWN * 6.5)
        older = safe_text("20× OLDER THAN THE PYRAMIDS.", font="Bebas Neue", font_size=50, color=GOLD)
        older.move_to(DOWN * 7.3)

        # ── Timing: 9.90s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.5); t += 0.5
        self.play(FadeIn(date, scale=1.3), run_time=0.7); t += 0.7
        self.play(Flash(date.get_center(), color=TEAL,
                        line_length=0.5, num_lines=10, run_time=0.4))      # t=1.6
        self.add(earth)
        self.play(Create(ground), run_time=0.3); t += 0.3

        self.play(
            LaggedStart(FadeIn(p1, shift=UP * 0.3), FadeIn(p2, shift=UP * 0.3),
                        FadeIn(p3, shift=UP * 0.3), lag_ratio=0.15),
            run_time=1.2,
        )                                                                   # t=3.1
        self.wait(0.9); t += 0.9

        # VTT 4.28: "Massive carved pillars."
        self.play(FadeIn(massive, scale=1.1), run_time=0.7); t += 0.7
        self.play(FadeIn(pillars_txt, scale=1.1), run_time=0.6); t += 0.6
        self.play(Flash(massive.get_center(), color=GOLD,
                        line_length=0.3, num_lines=8, run_time=0.3))        # t=5.6

        # VTT 5.88: "Built by hunter-gatherers."
        self.play(Create(div1), run_time=0.28); t += 0.28
        self.play(FadeIn(hunters, scale=1.08), run_time=0.7); t += 0.7
        self.play(Flash(hunters.get_center(), color=WHITE_SOFT,
                        line_length=0.4, num_lines=10, run_time=0.3))      # t=6.88

        # VTT 7.68: "20 times older than the pyramids."
        self.wait(0.5); t += 0.5
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(older, scale=1.1), run_time=0.7); t += 0.7
        self.play(Flash(older.get_center(), color=GOLD,
                        line_length=0.3, num_lines=8, run_time=0.3))        # t=8.68
        target = getattr(self.__class__, 'DURATION', 9.9)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 5: THE SCALE (28.9–35.7s = 6.80s)
# VTT: 0.06 "And then,"
#      0.94 "someone buried Göbekli Tepe on purpose."
#      3.78 "They did not build temples because they had civilization."
# Visual: Burial + first half of chiasmus (setup for the flip)
# ================================================================
class Scene5_Scale(Scene):
    DURATION = 6.8
    def construct(self):
        self.add(gradient_bg(), star_field(10, seed=55))
        t = 0

        pill = label_pill("THE SCALE", color=GOLD, fs=28)
        pill.move_to(UP * 7)

        # "GÖBEKLI TEPE" — prominent name
        gt_name = safe_text("GÖBEKLI TEPE", font="Bebas Neue", font_size=70, color=GOLD)
        gt_name.move_to(UP * 5)

        # T-pillar being buried
        gt_pillar = t_pillar(height=4.5, color=GOLD_DIM, stroke_w=2)
        gt_pillar.move_to(UP * 1.5)

        # "BURIED" — dramatic
        buried_txt = safe_text("BURIED.", font="Bebas Neue", font_size=90, color=RED)
        buried_txt.move_to(DOWN * 1.8)
        sub = safe_text("On purpose.", font="DM Serif Display", font_size=40, color=WHITE_SOFT)
        sub.move_to(DOWN * 3.0)

        dirt_bars = VGroup()
        for i in range(5):
            bar = Rectangle(width=9, height=0.3, fill_color=EARTH,
                            fill_opacity=0.3 + i * 0.1, stroke_width=0)
            bar.move_to(DOWN * (3.8 + i * 0.35))
            dirt_bars.add(bar)

        # First half of chiasmus — setup
        div = section_div(5, MUTED).move_to(DOWN * 5.5)
        setup1 = safe_text("They did not build temples", font="DM Serif Display",
                          font_size=36, color=MUTED)
        setup1.move_to(DOWN * 6.3)
        setup2 = safe_text("because they had civilization.", font="DM Serif Display",
                          font_size=36, color=MUTED)
        setup2.move_to(DOWN * 7.1)

        # ── Timing: 6.80s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.5); t += 0.5

        # VTT 0.94: "someone buried Göbekli Tepe on purpose."
        self.play(FadeIn(gt_name, scale=1.1), run_time=0.5); t += 0.5
        self.play(FadeIn(gt_pillar, shift=UP * 0.2), run_time=0.6); t += 0.6
        self.play(FadeIn(buried_txt, scale=1.15), run_time=0.7); t += 0.7
        self.play(Flash(buried_txt.get_center(), color=RED,
                        line_length=0.4, num_lines=8, run_time=0.3))        # t=2.6
        self.play(FadeIn(sub, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(
            LaggedStart(*[FadeIn(b) for b in dirt_bars], lag_ratio=0.06),
            run_time=0.4,
        )                                                                   # t=3.5

        # VTT 3.78: "They did not build temples because they had civilization."
        self.play(Create(div), run_time=0.28); t += 0.28
        self.play(FadeIn(setup1, shift=UP * 0.08), run_time=0.7); t += 0.7
        self.play(FadeIn(setup2, shift=UP * 0.08), run_time=0.7); t += 0.7
        target = getattr(self.__class__, 'DURATION', 6.8)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 6: THE PUNCH (35.7–41.3s = 5.60s)
# VTT: ~0.0 "They built civilization because they had temples."
# Visual: THE FLIP — just one line. Letterbox. Cinematic. 3s hold.
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 5.6
    def construct(self):
        self.add(gradient_bg())
        t = 0

        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP * (8 - bh / 2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN * (8 - bh / 2)),
        )

        ghost = t_pillar(height=12, color=GOLD, stroke_color=GOLD, stroke_w=0)
        ghost.set_opacity(0.04)
        ghost.move_to(UP * 1)
        self.add(ghost)

        stars = star_field(15, seed=99)
        stars.set_opacity(0.2)
        self.add(stars)

        div = section_div(4, GOLD).move_to(DOWN * 1)

        line_a = safe_text("They built civilization", font="DM Serif Display",
                          font_size=44, color=WHITE_SOFT)
        line_a.move_to(DOWN * 2.5)
        line_b = safe_text("because they had", font="DM Serif Display",
                          font_size=44, color=WHITE_SOFT)
        line_b.move_to(DOWN * 3.6)
        line_c = safe_text("temples.", font="Bebas Neue", font_size=90, color=GOLD)
        line_c.move_to(DOWN * 5)

        glow = Circle(radius=2.5, fill_color=GOLD, fill_opacity=0.04, stroke_width=0)
        glow.move_to(line_c)

        sig = t_pillar(height=0.5, color=GOLD, stroke_w=0)
        sig.set_opacity(0.4)
        sig.move_to(DOWN * 6.5)

        # ── Timing: 5.60s ──
        self.play(Create(div), run_time=0.4); t += 0.4
        self.play(FadeIn(line_a, shift=UP * 0.08), run_time=0.7); t += 0.7
        self.play(FadeIn(line_b, shift=UP * 0.08), run_time=0.6); t += 0.6
        self.play(FadeIn(glow), FadeIn(line_c, scale=1.08), run_time=0.9); t += 0.9
        self.play(FadeIn(sig, scale=0.8), run_time=0.3); t += 0.3

        # 3s hold — let it breathe
        target = getattr(self.__class__, 'DURATION', 5.6)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.2); t += 1.2


# ── Per-scene render ──────────────────────────────────────────
def render_single_scene(scene_idx):
    scene_classes = [
        Scene1_WrongAnswer, Scene2_Contradiction, Scene3_DismissedClue,
        Scene4_Proof, Scene5_Scale, Scene6_Punch,
    ]
    SC = scene_classes[scene_idx]
    output_dir = Path(__file__).parent
    config.output_file = f"gt_v3_scene_{scene_idx + 1}"
    config.media_dir = str(output_dir / "media")
    SC().render()
    for mp4 in Path(config.media_dir).rglob(f"gt_v3_scene_{scene_idx + 1}.mp4"):
        print(f"SCENE_FILE:{mp4}")
        return


# ── Preview mode ──────────────────────────────────────────────
def render_previews():
    preview_dir = Path(__file__).parent / "previews"
    preview_dir.mkdir(exist_ok=True)
    scenes = [Scene1_WrongAnswer, Scene2_Contradiction, Scene3_DismissedClue,
              Scene4_Proof, Scene5_Scale, Scene6_Punch]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, SC in enumerate(scenes):
        name = f"gobekli_v3_scene_{i + 1}"
        print(f"  Preview {name}...")
        config.output_file = name
        config.save_last_frame = True
        config.format = "png"
        SC().render()
        for png in Path(config.media_dir).rglob(f"{name}*"):
            if png.suffix == ".png":
                dest = preview_dir / f"{name}.png"
                shutil.copy2(str(png), str(dest))
                print(f"  OK: {dest} ({dest.stat().st_size // 1024} KB)")
                break
    config.save_last_frame = False
    config.format = None
    print(f"\nAll 6 previews saved to {preview_dir}/")


# ── MAIN ──────────────────────────────────────────────────────
if __name__ == "__main__":
    import time
    import gc

    output_dir = Path(__file__).parent

    if "--preview" in sys.argv:
        render_previews()
        sys.exit(0)

    if "--scene" in sys.argv:
        idx = int(sys.argv[sys.argv.index("--scene") + 1])
        timings_json = os.environ.get("TKK_SCENE_TIMINGS")
        if timings_json:
            import json as _json
            # Override DURATION on the scene class
            _durs = _json.loads(timings_json)
            # Find scene classes
            _scene_classes = [v for k, v in sorted(globals().items()) if k.startswith("Scene") and isinstance(v, type)]
            if idx < len(_scene_classes) and idx < len(_durs):
                _scene_classes[idx].DURATION = _durs[idx]
        render_single_scene(idx)
        sys.exit(0)

    scene_names = [
        "Scene1_WrongAnswer", "Scene2_Contradiction", "Scene3_DismissedClue",
        "Scene4_Proof", "Scene5_Scale", "Scene6_Punch",
    ]

    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = output_dir / "tts_gobekli_fish.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="gt_v3", audio_path=str(audio))
    final = output_dir / "gobekli_tepe_v3_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
    print(f"\n{'='*60}")
    print(f"  RENDER COMPLETE: {final}")
    print(f"  {mb:.1f} MB  |  {elapsed:.1f}s render time")
    print(f"{'='*60}")
