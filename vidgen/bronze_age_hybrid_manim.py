#!/usr/bin/env python3
"""Bronze Age Collapse — Pure Manim Screenplay.

VTT cues (approximate):
  0.00 — In 1177 BC, every major civilization collapsed at the same time.
  4.00 — Textbooks blame the Sea Peoples — raiders who burned everything.
  7.50 — Nobody knows who they were.
  9.00 — Hittites. Mycenaeans. Egyptians. Babylonians.
 12.50 — All fell within fifty years.
 14.00 — Every empire depended on the others.
 16.00 — Tin from Afghanistan. Copper from Cyprus. Grain from Egypt.
 20.50 — One break and everything starved.
 22.50 — Writing disappeared for 400 years.
 25.00 — A system so connected that when one part failed, everything fell.
 30.00 — Sound familiar?
"""

import os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from manim import (
    Scene, Text, Group, VGroup, Rectangle, RoundedRectangle, Circle,
    Line, Arrow, DashedLine, Dot, Polygon, Ellipse, Square,
    FadeIn, FadeOut, GrowFromCenter, Write, Create, DrawBorderThenFill,
    AnimationGroup, LaggedStart, Flash, GrowArrow,
    config, UP, DOWN, LEFT, RIGHT, ORIGIN, UL, UR, DL, DR,
    WHITE, BLACK, rate_functions, DEGREES, PI,
)
import numpy as np

# ── TTS Script (extracted by generate_tts.py) ──
TTS_SCRIPT = """In 1177 BC, every major civilization collapsed at the same time. Textbooks blame the Sea Peoples — raiders who burned everything. Nobody knows who they were. Hittites. Mycenaeans. Egyptians. Babylonians. All fell within fifty years. Every empire depended on the others. Tin from Afghanistan. Copper from Cyprus. Grain from Egypt. One break and everything starved. Writing disappeared for 400 years. A system so connected that when one part failed, everything fell. Sound familiar?"""

# ── Manim config (1080x1920 portrait) ──
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.frame_width = 9
config.frame_height = 16
config.background_color = "#080A10"
config.disable_caching = True

# ── Color palette ──
BG = "#080A10"
GRID = "#1A2030"
SURFACE = "#15192A"
WHITE_SOFT = "#F0F0F0"
GOLD = "#FFD700"
GOLD_DIM = "#B8960F"
RED = "#E63946"
MUTED = "#7B8DA0"
DEAD_GRAY = "#4A5568"
BRONZE = "#CD7F32"
BRONZE_DIM = "#8B5A2B"
BRONZE_LIGHT = "#DDA15E"
FLAME = "#FF6B35"
ASH = "#6B6B6B"

# ── Layout constants ──
SAFE_W = 8.0
SAFE_TOP = 7.2
SAFE_BOT = -6.4
ZONE_TITLE  = 6.2
ZONE_UPPER  = 3.5
ZONE_MID    = 0.0
ZONE_LOWER  = -3.5
ZONE_FOOTER = -6.0


# ============================================================
# CORE HELPERS
# ============================================================

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

def label_pill(txt, color=GOLD, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W:
        t.scale(SAFE_W / t.width)
    p = RoundedRectangle(
        width=t.width + 0.5, height=t.height + 0.3,
        corner_radius=0.15, fill_color=bg, fill_opacity=0.9, stroke_width=0
    ).move_to(t)
    return VGroup(p, t)


# ============================================================
# DOMAIN SHAPES (4 topic-specific shapes)
# ============================================================

def sword_shape(height=2.0, color=BRONZE):
    """Bronze Age sword — blade + crossguard + grip."""
    blade_w = height * 0.08
    blade_h = height * 0.6
    blade = Polygon(
        np.array([-blade_w, 0, 0]),
        np.array([0, blade_h, 0]),
        np.array([blade_w, 0, 0]),
        fill_color=color, fill_opacity=0.85, stroke_color=color, stroke_width=1,
    )
    guard_w = height * 0.2
    guard_h = height * 0.04
    guard = Rectangle(width=guard_w, height=guard_h,
                       fill_color=color, fill_opacity=0.9, stroke_width=0)
    guard.next_to(blade, DOWN, buff=0)
    grip_w = height * 0.05
    grip_h = height * 0.2
    grip = Rectangle(width=grip_w, height=grip_h,
                      fill_color=BRONZE_DIM, fill_opacity=0.9, stroke_width=0)
    grip.next_to(guard, DOWN, buff=0)
    pommel = Circle(radius=height * 0.04, fill_color=color, fill_opacity=0.9, stroke_width=0)
    pommel.next_to(grip, DOWN, buff=0)
    s = VGroup(blade, guard, grip, pommel)
    s.scale_to_fit_height(height)
    return s

def broken_pillar(height=3.0, color=ASH):
    """Broken column — base + shaft + jagged break at top."""
    base_w = height * 0.3
    base_h = height * 0.08
    base = Rectangle(width=base_w, height=base_h,
                      fill_color=color, fill_opacity=0.7, stroke_width=0)
    shaft_w = height * 0.18
    shaft_h = height * 0.55
    shaft = Rectangle(width=shaft_w, height=shaft_h,
                       fill_color=color, fill_opacity=0.5, stroke_color=color, stroke_width=1)
    shaft.next_to(base, UP, buff=0)
    # Jagged break at top — triangle fragments
    frag1 = Polygon(
        np.array([-shaft_w/2, 0, 0]),
        np.array([-shaft_w/4, height*0.12, 0]),
        np.array([0, height*0.04, 0]),
        fill_color=color, fill_opacity=0.4, stroke_width=0,
    )
    frag1.next_to(shaft, UP, buff=0).align_to(shaft, LEFT)
    frag2 = Polygon(
        np.array([0, 0, 0]),
        np.array([shaft_w/4, height*0.08, 0]),
        np.array([shaft_w/2, height*0.02, 0]),
        fill_color=color, fill_opacity=0.3, stroke_width=0,
    )
    frag2.next_to(shaft, UP, buff=0).align_to(shaft, RIGHT)
    # Debris dots
    d1 = Dot(radius=0.06, color=color).next_to(base, RIGHT, buff=0.3).shift(UP*0.2)
    d2 = Dot(radius=0.04, color=color).next_to(base, LEFT, buff=0.4).shift(UP*0.1)
    p = VGroup(base, shaft, frag1, frag2, d1, d2)
    p.scale_to_fit_height(height)
    return p

def trade_ship(width=1.5, color=BRONZE_LIGHT):
    """Ancient trade vessel — hull + mast + square sail."""
    w, h = width, width * 0.5
    hull = Polygon(
        np.array([-w/2, 0, 0]),
        np.array([-w/2.5, -h*0.3, 0]),
        np.array([w/2.5, -h*0.3, 0]),
        np.array([w/2, 0, 0]),
        fill_color=color, fill_opacity=0.7, stroke_color=color, stroke_width=1.5,
    )
    mast = Line(np.array([0, 0, 0]), np.array([0, h*0.7, 0]),
                color=color, stroke_width=2)
    sail = Rectangle(width=w*0.35, height=h*0.45,
                      fill_color=color, fill_opacity=0.4, stroke_color=color, stroke_width=1)
    sail.move_to(mast.get_center() + UP * h * 0.15)
    oar1 = Line(np.array([-w*0.3, -h*0.1, 0]), np.array([-w*0.3, -h*0.45, 0]),
                color=color, stroke_width=1).rotate(15*DEGREES)
    oar2 = Line(np.array([w*0.15, -h*0.1, 0]), np.array([w*0.15, -h*0.45, 0]),
                color=color, stroke_width=1).rotate(-15*DEGREES)
    return VGroup(hull, mast, sail, oar1, oar2)

def city_walls(width=2.5, height=1.5, color=GOLD_DIM):
    """Fortified city walls — crenellated wall with towers."""
    wall = Rectangle(width=width, height=height*0.5,
                      fill_color=color, fill_opacity=0.5, stroke_color=color, stroke_width=1.5)
    # Crenellations
    crens = VGroup()
    n_crens = 7
    cren_w = width / (n_crens * 2 + 1)
    for i in range(n_crens):
        c = Rectangle(width=cren_w, height=height*0.12,
                       fill_color=color, fill_opacity=0.6, stroke_width=0)
        c.move_to(wall.get_top() + UP*height*0.06 + LEFT*width/2 + RIGHT*(2*i+1)*cren_w)
        crens.add(c)
    # Two towers
    tw = height * 0.15
    th = height * 0.7
    tower_l = Rectangle(width=tw, height=th, fill_color=color, fill_opacity=0.6,
                          stroke_color=color, stroke_width=1)
    tower_l.align_to(wall, DOWN).align_to(wall, LEFT)
    tower_r = tower_l.copy()
    tower_r.align_to(wall, DOWN).align_to(wall, RIGHT)
    # Gate
    gate = Rectangle(width=width*0.12, height=height*0.25,
                      fill_color=BG, fill_opacity=0.8, stroke_color=color, stroke_width=1)
    gate.align_to(wall, DOWN).move_to(wall.get_center())
    gate.shift(DOWN * (height * 0.125))
    return VGroup(wall, crens, tower_l, tower_r, gate)


# ================================================================
# SCENE 1: THE HOOK — "1177 BC, every civilization collapsed"
# ================================================================
class Scene1_Hook(Scene):
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))

        # ZONE_TITLE — date pill
        pill = label_pill("1177 BC", color=RED, fs=32)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER — four empire city walls
        empires = ["HITTITES", "MYCENAE", "EGYPT", "BABYLON"]
        emp_colors = [BRONZE, GOLD, GOLD_DIM, BRONZE_LIGHT]
        walls_group = VGroup()
        for i, (name, col) in enumerate(zip(empires, emp_colors)):
            w = city_walls(width=1.6, height=1.0, color=col)
            lbl = safe_text(name, font="Inter", font_size=18, color=col, weight="BOLD")
            lbl.next_to(w, DOWN, buff=0.1)
            item = VGroup(w, lbl)
            walls_group.add(item)
        walls_group.arrange_in_grid(rows=2, cols=2, buff=0.6)
        walls_group.move_to(UP * ZONE_UPPER)

        # ZONE_MID — "COLLAPSED" big text
        collapsed = safe_text("COLLAPSED", font="Bebas Neue", font_size=100, color=RED)
        collapsed.move_to(UP * ZONE_MID)

        # ZONE_LOWER — red pulse ring
        pulse = Circle(radius=2.5, fill_color=RED, fill_opacity=0.0,
                        stroke_color=RED, stroke_width=3, stroke_opacity=0.4)
        pulse.move_to(UP * ZONE_MID)

        # ZONE_FOOTER — "at the same time"
        same_time = safe_text("at the same time.", font="DM Serif Display",
                              font_size=44, color=WHITE_SOFT)
        same_time.move_to(UP * ZONE_FOOTER)

        # ── Timing ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.4)                     # t=0.4
        self.play(
            LaggedStart(*[FadeIn(w, scale=0.8) for w in walls_group],
                         lag_ratio=0.1),
            run_time=1.0,
        )                                                                       # t=1.4
        self.wait(0.6)                                                          # t=2.0

        # Red flash on each empire
        self.play(
            *[Flash(walls_group[i].get_center(), color=RED,
                    line_length=0.3, num_lines=6, run_time=0.3) for i in range(4)],
        )                                                                       # t=2.3
        self.play(FadeIn(pulse, scale=0.3), run_time=0.3)                     # t=2.6

        # Walls turn gray — empires dying
        self.play(
            *[walls_group[i][0].animate.set_color(DEAD_GRAY).set_opacity(0.3)
              for i in range(4)],
            run_time=0.5,
        )                                                                       # t=3.1

        self.play(FadeIn(collapsed, scale=1.15), run_time=0.6)               # t=3.7
        self.play(Flash(collapsed.get_center(), color=RED,
                        line_length=0.5, num_lines=12, run_time=0.3))          # t=4.0
        self.play(FadeOut(pulse), run_time=0.2)                               # t=4.2
        self.play(FadeIn(same_time, shift=UP * 0.06), run_time=0.5)         # t=4.7
        self.wait(1.3)                                                          # t=6.0

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3))


# ================================================================
# SCENE 2: SEA PEOPLES — "raiders who burned everything"
# ================================================================
class Scene2_SeaPeoples(Scene):
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))

        # ZONE_TITLE — label
        pill = label_pill("THE SEA PEOPLES", color=FLAME, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER — fleet of trade ships approaching
        ships = VGroup()
        ship_positions = [
            (-2.5, 4.5, 1.2), (-1.0, 3.8, 1.0), (1.0, 4.2, 0.9),
            (-3.0, 3.0, 0.8), (0.0, 2.8, 1.1), (2.5, 3.5, 0.7),
        ]
        for x, y, w in ship_positions:
            s = trade_ship(width=w, color="#6A4040")
            s.move_to(np.array([x, y, 0]))
            ships.add(s)

        # Question marks — mystery identity
        qmarks = VGroup()
        for s in ships:
            q = safe_text("?", font="Bebas Neue", font_size=34, color=FLAME)
            q.move_to(s.get_center() + UP * 0.6)
            qmarks.add(q)

        # ZONE_MID — sword shapes flanking "RAIDERS"
        sword_l = sword_shape(height=2.0, color=FLAME)
        sword_l.move_to(LEFT * 3 + UP * ZONE_MID)
        sword_r = sword_shape(height=2.0, color=FLAME)
        sword_r.move_to(RIGHT * 3 + UP * ZONE_MID)
        sword_r.flip()

        raiders_txt = safe_text("RAIDERS", font="Bebas Neue", font_size=70, color=FLAME)
        raiders_txt.move_to(UP * ZONE_MID)

        # ZONE_LOWER — "Nobody knows who they were"
        nobody = safe_text("IDENTITY UNKNOWN", font="Bebas Neue", font_size=55, color=DEAD_GRAY)
        nobody.move_to(UP * ZONE_LOWER)

        # ZONE_FOOTER
        mystery = safe_text("3,200 years later — still a mystery",
                           font="Inter", font_size=24, color=MUTED)
        mystery.move_to(UP * ZONE_FOOTER)

        # ── Timing ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3)                     # t=0.3
        self.play(
            LaggedStart(*[FadeIn(s, shift=RIGHT * 0.5) for s in ships],
                         lag_ratio=0.08),
            run_time=0.8,
        )                                                                       # t=1.1
        self.play(
            LaggedStart(*[FadeIn(q, scale=0.5) for q in qmarks],
                         lag_ratio=0.06),
            run_time=0.4,
        )                                                                       # t=1.5
        self.wait(0.5)                                                          # t=2.0

        self.play(
            GrowFromCenter(sword_l),
            GrowFromCenter(sword_r),
            FadeIn(raiders_txt, scale=1.1),
            run_time=0.6,
        )                                                                       # t=2.6
        self.wait(1.0)                                                          # t=3.6

        self.play(FadeIn(nobody, shift=UP * 0.06), run_time=0.5)             # t=4.1
        self.play(FadeIn(mystery, shift=UP * 0.04), run_time=0.4)            # t=4.5
        self.wait(1.0)                                                          # t=5.5

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3))


# ================================================================
# SCENE 3: THE CHAIN — "Every empire depended on the others"
# ================================================================
class Scene3_Chain(Scene):
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))

        # ZONE_TITLE
        pill = label_pill("THE CHAIN", color=GOLD, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER — empire names (rapid fire list, labels only)
        empire_names = [
            ("HITTITES", BRONZE),
            ("MYCENAEANS", GOLD),
            ("EGYPTIANS", GOLD_DIM),
            ("BABYLONIANS", BRONZE_LIGHT),
        ]
        emp_texts = VGroup()
        for i, (name, col) in enumerate(empire_names):
            t = safe_text(name, font="Bebas Neue", font_size=55, color=col)
            emp_texts.add(t)
        emp_texts.arrange(DOWN, buff=0.3)
        emp_texts.move_to(UP * ZONE_UPPER)

        # ZONE_MID — "ALL FELL" + "50 YEARS"
        fell = safe_text("ALL FELL", font="Bebas Neue", font_size=80, color=RED)
        fell.move_to(UP * (ZONE_MID + 0.5))
        fifty = safe_text("WITHIN 50 YEARS", font="Bebas Neue", font_size=50, color=RED)
        fifty.move_to(UP * (ZONE_MID - 0.7))

        # ZONE_LOWER — trade resources: tin, copper, grain (as icons + labels)
        resources = [
            ("TIN", "Afghanistan", BRONZE),
            ("COPPER", "Cyprus", BRONZE_LIGHT),
            ("GRAIN", "Egypt", GOLD),
        ]
        res_group = VGroup()
        for res, origin, col in resources:
            # Resource circle icon
            icon = Circle(radius=0.35, fill_color=col, fill_opacity=0.6,
                           stroke_color=col, stroke_width=1.5)
            r_lbl = safe_text(res, font="Bebas Neue", font_size=28, color=col)
            r_lbl.move_to(icon)
            arrow = Arrow(ORIGIN, RIGHT * 0.8, color=col, stroke_width=2, buff=0.1)
            o_lbl = safe_text(origin, font="Inter", font_size=22, color=MUTED)
            row = VGroup(icon, r_lbl, arrow, o_lbl).arrange(RIGHT, buff=0.2)
            res_group.add(row)
        res_group.arrange(DOWN, buff=0.4)
        res_group.move_to(UP * ZONE_LOWER)

        # ZONE_FOOTER — connecting lines to show dependency
        dep_label = safe_text("interconnected supply chain",
                              font="Inter", font_size=22, color=MUTED)
        dep_label.move_to(UP * ZONE_FOOTER)

        # ── Timing ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3)                     # t=0.3

        # Empires rapid fire
        for et in emp_texts:
            self.play(FadeIn(et, shift=LEFT * 0.1), run_time=0.3)
        # t = 0.3 + 4*0.3 = 1.5
        self.wait(0.3)                                                          # t=1.8

        self.play(FadeIn(fell, scale=1.1), run_time=0.5)                     # t=2.3
        self.play(Flash(fell.get_center(), color=RED,
                        line_length=0.3, num_lines=8, run_time=0.3))            # t=2.6
        self.play(FadeIn(fifty, shift=UP * 0.06), run_time=0.4)              # t=3.0
        self.wait(0.5)                                                          # t=3.5

        # Resources one by one
        for rg in res_group:
            self.play(FadeIn(rg, shift=LEFT * 0.2), run_time=0.4)
            self.wait(0.3)
        # t = 3.5 + 3*(0.4+0.3) = 5.6
        self.play(FadeIn(dep_label, shift=UP * 0.04), run_time=0.3)          # t=5.9
        self.wait(0.6)                                                          # t=6.5

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3))


# ================================================================
# SCENE 4: COLLAPSE — "One break and everything starved"
# ================================================================
class Scene4_Collapse(Scene):
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))

        # ZONE_TITLE
        pill = label_pill("THE COLLAPSE", color=RED, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER — broken pillar as hero visual
        pillar = broken_pillar(height=4.0, color=ASH)
        pillar.move_to(UP * ZONE_UPPER)

        # Broken trade lines — three dashed lines snapping
        trade_lines = VGroup()
        line_data = [
            (LEFT*3.5 + UP*4.5, LEFT*0.5 + UP*3.5, BRONZE),
            (RIGHT*3.5 + UP*4.0, RIGHT*0.5 + UP*3.0, BRONZE_LIGHT),
            (LEFT*2.0 + UP*2.5, RIGHT*1.0 + UP*2.0, GOLD),
        ]
        for start, end, col in line_data:
            dl = DashedLine(start, end, color=col, stroke_width=2, dash_length=0.15)
            x_mark = safe_text("X", font="Bebas Neue", font_size=30, color=RED)
            x_mark.move_to((np.array(start) + np.array(end)) / 2)
            trade_lines.add(VGroup(dl, x_mark))

        # ZONE_MID — "ONE BREAK"
        one_break = safe_text("ONE BREAK", font="Bebas Neue", font_size=80, color=RED)
        one_break.move_to(UP * ZONE_MID)

        # ZONE_LOWER — "WRITING DISAPPEARED" + "400 YEARS"
        writing = safe_text("WRITING DISAPPEARED", font="Bebas Neue", font_size=55, color=ASH)
        writing.move_to(UP * (ZONE_LOWER + 0.5))
        four_hundred = safe_text("400 YEARS", font="Bebas Neue", font_size=90, color=DEAD_GRAY)
        four_hundred.move_to(UP * (ZONE_LOWER - 0.8))

        # ZONE_FOOTER
        dark_age = safe_text("The Greek Dark Ages", font="Inter", font_size=22, color=MUTED)
        dark_age.move_to(UP * ZONE_FOOTER)

        # ── Timing ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3)                     # t=0.3
        self.play(GrowFromCenter(pillar), run_time=0.6)                       # t=0.9

        # Trade lines appear then break
        self.play(
            LaggedStart(*[Create(tl[0]) for tl in trade_lines], lag_ratio=0.1),
            run_time=0.5,
        )                                                                       # t=1.4
        self.play(
            LaggedStart(*[FadeIn(tl[1], scale=1.5) for tl in trade_lines], lag_ratio=0.1),
            run_time=0.4,
        )                                                                       # t=1.8

        self.play(FadeIn(one_break, scale=1.15), run_time=0.6)               # t=2.4
        self.play(Flash(one_break.get_center(), color=RED,
                        line_length=0.4, num_lines=10, run_time=0.3))          # t=2.7
        self.wait(0.8)                                                          # t=3.5

        # Pillar crumbles (fades gray)
        self.play(pillar.animate.set_opacity(0.2), run_time=0.5)             # t=4.0

        self.play(FadeIn(writing, shift=LEFT * 0.1), run_time=0.5)           # t=4.5
        self.play(FadeIn(four_hundred, scale=1.1), run_time=0.5)             # t=5.0
        self.play(Flash(four_hundred.get_center(), color=ASH,
                        line_length=0.3, num_lines=6, run_time=0.3))           # t=5.3
        self.play(FadeIn(dark_age, shift=UP * 0.04), run_time=0.3)           # t=5.6
        self.wait(0.9)                                                          # t=6.5

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3))


# ================================================================
# SCENE 5: THE PUNCH — "Sound familiar?"
# ================================================================
class Scene5_Punch(Scene):
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))

        # ZONE_TITLE
        pill = label_pill("3,200 YEARS LATER", color=BRONZE, fs=24)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER — network diagram: 5 nodes connected by lines
        nodes = VGroup()
        node_positions = [
            UP*4.5,                        # top center
            LEFT*2.5 + UP*3.5,             # left
            RIGHT*2.5 + UP*3.5,            # right
            LEFT*1.5 + UP*2.0,             # lower-left
            RIGHT*1.5 + UP*2.0,            # lower-right
        ]
        for pos in node_positions:
            n = Circle(radius=0.25, fill_color=GOLD, fill_opacity=0.6,
                        stroke_color=GOLD, stroke_width=1.5)
            n.move_to(pos)
            nodes.add(n)

        # Connect all nodes to each other
        connections = VGroup()
        for i in range(len(node_positions)):
            for j in range(i+1, len(node_positions)):
                l = Line(node_positions[i], node_positions[j],
                          color=GOLD, stroke_width=1, stroke_opacity=0.3)
                connections.add(l)

        # ZONE_MID — "A system so connected"
        connected = safe_text("SO CONNECTED", font="Bebas Neue", font_size=70, color=WHITE_SOFT)
        connected.move_to(UP * ZONE_MID)

        # ZONE_LOWER — "everything fell" in red
        everything = safe_text("EVERYTHING FELL", font="Bebas Neue", font_size=80, color=RED)
        everything.move_to(UP * ZONE_LOWER)

        # ZONE_FOOTER — "Sound familiar?"
        familiar = safe_text("Sound familiar?", font="Bebas Neue", font_size=70, color=GOLD)
        familiar.move_to(UP * ZONE_FOOTER)
        glow = Circle(radius=2.0, fill_color=GOLD, fill_opacity=0.04, stroke_width=0)
        glow.move_to(familiar)

        # ── Timing ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3)                     # t=0.3

        # Network appears
        self.play(
            LaggedStart(*[Create(c) for c in connections], lag_ratio=0.02),
            run_time=0.5,
        )                                                                       # t=0.8
        self.play(
            LaggedStart(*[FadeIn(n, scale=0.5) for n in nodes], lag_ratio=0.06),
            run_time=0.4,
        )                                                                       # t=1.2
        self.wait(1.0)                                                          # t=2.2

        self.play(FadeIn(connected, shift=UP * 0.06), run_time=0.6)          # t=2.8
        self.wait(1.2)                                                          # t=4.0

        # Network breaks — connections turn red and fade
        self.play(
            *[c.animate.set_color(RED).set_opacity(0.1) for c in connections],
            *[n.animate.set_color(RED).set_opacity(0.3) for n in nodes],
            run_time=0.6,
        )                                                                       # t=4.6

        self.play(FadeIn(everything, scale=1.1), run_time=0.6)               # t=5.2
        self.play(Flash(everything.get_center(), color=RED,
                        line_length=0.4, num_lines=10, run_time=0.3))          # t=5.5
        self.wait(0.8)                                                          # t=6.3

        self.play(FadeIn(glow), FadeIn(familiar, scale=1.08), run_time=0.7)  # t=7.0
        self.wait(1.5)                                                          # t=8.5

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3))


# ================================================================
# SCENE 6: HOLD + FADE
# ================================================================
class Scene6_Hold(Scene):
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.02))

        self.wait(1.5)
        black = Rectangle(width=12, height=20, fill_color=BLACK,
                           fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5)                                # t=3.0

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3))


# ── Render Pipeline ──────────────────────────────────────────────
def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_SeaPeoples, Scene3_Chain,
          Scene4_Collapse, Scene5_Punch, Scene6_Hold]
    config.output_file = f"ba_hybrid_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"ba_hybrid_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}")
        return

def render_previews():
    d = Path(__file__).parent / "previews"
    d.mkdir(exist_ok=True)
    sc = [Scene1_Hook, Scene2_SeaPeoples, Scene3_Chain,
          Scene4_Collapse, Scene5_Punch, Scene6_Hold]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(sc):
        n = f"ba_hybrid_scene_{i+1}"
        print(f"  Preview {n}...")
        config.output_file = n
        config.save_last_frame = True
        config.format = "png"
        S().render()
        for p in Path(config.media_dir).rglob(f"{n}*"):
            if p.suffix == ".png":
                dst = d / f"{n}.png"
                shutil.copy2(str(p), str(dst))
                print(f"  OK: {dst} ({dst.stat().st_size//1024} KB)")
                break
    config.save_last_frame = False
    config.format = None
    print(f"\nAll 6 previews -> {d}/")

if __name__ == "__main__":
    import time, gc
    od = Path(__file__).parent
    if "--preview" in sys.argv:
        render_previews()
        sys.exit(0)
    if "--scene" in sys.argv:
        render_single_scene(int(sys.argv[sys.argv.index("--scene") + 1]))
        sys.exit(0)

    names = ["Scene1_Hook", "Scene2_SeaPeoples", "Scene3_Chain",
             "Scene4_Collapse", "Scene5_Punch", "Scene6_Hold"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_bronze_age.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="ba_hybrid",
                                   audio_path=str(audio))
    final = od / "bronze_age_hybrid_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
