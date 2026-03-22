#!/usr/bin/env python3
"""Death Bureaucracy S1 — '30 People a Day' (Manim).

6 scenes, ~35.9s (32.9s audio + 3s hold). Kafkaesque bureaucratic aesthetic.

VTT cues (absolute → relative to scene start):
  Scene 1 (0.0–4.5s = 4.50s):
    0.120 (0.12) The US government accidentally kills 30 Americans every day.
  Scene 2 (4.5–7.5s = 3.00s):
    4.560 (0.06) Not with weapons.
    5.600 (1.10) With a single database entry.
  Scene 3 (7.5–13.2s = 5.70s):
    7.500 (0.00) Your bank account freezes.
    9.140 (1.64) Medicare disappears.
    10.400 (2.90) You cannot work.
    11.360 (3.86) You cannot fill a prescription.
  Scene 4 (13.2–20.7s = 7.50s):
    13.200 (0.00) In 2025,
    14.660 (1.46) an 82 year old got a condolence letter from his own bank.
    17.840 (4.64) He spent four months proving he was alive.
  Scene 5 (20.7–29.0s = 8.30s):
    20.680 (0.0)  To fix it?
    21.780 (1.08) Visit a government office.
    23.160 (2.46) Bring original ID. Wait four hours.
    25.700 (5.00) Then call every bank,
    27.000 (6.30) insurer,
    27.580 (6.88) and employer yourself.
  Scene 6 (29.0–35.9s = 6.90s):
    29.040 (0.04) 12,000 people a year.
    31.000 (2.00) And there is no system to undo it.
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

TTS_SCRIPT = """The US government accidentally kills 30 Americans every day.
Not with weapons.
With a single database entry.
Your bank account freezes.
Medicare disappears.
You cannot work.
You cannot fill a prescription.
In 2025,
an 82 year old got a condolence letter from his own bank.
He spent four months proving he was alive.
To fix it?
Visit a government office.
Bring original ID. Wait four hours.
Then call every bank,
insurer,
and employer yourself.
12,000 people a year.
And there is no system to undo it."""

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

# Palette — dark bureaucratic / Kafkaesque
BG = "#0A0E16"
BG2 = "#0E1320"
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

SAFE_W = 8.0


# ── Helpers ───────────────────────────────────────────────────

def gradient_bg(color1=BG, color2="#0D1424"):
    bg = Rectangle(width=12, height=20, fill_color=color1, fill_opacity=1, stroke_width=0)
    glow = Circle(radius=5, fill_color="#1A1A2E", fill_opacity=0.08, stroke_width=0).move_to(UP * 2)
    return VGroup(bg, glow)


def grid_lines(rows=12, cols=6, opacity=0.06):
    """Subtle bureaucratic grid overlay."""
    lines = VGroup()
    for i in range(rows + 1):
        y = -8 + i * 16 / rows
        lines.add(Line(LEFT * 5, RIGHT * 5, color=GRID, stroke_width=0.5).move_to(UP * y).set_opacity(opacity))
    for j in range(cols + 1):
        x = -4.5 + j * 9 / cols
        lines.add(Line(DOWN * 8, UP * 8, color=GRID, stroke_width=0.5).move_to(RIGHT * x).set_opacity(opacity))
    return lines


def form_field(label, value="", width=6, x=0, y=0, label_color=MUTED, value_color=WHITE_SOFT):
    """Database form field — bureaucratic aesthetic."""
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


def x_mark(size=0.3, color=RED, stroke_w=3):
    l1 = Line(UL * size/2, DR * size/2, color=color, stroke_width=stroke_w)
    l2 = Line(UR * size/2, DL * size/2, color=color, stroke_width=stroke_w)
    return VGroup(l1, l2)


def checkbox(checked=False, size=0.3, x=0, y=0):
    box = Square(side_length=size, stroke_color=FORM_BORDER, stroke_width=1.5,
                 fill_color=FORM_BG, fill_opacity=0.8)
    box.move_to(np.array([x, y, 0]))
    if checked:
        check = x_mark(size * 0.6, RED, 2.5).move_to(box)
        return VGroup(box, check)
    return VGroup(box)


# ================================================================
# SCENE 1: THE STAT (0.0–4.5s = 4.50s)
# VTT: 0.12 "The US government accidentally kills 30 Americans every day."
# Visual: Giant "30" counter, official seal feel, stark
# ================================================================
class Scene1_Stat(Scene):
    DURATION = 4.1
    def construct(self):
        self.add(gradient_bg(), grid_lines(opacity=0.04))
        t = 0

        pill = label_pill("DEATH BY BUREAUCRACY", color=RED, fs=24)
        pill.move_to(UP * 7)

        # Official-looking header bar
        header = Rectangle(width=9, height=0.08, fill_color=RED, fill_opacity=0.6, stroke_width=0)
        header.move_to(UP * 6.2)

        # Giant "30"
        big_30 = safe_text("30", font="Bebas Neue", font_size=220, color=RED)
        big_30.move_to(UP * 2.5)

        people = safe_text("AMERICANS", font="Inter", font_size=40, color=WHITE_SOFT, weight="BOLD")
        people.move_to(UP * 0.2)
        per_day = safe_text("EVERY SINGLE DAY", font="Inter", font_size=36, color=MUTED, weight="BOLD")
        per_day.move_to(DOWN * 0.8)

        div = section_div(5, RED).move_to(DOWN * 2)

        killed = safe_text("Accidentally killed", font="DM Serif Display",
                          font_size=44, color=WHITE_SOFT)
        killed.move_to(DOWN * 3.2)
        by_govt = safe_text("by their own government.", font="DM Serif Display",
                           font_size=40, color=MUTED)
        by_govt.move_to(DOWN * 4.3)

        # ── Timing: 4.50s ──
        self.add(header)
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(big_30, scale=1.3), run_time=0.7); t += 0.7
        self.play(Flash(big_30.get_center(), color=RED,
                        line_length=0.6, num_lines=12, run_time=0.3))      # t=1.4
        self.play(FadeIn(people), run_time=0.5); t += 0.5
        self.play(FadeIn(per_day, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(killed, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(by_govt, shift=UP * 0.06), run_time=0.6); t += 0.6
        target = getattr(self.__class__, 'DURATION', 4.1)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 2: THE METHOD (4.5–7.5s = 3.00s)
# VTT: 0.06 "Not with weapons." / 1.10 "With a single database entry."
# Visual: Crossed-out weapon → database terminal / form field
# ================================================================
class Scene2_Method(Scene):
    DURATION = 2.7
    def construct(self):
        self.add(gradient_bg(), grid_lines(opacity=0.04))
        t = 0

        pill = label_pill("THE METHOD", color=WARN, fs=28)
        pill.move_to(UP * 7)

        # "Not with weapons" — crossed out
        weapons = safe_text("WEAPONS", font="Bebas Neue", font_size=80, color=DEAD_GRAY)
        weapons.move_to(UP * 3.5)
        strike = Line(weapons.get_left() + LEFT * 0.2, weapons.get_right() + RIGHT * 0.2,
                      color=RED, stroke_width=4)
        strike.move_to(weapons)

        # "With a single database entry"
        div = section_div(5, WARN).move_to(UP * 1)

        db_label = safe_text("A SINGLE", font="Bebas Neue", font_size=60, color=WHITE_SOFT)
        db_label.move_to(DOWN * 0.5)
        db_entry = safe_text("DATABASE ENTRY.", font="Bebas Neue", font_size=80, color=RED)
        db_entry.move_to(DOWN * 2)

        # Simulated form field
        field = form_field("DMF STATUS", "DECEASED", width=5, x=0, y=-4, value_color=RED)

        # Terminal cursor blink effect
        cursor = Rectangle(width=0.08, height=0.35, fill_color=RED, fill_opacity=0.8, stroke_width=0)
        cursor.next_to(field[2], RIGHT, buff=0.05) if len(field) > 2 else cursor.move_to(DOWN * 4)

        # ── Timing: 3.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(weapons), run_time=0.3); t += 0.3
        self.play(Create(strike), run_time=0.2); t += 0.2

        # VTT 1.10: "With a single database entry."
        self.play(Create(div), run_time=0.2); t += 0.2
        self.play(FadeIn(db_label, shift=UP * 0.06), run_time=0.4); t += 0.4
        self.play(FadeIn(db_entry, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(db_entry.get_center(), color=RED,
                        line_length=0.3, num_lines=8, run_time=0.3))        # t=2.2
        self.play(FadeIn(field), FadeIn(cursor), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 2.7)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 3: THE CASCADE (7.5–13.2s = 5.70s)
# VTT: 0.00 "Your bank account freezes."
#      1.64 "Medicare disappears."
#      2.90 "You cannot work."
#      3.86 "You cannot fill a prescription."
# Visual: Rapid-fire consequences slamming in with X marks
# ================================================================
class Scene3_Cascade(Scene):
    DURATION = 5.2
    def construct(self):
        self.add(gradient_bg("#0A0A12"), grid_lines(opacity=0.05))
        t = 0

        pill = label_pill("THE CASCADE", color=RED, fs=28)
        pill.move_to(UP * 7)

        # Each consequence as a form-field-style row with X
        items = [
            ("BANK ACCOUNT", "FROZEN", UP * 4),
            ("MEDICARE", "TERMINATED", UP * 2),
            ("EMPLOYMENT", "DENIED", DOWN * 0),
            ("PRESCRIPTIONS", "BLOCKED", DOWN * 2),
        ]

        rows = []
        for label, status, pos in items:
            xm = x_mark(0.35, RED, 3).move_to(LEFT * 3.5 + pos)
            lbl = safe_text(label, font="Inter", font_size=32, color=WHITE_SOFT, weight="BOLD")
            lbl.move_to(LEFT * 1 + pos)
            stat = safe_text(status, font="Bebas Neue", font_size=50, color=RED)
            stat.move_to(RIGHT * 2.5 + pos)
            row_line = Line(LEFT * 4, RIGHT * 4, color=FORM_BORDER, stroke_width=1)
            row_line.move_to(pos + DOWN * 0.7)
            rows.append(VGroup(xm, lbl, stat, row_line))

        # Bottom payoff
        div = section_div(5, RED).move_to(DOWN * 4.5)
        dead_txt = safe_text("LEGALLY DEAD.", font="Bebas Neue", font_size=80, color=RED)
        dead_txt.move_to(DOWN * 5.8)
        alive_txt = safe_text("Physically alive.", font="DM Serif Display",
                             font_size=40, color=MUTED)
        alive_txt.move_to(DOWN * 7)

        # ── Timing: 5.70s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.00: "Your bank account freezes." (slam in)
        self.play(FadeIn(rows[0], shift=LEFT * 0.2), run_time=0.5); t += 0.5
        self.play(Flash(rows[0][0].get_center(), color=RED,
                        line_length=0.2, num_lines=6, run_time=0.2))        # t=1.0

        # VTT 1.64: "Medicare disappears."
        self.wait(0.34); t += 0.34
        self.play(FadeIn(rows[1], shift=LEFT * 0.2), run_time=0.5); t += 0.5

        # VTT 2.90: "You cannot work."
        self.wait(0.76); t += 0.76
        self.play(FadeIn(rows[2], shift=LEFT * 0.2), run_time=0.5); t += 0.5

        # VTT 3.86: "You cannot fill a prescription."
        self.wait(0.46); t += 0.46
        self.play(FadeIn(rows[3], shift=LEFT * 0.2), run_time=0.5); t += 0.5
        self.play(Flash(rows[3][0].get_center(), color=RED,
                        line_length=0.2, num_lines=6, run_time=0.2))        # t=4.26

        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(dead_txt, scale=1.1), run_time=0.5); t += 0.5
        self.play(FadeIn(alive_txt, shift=UP * 0.06), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 5.2)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 4: THE STORY (13.2–20.7s = 7.50s)
# VTT: 0.00 "In 2025,"
#      1.46 "an 82 year old got a condolence letter from his own bank."
#      4.64 "He spent four months proving he was alive."
# Visual: Date stamp, condolence letter mockup, "4 MONTHS"
# ================================================================
class Scene4_Story(Scene):
    DURATION = 6.9
    def construct(self):
        self.add(gradient_bg(), grid_lines(opacity=0.03))
        t = 0

        pill = label_pill("THE STORY", color=GOLD, fs=28)
        pill.move_to(UP * 7)

        # Date stamp
        date = safe_text("2025", font="Bebas Neue", font_size=120, color=GOLD)
        date.move_to(UP * 5)

        # Age
        age = safe_text("82 YEARS OLD", font="Inter", font_size=36, color=WHITE_SOFT, weight="BOLD")
        age.move_to(UP * 3.2)

        # Condolence letter mockup
        letter = RoundedRectangle(width=6, height=3.5, corner_radius=0.1,
                                  fill_color="#1A1A2A", fill_opacity=0.9,
                                  stroke_color=FORM_BORDER, stroke_width=1.5)
        letter.move_to(UP * 0.5)

        letter_head = safe_text("FIRST NATIONAL BANK", font="Inter", font_size=18, color=MUTED)
        letter_head.move_to(letter.get_top() + DOWN * 0.4)
        letter_line1 = safe_text("Dear Family of the Deceased,", font="DM Serif Display",
                                font_size=24, color=WHITE_SOFT)
        letter_line1.move_to(letter.get_center() + UP * 0.3)
        letter_line2 = safe_text("We are sorry for your loss.", font="DM Serif Display",
                                font_size=22, color=MUTED)
        letter_line2.move_to(letter.get_center() + DOWN * 0.3)
        condolence_label = safe_text("CONDOLENCE LETTER", font="Inter",
                                    font_size=20, color=RED, weight="BOLD")
        condolence_label.move_to(letter.get_bottom() + DOWN * 0.4)

        # "From his own bank."
        own_bank = safe_text("From his own bank.", font="DM Serif Display",
                            font_size=40, color=GOLD)
        own_bank.move_to(DOWN * 2.5)

        div = section_div(5, GOLD).move_to(DOWN * 3.5)

        # "4 MONTHS proving he was alive"
        four = safe_text("4 MONTHS", font="Bebas Neue", font_size=90, color=RED)
        four.move_to(DOWN * 5)
        proving = safe_text("proving he was alive.", font="DM Serif Display",
                           font_size=38, color=WHITE_SOFT)
        proving.move_to(DOWN * 6.3)

        # ── Timing: 7.50s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(date, scale=1.2), run_time=0.5); t += 0.5

        # VTT 1.46: "an 82 year old got a condolence letter..."
        self.wait(0.26); t += 0.26
        self.play(FadeIn(age), run_time=0.4); t += 0.4
        self.play(FadeIn(letter), FadeIn(letter_head), run_time=0.5); t += 0.5
        self.play(FadeIn(letter_line1, shift=UP * 0.04), run_time=0.4); t += 0.4
        self.play(FadeIn(letter_line2, shift=UP * 0.04), run_time=0.3); t += 0.3
        self.play(FadeIn(condolence_label), run_time=0.3); t += 0.3
        self.play(FadeIn(own_bank, shift=UP * 0.06), run_time=0.6); t += 0.6

        # VTT 4.64: "He spent four months proving he was alive."
        self.wait(0.64); t += 0.64
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(four, scale=1.15), run_time=0.7); t += 0.7
        self.play(Flash(four.get_center(), color=RED,
                        line_length=0.4, num_lines=8, run_time=0.3))        # t=5.60
        self.play(FadeIn(proving, shift=UP * 0.06), run_time=0.6); t += 0.6
        target = getattr(self.__class__, 'DURATION', 6.9)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 5: THE FIX (20.7–29.0s = 8.30s)
# VTT: 0.0 "To fix it?"
#      1.08 "Visit a government office."
#      2.46 "Bring original ID. Wait four hours."
#      5.00 "Then call every bank,"
#      6.30 "insurer,"
#      6.88 "and employer yourself."
# Visual: Checklist of nightmare steps
# ================================================================
class Scene5_Fix(Scene):
    DURATION = 7.6
    def construct(self):
        self.add(gradient_bg(), grid_lines(opacity=0.04))
        t = 0

        pill = label_pill("THE FIX", color=WARN, fs=28)
        pill.move_to(UP * 7)

        fix_q = safe_text("To fix it?", font="Bebas Neue", font_size=80, color=WHITE_SOFT)
        fix_q.move_to(UP * 5)

        # Checklist items — bureaucratic steps
        steps = [
            ("Visit a government office.", UP * 2.5),
            ("Bring original ID.", UP * 1.0),
            ("Wait four hours.", DOWN * 0.5),
            ("Call every bank.", DOWN * 2.0),
            ("Call every insurer.", DOWN * 3.5),
            ("Call every employer.", DOWN * 5.0),
        ]

        step_groups = []
        for txt, pos in steps:
            cb = checkbox(checked=False, size=0.3, x=-3.5, y=pos[1])
            lbl = safe_text(txt, font="Inter", font_size=32, color=WHITE_SOFT, weight="BOLD")
            lbl.move_to(RIGHT * 0 + pos)
            step_groups.append(VGroup(cb, lbl))

        # "Yourself." emphasis
        yourself = safe_text("YOURSELF.", font="Bebas Neue", font_size=70, color=RED)
        yourself.move_to(DOWN * 6.8)

        # ── Timing: 8.30s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(fix_q, scale=1.05), run_time=0.5); t += 0.5

        # VTT 1.08: "Visit a government office."
        self.play(FadeIn(step_groups[0], shift=LEFT * 0.1), run_time=0.4); t += 0.4

        # VTT 2.46: "Bring original ID. Wait four hours."
        self.wait(0.96); t += 0.96
        self.play(FadeIn(step_groups[1], shift=LEFT * 0.1), run_time=0.4); t += 0.4
        self.play(FadeIn(step_groups[2], shift=LEFT * 0.1), run_time=0.5); t += 0.5

        self.wait(1.64); t += 1.64

        # VTT 5.00: "Then call every bank,"
        self.play(FadeIn(step_groups[3], shift=LEFT * 0.1), run_time=0.5); t += 0.5

        # VTT 6.30: "insurer,"
        self.wait(0.8); t += 0.8
        self.play(FadeIn(step_groups[4], shift=LEFT * 0.1), run_time=0.4); t += 0.4

        # VTT 6.88: "and employer yourself."
        self.wait(0.18); t += 0.18
        self.play(FadeIn(step_groups[5], shift=LEFT * 0.1), run_time=0.4); t += 0.4
        self.play(FadeIn(yourself, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(yourself.get_center(), color=RED,
                        line_length=0.3, num_lines=8, run_time=0.3))        # t=7.78
        target = getattr(self.__class__, 'DURATION', 7.6)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 6: THE PUNCH (29.0–35.9s = 6.90s)
# VTT: 0.04 "12,000 people a year."
#      2.00 "And there is no system to undo it."
# + 3s hold + fade to black
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 6.3
    def construct(self):
        self.add(gradient_bg())
        t = 0

        # Letterbox
        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP * (8 - bh / 2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN * (8 - bh / 2)),
        )

        # Ghost grid
        ghost_grid = grid_lines(opacity=0.03)
        self.add(ghost_grid)

        div1 = section_div(4, RED).move_to(UP * 1)

        big_num = safe_text("12,000", font="Bebas Neue", font_size=120, color=RED)
        big_num.move_to(DOWN * 0.5)
        ppl = safe_text("people a year.", font="DM Serif Display",
                       font_size=42, color=WHITE_SOFT)
        ppl.move_to(DOWN * 2)

        div2 = section_div(4, MUTED).move_to(DOWN * 3.2)

        no_sys = safe_text("No system to undo it.", font="DM Serif Display",
                          font_size=40, color=MUTED)
        no_sys.move_to(DOWN * 4.5)

        # ── Timing: 6.90s ──
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(big_num, scale=1.2), run_time=0.7); t += 0.7
        self.play(Flash(big_num.get_center(), color=RED,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=1.3
        self.play(FadeIn(ppl, shift=UP * 0.06), run_time=0.5); t += 0.5

        # VTT 2.00: "And there is no system to undo it."
        self.play(Create(div2), run_time=0.2); t += 0.2
        self.play(FadeIn(no_sys, shift=UP * 0.06), run_time=0.8); t += 0.8

        # 3s hold + fade
        target = getattr(self.__class__, 'DURATION', 6.3)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5


# ── Per-scene render ──────────────────────────────────────────
def render_single_scene(scene_idx):
    scene_classes = [Scene1_Stat, Scene2_Method, Scene3_Cascade,
                     Scene4_Story, Scene5_Fix, Scene6_Punch]
    SC = scene_classes[scene_idx]
    output_dir = Path(__file__).parent
    config.output_file = f"death_s1_scene_{scene_idx + 1}"
    config.media_dir = str(output_dir / "media")
    SC().render()
    for mp4 in Path(config.media_dir).rglob(f"death_s1_scene_{scene_idx + 1}.mp4"):
        print(f"SCENE_FILE:{mp4}")
        return


# ── Preview mode ──────────────────────────────────────────────
def render_previews():
    preview_dir = Path(__file__).parent / "previews"
    preview_dir.mkdir(exist_ok=True)
    scenes = [Scene1_Stat, Scene2_Method, Scene3_Cascade,
              Scene4_Story, Scene5_Fix, Scene6_Punch]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, SC in enumerate(scenes):
        name = f"death_s1_scene_{i + 1}"
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


# ── MAIN ──────────────────────────────────────────────────────
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

    scene_names = ["Scene1_Stat", "Scene2_Method", "Scene3_Cascade",
                   "Scene4_Story", "Scene5_Fix", "Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = output_dir / "tts_death_bureau_s1.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="death_s1", audio_path=str(audio))
    final = output_dir / "death_bureau_s1_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
    print(f"\n{'='*60}")
    print(f"  RENDER COMPLETE: {final}")
    print(f"  {mb:.1f} MB  |  {elapsed:.1f}s render time")
    print(f"{'='*60}")
