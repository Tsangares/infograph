#!/usr/bin/env python3
"""Death Bureaucracy S4 — '$255 Since Eisenhower' (Manim).

6 scenes, ~37.9s (34.9s audio + 3s hold). Bureaucratic absurdity, time decay.

VTT cues (absolute → relative to scene start):
  Scene 1 (0.0–4.6s = 4.60s):
    0.160 (0.16) When you die,
    1.240 (1.24) the US government sends your family 255 dollars.
    4.640 (4.64) That is it.   [straddles boundary — "That is it" lands at scene end]
  Scene 2 (4.6–10.5s = 5.90s):
    5.620 (1.02) That number has not changed since 1954. Eisenhower was president.
  Scene 3 (10.5–17.2s = 6.70s):
    10.560 (0.06) But if you die on March 2nd?
    12.320 (1.82) Your family owes back the entire March Social Security payment.
    16.080 (5.58) No prorating.
  Scene 4 (17.2–23.9s = 6.70s):
    17.220 (0.02) Then comes probate.
    18.500 (1.30) Average: 20 months.
    19.940 (2.74) Cost:
    20.840 (3.64) 3 to 7 percent of everything you ever owned.
  Scene 5 (23.9–29.6s = 5.70s):
    23.900 (0.00) Benefits terminate in days.
    27.240 (3.34) Taxes persist for months.
    27.560 (3.66) The estate drags on for years.
  Scene 6 (29.6–37.9s = 8.30s):
    29.660 (0.06) What gets processed fastest is what costs them money.
    32.800 (3.20) What costs you?
    33.960 (4.36) That takes forever.
    + 3s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """When you die,
the US government sends your family 255 dollars.
That is it.   [straddles boundary — "That is it" lands at scene end]
That number has not changed since 1954. Eisenhower was president.
But if you die on March 2nd?
Your family owes back the entire March Social Security payment.
No prorating.
Then comes probate.
Average: 20 months.
Cost:
3 to 7 percent of everything you ever owned.
Benefits terminate in days.
Taxes persist for months.
The estate drags on for years.
What gets processed fastest is what costs them money.
What costs you?
That takes forever."""

from manim import (
    Scene, Text, VGroup, Rectangle, RoundedRectangle, Circle,
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
config.background_color = "#0A0E16"
config.disable_caching = True

BG = "#0A0E16"; SURFACE = "#141C2B"; SURFACE2 = "#1A2538"; BORDER = "#2A3A50"
GRID = "#1A2030"; RED = "#E63946"; GOLD = "#FFD700"; GOLD_DIM = "#B8960F"
WHITE_SOFT = "#F0F0F0"; MUTED = "#7B8DA0"; TEAL = "#2EC4B6"; WARN = "#FF6B35"
DEAD_GRAY = "#4A5568"; FORM_BG = "#111827"; FORM_BORDER = "#374151"
SAFE_W = 8.0


def gradient_bg(c=BG, g="#1A1A2E"):
    bg = Rectangle(width=12, height=20, fill_color=c, fill_opacity=1, stroke_width=0)
    glow = Circle(radius=5, fill_color=g, fill_opacity=0.08, stroke_width=0).move_to(UP * 2)
    return VGroup(bg, glow)

def grid_lines(rows=12, cols=6, opacity=0.06):
    lines = VGroup()
    for i in range(rows+1):
        y = -8 + i*16/rows
        lines.add(Line(LEFT*5, RIGHT*5, color=GRID, stroke_width=0.5).move_to(UP*y).set_opacity(opacity))
    for j in range(cols+1):
        x = -4.5 + j*9/cols
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


# ================================================================
# SCENE 1: THE HOOK (0.0–4.6s = 4.60s)
# "$255. That's it."
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 4.2
    def construct(self):
        self.add(gradient_bg(), grid_lines(opacity=0.04))
        t = 0

        pill = label_pill("DEATH BENEFIT", color=MUTED, fs=24)
        pill.move_to(UP * 7)
        header = Rectangle(width=9, height=0.08, fill_color=MUTED, fill_opacity=0.4, stroke_width=0)
        header.move_to(UP * 6.2)

        when = safe_text("When you die,", font="DM Serif Display", font_size=50, color=WHITE_SOFT)
        when.move_to(UP * 4)
        govt = safe_text("the government sends", font="DM Serif Display", font_size=42, color=MUTED)
        govt.move_to(UP * 2.8)
        family = safe_text("your family", font="DM Serif Display", font_size=42, color=MUTED)
        family.move_to(UP * 1.8)

        div = section_div(5, GOLD).move_to(UP * 0.5)

        big_255 = safe_text("$255", font="Bebas Neue", font_size=220, color=GOLD)
        big_255.move_to(DOWN * 2.5)

        thats_it = safe_text("THAT'S IT.", font="Bebas Neue", font_size=70, color=RED)
        thats_it.move_to(DOWN * 5)

        # ── Timing: 4.60s ──
        self.add(header)
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(when, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(FadeIn(govt, shift=UP * 0.06), run_time=0.4); t += 0.4
        self.play(FadeIn(family, shift=UP * 0.06), run_time=0.4); t += 0.4
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(big_255, scale=1.3), run_time=0.7); t += 0.7
        self.play(Flash(big_255.get_center(), color=GOLD,
                        line_length=0.6, num_lines=12, run_time=0.3))      # t=2.9
        self.wait(0.7); t += 0.7
        self.play(FadeIn(thats_it, scale=1.15), run_time=0.5); t += 0.5
        self.play(Flash(thats_it.get_center(), color=RED,
                        line_length=0.3, num_lines=8, run_time=0.3))        # t=4.4
        target = getattr(self.__class__, 'DURATION', 4.2)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 2: THE FREEZE (4.6–10.5s = 5.90s)
# "That number has not changed since 1954. Eisenhower was president."
# ================================================================
class Scene2_Freeze(Scene):
    DURATION = 5.4
    def construct(self):
        self.add(gradient_bg(), grid_lines(opacity=0.04))
        t = 0

        pill = label_pill("THE FREEZE", color=WARN, fs=28)
        pill.move_to(UP * 7)

        # Timeline 1954 → 2026
        tl = Line(LEFT * 3.5, RIGHT * 3.5, color=MUTED, stroke_width=2.5)
        tl.move_to(UP * 3.5)

        tick_54 = Line(UP * 0.2, DOWN * 0.2, color=GOLD, stroke_width=2.5)
        tick_54.move_to(tl.get_center() + LEFT * 3)
        lbl_54 = safe_text("1954", font="Bebas Neue", font_size=40, color=GOLD)
        lbl_54.next_to(tick_54, DOWN, buff=0.2)

        tick_26 = Line(UP * 0.2, DOWN * 0.2, color=RED, stroke_width=2.5)
        tick_26.move_to(tl.get_center() + RIGHT * 3)
        lbl_26 = safe_text("2026", font="Bebas Neue", font_size=40, color=RED)
        lbl_26.next_to(tick_26, DOWN, buff=0.2)

        # Frozen bar spanning entire timeline
        freeze_bar = Rectangle(width=6.0, height=0.4, fill_color=WARN, fill_opacity=0.2,
                               stroke_color=WARN, stroke_width=1.5)
        freeze_bar.move_to(tl.get_center() + UP * 0.6)
        freeze_lbl = safe_text("$255 — UNCHANGED", font="Inter", font_size=22,
                              color=WARN, weight="BOLD")
        freeze_lbl.next_to(freeze_bar, UP, buff=0.1)

        # "72 YEARS"
        years_72 = safe_text("72 YEARS", font="Bebas Neue", font_size=100, color=RED)
        years_72.move_to(DOWN * 0.5)
        frozen = safe_text("FROZEN.", font="Bebas Neue", font_size=80, color=RED)
        frozen.move_to(DOWN * 1.8)

        div = section_div(5, MUTED).move_to(DOWN * 3.2)

        ike = safe_text("EISENHOWER", font="Bebas Neue", font_size=70, color=MUTED)
        ike.move_to(DOWN * 4.5)
        was_pres = safe_text("was president.", font="DM Serif Display", font_size=40, color=DEAD_GRAY)
        was_pres.move_to(DOWN * 5.7)

        # ── Timing: 5.90s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(Create(tl), run_time=0.3); t += 0.3
        self.play(FadeIn(tick_54), FadeIn(lbl_54),
                  FadeIn(tick_26), FadeIn(lbl_26), run_time=0.4)          # t=1.0
        self.play(FadeIn(freeze_bar), FadeIn(freeze_lbl), run_time=0.5); t += 0.5
        self.play(FadeIn(years_72, scale=1.2), run_time=0.6); t += 0.6
        self.play(FadeIn(frozen, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(years_72.get_center(), color=RED,
                        line_length=0.4, num_lines=8, run_time=0.3))        # t=2.9
        self.wait(1.0); t += 1.0
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(ike, scale=1.05), run_time=0.6); t += 0.6
        self.play(FadeIn(was_pres, shift=UP * 0.04), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 5.4)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 3: THE CLAWBACK (10.5–17.2s = 6.70s)
# "Die March 2nd → owe back entire month. No prorating."
# ================================================================
class Scene3_Clawback(Scene):
    DURATION = 6.2
    def construct(self):
        self.add(gradient_bg("#0A0A12"), grid_lines(opacity=0.05))
        t = 0

        pill = label_pill("THE CLAWBACK", color=RED, fs=28)
        pill.move_to(UP * 7)

        # Calendar mockup — March
        cal_bg = RoundedRectangle(width=6, height=5, corner_radius=0.15,
                                  fill_color=FORM_BG, fill_opacity=0.9,
                                  stroke_color=FORM_BORDER, stroke_width=1.5)
        cal_bg.move_to(UP * 2.5)
        cal_title = safe_text("MARCH", font="Bebas Neue", font_size=50, color=RED)
        cal_title.move_to(cal_bg.get_top() + DOWN * 0.5)

        # Day grid (simplified — just show day 2 highlighted)
        days = VGroup()
        for r in range(4):
            for c in range(7):
                d = r * 7 + c + 1
                if d > 31: break
                day_sq = Square(side_length=0.55, fill_color=FORM_BG, fill_opacity=0.5,
                               stroke_color=FORM_BORDER, stroke_width=0.5)
                day_sq.move_to(cal_bg.get_center() + LEFT * 2.1 + RIGHT * c * 0.7
                               + UP * 0.8 + DOWN * r * 0.7)
                day_num = Text(str(d), font="Inter", font_size=16, color=MUTED)
                day_num.move_to(day_sq)
                if d == 2:
                    day_sq.set_fill(RED, opacity=0.6)
                    day_sq.set_stroke(RED, width=2)
                    day_num.set_color(WHITE_SOFT)
                days.add(VGroup(day_sq, day_num))

        # "Die on March 2nd"
        march2 = safe_text("MARCH 2ND", font="Bebas Neue", font_size=80, color=RED)
        march2.move_to(DOWN * 1)

        div = section_div(5, RED).move_to(DOWN * 2.5)

        # "Owe back ENTIRE month"
        owe = safe_text("OWE BACK", font="Bebas Neue", font_size=70, color=WHITE_SOFT)
        owe.move_to(DOWN * 3.8)
        entire = safe_text("THE ENTIRE MONTH.", font="Bebas Neue", font_size=60, color=RED)
        entire.move_to(DOWN * 5)

        no_pro = safe_text("No prorating.", font="DM Serif Display", font_size=44, color=DEAD_GRAY)
        no_pro.move_to(DOWN * 6.5)

        # ── Timing: 6.70s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(cal_bg), FadeIn(cal_title), run_time=0.4); t += 0.4
        self.play(
            LaggedStart(*[FadeIn(d) for d in days], lag_ratio=0.01),
            run_time=0.5,
        )                                                                   # t=1.2

        # VTT 1.82: "Your family owes back..."
        self.wait(0.32); t += 0.32
        self.play(FadeIn(march2, scale=1.1), run_time=0.6); t += 0.6
        self.play(Flash(march2.get_center(), color=RED,
                        line_length=0.3, num_lines=8, run_time=0.3))        # t=2.42
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(owe, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(entire, scale=1.05), run_time=0.6); t += 0.6
        self.play(Flash(entire.get_center(), color=RED,
                        line_length=0.3, num_lines=6, run_time=0.3))        # t=4.22

        # VTT 5.58: "No prorating."
        self.wait(1.06); t += 1.06
        self.play(FadeIn(no_pro, shift=UP * 0.04), run_time=0.6); t += 0.6
        target = getattr(self.__class__, 'DURATION', 6.2)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 4: THE REAL COST (17.2–23.9s = 6.70s)
# "Probate. 20 months. 3-7% of everything you ever owned."
# ================================================================
class Scene4_RealCost(Scene):
    DURATION = 6.2
    def construct(self):
        self.add(gradient_bg(), grid_lines(opacity=0.04))
        t = 0

        pill = label_pill("THE REAL COST", color=GOLD, fs=28)
        pill.move_to(UP * 7)

        probate = safe_text("PROBATE", font="Bebas Neue", font_size=90, color=WHITE_SOFT)
        probate.move_to(UP * 5)

        div1 = section_div(5, GOLD).move_to(UP * 3.5)

        months = safe_text("20", font="Bebas Neue", font_size=180, color=GOLD)
        months.move_to(UP * 1)
        months_lbl = safe_text("MONTHS AVERAGE", font="Inter", font_size=32,
                              color=WHITE_SOFT, weight="BOLD")
        months_lbl.move_to(DOWN * 0.8)

        div2 = section_div(5, RED).move_to(DOWN * 2)

        cost_lbl = safe_text("COST:", font="Inter", font_size=30, color=MUTED, weight="BOLD")
        cost_lbl.move_to(DOWN * 3)

        pct = safe_text("3–7%", font="Bebas Neue", font_size=140, color=RED)
        pct.move_to(DOWN * 4.8)
        of_all = safe_text("of everything you ever owned.", font="DM Serif Display",
                          font_size=38, color=WHITE_SOFT)
        of_all.move_to(DOWN * 6.3)

        # ── Timing: 6.70s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.02: "Then comes probate."
        self.play(FadeIn(probate, scale=1.1), run_time=0.6); t += 0.6
        self.play(Create(div1), run_time=0.3); t += 0.3

        # VTT 1.30: "Average: 20 months."
        self.play(FadeIn(months, scale=1.3), run_time=0.7); t += 0.7
        self.play(Flash(months.get_center(), color=GOLD,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=2.2
        self.play(FadeIn(months_lbl), run_time=0.4); t += 0.4

        # VTT 2.74: "Cost:"
        self.play(Create(div2), run_time=0.2); t += 0.2
        self.play(FadeIn(cost_lbl), run_time=0.3); t += 0.3

        # VTT 3.64: "3 to 7 percent of everything you ever owned."
        self.wait(0.24); t += 0.24
        self.play(FadeIn(pct, scale=1.2), run_time=0.7); t += 0.7
        self.play(Flash(pct.get_center(), color=RED,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=4.34
        self.play(FadeIn(of_all, shift=UP * 0.06), run_time=0.7); t += 0.7
        target = getattr(self.__class__, 'DURATION', 6.2)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 5: THE ASYMMETRY (23.9–29.6s = 5.70s)
# "Benefits terminate in days. Taxes persist for months. Estate drags for years."
# ================================================================
class Scene5_Asymmetry(Scene):
    DURATION = 5.3
    def construct(self):
        self.add(gradient_bg(), grid_lines(opacity=0.04))
        t = 0

        pill = label_pill("THE ASYMMETRY", color=TEAL, fs=28)
        pill.move_to(UP * 7)

        # Three bars — accelerating width = accelerating time
        items = [
            ("BENEFITS TERMINATE", "DAYS", 1.5, TEAL, UP * 3.5),
            ("TAXES PERSIST", "MONTHS", 3.5, WARN, UP * 0.5),
            ("THE ESTATE DRAGS", "YEARS", 6.0, RED, DOWN * 2.5),
        ]

        rows = []
        for label, duration, bar_w, col, pos in items:
            bar = Rectangle(width=bar_w, height=0.8, fill_color=col, fill_opacity=0.3,
                           stroke_color=col, stroke_width=2)
            bar.move_to(pos + LEFT * (3 - bar_w / 2))
            lbl = safe_text(label, font="Inter", font_size=26, color=WHITE_SOFT, weight="BOLD")
            lbl.move_to(pos + UP * 0.9)
            dur = safe_text(duration, font="Bebas Neue", font_size=60, color=col)
            dur.move_to(pos + DOWN * 0.9)
            rows.append(VGroup(bar, lbl, dur))

        div = section_div(5, MUTED).move_to(DOWN * 5)
        speed = safe_text("Speed depends on who pays.", font="DM Serif Display",
                         font_size=38, color=DEAD_GRAY)
        speed.move_to(DOWN * 6.2)

        # ── Timing: 5.70s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.00: "Benefits terminate in days."
        self.play(FadeIn(rows[0], shift=LEFT * 0.2), run_time=0.7); t += 0.7
        self.play(Flash(rows[0][2].get_center(), color=TEAL,
                        line_length=0.2, num_lines=6, run_time=0.2))        # t=1.2

        # Wait for VTT timing gap
        self.wait(1.84); t += 1.84

        # VTT 3.34: "Taxes persist for months."
        self.play(FadeIn(rows[1], shift=LEFT * 0.2), run_time=0.6); t += 0.6

        # VTT 3.66: "The estate drags on for years."
        self.play(FadeIn(rows[2], shift=LEFT * 0.2), run_time=0.7); t += 0.7
        self.play(Flash(rows[2][2].get_center(), color=RED,
                        line_length=0.3, num_lines=8, run_time=0.3))        # t=4.64

        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(speed, shift=UP * 0.04), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 5.3)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 6: THE PUNCH (29.6–37.9s = 8.30s)
# "What gets processed fastest is what costs them money.
#  What costs you? That takes forever."
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 7.6
    def construct(self):
        self.add(gradient_bg())
        t = 0

        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP * (8 - bh/2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN * (8 - bh/2)),
        )
        self.add(grid_lines(opacity=0.02))

        # "What costs THEM" side
        div1 = section_div(4, TEAL).move_to(UP * 2)

        them1 = safe_text("What gets processed fastest", font="DM Serif Display",
                         font_size=36, color=WHITE_SOFT)
        them1.move_to(UP * 0.8)
        them2 = safe_text("is what costs them money.", font="DM Serif Display",
                         font_size=38, color=TEAL)
        them2.move_to(DOWN * 0.2)

        # "What costs YOU" side
        div2 = section_div(4, RED).move_to(DOWN * 1.8)

        you1 = safe_text("What costs you?", font="DM Serif Display",
                        font_size=42, color=WHITE_SOFT)
        you1.move_to(DOWN * 3.2)

        forever = safe_text("FOREVER.", font="Bebas Neue", font_size=100, color=RED)
        forever.move_to(DOWN * 5)

        glow = Circle(radius=2.5, fill_color=RED, fill_opacity=0.04, stroke_width=0)
        glow.move_to(forever)

        # ── Timing: 8.30s ──
        # VTT 0.06: "What gets processed fastest is what costs them money."
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(them1, shift=UP * 0.08), run_time=0.7); t += 0.7
        self.play(FadeIn(them2, shift=UP * 0.08), run_time=0.7); t += 0.7

        # VTT 3.20: "What costs you?"
        self.wait(1.2); t += 1.2
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(you1, shift=UP * 0.06), run_time=0.7); t += 0.7

        # VTT 4.36: "That takes forever."
        self.wait(0.16); t += 0.16
        self.play(FadeIn(glow), FadeIn(forever, scale=1.15), run_time=0.9); t += 0.9
        self.play(Flash(forever.get_center(), color=RED,
                        line_length=0.4, num_lines=10, run_time=0.3))      # t=5.26

        # 3s hold + fade
        target = getattr(self.__class__, 'DURATION', 7.6)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5


# ── Infra ─────────────────────────────────────────────────────
def render_single_scene(scene_idx):
    sc = [Scene1_Hook, Scene2_Freeze, Scene3_Clawback,
          Scene4_RealCost, Scene5_Asymmetry, Scene6_Punch]
    SC = sc[scene_idx]
    output_dir = Path(__file__).parent
    config.output_file = f"death_s4_scene_{scene_idx + 1}"
    config.media_dir = str(output_dir / "media")
    SC().render()
    for mp4 in Path(config.media_dir).rglob(f"death_s4_scene_{scene_idx + 1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    preview_dir = Path(__file__).parent / "previews"
    preview_dir.mkdir(exist_ok=True)
    scenes = [Scene1_Hook, Scene2_Freeze, Scene3_Clawback,
              Scene4_RealCost, Scene5_Asymmetry, Scene6_Punch]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, SC in enumerate(scenes):
        name = f"death_s4_scene_{i + 1}"
        print(f"  Preview {name}...")
        config.output_file = name
        config.save_last_frame = True; config.format = "png"
        SC().render()
        for png in Path(config.media_dir).rglob(f"{name}*"):
            if png.suffix == ".png":
                dest = preview_dir / f"{name}.png"
                shutil.copy2(str(png), str(dest))
                print(f"  OK: {dest} ({dest.stat().st_size // 1024} KB)"); break
    config.save_last_frame = False; config.format = None
    print(f"\nAll 6 previews saved to {preview_dir}/")

if __name__ == "__main__":
    import time, gc
    output_dir = Path(__file__).parent

    if "--preview" in sys.argv: render_previews(); sys.exit(0)
    if "--scene" in sys.argv:
        timings_json = os.environ.get("TKK_SCENE_TIMINGS")
        if timings_json:
            _idx = int(sys.argv[sys.argv.index("--scene")+1])
            _classes = sorted([v for k,v in globals().items() if k.startswith("Scene") and len(k) > 5 and k[5].isdigit() and isinstance(v, type)], key=lambda c: c.__name__); _classes[_idx].DURATION = json.loads(timings_json)[_idx]
        render_single_scene(int(sys.argv[sys.argv.index("--scene") + 1])); sys.exit(0)

    names = ["Scene1_Hook", "Scene2_Freeze", "Scene3_Clawback",
             "Scene4_RealCost", "Scene5_Asymmetry", "Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = output_dir / "tts_death_bureau_s4.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="death_s4", audio_path=str(audio))
    final = output_dir / "death_bureau_s4_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
