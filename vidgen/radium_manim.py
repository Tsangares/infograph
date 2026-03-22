#!/usr/bin/env python3
"""The Radium Girls (Manim). Radium green glow, 1920s corporate horror.

6 scenes, ~44.4s (41.4s audio + 3s hold).

VTT cues (absolute → relative):
  Scene 1 (0.0–5.5s = 5.50s):
    0.100 (0.10) A company told women to put radioactive paint in their mouths.
    4.020 (4.02) They said it was safe.
  Scene 2 (5.5–14.2s = 8.70s):
    5.480 (0.0)  The women painted watch dials with radium.
    8.160 (2.66) To get a fine point, they licked their brushes.
    11.100 (5.60) Lip, dip, paint.
    12.760 (7.26) Hundreds of times a day.
  Scene 3 (14.2–20.4s = 6.20s):
    14.260 (0.06) Their teeth fell out.
    15.300 (1.10) Their jaws crumbled.
    16.560 (2.36) Their bones glowed in the dark.
    18.320 (4.12) The company told them they were fine.
  Scene 4 (20.4–28.7s = 8.30s):
    20.400 (0.00) US Radium Corporation knew.
    22.500 (2.10) Their own scientists used lead shields.
    25.120 (4.72) They hired doctors to blame the women's symptoms on syphilis.
  Scene 5 (28.7–34.6s = 5.90s):
    28.700 (0.00) Five women sued.
    30.040 (1.34) They were dying.
    31.000 (2.30) The company called them liars.
    32.780 (4.08) The case went to trial anyway.
  Scene 6 (34.6–44.4s = 9.80s):
    34.660 (0.06) The Radium Girls lost everything.
    36.880 (2.28) But their lawsuit created the worker safety laws that protect every American today.
    + 3s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """A company told women to put radioactive paint in their mouths.
They said it was safe.
The women painted watch dials with radium.
To get a fine point, they licked their brushes.
Lip, dip, paint.
Hundreds of times a day.
Their teeth fell out.
Their jaws crumbled.
Their bones glowed in the dark.
The company told them they were fine.
US Radium Corporation knew.
Their own scientists used lead shields.
They hired doctors to blame the women's symptoms on syphilis.
Five women sued.
They were dying.
The company called them liars.
The case went to trial anyway.
The Radium Girls lost everything.
But their lawsuit created the worker safety laws that protect every American today."""

from manim import (
    Scene, Text, VGroup, Rectangle, RoundedRectangle, Circle,
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
config.background_color = "#080A08"
config.disable_caching = True

BG = "#080A08"; SURFACE = "#101810"; SURFACE2 = "#182018"
BORDER = "#2A3A2A"; GRID = "#141A14"
RED = "#E63946"; GOLD = "#FFD700"; GOLD_DIM = "#B8960F"
WHITE_SOFT = "#F0F0F0"; MUTED = "#7B8DA0"
DEAD_GRAY = "#4A5568"; FORM_BG = "#0C120C"; FORM_BORDER = "#2A3A2A"
# Radium signature colors
RADIUM = "#39FF14"; RADIUM_DIM = "#1A8A0A"; RADIUM_GLOW = "#2AE610"
RADIUM_DARK = "#0D3B06"; BONE_WHITE = "#E8E0D0"
CORP_GRAY = "#6B7280"; CORP_DARK = "#374151"
SAFE_W = 8.0


def gradient_bg(c=BG, g="#0A1A0A"):
    bg = Rectangle(width=12, height=20, fill_color=c, fill_opacity=1, stroke_width=0)
    glow = Circle(radius=5, fill_color=g, fill_opacity=0.10, stroke_width=0).move_to(UP * 2)
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

def section_div(width=5, color=RADIUM):
    l = Line(LEFT*width/2, LEFT*0.12, color=color, stroke_width=1.5)
    r = Line(RIGHT*0.12, RIGHT*width/2, color=color, stroke_width=1.5)
    d = Square(side_length=0.1, color=color, fill_color=color, fill_opacity=1).rotate(45*DEGREES)
    return VGroup(l, d, r)

def label_pill(txt, color=RADIUM, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    p = RoundedRectangle(width=t.width+0.5, height=t.height+0.3, corner_radius=0.18,
                         fill_color=bg, fill_opacity=0.95, stroke_color=color, stroke_width=1.5).move_to(t)
    return VGroup(p, t)

def safe_text(content, **kwargs):
    t = Text(content, **kwargs)
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    return t

def radium_glow_circle(r=2, x=0, y=0, opacity=0.06):
    return Circle(radius=r, fill_color=RADIUM, fill_opacity=opacity, stroke_width=0).move_to(
        np.array([x, y, 0]))

def paintbrush(x=0, y=0, height=4, angle=0):
    """Stylized paintbrush — handle + bristle tip with radium glow."""
    h = height; bw = h * 0.06
    handle = Rectangle(width=bw, height=h*0.7, fill_color="#8B6914",
                       fill_opacity=1, stroke_color="#5A3E0A", stroke_width=1.5)
    handle.move_to(np.array([x, y + h*0.15, 0]))
    ferrule = Rectangle(width=bw*1.3, height=h*0.06, fill_color=CORP_GRAY,
                        fill_opacity=1, stroke_width=0)
    ferrule.next_to(handle, DOWN, buff=0)
    tip = Polygon(
        np.array([x - bw*0.5, y - h*0.2, 0]),
        np.array([x + bw*0.5, y - h*0.2, 0]),
        np.array([x, y - h*0.5, 0]),
        fill_color=RADIUM, fill_opacity=0.9, stroke_color=RADIUM_DIM, stroke_width=1,
    )
    glow = Circle(radius=h*0.12, fill_color=RADIUM, fill_opacity=0.15, stroke_width=0)
    glow.move_to(tip.get_bottom() + UP * h * 0.05)
    grp = VGroup(handle, ferrule, tip, glow)
    if angle: grp.rotate(angle * DEGREES)
    return grp

def watch_dial(radius=2.0, x=0, y=0):
    """Watch face with radium-green numerals."""
    face = Circle(radius=radius, fill_color="#1A1A1A", fill_opacity=0.9,
                  stroke_color=CORP_GRAY, stroke_width=2)
    face.move_to(np.array([x, y, 0]))
    numerals = VGroup()
    for i in range(12):
        angle = PI/2 - i * 2*PI/12
        nx = x + radius*0.75 * np.cos(angle)
        ny = y + radius*0.75 * np.sin(angle)
        num = Text(str(i+1) if i > 0 else "12", font="Inter", font_size=18, color=RADIUM)
        num.move_to(np.array([nx, ny, 0]))
        numerals.add(num)
    # Hands
    hr = Line(np.array([x, y, 0]), np.array([x+radius*0.35, y+radius*0.25, 0]),
              color=RADIUM, stroke_width=2.5)
    mn = Line(np.array([x, y, 0]), np.array([x-radius*0.1, y+radius*0.55, 0]),
              color=RADIUM, stroke_width=2)
    glow = Circle(radius=radius*1.1, fill_color=RADIUM, fill_opacity=0.04, stroke_width=0)
    glow.move_to(face)
    return VGroup(face, numerals, hr, mn, glow)


# ================================================================
# SCENE 1: THE HOOK (0.0–5.5s = 5.50s)
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 5.1
    def construct(self):
        self.add(gradient_bg(), grid_lines())
        t = 0

        pill = label_pill("RADIUM GIRLS", color=RADIUM, fs=26)
        pill.move_to(UP * 7)

        glow = radium_glow_circle(3, 0, 2, 0.06)
        self.add(glow)

        company = safe_text("A company told women", font="DM Serif Display",
                           font_size=46, color=WHITE_SOFT)
        company.move_to(UP * 4)
        to_put = safe_text("to put radioactive paint", font="DM Serif Display",
                          font_size=44, color=RADIUM)
        to_put.move_to(UP * 2.8)
        mouths = safe_text("in their mouths.", font="DM Serif Display",
                          font_size=46, color=WHITE_SOFT)
        mouths.move_to(UP * 1.6)

        div = section_div(5, RADIUM).move_to(UP * 0.3)

        safe_txt = safe_text('"SAFE."', font="Bebas Neue", font_size=120, color=RADIUM)
        safe_txt.move_to(DOWN * 2)

        they_said = safe_text("They said it was safe.", font="DM Serif Display",
                             font_size=40, color=DEAD_GRAY)
        they_said.move_to(DOWN * 3.8)

        # ── Timing: 5.50s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(company, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(to_put, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(mouths, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(Create(div), run_time=0.3); t += 0.3
        self.wait(1.22); t += 1.22

        # VTT 4.02: "They said it was safe."
        self.play(FadeIn(safe_txt, scale=1.3), run_time=0.6); t += 0.6
        self.play(Flash(safe_txt.get_center(), color=RADIUM,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=4.62
        self.play(FadeIn(they_said, shift=UP * 0.04), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 5.1)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 2: THE METHOD (5.5–14.2s = 8.70s)
# ================================================================
class Scene2_Method(Scene):
    DURATION = 8.1
    def construct(self):
        self.add(gradient_bg(), grid_lines())
        t = 0

        pill = label_pill("THE METHOD", color=RADIUM, fs=28)
        pill.move_to(UP * 7)

        # Watch dial
        dial = watch_dial(radius=2.2, x=0, y=3.5)

        # "Painted watch dials with radium"
        painted = safe_text("Painted watch dials", font="DM Serif Display",
                           font_size=42, color=WHITE_SOFT)
        painted.move_to(UP * 0.5)
        with_rad = safe_text("with radium.", font="DM Serif Display",
                            font_size=44, color=RADIUM)
        with_rad.move_to(DOWN * 0.5)

        div1 = section_div(5, RADIUM).move_to(DOWN * 1.8)

        # "Lip. Dip. Paint." — the metronomic horror
        lip = safe_text("LIP.", font="Bebas Neue", font_size=80, color=RADIUM)
        lip.move_to(DOWN * 3)
        dip = safe_text("DIP.", font="Bebas Neue", font_size=80, color=RADIUM)
        dip.move_to(DOWN * 4.2)
        paint = safe_text("PAINT.", font="Bebas Neue", font_size=80, color=RADIUM)
        paint.move_to(DOWN * 5.4)

        div2 = section_div(5, DEAD_GRAY).move_to(DOWN * 6.5)

        hundreds = safe_text("Hundreds of times a day.", font="DM Serif Display",
                            font_size=40, color=DEAD_GRAY)
        hundreds.move_to(DOWN * 7.3)

        # ── Timing: 8.70s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.0: "The women painted watch dials with radium."
        self.play(FadeIn(dial, scale=0.8), run_time=0.7); t += 0.7
        self.play(FadeIn(painted, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(with_rad, shift=UP * 0.06), run_time=0.5); t += 0.5

        # VTT 2.66: "To get a fine point, they licked their brushes."
        self.wait(0.26); t += 0.26
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.wait(2.64); t += 2.64

        # VTT 5.60: "Lip, dip, paint."
        self.play(FadeIn(lip, scale=1.15), run_time=0.4); t += 0.4
        self.play(Flash(lip.get_center(), color=RADIUM,
                        line_length=0.2, num_lines=6, run_time=0.2))        # t=5.90
        self.play(FadeIn(dip, scale=1.15), run_time=0.4); t += 0.4
        self.play(FadeIn(paint, scale=1.15), run_time=0.4); t += 0.4
        self.play(Flash(paint.get_center(), color=RADIUM,
                        line_length=0.2, num_lines=6, run_time=0.2))        # t=6.90

        # VTT 7.26: "Hundreds of times a day."
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(hundreds, shift=UP * 0.04), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 8.1)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 3: THE HORROR (14.2–20.4s = 6.20s)
# ================================================================
class Scene3_Horror(Scene):
    DURATION = 5.8
    def construct(self):
        self.add(gradient_bg("#060806"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE HORROR", color=RED, fs=28)
        pill.move_to(UP * 7)

        # Rapid-fire body horror — each line slams in
        items = [
            ("TEETH FELL OUT.", UP * 4, RED),
            ("JAWS CRUMBLED.", UP * 2, RED),
            ("BONES GLOWED", DOWN * 0, RADIUM),
            ("IN THE DARK.", DOWN * 1.2, RADIUM),
        ]
        item_groups = []
        for txt, pos, col in items:
            lbl = safe_text(txt, font="Bebas Neue", font_size=70, color=col)
            lbl.move_to(pos)
            item_groups.append(lbl)

        # Radium glow behind "bones glowed"
        bone_glow = radium_glow_circle(3, 0, -0.5, 0.08)

        div = section_div(5, CORP_GRAY).move_to(DOWN * 3)

        fine = safe_text("The company told them", font="DM Serif Display",
                        font_size=40, color=CORP_GRAY)
        fine.move_to(DOWN * 4.2)
        fine2 = safe_text("they were fine.", font="DM Serif Display",
                         font_size=44, color=WHITE_SOFT)
        fine2.move_to(DOWN * 5.3)

        # ── Timing: 6.20s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.06: "Their teeth fell out."
        self.play(FadeIn(item_groups[0], shift=LEFT * 0.2), run_time=0.5); t += 0.5

        # VTT 1.10: "Their jaws crumbled."
        self.play(FadeIn(item_groups[1], shift=LEFT * 0.2), run_time=0.5); t += 0.5

        # VTT 2.36: "Their bones glowed in the dark."
        self.wait(0.76); t += 0.76
        self.add(bone_glow)
        self.play(FadeIn(item_groups[2], scale=1.1), run_time=0.5); t += 0.5
        self.play(FadeIn(item_groups[3], scale=1.1), run_time=0.4); t += 0.4
        self.play(Flash(item_groups[2].get_center(), color=RADIUM,
                        line_length=0.4, num_lines=10, run_time=0.3))      # t=3.26

        # VTT 4.12: "The company told them they were fine."
        self.wait(0.56); t += 0.56
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(fine, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(fine2, shift=UP * 0.06), run_time=0.6); t += 0.6
        target = getattr(self.__class__, 'DURATION', 5.8)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 4: THE COVERUP (20.4–28.7s = 8.30s)
# ================================================================
class Scene4_Coverup(Scene):
    DURATION = 7.7
    def construct(self):
        self.add(gradient_bg(), grid_lines())
        t = 0

        pill = label_pill("THE COVERUP", color=RED, fs=28)
        pill.move_to(UP * 7)

        corp = safe_text("US RADIUM", font="Bebas Neue", font_size=80, color=CORP_GRAY)
        corp.move_to(UP * 5)
        corp2 = safe_text("CORPORATION", font="Bebas Neue", font_size=70, color=CORP_GRAY)
        corp2.move_to(UP * 3.8)

        knew = safe_text("KNEW.", font="Bebas Neue", font_size=90, color=RED)
        knew.move_to(UP * 2)

        div1 = section_div(5, CORP_GRAY).move_to(UP * 0.5)

        shields = safe_text("Their own scientists", font="DM Serif Display",
                           font_size=40, color=WHITE_SOFT)
        shields.move_to(DOWN * 0.7)
        shields2 = safe_text("used lead shields.", font="DM Serif Display",
                            font_size=44, color=GOLD)
        shields2.move_to(DOWN * 1.8)

        div2 = section_div(5, RED).move_to(DOWN * 3)

        hired = safe_text("They hired doctors", font="DM Serif Display",
                         font_size=38, color=MUTED)
        hired.move_to(DOWN * 4.2)
        blame = safe_text("to blame the symptoms on", font="DM Serif Display",
                         font_size=36, color=MUTED)
        blame.move_to(DOWN * 5.2)
        syph = safe_text("SYPHILIS.", font="Bebas Neue", font_size=80, color=RED)
        syph.move_to(DOWN * 6.5)

        # ── Timing: 8.30s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.00: "US Radium Corporation knew."
        self.play(FadeIn(corp, scale=1.05), run_time=0.5); t += 0.5
        self.play(FadeIn(corp2), run_time=0.3); t += 0.3
        self.play(FadeIn(knew, scale=1.15), run_time=0.5); t += 0.5
        self.play(Flash(knew.get_center(), color=RED,
                        line_length=0.3, num_lines=8, run_time=0.3))        # t=1.9

        # VTT 2.10: "Their own scientists used lead shields."
        self.play(Create(div1), run_time=0.2); t += 0.2
        self.play(FadeIn(shields, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(shields2, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(Flash(shields2.get_center(), color=GOLD,
                        line_length=0.3, num_lines=6, run_time=0.3))        # t=3.6

        # VTT 4.72: "They hired doctors to blame... syphilis."
        self.wait(0.82); t += 0.82
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(hired, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(FadeIn(blame, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(FadeIn(syph, scale=1.1), run_time=0.6); t += 0.6
        self.play(Flash(syph.get_center(), color=RED,
                        line_length=0.4, num_lines=10, run_time=0.3))      # t=6.62
        target = getattr(self.__class__, 'DURATION', 7.7)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 5: THE FIGHT (28.7–34.6s = 5.90s)
# ================================================================
class Scene5_Fight(Scene):
    DURATION = 5.5
    def construct(self):
        self.add(gradient_bg(), grid_lines())
        t = 0

        pill = label_pill("THE FIGHT", color=GOLD, fs=28)
        pill.move_to(UP * 7)

        five = safe_text("5", font="Bebas Neue", font_size=200, color=GOLD)
        five.move_to(UP * 3.5)
        women = safe_text("WOMEN SUED.", font="Bebas Neue", font_size=70, color=WHITE_SOFT)
        women.move_to(UP * 1.2)

        dying = safe_text("They were dying.", font="DM Serif Display",
                         font_size=44, color=RED)
        dying.move_to(DOWN * 0.3)

        div = section_div(5, RED).move_to(DOWN * 1.5)

        liars = safe_text("The company called them", font="DM Serif Display",
                          font_size=38, color=CORP_GRAY)
        liars.move_to(DOWN * 2.7)
        liars2 = safe_text("LIARS.", font="Bebas Neue", font_size=80, color=RED)
        liars2.move_to(DOWN * 4)

        div2 = section_div(5, GOLD).move_to(DOWN * 5.2)

        trial = safe_text("The case went to trial", font="DM Serif Display",
                         font_size=42, color=WHITE_SOFT)
        trial.move_to(DOWN * 6.2)
        anyway = safe_text("anyway.", font="Bebas Neue", font_size=70, color=GOLD)
        anyway.move_to(DOWN * 7.2)

        # ── Timing: 5.90s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.00: "Five women sued."
        self.play(FadeIn(five, scale=1.3), run_time=0.5); t += 0.5
        self.play(Flash(five.get_center(), color=GOLD,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=1.1
        self.play(FadeIn(women), run_time=0.4); t += 0.4

        # VTT 1.34: "They were dying."
        self.play(FadeIn(dying, shift=UP * 0.04), run_time=0.5); t += 0.5

        # VTT 2.30: "The company called them liars."
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(liars, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(FadeIn(liars2, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(liars2.get_center(), color=RED,
                        line_length=0.3, num_lines=8, run_time=0.3))        # t=3.6

        # VTT 4.08: "The case went to trial anyway."
        self.wait(0.18); t += 0.18
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(trial, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(FadeIn(anyway, scale=1.08), run_time=0.5); t += 0.5
        self.play(Flash(anyway.get_center(), color=GOLD,
                        line_length=0.3, num_lines=8, run_time=0.3))        # t=5.38
        target = getattr(self.__class__, 'DURATION', 5.5)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 6: THE PUNCH (34.6–44.4s = 9.80s)
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 9.1
    def construct(self):
        self.add(gradient_bg("#050705"))
        t = 0

        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP * (8 - bh/2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN * (8 - bh/2)),
        )
        self.add(grid_lines(0.02))

        # Ghost glow
        ghost = radium_glow_circle(4, 0, 0, 0.03)
        self.add(ghost)

        div1 = section_div(4, MUTED).move_to(UP * 2)

        lost = safe_text("The Radium Girls", font="DM Serif Display",
                        font_size=44, color=RADIUM)
        lost.move_to(UP * 0.8)
        lost2 = safe_text("lost everything.", font="DM Serif Display",
                         font_size=46, color=WHITE_SOFT)
        lost2.move_to(DOWN * 0.2)

        div2 = section_div(4, GOLD).move_to(DOWN * 1.5)

        but = safe_text("But their lawsuit created", font="DM Serif Display",
                       font_size=38, color=WHITE_SOFT)
        but.move_to(DOWN * 2.8)
        laws = safe_text("the worker safety laws", font="DM Serif Display",
                        font_size=40, color=GOLD)
        laws.move_to(DOWN * 3.9)
        protect = safe_text("that protect every", font="DM Serif Display",
                           font_size=40, color=GOLD)
        protect.move_to(DOWN * 5)
        american = safe_text("American today.", font="Bebas Neue",
                            font_size=70, color=WHITE_SOFT)
        american.move_to(DOWN * 6.2)

        glow = Circle(radius=2.5, fill_color=RADIUM, fill_opacity=0.03, stroke_width=0)
        glow.move_to(american)

        # ── Timing: 9.80s ──
        # VTT 0.06: "The Radium Girls lost everything."
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(lost, shift=UP * 0.08), run_time=0.7); t += 0.7
        self.play(FadeIn(lost2, shift=UP * 0.08), run_time=0.7); t += 0.7

        # VTT 2.28: "But their lawsuit created the worker safety laws..."
        self.wait(0.28); t += 0.28
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(but, shift=UP * 0.06), run_time=0.7); t += 0.7
        self.play(FadeIn(laws, shift=UP * 0.06), run_time=0.7); t += 0.7
        self.play(FadeIn(protect, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(glow), FadeIn(american, scale=1.08), run_time=0.8); t += 0.8

        # 3s hold + fade
        target = getattr(self.__class__, 'DURATION', 9.1)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5


# ── Infra ─────────────────────────────────────────────────────
def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_Method, Scene3_Horror,
          Scene4_Coverup, Scene5_Fight, Scene6_Punch]
    config.output_file = f"radium_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"radium_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    sc = [Scene1_Hook, Scene2_Method, Scene3_Horror,
          Scene4_Coverup, Scene5_Fight, Scene6_Punch]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(sc):
        n = f"radium_scene_{i+1}"; print(f"  Preview {n}...")
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

    names = ["Scene1_Hook","Scene2_Method","Scene3_Horror",
             "Scene4_Coverup","Scene5_Fight","Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_radium.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="radium", audio_path=str(audio))
    final = od / "radium_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
