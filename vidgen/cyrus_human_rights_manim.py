#!/usr/bin/env python3
"""The First Human Rights — Cyrus the Great, 539 BC (Manim). Contradiction arc.

6 scenes, ~32.0s (29.0s audio + 3s hold).

VTT cues (absolute → relative):
  Scene 1 (0.0–4.5s = 4.50s):
    0.200 (0.20) Human rights.
    1.000 (1.00) The Enlightenment. The French Revolution.
    2.800 (2.80) 1776.
  Scene 2 (4.5–9.0s = 4.50s):
    4.700 (0.20) But there's a problem.
    5.800 (1.30) A Persian king wrote human rights on a clay cylinder
    7.500 (3.00) 2,500 years earlier.
  Scene 3 (9.0–14.0s = 5.00s):
    9.200 (0.20) The Cyrus Cylinder. 539 BC.
    10.500 (1.50) Freedom of religion. No slavery.
    12.000 (3.00) Conquered peoples go home.
    13.000 (4.00) The UN has a replica.
  Scene 4 (14.0–19.0s = 5.00s):
    14.200 (0.20) Cyrus freed the Jews. Rebuilt their temple.
    16.200 (2.20) He's the only non-Jew called messiah in the Hebrew Bible.
    18.000 (4.00) Isaiah 45:1.
  Scene 5 (19.0–23.5s = 4.50s):
    19.200 (0.20) His empire: 5.5 million square kilometers.
    21.200 (2.20) Forty-four percent of the world lived under Persian rule.
  Scene 6 (23.5–32.0s = 8.50s):
    23.700 (0.20) The first person to say 'you are free to believe what you want'
    26.500 (3.00) said it in Persian.
    28.000 (4.50) Not English.
    + 3s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """Human rights. The Enlightenment. 1776. But a Persian king wrote human rights on clay 2,500 years earlier. The Cyrus Cylinder. 539 BC. Freedom of religion. No slavery. Conquered peoples go home. Cyrus freed the Jews and rebuilt their temple. The only non-Jew called messiah in the Hebrew Bible. His empire spanned 5.5 million square kilometers. The first person to say you are free to believe what you want said it in Persian. Not English."""

from manim import (
    Scene, Text, Group, VGroup, Rectangle, RoundedRectangle, Circle,
    Line, Arrow, DashedLine, Dot, Polygon, Ellipse, Square, Arc,
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
PERSIAN_BLUE = "#1A4A7A"; PERSIAN_BLUE_LT = "#2A6AAA"
GOLD_CYLINDER = "#C8962A"; CLAY_TAN = "#B87333"
LIBERTY_RED = "#CC2233"; ANCIENT_CREAM = "#F5E8C0"
WHITE_SOFT = "#F0F0F0"; MUTED = "#7B8DA0"; DIM = "#404050"
DEAD_GRAY = "#4A5568"; GOLD = "#FFD700"
SAFE_W = 8.0

ZONE_TITLE  = 6.2
ZONE_UPPER  = 3.5
ZONE_MID    = 0.0
ZONE_LOWER  = -3.5
ZONE_FOOTER = -6.0


def gradient_bg(c=BG, g="#0A0A14"):
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

def label_pill(txt, color=GOLD_CYLINDER, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    p = RoundedRectangle(width=t.width + 0.5, height=t.height + 0.3, corner_radius=0.18,
                         fill_color=bg, fill_opacity=0.95, stroke_color=color, stroke_width=1.5).move_to(t)
    return VGroup(p, t)

def safe_text(content, **kwargs):
    t = Text(content, **kwargs)
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    return t


# ── Domain Shape Helpers ──────────────────────────────────────

def clay_cylinder(height=3.0, width=2.0, color=CLAY_TAN):
    """Barrel-shaped Cyrus Cylinder — rectangle body + arc top/bottom + cuneiform lines."""
    sc = height / 3.0
    body = Rectangle(width=width * sc, height=height * sc * 0.7, fill_color=color,
                     fill_opacity=0.85, stroke_color=GOLD_CYLINDER, stroke_width=1.5)
    top_fill = Ellipse(width=width * sc, height=0.5 * sc, fill_color=color,
                       fill_opacity=0.9, stroke_color=GOLD_CYLINDER, stroke_width=1)
    top_fill.move_to(body.get_top())
    bot_fill = Ellipse(width=width * sc, height=0.5 * sc, fill_color=color,
                       fill_opacity=0.7, stroke_color=GOLD_CYLINDER, stroke_width=1)
    bot_fill.move_to(body.get_bottom())
    lines = VGroup()
    for i in range(6):
        y_off = -0.25 * sc + i * 0.12 * sc
        l = Line(LEFT * 0.7 * sc, RIGHT * 0.7 * sc, color=GOLD_CYLINDER,
                 stroke_width=0.8).move_to(body.get_center() + UP * y_off)
        l.set_opacity(0.5)
        lines.add(l)
    return VGroup(body, top_fill, bot_fill, lines)

def persian_arch(height=4.0, width=2.5, color=PERSIAN_BLUE):
    """Persian pointed iwaan arch — tall pointed top, pillars, keystone."""
    sc = height / 4.0
    l_pillar = Rectangle(width=0.3 * sc, height=2.5 * sc, fill_color=color, fill_opacity=0.8,
                         stroke_color=PERSIAN_BLUE_LT, stroke_width=1)
    l_pillar.move_to(LEFT * width / 2 * sc + DOWN * 0.25 * sc)
    r_pillar = l_pillar.copy().move_to(RIGHT * width / 2 * sc + DOWN * 0.25 * sc)
    arch_top = Polygon(
        np.array([-width / 2 * sc - 0.15 * sc, 1.0 * sc, 0]),
        np.array([0, height * sc * 0.85, 0]),
        np.array([width / 2 * sc + 0.15 * sc, 1.0 * sc, 0]),
        fill_color=color, fill_opacity=0.7,
        stroke_color=PERSIAN_BLUE_LT, stroke_width=1.5,
    )
    keystone = Circle(radius=0.15 * sc, fill_color=GOLD_CYLINDER, fill_opacity=0.8,
                      stroke_width=0).move_to(UP * height * sc * 0.75)
    base = Rectangle(width=(width + 0.6) * sc, height=0.3 * sc, fill_color=color,
                     fill_opacity=0.6, stroke_color=PERSIAN_BLUE_LT, stroke_width=0.8)
    base.move_to(DOWN * 1.5 * sc)
    return VGroup(l_pillar, r_pillar, arch_top, keystone, base)

def map_persia(color=PERSIAN_BLUE, opacity=0.25):
    """Achaemenid Empire outline — large irregular Polygon, Middle East + Central Asia."""
    pts = [
        np.array([-3.5, 0.5, 0]),
        np.array([-2.5, 2.0, 0]),
        np.array([-0.5, 2.5, 0]),
        np.array([2.0, 2.0, 0]),
        np.array([3.5, 1.0, 0]),
        np.array([3.0, -0.5, 0]),
        np.array([2.0, -1.5, 0]),
        np.array([0.0, -2.0, 0]),
        np.array([-2.0, -1.5, 0]),
        np.array([-3.5, -0.5, 0]),
    ]
    return Polygon(*pts, fill_color=color, fill_opacity=opacity,
                   stroke_color=PERSIAN_BLUE_LT, stroke_width=1.5)

def star_of_david(size=1.0, color=GOLD):
    """Star of David — two overlapping triangles."""
    tri_up = Polygon(
        np.array([0, size, 0]),
        np.array([-size * 0.87, -size * 0.5, 0]),
        np.array([size * 0.87, -size * 0.5, 0]),
        stroke_color=color, stroke_width=2.5, fill_opacity=0,
    )
    tri_down = Polygon(
        np.array([0, -size, 0]),
        np.array([-size * 0.87, size * 0.5, 0]),
        np.array([size * 0.87, size * 0.5, 0]),
        stroke_color=color, stroke_width=2.5, fill_opacity=0,
    )
    return VGroup(tri_up, tri_down)


# ================================================================
# SCENE 1: THE WRONG ANSWER (0.0–4.5s = 4.50s)
# Zones: TITLE(pill) UPPER(1776) MID(scroll) LOWER(tricolor) FOOTER(assumption)
# ================================================================
class Scene1_WrongAnswer(Scene):
    DURATION = 4.5
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("HUMAN RIGHTS", color=LIBERTY_RED, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # "1776" — hero number at UPPER
        yr_1776 = safe_text("1776", font="Bebas Neue", font_size=160, color=LIBERTY_RED)
        yr_1776.move_to(UP * ZONE_UPPER)

        # Enlightenment / Revolution labels flanking
        lbl_enl = safe_text("ENLIGHTENMENT", font="Inter", font_size=28,
                            color=MUTED, weight="BOLD")
        lbl_enl.move_to(UP * 1.8 + LEFT * 2.2)
        lbl_rev = safe_text("REVOLUTION", font="Inter", font_size=28,
                            color=MUTED, weight="BOLD")
        lbl_rev.move_to(UP * 1.8 + RIGHT * 2.2)

        # Declaration scroll at MID
        scroll_body = Rectangle(width=2.2, height=3.0, fill_color=ANCIENT_CREAM,
                                fill_opacity=0.85, stroke_color=CLAY_TAN, stroke_width=1.5)
        scroll_top = Ellipse(width=2.5, height=0.4, fill_color=ANCIENT_CREAM,
                             fill_opacity=0.9, stroke_color=CLAY_TAN, stroke_width=1)
        scroll_top.move_to(scroll_body.get_top())
        scroll_bot = Ellipse(width=2.5, height=0.4, fill_color=ANCIENT_CREAM,
                             fill_opacity=0.8, stroke_color=CLAY_TAN, stroke_width=1)
        scroll_bot.move_to(scroll_body.get_bottom())
        scroll_lines = VGroup()
        for i in range(5):
            sl = Line(LEFT * 0.7, RIGHT * 0.7, color=CLAY_TAN,
                      stroke_width=0.8).move_to(scroll_body.get_center() + UP * (0.6 - i * 0.35))
            sl.set_opacity(0.5)
            scroll_lines.add(sl)
        scroll = VGroup(scroll_body, scroll_top, scroll_bot, scroll_lines)
        scroll.move_to(UP * ZONE_MID)

        # French tricolor at LOWER
        bar_b = Rectangle(width=2.0, height=4.0, fill_color="#002395", fill_opacity=0.4,
                          stroke_width=0).move_to(DOWN * ZONE_LOWER + LEFT * 2.0)
        bar_w = Rectangle(width=2.0, height=4.0, fill_color=WHITE_SOFT, fill_opacity=0.12,
                          stroke_width=0).move_to(DOWN * ZONE_LOWER)
        bar_r = Rectangle(width=2.0, height=4.0, fill_color=LIBERTY_RED, fill_opacity=0.4,
                          stroke_width=0).move_to(DOWN * ZONE_LOWER + RIGHT * 2.0)
        tricolor = VGroup(bar_b, bar_w, bar_r)
        tricolor.move_to(DOWN * 3.8)

        assumption = safe_text("THE ASSUMPTION", font="Inter", font_size=26,
                               color=DEAD_GRAY, weight="BOLD")
        assumption.move_to(UP * ZONE_FOOTER)

        # ── Timing: 4.50s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.20: "Human rights."
        self.play(FadeIn(yr_1776, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(yr_1776.get_center(), color=LIBERTY_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=1.1

        # VTT 1.00: "The Enlightenment. The French Revolution."
        self.play(LaggedStart(
            FadeIn(lbl_enl, shift=RIGHT * 0.3),
            FadeIn(lbl_rev, shift=LEFT * 0.3),
            lag_ratio=0.2), run_time=0.4)                                  # t=1.5
        self.play(GrowFromCenter(scroll), run_time=0.5); t += 0.5

        # VTT 2.80: "1776."
        self.play(FadeIn(tricolor, shift=UP * 0.3), run_time=0.5); t += 0.5
        self.play(FadeIn(assumption, shift=UP * 0.1), run_time=0.3); t += 0.3

        # Slow pulse on 1776 to fill hold time
        self.play(yr_1776.animate.scale(1.05), run_time=0.6); t += 0.6
        self.play(yr_1776.animate.scale(1 / 1.05), run_time=0.6); t += 0.6
        target = getattr(self.__class__, 'DURATION', 4.5)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE CONTRADICTION (4.5–9.0s = 4.50s)
# Zones: TITLE(pill) UPPER(539 BC) MID(cylinder) LOWER(1776 dim) FOOTER(gap)
# ================================================================
class Scene2_Contradiction(Scene):
    DURATION = 4.5
    def construct(self):
        self.add(gradient_bg("#080A0E"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE CONTRADICTION", color=GOLD_CYLINDER, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # "539 BC" huge at UPPER
        yr_539 = safe_text("539 BC", font="Bebas Neue", font_size=140, color=GOLD_CYLINDER)
        yr_539.move_to(UP * ZONE_UPPER)

        # Clay cylinder at MID — hero
        cylinder = clay_cylinder(2.5, 1.8, CLAY_TAN)
        cylinder.move_to(UP * ZONE_MID)

        # Cylinder glow ring
        cyl_glow = Circle(radius=2.0, fill_color=GOLD_CYLINDER, fill_opacity=0.06,
                          stroke_width=0).move_to(cylinder.get_center())

        # 1776 for comparison — dimmed at LOWER
        yr_1776_dim = safe_text("1776 AD", font="Bebas Neue", font_size=80, color=DIM)
        yr_1776_dim.move_to(DOWN * 2.8)

        # Timeline bar showing the gap
        tl_bar = Rectangle(width=7.0, height=0.35, fill_color=SURFACE2, fill_opacity=0.9,
                           stroke_color=BORDER, stroke_width=1)
        tl_bar.move_to(DOWN * 4.2)
        mark_539 = Dot(radius=0.12, color=GOLD_CYLINDER).move_to(DOWN * 4.2 + LEFT * 3.2)
        mark_1776 = Dot(radius=0.12, color=LIBERTY_RED).move_to(DOWN * 4.2 + RIGHT * 3.2)
        gap_dash = DashedLine(mark_539.get_center(), mark_1776.get_center(),
                              color=GOLD_CYLINDER, stroke_width=1.5, dash_length=0.15)

        gap_label = safe_text("2,315 YEARS EARLIER", font="Bebas Neue",
                              font_size=50, color=GOLD_CYLINDER)
        gap_label.move_to(UP * ZONE_FOOTER + UP * 0.3)

        # ── Timing: 4.50s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.20: "But there's a problem."
        self.play(FadeIn(yr_539, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(yr_539.get_center(), color=GOLD_CYLINDER,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=1.1

        # VTT 1.30: "A Persian king wrote human rights on a clay cylinder"
        self.play(FadeIn(cyl_glow), GrowFromCenter(cylinder),
                  run_time=0.6)                                             # t=1.7

        # Slow zoom on cylinder during narration
        self.play(cylinder.animate.scale(1.08), run_time=0.6); t += 0.6

        # VTT 3.00: "2,500 years earlier."
        self.play(FadeIn(yr_1776_dim, shift=UP * 0.2), run_time=0.3); t += 0.3
        self.play(FadeIn(tl_bar), FadeIn(mark_539, scale=1.3),
                  FadeIn(mark_1776, scale=1.3), run_time=0.3)             # t=2.9
        self.play(Create(gap_dash), run_time=0.4); t += 0.4
        self.play(FadeIn(gap_label, scale=1.05), run_time=0.4); t += 0.4

        # Pulse gap label for emphasis
        self.play(gap_label.animate.scale(1.08).set_color(GOLD), run_time=0.3); t += 0.3
        self.play(gap_label.animate.scale(1 / 1.08).set_color(GOLD_CYLINDER),
                  run_time=0.3); t += 0.3                                  # t=4.3

        target = getattr(self.__class__, 'DURATION', 4.5)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:])), run_time=0.3)


# ================================================================
# SCENE 3: THE DISMISSED TRUTH (9.0–14.0s = 5.00s)
# Zones: TITLE(pill) UPPER(539 BC) MID(cylinder+icons) LOWER(return home) FOOTER(UN)
# ================================================================
class Scene3_Truth(Scene):
    DURATION = 5.0
    def construct(self):
        self.add(gradient_bg(g="#0A0A14"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE CYRUS CYLINDER", color=GOLD_CYLINDER, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        yr_label = safe_text("539 BC", font="Bebas Neue", font_size=80, color=GOLD_CYLINDER)
        yr_label.move_to(UP * ZONE_UPPER)

        # Clay cylinder at MID — smaller, icons flanking
        cylinder = clay_cylinder(2.0, 1.5, CLAY_TAN)
        cylinder.move_to(UP * ZONE_MID)

        # Religion icon — cross + crescent
        cross_v = Line(UP * 0.3, DOWN * 0.3, color=ANCIENT_CREAM, stroke_width=2.5)
        cross_h = Line(LEFT * 0.18, RIGHT * 0.18, color=ANCIENT_CREAM, stroke_width=2.5)
        cross_h.move_to(cross_v.get_center() + UP * 0.1)
        crescent = Arc(radius=0.22, start_angle=PI * 0.3, angle=PI * 1.2,
                       stroke_color=ANCIENT_CREAM, stroke_width=2)
        crescent.next_to(cross_v, RIGHT, buff=0.15)
        religion_icon = VGroup(cross_v, cross_h, crescent)
        religion_icon.move_to(LEFT * 3.0 + UP * 0.5)
        rel_lbl = safe_text("RELIGION", font="Inter", font_size=22,
                            color=ANCIENT_CREAM, weight="BOLD")
        rel_lbl.move_to(LEFT * 3.0 + DOWN * 0.3)

        # No slavery — broken chain links
        link_l = Circle(radius=0.16, stroke_color=ANCIENT_CREAM, stroke_width=2.5,
                        fill_opacity=0).move_to(LEFT * 0.14)
        link_r = Circle(radius=0.16, stroke_color=ANCIENT_CREAM, stroke_width=2.5,
                        fill_opacity=0).move_to(RIGHT * 0.14)
        break_mark = Line(UP * 0.1, DOWN * 0.1, color=GOLD_CYLINDER, stroke_width=3)
        chain_icon = VGroup(link_l, link_r, break_mark)
        chain_icon.move_to(RIGHT * 3.0 + UP * 0.5)
        chain_lbl = safe_text("NO SLAVERY", font="Inter", font_size=22,
                              color=ANCIENT_CREAM, weight="BOLD")
        chain_lbl.move_to(RIGHT * 3.0 + DOWN * 0.3)

        # "Go home" icon at LOWER — arrow + house shape
        home_arrow = Arrow(LEFT * 0.5, RIGHT * 0.5, color=ANCIENT_CREAM,
                           stroke_width=3, max_tip_length_to_length_ratio=0.3)
        home_roof = Polygon(
            np.array([-0.3, 0.0, 0]),
            np.array([0, 0.3, 0]),
            np.array([0.3, 0.0, 0]),
            stroke_color=ANCIENT_CREAM, stroke_width=2, fill_opacity=0,
        )
        home_base = Rectangle(width=0.4, height=0.3, stroke_color=ANCIENT_CREAM,
                              stroke_width=2, fill_opacity=0)
        home_base.next_to(home_roof, DOWN, buff=0)
        house = VGroup(home_roof, home_base).move_to(RIGHT * 0.9)
        home_group = VGroup(home_arrow, house)
        home_group.move_to(DOWN * 2.5)
        home_lbl = safe_text("RETURN HOME", font="Inter", font_size=24,
                             color=ANCIENT_CREAM, weight="BOLD")
        home_lbl.move_to(DOWN * 3.5)

        # Rights pulse ring — animated circle behind cylinder
        pulse_ring = Circle(radius=1.5, stroke_color=GOLD_CYLINDER, stroke_width=1.5,
                            fill_opacity=0).move_to(cylinder.get_center())

        un_lbl = safe_text("UN HAS A REPLICA", font="Bebas Neue",
                           font_size=50, color=PERSIAN_BLUE)
        un_lbl.move_to(UP * ZONE_FOOTER + UP * 0.3)

        # ── Timing: 5.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.20: "The Cyrus Cylinder. 539 BC."
        self.play(FadeIn(yr_label, shift=DOWN * 0.2), run_time=0.3); t += 0.3
        self.play(GrowFromCenter(cylinder), run_time=0.5); t += 0.5

        # Pulse ring expands outward
        self.play(GrowFromCenter(pulse_ring), run_time=0.3); t += 0.3
        self.play(pulse_ring.animate.scale(1.8).set_opacity(0), run_time=0.4); t += 0.4

        # VTT 1.50: "Freedom of religion. No slavery."
        self.play(FadeIn(religion_icon, scale=0.8), FadeIn(rel_lbl, shift=UP * 0.1),
                  run_time=0.4)                                             # t=2.2
        self.play(FadeIn(chain_icon, scale=0.8), FadeIn(chain_lbl, shift=UP * 0.1),
                  run_time=0.4)                                             # t=2.6

        # VTT 3.00: "Conquered peoples go home."
        self.play(FadeIn(home_group, shift=RIGHT * 0.3), run_time=0.4); t += 0.4
        self.play(FadeIn(home_lbl, shift=UP * 0.1), run_time=0.3); t += 0.3

        # Arrow slides right to emphasize "going home"
        self.play(home_arrow.animate.shift(RIGHT * 0.3), run_time=0.3); t += 0.3

        # VTT 4.00: "The UN has a replica."
        self.play(FadeIn(un_lbl, scale=1.05), run_time=0.5); t += 0.5
        self.play(Flash(un_lbl.get_center(), color=PERSIAN_BLUE,
                        line_length=0.3, num_lines=6, run_time=0.3))       # t=4.4
        target = getattr(self.__class__, 'DURATION', 5.0)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE PROOF (14.0–19.0s = 5.00s)
# Zones: TITLE(pill) UPPER(CYRUS) MID(star+temple) LOWER(messiah) FOOTER(isaiah)
# ================================================================
class Scene4_Proof(Scene):
    DURATION = 5.0
    def construct(self):
        self.add(gradient_bg("#080A0C"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE PROOF", color=GOLD, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        cyrus_name = safe_text("CYRUS", font="Bebas Neue", font_size=90, color=GOLD_CYLINDER)
        cyrus_name.move_to(UP * ZONE_UPPER)

        # Star of David at MID-LEFT
        star = star_of_david(0.8, GOLD)
        star.move_to(LEFT * 2.0 + UP * ZONE_MID)

        # Temple shape at MID-RIGHT — pediment + columns
        temple_base = Rectangle(width=2.0, height=1.5, fill_color=PERSIAN_BLUE,
                                fill_opacity=0.6, stroke_color=PERSIAN_BLUE_LT, stroke_width=1.5)
        temple_top = Polygon(
            np.array([-1.2, 0.75, 0]),
            np.array([0, 1.5, 0]),
            np.array([1.2, 0.75, 0]),
            fill_color=PERSIAN_BLUE, fill_opacity=0.7,
            stroke_color=PERSIAN_BLUE_LT, stroke_width=1.5,
        )
        cols = VGroup()
        for x in [-0.6, -0.2, 0.2, 0.6]:
            c = Line(DOWN * 0.7, UP * 0.7, color=PERSIAN_BLUE_LT, stroke_width=2)
            c.move_to(RIGHT * x)
            cols.add(c)
        temple = VGroup(temple_base, temple_top, cols)
        temple.scale(0.8).move_to(RIGHT * 2.0 + UP * ZONE_MID)

        # Connecting arrow star → temple
        connect = Arrow(star.get_right() + RIGHT * 0.2, temple.get_left() + LEFT * 0.2,
                        color=GOLD_CYLINDER, stroke_width=2, max_tip_length_to_length_ratio=0.2)

        # "MESSIAH" at LOWER
        messiah = safe_text("MESSIAH", font="Bebas Neue", font_size=100, color=GOLD)
        messiah.move_to(DOWN * 2.8)

        only_lbl = safe_text("ONLY NON-JEW", font="Inter", font_size=26,
                             color=MUTED, weight="BOLD")
        only_lbl.move_to(DOWN * 4.2)

        isaiah = safe_text("ISAIAH 45:1", font="Bebas Neue", font_size=55, color=ANCIENT_CREAM)
        isaiah.move_to(UP * ZONE_FOOTER)

        # ── Timing: 5.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.20: "Cyrus freed the Jews. Rebuilt their temple."
        self.play(FadeIn(cyrus_name, scale=1.05), run_time=0.4); t += 0.4
        self.play(GrowFromCenter(star), run_time=0.4); t += 0.4
        self.play(FadeIn(temple, scale=0.9), run_time=0.4); t += 0.4
        self.play(GrowArrow(connect), run_time=0.3); t += 0.3

        # VTT 2.20: "Only non-Jew called messiah in the Hebrew Bible."
        self.play(FadeIn(messiah, scale=1.15), run_time=0.5); t += 0.5
        self.play(Flash(messiah.get_center(), color=GOLD,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=2.6
        self.play(FadeIn(only_lbl, shift=UP * 0.1), run_time=0.3); t += 0.3

        # Messiah glow pulse
        messiah_glow = Circle(radius=2.0, fill_color=GOLD, fill_opacity=0.04,
                              stroke_width=0).move_to(messiah.get_center())
        self.play(FadeIn(messiah_glow), run_time=0.3); t += 0.3

        # VTT 4.00: "Isaiah 45:1."
        target = getattr(self.__class__, 'DURATION', 5.0)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeIn(isaiah, scale=1.05), run_time=0.5); t += 0.5

        # Gentle scale on star during hold
        self.play(star.animate.scale(1.1), run_time=0.5); t += 0.5
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE SCALE (19.0–23.5s = 4.50s)
# Zones: TITLE(pill) UPPER(5.5M) MID(map) LOWER(44%) FOOTER(label)
# ================================================================
class Scene5_Scale(Scene):
    DURATION = 4.5
    def construct(self):
        self.add(gradient_bg(g="#0A0A14"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE EMPIRE", color=PERSIAN_BLUE, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        sq_km = safe_text("5.5M km²", font="Bebas Neue", font_size=90, color=PERSIAN_BLUE_LT)
        sq_km.move_to(UP * ZONE_UPPER)

        # Empire map at MID — hero
        empire = map_persia(PERSIAN_BLUE, 0.35)
        empire.move_to(UP * ZONE_MID)

        # Glow behind map
        map_glow = Circle(radius=3.0, fill_color=PERSIAN_BLUE, fill_opacity=0.05,
                          stroke_width=0).move_to(empire.get_center())

        # City dots on map — Persepolis, Babylon, Susa
        city_dots = VGroup()
        city_positions = [
            (0.5, 0.0),    # Persepolis
            (-1.0, 0.5),   # Babylon
            (0.0, 0.8),    # Susa
            (-2.5, 0.5),   # Sardis
        ]
        for cx, cy in city_positions:
            d = Dot(point=np.array([cx, cy, 0]), radius=0.08, color=GOLD_CYLINDER)
            city_dots.add(d)

        # "44%" at LOWER — hero stat
        pct_44 = safe_text("44%", font="Bebas Neue", font_size=160, color=GOLD)
        pct_44.move_to(DOWN * 3.8)

        of_world = safe_text("OF WORLD POPULATION", font="Inter", font_size=28,
                             color=WHITE_SOFT, weight="BOLD")
        of_world.move_to(DOWN * 5.3)

        under = safe_text("UNDER PERSIAN RULE", font="Inter", font_size=24,
                          color=MUTED, weight="BOLD")
        under.move_to(UP * ZONE_FOOTER)

        # ── Timing: 4.50s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.20: "His empire: 5.5 million square kilometers."
        self.play(FadeIn(sq_km, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(map_glow), DrawBorderThenFill(empire),
                  run_time=0.6)                                             # t=1.3

        # City dots appear with stagger
        self.play(LaggedStart(*[FadeIn(d, scale=2.0) for d in city_dots],
                              lag_ratio=0.1), run_time=0.4)                # t=1.7

        # Map slowly expands to show scale
        self.play(empire.animate.scale(1.1),
                  map_glow.animate.scale(1.15), run_time=0.5)             # t=2.2

        # VTT 2.20: "44% of the world lived under Persian rule."
        self.play(FadeIn(pct_44, scale=1.3), run_time=0.6); t += 0.6
        self.play(Flash(pct_44.get_center(), color=GOLD,
                        line_length=0.6, num_lines=12, run_time=0.3))      # t=3.1
        self.play(FadeIn(of_world, shift=UP * 0.1), run_time=0.3); t += 0.3
        self.play(FadeIn(under, shift=UP * 0.1), run_time=0.3); t += 0.3

        # Hold with gentle pct pulse
        self.play(pct_44.animate.scale(1.05), run_time=0.4); t += 0.4

        target = getattr(self.__class__, 'DURATION', 4.5)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:])), run_time=0.3)


# ================================================================
# SCENE 6: THE PUNCH (23.5–32.0s = 8.50s)
# Zones: TITLE(letterbox) UPPER(arch) MID(PERSIAN) LOWER(NOT ENGLISH) FOOTER(quote)
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 8.5
    def construct(self):
        self.add(gradient_bg("#050508"), grid_lines(0.02))
        t = 0

        # Letterbox bars
        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP * (8 - bh / 2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN * (8 - bh / 2)),
        )

        # Ghost cylinder at very low opacity — ambient texture
        ghost_cyl = clay_cylinder(4, 2.5, CLAY_TAN)
        ghost_cyl.move_to(UP * 1)
        ghost_cyl.set_opacity(0.04)
        self.add(ghost_cyl)

        # Persian arch at UPPER — will glow
        arch = persian_arch(3.5, 2.5, PERSIAN_BLUE)
        arch.move_to(UP * 2.5)

        # Arch glow
        arch_glow = Circle(radius=2.5, fill_color=PERSIAN_BLUE, fill_opacity=0.05,
                           stroke_width=0).move_to(arch.get_center())

        # "PERSIAN." at MID — the reveal word
        persian_word = safe_text("PERSIAN.", font="Bebas Neue", font_size=110,
                                 color=GOLD_CYLINDER)
        persian_word.move_to(DOWN * 1.5)

        glow = Circle(radius=2.5, fill_color=GOLD_CYLINDER, fill_opacity=0.04,
                       stroke_width=0).move_to(persian_word.get_center())

        not_eng = safe_text("NOT ENGLISH.", font="Bebas Neue", font_size=80,
                            color=MUTED)
        not_eng.move_to(DOWN * 4.0)

        free = safe_text("\"You are free.\"", font="DM Serif Display",
                         font_size=40, color=ANCIENT_CREAM)
        free.move_to(UP * ZONE_FOOTER)

        # ── Timing: 8.50s ──
        # VTT 0.20: "The first person to say 'you are free to believe what you want'"
        self.play(FadeIn(arch_glow), FadeIn(arch, scale=0.95), run_time=0.6); t += 0.6

        # Arch keystone glows during narration buildup
        self.play(arch[3].animate.scale(1.5).set_color(GOLD), run_time=0.5); t += 0.5

        self.wait(1.6); t += 1.6

        # VTT 3.00: "said it in Persian."
        self.play(FadeIn(glow), FadeIn(persian_word, scale=1.1),
                  run_time=0.7)                                             # t=3.4
        self.play(Flash(persian_word.get_center(), color=GOLD_CYLINDER,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=3.7

        # Slow scale on persian word
        self.play(persian_word.animate.scale(1.06), run_time=0.5); t += 0.5

        # VTT 4.50: "Not English."
        self.play(FadeIn(not_eng, scale=1.05), run_time=0.5); t += 0.5
        self.play(FadeIn(free, shift=UP * 0.06), run_time=0.5); t += 0.5

        # Persian word and arch pulse gently during hold
        self.play(glow.animate.scale(1.2).set_opacity(0.06), run_time=0.8); t += 0.8
        self.play(arch.animate.scale(1.03), run_time=0.5); t += 0.5

        # Hold then fade to black
        target = getattr(self.__class__, 'DURATION', 8.5)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.7); t += 1.7


# ── Infra ─────────────────────────────────────────────────────
def render_single_scene(idx):
    sc = [Scene1_WrongAnswer, Scene2_Contradiction, Scene3_Truth,
          Scene4_Proof, Scene5_Scale, Scene6_Punch]
    config.output_file = f"cyrus_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"cyrus_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    sc = [Scene1_WrongAnswer, Scene2_Contradiction, Scene3_Truth,
          Scene4_Proof, Scene5_Scale, Scene6_Punch]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(sc):
        n = f"cyrus_scene_{i+1}"; print(f"  Preview {n}...")
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

    names = ["Scene1_WrongAnswer","Scene2_Contradiction","Scene3_Truth",
             "Scene4_Proof","Scene5_Scale","Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_cyrus.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="cyrus", audio_path=str(audio))
    final = od / "cyrus_human_rights_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
