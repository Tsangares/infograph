#!/usr/bin/env python3
"""Ambition Installed — Visual-first per PRODUCTION_GUIDE.md.

6 scenes, ~40s total.
Domain shapes: compass_needle, chest_silhouette, signal_tower, block_tower.
Visual throughline: the compass_needle appears in EVERY scene.

VTT cues (absolute → relative):
  Scene 1 (0.0–6.5s):   0.0 You learn what success is... 3.0 compass needle...
  Scene 2 (6.5–13.5s):  6.5 But look closer... 10.0 ambition maps...
  Scene 3 (13.5–19.5s): 13.5 The child in a family... 16.0 medicine is the tall tower...
  Scene 4 (19.5–26.0s): 19.5 The child scrolling... 22.0 visibility is arrival...
  Scene 5 (26.0–33.0s): 26.0 None of them chose... 29.0 metrics were already...
  Scene 6 (33.0–40.0s): 33.0 The first crack... 36.0 compass was magnetized...
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """You learn what success is long before you learn to question it.
It arrives in childhood like a compass needle, pointing somewhere you haven't been yet but are certain exists.
But look closer, and the compass starts to wobble.
What you thought was inner orientation turns out to be an echo.
Your ambition maps suspiciously well onto the ambitions of the people around you, the images you consumed, the stories you were told.
The child in a family of doctors learns medicine is the tall tower.
The child scrolling curated lives learns visibility is arrival.
None of them chose their metrics.
The metrics were already in the room when they arrived.
The first crack in success is the recognition that the compass was magnetized by someone else's field."""

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
WHITE_SOFT = "#F0F0F0"; GOLD = "#FFD700"
COMPASS_BLUE = "#3B82F6"; SIGNAL_CYAN = "#06B6D4"
ECHO_RED = "#EF4444"; INSTALLED_AMBER = "#F59E0B"
MUTED = "#475569"; DIM = "#334155"; DEAD_GRAY = "#4A5568"
SAFE_W = 8.0

ZONE_TITLE = 6.2; ZONE_UPPER = 3.5; ZONE_MID = 0.0
ZONE_LOWER = -3.5; ZONE_FOOTER = -6.0


# ── Core helpers ─────────────────────────────────────────────

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

def compass_needle(height=2.0, color=COMPASS_BLUE):
    """Compass needle — diamond pointer shape, the visual throughline."""
    h = height
    needle = Polygon(
        np.array([0, h * 0.5, 0]),
        np.array([h * 0.08, 0, 0]),
        np.array([0, -h * 0.5, 0]),
        np.array([-h * 0.08, 0, 0]),
        fill_color=color, fill_opacity=0.9, stroke_color=WHITE_SOFT, stroke_width=1,
    )
    # Red north tip
    tip = Polygon(
        np.array([0, h * 0.5, 0]),
        np.array([h * 0.08, 0, 0]),
        np.array([-h * 0.08, 0, 0]),
        fill_color=ECHO_RED, fill_opacity=0.8, stroke_width=0,
    )
    pivot = Dot(radius=h * 0.04, color=WHITE_SOFT)
    ring = Circle(radius=h * 0.55, stroke_color=MUTED, stroke_width=1.5,
                  fill_opacity=0)
    return VGroup(ring, needle, tip, pivot)

def chest_silhouette(height=4.0, color=WHITE_SOFT):
    """Human torso silhouette — head + shoulders + body."""
    h = height
    head = Circle(radius=h * 0.1, fill_color=color, fill_opacity=0.3, stroke_width=0)
    head.move_to(UP * h * 0.4)
    neck = Rectangle(width=h * 0.06, height=h * 0.06, fill_color=color,
                     fill_opacity=0.2, stroke_width=0).move_to(UP * h * 0.3)
    body = Polygon(
        np.array([-h * 0.22, h * 0.28, 0]),
        np.array([h * 0.22, h * 0.28, 0]),
        np.array([h * 0.18, -h * 0.15, 0]),
        np.array([h * 0.25, -h * 0.5, 0]),
        np.array([h * 0.08, -h * 0.5, 0]),
        np.array([0, -h * 0.3, 0]),
        np.array([-h * 0.08, -h * 0.5, 0]),
        np.array([-h * 0.25, -h * 0.5, 0]),
        np.array([-h * 0.18, -h * 0.15, 0]),
        fill_color=color, fill_opacity=0.2, stroke_color=color, stroke_width=1, stroke_opacity=0.4,
    )
    return VGroup(body, neck, head)

def signal_tower(height=2.5, color=SIGNAL_CYAN):
    """Radio/signal tower — antenna with radiating arcs."""
    h = height
    pole = Line(DOWN * h * 0.5, UP * h * 0.35, color=color, stroke_width=2.5)
    base_l = Line(np.array([0, -h * 0.5, 0]), np.array([-h * 0.15, -h * 0.5, 0]),
                  color=color, stroke_width=2)
    base_r = Line(np.array([0, -h * 0.5, 0]), np.array([h * 0.15, -h * 0.5, 0]),
                  color=color, stroke_width=2)
    tip = Dot(radius=h * 0.03, color=color).move_to(UP * h * 0.38)
    # Radiating arcs
    arcs = VGroup()
    for i in range(3):
        r = h * (0.12 + i * 0.1)
        arc = Arc(radius=r, start_angle=30 * DEGREES, angle=120 * DEGREES,
                  color=color, stroke_width=1.5).set_opacity(0.6 - i * 0.15)
        arc.move_to(UP * h * 0.35)
        arcs.add(arc)
    return VGroup(pole, base_l, base_r, tip, arcs)

def block_tower(height=2.0, color=INSTALLED_AMBER):
    """Child's block tower — stacked colorful rectangles, freeform."""
    blocks = VGroup()
    colors = [COMPASS_BLUE, INSTALLED_AMBER, SIGNAL_CYAN, ECHO_RED]
    widths = [0.8, 0.6, 0.7, 0.4]
    y = -height * 0.4
    for i in range(4):
        bh = height * 0.18
        b = Rectangle(width=widths[i], height=bh, fill_color=colors[i],
                      fill_opacity=0.7, stroke_color=WHITE_SOFT, stroke_width=0.8)
        b.move_to(UP * y + RIGHT * ((-1)**i) * 0.05)
        blocks.add(b)
        y += bh + 0.02
    return blocks


# ================================================================
# SCENE 1: THE HOOK (0.0–6.5s)
# Compass in chest, dozens of identical silhouettes
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 7.2
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("YOUR DREAMS WERE NEVER YOURS", color=ECHO_RED)
        pill.move_to(UP * ZONE_TITLE)

        # Central silhouette with compass
        sil = chest_silhouette(height=4.5, color=WHITE_SOFT)
        sil.move_to(UP * 0.5)
        needle = compass_needle(height=1.2, color=COMPASS_BLUE)
        needle.move_to(sil.get_center() + DOWN * 0.3)

        # Trophy icon the needle points to
        trophy_base = Rectangle(width=0.6, height=0.15, fill_color=GOLD,
                                fill_opacity=0.8, stroke_width=0).move_to(UP * 3.8)
        trophy_cup = Arc(radius=0.4, start_angle=0, angle=PI, color=GOLD,
                         stroke_width=3).move_to(UP * 4.1)
        trophy = VGroup(trophy_base, trophy_cup)

        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(sil, scale=0.95), run_time=0.6); t += 0.6
        self.play(FadeIn(needle, scale=0.5), run_time=0.5); t += 0.5
        self.play(FadeIn(trophy, scale=1.1), run_time=0.4); t += 0.4

        # Needle glows with confidence
        self.play(needle.animate.scale(1.1).set_opacity(1), run_time=0.4); t += 0.4
        self.play(needle.animate.scale(1/1.1), run_time=0.3); t += 0.3

        self.wait(1.0); t += 1.0

        # Pull back: crowd of identical silhouettes — all with same compass
        crowd = VGroup()
        positions = [
            (-3.2, -3), (-1.6, -3.5), (0, -4), (1.6, -3.5), (3.2, -3),
            (-2.4, -5), (-0.8, -5.2), (0.8, -5.2), (2.4, -5),
        ]
        for x, y in positions:
            s = chest_silhouette(height=1.2, color=DIM)
            n = compass_needle(height=0.35, color=COMPASS_BLUE)
            s.move_to(RIGHT * x + UP * y)
            n.move_to(s.get_center())
            crowd.add(VGroup(s, n))

        self.play(
            LaggedStart(*[FadeIn(c, scale=0.8) for c in crowd], lag_ratio=0.06),
            run_time=1.2,
        )                                                                 # t=4.8

        target = getattr(self.__class__, 'DURATION', 7.2)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 2: THE MYSTERY (6.5–13.5s)
# Child building blocks, signal towers reshaping compass
# ================================================================
class Scene2_Mystery(Scene):
    DURATION = 7.7
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE ECHO", color=SIGNAL_CYAN)
        pill.move_to(UP * ZONE_TITLE)

        # Child silhouette with block tower
        child = chest_silhouette(height=2.0, color=WHITE_SOFT)
        child.move_to(UP * 1.5 + LEFT * 0.5)
        tower = block_tower(height=1.5, color=INSTALLED_AMBER)
        tower.move_to(UP * 1.5 + RIGHT * 1.5)

        # Compass in child's chest
        child_needle = compass_needle(height=0.6, color=COMPASS_BLUE)
        child_needle.move_to(child.get_center())

        # Signal towers (parent, teacher, screen)
        labels = ["PARENT", "TEACHER", "SCREEN"]
        tower_positions = [(-3.0, 3.0), (0, 4.0), (3.0, 3.0)]
        towers = VGroup()
        tower_labels = VGroup()
        for (x, y), lbl in zip(tower_positions, labels):
            lbl_mob = signal_tower(height=1.5, color=SIGNAL_CYAN)
            lbl_mob.move_to(RIGHT * x + UP * y)
            towers.add(lbl_mob)
            lb = safe_text(lbl, font="Inter", font_size=20, color=SIGNAL_CYAN)
            lb.next_to(t, DOWN, buff=0.15)
            tower_labels.add(lb)

        # Signal lines from towers to child
        signals = VGroup()
        for t in towers:
            line = DashedLine(t.get_bottom(), child_needle.get_center(),
                              color=SIGNAL_CYAN, stroke_width=1, dash_length=0.15)
            line.set_opacity(0.4)
            signals.add(line)

        # Timeline bar at bottom
        timeline_bg = Rectangle(width=7, height=0.3, fill_color=SURFACE,
                                fill_opacity=0.8, stroke_width=0).move_to(UP * ZONE_LOWER)
        ages = ["0", "5", "10", "15"]
        age_labels = VGroup()
        for i, a in enumerate(ages):
            lbl = safe_text(a, font="Bebas Neue", font_size=28, color=MUTED)
            lbl.move_to(timeline_bg.get_left() + RIGHT * (i * 2.33 + 0.5))
            age_labels.add(lbl)
        fill_bar = Rectangle(width=0.1, height=0.25, fill_color=COMPASS_BLUE,
                             fill_opacity=0.6, stroke_width=0)
        fill_bar.align_to(timeline_bg, LEFT).shift(RIGHT * 0.05)
        fill_bar.move_to(timeline_bg.get_center(), coor_mask=UP)

        # Footer
        caption = safe_text("THE COMPASS ROTATES TO MATCH", font="Inter",
                            font_size=22, color=MUTED)
        caption.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(child, scale=0.9), FadeIn(tower, scale=0.9),
                  run_time=0.5)                                           # t=0.9
        self.play(FadeIn(child_needle, scale=0.5), run_time=0.4); t += 0.4

        self.play(
            LaggedStart(*[FadeIn(t, scale=0.8) for t in towers], lag_ratio=0.1),
            LaggedStart(*[FadeIn(l, shift=UP*0.1) for l in tower_labels], lag_ratio=0.1),
            run_time=0.8,
        )                                                                 # t=2.1

        self.play(
            LaggedStart(*[Create(s) for s in signals], lag_ratio=0.1),
            run_time=0.6,
        )                                                                 # t=2.7

        # Needle rotates — external influence
        self.play(child_needle.animate.rotate(45 * DEGREES), run_time=0.6); t += 0.6

        self.wait(0.7); t += 0.7

        # Timeline appears
        self.play(FadeIn(timeline_bg), FadeIn(age_labels), run_time=0.4); t += 0.4
        self.play(fill_bar.animate.stretch_to_fit_width(6.9), run_time=1.2); t += 1.2

        # Tower morphs: blocks rearrange into dollar sign shape
        self.play(tower.animate.set_color(GOLD).scale(0.8), run_time=0.4); t += 0.4

        self.play(FadeIn(caption, shift=UP * 0.1), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 7.7)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 3: THE WRONG ANSWER (13.5–19.5s)
# Brain as origin — the myth of autonomous desire
# ================================================================
class Scene3_WrongAnswer(Scene):
    DURATION = 6.6
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE WRONG ANSWER", color=INSTALLED_AMBER)
        pill.move_to(UP * ZONE_TITLE)

        # Brain icon at center — pulsing with light
        brain_outer = Circle(radius=1.8, fill_color=COMPASS_BLUE, fill_opacity=0.1,
                             stroke_color=COMPASS_BLUE, stroke_width=2)
        brain_inner = Circle(radius=1.2, fill_color=COMPASS_BLUE, fill_opacity=0.15,
                             stroke_width=0)
        brain_core = Circle(radius=0.5, fill_color=COMPASS_BLUE, fill_opacity=0.3,
                            stroke_width=0)
        brain_label = safe_text("INNER DRIVE", font="Inter", font_size=26,
                                color=COMPASS_BLUE, weight="BOLD")
        brain_label.move_to(DOWN * 0.05)
        brain = VGroup(brain_outer, brain_inner, brain_core, brain_label)
        brain.move_to(UP * ZONE_MID + UP * 0.5)

        # Arrows pointing OUTWARD from brain to targets
        targets_data = [
            (LEFT * 3 + UP * 3.5, "CAREER", GOLD),
            (RIGHT * 3 + UP * 3.5, "MONEY", GOLD),
            (LEFT * 3.5 + DOWN * 2, "STATUS", GOLD),
            (RIGHT * 3.5 + DOWN * 2, "FAME", GOLD),
        ]
        arrows = VGroup()
        target_labels = VGroup()
        for pos, txt, col in targets_data:
            arr = Arrow(brain.get_center(), pos, color=col, stroke_width=2,
                        buff=1.5, max_tip_length_to_length_ratio=0.15)
            arrows.add(arr)
            lb = safe_text(txt, font="Inter", font_size=22, color=col, weight="BOLD")
            lb.move_to(pos)
            target_labels.add(lb)

        # Confidence meter at bottom
        meter_bg = Rectangle(width=5, height=0.4, fill_color=SURFACE,
                             fill_opacity=0.8, stroke_width=0).move_to(UP * ZONE_LOWER)
        meter_fill = Rectangle(width=0.1, height=0.35, fill_color=COMPASS_BLUE,
                               fill_opacity=0.7, stroke_width=0)
        meter_fill.align_to(meter_bg, LEFT).shift(RIGHT * 0.05)
        meter_fill.move_to(meter_bg.get_center(), coor_mask=UP)
        meter_label = safe_text("CONFIDENCE: 100%", font="Inter", font_size=22,
                                color=COMPASS_BLUE)
        meter_label.next_to(meter_bg, DOWN, buff=0.2)

        # Footer
        caption = safe_text("AUTONOMOUS DESIRE", font="Inter",
                            font_size=20, color=MUTED)
        caption.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(brain, scale=0.8), run_time=0.6); t += 0.6

        # Brain pulses
        self.play(brain_core.animate.scale(1.3).set_opacity(0.5), run_time=0.3); t += 0.3
        self.play(brain_core.animate.scale(1/1.3).set_opacity(0.3), run_time=0.3); t += 0.3

        # Arrows shoot outward
        self.play(
            LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.1),
            run_time=0.8,
        )                                                                 # t=2.4
        self.play(
            LaggedStart(*[FadeIn(l, scale=1.1) for l in target_labels], lag_ratio=0.08),
            run_time=0.6,
        )                                                                 # t=3.0

        self.wait(1.0); t += 1.0

        # Confidence meter fills
        self.play(FadeIn(meter_bg), run_time=0.3); t += 0.3
        self.play(meter_fill.animate.stretch_to_fit_width(4.9), run_time=0.8); t += 0.8
        self.play(FadeIn(meter_label, shift=UP * 0.1), run_time=0.3); t += 0.3
        self.play(FadeIn(caption, shift=UP * 0.1), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 6.6)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 4: THE CONTRADICTION (19.5–26.0s)
# Arrows reverse — external sources fire INTO the brain
# ================================================================
class Scene4_Contradiction(Scene):
    DURATION = 7.2
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("INSTALLED DRIVE", color=ECHO_RED)
        pill.move_to(UP * ZONE_TITLE)

        # Brain at center — will crack
        brain_outer = Circle(radius=1.5, fill_color=COMPASS_BLUE, fill_opacity=0.1,
                             stroke_color=COMPASS_BLUE, stroke_width=2)
        brain_label = safe_text("INNER DRIVE", font="Inter", font_size=24,
                                color=COMPASS_BLUE, weight="BOLD")
        brain = VGroup(brain_outer, brain_label)
        brain.move_to(UP * ZONE_MID + UP * 0.5)

        # External sources — pointing INWARD
        sources_data = [
            (LEFT * 3 + UP * 3.5, "TV"),
            (RIGHT * 3 + UP * 3.5, "PARENT"),
            (LEFT * 3.5 + DOWN * 2, "SOCIAL"),
            (RIGHT * 3.5 + DOWN * 2, "SCHOOL"),
        ]
        source_icons = VGroup()
        source_labels = VGroup()
        inward_arrows = VGroup()
        for pos, txt in sources_data:
            icon = Rectangle(width=0.8, height=0.8, fill_color=SIGNAL_CYAN,
                             fill_opacity=0.3, stroke_color=SIGNAL_CYAN, stroke_width=1.5)
            icon.move_to(pos)
            lb = safe_text(txt, font="Inter", font_size=20, color=SIGNAL_CYAN)
            lb.next_to(icon, DOWN, buff=0.1)
            arr = Arrow(pos, brain.get_center(), color=ECHO_RED, stroke_width=2.5,
                        buff=1.0, max_tip_length_to_length_ratio=0.15)
            source_icons.add(icon)
            source_labels.add(lb)
            inward_arrows.add(arr)

        # Cracked label replacement
        installed_label = safe_text("INSTALLED DRIVE", font="Inter", font_size=24,
                                    color=ECHO_RED, weight="BOLD")
        installed_label.move_to(brain_label.get_center())

        # Doctor-family compass at lower left
        doc_sil = chest_silhouette(height=1.5, color=DIM)
        doc_sil.move_to(LEFT * 2.5 + UP * ZONE_LOWER + UP * 0.5)
        doc_needle = compass_needle(height=0.5, color=ECHO_RED)
        doc_needle.move_to(doc_sil.get_center())
        doc_label = safe_text("MEDICINE", font="Inter", font_size=18, color=MUTED)
        doc_label.next_to(doc_sil, DOWN, buff=0.2)

        # Hustle-culture compass at lower right
        hustle_sil = chest_silhouette(height=1.5, color=DIM)
        hustle_sil.move_to(RIGHT * 2.5 + UP * ZONE_LOWER + UP * 0.5)
        hustle_needle = compass_needle(height=0.5, color=ECHO_RED)
        hustle_needle.move_to(hustle_sil.get_center())
        hustle_label = safe_text("REVENUE", font="Inter", font_size=18, color=MUTED)
        hustle_label.next_to(hustle_sil, DOWN, buff=0.2)

        # Footer
        caption = safe_text("THE METRICS CHOSE THEM", font="Inter",
                            font_size=22, color=ECHO_RED)
        caption.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(brain, scale=0.9), run_time=0.5); t += 0.5

        # Sources appear
        self.play(
            LaggedStart(*[FadeIn(i, scale=0.8) for i in source_icons], lag_ratio=0.08),
            LaggedStart(*[FadeIn(l, shift=UP*0.1) for l in source_labels], lag_ratio=0.08),
            run_time=0.6,
        )                                                                 # t=1.5

        # Arrows fire INWARD — reversal
        self.play(
            LaggedStart(*[GrowArrow(a) for a in inward_arrows], lag_ratio=0.08),
            run_time=0.8,
        )                                                                 # t=2.3

        # Brain cracks — label glitch
        self.play(
            brain_outer.animate.set_stroke(color=ECHO_RED),
            run_time=0.3,
        )                                                                 # t=2.6
        self.play(
            FadeOut(brain_label, scale=0.8),
            FadeIn(installed_label, scale=1.2),
            run_time=0.5,
        )                                                                 # t=3.1

        self.wait(0.5); t += 0.5

        # Lower examples
        self.play(
            FadeIn(doc_sil), FadeIn(doc_needle, scale=0.5),
            FadeIn(hustle_sil), FadeIn(hustle_needle, scale=0.5),
            run_time=0.6,
        )                                                                 # t=4.2
        self.play(
            FadeIn(doc_label, shift=UP*0.1),
            FadeIn(hustle_label, shift=UP*0.1),
            run_time=0.4,
        )                                                                 # t=4.6

        self.play(FadeIn(caption, shift=UP * 0.1), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 7.2)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 5: THE PROOF (26.0–33.0s)
# Three parallel columns showing installation mechanism
# ================================================================
class Scene5_Proof(Scene):
    DURATION = 7.7
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE INSTALLATION", color=INSTALLED_AMBER)
        pill.move_to(UP * ZONE_TITLE)

        # Three columns
        col_data = [
            ("DOCTOR\nFAMILY", "MEDICINE", COMPASS_BLUE, -3.0),
            ("HUSTLE\nMEDIA", "REVENUE", GOLD, 0.0),
            ("SOCIAL\nSCREEN", "VISIBILITY", SIGNAL_CYAN, 3.0),
        ]

        columns = VGroup()
        for source_txt, result_txt, col, x in col_data:
            # Source icon (top)
            src = signal_tower(height=1.2, color=col)
            src.move_to(RIGHT * x + UP * 3.5)
            src_label = safe_text(source_txt, font="Inter", font_size=18, color=col)
            src_label.next_to(src, DOWN, buff=0.15)

            # Arrow down
            arr = Arrow(RIGHT * x + UP * 2, RIGHT * x + UP * 0.5,
                        color=col, stroke_width=2, max_tip_length_to_length_ratio=0.2)

            # Child compass (middle)
            child_needle = compass_needle(height=0.8, color=col)
            child_needle.move_to(RIGHT * x + UP * ZONE_MID)

            # Arrow down to result
            arr2 = Arrow(RIGHT * x + DOWN * 0.8, RIGHT * x + DOWN * 2.3,
                         color=col, stroke_width=2, max_tip_length_to_length_ratio=0.2)

            # Result label (lower)
            res = safe_text(result_txt, font="Bebas Neue", font_size=36, color=col)
            res.move_to(RIGHT * x + UP * ZONE_LOWER + UP * 0.5)

            # "CHOSE THIS? NO" counter
            chose = safe_text("CHOSE THIS? NO", font="Inter", font_size=16,
                              color=ECHO_RED)
            chose.move_to(RIGHT * x + UP * ZONE_LOWER - UP * 0.5)

            columns.add(VGroup(src, src_label, arr, child_needle, arr2, res, chose))

        # Footer quote
        quote = safe_text("THE METRICS WERE ALREADY IN THE ROOM",
                          font="DM Serif Display", font_size=24, color=WHITE_SOFT)
        quote.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4

        # Columns appear left to right
        for i, col_grp in enumerate(columns):
            src, src_label, arr, needle, arr2, res, chose = col_grp
            self.play(FadeIn(src, scale=0.8), FadeIn(src_label, shift=UP*0.1),
                      run_time=0.4)
            self.play(GrowArrow(arr), run_time=0.3); t += 0.3
            self.play(FadeIn(needle, scale=0.5), run_time=0.3); t += 0.3
            self.play(GrowArrow(arr2), run_time=0.3); t += 0.3
            self.play(FadeIn(res, scale=1.05), run_time=0.3); t += 0.3
            self.play(FadeIn(chose, shift=UP*0.1), run_time=0.2); t += 0.2

        # Quote at end                                                    # t=5.8
        self.play(FadeIn(quote, shift=UP * 0.1), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 7.7)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 6: THE BETRAYAL (33.0–40.0s)
# Compass connected by red threads to external sources
# ================================================================
class Scene6_Betrayal(Scene):
    DURATION = 7.7
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE FIRST CRACK", color=ECHO_RED)
        pill.move_to(UP * ZONE_TITLE)

        # Central silhouette with compass
        sil = chest_silhouette(height=4.0, color=WHITE_SOFT)
        sil.move_to(UP * 1.0)
        needle = compass_needle(height=1.0, color=COMPASS_BLUE)
        needle.move_to(sil.get_center() + DOWN * 0.2)

        # External sources around the edges
        ext_positions = [
            (LEFT * 3.5 + UP * 4.0),   # media tower
            (RIGHT * 3.5 + UP * 4.0),  # family
            (LEFT * 4.0 + DOWN * 1.0), # institution
            (RIGHT * 4.0 + DOWN * 1.0),# screen
        ]
        ext_icons = VGroup()
        for pos in ext_positions:
            icon = signal_tower(height=1.0, color=DIM)
            icon.move_to(pos)
            ext_icons.add(icon)

        # Red threads from sources to compass
        threads = VGroup()
        for pos in ext_positions:
            thread = Line(pos, needle.get_center(), color=ECHO_RED,
                          stroke_width=1.5, stroke_opacity=0.6)
            threads.add(thread)

        # Crowd at bottom — all connected, all same direction
        crowd = VGroup()
        crowd_threads = VGroup()
        for i in range(7):
            x = -3.0 + i * 1.0
            s = chest_silhouette(height=1.0, color=DEAD_GRAY)
            n = compass_needle(height=0.3, color=ECHO_RED)
            s.move_to(RIGHT * x + UP * ZONE_LOWER)
            n.move_to(s.get_center())
            crowd.add(VGroup(s, n))
            # Thread upward
            ct = Line(s.get_top(), UP * 0.5 + RIGHT * x * 0.3,
                      color=ECHO_RED, stroke_width=0.8, stroke_opacity=0.3)
            crowd_threads.add(ct)

        # Free child at bottom — no threads
        free_child = chest_silhouette(height=1.0, color=INSTALLED_AMBER)
        free_tower = block_tower(height=0.6, color=INSTALLED_AMBER)
        free_child.move_to(UP * ZONE_FOOTER + UP * 0.3 + RIGHT * 0)
        free_tower.move_to(free_child.get_right() + RIGHT * 0.5)

        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(sil, scale=0.95), FadeIn(needle, scale=0.5),
                  run_time=0.6)                                           # t=1.0

        # External sources appear
        self.play(
            LaggedStart(*[FadeIn(i, scale=0.8) for i in ext_icons], lag_ratio=0.08),
            run_time=0.6,
        )                                                                 # t=1.6

        # Red threads connect
        self.play(
            LaggedStart(*[Create(t) for t in threads], lag_ratio=0.1),
            run_time=0.6,
        )                                                                 # t=2.2

        # Silhouette reaches for compass but threads pull taut
        self.play(
            needle.animate.shift(UP * 0.2),
            *[t.animate.set_opacity(1).set_stroke(width=3) for t in threads],
            run_time=0.5,
        )                                                                 # t=2.7
        self.play(
            needle.animate.shift(DOWN * 0.2),
            sil.animate.set_opacity(0.3),
            run_time=0.4,
        )                                                                 # t=3.1

        self.wait(0.5); t += 0.5

        # Crowd appears — all connected
        self.play(
            LaggedStart(*[FadeIn(c, scale=0.8) for c in crowd], lag_ratio=0.05),
            run_time=0.6,
        )                                                                 # t=4.2
        self.play(
            LaggedStart(*[Create(ct) for ct in crowd_threads], lag_ratio=0.05),
            run_time=0.5,
        )                                                                 # t=4.7

        # Free child — the only one not connected
        self.play(FadeIn(free_child, scale=0.9), FadeIn(free_tower, scale=0.9),
                  run_time=0.5)                                           # t=5.2

        self.play(Flash(free_child.get_center(), color=INSTALLED_AMBER,
                        line_length=0.3, num_lines=6, run_time=0.3))     # t=5.5
        target = getattr(self.__class__, 'DURATION', 7.7)
        self.wait(max(0.1, target - t - 0.8))


# ── Infra ─────────────────────────────────────────────────────
def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_Mystery, Scene3_WrongAnswer,
          Scene4_Contradiction, Scene5_Proof, Scene6_Betrayal]
    config.output_file = f"ambition_installed_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"ambition_installed_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    sc = [Scene1_Hook, Scene2_Mystery, Scene3_WrongAnswer,
          Scene4_Contradiction, Scene5_Proof, Scene6_Betrayal]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(sc):
        n = f"ambition_installed_scene_{i+1}"; print(f"  Preview {n}...")
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
    if "--preview" in sys.argv: render_previews(); sys.exit(0)
    if "--scene" in sys.argv:
        timings_json = os.environ.get("TKK_SCENE_TIMINGS")
        if timings_json:
            _idx = int(sys.argv[sys.argv.index("--scene")+1])
            _classes = sorted([v for k,v in globals().items() if k.startswith("Scene") and len(k) > 5 and k[5].isdigit() and isinstance(v, type)], key=lambda c: c.__name__); _classes[_idx].DURATION = json.loads(timings_json)[_idx]
        render_single_scene(int(sys.argv[sys.argv.index("--scene")+1])); sys.exit(0)

    names = ["Scene1_Hook","Scene2_Mystery","Scene3_WrongAnswer",
             "Scene4_Contradiction","Scene5_Proof","Scene6_Betrayal"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_ambition_installed.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="ambition_installed", audio_path=str(audio))
    final = od / "ambition_installed_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
