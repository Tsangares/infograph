#!/usr/bin/env python3
"""New Math — America's Cold War Math Panic (Manim).

6 scenes, ~59.5s (56.5s audio + 3s hold).

VTT cues (absolute → relative):
  Scene 1 THE HOOK (0.0–10.0s = 10.00s):
    0.100 (0.10) In 1957, Russia launched a satellite.
    3.000 (3.00) America panicked.
    5.000 (5.00) And the answer was: teach set theory to first graders.
  Scene 2 THE PLAN (10.0–20.0s = 10.00s):
    10.100 (0.10) Congress threw money at it.
    12.500 (2.50) Yale built a new curriculum.
    14.500 (4.50) Abstract algebra. Modular arithmetic. Number bases.
    17.500 (7.50) For children.
  Scene 3 THE SCALE (20.0–30.0s = 10.00s):
    20.100 (0.10) Textbook sales went from 23,000 to 1.8 million in 3 years.
    24.000 (4.00) 85 percent of high schools adopted it.
    27.000 (7.00) They called it the New Math.
  Scene 4 THE PROBLEM (30.0–40.0s = 10.00s):
    30.100 (0.10) Only 5 percent of elementary teachers were trained.
    33.500 (3.50) Parents couldn't help with homework.
    36.500 (6.50) A Harvard mathematician wrote a comedy song about it.
  Scene 5 THE COLLAPSE (40.0–50.0s = 10.00s):
    40.100 (0.10) By 1973, a bestseller called Why Johnny Can't Add killed it.
    44.500 (4.50) Even the guy who created New Math admitted
    47.000 (7.00) they never thought about how to actually teach it.
  Scene 6 THE PUNCH (50.0–59.5s = 9.50s):
    50.100 (0.10) America saw a satellite in the sky
    52.500 (2.50) and made 6-year-olds learn abstract algebra.
    55.000 (5.00) That's not education policy. That's a panic attack.
    + 3s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """In 1957, Russia launched a satellite. America panicked. The solution: teach set theory to first graders. Abstract algebra for children. Textbook sales went from 23,000 to 1.8 million in three years. Only five percent of teachers were trained. Parents couldn't help with homework. By 1973, it was dead. Even its creator admitted they never planned how to teach it. America saw a satellite and made six-year-olds learn abstract algebra. That's not education. That's a panic attack."""

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
SOVIET_RED = "#CC0000"
USA_BLUE = "#002868"
USA_RED = "#BF0A30"
CHALK_WHITE = "#E8E4D8"
CHALK_GREEN = "#2D5A27"
MATH_GOLD = "#FFD700"
MATH_CYAN = "#22CCFF"
BOOK_BROWN = "#6B4226"
BOOK_COVER = "#1A3A5C"
CRISIS_RED = "#FF3333"
PANIC_ORANGE = "#FF6B1A"
WHITE_SOFT = "#F0F0F0"
MUTED = "#7B8DA0"
DIM = "#404050"
DEAD_GRAY = "#4A5568"

SAFE_W = 8.0
SAFE_TOP = 7.2
SAFE_BOT = -6.4

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

def star_field(n=25, seed=42):
    np.random.seed(seed)
    stars = VGroup()
    for _ in range(n):
        x = np.random.uniform(-4.5, 4.5)
        y = np.random.uniform(-8, 8)
        r = np.random.uniform(0.015, 0.035)
        op = np.random.uniform(0.15, 0.45)
        stars.add(Dot(point=np.array([x, y, 0]), radius=r, color=WHITE).set_opacity(op))
    return stars

def section_div(width=5, color=MATH_CYAN):
    l = Line(LEFT*width/2, LEFT*0.12, color=color, stroke_width=1.5)
    r = Line(RIGHT*0.12, RIGHT*width/2, color=color, stroke_width=1.5)
    d = Square(side_length=0.1, color=color, fill_color=color, fill_opacity=1).rotate(45*DEGREES)
    return VGroup(l, d, r)

def label_pill(txt, color=MATH_CYAN, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W:
        t.scale(SAFE_W / t.width)
    p = RoundedRectangle(width=t.width+0.5, height=t.height+0.3, corner_radius=0.18,
                         fill_color=bg, fill_opacity=0.95, stroke_color=color, stroke_width=1.5).move_to(t)
    return VGroup(p, t)

def safe_text(content, **kwargs):
    t = Text(content, **kwargs)
    if t.width > SAFE_W:
        t.scale(SAFE_W / t.width)
    return t


# ── Domain shapes ──────────────────────────────────────────────

def sputnik_shape(height=2.0, color=MUTED, antenna_color=WHITE_SOFT):
    """Sputnik satellite — body sphere + 4 antenna spikes."""
    s = height / 2.0
    body = Circle(radius=0.4*s, fill_color=color, fill_opacity=0.9,
                  stroke_color=antenna_color, stroke_width=1.5)
    antennas = VGroup()
    angles = [225, 240, 300, 315]
    for ang in angles:
        rad = ang * PI / 180
        dx = np.cos(rad) * 1.0 * s
        dy = np.sin(rad) * 1.0 * s
        a = Line(ORIGIN, np.array([dx, dy, 0]), color=antenna_color, stroke_width=2)
        antennas.add(a)
    shine = Dot(point=UP * 0.12*s + LEFT * 0.1*s, radius=0.06*s, color=WHITE).set_opacity(0.6)
    return VGroup(body, antennas, shine)

def chalkboard_shape(width=4.0, height=2.5, color=CHALK_GREEN):
    """Chalkboard rectangle with math symbols."""
    s = width / 4.0
    board = Rectangle(width=width, height=height, fill_color=color, fill_opacity=0.85,
                      stroke_color=BOOK_BROWN, stroke_width=3)
    frame = Rectangle(width=width+0.2, height=height+0.2, fill_opacity=0,
                      stroke_color=BOOK_BROWN, stroke_width=4)
    sym1 = Text("{A, B}", font="DM Serif Display", font_size=int(28*s), color=CHALK_WHITE)
    sym1.move_to(UP * 0.4*s + LEFT * 0.8*s)
    sym2 = Text("3 mod 5", font="DM Serif Display", font_size=int(24*s), color=CHALK_WHITE)
    sym2.move_to(DOWN * 0.3*s + RIGHT * 0.5*s)
    return VGroup(frame, board, sym1, sym2)

def textbook_shape(height=2.0, color=BOOK_COVER):
    """Book shape — cover + spine + pages."""
    s = height / 2.0
    cover = Rectangle(width=1.2*s, height=1.8*s, fill_color=color, fill_opacity=0.9,
                      stroke_color="#2A5A8C", stroke_width=1.5)
    spine = Rectangle(width=0.15*s, height=1.8*s, fill_color="#0E2A4A", fill_opacity=0.9,
                      stroke_width=0).move_to(LEFT * 0.675*s)
    pages = Rectangle(width=1.05*s, height=1.7*s, fill_color="#E8E0D0", fill_opacity=0.3,
                      stroke_width=0).move_to(RIGHT * 0.02*s)
    title = Text("MATH", font="Inter", font_size=int(16*s), color=MATH_GOLD, weight="BOLD")
    title.move_to(UP * 0.2*s)
    return VGroup(cover, spine, pages, title)

def child_shape(height=1.5, color=WHITE_SOFT):
    """Simple stick figure child with desk seat."""
    s = height / 1.5
    head = Circle(radius=0.12*s, fill_color=color, fill_opacity=0.9,
                  stroke_color=color, stroke_width=1).move_to(UP * 0.45*s)
    body = Line(UP * 0.33*s, DOWN * 0.1*s, color=color, stroke_width=2)
    l_leg = Line(DOWN * 0.1*s, DOWN * 0.45*s + LEFT * 0.12*s, color=color, stroke_width=1.5)
    r_leg = Line(DOWN * 0.1*s, DOWN * 0.45*s + RIGHT * 0.12*s, color=color, stroke_width=1.5)
    l_arm = Line(UP * 0.2*s, UP * 0.05*s + LEFT * 0.18*s, color=color, stroke_width=1.5)
    r_arm = Line(UP * 0.2*s, UP * 0.05*s + RIGHT * 0.18*s, color=color, stroke_width=1.5)
    return VGroup(head, body, l_leg, r_leg, l_arm, r_arm)

def music_note_shape(height=0.8, color=MATH_GOLD):
    """Musical note — stem + filled head + flag."""
    s = height / 0.8
    head = Ellipse(width=0.18*s, height=0.12*s, fill_color=color,
                   fill_opacity=0.9, stroke_width=0).rotate(-20*DEGREES)
    stem = Line(head.get_right() + UP * 0.01*s,
                head.get_right() + UP * 0.5*s,
                color=color, stroke_width=1.5)
    flag = Line(stem.get_top(),
                stem.get_top() + RIGHT * 0.12*s + DOWN * 0.15*s,
                color=color, stroke_width=1.5)
    return VGroup(head, stem, flag)

def graduation_cap_shape(height=1.0, color=DIM):
    """Graduation cap / mortarboard."""
    s = height / 1.0
    # Diamond top of cap
    top = Polygon(
        LEFT * 0.5*s, UP * 0.25*s, RIGHT * 0.5*s, DOWN * 0.05*s,
        fill_color=color, fill_opacity=0.8, stroke_color=MUTED, stroke_width=1
    )
    # Band below
    band = Rectangle(width=0.5*s, height=0.15*s, fill_color="#222233",
                     fill_opacity=0.7, stroke_width=0).move_to(DOWN * 0.15*s)
    # Tassel
    tassel_line = Line(RIGHT * 0.3*s + UP * 0.1*s,
                       RIGHT * 0.45*s + DOWN * 0.25*s,
                       color=MATH_GOLD, stroke_width=1.5)
    tassel_end = Dot(point=tassel_line.get_end(), radius=0.03*s,
                     color=MATH_GOLD, fill_opacity=0.9)
    return VGroup(top, band, tassel_line, tassel_end)


# ================================================================
# SCENE 1: THE HOOK (0.0–10.0s = 10.00s)
# TITLE: 1957 pill | UPPER: sputnik + orbit | MID: flag + PANICKED
# LOWER: chalkboard | FOOTER: SET THEORY
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 10.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        stars = star_field(30, seed=1)
        self.add(stars)

        pill = label_pill("1957", color=SOVIET_RED, fs=32)
        pill.move_to(UP * ZONE_TITLE)

        # Sputnik at UPPER
        sputnik = sputnik_shape(2.5, MUTED, WHITE_SOFT)
        sputnik.move_to(UP * ZONE_UPPER)

        # Orbit ring
        orbit = Ellipse(width=5, height=1.5, fill_opacity=0,
                        stroke_color=MUTED, stroke_width=1, stroke_opacity=0.3)
        orbit.move_to(UP * (ZONE_UPPER - 0.3))

        # US flag at MID
        flag = child_shape(2.0, MUTED)  # silhouette figure looking up
        flag.move_to(LEFT * 2.0 + UP * ZONE_MID)

        us_flag = Rectangle(width=1.2, height=0.8, fill_color=USA_BLUE, fill_opacity=0.7,
                            stroke_color=USA_RED, stroke_width=2)
        us_flag.move_to(LEFT * 2.0 + UP * (ZONE_MID + 1.5))

        panicked = safe_text("PANICKED.", font="Bebas Neue", font_size=80, color=USA_RED)
        panicked.move_to(RIGHT * 1.5 + UP * ZONE_MID)

        # Chalkboard at LOWER with set theory
        board = chalkboard_shape(5.0, 2.5, CHALK_GREEN)
        board.move_to(UP * ZONE_LOWER)

        div = section_div(5, SOVIET_RED).move_to(UP * (ZONE_FOOTER + 0.8))

        footer = safe_text("SET THEORY.", font="Bebas Neue", font_size=50, color=MATH_GOLD)
        footer.move_to(UP * ZONE_FOOTER)

        # ── Timing: 10.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "In 1957, Russia launched a satellite."
        self.play(Create(orbit), run_time=0.4); t += 0.4
        self.play(GrowFromCenter(sputnik), run_time=0.6); t += 0.6
        self.play(Flash(sputnik.get_center(), color=WHITE_SOFT,
                        line_length=0.3, num_lines=8, run_time=0.3))       # t=1.6
        # Sputnik drifts slowly across orbit
        self.play(sputnik.animate.shift(RIGHT * 0.5 + DOWN * 0.15),
                  run_time=1.1)                                             # t=2.7

        # VTT 3.00: "America panicked."
        self.play(FadeIn(flag, shift=UP*0.2), run_time=0.4); t += 0.4
        self.play(FadeIn(panicked, scale=1.15), run_time=0.5); t += 0.5
        self.play(Flash(panicked.get_center(), color=USA_RED,
                        line_length=0.3, num_lines=6, run_time=0.3))       # t=3.9
        # Shake the figure
        self.play(flag.animate.shift(RIGHT*0.08), run_time=0.08); t += 0.08
        self.play(flag.animate.shift(LEFT*0.16), run_time=0.08); t += 0.08
        self.play(flag.animate.shift(RIGHT*0.08), run_time=0.08); t += 0.08
        self.wait(0.56); t += 0.56

        # VTT 5.00: "And the answer was: teach set theory to first graders."
        self.play(FadeIn(board, scale=0.9), run_time=0.7); t += 0.7
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(footer, scale=1.05), run_time=0.5); t += 0.5
        self.play(Flash(footer.get_center(), color=MATH_GOLD,
                        line_length=0.3, num_lines=6, run_time=0.3))       # t=6.5
        # Slow zoom on chalkboard during hold
        self.play(board.animate.scale(1.06), run_time=2.0); t += 2.0
        target = getattr(self.__class__, 'DURATION', 10.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE PLAN (10.0–20.0s = 10.00s)
# TITLE: THE PLAN | UPPER: dollar signs rain | MID: Yale columns
# LOWER: math symbols | FOOTER: FOR CHILDREN
# ================================================================
class Scene2_Plan(Scene):
    DURATION = 10.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE PLAN", color=MATH_GOLD, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # Dollar signs raining at UPPER
        dollars = VGroup()
        dollar_data = [
            (LEFT*3 + UP*4.5, 55), (LEFT*1 + UP*4.0, 65), (RIGHT*0.5 + UP*4.8, 50),
            (RIGHT*2.5 + UP*3.8, 60), (LEFT*2 + UP*3.5, 45), (RIGHT*1.5 + UP*4.3, 55),
        ]
        for pos, fs in dollar_data:
            d = safe_text("$", font="Bebas Neue", font_size=fs, color=MATH_GOLD)
            d.move_to(pos).set_opacity(0.7)
            dollars.add(d)

        # Yale columns at MID
        cols = VGroup()
        for i in range(4):
            c = Rectangle(width=0.35, height=2.8, fill_color=DIM, fill_opacity=0.6,
                          stroke_color=MUTED, stroke_width=1)
            cap = Rectangle(width=0.55, height=0.18, fill_color=DIM, fill_opacity=0.7,
                            stroke_width=0).move_to(c.get_top() + UP * 0.09)
            base = Rectangle(width=0.55, height=0.18, fill_color=DIM, fill_opacity=0.7,
                             stroke_width=0).move_to(c.get_bottom() + DOWN * 0.09)
            col = VGroup(c, cap, base)
            col.move_to(LEFT * 2.2 + RIGHT * i * 1.5 + UP * ZONE_MID)
            cols.add(col)

        yale_label = safe_text("YALE", font="Bebas Neue", font_size=50, color=MUTED)
        yale_label.move_to(UP * (ZONE_MID + 1.8))

        # Graduation cap above YALE text
        cap = graduation_cap_shape(0.8, DIM)
        cap.move_to(UP * (ZONE_MID + 2.5))

        # Math symbols scattered at LOWER
        symbols = VGroup()
        sym_data = [
            ("mod", LEFT*2.5 + UP*ZONE_LOWER + UP*0.5, MATH_CYAN, 50),
            ("base 8", RIGHT*2.0 + UP*ZONE_LOWER + UP*0.7, MATH_CYAN, 45),
            ("{A,B}", LEFT*0.5 + UP*ZONE_LOWER + DOWN*0.3, MATH_GOLD, 45),
            ("x + y", RIGHT*0.5 + UP*ZONE_LOWER + UP*0.2, MATH_GOLD, 40),
        ]
        for txt, pos, col, fs in sym_data:
            s = safe_text(txt, font="DM Serif Display", font_size=fs, color=col)
            s.move_to(pos)
            symbols.add(s)

        div = section_div(5, MATH_GOLD).move_to(UP * (ZONE_FOOTER + 1.0))

        for_children = safe_text("FOR CHILDREN.", font="Bebas Neue", font_size=65, color=CRISIS_RED)
        for_children.move_to(UP * ZONE_FOOTER)

        # ── Timing: 10.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "Congress threw money at it."
        self.play(LaggedStart(*[FadeIn(d, shift=DOWN*0.5) for d in dollars],
                              lag_ratio=0.08), run_time=0.8)               # t=1.1
        # Dollars drift down slowly
        self.play(*[d.animate.shift(DOWN * 0.3) for d in dollars],
                  run_time=1.1)                                             # t=2.2

        # VTT 2.50: "Yale built a new curriculum."
        self.play(LaggedStart(*[FadeIn(c, shift=UP*0.2) for c in cols],
                              lag_ratio=0.1), run_time=0.8)                # t=3.0
        self.play(FadeIn(yale_label, scale=1.05),
                  GrowFromCenter(cap), run_time=0.4)                       # t=3.4
        self.wait(0.8); t += 0.8

        # VTT 4.50: "Abstract algebra. Modular arithmetic. Number bases."
        self.play(LaggedStart(*[FadeIn(s, scale=1.1) for s in symbols],
                              lag_ratio=0.15), run_time=1.0)               # t=5.2
        # Symbols pulse gently
        self.play(*[s.animate.scale(1.1).set_opacity(1.0) for s in symbols],
                  run_time=0.8)                                             # t=6.0
        self.play(*[s.animate.scale(1/1.1) for s in symbols],
                  run_time=0.5)                                             # t=6.5
        self.wait(0.7); t += 0.7

        # VTT 7.50: "For children."
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(for_children, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(for_children.get_center(), color=CRISIS_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=8.3
        # Glow pulse behind text
        glow = Circle(radius=2.0, fill_color=CRISIS_RED, fill_opacity=0.04,
                      stroke_width=0).move_to(for_children)
        self.play(FadeIn(glow), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 10.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: THE SCALE (20.0–30.0s = 10.00s)
# TITLE: THE SCALE | UPPER: textbook stack | MID: bar chart 23K→1.8M
# LOWER: 85% | FOOTER: NEW MATH
# ================================================================
class Scene3_Scale(Scene):
    DURATION = 10.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE SCALE", color=MATH_CYAN, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # Textbooks stacked at UPPER
        books = VGroup()
        for i in range(5):
            b = textbook_shape(1.5, BOOK_COVER)
            b.move_to(LEFT * 2 + RIGHT * i * 1.1 + UP * ZONE_UPPER)
            books.add(b)

        # Bar chart at MID — 23K vs 1.8M (bars start from baseline at ZONE_MID - 1)
        bar_baseline_y = ZONE_MID - 1.0
        bar_old = Rectangle(width=1.2, height=0.5, fill_color=DIM, fill_opacity=0.7,
                            stroke_color=DIM, stroke_width=1)
        bar_old.move_to(LEFT * 2 + UP * (bar_baseline_y + 0.25))
        old_label = safe_text("23K", font="Bebas Neue", font_size=35, color=DIM)
        old_label.next_to(bar_old, UP, buff=0.15)

        bar_new_target = Rectangle(width=1.2, height=3.5, fill_color=MATH_CYAN, fill_opacity=0.8,
                                   stroke_color=MATH_CYAN, stroke_width=1)
        bar_new_target.move_to(RIGHT * 1.5 + UP * (bar_baseline_y + 1.75))
        new_label = safe_text("1.8M", font="Bebas Neue", font_size=55, color=MATH_CYAN)
        new_label.next_to(bar_new_target, UP, buff=0.15)

        years_label = safe_text("3 YEARS", font="Inter", font_size=24, color=MUTED, weight="BOLD")
        years_label.move_to(UP * (bar_baseline_y - 0.4))

        # Arrow from old to new bar
        grow_arrow = Arrow(bar_old.get_right() + RIGHT * 0.2,
                           bar_new_target.get_left() + LEFT * 0.2,
                           color=MATH_GOLD, stroke_width=2, buff=0.1)

        # 85% at LOWER
        eighty_five = safe_text("85%", font="Bebas Neue", font_size=150, color=MATH_CYAN)
        eighty_five.move_to(UP * ZONE_LOWER)

        adopted = safe_text("ADOPTED IT.", font="Bebas Neue", font_size=45, color=MUTED)
        adopted.move_to(UP * (ZONE_LOWER - 1.3))

        div = section_div(5, MATH_GOLD).move_to(UP * (ZONE_FOOTER + 0.8))

        new_math = safe_text("NEW MATH.", font="Bebas Neue", font_size=60, color=MATH_GOLD)
        new_math.move_to(UP * ZONE_FOOTER)

        # ── Timing: 10.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "Textbook sales went from 23,000 to 1.8 million"
        self.play(LaggedStart(*[FadeIn(b, scale=0.9) for b in books],
                              lag_ratio=0.08), run_time=0.7)               # t=1.0
        self.play(FadeIn(bar_old), FadeIn(old_label), run_time=0.4); t += 0.4
        self.wait(0.6); t += 0.6

        # Bar grows from small
        bar_new = bar_new_target.copy().stretch_to_fit_height(0.3)
        bar_new.move_to(RIGHT * 1.5 + UP * (bar_baseline_y + 0.15))
        self.play(FadeIn(bar_new), run_time=0.2); t += 0.2
        self.play(bar_new.animate.become(bar_new_target), run_time=0.8); t += 0.8
        self.play(FadeIn(new_label, scale=1.1),
                  GrowArrow(grow_arrow), run_time=0.4)                    # t=3.4
        self.play(FadeIn(years_label), run_time=0.3); t += 0.3

        # VTT 4.00: "85 percent of high schools adopted it."
        self.play(FadeIn(eighty_five, scale=1.3), run_time=0.6); t += 0.6
        self.play(Flash(eighty_five.get_center(), color=MATH_CYAN,
                        line_length=0.5, num_lines=10, run_time=0.3))     # t=4.6
        self.play(FadeIn(adopted, shift=UP*0.1), run_time=0.4); t += 0.4
        # Books slowly drift apart to show spread
        self.play(*[b.animate.shift(RIGHT * 0.15 * (i - 2))
                    for i, b in enumerate(books)], run_time=1.7)          # t=6.7

        # VTT 7.00: "They called it the New Math."
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(new_math, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(new_math.get_center(), color=MATH_GOLD,
                        line_length=0.3, num_lines=6, run_time=0.3))      # t=7.8
        target = getattr(self.__class__, 'DURATION', 10.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE PROBLEM (30.0–40.0s = 10.00s)
# TITLE: THE PROBLEM | UPPER: chalkboard+??? | MID: parent+child+homework
# LOWER: 5% TRAINED | FOOTER: music notes (comedy song)
# ================================================================
class Scene4_Problem(Scene):
    DURATION = 10.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE PROBLEM", color=CRISIS_RED, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # Teacher at chalkboard UPPER
        board_sm = chalkboard_shape(4.5, 2.2, CHALK_GREEN)
        board_sm.move_to(UP * ZONE_UPPER)
        question = safe_text("???", font="Bebas Neue", font_size=80, color=CRISIS_RED)
        question.move_to(UP * ZONE_UPPER)

        # Confused parent + child at MID
        parent = child_shape(2.0, MUTED)
        parent.move_to(LEFT * 1.5 + UP * ZONE_MID)
        child = child_shape(1.3, WHITE_SOFT)
        child.move_to(RIGHT * 0.0 + UP * (ZONE_MID - 0.2))

        # Homework paper
        hw = Rectangle(width=0.8, height=1.0, fill_color="#E8E0D0", fill_opacity=0.5,
                       stroke_color=MUTED, stroke_width=1)
        hw.move_to(RIGHT * 1.8 + UP * ZONE_MID)
        hw_q = safe_text("?", font="Bebas Neue", font_size=40, color=CRISIS_RED)
        hw_q.move_to(hw.get_center())

        confused = safe_text("CAN'T HELP.", font="Bebas Neue", font_size=50, color=MUTED)
        confused.move_to(UP * (ZONE_MID - 1.5))

        div = section_div(5, CRISIS_RED).move_to(UP * (ZONE_LOWER + 1.2))

        # 5% TRAINED at LOWER
        five_pct = safe_text("5%", font="Bebas Neue", font_size=160, color=CRISIS_RED)
        five_pct.move_to(UP * ZONE_LOWER)

        trained = safe_text("TEACHERS TRAINED.", font="Bebas Neue", font_size=45, color=MUTED)
        trained.move_to(UP * (ZONE_LOWER - 1.4))

        # Music notes for the comedy song beat — at FOOTER
        notes = VGroup()
        note_positions = [LEFT*2.5, LEFT*1.0, RIGHT*0.5, RIGHT*2.0]
        for pos in note_positions:
            n = music_note_shape(0.7, MATH_GOLD)
            n.move_to(pos + UP * ZONE_FOOTER)
            notes.add(n)

        harvard_label = safe_text("HARVARD", font="Inter", font_size=22,
                                  color=DEAD_GRAY, weight="BOLD")
        harvard_label.move_to(UP * (ZONE_FOOTER - 0.5))

        # ── Timing: 10.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "Only 5 percent of elementary teachers were trained."
        self.play(FadeIn(board_sm, scale=0.9), run_time=0.5); t += 0.5
        self.play(FadeIn(question, scale=1.2), run_time=0.4); t += 0.4
        # Question marks shake
        self.play(question.animate.shift(RIGHT*0.1), run_time=0.08); t += 0.08
        self.play(question.animate.shift(LEFT*0.2), run_time=0.08); t += 0.08
        self.play(question.animate.shift(RIGHT*0.1), run_time=0.08); t += 0.08
        self.wait(1.76); t += 1.76

        # VTT 3.50: "Parents couldn't help with homework."
        self.play(FadeIn(parent, shift=UP*0.15), FadeIn(child, shift=UP*0.15),
                  run_time=0.5)                                             # t=3.7
        self.play(FadeIn(hw), FadeIn(hw_q), run_time=0.3); t += 0.3
        self.play(FadeIn(confused, shift=UP*0.1), run_time=0.4); t += 0.4
        self.play(Create(div), run_time=0.3); t += 0.3

        self.play(FadeIn(five_pct, scale=1.3), run_time=0.6); t += 0.6
        self.play(Flash(five_pct.get_center(), color=CRISIS_RED,
                        line_length=0.5, num_lines=10, run_time=0.3))     # t=5.6
        self.play(FadeIn(trained, shift=UP*0.1), run_time=0.4); t += 0.4
        self.wait(0.3); t += 0.3

        # VTT 6.50: "A Harvard mathematician wrote a comedy song about it."
        self.play(LaggedStart(*[GrowFromCenter(n) for n in notes],
                              lag_ratio=0.12), run_time=0.7)               # t=7.0
        self.play(FadeIn(harvard_label, shift=UP*0.05), run_time=0.3); t += 0.3
        # Notes bounce/drift up
        self.play(*[n.animate.shift(UP * np.random.uniform(0.2, 0.5) +
                                    RIGHT * np.random.uniform(-0.15, 0.15))
                    for n in notes], run_time=1.0)                         # t=8.3
        # Notes fade to dim
        self.play(*[n.animate.set_opacity(0.4) for n in notes],
                  run_time=0.5)                                             # t=8.8
        target = getattr(self.__class__, 'DURATION', 10.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE COLLAPSE (40.0–50.0s = 10.00s)
# TITLE: THE COLLAPSE | UPPER: book + 1973 | MID: red X over math
# LOWER: NEVER THOUGHT / ABOUT TEACHING | FOOTER: creator admitted
# ================================================================
class Scene5_Collapse(Scene):
    DURATION = 10.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE COLLAPSE", color=CRISIS_RED, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # Book at UPPER — "WHY JOHNNY CAN'T ADD"
        book = textbook_shape(3.0, CRISIS_RED)
        book.move_to(UP * ZONE_UPPER)
        book_title1 = safe_text("WHY JOHNNY", font="Bebas Neue", font_size=35, color=WHITE_SOFT)
        book_title1.move_to(UP * (ZONE_UPPER + 0.3))
        book_title2 = safe_text("CAN'T ADD", font="Bebas Neue", font_size=40, color=MATH_GOLD)
        book_title2.move_to(UP * (ZONE_UPPER - 0.3))

        yr_1973 = safe_text("1973", font="Inter", font_size=26, color=MUTED, weight="BOLD")
        yr_1973.move_to(UP * (ZONE_UPPER - 1.5))

        # Red X through math symbols at MID
        math_syms = VGroup()
        sym_texts = ["{A,B}", "mod", "base 8", "x + y"]
        sym_offsets = [LEFT*1.8 + UP*0.3, RIGHT*1.5 + UP*0.5,
                       LEFT*1.0 + DOWN*0.5, RIGHT*2.0 + DOWN*0.3]
        for txt, offset in zip(sym_texts, sym_offsets):
            s = safe_text(txt, font="DM Serif Display", font_size=40, color=DIM)
            s.move_to(UP * ZONE_MID + offset)
            math_syms.add(s)

        x_line1 = Line(LEFT*3 + UP*(ZONE_MID + 1.2), RIGHT*3 + UP*(ZONE_MID - 1.2),
                       color=CRISIS_RED, stroke_width=7)
        x_line2 = Line(RIGHT*3 + UP*(ZONE_MID + 1.2), LEFT*3 + UP*(ZONE_MID - 1.2),
                       color=CRISIS_RED, stroke_width=7)

        div = section_div(5, CRISIS_RED).move_to(UP * (ZONE_LOWER + 1.5))

        # "NEVER THOUGHT ABOUT TEACHING" at LOWER
        never1 = safe_text("NEVER THOUGHT", font="Bebas Neue", font_size=70, color=WHITE_SOFT)
        never1.move_to(UP * ZONE_LOWER)
        never2 = safe_text("ABOUT TEACHING.", font="Bebas Neue", font_size=70, color=CRISIS_RED)
        never2.move_to(UP * (ZONE_LOWER - 1.2))

        footer_div = section_div(3, MUTED).move_to(UP * (ZONE_FOOTER + 0.7))

        admitted = safe_text("THE CREATOR ADMITTED IT.", font="Inter", font_size=22,
                             color=DEAD_GRAY, weight="BOLD")
        admitted.move_to(UP * ZONE_FOOTER)

        # ── Timing: 10.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "By 1973, a bestseller called Why Johnny Can't Add killed it."
        self.play(GrowFromCenter(book), run_time=0.6); t += 0.6
        self.play(FadeIn(book_title1, shift=DOWN*0.05),
                  FadeIn(book_title2, shift=UP*0.05), run_time=0.5)       # t=1.4
        self.play(FadeIn(yr_1973), run_time=0.3); t += 0.3
        # Book settles with a slight bounce
        self.play(book.animate.shift(DOWN * 0.1), run_time=0.2); t += 0.2
        self.play(book.animate.shift(UP * 0.1), run_time=0.2); t += 0.2
        self.wait(1.6); t += 1.6

        # VTT 4.50: "Even the guy who created New Math admitted"
        self.play(LaggedStart(*[FadeIn(s, scale=0.9) for s in math_syms],
                              lag_ratio=0.1), run_time=0.6)                # t=4.3
        self.play(Create(x_line1), run_time=0.3); t += 0.3
        self.play(Create(x_line2), run_time=0.3); t += 0.3
        # Math symbols fade to ghostly after X
        self.play(*[s.animate.set_opacity(0.25) for s in math_syms],
                  run_time=0.5)                                             # t=5.4
        self.wait(1.3); t += 1.3

        # VTT 7.00: "they never thought about how to actually teach it."
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(never1, scale=1.05), run_time=0.5); t += 0.5
        self.play(FadeIn(never2, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(never2.get_center(), color=CRISIS_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=8.3
        self.play(Create(footer_div), run_time=0.2); t += 0.2
        self.play(FadeIn(admitted, shift=UP*0.05), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 10.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE PUNCH (50.0–59.5s = 9.50s)
# Sputnik UPPER | child+book MID | PANIC ATTACK LOWER | letterbox
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 9.5
    def construct(self):
        self.add(gradient_bg("#050508"), grid_lines(0.02))
        t = 0

        # Cinematic letterbox bars
        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP * (8 - bh/2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN * (8 - bh/2)),
        )

        stars = star_field(20, seed=99)
        self.add(stars)

        # Ghost chalkboard — barely visible
        ghost = chalkboard_shape(7, 4, CHALK_GREEN)
        ghost.move_to(UP * ZONE_MID)
        ghost.set_opacity(0.04)
        self.add(ghost)

        # Sputnik small at UPPER
        sputnik = sputnik_shape(1.5, MUTED, WHITE_SOFT)
        sputnik.move_to(UP * (ZONE_UPPER + 0.5))

        # Orbit echo
        orbit_echo = Ellipse(width=3, height=0.8, fill_opacity=0,
                             stroke_color=MUTED, stroke_width=0.8, stroke_opacity=0.2)
        orbit_echo.move_to(sputnik.get_center())

        # Child with algebra book at MID
        kid = child_shape(2.0, WHITE_SOFT)
        kid.move_to(LEFT * 1.0 + UP * ZONE_MID)
        book = textbook_shape(1.8, BOOK_COVER)
        book.move_to(RIGHT * 1.5 + UP * ZONE_MID)

        div1 = section_div(4, CRISIS_RED).move_to(UP * (ZONE_LOWER + 2.0))

        # "PANIC ATTACK." at LOWER
        not_policy = safe_text("NOT POLICY.", font="Bebas Neue", font_size=70, color=MUTED)
        not_policy.move_to(UP * (ZONE_LOWER + 0.7))

        panic = safe_text("PANIC ATTACK.", font="Bebas Neue", font_size=90, color=CRISIS_RED)
        panic.move_to(UP * (ZONE_LOWER - 0.7))

        glow = Circle(radius=2.5, fill_color=CRISIS_RED, fill_opacity=0.04,
                      stroke_width=0).move_to(panic)

        div2 = section_div(3, MUTED).move_to(UP * ZONE_FOOTER)

        # ── Timing: 9.50s ──
        # VTT 0.10: "America saw a satellite in the sky"
        self.play(GrowFromCenter(sputnik), Create(orbit_echo), run_time=0.5); t += 0.5
        # Sputnik drifts slowly
        self.play(sputnik.animate.shift(RIGHT * 0.4 + DOWN * 0.1),
                  orbit_echo.animate.shift(RIGHT * 0.4 + DOWN * 0.1),
                  run_time=1.7)                                             # t=2.2

        # VTT 2.50: "and made 6-year-olds learn abstract algebra."
        self.play(FadeIn(kid, shift=UP*0.15), run_time=0.4); t += 0.4
        self.play(FadeIn(book, shift=LEFT*0.15), run_time=0.4); t += 0.4
        # Kid and book drift together slightly
        self.play(kid.animate.shift(RIGHT * 0.15),
                  book.animate.shift(LEFT * 0.15), run_time=1.0)          # t=4.0
        target = getattr(self.__class__, 'DURATION', 9.5)
        self.wait(max(0.1, target - t - 0.8))

        # VTT 5.00: "That's not education policy. That's a panic attack."
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(not_policy, shift=UP*0.08), run_time=0.5); t += 0.5
        self.play(FadeIn(glow), FadeIn(panic, scale=1.15), run_time=0.7); t += 0.7
        self.play(Flash(panic.get_center(), color=CRISIS_RED,
                        line_length=0.5, num_lines=10, run_time=0.4))     # t=6.6
        self.play(Create(div2), run_time=0.3); t += 0.3

        # Hold + fade to black
        # Slow zoom on panic text during hold
        self.play(panic.animate.scale(1.05), glow.animate.scale(1.1),
                  run_time=1.1)                                             # t=8.0
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5


# ── Infra ─────────────────────────────────────────────────────
def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_Plan, Scene3_Scale,
          Scene4_Problem, Scene5_Collapse, Scene6_Punch]
    config.output_file = f"new_math_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"new_math_scene_{idx+1}.mp4"):
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

    names = ["Scene1_Hook","Scene2_Plan","Scene3_Scale",
             "Scene4_Problem","Scene5_Collapse","Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_new_math.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="new_math", audio_path=str(audio))
    final = od / "new_math_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
