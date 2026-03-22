#!/usr/bin/env python3
"""Tunguska — The Explosion That Left Nothing Behind (Manim). Mystery/awe arc.

6 scenes, ~37.0s (34.0s audio + 3s hold).

VTT cues (absolute → relative):
  Scene 1 (0.0–5.5s = 5.50s):
    0.200 (0.20) June 30th, 1908.
    1.200 (1.20) The largest explosion in recorded history hit Siberia.
    3.200 (3.20) No crater. No meteorite.
    4.500 (4.50) No explanation for 19 years.
  Scene 2 (5.5–10.5s = 5.00s):
    5.700 (0.20) Locals thought a god was punishing them.
    7.200 (1.70) Scientists guessed a volcano. Then a comet.
    9.000 (3.50) Every theory fell apart.
  Scene 3 (10.5–16.5s = 6.00s):
    10.700 (0.20) 80 million trees flattened in a radial pattern.
    12.500 (2.00) 2,150 square kilometers destroyed.
    14.000 (3.50) The shockwave registered in London.
    15.200 (4.70) Night skies across Europe glowed white for weeks.
  Scene 4 (16.5–21.5s = 5.00s):
    16.700 (0.20) But there was no crater.
    17.800 (1.30) No meteorite fragments.
    19.000 (2.50) If something that powerful hit the ground,
    19.800 (3.30) there should be a hole.
    20.500 (4.00) There wasn't.
  Scene 5 (21.5–27.5s = 6.00s):
    21.700 (0.20) It was an airburst.
    22.800 (1.30) A rock 50 to 80 meters wide
    23.800 (2.30) exploded 5 to 10 kilometers above the surface.
    25.200 (3.70) It vaporized before impact.
    26.200 (4.70) The ground was hit by pure energy.
  Scene 6 (27.5–37.0s = 9.50s):
    27.700 (0.20) A rock the size of a building
    29.000 (1.50) destroyed an area the size of a major city.
    31.000 (3.50) And it left absolutely nothing behind.
    + 3s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """June 30th, 1908. Largest explosion in recorded history hit Siberia. No crater. No meteorite. 80 million trees flattened. The shockwave registered in London. Night skies glowed for weeks. But there was no hole. No fragments. Something that powerful should leave a crater. It was an airburst. A rock 50 meters wide exploded kilometers above the surface. Vaporized before impact. An area the size of a city, destroyed by pure energy. Nothing left behind."""

from manim import (
    Scene, Text, Group, VGroup, Rectangle, RoundedRectangle, Circle,
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
config.background_color = "#0A0A10"
config.disable_caching = True

# ── Color Palette ────────────────────────────────────────────
BG = "#0A0A10"
SURFACE = "#12121C"
SURFACE2 = "#1A1A26"
BORDER = "#2A2A3A"
GRID = "#14141C"
EXPLOSION_WHITE = "#FFFFF0"
FOREST_GREEN = "#2D5A27"
BLAST_ORANGE = "#FF6B35"
SIBERIA_BLUE = "#3A5A7C"
ASH_GRAY = "#808080"
WHITE_SOFT = "#F0F0F0"
MUTED = "#7B8DA0"
DIM = "#404050"
DEAD_GRAY = "#4A5568"
GOLD = "#FFD700"

# ── Safe zone & layout constants ─────────────────────────────
SAFE_W = 8.0
SAFE_TOP = 7.2
SAFE_BOT = -6.4

ZONE_TITLE  = 6.2
ZONE_UPPER  = 3.5
ZONE_MID    = 0.0
ZONE_LOWER  = -3.5
ZONE_FOOTER = -6.0


# ── Core Helpers ─────────────────────────────────────────────

def gradient_bg(c=BG, g="#0A0A12"):
    bg = Rectangle(width=12, height=20, fill_color=c, fill_opacity=1, stroke_width=0)
    glow = Circle(radius=5, fill_color=g, fill_opacity=0.10, stroke_width=0).move_to(UP * 2)
    return VGroup(bg, glow)

def grid_lines(opacity=0.04):
    lines = VGroup()
    for i in range(13):
        y = -8 + i * 16 / 12
        lines.add(Line(LEFT * 5, RIGHT * 5, color=GRID, stroke_width=0.5).move_to(UP * y).set_opacity(opacity))
    for j in range(7):
        x = -4.5 + j * 9 / 6
        lines.add(Line(DOWN * 8, UP * 8, color=GRID, stroke_width=0.5).move_to(RIGHT * x).set_opacity(opacity))
    return lines

def safe_text(content, **kwargs):
    t = Text(content, **kwargs)
    if t.width > SAFE_W:
        t.scale(SAFE_W / t.width)
    return t

def label_pill(txt, color=BLAST_ORANGE, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W:
        t.scale(SAFE_W / t.width)
    p = RoundedRectangle(
        width=t.width + 0.5, height=t.height + 0.3,
        corner_radius=0.18, fill_color=bg, fill_opacity=0.95,
        stroke_color=color, stroke_width=1.5
    ).move_to(t)
    return VGroup(p, t)

def section_div(width=5, color=BLAST_ORANGE):
    l = Line(LEFT * width / 2, LEFT * 0.12, color=color, stroke_width=1.5)
    r = Line(RIGHT * 0.12, RIGHT * width / 2, color=color, stroke_width=1.5)
    d = Square(side_length=0.1, color=color, fill_color=color, fill_opacity=1).rotate(45 * DEGREES)
    return VGroup(l, d, r)


# ── Domain Shape Helpers (4 custom shapes) ───────────────────

def explosion_ring(radius=1.0, color=BLAST_ORANGE, n_rings=3):
    """Concentric expanding rings — blast wave visualization."""
    rings = VGroup()
    for i in range(n_rings):
        r = radius * (0.4 + i * 0.3)
        ring = Circle(radius=r, color=color, stroke_width=3 - i * 0.8, fill_opacity=0)
        ring.set_opacity(0.9 - i * 0.25)
        rings.add(ring)
    return rings

def tree_silhouette(color=FOREST_GREEN, h=1.0):
    """Simple pine tree — triangle crown on rectangle trunk."""
    sc = h / 1.0
    trunk = Rectangle(width=0.1 * sc, height=0.3 * sc, fill_color=ASH_GRAY,
                      fill_opacity=0.8, stroke_width=0)
    trunk.move_to(DOWN * 0.15 * sc)
    crown = Polygon(
        np.array([-0.25 * sc, 0, 0]),
        np.array([0.25 * sc, 0, 0]),
        np.array([0, 0.6 * sc, 0]),
        fill_color=color, fill_opacity=0.85, stroke_width=0
    )
    crown.move_to(UP * 0.25 * sc)
    return VGroup(trunk, crown)

def fallen_tree(color=ASH_GRAY, h=0.8):
    """Fallen tree — horizontal, pointing outward from blast center."""
    sc = h / 0.8
    trunk = Rectangle(width=0.6 * sc, height=0.08 * sc, fill_color=color,
                      fill_opacity=0.7, stroke_width=0)
    crown = Polygon(
        np.array([0.3 * sc, -0.15 * sc, 0]),
        np.array([0.3 * sc, 0.15 * sc, 0]),
        np.array([0.6 * sc, 0, 0]),
        fill_color=color, fill_opacity=0.5, stroke_width=0
    )
    return VGroup(trunk, crown)

def rock_fragment(color=ASH_GRAY, size=1.0):
    """Irregular polygon asteroid/rock shape."""
    sc = size
    pts = [
        np.array([-0.3 * sc, 0.4 * sc, 0]),
        np.array([0.2 * sc, 0.5 * sc, 0]),
        np.array([0.5 * sc, 0.2 * sc, 0]),
        np.array([0.4 * sc, -0.3 * sc, 0]),
        np.array([0.0 * sc, -0.5 * sc, 0]),
        np.array([-0.4 * sc, -0.2 * sc, 0]),
        np.array([-0.5 * sc, 0.1 * sc, 0]),
    ]
    return Polygon(*pts, fill_color=color, fill_opacity=0.8,
                   stroke_color=MUTED, stroke_width=1.2)


# ================================================================
# SCENE 1: THE HOOK (0.0–5.5s = 5.50s)
# Visual: Date "JUNE 30, 1908" — forest — explosion flash — "NO CRATER"
# Zones: TITLE(pill) UPPER(date) MID(forest+flash) LOWER(no crater) FOOTER(19 years)
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 5.5
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("TUNGUSKA", color=BLAST_ORANGE, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # Date — ZONE_UPPER
        date = safe_text("JUNE 30, 1908", font="Bebas Neue", font_size=120, color=EXPLOSION_WHITE)
        date.move_to(UP * ZONE_UPPER)

        # Siberia forest landscape — ZONE_MID
        sib_ground = Line(LEFT * 4.2, RIGHT * 4.2, color=FOREST_GREEN, stroke_width=2)
        sib_ground.move_to(DOWN * 0.5)
        sib_trees = VGroup()
        _xs = [-3.2, -2.4, -1.7, -1.0, -0.2, 0.6, 1.3, 2.2, 3.0]
        np.random.seed(77)
        for _x in _xs:
            _h = 0.55 + np.random.uniform(0, 0.25)
            _tr = tree_silhouette(FOREST_GREEN, h=_h)
            _tr.move_to(np.array([_x, -0.5 + _h * 0.38, 0]))
            sib_trees.add(_tr)
        sib_lbl = safe_text("TUNGUSKA · SIBERIA", font="Inter", font_size=20,
                            color=SIBERIA_BLUE, weight="BOLD")
        sib_lbl.move_to(UP * 0.8)

        # Explosion flash — ZONE_MID
        flash = Circle(radius=0.3, fill_color=EXPLOSION_WHITE, fill_opacity=1, stroke_width=0)
        flash.move_to(UP * ZONE_MID)
        flash_big = Circle(radius=4, fill_color=EXPLOSION_WHITE, fill_opacity=0, stroke_width=0)
        flash_big.move_to(UP * ZONE_MID)

        # Blast rings
        rings = explosion_ring(2.5, BLAST_ORANGE, n_rings=3)
        rings.move_to(UP * ZONE_MID)
        rings.set_opacity(0)

        div = section_div(5, MUTED).move_to(DOWN * 2)

        # Triple denial — ZONE_LOWER
        no_crater = safe_text("NO CRATER.", font="Bebas Neue", font_size=70, color=SIBERIA_BLUE)
        no_crater.move_to(DOWN * 3)
        no_met = safe_text("NO METEORITE.", font="Bebas Neue", font_size=70, color=SIBERIA_BLUE)
        no_met.move_to(DOWN * 4.2)

        # ZONE_FOOTER
        no_exp = safe_text("19 YEARS. NO EXPLANATION.", font="Inter",
                           font_size=26, color=DEAD_GRAY, weight="BOLD")
        no_exp.move_to(DOWN * abs(ZONE_FOOTER))

        # ── Timing: 5.50s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.20: "June 30th, 1908."
        self.play(FadeIn(date, scale=1.2), run_time=0.5); t += 0.5

        # Show Siberia forest at ZONE_MID
        self.play(FadeIn(sib_ground), FadeIn(sib_lbl), run_time=0.2); t += 0.2
        self.play(LaggedStart(*[FadeIn(t, scale=0.8) for t in sib_trees],
                              lag_ratio=0.04), run_time=0.3)                # t=1.3

        # VTT 1.20: "The largest explosion in recorded history."
        self.play(FadeIn(flash, scale=0.5), run_time=0.2); t += 0.2
        self.play(
            flash_big.animate.set_opacity(0.6),
            sib_trees.animate.set_opacity(0.12),
            *[r.animate.set_opacity(0.8).scale(1.5) for r in rings],
            run_time=0.5,
        )                                                                   # t=2.0
        self.play(
            flash_big.animate.set_opacity(0),
            *[r.animate.set_opacity(0.2) for r in rings],
            run_time=0.4,
        )                                                                   # t=2.4

        # VTT 3.20: "No crater. No meteorite."
        self.wait(0.5); t += 0.5
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(no_crater, shift=UP * 0.15), run_time=0.4); t += 0.4
        self.play(FadeIn(no_met, shift=UP * 0.15), run_time=0.4); t += 0.4

        # VTT 4.50: "No explanation for 19 years."
        self.wait(0.2); t += 0.2
        self.play(FadeIn(no_exp, shift=UP * 0.1), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 5.5)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE WRONG ANSWER (5.5–10.5s = 5.00s)
# Visual: Wrong guesses with domain shapes, then X'd out
# Zones: TITLE(pill) UPPER(god+volcano icons) MID(comet icon) LOWER(fell apart) FOOTER(label)
# ================================================================
class Scene2_WrongAnswer(Scene):
    DURATION = 5.0
    def construct(self):
        self.add(gradient_bg("#080808"), grid_lines(0.025))
        t = 0

        pill = label_pill("THE GUESSES", color=SIBERIA_BLUE, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # Wrong answer icons — volcano shape, lightning bolt, comet trail
        # God guess — lightning bolt shape at UPPER-LEFT
        bolt_pts = [
            np.array([0.0, 0.8, 0]), np.array([-0.2, 0.2, 0]),
            np.array([0.1, 0.25, 0]), np.array([-0.1, -0.4, 0]),
            np.array([0.3, 0.15, 0]), np.array([0.1, 0.2, 0]),
        ]
        bolt = Polygon(*bolt_pts, fill_color=SIBERIA_BLUE, fill_opacity=0.7,
                        stroke_color=SIBERIA_BLUE, stroke_width=1.5)
        bolt.scale(1.6).move_to(UP * ZONE_UPPER + LEFT * 2.5)
        god_lbl = safe_text("GOD?", font="Inter", font_size=22, color=SIBERIA_BLUE, weight="BOLD")
        god_lbl.next_to(bolt, DOWN, buff=0.3)
        god_group = VGroup(bolt, god_lbl)

        # Volcano guess — triangle mountain at UPPER-RIGHT
        volcano = Polygon(
            np.array([-1.0, -0.6, 0]), np.array([1.0, -0.6, 0]),
            np.array([0.15, 0.7, 0]), np.array([-0.15, 0.7, 0]),
            fill_color=BLAST_ORANGE, fill_opacity=0.5,
            stroke_color=BLAST_ORANGE, stroke_width=1.5
        )
        # Smoke puffs at top
        smoke1 = Circle(radius=0.2, fill_color=ASH_GRAY, fill_opacity=0.4, stroke_width=0)
        smoke1.move_to(UP * 0.9 + LEFT * 0.1)
        smoke2 = Circle(radius=0.15, fill_color=ASH_GRAY, fill_opacity=0.3, stroke_width=0)
        smoke2.move_to(UP * 1.15 + RIGHT * 0.1)
        volcano_grp = VGroup(volcano, smoke1, smoke2)
        volcano_grp.scale(1.1).move_to(UP * ZONE_UPPER + RIGHT * 2.5)
        volc_lbl = safe_text("VOLCANO?", font="Inter", font_size=22, color=BLAST_ORANGE, weight="BOLD")
        volc_lbl.next_to(volcano_grp, DOWN, buff=0.3)
        volc_group = VGroup(volcano_grp, volc_lbl)

        # Comet guess — rock with tail at ZONE_MID
        comet_rock = rock_fragment(SIBERIA_BLUE, size=0.7)
        comet_tail = VGroup()
        for i in range(5):
            streak = Line(
                RIGHT * 0.5 + UP * (0.15 - i * 0.07),
                RIGHT * (1.8 + i * 0.3) + UP * (0.15 - i * 0.07),
                color=SIBERIA_BLUE, stroke_width=2.5 - i * 0.4
            ).set_opacity(0.6 - i * 0.1)
            comet_tail.add(streak)
        comet = VGroup(comet_rock, comet_tail)
        comet.move_to(UP * ZONE_MID + LEFT * 0.5)
        comet_lbl = safe_text("COMET?", font="Inter", font_size=22, color=SIBERIA_BLUE, weight="BOLD")
        comet_lbl.next_to(comet, DOWN, buff=0.4)
        comet_group = VGroup(comet, comet_lbl)

        # Red X marks for each guess
        def make_x(center, size=0.7):
            x1 = Line(center + LEFT * size + UP * size, center + RIGHT * size + DOWN * size,
                       color=BLAST_ORANGE, stroke_width=5)
            x2 = Line(center + RIGHT * size + UP * size, center + LEFT * size + DOWN * size,
                       color=BLAST_ORANGE, stroke_width=5)
            return VGroup(x1, x2)

        god_x = make_x(bolt.get_center(), 0.7)
        volc_x = make_x(volcano_grp.get_center(), 0.7)
        comet_x = make_x(comet_rock.get_center(), 0.7)

        div = section_div(5, BLAST_ORANGE).move_to(DOWN * 2.5)

        fell = safe_text("EVERY THEORY", font="Bebas Neue", font_size=80, color=BLAST_ORANGE)
        fell.move_to(DOWN * ZONE_LOWER)
        fell2 = safe_text("FELL APART.", font="Bebas Neue", font_size=80, color=DEAD_GRAY)
        fell2.move_to(DOWN * 4.8)

        footer = safe_text("SIBERIA, 1908", font="Inter", font_size=22,
                           color=DEAD_GRAY, weight="BOLD")
        footer.move_to(DOWN * abs(ZONE_FOOTER))

        # ── Timing: 5.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.20: "Locals thought a god was punishing them."
        self.play(FadeIn(god_group, scale=0.9), run_time=0.4); t += 0.4

        # VTT 1.70: "Scientists guessed a volcano. Then a comet."
        self.wait(0.7); t += 0.7
        self.play(FadeIn(volc_group, scale=0.9), run_time=0.4); t += 0.4
        self.play(FadeIn(comet_group, scale=0.9), run_time=0.4); t += 0.4

        # VTT 3.50: "Every theory fell apart." — X out all
        self.wait(1.0); t += 1.0
        self.play(
            Create(god_x), Create(volc_x), Create(comet_x),
            god_group.animate.set_opacity(0.3),
            volc_group.animate.set_opacity(0.3),
            comet_group.animate.set_opacity(0.3),
            run_time=0.4,
        )                                                                   # t=3.6
        self.play(Create(div), run_time=0.2); t += 0.2
        self.play(FadeIn(fell, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(fell2, shift=UP * 0.1), run_time=0.3); t += 0.3
        self.play(FadeIn(footer), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 5.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: THE SCALE (10.5–16.5s = 6.00s)
# Visual: 80 MILLION + radial fallen trees + 2,150 km² + shockwave ripple
# Zones: TITLE(pill) UPPER(80 MILLION) MID(radial trees) LOWER(2150 km²) FOOTER(shockwave)
# ================================================================
class Scene3_Scale(Scene):
    DURATION = 6.0
    def construct(self):
        self.add(gradient_bg(g="#0A0F0A"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE SCALE", color=BLAST_ORANGE, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        eighty_mil = safe_text("80 MILLION", font="Bebas Neue", font_size=120, color=BLAST_ORANGE)
        eighty_mil.move_to(UP * ZONE_UPPER)
        trees_lbl = safe_text("TREES FLATTENED", font="Inter", font_size=28,
                              color=WHITE_SOFT, weight="BOLD")
        trees_lbl.move_to(UP * 1.8)

        # Radial fallen trees — ZONE_MID
        blast_center = Dot(ORIGIN, radius=0.15, color=BLAST_ORANGE, fill_opacity=0.9)
        fallen_trees = VGroup()
        np.random.seed(30)
        for i in range(24):
            angle = i * (2 * PI / 24) + np.random.uniform(-0.1, 0.1)
            dist = np.random.uniform(1.2, 3.0)
            ft = fallen_tree(ASH_GRAY, h=0.6)
            ft.rotate(angle)
            ft.move_to(np.array([np.cos(angle) * dist, np.sin(angle) * dist, 0]))
            fallen_trees.add(ft)

        blast_outline = Circle(radius=3.2, color=BLAST_ORANGE, stroke_width=1.5,
                               fill_opacity=0).set_opacity(0.4)

        # Shockwave pulse ring — animates outward
        shockwave_ring = Circle(radius=0.5, color=BLAST_ORANGE, stroke_width=2,
                                fill_opacity=0).set_opacity(0.6)

        div = section_div(5, BLAST_ORANGE).move_to(DOWN * 2.5)

        area = safe_text("2,150 KM²", font="Bebas Neue", font_size=100, color=EXPLOSION_WHITE)
        area.move_to(DOWN * ZONE_LOWER)

        shockwave = safe_text("SHOCKWAVE FELT IN LONDON", font="Inter",
                              font_size=24, color=MUTED, weight="BOLD")
        shockwave.move_to(DOWN * 5)
        skies = safe_text("SKIES GLOWED WHITE FOR WEEKS", font="Inter",
                          font_size=22, color=DEAD_GRAY, weight="BOLD")
        skies.move_to(DOWN * abs(ZONE_FOOTER))

        # ── Timing: 6.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.20: "80 million trees flattened in a radial pattern."
        self.play(FadeIn(eighty_mil, scale=1.15), run_time=0.5); t += 0.5
        self.play(Flash(eighty_mil.get_center(), color=BLAST_ORANGE,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=1.1
        self.play(FadeIn(trees_lbl, shift=UP * 0.1), run_time=0.3); t += 0.3

        # Trees fall radially from center
        self.play(FadeIn(blast_center), run_time=0.2); t += 0.2
        self.play(LaggedStart(*[FadeIn(t, scale=0.7) for t in fallen_trees],
                              lag_ratio=0.02), run_time=0.8)                # t=2.4
        self.play(FadeIn(blast_outline),
                  shockwave_ring.animate.scale(6).set_opacity(0),
                  run_time=0.5)                                             # t=2.9

        # VTT 2.00: "2,150 square kilometers destroyed."
        self.play(Create(div), run_time=0.2); t += 0.2
        self.play(FadeIn(area, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(area.get_center(), color=EXPLOSION_WHITE,
                        line_length=0.4, num_lines=8, run_time=0.3))        # t=3.9

        # VTT 3.50: "The shockwave registered in London."
        self.play(FadeIn(shockwave, shift=UP * 0.1), run_time=0.4); t += 0.4

        # Pulse the blast outline for visual motion
        self.play(blast_outline.animate.set_opacity(0.7).scale(1.05),
                  run_time=0.3)                                             # t=4.6

        # VTT 4.70: "Night skies glowed white for weeks."
        self.play(blast_outline.animate.set_opacity(0.3).scale(1 / 1.05),
                  FadeIn(skies, shift=UP * 0.1), run_time=0.4)             # t=5.0
        target = getattr(self.__class__, 'DURATION', 6.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE CONTRADICTION (16.5–21.5s = 5.00s)
# Visual: Crater outline with big X — "NO CRATER" + rock X'd out
# Zones: TITLE(pill) UPPER(NO CRATER) MID(crater X) LOWER(no fragments) FOOTER(label)
# ================================================================
class Scene4_Contradiction(Scene):
    DURATION = 5.0
    def construct(self):
        self.add(gradient_bg("#0A0808"), grid_lines(0.025))
        t = 0

        pill = label_pill("THE MYSTERY", color=SIBERIA_BLUE, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        no_cr = safe_text("NO CRATER.", font="Bebas Neue", font_size=100, color=SIBERIA_BLUE)
        no_cr.move_to(UP * ZONE_UPPER)

        # Crater outline at ZONE_MID — dashed circle + big X
        crater = Circle(radius=2.0, color=SIBERIA_BLUE, stroke_width=5, fill_opacity=0.06)
        crater.set_stroke(color=SIBERIA_BLUE, width=5, opacity=0.9)
        crater.move_to(UP * ZONE_MID)
        crater_dash = DashedLine(
            crater.get_left(), crater.get_right(),
            color=SIBERIA_BLUE, stroke_width=2, dash_length=0.15
        ).move_to(UP * ZONE_MID)

        # Question marks inside crater — pulsing
        qmarks = VGroup()
        for _pos in [LEFT * 0.8 + UP * 0.4, ORIGIN, RIGHT * 0.8 + UP * 0.4]:
            _q = safe_text("?", font="Bebas Neue", font_size=60, color=SIBERIA_BLUE)
            _q.set_opacity(0.55)
            _q.move_to(UP * ZONE_MID + _pos)
            qmarks.add(_q)

        crater_x1 = Line(LEFT * 1.8 + UP * 1.8, RIGHT * 1.8 + DOWN * 1.8,
                         color=BLAST_ORANGE, stroke_width=5)
        crater_x2 = Line(RIGHT * 1.8 + UP * 1.8, LEFT * 1.8 + DOWN * 1.8,
                         color=BLAST_ORANGE, stroke_width=5)
        crater_x = VGroup(crater_x1, crater_x2).move_to(UP * ZONE_MID)

        div = section_div(5, SIBERIA_BLUE).move_to(DOWN * 2.5)

        no_frag = safe_text("NO FRAGMENTS.", font="Bebas Neue", font_size=80, color=SIBERIA_BLUE)
        no_frag.move_to(DOWN * ZONE_LOWER)

        # Rock shape X'd out
        rock = rock_fragment(ASH_GRAY, size=1.0)
        rock.move_to(DOWN * 4.5)
        rock_x1 = Line(rock.get_corner(UL), rock.get_corner(DR),
                        color=BLAST_ORANGE, stroke_width=3)
        rock_x2 = Line(rock.get_corner(UR), rock.get_corner(DL),
                        color=BLAST_ORANGE, stroke_width=3)

        footer = safe_text("NO HOLE. NO EVIDENCE.", font="Inter",
                           font_size=22, color=DEAD_GRAY, weight="BOLD")
        footer.move_to(DOWN * abs(ZONE_FOOTER))

        # ── Timing: 5.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.20: "But there was no crater."
        self.play(FadeIn(no_cr, scale=1.08), run_time=0.5); t += 0.5
        self.play(FadeIn(crater), Create(crater_dash), FadeIn(qmarks), run_time=0.4); t += 0.4

        # Shake question marks then X out
        self.play(
            qmarks.animate.shift(RIGHT * 0.1),
            run_time=0.1,
        )                                                                   # t=1.3
        self.play(
            qmarks.animate.shift(LEFT * 0.2),
            run_time=0.1,
        )                                                                   # t=1.4
        self.play(
            qmarks.animate.shift(RIGHT * 0.1),
            Create(crater_x1), Create(crater_x2),
            run_time=0.3,
        )                                                                   # t=1.7

        # VTT 1.30: "No meteorite fragments."
        self.play(Create(div), run_time=0.2); t += 0.2
        self.play(FadeIn(no_frag, shift=UP * 0.15), run_time=0.4); t += 0.4
        self.play(GrowFromCenter(rock), run_time=0.3); t += 0.3
        self.play(Create(rock_x1), Create(rock_x2),
                  rock.animate.set_opacity(0.4), run_time=0.3)             # t=2.9

        # VTT 2.50-4.00: "Should be a hole. There wasn't."
        self.wait(0.2); t += 0.2
        self.play(FadeIn(footer, shift=UP * 0.1), run_time=0.4); t += 0.4

        # Pulse crater for unease
        self.play(crater.animate.set_stroke(opacity=0.4), run_time=0.4); t += 0.4
        self.play(crater.animate.set_stroke(opacity=0.9), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 5.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE PROOF (21.5–27.5s = 6.00s)
# Visual: Cross-section — rock exploding above ground line
# Zones: TITLE(pill) UPPER(AIRBURST) MID(cross-section diagram) LOWER(50-80 M) FOOTER(pure energy)
# ================================================================
class Scene5_Proof(Scene):
    DURATION = 6.0
    def construct(self):
        self.add(gradient_bg(g="#0A0808"), grid_lines(0.025))
        t = 0

        pill = label_pill("THE ANSWER", color=BLAST_ORANGE, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        airburst = safe_text("AIRBURST.", font="Bebas Neue", font_size=110, color=BLAST_ORANGE)
        airburst.move_to(UP * ZONE_UPPER)

        # Cross-section at ZONE_MID — ground line with forest
        ground = Line(LEFT * 4, RIGHT * 4, color=FOREST_GREEN, stroke_width=3)
        ground.move_to(DOWN * 0.5)
        ground_fill = Rectangle(width=8, height=2, fill_color=FOREST_GREEN,
                                fill_opacity=0.12, stroke_width=0)
        ground_fill.move_to(DOWN * 1.5)

        # Small trees on ground line
        ground_trees = VGroup()
        for gx in [-3, -2, -1, 0, 1, 2, 3]:
            gt = tree_silhouette(FOREST_GREEN, h=0.4)
            gt.move_to(np.array([gx, -0.25, 0]))
            ground_trees.add(gt)

        # Rock above ground
        rock = rock_fragment(ASH_GRAY, size=0.8)
        rock.move_to(UP * 2)

        # Height label
        height_line = DashedLine(UP * 2, DOWN * 0.5, color=MUTED, stroke_width=1,
                                 dash_length=0.15)
        height_lbl = safe_text("5-10 KM", font="Inter", font_size=22,
                               color=MUTED, weight="BOLD")
        height_lbl.move_to(RIGHT * 2 + UP * 0.8)

        # Blast rings — replace rock on explosion
        blast = explosion_ring(2.0, BLAST_ORANGE, n_rings=3)
        blast.move_to(UP * 2)
        blast.set_opacity(0)

        # Energy arrows pointing down
        energy_arrows = VGroup()
        for x in [-1.5, -0.5, 0.5, 1.5]:
            a = Arrow(UP * 1.2 + RIGHT * x * 0.6, DOWN * 0.5 + RIGHT * x,
                      color=BLAST_ORANGE, stroke_width=2, buff=0.1)
            energy_arrows.add(a)

        div = section_div(5, BLAST_ORANGE).move_to(DOWN * 3)

        size_lbl = safe_text("50-80 METERS", font="Bebas Neue", font_size=70, color=EXPLOSION_WHITE)
        size_lbl.move_to(DOWN * 4)

        pure = safe_text("PURE ENERGY.", font="Bebas Neue", font_size=55, color=BLAST_ORANGE)
        pure.move_to(DOWN * 5.2)
        vaporized = safe_text("VAPORIZED BEFORE IMPACT", font="Inter",
                              font_size=22, color=DEAD_GRAY, weight="BOLD")
        vaporized.move_to(DOWN * abs(ZONE_FOOTER))

        # ── Timing: 6.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.20: "It was an airburst."
        self.play(FadeIn(airburst, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(airburst.get_center(), color=BLAST_ORANGE,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=1.1

        # VTT 1.30: "A rock 50 to 80 meters wide" — show cross-section
        self.play(FadeIn(ground), FadeIn(ground_fill),
                  LaggedStart(*[FadeIn(gt, scale=0.8) for gt in ground_trees],
                              lag_ratio=0.03),
                  run_time=0.3)                                             # t=1.4
        self.play(FadeIn(rock, scale=0.8), run_time=0.3); t += 0.3
        self.play(FadeIn(height_line), FadeIn(height_lbl), run_time=0.2); t += 0.2

        # VTT 2.30: "exploded 5 to 10 km above the surface."
        self.play(
            FadeOut(rock),
            blast.animate.set_opacity(0.8).scale(1.5),
            Flash(rock.get_center(), color=EXPLOSION_WHITE,
                  line_length=1.0, num_lines=15, run_time=0.4),
            ground_trees.animate.set_opacity(0.15),
            run_time=0.5,
        )                                                                   # t=2.4

        # VTT 3.70: "It vaporized before impact."
        self.play(LaggedStart(*[GrowArrow(a) for a in energy_arrows],
                              lag_ratio=0.1), run_time=0.6)                 # t=3.0
        self.play(Create(div), run_time=0.2); t += 0.2
        self.play(FadeIn(size_lbl, scale=1.05), run_time=0.4); t += 0.4

        # Blast rings pulse
        self.play(blast.animate.set_opacity(0.4).scale(1.1), run_time=0.3); t += 0.3

        # VTT 4.70: "The ground was hit by pure energy."
        self.play(FadeIn(pure, scale=1.05), run_time=0.4); t += 0.4
        self.play(Flash(pure.get_center(), color=BLAST_ORANGE,
                        line_length=0.3, num_lines=6, run_time=0.3))        # t=4.6
        self.play(blast.animate.set_opacity(0.15), run_time=0.2); t += 0.2
        self.play(FadeIn(vaporized, shift=UP * 0.1), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 6.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE PUNCH (27.5–37.0s = 9.50s)
# Visual: Building-sized rock → city-sized destruction → nothing left
# Zones: TITLE(letterbox) UPPER(building) MID(rock→explosion) LOWER(city) FOOTER(nothing)
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 9.5
    def construct(self):
        self.add(gradient_bg("#050508"), grid_lines(0.02))
        t = 0

        # Letterbox bars
        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP * (8 - bh / 2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN * (8 - bh / 2)),
        )

        # Ghost radial fallen trees bg — subtle atmosphere
        ghost_trees = VGroup()
        np.random.seed(66)
        for i in range(16):
            angle = i * (2 * PI / 16)
            dist = np.random.uniform(2, 4)
            ft = fallen_tree(ASH_GRAY, h=0.5)
            ft.rotate(angle)
            ft.move_to(np.array([np.cos(angle) * dist, np.sin(angle) * dist - 1, 0]))
            ghost_trees.add(ft)
        ghost_trees.set_opacity(0.06)
        self.add(ghost_trees)

        # Building comparison — ZONE_UPPER
        # Simple building shape
        bld_body = Rectangle(width=1.2, height=2.0, fill_color=SURFACE2, fill_opacity=0.8,
                             stroke_color=MUTED, stroke_width=1.5)
        # Windows
        bld_windows = VGroup()
        for wy in [0.5, 0.0, -0.5]:
            for wx in [-0.3, 0.3]:
                win = Rectangle(width=0.2, height=0.25, fill_color=SIBERIA_BLUE,
                                fill_opacity=0.4, stroke_width=0)
                win.move_to(np.array([wx, wy, 0]))
                bld_windows.add(win)
        building_shape = VGroup(bld_body, bld_windows)
        building_shape.move_to(UP * ZONE_UPPER + LEFT * 2.5)
        building_lbl = safe_text("SIZE OF A BUILDING", font="DM Serif Display",
                                 font_size=36, color=WHITE_SOFT)
        building_lbl.move_to(UP * ZONE_UPPER + RIGHT * 1.2)

        # Rock at ZONE_MID
        rock = rock_fragment(ASH_GRAY, size=1.2)
        rock.move_to(UP * ZONE_MID)

        # Comparison arrow from building to rock
        comp_arrow = Arrow(building_shape.get_bottom() + DOWN * 0.2,
                           rock.get_top() + UP * 0.2,
                           color=MUTED, stroke_width=1.5, buff=0.1)

        div1 = section_div(4, MUTED).move_to(UP * 2)
        div2 = section_div(4, BLAST_ORANGE).move_to(DOWN * 1.5)

        # City destruction text — ZONE_LOWER
        city = safe_text("DESTROYED A CITY.", font="Bebas Neue", font_size=80,
                         color=BLAST_ORANGE)
        city.move_to(DOWN * 2.8)

        # Destruction rings behind city text
        city_ring = Circle(radius=2.5, color=BLAST_ORANGE, stroke_width=1.5,
                           fill_opacity=0).set_opacity(0.2)
        city_ring.move_to(DOWN * 2.8)

        div3 = section_div(4, DEAD_GRAY).move_to(DOWN * 4.2)

        nothing = safe_text("Left absolutely", font="DM Serif Display",
                            font_size=40, color=MUTED)
        nothing.move_to(DOWN * 5.0)
        nothing2 = safe_text("nothing behind.", font="Bebas Neue", font_size=70,
                             color=SIBERIA_BLUE)
        nothing2.move_to(DOWN * 6.2)

        glow = Circle(radius=2.5, fill_color=SIBERIA_BLUE, fill_opacity=0.04, stroke_width=0)
        glow.move_to(nothing2)

        # ── Timing: 9.50s ──
        # VTT 0.20: "A rock the size of a building"
        self.play(FadeIn(building_shape, shift=DOWN * 0.2),
                  FadeIn(building_lbl, shift=LEFT * 0.2), run_time=0.5)    # t=0.5
        self.play(Create(div1), run_time=0.2); t += 0.2
        self.play(GrowFromCenter(rock), run_time=0.4); t += 0.4
        self.play(GrowArrow(comp_arrow), run_time=0.3); t += 0.3

        # VTT 1.50: "destroyed an area the size of a major city."
        self.play(Create(div2), run_time=0.2); t += 0.2
        self.play(FadeIn(city_ring),
                  FadeIn(city, scale=1.08), run_time=0.6)                   # t=2.2
        self.play(Flash(city.get_center(), color=BLAST_ORANGE,
                        line_length=0.4, num_lines=8, run_time=0.3))        # t=2.5

        # Rock dissolves — vaporized
        self.play(rock.animate.set_opacity(0.1).scale(0.3),
                  comp_arrow.animate.set_opacity(0.1),
                  run_time=0.5)                                             # t=3.0

        # VTT 3.50: "And it left absolutely nothing behind."
        self.play(Create(div3), run_time=0.3); t += 0.3
        self.play(FadeIn(nothing, shift=UP * 0.1), run_time=0.5); t += 0.5
        self.play(FadeIn(glow), FadeIn(nothing2, scale=1.08), run_time=0.7); t += 0.7

        # Slow pulse on city ring + ghost trees fade
        self.play(city_ring.animate.scale(1.1).set_opacity(0.1),
                  ghost_trees.animate.set_opacity(0.02),
                  run_time=1.0)                                             # t=5.5

        # Hold + fade to black
        self.wait(2.0); t += 2.0
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5
        target = getattr(self.__class__, 'DURATION', 9.5)
        self.wait(max(0.1, target - t - 0.8))


# ── Infra ─────────────────────────────────────────────────────
def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_WrongAnswer, Scene3_Scale,
          Scene4_Contradiction, Scene5_Proof, Scene6_Punch]
    config.output_file = f"tunguska_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"tunguska_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    sc = [Scene1_Hook, Scene2_WrongAnswer, Scene3_Scale,
          Scene4_Contradiction, Scene5_Proof, Scene6_Punch]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(sc):
        n = f"tunguska_scene_{i+1}"; print(f"  Preview {n}...")
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

    names = ["Scene1_Hook","Scene2_WrongAnswer","Scene3_Scale",
             "Scene4_Contradiction","Scene5_Proof","Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_tunguska.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="tunguska", audio_path=str(audio))
    final = od / "tunguska_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
