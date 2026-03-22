#!/usr/bin/env python3
"""The Bronze Age Collapse — When Every Civilization Fell (Manim).

6 scenes, ~46.3s (43.3s audio + 3s hold).

VTT cues (absolute -> relative):
  Scene 1 THE HOOK (0.0-7.5s = 7.50s):
    0.100 (0.10) In 1177 BC,
    1.500 (1.50) every major civilization on Earth collapsed at the same time.
  Scene 2 THE WRONG ANSWER (7.5-15.5s = 8.00s):
    7.600 (0.10) Textbooks blame the Sea Peoples.
    9.500 (2.00) Raiders from the sea who burned everything.
    12.000 (4.50) But no one knows who they actually were.
  Scene 3 THE CONTRADICTION (15.5-23.0s = 7.50s):
    15.600 (0.10) The Hittites. Mycenaeans. Egyptians. Babylonians.
    18.500 (3.00) They all fell within fifty years.
    20.500 (5.00) No single invader could do that.
  Scene 4 THE THEORY (23.0-31.0s = 8.00s):
    23.100 (0.10) Every empire depended on the others.
    25.000 (2.00) Tin from Afghanistan. Copper from Cyprus. Grain from Egypt.
    28.000 (5.00) One break in the chain and everything starved.
  Scene 5 THE SCALE (31.0-38.5s = 7.50s):
    31.100 (0.10) Writing disappeared for 400 years.
    33.500 (2.50) Entire languages were lost.
    35.500 (4.50) The world forgot how to build cities.
  Scene 6 THE PUNCH (38.5-46.3s = 7.80s):
    38.600 (0.10) It took 3,000 years to figure out what happened.
    41.500 (3.00) A globalized system so connected that when one part failed,
    44.000 (5.50) everything fell. Sound familiar?
    + 3s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """In 1177 BC, every major civilization collapsed at the same time. Textbooks blame the Sea Peoples — raiders who burned everything. Nobody knows who they were. Hittites. Mycenaeans. Egyptians. Babylonians. All fell within fifty years. Every empire depended on the others. Tin from Afghanistan. Copper from Cyprus. Grain from Egypt. One break and everything starved. Writing disappeared for 400 years. A system so connected that when one part failed, everything fell. Sound familiar?"""

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
config.background_color = "#0A0A0A"
config.disable_caching = True

# -- Color Palette -----------------------------------------------------
BG = "#0A0A0A"; SURFACE = "#12121C"; SURFACE2 = "#1A1A26"
BORDER = "#2A2A3A"; GRID = "#14141C"
BRONZE = "#CD7F32"; BRONZE_LT = "#DAA06D"; BRONZE_DK = "#8B5E3C"
FLAME_RED = "#E63B12"; FLAME_ORANGE = "#FF8C00"; FLAME_YELLOW = "#FFD700"
SEA_BLUE = "#1A5276"; SEA_TEAL = "#1A8A8A"
RUIN_GRAY = "#6B6B6B"; RUIN_DK = "#3A3A3A"
EMPIRE_GOLD = "#C9A84C"; HITTITE = "#B85C2F"; MYCENAE = "#3A6B8C"
EGYPT_GOLD = "#D4A017"; BABYLON = "#8B6914"
CRISIS_RED = "#CC2222"; DEATH_RED = "#FF3333"
WHITE_SOFT = "#F0F0F0"; MUTED = "#7B8DA0"; DIM = "#404050"
DEAD_GRAY = "#4A5568"
SAFE_W = 8.0

ZONE_TITLE  = 6.2
ZONE_UPPER  = 3.5
ZONE_MID    = 0.0
ZONE_LOWER  = -3.5
ZONE_FOOTER = -6.0


# -- Core helpers ------------------------------------------------------

def gradient_bg(c=BG, g="#0A0A12"):
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

def section_div(width=5, color=BRONZE):
    l = Line(LEFT*width/2, LEFT*0.12, color=color, stroke_width=1.5)
    r = Line(RIGHT*0.12, RIGHT*width/2, color=color, stroke_width=1.5)
    d = Square(side_length=0.1, color=color, fill_color=color, fill_opacity=1).rotate(45*DEGREES)
    return VGroup(l, d, r)

def label_pill(txt, color=BRONZE, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    p = RoundedRectangle(width=t.width+0.5, height=t.height+0.3, corner_radius=0.18,
                         fill_color=bg, fill_opacity=0.95, stroke_color=color, stroke_width=1.5).move_to(t)
    return VGroup(p, t)

def safe_text(content, **kwargs):
    t = Text(content, **kwargs)
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    return t


# -- Domain shapes (4 custom shapes) ----------------------------------

def ancient_ship_shape(height=2.5, hull_color=BRONZE_DK, sail_color=MUTED):
    """Warship with curved hull, sail, oars, and ram."""
    s = height / 2.5
    hull = Polygon(
        np.array([-1.5*s, 0, 0]), np.array([-1.8*s, -0.3*s, 0]),
        np.array([-1.2*s, -0.6*s, 0]), np.array([1.2*s, -0.6*s, 0]),
        np.array([1.8*s, -0.3*s, 0]), np.array([1.5*s, 0, 0]),
        fill_color=hull_color, fill_opacity=0.85, stroke_color=BRONZE_LT, stroke_width=1.5,
    )
    mast = Line(ORIGIN, UP * 1.4*s, color=BRONZE_DK, stroke_width=2.5)
    sail = Polygon(
        np.array([0, 1.4*s, 0]), np.array([0, 0.3*s, 0]), np.array([0.9*s, 0.5*s, 0]),
        fill_color=sail_color, fill_opacity=0.6, stroke_color=sail_color, stroke_width=1,
    )
    ram = Polygon(
        np.array([1.5*s, 0, 0]), np.array([2.0*s, -0.15*s, 0]), np.array([1.8*s, -0.3*s, 0]),
        fill_color=BRONZE, fill_opacity=0.9, stroke_width=0,
    )
    oars = VGroup()
    for i in range(5):
        x = -1.0*s + i * 0.5*s
        oars.add(Line(np.array([x, -0.3*s, 0]), np.array([x - 0.2*s, -0.9*s, 0]),
                      color=BRONZE_DK, stroke_width=1.2))
    return VGroup(hull, mast, sail, ram, oars)

def column_ruins_shape(height=3.0, color=RUIN_GRAY):
    """Broken classical column -- shaft + base + fallen capital + rubble."""
    s = height / 3.0
    shaft = Polygon(
        np.array([-0.25*s, -1.2*s, 0]), np.array([0.25*s, -1.2*s, 0]),
        np.array([0.22*s, 0.8*s, 0]), np.array([0.3*s, 0.9*s, 0]),
        np.array([-0.1*s, 0.7*s, 0]),
        fill_color=color, fill_opacity=0.8, stroke_color=RUIN_DK, stroke_width=1.5,
    )
    base = Rectangle(width=0.7*s, height=0.2*s, fill_color=color, fill_opacity=0.7,
                     stroke_color=RUIN_DK, stroke_width=1).move_to(DOWN * 1.3*s)
    capital = Polygon(
        np.array([0.5*s, -1.0*s, 0]), np.array([1.0*s, -1.0*s, 0]),
        np.array([0.9*s, -0.7*s, 0]), np.array([0.6*s, -0.8*s, 0]),
        fill_color=color, fill_opacity=0.6, stroke_color=RUIN_DK, stroke_width=1,
    )
    rubble = VGroup()
    for x, y in [(0.3*s, -1.3*s), (0.7*s, -1.35*s), (-0.4*s, -1.35*s)]:
        rubble.add(Circle(radius=0.06*s, fill_color=RUIN_DK, fill_opacity=0.5, stroke_width=0)
                   .move_to(np.array([x, y, 0])))
    return VGroup(shaft, base, capital, rubble)

def tablet_shape(height=2.0, color=BRONZE_LT):
    """Clay tablet with cuneiform-like wedge marks."""
    s = height / 2.0
    body = RoundedRectangle(width=1.4*s, height=1.8*s, corner_radius=0.15*s,
                            fill_color=color, fill_opacity=0.8,
                            stroke_color=BRONZE_DK, stroke_width=2)
    marks = VGroup()
    for row in range(4):
        for col in range(3):
            x = -0.35*s + col * 0.35*s
            y = 0.5*s - row * 0.3*s
            marks.add(Line(np.array([x, y, 0]), np.array([x + 0.12*s, y - 0.08*s, 0]),
                           color=BRONZE_DK, stroke_width=1.5*s))
    return VGroup(body, marks)

def flame_shape(height=1.5):
    """Simple flame from overlapping ellipses -- red/orange/yellow layers."""
    s = height / 1.5
    f1 = Ellipse(width=0.6*s, height=1.0*s, fill_color=FLAME_ORANGE, fill_opacity=0.7,
                 stroke_width=0).move_to(UP * 0.1*s)
    f2 = Ellipse(width=0.35*s, height=0.7*s, fill_color=FLAME_YELLOW, fill_opacity=0.6,
                 stroke_width=0).move_to(UP * 0.15*s)
    f3 = Ellipse(width=0.8*s, height=0.5*s, fill_color=FLAME_RED, fill_opacity=0.4,
                 stroke_width=0).move_to(DOWN * 0.2*s)
    return VGroup(f3, f1, f2)

def med_map_outline():
    """Simplified Mediterranean coastline polygon."""
    pts = [
        np.array([-4.0, 2.0, 0]), np.array([-2.5, 2.5, 0]), np.array([-1.0, 2.0, 0]),
        np.array([0.5, 2.8, 0]), np.array([2.0, 2.0, 0]), np.array([3.5, 2.5, 0]),
        np.array([4.0, 1.5, 0]), np.array([3.5, 0.0, 0]), np.array([2.5, -0.5, 0]),
        np.array([1.5, 0.5, 0]), np.array([0.5, -0.5, 0]), np.array([-0.5, 0.0, 0]),
        np.array([-1.5, -0.8, 0]), np.array([-2.5, 0.0, 0]), np.array([-3.5, 0.5, 0]),
        np.array([-4.0, 1.0, 0]),
    ]
    return Polygon(*pts, fill_color=SEA_BLUE, fill_opacity=0.15,
                   stroke_color=SEA_TEAL, stroke_width=1.5)


# ================================================================
# SCENE 1: THE HOOK (0.0-7.5s = 7.50s)
# Zones: TITLE (pill), UPPER+MID (map with X marks), LOWER (text), FOOTER (divider)
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 6.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("1177 BC", color=BRONZE, fs=32)
        pill.move_to(UP * ZONE_TITLE)

        # Mediterranean map centered across UPPER + MID
        med = med_map_outline()
        med.move_to(UP * ZONE_UPPER * 0.5)

        # Red X marks at civilization locations on the map
        x_marks = VGroup()
        civ_positions = [
            (LEFT*2.5 + UP*2.0, "HITTITES"),
            (RIGHT*1.0 + UP*2.5, "MYCENAE"),
            (LEFT*0.5 + UP*0.5, "EGYPT"),
            (RIGHT*3.0 + UP*1.5, "BABYLON"),
            (RIGHT*0.0 + UP*1.8, "CYPRUS"),
        ]
        for pos, name in civ_positions:
            x1 = Line(pos + LEFT*0.2 + UP*0.2, pos + RIGHT*0.2 + DOWN*0.2,
                       color=CRISIS_RED, stroke_width=4)
            x2 = Line(pos + RIGHT*0.2 + UP*0.2, pos + LEFT*0.2 + DOWN*0.2,
                       color=CRISIS_RED, stroke_width=4)
            lbl = Text(name, font="Inter", font_size=14, color=CRISIS_RED, weight="BOLD")
            lbl.move_to(pos + DOWN * 0.35)
            x_marks.add(VGroup(x1, x2, lbl))

        div = section_div(5, CRISIS_RED).move_to(DOWN * 1.5)

        # ZONE_LOWER text
        every = safe_text("EVERY", font="Bebas Neue", font_size=100, color=WHITE_SOFT)
        every.move_to(UP * (ZONE_LOWER + 1.0))
        civilization = safe_text("CIVILIZATION.", font="Bebas Neue", font_size=90, color=CRISIS_RED)
        civilization.move_to(UP * ZONE_LOWER)

        # ZONE_FOOTER
        same_time = safe_text("AT THE SAME TIME.", font="Inter", font_size=24,
                              color=MUTED, weight="BOLD")
        same_time.move_to(UP * (ZONE_FOOTER + 0.5))
        footer_div = section_div(3, MUTED).move_to(UP * ZONE_FOOTER)

        # -- Timing: 7.50s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "In 1177 BC,"
        self.play(FadeIn(med, scale=0.9), run_time=0.6); t += 0.6
        target = getattr(self.__class__, 'DURATION', 6.0)
        self.wait(max(0.1, target - t - 0.3))

        # VTT 1.50: "every major civilization collapsed"
        self.play(LaggedStart(*[FadeIn(xm, scale=1.2) for xm in x_marks],
                              lag_ratio=0.15), run_time=1.2)               # t=2.5

        # Map pulses red after X marks appear
        self.play(med.animate.set_stroke(color=CRISIS_RED, opacity=0.8), run_time=0.3); t += 0.3

        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(every, scale=1.1), run_time=0.5); t += 0.5
        self.play(FadeIn(civilization, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(civilization.get_center(), color=CRISIS_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))      # t=4.4
        self.play(FadeIn(same_time, shift=UP*0.05), run_time=0.3); t += 0.3
        self.play(Create(footer_div), run_time=0.2); t += 0.2

        # Slow zoom on map during remaining hold
        self.play(med.animate.scale(1.08), run_time=2.3); t += 2.3

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE WRONG ANSWER (7.5-15.5s = 8.00s)
# Zones: TITLE (pill), UPPER (ship), MID (flames+text), LOWER (?), FOOTER (who)
# ================================================================
class Scene2_WrongAnswer(Scene):
    DURATION = 4.6
    def construct(self):
        self.add(gradient_bg("#0A0808"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE WRONG ANSWER", color=MUTED, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # Ship at ZONE_UPPER
        ship = ancient_ship_shape(3.0, BRONZE_DK, MUTED)
        ship.move_to(UP * ZONE_UPPER)

        sea_lbl = safe_text("SEA PEOPLES", font="Bebas Neue", font_size=55, color=BRONZE)
        sea_lbl.move_to(UP * 1.5)

        # Flames at ZONE_MID
        flames = VGroup()
        for pos in [LEFT*2.5, LEFT*0.8, RIGHT*0.5, RIGHT*2.2]:
            flames.add(flame_shape(2.0).move_to(pos + DOWN * 0.3))

        burned = safe_text("BURNED EVERYTHING.", font="Bebas Neue", font_size=50, color=FLAME_ORANGE)
        burned.move_to(DOWN * 1.5)

        div = section_div(5, MUTED).move_to(DOWN * 2.5)

        # ZONE_LOWER: mystery question mark
        mystery = safe_text("?", font="Bebas Neue", font_size=200, color=MUTED)
        mystery.move_to(UP * ZONE_LOWER)

        # ZONE_FOOTER: who were they
        who = safe_text("WHO WERE THEY?", font="Bebas Neue", font_size=50, color=DEAD_GRAY)
        who.move_to(UP * (ZONE_FOOTER + 0.5))

        # -- Timing: 8.00s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "Textbooks blame the Sea Peoples."
        self.play(GrowFromCenter(ship), run_time=0.7); t += 0.7
        self.play(FadeIn(sea_lbl, scale=1.05), run_time=0.4); t += 0.4
        self.wait(0.4); t += 0.4

        # VTT 2.00: "Raiders who burned everything."
        self.play(LaggedStart(*[FadeIn(f, scale=0.8) for f in flames],
                              lag_ratio=0.1), run_time=0.6)                # t=2.4
        # Ship drifts forward while flames burn
        self.play(FadeIn(burned, shift=UP*0.1),
                  ship.animate.shift(RIGHT * 0.4), run_time=0.5)          # t=2.9
        self.wait(1.3); t += 1.3

        # VTT 4.50: "But no one knows who they actually were."
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(mystery, scale=1.3), run_time=0.6); t += 0.6
        self.play(Flash(mystery.get_center(), color=MUTED,
                        line_length=0.5, num_lines=8, run_time=0.3))       # t=5.4
        self.play(FadeIn(who, shift=UP*0.1), run_time=0.4); t += 0.4

        # Flames flicker during hold: scale up slightly
        self.play(flames.animate.scale(1.06).shift(UP * 0.05), run_time=1.0); t += 1.0
        target = getattr(self.__class__, 'DURATION', 4.6)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: THE CONTRADICTION (15.5-23.0s = 7.50s)
# Zones: TITLE (pill), UPPER+MID (empire badges + X), LOWER (50 YEARS), FOOTER (no invader)
# ================================================================
class Scene3_Contradiction(Scene):
    DURATION = 10.1
    def construct(self):
        self.add(gradient_bg("#0A0A0E"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE CONTRADICTION", color=EMPIRE_GOLD, fs=24)
        pill.move_to(UP * ZONE_TITLE)

        # Empire badges spread from UPPER through MID
        empires = []
        empire_data = [
            ("HITTITES", HITTITE, UP * 4.5),
            ("MYCENAEANS", MYCENAE, UP * 3.0),
            ("EGYPTIANS", EGYPT_GOLD, UP * 1.5),
            ("BABYLONIANS", BABYLON, UP * ZONE_MID),
        ]
        for name, col, pos in empire_data:
            badge = label_pill(name, color=col, bg=SURFACE2, fs=32)
            badge.move_to(pos)
            empires.append(badge)

        # X overlays for each empire
        x_overlays = VGroup()
        for _, _, pos in empire_data:
            x1 = Line(pos + LEFT*1.5 + UP*0.3, pos + RIGHT*1.5 + DOWN*0.3,
                       color=CRISIS_RED, stroke_width=5)
            x2 = Line(pos + RIGHT*1.5 + UP*0.3, pos + LEFT*1.5 + DOWN*0.3,
                       color=CRISIS_RED, stroke_width=5)
            x_overlays.add(VGroup(x1, x2))

        div = section_div(5, CRISIS_RED).move_to(DOWN * 1.5)

        # ZONE_LOWER: 50 YEARS
        fifty = safe_text("50 YEARS.", font="Bebas Neue", font_size=120, color=CRISIS_RED)
        fifty.move_to(UP * ZONE_LOWER)

        # Between LOWER and FOOTER
        no_invader = safe_text("NO INVADER COULD.", font="Bebas Neue", font_size=45, color=MUTED)
        no_invader.move_to(DOWN * 5.0)
        footer_div = section_div(3, MUTED).move_to(UP * ZONE_FOOTER)

        # -- Timing: 7.50s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "The Hittites. Mycenaeans. Egyptians. Babylonians."
        self.play(LaggedStart(*[FadeIn(e, scale=1.05) for e in empires],
                              lag_ratio=0.2), run_time=1.2)                # t=1.5
        self.wait(1.2); t += 1.2

        # VTT 3.00: "They all fell within fifty years."
        self.play(LaggedStart(*[FadeIn(x, scale=1.1) for x in x_overlays],
                              lag_ratio=0.1), run_time=0.8)                # t=3.5

        # Badges turn dim after being crossed
        self.play(*[e.animate.set_opacity(0.4) for e in empires], run_time=0.3); t += 0.3

        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(fifty, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(fifty.get_center(), color=CRISIS_RED,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=4.9

        # VTT 5.00: "No single invader could do that."
        self.play(FadeIn(no_invader, shift=UP*0.1), run_time=0.4); t += 0.4
        self.play(Create(footer_div), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 10.1)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE THEORY (23.0-31.0s = 8.00s)
# Zones: TITLE (pill), UPPER+MID (trade web), LOWER (text), FOOTER (label)
# ================================================================
class Scene4_Theory(Scene):
    DURATION = 19.2
    def construct(self):
        self.add(gradient_bg("#0A080A"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE THEORY", color=EMPIRE_GOLD, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # Trade web nodes across UPPER + MID
        nodes = [
            (-2.5, ZONE_UPPER, "TIN"), (2.5, ZONE_UPPER, "COPPER"),
            (0, 1.5, "TRADE"), (-2.0, ZONE_MID, "GRAIN"), (2.0, ZONE_MID, "IRON"),
        ]
        node_circles = VGroup()
        node_labels = VGroup()
        for x, y, lbl in nodes:
            pos = np.array([x, y, 0])
            circ = Circle(radius=0.35, fill_color=SURFACE2, fill_opacity=0.9,
                          stroke_color=BRONZE, stroke_width=2).move_to(pos)
            txt = safe_text(lbl, font="Inter", font_size=18, color=BRONZE, weight="BOLD")
            txt.move_to(pos)
            node_circles.add(circ)
            node_labels.add(txt)

        connections = [(0,2), (1,2), (2,3), (2,4), (0,3), (1,4)]
        trade_lines = VGroup()
        for a, b in connections:
            xa, ya, _ = nodes[a]; xb, yb, _ = nodes[b]
            trade_lines.add(DashedLine(np.array([xa, ya, 0]), np.array([xb, yb, 0]),
                                       color=EMPIRE_GOLD, stroke_width=1.5, dash_length=0.12))

        # The break line (TRADE -> GRAIN)
        break_line = Line(np.array([nodes[2][0], nodes[2][1], 0]),
                          np.array([nodes[3][0], nodes[3][1], 0]),
                          color=CRISIS_RED, stroke_width=5)

        source_labels = VGroup()
        for txt, pos, col in [("AFGHANISTAN", LEFT*2.5 + UP*(ZONE_UPPER + 0.8), DIM),
                               ("CYPRUS", RIGHT*2.5 + UP*(ZONE_UPPER + 0.8), DIM),
                               ("EGYPT", LEFT*2.0 + DOWN*0.8, DIM)]:
            source_labels.add(safe_text(txt, font="Inter", font_size=16, color=col, weight="BOLD")
                              .move_to(pos))

        div = section_div(5, CRISIS_RED).move_to(DOWN * 2.0)

        # ZONE_LOWER text
        starved1 = safe_text("ONE BREAK.", font="Bebas Neue", font_size=70, color=WHITE_SOFT)
        starved1.move_to(DOWN * 3.0)
        starved2 = safe_text("EVERYTHING STARVED.", font="Bebas Neue", font_size=65, color=CRISIS_RED)
        starved2.move_to(DOWN * 4.3)

        # ZONE_FOOTER
        footer_div = section_div(3, MUTED).move_to(DOWN * 5.3)
        supply = safe_text("SUPPLY CHAIN COLLAPSE.", font="Inter", font_size=22,
                           color=DEAD_GRAY, weight="BOLD")
        supply.move_to(UP * ZONE_FOOTER)

        # -- Timing: 8.00s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "Every empire depended on the others."
        self.play(LaggedStart(*[FadeIn(c, scale=1.1) for c in node_circles],
                              lag_ratio=0.08), run_time=0.6)               # t=0.9
        self.play(FadeIn(node_labels), run_time=0.3); t += 0.3
        self.wait(0.5); t += 0.5

        # VTT 2.00: "Tin from Afghanistan. Copper from Cyprus."
        self.play(LaggedStart(*[Create(dl) for dl in trade_lines],
                              lag_ratio=0.1), run_time=0.8)                # t=2.5
        self.play(FadeIn(source_labels), run_time=0.3); t += 0.3

        # Pulsing glow on TRADE hub during narration
        trade_glow = Circle(radius=0.7, fill_color=EMPIRE_GOLD, fill_opacity=0.08,
                            stroke_width=0).move_to(np.array([0, 1.5, 0]))
        self.play(FadeIn(trade_glow), run_time=0.4); t += 0.4
        self.play(trade_glow.animate.scale(1.4).set_opacity(0), run_time=1.5); t += 1.5

        # VTT 5.00: "One break and everything starved."
        self.play(Create(break_line), run_time=0.3); t += 0.3
        self.play(Flash(break_line.get_center(), color=CRISIS_RED,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=5.3

        # Connected nodes go dim after break
        self.play(node_circles.animate.set_stroke(color=RUIN_DK),
                  trade_lines.animate.set_color(RUIN_DK), run_time=0.3)   # t=5.6

        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(starved1, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(starved2, scale=1.1), run_time=0.5); t += 0.5
        self.play(Create(footer_div), run_time=0.2); t += 0.2
        self.play(FadeIn(supply, shift=UP*0.05), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 19.2)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE SCALE (31.0-38.5s = 7.50s)
# Zones: TITLE (pill), UPPER (tablet), MID (columns), LOWER (400 YEARS), FOOTER (forgot)
# ================================================================
class Scene5_Scale(Scene):
    DURATION = 5.2
    def construct(self):
        self.add(gradient_bg("#080808"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE SCALE", color=RUIN_GRAY, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # Tablet at ZONE_UPPER
        tab = tablet_shape(2.5, BRONZE_LT)
        tab.move_to(UP * ZONE_UPPER)
        writing_lbl = safe_text("WRITING", font="Bebas Neue", font_size=40, color=BRONZE_LT)
        writing_lbl.move_to(UP * 1.8)

        # Columns at ZONE_MID
        col1 = column_ruins_shape(3.0, RUIN_GRAY)
        col1.move_to(LEFT * 2.0 + UP * ZONE_MID)
        col2 = column_ruins_shape(2.5, RUIN_GRAY)
        col2.move_to(RIGHT * 2.0 + DOWN * 0.2)

        lost_lbl = safe_text("LANGUAGES LOST.", font="Bebas Neue", font_size=45, color=MUTED)
        lost_lbl.move_to(DOWN * 1.5)

        div = section_div(5, RUIN_GRAY).move_to(DOWN * 2.3)

        # ZONE_LOWER: 400 YEARS
        four_hundred = safe_text("400 YEARS", font="Bebas Neue", font_size=110, color=WHITE_SOFT)
        four_hundred.move_to(UP * (ZONE_LOWER + 0.2))
        silence = safe_text("OF SILENCE.", font="Bebas Neue", font_size=60, color=RUIN_GRAY)
        silence.move_to(DOWN * 4.5)

        # ZONE_FOOTER: forgot how to build
        forgot = safe_text("FORGOT HOW TO BUILD.", font="Bebas Neue", font_size=40, color=CRISIS_RED)
        forgot.move_to(UP * (ZONE_FOOTER + 0.4))
        footer_div = section_div(3, CRISIS_RED).move_to(UP * ZONE_FOOTER)

        # -- Timing: 7.50s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "Writing disappeared for 400 years."
        self.play(GrowFromCenter(tab), run_time=0.5); t += 0.5
        self.play(FadeIn(writing_lbl), run_time=0.3); t += 0.3

        # Tablet crumbles: fades + shifts down
        self.play(tab.animate.set_opacity(0.15).shift(DOWN*0.3),
                  writing_lbl.animate.set_opacity(0.3), run_time=0.6)     # t=1.7
        self.wait(0.5); t += 0.5

        # VTT 2.50: "Entire languages were lost."
        self.play(FadeIn(col1, shift=UP*0.2), FadeIn(col2, shift=UP*0.2),
                  run_time=0.6)                                             # t=2.8
        self.play(FadeIn(lost_lbl, shift=UP*0.1), run_time=0.4); t += 0.4

        # Columns slowly tilt/lean during narration
        self.play(col1.animate.rotate(3 * DEGREES),
                  col2.animate.rotate(-4 * DEGREES), run_time=0.8)        # t=4.0

        # VTT 4.50: "The world forgot how to build cities."
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(four_hundred, scale=1.2), run_time=0.5); t += 0.5
        self.play(FadeIn(silence, shift=UP*0.1), run_time=0.4); t += 0.4
        self.play(FadeIn(forgot, scale=1.05), run_time=0.4); t += 0.4
        self.play(Create(footer_div), run_time=0.2); t += 0.2
        self.play(Flash(forgot.get_center(), color=CRISIS_RED,
                        line_length=0.3, num_lines=6, run_time=0.3))       # t=6.1
        target = getattr(self.__class__, 'DURATION', 5.2)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE PUNCH (38.5-46.3s = 7.80s)
# Zones: TITLE (letterbox), UPPER (modern trade web), MID (3000 YEARS), LOWER (SOUND FAMILIAR?), FOOTER (glow)
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 1.2
    def construct(self):
        self.add(gradient_bg("#050508"), grid_lines(0.02))
        t = 0

        # Letterbox bars
        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP * (8 - bh/2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN * (8 - bh/2)),
        )

        # Ghost column ruins behind everything
        ghost = column_ruins_shape(5, RUIN_GRAY)
        ghost.move_to(DOWN * 1)
        ghost.set_opacity(0.04)
        self.add(ghost)

        # Modern trade web at ZONE_UPPER
        web_nodes = VGroup()
        web_positions = [(-2, ZONE_UPPER), (2, ZONE_UPPER), (0, 2), (-2, 0.8), (2, 0.8)]
        web_labels_list = ["OIL", "CHIPS", "TRADE", "GRAIN", "RARE\nEARTH"]
        for (x, y), lbl in zip(web_positions, web_labels_list):
            circ = Circle(radius=0.3, fill_color=SURFACE2, fill_opacity=0.9,
                          stroke_color=BRONZE, stroke_width=2).move_to(np.array([x, y, 0]))
            txt = safe_text(lbl, font="Inter", font_size=14, color=BRONZE, weight="BOLD")
            txt.move_to(np.array([x, y, 0]))
            web_nodes.add(VGroup(circ, txt))

        web_lines = VGroup()
        for a, b in [(0,2), (1,2), (2,3), (2,4), (0,3), (1,4)]:
            xa, ya = web_positions[a]; xb, yb = web_positions[b]
            web_lines.add(DashedLine(np.array([xa, ya, 0]), np.array([xb, yb, 0]),
                                     color=EMPIRE_GOLD, stroke_width=1.5, dash_length=0.12))

        div1 = section_div(4, CRISIS_RED).move_to(DOWN * 0.5)

        # ZONE_MID-ish: 3000 years
        three_k = safe_text("3,000 YEARS.", font="Bebas Neue", font_size=60, color=MUTED)
        three_k.move_to(DOWN * 1.5)

        # ZONE_LOWER: SOUND FAMILIAR?
        sound = safe_text("SOUND", font="Bebas Neue", font_size=90, color=WHITE_SOFT)
        sound.move_to(DOWN * 3.0)
        familiar = safe_text("FAMILIAR?", font="Bebas Neue", font_size=100, color=CRISIS_RED)
        familiar.move_to(DOWN * 4.3)
        glow = Circle(radius=2.5, fill_color=CRISIS_RED, fill_opacity=0.04,
                      stroke_width=0).move_to(familiar)

        # -- Timing: 7.80s + 3s hold+fade --
        # VTT 0.10: "It took 3,000 years to figure out what happened."
        self.play(LaggedStart(*[Create(dl) for dl in web_lines],
                              lag_ratio=0.08), run_time=0.6)               # t=0.6
        self.play(LaggedStart(*[FadeIn(n, scale=1.1) for n in web_nodes],
                              lag_ratio=0.06), run_time=0.5)               # t=1.1
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(three_k, shift=UP*0.08), run_time=0.5); t += 0.5

        # VTT 3.00: "A globalized system so connected..."
        # Web pulses and lines turn red to echo the ancient collapse
        web_pulse = Circle(radius=1.2, fill_color=EMPIRE_GOLD, fill_opacity=0.06,
                           stroke_width=0).move_to(np.array([0, 2, 0]))
        self.play(FadeIn(web_pulse), run_time=0.4); t += 0.4
        self.play(web_pulse.animate.scale(1.5).set_opacity(0),
                  web_lines.animate.set_color(CRISIS_RED), run_time=1.4)  # t=3.7

        # Ghost ruins slowly emerge during "when one part failed"
        self.play(ghost.animate.set_opacity(0.12), run_time=1.0); t += 1.0

        # VTT 5.50: "everything fell. Sound familiar?"
        self.play(FadeIn(sound, shift=UP*0.08), run_time=0.5); t += 0.5
        self.play(FadeIn(glow), FadeIn(familiar, scale=1.15), run_time=0.7); t += 0.7
        self.play(Flash(familiar.get_center(), color=CRISIS_RED,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=6.2

        # Hold + fade
        target = getattr(self.__class__, 'DURATION', 1.2)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5


# -- Infra -------------------------------------------------------------
def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_WrongAnswer, Scene3_Contradiction,
          Scene4_Theory, Scene5_Scale, Scene6_Punch]
    config.output_file = f"bronze_age_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"bronze_age_scene_{idx+1}.mp4"):
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

    names = ["Scene1_Hook","Scene2_WrongAnswer","Scene3_Contradiction",
             "Scene4_Theory","Scene5_Scale","Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_bronze_age.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="bronze_age", audio_path=str(audio))
    final = od / "bronze_age_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
