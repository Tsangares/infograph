#!/usr/bin/env python3
"""Someone Else's War — The Aztec Conquest Reframe (Manim). Mystery arc.

6 scenes, ~37.0s (34.0s audio + 3s hold).

VTT cues (absolute → relative):
  Scene 1 (0.0–5.0s = 5.00s):
    0.100 (0.10) 600 Spanish soldiers conquered an empire of 5 million people.
    2.800 (2.80) That's the story.
    3.800 (3.80) It's a lie.
  Scene 2 (5.0–10.0s = 5.00s):
    5.100 (0.10) Cortés was a genius.
    6.200 (1.20) Spanish steel. Horses. Gunpowder.
    7.800 (2.80) A small band of brave men toppled the mighty Aztecs.
  Scene 3 (10.0–15.5s = 5.50s):
    10.100 (0.10) But Cortés didn't fight alone.
    11.300 (1.30) He had 200,000 indigenous allies.
    13.000 (3.00) The Tlaxcalans hated the Aztecs more than they feared the Spanish.
  Scene 4 (15.5–21.0s = 5.50s):
    15.600 (0.10) At the siege of Tenochtitlan,
    16.800 (1.30) the Spanish were outnumbered by their own allies 100 to 1.
    18.500 (3.00) Cortés didn't conquer the Aztecs.
    19.500 (4.00) The Aztecs' enemies did.
  Scene 5 (21.0–27.0s = 6.00s):
    21.100 (0.10) The Tlaxcalans expected power-sharing.
    22.500 (1.50) They got colonization.
    24.000 (3.00) Within a generation, Spain ruled everyone.
    25.500 (4.50) Allies and enemies alike.
  Scene 6 (27.0–37.0s = 10.00s):
    27.100 (0.10) Cortés didn't outsmart an empire.
    29.000 (2.00) He walked into someone else's war
    31.000 (4.00) and took credit for the win.
    + 3s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """600 Spanish soldiers conquered an empire of five million. That's the story. It's a lie. Cortés had 200,000 indigenous allies. The Tlaxcalans hated the Aztecs more than they feared the Spanish. At Tenochtitlan, Spanish were outnumbered by their own allies a hundred to one. Cortés didn't conquer the Aztecs. Their enemies did. The Tlaxcalans expected power-sharing. They got colonization. Cortés walked into someone else's war and took credit for the win."""

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

BG = "#080A10"
GRID = "#1A2030"
SURFACE = "#15192A"
WHITE_SOFT = "#F0F0F0"
GOLD = "#FFD700"
AZTEC_GOLD = "#C9A84C"
AZTEC_GREEN = "#2D5A27"
AZTEC_GREEN_LT = "#3E7A34"
SPAIN_RED = "#C60B1E"
SPAIN_YELLOW = "#FFC400"
MUTED = "#7B8DA0"
DIM = "#404050"
DEAD_GRAY = "#4A5568"

SAFE_W = 8.0

ZONE_TITLE  = 6.2
ZONE_UPPER  = 3.5
ZONE_MID    = 0.0
ZONE_LOWER  = -3.5
ZONE_FOOTER = -6.0


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

def section_div(width=5, color=AZTEC_GOLD):
    l = Line(LEFT*width/2, LEFT*0.12, color=color, stroke_width=1.5)
    r = Line(RIGHT*0.12, RIGHT*width/2, color=color, stroke_width=1.5)
    d = Square(side_length=0.1, color=color, fill_color=color, fill_opacity=1).rotate(45*DEGREES)
    return VGroup(l, d, r)

def label_pill(txt, color=AZTEC_GOLD, bg=SURFACE, fs=28):
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

def pyramid_aztec(height=3.5, width=5, color=AZTEC_GREEN):
    """Stepped Aztec pyramid — 4 stacked trapezoids + temple block."""
    steps = 4
    blocks = VGroup()
    for i in range(steps):
        frac_bot = 1 - i / steps
        frac_top = 1 - (i + 1) / steps
        w_bot = width * frac_bot
        w_top = width * frac_top
        h = height / steps
        y_base = i * h
        trap = Polygon(
            np.array([-w_bot/2, y_base, 0]),
            np.array([w_bot/2, y_base, 0]),
            np.array([w_top/2, y_base + h, 0]),
            np.array([-w_top/2, y_base + h, 0]),
            fill_color=color, fill_opacity=0.75,
            stroke_color=AZTEC_GREEN_LT, stroke_width=1.2,
        )
        blocks.add(trap)
    # Top temple block
    tw = width * 0.12
    temple = Rectangle(width=tw, height=height*0.12,
                       fill_color=color, fill_opacity=0.9,
                       stroke_color=AZTEC_GREEN_LT, stroke_width=1)
    temple.move_to(np.array([0, height + height*0.06, 0]))
    blocks.add(temple)
    return blocks

def warrior_fig(color=WHITE_SOFT, spear_color=AZTEC_GOLD, height=1.5):
    """Stick-figure warrior with spear."""
    s = height / 1.5  # scale factor
    head = Circle(radius=0.12*s, fill_color=color, fill_opacity=0.9,
                  stroke_color=color, stroke_width=1).move_to(UP * 0.55 * s)
    body = Line(UP * 0.43*s, DOWN * 0.15*s, color=color, stroke_width=2)
    l_leg = Line(DOWN * 0.15*s, DOWN * 0.55*s + LEFT * 0.18*s, color=color, stroke_width=1.5)
    r_leg = Line(DOWN * 0.15*s, DOWN * 0.55*s + RIGHT * 0.18*s, color=color, stroke_width=1.5)
    l_arm = Line(UP * 0.25*s, UP * 0.05*s + LEFT * 0.22*s, color=color, stroke_width=1.5)
    r_arm = Line(UP * 0.25*s, UP * 0.45*s + RIGHT * 0.15*s, color=color, stroke_width=1.5)
    spear = Line(UP * 0.45*s + RIGHT * 0.15*s, UP * 0.95*s + RIGHT * 0.15*s,
                 color=spear_color, stroke_width=2)
    tip = Polygon(
        np.array([0.15*s, 0.95*s, 0]),
        np.array([0.10*s, 1.10*s, 0]),
        np.array([0.20*s, 1.10*s, 0]),
        fill_color=spear_color, fill_opacity=1, stroke_width=0,
    )
    return VGroup(head, body, l_leg, r_leg, l_arm, r_arm, spear, tip)

def battle_banner(color=SPAIN_RED, pole_color=DIM, height=2.0):
    """Flag/banner on a pole."""
    s = height / 2.0
    pole = Line(DOWN * 0.8*s, UP * 0.8*s, color=pole_color, stroke_width=2.5)
    flag = Polygon(
        np.array([0, 0.8*s, 0]),
        np.array([0.7*s, 0.6*s, 0]),
        np.array([0.7*s, 0.2*s, 0]),
        np.array([0, 0.0*s, 0]),
        fill_color=color, fill_opacity=0.85, stroke_color=color, stroke_width=1,
    )
    return VGroup(pole, flag)

def map_region(color=AZTEC_GREEN, opacity=0.3):
    """Simplified Mesoamerica territory polygon."""
    pts = [
        np.array([-3.0, 1.5, 0]),
        np.array([-1.0, 2.0, 0]),
        np.array([1.5, 1.2, 0]),
        np.array([2.5, 0.0, 0]),
        np.array([2.0, -1.5, 0]),
        np.array([0.5, -2.0, 0]),
        np.array([-1.0, -1.8, 0]),
        np.array([-2.5, -0.5, 0]),
        np.array([-3.5, 0.5, 0]),
    ]
    return Polygon(*pts, fill_color=color, fill_opacity=opacity,
                   stroke_color=AZTEC_GREEN_LT, stroke_width=1.5)


# ================================================================
# SCENE 1: THE HOOK (0.0–5.0s = 5.00s)
# Visual: "600 vs 5,000,000" number contrast + ghost pyramid
# Zones: TITLE(pill) UPPER(600) MID(5M) LOWER(pyramid) FOOTER(lie)
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 5.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE AZTEC EMPIRE", color=AZTEC_GOLD, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # Big number contrast — hero at ZONE_UPPER / ZONE_MID
        six_hundred = safe_text("600", font="Bebas Neue", font_size=160, color=SPAIN_RED)
        six_hundred.move_to(UP * ZONE_UPPER)

        vs = safe_text("vs", font="DM Serif Display", font_size=50, color=MUTED)
        vs.move_to(UP * 1.5)

        five_mil = safe_text("5,000,000", font="Bebas Neue", font_size=160, color=AZTEC_GOLD)
        five_mil.move_to(UP * ZONE_MID)

        div = section_div(5, MUTED).move_to(DOWN * 1.5)

        # Small pyramid silhouette in LOWER zone
        pyr = pyramid_aztec(2.5, 4, AZTEC_GREEN)
        pyr.move_to(DOWN * 3.8)
        pyr.set_opacity(0.25)

        # "IT'S A LIE." at FOOTER
        lie = safe_text("IT'S A LIE.", font="Bebas Neue", font_size=80, color=SPAIN_RED)
        lie.move_to(UP * (ZONE_FOOTER + 0.3))

        # ── Timing: 5.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.add(pyr)

        # VTT 0.10: "600 Spanish soldiers conquered an empire of 5 million"
        self.play(FadeIn(six_hundred, scale=1.3), run_time=0.5); t += 0.5
        self.play(FadeIn(vs, shift=UP*0.05), run_time=0.3); t += 0.3
        self.play(FadeIn(five_mil, scale=1.3), run_time=0.6); t += 0.6
        self.play(Flash(five_mil.get_center(), color=AZTEC_GOLD,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=2.0

        # VTT 2.80: "That's the story."
        self.wait(0.5); t += 0.5
        self.play(Create(div), run_time=0.3); t += 0.3

        # VTT 3.80: "It's a lie."
        self.wait(0.7); t += 0.7
        self.play(FadeIn(lie, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(lie.get_center(), color=SPAIN_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=4.3
        target = getattr(self.__class__, 'DURATION', 5.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE WRONG ANSWER (5.0–10.0s = 5.00s)
# Visual: pyramid + tiny Spanish warrior icons — the "textbook story"
# Zones: TITLE(pill) UPPER+MID(pyramid) LOWER(warriors) FOOTER(labels)
# ================================================================
class Scene2_WrongAnswer(Scene):
    DURATION = 5.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE TEXTBOOK STORY", color=SPAIN_RED, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # Pyramid centered at MID — the "mighty Aztecs"
        pyr = pyramid_aztec(3.5, 5, AZTEC_GREEN)
        pyr.move_to(UP * 0.5)

        # Tiny Spanish warriors at LOWER — 6 figures approaching
        warriors = VGroup()
        for i in range(6):
            w = warrior_fig(color=SPAIN_RED, spear_color=SPAIN_YELLOW, height=1.0)
            w.move_to(LEFT * 2.5 + RIGHT * i * 1.0 + DOWN * 3.5)
            warriors.add(w)

        # Weapon labels spread across bottom
        items_data = [
            ("STEEL.", DOWN * 5.0 + LEFT * 2.5, SPAIN_YELLOW),
            ("HORSES.", DOWN * 5.0, SPAIN_YELLOW),
            ("GUNPOWDER.", DOWN * 5.0 + RIGHT * 2.5, SPAIN_YELLOW),
        ]
        item_texts = []
        for txt, pos, col in items_data:
            lbl = safe_text(txt, font="Bebas Neue", font_size=40, color=col)
            lbl.move_to(pos)
            item_texts.append(lbl)

        footer = safe_text("THE TEXTBOOK VERSION", font="Inter",
                           font_size=28, color=DEAD_GRAY, weight="BOLD")
        footer.move_to(UP * ZONE_FOOTER)

        # ── Timing: 5.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "Cortés was a genius."
        self.play(FadeIn(pyr, scale=0.9), run_time=0.6); t += 0.6

        # VTT 1.20: "Spanish steel. Horses. Gunpowder."
        self.play(LaggedStart(*[FadeIn(w, shift=UP*0.2) for w in warriors],
                              lag_ratio=0.08), run_time=0.6)               # t=1.5
        self.play(LaggedStart(*[FadeIn(t, shift=UP*0.1) for t in item_texts],
                              lag_ratio=0.15), run_time=0.7)               # t=2.2

        # VTT 2.80: "A small band of brave men toppled the mighty Aztecs."
        self.wait(0.3); t += 0.3
        self.play(FadeIn(footer, shift=UP*0.04), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 5.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: THE TRUTH (10.0–15.5s = 5.50s)
# Visual: Tlaxcala warrior army spans full frame, tiny Spanish cluster dwarfed
# Zones: TITLE(pill) UPPER(NOT ALONE) MID(200K+ALLIES label) LOWER(warrior rows) FOOTER(+600 spanish)
# ================================================================
class Scene3_Contradiction(Scene):
    DURATION = 5.5
    def construct(self):
        self.add(gradient_bg(g="#0A1A0A"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE TRUTH", color=AZTEC_GOLD, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        not_alone = safe_text("NOT ALONE.", font="Bebas Neue", font_size=100, color=AZTEC_GOLD)
        not_alone.move_to(UP * ZONE_UPPER)

        # 200,000 number at MID-UPPER
        two_hundred_k = safe_text("200,000", font="Bebas Neue", font_size=120, color=AZTEC_GOLD)
        two_hundred_k.move_to(UP * 1.5)

        allies_lbl = safe_text("INDIGENOUS ALLIES", font="Inter", font_size=30,
                               color=WHITE_SOFT, weight="BOLD")
        allies_lbl.move_to(UP * 0.5)

        div = section_div(5, AZTEC_GOLD).move_to(UP * ZONE_MID)

        # "ALLIES" label prominent at LOWER zone top
        allies_lower = safe_text("ALLIES:", font="Bebas Neue", font_size=72, color=AZTEC_GOLD)
        allies_lower.move_to(DOWN * 1.0)

        # ── LOWER zone: Two rows of Tlaxcala warriors spanning full width ──
        tlax_row1 = VGroup()
        for col in range(7):
            w = warrior_fig(color=AZTEC_GOLD, spear_color=AZTEC_GREEN_LT, height=1.3)
            x = -3.0 + col * 1.0
            w.move_to(np.array([x, -2.3, 0]))
            tlax_row1.add(w)

        tlax_row2 = VGroup()
        for col in range(7):
            w = warrior_fig(color=AZTEC_GOLD, spear_color=AZTEC_GREEN_LT, height=1.1)
            x = -2.6 + col * 0.95
            w.move_to(np.array([x, -3.8, 0]))
            tlax_row2.add(w)

        # Tlaxcala label
        tlax_label = safe_text("TLAXCALA", font="Bebas Neue", font_size=38, color=AZTEC_GOLD)
        tlax_label.move_to(LEFT * 2.5 + DOWN * 5.0)

        # Spanish joining on right — tiny cluster showing coalition
        spain_label = safe_text("+ 600 SPANISH", font="Bebas Neue", font_size=38, color=SPAIN_RED)
        spain_label.move_to(RIGHT * 1.8 + DOWN * 5.0)

        spanish_cluster = VGroup()
        for i in range(4):
            s = warrior_fig(color=SPAIN_RED, spear_color=SPAIN_YELLOW, height=0.75)
            s.move_to(RIGHT * 0.8 + RIGHT * i * 0.75 + DOWN * 5.9)
            spanish_cluster.add(s)

        # ── Timing: 5.50s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "But Cortés didn't fight alone."
        self.play(FadeIn(not_alone, scale=1.1), run_time=0.5); t += 0.5

        # VTT 1.30: "He had 200,000 indigenous allies."
        self.wait(0.2); t += 0.2
        self.play(FadeIn(two_hundred_k, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(two_hundred_k.get_center(), color=AZTEC_GOLD,
                        line_length=0.5, num_lines=12, run_time=0.3))      # t=1.8
        self.play(FadeIn(allies_lbl), run_time=0.2); t += 0.2
        self.play(Create(div), run_time=0.2); t += 0.2
        self.play(FadeIn(allies_lower, scale=1.1), run_time=0.3); t += 0.3

        # VTT 3.00: "The Tlaxcalans hated the Aztecs..." — warriors flood LOWER
        self.play(LaggedStart(*[FadeIn(w, scale=0.85) for w in tlax_row1],
                              lag_ratio=0.06), run_time=0.6)               # t=3.1
        self.play(LaggedStart(*[FadeIn(w, scale=0.85) for w in tlax_row2],
                              lag_ratio=0.06), run_time=0.5)               # t=3.6

        # Spanish joining — dwarfed by ally army
        self.play(FadeIn(tlax_label, shift=UP*0.1),
                  FadeIn(spain_label, shift=UP*0.1), run_time=0.4)        # t=4.0
        self.play(LaggedStart(*[FadeIn(s, shift=UP*0.1) for s in spanish_cluster],
                              lag_ratio=0.08), run_time=0.5)               # t=4.5
        target = getattr(self.__class__, 'DURATION', 5.5)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE SIEGE (15.5–21.0s = 5.50s)
# Visual: Lake Texcoco / Tenochtitlan — island, causeways, siege boats
# Zones: TITLE(pill) UPPER(TENOCHTITLAN) MID(lake+island+causeways) LOWER(ratio) FOOTER(punch)
# ================================================================
class Scene4_Proof(Scene):
    DURATION = 5.5
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE SIEGE", color=GOLD, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        siege_lbl = safe_text("TENOCHTITLAN", font="Bebas Neue", font_size=70, color=WHITE_SOFT)
        siege_lbl.move_to(UP * ZONE_UPPER)

        # ── MID zone: Lake Texcoco with island city ──
        # Water — large dark-blue ellipse
        lake = Ellipse(width=7.8, height=3.8, fill_color="#06152A", fill_opacity=0.9,
                       stroke_color="#1A4A7A", stroke_width=2.5)
        lake.move_to(UP * 0.3)

        # Lake water shimmer lines
        shimmer1 = DashedLine(LEFT * 3.2 + UP * 0.8, RIGHT * 3.2 + UP * 0.8,
                              color="#1A4A8A", stroke_width=1.0, dash_length=0.2)
        shimmer2 = DashedLine(LEFT * 2.6 + UP * 0.1, RIGHT * 2.6 + UP * 0.1,
                              color="#1A4A8A", stroke_width=1.0, dash_length=0.2)
        shimmer3 = DashedLine(LEFT * 3.0 + DOWN * 0.5, RIGHT * 3.0 + DOWN * 0.5,
                              color="#1A4A8A", stroke_width=0.8, dash_length=0.15)
        shimmers = VGroup(shimmer1, shimmer2, shimmer3)

        # Island (city) — small filled circle in lake center
        island = Circle(radius=0.6, fill_color=AZTEC_GREEN, fill_opacity=0.95,
                        stroke_color=AZTEC_GREEN_LT, stroke_width=2.5)
        island.move_to(UP * 0.3)

        city_dot = Dot(point=island.get_center(), radius=0.14, color=AZTEC_GOLD)

        # Causeways — 3 roads from island to lake edges
        cw_north = Line(island.get_center() + UP * 0.62,
                        island.get_center() + UP * 1.85,
                        color=DIM, stroke_width=5)
        cw_west  = Line(island.get_center() + LEFT * 0.62,
                        island.get_center() + LEFT * 3.5,
                        color=DIM, stroke_width=5)
        cw_south = Line(island.get_center() + DOWN * 0.62,
                        island.get_center() + DOWN * 1.8,
                        color=DIM, stroke_width=5)
        causeways = VGroup(cw_north, cw_west, cw_south)

        # Siege boats — small red rectangles on the lake
        def siege_boat(x, y):
            b = Rectangle(width=0.5, height=0.2, fill_color=SPAIN_RED, fill_opacity=0.9,
                          stroke_color=SPAIN_RED, stroke_width=1)
            b.move_to(np.array([x, y, 0]))
            return b

        boats = VGroup(
            siege_boat(-2.8, 0.9), siege_boat(-2.1, -0.3), siege_boat(-1.5, 1.0),
            siege_boat(2.2, 0.7),  siege_boat(2.7, -0.2), siege_boat(1.0, -0.9),
            siege_boat(-0.3, 1.2), siege_boat(1.8, 1.1),
        )

        # ── LOWER zone: 100:1 ratio ──
        ratio = safe_text("100 : 1", font="Bebas Neue", font_size=95, color=GOLD)
        ratio.move_to(DOWN * 2.9)

        outnumbered = safe_text("OUTNUMBERED BY THEIR OWN ALLIES", font="Inter",
                                font_size=27, color=MUTED, weight="BOLD")
        outnumbered.move_to(DOWN * 4.0)

        div = section_div(5, GOLD).move_to(DOWN * 4.9)

        punch = safe_text("THEIR ENEMIES DID.", font="Bebas Neue",
                          font_size=52, color=AZTEC_GOLD)
        punch.move_to(DOWN * 5.8)

        # ── Timing: 5.50s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "At the siege of Tenochtitlan,"
        self.play(FadeIn(siege_lbl, scale=1.05), run_time=0.5); t += 0.5

        # VTT 1.30: Lake and island appear
        self.play(FadeIn(lake, scale=0.92), run_time=0.5); t += 0.5
        self.play(Create(shimmers), run_time=0.3); t += 0.3
        self.play(Create(causeways), run_time=0.4); t += 0.4
        self.play(GrowFromCenter(island), FadeIn(city_dot), run_time=0.4); t += 0.4
        self.play(LaggedStart(*[FadeIn(b, scale=0.7) for b in boats],
                              lag_ratio=0.05), run_time=0.5)               # t=2.9

        # VTT 3.00/4.00: "outnumbered 100:1 / Aztecs' enemies did."
        self.play(FadeIn(ratio, scale=1.15), run_time=0.4); t += 0.4
        self.play(Flash(ratio.get_center(), color=GOLD,
                        line_length=0.4, num_lines=10, run_time=0.3))      # t=3.6
        self.play(FadeIn(outnumbered), run_time=0.3); t += 0.3
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(punch, scale=1.05), run_time=0.5); t += 0.5
        self.play(Flash(punch.get_center(), color=AZTEC_GOLD,
                        line_length=0.3, num_lines=8, run_time=0.3))       # t=5.0
        target = getattr(self.__class__, 'DURATION', 5.5)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE BETRAYAL (21.0–27.0s = 6.00s)
# Visual: warriors fade, Spain banners plant, red overlay covers map
# Zones: TITLE(pill) UPPER+MID(map+warriors→banners) LOWER(COLONIZED) FOOTER(alike)
# ================================================================
class Scene5_Betrayal(Scene):
    DURATION = 6.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE BETRAYAL", color=SPAIN_RED, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # Map region centered at MID
        # CRITICAL: add immediately so frame 0 of clip is never black
        region = map_region(color=AZTEC_GREEN, opacity=0.35)
        region.move_to(UP * 0.5)
        self.add(region)

        # Allied warriors on the map — will disappear
        map_warriors = VGroup()
        positions = [
            LEFT*1.5 + UP*1.2, RIGHT*0.5 + UP*0.8, LEFT*0.5 + DOWN*0.2,
            RIGHT*1.5 + UP*0.3, LEFT*2 + DOWN*0.5, ORIGIN + UP*1.5,
        ]
        for pos in positions:
            w = warrior_fig(color=AZTEC_GOLD, spear_color=AZTEC_GREEN_LT, height=0.9)
            w.move_to(pos + UP * 0.5)
            map_warriors.add(w)

        # Spain banners — will cover the map
        banners = VGroup()
        banner_positions = [
            LEFT*2 + UP*1, RIGHT*1.5 + UP*0.5, LEFT*0.5 + DOWN*0.5,
            RIGHT*0.5 + UP*1.5, LEFT*1 + DOWN*1,
        ]
        for pos in banner_positions:
            b = battle_banner(color=SPAIN_RED, height=1.5)
            b.move_to(pos + UP * 0.5)
            banners.add(b)

        # Spain overlay — red tint
        spain_overlay = Rectangle(width=8, height=6, fill_color=SPAIN_RED,
                                  fill_opacity=0.25, stroke_width=0)
        spain_overlay.move_to(UP * 0.5)

        div = section_div(5, SPAIN_RED).move_to(DOWN * 3.0)

        colonized = safe_text("COLONIZED.", font="Bebas Neue", font_size=90, color=SPAIN_RED)
        colonized.move_to(DOWN * 4.0)

        everyone = safe_text("Allies and enemies alike.", font="DM Serif Display",
                             font_size=40, color=DEAD_GRAY)
        everyone.move_to(UP * ZONE_FOOTER)

        # ── Timing: 6.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "The Tlaxcalans expected power-sharing."
        # region already added via self.add() — animate warriors in
        self.play(LaggedStart(*[FadeIn(w, scale=0.9) for w in map_warriors],
                              lag_ratio=0.08), run_time=0.8)               # t=1.1

        # VTT 1.50: "They got colonization."
        self.wait(0.4); t += 0.4
        # Warriors disappear
        self.play(LaggedStart(*[w.animate.shift(DOWN*0.5).set_opacity(0) for w in map_warriors],
                              lag_ratio=0.06), run_time=0.8)               # t=2.3
        # Banners plant
        self.play(LaggedStart(*[FadeIn(b, shift=DOWN*0.3) for b in banners],
                              lag_ratio=0.08), run_time=0.6)               # t=2.9

        # VTT 3.00: "Within a generation, Spain ruled everyone."
        self.play(FadeIn(spain_overlay), run_time=0.5); t += 0.5
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(colonized, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(colonized.get_center(), color=SPAIN_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=4.5

        # VTT 4.50: "Allies and enemies alike."
        self.play(FadeIn(everyone, shift=UP*0.04), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 6.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE PUNCH (27.0–37.0s = 10.00s)
# Visual: lone figure + banner, ghost pyramid, cinematic letterbox
# Zones: TITLE(div) UPPER(letterbox) MID(SOMEONE ELSE'S WAR) LOWER(figure+banner) FOOTER(credit)
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 10.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.02))
        t = 0

        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP * (8 - bh/2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN * (8 - bh/2)),
        )

        # Ghost pyramid — barely visible
        ghost = pyramid_aztec(5, 7, AZTEC_GREEN)
        ghost.move_to(DOWN * 1)
        ghost.set_opacity(0.04)
        self.add(ghost)

        div1 = section_div(4, SPAIN_RED).move_to(UP * 2.0)

        # "SOMEONE ELSE'S WAR" at MID
        line1 = safe_text("SOMEONE ELSE'S", font="Bebas Neue", font_size=80, color=WHITE_SOFT)
        line1.move_to(UP * 0.5)
        line2 = safe_text("WAR.", font="Bebas Neue", font_size=100, color=SPAIN_RED)
        line2.move_to(DOWN * 1.0)

        div2 = section_div(4, MUTED).move_to(DOWN * 2.3)

        # Lone figure + banner at LOWER
        lone_fig = warrior_fig(color=SPAIN_RED, spear_color=SPAIN_YELLOW, height=1.8)
        lone_fig.move_to(DOWN * 3.8 + RIGHT * 0.5)

        banner = battle_banner(color=SPAIN_RED, height=1.2)
        banner.move_to(DOWN * 3.2 + RIGHT * 1.5)

        div3 = section_div(4, AZTEC_GOLD).move_to(DOWN * 5.0)

        credit = safe_text("TOOK CREDIT.", font="Bebas Neue",
                           font_size=60, color=AZTEC_GOLD)
        credit.move_to(UP * ZONE_FOOTER)

        glow = Circle(radius=2.5, fill_color=SPAIN_RED, fill_opacity=0.04, stroke_width=0)
        glow.move_to(line2)

        # ── Timing: 10.00s ──
        # VTT 0.10: "Cortés didn't outsmart an empire."
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(line1, shift=UP*0.08), run_time=0.6); t += 0.6

        # VTT 2.00: "He walked into someone else's war"
        self.wait(0.8); t += 0.8
        self.play(FadeIn(glow), FadeIn(line2, scale=1.1), run_time=0.7); t += 0.7
        self.play(Flash(line2.get_center(), color=SPAIN_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=2.7
        self.play(Create(div2), run_time=0.3); t += 0.3

        # Lone figure + banner
        self.play(FadeIn(lone_fig, shift=RIGHT*0.3), run_time=0.5); t += 0.5
        self.play(FadeIn(banner, shift=RIGHT*0.2), run_time=0.4); t += 0.4

        # VTT 4.00: "and took credit for the win."
        self.play(Create(div3), run_time=0.3); t += 0.3
        self.play(FadeIn(credit, scale=1.05), run_time=0.6); t += 0.6
        self.play(Flash(credit.get_center(), color=AZTEC_GOLD,
                        line_length=0.3, num_lines=6, run_time=0.3))       # t=5.1

        # 3s hold + fade to black
        target = getattr(self.__class__, 'DURATION', 10.0)
        self.wait(max(0.1, target - t - 0.8))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3

        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.2); t += 1.2


# ── Infra ─────────────────────────────────────────────────────
def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_WrongAnswer, Scene3_Contradiction,
          Scene4_Proof, Scene5_Betrayal, Scene6_Punch]
    config.output_file = f"aztec_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"aztec_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    sc = [Scene1_Hook, Scene2_WrongAnswer, Scene3_Contradiction,
          Scene4_Proof, Scene5_Betrayal, Scene6_Punch]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(sc):
        n = f"aztec_scene_{i+1}"; print(f"  Preview {n}...")
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

    names = ["Scene1_Hook","Scene2_WrongAnswer","Scene3_Contradiction",
             "Scene4_Proof","Scene5_Betrayal","Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_aztec.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="aztec", audio_path=str(audio))
    final = od / "aztec_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
