#!/usr/bin/env python3
"""Antibiotics Have No GPS — Why an ear infection pill wrecks your gut.

6 scenes, ~40.0s (37.0s audio + 3s hold).
Domain shapes: body_silhouette, gut_lining, bacteria_dot, heart_pump.

VTT cues (absolute → relative):
  Scene 1 (0.0–6.5s):   0.30 when you swallow... 3.00 does not go... 5.20 every tissue
  Scene 2 (6.5–13.0s):  6.80 floods everywhere... 9.20 can't tell... 11.40 indiscriminately
  Scene 3 (13.0–18.0s): 13.40 what you think... 15.20 guided missile... 17.00 90% to ear
  Scene 4 (18.0–24.5s): 18.40 that's wrong... 20.80 heart pumps... 23.00 every organ
  Scene 5 (24.5–31.0s): 24.80 diarrhea... 27.00 yeast infections... 29.40 C. diff
  Scene 6 (31.0–40.0s): 31.40 ear heals... 33.80 gut wrecked... 36.20 six months... 38.60 never
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """When you swallow an antibiotic for an ear infection, it does not go straight to your ear. It floods every tissue in your body.
The drug washes through your gut, and it can't tell friend from foe. It kills bacteria indiscriminately.
Most people think an antibiotic is a guided missile. Ninety percent goes to the ear, ten percent everywhere else.
That's completely wrong. Your heart pumps that drug equally to every organ. Brain, kidneys, liver, skin, gut, everything.
So while the ear infection clears up, you get diarrhea, yeast infections, and five hundred thousand Americans a year get C. diff.
Your ear heals in a week. Your gut stays wrecked for six months or more. And some species of bacteria never return."""

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
DRUG_BLUE = "#3B82F6"; BODY_PURPLE = "#8B5CF6"; GUT_GREEN = "#22C55E"
DANGER_RED = "#EF4444"; WARN_ORANGE = "#F59E0B"; MUTED = "#475569"
DEAD_GRAY = "#4A5568"; DIM = "#334155"
SAFE_W = 8.0

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

def body_silhouette(height=8, color=BODY_PURPLE):
    """Simplified human body outline — head, torso, limbs."""
    head = Circle(radius=height*0.06, fill_color=color, fill_opacity=0.15,
                  stroke_color=color, stroke_width=1.5)
    head.move_to(UP * height * 0.42)
    torso = RoundedRectangle(width=height*0.2, height=height*0.3, corner_radius=height*0.03,
                             fill_color=color, fill_opacity=0.08,
                             stroke_color=color, stroke_width=1.5)
    torso.move_to(UP * height * 0.18)
    arm_l = Rectangle(width=height*0.05, height=height*0.25, fill_color=color,
                      fill_opacity=0.06, stroke_color=color, stroke_width=1)
    arm_l.move_to(LEFT * height * 0.15 + UP * height * 0.2)
    arm_r = arm_l.copy().move_to(RIGHT * height * 0.15 + UP * height * 0.2)
    leg_l = Rectangle(width=height*0.06, height=height*0.3, fill_color=color,
                      fill_opacity=0.06, stroke_color=color, stroke_width=1)
    leg_l.move_to(LEFT * height * 0.06 + DOWN * height * 0.1)
    leg_r = leg_l.copy().move_to(RIGHT * height * 0.06 + DOWN * height * 0.1)
    return VGroup(head, torso, arm_l, arm_r, leg_l, leg_r)

def gut_lining(width=6, height=2, color=GUT_GREEN):
    """Cross-section of intestinal lining with villi bumps."""
    base = Rectangle(width=width, height=height*0.3, fill_color=color,
                     fill_opacity=0.15, stroke_color=color, stroke_width=1)
    villi = VGroup()
    n_villi = int(width / 0.4)
    for i in range(n_villi):
        v = Ellipse(width=0.2, height=height*0.5, fill_color=color,
                    fill_opacity=0.2, stroke_width=0)
        v.move_to(base.get_top() + UP * height * 0.2 + LEFT * width/2 + RIGHT * (i * 0.4 + 0.2))
        villi.add(v)
    return VGroup(base, villi)

def bacteria_dot(radius=0.1, color=GUT_GREEN):
    """Single bacterium dot."""
    return Circle(radius=radius, fill_color=color, fill_opacity=0.7, stroke_width=0)

def heart_pump(size=1.0, color=DANGER_RED):
    """Simple heart shape from two arcs + triangle."""
    left_bump = Circle(radius=size*0.3, fill_color=color, fill_opacity=0.3,
                       stroke_width=0).move_to(LEFT*size*0.15 + UP*size*0.1)
    right_bump = Circle(radius=size*0.3, fill_color=color, fill_opacity=0.3,
                        stroke_width=0).move_to(RIGHT*size*0.15 + UP*size*0.1)
    bottom = Polygon(
        np.array([-size*0.45, 0, 0]), np.array([size*0.45, 0, 0]),
        np.array([0, -size*0.5, 0]),
        fill_color=color, fill_opacity=0.3, stroke_width=0,
    )
    return VGroup(left_bump, right_bump, bottom)


# ================================================================
# SCENE 1: THE HOOK (0.0–6.5s)
# Body silhouette → infection dot on ear → pill → dye floods EVERYWHERE
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 7.4
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill_label = label_pill("NO GPS", color=DANGER_RED)
        pill_label.move_to(UP * 6.2)

        # Body
        body = body_silhouette(height=10, color=BODY_PURPLE)
        body.move_to(UP * 0.5)

        # Infection dot on ear
        infection = Dot(radius=0.15, color=DANGER_RED).move_to(UP * 4.7 + RIGHT * 0.7)
        inf_pulse = Circle(radius=0.3, stroke_color=DANGER_RED, stroke_width=1.5,
                           fill_opacity=0).move_to(infection)

        # Pill dropping in
        pill = RoundedRectangle(width=0.6, height=0.3, corner_radius=0.1,
                                fill_color=DRUG_BLUE, fill_opacity=0.9, stroke_width=0)
        pill.move_to(UP * 7)

        # Flood circles (drug spreading from gut)
        flood_origin = UP * 1.5  # gut area

        footer = safe_text("antibiotics flood every tissue", font="Inter",
                           font_size=18, color=MUTED)
        footer.move_to(DOWN * 6.0)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(body, scale=0.95), run_time=0.5); t += 0.5
        self.play(FadeIn(infection, scale=2), run_time=0.3); t += 0.3
        self.play(GrowFromCenter(inf_pulse), run_time=0.3); t += 0.3

        # Pill drops into body
        self.play(pill.animate.move_to(flood_origin), run_time=0.8); t += 0.8

        # Drug floods outward — expanding blue tint
        flood_rings = VGroup()
        for r in [1, 2.5, 4, 5.5]:
            ring = Circle(radius=r, stroke_color=DRUG_BLUE, stroke_width=1.5,
                          fill_color=DRUG_BLUE, fill_opacity=0.04)
            ring.move_to(flood_origin)
            flood_rings.add(ring)

        self.play(LaggedStart(*[GrowFromCenter(r) for r in flood_rings],
                              lag_ratio=0.15), run_time=1.5)              # t=3.8

        # Body tints blue
        self.play(*[part.animate.set_fill(DRUG_BLUE, opacity=0.15) for part in body],
                  run_time=0.6)                                            # t=4.4

        self.play(FadeIn(footer), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 7.4)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 2: THE MYSTERY (6.5–13.0s)
# Gut zoom → friendly bacteria → drug washing over → flickering
# ================================================================
class Scene2_GutFlood(Scene):
    DURATION = 7.4
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill_label = label_pill("THE FLOOD", color=DRUG_BLUE)
        pill_label.move_to(UP * 6.2)

        # Gut lining at center
        gut = gut_lining(width=7, height=2.5, color=GUT_GREEN)
        gut.move_to(UP * 1)

        # Friendly bacteria (green dots)
        friendly = VGroup()
        np.random.seed(42)
        for _ in range(30):
            b = bacteria_dot(0.08, GUT_GREEN)
            b.move_to(UP * 1 + np.array([
                np.random.uniform(-3, 3), np.random.uniform(-0.8, 1.5), 0]))
            friendly.add(b)

        # Blue drug wave
        wave = Rectangle(width=8, height=3.5, fill_color=DRUG_BLUE, fill_opacity=0.15,
                         stroke_width=0)
        wave.move_to(UP * 1)

        # "NOT THE INFECTION SITE" text
        not_infection = safe_text("NOT THE INFECTION SITE", font="Bebas Neue",
                                  font_size=50, color=DANGER_RED)
        not_infection.move_to(DOWN * 3)

        # Ear icon at bottom for reference
        ear_label = safe_text("ear infection is up here", font="Inter",
                              font_size=18, color=MUTED)
        ear_label.move_to(DOWN * 5)
        ear_arrow = Arrow(ear_label.get_top(), UP * (-4), color=MUTED,
                          stroke_width=1, max_tip_length_to_length_ratio=0.2)

        footer = safe_text("collateral damage", font="Inter", font_size=18, color=MUTED)
        footer.move_to(DOWN * 6.0)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(gut), run_time=0.4); t += 0.4
        self.play(LaggedStart(*[FadeIn(b, scale=2) for b in friendly],
                              lag_ratio=0.02), run_time=0.6)              # t=1.3

        # Drug wave washes in
        wave.move_to(LEFT * 6 + UP * 1)
        self.play(wave.animate.move_to(UP * 1), run_time=1.2); t += 1.2

        # Bacteria start flickering
        self.play(
            *[b.animate.set_opacity(np.random.uniform(0.1, 0.5)) for b in friendly],
            run_time=0.8,
        )                                                                   # t=3.3

        self.play(FadeIn(not_infection, scale=1.1), run_time=0.4); t += 0.4
        self.play(Flash(not_infection.get_center(), color=DANGER_RED,
                        line_length=0.3, num_lines=6, run_time=0.3))      # t=4.0

        self.play(FadeIn(ear_label), GrowArrow(ear_arrow), run_time=0.4); t += 0.4
        self.play(FadeIn(footer), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 7.4)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 3: THE WRONG ANSWER (13.0–18.0s)
# "Guided missile" myth → 90% to ear, 10% elsewhere
# ================================================================
class Scene3_WrongAnswer(Scene):
    DURATION = 5.7
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill_label = label_pill("WHAT YOU THINK", color=WARN_ORANGE)
        pill_label.move_to(UP * 6.2)

        # Pill at center
        pill = RoundedRectangle(width=1, height=0.5, corner_radius=0.15,
                                fill_color=DRUG_BLUE, fill_opacity=0.9, stroke_width=0)
        pill.move_to(UP * 2)

        # Big arrow to ear (90%)
        ear_dot = Dot(radius=0.25, color=DANGER_RED).move_to(RIGHT * 2.5 + UP * 4)
        ear_lbl = safe_text("EAR", font="Inter", font_size=20, color=WHITE_SOFT)
        ear_lbl.next_to(ear_dot, RIGHT, buff=0.2)

        big_arrow = Arrow(pill.get_right(), ear_dot.get_left(), color=DRUG_BLUE,
                          stroke_width=6, max_tip_length_to_length_ratio=0.1)
        pct_90 = safe_text("90%", font="Bebas Neue", font_size=60, color=DRUG_BLUE)
        pct_90.next_to(big_arrow, RIGHT, buff=0.2)

        # Thin trickle to "rest of body"
        body_dot = Dot(radius=0.15, color=MUTED).move_to(DOWN * 2)
        body_lbl = safe_text("REST OF BODY", font="Inter", font_size=18, color=MUTED)
        body_lbl.next_to(body_dot, DOWN, buff=0.2)
        thin_arrow = Arrow(pill.get_bottom(), body_dot.get_top(), color=MUTED,
                           stroke_width=1.5, max_tip_length_to_length_ratio=0.15)
        pct_10 = safe_text("10%", font="Inter", font_size=30, color=MUTED)
        pct_10.next_to(thin_arrow, LEFT, buff=0.2)

        # "GUIDED MISSILE" label
        myth = safe_text("GUIDED MISSILE", font="Bebas Neue", font_size=50, color=WARN_ORANGE)
        myth.move_to(DOWN * 4.5)

        footer = safe_text("this is what people imagine", font="Inter",
                           font_size=18, color=MUTED)
        footer.move_to(DOWN * 6.0)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(pill), run_time=0.3); t += 0.3
        self.play(FadeIn(ear_dot), FadeIn(ear_lbl), run_time=0.3); t += 0.3
        self.play(GrowArrow(big_arrow), run_time=0.5); t += 0.5
        self.play(FadeIn(pct_90, scale=1.1), run_time=0.3); t += 0.3
        self.play(FadeIn(body_dot), FadeIn(body_lbl), run_time=0.3); t += 0.3
        self.play(GrowArrow(thin_arrow), FadeIn(pct_10), run_time=0.4); t += 0.4
        self.play(FadeIn(myth, shift=UP * 0.2), run_time=0.4); t += 0.4
        self.play(FadeIn(footer), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 5.7)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 4: THE CONTRADICTION (18.0–24.5s)
# Smash the myth → heart pumps equally to ALL organs
# ================================================================
class Scene4_Truth(Scene):
    DURATION = 7.4
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill_label = label_pill("THE TRUTH", color=DANGER_RED)
        pill_label.move_to(UP * 6.2)

        # Heart at center
        heart = heart_pump(size=1.2, color=DANGER_RED)
        heart.move_to(UP * 1)

        # Organs as labeled dots radiating outward
        organs = [
            ("EAR", RIGHT * 2.5 + UP * 4),
            ("GUT", DOWN * 0.5),
            ("KIDNEYS", LEFT * 3 + UP * 2),
            ("LIVER", RIGHT * 3 + UP * 2),
            ("BRAIN", UP * 4),
            ("KNEES", LEFT * 2 + DOWN * 3),
            ("SKIN", RIGHT * 2 + DOWN * 3),
        ]
        organ_dots = VGroup()
        organ_labels = VGroup()
        organ_arrows = VGroup()
        for name, pos in organs:
            d = Dot(radius=0.15, color=DRUG_BLUE).move_to(pos)
            l = safe_text(name, font="Inter", font_size=16, color=WHITE_SOFT)
            l.next_to(d, DOWN, buff=0.1)
            a = Arrow(heart.get_center(), d.get_center(), color=DRUG_BLUE,
                      stroke_width=2, max_tip_length_to_length_ratio=0.12,
                      buff=0.2)
            organ_dots.add(d)
            organ_labels.add(l)
            organ_arrows.add(a)

        # "EVERY TISSUE" flash
        every = safe_text("EVERY TISSUE", font="Bebas Neue", font_size=80, color=DRUG_BLUE)
        every.move_to(DOWN * 5.5)

        footer = safe_text("the heart pumps drug everywhere equally", font="Inter",
                           font_size=18, color=MUTED)
        footer.move_to(DOWN * 6.5)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3

        # Heart appears with pulse
        self.play(GrowFromCenter(heart), run_time=0.4); t += 0.4
        self.play(heart.animate.scale(1.15), run_time=0.15); t += 0.15
        self.play(heart.animate.scale(1/1.15), run_time=0.15); t += 0.15

        # Arrows spray out to all organs simultaneously
        self.play(
            LaggedStart(*[GrowArrow(a) for a in organ_arrows], lag_ratio=0.06),
            run_time=0.8,
        )                                                                   # t=1.8
        self.play(
            LaggedStart(*[FadeIn(d, scale=2) for d in organ_dots], lag_ratio=0.06),
            LaggedStart(*[FadeIn(l) for l in organ_labels], lag_ratio=0.06),
            run_time=0.6,
        )                                                                   # t=2.4

        # All arrows pulse — same thickness (equal distribution)
        self.play(*[a.animate.set_stroke(width=4) for a in organ_arrows],
                  run_time=0.4)                                            # t=2.8

        self.wait(0.7); t += 0.7
        self.play(FadeIn(every, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(every.get_center(), color=DRUG_BLUE,
                        line_length=0.4, num_lines=8, run_time=0.3))      # t=4.3
        self.play(FadeIn(footer), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 7.4)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 5: THE PROOF (24.5–31.0s)
# Gut bacteria dying + stat bars (diarrhea, yeast, C. diff)
# ================================================================
class Scene5_Cost(Scene):
    DURATION = 7.4
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill_label = label_pill("THE COST", color=DANGER_RED)
        pill_label.move_to(UP * 6.2)

        # Gut bacteria field — green dots turning gray
        bacteria = VGroup()
        np.random.seed(99)
        for _ in range(25):
            b = bacteria_dot(0.08, GUT_GREEN)
            b.move_to(np.array([np.random.uniform(-3.5, 3.5),
                                np.random.uniform(2, 4.5), 0]))
            bacteria.add(b)

        # Blue wave sweeping through
        wave = Rectangle(width=0.5, height=4, fill_color=DRUG_BLUE, fill_opacity=0.2,
                         stroke_width=0)
        wave.move_to(LEFT * 5 + UP * 3)

        # Stat bars at ZONE_LOWER
        bar_y = -5.5
        stats = [
            ("DIARRHEA", "5-39%", 2.5, WARN_ORANGE),
            ("YEAST", "10-30%", 1.8, DANGER_RED),
            ("C. DIFF", "500K/yr", 3.0, DANGER_RED),
        ]
        stat_bars = VGroup()
        stat_labels = VGroup()
        stat_values = VGroup()
        for i, (name, val, bar_h, col) in enumerate(stats):
            x = -2.5 + i * 2.5
            bar = Rectangle(width=1.5, height=bar_h, fill_color=col, fill_opacity=0.6,
                            stroke_width=0)
            bar.move_to(RIGHT * x + UP * (bar_y + bar_h / 2))
            lbl = safe_text(name, font="Inter", font_size=16, color=MUTED)
            lbl.next_to(bar, DOWN, buff=0.15)
            v = safe_text(val, font="Bebas Neue", font_size=28, color=col)
            v.next_to(bar, UP, buff=0.1)
            stat_bars.add(bar)
            stat_labels.add(lbl)
            stat_values.add(v)

        footer = safe_text("side effects of flooding every tissue", font="Inter",
                           font_size=18, color=MUTED)
        footer.move_to(DOWN * 6.2)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3
        self.play(LaggedStart(*[FadeIn(b, scale=2) for b in bacteria],
                              lag_ratio=0.02), run_time=0.5)              # t=0.8

        # Wave sweeps through
        self.play(wave.animate.move_to(RIGHT * 5 + UP * 3), run_time=1.2); t += 1.2

        # Bacteria turn gray and fade
        self.play(
            *[b.animate.set_color(DEAD_GRAY).set_opacity(0.2) for b in bacteria],
            run_time=0.8,
        )                                                                   # t=2.8

        # Stat bars rise
        self.play(
            LaggedStart(*[FadeIn(b, shift=UP * 0.3) for b in stat_bars], lag_ratio=0.15),
            LaggedStart(*[FadeIn(l) for l in stat_labels], lag_ratio=0.15),
            run_time=0.8,
        )                                                                   # t=3.6
        self.play(
            LaggedStart(*[FadeIn(v, scale=1.1) for v in stat_values], lag_ratio=0.15),
            run_time=0.5,
        )                                                                   # t=4.1
        self.play(FadeIn(footer), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 7.4)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 6: THE PUNCH (31.0–40.0s)
# Body silhouette: ear healed, gut devastated → "6+ MONTHS" → "NEVER"
# ================================================================
class Scene6_Aftermath(Scene):
    DURATION = 10.2
    def construct(self):
        self.add(gradient_bg("#0A0E18"), grid_lines(0.02))
        t = 0

        pill_label = label_pill("THE AFTERMATH", color=DANGER_RED)
        pill_label.move_to(UP * 6.2)

        # Body silhouette
        body = body_silhouette(height=8, color=BODY_PURPLE)
        body.move_to(UP * 1)

        # Ear: green check (healed)
        ear_check = safe_text("✓", font="Inter", font_size=30, color=GUT_GREEN)
        ear_check.move_to(UP * 4.5 + RIGHT * 1.2)
        ear_lbl = safe_text("HEALED", font="Inter", font_size=16, color=GUT_GREEN)
        ear_lbl.next_to(ear_check, RIGHT, buff=0.15)

        # Gut: red X (wrecked)
        gut_x = safe_text("✕", font="Inter", font_size=30, color=DANGER_RED)
        gut_x.move_to(UP * 1.5 + RIGHT * 1.5)
        gut_lbl = safe_text("WRECKED", font="Inter", font_size=16, color=DANGER_RED)
        gut_lbl.next_to(gut_x, RIGHT, buff=0.15)

        # Timeline bar at ZONE_LOWER
        timeline_bg = Rectangle(width=7, height=0.4, fill_color=SURFACE, fill_opacity=0.5,
                                stroke_color=MUTED, stroke_width=1)
        timeline_bg.move_to(DOWN * 3)
        # Recovery progress (partial)
        recovery = Rectangle(width=4, height=0.3, fill_color=WARN_ORANGE, fill_opacity=0.5,
                             stroke_width=0)
        recovery.align_to(timeline_bg, LEFT).shift(RIGHT * 0.1)
        recovery.move_to(DOWN * 3 + LEFT * 1.4)
        tl_label = safe_text("6+ MONTHS", font="Bebas Neue", font_size=60, color=WARN_ORANGE)
        tl_label.move_to(DOWN * 4.2)

        # "SOME SPECIES" text
        never = safe_text("NEVER RETURN", font="Bebas Neue", font_size=70, color=DANGER_RED)
        never.move_to(DOWN * 5.5)

        # ── Timing: 9.00s ──
        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(body), run_time=0.5); t += 0.5

        # Ear healed
        self.play(FadeIn(ear_check, scale=1.5), FadeIn(ear_lbl), run_time=0.4); t += 0.4

        # Gut wrecked
        self.wait(0.5); t += 0.5
        self.play(FadeIn(gut_x, scale=1.5), FadeIn(gut_lbl), run_time=0.4); t += 0.4

        # Gut area dims/empties
        self.play(body[1].animate.set_fill(DEAD_GRAY, opacity=0.1), run_time=0.5); t += 0.5

        # Timeline
        self.play(FadeIn(timeline_bg), run_time=0.3); t += 0.3
        self.play(FadeIn(recovery), run_time=0.5); t += 0.5
        self.play(FadeIn(tl_label, scale=1.1), run_time=0.4); t += 0.4

        # "NEVER RETURN"
        self.wait(1.0); t += 1.0
        self.play(FadeIn(never, scale=1.15), run_time=0.5); t += 0.5
        self.play(Flash(never.get_center(), color=DANGER_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))      # t=5.6

        # Hold
        target = getattr(self.__class__, 'DURATION', 10.2)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.0); t += 1.0


# ── Infra ─────────────────────────────────────────────────────
SCENES = [Scene1_Hook, Scene2_GutFlood, Scene3_WrongAnswer,
          Scene4_Truth, Scene5_Cost, Scene6_Aftermath]

def render_single_scene(idx):
    config.output_file = f"antibiotics_no_gps_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    SCENES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"antibiotics_no_gps_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENES):
        n = f"antibiotics_no_gps_scene_{i+1}"; print(f"  Preview {n}...")
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
    audio = od / "tts_antibiotics_no_gps.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="antibiotics_no_gps", audio_path=str(audio))
    final = od / "antibiotics_no_gps_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")

    from render_utils import run_post_render_qa
    run_post_render_qa(str(final), scene_count=6)
