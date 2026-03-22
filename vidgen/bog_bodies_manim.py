#!/usr/bin/env python3
"""Bog Bodies — 2,000-year-old preserved humans in European peat bogs (Manim).
Contradiction/ritual arc. Dark, atmospheric, minimal.

6 scenes, ~37.0s (34.0s audio + 3s hold).

VTT cues (absolute → relative):
  Scene 1 (0.0–5.5s = 5.50s):
    0.200 (0.20) Tollund Man was found in a Danish bog in 1950.
    2.500 (2.50) He looked like he'd been dead for a week.
    4.000 (4.00) He had been dead for 2,400 years.
  Scene 2 (5.5–10.5s = 5.00s):
    5.700 (0.20) The peat cutters thought they'd found a murder victim.
    7.800 (2.30) His face was so well preserved
    9.000 (3.50) that police opened a homicide case.
  Scene 3 (10.5–16.5s = 6.00s):
    10.700 (0.20) Peat bogs are natural time capsules.
    12.200 (1.70) Cold, acidic, no oxygen.
    13.500 (3.00) They stop decay completely.
    14.500 (4.00) But Tollund Man wasn't just preserved.
    15.500 (5.00) He was hanged.
  Scene 4 (16.5–22.5s = 6.00s):
    16.700 (0.20) Over a thousand bog bodies have been found
    18.200 (1.70) across Northern Europe.
    19.200 (2.70) Beaten. Stabbed. Throats cut.
    20.500 (4.00) Sometimes all three.
    21.500 (5.00) Archaeologists call it the triple death.
  Scene 5 (22.5–28.0s = 5.50s):
    22.700 (0.20) These weren't random killings.
    24.000 (1.50) The pattern suggests ritual sacrifice.
    25.200 (2.70) Some were high-status. Well-fed. Groomed.
    26.500 (4.00) You don't sacrifice your slaves.
    27.200 (4.70) You sacrifice your best.
  Scene 6 (28.0–37.0s = 9.00s):
    28.200 (0.20) Two thousand years ago,
    29.500 (1.50) someone killed their most valuable person,
    31.000 (3.00) placed them in a bog, and walked away.
    33.000 (5.00) The bog preserved everything
    34.500 (6.50) except the reason.
    + 2.5s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """Tollund Man was found in a Danish bog in 1950. He looked dead for a week. He'd been dead 2,400 years. Police opened a homicide case. Peat bogs are time capsules. Cold, acidic, no oxygen. But he wasn't just preserved. He was hanged. Over a thousand bog bodies across Northern Europe. Beaten. Stabbed. Throats cut. The triple death. Ritual sacrifice. They weren't slaves — they were the best. The bog preserved everything except the reason."""

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
BOG_DARK = "#1A1208"; PEAT_BROWN = "#5C3A1E"
FLESH_TAN = "#C4956A"; RITUAL_RED = "#8B1A1A"
COLD_GRAY = "#606060"
WHITE_SOFT = "#F0F0F0"; MUTED = "#7B8DA0"; DIM = "#404050"
DEAD_GRAY = "#4A5568"; GOLD = "#FFD700"
VIOLENCE_RED = "#DD3333"
SAFE_W = 8.0

ZONE_TITLE  = 6.2
ZONE_UPPER  = 3.5
ZONE_MID    = 0.0
ZONE_LOWER  = -3.5
ZONE_FOOTER = -6.0


def gradient_bg(c=BG, g="#0A0805"):
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

def section_div(width=5, color=PEAT_BROWN):
    l = Line(LEFT * width / 2, LEFT * 0.12, color=color, stroke_width=1.5)
    r = Line(RIGHT * 0.12, RIGHT * width / 2, color=color, stroke_width=1.5)
    d = Square(side_length=0.1, color=color, fill_color=color, fill_opacity=1).rotate(45 * DEGREES)
    return VGroup(l, d, r)

def label_pill(txt, color=PEAT_BROWN, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    p = RoundedRectangle(width=t.width + 0.5, height=t.height + 0.3, corner_radius=0.18,
                         fill_color=bg, fill_opacity=0.95, stroke_color=color, stroke_width=1.5).move_to(t)
    return VGroup(p, t)

def safe_text(content, **kwargs):
    t = Text(content, **kwargs)
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    return t


# ── Domain Shape Helpers ──────────────────────────────────────

def bog_surface(width=8.0, color=BOG_DARK):
    """Dark water surface with reeds — horizontal line + vertical thin rects."""
    sc = width / 8.0
    water = Rectangle(width=width, height=0.15 * sc, fill_color=color, fill_opacity=0.8,
                      stroke_color=PEAT_BROWN, stroke_width=1)
    reeds = VGroup()
    np.random.seed(67)
    for _ in range(12):
        x = np.random.uniform(-width / 2 * 0.9, width / 2 * 0.9)
        h = np.random.uniform(0.4, 1.2) * sc
        reed = Rectangle(width=0.04 * sc, height=h, fill_color=PEAT_BROWN,
                         fill_opacity=np.random.uniform(0.3, 0.6), stroke_width=0)
        reed.move_to(np.array([x, h / 2 + 0.08 * sc, 0]))
        reeds.add(reed)
    return VGroup(water, reeds)

def noose_rope(color=PEAT_BROWN, h=2.0):
    """Hanging rope — arc loop + straight line down."""
    sc = h / 2.0
    line_down = Line(UP * 0.8 * sc, DOWN * 0.2 * sc, color=color, stroke_width=3 * sc)
    loop = Arc(radius=0.25 * sc, start_angle=-PI / 2, angle=-2 * PI * 0.85,
               color=color, stroke_width=3 * sc)
    loop.move_to(DOWN * 0.45 * sc)
    return VGroup(line_down, loop)

def face_preserved(color=FLESH_TAN, r=1.0):
    """Simple preserved face — circle with closed eyes, nose line, slight expression."""
    sc = r / 1.0
    head = Circle(radius=r, fill_color=color, fill_opacity=0.7,
                  stroke_color=PEAT_BROWN, stroke_width=1.5)
    l_eye = Arc(radius=0.15 * sc, start_angle=0, angle=PI,
                color=PEAT_BROWN, stroke_width=2).move_to(LEFT * 0.3 * sc + UP * 0.2 * sc)
    r_eye = Arc(radius=0.15 * sc, start_angle=0, angle=PI,
                color=PEAT_BROWN, stroke_width=2).move_to(RIGHT * 0.3 * sc + UP * 0.2 * sc)
    nose = Line(DOWN * 0.05 * sc, DOWN * 0.25 * sc, color=PEAT_BROWN, stroke_width=1.5)
    mouth = Line(LEFT * 0.2 * sc + DOWN * 0.45 * sc, RIGHT * 0.2 * sc + DOWN * 0.45 * sc,
                 color=PEAT_BROWN, stroke_width=1.5)
    return VGroup(head, l_eye, r_eye, nose, mouth)

def triple_death_icons(color=RITUAL_RED, sc=1.0):
    """3 small symbols: rope, dagger, slash — the triple death."""
    rope = noose_rope(color=color, h=0.8 * sc)
    rope.move_to(LEFT * 1.5 * sc)
    blade = Polygon(
        np.array([0, 0.4 * sc, 0]),
        np.array([-0.08 * sc, -0.1 * sc, 0]),
        np.array([0.08 * sc, -0.1 * sc, 0]),
        fill_color=color, fill_opacity=0.9, stroke_width=0
    )
    hilt = Rectangle(width=0.2 * sc, height=0.08 * sc, fill_color=color,
                     fill_opacity=0.7, stroke_width=0).move_to(DOWN * 0.14 * sc)
    dagger = VGroup(blade, hilt)
    slash = Line(LEFT * 0.2 * sc + UP * 0.2 * sc, RIGHT * 0.2 * sc + DOWN * 0.2 * sc,
                 color=color, stroke_width=3 * sc)
    slash.move_to(RIGHT * 1.5 * sc)
    return VGroup(rope, dagger, slash)

def crowned_figure(sc=1.0):
    """High-status stick figure with golden crown — sacrifice victim."""
    fig_head = Circle(radius=0.25 * sc, fill_color=FLESH_TAN, fill_opacity=0.8, stroke_width=0)
    fig_head.move_to(UP * 0.8 * sc)
    fig_body = Line(UP * 0.55 * sc, DOWN * 0.4 * sc, color=FLESH_TAN, stroke_width=3)
    fig_ll = Line(DOWN * 0.4 * sc, DOWN * 1.0 * sc + LEFT * 0.2 * sc, color=FLESH_TAN, stroke_width=2)
    fig_rl = Line(DOWN * 0.4 * sc, DOWN * 1.0 * sc + RIGHT * 0.2 * sc, color=FLESH_TAN, stroke_width=2)
    fig_la = Line(UP * 0.35 * sc, LEFT * 0.3 * sc + DOWN * 0.1 * sc, color=FLESH_TAN, stroke_width=2)
    fig_ra = Line(UP * 0.35 * sc, RIGHT * 0.3 * sc + DOWN * 0.1 * sc, color=FLESH_TAN, stroke_width=2)
    crown = Polygon(
        np.array([-0.2 * sc, 1.05 * sc, 0]), np.array([-0.12 * sc, 1.25 * sc, 0]),
        np.array([0, 1.1 * sc, 0]), np.array([0.12 * sc, 1.25 * sc, 0]),
        np.array([0.2 * sc, 1.05 * sc, 0]),
        fill_color=GOLD, fill_opacity=0.8, stroke_width=0
    )
    return VGroup(fig_head, fig_body, fig_ll, fig_rl, fig_la, fig_ra, crown)


# ================================================================
# SCENE 1: THE HOOK (0.0–5.5s = 5.50s)
# "Tollund Man. Dead for a week. Dead for 2,400 years."
# Zones: TITLE(pill) UPPER(1950+face) MID(bog surface) LOWER(contradiction) FOOTER(Denmark)
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 8.7
    def construct(self):
        self.add(gradient_bg(g="#0A0805"), grid_lines(0.03))
        t = 0

        pill = label_pill("TOLLUND MAN", color=FLESH_TAN, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # Year — ZONE_UPPER
        yr_1950 = safe_text("1950", font="Bebas Neue", font_size=90, color=COLD_GRAY)
        yr_1950.move_to(UP * 4.5)

        # Bog surface at ZONE_MID top
        bog = bog_surface(7.0, BOG_DARK)
        bog.move_to(UP * 1.5)

        # Face emerging from bog — ZONE_MID, half-submerged
        face = face_preserved(FLESH_TAN, r=1.2)
        face.move_to(UP * 0.2)
        face.set_opacity(0)

        # Peat layer beneath — adds depth to cross-section
        peat_layer = Rectangle(width=7.0, height=3.0, fill_color=BOG_DARK,
                               fill_opacity=0.3, stroke_width=0)
        peat_layer.move_to(DOWN * 0.8)

        div = section_div(5, MUTED).move_to(DOWN * 1.8)

        # The contradiction — ZONE_LOWER
        week = safe_text("A WEEK.", font="Bebas Neue", font_size=65, color=FLESH_TAN)
        week.move_to(DOWN * 2.8)

        div2 = section_div(5, RITUAL_RED).move_to(DOWN * 3.8)

        years = safe_text("2,400 YEARS.", font="Bebas Neue", font_size=100, color=RITUAL_RED)
        years.move_to(DOWN * 5.0)

        footer = safe_text("DENMARK", font="Inter", font_size=22,
                          color=DEAD_GRAY, weight="BOLD")
        footer.move_to(DOWN * ZONE_FOOTER)

        # ── Timing: 5.50s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.20: "Tollund Man was found in a Danish bog in 1950."
        self.play(FadeIn(yr_1950), run_time=0.3); t += 0.3
        self.play(FadeIn(bog), FadeIn(peat_layer), run_time=0.4); t += 0.4
        # Face slowly emerges
        self.play(face.animate.set_opacity(0.8), run_time=0.8); t += 0.8
        self.play(FadeIn(footer), run_time=0.2); t += 0.2

        # VTT 2.50: "He looked like he'd been dead for a week."
        self.wait(0.2); t += 0.2
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(week, shift=UP * 0.06), run_time=0.5); t += 0.5

        # Gentle zoom on face while viewer absorbs
        self.play(face.animate.scale(1.08), run_time=0.7); t += 0.7

        # VTT 4.00: "He had been dead for 2,400 years."
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(years, scale=1.15), run_time=0.5); t += 0.5
        self.play(Flash(years.get_center(), color=RITUAL_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=4.8
        target = getattr(self.__class__, 'DURATION', 8.7)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE WRONG ANSWER (5.5–10.5s = 5.00s)
# "They thought it was a murder victim. Police opened a case."
# Zones: TITLE(pill) UPPER(face detail) MID(police tape) LOWER(HOMICIDE) FOOTER(label)
# ================================================================
class Scene2_WrongAnswer(Scene):
    DURATION = 7.9
    def construct(self):
        self.add(gradient_bg("#080808"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE MISTAKE", color=COLD_GRAY, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # Preserved face close-up at UPPER — what the peat cutters saw
        face = face_preserved(FLESH_TAN, r=1.5)
        face.move_to(UP * ZONE_UPPER)

        # Question mark hovering — the mystery
        q_mark = safe_text("?", font="Bebas Neue", font_size=120, color=COLD_GRAY)
        q_mark.move_to(UP * ZONE_UPPER + RIGHT * 2.5)
        q_mark.set_opacity(0.5)

        # Police tape — diagonal stripe across MID
        tape = Rectangle(width=10, height=0.5, fill_color="#CCCC00",
                         fill_opacity=0.6, stroke_width=0)
        tape.rotate(15 * DEGREES)
        tape.move_to(UP * ZONE_MID + UP * 0.5)

        tape_txt = safe_text("CRIME SCENE", font="Inter", font_size=22,
                            color=BLACK, weight="BOLD")
        tape_txt.rotate(15 * DEGREES)
        tape_txt.move_to(UP * ZONE_MID + UP * 0.5)

        # Second tape stripe lower for visual density
        tape2 = Rectangle(width=10, height=0.35, fill_color="#CCCC00",
                          fill_opacity=0.35, stroke_width=0)
        tape2.rotate(-10 * DEGREES)
        tape2.move_to(DOWN * 0.8)

        div = section_div(5, COLD_GRAY).move_to(DOWN * 2.0)

        # HOMICIDE CASE — big impact text at ZONE_LOWER
        homicide = safe_text("HOMICIDE", font="Bebas Neue", font_size=90,
                            color=COLD_GRAY)
        homicide.move_to(DOWN * 3.0)

        case_lbl = safe_text("CASE OPENED", font="Bebas Neue", font_size=50,
                            color=DEAD_GRAY)
        case_lbl.move_to(DOWN * 4.2)

        # Skull icon to reinforce the "murder" read — visual, not text
        skull = Circle(radius=0.4, fill_color=COLD_GRAY, fill_opacity=0.15,
                      stroke_color=COLD_GRAY, stroke_width=1)
        skull_x1 = Line(LEFT * 0.15 + UP * 0.05, RIGHT * 0.15 + DOWN * 0.05,
                       color=COLD_GRAY, stroke_width=2)
        skull_x2 = Line(RIGHT * 0.15 + UP * 0.05, LEFT * 0.15 + DOWN * 0.05,
                       color=COLD_GRAY, stroke_width=2)
        skull_mark = VGroup(skull, skull_x1, skull_x2)
        skull_mark.move_to(DOWN * 5.2)

        footer = safe_text("1950 — SILKEBORG", font="Inter",
                          font_size=22, color=DEAD_GRAY, weight="BOLD")
        footer.move_to(DOWN * ZONE_FOOTER)

        # ── Timing: 5.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.20: "The peat cutters thought they'd found a murder victim."
        self.play(FadeIn(face, scale=0.9), run_time=0.5); t += 0.5
        self.play(FadeIn(q_mark, scale=1.3), run_time=0.3); t += 0.3
        self.play(FadeIn(tape), FadeIn(tape_txt), run_time=0.4); t += 0.4

        # VTT 2.30: "His face was so well preserved"
        self.wait(0.3); t += 0.3
        # Face pulses subtly — emphasis on preservation
        self.play(face.animate.scale(1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(tape2), run_time=0.3); t += 0.3

        # VTT 3.50: "that police opened a homicide case."
        self.play(Create(div), run_time=0.3); t += 0.3
        self.wait(0.4); t += 0.4
        self.play(FadeIn(homicide, scale=1.05), run_time=0.5); t += 0.5
        self.play(FadeIn(case_lbl, shift=UP * 0.04), run_time=0.3); t += 0.3
        self.play(FadeIn(skull_mark, scale=0.8), run_time=0.3); t += 0.3
        self.play(FadeIn(footer), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 7.9)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: THE CONTRADICTION (10.5–16.5s = 6.00s)
# "Bogs stop decay. But he was hanged."
# Zones: TITLE(pill) UPPER(TIME CAPSULE) MID(bog cross-section) LOWER(noose) FOOTER(HANGED)
# ================================================================
class Scene3_Contradiction(Scene):
    DURATION = 9.5
    def construct(self):
        self.add(gradient_bg(g="#0A0805"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE BOG", color=PEAT_BROWN, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        capsule = safe_text("TIME CAPSULE.", font="Bebas Neue", font_size=80,
                           color=PEAT_BROWN)
        capsule.move_to(UP * ZONE_UPPER)

        div1 = section_div(5, PEAT_BROWN).move_to(UP * 1.8)

        # Bog cross-section — stacked layers at ZONE_MID
        layer_water = Rectangle(width=6, height=0.5, fill_color="#1A2A1A",
                               fill_opacity=0.6, stroke_width=0.5, stroke_color=PEAT_BROWN)
        layer_water.move_to(UP * 1.0)
        lbl_water = safe_text("COLD", font="Inter", font_size=18, color=COLD_GRAY, weight="BOLD")
        lbl_water.move_to(LEFT * 3.8 + UP * 1.0)

        layer_acid = Rectangle(width=6, height=0.5, fill_color=PEAT_BROWN,
                              fill_opacity=0.5, stroke_width=0.5, stroke_color=PEAT_BROWN)
        layer_acid.move_to(UP * 0.4)
        lbl_acid = safe_text("ACIDIC", font="Inter", font_size=18, color=PEAT_BROWN, weight="BOLD")
        lbl_acid.move_to(LEFT * 3.8 + UP * 0.4)

        layer_anoxic = Rectangle(width=6, height=0.5, fill_color=BOG_DARK,
                                fill_opacity=0.7, stroke_width=0.5, stroke_color=PEAT_BROWN)
        layer_anoxic.move_to(DOWN * 0.2)
        lbl_anoxic = safe_text("NO O\u2082", font="Inter", font_size=18, color=COLD_GRAY, weight="BOLD")
        lbl_anoxic.move_to(LEFT * 3.8 + DOWN * 0.2)

        layers = VGroup(layer_water, layer_acid, layer_anoxic)
        labels = VGroup(lbl_water, lbl_acid, lbl_anoxic)

        # Red X through "DECAY" — ZONE_MID bottom
        decay = safe_text("DECAY", font="Bebas Neue", font_size=50, color=COLD_GRAY)
        decay.move_to(DOWN * 1.2)
        decay_x1 = Line(decay.get_corner(UL), decay.get_corner(DR),
                       color=RITUAL_RED, stroke_width=3)
        decay_x2 = Line(decay.get_corner(UR), decay.get_corner(DL),
                       color=RITUAL_RED, stroke_width=3)

        div2 = section_div(5, RITUAL_RED).move_to(DOWN * 2.2)

        # Noose — ZONE_LOWER
        noose = noose_rope(PEAT_BROWN, h=2.0)
        noose.move_to(DOWN * ZONE_LOWER)

        hanged = safe_text("HANGED.", font="Bebas Neue", font_size=90, color=RITUAL_RED)
        hanged.move_to(DOWN * 5.2)

        footer = safe_text("NOT JUST PRESERVED.", font="Inter",
                          font_size=22, color=DEAD_GRAY, weight="BOLD")
        footer.move_to(DOWN * ZONE_FOOTER)

        # ── Timing: 6.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.20: "Peat bogs are natural time capsules."
        self.play(FadeIn(capsule, scale=1.05), run_time=0.5); t += 0.5
        self.play(Create(div1), run_time=0.2); t += 0.2

        # VTT 1.70: "Cold, acidic, no oxygen."
        self.play(LaggedStart(*[FadeIn(l) for l in layers],
                              lag_ratio=0.15), run_time=0.5)               # t=1.5
        self.play(LaggedStart(*[FadeIn(l) for l in labels],
                              lag_ratio=0.15), run_time=0.4)               # t=1.9

        # Layers darken slightly — the bog deepens
        self.play(
            layer_water.animate.set_opacity(0.8),
            layer_acid.animate.set_opacity(0.7),
            layer_anoxic.animate.set_opacity(0.9),
            run_time=0.5,
        )                                                                   # t=2.4

        # VTT 3.00: "They stop decay completely."
        self.wait(0.3); t += 0.3
        self.play(FadeIn(decay), run_time=0.3); t += 0.3
        self.play(Create(decay_x1), Create(decay_x2), run_time=0.3); t += 0.3

        # VTT 4.00: "But Tollund Man wasn't just preserved."
        self.wait(0.4); t += 0.4
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(noose, scale=0.9), run_time=0.5); t += 0.5

        # VTT 5.00: "He was hanged."
        self.play(FadeIn(hanged, scale=1.15), run_time=0.5); t += 0.5
        self.play(Flash(hanged.get_center(), color=RITUAL_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=5.3
        self.play(FadeIn(footer), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 9.5)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE RITUAL (16.5–22.5s = 6.00s)
# "1,000 bodies. Beaten. Stabbed. Throats cut. Triple death."
# Zones: TITLE(pill) UPPER(1000+) MID(Europe dots) LOWER(triple death icons) FOOTER(label)
# ================================================================
class Scene4_Ritual(Scene):
    DURATION = 9.5
    def construct(self):
        self.add(gradient_bg("#080808"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE PATTERN", color=RITUAL_RED, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # "1,000+" — ZONE_UPPER
        thousand = safe_text("1,000+", font="Bebas Neue", font_size=120, color=FLESH_TAN)
        thousand.move_to(UP * 4)
        bodies_lbl = safe_text("BOG BODIES", font="Inter", font_size=28,
                              color=FLESH_TAN, weight="BOLD")
        bodies_lbl.move_to(UP * 2.5)

        div1 = section_div(5, PEAT_BROWN).move_to(UP * 1.5)

        # Map dots — simplified Europe outline (cluster of dots at ZONE_MID)
        map_dots = VGroup()
        np.random.seed(44)
        for _ in range(30):
            x = np.random.uniform(-2.5, 2.5)
            y = np.random.uniform(-1.0, 1.0)
            d = Dot(np.array([x, y, 0]), radius=0.06, color=VIOLENCE_RED).set_opacity(0.85)
            map_dots.add(d)

        europe_outline = Ellipse(width=6, height=3, fill_color=PEAT_BROWN,
                                fill_opacity=0.08, stroke_color=PEAT_BROWN, stroke_width=0.8)
        europe_label = safe_text("N. EUROPE", font="Inter", font_size=20,
                                color=COLD_GRAY, weight="BOLD")
        europe_label.move_to(RIGHT * 3.5)

        div2 = section_div(5, RITUAL_RED).move_to(DOWN * 2)

        # Violence labels — ZONE_LOWER
        violence = VGroup()
        v_data = [("BEATEN.", LEFT * 2.5), ("STABBED.", ORIGIN), ("THROAT CUT.", RIGHT * 2.5)]
        for txt, pos in v_data:
            lbl = safe_text(txt, font="Bebas Neue", font_size=45, color=VIOLENCE_RED)
            lbl.move_to(pos + DOWN * 3)
            violence.add(lbl)

        # Wound marks — diagonal slash pairs behind violence text
        wound_marks = VGroup()
        for xoff in [-2.5, 0, 2.5]:
            for dy in [-0.15, 0.15]:
                slash = Line(
                    LEFT * 0.18 + UP * (0.22 + dy),
                    RIGHT * 0.18 + DOWN * (0.22 - dy),
                    color=VIOLENCE_RED, stroke_width=2.5
                ).move_to(np.array([xoff, -3.0 + dy * 1.5, 0]))
                slash.set_opacity(0.55)
                wound_marks.add(slash)

        # Triple death icons — ZONE_LOWER/FOOTER
        triple = triple_death_icons(VIOLENCE_RED, sc=1.2)
        triple.move_to(DOWN * 4.5)

        triple_lbl = safe_text("TRIPLE DEATH", font="Bebas Neue", font_size=60,
                              color=VIOLENCE_RED)
        triple_lbl.move_to(DOWN * 5.8)

        footer = safe_text("RITUAL PATTERN", font="Inter",
                          font_size=22, color=DEAD_GRAY, weight="BOLD")
        footer.move_to(DOWN * ZONE_FOOTER)

        # ── Timing: 6.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.20: "Over a thousand bog bodies have been found"
        self.play(FadeIn(thousand, scale=1.15), run_time=0.5); t += 0.5
        self.play(Flash(thousand.get_center(), color=FLESH_TAN,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=1.1
        self.play(FadeIn(bodies_lbl), run_time=0.3); t += 0.3

        # VTT 1.70: "across Northern Europe."
        self.play(Create(div1), run_time=0.2); t += 0.2
        self.play(FadeIn(europe_outline), FadeIn(europe_label), run_time=0.3); t += 0.3
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in map_dots],
                              lag_ratio=0.02), run_time=0.6)               # t=2.5

        # Dots pulse outward — the pattern is everywhere
        self.play(
            *[d.animate.scale(1.3).set_opacity(1.0) for d in map_dots[:10]],
            run_time=0.3,
        )                                                                   # t=2.8

        # VTT 2.70: "Beaten. Stabbed. Throats cut."
        self.play(Create(div2), run_time=0.2); t += 0.2
        self.play(
            LaggedStart(*[FadeIn(v, shift=UP * 0.1) for v in violence], lag_ratio=0.2),
            FadeIn(wound_marks),
            run_time=0.7,
        )                                                                    # t=3.7

        # VTT 4.00: "Sometimes all three."
        self.play(FadeIn(triple, scale=0.9), run_time=0.5); t += 0.5

        # VTT 5.00: "Archaeologists call it the triple death."
        target = getattr(self.__class__, 'DURATION', 9.5)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeIn(triple_lbl, scale=1.08), run_time=0.5); t += 0.5
        self.play(Flash(triple_lbl.get_center(), color=RITUAL_RED,
                        line_length=0.3, num_lines=8, run_time=0.3))       # t=5.5
        self.play(FadeIn(footer), run_time=0.2); t += 0.2

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE THEORY (22.5–28.0s = 5.50s)
# "Ritual sacrifice. High-status. You sacrifice your best."
# Zones: TITLE(pill) UPPER(RITUAL) MID(crowned figure sinking) LOWER(YOUR BEST) FOOTER(label)
# ================================================================
class Scene5_Theory(Scene):
    DURATION = 8.7
    def construct(self):
        self.add(gradient_bg(g="#0A0805"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE THEORY", color=FLESH_TAN, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        ritual = safe_text("RITUAL SACRIFICE.", font="Bebas Neue", font_size=75,
                          color=PEAT_BROWN)
        ritual.move_to(UP * ZONE_UPPER)

        div1 = section_div(5, PEAT_BROWN).move_to(UP * 1.8)

        # High-status figure — ZONE_MID (stick figure with crown)
        figure = crowned_figure(sc=1.0)

        # Bog surface below figure — they're being lowered in
        bog_line = bog_surface(6.0, BOG_DARK)
        bog_line.move_to(DOWN * 1.2)

        # Status labels — ZONE_LOWER
        status_data = [
            ("WELL-FED.", LEFT * 2.2, FLESH_TAN),
            ("GROOMED.", RIGHT * 0, FLESH_TAN),
            ("HIGH-STATUS.", RIGHT * 2.2, GOLD),
        ]
        status_pills = []
        for txt, pos, col in status_data:
            p = label_pill(txt, color=col, bg=BOG_DARK, fs=22)
            p.move_to(pos + DOWN * 2.5)
            status_pills.append(p)

        div2 = section_div(5, GOLD).move_to(DOWN * ZONE_LOWER)

        # The turn — ZONE_LOWER
        your_best = safe_text("YOUR BEST.", font="Bebas Neue", font_size=90,
                             color=GOLD)
        your_best.move_to(DOWN * 4.8)

        footer = safe_text("NOT SLAVES. NOT CRIMINALS.", font="Inter",
                          font_size=22, color=DEAD_GRAY, weight="BOLD")
        footer.move_to(DOWN * ZONE_FOOTER)

        # ── Timing: 5.50s ──
        self.add(pill, ritual)

        # VTT 0.20: "These weren't random killings." — div1 enters
        self.play(Create(div1), run_time=0.3); t += 0.3

        # VTT 1.50: "The pattern suggests ritual sacrifice."
        self.wait(0.9); t += 0.9
        self.play(FadeIn(figure, scale=0.9), run_time=0.5); t += 0.5
        self.play(FadeIn(bog_line), run_time=0.3); t += 0.3

        # VTT 2.70: "Some were high-status. Well-fed. Groomed."
        target = getattr(self.__class__, 'DURATION', 8.7)
        self.wait(max(0.1, target - t - 0.3))
        self.play(LaggedStart(*[FadeIn(p, scale=1.05) for p in status_pills],
                              lag_ratio=0.15), run_time=0.6)               # t=3.0

        # Crown glows briefly — emphasis on high status
        crown = figure[-1]
        glow = Circle(radius=0.4, fill_color=GOLD, fill_opacity=0.15, stroke_width=0)
        glow.move_to(crown)
        self.play(FadeIn(glow, run_time=0.2)); t += 0.2

        # Figure sinks into bog
        self.play(
            figure.animate.shift(DOWN * 1.0).set_opacity(0.3),
            glow.animate.shift(DOWN * 1.0).set_opacity(0),
            run_time=0.5,
        )                                                                   # t=3.7

        # VTT 4.00/4.70: "You don't sacrifice your slaves. You sacrifice your best."
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(your_best, scale=1.12), run_time=0.5); t += 0.5
        self.play(Flash(your_best.get_center(), color=GOLD,
                        line_length=0.4, num_lines=10, run_time=0.3))      # t=4.8
        self.play(FadeIn(footer), run_time=0.2); t += 0.2

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE PUNCH (28.0–37.0s = 9.00s)
# "Placed them in a bog and walked away. Preserved everything except the reason."
# Zones: TITLE(letterbox) UPPER(face in water) MID(ripples/divider) LOWER(text) FOOTER(reason)
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 14.2
    def construct(self):
        self.add(gradient_bg("#050505"), grid_lines(0.02))
        t = 0

        # Letterbox bars
        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP * (8 - bh / 2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN * (8 - bh / 2)),
        )

        # Bog surface spanning full width — ZONE_UPPER
        bog = bog_surface(8.0, BOG_DARK)
        bog.move_to(UP * 3.5)
        self.add(bog)

        # Face in dark water — ZONE_UPPER, very subtle
        face = face_preserved(FLESH_TAN, r=1.5)
        face.move_to(UP * 2)
        face.set_opacity(0.2)
        self.add(face)

        # Ripple rings expanding from face — concentric circles
        ripples = VGroup()
        for i in range(4):
            r = Circle(radius=1.5 + i * 0.7, stroke_color=PEAT_BROWN,
                      stroke_width=1, fill_opacity=0)
            r.move_to(UP * 2)
            r.set_opacity(0)
            ripples.add(r)

        div1 = section_div(4, PEAT_BROWN).move_to(DOWN * 0.2)

        # Crowned figure walking away — small, at left side, moving right
        walker = crowned_figure(sc=0.6)
        walker.move_to(LEFT * 3.0 + DOWN * 1.0)
        walker.set_opacity(0.4)

        # Lower content — visual story beats
        line1 = safe_text("KILLED.", font="Bebas Neue", font_size=55, color=MUTED)
        line1.move_to(DOWN * 2.0)
        line2 = safe_text("PLACED.", font="Bebas Neue", font_size=55, color=FLESH_TAN)
        line2.move_to(DOWN * 3.0)
        line3 = safe_text("WALKED AWAY.", font="Bebas Neue", font_size=55, color=COLD_GRAY)
        line3.move_to(DOWN * 4.0)

        div2 = section_div(4, COLD_GRAY).move_to(DOWN * 4.8)

        reason = safe_text("EXCEPT THE REASON.", font="Bebas Neue", font_size=70,
                          color=PEAT_BROWN)
        reason.move_to(DOWN * 5.8)

        glow = Circle(radius=2.5, fill_color=PEAT_BROWN, fill_opacity=0.04, stroke_width=0)
        glow.move_to(reason)

        # ── Timing: 9.00s ──
        # VTT 0.20: "Two thousand years ago,"
        # Face brightens slightly
        self.play(face.animate.set_opacity(0.45), run_time=0.6); t += 0.6

        # Ripples expand slowly
        self.play(
            *[r.animate.set_opacity(0.15).scale(1.3) for r in ripples],
            run_time=1.0,
        )                                                                   # t=1.6

        # VTT 1.50: "someone killed their most valuable person,"
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(line1, shift=UP * 0.08), run_time=0.5); t += 0.5

        # VTT 3.00: "placed them in a bog, and walked away."
        self.play(FadeIn(line2, shift=UP * 0.06), run_time=0.5); t += 0.5

        # Walker appears and drifts away
        self.play(FadeIn(walker), run_time=0.3); t += 0.3
        self.play(
            walker.animate.shift(RIGHT * 6).set_opacity(0),
            FadeIn(line3, shift=UP * 0.06),
            run_time=0.8,
        )                                                                   # t=4.0

        # Face sinks back
        self.play(face.animate.set_opacity(0.12).shift(DOWN * 0.3),
                  run_time=0.7)                                             # t=4.7

        # VTT 5.00: "The bog preserved everything"
        # Ripples continue fading
        self.play(
            *[r.animate.set_opacity(0.05) for r in ripples],
            run_time=0.5,
        )                                                                   # t=5.2

        self.play(Create(div2), run_time=0.3); t += 0.3

        # VTT 6.50: "except the reason."
        self.wait(0.7); t += 0.7
        self.play(FadeIn(glow), FadeIn(reason, scale=1.08), run_time=0.8); t += 0.8

        # Hold + fade to black
        target = getattr(self.__class__, 'DURATION', 14.2)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5


# ── Infra ─────────────────────────────────────────────────────
def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_WrongAnswer, Scene3_Contradiction,
          Scene4_Ritual, Scene5_Theory, Scene6_Punch]
    config.output_file = f"bog_bodies_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"bog_bodies_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    sc = [Scene1_Hook, Scene2_WrongAnswer, Scene3_Contradiction,
          Scene4_Ritual, Scene5_Theory, Scene6_Punch]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(sc):
        n = f"bog_bodies_scene_{i+1}"; print(f"  Preview {n}...")
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

    names = ["Scene1_Hook","Scene2_WrongAnswer","Scene3_Contradiction",
             "Scene4_Ritual","Scene5_Theory","Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_bog_bodies.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="bog_bodies", audio_path=str(audio))
    final = od / "bog_bodies_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
