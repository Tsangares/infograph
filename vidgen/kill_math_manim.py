#!/usr/bin/env python3
"""The Math of Killing — Tidal wave vs campfire dosing strategies.

6 scenes, ~40.0s (37.0s audio + 3s hold).
Domain shapes: pill_bottle, concentration_curve, bacteria_cluster, clock_face.

VTT cues (absolute → relative):
  Scene 1 (0.0–6.0s):   0.30 some antibiotics... 2.80 once a day... 4.60 different rules
  Scene 2 (6.0–11.5s):  6.30 every antibiotic... 8.50 MIC line... 10.80 battlefield
  Scene 3 (11.5–16.5s): 11.80 assumption... 13.60 more drug... 15.40 pile it on
  Scene 4 (16.5–25.0s): 16.80 tidal wave... 19.40 campfire... 22.00 different math... 24.20 split
  Scene 5 (25.0–33.0s): 25.40 gentamicin... 27.80 amoxicillin... 30.20 miss dose... 32.00 regrow
  Scene 6 (33.0–40.0s): 33.40 schedule... 35.60 not arbitrary... 37.80 war strategy
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """Some antibiotics you take once a day. Others, four times. Same disease. Both work. Every antibiotic has a kill line — the MIC. Above it, bacteria die. Below, they grow. Gentamicin is a tidal wave. One massive dose, ten times the MIC. Bacteria can't recover for hours. Amoxicillin is a campfire. It stays above the line constantly. Miss a dose, bacteria regrow in the gap. Your dosing schedule isn't arbitrary. It's a war strategy."""

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
WAVE_BLUE = "#3B82F6"; FIRE_ORANGE = "#F59E0B"; BACTERIA_GREEN = "#22C55E"
DANGER_RED = "#EF4444"; MIC_RED = "#DC2626"; MUTED = "#475569"
DIM = "#334155"

SAFE_W = 8.0
SAFE_TOP = 7.2
SAFE_BOT = -6.4

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

def pill_bottle(height=2.0, color=WAVE_BLUE):
    """Simple pill bottle — rectangle with cap."""
    body = RoundedRectangle(width=height*0.4, height=height*0.65, corner_radius=height*0.05,
                            fill_color=color, fill_opacity=0.3, stroke_color=color, stroke_width=2)
    cap = Rectangle(width=height*0.35, height=height*0.12, fill_color=color,
                    fill_opacity=0.6, stroke_width=0)
    cap.next_to(body, UP, buff=0)
    label_rect = Rectangle(width=height*0.3, height=height*0.2, fill_color=WHITE_SOFT,
                           fill_opacity=0.15, stroke_width=0)
    label_rect.move_to(body)
    return VGroup(body, cap, label_rect)

def bacteria_cluster(n=6, color=BACTERIA_GREEN, spread=0.8):
    """Cluster of small bacteria dots."""
    grp = VGroup()
    np.random.seed(77)
    for _ in range(n):
        b = RoundedRectangle(width=0.2, height=0.1, corner_radius=0.04,
                             fill_color=color, fill_opacity=0.7, stroke_width=0)
        b.move_to(np.array([np.random.uniform(-spread, spread),
                            np.random.uniform(-spread/2, spread/2), 0]))
        grp.add(b)
    return grp

def clock_face(radius=1.0, color=WHITE_SOFT):
    """Simple clock face with tick marks."""
    face = Circle(radius=radius, stroke_color=color, stroke_width=2,
                  fill_color=SURFACE, fill_opacity=0.3)
    ticks = VGroup()
    for h in range(12):
        angle = h * 30 * PI / 180
        outer = np.array([np.cos(angle)*radius*0.85, np.sin(angle)*radius*0.85, 0])
        inner = np.array([np.cos(angle)*radius*0.7, np.sin(angle)*radius*0.7, 0])
        ticks.add(Line(inner, outer, color=color, stroke_width=1.5))
    return VGroup(face, ticks)

def concentration_curve(width=5.0, peak_height=3.0, color=WAVE_BLUE, style="spike"):
    """Drug concentration curve — spike (tidal wave) or sustained (campfire).

    style="spike": single tall peak that drops fast (gentamicin).
    style="sustained": three even humps (amoxicillin / campfire).
    Returns a VGroup of the curve shape(s).
    """
    if style == "spike":
        pts = [
            np.array([-width/2, 0, 0]),
            np.array([-width*0.15, peak_height, 0]),
            np.array([width*0.1, peak_height*0.3, 0]),
            np.array([width/2, 0, 0]),
        ]
        curve = Polygon(*pts, fill_color=color, fill_opacity=0.2,
                         stroke_color=color, stroke_width=2)
        return VGroup(curve)
    else:  # sustained
        bumps = VGroup()
        bump_w = width / 3.5
        for i in range(3):
            bump = RoundedRectangle(width=bump_w, height=peak_height*0.6,
                                    corner_radius=0.25,
                                    fill_color=color, fill_opacity=0.15,
                                    stroke_color=color, stroke_width=1.5)
            bump.move_to(RIGHT * (-width/3 + i * width/3))
            bumps.add(bump)
        return bumps


# ================================================================
# SCENE 1: THE HOOK (0.0–6.0s)
# Two pill bottles side by side — "1x/DAY" vs "4x/DAY"
# Zones: TITLE, UPPER+MID (bottles), LOWER (question), FOOTER (clock)
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 6.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE
        pill_label = label_pill("THE MATH OF KILLING", color=GOLD)
        pill_label.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER — two bottles centered at ~ZONE_UPPER
        bottle1 = pill_bottle(height=3, color=WAVE_BLUE)
        bottle1.move_to(LEFT * 2 + UP * ZONE_UPPER)
        lbl1 = safe_text("1x / DAY", font="Bebas Neue", font_size=40, color=WAVE_BLUE)
        lbl1.next_to(bottle1, DOWN, buff=0.3)

        bottle2 = pill_bottle(height=3, color=FIRE_ORANGE)
        bottle2.move_to(RIGHT * 2 + UP * ZONE_UPPER)
        lbl2 = safe_text("4x / DAY", font="Bebas Neue", font_size=40, color=FIRE_ORANGE)
        lbl2.next_to(bottle2, DOWN, buff=0.3)

        vs = safe_text("VS", font="Bebas Neue", font_size=60, color=MUTED)
        vs.move_to(UP * ZONE_UPPER)

        # ZONE_LOWER — question text
        question = safe_text("same disease. both work. why?", font="DM Serif Display",
                             font_size=32, color=WHITE_SOFT)
        question.move_to(UP * ZONE_LOWER)

        # ZONE_FOOTER — clock
        clk = clock_face(radius=1.0, color=DIM)
        clk.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(bottle1, scale=0.9), FadeIn(lbl1), run_time=0.5); t += 0.5
        self.play(FadeIn(vs), run_time=0.2); t += 0.2
        self.play(FadeIn(bottle2, scale=0.9), FadeIn(lbl2), run_time=0.5); t += 0.5
        self.play(FadeIn(question, shift=UP * 0.1), run_time=0.4); t += 0.4
        self.play(FadeIn(clk), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 6.0)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE MIC LINE (6.0–11.5s)
# Graph axes + MIC dashed line — above = kill, below = grow
# Zones: TITLE, UPPER (axes+MIC), MID (zones), LOWER (arrows), FOOTER
# ================================================================
class Scene2_MICLine(Scene):
    DURATION = 5.5
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE
        pill_label = label_pill("THE LINE", color=MIC_RED)
        pill_label.move_to(UP * ZONE_TITLE)

        # ZONE_MID — graph axes centered at MID, spanning UPPER to LOWER
        origin_pt = LEFT * 3.5 + DOWN * 1.5
        x_axis = Arrow(origin_pt, origin_pt + RIGHT * 7, color=MUTED, stroke_width=2,
                       max_tip_length_to_length_ratio=0.05)
        y_axis = Arrow(origin_pt, origin_pt + UP * 8, color=MUTED, stroke_width=2,
                       max_tip_length_to_length_ratio=0.05)
        x_lbl = safe_text("TIME", font="Inter", font_size=18, color=MUTED)
        x_lbl.next_to(x_axis, DOWN, buff=0.1)
        y_lbl = safe_text("DRUG LEVEL", font="Inter", font_size=18, color=MUTED)
        y_lbl.next_to(y_axis, LEFT, buff=0.1).rotate(90 * DEGREES)

        # MIC dashed line at ZONE_MID
        mic_y = ZONE_MID + 1.0
        mic_line = DashedLine(LEFT * 3.5 + UP * mic_y, RIGHT * 3.5 + UP * mic_y,
                              color=MIC_RED, stroke_width=2, dash_length=0.2)
        mic_label = safe_text("MIC", font="Bebas Neue", font_size=36, color=MIC_RED)
        mic_label.next_to(mic_line, RIGHT, buff=0.2)

        # Above = kill (ZONE_UPPER area)
        kill_zone = safe_text("BACTERIA DIE", font="Inter", font_size=20,
                              color=BACTERIA_GREEN, weight="BOLD")
        kill_zone.move_to(UP * ZONE_UPPER + RIGHT * 1)
        up_arrow = Arrow(UP * 2.5 + RIGHT * 1, UP * 3.5 + RIGHT * 1, color=BACTERIA_GREEN,
                         stroke_width=2)

        # Below = grow (ZONE_LOWER area)
        grow_zone = safe_text("BACTERIA GROW", font="Inter", font_size=20,
                              color=DANGER_RED, weight="BOLD")
        grow_zone.move_to(UP * ZONE_LOWER + RIGHT * 1)
        down_arrow = Arrow(DOWN * 2.5 + RIGHT * 1, DOWN * 3.5 + RIGHT * 1, color=DANGER_RED,
                           stroke_width=2)

        # Bacteria clusters in lower zone to show what's at stake
        bact_alive = bacteria_cluster(5, BACTERIA_GREEN, 0.6)
        bact_alive.move_to(LEFT * 2 + DOWN * 4)

        # ZONE_FOOTER
        footer = safe_text("crossing this line changes everything", font="Inter",
                           font_size=18, color=MUTED)
        footer.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3
        self.play(GrowArrow(x_axis), GrowArrow(y_axis), run_time=0.5); t += 0.5
        self.play(FadeIn(x_lbl), FadeIn(y_lbl), run_time=0.2); t += 0.2
        self.play(Create(mic_line), FadeIn(mic_label), run_time=0.5); t += 0.5
        self.play(Flash(mic_label.get_center(), color=MIC_RED,
                        line_length=0.2, num_lines=6, run_time=0.3))      # t=1.8
        self.play(FadeIn(kill_zone), GrowArrow(up_arrow), run_time=0.4); t += 0.4
        self.play(FadeIn(grow_zone), GrowArrow(down_arrow),
                  FadeIn(bact_alive), run_time=0.4)                       # t=2.6
        self.play(FadeIn(footer), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 5.5)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: THE WRONG ANSWER (11.5–16.5s)
# "More = better" myth — stacking bars
# Zones: TITLE, UPPER+MID (bars), LOWER (label), FOOTER
# ================================================================
class Scene3_WrongAnswer(Scene):
    DURATION = 5.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE
        pill_label = label_pill("WHAT YOU THINK", color=FIRE_ORANGE)
        pill_label.move_to(UP * ZONE_TITLE)

        # Bars spanning ZONE_MID to ZONE_UPPER — bases at y=-1 (below MID)
        bars = VGroup()
        bar_base_y = -1.0
        for i, h in enumerate([2.5, 4.0, 5.5]):
            bar = Rectangle(width=2, height=h, fill_color=WAVE_BLUE,
                            fill_opacity=0.4 + i * 0.15, stroke_color=WAVE_BLUE, stroke_width=1)
            bar.move_to(LEFT * 2.5 + RIGHT * i * 2.5 + UP * (bar_base_y + h / 2))
            bars.add(bar)

        # Arrow pointing up alongside bars
        more_arrow = Arrow(RIGHT * 3.5 + UP * (bar_base_y), RIGHT * 3.5 + UP * 4.5,
                           color=FIRE_ORANGE, stroke_width=4,
                           max_tip_length_to_length_ratio=0.1)

        # ZONE_LOWER — "MORE = BETTER" label
        more_label = safe_text("MORE = BETTER", font="Bebas Neue", font_size=50, color=FIRE_ORANGE)
        more_label.move_to(UP * ZONE_LOWER)

        # Below ZONE_LOWER
        wrong = safe_text("only half right", font="Inter", font_size=22, color=DANGER_RED)
        wrong.move_to(DOWN * 4.8)

        # ZONE_FOOTER
        footer = safe_text("true for some drugs, wrong for others", font="Inter",
                           font_size=18, color=MUTED)
        footer.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3
        self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.3) for b in bars],
                              lag_ratio=0.2), run_time=0.8)               # t=1.1
        self.play(GrowArrow(more_arrow), run_time=0.4); t += 0.4
        self.play(FadeIn(more_label, scale=1.1), run_time=0.4); t += 0.4
        self.play(FadeIn(wrong), FadeIn(footer), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 5.0)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE CONTRADICTION (16.5–25.0s)
# Split screen: TIDAL WAVE (left) vs CAMPFIRE (right)
# Zones: TITLE, UPPER (labels), MID (curves+MIC), LOWER (bacteria), FOOTER
# ================================================================
class Scene4_TwoStrategies(Scene):
    DURATION = 8.5
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE
        pill_label = label_pill("TWO STRATEGIES", color=GOLD)
        pill_label.move_to(UP * ZONE_TITLE)

        # Divider spanning UPPER to LOWER
        divider = DashedLine(UP * 5.5, DOWN * 5.5, color=MUTED, stroke_width=1, dash_length=0.2)

        # LEFT: TIDAL WAVE — label in ZONE_UPPER
        wave_title = safe_text("TIDAL WAVE", font="Bebas Neue", font_size=36, color=WAVE_BLUE)
        wave_title.move_to(LEFT * 2.2 + UP * ZONE_UPPER)

        # Spike curve using domain shape — centered at ZONE_MID
        spike = concentration_curve(width=4.0, peak_height=4.0, color=WAVE_BLUE, style="spike")
        spike.move_to(LEFT * 2.2 + UP * ZONE_MID)

        # MIC line (left side)
        mic_l = DashedLine(LEFT * 4 + DOWN * 0.5, LEFT * 0.5 + DOWN * 0.5, color=MIC_RED,
                           stroke_width=1.5, dash_length=0.15)
        mic_l_lbl = safe_text("MIC", font="Inter", font_size=14, color=MIC_RED)
        mic_l_lbl.next_to(mic_l, LEFT, buff=0.1)

        # Bacteria under spike — ZONE_LOWER
        dead_bact_l = bacteria_cluster(4, BACTERIA_GREEN, 0.6)
        dead_bact_l.move_to(LEFT * 2.2 + UP * ZONE_LOWER)

        # RIGHT: CAMPFIRE — label in ZONE_UPPER
        fire_title = safe_text("CAMPFIRE", font="Bebas Neue", font_size=36, color=FIRE_ORANGE)
        fire_title.move_to(RIGHT * 2.2 + UP * ZONE_UPPER)

        # Sustained bumps using domain shape — centered at ZONE_MID
        bumps = concentration_curve(width=4.0, peak_height=3.0, color=FIRE_ORANGE, style="sustained")
        bumps.move_to(RIGHT * 2.2 + UP * ZONE_MID)

        # MIC line (right side)
        mic_r = DashedLine(RIGHT * 0.5 + DOWN * 0.5, RIGHT * 4.2 + DOWN * 0.5, color=MIC_RED,
                           stroke_width=1.5, dash_length=0.15)

        # Bacteria under campfire — ZONE_LOWER
        dead_bact_r = bacteria_cluster(4, BACTERIA_GREEN, 0.6)
        dead_bact_r.move_to(RIGHT * 2.2 + UP * ZONE_LOWER)

        # ZONE_FOOTER
        footer = safe_text("same goal, different rules", font="Inter",
                           font_size=18, color=MUTED)
        footer.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3
        self.play(Create(divider), run_time=0.3); t += 0.3

        # Left: tidal wave
        self.play(FadeIn(wave_title), run_time=0.3); t += 0.3
        self.play(FadeIn(spike), Create(mic_l), FadeIn(mic_l_lbl), run_time=0.5); t += 0.5
        self.play(FadeIn(dead_bact_l), run_time=0.3); t += 0.3
        self.play(*[b.animate.set_opacity(0.15) for b in dead_bact_l], run_time=0.4); t += 0.4

        # Right: campfire
        self.play(FadeIn(fire_title), run_time=0.3); t += 0.3
        self.play(LaggedStart(*[FadeIn(b) for b in bumps], lag_ratio=0.1),
                  Create(mic_r), run_time=0.6)                            # t=3.0
        self.play(FadeIn(dead_bact_r), run_time=0.3); t += 0.3
        self.play(*[b.animate.set_opacity(0.15) for b in dead_bact_r], run_time=0.6); t += 0.6

        self.play(FadeIn(footer), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 8.5)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE PROOF (25.0–33.0s)
# Gentamicin: one peak + PAE glow vs Amoxicillin: three bumps + gap danger
# Zones: TITLE, UPPER (gentamicin), MID (divider+MIC), LOWER (amoxicillin), FOOTER
# ================================================================
class Scene5_Proof(Scene):
    DURATION = 8.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE
        pill_label = label_pill("THE PROOF", color=GOLD)
        pill_label.move_to(UP * ZONE_TITLE)

        # ── GENTAMICIN section (ZONE_UPPER) ──
        gent_label = safe_text("GENTAMICIN", font="Bebas Neue", font_size=36, color=WAVE_BLUE)
        gent_label.move_to(LEFT * 2.5 + UP * 5.0)

        # Spike curve centered in upper zone
        gent_spike = concentration_curve(width=5.0, peak_height=3.0, color=WAVE_BLUE, style="spike")
        gent_spike.move_to(LEFT * 0.5 + UP * ZONE_UPPER)

        ratio_lbl = safe_text("8-10x MIC", font="Bebas Neue", font_size=28, color=WAVE_BLUE)
        ratio_lbl.move_to(UP * 5.2 + RIGHT * 1.5)

        # PAE glow zone after spike
        pae = Rectangle(width=2, height=0.8, fill_color=WAVE_BLUE, fill_opacity=0.08,
                        stroke_color=WAVE_BLUE, stroke_width=1)
        pae.move_to(RIGHT * 2.5 + UP * 3.0)
        pae_lbl = safe_text("STUNNED", font="Inter", font_size=16, color=WAVE_BLUE)
        pae_lbl.move_to(pae)

        once_daily = safe_text("1x / DAY", font="Inter", font_size=22, color=WAVE_BLUE, weight="BOLD")
        once_daily.move_to(RIGHT * 3.5 + UP * 4.5)

        # ── MIC line at ZONE_MID ──
        mic_line = DashedLine(LEFT * 4 + UP * ZONE_MID, RIGHT * 4 + UP * ZONE_MID,
                              color=MIC_RED, stroke_width=1.5, dash_length=0.15)
        mic_lbl = safe_text("MIC", font="Inter", font_size=16, color=MIC_RED)
        mic_lbl.next_to(mic_line, RIGHT, buff=0.15)

        # ── AMOXICILLIN section (ZONE_LOWER) ──
        amox_label = safe_text("AMOXICILLIN", font="Bebas Neue", font_size=36, color=FIRE_ORANGE)
        amox_label.move_to(LEFT * 2.5 + DOWN * 1.5)

        # Three bumps using domain shape
        amox_bumps = concentration_curve(width=6.0, peak_height=2.5, color=FIRE_ORANGE, style="sustained")
        amox_bumps.move_to(UP * ZONE_LOWER)

        three_daily = safe_text("3x / DAY", font="Inter", font_size=22, color=FIRE_ORANGE, weight="BOLD")
        three_daily.move_to(RIGHT * 3.5 + DOWN * 2.0)

        # Gap danger — between bumps in ZONE_LOWER
        gap = Rectangle(width=0.5, height=1.5, fill_color=DANGER_RED, fill_opacity=0.15,
                        stroke_color=DANGER_RED, stroke_width=1)
        gap.move_to(UP * ZONE_LOWER)
        gap_lbl = safe_text("REGROWTH", font="Inter", font_size=14, color=DANGER_RED)
        gap_lbl.next_to(gap, DOWN, buff=0.1)

        # ZONE_FOOTER
        footer = safe_text("miss a dose — different consequences", font="Inter",
                           font_size=18, color=MUTED)
        footer.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3

        # Gentamicin
        self.play(FadeIn(gent_label), run_time=0.2); t += 0.2
        self.play(FadeIn(gent_spike), run_time=0.4); t += 0.4
        self.play(FadeIn(ratio_lbl, scale=1.1), run_time=0.3); t += 0.3
        self.play(FadeIn(pae), FadeIn(pae_lbl), run_time=0.3); t += 0.3
        self.play(FadeIn(once_daily), run_time=0.2); t += 0.2

        # MIC line
        self.play(Create(mic_line), FadeIn(mic_lbl), run_time=0.3); t += 0.3

        # Amoxicillin
        self.play(FadeIn(amox_label), run_time=0.2); t += 0.2
        self.play(LaggedStart(*[FadeIn(b) for b in amox_bumps],
                              lag_ratio=0.15), run_time=0.6)              # t=2.8
        self.play(FadeIn(three_daily), run_time=0.2); t += 0.2

        # Gap danger
        self.wait(0.8); t += 0.8
        self.play(FadeIn(gap), FadeIn(gap_lbl), run_time=0.4); t += 0.4
        self.play(Flash(gap.get_center(), color=DANGER_RED,
                        line_length=0.2, num_lines=6, run_time=0.3))      # t=4.5
        self.play(FadeIn(footer), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 8.0)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE PUNCH (33.0–40.0s)
# Pill bottle → "WAR STRATEGY" → the schedule IS the science
# Zones: TITLE (pill label), UPPER (bottle), MID (WAR STRATEGY), LOWER (sub), FOOTER
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 7.0
    def construct(self):
        self.add(gradient_bg("#0A0E18"), grid_lines(0.02))
        t = 0

        # ZONE_TITLE — subtle pill
        title_pill = label_pill("THE SCHEDULE", color=GOLD)
        title_pill.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER — large pill bottle centered at hero position
        bottle = pill_bottle(height=4, color=GOLD)
        bottle.move_to(UP * ZONE_UPPER)

        # Schedule text on bottle
        sched = safe_text("EVERY 8 HRS", font="Bebas Neue", font_size=30, color=WHITE_SOFT)
        sched.move_to(bottle.get_center())

        # ZONE_MID — "WAR STRATEGY" big reveal
        war = safe_text("WAR STRATEGY", font="Bebas Neue", font_size=80, color=GOLD)
        war.move_to(UP * ZONE_MID)

        # ZONE_LOWER — subtitle
        sub = safe_text("not arbitrary. calculated.", font="DM Serif Display",
                        font_size=32, color=MUTED)
        sub.move_to(UP * ZONE_LOWER)

        # Clock at bottom to bookend scene 1
        clk = clock_face(radius=0.8, color=DIM)
        clk.move_to(DOWN * 4.8)

        # ZONE_FOOTER
        footer = safe_text("half-life x killing pattern x MIC = schedule",
                           font="Inter", font_size=18, color=MUTED)
        footer.move_to(UP * ZONE_FOOTER)

        # ── Timing: 7.00s ──
        self.play(FadeIn(title_pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(GrowFromCenter(bottle), run_time=0.6); t += 0.6
        self.play(FadeIn(sched), run_time=0.3); t += 0.3

        self.wait(1.3); t += 1.3
        self.play(FadeIn(war, scale=1.15), run_time=0.5); t += 0.5
        self.play(Flash(war.get_center(), color=GOLD,
                        line_length=0.4, num_lines=8, run_time=0.3))      # t=3.3
        self.play(FadeIn(sub, shift=UP * 0.05), run_time=0.4); t += 0.4
        self.play(FadeIn(clk), run_time=0.2); t += 0.2
        self.play(FadeIn(footer), run_time=0.3); t += 0.3

        # Hold
        target = getattr(self.__class__, 'DURATION', 7.0)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.0); t += 1.0


# ── Infra ─────────────────────────────────────────────────────
SCENES = [Scene1_Hook, Scene2_MICLine, Scene3_WrongAnswer,
          Scene4_TwoStrategies, Scene5_Proof, Scene6_Punch]

def render_single_scene(idx):
    config.output_file = f"kill_math_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    SCENES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"kill_math_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENES):
        n = f"kill_math_scene_{i+1}"; print(f"  Preview {n}...")
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
    audio = od / "tts_kill_math.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="kill_math", audio_path=str(audio))
    final = od / "kill_math_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")

    from render_utils import run_post_render_qa
    run_post_render_qa(str(final), scene_count=6)
