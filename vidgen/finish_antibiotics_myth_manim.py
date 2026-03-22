#!/usr/bin/env python3
"""Finish Your Antibiotics Is Wrong — The myth that stopping early breeds resistance.

6 scenes, ~41.0s (38.0s audio + 3s hold).
Domain shapes: prescription_bottle, patient_bed, bacteria_battlefield, calendar_strip.

VTT cues (absolute -> relative):
  Scene 1 (0.0-6.0s = 6.00s):
    0.10 (0.10) Always finish your antibiotics.
    1.60 (1.60) It's the most repeated advice in medicine.
    3.20 (3.20) The logic sounds bulletproof:
    4.40 (4.40) stop early and the strongest bacteria survive.
  Scene 2 (6.0-12.0s = 6.00s):
    6.10 (0.10) But in twenty seventeen, researchers published
    7.80 (1.80) a landmark paper in the BMJ.
    9.00 (3.00) For most common infections,
    10.20 (4.20) there's little evidence stopping early causes resistance.
  Scene 3 (12.0-17.5s = 5.50s):
    12.10 (0.10) The real driver is the opposite.
    13.40 (1.40) Every extra day of antibiotics
    14.80 (2.80) puts pressure on bacteria throughout your entire body.
    16.20 (4.20) Longer courses breed more resistance, not less.
  Scene 4 (17.5-24.0s = 6.50s):
    17.60 (0.10) Over a hundred and twenty randomized trials
    19.20 (1.70) show shorter courses work just as well.
    20.80 (3.30) Pneumonia: three to five days equals seven to fourteen.
    22.20 (4.70) Cystitis: three days equals seven.
    23.20 (5.70) Cellulitis: six days equals twelve.
  Scene 5 (24.0-31.0s = 7.00s):
    24.10 (0.10) The seven-to-fourteen-day convention?
    25.80 (1.80) It traces to the Roman calendar,
    27.00 (3.00) not science.
    28.40 (4.40) For eighty years, doctors prescribed extra days
    30.00 (6.00) that did nothing for the infection.
  Scene 6 (31.0-41.0s = 10.00s):
    31.10 (0.10) but put selective pressure on your gut bacteria.
    33.40 (2.40) The advice meant to prevent resistance
    35.80 (4.80) may have accelerated it.
    + 3s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """Always finish your antibiotics. Most repeated advice in medicine. Stop early and resistant bacteria survive. In twenty-seventeen, a landmark BMJ paper found the opposite. Longer courses breed more resistance. Every extra day puts pressure on bacteria throughout your entire body. A hundred and twenty trials show shorter courses work just as well. The seven-to-fourteen-day convention traces to the Roman calendar, not science. The advice meant to prevent resistance may have accelerated it."""

from manim import (
    Scene, Text, Group, VGroup, Rectangle, RoundedRectangle, Circle,
    Line, Arrow, DashedLine, Dot, Polygon, Ellipse, Square, Arc,
    FadeIn, FadeOut, GrowFromCenter, Write, Create, DrawBorderThenFill,
    AnimationGroup, LaggedStart, Flash, GrowArrow, MoveToTarget,
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

# -- Color palette ----------------------------------------------------
BG = "#080A10"; GRID = "#1A2030"; SURFACE = "#15192A"
WHITE_SOFT = "#F0F0F0"; GOLD = "#FFD700"
PILL_BLUE = "#3B82F6"; CAPSULE_WHITE = "#CBD5E1"
DANGER_RED = "#EF4444"; WARN_ORANGE = "#F59E0B"
BODY_PURPLE = "#8B5CF6"; GUT_GREEN = "#22C55E"
BMJ_TEAL = "#14B8A6"; CALENDAR_RUST = "#D97706"
MUTED = "#475569"; DIM = "#334155"; DEAD_GRAY = "#4A5568"
SAFE_W = 8.0; SAFE_TOP = 7.2; SAFE_BOT = -6.4

ZONE_TITLE  = 6.2
ZONE_UPPER  = 3.5
ZONE_MID    = 0.0
ZONE_LOWER  = -3.5
ZONE_FOOTER = -6.0

# -- Core helpers ------------------------------------------------------

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
    p = RoundedRectangle(
        width=t.width + 0.5, height=t.height + 0.3,
        corner_radius=0.15, fill_color=bg, fill_opacity=0.9, stroke_width=0
    ).move_to(t)
    return VGroup(p, t)

def section_div(width=5, color=GOLD):
    l = Line(LEFT*width/2, LEFT*0.12, color=color, stroke_width=1.5)
    r = Line(RIGHT*0.12, RIGHT*width/2, color=color, stroke_width=1.5)
    d = Square(side_length=0.1, color=color, fill_color=color, fill_opacity=1).rotate(45*DEGREES)
    return VGroup(l, d, r)


# -- Domain shape helpers ----------------------------------------------

def prescription_bottle(h=3.0, color=PILL_BLUE, label_txt="TAKE ALL 14"):
    """Rounded rectangle bottle with cap and label text."""
    sc = h / 3.0
    body = RoundedRectangle(
        width=1.8*sc, height=2.8*sc, corner_radius=0.15*sc,
        fill_color=color, fill_opacity=0.15,
        stroke_color=color, stroke_width=2
    )
    cap = Rectangle(
        width=1.4*sc, height=0.5*sc,
        fill_color=color, fill_opacity=0.35,
        stroke_color=color, stroke_width=1.5
    )
    cap.move_to(body.get_top() + DOWN * 0.25*sc)
    label_bg = Rectangle(
        width=1.4*sc, height=0.8*sc,
        fill_color=WHITE_SOFT, fill_opacity=0.12, stroke_width=0
    )
    label_bg.move_to(body.get_center())
    label_t = Text(label_txt, font="Inter", font_size=int(18*sc), color=WHITE_SOFT, weight="BOLD")
    if label_t.width > 1.3*sc: label_t.scale(1.3*sc / label_t.width)
    label_t.move_to(label_bg)
    # Capsule pills inside bottle (decorative)
    pills = VGroup()
    for dy in [-0.5*sc, 0.5*sc]:
        pill = Ellipse(width=0.35*sc, height=0.15*sc,
                       fill_color=CAPSULE_WHITE, fill_opacity=0.2,
                       stroke_width=0).move_to(body.get_center() + DOWN * dy)
        pills.add(pill)
    return VGroup(body, cap, label_bg, label_t, pills)


def patient_bed(h=1.5, color=WHITE_SOFT):
    """Simplified hospital bed with patient silhouette."""
    sc = h / 1.5
    bed_frame = Rectangle(
        width=2.5*sc, height=0.15*sc,
        fill_color=color, fill_opacity=0.3,
        stroke_color=color, stroke_width=1.5
    )
    leg_l = Line(
        bed_frame.get_corner(DL), bed_frame.get_corner(DL) + DOWN * 0.4*sc,
        color=color, stroke_width=1.5
    )
    leg_r = Line(
        bed_frame.get_corner(DR), bed_frame.get_corner(DR) + DOWN * 0.4*sc,
        color=color, stroke_width=1.5
    )
    body_shape = Ellipse(
        width=1.8*sc, height=0.35*sc,
        fill_color=color, fill_opacity=0.2,
        stroke_color=color, stroke_width=1
    ).move_to(bed_frame.get_center() + UP * 0.25*sc)
    head = Circle(
        radius=0.2*sc, fill_color=color, fill_opacity=0.25,
        stroke_color=color, stroke_width=1
    ).move_to(bed_frame.get_left() + RIGHT * 0.3*sc + UP * 0.4*sc)
    return VGroup(bed_frame, leg_l, leg_r, body_shape, head)


def bacteria_battlefield(rows=3, cols=6, h=3.0):
    """Grid of bacteria dots -- weak (dim), medium, strong (bright red)."""
    sc = h / 3.0
    dots = VGroup()
    np.random.seed(42)
    for r in range(rows):
        for c in range(cols):
            strength = np.random.choice([0, 1, 2], p=[0.5, 0.3, 0.2])
            colors = [GUT_GREEN, WARN_ORANGE, DANGER_RED]
            opacities = [0.4, 0.65, 0.95]
            radii = [0.12*sc, 0.14*sc, 0.17*sc]
            x = (-cols/2 + c + 0.5) * 0.6*sc
            y = (-rows/2 + r + 0.5) * 0.6*sc
            dot = Dot(
                np.array([x, y, 0]),
                radius=radii[strength],
                color=colors[strength]
            ).set_opacity(opacities[strength])
            dots.add(dot)
    return dots


def calendar_strip(n_days=14, crossed=0, color=CALENDAR_RUST, h=0.6):
    """Row of day boxes. First `crossed` boxes get an X."""
    sc = h / 0.6
    boxes = VGroup()
    crosses = VGroup()
    total_w = n_days * 0.45 * sc
    for i in range(n_days):
        x = -total_w/2 + (i + 0.5) * 0.45*sc
        box = Square(
            side_length=0.38*sc,
            fill_color=color if i < crossed else DIM,
            fill_opacity=0.2 if i < crossed else 0.08,
            stroke_color=color if i < crossed else DIM,
            stroke_width=1.2
        ).move_to(RIGHT * x)
        boxes.add(box)
        if i < crossed:
            x1 = Line(LEFT * 0.12*sc + UP * 0.12*sc, RIGHT * 0.12*sc + DOWN * 0.12*sc,
                       color=DANGER_RED, stroke_width=2*sc)
            x2 = Line(RIGHT * 0.12*sc + UP * 0.12*sc, LEFT * 0.12*sc + DOWN * 0.12*sc,
                       color=DANGER_RED, stroke_width=2*sc)
            cross = VGroup(x1, x2).move_to(box)
            crosses.add(cross)
    return VGroup(boxes, crosses)


# ================================================================
# SCENE 1: THE SACRED RULE (0.0-6.0s = 6.00s)
# Zones: TITLE(pill) UPPER(prescription bottle) MID(doctor+FINISH) LOWER(calendar) FOOTER(label)
# ================================================================
class Scene1_SacredRule(Scene):
    DURATION = 9.7
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE SACRED RULE", color=PILL_BLUE, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # Prescription bottle -- ZONE_UPPER
        bottle = prescription_bottle(h=3.2, color=PILL_BLUE, label_txt="TAKE ALL 14")
        bottle.move_to(UP * ZONE_UPPER)

        # Doctor figure pointing -- ZONE_MID
        doc_head = Circle(radius=0.35, fill_color=WHITE_SOFT, fill_opacity=0.2,
                         stroke_color=WHITE_SOFT, stroke_width=2)
        doc_body = Polygon(
            np.array([-0.5, -0.9, 0]), np.array([0.5, -0.9, 0]),
            np.array([0.3, 0, 0]), np.array([-0.3, 0, 0]),
            fill_color=PILL_BLUE, fill_opacity=0.2,
            stroke_color=PILL_BLUE, stroke_width=1.5
        )
        doc_body.move_to(DOWN * 0.6)
        doc_arm = Line(RIGHT * 0.3 + UP * 0.05, RIGHT * 1.2 + UP * 0.3,
                       color=WHITE_SOFT, stroke_width=2)
        doc = VGroup(doc_head, doc_body, doc_arm)
        doc.move_to(LEFT * 2.5 + UP * ZONE_MID)

        finish_txt = safe_text("FINISH.", font="Bebas Neue", font_size=100, color=PILL_BLUE)
        finish_txt.move_to(RIGHT * 1.0 + UP * ZONE_MID)

        # Calendar strip -- ZONE_LOWER
        cal = calendar_strip(n_days=14, crossed=0, color=CALENDAR_RUST, h=0.7)
        cal.move_to(UP * ZONE_LOWER)

        day_lbl = safe_text("14-DAY COURSE", font="Inter", font_size=24,
                           color=CALENDAR_RUST, weight="BOLD")
        day_lbl.move_to(UP * (ZONE_LOWER - 1.0))

        # Capsule icons scattered at ZONE_LOWER area for depth
        capsules = VGroup()
        for cx, cy in [(-3, -2.5), (3.2, -2.8), (-2, -5.2), (2.8, -5.0)]:
            cap = Ellipse(width=0.5, height=0.2,
                          fill_color=PILL_BLUE, fill_opacity=0.12,
                          stroke_color=PILL_BLUE, stroke_width=0.8)
            cap.move_to(RIGHT * cx + UP * cy)
            capsules.add(cap)

        footer = safe_text("THE MOST REPEATED ADVICE", font="Inter",
                          font_size=22, color=DEAD_GRAY, weight="BOLD")
        footer.move_to(UP * ZONE_FOOTER)

        # -- Timing: 6.00s --
        # VTT 0.10: "Always finish your antibiotics."
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(GrowFromCenter(bottle), run_time=0.6); t += 0.6

        # VTT 1.60: "It's the most repeated advice in medicine."
        self.wait(0.4); t += 0.4
        self.play(FadeIn(doc, shift=RIGHT * 0.2), run_time=0.5); t += 0.5
        self.play(FadeIn(finish_txt, scale=1.15), run_time=0.5); t += 0.5
        self.play(Flash(finish_txt.get_center(), color=PILL_BLUE,
                        line_length=0.4, num_lines=8, run_time=0.3))        # t=2.6

        # VTT 3.20: "The logic sounds bulletproof:"
        self.play(FadeIn(cal, shift=UP * 0.15), run_time=0.5); t += 0.5

        # VTT 4.40: "stop early and the strongest bacteria survive."
        self.play(FadeIn(day_lbl), run_time=0.3); t += 0.3
        self.play(LaggedStart(*[FadeIn(c, scale=0.6) for c in capsules],
                              lag_ratio=0.08), run_time=0.4)                # t=3.8
        self.play(FadeIn(footer), run_time=0.3); t += 0.3

        # Ambient: bottle pulses gently
        self.play(bottle.animate.scale(1.04), run_time=0.6); t += 0.6
        self.play(bottle.animate.scale(1/1.04), run_time=0.6); t += 0.6
        target = getattr(self.__class__, 'DURATION', 9.7)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE REVERSAL (6.0-12.0s = 6.00s)
# Zones: TITLE(pill) UPPER(2017 year) MID(journal page) LOWER(bed + finding) FOOTER(source)
# ================================================================
class Scene2_Origin(Scene):
    DURATION = 9.7
    def construct(self):
        self.add(gradient_bg(g="#0A1218"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE REVERSAL", color=BMJ_TEAL, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # BMJ year -- ZONE_UPPER
        yr_2017 = safe_text("2017", font="Bebas Neue", font_size=150, color=BMJ_TEAL)
        yr_2017.move_to(UP * ZONE_UPPER)

        bmj_lbl = safe_text("BMJ", font="Bebas Neue", font_size=70, color=WHITE_SOFT)
        bmj_lbl.move_to(UP * 1.8)

        # Journal page icon -- ZONE_MID
        page_bg = RoundedRectangle(
            width=3.5, height=2.5, corner_radius=0.12,
            fill_color=SURFACE, fill_opacity=0.8,
            stroke_color=BMJ_TEAL, stroke_width=2
        ).move_to(UP * ZONE_MID)
        page_lines = VGroup()
        for i in range(5):
            ln_w = 1.2 - i * 0.05
            ln = Line(LEFT * ln_w, RIGHT * ln_w, color=BMJ_TEAL,
                      stroke_width=1.5).set_opacity(0.3 + i * 0.1)
            ln.move_to(UP * ZONE_MID + UP * (0.6 - i * 0.3))
            page_lines.add(ln)
        journal = VGroup(page_bg, page_lines)

        # Red stamp over journal
        finding = safe_text("NO EVIDENCE", font="Bebas Neue", font_size=70,
                           color=DANGER_RED)
        finding.move_to(UP * ZONE_MID)
        finding_border = Rectangle(
            width=finding.width + 0.4, height=finding.height + 0.2,
            stroke_color=DANGER_RED, stroke_width=3, fill_opacity=0
        ).move_to(finding).rotate(0.06)
        stamp_group = VGroup(finding, finding_border)

        # Patient bed -- ZONE_LOWER
        bed = patient_bed(h=1.4, color=WHITE_SOFT)
        bed.move_to(UP * (ZONE_LOWER + 0.5))

        # Recovery checkmark next to bed
        check = safe_text("OK", font="Bebas Neue", font_size=40, color=GUT_GREEN)
        check.move_to(bed.get_right() + RIGHT * 1.2)

        stopped_lbl = safe_text("STOPPING EARLY", font="Inter", font_size=26,
                               color=MUTED, weight="BOLD")
        stopped_lbl.move_to(UP * (ZONE_LOWER - 1.2))

        footer = safe_text("BMJ 2017;358:j3418", font="Inter",
                          font_size=20, color=DEAD_GRAY, weight="BOLD")
        footer.move_to(UP * ZONE_FOOTER)

        # -- Timing: 6.00s --
        # VTT 0.10: "But in twenty seventeen, researchers published"
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(yr_2017, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(yr_2017.get_center(), color=BMJ_TEAL,
                        line_length=0.5, num_lines=10, run_time=0.3))       # t=1.1

        # VTT 1.80: "a landmark paper in the BMJ."
        self.play(FadeIn(bmj_lbl), run_time=0.3); t += 0.3
        self.play(FadeIn(journal, scale=0.9), run_time=0.5); t += 0.5

        # VTT 3.00: "For most common infections,"
        target = getattr(self.__class__, 'DURATION', 9.7)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeIn(stamp_group, scale=1.15), run_time=0.4); t += 0.4
        self.play(Flash(finding.get_center(), color=DANGER_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))        # t=3.4

        # VTT 4.20: "there's little evidence stopping early causes resistance."
        self.play(FadeIn(bed, shift=UP * 0.15), run_time=0.4); t += 0.4
        self.play(FadeIn(check, scale=1.3), run_time=0.3); t += 0.3
        self.play(FadeIn(stopped_lbl), run_time=0.3); t += 0.3
        self.play(FadeIn(footer), run_time=0.3); t += 0.3

        # Ambient drift: journal slowly scales down as finding dominates
        self.play(journal.animate.scale(0.92).set_opacity(0.4), run_time=1.0); t += 1.0

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: COLLATERAL DAMAGE (12.0-17.5s = 5.50s)
# Zones: TITLE(pill) UPPER(body silhouette + arrows) MID(DAY 5 vs 14) LOWER(gut bacteria) FOOTER(label)
# ================================================================
class Scene3_Logic(Scene):
    DURATION = 8.9
    def construct(self):
        self.add(gradient_bg(g="#120A0A"), grid_lines(0.03))
        t = 0

        pill = label_pill("COLLATERAL DAMAGE", color=DANGER_RED, fs=24)
        pill.move_to(UP * ZONE_TITLE)

        # Body silhouette -- ZONE_UPPER (oval head + trapezoid torso)
        body_head = Circle(radius=0.45, fill_color=BODY_PURPLE, fill_opacity=0.15,
                          stroke_color=BODY_PURPLE, stroke_width=2)
        body_head.move_to(UP * 5.0)
        body_torso = Polygon(
            np.array([-0.8, 0, 0]), np.array([0.8, 0, 0]),
            np.array([1.0, -2.5, 0]), np.array([-1.0, -2.5, 0]),
            fill_color=BODY_PURPLE, fill_opacity=0.08,
            stroke_color=BODY_PURPLE, stroke_width=1.5
        ).move_to(UP * 3.0)

        # Healed marker
        healed_dot = Dot(UP * 4.5 + RIGHT * 0.8, radius=0.15, color=GUT_GREEN)
        healed_lbl = safe_text("HEALED", font="Inter", font_size=18,
                              color=GUT_GREEN, weight="BOLD")
        healed_lbl.move_to(UP * 4.5 + RIGHT * 2.0)

        # Drug arrows flooding the body
        arrows = VGroup()
        for y_off in [4.0, 3.2, 2.4]:
            for x_off in [-0.4, 0.4]:
                arr = Arrow(
                    UP * (y_off + 0.3) + RIGHT * x_off,
                    UP * (y_off - 0.3) + RIGHT * x_off,
                    color=PILL_BLUE, stroke_width=2, buff=0,
                    max_tip_length_to_length_ratio=0.3
                ).set_opacity(0.5)
                arrows.add(arr)

        # "DAY 5 vs DAY 14" -- ZONE_MID
        day5 = safe_text("DAY 5", font="Bebas Neue", font_size=70, color=GUT_GREEN)
        day5.move_to(LEFT * 2.0 + UP * ZONE_MID)
        arrow_mid = Arrow(LEFT * 0.3, RIGHT * 0.8, color=MUTED, stroke_width=2, buff=0)
        arrow_mid.move_to(UP * ZONE_MID)
        day14 = safe_text("DAY 14", font="Bebas Neue", font_size=70, color=DANGER_RED)
        day14.move_to(RIGHT * 2.2 + UP * ZONE_MID)
        plus9 = safe_text("+9 UNNECESSARY", font="Inter", font_size=22,
                         color=DANGER_RED, weight="BOLD")
        plus9.move_to(UP * (ZONE_MID - 1.0))

        # Gut bacteria under pressure -- ZONE_LOWER
        gut_field = bacteria_battlefield(rows=3, cols=7, h=2.2)
        gut_field.move_to(UP * ZONE_LOWER)

        pressure_lbl = safe_text("GUT UNDER PRESSURE", font="Inter",
                                font_size=22, color=WARN_ORANGE, weight="BOLD")
        pressure_lbl.move_to(UP * (ZONE_LOWER - 1.3))

        footer = safe_text("NOT JUST THE INFECTION", font="Inter",
                          font_size=20, color=DEAD_GRAY, weight="BOLD")
        footer.move_to(UP * ZONE_FOOTER)

        # -- Timing: 5.50s --
        # VTT 0.10: "The real driver is the opposite."
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(body_head), FadeIn(body_torso), run_time=0.4); t += 0.4

        # VTT 1.40: "Every extra day of antibiotics"
        self.play(FadeIn(healed_dot), FadeIn(healed_lbl), run_time=0.3); t += 0.3
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows],
                              lag_ratio=0.05), run_time=0.5)                # t=1.5

        # VTT 2.80: "puts pressure on bacteria throughout your entire body."
        self.play(FadeIn(day5, shift=RIGHT * 0.15), run_time=0.3); t += 0.3
        self.play(GrowArrow(arrow_mid), run_time=0.2); t += 0.2
        self.play(FadeIn(day14, shift=LEFT * 0.15), run_time=0.3); t += 0.3
        self.play(FadeIn(plus9, scale=1.05), run_time=0.3); t += 0.3

        # VTT 4.20: "Longer courses breed more resistance, not less."
        self.play(FadeIn(gut_field, scale=0.9), run_time=0.5); t += 0.5
        self.play(Flash(gut_field.get_center(), color=WARN_ORANGE,
                        line_length=0.3, num_lines=8, run_time=0.3))        # t=3.4

        # Bacteria pulse red under pressure
        self.play(*[d.animate.set_color(DANGER_RED).set_opacity(0.8)
                    for d in gut_field], run_time=0.5)                      # t=3.9
        self.play(FadeIn(pressure_lbl), run_time=0.3); t += 0.3
        self.play(FadeIn(footer), run_time=0.3); t += 0.3

        # Ambient: arrows pulse opacity
        self.play(arrows.animate.set_opacity(0.8), run_time=0.4); t += 0.4
        self.play(arrows.animate.set_opacity(0.3), run_time=0.3); t += 0.3

        target = getattr(self.__class__, 'DURATION', 8.9)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:])), run_time=0.3)


# ================================================================
# SCENE 4: THE EVIDENCE (17.5-24.0s = 6.50s)
# Zones: TITLE(pill) UPPER(120+ number) MID+LOWER(comparison rows) FOOTER(label)
# ================================================================
class Scene4_Reversal(Scene):
    DURATION = 10.5
    def construct(self):
        self.add(gradient_bg(g="#0A100A"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE EVIDENCE", color=GUT_GREEN, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # "120+" hero number -- ZONE_UPPER
        rct_num = safe_text("120+", font="Bebas Neue", font_size=160, color=GUT_GREEN)
        rct_num.move_to(UP * ZONE_UPPER)
        rct_lbl = safe_text("RANDOMIZED TRIALS", font="Inter", font_size=26,
                           color=MUTED, weight="BOLD")
        rct_lbl.move_to(UP * 1.8)

        # Comparison chart -- spans ZONE_MID through ZONE_LOWER
        comparisons = [
            ("PNEUMONIA", "3-5", "7-14", UP * 0.2),
            ("CYSTITIS", "3", "7", DOWN * 1.4),
            ("CELLULITIS", "6", "12", DOWN * 3.0),
        ]
        comp_rows = []
        equals_signs = []
        for name, short, long, pos in comparisons:
            nm = safe_text(name, font="Inter", font_size=22, color=MUTED, weight="BOLD")
            nm.move_to(pos + LEFT * 3.0)
            short_t = safe_text(short, font="Bebas Neue", font_size=60, color=GUT_GREEN)
            short_t.move_to(pos + LEFT * 0.8)
            eq = safe_text("=", font="Bebas Neue", font_size=50, color=GOLD)
            eq.move_to(pos)
            long_t = safe_text(long, font="Bebas Neue", font_size=60, color=DANGER_RED)
            long_t.move_to(pos + RIGHT * 1.2)
            days_short = safe_text("DAYS", font="Inter", font_size=16, color=DIM, weight="BOLD")
            days_short.move_to(pos + LEFT * 0.8 + DOWN * 0.45)
            days_long = safe_text("DAYS", font="Inter", font_size=16, color=DIM, weight="BOLD")
            days_long.move_to(pos + RIGHT * 1.2 + DOWN * 0.45)
            # Connecting line between rows
            sep = Line(LEFT * 3.5, RIGHT * 3.0, color=DIM,
                       stroke_width=0.5).set_opacity(0.3)
            sep.move_to(pos + DOWN * 0.7)
            row = VGroup(nm, short_t, long_t, days_short, days_long, sep)
            comp_rows.append(row)
            equals_signs.append(eq)

        shorter_lbl = safe_text("SHORTER = SAME OUTCOME", font="Bebas Neue",
                               font_size=45, color=GOLD)
        shorter_lbl.move_to(UP * (ZONE_LOWER - 1.0))

        footer = safe_text("SYSTEMATIC REVIEW DATA", font="Inter",
                          font_size=20, color=DEAD_GRAY, weight="BOLD")
        footer.move_to(UP * ZONE_FOOTER)

        # -- Timing: 6.50s --
        # VTT 0.10: "Over a hundred and twenty randomized trials"
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(rct_num, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(rct_num.get_center(), color=GUT_GREEN,
                        line_length=0.5, num_lines=10, run_time=0.3))       # t=1.1

        # VTT 1.70: "show shorter courses work just as well."
        self.play(FadeIn(rct_lbl), run_time=0.3); t += 0.3
        self.wait(0.6); t += 0.6

        # VTT 3.30: "Pneumonia: three to five days equals seven to fourteen."
        self.play(FadeIn(comp_rows[0], shift=LEFT * 0.2), run_time=0.4); t += 0.4
        self.play(FadeIn(equals_signs[0], scale=1.3), run_time=0.3); t += 0.3

        # VTT 4.70: "Cystitis: three days equals seven."
        self.wait(0.5); t += 0.5
        self.play(FadeIn(comp_rows[1], shift=LEFT * 0.2), run_time=0.4); t += 0.4
        self.play(FadeIn(equals_signs[1], scale=1.3), run_time=0.3); t += 0.3

        # VTT 5.70: "Cellulitis: six days equals twelve."
        self.wait(0.3); t += 0.3
        self.play(FadeIn(comp_rows[2], shift=LEFT * 0.2), run_time=0.4); t += 0.4
        self.play(FadeIn(equals_signs[2], scale=1.3), run_time=0.3); t += 0.3

        self.play(FadeIn(shorter_lbl, scale=1.05), run_time=0.5); t += 0.5
        self.play(Flash(shorter_lbl.get_center(), color=GOLD,
                        line_length=0.3, num_lines=8, run_time=0.3))        # t=5.7
        self.play(FadeIn(footer), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 10.5)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE ORIGIN MYTH (24.0-31.0s = 7.00s)
# Zones: TITLE(pill) UPPER(calendar strips) MID(ROMAN CALENDAR) LOWER(80 years) FOOTER(label)
# ================================================================
class Scene5_Evidence(Scene):
    DURATION = 11.3
    def construct(self):
        self.add(gradient_bg(g="#12100A"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE ORIGIN MYTH", color=CALENDAR_RUST, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # Calendar strip -- ZONE_UPPER: week 1
        cal_7 = calendar_strip(n_days=7, crossed=7, color=CALENDAR_RUST, h=0.65)
        cal_7.move_to(UP * 4.5)
        cal_lbl_7 = safe_text("WEEK 1", font="Inter", font_size=20,
                             color=CALENDAR_RUST, weight="BOLD")
        cal_lbl_7.move_to(UP * 3.8)

        # Week 2 (unnecessary)
        cal_14 = calendar_strip(n_days=7, crossed=7, color=DANGER_RED, h=0.65)
        cal_14.move_to(UP * 2.8)
        cal_lbl_14 = safe_text("WEEK 2", font="Inter", font_size=20,
                              color=DANGER_RED, weight="BOLD")
        cal_lbl_14.move_to(UP * 2.1)

        # Strike-through line over week 2
        strike = Line(LEFT * 2.2, RIGHT * 2.2, color=DANGER_RED, stroke_width=3)
        strike.move_to(cal_14)

        # "ROMAN CALENDAR" -- ZONE_MID
        roman = safe_text("ROMAN CALENDAR", font="Bebas Neue", font_size=80,
                         color=CALENDAR_RUST)
        roman.move_to(UP * ZONE_MID)

        not_science = safe_text("NOT SCIENCE", font="Bebas Neue", font_size=60,
                               color=DANGER_RED)
        not_science.move_to(UP * (ZONE_MID - 1.2))

        # "80 YEARS" -- ZONE_LOWER
        eighty = safe_text("80", font="Bebas Neue", font_size=130, color=WARN_ORANGE)
        eighty.move_to(UP * (ZONE_LOWER + 0.3))
        years_lbl = safe_text("YEARS OF EXTRA DAYS", font="Inter", font_size=24,
                             color=MUTED, weight="BOLD")
        years_lbl.move_to(UP * (ZONE_LOWER - 1.2))

        # Fading prescription bottles in background for visual depth
        ghost_bottles = VGroup()
        for gx, gy, gs in [(-2.8, -4.5, 0.6), (3.0, -5.0, 0.5), (0, -5.5, 0.4)]:
            gb = prescription_bottle(h=1.2 * gs, color=MUTED, label_txt="Rx")
            gb.move_to(RIGHT * gx + UP * gy).set_opacity(0.15)
            ghost_bottles.add(gb)

        footer = safe_text("CONVENTION, NOT EVIDENCE", font="Inter",
                          font_size=20, color=DEAD_GRAY, weight="BOLD")
        footer.move_to(UP * ZONE_FOOTER)

        # -- Timing: 7.00s --
        # VTT 0.10: "The seven-to-fourteen-day convention?"
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(cal_7, shift=DOWN * 0.1), run_time=0.5); t += 0.5
        self.play(FadeIn(cal_lbl_7), run_time=0.2); t += 0.2

        # VTT 1.80: "It traces to the Roman calendar,"
        self.play(FadeIn(cal_14, shift=DOWN * 0.1), run_time=0.5); t += 0.5
        self.play(FadeIn(cal_lbl_14), run_time=0.2); t += 0.2
        self.play(FadeIn(roman, scale=1.1), run_time=0.5); t += 0.5

        # VTT 3.00: "not science."
        self.play(FadeIn(not_science, scale=1.1), run_time=0.4); t += 0.4
        self.play(Create(strike), run_time=0.3); t += 0.3
        self.play(Flash(not_science.get_center(), color=DANGER_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))        # t=3.2

        # VTT 4.40: "For eighty years, doctors prescribed extra days"
        target = getattr(self.__class__, 'DURATION', 11.3)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeIn(eighty, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(eighty.get_center(), color=WARN_ORANGE,
                        line_length=0.5, num_lines=10, run_time=0.3))       # t=4.8
        self.play(FadeIn(years_lbl), run_time=0.3); t += 0.3

        # VTT 6.00: "that did nothing for the infection."
        self.play(LaggedStart(*[FadeIn(gb, scale=0.8) for gb in ghost_bottles],
                              lag_ratio=0.1), run_time=0.5)                 # t=5.6
        self.play(FadeIn(footer), run_time=0.3); t += 0.3

        # Ambient: eighty pulses
        self.play(eighty.animate.scale(1.06), run_time=0.4); t += 0.4
        self.play(eighty.animate.scale(1/1.06), run_time=0.4); t += 0.4

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE COST (31.0-41.0s = 10.00s)
# Zones: TITLE(pill) UPPER(gut bacteria turning red) MID(SELECTIVE PRESSURE) LOWER(ACCELERATED) FOOTER(punch)
# ================================================================
class Scene6_Cost(Scene):
    DURATION = 16.2
    def construct(self):
        self.add(gradient_bg("#050508"), grid_lines(0.02))
        t = 0

        pill = label_pill("THE COST", color=DANGER_RED, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # Gut bacteria field -- ZONE_UPPER
        gut_dots = VGroup()
        np.random.seed(77)
        for i in range(28):
            x = np.random.uniform(-3.5, 3.5)
            y = np.random.uniform(2.0, 5.0)
            r = np.random.uniform(0.08, 0.18)
            dot = Dot(np.array([x, y, 0]), radius=r, color=GUT_GREEN).set_opacity(0.6)
            gut_dots.add(dot)

        # Drug pressure arrows raining down
        pressure_arrows = VGroup()
        for x in np.linspace(-3, 3, 7):
            arr = Arrow(
                UP * 5.5 + RIGHT * x, UP * 2.0 + RIGHT * x,
                color=PILL_BLUE, stroke_width=1.5, buff=0,
                max_tip_length_to_length_ratio=0.2
            ).set_opacity(0.3)
            pressure_arrows.add(arr)

        # "SELECTIVE PRESSURE" -- ZONE_MID
        selective = safe_text("SELECTIVE PRESSURE", font="Bebas Neue",
                             font_size=70, color=WARN_ORANGE)
        selective.move_to(UP * ZONE_MID)

        on_gut = safe_text("ON YOUR GUT BACTERIA", font="Inter", font_size=24,
                          color=MUTED, weight="BOLD")
        on_gut.move_to(UP * (ZONE_MID - 0.9))

        # "ACCELERATED" big reveal -- ZONE_LOWER
        accelerated = safe_text("ACCELERATED", font="Bebas Neue", font_size=90,
                               color=DANGER_RED)
        accelerated.move_to(UP * (ZONE_LOWER + 0.5))

        glow = Circle(radius=2.5, fill_color=DANGER_RED, fill_opacity=0.08, stroke_width=0)
        glow.move_to(accelerated)

        the_crisis = safe_text("THE RESISTANCE CRISIS", font="Inter", font_size=26,
                              color=DANGER_RED, weight="BOLD")
        the_crisis.move_to(UP * (ZONE_LOWER - 1.0))

        # Exception note
        exceptions = safe_text("TB  |  ENDOCARDITIS  |  BONE", font="Inter",
                              font_size=18, color=DIM, weight="BOLD")
        exceptions.move_to(UP * (ZONE_FOOTER + 0.6))
        except_lbl = safe_text("EXCEPTIONS EXIST", font="Inter",
                              font_size=16, color=DIM)
        except_lbl.move_to(UP * (ZONE_FOOTER + 0.2))

        footer = safe_text("SHORTER IS BETTER.", font="Bebas Neue",
                          font_size=40, color=GOLD)
        footer.move_to(UP * ZONE_FOOTER)

        # -- Timing: 10.00s --
        # VTT 0.10: "but put selective pressure on your gut bacteria."
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(LaggedStart(*[FadeIn(d, scale=0.8) for d in gut_dots],
                              lag_ratio=0.02), run_time=0.5)                # t=0.8

        # Drug pressure arrives -- dots turn red
        self.play(LaggedStart(*[GrowArrow(a) for a in pressure_arrows],
                              lag_ratio=0.04), run_time=0.5)                # t=1.3
        self.play(*[d.animate.set_color(DANGER_RED).set_opacity(0.9)
                    for d in gut_dots], run_time=0.6)                        # t=1.9

        # VTT 2.40: "The advice meant to prevent resistance"
        self.play(FadeIn(selective, scale=1.05), run_time=0.5); t += 0.5
        self.play(FadeIn(on_gut), run_time=0.3); t += 0.3

        # Ambient: bacteria drift outward showing spread
        self.play(*[d.animate.shift(
            (d.get_center() - UP * ZONE_UPPER) * 0.08
        ) for d in gut_dots], run_time=0.8)                                  # t=3.5

        self.wait(1.0); t += 1.0

        # VTT 4.80: "may have accelerated it."
        self.play(FadeIn(glow), FadeIn(accelerated, scale=1.15), run_time=0.6); t += 0.6
        self.play(Flash(accelerated.get_center(), color=DANGER_RED,
                        line_length=0.5, num_lines=12, run_time=0.4))       # t=5.5
        self.play(FadeIn(the_crisis), run_time=0.3); t += 0.3

        # Exceptions + footer
        self.play(FadeIn(exceptions), FadeIn(except_lbl), run_time=0.3); t += 0.3
        self.play(FadeIn(footer, scale=1.05), run_time=0.4); t += 0.4

        # Hold + fade to black
        self.wait(1.5); t += 1.5
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.2); t += 1.2
        target = getattr(self.__class__, 'DURATION', 16.2)
        self.wait(max(0.1, target - t - 0.8))


# -- Infra -------------------------------------------------------------
SCENES = [Scene1_SacredRule, Scene2_Origin, Scene3_Logic, Scene4_Reversal, Scene5_Evidence, Scene6_Cost]

def render_single_scene(idx):
    config.output_file = f"finish_antibiotics_myth_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    SCENES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"finish_antibiotics_myth_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENES):
        n = f"finish_antibiotics_myth_scene_{i+1}"; print(f"  Preview {n}...")
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
    audio = od / "tts_finish_antibiotics_myth.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="finish_antibiotics_myth", audio_path=str(audio))
    final = od / "finish_antibiotics_myth_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))
    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
    from render_utils import run_post_render_qa
    run_post_render_qa(str(final), scene_count=6)
    from render_utils import make_short
    scene_ends = [6.0, 12.0, 17.5, 24.0, 31.0, 38.0]
    short, dur = make_short(str(final), scene_ends)
    print(f"  SHORT: {short} ({Path(short).stat().st_size/1024/1024:.1f} MB, {dur:.1f}s)")
