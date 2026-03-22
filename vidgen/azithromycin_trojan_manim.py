#!/usr/bin/env python3
"""Azithromycin's Trojan Horse — How a drug with 37% bioavailability dominates lungs.

6 scenes, ~40.0s (37.0s audio + 3s hold).
Domain shapes: pill_capsule, neutrophil_cell, lung_outline, bacteria_dot.

VTT cues (absolute → relative):
  Scene 1 (0.0–6.5s):   0.30 one of the most... 2.80 thirty-seven percent... 5.20 useless
  Scene 2 (6.5–12.0s):  6.80 bigger doses... 9.40 didn't help... 11.20 vanished
  Scene 3 (12.0–19.0s): 12.40 discovered... 14.80 hiding... 16.60 immune cells... 18.20 sponges
  Scene 4 (19.0–27.0s): 19.40 sixty to ninety-eight... 22.00 carrying it... 24.60 payload
  Scene 5 (27.0–33.0s): 27.40 immune system... 29.60 fighting... 31.40 delivery truck
  Scene 6 (33.0–40.0s): 33.40 wildest part... 35.80 keep delivering... 38.00 week after
"""

TTS_SCRIPT = """One of the most prescribed antibiotics in the world has a dirty secret. Only thirty-seven percent of it makes it into your blood. The rest? Useless.
So doctors tried bigger doses. It didn't help. The drug just vanished from the bloodstream.
Then someone discovered where it was hiding. Azithromycin wasn't floating in blood. It was inside your immune cells, soaking in like a sponge.
White blood cells carry sixty to ninety-eight times more drug than your blood plasma. They're not just fighting infection. They're carrying the payload directly to it.
Your immune system isn't just fighting alongside the drug. It's the delivery truck.
Here's the wildest part. You stop taking the pills after five days. But your immune cells keep delivering azithromycin for a week after your last dose. A hundred and thirty-three hours."""

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
config.background_color = "#080A10"
config.disable_caching = True

BG = "#080A10"; GRID = "#1A2030"; SURFACE = "#15192A"
WHITE_SOFT = "#F0F0F0"; GOLD = "#FFD700"
DRUG_BLUE = "#3B82F6"; CELL_CYAN = "#06B6D4"; LUNG_PINK = "#F472B6"
BACTERIA_GREEN = "#22C55E"; DANGER_RED = "#EF4444"; MUTED = "#475569"
DIM = "#334155"
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

def pill_capsule(height=2.0, color_top=DRUG_BLUE, color_bot="#1D4ED8"):
    """Vertical pill capsule — two halves."""
    top = RoundedRectangle(width=height*0.4, height=height*0.5, corner_radius=height*0.15,
                           fill_color=color_top, fill_opacity=0.9, stroke_width=0)
    top.move_to(UP * height * 0.22)
    bot = RoundedRectangle(width=height*0.4, height=height*0.5, corner_radius=height*0.15,
                           fill_color=color_bot, fill_opacity=0.9, stroke_width=0)
    bot.move_to(DOWN * height * 0.22)
    band = Rectangle(width=height*0.42, height=height*0.06, fill_color=WHITE_SOFT,
                     fill_opacity=0.3, stroke_width=0)
    return VGroup(top, bot, band)

def neutrophil_cell(radius=0.6, color=CELL_CYAN, glow=True):
    """Immune cell — blobby circle with lobed nucleus."""
    body = Circle(radius=radius, fill_color=color, fill_opacity=0.25,
                  stroke_color=color, stroke_width=2)
    # Multi-lobed nucleus
    lobes = VGroup()
    for angle in [0, 120, 240]:
        lobe = Circle(radius=radius*0.22, fill_color=color, fill_opacity=0.6, stroke_width=0)
        lobe.move_to(np.array([np.cos(angle*PI/180)*radius*0.25,
                               np.sin(angle*PI/180)*radius*0.25, 0]))
        lobes.add(lobe)
    grp = VGroup(body, lobes)
    if glow:
        halo = Circle(radius=radius*1.3, fill_color=color, fill_opacity=0.06, stroke_width=0)
        grp.add_to_back(halo)
    return grp

def lung_outline(height=6, color=LUNG_PINK):
    """Simplified pair of lungs — two rounded shapes with trachea."""
    left_lung = Ellipse(width=height*0.38, height=height*0.6, fill_color=color,
                        fill_opacity=0.12, stroke_color=color, stroke_width=1.5)
    left_lung.move_to(LEFT * height * 0.22 + DOWN * height * 0.08)
    right_lung = Ellipse(width=height*0.38, height=height*0.6, fill_color=color,
                         fill_opacity=0.12, stroke_color=color, stroke_width=1.5)
    right_lung.move_to(RIGHT * height * 0.22 + DOWN * height * 0.08)
    trachea = Line(UP * height * 0.35, DOWN * height * 0.05, color=color,
                   stroke_width=2)
    branch_l = Line(ORIGIN, LEFT * height * 0.15 + DOWN * height * 0.12,
                    color=color, stroke_width=1.5).move_to(DOWN * height * 0.02 + LEFT * height * 0.07)
    branch_r = Line(ORIGIN, RIGHT * height * 0.15 + DOWN * height * 0.12,
                    color=color, stroke_width=1.5).move_to(DOWN * height * 0.02 + RIGHT * height * 0.07)
    return VGroup(left_lung, right_lung, trachea, branch_l, branch_r)

def bacteria_dot(radius=0.12, color=BACTERIA_GREEN):
    """Single bacterium — small rod shape."""
    body = RoundedRectangle(width=radius*3, height=radius*1.2, corner_radius=radius*0.5,
                            fill_color=color, fill_opacity=0.8, stroke_width=0)
    return body


# ================================================================
# SCENE 1: THE HOOK (0.0–6.5s)
# Giant pill splits → "37%" → drug barely in blood
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 8.2
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill_label = label_pill("THE WORST DRUG?", color=DANGER_RED)
        pill_label.move_to(UP * 6.2)

        # Giant pill capsule
        cap = pill_capsule(height=4, color_top=DRUG_BLUE, color_bot="#1D4ED8")
        cap.move_to(UP * 1.5)

        # 37% number
        pct = safe_text("37%", font="Bebas Neue", font_size=180, color=DANGER_RED)
        pct.move_to(UP * 1.5)

        # Bloodstream ribbon at ZONE_LOWER
        stream = Rectangle(width=8, height=0.6, fill_color=DANGER_RED, fill_opacity=0.1,
                           stroke_color=DANGER_RED, stroke_width=1)
        stream.move_to(DOWN * 3.5)
        stream_label = safe_text("BLOOD LEVEL", font="Inter", font_size=22, color=MUTED)
        stream_label.next_to(stream, UP, buff=0.2)

        # Tiny drug particles in stream (barely any)
        particles = VGroup()
        for x in [-2.5, 0.5, 2.8]:
            d = Dot(radius=0.06, color=DRUG_BLUE).move_to(DOWN * 3.5 + RIGHT * x)
            particles.add(d)

        # Footer
        footer = safe_text("azithromycin bioavailability", font="Inter", font_size=18, color=MUTED)
        footer.move_to(DOWN * 6.0)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(cap, scale=0.9), run_time=0.6); t += 0.6

        # Pill splits apart
        self.wait(1.5); t += 1.5
        self.play(cap[0].animate.shift(UP * 0.8).set_opacity(0.3),
                  cap[1].animate.shift(DOWN * 0.8).set_opacity(0.3),
                  cap[2].animate.set_opacity(0), run_time=0.5)            # t=3.0

        # 37% appears
        self.play(FadeIn(pct, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(pct.get_center(), color=DANGER_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))      # t=3.8

        # Stream with barely any particles
        self.play(FadeIn(stream), FadeIn(stream_label), run_time=0.4); t += 0.4
        self.play(LaggedStart(*[FadeIn(p, scale=2) for p in particles],
                              lag_ratio=0.15), run_time=0.4)              # t=4.6
        self.play(FadeIn(footer), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 8.2)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 2: THE WRONG ANSWER (6.5–12.0s)
# Pile of pills → brute force fails → drug vanishes
# ================================================================
class Scene2_MorePills(Scene):
    DURATION = 7.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill_label = label_pill("MORE PILLS?", color=DRUG_BLUE)
        pill_label.move_to(UP * 6.2)

        # Stack of pills
        pills = VGroup()
        for i in range(6):
            p = pill_capsule(height=1.2)
            p.move_to(UP * (3.5 - i * 0.9) + LEFT * (0.3 if i % 2 else -0.3))
            pills.add(p)

        # Blood level bar (stays tiny)
        bar_bg = Rectangle(width=1.2, height=6, fill_color=SURFACE, fill_opacity=0.5,
                           stroke_color=MUTED, stroke_width=1)
        bar_bg.move_to(RIGHT * 3 + DOWN * 0.5)
        bar_fill = Rectangle(width=0.8, height=0.6, fill_color=DRUG_BLUE, fill_opacity=0.6,
                             stroke_width=0)
        bar_fill.align_to(bar_bg, DOWN).shift(UP * 0.2)
        bar_label = safe_text("BLOOD", font="Inter", font_size=18, color=MUTED)
        bar_label.next_to(bar_bg, DOWN, buff=0.2)

        # "STILL LOW" flash
        still_low = safe_text("STILL LOW", font="Bebas Neue", font_size=60, color=DANGER_RED)
        still_low.move_to(DOWN * 4.5)

        footer = safe_text("brute force doesn't work", font="Inter", font_size=18, color=MUTED)
        footer.move_to(DOWN * 6.0)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(bar_bg), FadeIn(bar_fill), FadeIn(bar_label),
                  run_time=0.4)                                            # t=0.7

        # Pills drop in one by one
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.5) for p in pills],
                              lag_ratio=0.12), run_time=1.5)              # t=2.2

        # Bar barely moves
        self.play(bar_fill.animate.stretch_to_fit_height(0.9).align_to(bar_bg, DOWN).shift(UP * 0.2),
                  run_time=0.8)                                            # t=3.0

        # More pills pile but bar stays low
        self.wait(0.8); t += 0.8
        self.play(FadeIn(still_low, scale=1.1), run_time=0.4); t += 0.4
        self.play(Flash(still_low.get_center(), color=DANGER_RED,
                        line_length=0.3, num_lines=6, run_time=0.3))      # t=4.5
        self.play(FadeIn(footer), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 7.0)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 3: THE CONTRADICTION (12.0–19.0s)
# Neutrophil absorbs drug → glows → enters lung → "64-98x"
# ================================================================
class Scene3_TrojanHorse(Scene):
    DURATION = 8.8
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill_label = label_pill("WAIT...", color=CELL_CYAN)
        pill_label.move_to(UP * 6.2)

        # Bloodstream ribbon
        stream = Rectangle(width=8, height=0.8, fill_color=DANGER_RED, fill_opacity=0.06,
                           stroke_color=DIM, stroke_width=1)
        stream.move_to(UP * 3)

        # Drug dots floating in stream
        drug_dots = VGroup()
        for x in np.linspace(-3, 3, 8):
            d = Dot(radius=0.08, color=DRUG_BLUE).move_to(UP * 3 + RIGHT * x)
            drug_dots.add(d)

        # Neutrophil enters from left
        cell = neutrophil_cell(radius=0.8, color=CELL_CYAN)
        cell.move_to(LEFT * 5 + UP * 3)

        # Lung at bottom
        lungs = lung_outline(height=5, color=LUNG_PINK)
        lungs.move_to(DOWN * 2.5)

        # Big number
        multiplier = safe_text("64-98x", font="Bebas Neue", font_size=120, color=CELL_CYAN)
        multiplier.move_to(DOWN * 0.5)

        footer = safe_text("tissue vs. blood concentration", font="Inter", font_size=18, color=MUTED)
        footer.move_to(DOWN * 6.0)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(stream), run_time=0.3); t += 0.3
        self.play(LaggedStart(*[FadeIn(d, scale=2) for d in drug_dots],
                              lag_ratio=0.05), run_time=0.4)              # t=1.0

        # Neutrophil drifts in
        self.play(cell.animate.move_to(UP * 3), run_time=1.0); t += 1.0

        # Cell absorbs drug dots — they fly into it
        self.play(
            *[d.animate.move_to(cell.get_center()).set_opacity(0) for d in drug_dots],
            cell[0].animate.set_fill(opacity=0.5),
            run_time=0.8,
        )                                                                   # t=2.8

        # Cell glows brighter (now loaded with drug)
        self.play(cell.animate.set_color(DRUG_BLUE).scale(1.15), run_time=0.4); t += 0.4

        # Lungs appear
        self.play(FadeIn(lungs), run_time=0.5); t += 0.5

        # Cell moves into lung
        self.play(cell.animate.move_to(DOWN * 2.5).scale(0.6), run_time=1.0); t += 1.0

        # Cell bursts — expanding ring
        burst = Circle(radius=0.3, stroke_color=DRUG_BLUE, stroke_width=3,
                       fill_opacity=0).move_to(cell.get_center())
        self.play(FadeOut(cell), GrowFromCenter(burst), run_time=0.3); t += 0.3
        self.play(burst.animate.scale(4).set_opacity(0), run_time=0.5); t += 0.5

        # 64-98x appears
        self.play(FadeIn(multiplier, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(multiplier.get_center(), color=CELL_CYAN,
                        line_length=0.4, num_lines=8, run_time=0.3))      # t=6.3
        self.play(FadeIn(footer), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 8.8)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 4: THE PROOF (19.0–27.0s)
# Stream of neutrophils into lung → bacteria dissolve → bar chart
# ================================================================
class Scene4_Proof(Scene):
    DURATION = 10.1
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill_label = label_pill("THE PROOF", color=GOLD)
        pill_label.move_to(UP * 6.2)

        # Lung at upper area
        lungs = lung_outline(height=4.5, color=LUNG_PINK)
        lungs.move_to(UP * 2)

        # Bacteria inside lung
        bacteria = VGroup()
        positions = [UP*2.5+LEFT*0.8, UP*1.5+RIGHT*0.6, UP*2+RIGHT*0.2,
                     UP*2.8+LEFT*0.2, UP*1.8+LEFT*0.4, UP*2.3+RIGHT*0.5]
        for pos in positions:
            b = bacteria_dot(0.15, BACTERIA_GREEN)
            b.move_to(pos)
            bacteria.add(b)

        # Neutrophil convoy
        cells = VGroup()
        for i in range(4):
            c = neutrophil_cell(radius=0.4, color=DRUG_BLUE)
            c.move_to(LEFT * 4 + RIGHT * i * 0.3 + DOWN * 0.5)
            cells.add(c)

        # Bar chart at ZONE_LOWER
        chart_base_y = -5.5
        blood_bar = Rectangle(width=1.5, height=0.4, fill_color=DANGER_RED, fill_opacity=0.6,
                              stroke_width=0)
        blood_bar.move_to(LEFT * 2 + UP * (chart_base_y + 0.2))
        blood_label = safe_text("BLOOD: 1x", font="Inter", font_size=20, color=MUTED)
        blood_label.next_to(blood_bar, UP, buff=0.15)

        lung_bar = Rectangle(width=1.5, height=4.0, fill_color=CELL_CYAN, fill_opacity=0.7,
                             stroke_width=0)
        lung_bar.align_to(blood_bar, DOWN)
        lung_bar.move_to(RIGHT * 2 + UP * (chart_base_y + 2.0))
        lung_label = safe_text("LUNG: 98x", font="Inter", font_size=20, color=CELL_CYAN)
        lung_label.next_to(lung_bar, UP, buff=0.15)

        footer = safe_text("Trojan horse delivery", font="Inter", font_size=18, color=MUTED)
        footer.move_to(DOWN * 6.0)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(lungs), run_time=0.4); t += 0.4
        self.play(LaggedStart(*[FadeIn(b, scale=2) for b in bacteria],
                              lag_ratio=0.08), run_time=0.5)              # t=1.2

        # Neutrophil convoy enters
        self.play(LaggedStart(*[c.animate.move_to(UP * 2 + LEFT * (0.5 - i * 0.6))
                  for i, c in enumerate(cells)], lag_ratio=0.15),
                  run_time=1.2)                                            # t=2.4

        # Bacteria dissolve as cells arrive
        self.play(
            *[b.animate.set_opacity(0).scale(0.3) for b in bacteria],
            run_time=0.8,
        )                                                                   # t=3.2

        # Expanding rings from each cell (drug release)
        rings = VGroup()
        for c in cells:
            r = Circle(radius=0.2, stroke_color=DRUG_BLUE, stroke_width=2,
                       fill_opacity=0).move_to(c.get_center())
            rings.add(r)
        self.play(*[GrowFromCenter(r) for r in rings], run_time=0.3); t += 0.3
        self.play(*[r.animate.scale(3).set_opacity(0) for r in rings],
                  run_time=0.5)                                            # t=4.0

        # Bar chart
        self.play(FadeIn(blood_bar), FadeIn(blood_label), run_time=0.3); t += 0.3
        self.play(FadeIn(lung_bar, shift=UP*0.3), FadeIn(lung_label),
                  run_time=0.5)                                            # t=4.8
        self.play(Flash(lung_bar.get_top(), color=CELL_CYAN,
                        line_length=0.3, num_lines=6, run_time=0.3))      # t=5.1
        self.play(FadeIn(footer), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 10.1)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 5: THE BETRAYAL (27.0–33.0s)
# Calendar days crossed off → pills stop → cells keep marching → "133 HOURS"
# ================================================================
class Scene5_StillWorking(Scene):
    DURATION = 7.6
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill_label = label_pill("THE TRUTH", color=GOLD)
        pill_label.move_to(UP * 6.2)

        # Calendar grid — 10 days
        cal = VGroup()
        day_labels = VGroup()
        for i in range(10):
            box = Square(side_length=0.7, fill_color=SURFACE, fill_opacity=0.5,
                         stroke_color=MUTED, stroke_width=1)
            box.move_to(LEFT * 3.15 + RIGHT * i * 0.7 + UP * 3.5)
            cal.add(box)
            dl = safe_text(str(i+1), font="Inter", font_size=16, color=WHITE_SOFT)
            dl.move_to(box)
            day_labels.add(dl)

        # X marks for days 1-5 (pills taken)
        x_marks = VGroup()
        for i in range(5):
            x = safe_text("X", font="Inter", font_size=24, color=DRUG_BLUE)
            x.move_to(cal[i].get_center())
            x_marks.add(x)

        # "PILLS STOP" label
        stop_label = safe_text("PILLS STOP", font="Bebas Neue", font_size=40, color=DANGER_RED)
        stop_label.move_to(UP * 2.2)
        stop_arrow = Arrow(stop_label.get_bottom(), cal[4].get_top() + DOWN*0.1,
                           color=DANGER_RED, stroke_width=2, max_tip_length_to_length_ratio=0.15)

        # Neutrophils still marching (days 6-10)
        marching_cells = VGroup()
        for i in range(5):
            c = neutrophil_cell(radius=0.35, color=DRUG_BLUE)
            c.move_to(LEFT * 3.15 + RIGHT * (i + 5) * 0.7 + UP * 1)
            c.set_opacity(0.9 - i * 0.1)
            marching_cells.add(c)

        # "133 HOURS" huge number
        hours = safe_text("133", font="Bebas Neue", font_size=160, color=CELL_CYAN)
        hours.move_to(DOWN * 1.5)
        hours_label = safe_text("HOURS", font="Inter", font_size=36, color=MUTED, weight="BOLD")
        hours_label.next_to(hours, DOWN, buff=0.2)
        sub = safe_text("lung tissue half-life", font="Inter", font_size=20, color=MUTED)
        sub.move_to(DOWN * 4)

        footer = safe_text("still delivering after the last pill", font="Inter",
                           font_size=18, color=MUTED)
        footer.move_to(DOWN * 6.0)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3
        self.play(LaggedStart(*[FadeIn(b) for b in cal],
                              lag_ratio=0.04), FadeIn(day_labels), run_time=0.5)  # t=0.8

        # X marks on days 1-5
        self.play(LaggedStart(*[FadeIn(x, scale=1.5) for x in x_marks],
                              lag_ratio=0.08), run_time=0.5)              # t=1.3

        # "Pills stop" after day 5
        self.play(FadeIn(stop_label), GrowArrow(stop_arrow), run_time=0.4); t += 0.4

        # But cells keep marching for days 6-10
        self.wait(0.5); t += 0.5
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in marching_cells],
                              lag_ratio=0.12), run_time=0.8)              # t=3.0

        # Highlight days 6-10 boxes in cyan
        self.play(*[cal[i+5].animate.set_stroke(color=CELL_CYAN, width=2) for i in range(5)],
                  run_time=0.4)                                            # t=3.4

        # 133 hours
        self.play(FadeIn(hours, scale=1.1), FadeIn(hours_label), run_time=0.5); t += 0.5
        self.play(Flash(hours.get_center(), color=CELL_CYAN,
                        line_length=0.5, num_lines=8, run_time=0.3))      # t=4.2
        self.play(FadeIn(sub), FadeIn(footer), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 7.6)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 6: THE PUNCH (33.0–40.0s)
# Neutrophil = delivery truck → final image
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 8.8
    def construct(self):
        self.add(gradient_bg("#0A0E18"), grid_lines(0.02))
        t = 0

        # Large neutrophil centered — the star of the show
        hero_cell = neutrophil_cell(radius=2.0, color=CELL_CYAN)
        hero_cell.move_to(UP * 0.5)

        # Drug particles glowing inside
        inner_dots = VGroup()
        for angle in range(0, 360, 40):
            d = Dot(radius=0.08, color=DRUG_BLUE)
            d.move_to(hero_cell.get_center() + np.array([
                np.cos(angle*PI/180)*0.8, np.sin(angle*PI/180)*0.8, 0]))
            inner_dots.add(d)

        # Label
        truck_label = safe_text("DELIVERY TRUCK", font="Bebas Neue", font_size=70, color=CELL_CYAN)
        truck_label.move_to(DOWN * 3.5)

        # Subtitle
        sub = safe_text("your immune system", font="DM Serif Display",
                        font_size=36, color=MUTED)
        sub.move_to(DOWN * 5)

        footer = safe_text("azithromycin's Trojan horse", font="Inter",
                           font_size=18, color=MUTED)
        footer.move_to(DOWN * 6.0)

        # ── Timing: 7.00s ──
        self.play(GrowFromCenter(hero_cell), run_time=1.0); t += 1.0

        # Drug dots pulse inside
        self.play(LaggedStart(*[FadeIn(d, scale=3) for d in inner_dots],
                              lag_ratio=0.06), run_time=0.6)              # t=1.6

        # Pulsing glow
        self.play(hero_cell.animate.scale(1.08), run_time=0.4); t += 0.4
        self.play(hero_cell.animate.scale(1/1.08), run_time=0.4); t += 0.4

        self.play(FadeIn(truck_label, shift=UP * 0.2), run_time=0.5); t += 0.5
        self.play(Flash(truck_label.get_center(), color=CELL_CYAN,
                        line_length=0.3, num_lines=8, run_time=0.3))      # t=3.2

        self.play(FadeIn(sub, shift=UP * 0.1), run_time=0.4); t += 0.4
        self.play(FadeIn(footer), run_time=0.3); t += 0.3

        # Hold
        target = getattr(self.__class__, 'DURATION', 8.8)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.0); t += 1.0


# ── Infra ─────────────────────────────────────────────────────
SCENES = [Scene1_Hook, Scene2_MorePills, Scene3_TrojanHorse,
          Scene4_Proof, Scene5_StillWorking, Scene6_Punch]

def render_single_scene(idx):
    config.output_file = f"azithromycin_trojan_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    SCENES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"azithromycin_trojan_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENES):
        n = f"azithromycin_trojan_scene_{i+1}"; print(f"  Preview {n}...")
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
    audio = od / "tts_azithromycin_trojan.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="azithromycin_trojan", audio_path=str(audio))
    final = od / "azithromycin_trojan_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")

    from render_utils import run_post_render_qa
    run_post_render_qa(str(final), scene_count=6)
