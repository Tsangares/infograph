#!/usr/bin/env python3
"""Death Bureaucracy S2 — 'Your Life is Worth $13.7 Million' (Manim).

6 scenes, ~37.4s (34.4s audio + 3s hold). Clinical, cold bureaucratic aesthetic.

VTT cues (absolute → relative to scene start):
  Scene 1 (0.0–4.8s = 4.80s):
    0.160 (0.16) The US government calculated exactly how much your life is worth.
  Scene 2 (4.8–10.1s = 5.30s):
    4.800 (0.00) 13.7 million dollars.
    6.800 (2.00) That is the official number.
    8.320 (3.52) Every federal agency uses it.
  Scene 3 (10.1–15.8s = 5.70s):
    10.160 (0.06) How?
    10.780 (0.68) They measure how much extra pay workers demand for dangerous jobs.
    14.520 (4.42) Then they do the math.
  Scene 4 (15.8–25.1s = 9.30s):
    15.840 (0.04) In 2002,
    17.300 (1.50) the EPA said seniors are worth 37 percent less.
    20.480 (4.68) AARP put out fliers: Seniors are three fifths of a person.
  Scene 5 (25.1–31.2s = 6.10s):
    25.100 (0.00) Then in 2026,
    26.320 (1.22) the EPA stopped counting health benefits from pollution entirely.
    29.920 (4.82) Cited uncertainty.
  Scene 6 (31.2–37.4s = 6.20s):
    31.260 (0.06) Your life has a price tag.
    32.960 (1.76) And they just zeroed it out.
    + 3s hold + fade
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

TTS_SCRIPT = """The US government calculated exactly how much your life is worth.
13.7 million dollars.
That is the official number.
Every federal agency uses it.
How?
They measure how much extra pay workers demand for dangerous jobs.
Then they do the math.
In 2002,
the EPA said seniors are worth 37 percent less.
AARP put out fliers: Seniors are three fifths of a person.
Then in 2026,
the EPA stopped counting health benefits from pollution entirely.
Cited uncertainty.
Your life has a price tag.
And they just zeroed it out."""

from manim import (
    Scene, Text, VGroup, VMobject, Group, Rectangle, RoundedRectangle, Circle,
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
config.background_color = "#0A0E16"
config.disable_caching = True

# Palette — clinical, cold bureaucratic
BG = "#0A0E16"
SURFACE = "#141C2B"
SURFACE2 = "#1A2538"
BORDER = "#2A3A50"
GRID = "#1A2030"
RED = "#E63946"
RED_DARK = "#8B1A22"
GOLD = "#FFD700"
GOLD_DIM = "#B8960F"
WHITE_SOFT = "#F0F0F0"
MUTED = "#7B8DA0"
TEAL = "#2EC4B6"
WARN = "#FF6B35"
DEAD_GRAY = "#4A5568"
FORM_BG = "#111827"
FORM_BORDER = "#374151"
CLINICAL_BLUE = "#3B82F6"
CLINICAL_DIM = "#1E40AF"
ICE = "#93C5FD"

SAFE_W = 8.0


# ── Helpers (shared with S1) ──────────────────────────────────

def gradient_bg(color1=BG, glow_color="#1A1A2E"):
    bg = Rectangle(width=12, height=20, fill_color=color1, fill_opacity=1, stroke_width=0)
    glow = Circle(radius=5, fill_color=glow_color, fill_opacity=0.08, stroke_width=0).move_to(UP * 2)
    return VGroup(bg, glow)


def grid_lines(rows=12, cols=6, opacity=0.06):
    lines = VGroup()
    for i in range(rows + 1):
        y = -8 + i * 16 / rows
        lines.add(Line(LEFT * 5, RIGHT * 5, color=GRID, stroke_width=0.5).move_to(UP * y).set_opacity(opacity))
    for j in range(cols + 1):
        x = -4.5 + j * 9 / cols
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
    p = RoundedRectangle(width=t.width + 0.5, height=t.height + 0.3,
                         corner_radius=0.18, fill_color=bg, fill_opacity=0.95,
                         stroke_color=color, stroke_width=1.5).move_to(t)
    return VGroup(p, t)


def safe_text(content, **kwargs):
    t = Text(content, **kwargs)
    if t.width > SAFE_W:
        t.scale(SAFE_W / t.width)
    return t


def form_field(label, value="", width=6, x=0, y=0, label_color=MUTED, value_color=WHITE_SOFT):
    lbl = Text(label, font="Inter", font_size=18, color=label_color)
    lbl.move_to(np.array([x - width/2 + lbl.width/2 + 0.1, y + 0.2, 0]))
    box = Rectangle(width=width, height=0.5, fill_color=FORM_BG, fill_opacity=0.8,
                    stroke_color=FORM_BORDER, stroke_width=1)
    box.move_to(np.array([x, y - 0.15, 0]))
    val = Text(value, font="Inter", font_size=22, color=value_color) if value else VGroup()
    if value:
        if val.width > width - 0.3:
            val.scale((width - 0.3) / val.width)
        val.move_to(box.get_center())
    return VGroup(box, lbl, val)


def stamp_overlay(text, color=RED, angle=12, fs=60):
    t = safe_text(text, font="Bebas Neue", font_size=fs, color=color)
    border = RoundedRectangle(width=t.width + 0.5, height=t.height + 0.35,
                              corner_radius=0.08, stroke_color=color,
                              stroke_width=5, fill_opacity=0)
    border.move_to(t)
    return VGroup(border, t).rotate(angle * DEGREES)


# ================================================================
# SCENE 1: THE HOOK (0.0–4.8s = 4.80s)
# VTT: 0.16 "The US government calculated exactly how much your life is worth."
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 4.4
    def construct(self):
        self.add(gradient_bg(), grid_lines(opacity=0.04))
        t = 0

        pill = label_pill("VALUE OF A STATISTICAL LIFE", color=CLINICAL_BLUE, fs=22)
        pill.move_to(UP * 7)

        header = Rectangle(width=9, height=0.08, fill_color=CLINICAL_BLUE,
                           fill_opacity=0.5, stroke_width=0)
        header.move_to(UP * 6.2)

        # The hook question
        calc = safe_text("Your government", font="DM Serif Display",
                        font_size=48, color=WHITE_SOFT)
        calc.move_to(UP * 3.5)
        calc2 = safe_text("calculated exactly", font="DM Serif Display",
                         font_size=48, color=WHITE_SOFT)
        calc2.move_to(UP * 2.3)

        div = section_div(5, CLINICAL_BLUE).move_to(UP * 0.8)

        how_much = safe_text("HOW MUCH", font="Bebas Neue", font_size=90, color=GOLD)
        how_much.move_to(DOWN * 0.8)
        your_life = safe_text("YOUR LIFE", font="Bebas Neue", font_size=90, color=GOLD)
        your_life.move_to(DOWN * 2.2)
        is_worth = safe_text("IS WORTH.", font="Bebas Neue", font_size=90, color=RED)
        is_worth.move_to(DOWN * 3.6)

        # ── Timing: 4.80s ──
        self.add(header)
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(calc, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(calc2, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(how_much, scale=1.1), run_time=0.6); t += 0.6
        self.play(FadeIn(your_life, scale=1.1), run_time=0.6); t += 0.6
        self.play(FadeIn(is_worth, scale=1.15), run_time=0.6); t += 0.6
        self.play(Flash(is_worth.get_center(), color=RED,
                        line_length=0.4, num_lines=8, run_time=0.3))        # t=4.0
        target = getattr(self.__class__, 'DURATION', 4.4)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 2: THE NUMBER (4.8–10.1s = 5.30s)
# VTT: 0.00 "13.7 million dollars."
#      2.00 "That is the official number."
#      3.52 "Every federal agency uses it."
# ================================================================
class Scene2_Number(Scene):
    DURATION = 4.9
    def construct(self):
        self.add(gradient_bg(glow_color="#1A2A1A"), grid_lines(opacity=0.04))
        t = 0

        pill = label_pill("THE NUMBER", color=GOLD, fs=28)
        pill.move_to(UP * 7)

        # Dollar sign
        dollar = safe_text("$", font="Bebas Neue", font_size=100, color=GOLD_DIM)
        dollar.move_to(UP * 4.5 + LEFT * 3)

        # Giant number
        big_num = safe_text("$13,700,000", font="Bebas Neue", font_size=110, color=GOLD)
        big_num.move_to(UP * 2.5)

        # Official badge
        official = safe_text("OFFICIAL VALUE", font="Inter", font_size=30,
                            color=WHITE_SOFT, weight="BOLD")
        official.move_to(UP * 0.8)
        of_life = safe_text("OF A STATISTICAL LIFE", font="Inter", font_size=26,
                           color=MUTED, weight="BOLD")
        of_life.move_to(UP * 0.1)

        # Agency list
        div = section_div(5, CLINICAL_BLUE).move_to(DOWN * 1.2)

        agencies = [
            ("EPA", DOWN * 2.3, TEAL),
            ("DOT", DOWN * 3.1, CLINICAL_BLUE),
            ("FDA", DOWN * 3.9, ICE),
            ("HHS", DOWN * 4.7, MUTED),
        ]
        agency_items = VGroup()
        for name, pos, col in agencies:
            dot = Dot(radius=0.08, color=col).move_to(LEFT * 2.5 + pos)
            lbl = safe_text(name, font="Inter", font_size=28, color=col, weight="BOLD")
            lbl.move_to(LEFT * 1.5 + pos)
            uses = safe_text("uses this number", font="Inter", font_size=24, color=MUTED)
            uses.move_to(RIGHT * 1.2 + pos)
            agency_items.add(VGroup(dot, lbl, uses))

        # ── Timing: 5.30s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(dollar, scale=1.3), run_time=0.3); t += 0.3
        self.play(FadeIn(big_num, scale=1.2), run_time=0.7); t += 0.7
        self.play(Flash(big_num.get_center(), color=GOLD,
                        line_length=0.5, num_lines=12, run_time=0.3))      # t=1.6

        # VTT 2.00: "That is the official number."
        self.play(FadeIn(official), FadeIn(of_life), run_time=0.5); t += 0.5

        # VTT 3.52: "Every federal agency uses it."
        self.wait(1.12); t += 1.12
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(
            LaggedStart(*[FadeIn(a, shift=LEFT * 0.1) for a in agency_items],
                         lag_ratio=0.12),
            run_time=1.0,
        )                                                                   # t=4.52
        target = getattr(self.__class__, 'DURATION', 4.9)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 3: THE METHOD (10.1–15.8s = 5.70s)
# VTT: 0.06 "How?"
#      0.68 "They measure how much extra pay workers demand for dangerous jobs."
#      4.42 "Then they do the math."
# ================================================================
class Scene3_Method(Scene):
    DURATION = 5.2
    def construct(self):
        self.add(gradient_bg(), grid_lines(opacity=0.05))
        t = 0

        pill = label_pill("THE METHOD", color=CLINICAL_BLUE, fs=28)
        pill.move_to(UP * 7)

        # "How?"
        how = safe_text("How?", font="Bebas Neue", font_size=100, color=WHITE_SOFT)
        how.move_to(UP * 5)

        # Diagram: worker → danger → extra pay → math → dollar value
        worker_lbl = safe_text("DANGEROUS JOB", font="Inter", font_size=26,
                              color=WARN, weight="BOLD")
        worker_lbl.move_to(UP * 2.5)

        plus = safe_text("+", font="Bebas Neue", font_size=60, color=MUTED)
        plus.move_to(UP * 1.5)

        extra_lbl = safe_text("EXTRA PAY DEMANDED", font="Inter", font_size=26,
                             color=GOLD, weight="BOLD")
        extra_lbl.move_to(UP * 0.5)

        arrow = Arrow(UP * 0.0 + LEFT * 0.3, DOWN * 1.0 + LEFT * 0.3,
                      color=CLINICAL_BLUE, stroke_width=3, buff=0.1)
        arrow.move_to(DOWN * 0.5)

        equals_lbl = safe_text("= VALUE OF YOUR LIFE", font="Inter", font_size=28,
                              color=WHITE_SOFT, weight="BOLD")
        equals_lbl.move_to(DOWN * 1.5)

        result = safe_text("$13.7M", font="Bebas Neue", font_size=80, color=GOLD)
        result.move_to(DOWN * 3)

        # "Then they do the math."
        div = section_div(5, MUTED).move_to(DOWN * 4.5)
        math_txt = safe_text("Then they do the math.", font="DM Serif Display",
                            font_size=40, color=MUTED)
        math_txt.move_to(DOWN * 5.5)

        # Formula mockup
        formula = safe_text("VSL = ΔWage / ΔRisk", font="Inter", font_size=28,
                           color=DEAD_GRAY)
        formula.move_to(DOWN * 6.8)

        # ── Timing: 5.70s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.06: "How?"
        self.play(FadeIn(how, scale=1.15), run_time=0.4); t += 0.4

        # VTT 0.68: "They measure how much extra pay..."
        self.play(FadeIn(worker_lbl, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(FadeIn(plus), run_time=0.2); t += 0.2
        self.play(FadeIn(extra_lbl, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(GrowArrow(arrow), run_time=0.3); t += 0.3
        self.play(FadeIn(equals_lbl), run_time=0.4); t += 0.4
        self.play(FadeIn(result, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(result.get_center(), color=GOLD,
                        line_length=0.3, num_lines=8, run_time=0.3))        # t=3.4

        # VTT 4.42: "Then they do the math."
        self.wait(0.72); t += 0.72
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(math_txt, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(FadeIn(formula), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 5.2)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 4: THE SCANDAL (15.8–25.1s = 9.30s)
# VTT: 0.04 "In 2002,"
#      1.50 "the EPA said seniors are worth 37 percent less."
#      4.68 "AARP put out fliers: Seniors are three fifths of a person."
# ================================================================
class Scene4_Scandal(Scene):
    DURATION = 8.5
    def construct(self):
        self.add(gradient_bg("#0A0A12"), grid_lines(opacity=0.04))
        t = 0

        pill = label_pill("THE SCANDAL", color=RED, fs=28)
        pill.move_to(UP * 7)

        # Date
        date = safe_text("2002", font="Bebas Neue", font_size=120, color=RED)
        date.move_to(UP * 5)

        # EPA ruling
        epa = safe_text("THE EPA RULED:", font="Inter", font_size=30,
                        color=MUTED, weight="BOLD")
        epa.move_to(UP * 3)

        # "37% LESS"
        pct = safe_text("37%", font="Bebas Neue", font_size=140, color=RED)
        pct.move_to(UP * 1)
        less = safe_text("LESS", font="Bebas Neue", font_size=80, color=RED)
        less.move_to(DOWN * 0.6)

        target = safe_text("if you're a senior.", font="DM Serif Display",
                          font_size=40, color=MUTED)
        target.move_to(DOWN * 1.8)

        div = section_div(5, RED).move_to(DOWN * 3)

        # "3/5 of a person" — the historic echo
        aarp = safe_text("AARP RESPONSE:", font="Inter", font_size=24,
                        color=WARN, weight="BOLD")
        aarp.move_to(DOWN * 4)

        three_fifths = safe_text("3/5", font="Bebas Neue", font_size=120, color=GOLD)
        three_fifths.move_to(DOWN * 5.5)
        of_person = safe_text("OF A PERSON.", font="Bebas Neue", font_size=60, color=WHITE_SOFT)
        of_person.move_to(DOWN * 6.8)

        # ── Timing: 9.30s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(date, scale=1.2), run_time=0.6); t += 0.6
        self.play(Flash(date.get_center(), color=RED,
                        line_length=0.4, num_lines=8, run_time=0.3))        # t=1.3

        # VTT 1.50: "the EPA said seniors are worth 37 percent less."
        self.play(FadeIn(epa), run_time=0.3); t += 0.3
        self.play(FadeIn(pct, scale=1.3), run_time=0.7); t += 0.7
        self.play(FadeIn(less, scale=1.1), run_time=0.4); t += 0.4
        self.play(Flash(pct.get_center(), color=RED,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=3.0
        self.play(FadeIn(target, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.wait(0.88); t += 0.88

        # VTT 4.68: "AARP put out fliers: Seniors are three fifths of a person."
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(aarp), run_time=0.3); t += 0.3
        self.play(FadeIn(three_fifths, scale=1.2), run_time=0.7); t += 0.7
        self.play(Flash(three_fifths.get_center(), color=GOLD,
                        line_length=0.4, num_lines=10, run_time=0.3))      # t=5.98
        self.play(FadeIn(of_person, scale=1.05), run_time=0.6); t += 0.6
        target = getattr(self.__class__, 'DURATION', 8.5)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 5: THE TWIST (25.1–31.2s = 6.10s)
# VTT: 0.00 "Then in 2026,"
#      1.22 "the EPA stopped counting health benefits from pollution entirely."
#      4.82 "Cited uncertainty."
# ================================================================
class Scene5_Twist(Scene):
    DURATION = 5.6
    def construct(self):
        self.add(gradient_bg(), grid_lines(opacity=0.04))
        t = 0

        pill = label_pill("THE TWIST", color=WARN, fs=28)
        pill.move_to(UP * 7)

        date = safe_text("2026", font="Bebas Neue", font_size=120, color=WARN)
        date.move_to(UP * 5)

        epa2 = safe_text("THE EPA", font="Inter", font_size=32,
                         color=MUTED, weight="BOLD")
        epa2.move_to(UP * 3)

        stopped = safe_text("STOPPED COUNTING", font="Bebas Neue", font_size=70, color=RED)
        stopped.move_to(UP * 1.5)
        health = safe_text("health benefits from pollution.", font="DM Serif Display",
                          font_size=38, color=WHITE_SOFT)
        health.move_to(UP * 0.2)

        entirely = safe_text("ENTIRELY.", font="Bebas Neue", font_size=80, color=RED)
        entirely.move_to(DOWN * 1.5)

        div = section_div(5, DEAD_GRAY).move_to(DOWN * 3)

        # "UNCERTAINTY" stamp
        stamp = stamp_overlay("UNCERTAINTY", color=DEAD_GRAY, angle=-8, fs=55)
        stamp.move_to(DOWN * 4.8)

        cited = safe_text("Cited uncertainty.", font="DM Serif Display",
                         font_size=40, color=DEAD_GRAY)
        cited.move_to(DOWN * 6.5)

        # ── Timing: 6.10s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(date, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(date.get_center(), color=WARN,
                        line_length=0.4, num_lines=8, run_time=0.3))        # t=1.1

        # VTT 1.22: "the EPA stopped counting..."
        self.play(FadeIn(epa2), run_time=0.2); t += 0.2
        self.play(FadeIn(stopped, scale=1.05), run_time=0.6); t += 0.6
        self.play(FadeIn(health, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(FadeIn(entirely, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(entirely.get_center(), color=RED,
                        line_length=0.3, num_lines=8, run_time=0.3))        # t=3.2

        # VTT 4.82: "Cited uncertainty."
        self.wait(1.32); t += 1.32
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(stamp, scale=1.3), run_time=0.4); t += 0.4
        self.play(FadeIn(cited, shift=UP * 0.06), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 5.6)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 6: THE PUNCH (31.2–37.4s = 6.20s)
# VTT: 0.06 "Your life has a price tag."
#      1.76 "And they just zeroed it out."
# + 3s hold + fade
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 5.7
    def construct(self):
        self.add(gradient_bg())
        t = 0

        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP * (8 - bh / 2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN * (8 - bh / 2)),
        )
        self.add(grid_lines(opacity=0.02))

        div1 = section_div(4, GOLD).move_to(UP * 1)

        price = safe_text("Your life has a price tag.", font="DM Serif Display",
                         font_size=42, color=WHITE_SOFT)
        price.move_to(DOWN * 0.3)

        # The zeroed-out number
        amount = safe_text("$13,700,000", font="Bebas Neue", font_size=80, color=GOLD)
        amount.move_to(DOWN * 2)

        div2 = section_div(4, RED).move_to(DOWN * 3.2)

        zeroed = safe_text("$0", font="Bebas Neue", font_size=120, color=RED)
        zeroed.move_to(DOWN * 4.8)

        strike = Line(amount.get_left() + LEFT * 0.2, amount.get_right() + RIGHT * 0.2,
                      color=RED, stroke_width=5)
        strike.move_to(amount)

        out_txt = safe_text("Zeroed out.", font="DM Serif Display",
                           font_size=40, color=MUTED)
        out_txt.move_to(DOWN * 6.5)

        # ── Timing: 6.20s ──
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(price, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(amount, scale=1.05), run_time=0.6); t += 0.6

        # VTT 1.76: "And they just zeroed it out."
        self.play(Create(strike), run_time=0.3); t += 0.3
        self.play(Create(div2), run_time=0.2); t += 0.2
        self.play(FadeIn(zeroed, scale=1.3), run_time=0.7); t += 0.7
        self.play(Flash(zeroed.get_center(), color=RED,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=3.0
        self.play(FadeIn(out_txt, shift=UP * 0.06), run_time=0.5); t += 0.5

        # 3s hold + fade
        target = getattr(self.__class__, 'DURATION', 5.7)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.2); t += 1.2


# ── Per-scene render ──────────────────────────────────────────
def render_single_scene(scene_idx):
    scene_classes = [Scene1_Hook, Scene2_Number, Scene3_Method,
                     Scene4_Scandal, Scene5_Twist, Scene6_Punch]
    SC = scene_classes[scene_idx]
    output_dir = Path(__file__).parent
    config.output_file = f"death_s2_scene_{scene_idx + 1}"
    config.media_dir = str(output_dir / "media")
    SC().render()
    for mp4 in Path(config.media_dir).rglob(f"death_s2_scene_{scene_idx + 1}.mp4"):
        print(f"SCENE_FILE:{mp4}")
        return


def render_previews():
    preview_dir = Path(__file__).parent / "previews"
    preview_dir.mkdir(exist_ok=True)
    scenes = [Scene1_Hook, Scene2_Number, Scene3_Method,
              Scene4_Scandal, Scene5_Twist, Scene6_Punch]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, SC in enumerate(scenes):
        name = f"death_s2_scene_{i + 1}"
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

    scene_names = ["Scene1_Hook", "Scene2_Number", "Scene3_Method",
                   "Scene4_Scandal", "Scene5_Twist", "Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = output_dir / "tts_death_bureau_s2.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="death_s2", audio_path=str(audio))
    final = output_dir / "death_bureau_s2_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
    print(f"\n{'='*60}")
    print(f"  RENDER COMPLETE: {final}")
    print(f"  {mb:.1f} MB  |  {elapsed:.1f}s render time")
    print(f"{'='*60}")
