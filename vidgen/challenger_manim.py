#!/usr/bin/env python3
"""Challenger Disaster — Visual-first per PRODUCTION_GUIDE.md.

6 scenes, ~47.0s (44.0s audio + 3s hold).
Domain shapes: shuttle_silhouette, oring_ring, thermometer_bar, person_icon.
Visual throughline: the oring_ring appears in EVERY scene.

VTT cues (absolute → relative):
  Scene 1 (0.0–8.7s):   0.38 Seven people died... 3.68 NASA knew... 6.34 engineers begged
  Scene 2 (8.7–13.2s):  8.68 malfunction... 10.84 unforeseeable... 12.06 unpredictable
  Scene 3 (13.2–21.1s): 13.20 engineers warned... 15.78 O-rings cracked... 18.32 36 degrees
  Scene 4 (21.1–28.7s): 21.08 engineers told NASA... 24.30 reconsider... 26.24 overruled
  Scene 5 (28.7–35.2s): 28.66 children watched... 32.08 73 seconds... 33.92 O-ring failed
  Scene 6 (35.2–47.0s): 35.22 Feynman... 37.52 dropped O-ring... 40.04 cracked... 40.92 6 cent
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
config.background_color = "#0F172A"
config.disable_caching = True

BG = "#0F172A"; GRID = "#1E293B"; SURFACE = "#1E293B"
SHUTTLE_WHITE = "#F0F0F0"; RING_GOLD = "#D4A017"
DANGER_RED = "#EF4444"; CHECK_GREEN = "#22C55E"
BUREAUCRAT_GREY = "#64748B"; MUTED = "#475569"
GOLD = "#FFD700"; WHITE_SOFT = "#F0F0F0"; DEAD_GRAY = "#4A5568"
SAFE_W = 8.0


# ── Core helpers ─────────────────────────────────────────────

def gradient_bg(c=BG, g="#1E293B"):
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

def shuttle_silhouette(height=6, color=SHUTTLE_WHITE, angle=75):
    """Space Shuttle side profile — fuselage, wings, tail, boosters."""
    h = height; w = h * 0.25
    # Fuselage
    fuse = Polygon(
        np.array([0, h*0.5, 0]), np.array([w*0.3, h*0.45, 0]),
        np.array([w*0.35, h*0.1, 0]), np.array([w*0.3, -h*0.3, 0]),
        np.array([w*0.2, -h*0.5, 0]), np.array([-w*0.2, -h*0.5, 0]),
        np.array([-w*0.3, -h*0.3, 0]), np.array([-w*0.35, h*0.1, 0]),
        np.array([-w*0.3, h*0.45, 0]),
        fill_color=color, fill_opacity=0.9, stroke_color=MUTED, stroke_width=1.5,
    )
    # Wings
    wing_l = Polygon(
        np.array([-w*0.35, -h*0.1, 0]), np.array([-w*1.2, -h*0.35, 0]),
        np.array([-w*0.35, -h*0.25, 0]),
        fill_color=color, fill_opacity=0.7, stroke_color=MUTED, stroke_width=1,
    )
    wing_r = Polygon(
        np.array([w*0.35, -h*0.1, 0]), np.array([w*1.2, -h*0.35, 0]),
        np.array([w*0.35, -h*0.25, 0]),
        fill_color=color, fill_opacity=0.7, stroke_color=MUTED, stroke_width=1,
    )
    # Tail
    tail = Polygon(
        np.array([0, -h*0.25, 0]), np.array([w*0.1, -h*0.5, 0]),
        np.array([-w*0.1, -h*0.5, 0]),
        fill_color=color, fill_opacity=0.6, stroke_width=0,
    )
    grp = VGroup(fuse, wing_l, wing_r, tail)
    grp.rotate(angle * DEGREES)
    return grp

def oring_ring(radius=0.4, color=RING_GOLD, stroke_w=4):
    """Small rubber O-ring — the visual throughline."""
    ring = Circle(radius=radius, stroke_color=color, stroke_width=stroke_w,
                  fill_color=color, fill_opacity=0.15)
    return ring

def thermometer_bar(temp=70, max_temp=80, height=5, x=0, y=0):
    """Vertical temperature gauge with fill and reading."""
    # Outer tube
    tube = RoundedRectangle(width=0.6, height=height, corner_radius=0.2,
                            fill_color="#1A1A2A", fill_opacity=0.8,
                            stroke_color=MUTED, stroke_width=1.5)
    tube.move_to(np.array([x, y, 0]))
    # Fill
    fill_h = max(0.1, height * 0.85 * (temp / max_temp))
    color = CHECK_GREEN if temp > 53 else (GOLD if temp > 40 else DANGER_RED)
    fill = Rectangle(width=0.4, height=fill_h, fill_color=color, fill_opacity=0.8,
                     stroke_width=0)
    fill.align_to(tube, DOWN).shift(UP * height * 0.05)
    # Reading
    reading = safe_text(f"{temp}°F", font="Bebas Neue", font_size=36, color=color)
    reading.next_to(tube, RIGHT, buff=0.2)
    # Bulb at bottom
    bulb = Circle(radius=0.2, fill_color=color, fill_opacity=0.6, stroke_width=0)
    bulb.move_to(tube.get_bottom() + UP * 0.15)
    return VGroup(tube, fill, bulb, reading)

def person_icon(color=WHITE_SOFT, height=1.0):
    """Simple standing figure silhouette."""
    head = Circle(radius=height*0.1, fill_color=color, fill_opacity=0.8, stroke_width=0)
    head.move_to(UP * height * 0.35)
    body = Polygon(
        np.array([-height*0.12, height*0.22, 0]),
        np.array([height*0.12, height*0.22, 0]),
        np.array([height*0.1, -height*0.25, 0]),
        np.array([-height*0.1, -height*0.25, 0]),
        fill_color=color, fill_opacity=0.7, stroke_width=0,
    )
    return VGroup(head, body).scale_to_fit_height(height)


# ================================================================
# SCENE 1: THE HOOK (0.0–8.7s)
# Shuttle + crew dots + crack + O-ring pulse
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 8.2
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("JANUARY 28, 1986", color=DANGER_RED)
        pill.move_to(UP * 7)

        # Shuttle
        shuttle = shuttle_silhouette(height=5, color=SHUTTLE_WHITE, angle=75)
        shuttle.move_to(UP * 2)

        # 7 crew dots along fuselage
        crew = VGroup()
        for i in range(7):
            d = Dot(radius=0.08, color=SHUTTLE_WHITE).set_opacity(0.8)
            d.move_to(shuttle.get_center() + UP * (1.5 - i * 0.4) + RIGHT * 0.1)
            crew.add(d)

        # Crack line across shuttle
        crack = Line(shuttle.get_left() + RIGHT * 0.3, shuttle.get_right() + LEFT * 0.3,
                     color=DANGER_RED, stroke_width=2).set_opacity(0)
        crack.move_to(shuttle.get_center() + DOWN * 0.5)

        # O-ring — the throughline
        ring = oring_ring(0.5, DANGER_RED)
        ring.move_to(DOWN * 3.5)

        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(shuttle, scale=0.9), run_time=0.6); t += 0.6

        # Crew dots glow on in sequence
        self.play(
            LaggedStart(*[FadeIn(d, scale=2) for d in crew], lag_ratio=0.08),
            run_time=0.8,
        )                                                                   # t=1.8

        # VTT 3.68: "NASA knew it would happen" — crack appears
        self.wait(1.5); t += 1.5
        self.play(crack.animate.set_opacity(0.7), run_time=0.4); t += 0.4

        # VTT 6.34: "engineers begged" — O-ring fades in, pulsing
        self.wait(2.24); t += 2.24
        self.play(FadeIn(ring, scale=0.5), run_time=0.4); t += 0.4
        self.play(ring.animate.scale(1.15), run_time=0.3); t += 0.3
        self.play(ring.animate.scale(1/1.15), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 8.2)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 2: THE WRONG ANSWER (8.7–13.2s)
# Document + MALFUNCTION stamp + checkboxes
# ================================================================
class Scene2_WrongAnswer(Scene):
    DURATION = 4.2
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE OFFICIAL STORY", color=BUREAUCRAT_GREY)
        pill.move_to(UP * 7)

        # Document outline
        doc = RoundedRectangle(width=5.5, height=7, corner_radius=0.1,
                               stroke_color=BUREAUCRAT_GREY, stroke_width=1.5,
                               fill_color=SURFACE, fill_opacity=0.3)
        doc.move_to(UP * 1.5)
        seal = Circle(radius=0.4, stroke_color=BUREAUCRAT_GREY, stroke_width=1.5,
                      fill_opacity=0).move_to(doc.get_top() + DOWN * 0.8)

        # Redacted bars
        bars = VGroup()
        for i in range(4):
            bar = Rectangle(width=4, height=0.25, fill_color=BUREAUCRAT_GREY,
                            fill_opacity=0.4, stroke_width=0)
            bar.move_to(doc.get_center() + UP * (0.8 - i * 0.6))
            bars.add(bar)

        # "MALFUNCTION" stamp
        stamp_txt = safe_text("MALFUNCTION", font="Bebas Neue", font_size=55, color=DANGER_RED)
        stamp_border = RoundedRectangle(width=stamp_txt.width+0.4, height=stamp_txt.height+0.3,
                                        corner_radius=0.08, stroke_color=DANGER_RED, stroke_width=4,
                                        fill_opacity=0).move_to(stamp_txt)
        malfunction = VGroup(stamp_border, stamp_txt).rotate(-8 * DEGREES)
        malfunction.move_to(doc.get_center() + DOWN * 0.5)

        # O-ring (throughline) — small, in corner
        ring = oring_ring(0.3, DANGER_RED)
        ring.move_to(DOWN * 5.5 + RIGHT * 3)
        ring.set_opacity(0.3)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(doc), FadeIn(seal), run_time=0.4); t += 0.4
        self.play(
            LaggedStart(*[FadeIn(b, shift=RIGHT * 0.5) for b in bars], lag_ratio=0.1),
            run_time=0.5,
        )                                                                   # t=1.2

        # VTT 0.0 (rel): "NASA called it a malfunction" — stamp slams
        self.play(FadeIn(malfunction, scale=2.5), run_time=0.2); t += 0.2
        self.play(Flash(malfunction.get_center(), color=DANGER_RED,
                        line_length=0.3, num_lines=8, run_time=0.2))       # t=1.6
        self.add(ring)
        target = getattr(self.__class__, 'DURATION', 4.2)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 3: THE CONTRADICTION (13.2–21.1s)
# O-ring cracking + thermometer dropping
# ================================================================
class Scene3_Contradiction(Scene):
    DURATION = 7.4
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE EVIDENCE", color=DANGER_RED)
        pill.move_to(UP * 7)

        # Large O-ring (left side)
        ring = oring_ring(1.5, RING_GOLD, stroke_w=6)
        ring.move_to(LEFT * 1.5 + UP * 2.5)

        # Crack line (hidden initially)
        crack = Line(ring.get_left() + RIGHT * 0.3 + UP * 0.2,
                     ring.get_right() + LEFT * 0.3 + DOWN * 0.2,
                     color=DANGER_RED, stroke_width=4).set_opacity(0)
        crack.move_to(ring)

        # Thermometer (right side) — starts at 70, drops to 36
        therm_70 = thermometer_bar(70, 80, height=5, x=2.5, y=2.5)
        therm_36 = thermometer_bar(36, 80, height=5, x=2.5, y=2.5)

        # "36°F AT LAUNCH" text
        temp_text = safe_text("36°F AT LAUNCH", font="Bebas Neue", font_size=60, color=DANGER_RED)
        temp_text.move_to(DOWN * 2)

        # Small O-ring throughline at bottom
        ring_small = oring_ring(0.3, DANGER_RED)
        ring_small.move_to(DOWN * 5)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(ring, scale=0.8), run_time=0.5); t += 0.5

        # Ring wobbles (flexible)
        self.play(ring.animate.scale(1.05), run_time=0.2); t += 0.2
        self.play(ring.animate.scale(1/1.05), run_time=0.2); t += 0.2
        self.play(ring.animate.scale(1.03), run_time=0.2); t += 0.2
        self.play(ring.animate.scale(1/1.03), run_time=0.2); t += 0.2

        # Thermometer appears at 70
        self.play(FadeIn(therm_70), run_time=0.4); t += 0.4

        # VTT 2.58: "O-rings cracked in cold weather"
        # Temperature drops 70→36
        self.wait(0.6); t += 0.6
        self.play(therm_70.animate.become(therm_36), run_time=2.0); t += 2.0

        # O-ring stiffens and cracks at 36°
        self.play(crack.animate.set_opacity(1), run_time=0.3); t += 0.3
        self.play(Flash(ring.get_center(), color=DANGER_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=5.2
        self.play(ring.animate.set_color(DANGER_RED), run_time=0.3); t += 0.3

        self.play(FadeIn(temp_text, scale=1.1), run_time=0.5); t += 0.5
        self.play(FadeIn(ring_small), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 7.4)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 4: THE DECISION (21.1–28.7s)
# Engineers X's → managers override → O-ring ignored
# ================================================================
class Scene4_Decision(Scene):
    DURATION = 7.1
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE DECISION", color=DANGER_RED)
        pill.move_to(UP * 7)

        # Engineers (left) — 5 figures with red X's
        engineers = VGroup()
        x_marks = VGroup()
        for i in range(5):
            p = person_icon(SHUTTLE_WHITE, 1.0)
            p.move_to(LEFT * 3 + RIGHT * i * 0.8 + UP * 4)
            engineers.add(p)
            x = safe_text("✕", font="Inter", font_size=30, color=DANGER_RED)
            x.move_to(p.get_top() + UP * 0.3)
            x_marks.add(x)

        eng_label = safe_text("ENGINEERS", font="Inter", font_size=20, color=SHUTTLE_WHITE, weight="BOLD")
        eng_label.move_to(LEFT * 1.5 + UP * 2.5)

        # Managers (right) — 3 figures with green checks
        managers = VGroup()
        checks = VGroup()
        for i in range(3):
            p = person_icon(BUREAUCRAT_GREY, 1.2)
            p.move_to(RIGHT * 1.5 + RIGHT * i * 1.0 + UP * 4)
            managers.add(p)
            c = safe_text("✓", font="Inter", font_size=30, color=CHECK_GREEN)
            c.move_to(p.get_top() + UP * 0.3)
            checks.add(c)

        mgr_label = safe_text("MANAGEMENT", font="Inter", font_size=20, color=BUREAUCRAT_GREY, weight="BOLD")
        mgr_label.move_to(RIGHT * 2.5 + UP * 2.5)

        # Divider
        split = DashedLine(UP * 5.5, UP * 2, color=MUTED, stroke_width=1, dash_length=0.15)
        split.move_to(UP * 3.5 + RIGHT * 0)

        # "OVERRULED" — the X's flip to checks
        overruled = safe_text("OVERRULED", font="Bebas Neue", font_size=80, color=DANGER_RED)
        overruled.move_to(DOWN * 0.5)

        # O-ring at bottom — cracked, ignored
        ring = oring_ring(0.4, DANGER_RED)
        ring.move_to(DOWN * 4)
        crack = Line(ring.get_left() + RIGHT * 0.1, ring.get_right() + LEFT * 0.1,
                     color=DANGER_RED, stroke_width=3)
        crack.move_to(ring)
        ignored = VGroup(ring, crack)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(
            LaggedStart(*[FadeIn(e, shift=UP * 0.1) for e in engineers], lag_ratio=0.06),
            run_time=0.4,
        )                                                                   # t=0.7
        self.play(LaggedStart(*[FadeIn(x) for x in x_marks], lag_ratio=0.06), run_time=0.3); t += 0.3
        self.play(FadeIn(eng_label), run_time=0.2); t += 0.2
        self.play(Create(split), run_time=0.3); t += 0.3

        # VTT ~3.2 (rel): "NASA asked them to reconsider"
        self.wait(1.5); t += 1.5
        self.play(
            LaggedStart(*[FadeIn(m, shift=UP * 0.1) for m in managers], lag_ratio=0.08),
            run_time=0.4,
        )                                                                   # t=3.4
        self.play(LaggedStart(*[FadeIn(c) for c in checks], lag_ratio=0.08), run_time=0.3); t += 0.3
        self.play(FadeIn(mgr_label), run_time=0.2); t += 0.2

        # VTT ~5.14 (rel): "Their managers overruled them" — X's flip to checks
        self.wait(0.94); t += 0.94
        for xm in x_marks:
            new_check = safe_text("✓", font="Inter", font_size=30, color=CHECK_GREEN)
            new_check.move_to(xm)
            self.play(xm.animate.become(new_check), run_time=0.15); t += 0.15

        # t=5.59
        self.play(FadeIn(overruled, scale=1.15), run_time=0.4); t += 0.4
        self.play(Flash(overruled.get_center(), color=DANGER_RED,
                        line_length=0.3, num_lines=8, run_time=0.3))       # t=6.29

        # O-ring sits ignored at bottom
        self.play(FadeIn(ignored), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 7.1)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 5: THE LAUNCH (28.7–35.2s)
# Shuttle ascending → 73 counter → O-ring snaps → fragments
# ================================================================
class Scene5_Launch(Scene):
    DURATION = 6.1
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # Shuttle at bottom, ascending
        shuttle = shuttle_silhouette(height=3.5, color=SHUTTLE_WHITE, angle=0)
        shuttle.move_to(DOWN * 3)

        # Crowd of children (person icons)
        crowd = VGroup()
        for i in range(12):
            p = person_icon(MUTED, 0.5)
            p.move_to(LEFT * 3.5 + RIGHT * i * 0.6 + DOWN * 6)
            p.set_opacity(0.4)
            crowd.add(p)

        # Exhaust trail
        exhaust = DashedLine(DOWN * 5, DOWN * 8, color=SHUTTLE_WHITE,
                             stroke_width=3, dash_length=0.3).set_opacity(0.3)

        # Counter
        counter_pos = DOWN * 5 + LEFT * 3

        # O-ring on booster
        ring = oring_ring(0.25, RING_GOLD, 3)
        ring.move_to(shuttle.get_bottom() + DOWN * 0.3)

        # Fragments (hidden initially)
        frags = VGroup()
        for dx, dy, ang in [(-1, 0.5, 30), (0.8, 0.3, -20), (-0.5, -0.8, 45),
                            (1, -0.5, -35), (0, 1, 15)]:
            f = Rectangle(width=0.4, height=0.2, fill_color=SHUTTLE_WHITE,
                          fill_opacity=0.6, stroke_width=0)
            f.rotate(ang * DEGREES)
            frags.add(f)

        self.play(FadeIn(crowd), run_time=0.3); t += 0.3
        self.play(FadeIn(shuttle, shift=UP * 0.3), FadeIn(ring), run_time=0.5); t += 0.5

        # Shuttle ascends
        self.add(exhaust)
        self.play(
            shuttle.animate.shift(UP * 5),
            ring.animate.shift(UP * 5),
            exhaust.animate.shift(UP * 3),
            run_time=2.5,
        )                                                                   # t=3.3

        # Counter: "73 SECONDS"
        counter = safe_text("73", font="Bebas Neue", font_size=100, color=DANGER_RED)
        counter.move_to(UP * 0)
        seconds = safe_text("SECONDS", font="Inter", font_size=30, color=MUTED, weight="BOLD")
        seconds.next_to(counter, DOWN, buff=0.2)

        self.play(FadeIn(counter, scale=1.2), FadeIn(seconds), run_time=0.5); t += 0.5

        # VTT ~5.22 (rel): "the O-ring failed" — ring snaps, shuttle fragments
        self.wait(1.0); t += 1.0
        self.play(Flash(ring.get_center(), color=DANGER_RED,
                        line_length=0.5, num_lines=12, run_time=0.2))      # t=5.0

        # Shuttle splits into fragments
        for f in frags:
            f.move_to(shuttle.get_center())
        self.play(FadeOut(shuttle), FadeOut(ring), FadeIn(frags), run_time=0.15); t += 0.15

        # Fragments drift apart slowly
        self.play(
            *[f.animate.shift(np.array([dx, dy, 0]) * 2) for f, (dx, dy, _) in
              zip(frags, [(-1, 0.5, 0), (0.8, 0.3, 0), (-0.5, -0.8, 0),
                          (1, -0.5, 0), (0, 1, 0)])],
            run_time=1.0,
        )                                                                   # t=6.15

        # Crowd stays frozen. Silence.
        target = getattr(self.__class__, 'DURATION', 6.1)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 6: THE PUNCH (35.2–47.0s)
# Glass + O-ring drops in → cracks → "6¢"
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 11.1
    def construct(self):
        self.add(gradient_bg("#0A1020"))
        t = 0

        # Letterbox
        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP*(8-bh/2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN*(8-bh/2)),
        )
        self.add(grid_lines(0.02))

        # Glass of ice water
        glass = Rectangle(width=1.5, height=2.5, fill_color="#1A2A4A", fill_opacity=0.4,
                          stroke_color=MUTED, stroke_width=2)
        glass.move_to(UP * 1)
        water = Rectangle(width=1.3, height=1.8, fill_color="#2563EB", fill_opacity=0.25,
                          stroke_width=0)
        water.align_to(glass, DOWN).shift(UP * 0.15)
        ice1 = Square(side_length=0.25, fill_color=WHITE_SOFT, fill_opacity=0.3,
                      stroke_width=0).move_to(glass.get_center() + LEFT * 0.2 + UP * 0.3)
        ice2 = Square(side_length=0.2, fill_color=WHITE_SOFT, fill_opacity=0.25,
                      stroke_width=0).move_to(glass.get_center() + RIGHT * 0.3 + UP * 0.1)

        # O-ring (starts above, drops in)
        ring = oring_ring(0.5, RING_GOLD, 5)
        ring.move_to(UP * 5)

        # Crack (hidden)
        crack = Line(ring.get_left() + RIGHT * 0.1, ring.get_right() + LEFT * 0.1,
                     color=DANGER_RED, stroke_width=4)

        # "6¢" text
        six_cents = safe_text("6¢", font="Bebas Neue", font_size=120, color=RING_GOLD)
        six_cents.move_to(DOWN * 3)

        ignored = safe_text("That is what they ignored.", font="DM Serif Display",
                           font_size=38, color=MUTED)
        ignored.move_to(DOWN * 5)

        # ── Timing: 11.80s ──
        self.play(FadeIn(glass), FadeIn(water), FadeIn(ice1), FadeIn(ice2),
                  run_time=0.6)                                             # t=0.6

        # VTT 2.32 (rel): "He dropped an O-ring in a glass of ice water"
        self.wait(1.42); t += 1.42
        # O-ring drops slowly into glass
        ring.generate_target()
        ring.target.move_to(glass.get_center())
        self.play(MoveToTarget(ring), run_time=1.2,
                  rate_func=rate_functions.ease_in_cubic); t += 1.2

        # Ring sits in water
        self.wait(0.8); t += 0.8

        # VTT 4.84 (rel): "It cracked."
        crack.move_to(ring)
        self.play(Create(crack), run_time=0.2); t += 0.2
        self.play(Flash(ring.get_center(), color=DANGER_RED,
                        line_length=0.3, num_lines=6, run_time=0.2))       # t=4.42

        # Ring breaks in half — shift two halves apart
        left_half = ring.copy().shift(LEFT * 0.15).set_opacity(0.6)
        right_half = ring.copy().shift(RIGHT * 0.15).set_opacity(0.6)
        self.play(FadeOut(ring), FadeIn(left_half), FadeIn(right_half), run_time=0.3); t += 0.3

        # VTT 5.72 (rel): "A six cent rubber ring"
        self.wait(0.68); t += 0.68
        self.play(FadeIn(six_cents, scale=1.2), run_time=0.6); t += 0.6
        self.play(Flash(six_cents.get_center(), color=RING_GOLD,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=6.30

        # VTT 7.72: "That is what they ignored"
        self.wait(1.12); t += 1.12
        self.play(FadeIn(ignored, shift=UP * 0.04), run_time=0.6); t += 0.6

        # Hold — stillness
        target = getattr(self.__class__, 'DURATION', 11.1)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5


# ── Infra ─────────────────────────────────────────────────────
SCENES = [Scene1_Hook, Scene2_WrongAnswer, Scene3_Contradiction,
          Scene4_Decision, Scene5_Launch, Scene6_Punch]

def render_single_scene(idx):
    config.output_file = f"challenger_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    SCENES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"challenger_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENES):
        n = f"challenger_scene_{i+1}"; print(f"  Preview {n}...")
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
    audio = od / "tts_challenger.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="challenger", audio_path=str(audio))
    final = od / "challenger_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")

    from render_utils import run_post_render_qa
    run_post_render_qa(str(final), scene_count=6)

    from render_utils import make_short
    scene_ends = [8.7, 13.2, 21.1, 28.7, 35.2, 47.0]
    short, dur = make_short(str(final), scene_ends)
    print(f"  SHORT: {short} ({Path(short).stat().st_size/1024/1024:.1f} MB, {dur:.1f}s)")
