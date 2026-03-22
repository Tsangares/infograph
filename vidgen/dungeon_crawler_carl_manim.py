#!/usr/bin/env python3
"""Dungeon Crawler Carl — Book Rec (Manim). Chaotic fun energy.

6 scenes, ~37.0s (34.0s audio + 3s hold).
NOTE: Book recommendation format — playful, fast, enthusiastic. Not mystery arc.

VTT cues (absolute → relative):
  Scene 1 (0.0–5.0s = 5.00s):
    0.100 (0.10) One morning, aliens collapsed every building on the planet.
    2.500 (2.50) Billions dead.
    3.500 (3.50) No warning. No reason.
  Scene 2 (5.0–10.0s = 5.00s):
    5.100 (0.10) The survivors got a message:
    6.200 (1.20) enter the dungeon beneath the rubble,
    7.500 (2.50) or die on the surface in 12 hours.
    8.800 (3.80) Carl entered in his underwear.
  Scene 3 (10.0–15.5s = 5.50s):
    10.100 (0.10) He grabbed one thing.
    11.000 (1.00) His ex-girlfriend's cat.
    12.000 (2.00) Her name is Princess Donut.
    13.200 (3.20) She got a character class.
    14.200 (4.20) And she is an absolute menace.
  Scene 4 (15.5–21.0s = 5.50s):
    15.600 (0.10) The whole thing is a game show.
    16.800 (1.30) The entire galaxy is watching.
    18.000 (2.50) They're placing bets.
    19.000 (3.50) They're sending care packages.
    19.800 (4.30) They have fan favorites.
  Scene 5 (21.0–27.0s = 6.00s):
    21.100 (0.10) Carl is fighting eldritch horrors in boxer shorts.
    23.000 (2.00) The cat has a tiara and a kill count.
    24.500 (3.50) Every floor is worse than the last.
    25.500 (4.50) And it's somehow hilarious.
  Scene 6 (27.0–37.0s = 10.00s):
    27.100 (0.10) The worst part?
    28.500 (1.50) You're gonna be cheering for them
    30.000 (3.00) by page 50.
    + 3s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """One morning, aliens collapsed every building on the planet. Billions dead. No warning. No reason.
The survivors got a message: enter the dungeon beneath the rubble, or die on the surface in twelve hours. Carl entered in his underwear.
He grabbed one thing. His ex-girlfriend's cat. Her name is Princess Donut. She got a character class. And she is an absolute menace.
The whole thing is a game show. The entire galaxy is watching. They're placing bets. They're sending care packages. They have fan favorites.
Carl is fighting eldritch horrors in boxer shorts. The cat has a tiara and a kill count. Every floor is worse than the last. And it's somehow hilarious.
The worst part? You're gonna be cheering for them by page fifty."""

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
DUNGEON_STONE = "#4A4A5A"; CHAOS_PURPLE = "#7B2FBE"
CAT_ORANGE = "#FF8C00"; TIARA_GOLD = "#FFD700"
BLOOD_RED = "#CC0000"
WHITE_SOFT = "#F0F0F0"; MUTED = "#7B8DA0"; DIM = "#404050"
DEAD_GRAY = "#4A5568"; GOLD = "#FFD700"
SAFE_W = 8.0

ZONE_TITLE  = 6.2
ZONE_UPPER  = 3.5
ZONE_MID    = 0.0
ZONE_LOWER  = -3.5
ZONE_FOOTER = -6.0


def gradient_bg(c=BG, g="#100A18"):
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

def section_div(width=5, color=CHAOS_PURPLE):
    l = Line(LEFT*width/2, LEFT*0.12, color=color, stroke_width=1.5)
    r = Line(RIGHT*0.12, RIGHT*width/2, color=color, stroke_width=1.5)
    d = Square(side_length=0.1, color=color, fill_color=color, fill_opacity=1).rotate(45*DEGREES)
    return VGroup(l, d, r)

def label_pill(txt, color=CHAOS_PURPLE, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    p = RoundedRectangle(width=t.width+0.5, height=t.height+0.3, corner_radius=0.18,
                         fill_color=bg, fill_opacity=0.95, stroke_color=color, stroke_width=1.5).move_to(t)
    return VGroup(p, t)

def safe_text(content, **kwargs):
    t = Text(content, **kwargs)
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    return t


# -- Domain Shape Helpers ------------------------------------------------

def dungeon_door(height=3.5, width=2.5, color=DUNGEON_STONE):
    """Heavy stone door with iron bars and arch."""
    sc = height / 3.5
    frame = Rectangle(width=width*sc, height=height*sc, fill_color=color,
                      fill_opacity=0.7, stroke_color=MUTED, stroke_width=2)
    bars = VGroup()
    for i in range(4):
        x = -0.6*sc + i * 0.4*sc
        bar = Line(UP * 1.5*sc, DOWN * 1.5*sc, color=DEAD_GRAY, stroke_width=2.5)
        bar.move_to(RIGHT * x)
        bars.add(bar)
    cross = Line(LEFT * 0.8*sc, RIGHT * 0.8*sc, color=DEAD_GRAY, stroke_width=2.5)
    cross.move_to(UP * 0.3*sc)
    arch = Arc(radius=0.9*sc, start_angle=0, angle=PI, color=MUTED, stroke_width=2.5)
    arch.move_to(UP * 1.4*sc)
    return VGroup(frame, bars, cross, arch)

def cat_face(color=CAT_ORANGE, h=2.0):
    """Simple cat head -- circle + triangle ears + eyes + whiskers."""
    sc = h / 2.0
    head = Circle(radius=0.8*sc, fill_color=color, fill_opacity=0.85,
                  stroke_color=color, stroke_width=1.5)
    ear_l = Polygon(
        np.array([-0.55*sc, 0.55*sc, 0]),
        np.array([-0.75*sc, 1.1*sc, 0]),
        np.array([-0.3*sc, 0.75*sc, 0]),
        fill_color=color, fill_opacity=0.9, stroke_width=0)
    ear_r = Polygon(
        np.array([0.55*sc, 0.55*sc, 0]),
        np.array([0.75*sc, 1.1*sc, 0]),
        np.array([0.3*sc, 0.75*sc, 0]),
        fill_color=color, fill_opacity=0.9, stroke_width=0)
    eye_l = Dot(LEFT * 0.3*sc + UP * 0.15*sc, radius=0.08*sc, color=TIARA_GOLD)
    eye_r = Dot(RIGHT * 0.3*sc + UP * 0.15*sc, radius=0.08*sc, color=TIARA_GOLD)
    nose = Dot(DOWN * 0.05*sc, radius=0.04*sc, color=BLOOD_RED)
    whiskers = VGroup()
    for side in [-1, 1]:
        for dy in [-0.08, 0.0, 0.08]:
            w = Line(np.array([side * 0.35*sc, -0.1*sc + dy*sc, 0]),
                     np.array([side * 0.8*sc, -0.15*sc + dy*sc, 0]),
                     color=WHITE_SOFT, stroke_width=1)
            whiskers.add(w)
    return VGroup(head, ear_l, ear_r, eye_l, eye_r, nose, whiskers)

def crown_tiara(color=TIARA_GOLD, w=1.2):
    """Tiara/crown -- arc of points from base."""
    sc = w / 1.2
    base = Rectangle(width=1.0*sc, height=0.12*sc, fill_color=color,
                     fill_opacity=0.9, stroke_width=0).move_to(DOWN * 0.05*sc)
    points = VGroup()
    for i in range(5):
        x = -0.4*sc + i * 0.2*sc
        tip_h = 0.35*sc if i % 2 == 0 else 0.25*sc
        pt = Polygon(
            np.array([x - 0.06*sc, 0.0, 0]),
            np.array([x, tip_h, 0]),
            np.array([x + 0.06*sc, 0.0, 0]),
            fill_color=color, fill_opacity=0.9, stroke_width=0)
        points.add(pt)
    return VGroup(base, points)

def alien_shape(color=CHAOS_PURPLE, h=1.5):
    """UFO silhouette -- dome + disc base + lights."""
    sc = h / 1.5
    dome = Ellipse(width=1.0*sc, height=0.6*sc, fill_color=color, fill_opacity=0.7,
                   stroke_color=color, stroke_width=1.5).move_to(UP * 0.2*sc)
    disc = Ellipse(width=1.8*sc, height=0.4*sc, fill_color=color, fill_opacity=0.5,
                   stroke_color=color, stroke_width=1).move_to(DOWN * 0.05*sc)
    lights = VGroup()
    for x in [-0.4, 0, 0.4]:
        l = Dot(np.array([x*sc, -0.2*sc, 0]), radius=0.04*sc, color=TIARA_GOLD)
        lights.add(l)
    return VGroup(disc, dome, lights)

def stick_figure(color=WHITE_SOFT, h=1.5, boxers=False):
    """Simple stick figure -- optional boxer shorts."""
    sc = h / 1.5
    head = Circle(radius=0.12*sc, fill_color=color, fill_opacity=0.9, stroke_width=0)
    head.move_to(UP * 0.55*sc)
    body = Line(UP * 0.43*sc, DOWN * 0.15*sc, color=color, stroke_width=2)
    l_leg = Line(DOWN * 0.15*sc, DOWN * 0.55*sc + LEFT * 0.18*sc, color=color, stroke_width=1.5)
    r_leg = Line(DOWN * 0.15*sc, DOWN * 0.55*sc + RIGHT * 0.18*sc, color=color, stroke_width=1.5)
    l_arm = Line(UP * 0.25*sc, LEFT * 0.22*sc + UP * 0.05*sc, color=color, stroke_width=1.5)
    r_arm = Line(UP * 0.25*sc, RIGHT * 0.22*sc + UP * 0.05*sc, color=color, stroke_width=1.5)
    parts = VGroup(head, body, l_leg, r_leg, l_arm, r_arm)
    if boxers:
        shorts = Rectangle(width=0.25*sc, height=0.15*sc, fill_color=CHAOS_PURPLE,
                          fill_opacity=0.9, stroke_width=0).move_to(DOWN * 0.1*sc)
        parts.add(shorts)
    return parts

def rubble_pile(w=6.0, h=1.5, color=DUNGEON_STONE):
    """Heap of broken rectangles -- post-collapse rubble."""
    sc = w / 6.0
    pile = VGroup()
    np.random.seed(33)
    for _ in range(12):
        bw = np.random.uniform(0.3, 0.9) * sc
        bh = np.random.uniform(0.15, 0.4) * sc
        ang = np.random.uniform(-30, 30) * DEGREES
        x = np.random.uniform(-2.5, 2.5) * sc
        y = np.random.uniform(-0.3, 0.4) * sc
        r = Rectangle(width=bw, height=bh, fill_color=color, fill_opacity=0.5,
                      stroke_color=MUTED, stroke_width=0.6).rotate(ang)
        r.move_to(np.array([x, y, 0]))
        pile.add(r)
    return pile


# ================================================================
# SCENE 1: THE END (0.0-5.0s = 5.00s)
# "Aliens collapsed every building. Billions dead."
# Zones: TITLE(pill) UPPER(UFOs descending) MID(buildings collapse) LOWER(BILLIONS DEAD flash) FOOTER(rubble)
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 3.9
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0
        self.add(star_field(20, seed=1))

        pill = label_pill("BOOK REC", color=CHAOS_PURPLE, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # UFOs at ZONE_UPPER -- will drift down
        ufos = VGroup()
        ufo_targets = [LEFT*2.5 + UP*4.5, RIGHT*1 + UP*5, LEFT*0.5 + UP*3.8]
        for pos in ufo_targets:
            u = alien_shape(CHAOS_PURPLE, h=1.0)
            u.move_to(pos + UP * 2)  # start offscreen high
            ufos.add(u)

        # Buildings at ZONE_MID -- will collapse
        buildings = VGroup()
        np.random.seed(11)
        for i in range(7):
            bw = np.random.uniform(0.6, 1.0)
            bh = np.random.uniform(1.5, 3.0)
            b = Rectangle(width=bw, height=bh, fill_color=DUNGEON_STONE,
                         fill_opacity=0.6, stroke_color=MUTED, stroke_width=0.8)
            b.move_to(LEFT * 3 + RIGHT * i * 0.9 + UP * (bh/2 - 0.5))
            buildings.add(b)

        # Rubble at ZONE_LOWER -- appears after collapse
        rubble = rubble_pile(7, 1.2, DUNGEON_STONE)
        rubble.move_to(DOWN * ZONE_LOWER + UP * 1)

        billions = safe_text("BILLIONS DEAD.", font="Bebas Neue", font_size=100,
                            color=BLOOD_RED)
        billions.move_to(DOWN * ZONE_LOWER)

        footer = safe_text("DUNGEON CRAWLER CARL", font="Inter",
                          font_size=22, color=CHAOS_PURPLE, weight="BOLD")
        footer.move_to(DOWN * ZONE_FOOTER)

        # -- Timing: 5.00s (fast energy) --
        self.play(FadeIn(pill, scale=1.05), run_time=0.2); t += 0.2
        # UFOs drift in from above
        self.play(
            LaggedStart(*[u.animate.shift(DOWN * 2) for u in ufos], lag_ratio=0.08),
            run_time=0.5,
        )                                                                   # t=0.7
        self.play(FadeIn(buildings), run_time=0.3); t += 0.3
        # Buildings collapse -- shake then fall
        self.play(
            *[b.animate.shift(RIGHT * 0.08) for b in buildings],
            run_time=0.08,
        )                                                                   # t=1.08
        self.play(
            *[b.animate.shift(LEFT * 0.16) for b in buildings],
            run_time=0.08,
        )                                                                   # t=1.16
        self.play(
            *[b.animate.shift(DOWN * 3).set_opacity(0.1) for b in buildings],
            run_time=0.5,
        )                                                                   # t=1.66
        self.play(FadeIn(rubble, scale=0.9), run_time=0.3); t += 0.3
        self.wait(0.54); t += 0.54
        self.play(FadeIn(billions, scale=1.2), run_time=0.35); t += 0.35
        self.play(Flash(billions.get_center(), color=BLOOD_RED,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=3.15
        # UFOs pulse menacingly during wait
        self.play(
            *[u.animate.scale(1.08) for u in ufos],
            run_time=0.3,
        )                                                                   # t=3.45
        self.play(
            *[u.animate.scale(1/1.08) for u in ufos],
            FadeIn(footer),
            run_time=0.3,
        )                                                                   # t=3.75
        target = getattr(self.__class__, 'DURATION', 3.9)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE OFFER (5.0-10.0s = 5.00s)
# "Enter the dungeon or die. Carl entered in his underwear."
# Zones: TITLE(pill) UPPER(12 HOURS) MID(dungeon door opening) LOWER(Carl walking in) FOOTER(label)
# ================================================================
class Scene2_Offer(Scene):
    DURATION = 3.9
    def construct(self):
        self.add(gradient_bg("#080810"), grid_lines(0.03))
        t = 0
        self.add(star_field(10, seed=7))

        pill = label_pill("THE OFFER", color=DUNGEON_STONE, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        hours = safe_text("12 HOURS", font="Bebas Neue", font_size=110, color=BLOOD_RED)
        hours.move_to(UP * ZONE_UPPER)

        # Dungeon door at ZONE_MID -- will "open" (split apart)
        door_left = Rectangle(width=1.2, height=3.5, fill_color=DUNGEON_STONE,
                              fill_opacity=0.7, stroke_color=MUTED, stroke_width=2)
        door_right = door_left.copy()
        door_left.move_to(LEFT * 0.6 + UP * ZONE_MID)
        door_right.move_to(RIGHT * 0.6 + UP * ZONE_MID)
        # Arch over the doors
        arch = Arc(radius=1.3, start_angle=0, angle=PI, color=MUTED, stroke_width=2.5)
        arch.move_to(UP * 1.5)
        # Iron bars across
        bars = VGroup()
        for i in range(4):
            x = -0.6 + i * 0.4
            bar = Line(UP * 1.5, DOWN * 1.5, color=DEAD_GRAY, stroke_width=2)
            bar.move_to(RIGHT * x + UP * ZONE_MID)
            bars.add(bar)
        door_group = VGroup(door_left, door_right, bars, arch)

        # Glow behind door (reveals when it opens)
        door_glow = Circle(radius=1.8, fill_color=CHAOS_PURPLE, fill_opacity=0.12,
                          stroke_width=0).move_to(UP * ZONE_MID)

        # Carl walking toward door -- ZONE_LOWER
        carl = stick_figure(WHITE_SOFT, h=1.5, boxers=True)
        carl.move_to(DOWN * ZONE_LOWER + RIGHT * 3)  # starts right, walks left

        underwear_pill = label_pill("UNDERWEAR.", color=CHAOS_PURPLE, fs=26)
        underwear_pill.move_to(DOWN * 5.2)

        footer = safe_text("CARL ENTERED", font="Inter",
                          font_size=20, color=DEAD_GRAY, weight="BOLD")
        footer.move_to(DOWN * ZONE_FOOTER)

        # -- Timing: 5.00s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.2); t += 0.2
        self.play(FadeIn(hours, scale=1.15), run_time=0.4); t += 0.4
        self.play(Flash(hours.get_center(), color=BLOOD_RED,
                        line_length=0.4, num_lines=8, run_time=0.2))       # t=0.8
        self.play(FadeIn(door_group, scale=0.9), run_time=0.5); t += 0.5
        self.wait(0.7); t += 0.7
        # Door opens -- halves slide apart, glow revealed
        self.play(
            door_left.animate.shift(LEFT * 1.2),
            door_right.animate.shift(RIGHT * 1.2),
            *[b.animate.set_opacity(0.2) for b in bars],
            FadeIn(door_glow),
            run_time=0.5,
        )                                                                   # t=2.5
        self.wait(0.5); t += 0.5
        # Carl walks in from right
        self.play(FadeIn(carl, shift=LEFT * 0.3), run_time=0.3); t += 0.3
        self.play(carl.animate.shift(LEFT * 3), run_time=0.7); t += 0.7
        self.play(FadeIn(underwear_pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(footer), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 3.9)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: THE CAT (10.0-15.5s = 5.50s)
# "Princess Donut. Character class. Absolute menace."
# Zones: TITLE(pill) UPPER(cat grows) MID(PRINCESS DONUT) LOWER(class pill+tiara flash) FOOTER(label)
# ================================================================
class Scene3_Cat(Scene):
    DURATION = 4.3
    def construct(self):
        self.add(gradient_bg(g="#180A00"), grid_lines(0.03))
        t = 0
        self.add(star_field(12, seed=13))

        pill = label_pill("THE CAT", color=CAT_ORANGE, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # Cat face at UPPER/MID boundary -- grows in
        cat = cat_face(CAT_ORANGE, h=3.5)
        cat.move_to(UP * 1.5)

        # Tiara drops onto cat
        tiara = crown_tiara(TIARA_GOLD, w=1.5)
        tiara.move_to(UP * 3.3)

        princess = safe_text("PRINCESS DONUT", font="Bebas Neue", font_size=90,
                            color=CAT_ORANGE)
        princess.move_to(DOWN * 1.2)

        # Class pill at ZONE_LOWER
        lvl = label_pill("LVL ???", color=CHAOS_PURPLE, fs=24)
        lvl.move_to(DOWN * ZONE_LOWER + UP * 0.5)

        # Kill tally marks at ZONE_LOWER
        tallies = VGroup()
        for i in range(5):
            mark = Line(UP * 0.3, DOWN * 0.3, color=BLOOD_RED, stroke_width=2)
            mark.move_to(LEFT * 1.5 + RIGHT * i * 0.3 + DOWN * ZONE_LOWER - UP * 0.5)
            tallies.add(mark)
        # Cross-line for 5th
        cross_tally = Line(
            tallies[0].get_center() + DOWN * 0.35 + LEFT * 0.1,
            tallies[4].get_center() + UP * 0.35 + RIGHT * 0.1,
            color=BLOOD_RED, stroke_width=1.5,
        )

        menace = safe_text("MENACE.", font="Bebas Neue", font_size=70,
                          color=TIARA_GOLD)
        menace.move_to(DOWN * 5.2)

        footer = safe_text("CLASS: ACQUIRED", font="Inter",
                          font_size=20, color=DEAD_GRAY, weight="BOLD")
        footer.move_to(DOWN * ZONE_FOOTER)

        # -- Timing: 5.50s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.2); t += 0.2
        self.play(GrowFromCenter(cat), run_time=0.5); t += 0.5
        self.wait(0.3); t += 0.3
        # Tiara drops from above
        tiara_start = tiara.copy().shift(UP * 3)
        self.add(tiara_start)
        self.play(tiara_start.animate.move_to(tiara.get_center()),
                  run_time=0.3)                                             # t=1.3
        self.remove(tiara_start); self.add(tiara)
        self.play(Flash(tiara.get_center(), color=TIARA_GOLD,
                        line_length=0.3, num_lines=8, run_time=0.2))       # t=1.5
        # Cat eyes flash
        self.play(
            cat[3].animate.scale(1.4),  # eye_l
            cat[4].animate.scale(1.4),  # eye_r
            run_time=0.15,
        )                                                                   # t=1.65
        self.play(
            cat[3].animate.scale(1/1.4),
            cat[4].animate.scale(1/1.4),
            run_time=0.15,
        )                                                                   # t=1.8
        self.play(FadeIn(princess, scale=1.1), run_time=0.4); t += 0.4
        self.play(Flash(princess.get_center(), color=CAT_ORANGE,
                        line_length=0.4, num_lines=10, run_time=0.2))      # t=2.4
        self.play(FadeIn(lvl, scale=1.05), run_time=0.3); t += 0.3
        self.wait(0.5); t += 0.5
        # Tally marks appear one by one
        self.play(LaggedStart(*[Create(m) for m in tallies],
                              lag_ratio=0.1), run_time=0.4)                # t=3.6
        self.play(Create(cross_tally), run_time=0.15); t += 0.15
        self.wait(0.45); t += 0.45
        self.play(FadeIn(menace, scale=1.08), run_time=0.3); t += 0.3
        self.play(Flash(menace.get_center(), color=TIARA_GOLD,
                        line_length=0.3, num_lines=6, run_time=0.2))       # t=4.7
        self.play(FadeIn(footer), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 4.3)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE SHOW (15.5-21.0s = 5.50s)
# "Game show. Galaxy watching. Placing bets."
# Zones: TITLE(pill) UPPER(broadcast screens) MID(viewer crowd) LOWER(bet ticker) FOOTER(fan faves)
# ================================================================
class Scene4_Show(Scene):
    DURATION = 4.3
    def construct(self):
        self.add(gradient_bg("#0A0810"), grid_lines(0.03))
        t = 0
        self.add(star_field(15, seed=44))

        pill = label_pill("THE SHOW", color=CHAOS_PURPLE, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # 3 broadcast screens at ZONE_UPPER
        screens = VGroup()
        for i, x in enumerate([-2.5, 0, 2.5]):
            screen = Rectangle(width=2.2, height=1.6, fill_color=SURFACE2,
                              fill_opacity=0.8, stroke_color=CHAOS_PURPLE, stroke_width=1.5)
            screen.move_to(RIGHT * x + UP * ZONE_UPPER)
            # Scanline effect
            scanlines = VGroup()
            for sy in range(-3, 4):
                sl = Line(LEFT * 0.9, RIGHT * 0.9, color=CHAOS_PURPLE, stroke_width=0.3)
                sl.set_opacity(0.2).move_to(screen.get_center() + UP * sy * 0.2)
                scanlines.add(sl)
            screens.add(VGroup(screen, scanlines))

        # Central "LIVE" indicator
        live_dot = Dot(UP * ZONE_UPPER + UP * 1.2 + RIGHT * 3.2,
                      radius=0.08, color=BLOOD_RED)
        live_txt = safe_text("LIVE", font="Inter", font_size=18, color=BLOOD_RED, weight="BOLD")
        live_txt.next_to(live_dot, RIGHT, buff=0.1)
        live_group = VGroup(live_dot, live_txt)

        # Viewer crowd at ZONE_MID -- rows of dots (galactic audience)
        crowd = VGroup()
        np.random.seed(77)
        for row in range(4):
            for col in range(10):
                x = -3.5 + col * 0.8 + np.random.uniform(-0.15, 0.15)
                y = -0.5 - row * 0.7 + np.random.uniform(-0.1, 0.1)
                color = [MUTED, CHAOS_PURPLE, DEAD_GRAY][np.random.randint(0, 3)]
                d = Dot(np.array([x, y, 0]), radius=0.06, color=color).set_opacity(0.5)
                crowd.add(d)

        # Bet ticker at ZONE_LOWER
        bet_bar = Rectangle(width=7, height=0.6, fill_color=SURFACE2,
                           fill_opacity=0.85, stroke_color=CHAOS_PURPLE, stroke_width=1)
        bet_bar.move_to(DOWN * ZONE_LOWER + UP * 0.5)
        bet_txt = safe_text("BETS: 2.4M CR", font="Bebas Neue", font_size=36,
                           color=TIARA_GOLD)
        bet_txt.move_to(bet_bar)
        bet_group = VGroup(bet_bar, bet_txt)

        # Care packages -- small gift boxes at ZONE_LOWER
        packages = VGroup()
        for i, x in enumerate([-2.5, -0.8, 1.0, 2.8]):
            box = Rectangle(width=0.5, height=0.5, fill_color=CHAOS_PURPLE,
                           fill_opacity=0.5, stroke_color=TIARA_GOLD, stroke_width=1)
            ribbon_v = Line(UP * 0.25, DOWN * 0.25, color=TIARA_GOLD, stroke_width=1)
            ribbon_h = Line(LEFT * 0.25, RIGHT * 0.25, color=TIARA_GOLD, stroke_width=1)
            pkg = VGroup(box, ribbon_v, ribbon_h)
            pkg.move_to(RIGHT * x + DOWN * ZONE_LOWER - UP * 0.5)
            packages.add(pkg)

        fan_faves = safe_text("FAN FAVORITES", font="Inter", font_size=28,
                             color=CHAOS_PURPLE, weight="BOLD")
        fan_faves.move_to(DOWN * ZONE_FOOTER)

        # -- Timing: 5.50s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.2); t += 0.2
        self.play(LaggedStart(*[FadeIn(s, scale=0.9) for s in screens],
                              lag_ratio=0.1), run_time=0.5)                # t=0.7
        self.play(FadeIn(live_group), run_time=0.2); t += 0.2
        # Crowd appears in wave
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in crowd],
                              lag_ratio=0.01), run_time=0.5)               # t=1.4
        self.wait(0.6); t += 0.6
        # Screens flicker -- brief color pulse
        self.play(
            *[s[0].animate.set_stroke(color=TIARA_GOLD) for s in screens],
            run_time=0.15,
        )                                                                   # t=2.15
        self.play(
            *[s[0].animate.set_stroke(color=CHAOS_PURPLE) for s in screens],
            run_time=0.15,
        )                                                                   # t=2.3
        self.play(FadeIn(bet_group, shift=UP * 0.2), run_time=0.3); t += 0.3
        self.wait(0.4); t += 0.4
        # Care packages drop in
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.5) for p in packages],
                              lag_ratio=0.08), run_time=0.4)               # t=3.4
        self.wait(0.8); t += 0.8
        # Crowd pulses (excitement)
        self.play(
            *[d.animate.scale(1.3).set_opacity(0.7) for d in crowd[:15]],
            run_time=0.2,
        )                                                                   # t=4.4
        self.play(
            *[d.animate.scale(1/1.3).set_opacity(0.5) for d in crowd[:15]],
            run_time=0.2,
        )                                                                   # t=4.6
        self.play(FadeIn(fan_faves, shift=UP * 0.04), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 4.3)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE CHAOS (21.0-27.0s = 6.00s)
# "Eldritch horrors vs Carl in boxers. Cat has kill count."
# Zones: TITLE(pill) UPPER(monster) MID(carl+cat fighting) LOWER(kill counter) FOOTER(floor counter)
# ================================================================
class Scene5_Chaos(Scene):
    DURATION = 4.7
    def construct(self):
        self.add(gradient_bg(g="#0A050A"), grid_lines(0.03))
        t = 0
        self.add(star_field(10, seed=55))

        pill = label_pill("THE CHAOS", color=BLOOD_RED, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # Monster silhouette -- ZONE_UPPER (tentacle horror)
        monster_body = Ellipse(width=4, height=2.5, fill_color=BLOOD_RED,
                              fill_opacity=0.15, stroke_color=BLOOD_RED, stroke_width=2)
        monster_body.move_to(UP * ZONE_UPPER)
        m_eye_l = Dot(LEFT * 0.8 + UP * ZONE_UPPER + UP * 0.2, radius=0.15, color=BLOOD_RED)
        m_eye_r = Dot(RIGHT * 0.8 + UP * ZONE_UPPER + UP * 0.2, radius=0.15, color=BLOOD_RED)
        # Tentacles
        tentacles = VGroup()
        for angle, length in [(-0.6, 2.5), (-0.3, 2.0), (0.3, 2.0), (0.6, 2.5)]:
            tl = Line(
                monster_body.get_center() + DOWN * 0.8,
                monster_body.get_center() + DOWN * length + RIGHT * angle * 3,
                color=BLOOD_RED, stroke_width=1.5,
            ).set_opacity(0.4)
            tentacles.add(tl)
        monster = VGroup(monster_body, m_eye_l, m_eye_r, tentacles)

        # Carl + cat at ZONE_MID -- facing the monster
        carl = stick_figure(WHITE_SOFT, h=1.4, boxers=True)
        carl.move_to(LEFT * 1.5 + UP * ZONE_MID)
        cat_mini = cat_face(CAT_ORANGE, h=1.0)
        cat_mini.move_to(RIGHT * 1.0 + UP * ZONE_MID - UP * 0.2)
        tiara_mini = crown_tiara(TIARA_GOLD, w=0.6)
        tiara_mini.move_to(RIGHT * 1.0 + UP * ZONE_MID + UP * 0.5)

        # Kill counter at ZONE_LOWER
        kill_bg = Rectangle(width=4, height=1.2, fill_color=SURFACE2,
                           fill_opacity=0.85, stroke_color=BLOOD_RED, stroke_width=1.5)
        kill_bg.move_to(DOWN * ZONE_LOWER + UP * 0.3)
        kill_label = safe_text("KILLS", font="Inter", font_size=24, color=DEAD_GRAY, weight="BOLD")
        kill_label.move_to(kill_bg.get_center() + UP * 0.25)
        kill_num = safe_text("47", font="Bebas Neue", font_size=70, color=BLOOD_RED)
        kill_num.move_to(kill_bg.get_center() + DOWN * 0.15)
        kill_group = VGroup(kill_bg, kill_label, kill_num)

        # Floor counter at ZONE_LOWER bottom
        floors = VGroup()
        for i in range(6):
            f = Rectangle(width=0.8, height=0.35, fill_color=DUNGEON_STONE,
                         fill_opacity=0.4 + i * 0.1, stroke_color=MUTED, stroke_width=0.8)
            f.move_to(LEFT * 2 + RIGHT * i * 1.0 + DOWN * ZONE_LOWER - UP * 0.8)
            floors.add(f)
        floor_label = safe_text("FLOORS", font="Inter", font_size=18, color=DEAD_GRAY)
        floor_label.move_to(DOWN * ZONE_LOWER - UP * 1.5)

        footer = safe_text("EVERY FLOOR WORSE", font="Inter",
                          font_size=22, color=DEAD_GRAY, weight="BOLD")
        footer.move_to(DOWN * ZONE_FOOTER)

        # -- Timing: 6.00s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.2); t += 0.2
        self.play(FadeIn(monster, scale=0.85), run_time=0.4); t += 0.4
        # Monster pulses
        self.play(monster_body.animate.scale(1.06), run_time=0.15); t += 0.15
        self.play(monster_body.animate.scale(1/1.06), run_time=0.15); t += 0.15
        self.play(
            FadeIn(carl, shift=RIGHT * 0.3),
            run_time=0.3,
        )                                                                   # t=1.2
        self.play(
            FadeIn(cat_mini, scale=0.9),
            FadeIn(tiara_mini, shift=DOWN * 0.1),
            run_time=0.3,
        )                                                                   # t=1.5
        # Tiara sparkle
        self.play(Flash(tiara_mini.get_center(), color=TIARA_GOLD,
                        line_length=0.2, num_lines=6, run_time=0.2))       # t=1.7
        self.wait(0.3); t += 0.3
        # Kill counter slams in
        self.play(FadeIn(kill_group, scale=1.15), run_time=0.3); t += 0.3
        self.play(Flash(kill_num.get_center(), color=BLOOD_RED,
                        line_length=0.3, num_lines=8, run_time=0.2))       # t=2.5
        # Monster tentacles reach toward carl
        self.play(
            *[t.animate.shift(DOWN * 0.5) for t in tentacles],
            carl.animate.shift(LEFT * 0.15),  # carl dodges
            run_time=0.3,
        )                                                                   # t=2.8
        self.play(
            *[t.animate.shift(UP * 0.5) for t in tentacles],
            carl.animate.shift(RIGHT * 0.15),
            run_time=0.3,
        )                                                                   # t=3.1
        self.wait(0.4); t += 0.4
        # Floor blocks appear
        self.play(LaggedStart(*[FadeIn(f, scale=0.8) for f in floors],
                              lag_ratio=0.06), run_time=0.4)               # t=3.9
        # Each floor gets darker
        self.play(
            *[f.animate.set_fill(opacity=0.3 + i * 0.12) for i, f in enumerate(floors)],
            run_time=0.3,
        )                                                                   # t=4.2
        self.play(FadeIn(floor_label), run_time=0.2); t += 0.2
        self.play(FadeIn(footer), run_time=0.2); t += 0.2
        # Monster eyes glow brighter
        self.play(
            m_eye_l.animate.scale(1.3).set_color(WHITE_SOFT),
            m_eye_r.animate.scale(1.3).set_color(WHITE_SOFT),
            run_time=0.2,
        )                                                                   # t=4.8
        self.play(
            m_eye_l.animate.scale(1/1.3).set_color(BLOOD_RED),
            m_eye_r.animate.scale(1/1.3).set_color(BLOOD_RED),
            run_time=0.2,
        )                                                                   # t=5.0
        target = getattr(self.__class__, 'DURATION', 4.7)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE PUNCH (27.0-37.0s = 10.00s)
# "You're gonna be cheering for them by page 50."
# Zones: TITLE(pill) UPPER+MID(big book cover) LOWER(stars) FOOTER(page 50)
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 7.8
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
        self.add(star_field(8, seed=99))

        # Title badge
        pill = label_pill("READ IT.", color=TIARA_GOLD, fs=30)
        pill.move_to(UP * ZONE_TITLE)

        # -- Large book cover at UPPER+MID zone --
        book_w, book_h = 4.8, 6.2
        book_cx = UP * 2.1

        book_body = Rectangle(width=book_w, height=book_h,
                              fill_color="#1A082E", fill_opacity=0.97,
                              stroke_color=CHAOS_PURPLE, stroke_width=3)
        book_body.move_to(book_cx)

        # Spine panel on left edge
        spine = Rectangle(width=0.4, height=book_h,
                          fill_color="#100520", fill_opacity=1, stroke_width=0)
        spine.move_to(book_cx + LEFT * (book_w / 2 - 0.2))

        # Inner border inset
        inner_border = Rectangle(width=book_w - 0.35, height=book_h - 0.35,
                                 fill_opacity=0, stroke_color=CHAOS_PURPLE,
                                 stroke_width=1).set_stroke(opacity=0.35)
        inner_border.move_to(book_cx)

        # Cover glow behind title
        cover_glow = Circle(radius=2.0, fill_color=CHAOS_PURPLE,
                            fill_opacity=0.08, stroke_width=0)
        cover_glow.move_to(book_cx + UP * 0.6)

        # Book title -- three lines
        line1 = Text("DUNGEON", font="Bebas Neue", font_size=68, color=WHITE_SOFT)
        if line1.width > book_w - 0.5: line1.scale((book_w - 0.5) / line1.width)
        line1.move_to(book_cx + UP * 2.0)

        line2 = Text("CRAWLER", font="Bebas Neue", font_size=68, color=WHITE_SOFT)
        if line2.width > book_w - 0.5: line2.scale((book_w - 0.5) / line2.width)
        line2.move_to(book_cx + UP * 1.15)

        line3 = Text("CARL", font="Bebas Neue", font_size=96, color=CHAOS_PURPLE)
        if line3.width > book_w - 0.5: line3.scale((book_w - 0.5) / line3.width)
        line3.move_to(book_cx + UP * 0.15)

        # Thin rule under title
        cover_rule = Line(LEFT * 1.6, RIGHT * 1.6, color=CHAOS_PURPLE, stroke_width=1.5)
        cover_rule.set_stroke(opacity=0.6).move_to(book_cx + DOWN * 0.55)

        # Author name
        author = Text("MATT DINNIMAN", font="Inter", font_size=26, color=MUTED, weight="BOLD")
        if author.width > book_w - 0.6: author.scale((book_w - 0.6) / author.width)
        author.move_to(book_cx + DOWN * 0.95)

        # "Book 1" tag at bottom of cover
        book_num = Text("BOOK 1", font="Inter", font_size=22, color=DEAD_GRAY, weight="BOLD")
        book_num.move_to(book_cx + DOWN * 2.3)

        # Cat silhouette on cover
        cover_cat = cat_face(CAT_ORANGE, h=0.8)
        cover_cat.set_opacity(0.3).move_to(book_cx + DOWN * 1.6 + RIGHT * 1.2)

        book_cover = VGroup(book_body, spine, inner_border, cover_glow,
                            line1, line2, line3, cover_rule, author, book_num, cover_cat)

        # PAGE 50 -- below book
        page = safe_text("PAGE 50.", font="Bebas Neue", font_size=110, color=CHAOS_PURPLE)
        page.move_to(DOWN * 1.8)
        glow = Circle(radius=2.0, fill_color=CHAOS_PURPLE, fill_opacity=0.05, stroke_width=0)
        glow.move_to(page)

        # -- Star rating at LOWER zone --
        star_icons = VGroup()
        for i in range(5):
            s = Polygon(
                np.array([0, 0.3, 0]),
                np.array([0.07, 0.1, 0]),
                np.array([0.28, 0.1, 0]),
                np.array([0.12, -0.05, 0]),
                np.array([0.18, -0.28, 0]),
                np.array([0, -0.13, 0]),
                np.array([-0.18, -0.28, 0]),
                np.array([-0.12, -0.05, 0]),
                np.array([-0.28, 0.1, 0]),
                np.array([-0.07, 0.1, 0]),
                fill_color=TIARA_GOLD, fill_opacity=0.9, stroke_width=0,
            )
            s.scale(0.8).move_to(LEFT * 2 + RIGHT * i * 1.0)
            star_icons.add(s)
        star_icons.move_to(DOWN * ZONE_LOWER + UP * 0.5)

        rating_sub = safe_text("4.6 GOODREADS", font="Inter",
                               font_size=24, color=MUTED, weight="BOLD")
        rating_sub.move_to(DOWN * ZONE_LOWER - UP * 0.3)

        # -- Timing: 10.00s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(book_cover, scale=0.93), run_time=0.6); t += 0.6
        # Book subtle hover
        self.play(book_cover.animate.shift(UP * 0.1), run_time=0.5); t += 0.5
        self.play(book_cover.animate.shift(DOWN * 0.1), run_time=0.5); t += 0.5
        self.wait(0.5); t += 0.5
        self.play(FadeIn(glow), FadeIn(page, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(page.get_center(), color=CHAOS_PURPLE,
                        line_length=0.5, num_lines=12, run_time=0.3))      # t=3.2
        self.wait(0.8); t += 0.8
        # Stars appear one by one
        self.play(LaggedStart(*[GrowFromCenter(s) for s in star_icons],
                              lag_ratio=0.1), run_time=0.5)                # t=4.5
        self.play(FadeIn(rating_sub), run_time=0.25); t += 0.25
        # Cover glow pulses
        self.play(cover_glow.animate.scale(1.15).set_opacity(0.12),
                  run_time=0.4)                                             # t=5.15
        self.play(cover_glow.animate.scale(1/1.15).set_opacity(0.08),
                  run_time=0.4)                                             # t=5.55
        self.wait(2.45); t += 2.45
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5
        target = getattr(self.__class__, 'DURATION', 7.8)
        self.wait(max(0.1, target - t - 0.8))


# -- Infra -------------------------------------------------------
def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_Offer, Scene3_Cat,
          Scene4_Show, Scene5_Chaos, Scene6_Punch]
    config.output_file = f"dcc_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"dcc_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    sc = [Scene1_Hook, Scene2_Offer, Scene3_Cat,
          Scene4_Show, Scene5_Chaos, Scene6_Punch]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(sc):
        n = f"dcc_scene_{i+1}"; print(f"  Preview {n}...")
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

    names = ["Scene1_Hook","Scene2_Offer","Scene3_Cat",
             "Scene4_Show","Scene5_Chaos","Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_dungeon_crawler_carl.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="dcc", audio_path=str(audio))
    final = od / "dungeon_crawler_carl_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
