#!/usr/bin/env python3
"""The Roman Empire Didn't Fall in 476 (Manim). Byzantine survival/loss arc.

6 scenes, ~37.0s (34.0s audio + 3s hold).

VTT cues (absolute → relative):
  Scene 1 (0.0–5.0s = 5.00s):
    0.10 (0.10) The Roman Empire didn't fall in 476.
    1.80 (1.80) It lasted another thousand years.
    3.40 (3.40) And when it actually ended, the world barely noticed.
  Scene 2 (5.0–10.0s = 5.00s):
    5.10 (0.10) Every history class says Rome fell to barbarians.
    7.00 (2.00) Romulus Augustulus, 476 AD. End of story.
    8.50 (3.50) But that was only the western half.
  Scene 3 (10.0–15.5s = 5.50s):
    10.10 (0.10) Constantinople had running water, hospitals,
    11.50 (1.50) a fire department, and a legal code
    12.80 (2.80) that still shapes European law.
    13.80 (3.80) In 1000 AD, it was the largest and richest city
    14.80 (4.80) in the Christian world.
  Scene 4 (15.5–21.0s = 5.50s):
    15.60 (0.10) May 29th, 1453.
    16.50 (1.00) Ottoman cannons breached walls
    17.50 (2.00) that had held for 1,100 years.
    18.80 (3.30) The last emperor, Constantine XI,
    19.60 (4.10) charged into the final battle.
    20.30 (4.80) His body was never found.
  Scene 5 (21.0–27.0s = 6.00s):
    21.10 (0.10) The great library was scattered.
    22.50 (1.50) Greek manuscripts that preserved
    23.50 (2.50) Aristotle, Plato, and Euclid
    24.50 (3.50) for a thousand years flooded into Italy.
    25.50 (4.50) They called what happened next the Renaissance.
  Scene 6 (27.0–37.0s = 10.00s):
    27.10 (0.10) The Roman Empire lasted 2,000 years.
    29.50 (2.50) We named the rebirth of learning
    31.00 (4.00) after what fell out of its corpse.
    + 3s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """The Roman Empire didn't fall in 476. It lasted another thousand years. Every history class says Rome fell to barbarians. That was only the western half. Constantinople had running water, hospitals, and a legal code that still shapes law today. May 29th, 1453. Ottoman cannons breached walls that held for eleven hundred years. The last emperor charged into battle. His body was never found. The manuscripts that spilled out sparked the Renaissance."""

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
WHITE_SOFT = "#F0F0F0"; MUTED = "#7B8DA0"; DEAD_GRAY = "#4A5568"
GOLD = "#FFD700"; GOLD_DIM = "#B8960F"
BYZANTINE_PURPLE = "#4A1942"; BYZANTINE_GOLD = "#D4AF37"
OTTOMAN_RED = "#8B0000"; STONE_GRAY = "#8A8A8A"
RENAISSANCE_AMBER = "#FF8C00"
SAFE_W = 8.0

ZONE_TITLE  = 6.2
ZONE_UPPER  = 3.5
ZONE_MID    = 0.0
ZONE_LOWER  = -3.5
ZONE_FOOTER = -6.0


def gradient_bg(c=BG, g="#0A0A1A"):
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

def section_div(width=5, color=GOLD):
    l = Line(LEFT*width/2, LEFT*0.12, color=color, stroke_width=1.5)
    r = Line(RIGHT*0.12, RIGHT*width/2, color=color, stroke_width=1.5)
    d = Square(side_length=0.1, color=color, fill_color=color, fill_opacity=1).rotate(45*DEGREES)
    return VGroup(l, d, r)

def label_pill(txt, color=GOLD, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    p = RoundedRectangle(width=t.width+0.5, height=t.height+0.3, corner_radius=0.18,
                         fill_color=bg, fill_opacity=0.95, stroke_color=color, stroke_width=1.5).move_to(t)
    return VGroup(p, t)

def safe_text(content, **kwargs):
    t = Text(content, **kwargs)
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    return t


# -- Domain shapes -----------------------------------------------------------

def hagia_sophia(height=3.5, color=BYZANTINE_GOLD):
    """Iconic Hagia Sophia silhouette -- dome + base + minarets."""
    sc = height / 3.5
    base = Rectangle(width=3.5*sc, height=1.5*sc, fill_color=color, fill_opacity=0.7,
                     stroke_color=BYZANTINE_PURPLE, stroke_width=1.2)
    base.move_to(DOWN * 0.4 * sc)
    dome = Ellipse(width=2.5*sc, height=2.0*sc, fill_color=color, fill_opacity=0.8,
                   stroke_color=BYZANTINE_PURPLE, stroke_width=1.2)
    dome.move_to(UP * 0.8 * sc)
    minaret_l = Rectangle(width=0.12*sc, height=2.2*sc, fill_color=color,
                          fill_opacity=0.6, stroke_width=0.5, stroke_color=BYZANTINE_PURPLE)
    minaret_l.move_to(LEFT * 2.0*sc + UP * 0.3*sc)
    minaret_r = minaret_l.copy().move_to(RIGHT * 2.0*sc + UP * 0.3*sc)
    tip_l = Circle(radius=0.08*sc, fill_color=color, fill_opacity=1, stroke_width=0)
    tip_l.move_to(minaret_l.get_top() + UP * 0.08*sc)
    tip_r = tip_l.copy().move_to(minaret_r.get_top() + UP * 0.08*sc)
    return VGroup(base, dome, minaret_l, minaret_r, tip_l, tip_r)

def cannon_shape(color=OTTOMAN_RED, h=1.5):
    """Ottoman cannon -- barrel + base + wheels."""
    sc = h / 1.5
    barrel = Rectangle(width=2.0*sc, height=0.4*sc, fill_color=color, fill_opacity=0.9,
                       stroke_color=WHITE_SOFT, stroke_width=1)
    barrel.move_to(UP * 0.2*sc)
    base = Polygon(
        np.array([-0.8*sc, -0.1*sc, 0]),
        np.array([0.8*sc, -0.1*sc, 0]),
        np.array([0.6*sc, -0.4*sc, 0]),
        np.array([-0.6*sc, -0.4*sc, 0]),
        fill_color=STONE_GRAY, fill_opacity=0.8, stroke_width=0.8, stroke_color=MUTED
    )
    wheel_l = Circle(radius=0.2*sc, fill_color=STONE_GRAY, fill_opacity=0.7,
                     stroke_color=MUTED, stroke_width=1)
    wheel_l.move_to(LEFT * 0.5*sc + DOWN * 0.5*sc)
    wheel_r = wheel_l.copy().move_to(RIGHT * 0.5*sc + DOWN * 0.5*sc)
    return VGroup(barrel, base, wheel_l, wheel_r)

def scroll_book(color=BYZANTINE_GOLD, h=0.8):
    """Manuscript/scroll -- rolled rectangle with endcaps."""
    sc = h / 0.8
    body = Rectangle(width=0.7*sc, height=0.5*sc, fill_color=color, fill_opacity=0.85,
                     stroke_color=BYZANTINE_PURPLE, stroke_width=0.8)
    cap_top = Circle(radius=0.08*sc, fill_color=color, fill_opacity=1,
                     stroke_width=0.5, stroke_color=BYZANTINE_PURPLE)
    cap_top.move_to(body.get_top())
    cap_bot = cap_top.copy().move_to(body.get_bottom())
    return VGroup(body, cap_top, cap_bot)

def city_wall(width=7, height=1.4, color=STONE_GRAY):
    """Fortified wall with crenellations along the top."""
    sc = height / 1.4
    base = Rectangle(width=width, height=height * 0.7, fill_color=color,
                     fill_opacity=0.8, stroke_color=MUTED, stroke_width=1.5)
    crenels = VGroup()
    n_teeth = int(width / 0.5)
    tooth_w = width / n_teeth * 0.6
    for i in range(n_teeth):
        x = -width / 2 + (i + 0.5) * (width / n_teeth)
        tooth = Rectangle(width=tooth_w, height=0.25*sc, fill_color=color,
                          fill_opacity=0.8, stroke_color=MUTED, stroke_width=0.8)
        tooth.move_to(np.array([x, base.get_top()[1] + 0.125*sc, 0]))
        crenels.add(tooth)
    return VGroup(base, crenels)


# ================================================================
# SCENE 1: THE HOOK (0.0-5.0s = 5.00s)
# "The Roman Empire didn't fall in 476. It lasted another thousand years."
# Visual: Timeline with 476 crossed out, 1453 revealed
# Zones: TITLE(pill) UPPER(476/1453) MID(timeline) LOWER(1000 MORE) FOOTER(divider)
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 5.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE ROMAN EMPIRE", color=BYZANTINE_GOLD, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # 476 -- the "wrong" end -- ZONE_UPPER
        yr_476 = safe_text("476", font="Bebas Neue", font_size=120, color=OTTOMAN_RED)
        yr_476.move_to(UP * ZONE_UPPER)
        crossed = Line(LEFT * 1.2, RIGHT * 1.2, color=OTTOMAN_RED, stroke_width=4)
        crossed.move_to(yr_476).rotate(15 * DEGREES)

        # 1453 -- the real end
        yr_1453 = safe_text("1453", font="Bebas Neue", font_size=140, color=BYZANTINE_GOLD)
        yr_1453.move_to(UP * ZONE_UPPER)

        # Timeline bar -- ZONE_MID: long purple bar spanning the width
        tl_bar = Rectangle(width=7.5, height=0.35, fill_color=BYZANTINE_PURPLE,
                           fill_opacity=0.6, stroke_color=BYZANTINE_GOLD, stroke_width=1)
        tl_bar.move_to(UP * ZONE_MID)

        # Year markers on timeline
        start_mark = Line(UP * 0.3, DOWN * 0.3, color=BYZANTINE_GOLD, stroke_width=2)
        start_mark.move_to(tl_bar.get_left() + RIGHT * 0.2)
        end_mark = start_mark.copy().move_to(tl_bar.get_right() + LEFT * 0.2)

        yr_27bc = safe_text("27 BC", font="Inter", font_size=28, color=MUTED, weight="BOLD")
        yr_27bc.move_to(tl_bar.get_left() + RIGHT * 0.2 + DOWN * 0.6)
        yr_1453_sm = safe_text("1453", font="Inter", font_size=28, color=BYZANTINE_GOLD, weight="BOLD")
        yr_1453_sm.move_to(tl_bar.get_right() + LEFT * 0.2 + DOWN * 0.6)

        # Pulsing glow behind timeline
        tl_glow = Circle(radius=2.0, fill_color=BYZANTINE_PURPLE, fill_opacity=0.05,
                         stroke_width=0).move_to(UP * ZONE_MID)

        # "Another thousand years" -- ZONE_LOWER
        thousand = safe_text("1,000 MORE YEARS", font="Bebas Neue", font_size=80,
                            color=BYZANTINE_GOLD)
        thousand.move_to(UP * ZONE_LOWER)

        # Small Hagia Sophia silhouette at footer as a teaser
        teaser_sophia = hagia_sophia(1.5, color=BYZANTINE_GOLD)
        teaser_sophia.set_opacity(0.25)
        teaser_sophia.move_to(UP * ZONE_FOOTER)

        # -- Timing: 5.00s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "The Roman Empire didn't fall in 476."
        self.play(FadeIn(tl_glow), FadeIn(tl_bar), run_time=0.3); t += 0.3
        self.play(FadeIn(start_mark), FadeIn(yr_27bc), run_time=0.3); t += 0.3
        self.play(FadeIn(yr_476, scale=1.2), run_time=0.4); t += 0.4
        self.play(Create(crossed), run_time=0.3); t += 0.3

        # VTT 1.80: "It lasted another thousand years."
        self.play(FadeOut(yr_476), FadeOut(crossed), run_time=0.3); t += 0.3
        self.play(FadeIn(yr_1453, scale=1.15), run_time=0.5); t += 0.5
        self.play(Flash(yr_1453.get_center(), color=BYZANTINE_GOLD,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=2.7
        self.play(FadeIn(end_mark), FadeIn(yr_1453_sm), run_time=0.2); t += 0.2

        self.play(FadeIn(thousand, scale=1.08), run_time=0.5); t += 0.5

        # VTT 3.40: "And when it actually ended, the world barely noticed."
        self.play(FadeIn(teaser_sophia, scale=0.8), run_time=0.4); t += 0.4
        # Gentle drift on the timeline glow
        self.play(tl_glow.animate.scale(1.3).set_opacity(0.02), run_time=1.2); t += 1.2

        target = getattr(self.__class__, 'DURATION', 5.0)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:])), run_time=0.3)


# ================================================================
# SCENE 2: THE WRONG ANSWER (5.0-10.0s = 5.00s)
# "Every history class says Rome fell to barbarians. 476 AD. Only the western half."
# Zones: TITLE(pill) UPPER(ROME FELL) MID(pillar+sword) LOWER(W/E blocks) FOOTER(label)
# ================================================================
class Scene2_WrongAnswer(Scene):
    DURATION = 5.0
    def construct(self):
        self.add(gradient_bg("#080808"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE TEXTBOOK", color=OTTOMAN_RED, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # The textbook answer -- ZONE_UPPER
        fell = safe_text("ROME FELL.", font="Bebas Neue", font_size=100, color=OTTOMAN_RED)
        fell.move_to(UP * ZONE_UPPER)

        # Crumbling column/pillar -- MID zone, left side
        col_shaft = Rectangle(width=0.65, height=2.8, fill_color=STONE_GRAY, fill_opacity=0.85,
                              stroke_color=MUTED, stroke_width=1.5)
        col_shaft.move_to(LEFT * 1.8 + UP * ZONE_MID)
        col_capital = Rectangle(width=1.15, height=0.22, fill_color=STONE_GRAY, fill_opacity=0.85,
                                stroke_color=MUTED, stroke_width=1)
        col_capital.move_to(col_shaft.get_top() + DOWN * 0.11)
        col_base = Rectangle(width=1.05, height=0.22, fill_color=STONE_GRAY, fill_opacity=0.85,
                             stroke_color=MUTED, stroke_width=1)
        col_base.move_to(col_shaft.get_bottom() + UP * 0.11)
        # Debris fragments scattered around the pillar
        frag1 = Rectangle(width=0.38, height=0.22, fill_color=STONE_GRAY, fill_opacity=0.6,
                          stroke_width=0).rotate(28 * DEGREES)
        frag1.move_to(LEFT * 2.8 + DOWN * 0.6)
        frag2 = Rectangle(width=0.28, height=0.18, fill_color=STONE_GRAY, fill_opacity=0.5,
                          stroke_width=0).rotate(-18 * DEGREES)
        frag2.move_to(LEFT * 1.0 + DOWN * 1.0)
        frag3 = Rectangle(width=0.20, height=0.14, fill_color=MUTED, fill_opacity=0.45,
                          stroke_width=0).rotate(50 * DEGREES)
        frag3.move_to(LEFT * 2.2 + DOWN * 1.4)
        pillar_group = VGroup(col_base, col_shaft, col_capital, frag1, frag2, frag3)

        # Sword -- right side of MID zone
        sword_blade = Polygon(
            np.array([0.0,  1.4, 0]),
            np.array([0.14, 0.0, 0]),
            np.array([-0.14, 0.0, 0]),
            fill_color=STONE_GRAY, fill_opacity=0.9,
            stroke_color=WHITE_SOFT, stroke_width=1,
        )
        sword_guard = Rectangle(width=0.85, height=0.13, fill_color=MUTED, fill_opacity=0.9,
                                stroke_color=WHITE_SOFT, stroke_width=0.8)
        sword_guard.move_to(np.array([0, 0.0, 0]))
        sword_handle = Rectangle(width=0.22, height=0.58, fill_color=OTTOMAN_RED, fill_opacity=0.85,
                                 stroke_color=MUTED, stroke_width=0.5)
        sword_handle.move_to(np.array([0, -0.35, 0]))
        sword_group = VGroup(sword_blade, sword_guard, sword_handle)
        sword_group.move_to(RIGHT * 2.2 + UP * ZONE_MID)

        div = section_div(5, BYZANTINE_GOLD).move_to(DOWN * 1.8)

        # West/East split blocks -- ZONE_LOWER
        west_block = Rectangle(width=3.0, height=2.5, fill_color=DEAD_GRAY,
                               fill_opacity=0.4, stroke_color=MUTED, stroke_width=1)
        west_block.move_to(LEFT * 2.0 + UP * ZONE_LOWER)
        east_block = Rectangle(width=3.0, height=2.5, fill_color=BYZANTINE_PURPLE,
                               fill_opacity=0.7, stroke_color=BYZANTINE_GOLD, stroke_width=1.5)
        east_block.move_to(RIGHT * 2.0 + UP * ZONE_LOWER)
        west_l = safe_text("WEST", font="Inter", font_size=26, color=DEAD_GRAY, weight="BOLD")
        west_l.move_to(west_block.get_center() + UP * 0.3)
        east_l = safe_text("EAST", font="Inter", font_size=26, color=BYZANTINE_GOLD, weight="BOLD")
        east_l.move_to(east_block.get_center() + UP * 0.3)

        # X over west block to show it fell
        west_x = VGroup(
            Line(west_block.get_corner(UL) + RIGHT*0.3 + DOWN*0.3,
                 west_block.get_corner(DR) + LEFT*0.3 + UP*0.3,
                 color=OTTOMAN_RED, stroke_width=3),
            Line(west_block.get_corner(UR) + LEFT*0.3 + DOWN*0.3,
                 west_block.get_corner(DL) + RIGHT*0.3 + UP*0.3,
                 color=OTTOMAN_RED, stroke_width=3),
        )

        # Check on east block to show it survived
        east_check = safe_text("476", font="Bebas Neue", font_size=40, color=DEAD_GRAY)
        east_check.move_to(west_block.get_center() + DOWN * 0.4)
        east_alive = safe_text("1453", font="Bebas Neue", font_size=40, color=BYZANTINE_GOLD)
        east_alive.move_to(east_block.get_center() + DOWN * 0.4)

        # Footer source
        footer = safe_text("ONLY HALF THE STORY", font="Inter", font_size=22,
                          color=MUTED, weight="BOLD")
        footer.move_to(UP * ZONE_FOOTER)

        # -- Timing: 5.00s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "Every history class says Rome fell to barbarians."
        self.play(FadeIn(fell, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(fell.get_center(), color=OTTOMAN_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=1.1

        # VTT 2.00: domain shapes -- crumbling column + sword
        self.wait(0.4); t += 0.4
        self.play(FadeIn(pillar_group, scale=0.95), run_time=0.5); t += 0.5
        self.play(FadeIn(sword_group, shift=DOWN * 0.3), run_time=0.4); t += 0.4

        # VTT 3.50: "But that was only the western half."
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(
            FadeIn(west_block), FadeIn(east_block),
            FadeIn(west_l), FadeIn(east_l),
            run_time=0.4,
        )                                                                   # t=3.1
        self.play(
            Create(west_x[0]), Create(west_x[1]),
            FadeIn(east_check), FadeIn(east_alive),
            run_time=0.5,
        )                                                                   # t=3.6
        # Pulse the east block to highlight survival
        self.play(
            east_block.animate.set_fill(BYZANTINE_PURPLE, opacity=0.9),
            run_time=0.3,
        )                                                                   # t=3.9
        self.play(
            east_block.animate.set_fill(BYZANTINE_PURPLE, opacity=0.7),
            FadeIn(footer, shift=UP * 0.04),
            run_time=0.3,
        )                                                                   # t=4.2
        # Pillar crumbles -- fragments drift
        self.play(
            frag1.animate.shift(LEFT * 0.5 + DOWN * 0.4).set_opacity(0.3),
            frag2.animate.shift(RIGHT * 0.3 + DOWN * 0.5).set_opacity(0.2),
            frag3.animate.shift(LEFT * 0.3 + DOWN * 0.6).set_opacity(0.15),
            run_time=0.5,
        )                                                                   # t=4.7
        target = getattr(self.__class__, 'DURATION', 5.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: THE CONTRADICTION (10.0-15.5s = 5.50s)
# "Constantinople -- running water, hospitals, richest city in Christendom."
# Zones: TITLE(pill) UPPER(sophia) MID(amenities) LOWER(law) FOOTER(1000AD)
# ================================================================
class Scene3_Contradiction(Scene):
    DURATION = 5.5
    def construct(self):
        self.add(gradient_bg(g="#100A1A"), grid_lines(0.03))
        t = 0

        pill = label_pill("CONSTANTINOPLE", color=BYZANTINE_GOLD, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # Hagia Sophia -- hero spanning UPPER
        sophia = hagia_sophia(3.0, color=BYZANTINE_GOLD)
        sophia.move_to(UP * 2.0)

        # Ambient glow behind the building
        sophia_glow = Circle(radius=2.5, fill_color=BYZANTINE_PURPLE,
                             fill_opacity=0.06, stroke_width=0).move_to(sophia)

        div1 = section_div(5, BYZANTINE_GOLD).move_to(UP * 0.1)

        # City amenity pills -- ZONE_MID area
        amenity_data = [
            ("WATER", LEFT * 2.5, BYZANTINE_GOLD),
            ("HOSPITALS", LEFT * 0, BYZANTINE_GOLD),
            ("FIRE DEPT", RIGHT * 2.5, BYZANTINE_GOLD),
        ]
        amenity_pills = []
        for txt, pos, col in amenity_data:
            p = label_pill(txt, color=col, bg=BYZANTINE_PURPLE, fs=22)
            p.move_to(pos + DOWN * 1.2)
            amenity_pills.append(p)

        # Small dots representing infrastructure below each pill
        infra_dots = VGroup()
        for ap in amenity_pills:
            for j in range(3):
                dot = Dot(radius=0.04, color=BYZANTINE_GOLD, fill_opacity=0.4)
                dot.move_to(ap.get_bottom() + DOWN * 0.3 + LEFT * 0.15 + RIGHT * j * 0.15)
                infra_dots.add(dot)

        # LEGAL CODE -- ZONE_LOWER
        law_pill = label_pill("LEGAL CODE", color=WHITE_SOFT, bg=BYZANTINE_PURPLE, fs=24)
        law_pill.move_to(UP * ZONE_LOWER + UP * 0.8)

        # Scroll representing the Corpus Juris Civilis
        law_scroll = scroll_book(color=BYZANTINE_GOLD, h=1.6)
        law_scroll.move_to(UP * ZONE_LOWER + DOWN * 0.6)

        div2 = section_div(5, BYZANTINE_GOLD).move_to(UP * ZONE_LOWER + DOWN * 1.8)

        # "1000 AD" stat -- ZONE_FOOTER
        yr_1000 = safe_text("1000 AD", font="Bebas Neue", font_size=90, color=BYZANTINE_GOLD)
        yr_1000.move_to(UP * ZONE_FOOTER + UP * 0.3)
        richest = safe_text("LARGEST CITY IN CHRISTENDOM", font="Inter", font_size=24,
                           color=WHITE_SOFT, weight="BOLD")
        richest.move_to(UP * ZONE_FOOTER + DOWN * 0.6)

        # -- Timing: 5.50s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "Constantinople had running water, hospitals,"
        self.play(FadeIn(sophia_glow), FadeIn(sophia, scale=0.9), run_time=0.5); t += 0.5
        self.play(Create(div1), run_time=0.2); t += 0.2
        self.play(LaggedStart(*[FadeIn(p, scale=1.05) for p in amenity_pills],
                              lag_ratio=0.15), run_time=0.6)               # t=1.6
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in infra_dots],
                              lag_ratio=0.03), run_time=0.3)               # t=1.9

        # VTT 2.80: "that still shapes European law."
        target = getattr(self.__class__, 'DURATION', 5.5)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeIn(law_pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(GrowFromCenter(law_scroll), run_time=0.4); t += 0.4

        # VTT 3.80: "In 1000 AD, it was the largest and richest city"
        self.play(Create(div2), run_time=0.2); t += 0.2
        self.play(FadeIn(yr_1000, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(yr_1000.get_center(), color=BYZANTINE_GOLD,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=4.2

        # VTT 4.80: "in the Christian world."
        self.play(FadeIn(richest), run_time=0.4); t += 0.4
        # Gentle pulse on the sophia glow
        self.play(sophia_glow.animate.scale(1.2).set_opacity(0.03), run_time=0.9); t += 0.9

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE SIEGE (15.5-21.0s = 5.50s)
# "May 29th, 1453. Cannons breached walls that held 1,100 years."
# Zones: TITLE(pill) UPPER(date) MID(wall+cannon) LOWER(CONSTANTINE XI) FOOTER(never found)
# ================================================================
class Scene4_Siege(Scene):
    DURATION = 5.5
    def construct(self):
        self.add(gradient_bg("#0A0505"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE SIEGE", color=OTTOMAN_RED, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # Date -- ZONE_UPPER
        date = safe_text("MAY 29, 1453", font="Bebas Neue", font_size=100, color=OTTOMAN_RED)
        date.move_to(UP * ZONE_UPPER)

        div1 = section_div(5, OTTOMAN_RED).move_to(UP * 2.0)

        # Wall with crenellations -- ZONE_MID
        wall = city_wall(width=7, height=1.4, color=STONE_GRAY)
        wall.move_to(UP * 0.8)
        wall_label = safe_text("1,100 YEARS", font="Inter", font_size=24,
                              color=WHITE_SOFT, weight="BOLD")
        wall_label.move_to(wall.get_center())

        # Cannon -- below wall, left
        cannon = cannon_shape(color=OTTOMAN_RED, h=1.5)
        cannon.move_to(LEFT * 2.5 + DOWN * 1.2)

        # Cannonball arc (animated)
        cannonball = Circle(radius=0.12, fill_color=OTTOMAN_RED, fill_opacity=1,
                           stroke_width=0)
        cannonball.move_to(cannon.get_right() + RIGHT * 0.1)

        # Wall breach fragments
        fragments = VGroup()
        np.random.seed(77)
        for _ in range(12):
            frag = Rectangle(width=np.random.uniform(0.15, 0.4),
                            height=np.random.uniform(0.1, 0.3),
                            fill_color=STONE_GRAY, fill_opacity=0.7, stroke_width=0)
            frag.rotate(np.random.uniform(0, 2*PI))
            frag.move_to(np.array([
                np.random.uniform(-1, 1),
                np.random.uniform(0, 1.6),
                0
            ]))
            fragments.add(frag)
        fragments.set_opacity(0)

        div2 = section_div(5, BYZANTINE_GOLD).move_to(DOWN * 2.5)

        # Last emperor -- ZONE_LOWER
        constantine = safe_text("CONSTANTINE XI", font="Bebas Neue", font_size=65,
                               color=BYZANTINE_GOLD)
        constantine.move_to(UP * ZONE_LOWER + UP * 0.5)

        # Sword representing his final charge
        final_sword = Polygon(
            np.array([0.0,  0.8, 0]),
            np.array([0.08, 0.0, 0]),
            np.array([-0.08, 0.0, 0]),
            fill_color=BYZANTINE_GOLD, fill_opacity=0.8,
            stroke_color=WHITE_SOFT, stroke_width=0.8,
        )
        final_sword.move_to(UP * ZONE_LOWER + DOWN * 0.6)

        never_found = safe_text("BODY NEVER FOUND", font="Inter", font_size=30,
                               color=DEAD_GRAY, weight="BOLD")
        never_found.move_to(UP * ZONE_FOOTER)

        # -- Timing: 5.50s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "May 29th, 1453."
        self.play(FadeIn(date, scale=1.15), run_time=0.5); t += 0.5
        self.play(Flash(date.get_center(), color=OTTOMAN_RED,
                        line_length=0.5, num_lines=8, run_time=0.3))       # t=1.1

        # VTT 1.00: "Ottoman cannons breached walls"
        self.play(Create(div1), run_time=0.2); t += 0.2
        self.play(FadeIn(wall), FadeIn(wall_label), run_time=0.4); t += 0.4
        self.play(FadeIn(cannon, shift=RIGHT * 0.3), run_time=0.3); t += 0.3

        # Cannonball fires at wall
        self.add(cannonball)
        self.play(
            cannonball.animate.move_to(wall.get_center()),
            run_time=0.2,
        )                                                                   # t=2.2

        # VTT 2.00: "that had held for 1,100 years." -- BREACH
        self.add(fragments)
        self.play(
            FadeOut(cannonball, run_time=0.1),
            wall[0].animate.set_opacity(0.3).set_color(OTTOMAN_RED),
            *[frag.animate.set_opacity(0.8).shift(
                RIGHT * np.random.uniform(0.5, 2.5) + UP * np.random.uniform(-1, 2)
            ) for frag in fragments],
            Flash(wall.get_center(), color=RENAISSANCE_AMBER,
                  line_length=0.8, num_lines=15, run_time=0.4),
            run_time=0.5,
        )                                                                   # t=2.7

        # VTT 3.30: "The last emperor, Constantine XI,"
        self.play(Create(div2), run_time=0.2); t += 0.2
        self.play(FadeIn(constantine, scale=1.05), run_time=0.5); t += 0.5
        self.play(GrowFromCenter(final_sword), run_time=0.3); t += 0.3

        # VTT 4.10: "charged into the final battle."
        # Sword drifts upward as he charges
        self.play(final_sword.animate.shift(UP * 0.4).set_opacity(0.4),
                  run_time=0.6)                                             # t=4.3

        # VTT 4.80: "His body was never found."
        self.play(FadeOut(final_sword), run_time=0.2); t += 0.2
        self.play(FadeIn(never_found, shift=UP * 0.04), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 5.5)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE COST (21.0-27.0s = 6.00s)
# "The great library was scattered. Manuscripts flooded into Italy. Renaissance."
# Zones: TITLE(pill) UPPER(scrolls scatter) MID(arrow flow) LOWER(names) FOOTER(RENAISSANCE)
# ================================================================
class Scene5_Cost(Scene):
    DURATION = 6.0
    def construct(self):
        self.add(gradient_bg(g="#1A0A00"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE LEGACY", color=RENAISSANCE_AMBER, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # Hagia Sophia ghost -- faint, showing origin of the scrolls
        ghost_sophia = hagia_sophia(2.5, color=BYZANTINE_GOLD)
        ghost_sophia.set_opacity(0.15)
        ghost_sophia.move_to(UP * ZONE_UPPER + RIGHT * 2.0)

        # Scrolls -- spread across UPPER and MID zones
        scrolls = VGroup()
        scroll_positions = [
            LEFT * 2.8 + UP * 3.5,
            LEFT * 0.8 + UP * 4.0,
            RIGHT * 0.5 + UP * 3.0,
            LEFT * 3.0 + UP * 1.0,
            ORIGIN + UP * 0.5,
            RIGHT * 2.8 + UP * 1.5,
            LEFT * 1.5 + DOWN * 0.5,
            RIGHT * 1.5 + DOWN * 0.3,
        ]
        for pos in scroll_positions:
            s = scroll_book(color=BYZANTINE_GOLD, h=1.0)
            s.move_to(pos)
            scrolls.add(s)

        # Flow arrow pointing left (east to west / Constantinople to Italy)
        flow_arrow = Arrow(RIGHT * 3, LEFT * 3, color=RENAISSANCE_AMBER,
                          stroke_width=3, buff=0)
        flow_arrow.move_to(DOWN * 1.5)

        div1 = section_div(5, RENAISSANCE_AMBER).move_to(DOWN * 2.5)

        # Author names -- ZONE_LOWER
        names_data = ["ARISTOTLE", "PLATO", "EUCLID"]
        name_pills = []
        for i, name in enumerate(names_data):
            np_ = label_pill(name, color=BYZANTINE_GOLD, bg=SURFACE, fs=24)
            np_.move_to(LEFT * 2.5 + RIGHT * i * 2.5 + UP * ZONE_LOWER)
            name_pills.append(np_)

        # RENAISSANCE -- approaching ZONE_FOOTER
        renaissance = safe_text("RENAISSANCE", font="Bebas Neue", font_size=100,
                               color=RENAISSANCE_AMBER)
        renaissance.move_to(DOWN * 5.0)

        ren_glow = Circle(radius=2.5, fill_color=RENAISSANCE_AMBER, fill_opacity=0.06,
                          stroke_width=0)
        ren_glow.move_to(renaissance)

        # -- Timing: 6.00s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "The great library was scattered."
        self.play(FadeIn(ghost_sophia), run_time=0.3); t += 0.3

        # VTT 1.50: "Greek manuscripts that preserved"
        self.play(LaggedStart(*[FadeIn(s, scale=0.8) for s in scrolls],
                              lag_ratio=0.06), run_time=0.6)               # t=1.2

        # VTT 2.50: "Aristotle, Plato, and Euclid" -- scrolls flow west
        self.play(
            *[s.animate.shift(LEFT * 5 + DOWN * 1) for s in scrolls],
            GrowArrow(flow_arrow),
            run_time=0.8,
        )                                                                   # t=2.0

        self.play(LaggedStart(*[FadeIn(np_, scale=1.05) for np_ in name_pills],
                              lag_ratio=0.12), run_time=0.6)               # t=2.6

        # VTT 3.50: "for a thousand years flooded into Italy."
        self.play(Create(div1), run_time=0.3); t += 0.3
        # Ghost sophia fades as knowledge leaves
        self.play(ghost_sophia.animate.set_opacity(0.04), run_time=0.6); t += 0.6

        # VTT 4.50: "They called what happened next the Renaissance."
        target = getattr(self.__class__, 'DURATION', 6.0)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeIn(ren_glow), FadeIn(renaissance, scale=1.15),
                  run_time=0.6)                                             # t=4.8
        self.play(Flash(renaissance.get_center(), color=RENAISSANCE_AMBER,
                        line_length=0.6, num_lines=12, run_time=0.3))      # t=5.1
        # Glow expands
        self.play(ren_glow.animate.scale(1.4).set_opacity(0.03), run_time=0.9); t += 0.9

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE PUNCH (27.0-37.0s = 10.00s)
# "2,000 years. We named the rebirth after what fell out of its corpse."
# Visual: Ghost Hagia Sophia, timeline, "2,000 YEARS" + scrolls dissolving
# Zones: TITLE(none-cinematic) UPPER(2000) MID(sophia ghost) LOWER(scrolls) FOOTER(glow)
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 10.0
    def construct(self):
        self.add(gradient_bg("#050508"), grid_lines(0.02))
        t = 0

        # Letterbox bars for cinematic feel
        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP * (8 - bh/2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN * (8 - bh/2)),
        )

        # Ghost Hagia Sophia -- the centerpiece, faint but present
        ghost = hagia_sophia(5.0, color=BYZANTINE_GOLD)
        ghost.set_opacity(0.0)
        ghost.move_to(UP * ZONE_MID)

        # "2,000 YEARS" -- ZONE_UPPER
        two_k = safe_text("2,000 YEARS", font="Bebas Neue", font_size=120,
                         color=BYZANTINE_GOLD)
        two_k.move_to(UP * ZONE_UPPER)

        # Full-width timeline bar -- ZONE_MID area above sophia
        tl_bar = Rectangle(width=7.5, height=0.25, fill_color=BYZANTINE_PURPLE,
                           fill_opacity=0.5, stroke_color=BYZANTINE_GOLD, stroke_width=0.8)
        tl_bar.move_to(UP * 1.5)
        tl_start = safe_text("27 BC", font="Inter", font_size=22, color=MUTED, weight="BOLD")
        tl_start.move_to(tl_bar.get_left() + DOWN * 0.4 + RIGHT * 0.3)
        tl_end = safe_text("1453", font="Inter", font_size=22, color=OTTOMAN_RED, weight="BOLD")
        tl_end.move_to(tl_bar.get_right() + DOWN * 0.4 + LEFT * 0.3)

        # Scattered scrolls at ZONE_LOWER representing the knowledge that survived
        decay_scrolls = VGroup()
        np.random.seed(66)
        for _ in range(6):
            s = scroll_book(color=BYZANTINE_GOLD, h=0.7)
            x = np.random.uniform(-3.5, 3.5)
            y = np.random.uniform(-4.5, -2.5)
            s.move_to(np.array([x, y, 0]))
            s.set_opacity(0.5)
            decay_scrolls.add(s)

        # Warm amber glow at ZONE_FOOTER -- the Renaissance emerging
        ren_glow = Circle(radius=3.0, fill_color=RENAISSANCE_AMBER, fill_opacity=0.0,
                          stroke_width=0)
        ren_glow.move_to(UP * ZONE_FOOTER)

        # -- Timing: 10.00s --
        # VTT 0.10: "The Roman Empire lasted 2,000 years."
        self.play(FadeIn(two_k, scale=1.15), run_time=0.6); t += 0.6
        self.play(Flash(two_k.get_center(), color=BYZANTINE_GOLD,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=0.9
        self.play(FadeIn(tl_bar), FadeIn(tl_start), FadeIn(tl_end),
                  run_time=0.4)                                             # t=1.3

        # Ghost sophia slowly materializes
        self.play(ghost.animate.set_opacity(0.35), run_time=1.0); t += 1.0

        # VTT 2.50: "We named the rebirth of learning"
        self.play(LaggedStart(*[FadeIn(s, scale=0.7) for s in decay_scrolls],
                              lag_ratio=0.08), run_time=0.6)               # t=2.9

        # Scrolls drift downward, knowledge falling
        self.play(
            *[s.animate.shift(DOWN * 1.0).set_opacity(0.25) for s in decay_scrolls],
            run_time=0.8,
        )                                                                   # t=3.7

        # VTT 4.00: "after what fell out of its corpse."
        # Ghost sophia dims while Renaissance glow builds
        self.play(
            ghost.animate.set_opacity(0.12),
            ren_glow.animate.set_opacity(0.08),
            run_time=0.8,
        )                                                                   # t=4.5

        # Scrolls dissolve as their knowledge transforms
        self.play(
            *[s.animate.set_color(RENAISSANCE_AMBER).set_opacity(0.1) for s in decay_scrolls],
            ren_glow.animate.set_opacity(0.12).scale(1.3),
            run_time=0.8,
        )                                                                   # t=5.3

        # Final hold -- sophia ghost fades, glow persists
        self.play(
            ghost.animate.set_opacity(0.05),
            two_k.animate.set_opacity(0.4),
            run_time=1.2,
        )                                                                   # t=6.5

        # 3s hold + fade to black
        self.wait(1.5); t += 1.5
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5
        target = getattr(self.__class__, 'DURATION', 10.0)
        self.wait(max(0.1, target - t - 0.8))


# -- Infra ----------------------------------------------------------------
def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_WrongAnswer, Scene3_Contradiction,
          Scene4_Siege, Scene5_Cost, Scene6_Punch]
    config.output_file = f"byzantine_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"byzantine_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    sc = [Scene1_Hook, Scene2_WrongAnswer, Scene3_Contradiction,
          Scene4_Siege, Scene5_Cost, Scene6_Punch]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(sc):
        n = f"byzantine_scene_{i+1}"; print(f"  Preview {n}...")
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
             "Scene4_Siege","Scene5_Cost","Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_byzantine.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="byzantine", audio_path=str(audio))
    final = od / "byzantine_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
