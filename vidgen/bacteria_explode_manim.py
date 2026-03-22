#!/usr/bin/env python3
"""Bacteria Literally Explode — 20 ATM of pressure vs. a sabotaged wall.

6 scenes, ~39.0s (36.0s audio + 3s hold).
Domain shapes: bacterium_rod, cell_wall_ring, pbp_wrench, beta_lactam_ring.

VTT cues (absolute → relative):
  Scene 1 (0.0–6.0s):   0.30 inside every... 2.50 twenty atmospheres... 4.80 microscopic
  Scene 2 (6.0–12.0s):  6.30 wall alive... 8.50 enzymes repairing... 10.80 never stop
  Scene 3 (12.0–18.0s): 12.40 most think... 14.60 poison... 16.40 chemical kills
  Scene 4 (18.0–25.5s): 18.40 penicillin... 20.80 fake block... 23.00 handcuffed... 24.80 growing
  Scene 5 (25.5–32.0s): 25.80 explodes... 27.60 ruptures... 29.80 twenty atmospheres
  Scene 6 (32.0–39.0s): 32.40 didn't kill... 34.60 pressure did... 37.00 removed the wall
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """Inside every bacterium, twenty atmospheres of pressure trying to rip it apart. Ten times a car tire. The cell wall holds it together. Enzymes called PBPs repair it every second. Penicillin isn't a poison. It's a fake building block that locks onto those enzymes. The wall stops being rebuilt. The bacterium keeps growing. Thinner and thinner until it ruptures. Twenty atmospheres released at once. The drug didn't kill it. The pressure did."""

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

# ── Color palette ────────────────────────────────────────────
BG = "#080A10"; GRID = "#1A2030"; SURFACE = "#15192A"
WHITE_SOFT = "#F0F0F0"; GOLD = "#FFD700"
WALL_AMBER = "#D97706"; ENZYME_GREEN = "#22C55E"; DRUG_BLUE = "#3B82F6"
DANGER_RED = "#EF4444"; PRESSURE_YELLOW = "#FACC15"; MUTED = "#475569"
DEAD_GRAY = "#4A5568"; DIM = "#334155"

# ── Safe zone & layout constants ─────────────────────────────
SAFE_W = 8.0
SAFE_TOP = 7.2
SAFE_BOT = -6.4

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

def bacterium_rod(height=3.0, color=WALL_AMBER, wall_visible=True):
    """Rod-shaped bacterium with visible cell wall ring."""
    inner = RoundedRectangle(width=height*0.4, height=height*0.8,
                             corner_radius=height*0.15,
                             fill_color="#1A1A2A", fill_opacity=0.6, stroke_width=0)
    wall = RoundedRectangle(width=height*0.5, height=height*0.9,
                            corner_radius=height*0.18,
                            fill_color=color, fill_opacity=0.2 if wall_visible else 0.05,
                            stroke_color=color, stroke_width=3 if wall_visible else 1)
    return VGroup(wall, inner)

def cell_wall_ring(radius=2.0, color=WALL_AMBER, thickness=0.15):
    """The cell wall as a visible ring around the bacterium."""
    outer = Circle(radius=radius, stroke_color=color, stroke_width=4,
                   fill_color=color, fill_opacity=0.1)
    inner = Circle(radius=radius - thickness, stroke_color=color, stroke_width=2,
                   fill_opacity=0)
    # Cross-links
    links = VGroup()
    for angle in range(0, 360, 30):
        r = radius - thickness / 2
        pt = np.array([np.cos(angle*PI/180)*r, np.sin(angle*PI/180)*r, 0])
        link = Dot(radius=0.04, color=color, fill_opacity=0.6).move_to(pt)
        links.add(link)
    return VGroup(outer, inner, links)

def pbp_wrench(height=0.6, color=ENZYME_GREEN):
    """PBP enzyme — small wrench shape (simplified)."""
    handle = Rectangle(width=height*0.2, height=height*0.6, fill_color=color,
                       fill_opacity=0.8, stroke_width=0)
    jaw = Polygon(
        np.array([-height*0.2, height*0.3, 0]),
        np.array([height*0.2, height*0.3, 0]),
        np.array([height*0.15, height*0.5, 0]),
        np.array([-height*0.15, height*0.5, 0]),
        fill_color=color, fill_opacity=0.8, stroke_width=0,
    )
    return VGroup(handle, jaw)

def beta_lactam_ring(size=0.4, color=DRUG_BLUE):
    """Beta-lactam ring — small square-ish ring (4-membered)."""
    ring = Square(side_length=size, stroke_color=color, stroke_width=3,
                  fill_color=color, fill_opacity=0.3)
    ring.rotate(45 * DEGREES)
    dot = Dot(radius=size*0.15, color=color).move_to(ring.get_center())
    return VGroup(ring, dot)


# ================================================================
# SCENE 1: THE HOOK (0.0–6.0s)
# Single bacterium + pressure arrows + "20 ATM"
# Zones: TITLE, UPPER/MID (hero bacterium), LOWER (20 ATM), FOOTER
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 5.7
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE — scene pill
        pill_label = label_pill("PRESSURE BOMB", color=DANGER_RED)
        pill_label.move_to(UP * ZONE_TITLE)

        # ZONE_MID — Large bacterium centered at hero position
        bact = bacterium_rod(height=5, color=WALL_AMBER)
        bact.move_to(UP * ZONE_MID)

        # Pressure arrows pushing outward from center
        arrows = VGroup()
        for angle in range(0, 360, 45):
            start = bact.get_center()
            direction = np.array([np.cos(angle*PI/180), np.sin(angle*PI/180), 0])
            end = start + direction * 1.2
            a = Arrow(start + direction * 0.2, end, color=PRESSURE_YELLOW,
                      stroke_width=2, max_tip_length_to_length_ratio=0.2)
            arrows.add(a)

        # ZONE_LOWER — "20 ATM" huge
        atm = safe_text("20 ATM", font="Bebas Neue", font_size=140, color=PRESSURE_YELLOW)
        atm.move_to(UP * ZONE_LOWER)

        sub = safe_text("10x a car tire", font="Inter", font_size=24, color=MUTED)
        sub.next_to(atm, DOWN, buff=0.3)

        # ZONE_FOOTER — source label
        footer = safe_text("turgor pressure", font="Inter", font_size=18, color=DIM)
        footer.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(bact, scale=0.9), run_time=0.6); t += 0.6

        # Pressure arrows pulse outward
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows],
                              lag_ratio=0.05), run_time=0.8)              # t=1.8

        # Arrows pulse
        self.play(*[a.animate.scale(1.1) for a in arrows], run_time=0.2); t += 0.2
        self.play(*[a.animate.scale(1/1.1) for a in arrows], run_time=0.2); t += 0.2

        # 20 ATM
        self.play(FadeIn(atm, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(atm.get_center(), color=PRESSURE_YELLOW,
                        line_length=0.4, num_lines=8, run_time=0.3))      # t=3.0
        self.play(FadeIn(sub), FadeIn(footer), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 5.7)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE WALL (6.0–12.0s)
# Cell wall ring + PBP wrenches constantly repairing
# Zones: TITLE, MID (wall ring), LOWER (labels), FOOTER
# ================================================================
class Scene2_TheWall(Scene):
    DURATION = 7.6
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE — scene pill
        pill_label = label_pill("THE WALL", color=WALL_AMBER)
        pill_label.move_to(UP * ZONE_TITLE)

        # ZONE_MID — Cell wall ring centered at hero position
        wall = cell_wall_ring(radius=2.5, color=WALL_AMBER)
        wall.move_to(UP * ZONE_MID)

        # PBP wrenches at repair points around the ring
        wrenches = VGroup()
        wrench_angles = [0, 72, 144, 216, 288]
        for angle in wrench_angles:
            w = pbp_wrench(height=0.5, color=ENZYME_GREEN)
            r = 2.7
            pos = np.array([np.cos(angle*PI/180)*r, np.sin(angle*PI/180)*r, 0])
            w.move_to(wall.get_center() + pos)
            w.rotate(angle * DEGREES + 90 * DEGREES)
            wrenches.add(w)

        # ZONE_LOWER — wall label and enzyme indicator
        wall_label = safe_text("PEPTIDOGLYCAN", font="Bebas Neue", font_size=48, color=WALL_AMBER)
        wall_label.move_to(UP * ZONE_LOWER)

        # Enzyme count indicator below wall label
        enzyme_row = VGroup()
        for i in range(5):
            ew = pbp_wrench(height=0.35, color=ENZYME_GREEN)
            enzyme_row.add(ew)
        enzyme_row.arrange(RIGHT, buff=0.6)
        enzyme_row.move_to(UP * (ZONE_LOWER - 1.2))

        pbp_label = safe_text("PBP ENZYMES", font="Inter", font_size=20, color=ENZYME_GREEN)
        pbp_label.next_to(enzyme_row, DOWN, buff=0.2)

        # ZONE_FOOTER — source label
        footer = safe_text("peptidoglycan synthesis", font="Inter", font_size=18, color=DIM)
        footer.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(wall), run_time=0.5); t += 0.5

        # Wall pulses (strong)
        self.play(wall[0].animate.set_stroke(width=6), run_time=0.3); t += 0.3
        self.play(wall[0].animate.set_stroke(width=4), run_time=0.3); t += 0.3

        # Wrenches appear — the repair crew
        self.play(LaggedStart(*[FadeIn(w, scale=1.5) for w in wrenches],
                              lag_ratio=0.1), run_time=0.6)               # t=2.0

        # Wrenches bob (working)
        self.play(*[w.animate.shift(UP * 0.08) for w in wrenches], run_time=0.2); t += 0.2
        self.play(*[w.animate.shift(DOWN * 0.08) for w in wrenches], run_time=0.2); t += 0.2
        self.play(*[w.animate.shift(UP * 0.06) for w in wrenches], run_time=0.15); t += 0.15
        self.play(*[w.animate.shift(DOWN * 0.06) for w in wrenches], run_time=0.15); t += 0.15

        self.play(FadeIn(wall_label), run_time=0.3); t += 0.3
        self.play(LaggedStart(*[FadeIn(e, scale=1.3) for e in enzyme_row],
                              lag_ratio=0.08), run_time=0.4)              # t=3.4
        self.play(FadeIn(pbp_label), FadeIn(footer), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 7.6)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: THE WRONG ANSWER (12.0–18.0s)
# Poison idea → bacterium melts → "WRONG" stamp
# Zones: TITLE, UPPER (poison cloud), MID (bacterium), LOWER (WRONG), FOOTER
# ================================================================
class Scene3_WrongAnswer(Scene):
    DURATION = 9.4
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE — scene pill
        pill_label = label_pill("WHAT YOU THINK", color=DANGER_RED)
        pill_label.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER — Poison cloud
        poison = Circle(radius=0.8, fill_color=DANGER_RED, fill_opacity=0.3,
                        stroke_color=DANGER_RED, stroke_width=2)
        poison.move_to(LEFT * 2 + UP * ZONE_UPPER)
        skull_x = safe_text("X", font="Bebas Neue", font_size=50, color=DANGER_RED)
        skull_x.move_to(poison)
        poison_grp = VGroup(poison, skull_x)

        # ZONE_MID — Bacterium as hero
        bact = bacterium_rod(height=3.5, color=WALL_AMBER)
        bact.move_to(RIGHT * 0.5 + UP * ZONE_MID)

        # Arrow from poison to bacterium
        poison_arrow = Arrow(poison.get_right(), bact.get_left(), color=DANGER_RED,
                             stroke_width=3, max_tip_length_to_length_ratio=0.12)

        # ZONE_LOWER — "WRONG" stamp
        wrong = safe_text("WRONG", font="Bebas Neue", font_size=100, color=DANGER_RED)
        wrong.move_to(UP * ZONE_LOWER)

        # X marks across the wrong idea — visual rejection
        cross1 = Line(LEFT * 3 + UP * (ZONE_LOWER + 1), RIGHT * 3 + UP * (ZONE_LOWER - 1),
                      color=DANGER_RED, stroke_width=4, stroke_opacity=0.4)
        cross2 = Line(LEFT * 3 + UP * (ZONE_LOWER - 1), RIGHT * 3 + UP * (ZONE_LOWER + 1),
                      color=DANGER_RED, stroke_width=4, stroke_opacity=0.4)

        # ZONE_FOOTER — source label
        footer = safe_text("common misconception", font="Inter", font_size=18, color=DIM)
        footer.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(bact), run_time=0.4); t += 0.4
        self.play(FadeIn(poison_grp), run_time=0.3); t += 0.3
        self.play(GrowArrow(poison_arrow), run_time=0.4); t += 0.4

        # Bacterium "melts" (wrong version)
        self.play(bact.animate.set_opacity(0.3).scale(0.7), run_time=0.8); t += 0.8

        self.wait(0.8); t += 0.8

        # "WRONG" stamp
        self.play(FadeIn(wrong, scale=2), run_time=0.3); t += 0.3
        self.play(Flash(wrong.get_center(), color=DANGER_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))      # t=3.6
        self.play(Create(cross1), Create(cross2), run_time=0.3); t += 0.3
        self.play(FadeIn(footer), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 9.4)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE CONTRADICTION (18.0–25.5s)
# Penicillin locks PBP wrenches → wall stops being repaired → grows thin
# Zones: TITLE, MID (wall + wrenches), LOWER (HANDCUFFED), FOOTER
# ================================================================
class Scene4_Sabotage(Scene):
    DURATION = 2.8
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE — scene pill
        pill_label = label_pill("NOT POISON", color=DRUG_BLUE)
        pill_label.move_to(UP * ZONE_TITLE)

        # ZONE_MID — Cell wall ring with wrenches, hero at center
        wall = cell_wall_ring(radius=2.0, color=WALL_AMBER)
        wall.move_to(UP * 0.5)

        wrenches = VGroup()
        wrench_positions = []
        for angle in [0, 90, 180, 270]:
            w = pbp_wrench(height=0.5, color=ENZYME_GREEN)
            r = 2.3
            pos = np.array([np.cos(angle*PI/180)*r, np.sin(angle*PI/180)*r, 0])
            w.move_to(wall.get_center() + pos)
            wrenches.add(w)
            wrench_positions.append(wall.get_center() + pos)

        # Beta-lactam rings (the saboteurs) — start off-screen left
        drugs = VGroup()
        for i in range(4):
            d = beta_lactam_ring(size=0.35, color=DRUG_BLUE)
            d.move_to(LEFT * 5 + UP * (2.5 - i * 1.5))
            drugs.add(d)

        # ZONE_LOWER — "HANDCUFFED" label
        handcuffed = safe_text("HANDCUFFED", font="Bebas Neue", font_size=60, color=DRUG_BLUE)
        handcuffed.move_to(UP * ZONE_LOWER)

        # Wall thinning visual — dashed arc showing weakness
        thin_arcs = VGroup()
        for start_angle in [0, 90, 180, 270]:
            arc = Arc(radius=2.2, start_angle=start_angle * DEGREES,
                      angle=30 * DEGREES, color=DANGER_RED,
                      stroke_width=2, stroke_opacity=0.5)
            arc.move_to(wall.get_center())
            thin_arcs.add(arc)

        # ZONE_FOOTER — source label
        footer = safe_text("beta-lactam mechanism", font="Inter", font_size=18, color=DIM)
        footer.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(wall), run_time=0.4); t += 0.4
        self.play(LaggedStart(*[FadeIn(w, scale=1.5) for w in wrenches],
                              lag_ratio=0.08), run_time=0.4)              # t=1.1

        # Beta-lactams fly in and lock onto wrenches one by one
        for i, (d, w) in enumerate(zip(drugs, wrenches)):
            self.play(d.animate.move_to(w.get_center()), run_time=0.35); t += 0.35
            self.play(w.animate.set_color(DRUG_BLUE).set_opacity(0.4),
                      run_time=0.15)                                       # each pair ~0.5s
        # t = 1.1 + 4 * 0.5 = 3.1

        self.play(FadeIn(handcuffed, scale=1.1), run_time=0.4); t += 0.4

        # Wall thins
        self.play(wall[0].animate.set_stroke(width=1.5).set_fill(opacity=0.03),
                  wall[1].animate.set_stroke(width=0.5),
                  run_time=0.8)                                            # t=4.3

        # Bacterium (wall) expands slightly — still growing
        self.play(wall.animate.scale(1.15), run_time=0.5); t += 0.5
        self.play(FadeIn(VGroup(*thin_arcs)), FadeIn(footer), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 2.8)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE PROOF (25.5–32.0s)
# Bacterium BURSTS → chain of explosions → pressure comparison
# Zones: TITLE, UPPER (bacterium), MID (explosion), LOWER (bars), FOOTER
# ================================================================
class Scene5_Burst(Scene):
    DURATION = 2.5
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE — scene pill
        pill_label = label_pill("THE PROOF", color=GOLD)
        pill_label.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER — Bacterium with paper-thin wall
        bact = bacterium_rod(height=3.5, color=WALL_AMBER)
        bact[0].set_stroke(width=1).set_fill(opacity=0.05)  # wall nearly gone
        bact.move_to(UP * ZONE_UPPER)

        # Pressure arrows intensifying
        arrows = VGroup()
        for angle in range(0, 360, 45):
            direction = np.array([np.cos(angle*PI/180), np.sin(angle*PI/180), 0])
            a = Arrow(bact.get_center() + direction * 0.3,
                      bact.get_center() + direction * 1.0,
                      color=PRESSURE_YELLOW, stroke_width=3,
                      max_tip_length_to_length_ratio=0.2)
            arrows.add(a)

        # Explosion fragments
        frag_offsets = [(-1.5, 1), (1.2, 0.8), (-0.8, -1.2), (1.5, -0.6),
                        (0, 1.5), (-1, -0.5), (0.5, -1.3)]
        frags = VGroup()
        for dx, dy in frag_offsets:
            f = Rectangle(width=0.3, height=0.15, fill_color=WALL_AMBER,
                          fill_opacity=0.5, stroke_width=0)
            f.rotate(np.random.uniform(0, 360) * DEGREES)
            f.move_to(bact.get_center())
            frags.add(f)

        # ZONE_LOWER — Pressure comparison bars
        bar_y = -5.5
        tire_bar = Rectangle(width=1.5, height=0.5, fill_color=MUTED, fill_opacity=0.5,
                             stroke_width=0)
        tire_bar.move_to(LEFT * 2 + UP * (bar_y + 0.25))
        tire_lbl = safe_text("CAR TIRE", font="Inter", font_size=16, color=MUTED)
        tire_lbl.next_to(tire_bar, DOWN, buff=0.1)
        tire_val = safe_text("2 ATM", font="Bebas Neue", font_size=28, color=MUTED)
        tire_val.next_to(tire_bar, UP, buff=0.1)

        bact_bar = Rectangle(width=1.5, height=3.5, fill_color=PRESSURE_YELLOW, fill_opacity=0.6,
                             stroke_width=0)
        bact_bar.move_to(RIGHT * 2 + UP * (bar_y + 1.75))
        bact_lbl = safe_text("BACTERIUM", font="Inter", font_size=16, color=PRESSURE_YELLOW)
        bact_lbl.next_to(bact_bar, DOWN, buff=0.1)
        bact_val = safe_text("20 ATM", font="Bebas Neue", font_size=28, color=PRESSURE_YELLOW)
        bact_val.next_to(bact_bar, UP, buff=0.1)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(bact), run_time=0.4); t += 0.4

        # Pressure arrows intensify
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows],
                              lag_ratio=0.05), run_time=0.5)              # t=1.2

        # Wall bulges
        self.play(bact.animate.scale(1.2), run_time=0.5); t += 0.5
        self.play(bact.animate.scale(1.1), run_time=0.3); t += 0.3

        # BURST!
        self.play(
            FadeOut(bact), FadeOut(arrows),
            *[f.animate.shift(np.array([dx, dy, 0]) * 2.5)
              for f, (dx, dy) in zip(frags, frag_offsets)],
            Flash(bact.get_center(), color=PRESSURE_YELLOW,
                  line_length=0.6, num_lines=12, run_time=0.3),
            run_time=0.4,
        )                                                                   # t=2.4

        # Fragments fade
        self.play(*[f.animate.set_opacity(0.1) for f in frags], run_time=0.5); t += 0.5

        # Comparison bars
        self.play(FadeIn(tire_bar), FadeIn(tire_lbl), FadeIn(tire_val),
                  run_time=0.4)                                            # t=3.3
        self.play(FadeIn(bact_bar, shift=UP * 0.3), FadeIn(bact_lbl),
                  FadeIn(bact_val), run_time=0.5)                        # t=3.8
        self.play(Flash(bact_val.get_center(), color=PRESSURE_YELLOW,
                        line_length=0.3, num_lines=6, run_time=0.3))      # t=4.1
        target = getattr(self.__class__, 'DURATION', 2.5)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE PUNCH (32.0–39.0s)
# Drug = saboteur, pressure = executioner
# Zones: TITLE (implicit in pill), UPPER (divider/labels), MID (drug vs pressure),
#        LOWER (20 ATM), FOOTER
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 27.3
    def construct(self):
        self.add(gradient_bg("#0A0E18"), grid_lines(0.02))
        t = 0

        # Divider line — visual split
        divider = DashedLine(UP * 5, DOWN * 1.5, color=MUTED, stroke_width=1, dash_length=0.2)

        # ZONE_UPPER — left: drug shape, right: pressure arrows
        # Beta-lactam ring (large, the saboteur)
        drug = beta_lactam_ring(size=1.2, color=DRUG_BLUE)
        drug.move_to(LEFT * 2 + UP * ZONE_UPPER)

        drug_label = safe_text("SABOTEUR", font="Bebas Neue", font_size=50, color=DRUG_BLUE)
        drug_label.next_to(drug, DOWN, buff=0.5)

        # Pressure arrows (large, the executioner)
        pressure_grp = VGroup()
        center = RIGHT * 2 + UP * ZONE_UPPER
        for angle in range(0, 360, 60):
            direction = np.array([np.cos(angle*PI/180), np.sin(angle*PI/180), 0])
            a = Arrow(center, center + direction * 1.0, color=PRESSURE_YELLOW,
                      stroke_width=4, max_tip_length_to_length_ratio=0.2)
            pressure_grp.add(a)

        press_label = safe_text("EXECUTIONER", font="Bebas Neue", font_size=50,
                                color=PRESSURE_YELLOW)
        press_label.next_to(pressure_grp, DOWN, buff=0.5)

        # ZONE_LOWER — Final "20 ATM" reveal
        final = safe_text("20 ATM", font="Bebas Neue", font_size=120, color=PRESSURE_YELLOW)
        final.move_to(UP * ZONE_LOWER)

        # Arrow from drug → pressure showing causality
        cause_arrow = Arrow(LEFT * 0.5 + UP * (ZONE_LOWER + 1.5),
                            RIGHT * 0.5 + UP * (ZONE_LOWER + 1.5),
                            color=MUTED, stroke_width=2)

        # ZONE_FOOTER
        sub = safe_text("pressure did the killing", font="Inter",
                        font_size=22, color=DIM)
        sub.move_to(UP * ZONE_FOOTER)

        # ── Timing: 7.00s ──
        self.play(Create(divider), run_time=0.3); t += 0.3
        self.play(GrowFromCenter(drug), run_time=0.5); t += 0.5
        self.play(FadeIn(drug_label, shift=UP * 0.1), run_time=0.3); t += 0.3

        self.play(LaggedStart(*[GrowArrow(a) for a in pressure_grp],
                              lag_ratio=0.06), run_time=0.5)              # t=1.6
        self.play(FadeIn(press_label, shift=UP * 0.1), run_time=0.3); t += 0.3

        # Pause
        self.wait(1.1); t += 1.1
        self.play(FadeIn(final, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(final.get_center(), color=PRESSURE_YELLOW,
                        line_length=0.5, num_lines=8, run_time=0.3))      # t=3.8
        self.play(FadeIn(sub, shift=UP * 0.05), run_time=0.4); t += 0.4

        # Hold
        target = getattr(self.__class__, 'DURATION', 27.3)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.0); t += 1.0

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ── Infra ─────────────────────────────────────────────────────
SCENES = [Scene1_Hook, Scene2_TheWall, Scene3_WrongAnswer,
          Scene4_Sabotage, Scene5_Burst, Scene6_Punch]

def render_single_scene(idx):
    config.output_file = f"bacteria_explode_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    SCENES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"bacteria_explode_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENES):
        n = f"bacteria_explode_scene_{i+1}"; print(f"  Preview {n}...")
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
    audio = od / "tts_bacteria_explode.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="bacteria_explode", audio_path=str(audio))
    final = od / "bacteria_explode_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")

    from render_utils import run_post_render_qa
    run_post_render_qa(str(final), scene_count=6)
