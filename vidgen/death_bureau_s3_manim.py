#!/usr/bin/env python3
"""Death Bureaucracy S3 — '50 Fields to Summarize a Life' (Manim).

6 scenes, ~41.7s (38.7s audio + 3s hold). Existential, form-aesthetic.

VTT cues (absolute → relative to scene start):
  Scene 1 (0.0–5.9s = 5.90s):
    0.180 (0.18) When you die,
    1.440 (1.44) the US government reduces your entire life to 50 boxes on a form.
  Scene 2 (5.9–11.9s = 6.00s):
    5.940 (0.04) It asks your Social Security Number.
    8.420 (2.52) Your occupation.
    9.420 (3.52) Your parents names.
    10.640 (4.74) How you died.
  Scene 3 (11.9–17.5s = 5.60s):
    11.960 (0.06) It does not ask what you believed.
    13.880 (1.98) Who you loved.
    14.920 (3.02) What you created.
    16.100 (4.20) Or what you feared.
  Scene 4 (17.5–25.7s = 8.20s):
    17.500 (0.00) That form is the key to everything.
    19.660 (2.16) Without it, no bank releases a dollar.
    22.540 (5.04) No insurance pays out.
    24.120 (6.62) No property transfers.
  Scene 5 (25.7–32.0s = 6.30s):
    25.720 (0.02) Families need 8 to 15 copies.
    27.880 (2.18) At up to 30 dollars each.
    29.880 (4.18) Every institution demands its own.
  Scene 6 (32.0–41.7s = 9.70s):
    32.000 (0.00) The form captures exactly what the state valued about you.
    34.960 (2.96) And in everything it does not ask,
    36.920 (4.92) lies everything you actually were.
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

TTS_SCRIPT = """When you die,
the US government reduces your entire life to 50 boxes on a form.
It asks your Social Security Number.
Your occupation.
Your parents names.
How you died.
It does not ask what you believed.
Who you loved.
What you created.
Or what you feared.
That form is the key to everything.
Without it, no bank releases a dollar.
No insurance pays out.
No property transfers.
Families need 8 to 15 copies.
At up to 30 dollars each.
Every institution demands its own.
The form captures exactly what the state valued about you.
And in everything it does not ask,
lies everything you actually were."""

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

# Palette
BG = "#0A0E16"
SURFACE = "#141C2B"
SURFACE2 = "#1A2538"
BORDER = "#2A3A50"
GRID = "#1A2030"
RED = "#E63946"
GOLD = "#FFD700"
GOLD_DIM = "#B8960F"
WHITE_SOFT = "#F0F0F0"
MUTED = "#7B8DA0"
TEAL = "#2EC4B6"
WARN = "#FF6B35"
DEAD_GRAY = "#4A5568"
FORM_BG = "#111827"
FORM_BORDER = "#374151"
FORM_LABEL = "#6B7280"
HUMAN = "#A78BFA"  # soft violet for human/emotional elements

SAFE_W = 8.0


# ── Helpers ───────────────────────────────────────────────────

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


def form_row(label, value="", y=0, filled=True, label_color=FORM_LABEL,
             value_color=WHITE_SOFT, width=7):
    """Single form field row — label above, box with value below."""
    lbl = Text(label, font="Inter", font_size=18, color=label_color)
    lbl.move_to(LEFT * (width / 2 - lbl.width / 2 - 0.1) + UP * 0.18 + UP * y)
    box = Rectangle(width=width, height=0.55, fill_color=FORM_BG, fill_opacity=0.9,
                    stroke_color=FORM_BORDER, stroke_width=1)
    box.move_to(UP * (y - 0.2))
    if value and filled:
        val = Text(value, font="Inter", font_size=24, color=value_color)
        if val.width > width - 0.4:
            val.scale((width - 0.4) / val.width)
        val.move_to(box.get_center())
        return VGroup(box, lbl, val)
    return VGroup(box, lbl)


def form_row_empty(label, y=0, width=7):
    """Empty/greyed form field — the absence is the visual."""
    lbl = Text(label, font="Inter", font_size=18, color=DEAD_GRAY)
    lbl.move_to(LEFT * (width / 2 - lbl.width / 2 - 0.1) + UP * 0.18 + UP * y)
    box = Rectangle(width=width, height=0.55, fill_color="#080C14", fill_opacity=0.9,
                    stroke_color="#1F2937", stroke_width=1,
                    stroke_opacity=0.5)
    box.move_to(UP * (y - 0.2))
    # Dashed placeholder
    dash = DashedLine(LEFT * 2.5, RIGHT * 2.5, color="#1F2937",
                      stroke_width=1, dash_length=0.15)
    dash.move_to(box.get_center())
    return VGroup(box, lbl, dash)


# ================================================================
# SCENE 1: THE HOOK (0.0–5.9s = 5.90s)
# VTT: 0.18 "When you die," / 1.44 "...50 boxes on a form."
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 5.5
    def construct(self):
        self.add(gradient_bg(), grid_lines(opacity=0.04))
        t = 0

        pill = label_pill("DEATH CERTIFICATE", color=MUTED, fs=24)
        pill.move_to(UP * 7)

        header = Rectangle(width=9, height=0.08, fill_color=MUTED,
                           fill_opacity=0.4, stroke_width=0)
        header.move_to(UP * 6.2)

        when = safe_text("When you die,", font="DM Serif Display",
                        font_size=50, color=WHITE_SOFT)
        when.move_to(UP * 4)

        govt = safe_text("the government reduces", font="DM Serif Display",
                        font_size=42, color=MUTED)
        govt.move_to(UP * 2.5)
        life = safe_text("your entire life", font="DM Serif Display",
                        font_size=46, color=WHITE_SOFT)
        life.move_to(UP * 1.4)

        div = section_div(5, MUTED).move_to(UP * 0.2)

        big_50 = safe_text("50", font="Bebas Neue", font_size=200, color=GOLD)
        big_50.move_to(DOWN * 2.5)
        boxes = safe_text("BOXES ON A FORM", font="Inter", font_size=36,
                         color=WHITE_SOFT, weight="BOLD")
        boxes.move_to(DOWN * 4.5)

        # Mini form preview — faint grid of boxes
        mini_grid = VGroup()
        for r in range(5):
            for c in range(5):
                b = Rectangle(width=1.0, height=0.35, fill_color=FORM_BG,
                              fill_opacity=0.4, stroke_color=FORM_BORDER,
                              stroke_width=0.5)
                b.move_to(LEFT * 2 + RIGHT * c * 1.1 + DOWN * 5.5 + DOWN * r * 0.45)
                mini_grid.add(b)

        # ── Timing: 5.90s ──
        self.add(header)
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(when, shift=UP * 0.06), run_time=0.6); t += 0.6

        # VTT 1.44: "the US government reduces..."
        self.play(FadeIn(govt, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(FadeIn(life, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(big_50, scale=1.3), run_time=0.7); t += 0.7
        self.play(Flash(big_50.get_center(), color=GOLD,
                        line_length=0.6, num_lines=12, run_time=0.3))      # t=3.3
        self.play(FadeIn(boxes), run_time=0.5); t += 0.5
        self.play(
            LaggedStart(*[FadeIn(b) for b in mini_grid], lag_ratio=0.01),
            run_time=0.6,
        )                                                                   # t=4.4
        target = getattr(self.__class__, 'DURATION', 5.5)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 2: WHAT IT ASKS (5.9–11.9s = 6.00s)
# VTT: 0.04 "It asks your Social Security Number."
#      2.52 "Your occupation."
#      3.52 "Your parents names."
#      4.74 "How you died."
# Visual: Form fields filling in one by one — metronomic
# ================================================================
class Scene2_WhatItAsks(Scene):
    DURATION = 5.6
    def construct(self):
        self.add(gradient_bg(), grid_lines(opacity=0.05))
        t = 0

        pill = label_pill("WHAT IT ASKS", color=WHITE_SOFT, fs=28)
        pill.move_to(UP * 7)

        # Form header
        form_title = safe_text("U.S. STANDARD CERTIFICATE OF DEATH",
                              font="Inter", font_size=22, color=MUTED, weight="BOLD")
        form_title.move_to(UP * 5.5)
        form_line = Line(LEFT * 3.5, RIGHT * 3.5, color=FORM_BORDER, stroke_width=1)
        form_line.move_to(UP * 5.1)

        # Fields that appear one by one
        f1 = form_row("SOCIAL SECURITY NUMBER", "XXX-XX-XXXX", y=4, value_color=WHITE_SOFT)
        f2 = form_row("OCCUPATION", "________________", y=2.5, value_color=MUTED)
        f3 = form_row("PARENTS' NAMES", "________________", y=1, value_color=MUTED)
        f4 = form_row("CAUSE OF DEATH", "________________", y=-0.5, value_color=RED)

        div = section_div(5, MUTED).move_to(DOWN * 2.2)

        asked = safe_text("Data points.", font="Bebas Neue", font_size=70, color=MUTED)
        asked.move_to(DOWN * 3.5)
        nothing = safe_text("Nothing more.", font="DM Serif Display",
                           font_size=40, color=DEAD_GRAY)
        nothing.move_to(DOWN * 4.8)

        # ── Timing: 6.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.add(form_title, form_line)

        # VTT 0.04: "It asks your Social Security Number."
        self.play(FadeIn(f1, shift=LEFT * 0.1), run_time=0.6); t += 0.6
        self.wait(1.32); t += 1.32

        # VTT 2.52: "Your occupation."
        self.play(FadeIn(f2, shift=LEFT * 0.1), run_time=0.5); t += 0.5

        # VTT 3.52: "Your parents names."
        self.wait(0.5); t += 0.5
        self.play(FadeIn(f3, shift=LEFT * 0.1), run_time=0.5); t += 0.5

        # VTT 4.74: "How you died."
        self.wait(0.72); t += 0.72
        self.play(FadeIn(f4, shift=LEFT * 0.1), run_time=0.5); t += 0.5

        self.play(Create(div), run_time=0.2); t += 0.2
        self.play(FadeIn(asked), run_time=0.4); t += 0.4
        self.play(FadeIn(nothing, shift=UP * 0.04), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 5.6)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 3: WHAT IT SKIPS (11.9–17.5s = 5.60s)
# VTT: 0.06 "It does not ask what you believed."
#      1.98 "Who you loved."
#      3.02 "What you created."
#      4.20 "Or what you feared."
# Visual: Empty/greyed form fields — the absence IS the visual
# ================================================================
class Scene3_WhatItSkips(Scene):
    DURATION = 5.2
    def construct(self):
        self.add(gradient_bg("#080A10"), grid_lines(opacity=0.03))
        t = 0

        pill = label_pill("WHAT IT SKIPS", color=HUMAN, fs=28)
        pill.move_to(UP * 7)

        not_ask = safe_text("It does not ask.", font="DM Serif Display",
                           font_size=46, color=HUMAN)
        not_ask.move_to(UP * 5)

        # Empty form fields — greyed, ghostly
        f1 = form_row_empty("WHAT YOU BELIEVED", y=3)
        f2 = form_row_empty("WHO YOU LOVED", y=1.5)
        f3 = form_row_empty("WHAT YOU CREATED", y=0)
        f4 = form_row_empty("WHAT YOU FEARED", y=-1.5)

        div = section_div(5, HUMAN).move_to(DOWN * 3.5)

        absent = safe_text("ABSENT.", font="Bebas Neue", font_size=80, color=HUMAN)
        absent.move_to(DOWN * 5)
        from_form = safe_text("From every form.", font="DM Serif Display",
                             font_size=38, color=DEAD_GRAY)
        from_form.move_to(DOWN * 6.3)

        # ── Timing: 5.60s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(not_ask, shift=UP * 0.06), run_time=0.4); t += 0.4

        # VTT 0.06: "...what you believed."
        self.play(FadeIn(f1, shift=DOWN * 0.05), run_time=0.5); t += 0.5
        self.wait(0.48); t += 0.48

        # VTT 1.98: "Who you loved."
        self.play(FadeIn(f2, shift=DOWN * 0.05), run_time=0.5); t += 0.5
        self.wait(0.54); t += 0.54

        # VTT 3.02: "What you created."
        self.play(FadeIn(f3, shift=DOWN * 0.05), run_time=0.5); t += 0.5
        self.wait(0.68); t += 0.68

        # VTT 4.20: "Or what you feared."
        self.play(FadeIn(f4, shift=DOWN * 0.05), run_time=0.5); t += 0.5
        self.play(Create(div), run_time=0.2); t += 0.2
        self.play(FadeIn(absent, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(from_form, shift=UP * 0.04), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 5.2)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 4: THE KEY (17.5–25.7s = 8.20s)
# VTT: 0.00 "That form is the key to everything."
#      2.16 "Without it, no bank releases a dollar."
#      5.04 "No insurance pays out."
#      6.62 "No property transfers."
# ================================================================
class Scene4_Key(Scene):
    DURATION = 7.6
    def construct(self):
        self.add(gradient_bg(), grid_lines(opacity=0.04))
        t = 0

        pill = label_pill("THE KEY", color=GOLD, fs=28)
        pill.move_to(UP * 7)

        key_txt = safe_text("THE KEY", font="Bebas Neue", font_size=90, color=GOLD)
        key_txt.move_to(UP * 4.5)
        to_every = safe_text("to everything.", font="DM Serif Display",
                            font_size=46, color=WHITE_SOFT)
        to_every.move_to(UP * 3)

        # Locked doors — each institution blocked
        items = [
            ("NO BANK", "releases a dollar.", DOWN * 0.5, RED),
            ("NO INSURANCE", "pays out.", DOWN * 2.2, RED),
            ("NO PROPERTY", "transfers.", DOWN * 3.9, RED),
        ]
        blocked = []
        for title, sub, pos, col in items:
            lbl = safe_text(title, font="Bebas Neue", font_size=60, color=col)
            lbl.move_to(pos)
            s = safe_text(sub, font="DM Serif Display", font_size=34, color=MUTED)
            s.move_to(pos + DOWN * 0.8)
            blocked.append(VGroup(lbl, s))

        div = section_div(5, RED).move_to(DOWN * 5.5)
        without = safe_text("Without the form.", font="DM Serif Display",
                           font_size=40, color=DEAD_GRAY)
        without.move_to(DOWN * 6.5)

        # ── Timing: 8.20s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(key_txt, scale=1.1), run_time=0.6); t += 0.6
        self.play(Flash(key_txt.get_center(), color=GOLD,
                        line_length=0.4, num_lines=8, run_time=0.3))        # t=1.2
        self.play(FadeIn(to_every, shift=UP * 0.06), run_time=0.5); t += 0.5

        # VTT 2.16: "Without it, no bank releases a dollar."
        self.wait(0.16); t += 0.16
        self.play(FadeIn(blocked[0], shift=LEFT * 0.1), run_time=0.6); t += 0.6
        self.play(Flash(blocked[0][0].get_center(), color=RED,
                        line_length=0.2, num_lines=6, run_time=0.2))        # t=2.66

        self.wait(2.08); t += 2.08

        # VTT 5.04: "No insurance pays out."
        self.play(FadeIn(blocked[1], shift=LEFT * 0.1), run_time=0.6); t += 0.6

        # VTT 6.62: "No property transfers."
        self.wait(0.98); t += 0.98
        self.play(FadeIn(blocked[2], shift=LEFT * 0.1), run_time=0.6); t += 0.6
        self.play(Create(div), run_time=0.2); t += 0.2
        self.play(FadeIn(without, shift=UP * 0.04), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 7.6)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 5: THE COST (25.7–32.0s = 6.30s)
# VTT: 0.02 "Families need 8 to 15 copies."
#      2.18 "At up to 30 dollars each."
#      4.18 "Every institution demands its own."
# ================================================================
class Scene5_Cost(Scene):
    DURATION = 5.9
    def construct(self):
        self.add(gradient_bg(), grid_lines(opacity=0.04))
        t = 0

        pill = label_pill("THE COST", color=WARN, fs=28)
        pill.move_to(UP * 7)

        # Stacked copies — visual of multiple forms
        copies = VGroup()
        for i in range(6):
            sheet = Rectangle(width=4.5, height=6, fill_color=FORM_BG,
                              fill_opacity=0.7 - i * 0.08,
                              stroke_color=FORM_BORDER, stroke_width=1)
            sheet.move_to(UP * 2 + RIGHT * i * 0.12 + DOWN * i * 0.12)
            copies.add(sheet)

        # Numbers overlay
        range_txt = safe_text("8–15", font="Bebas Neue", font_size=120, color=GOLD)
        range_txt.move_to(UP * 2.5)
        copies_lbl = safe_text("COPIES NEEDED", font="Inter", font_size=32,
                              color=WHITE_SOFT, weight="BOLD")
        copies_lbl.move_to(UP * 0.8)

        div = section_div(5, WARN).move_to(DOWN * 0.5)

        price = safe_text("$30", font="Bebas Neue", font_size=100, color=RED)
        price.move_to(DOWN * 2)
        each = safe_text("EACH.", font="Inter", font_size=36, color=WHITE_SOFT, weight="BOLD")
        each.move_to(DOWN * 3.2)

        # Total
        total = safe_text("Up to $450 to prove someone died.", font="DM Serif Display",
                         font_size=34, color=MUTED)
        total.move_to(DOWN * 4.5)

        div2 = section_div(5, MUTED).move_to(DOWN * 5.5)
        demands = safe_text("Every institution demands its own.", font="DM Serif Display",
                           font_size=36, color=DEAD_GRAY)
        demands.move_to(DOWN * 6.5)

        # ── Timing: 6.30s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.02: "Families need 8 to 15 copies."
        self.play(
            LaggedStart(*[FadeIn(c) for c in copies], lag_ratio=0.04),
            run_time=0.5,
        )                                                                   # t=0.8
        self.play(FadeIn(range_txt, scale=1.2), run_time=0.6); t += 0.6
        self.play(FadeIn(copies_lbl), run_time=0.3); t += 0.3

        # VTT 2.18: "At up to 30 dollars each."
        self.wait(0.18); t += 0.18
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(price, scale=1.15), run_time=0.6); t += 0.6
        self.play(Flash(price.get_center(), color=RED,
                        line_length=0.3, num_lines=8, run_time=0.3))        # t=3.08
        self.play(FadeIn(each), run_time=0.3); t += 0.3
        self.play(FadeIn(total, shift=UP * 0.04), run_time=0.5); t += 0.5

        # VTT 4.18: "Every institution demands its own."
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(demands, shift=UP * 0.04), run_time=0.6); t += 0.6
        target = getattr(self.__class__, 'DURATION', 5.9)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 6: THE PUNCH (32.0–41.7s = 9.70s)
# VTT: 0.00 "The form captures exactly what the state valued about you."
#      2.96 "And in everything it does not ask,"
#      4.92 "lies everything you actually were."
# + 3s hold + fade
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 9.0
    def construct(self):
        self.add(gradient_bg("#060810"))
        t = 0

        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP * (8 - bh / 2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN * (8 - bh / 2)),
        )
        self.add(grid_lines(opacity=0.02))

        # First part — what the state valued
        div1 = section_div(4, MUTED).move_to(UP * 2)

        state1 = safe_text("The form captures exactly", font="DM Serif Display",
                          font_size=38, color=MUTED)
        state1.move_to(UP * 0.8)
        state2 = safe_text("what the state valued", font="DM Serif Display",
                          font_size=40, color=MUTED)
        state2.move_to(DOWN * 0.2)
        state3 = safe_text("about you.", font="DM Serif Display",
                          font_size=42, color=WHITE_SOFT)
        state3.move_to(DOWN * 1.2)

        # Second part — the flip
        div2 = section_div(4, HUMAN).move_to(DOWN * 2.5)

        flip1 = safe_text("And in everything it does not ask,", font="DM Serif Display",
                          font_size=34, color=MUTED)
        flip1.move_to(DOWN * 3.7)

        # The closer
        flip2 = safe_text("lies everything", font="DM Serif Display",
                         font_size=44, color=WHITE_SOFT)
        flip2.move_to(DOWN * 5)
        flip3 = safe_text("you actually were.", font="Bebas Neue",
                         font_size=70, color=HUMAN)
        flip3.move_to(DOWN * 6.2)

        glow = Circle(radius=2.5, fill_color=HUMAN, fill_opacity=0.04, stroke_width=0)
        glow.move_to(flip3)

        # ── Timing: 9.70s ──
        # VTT 0.00: "The form captures exactly what the state valued about you."
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(state1, shift=UP * 0.08), run_time=0.7); t += 0.7
        self.play(FadeIn(state2, shift=UP * 0.08), run_time=0.7); t += 0.7
        self.play(FadeIn(state3, shift=UP * 0.08), run_time=0.7); t += 0.7

        # VTT 2.96: "And in everything it does not ask,"
        self.wait(0.26); t += 0.26
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(flip1, shift=UP * 0.06), run_time=0.8); t += 0.8

        # VTT 4.92: "lies everything you actually were."
        self.wait(0.86); t += 0.86
        self.play(FadeIn(flip2, shift=UP * 0.08), run_time=0.6); t += 0.6
        self.play(FadeIn(glow), FadeIn(flip3, scale=1.08), run_time=0.9); t += 0.9

        # 3s hold + fade
        target = getattr(self.__class__, 'DURATION', 9.0)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK,
                          fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5


# ── Per-scene render ──────────────────────────────────────────
def render_single_scene(scene_idx):
    scene_classes = [Scene1_Hook, Scene2_WhatItAsks, Scene3_WhatItSkips,
                     Scene4_Key, Scene5_Cost, Scene6_Punch]
    SC = scene_classes[scene_idx]
    output_dir = Path(__file__).parent
    config.output_file = f"death_s3_scene_{scene_idx + 1}"
    config.media_dir = str(output_dir / "media")
    SC().render()
    for mp4 in Path(config.media_dir).rglob(f"death_s3_scene_{scene_idx + 1}.mp4"):
        print(f"SCENE_FILE:{mp4}")
        return


def render_previews():
    preview_dir = Path(__file__).parent / "previews"
    preview_dir.mkdir(exist_ok=True)
    scenes = [Scene1_Hook, Scene2_WhatItAsks, Scene3_WhatItSkips,
              Scene4_Key, Scene5_Cost, Scene6_Punch]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, SC in enumerate(scenes):
        name = f"death_s3_scene_{i + 1}"
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

    scene_names = ["Scene1_Hook", "Scene2_WhatItAsks", "Scene3_WhatItSkips",
                   "Scene4_Key", "Scene5_Cost", "Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = output_dir / "tts_death_bureau_s3.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="death_s3", audio_path=str(audio))
    final = output_dir / "death_bureau_s3_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
    print(f"\n{'='*60}")
    print(f"  RENDER COMPLETE: {final}")
    print(f"  {mb:.1f} MB  |  {elapsed:.1f}s render time")
    print(f"{'='*60}")
