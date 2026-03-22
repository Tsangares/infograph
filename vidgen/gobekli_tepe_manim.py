#!/usr/bin/env python3
"""Gobekli Tepe -- 'They Built Civilization Because They Had Temples' (Manim).

6 scenes, 39.7s total, word-level sync to tts_gobekli_tepe.vtt.
Style: Easter Island History template (gradient_bg, grid_lines, vector art, bold type).

VTT cues (absolute -> relative to scene start):
  Scene 1 (0.0-6.67s = 6.67s):
    0.100 (0.10)  Every textbook says the same thing.
    2.625 (2.63)  Humans settled down, learned to farm, then built cities.
  Scene 2 (6.67-13.09s = 6.42s):
    6.670 (0.00)  But this temple is 12,000 years old.
    9.670 (3.00)  6,000 years before farming even existed.
  Scene 3 (13.09-19.43s = 6.34s):
    13.090 (0.00) Local shepherds always said the hilltop was sacred.
    16.465 (3.38) Archaeologists ignored them for decades.
  Scene 4 (19.43-27.35s = 7.92s):
    19.431 (0.00) In 1994, Klaus Schmidt started digging.
    23.000 (3.57) Massive carved pillars.
    25.204 (5.77) Built by hunter-gatherers.
  Scene 5 (27.35-33.06s = 5.71s):
    27.352 (0.00) 20 times older than the pyramids.
    29.988 (2.64) And someone buried the whole thing on purpose.
  Scene 6 (33.06-39.62s = 6.57s):
    33.056 (0.00) They didn't build temples because they had civilization.
    36.386 (3.33) They built civilization because they had temples.
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

TTS_SCRIPT = """Every textbook says humans settled, farmed, then built cities. This temple is 12,000 years old. 6,000 years before farming. Shepherds always said the hilltop was sacred. Archaeologists ignored them. In 1994, Klaus Schmidt started digging. Massive carved pillars built by hunter-gatherers. Twenty times older than the pyramids. Someone buried it on purpose. They didn't build temples because they had civilization. They built civilization because they had temples."""

from manim import (
    Scene, Text, Group, VGroup, VMobject, Group, Rectangle, RoundedRectangle, Circle,
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

# Palette -- warm sandstone / archaeological feel
BG = "#0B0F18"
GRID = "#1A2030"
SURFACE = "#141C2B"
SURFACE2 = "#1A2538"
WHITE_SOFT = "#F0F0F0"
GOLD = "#FFD700"
GOLD_DIM = "#B8960F"
RED = "#E63946"
MUTED = "#7B8DA0"
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

# Safe zone + vertical layout zones
SAFE_W = 8.0
SAFE_TOP = 7.2
SAFE_BOT = -6.4

ZONE_TITLE  = 6.2    # y 5.5-7.0  -- scene label pills
ZONE_UPPER  = 3.5    # y 1.5-5.5  -- hero visual top portion
ZONE_MID    = 0.0    # y -1.5-1.5 -- central focal point, big numbers
ZONE_LOWER  = -3.5   # y -5.5--1.5 -- supporting visuals, bars, icons
ZONE_FOOTER = -6.0   # y -6.4--5.5 -- captions, source labels


# -- Helpers -------------------------------------------------------

def gradient_bg(c=BG, g="#1A2A1C"):
    bg = Rectangle(width=12, height=20, fill_color=c, fill_opacity=1, stroke_width=0)
    glow = Circle(radius=5, fill_color=g, fill_opacity=0.10, stroke_width=0).move_to(UP * 2)
    return VGroup(bg, glow)


def grid_lines(opacity=0.04):
    lines = VGroup()
    for i in range(13):
        y = -8 + i * 16 / 12
        lines.add(Line(LEFT * 5, RIGHT * 5, color=GRID, stroke_width=0.5).move_to(UP * y).set_opacity(opacity))
    for j in range(7):
        x = -4.5 + j * 9 / 6
        lines.add(Line(DOWN * 8, UP * 8, color=GRID, stroke_width=0.5).move_to(RIGHT * x).set_opacity(opacity))
    return lines


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


# -- Domain Shape Helpers (4 shapes) --------------------------------

def t_pillar(height=4.0, width=None, color=STONE_GT, stroke_color=None, stroke_w=2):
    """Gobekli Tepe T-shaped pillar -- the iconic archaeological symbol."""
    w = width or height * 0.3
    h = height
    cap_w = w * 2.2
    cap_h = h * 0.12

    shaft = Rectangle(
        width=w, height=h * 0.88,
        fill_color=color, fill_opacity=1,
        stroke_color=stroke_color or STONE_GT_DARK, stroke_width=stroke_w,
    )
    shaft.move_to(DOWN * cap_h / 2)

    cap = Rectangle(
        width=cap_w, height=cap_h,
        fill_color=color, fill_opacity=1,
        stroke_color=stroke_color or STONE_GT_DARK, stroke_width=stroke_w,
    )
    cap.next_to(shaft, UP, buff=0)

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
    """Gentle hill shape -- Gobekli Tepe's mound."""
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


def stone_circle(radius=2.0, n_stones=8, color=STONE_GT):
    """Ring of standing stones -- Gobekli Tepe enclosure viewed from above."""
    group = VGroup()
    outer = Circle(radius=radius, stroke_color=EARTH_LIGHT, stroke_width=1,
                   fill_opacity=0)
    group.add(outer)
    for i in range(n_stones):
        angle = i * 2 * PI / n_stones
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        stone = Rectangle(
            width=0.18 * radius, height=0.4 * radius,
            fill_color=color, fill_opacity=0.9,
            stroke_color=STONE_GT_DARK, stroke_width=1,
        ).rotate(angle + PI / 2)
        stone.move_to(np.array([x, y, 0]))
        group.add(stone)
    return group


# ================================================================
# SCENE 1: THE WRONG ANSWER (0.0-6.67s = 6.67s)
# VTT: 0.10 "Every textbook..." / 2.63 "Humans settled..."
# Visual: Timeline showing wrong order (farming->cities->temples)
# Zones: TITLE, UPPER, MID, LOWER, FOOTER
# ================================================================
class Scene1_WrongAnswer(Scene):
    DURATION = 6.7
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE -- scene pill
        pill = label_pill("THE TEXTBOOK STORY", color=MUTED, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER -- timeline with steps
        timeline = Line(LEFT * 3.5, RIGHT * 3.5, color=MUTED, stroke_width=2.5)
        timeline.move_to(UP * ZONE_UPPER)

        steps = [
            ("FARMING", -2.5, TEAL),
            ("CITIES", 0.0, AMBER),
            ("TEMPLES", 2.5, GOLD),
        ]
        step_groups = VGroup()
        arrows = VGroup()
        for txt, x, col in steps:
            tick = Line(UP * 0.2, DOWN * 0.2, color=col, stroke_width=2)
            tick.move_to(UP * ZONE_UPPER + RIGHT * x)
            icon = Circle(radius=0.25, fill_color=col, fill_opacity=0.3,
                          stroke_color=col, stroke_width=2)
            icon.move_to(tick.get_center() + UP * 0.6)
            lbl = safe_text(txt, font="Inter", font_size=22, color=col, weight="BOLD")
            lbl.next_to(tick, DOWN, buff=0.2)
            step_groups.add(VGroup(tick, icon, lbl))

        for i in range(2):
            a = Arrow(
                step_groups[i][1].get_right() + RIGHT * 0.1,
                step_groups[i + 1][1].get_left() + LEFT * 0.1,
                color=MUTED, stroke_width=2, buff=0,
                max_tip_length_to_length_ratio=0.3,
            )
            arrows.add(a)

        # ZONE_MID -- big words
        title = safe_text("SETTLED.", font="Bebas Neue", font_size=80, color=GOLD)
        title.move_to(UP * 0.5)
        title2 = safe_text("FARMED.", font="Bebas Neue", font_size=80, color=GOLD)
        title2.move_to(DOWN * 0.7)
        title3 = safe_text("BUILT.", font="Bebas Neue", font_size=80, color=GOLD)
        title3.move_to(DOWN * 1.9)

        # ZONE_LOWER -- WRONG stamp
        wrong = safe_text("WRONG", font="Bebas Neue", font_size=70, color=RED)
        wrong_border = RoundedRectangle(
            width=wrong.width + 0.5, height=wrong.height + 0.35,
            corner_radius=0.08, stroke_color=RED, stroke_width=5, fill_opacity=0,
        ).move_to(wrong)
        stamp = VGroup(wrong_border, wrong).rotate(12 * DEGREES)
        stamp.move_to(DOWN * abs(ZONE_LOWER))

        # ZONE_FOOTER -- source label
        src = safe_text("Standard archaeological timeline", font="Inter",
                       font_size=20, color=MUTED)
        src.move_to(UP * ZONE_FOOTER)

        # -- Timing: 6.67s --
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

        # VTT 2.63: "Humans settled down, learned to farm, then built cities."
        self.play(FadeIn(title, scale=1.1), run_time=0.6); t += 0.6
        self.play(FadeIn(title2, scale=1.1), run_time=0.6); t += 0.6
        self.play(FadeIn(title3, scale=1.1), run_time=0.6); t += 0.6
        self.wait(0.3); t += 0.3
        self.play(FadeIn(stamp, scale=1.4), run_time=0.4); t += 0.4
        self.play(Flash(stamp.get_center(), color=RED,
                        line_length=0.3, num_lines=8, run_time=0.4))        # t=5.1
        self.play(FadeIn(src, shift=UP * 0.05), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 6.7)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE CONTRADICTION (6.67-13.09s = 6.42s)
# VTT: 0.00 "But this temple is 12,000 years old."
#      3.00 "6,000 years before farming even existed."
# Visual: T-pillar + "12,000 YEARS" + broken timeline
# Zones: TITLE, UPPER, MID, LOWER, FOOTER
# ================================================================
class Scene2_Contradiction(Scene):
    DURATION = 6.4
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE -- pill
        pill = label_pill("THE CONTRADICTION", color=RED, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER -- T-shaped pillar centered at hero position
        pillar = t_pillar(height=4.5, color=STONE_GT, stroke_w=2)
        pillar.move_to(UP * ZONE_UPPER)

        # ZONE_MID -- giant number
        big_num = safe_text("12,000", font="Bebas Neue", font_size=120, color=GOLD)
        big_num.move_to(UP * ZONE_MID)
        years = safe_text("YEARS OLD", font="Inter", font_size=36, color=WHITE_SOFT, weight="BOLD")
        years.next_to(big_num, DOWN, buff=0.2)

        # ZONE_LOWER -- broken timeline showing the gap
        tl = Line(LEFT * 3.5, RIGHT * 3.5, color=MUTED, stroke_width=2)
        tl.move_to(UP * ZONE_LOWER)

        gt_tick = Line(UP * 0.2, DOWN * 0.2, color=GOLD, stroke_width=2.5)
        gt_tick.move_to(UP * ZONE_LOWER + LEFT * 3)
        gt_lbl = safe_text("10,000 BC", font="Inter", font_size=20, color=GOLD, weight="BOLD")
        gt_lbl.next_to(gt_tick, DOWN, buff=0.15)

        farm_tick = Line(UP * 0.2, DOWN * 0.2, color=TEAL, stroke_width=2)
        farm_tick.move_to(UP * ZONE_LOWER + RIGHT * 0)
        farm_lbl = safe_text("4,000 BC", font="Inter", font_size=20, color=TEAL)
        farm_lbl.next_to(farm_tick, DOWN, buff=0.15)
        farm_tag = safe_text("FARMING", font="Inter", font_size=16, color=TEAL)
        farm_tag.next_to(farm_tick, UP, buff=0.15)

        # Gap indicator
        gap_bar = Rectangle(
            width=3.0, height=0.3,
            fill_color=RED, fill_opacity=0.3,
            stroke_color=RED, stroke_width=1.5,
        ).move_to(UP * (ZONE_LOWER + 0.6) + LEFT * 1.5)
        gap_lbl = safe_text("6,000 YEARS BEFORE", font="Inter",
                           font_size=18, color=RED, weight="BOLD")
        gap_lbl.next_to(gap_bar, UP, buff=0.1)

        # ZONE_FOOTER -- source
        footer = safe_text("Pre-Pottery Neolithic", font="Inter",
                          font_size=20, color=MUTED)
        footer.move_to(UP * ZONE_FOOTER)

        # -- Timing: 6.42s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.5); t += 0.5
        self.play(FadeIn(pillar, shift=UP * 0.2), run_time=0.8); t += 0.8
        self.play(FadeIn(big_num, scale=1.2), run_time=0.7); t += 0.7
        self.play(FadeIn(years), run_time=0.4); t += 0.4

        # VTT 3.00: "6,000 years before farming even existed."
        self.wait(0.3); t += 0.3
        self.play(Create(tl), run_time=0.3); t += 0.3
        self.play(
            FadeIn(gt_tick), FadeIn(gt_lbl),
            FadeIn(farm_tick), FadeIn(farm_lbl), FadeIn(farm_tag),
            run_time=0.5,
        )                                                                   # t=3.5
        self.play(FadeIn(gap_bar), FadeIn(gap_lbl), run_time=0.6); t += 0.6
        self.play(Flash(gap_bar.get_center(), color=RED,
                        line_length=0.3, num_lines=6, run_time=0.3))        # t=4.4
        self.play(FadeIn(footer, shift=UP * 0.05), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 6.4)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: THE DISMISSED CLUE (13.09-19.43s = 6.34s)
# VTT: 0.00 "Local shepherds always said the hilltop was sacred."
#      3.38 "Archaeologists ignored them for decades."
# Visual: Hilltop + sacred glow vs dismissal
# Zones: TITLE, UPPER, MID, LOWER, FOOTER
# ================================================================
class Scene3_DismissedClue(Scene):
    DURATION = 6.3
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE -- pill
        pill = label_pill("THE DISMISSED CLUE", color=AMBER, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER -- hilltop silhouette with sacred glow
        hill = hilltop_silhouette(width=8, height=2.5, color=EARTH)
        hill.move_to(UP * (ZONE_UPPER - 0.5))

        glow = Circle(radius=2, fill_color=GOLD, fill_opacity=0.08, stroke_width=0)
        glow.move_to(UP * (ZONE_UPPER + 1))

        # Mini T-pillars emerging from hill
        mini_p1 = t_pillar(height=1.0, color=STONE_GT, stroke_w=1)
        mini_p1.move_to(LEFT * 0.5 + UP * (ZONE_UPPER + 0.7))
        mini_p2 = t_pillar(height=0.8, color=STONE_GT, stroke_w=1)
        mini_p2.move_to(RIGHT * 0.8 + UP * (ZONE_UPPER + 0.5))

        # ZONE_MID -- split comparison
        vs_line = DashedLine(UP * 1.5, DOWN * 1.5, color=BORDER, stroke_width=1.5)
        vs_line.move_to(UP * ZONE_MID)

        shep_lbl = safe_text("SHEPHERDS", font="Inter", font_size=24,
                            color=GOLD, weight="BOLD")
        shep_lbl.move_to(LEFT * 2.2 + UP * 0.8)
        shep_quote = safe_text('"Sacred."', font="DM Serif Display",
                              font_size=34, color=GOLD)
        shep_quote.move_to(LEFT * 2.2 + DOWN * 0.2)

        sci_lbl = safe_text("SCIENTISTS", font="Inter", font_size=24,
                           color=MUTED, weight="BOLD")
        sci_lbl.move_to(RIGHT * 2.2 + UP * 0.8)
        sci_quote = safe_text('"Cemetery."', font="DM Serif Display",
                             font_size=30, color=MUTED)
        sci_quote.move_to(RIGHT * 2.2 + DOWN * 0.2)

        # ZONE_LOWER -- "Ignored for decades."
        ignored = safe_text("IGNORED.", font="Bebas Neue",
                           font_size=80, color=RED)
        ignored.move_to(UP * ZONE_LOWER)

        decades = safe_text("For decades.", font="DM Serif Display",
                           font_size=40, color=WHITE_SOFT)
        decades.move_to(UP * (ZONE_LOWER - 1.2))

        # ZONE_FOOTER -- source
        footer = safe_text("1963 survey dismissed site", font="Inter",
                          font_size=20, color=MUTED)
        footer.move_to(UP * ZONE_FOOTER)

        # -- Timing: 6.34s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.5); t += 0.5
        self.add(glow)
        self.play(DrawBorderThenFill(hill), run_time=0.7); t += 0.7
        self.play(FadeIn(mini_p1, shift=UP * 0.1),
                  FadeIn(mini_p2, shift=UP * 0.1), run_time=0.5)          # t=1.7
        self.play(FadeIn(shep_lbl), FadeIn(shep_quote, shift=UP * 0.06),
                  run_time=0.7)                                             # t=2.4
        self.play(Create(vs_line), run_time=0.3); t += 0.3

        # VTT 3.38: "Archaeologists ignored them for decades."
        self.wait(0.38); t += 0.38
        self.play(FadeIn(sci_lbl), FadeIn(sci_quote, shift=UP * 0.06),
                  run_time=0.7)                                             # t=3.78
        self.play(FadeIn(ignored, scale=1.1), run_time=0.6); t += 0.6
        self.play(Flash(ignored.get_center(), color=RED,
                        line_length=0.3, num_lines=8, run_time=0.3))        # t=4.68
        self.play(FadeIn(decades, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(FadeIn(footer, shift=UP * 0.05), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 6.3)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE PROOF (19.43-27.35s = 7.92s)
# VTT: 0.00 "In 1994, Klaus Schmidt started digging."
#      3.57 "Massive carved pillars."
#      5.77 "Built by hunter-gatherers."
# Visual: Date stamp, pillar excavation reveal, punch text
# Zones: TITLE, UPPER+MID (pillars span), LOWER, FOOTER
# ================================================================
class Scene4_Proof(Scene):
    DURATION = 7.9
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE -- pill + giant date
        pill = label_pill("THE PROOF", color=TEAL, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        date = safe_text("1994", font="Bebas Neue", font_size=120, color=TEAL)
        date.move_to(UP * (ZONE_TITLE - 1.2))
        date.set_z_index(10)

        # ZONE_UPPER+MID -- excavation with T-pillars spanning hero area
        ground = Line(LEFT * 4.5, RIGHT * 4.5, color=EARTH_LIGHT, stroke_width=2.5)
        ground.move_to(UP * 1.0)

        earth = Rectangle(width=9, height=2.5, fill_color=EARTH, fill_opacity=0.4,
                          stroke_width=0)
        earth.move_to(DOWN * 0.25)

        p1 = t_pillar(height=3.5, color=STONE_GT, stroke_w=2)
        p1.move_to(LEFT * 2 + UP * (ZONE_MID + 1))
        p2 = t_pillar(height=4.0, color=SAND, stroke_w=2)
        p2.move_to(RIGHT * 0 + UP * (ZONE_MID + 1.2))
        p3 = t_pillar(height=3.0, color=STONE_GT, stroke_w=2)
        p3.move_to(RIGHT * 2.2 + UP * (ZONE_MID + 0.8))

        # ZONE_LOWER -- "MASSIVE CARVED PILLARS"
        massive = safe_text("MASSIVE CARVED", font="Bebas Neue", font_size=70, color=GOLD)
        massive.move_to(UP * (ZONE_LOWER + 1.0))
        pillars_txt = safe_text("PILLARS.", font="Bebas Neue", font_size=70, color=GOLD)
        pillars_txt.move_to(UP * (ZONE_LOWER - 0.2))

        # ZONE_LOWER (bottom) -- "HUNTER-GATHERERS."
        hunters = safe_text("HUNTER-", font="Bebas Neue", font_size=80, color=WHITE_SOFT)
        hunters.move_to(UP * (ZONE_LOWER - 1.8))
        gatherers = safe_text("GATHERERS.", font="Bebas Neue", font_size=80, color=WHITE_SOFT)
        gatherers.move_to(UP * (ZONE_LOWER - 3.0))

        # ZONE_FOOTER -- source
        footer = safe_text("Klaus Schmidt, 1994 excavation", font="Inter",
                          font_size=20, color=MUTED)
        footer.move_to(UP * ZONE_FOOTER)

        # -- Timing: 7.92s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.5); t += 0.5
        self.play(FadeIn(date, scale=1.3), run_time=0.7); t += 0.7
        self.play(Flash(date.get_center(), color=TEAL,
                        line_length=0.5, num_lines=10, run_time=0.4))      # t=1.6
        self.add(earth)
        self.play(Create(ground), run_time=0.3); t += 0.3

        # Pillars rise from earth
        self.play(
            LaggedStart(
                FadeIn(p1, shift=UP * 0.3),
                FadeIn(p2, shift=UP * 0.3),
                FadeIn(p3, shift=UP * 0.3),
                lag_ratio=0.15,
            ),
            run_time=1.0,
        )                                                                   # t=2.9

        # VTT 3.57: "Massive carved pillars."
        self.wait(0.37); t += 0.37
        self.play(FadeIn(massive, scale=1.1), run_time=0.7); t += 0.7
        self.play(FadeIn(pillars_txt, scale=1.1), run_time=0.6); t += 0.6
        self.play(Flash(massive.get_center(), color=GOLD,
                        line_length=0.3, num_lines=8, run_time=0.3))        # t=4.87

        # VTT 5.77: "Built by hunter-gatherers."
        self.wait(0.6); t += 0.6
        self.play(FadeIn(hunters, scale=1.08), run_time=0.7); t += 0.7
        self.play(FadeIn(gatherers, scale=1.08), run_time=0.7); t += 0.7
        self.play(Flash(hunters.get_center(), color=WHITE_SOFT,
                        line_length=0.4, num_lines=10, run_time=0.35))      # t=7.22
        self.play(FadeIn(footer, shift=UP * 0.05), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 7.9)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE SCALE (27.35-33.06s = 5.71s)
# VTT: 0.00 "20 times older than the pyramids."
#      2.64 "And someone buried the whole thing on purpose."
# Visual: Size comparison + BURIED effect
# Zones: TITLE, UPPER (comparison), MID (20x badge), LOWER (BURIED), FOOTER
# ================================================================
class Scene5_Scale(Scene):
    DURATION = 5.7
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE -- pill
        pill = label_pill("THE SCALE", color=GOLD, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER -- comparison: T-pillar vs pyramid side by side
        gt_pillar = t_pillar(height=3.5, color=GOLD_DIM, stroke_w=2)
        gt_pillar.move_to(LEFT * 2 + UP * ZONE_UPPER)
        gt_lbl = safe_text("GOBEKLI TEPE", font="Inter", font_size=20, color=GOLD, weight="BOLD")
        gt_lbl.next_to(gt_pillar, DOWN, buff=0.15)
        gt_age = safe_text("12,000 yrs", font="Inter", font_size=18, color=GOLD)
        gt_age.next_to(gt_lbl, DOWN, buff=0.1)

        pyr = pyramid_shape(height=1.5, base=2.0, color=SAND)
        pyr.move_to(RIGHT * 2 + UP * (ZONE_UPPER - 0.5))
        pyr_lbl = safe_text("PYRAMIDS", font="Inter", font_size=20, color=SAND, weight="BOLD")
        pyr_lbl.next_to(pyr, DOWN, buff=0.15)
        pyr_age = safe_text("4,500 yrs", font="Inter", font_size=18, color=MUTED)
        pyr_age.next_to(pyr_lbl, DOWN, buff=0.1)

        # ZONE_MID -- "20x" badge
        badge_bg = Circle(radius=0.8, fill_color=RED, fill_opacity=0.9,
                          stroke_color=RED, stroke_width=0)
        badge_bg.move_to(UP * ZONE_MID)
        badge = safe_text("20x", font="Bebas Neue", font_size=60, color=WHITE_SOFT)
        badge.move_to(badge_bg)
        older_lbl = safe_text("OLDER", font="Inter", font_size=28, color=RED, weight="BOLD")
        older_lbl.next_to(badge_bg, DOWN, buff=0.2)

        # ZONE_LOWER -- "BURIED." dramatic
        buried_txt = safe_text("BURIED.", font="Bebas Neue", font_size=90, color=RED)
        buried_txt.move_to(UP * ZONE_LOWER)
        sub = safe_text("On purpose.", font="DM Serif Display",
                       font_size=40, color=WHITE_SOFT)
        sub.move_to(UP * (ZONE_LOWER - 1.2))

        # ZONE_FOOTER -- earth/dirt bars covering the bottom
        dirt_bars = VGroup()
        for i in range(4):
            bar = Rectangle(
                width=9, height=0.3,
                fill_color=EARTH, fill_opacity=0.3 + i * 0.15,
                stroke_width=0,
            )
            bar.move_to(UP * (ZONE_FOOTER - 0.5 + i * 0.35))
            dirt_bars.add(bar)

        # -- Timing: 5.71s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.5); t += 0.5
        self.play(FadeIn(gt_pillar, shift=UP * 0.2), run_time=0.5); t += 0.5
        self.play(FadeIn(gt_lbl), FadeIn(gt_age), run_time=0.3); t += 0.3
        self.play(FadeIn(pyr, scale=0.8), run_time=0.4); t += 0.4
        self.play(FadeIn(pyr_lbl), FadeIn(pyr_age), run_time=0.3); t += 0.3
        self.play(FadeIn(badge_bg), FadeIn(badge, scale=1.2),
                  FadeIn(older_lbl), run_time=0.4)                         # t=2.4

        # VTT 2.64: "And someone buried the whole thing on purpose."
        self.wait(0.2); t += 0.2
        self.play(FadeIn(buried_txt, scale=1.15), run_time=0.7); t += 0.7
        self.play(Flash(buried_txt.get_center(), color=RED,
                        line_length=0.4, num_lines=8, run_time=0.3))        # t=3.6
        self.play(FadeIn(sub, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(
            LaggedStart(*[FadeIn(b) for b in dirt_bars], lag_ratio=0.06),
            run_time=0.5,
        )                                                                   # t=4.7
        target = getattr(self.__class__, 'DURATION', 5.7)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE PUNCH (33.06-39.62s = 6.57s)
# VTT: 0.00 "They didn't build temples because they had civilization."
#      3.33 "They built civilization because they had temples."
# Visual: Chiasmus -- mirrored text. Letterbox. Cinematic.
# Zones: TITLE (letterbox), UPPER (stone circle), MID+LOWER (chiasmus text), FOOTER
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 6.6
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.02))
        t = 0

        # Letterbox bars (top/bottom)
        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP * (8 - bh / 2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN * (8 - bh / 2)),
        )

        # ZONE_UPPER -- ghost stone circle as atmospheric backdrop
        ghost_circle = stone_circle(radius=2.5, n_stones=10, color=GOLD)
        ghost_circle.set_opacity(0.06)
        ghost_circle.move_to(UP * ZONE_UPPER)
        self.add(ghost_circle)

        # Ghost T-pillar spanning background
        ghost = t_pillar(height=10, color=GOLD, stroke_color=GOLD, stroke_w=0)
        ghost.set_opacity(0.04)
        ghost.move_to(UP * ZONE_MID)
        self.add(ghost)

        # ZONE_MID (upper) -- first half dimmed / crossed out
        line1a = safe_text("They didn't build temples", font="DM Serif Display",
                          font_size=38, color=MUTED)
        line1a.move_to(UP * 1.5)
        line1b = safe_text("because they had", font="DM Serif Display",
                          font_size=38, color=MUTED)
        line1b.move_to(UP * 0.5)
        line1c = safe_text("civilization.", font="DM Serif Display",
                          font_size=42, color=MUTED)
        line1c.move_to(DOWN * 0.5)

        # ZONE_LOWER -- the flip. Bright, gold.
        line2a = safe_text("They built civilization", font="DM Serif Display",
                          font_size=40, color=WHITE_SOFT)
        line2a.move_to(UP * (ZONE_LOWER + 1.5))
        line2b = safe_text("because they had", font="DM Serif Display",
                          font_size=40, color=WHITE_SOFT)
        line2b.move_to(UP * (ZONE_LOWER + 0.5))
        line2c = safe_text("temples.", font="Bebas Neue", font_size=80, color=GOLD)
        line2c.move_to(UP * (ZONE_LOWER - 0.7))

        glow = Circle(radius=2.5, fill_color=GOLD, fill_opacity=0.04, stroke_width=0)
        glow.move_to(line2c)

        # ZONE_FOOTER -- tiny signature pillar
        sig = t_pillar(height=0.5, color=GOLD, stroke_w=0)
        sig.set_opacity(0.4)
        sig.move_to(UP * ZONE_FOOTER)

        # -- Timing: 6.57s --
        self.play(FadeIn(line1a, shift=UP * 0.08), run_time=0.7); t += 0.7
        self.play(FadeIn(line1b, shift=UP * 0.08), run_time=0.7); t += 0.7
        self.play(FadeIn(line1c, shift=UP * 0.08), run_time=0.7); t += 0.7

        # VTT 3.33: "They built civilization because they had temples."
        self.wait(0.9); t += 0.9
        self.play(FadeIn(line2a, shift=UP * 0.08), run_time=0.7); t += 0.7
        self.play(FadeIn(line2b, shift=UP * 0.08), run_time=0.6); t += 0.6
        self.play(FadeIn(glow), FadeIn(line2c, scale=1.08), run_time=0.8); t += 0.8
        self.play(FadeIn(sig, scale=0.8), run_time=0.3); t += 0.3

        # Hold + fade to black
        target = getattr(self.__class__, 'DURATION', 6.6)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1,
                          stroke_width=0)
        self.play(FadeIn(black), run_time=0.5); t += 0.5


# -- Per-scene render ----------------------------------------------
def render_single_scene(scene_idx):
    scene_classes = [
        Scene1_WrongAnswer, Scene2_Contradiction, Scene3_DismissedClue,
        Scene4_Proof, Scene5_Scale, Scene6_Punch,
    ]
    SC = scene_classes[scene_idx]
    output_dir = Path(__file__).parent
    config.output_file = f"gt_scene_{scene_idx + 1}"
    config.media_dir = str(output_dir / "media")
    SC().render()
    for mp4 in Path(config.media_dir).rglob(f"gt_scene_{scene_idx + 1}.mp4"):
        print(f"SCENE_FILE:{mp4}")
        return


# -- Preview mode --------------------------------------------------
def render_previews():
    """Render peak-frame PNGs for QA."""
    preview_dir = Path(__file__).parent / "previews"
    preview_dir.mkdir(exist_ok=True)

    preview_scenes = [
        Scene1_WrongAnswer, Scene2_Contradiction, Scene3_DismissedClue,
        Scene4_Proof, Scene5_Scale, Scene6_Punch,
    ]

    config.media_dir = str(Path(__file__).parent / "media")

    for i, SC in enumerate(preview_scenes):
        name = f"gobekli_scene_{i + 1}"
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


# -- MAIN ----------------------------------------------------------
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

    # Full render -- all 6 scenes via subprocesses
    scene_names = [
        "Scene1_WrongAnswer", "Scene2_Contradiction", "Scene3_DismissedClue",
        "Scene4_Proof", "Scene5_Scale", "Scene6_Punch",
    ]

    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = output_dir / "tts_gobekli_tepe.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="gt", audio_path=str(audio))
    final = output_dir / "gobekli_tepe_manim.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
