#!/usr/bin/env python3
"""America's 100-Year Math War (Manim). Visual-first per PRODUCTION_GUIDE.

6 scenes, ~49.5s (46.5s audio + 3s hold).
Domain shapes: pendulum_arm, chalkboard, bar_column, bridge_merge.
Visual throughline: pendulum swings in S1/S5/S6 — stops in S6.

VTT cues (absolute → relative):
  Scene 1 (0.0–7.0s):   0.42 fighting over math... 5.18 still haven't figured it out
  Scene 2 (7.0–15.3s):  7.48 every few decades... 10.44 basics... 11.84 memorize... 13.64 drill
  Scene 3 (15.3–24.1s): 15.28 countries that drill least... 18.52 Finland... 20.56 Japan
  Scene 4 (24.1–34.6s): 24.08 1990s Singapore... 27.28 combined... 30.84 average to #1
  Scene 5 (34.6–42.1s): 34.80 Singapore/Japan/Korea solved... 39.06 still arguing
  Scene 6 (42.1–49.5s): 42.10 spent a century arguing... 45.20 Singapore just taught it
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from manim import (
    Scene, Text, VGroup, Rectangle, RoundedRectangle, Circle,
    Line, Arrow, DashedLine, Dot, Polygon, Ellipse, Square, Arc,
    FadeIn, FadeOut, GrowFromCenter, Write, Create, DrawBorderThenFill,
    AnimationGroup, LaggedStart, Flash, GrowArrow, MoveToTarget,
    config, UP, DOWN, LEFT, RIGHT, ORIGIN,
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

BG = "#080A10"; GRID = "#1A2030"; SURFACE = "#15192A"
DRILL_RED = "#EF4444"; CONCEPT_BLUE = "#3B82F6"
GOLD = "#FFD700"; GOLD_DIM = "#B8960F"
WHITE_SOFT = "#F0F0F0"; MUTED = "#7B8DA0"; DIM = "#4A5568"
CHALK_GREEN = "#2D4A3E"; CHALK_BG = "#1A3028"
SAFE_W = 8.0; SAFE_TOP = 7.2; SAFE_BOT = -6.4


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
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    return t

def label_pill(txt, color=GOLD, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    p = RoundedRectangle(width=t.width+0.5, height=t.height+0.3, corner_radius=0.15,
                         fill_color=bg, fill_opacity=0.9, stroke_width=0).move_to(t)
    return VGroup(p, t)


# ── Domain shapes (4 required) ───────────────────────────────

def pendulum_arm(length=3.5, bob_radius=0.3, bob_color=MUTED, pivot_y=0):
    """Hinged pendulum arm with weighted bob. Swings via rotate()."""
    arm = Line(UP * 0, DOWN * length, color=MUTED, stroke_width=2)
    pivot = Dot(ORIGIN, radius=0.06, color=WHITE_SOFT)
    bob = Circle(radius=bob_radius, fill_color=bob_color, fill_opacity=0.8,
                 stroke_color=bob_color, stroke_width=2)
    bob.move_to(arm.get_bottom())
    grp = VGroup(arm, pivot, bob)
    grp.move_to(UP * pivot_y, aligned_edge=UP)
    return grp

def chalkboard(width=7, height=5):
    """Rounded rectangle with chalk-texture green fill."""
    board = RoundedRectangle(width=width, height=height, corner_radius=0.2,
                             fill_color=CHALK_GREEN, fill_opacity=0.9,
                             stroke_color="#4A6A5A", stroke_width=3)
    # Chalk dust line at bottom
    ledge = Rectangle(width=width*0.9, height=0.1, fill_color="#4A6A5A",
                      fill_opacity=0.6, stroke_width=0)
    ledge.align_to(board, DOWN).shift(DOWN * 0.05)
    return VGroup(board, ledge)

def bar_column(height=4, width=0.8, color=GOLD, label="", x=0, y_base=-2):
    """Simple scalable bar for charts."""
    bar = Rectangle(width=width, height=max(0.1, height), fill_color=color,
                    fill_opacity=0.8, stroke_color=color, stroke_width=1)
    bar.move_to(np.array([x, y_base + height/2, 0]))
    grp = VGroup(bar)
    if label:
        lbl = Text(label, font="Inter", font_size=22, color=WHITE_SOFT, weight="BOLD")
        lbl.next_to(bar, DOWN, buff=0.15)
        grp.add(lbl)
    return grp

def bridge_merge(width=3, height=2, color=GOLD):
    """Two angled lines converging into one upward arrow — synthesis."""
    left = Line(LEFT * width/2 + DOWN * height/2, ORIGIN,
                color=DRILL_RED, stroke_width=3)
    right = Line(RIGHT * width/2 + DOWN * height/2, ORIGIN,
                 color=CONCEPT_BLUE, stroke_width=3)
    arrow_shaft = Line(ORIGIN, UP * height * 0.6, color=color, stroke_width=4)
    arrow_head = Polygon(
        UP * height * 0.6 + LEFT * 0.2,
        UP * height * 0.6 + RIGHT * 0.2,
        UP * height * 0.85,
        fill_color=color, fill_opacity=1, stroke_width=0,
    )
    return VGroup(left, right, arrow_shaft, arrow_head)


# ================================================================
# SCENE 1: THE HOOK (0.0–7.0s)
# Timeline + pendulum swinging red/blue
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 7.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # Timeline
        tl = Line(LEFT * 3.5, RIGHT * 3.5, color=MUTED, stroke_width=2)
        tl.move_to(UP * 1)
        decades = ["1920", "1940", "1960", "1980", "2000", "2020"]
        ticks = VGroup()
        for i, yr in enumerate(decades):
            x = -3.5 + i * 7/5
            tick = Line(UP * 0.15, DOWN * 0.15, color=MUTED, stroke_width=1.5).move_to(UP * 1 + RIGHT * x)
            lbl = Text(yr, font="Bebas Neue", font_size=24, color=DIM).next_to(tick, DOWN, buff=0.1)
            ticks.add(VGroup(tick, lbl))

        # Pendulum — represents the 100-year debate swinging back and forth
        pend = pendulum_arm(length=2.5, bob_radius=0.35, bob_color=DRILL_RED, pivot_y=4.5)
        pivot = pend[1].get_center()

        # Context labels: DRILL on left, CONCEPTS on right (persistent, dimmed)
        drill_pill = label_pill("DRILL", color=DRILL_RED, fs=28)
        drill_pill.move_to(LEFT * 2.8 + UP * 5.5)
        concept_pill = label_pill("CONCEPTS", color=CONCEPT_BLUE, fs=28)
        concept_pill.move_to(RIGHT * 2.3 + UP * 5.5)

        # Subtitle explaining the pendulum
        context = safe_text("100 years of debate", font="Inter", font_size=22, color=DIM)
        context.move_to(UP * 3.2)

        self.play(Create(tl), run_time=0.5); t += 0.5
        self.play(LaggedStart(*[FadeIn(t) for t in ticks], lag_ratio=0.08), run_time=0.6); t += 0.6
        self.play(FadeIn(pend), FadeIn(context), run_time=0.3); t += 0.3

        # Both labels appear dimmed — the pendulum lights up whichever side it swings to
        drill_pill.set_opacity(0.25)
        concept_pill.set_opacity(0.25)
        self.play(FadeIn(drill_pill), FadeIn(concept_pill), run_time=0.2); t += 0.2

        # Swing 1: LEFT → DRILL lights up
        self.play(
            pend.animate.rotate(-25 * DEGREES, about_point=pivot),
            pend[2].animate.set_color(DRILL_RED),
            drill_pill.animate.set_opacity(1.0),
            run_time=0.5,
        )
        self.wait(0.4); t += 0.4

        # Swing 2: RIGHT → CONCEPTS lights up, DRILL dims
        self.play(
            pend.animate.rotate(50 * DEGREES, about_point=pivot),
            pend[2].animate.set_color(CONCEPT_BLUE),
            drill_pill.animate.set_opacity(0.25),
            concept_pill.animate.set_opacity(1.0),
            run_time=0.6,
        )
        self.wait(0.4); t += 0.4

        # Swing 3: LEFT → DRILL lights up again, CONCEPTS dims
        self.play(
            pend.animate.rotate(-50 * DEGREES, about_point=pivot),
            pend[2].animate.set_color(DRILL_RED),
            drill_pill.animate.set_opacity(1.0),
            concept_pill.animate.set_opacity(0.25),
            run_time=0.5,
        )
        self.wait(0.3); t += 0.3

        # Decelerate to center — natural physics (big swing → small → stop)
        self.play(
            pend.animate.rotate(25 * DEGREES, about_point=pivot),
            pend[2].animate.set_color(MUTED),
            drill_pill.animate.set_opacity(0.25),
            run_time=0.4,
        )
        target = getattr(self.__class__, 'DURATION', 7.0)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 2: THE WRONG ANSWER (7.0–15.3s)
# Chalkboard FILLING the frame with equations — claustrophobic, mechanical
# ================================================================
class Scene2_WrongAnswer(Scene):
    DURATION = 8.3
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE WRONG ANSWER", color=DRILL_RED)
        pill.move_to(UP * SAFE_TOP)

        # Board fills most of the safe zone
        board = chalkboard(SAFE_W, 10)
        board.move_to(UP * 0.5)

        # Two columns of equations — fills the board surface
        equations_left = [
            "7 × 8 = 56", "9 × 6 = 54", "12 × 12 = 144",
            "8 × 7 = 56", "6 × 9 = 54", "11 × 11 = 121",
        ]
        equations_right = [
            "5 × 13 = 65", "4 × 17 = 68", "3 × 9 = 27",
            "15 × 4 = 60", "7 × 7 = 49", "8 × 12 = 96",
        ]
        eq_texts = VGroup()
        for i, eq in enumerate(equations_left):
            lbl = Text(eq, font="Space Mono", font_size=28, color="#D4D4CC")
            lbl.move_to(LEFT * 2 + UP * (4.5 - i * 1.1))
            eq_texts.add(lbl)
        for i, eq in enumerate(equations_right):
            lbl = Text(eq, font="Space Mono", font_size=28, color="#D4D4CC")
            lbl.move_to(RIGHT * 2 + UP * (4.5 - i * 1.1))
            eq_texts.add(lbl)

        # "MEMORIZE" and "DRILL" stamps — clearly below the board
        memorize = safe_text("MEMORIZE.", font="Bebas Neue", font_size=70, color=DRILL_RED)
        memorize.move_to(DOWN * 5.2)
        drill = safe_text("DRILL.", font="Bebas Neue", font_size=70, color=DRILL_RED)
        drill.move_to(DOWN * 6.2)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(board, scale=1.02), run_time=0.5); t += 0.5

        # Equations write in two columns, accelerating
        speeds = [0.4, 0.35, 0.3, 0.25, 0.22, 0.2, 0.35, 0.3, 0.25, 0.22, 0.2, 0.18]
        for eq, speed in zip(eq_texts, speeds):
            self.play(Write(eq), run_time=speed)
        # Total write time: ~3.2s → t≈4.0

        # Stamps slam in
        self.play(FadeIn(memorize, scale=1.2), run_time=0.3); t += 0.3
        self.play(FadeIn(drill, scale=1.2), run_time=0.3); t += 0.3
        self.play(Flash(drill.get_center(), color=DRILL_RED,
                        line_length=0.3, num_lines=6, run_time=0.2))       # t=4.8
        target = getattr(self.__class__, 'DURATION', 8.3)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 3: THE CONTRADICTION (15.3–24.1s)
# Bar comparison: drill vs scores inverted
# ================================================================
class Scene3_Contradiction(Scene):
    DURATION = 8.8
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE CONTRADICTION", color=CONCEPT_BLUE)
        pill.move_to(UP * SAFE_TOP)

        # Clear layout: two side-by-side comparisons
        # Left side: HOW MUCH THEY DRILL (bar height = drill amount)
        # Right side: HOW THEY SCORE (bar height = test scores)
        # The punchline: the bars are INVERTED

        drill_title = safe_text("DRILL HOURS", font="Bebas Neue", font_size=32, color=DRILL_RED)
        drill_title.move_to(LEFT * 2.2 + UP * 5.8)
        score_title = safe_text("TEST SCORES", font="Bebas Neue", font_size=32, color=GOLD)
        score_title.move_to(RIGHT * 2.2 + UP * 5.8)

        # Divider between the two charts
        div = DashedLine(UP * 5.3, DOWN * 2, color=MUTED, stroke_width=1, dash_length=0.15)

        # DRILL side (left) — US tall, FIN/JPN short
        drill_us = bar_column(4.5, 0.8, DRILL_RED, "US", -3.2, -1)
        drill_fin = bar_column(1.5, 0.8, CONCEPT_BLUE, "FIN", -2.0, -1)
        drill_jpn = bar_column(1.8, 0.8, CONCEPT_BLUE, "JPN", -0.9, -1)

        # SCORE side (right) — US short, FIN/JPN tall (INVERTED!)
        score_us = bar_column(1.8, 0.8, DIM, "US", 0.9, -1)
        score_fin = bar_column(4.2, 0.8, GOLD, "FIN", 2.0, -1)
        score_jpn = bar_column(4.5, 0.8, GOLD, "JPN", 3.2, -1)

        # Punchline text
        punchline = safe_text("LESS DRILL = HIGHER SCORES", font="Bebas Neue",
                              font_size=38, color=GOLD)
        punchline.move_to(DOWN * 4)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(drill_title), FadeIn(score_title), Create(div), run_time=0.4); t += 0.4

        # Drill bars grow
        self.play(GrowFromCenter(drill_us), GrowFromCenter(drill_fin),
                  GrowFromCenter(drill_jpn), run_time=0.7)
        self.wait(0.8); t += 0.8

        # Score bars grow — the inversion is the visual surprise
        self.play(GrowFromCenter(score_us), GrowFromCenter(score_fin),
                  GrowFromCenter(score_jpn), run_time=0.7)
        self.wait(0.6); t += 0.6

        # Punchline
        self.play(FadeIn(punchline, shift=UP * 0.3), run_time=0.4); t += 0.4

        # US score pulses to draw attention to how low it is
        self.play(score_us[0].animate.set_color(DRILL_RED), run_time=0.3); t += 0.3
        self.play(score_us[0].animate.set_color(DIM), run_time=0.3); t += 0.3

        target = getattr(self.__class__, 'DURATION', 8.8)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 4: THE PROOF (24.1–34.6s)
# Singapore merge: LABELED concepts + COLORED bars
# ================================================================
class Scene4_Proof(Scene):
    DURATION = 10.5
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("SINGAPORE", color=GOLD)
        pill.move_to(UP * SAFE_TOP)

        # Simple text equation: DRILL + CONCEPTS = SINGAPORE #1
        drill_word = safe_text("DRILL", font="Bebas Neue", font_size=56, color=DRILL_RED)
        plus = safe_text("+", font="Bebas Neue", font_size=56, color=WHITE_SOFT)
        concepts_word = safe_text("CONCEPTS", font="Bebas Neue", font_size=56, color=CONCEPT_BLUE)
        equals = safe_text("=", font="Bebas Neue", font_size=56, color=WHITE_SOFT)
        equation = VGroup(drill_word, plus, concepts_word).arrange(RIGHT, buff=0.3)
        equation.move_to(UP * 4.5)

        # Result: SINGAPORE #1
        result = safe_text("SINGAPORE", font="Bebas Neue", font_size=64, color=GOLD)
        result.move_to(UP * 2.5)

        # Bar chart — SG rises from average to #1
        other_data = [("US", 2.2, DIM), ("UK", 1.8, DIM), ("SG", 2.2, DIM), ("AUS", 2.0, DIM), ("CAN", 1.9, DIM)]
        bars = VGroup()
        for i, (name, h, col) in enumerate(other_data):
            x = -3 + i * 1.5
            b = bar_column(h, 0.8, col, name, x, -3)
            bars.add(b)

        # SG gold target (taller)
        sg_gold = bar_column(5.5, 0.8, GOLD, "SG", 0, -3)
        num_one = safe_text("#1", font="Bebas Neue", font_size=70, color=GOLD)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # Equation builds
        self.play(FadeIn(drill_word, shift=RIGHT * 0.3), run_time=0.3); t += 0.3
        self.play(FadeIn(plus), FadeIn(concepts_word, shift=LEFT * 0.3), run_time=0.3); t += 0.3
        self.wait(1.5); t += 1.5

        # = SINGAPORE
        self.play(FadeIn(equals.next_to(equation, RIGHT, buff=0.3)), run_time=0.2); t += 0.2
        self.play(FadeIn(result, scale=1.2), run_time=0.4); t += 0.4
        self.wait(1.0); t += 1.0

        # Bars appear — all average height
        self.play(LaggedStart(*[GrowFromCenter(b) for b in bars], lag_ratio=0.1), run_time=0.6); t += 0.6
        self.wait(1.0); t += 1.0

        # SG bar rises to #1
        self.play(bars[2].animate.become(sg_gold), run_time=1.2); t += 1.2
        num_one.next_to(sg_gold[0], UP, buff=0.2)
        self.play(FadeIn(num_one, scale=1.3), run_time=0.4); t += 0.4
        self.play(Flash(num_one.get_center(), color=GOLD,
                        line_length=0.4, num_lines=10, run_time=0.3))
        target = getattr(self.__class__, 'DURATION', 10.5)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 5: THE SCALE (34.6–42.1s)
# Leaderboard: SG/JPN/KOR solved — US still arguing (mini pendulum)
# ================================================================
class Scene5_Scale(Scene):
    DURATION = 7.5
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE SCALE", color=GOLD)
        pill.move_to(UP * SAFE_TOP)

        # All 4 bars — built with plain rectangles for reliable sizing
        bar_bottom = -2.0
        countries = [
            ("SG", 5.5, GOLD, "#1"),
            ("JPN", 5.0, GOLD, "#5"),
            ("KOR", 4.8, GOLD, "#7"),
            ("US", 2.5, DRILL_RED, "#37"),
        ]
        all_bars = VGroup()
        rank_labels = VGroup()
        name_labels = VGroup()
        for i, (name, h, col, rank) in enumerate(countries):
            x = -2.5 + i * 1.7
            bar = Rectangle(width=1.0, height=h, fill_color=col, fill_opacity=0.8,
                            stroke_color=col, stroke_width=1)
            bar.move_to(RIGHT * x + UP * (bar_bottom + h/2))
            all_bars.add(bar)

            nlbl = safe_text(name, font="Inter", font_size=26, color=WHITE_SOFT, weight="BOLD")
            nlbl.next_to(bar, DOWN, buff=0.15)
            name_labels.add(nlbl)

            rlbl = safe_text(rank, font="Bebas Neue", font_size=40, color=col)
            rlbl.next_to(bar, UP, buff=0.15)
            rank_labels.add(rlbl)

        # Status labels below bars
        solved_lbl = safe_text("SOLVED", font="Inter", font_size=28, color="#22C55E", weight="BOLD")
        solved_lbl.move_to(DOWN * 3.5 + LEFT * 0.8)

        # US-specific: show the cycle of failed reforms
        us_cycle = safe_text("NEW MATH → BACK TO BASICS\n→ COMMON CORE → ???",
                             font="Inter", font_size=22, color=DRILL_RED)
        us_cycle.move_to(DOWN * 5)

        divider_line = Line(LEFT * 0.3, LEFT * 0.3 + DOWN * 4, color=MUTED,
                            stroke_width=1, stroke_opacity=0.3)
        divider_line.move_to(RIGHT * 1.05 + DOWN * 1)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # Gold bars first (SG, JPN, KOR)
        self.play(
            LaggedStart(*[GrowFromCenter(b, DOWN) for b in all_bars[:3]], lag_ratio=0.15),
            LaggedStart(*[FadeIn(n) for n in name_labels[:3]], lag_ratio=0.15),
            run_time=0.7,
        )
        self.play(
            LaggedStart(*[FadeIn(r, scale=1.3) for r in rank_labels[:3]], lag_ratio=0.1),
            run_time=0.4,
        )
        self.play(FadeIn(solved_lbl), run_time=0.3); t += 0.3
        self.wait(0.8); t += 0.8

        # Divider then US bar
        self.play(Create(divider_line), run_time=0.2); t += 0.2
        self.play(GrowFromCenter(all_bars[3], DOWN), FadeIn(name_labels[3]),
                  FadeIn(rank_labels[3], scale=1.3), run_time=0.5)
        self.wait(0.5); t += 0.5

        # US reform cycle text
        self.play(FadeIn(us_cycle, shift=UP * 0.3), run_time=0.5); t += 0.5

        target = getattr(self.__class__, 'DURATION', 7.5)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 6: THE PUNCH (42.1–49.5s)
# Pendulum decelerates → stops. Gold line. Stillness.
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 7.4
    def construct(self):
        self.add(gradient_bg())
        t = 0

        # Letterbox bars
        bh = 1.2
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).to_edge(UP, buff=0),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).to_edge(DOWN, buff=0),
        )

        # Ghost pendulum in background — stopped, at center, very faint
        pend = pendulum_arm(length=3.0, bob_radius=0.3, bob_color=MUTED, pivot_y=4)
        pend.set_opacity(0.08)
        self.add(pend)

        # Text closer — two lines
        line1 = safe_text("We spent a century arguing", font="DM Serif Display",
                          font_size=44, color=WHITE_SOFT)
        line2 = safe_text("how to teach math.", font="DM Serif Display",
                          font_size=44, color=MUTED)
        top_text = VGroup(line1, line2).arrange(DOWN, buff=0.2).move_to(UP * 2)

        divider_line = Line(LEFT * 3, RIGHT * 3, color=GOLD, stroke_width=2)
        divider_line.move_to(ORIGIN)

        punch = safe_text("Singapore just taught it.", font="DM Serif Display",
                          font_size=52, color=GOLD)
        punch.move_to(DOWN * 2.5)

        # Slow reveal
        self.play(FadeIn(line1, shift=UP * 0.2), run_time=0.8); t += 0.8
        self.play(FadeIn(line2, shift=UP * 0.2), run_time=0.6); t += 0.6
        self.wait(0.5); t += 0.5
        self.play(Create(divider_line), run_time=0.5); t += 0.5
        self.wait(0.3); t += 0.3
        self.play(FadeIn(punch, shift=UP * 0.2), run_time=0.8); t += 0.8

        # Hold — let it land
        target = getattr(self.__class__, 'DURATION', 7.4)
        self.wait(max(0.1, target - t - 0.8))

        # Fade everything
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.2); t += 1.2
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=0.9); t += 0.9


# ── Infra ─────────────────────────────────────────────────────
SCENES = [Scene1_Hook, Scene2_WrongAnswer, Scene3_Contradiction,
          Scene4_Proof, Scene5_Scale, Scene6_Punch]

def render_single_scene(idx):
    config.output_file = f"math_wars_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    SCENES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"math_wars_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENES):
        n = f"math_wars_scene_{i+1}"; print(f"  Preview {n}...")
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
    if "--preview" in sys.argv:
        render_previews()
        from render_utils import run_preview_qa
        run_preview_qa(od / "previews")
        sys.exit(0)
    if "--scene" in sys.argv:
        timings_json = os.environ.get("TKK_SCENE_TIMINGS")
        if timings_json:
            _idx = int(sys.argv[sys.argv.index("--scene")+1])
            SCENES[_idx].DURATION = json.loads(timings_json)[_idx]
        render_single_scene(int(sys.argv[sys.argv.index("--scene")+1])); sys.exit(0)

    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_math_wars.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="math_wars", audio_path=str(audio))
    final = od / "math_wars_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")

    from render_utils import run_post_render_qa
    run_post_render_qa(str(final), scene_count=6)
