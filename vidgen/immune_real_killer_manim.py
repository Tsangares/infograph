#!/usr/bin/env python3
"""Your Immune System Does the Real Killing — Antibiotics are assistants, not cures.

6 scenes, ~40.0s (37.0s audio + 3s hold).
Domain shapes: mouse_shape, neutrophil_cell, shield_icon, bacteria_cluster.

VTT cues (absolute → relative):
  Scene 1 (0.0–6.5s):   0.30 here's what you think... 3.00 drug floods... 5.40 cured
  Scene 2 (6.5–13.0s):  6.80 two groups of mice... 9.20 same drug... 11.60 what happens
  Scene 3 (13.0–18.0s): 13.40 obvious answer... 15.20 both survive... 17.00 drug hero
  Scene 4 (18.0–24.0s): 18.40 mouse A survives... 20.80 mouse B dies... 23.00 same drug
  Scene 5 (24.0–31.0s): 24.40 reduce population... 27.00 neutrophils... 29.40 33 trials
  Scene 6 (31.0–40.0s): 31.40 immunocompromised... 34.00 higher doses... 37.00 can't
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """Two mice get the same infection. Same antibiotic. One has an immune system. One doesn't. Same drug. Same bacteria. The mouse without immunity dies. Antibiotics don't kill everything. They knock millions down to thousands. Your immune system finishes the job. Thirty-three clinical trials confirmed it. When immunity breaks — chemo, transplants, HIV — you get one hour from fever to antibiotics. The drug does everything alone. And it usually can't."""

from manim import (
    Scene, Text, Group, VGroup, Rectangle, RoundedRectangle, Circle,
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
DRUG_BLUE = "#3B82F6"; IMMUNE_CYAN = "#06B6D4"; BACTERIA_GREEN = "#22C55E"
DANGER_RED = "#EF4444"; CHECK_GREEN = "#22C55E"; MUTED = "#475569"
DEAD_GRAY = "#4A5568"; SHIELD_GOLD = "#D4A017"; DIM = "#334155"
SAFE_W = 8.0

# Vertical layout zones — USE THESE for all positioning
ZONE_TITLE  = 6.2    # y 5.5–7.0  — scene label pills
ZONE_UPPER  = 3.5    # y 1.5–5.5  — hero visual top portion
ZONE_MID    = 0.0    # y -1.5–1.5 — central focal point, big numbers
ZONE_LOWER  = -3.5   # y -5.5–-1.5 — supporting visuals, bars, icons
ZONE_FOOTER = -6.0   # y -6.4–-5.5 — captions, source labels

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


# ── Domain shapes ────────────────────────────────────────────

def mouse_shape(height=2.0, color=WHITE_SOFT):
    """Simple mouse — oval body, round head, tail, ears."""
    body = Ellipse(width=height*0.5, height=height*0.35, fill_color=color,
                   fill_opacity=0.3, stroke_color=color, stroke_width=1.5)
    head = Circle(radius=height*0.12, fill_color=color, fill_opacity=0.4,
                  stroke_color=color, stroke_width=1.5)
    head.move_to(body.get_right() + RIGHT * height * 0.08)
    ear_l = Circle(radius=height*0.05, fill_color=color, fill_opacity=0.3, stroke_width=0)
    ear_l.move_to(head.get_top() + LEFT * height * 0.04 + UP * height * 0.02)
    ear_r = ear_l.copy().move_to(head.get_top() + RIGHT * height * 0.04 + UP * height * 0.02)
    tail = Arc(radius=height*0.2, angle=150*DEGREES, stroke_color=color, stroke_width=1.5)
    tail.move_to(body.get_left() + LEFT * height * 0.1)
    eye = Dot(radius=height*0.02, color=BG).move_to(head.get_center() + RIGHT * height * 0.03)
    return VGroup(body, head, ear_l, ear_r, tail, eye)

def neutrophil_cell(radius=0.6, color=IMMUNE_CYAN):
    """Immune cell — blobby circle with lobed nucleus."""
    body = Circle(radius=radius, fill_color=color, fill_opacity=0.25,
                  stroke_color=color, stroke_width=2)
    lobes = VGroup()
    for angle in [0, 120, 240]:
        lobe = Circle(radius=radius*0.22, fill_color=color, fill_opacity=0.6, stroke_width=0)
        lobe.move_to(np.array([np.cos(angle*PI/180)*radius*0.25,
                               np.sin(angle*PI/180)*radius*0.25, 0]))
        lobes.add(lobe)
    return VGroup(body, lobes)

def shield_icon(height=1.5, color=SHIELD_GOLD, cracked=False):
    """Shield shape — intact or cracked."""
    pts = [
        np.array([0, height*0.5, 0]),
        np.array([height*0.35, height*0.3, 0]),
        np.array([height*0.35, -height*0.1, 0]),
        np.array([0, -height*0.5, 0]),
        np.array([-height*0.35, -height*0.1, 0]),
        np.array([-height*0.35, height*0.3, 0]),
    ]
    shield = Polygon(*pts, fill_color=color, fill_opacity=0.3,
                     stroke_color=color, stroke_width=2)
    grp = VGroup(shield)
    if cracked:
        crack = Line(UP * height * 0.2, DOWN * height * 0.3, color=DANGER_RED,
                     stroke_width=3)
        crack.move_to(shield.get_center() + RIGHT * 0.05)
        grp.add(crack)
        shield.set_fill(opacity=0.1)
        shield.set_stroke(color=DEAD_GRAY)
    return grp

def bacteria_cluster(n=8, color=BACTERIA_GREEN, spread=1.0):
    """Cluster of bacteria dots."""
    grp = VGroup()
    np.random.seed(55)
    for _ in range(n):
        b = RoundedRectangle(width=0.18, height=0.09, corner_radius=0.03,
                             fill_color=color, fill_opacity=0.7, stroke_width=0)
        b.move_to(np.array([np.random.uniform(-spread, spread),
                            np.random.uniform(-spread/2, spread/2), 0]))
        grp.add(b)
    return grp


# ================================================================
# SCENE 1: THE HOOK (0.0–6.5s)
# Drug wipes out bacteria → rewind → "is that what actually happens?"
# Zones: TITLE, MID (bacteria + drug), LOWER (missing text), FOOTER
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 6.5
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE — pill label
        pill_label = label_pill("WHO KILLS?", color=DANGER_RED)
        pill_label.move_to(UP * ZONE_TITLE)

        # ZONE_MID — bacteria cluster + drug pill animation
        bact = bacteria_cluster(12, BACTERIA_GREEN, 1.5)
        bact.move_to(UP * ZONE_MID)

        pill = RoundedRectangle(width=0.8, height=0.4, corner_radius=0.12,
                                fill_color=DRUG_BLUE, fill_opacity=0.9, stroke_width=0)
        pill.move_to(UP * ZONE_UPPER)

        # Drug particles
        particles = VGroup()
        for _ in range(15):
            p = Dot(radius=0.05, color=DRUG_BLUE)
            p.move_to(UP * ZONE_MID + np.array([np.random.uniform(-2, 2),
                                                  np.random.uniform(-1, 1), 0]))
            particles.add(p)

        # ZONE_LOWER — "SOMETHING IS MISSING"
        missing = safe_text("SOMETHING IS MISSING", font="Bebas Neue",
                            font_size=50, color=DANGER_RED)
        missing.move_to(UP * ZONE_LOWER)

        # ZONE_FOOTER — question
        footer = safe_text("is that what actually happens?", font="Inter",
                           font_size=18, color=MUTED)
        footer.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(bact), run_time=0.4); t += 0.4

        # Pill drops to bacteria
        self.play(pill.animate.move_to(UP * ZONE_MID), run_time=0.5); t += 0.5

        # Bacteria dissolve
        self.play(
            *[b.animate.set_opacity(0) for b in bact],
            FadeOut(pill),
            LaggedStart(*[FadeIn(p, scale=2) for p in particles], lag_ratio=0.03),
            run_time=0.8,
        )                                                                   # t=2.1

        # Rewind — bacteria come back
        self.wait(0.5); t += 0.5
        self.play(
            *[b.animate.set_opacity(0.7) for b in bact],
            *[p.animate.set_opacity(0) for p in particles],
            run_time=0.6,
        )                                                                   # t=3.2

        self.play(FadeIn(missing, scale=1.1), run_time=0.4); t += 0.4
        self.play(Flash(missing.get_center(), color=DANGER_RED,
                        line_length=0.3, num_lines=6, run_time=0.3))      # t=3.9
        self.play(FadeIn(footer), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 6.5)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE EXPERIMENT (6.5–13.0s)
# Two mice + same drug + one has immune system, one doesn't
# Zones: TITLE, UPPER (mice), MID (shields), LOWER (pills + same drug), FOOTER
# ================================================================
class Scene2_Experiment(Scene):
    DURATION = 6.5
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE
        pill_label = label_pill("THE EXPERIMENT", color=GOLD)
        pill_label.move_to(UP * ZONE_TITLE)

        # Divider
        divider = DashedLine(UP * 5, DOWN * 4, color=MUTED, stroke_width=1, dash_length=0.15)

        # ZONE_UPPER — Mouse A (with immune system)
        mouse_a = mouse_shape(height=2.5, color=WHITE_SOFT)
        mouse_a.move_to(LEFT * 2.2 + UP * ZONE_UPPER)
        label_a = safe_text("MOUSE A", font="Inter", font_size=22, color=WHITE_SOFT, weight="BOLD")
        label_a.next_to(mouse_a, UP, buff=0.3)

        # ZONE_MID — shields
        shield_a = shield_icon(height=1.0, color=SHIELD_GOLD, cracked=False)
        shield_a.move_to(LEFT * 2.2 + UP * (ZONE_MID + 0.5))
        immune_lbl = safe_text("IMMUNE: ON", font="Inter", font_size=16, color=CHECK_GREEN)
        immune_lbl.next_to(shield_a, DOWN, buff=0.2)

        # ZONE_UPPER — Mouse B (no immune system)
        mouse_b = mouse_shape(height=2.5, color=DEAD_GRAY)
        mouse_b.move_to(RIGHT * 2.2 + UP * ZONE_UPPER)
        label_b = safe_text("MOUSE B", font="Inter", font_size=22, color=DEAD_GRAY, weight="BOLD")
        label_b.next_to(mouse_b, UP, buff=0.3)

        # ZONE_MID — shield B
        shield_b = shield_icon(height=1.0, color=DEAD_GRAY, cracked=True)
        shield_b.move_to(RIGHT * 2.2 + UP * (ZONE_MID + 0.5))
        no_immune = safe_text("IMMUNE: OFF", font="Inter", font_size=16, color=DANGER_RED)
        no_immune.next_to(shield_b, DOWN, buff=0.2)

        # Infection dots on mice
        inf_a = Dot(radius=0.12, color=DANGER_RED).move_to(mouse_a.get_center())
        inf_b = Dot(radius=0.12, color=DANGER_RED).move_to(mouse_b.get_center())

        # ZONE_LOWER — Same drug (blue pills)
        pill_a = RoundedRectangle(width=0.5, height=0.25, corner_radius=0.08,
                                  fill_color=DRUG_BLUE, fill_opacity=0.9, stroke_width=0)
        pill_a.move_to(LEFT * 2.2 + UP * (ZONE_LOWER + 1.0))
        pill_b = pill_a.copy().move_to(RIGHT * 2.2 + UP * (ZONE_LOWER + 1.0))

        same = safe_text("SAME DRUG. SAME BACTERIA.", font="Bebas Neue",
                         font_size=36, color=WHITE_SOFT)
        same.move_to(UP * ZONE_LOWER)

        # ZONE_FOOTER
        footer = safe_text("what happens?", font="Inter", font_size=18, color=MUTED)
        footer.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3
        self.play(Create(divider), run_time=0.2); t += 0.2

        # Mouse A
        self.play(FadeIn(mouse_a), FadeIn(label_a), run_time=0.4); t += 0.4
        self.play(FadeIn(shield_a), FadeIn(immune_lbl), run_time=0.3); t += 0.3
        self.play(FadeIn(inf_a, scale=2), run_time=0.2); t += 0.2

        # Mouse B
        self.play(FadeIn(mouse_b), FadeIn(label_b), run_time=0.4); t += 0.4
        self.play(FadeIn(shield_b), FadeIn(no_immune), run_time=0.3); t += 0.3
        self.play(FadeIn(inf_b, scale=2), run_time=0.2); t += 0.2

        # Same drug
        self.play(FadeIn(pill_a, shift=DOWN * 0.2), FadeIn(pill_b, shift=DOWN * 0.2),
                  run_time=0.4)                                            # t=2.7
        self.play(FadeIn(same), run_time=0.3); t += 0.3
        self.play(FadeIn(footer), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 6.5)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: THE WRONG ANSWER (13.0–18.0s)
# Both survive? Both get checks? Nope.
# Zones: TITLE, UPPER (mice), MID (checks), LOWER (both cured), FOOTER
# ================================================================
class Scene3_WrongAnswer(Scene):
    DURATION = 5.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE
        pill_label = label_pill("WHAT YOU'D EXPECT", color=CHECK_GREEN)
        pill_label.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER — Two mice both healthy (green)
        mouse_a = mouse_shape(height=2.5, color=CHECK_GREEN)
        mouse_a.move_to(LEFT * 2.2 + UP * ZONE_UPPER)

        mouse_b = mouse_shape(height=2.5, color=CHECK_GREEN)
        mouse_b.move_to(RIGHT * 2.2 + UP * ZONE_UPPER)

        # ZONE_MID — check marks
        check_a = safe_text("✓", font="Inter", font_size=50, color=CHECK_GREEN)
        check_a.move_to(LEFT * 2.2 + UP * ZONE_MID)
        check_b = safe_text("✓", font="Inter", font_size=50, color=CHECK_GREEN)
        check_b.move_to(RIGHT * 2.2 + UP * ZONE_MID)

        # ZONE_LOWER — "BOTH CURED"
        both = safe_text("BOTH CURED", font="Bebas Neue", font_size=60, color=CHECK_GREEN)
        both.move_to(UP * (ZONE_LOWER + 1.0))

        drug_hero = safe_text("the drug is the hero", font="DM Serif Display",
                              font_size=30, color=MUTED)
        drug_hero.move_to(UP * ZONE_LOWER)

        # ZONE_FOOTER
        footer = safe_text("this is the assumption", font="Inter", font_size=18, color=MUTED)
        footer.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(mouse_a), FadeIn(mouse_b), run_time=0.4); t += 0.4
        self.play(FadeIn(check_a, scale=1.5), FadeIn(check_b, scale=1.5),
                  run_time=0.4)                                            # t=1.1
        self.play(FadeIn(both, scale=1.1), run_time=0.4); t += 0.4
        self.play(FadeIn(drug_hero), FadeIn(footer), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 5.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE RESULT (18.0–24.0s)
# Mouse A: green check. Mouse B: red X. Same drug failed.
# Zones: TITLE, UPPER (mice), MID (shields + checks), LOWER (failed), FOOTER
# ================================================================
class Scene4_Result(Scene):
    DURATION = 6.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE
        pill_label = label_pill("THE RESULT", color=DANGER_RED)
        pill_label.move_to(UP * ZONE_TITLE)

        divider = DashedLine(UP * 5, DOWN * 4, color=MUTED, stroke_width=1, dash_length=0.15)

        # ZONE_UPPER — Mouse A survives
        mouse_a = mouse_shape(height=2.5, color=CHECK_GREEN)
        mouse_a.move_to(LEFT * 2.2 + UP * ZONE_UPPER)

        # ZONE_MID — shields + result marks
        shield_a = shield_icon(height=0.8, color=SHIELD_GOLD)
        shield_a.move_to(LEFT * 2.2 + UP * (ZONE_MID + 0.8))
        check_a = safe_text("✓", font="Inter", font_size=60, color=CHECK_GREEN)
        check_a.move_to(LEFT * 2.2 + UP * (ZONE_MID - 0.5))

        # ZONE_UPPER — Mouse B dies
        mouse_b = mouse_shape(height=2.5, color=DEAD_GRAY)
        mouse_b.move_to(RIGHT * 2.2 + UP * ZONE_UPPER)
        shield_b = shield_icon(height=0.8, color=DEAD_GRAY, cracked=True)
        shield_b.move_to(RIGHT * 2.2 + UP * (ZONE_MID + 0.8))
        x_b = safe_text("✕", font="Inter", font_size=60, color=DANGER_RED)
        x_b.move_to(RIGHT * 2.2 + UP * (ZONE_MID - 0.5))

        # ZONE_LOWER — Flash text
        failed = safe_text("THE DRUG ALONE FAILED", font="Bebas Neue",
                           font_size=50, color=DANGER_RED)
        failed.move_to(UP * ZONE_LOWER)

        sub = safe_text("same bacteria. fully susceptible.", font="Inter",
                        font_size=20, color=MUTED)
        sub.move_to(UP * (ZONE_LOWER - 1.2))

        # ZONE_FOOTER
        footer = safe_text("Frontiers in Immunology, 2025", font="Inter",
                           font_size=18, color=MUTED)
        footer.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3
        self.play(Create(divider), run_time=0.2); t += 0.2

        # Mouse A
        self.play(FadeIn(mouse_a), FadeIn(shield_a), run_time=0.4); t += 0.4
        self.play(FadeIn(check_a, scale=1.5), run_time=0.3); t += 0.3

        # Mouse B
        self.play(FadeIn(mouse_b), FadeIn(shield_b), run_time=0.4); t += 0.4
        self.play(FadeIn(x_b, scale=1.5), run_time=0.3); t += 0.3
        self.play(Flash(x_b.get_center(), color=DANGER_RED,
                        line_length=0.3, num_lines=6, run_time=0.3))      # t=2.2

        # Failed
        self.wait(0.5); t += 0.5
        self.play(FadeIn(failed, scale=1.1), run_time=0.4); t += 0.4
        self.play(Flash(failed.get_center(), color=DANGER_RED,
                        line_length=0.3, num_lines=8, run_time=0.3))      # t=3.4
        self.play(FadeIn(sub), FadeIn(footer), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 6.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE TRUTH (24.0–31.0s)
# Antibiotics reduce population → immune cells finish → 33 trials RR 0.99
# Zones: TITLE, UPPER (33 TRIALS stat), MID (neutrophils), LOWER (bar chart), FOOTER
# ================================================================
class Scene5_Truth(Scene):
    DURATION = 7.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE
        pill_label = label_pill("THE TRUTH", color=GOLD)
        pill_label.move_to(UP * ZONE_TITLE)

        # Bacteria bar chart: before → after antibiotic → after immune
        # Bars start low at ZONE_LOWER to fill the frame
        bar_y_base = -5.5

        # Before: tall bar (millions)
        before = Rectangle(width=1.5, height=5.0, fill_color=BACTERIA_GREEN, fill_opacity=0.5,
                           stroke_width=0)
        before.move_to(LEFT * 2.5 + UP * (bar_y_base + 2.5))
        before_lbl = safe_text("MILLIONS", font="Inter", font_size=16, color=BACTERIA_GREEN)
        before_lbl.next_to(before, UP, buff=0.1)

        # After drug: shorter bar (thousands)
        after_drug = Rectangle(width=1.5, height=1.2, fill_color=BACTERIA_GREEN, fill_opacity=0.5,
                               stroke_width=0)
        after_drug.move_to(UP * (bar_y_base + 0.6))
        after_lbl = safe_text("THOUSANDS", font="Inter", font_size=16, color=BACTERIA_GREEN)
        after_lbl.next_to(after_drug, UP, buff=0.1)

        # After immune: zero
        after_immune = Rectangle(width=1.5, height=0.1, fill_color=BACTERIA_GREEN, fill_opacity=0.3,
                                 stroke_width=0)
        after_immune.move_to(RIGHT * 2.5 + UP * bar_y_base)
        zero_lbl = safe_text("ZERO", font="Inter", font_size=16, color=IMMUNE_CYAN)
        zero_lbl.next_to(after_immune, UP, buff=0.1)

        # Arrows between bars
        drug_arrow = Arrow(LEFT * 1.5 + UP * (bar_y_base + 1.0), LEFT * 0.3 + UP * (bar_y_base + 1.0),
                           color=DRUG_BLUE, stroke_width=2, max_tip_length_to_length_ratio=0.15)
        drug_tag = safe_text("DRUG", font="Inter", font_size=14, color=DRUG_BLUE)
        drug_tag.next_to(drug_arrow, DOWN, buff=0.1)

        immune_arrow = Arrow(RIGHT * 1 + UP * (bar_y_base + 0.5), RIGHT * 2.2 + UP * (bar_y_base + 0.5),
                             color=IMMUNE_CYAN, stroke_width=2, max_tip_length_to_length_ratio=0.15)
        immune_tag = safe_text("IMMUNE", font="Inter", font_size=14, color=IMMUNE_CYAN)
        immune_tag.next_to(immune_arrow, DOWN, buff=0.1)

        # ZONE_MID — Neutrophils eating remaining bacteria
        cells = VGroup()
        for i in range(3):
            c = neutrophil_cell(radius=0.5, color=IMMUNE_CYAN)
            c.move_to(LEFT * 1.5 + RIGHT * i * 1.5 + UP * ZONE_MID)
            cells.add(c)

        # ZONE_UPPER — 33 TRIALS stat
        trials = safe_text("33 TRIALS", font="Bebas Neue", font_size=80, color=GOLD)
        trials.move_to(UP * ZONE_UPPER)

        rr = safe_text("RR 0.99", font="Bebas Neue", font_size=50, color=WHITE_SOFT)
        rr.move_to(UP * (ZONE_UPPER - 1.5))

        sub = safe_text("bactericidal = bacteriostatic", font="Inter",
                        font_size=18, color=MUTED)
        sub.move_to(UP * (ZONE_MID + 1.5))

        # ZONE_FOOTER
        footer = safe_text("the immune system does the real killing", font="Inter",
                           font_size=18, color=MUTED)
        footer.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3

        # Before bar
        self.play(FadeIn(before, shift=UP * 0.3), FadeIn(before_lbl), run_time=0.4); t += 0.4

        # Drug reduces
        self.play(GrowArrow(drug_arrow), FadeIn(drug_tag), run_time=0.3); t += 0.3
        self.play(FadeIn(after_drug, shift=UP * 0.2), FadeIn(after_lbl), run_time=0.4); t += 0.4

        # Immune finishes
        self.play(LaggedStart(*[FadeIn(c, scale=1.5) for c in cells],
                              lag_ratio=0.1), run_time=0.4)               # t=1.8
        self.play(GrowArrow(immune_arrow), FadeIn(immune_tag), run_time=0.3); t += 0.3
        self.play(FadeIn(after_immune), FadeIn(zero_lbl), run_time=0.3); t += 0.3

        # 33 trials
        self.wait(0.6); t += 0.6
        self.play(FadeIn(trials, scale=1.1), run_time=0.4); t += 0.4
        self.play(FadeIn(rr), FadeIn(sub), run_time=0.3); t += 0.3
        self.play(FadeIn(footer), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 7.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE PUNCH (31.0–40.0s)
# Cracked shield → higher doses → "the drug has to do everything alone"
# Zones: TITLE, UPPER (cracked shield), MID (conditions), LOWER (1 HOUR), FOOTER
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 9.0
    def construct(self):
        self.add(gradient_bg("#0A0E18"), grid_lines(0.02))
        t = 0

        # ZONE_TITLE
        pill_label = label_pill("WHEN IT BREAKS", color=DANGER_RED)
        pill_label.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER — Cracked shield (large, hero at UPPER not top)
        broken = shield_icon(height=3.0, color=DEAD_GRAY, cracked=True)
        broken.move_to(UP * ZONE_UPPER)

        # ZONE_MID — Conditions
        conditions = ["CHEMO", "TRANSPLANTS", "HIV"]
        cond_labels = VGroup()
        for i, cond in enumerate(conditions):
            lbl = safe_text(cond, font="Inter", font_size=22, color=DANGER_RED, weight="BOLD")
            lbl.move_to(LEFT * 2.5 + RIGHT * i * 2.5 + UP * ZONE_MID)
            cond_labels.add(lbl)

        # ZONE_LOWER — Rules change
        rules = safe_text("1 HOUR", font="Bebas Neue", font_size=90, color=DANGER_RED)
        rules.move_to(UP * ZONE_LOWER)
        rules_sub = safe_text("to start antibiotics from fever", font="Inter",
                              font_size=20, color=MUTED)
        rules_sub.next_to(rules, DOWN, buff=0.2)

        # ZONE_FOOTER — Final line
        alone = safe_text("and it usually can't", font="DM Serif Display",
                          font_size=34, color=WHITE_SOFT)
        alone.move_to(UP * ZONE_FOOTER)

        # ── Timing: 9.00s ──
        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(broken, scale=0.8), run_time=0.5); t += 0.5
        self.play(Flash(broken.get_center(), color=DANGER_RED,
                        line_length=0.3, num_lines=6, run_time=0.3))      # t=1.1

        self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.1) for l in cond_labels],
                              lag_ratio=0.15), run_time=0.5)              # t=1.6

        self.wait(0.8); t += 0.8
        self.play(FadeIn(rules, scale=1.15), run_time=0.5); t += 0.5
        self.play(Flash(rules.get_center(), color=DANGER_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))      # t=3.2
        self.play(FadeIn(rules_sub), run_time=0.3); t += 0.3

        self.wait(1.5); t += 1.5
        self.play(FadeIn(alone, shift=UP * 0.05), run_time=0.5); t += 0.5

        # Hold
        target = getattr(self.__class__, 'DURATION', 9.0)
        self.wait(max(0.1, target - t - 0.8))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=0.7); t += 0.7


# ── Infra ─────────────────────────────────────────────────────
SCENES = [Scene1_Hook, Scene2_Experiment, Scene3_WrongAnswer,
          Scene4_Result, Scene5_Truth, Scene6_Punch]

def render_single_scene(idx):
    config.output_file = f"immune_real_killer_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    SCENES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"immune_real_killer_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENES):
        n = f"immune_real_killer_scene_{i+1}"; print(f"  Preview {n}...")
        config.output_file = n; config.save_last_frame = True; config.format = "png"
        S().render()
        for p in Path(config.media_dir).rglob(f"{n}*"):
            if p.suffix == ".png":
                dst = d / f"{n}.png"; shutil.copy2(str(p), str(dst))
                print(f"  OK: {dst} ({dst.stat().st_size//1024} KB)"); break
    config.save_last_frame = False; config.format = None
    print(f"\nAll 6 previews -> {d}/")

if __name__ == "__main__":
    import time
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
    audio = od / "tts_immune_real_killer.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="immune_real_killer", audio_path=str(audio))
    final = od / "immune_real_killer_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")

    from render_utils import run_post_render_qa
    run_post_render_qa(str(final), scene_count=6)
