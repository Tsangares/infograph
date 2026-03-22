#!/usr/bin/env python3
"""The Superbug Clock — Antibiotic Resistance Crisis (Manim). Countdown arc.

6 scenes, ~37.0s (34.0s audio + 3s hold).

VTT cues (absolute → relative):
  Scene 1 (0.0–5.0s = 5.00s):
    0.100 (0.10) Every antibiotic humanity has ever made
    1.500 (1.50) has been defeated by bacteria.
    3.000 (3.00) And we've basically stopped making new ones.
  Scene 2 (5.0–10.0s = 5.00s):
    5.100 (0.10) Penicillin: resistance within 2 years.
    6.800 (1.80) Methicillin: 2 years.
    8.000 (3.00) Even vancomycin, the drug of last resort, has been beaten.
  Scene 3 (10.0–15.5s = 5.50s):
    10.100 (0.10) The last truly new class of antibiotic
    11.500 (1.50) was discovered in 1987.
    12.800 (2.80) 39 years ago.
    13.800 (3.80) The pipeline has 27 drugs total. Only 6 are innovative.
  Scene 4 (15.5–21.0s = 5.50s):
    15.600 (0.10) 1.27 million people died
    16.800 (1.30) from drug-resistant infections in 2019 alone.
    18.500 (3.00) By 2050, the projection is
    19.500 (4.00) 39 million cumulative deaths.
  Scene 5 (21.0–27.0s = 6.00s):
    21.100 (0.10) Pharma left the field.
    22.500 (1.50) Antibiotics are used for days, not years.
    24.000 (3.00) They go obsolete.
    25.000 (4.00) There's no money in saving the world for a week.
  Scene 6 (27.0–37.0s = 10.00s):
    27.100 (0.10) Alexander Fleming warned us in his Nobel speech.
    29.500 (2.50) 1945.
    30.500 (3.50) We had the answer before we had the problem.
    32.000 (5.00) We just didn't listen.
    + 3s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """Every antibiotic humanity has made has been defeated by bacteria. Penicillin: resistance in two years. Methicillin: two years. Vancomycin, the last resort — beaten. The last truly new class was discovered in 1987. 1.27 million died from resistant infections in 2019. By 2050, thirty-nine million projected deaths. Pharma left. Antibiotics earn for days, not years. No money in it. Fleming warned us in his Nobel speech. 1945. We had the answer before the problem."""

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
BACTERIA_GREEN = "#4CAF50"; DANGER_RED = "#F44336"
PILL_BLUE = "#2196F3"; CLOCK_ORANGE = "#FF9800"
DEATH_GRAY = "#607D8B"
WHITE_SOFT = "#F0F0F0"; MUTED = "#7B8DA0"; DIM = "#404050"
DEAD_GRAY = "#4A5568"; GOLD = "#FFD700"
SAFE_W = 8.0

ZONE_TITLE  = 6.2
ZONE_UPPER  = 3.5
ZONE_MID    = 0.0
ZONE_LOWER  = -3.5
ZONE_FOOTER = -6.0


def gradient_bg(c=BG, g="#0A100A"):
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

def section_div(width=5, color=DANGER_RED):
    l = Line(LEFT*width/2, LEFT*0.12, color=color, stroke_width=1.5)
    r = Line(RIGHT*0.12, RIGHT*width/2, color=color, stroke_width=1.5)
    d = Square(side_length=0.1, color=color, fill_color=color, fill_opacity=1).rotate(45*DEGREES)
    return VGroup(l, d, r)

def label_pill(txt, color=DANGER_RED, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    p = RoundedRectangle(width=t.width+0.5, height=t.height+0.3, corner_radius=0.18,
                         fill_color=bg, fill_opacity=0.95, stroke_color=color, stroke_width=1.5).move_to(t)
    return VGroup(p, t)

def safe_text(content, **kwargs):
    t = Text(content, **kwargs)
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    return t


# -- Domain Shape Helpers (4 custom shapes) ----------------------------

def bacteria_cell(color=BACTERIA_GREEN, h=1.0):
    """Oval bacterium with flagella tendrils and inner detail."""
    sc = h / 1.0
    body = Ellipse(width=0.7*sc, height=0.4*sc, fill_color=color, fill_opacity=0.85,
                   stroke_color=color, stroke_width=1.5)
    # Nucleoid — small inner ellipse
    nucleoid = Ellipse(width=0.25*sc, height=0.15*sc, fill_color=color, fill_opacity=0.3,
                       stroke_color=color, stroke_width=0.8)
    # Flagella — 3 wavy lines on right side
    flagella = VGroup()
    for dy in [-0.1, 0.0, 0.1]:
        pts = [np.array([0.35*sc + j*0.12*sc, dy*sc + 0.04*sc*np.sin(j*1.5), 0])
               for j in range(5)]
        for j in range(len(pts)-1):
            seg = Line(pts[j], pts[j+1], color=color, stroke_width=1.5*sc)
            seg.set_opacity(0.7)
            flagella.add(seg)
    return VGroup(body, nucleoid, flagella)

def pill_capsule(color_l=PILL_BLUE, color_r="#FFFFFF", h=0.8):
    """Medicine capsule — two-tone rounded rectangle with center band."""
    sc = h / 0.8
    left_half = RoundedRectangle(width=0.5*sc, height=0.3*sc, corner_radius=0.1*sc,
                                  fill_color=color_l, fill_opacity=0.9, stroke_width=0.8,
                                  stroke_color=PILL_BLUE)
    left_half.move_to(LEFT * 0.15*sc)
    right_half = RoundedRectangle(width=0.5*sc, height=0.3*sc, corner_radius=0.1*sc,
                                   fill_color=color_r, fill_opacity=0.7, stroke_width=0.8,
                                   stroke_color=PILL_BLUE)
    right_half.move_to(RIGHT * 0.15*sc)
    band = Line(UP * 0.13*sc, DOWN * 0.13*sc, color=color_l, stroke_width=1.5*sc)
    return VGroup(left_half, right_half, band)

def clock_ring(radius=1.5, color=CLOCK_ORANGE, progress=0.75):
    """Countdown clock — circle arc with tick marker and inner ticks."""
    outer = Circle(radius=radius, color=DEATH_GRAY, stroke_width=2).set_opacity(0.3)
    arc = Arc(radius=radius, start_angle=PI/2, angle=-progress * 2 * PI,
              color=color, stroke_width=4)
    # Tick marker at current position
    angle = PI/2 - progress * 2 * PI
    tick_pos = np.array([radius * np.cos(angle), radius * np.sin(angle), 0])
    tick = Dot(tick_pos, radius=0.08, color=color)
    # Hour marks (12 ticks around the ring)
    marks = VGroup()
    for i in range(12):
        a = PI/2 - i * PI/6
        inner = np.array([(radius-0.15) * np.cos(a), (radius-0.15) * np.sin(a), 0])
        outer_pt = np.array([radius * np.cos(a), radius * np.sin(a), 0])
        marks.add(Line(inner, outer_pt, color=DEATH_GRAY, stroke_width=1.5).set_opacity(0.4))
    return VGroup(outer, marks, arc, tick)

def skull_icon(color=DEATH_GRAY, h=1.2):
    """Simple skull — circle head + eye sockets + nasal cavity + jaw teeth."""
    sc = h / 1.2
    head = Circle(radius=0.4*sc, fill_color=color, fill_opacity=0.2,
                  stroke_color=color, stroke_width=1.5)
    eye_l = Dot(LEFT * 0.15*sc + UP * 0.08*sc, radius=0.06*sc, color=DANGER_RED)
    eye_r = Dot(RIGHT * 0.15*sc + UP * 0.08*sc, radius=0.06*sc, color=DANGER_RED)
    # Nasal cavity
    nose = Polygon(
        UP * 0.02*sc, LEFT * 0.04*sc + DOWN * 0.08*sc, RIGHT * 0.04*sc + DOWN * 0.08*sc,
        fill_color=color, fill_opacity=0.4, stroke_width=0
    )
    jaw = Rectangle(width=0.35*sc, height=0.15*sc, fill_color=color, fill_opacity=0.15,
                    stroke_color=color, stroke_width=1)
    jaw.move_to(DOWN * 0.35*sc)
    # Teeth marks
    teeth = VGroup()
    for i in range(4):
        t = Line(DOWN * 0.27*sc + LEFT * 0.1*sc + RIGHT * i * 0.07*sc,
                 DOWN * 0.32*sc + LEFT * 0.1*sc + RIGHT * i * 0.07*sc,
                 color=color, stroke_width=1*sc)
        teeth.add(t)
    return VGroup(head, eye_l, eye_r, nose, jaw, teeth)


# ================================================================
# SCENE 1: THE HOOK (0.0-5.0s = 5.00s)
# Zones: TITLE(pill) UPPER(bacteria swarm) MID(pills X'd) LOWER(clock) FOOTER(label)
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 5.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("ANTIBIOTIC RESISTANCE", color=DANGER_RED, fs=24)
        pill.move_to(UP * ZONE_TITLE)

        # Bacteria swarm — ZONE_UPPER
        bacteria = VGroup()
        np.random.seed(11)
        for i in range(10):
            b = bacteria_cell(BACTERIA_GREEN, h=0.7 + np.random.uniform(-0.1, 0.2))
            x = np.random.uniform(-3.5, 3.5)
            y = np.random.uniform(ZONE_UPPER - 1.5, ZONE_UPPER + 1.5)
            b.move_to(np.array([x, y, 0]))
            b.rotate(np.random.uniform(-0.3, 0.3))
            bacteria.add(b)

        # Pills getting X'd — ZONE_MID
        pills_row = VGroup()
        pill_crosses = VGroup()
        for i in range(5):
            p = pill_capsule(PILL_BLUE, WHITE_SOFT, h=0.7)
            x = -3.0 + i * 1.5
            p.move_to(np.array([x, ZONE_MID, 0]))
            pills_row.add(p)

            x1 = Line(LEFT * 0.3 + UP * 0.2, RIGHT * 0.3 + DOWN * 0.2,
                      color=DANGER_RED, stroke_width=4)
            x2 = Line(RIGHT * 0.3 + UP * 0.2, LEFT * 0.3 + DOWN * 0.2,
                      color=DANGER_RED, stroke_width=4)
            cross = VGroup(x1, x2).move_to(np.array([x, ZONE_MID, 0]))
            pill_crosses.add(cross)

        # Countdown clock draining — ZONE_LOWER
        clock = clock_ring(radius=1.6, color=DANGER_RED, progress=0.85)
        clock.move_to(DOWN * abs(ZONE_LOWER))

        clock_lbl = safe_text("TIME RUNNING OUT", font="Inter", font_size=22,
                              color=DEAD_GRAY, weight="BOLD")
        clock_lbl.move_to(DOWN * abs(ZONE_LOWER))

        footer = safe_text("SUPERBUG CRISIS", font="Inter",
                          font_size=22, color=DEAD_GRAY, weight="BOLD")
        footer.move_to(DOWN * abs(ZONE_FOOTER))

        # -- Timing: 5.00s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "Every antibiotic humanity has ever made"
        self.play(LaggedStart(*[FadeIn(b, scale=0.6) for b in bacteria],
                              lag_ratio=0.04), run_time=0.5)               # t=0.8
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.15) for p in pills_row],
                              lag_ratio=0.08), run_time=0.5)               # t=1.3

        # VTT 1.50: "has been defeated by bacteria."
        # Bacteria drift toward pills aggressively
        self.play(*[b.animate.shift(DOWN * 0.6 + RIGHT * np.random.uniform(-0.3, 0.3))
                    for b in bacteria], run_time=0.4)                      # t=1.7
        self.play(LaggedStart(*[Create(c) for c in pill_crosses],
                              lag_ratio=0.08), run_time=0.6)               # t=2.3
        # Pills fade to gray — defeated
        self.play(*[p.animate.set_opacity(0.3) for p in pills_row],
                  run_time=0.3)                                            # t=2.6

        # VTT 3.00: "And we've basically stopped making new ones."
        self.play(GrowFromCenter(clock), run_time=0.5); t += 0.5
        self.play(FadeIn(clock_lbl), run_time=0.2); t += 0.2
        self.play(FadeIn(footer), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 5.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE PATTERN (5.0-10.0s = 5.00s)
# Zones: TITLE(pill) UPPER+MID(3 drug rows with X) LOWER(timeline) FOOTER(label)
# ================================================================
class Scene2_Pattern(Scene):
    DURATION = 5.0
    def construct(self):
        self.add(gradient_bg("#080808"), grid_lines(0.03))
        t = 0

        pill_lbl = label_pill("THE PATTERN", color=CLOCK_ORANGE, fs=28)
        pill_lbl.move_to(UP * ZONE_TITLE)

        # 3 drug resistance rows — spread UPPER through MID
        drug_data = [
            ("PENICILLIN", "2 YEARS", ZONE_UPPER, PILL_BLUE),
            ("METHICILLIN", "2 YEARS", ZONE_MID + 0.5, PILL_BLUE),
            ("VANCOMYCIN", "DEFEATED", ZONE_MID - 2.0, DANGER_RED),
        ]

        drug_rows = []
        drug_crosses = []
        for name, time_txt, y_pos, col in drug_data:
            # Drug capsule icon on left
            cap = pill_capsule(col, WHITE_SOFT, h=0.5)
            cap.move_to(LEFT * 3.5 + UP * y_pos)
            # Drug name
            drug_name = safe_text(name, font="Bebas Neue", font_size=52, color=col)
            drug_name.move_to(LEFT * 1.2 + UP * y_pos)
            # Arrow
            arrow = Arrow(LEFT * 0.2, RIGHT * 0.8, color=MUTED, stroke_width=2, buff=0)
            arrow.move_to(RIGHT * 0.8 + UP * y_pos)
            # Time text on right
            time_t = safe_text(time_txt, font="Bebas Neue", font_size=52, color=DANGER_RED)
            time_t.move_to(RIGHT * 2.8 + UP * y_pos)
            # Red X over capsule
            x1 = Line(LEFT * 0.25 + UP * 0.25, RIGHT * 0.25 + DOWN * 0.25,
                      color=DANGER_RED, stroke_width=4)
            x2 = Line(RIGHT * 0.25 + UP * 0.25, LEFT * 0.25 + DOWN * 0.25,
                      color=DANGER_RED, stroke_width=4)
            cross = VGroup(x1, x2).move_to(cap)

            drug_rows.append(VGroup(cap, drug_name, arrow, time_t))
            drug_crosses.append(cross)

        # Resistance timeline bar — ZONE_LOWER
        tl_bg = Rectangle(width=7, height=0.35, fill_color=SURFACE2, fill_opacity=0.7,
                          stroke_color=BORDER, stroke_width=1)
        tl_bg.move_to(DOWN * abs(ZONE_LOWER))
        tl_fill = Rectangle(width=0.01, height=0.30, fill_color=DANGER_RED,
                            fill_opacity=0.6, stroke_width=0)
        tl_fill.align_to(tl_bg, LEFT).align_to(tl_bg, DOWN)
        tl_fill.shift(RIGHT * 0.025 + UP * 0.025)

        tl_label = safe_text("RESISTANCE SPREAD", font="Inter", font_size=22,
                            color=MUTED, weight="BOLD")
        tl_label.move_to(DOWN * (abs(ZONE_LOWER) - 0.7))

        footer = safe_text("ALL DEFEATED", font="Inter",
                          font_size=22, color=DEAD_GRAY, weight="BOLD")
        footer.move_to(DOWN * abs(ZONE_FOOTER))

        # -- Timing: 5.00s --
        self.play(FadeIn(pill_lbl, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "Penicillin: resistance within 2 years."
        self.play(FadeIn(drug_rows[0], shift=LEFT * 0.3), run_time=0.5); t += 0.5
        self.play(Create(drug_crosses[0]), run_time=0.3); t += 0.3

        # Show timeline filling as resistance spreads
        self.play(FadeIn(tl_bg), FadeIn(tl_label), run_time=0.2); t += 0.2
        self.play(tl_fill.animate.stretch_to_fit_width(2.3).align_to(tl_bg, LEFT).shift(RIGHT * 0.025),
                  run_time=0.3)                                            # t=1.6

        # VTT 1.80: "Methicillin: 2 years."
        self.play(FadeIn(drug_rows[1], shift=LEFT * 0.3), run_time=0.5); t += 0.5
        self.play(Create(drug_crosses[1]), run_time=0.3); t += 0.3
        self.play(tl_fill.animate.stretch_to_fit_width(4.6).align_to(tl_bg, LEFT).shift(RIGHT * 0.025),
                  run_time=0.3)                                            # t=2.7

        # VTT 3.00: "Even vancomycin... has been beaten."
        self.play(FadeIn(drug_rows[2], shift=LEFT * 0.3), run_time=0.5); t += 0.5
        self.play(Create(drug_crosses[2]),
                  Flash(drug_rows[2][0].get_center(), color=DANGER_RED,
                        line_length=0.3, num_lines=6, run_time=0.3),
                  run_time=0.3)                                            # t=3.5
        # Timeline fills completely — all resistance won
        self.play(tl_fill.animate.stretch_to_fit_width(6.95).align_to(tl_bg, LEFT).shift(RIGHT * 0.025),
                  run_time=0.4)                                            # t=3.9
        self.play(FadeIn(footer), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 5.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: THE GAP (10.0-15.5s = 5.50s)
# Zones: TITLE(pill) UPPER(1987 + clock) MID(timeline gap) LOWER(27/6 pipeline) FOOTER(label)
# ================================================================
class Scene3_Gap(Scene):
    DURATION = 5.5
    def construct(self):
        self.add(gradient_bg(g="#0A0A08"), grid_lines(0.03))
        t = 0

        pill_lbl = label_pill("THE GAP", color=CLOCK_ORANGE, fs=28)
        pill_lbl.move_to(UP * ZONE_TITLE)

        # "1987" — hero at ZONE_UPPER with flanking clock
        yr_1987 = safe_text("1987", font="Bebas Neue", font_size=140, color=CLOCK_ORANGE)
        yr_1987.move_to(UP * ZONE_UPPER)

        # Small clock showing time elapsed, next to year
        mini_clock = clock_ring(radius=0.8, color=CLOCK_ORANGE, progress=0.97)
        mini_clock.move_to(UP * ZONE_UPPER + RIGHT * 3.2)

        last_class = safe_text("LAST NEW CLASS", font="Inter", font_size=28,
                              color=MUTED, weight="BOLD")
        last_class.move_to(UP * (ZONE_UPPER - 1.5))

        # Timeline bar — ZONE_MID showing 39-year gap
        tl_bar = Rectangle(width=7, height=0.4, fill_color=SURFACE2, fill_opacity=0.8,
                          stroke_color=BORDER, stroke_width=1)
        tl_bar.move_to(UP * ZONE_MID)
        # 1987 mark on left
        mark_87 = Line(UP * 0.3, DOWN * 0.3, color=CLOCK_ORANGE, stroke_width=3)
        mark_87.move_to(tl_bar.get_left() + RIGHT * 0.3)
        lbl_87 = safe_text("1987", font="Inter", font_size=20, color=CLOCK_ORANGE, weight="BOLD")
        lbl_87.move_to(mark_87.get_bottom() + DOWN * 0.3)
        # NOW mark on right
        mark_now = Line(UP * 0.3, DOWN * 0.3, color=DANGER_RED, stroke_width=3)
        mark_now.move_to(tl_bar.get_right() + LEFT * 0.3)
        lbl_now = safe_text("NOW", font="Inter", font_size=20, color=DANGER_RED, weight="BOLD")
        lbl_now.move_to(mark_now.get_bottom() + DOWN * 0.3)
        # Gap number floats above the bar
        gap_39 = safe_text("39 YEARS", font="Bebas Neue", font_size=65, color=DANGER_RED)
        gap_39.move_to(UP * (ZONE_MID + 1.0))

        # Dashed line to emphasize emptiness in the gap
        gap_dash = DashedLine(mark_87.get_center(), mark_now.get_center(),
                              color=DEAD_GRAY, stroke_width=1.5, dash_length=0.15)

        # Pipeline stats — ZONE_LOWER
        # 27 small pill shapes, only 6 colored
        pipeline_grid = VGroup()
        for row in range(3):
            for col in range(9):
                idx = row * 9 + col
                if idx >= 27:
                    break
                is_innovative = idx < 6
                pc = pill_capsule(
                    BACTERIA_GREEN if is_innovative else DEAD_GRAY,
                    WHITE_SOFT if is_innovative else DIM,
                    h=0.35
                )
                pc.move_to(LEFT * 3.2 + RIGHT * col * 0.85 + DOWN * (abs(ZONE_LOWER) - 1.0 + row * 0.65))
                if not is_innovative:
                    pc.set_opacity(0.35)
                pipeline_grid.add(pc)

        stat_27 = safe_text("27", font="Bebas Neue", font_size=60, color=MUTED)
        stat_27.move_to(DOWN * (abs(ZONE_LOWER) + 1.5) + LEFT * 2)
        stat_lbl = safe_text("TOTAL", font="Inter", font_size=20, color=MUTED, weight="BOLD")
        stat_lbl.move_to(stat_27.get_center() + DOWN * 0.7)

        stat_6 = safe_text("6", font="Bebas Neue", font_size=60, color=DANGER_RED)
        stat_6.move_to(DOWN * (abs(ZONE_LOWER) + 1.5) + RIGHT * 2)
        innov_lbl = safe_text("INNOVATIVE", font="Inter", font_size=20,
                             color=DANGER_RED, weight="BOLD")
        innov_lbl.move_to(stat_6.get_center() + DOWN * 0.7)

        footer = safe_text("EMPTY PIPELINE", font="Inter",
                          font_size=22, color=DEAD_GRAY, weight="BOLD")
        footer.move_to(DOWN * abs(ZONE_FOOTER))

        # -- Timing: 5.50s --
        self.play(FadeIn(pill_lbl, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "The last truly new class of antibiotic"
        # VTT 1.50: "was discovered in 1987."
        self.play(FadeIn(yr_1987, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(yr_1987.get_center(), color=CLOCK_ORANGE,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=1.1
        self.play(FadeIn(mini_clock), FadeIn(last_class), run_time=0.3); t += 0.3

        # VTT 2.80: "39 years ago."
        self.wait(1.1); t += 1.1
        self.play(FadeIn(tl_bar), FadeIn(mark_87), FadeIn(lbl_87),
                  FadeIn(mark_now), FadeIn(lbl_now), run_time=0.3)         # t=2.8
        self.play(Create(gap_dash), run_time=0.3); t += 0.3
        self.play(FadeIn(gap_39, scale=1.1), run_time=0.4); t += 0.4

        # VTT 3.80: "The pipeline has 27 drugs total. Only 6 innovative."
        self.play(LaggedStart(*[FadeIn(pc, scale=0.7) for pc in pipeline_grid],
                              lag_ratio=0.02), run_time=0.6)               # t=4.1
        self.play(FadeIn(stat_27), FadeIn(stat_lbl),
                  FadeIn(stat_6), FadeIn(innov_lbl), run_time=0.4)         # t=4.5
        # Flash the 6 innovative ones
        self.play(*[pipeline_grid[i].animate.scale(1.2) for i in range(6)],
                  run_time=0.3)                                            # t=4.8
        self.play(FadeIn(footer), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 5.5)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE BODY COUNT (15.5-21.0s = 5.50s)
# Zones: TITLE(pill) UPPER(1.27M counter) MID(skull grid) LOWER(39M) FOOTER(source)
# ================================================================
class Scene4_BodyCount(Scene):
    DURATION = 5.5
    def construct(self):
        self.add(gradient_bg("#0A0505"), grid_lines(0.03))
        t = 0

        pill_lbl = label_pill("THE BODY COUNT", color=DANGER_RED, fs=28)
        pill_lbl.move_to(UP * ZONE_TITLE)

        # Animated counter counting up — ZONE_UPPER
        counter_stages = ["127,000", "508,000", "889,000", "1,270,000"]
        counter_texts = [
            safe_text(v, font="Bebas Neue", font_size=105, color=DANGER_RED).move_to(UP * ZONE_UPPER)
            for v in counter_stages
        ]

        yr_2019 = safe_text("2019", font="Bebas Neue", font_size=44,
                           color=MUTED)
        yr_2019.move_to(UP * (ZONE_UPPER - 1.3))

        # Skull grid — ZONE_MID (visual weight)
        skull_grid = VGroup()
        for row in range(2):
            for col in range(5):
                sk = skull_icon(DEATH_GRAY, h=0.8)
                sk.move_to(LEFT * 2.5 + RIGHT * col * 1.25 +
                           UP * (ZONE_MID + 0.4 - row * 1.2))
                skull_grid.add(sk)

        # Divider
        div_mid = section_div(5, CLOCK_ORANGE).move_to(DOWN * 1.5)

        # "39,000,000" — ZONE_LOWER
        count_2050 = safe_text("39,000,000", font="Bebas Neue", font_size=100,
                              color=CLOCK_ORANGE)
        count_2050.move_to(DOWN * (abs(ZONE_LOWER) - 0.5))

        by_2050 = safe_text("BY 2050", font="Bebas Neue", font_size=50, color=MUTED)
        by_2050.move_to(DOWN * (abs(ZONE_LOWER) + 0.8))

        # Arrow showing escalation between the two numbers
        escalation = Arrow(
            UP * (ZONE_UPPER - 1.8), DOWN * (abs(ZONE_LOWER) - 1.5),
            color=DANGER_RED, stroke_width=2.5, buff=0.3
        )
        escalation.set_opacity(0.4)

        footer = safe_text("WHO / LANCET", font="Inter",
                          font_size=20, color=DEAD_GRAY, weight="BOLD")
        footer.move_to(DOWN * abs(ZONE_FOOTER))

        # -- Timing: 5.50s --
        self.play(FadeIn(pill_lbl, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "1.27 million people died" — animated counter
        self.play(FadeIn(counter_texts[0]), run_time=0.2); t += 0.2
        self.play(FadeOut(counter_texts[0]), FadeIn(counter_texts[1]),
                  run_time=0.2)                                            # t=0.7
        self.play(FadeOut(counter_texts[1]), FadeIn(counter_texts[2]),
                  run_time=0.2)                                            # t=0.9
        self.play(FadeOut(counter_texts[2]), FadeIn(counter_texts[3]),
                  run_time=0.25)                                           # t=1.15
        self.play(Flash(counter_texts[3].get_center(), color=DANGER_RED,
                        line_length=0.5, num_lines=10, run_time=0.25))     # t=1.4

        # VTT 1.30: "from drug-resistant infections in 2019 alone."
        self.play(FadeIn(yr_2019), run_time=0.2); t += 0.2

        # Skulls fill in — wave pattern
        self.play(LaggedStart(*[FadeIn(sk, scale=0.7) for sk in skull_grid],
                              lag_ratio=0.04), run_time=0.6)               # t=2.2
        # Skulls pulse red
        self.play(*[sk[1].animate.set_color(DANGER_RED).scale(1.3)
                    for sk in skull_grid],
                  *[sk[2].animate.set_color(DANGER_RED).scale(1.3)
                    for sk in skull_grid],
                  run_time=0.3)                                            # t=2.5

        # VTT 3.00: "By 2050, the projection is"
        self.play(Create(div_mid), run_time=0.2); t += 0.2
        self.play(GrowArrow(escalation), run_time=0.4); t += 0.4

        # VTT 4.00: "39 million cumulative deaths."
        self.wait(0.6); t += 0.6
        self.play(FadeIn(count_2050, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(count_2050.get_center(), color=CLOCK_ORANGE,
                        line_length=0.6, num_lines=12, run_time=0.3))      # t=4.5
        self.play(FadeIn(by_2050), run_time=0.2); t += 0.2
        self.play(FadeIn(footer), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 5.5)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE WHY (21.0-27.0s = 6.00s)
# Zones: TITLE(pill) UPPER(dollar shrinking pill) MID(7 days vs 7 years bars) LOWER(broken pills) FOOTER(label)
# ================================================================
class Scene5_Why(Scene):
    DURATION = 6.0
    def construct(self):
        self.add(gradient_bg(g="#0A0A08"), grid_lines(0.03))
        t = 0

        pill_lbl = label_pill("THE REASON", color=DEATH_GRAY, fs=28)
        pill_lbl.move_to(UP * ZONE_TITLE)

        # Dollar sign growing, pill shrinking — ZONE_UPPER
        dollar = safe_text("$", font="Bebas Neue", font_size=160, color=BACTERIA_GREEN)
        dollar.move_to(LEFT * 2 + UP * ZONE_UPPER)

        tiny_pill = pill_capsule(PILL_BLUE, WHITE_SOFT, h=0.6)
        tiny_pill.move_to(RIGHT * 2 + UP * ZONE_UPPER)

        vs_arrow = Arrow(LEFT * 0.5, RIGHT * 0.5, color=MUTED, stroke_width=2, buff=0)
        vs_arrow.move_to(UP * ZONE_UPPER)

        # Duration comparison bars — ZONE_MID
        bar_7d = Rectangle(width=1.5, height=0.5, fill_color=PILL_BLUE,
                          fill_opacity=0.7, stroke_color=PILL_BLUE, stroke_width=1)
        bar_7d.move_to(LEFT * 2 + UP * ZONE_MID)
        lbl_7d = safe_text("7 DAYS", font="Bebas Neue", font_size=44, color=PILL_BLUE)
        lbl_7d.move_to(LEFT * 2 + UP * (ZONE_MID + 0.8))

        bar_7y = Rectangle(width=5.5, height=0.5, fill_color=BACTERIA_GREEN,
                          fill_opacity=0.7, stroke_color=BACTERIA_GREEN, stroke_width=1)
        bar_7y.move_to(RIGHT * 0.5 + DOWN * 1.0)
        lbl_7y = safe_text("7 YEARS", font="Bebas Neue", font_size=44, color=BACTERIA_GREEN)
        lbl_7y.move_to(RIGHT * 0.5 + DOWN * 0.2)

        antibiotic_lbl = safe_text("ANTIBIOTIC COURSE", font="Inter", font_size=18,
                                  color=MUTED, weight="BOLD")
        antibiotic_lbl.move_to(LEFT * 2 + UP * (ZONE_MID - 0.6))

        chronic_lbl = safe_text("CHRONIC DRUG PROFIT", font="Inter", font_size=18,
                               color=MUTED, weight="BOLD")
        chronic_lbl.move_to(RIGHT * 0.5 + DOWN * 1.7)

        # Broken pills scattered — ZONE_LOWER (pharma abandoned)
        broken_pills = VGroup()
        np.random.seed(55)
        for i in range(6):
            bp = pill_capsule(DEAD_GRAY, DIM, h=0.4)
            bp.set_opacity(0.4)
            x = np.random.uniform(-3.0, 3.0)
            y = np.random.uniform(ZONE_LOWER - 1.0, ZONE_LOWER + 1.0)
            bp.move_to(np.array([x, y, 0]))
            bp.rotate(np.random.uniform(-0.5, 0.5))
            broken_pills.add(bp)

        # X marks over broken pills
        broken_crosses = VGroup()
        for bp in broken_pills:
            x1 = Line(LEFT * 0.2 + UP * 0.15, RIGHT * 0.2 + DOWN * 0.15,
                      color=DANGER_RED, stroke_width=2.5)
            x2 = Line(RIGHT * 0.2 + UP * 0.15, LEFT * 0.2 + DOWN * 0.15,
                      color=DANGER_RED, stroke_width=2.5)
            cross = VGroup(x1, x2).move_to(bp)
            cross.set_opacity(0.5)
            broken_crosses.add(cross)

        footer = safe_text("NO PROFIT MODEL", font="Inter",
                          font_size=22, color=DEAD_GRAY, weight="BOLD")
        footer.move_to(DOWN * abs(ZONE_FOOTER))

        # -- Timing: 6.00s --
        self.add(pill_lbl)

        # VTT 0.10: "Pharma left the field."
        self.play(FadeIn(dollar, scale=1.1), run_time=0.4); t += 0.4
        self.play(FadeIn(vs_arrow), FadeIn(tiny_pill, scale=0.8), run_time=0.3); t += 0.3

        # VTT 1.50: "Antibiotics are used for days, not years."
        self.wait(0.5); t += 0.5
        # Pill shrinks, dollar grows
        self.play(dollar.animate.scale(1.3),
                  tiny_pill.animate.scale(0.5).set_opacity(0.4),
                  run_time=0.5)                                            # t=1.7

        # Bar comparison appears
        self.play(FadeIn(lbl_7d), GrowFromCenter(bar_7d), run_time=0.4); t += 0.4
        self.play(FadeIn(antibiotic_lbl), run_time=0.2); t += 0.2

        # VTT 3.00: "They go obsolete."
        self.play(FadeIn(lbl_7y), GrowFromCenter(bar_7y), run_time=0.5); t += 0.5
        self.play(FadeIn(chronic_lbl), run_time=0.2); t += 0.2

        # Broken pills rain down — ZONE_LOWER
        self.wait(0.5); t += 0.5
        self.play(LaggedStart(*[FadeIn(bp, shift=DOWN * 0.4) for bp in broken_pills],
                              lag_ratio=0.06), run_time=0.5)               # t=4.0

        # VTT 4.00: "There's no money in saving the world for a week."
        self.play(LaggedStart(*[Create(c) for c in broken_crosses],
                              lag_ratio=0.05), run_time=0.4)               # t=4.4
        self.play(FadeIn(footer), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 6.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE PUNCH (27.0-37.0s = 10.00s)
# Zones: TITLE(letterbox+pill) UPPER(clock+Fleming) MID(1945) LOWER(quote concept) FOOTER(final)
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 10.0
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

        pill_lbl = label_pill("THE WARNING", color=CLOCK_ORANGE, fs=28)
        pill_lbl.move_to(UP * ZONE_TITLE)

        # Clock ring — ZONE_UPPER, nearly complete
        clock = clock_ring(radius=1.8, color=CLOCK_ORANGE, progress=0.95)
        clock.move_to(UP * ZONE_UPPER)
        clock[2].set_stroke(width=6)  # arc stroke thicker

        # Abstract Fleming figure inside/below clock
        head = Circle(radius=0.55, fill_color=MUTED, fill_opacity=0.3,
                     stroke_color=WHITE_SOFT, stroke_width=2.5)
        head.move_to(UP * (ZONE_UPPER + 0.2))
        shoulders = Ellipse(width=2.2, height=0.7, fill_color=MUTED, fill_opacity=0.2,
                           stroke_color=WHITE_SOFT, stroke_width=1.5)
        shoulders.move_to(UP * (ZONE_UPPER - 0.7))

        # "1945" — hero at ZONE_MID
        yr_1945 = safe_text("1945", font="Bebas Neue", font_size=150, color=CLOCK_ORANGE)
        yr_1945.move_to(UP * ZONE_MID)

        yr_glow = Circle(radius=2.0, fill_color=CLOCK_ORANGE, fill_opacity=0.06, stroke_width=0)
        yr_glow.move_to(yr_1945)

        fleming_name = safe_text("FLEMING", font="Bebas Neue", font_size=36,
                                color=CLOCK_ORANGE, weight="BOLD")
        fleming_name.move_to(UP * (ZONE_MID + 1.5))

        div1 = section_div(4, CLOCK_ORANGE).move_to(DOWN * 1.5)

        # Nobel medal shape — ZONE_LOWER top
        medal_outer = Circle(radius=0.6, color=GOLD, stroke_width=2)
        medal_inner = Circle(radius=0.45, color=GOLD, fill_opacity=0.15, stroke_width=1)
        medal_star = VGroup()
        for i in range(5):
            a = PI/2 + i * 2 * PI / 5
            pt = np.array([0.3 * np.cos(a), 0.3 * np.sin(a), 0])
            medal_star.add(Dot(pt, radius=0.04, color=GOLD))
        medal = VGroup(medal_outer, medal_inner, medal_star)
        medal.move_to(DOWN * 2.5)

        nobel_lbl = safe_text("NOBEL SPEECH", font="Inter", font_size=22,
                             color=MUTED, weight="BOLD")
        nobel_lbl.move_to(DOWN * 3.3)

        div2 = section_div(4, DANGER_RED).move_to(DOWN * 4.2)

        # Final emphasis — ZONE_FOOTER area
        didnt_listen = safe_text("WE DIDN'T LISTEN.", font="Bebas Neue",
                                font_size=68, color=DANGER_RED)
        didnt_listen.move_to(DOWN * 5.2)

        glow = Circle(radius=2.5, fill_color=DANGER_RED, fill_opacity=0.08, stroke_width=0)
        glow.move_to(didnt_listen)

        # -- Timing: 10.00s --
        # VTT 0.10: "Alexander Fleming warned us in his Nobel speech."
        self.play(FadeIn(pill_lbl, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(clock), run_time=0.4); t += 0.4
        self.play(FadeIn(head), FadeIn(shoulders), run_time=0.4); t += 0.4
        self.play(FadeIn(fleming_name), run_time=0.3); t += 0.3

        # VTT 2.50: "1945."
        self.wait(0.8); t += 0.8
        self.play(FadeIn(yr_glow), FadeIn(yr_1945, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(yr_1945.get_center(), color=CLOCK_ORANGE,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=3.0

        # VTT 3.50: "We had the answer before we had the problem."
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(GrowFromCenter(medal), run_time=0.5); t += 0.5
        self.play(FadeIn(nobel_lbl), run_time=0.3); t += 0.3

        # VTT 5.00: "We just didn't listen."
        self.wait(0.6); t += 0.6
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(glow), FadeIn(didnt_listen, scale=1.08), run_time=0.7); t += 0.7
        self.play(Flash(didnt_listen.get_center(), color=DANGER_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=6.0

        # Hold + fade to black
        self.wait(2.0); t += 2.0
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5
        target = getattr(self.__class__, 'DURATION', 10.0)
        self.wait(max(0.1, target - t - 0.8))


# -- Infra -------------------------------------------------------------
def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_Pattern, Scene3_Gap,
          Scene4_BodyCount, Scene5_Why, Scene6_Punch]
    config.output_file = f"superbug_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"superbug_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    sc = [Scene1_Hook, Scene2_Pattern, Scene3_Gap,
          Scene4_BodyCount, Scene5_Why, Scene6_Punch]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(sc):
        n = f"superbug_scene_{i+1}"; print(f"  Preview {n}...")
        config.output_file = n; config.save_last_frame = True; config.format = "png"
        S().render()
        for p in Path(config.media_dir).rglob(f"{n}*"):
            if p.suffix == ".png":
                dst = d / f"{n}.png"; shutil.copy2(str(p), str(dst))
                print(f"  OK: {dst} ({dst.stat().st_size//1024} KB)"); break
    config.save_last_frame = False; config.format = None
    print(f"\nAll 6 previews -> {d}/")

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

    names = ["Scene1_Hook","Scene2_Pattern","Scene3_Gap",
             "Scene4_BodyCount","Scene5_Why","Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_superbug_clock.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="superbug", audio_path=str(audio))
    final = od / "superbug_clock_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
