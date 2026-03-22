#!/usr/bin/env python3
"""Gobekli Tepe v2 -- clarity-audited script (Manim).

6 scenes, 41.3s total, word-level sync to tts_gobekli_tepe_v2.vtt.
Changes from v1: "Gobekli Tepe" named in scenes 2+5, "in Turkey", "German archaeologist".

VTT cues (absolute -> relative to scene start):
  Scene 1 (0.0-6.67s = 6.67s):
    0.100 (0.10)  Every textbook says the same thing.
    2.625 (2.63)  Humans settled down, learned to farm, then built cities.
  Scene 2 (6.67-13.16s = 6.49s):
    6.670 (0.00)  Gobekli Tepe is 12,000 years old.
    9.738 (3.07)  6,000 years before farming even existed.
  Scene 3 (13.16-19.95s = 6.79s):
    13.159 (0.00) Local shepherds in Turkey always said the hilltop was sacred.
    16.988 (3.83) Archaeologists ignored them for decades.
  Scene 4 (19.95-28.43s = 8.48s):
    19.954 (0.00) In 1994, a German archaeologist started digging.
    24.079 (4.13) Massive carved pillars.
    26.284 (6.33) Built by hunter-gatherers.
  Scene 5 (28.43-34.74s = 6.31s):
    28.431 (0.00) 20 times older than the pyramids.
    31.068 (2.64) And then, someone buried Gobekli Tepe on purpose.
  Scene 6 (34.74-41.31s = 6.57s):
    34.738 (0.00) They didn't build temples because they had civilization.
    38.068 (3.33) They built civilization because they had temples.
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

TTS_SCRIPT = """Every textbook says humans settled, farmed, then built cities. Gobekli Tepe is 12,000 years old. 6,000 years before farming existed. Shepherds always said the hilltop was sacred. Archaeologists ignored them for decades. In 1994, a German archaeologist started digging. Massive carved pillars built by hunter-gatherers. Twenty times older than the pyramids. Then someone buried it on purpose. They didn't build temples because they had civilization. They built civilization because they had temples."""

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
GOLD = "#FFD700"
GOLD_DIM = "#B8960F"
RED = "#E63946"
WHITE_SOFT = "#F0F0F0"
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

# Safe zone constants
SAFE_W = 8.0
SAFE_TOP = 7.2
SAFE_BOT = -6.4

# Vertical layout zones -- USE THESE for all positioning
ZONE_TITLE  = 6.2    # y 5.5-7.0  -- scene label pills
ZONE_UPPER  = 3.5    # y 1.5-5.5  -- hero visual top portion
ZONE_MID    = 0.0    # y -1.5-1.5 -- central focal point, big numbers
ZONE_LOWER  = -3.5   # y -5.5--1.5 -- supporting visuals, bars, icons
ZONE_FOOTER = -6.0   # y -6.4--5.5 -- captions, source labels


# -- Helpers -------------------------------------------------------

def gradient_bg():
    bg = Rectangle(width=12, height=20, fill_color=BG, fill_opacity=1, stroke_width=0)
    glow = Circle(radius=5, fill_color="#1A2A1C", fill_opacity=0.10, stroke_width=0).move_to(UP * 2)
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


# -- Domain Shape Helpers (4 topic-specific shapes) ----------------

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


def shovel_shape(height=2.5, color=EARTH_LIGHT):
    """Excavation shovel -- symbolizes archaeological dig."""
    handle_w = height * 0.06
    handle_h = height * 0.6
    handle = Rectangle(
        width=handle_w, height=handle_h,
        fill_color=SAND_DARK, fill_opacity=1,
        stroke_color=EARTH, stroke_width=1,
    )
    blade_w = height * 0.25
    blade_h = height * 0.4
    blade = Polygon(
        np.array([-blade_w / 2, 0, 0]),
        np.array([-blade_w * 0.35, -blade_h, 0]),
        np.array([blade_w * 0.35, -blade_h, 0]),
        np.array([blade_w / 2, 0, 0]),
        fill_color=color, fill_opacity=1,
        stroke_color=STONE_GT_DARK, stroke_width=1.5,
    )
    blade.next_to(handle, DOWN, buff=0)
    return VGroup(handle, blade)


# ================================================================
# SCENE 1: THE WRONG ANSWER (0.0-6.67s = 6.67s)
# VTT: 0.10 "Every textbook..." / 2.63 "Humans settled..."
# Visual: Timeline showing wrong order (farming->cities->temples)
# Zones: TITLE (pill), UPPER (timeline), MID (words), LOWER (stamp), FOOTER (source)
# ================================================================
class Scene1_WrongAnswer(Scene):
    DURATION = 6.7
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE -- label pill
        pill = label_pill("THE TEXTBOOK STORY", color=MUTED, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER -- timeline with wrong sequence
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
            tick.move_to(timeline.get_center() + RIGHT * x)
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

        # ZONE_MID -- big impact words
        title = safe_text("SETTLED.", font="Bebas Neue", font_size=80, color=GOLD)
        title.move_to(UP * (ZONE_MID + 1.0))
        title2 = safe_text("FARMED.", font="Bebas Neue", font_size=80, color=GOLD)
        title2.move_to(UP * ZONE_MID)
        title3 = safe_text("BUILT.", font="Bebas Neue", font_size=80, color=GOLD)
        title3.move_to(UP * (ZONE_MID - 1.0))

        # ZONE_LOWER -- WRONG stamp
        wrong = safe_text("WRONG", font="Bebas Neue", font_size=70, color=RED)
        wrong_border = RoundedRectangle(
            width=wrong.width + 0.5, height=wrong.height + 0.35,
            corner_radius=0.08, stroke_color=RED, stroke_width=5, fill_opacity=0,
        ).move_to(wrong)
        stamp = VGroup(wrong_border, wrong).rotate(12 * DEGREES)
        stamp.move_to(DOWN * abs(ZONE_LOWER))

        # ZONE_FOOTER -- source label
        source = safe_text("CONVENTIONAL HISTORY", font="Inter",
                          font_size=20, color=MUTED)
        source.move_to(UP * ZONE_FOOTER)

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
        self.play(FadeIn(title, scale=1.1), run_time=0.5); t += 0.5
        self.play(FadeIn(title2, scale=1.1), run_time=0.5); t += 0.5
        self.play(FadeIn(title3, scale=1.1), run_time=0.5); t += 0.5
        self.play(FadeIn(source, shift=UP * 0.06), run_time=0.4); t += 0.4
        self.wait(0.5); t += 0.5
        self.play(FadeIn(stamp, scale=1.4), run_time=0.4); t += 0.4
        self.play(Flash(stamp.get_center(), color=RED,
                        line_length=0.3, num_lines=8, run_time=0.4))        # t=5.4
        target = getattr(self.__class__, 'DURATION', 6.7)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE CONTRADICTION (6.67-13.16s = 6.49s)
# VTT: 0.00 "Gobekli Tepe is 12,000 years old."
#      3.07 "6,000 years before farming even existed."
# Zones: TITLE (pill+name), UPPER (pillar), MID (12000), LOWER (timeline), FOOTER (gap label)
# ================================================================
class Scene2_Contradiction(Scene):
    DURATION = 6.5
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE -- pill + name
        pill = label_pill("THE CONTRADICTION", color=RED, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        gt_name = safe_text("GOBEKLI TEPE", font="Bebas Neue", font_size=70, color=GOLD)
        gt_name.move_to(UP * (ZONE_TITLE - 1.0))

        # ZONE_UPPER -> ZONE_MID -- T-shaped pillar hero visual centered at y=1
        pillar = t_pillar(height=4.0, color=STONE_GT, stroke_w=2)
        pillar.move_to(UP * 1.0)

        # ZONE_MID -- "12,000 YEARS" giant number
        big_num = safe_text("12,000", font="Bebas Neue", font_size=120, color=GOLD)
        big_num.move_to(DOWN * 1.5)
        years = safe_text("YEARS OLD", font="Inter", font_size=36, color=WHITE_SOFT, weight="BOLD")
        years.next_to(big_num, DOWN, buff=0.2)

        # ZONE_LOWER -- broken timeline showing the gap
        tl = Line(LEFT * 3.5, RIGHT * 3.5, color=MUTED, stroke_width=2)
        tl.move_to(UP * ZONE_LOWER)

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

        gap_bar = Rectangle(
            width=3.0, height=0.3,
            fill_color=RED, fill_opacity=0.3,
            stroke_color=RED, stroke_width=1.5,
        ).move_to(tl.get_center() + LEFT * 1.5 + UP * 0.5)

        # ZONE_FOOTER -- gap label
        gap_lbl = safe_text("6,000 YEARS BEFORE FARMING", font="Inter",
                           font_size=20, color=RED, weight="BOLD")
        gap_lbl.move_to(UP * ZONE_FOOTER)

        # -- Timing: 6.49s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.5); t += 0.5
        self.play(FadeIn(gt_name, scale=1.1), run_time=0.6); t += 0.6
        self.play(FadeIn(pillar, shift=UP * 0.2), run_time=0.7); t += 0.7
        self.play(FadeIn(big_num, scale=1.2), run_time=0.7); t += 0.7
        self.play(FadeIn(years), run_time=0.3); t += 0.3

        # VTT 3.07: "6,000 years before farming even existed."
        self.play(Create(tl), run_time=0.3); t += 0.3
        self.play(
            FadeIn(gt_tick), FadeIn(gt_lbl),
            FadeIn(farm_tick), FadeIn(farm_lbl), FadeIn(farm_tag),
            run_time=0.5,
        )                                                                   # t=3.6
        self.play(FadeIn(gap_bar), run_time=0.4); t += 0.4
        self.play(Flash(gap_bar.get_center(), color=RED,
                        line_length=0.3, num_lines=6, run_time=0.3))        # t=4.3
        self.play(FadeIn(gap_lbl, shift=UP * 0.06), run_time=0.7); t += 0.7
        target = getattr(self.__class__, 'DURATION', 6.5)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: THE DISMISSED CLUE (13.16-19.95s = 6.79s)
# VTT: 0.00 "Local shepherds in Turkey always said the hilltop was sacred."
#      3.83 "Archaeologists ignored them for decades."
# Zones: TITLE (pill+loc), UPPER (hill+pillars), MID (vs divider), LOWER (ignored), FOOTER (decades)
# ================================================================
class Scene3_DismissedClue(Scene):
    DURATION = 6.8
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE -- pill + location
        pill = label_pill("THE DISMISSED CLUE", color=AMBER, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        loc = safe_text("TURKEY", font="Inter", font_size=26, color=AMBER, weight="BOLD")
        loc.move_to(UP * (ZONE_TITLE - 0.8))

        # ZONE_UPPER -- hilltop silhouette with sacred glow + mini pillars
        hill = hilltop_silhouette(width=8, height=2.5, color=EARTH)
        hill.move_to(UP * (ZONE_UPPER - 0.5))

        glow = Circle(radius=2, fill_color=GOLD, fill_opacity=0.08, stroke_width=0)
        glow.move_to(UP * (ZONE_UPPER + 1.0))

        mini_p1 = t_pillar(height=1.0, color=STONE_GT, stroke_w=1)
        mini_p1.move_to(LEFT * 0.5 + UP * (ZONE_UPPER + 0.7))
        mini_p2 = t_pillar(height=0.8, color=STONE_GT, stroke_w=1)
        mini_p2.move_to(RIGHT * 0.8 + UP * (ZONE_UPPER + 0.5))

        # ZONE_MID -- vs divider between shepherds and archaeologists
        vs_line = DashedLine(UP * 0.2, DOWN * 3.0, color=BORDER, stroke_width=1.5)
        vs_line.move_to(DOWN * abs(ZONE_MID))

        shep_lbl = safe_text("SHEPHERDS", font="Inter", font_size=24,
                            color=GOLD, weight="BOLD")
        shep_lbl.move_to(LEFT * 2.2 + UP * (ZONE_MID + 0.5))

        sci_lbl = safe_text("SCIENTISTS", font="Inter", font_size=24,
                           color=MUTED, weight="BOLD")
        sci_lbl.move_to(RIGHT * 2.2 + UP * (ZONE_MID + 0.5))

        # Sacred glow on shepherd side, X on scientist side
        sacred_dot = Circle(radius=0.35, fill_color=GOLD, fill_opacity=0.3,
                           stroke_color=GOLD, stroke_width=1.5)
        sacred_dot.move_to(LEFT * 2.2 + UP * (ZONE_MID - 0.5))
        sacred_lbl = safe_text("SACRED", font="Inter", font_size=18, color=GOLD)
        sacred_lbl.next_to(sacred_dot, DOWN, buff=0.15)

        dismiss_x = safe_text("X", font="Bebas Neue", font_size=50, color=RED)
        dismiss_x.move_to(RIGHT * 2.2 + UP * (ZONE_MID - 0.5))
        dismiss_lbl = safe_text("DISMISSED", font="Inter", font_size=18, color=RED)
        dismiss_lbl.next_to(dismiss_x, DOWN, buff=0.15)

        # ZONE_LOWER -- ignored text
        ignored = safe_text("IGNORED", font="Bebas Neue", font_size=70, color=RED)
        ignored.move_to(UP * ZONE_LOWER)

        # ZONE_FOOTER -- decades label
        decades = safe_text("FOR DECADES", font="Inter", font_size=28,
                           color=WHITE_SOFT, weight="BOLD")
        decades.move_to(UP * ZONE_FOOTER)

        # -- Timing: 6.79s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.5); t += 0.5
        self.play(FadeIn(loc, shift=DOWN * 0.06), run_time=0.4); t += 0.4
        self.add(glow)
        self.play(DrawBorderThenFill(hill), run_time=0.7); t += 0.7
        self.play(FadeIn(mini_p1, shift=UP * 0.1),
                  FadeIn(mini_p2, shift=UP * 0.1), run_time=0.5)          # t=2.1
        self.play(FadeIn(shep_lbl), FadeIn(sacred_dot), FadeIn(sacred_lbl),
                  run_time=0.5)                                             # t=2.6
        self.play(Create(vs_line), run_time=0.3); t += 0.3

        # VTT 3.83: "Archaeologists ignored them for decades."
        self.wait(0.63); t += 0.63
        self.play(FadeIn(sci_lbl), FadeIn(dismiss_x, scale=1.2),
                  FadeIn(dismiss_lbl), run_time=0.7)                        # t=4.23
        self.play(FadeIn(ignored, scale=1.1), run_time=0.7); t += 0.7
        self.play(Flash(ignored.get_center(), color=RED,
                        line_length=0.3, num_lines=8, run_time=0.4))        # t=5.33
        self.play(FadeIn(decades, shift=UP * 0.06), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 6.8)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE PROOF (19.95-28.43s = 8.48s)
# VTT: 0.00 "In 1994, a German archaeologist started digging."
#      4.13 "Massive carved pillars."
#      6.33 "Built by hunter-gatherers."
# Zones: TITLE (pill+date), UPPER (pillars), MID (ground), LOWER (text), FOOTER (hunter-gatherers)
# ================================================================
class Scene4_Proof(Scene):
    DURATION = 8.5
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE -- pill + giant date
        pill = label_pill("THE PROOF", color=TEAL, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        date = safe_text("1994", font="Bebas Neue", font_size=120, color=TEAL)
        date.move_to(UP * (ZONE_TITLE - 1.2))
        date.set_z_index(10)

        # Shovel icon next to date
        shovel = shovel_shape(height=1.5, color=EARTH_LIGHT)
        shovel.next_to(date, RIGHT, buff=0.4)
        shovel.set_z_index(10)

        # ZONE_UPPER -> ZONE_MID -- pillars rising from ground (hero at y=1)
        ground = Line(LEFT * 4.5, RIGHT * 4.5, color=EARTH_LIGHT, stroke_width=2.5)
        ground.move_to(UP * (ZONE_MID - 0.5))

        earth = Rectangle(width=9, height=2.0, fill_color=EARTH, fill_opacity=0.4,
                          stroke_width=0)
        earth.move_to(UP * (ZONE_MID - 1.5))

        p1 = t_pillar(height=3.5, color=STONE_GT, stroke_w=2)
        p1.move_to(LEFT * 2 + UP * (ZONE_MID + 1.5))
        p2 = t_pillar(height=4.0, color=SAND, stroke_w=2)
        p2.move_to(RIGHT * 0 + UP * (ZONE_MID + 1.8))
        p3 = t_pillar(height=3.0, color=STONE_GT, stroke_w=2)
        p3.move_to(RIGHT * 2.2 + UP * (ZONE_MID + 1.2))

        # ZONE_LOWER -- "MASSIVE CARVED PILLARS" text
        massive = safe_text("MASSIVE CARVED", font="Bebas Neue", font_size=70, color=GOLD)
        massive.move_to(UP * (ZONE_LOWER + 1.0))
        pillars_txt = safe_text("PILLARS", font="Bebas Neue", font_size=70, color=GOLD)
        pillars_txt.move_to(UP * (ZONE_LOWER))

        div = section_div(5, TEAL).move_to(UP * (ZONE_LOWER - 1.0))

        # ZONE_FOOTER -- hunter-gatherers
        hunters = safe_text("HUNTER-GATHERERS", font="Bebas Neue", font_size=60, color=WHITE_SOFT)
        hunters.move_to(UP * (ZONE_FOOTER + 0.3))

        # -- Timing: 8.48s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.5); t += 0.5
        self.play(FadeIn(date, scale=1.3), run_time=0.7); t += 0.7
        self.play(FadeIn(shovel, shift=DOWN * 0.2), run_time=0.4); t += 0.4
        self.play(Flash(date.get_center(), color=TEAL,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=1.9
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
            run_time=1.2,
        )                                                                   # t=3.4

        self.wait(0.4); t += 0.4

        # VTT 4.13: "Massive carved pillars."
        self.play(FadeIn(massive, scale=1.1), run_time=0.7); t += 0.7
        self.play(FadeIn(pillars_txt, scale=1.1), run_time=0.6); t += 0.6
        self.play(Flash(massive.get_center(), color=GOLD,
                        line_length=0.3, num_lines=8, run_time=0.3))        # t=5.4

        # VTT 6.33: "Built by hunter-gatherers."
        self.wait(0.63); t += 0.63
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(hunters, scale=1.08), run_time=0.7); t += 0.7
        self.play(Flash(hunters.get_center(), color=WHITE_SOFT,
                        line_length=0.4, num_lines=10, run_time=0.35))      # t=7.38
        target = getattr(self.__class__, 'DURATION', 8.5)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE SCALE (28.43-34.74s = 6.31s)
# VTT: 0.00 "20 times older than the pyramids."
#      2.64 "And then, someone buried Gobekli Tepe on purpose."
# Zones: TITLE (pill), UPPER (comparison), MID (badge), LOWER (buried), FOOTER (dirt)
# ================================================================
class Scene5_Scale(Scene):
    DURATION = 6.3
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE -- pill
        pill = label_pill("THE SCALE", color=GOLD, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER -- side-by-side comparison: pillar vs pyramid
        gt_pillar = t_pillar(height=4.0, color=GOLD_DIM, stroke_w=2)
        gt_pillar.move_to(LEFT * 2 + UP * ZONE_UPPER)
        gt_lbl = safe_text("GOBEKLI TEPE", font="Inter", font_size=20, color=GOLD, weight="BOLD")
        gt_lbl.move_to(LEFT * 2 + UP * (ZONE_UPPER - 2.5))
        gt_age = safe_text("12,000 yrs", font="Inter", font_size=18, color=GOLD)
        gt_age.next_to(gt_lbl, DOWN, buff=0.1)

        pyr = pyramid_shape(height=1.5, base=2.0, color=SAND)
        pyr.move_to(RIGHT * 2 + UP * (ZONE_UPPER - 0.5))
        pyr_lbl = safe_text("PYRAMIDS", font="Inter", font_size=20, color=SAND, weight="BOLD")
        pyr_lbl.next_to(pyr, DOWN, buff=0.2)
        pyr_age = safe_text("4,500 yrs", font="Inter", font_size=18, color=MUTED)
        pyr_age.next_to(pyr_lbl, DOWN, buff=0.1)

        # ZONE_MID -- 20x badge
        badge_bg = Circle(radius=0.7, fill_color=RED, fill_opacity=0.9,
                          stroke_color=RED, stroke_width=0)
        badge_bg.move_to(UP * ZONE_MID)
        badge = safe_text("20x", font="Bebas Neue", font_size=55, color=WHITE_SOFT)
        badge.move_to(badge_bg)

        # ZONE_LOWER -- "GOBEKLI TEPE" + "BURIED"
        gt_name_big = safe_text("GOBEKLI TEPE", font="Bebas Neue", font_size=60, color=GOLD)
        gt_name_big.move_to(UP * (ZONE_LOWER + 1.0))

        buried_txt = safe_text("BURIED.", font="Bebas Neue", font_size=90, color=RED)
        buried_txt.move_to(UP * ZONE_LOWER)

        sub = safe_text("On purpose.", font="DM Serif Display",
                       font_size=40, color=WHITE_SOFT)
        sub.move_to(UP * (ZONE_LOWER - 1.2))

        # ZONE_FOOTER -- dirt bars covering the bottom
        dirt_bars = VGroup()
        for i in range(5):
            bar = Rectangle(
                width=9, height=0.3,
                fill_color=EARTH, fill_opacity=0.3 + i * 0.1,
                stroke_width=0,
            )
            bar.move_to(UP * (ZONE_FOOTER - 0.3 + i * 0.35))
            dirt_bars.add(bar)

        # -- Timing: 6.31s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.5); t += 0.5
        self.play(FadeIn(gt_pillar, shift=UP * 0.2), run_time=0.6); t += 0.6
        self.play(FadeIn(gt_lbl), FadeIn(gt_age), run_time=0.3); t += 0.3
        self.play(FadeIn(pyr, scale=0.8), run_time=0.5); t += 0.5
        self.play(FadeIn(pyr_lbl), FadeIn(pyr_age), run_time=0.3); t += 0.3
        self.play(FadeIn(badge_bg), FadeIn(badge, scale=1.2), run_time=0.4); t += 0.4

        # VTT 2.64: "And then, someone buried Gobekli Tepe on purpose."
        self.play(FadeIn(gt_name_big, scale=1.1), run_time=0.5); t += 0.5
        self.play(FadeIn(buried_txt, scale=1.15), run_time=0.7); t += 0.7
        self.play(Flash(buried_txt.get_center(), color=RED,
                        line_length=0.4, num_lines=8, run_time=0.3))        # t=4.1
        self.play(FadeIn(sub, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(
            LaggedStart(*[FadeIn(b) for b in dirt_bars], lag_ratio=0.06),
            run_time=0.5,
        )                                                                   # t=5.2
        target = getattr(self.__class__, 'DURATION', 6.3)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE PUNCH (34.74-41.31s = 6.57s)
# VTT: 0.00 "They didn't build temples because they had civilization."
#      3.33 "They built civilization because they had temples."
# Zones: TITLE (letterbox), UPPER (ghost pillar), MID (divider+chiasmus pt1),
#        LOWER (chiasmus pt2), FOOTER (temples + sig)
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 6.6
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.02))
        t = 0

        # Letterbox bars
        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP * (8 - bh / 2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN * (8 - bh / 2)),
        )

        # Ghost T-pillar (subtle background element spanning UPPER -> LOWER)
        ghost = t_pillar(height=12, color=GOLD, stroke_color=GOLD, stroke_w=0)
        ghost.set_opacity(0.04)
        ghost.move_to(UP * ZONE_MID)
        self.add(ghost)

        # ZONE_TITLE area -- first divider
        div1 = section_div(4, MUTED).move_to(UP * (ZONE_TITLE - 1.5))

        # ZONE_UPPER -> ZONE_MID -- first half of chiasmus (dimmed)
        line1a = safe_text("TEMPLES", font="DM Serif Display",
                          font_size=44, color=WHITE_SOFT)
        line1a.move_to(UP * ZONE_UPPER)
        cross1 = Line(LEFT * 1.5, RIGHT * 1.5, color=RED, stroke_width=3)
        cross1.move_to(line1a)

        line1b = safe_text("CIVILIZATION", font="DM Serif Display",
                          font_size=44, color=MUTED)
        line1b.move_to(UP * (ZONE_UPPER - 1.5))

        # ZONE_MID -- arrow pointing down (the flip)
        flip_arrow = Arrow(UP * 0.5, DOWN * 0.5, color=GOLD, stroke_width=3, buff=0)
        flip_arrow.move_to(UP * ZONE_MID)

        # ZONE_LOWER -- second half of chiasmus (bright, gold)
        div2 = section_div(4, GOLD).move_to(UP * (ZONE_LOWER + 1.5))

        line2a = safe_text("CIVILIZATION", font="DM Serif Display",
                          font_size=44, color=WHITE_SOFT)
        line2a.move_to(UP * ZONE_LOWER)

        # ZONE_FOOTER -- "TEMPLES" in gold, big, the punchline
        line2b = safe_text("TEMPLES.", font="Bebas Neue", font_size=80, color=GOLD)
        line2b.move_to(UP * (ZONE_FOOTER + 0.5))

        glow = Circle(radius=2.5, fill_color=GOLD, fill_opacity=0.04, stroke_width=0)
        glow.move_to(line2b)

        # Signature pillar
        sig = t_pillar(height=0.5, color=GOLD, stroke_w=0)
        sig.set_opacity(0.4)
        sig.move_to(UP * (ZONE_FOOTER - 0.8))

        # -- Timing: 6.57s --
        self.play(Create(div1), run_time=0.4); t += 0.4
        self.play(FadeIn(line1a, shift=UP * 0.08), run_time=0.7); t += 0.7
        self.play(FadeIn(line1b, shift=UP * 0.08), run_time=0.7); t += 0.7
        self.play(Create(cross1), run_time=0.4); t += 0.4

        # VTT 3.33: "They built civilization because they had temples."
        self.wait(0.5); t += 0.5
        self.play(FadeIn(flip_arrow, shift=DOWN * 0.2), run_time=0.3); t += 0.3
        self.play(Create(div2), run_time=0.33); t += 0.33
        self.play(FadeIn(line2a, shift=UP * 0.08), run_time=0.7); t += 0.7
        self.play(FadeIn(glow), FadeIn(line2b, scale=1.08), run_time=0.8); t += 0.8
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
    config.output_file = f"gt_v2_scene_{scene_idx + 1}"
    config.media_dir = str(output_dir / "media")
    SC().render()
    for mp4 in Path(config.media_dir).rglob(f"gt_v2_scene_{scene_idx + 1}.mp4"):
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
        name = f"gobekli_v2_scene_{i + 1}"
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
    audio = output_dir / "tts_gobekli_tepe_v2.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="gt_v2", audio_path=str(audio))
    final = output_dir / "gobekli_tepe_v2_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    elapsed = time.time() - t0
    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}")
    print(f"  RENDER COMPLETE: {final}")
    print(f"  {mb:.1f} MB  |  {elapsed:.1f}s render time")
    print(f"{'='*60}")
