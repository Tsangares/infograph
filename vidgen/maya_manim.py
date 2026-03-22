#!/usr/bin/env python3
"""The Maya Didn't Disappear (Manim). Mystery/erasure arc.

6 scenes, ~44.0s (41.0s audio + 3s hold).

VTT cues (absolute → relative):
  Scene 1 (0.0–6.2s = 6.20s):
    0.180 (0.18) The Maya civilization vanished.
    2.360 (2.36) Millions of people, gone.
    4.480 (4.48) That is what every documentary says.
  Scene 2 (6.2–14.0s = 7.80s):
    7.060 (0.86) Historians blamed drought.
    8.860 (2.66) War. Collapse.
    10.700 (4.50) They said the jungle swallowed the cities
    12.120 (5.92) and the people just disappeared.
  Scene 3 (14.0–22.5s = 8.50s):
    14.400 (0.40) But the Maya did not vanish.
    16.760 (2.76) When the Spanish arrived,
    18.200 (4.20) they found millions of them.
    19.620 (5.62) Living in cities.
    20.780 (6.78) Speaking their language.
    21.960 (7.96) Writing books.
  Scene 4 (22.5–30.0s = 7.50s):
    23.140 (0.64) The Spanish burned every Maya book they could find.
    26.300 (3.80) Out of thousands,
    27.500 (5.00) four survived.
    28.720 (6.22) They called it saving souls.
  Scene 5 (30.0–35.6s = 5.60s):
    30.800 (0.80) Six million Maya are alive today.
    33.220 (3.22) They speak 30 languages.
    34.920 (4.92) They never left.
  Scene 6 (35.6–44.0s = 8.40s):
    36.200 (0.60) The Maya did not disappear.
    37.940 (2.34) We just stopped looking.
    39.380 (3.78) And then we called it a mystery.
    + 3s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """The Maya civilization vanished.
Millions of people, gone.
That is what every documentary says.
Historians blamed drought.
War. Collapse.
They said the jungle swallowed the cities
and the people just disappeared.
But the Maya did not vanish.
When the Spanish arrived,
they found millions of them.
Living in cities.
Speaking their language.
Writing books.
The Spanish burned every Maya book they could find.
Out of thousands,
four survived.
They called it saving souls.
Six million Maya are alive today.
They speak 30 languages.
They never left.
The Maya did not disappear.
We just stopped looking.
And then we called it a mystery."""

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
config.background_color = "#0A0A10"
config.disable_caching = True

BG = "#0A0A10"; SURFACE = "#12121C"; SURFACE2 = "#1A1A26"
BORDER = "#2A2A3A"; GRID = "#14141C"
RED = "#E63946"; GOLD = "#FFD700"; GOLD_DIM = "#B8960F"
WHITE_SOFT = "#F0F0F0"; MUTED = "#7B8DA0"; DEAD_GRAY = "#4A5568"
JADE = "#2ECC71"; JADE_DIM = "#1A8A4A"
JUNGLE = "#1B5E20"; JUNGLE_LIGHT = "#388E3C"
FLAME = "#FF6B35"; TERRACOTTA = "#C0392B"
SAFE_W = 8.0


def gradient_bg(c=BG, g="#0A1A12"):
    bg = Rectangle(width=12, height=20, fill_color=c, fill_opacity=1, stroke_width=0)
    glow = Circle(radius=5, fill_color=g, fill_opacity=0.10, stroke_width=0).move_to(UP * 2)
    return VGroup(bg, glow)

def star_field(n=25, seed=42):
    np.random.seed(seed)
    stars = VGroup()
    for _ in range(n):
        x = np.random.uniform(-4.5, 4.5); y = np.random.uniform(-8, 8)
        r = np.random.uniform(0.015, 0.035); op = np.random.uniform(0.15, 0.45)
        stars.add(Dot(point=np.array([x, y, 0]), radius=r, color=WHITE).set_opacity(op))
    return stars

def section_div(width=5, color=GOLD):
    l = Line(LEFT*width/2, LEFT*0.12, color=color, stroke_width=1.5)
    r = Line(RIGHT*0.12, RIGHT*width/2, color=color, stroke_width=1.5)
    d = Square(side_length=0.1, color=color, fill_color=color, fill_opacity=1).rotate(45*DEGREES)
    return VGroup(l, d, r)

def label_pill(txt, color=GOLD, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    p = RoundedRectangle(width=t.width+0.5, height=t.height+0.3, corner_radius=0.18,
                         fill_color=bg, fill_opacity=0.95, stroke_color=color, stroke_width=1.5).move_to(t)
    return VGroup(p, t)

def safe_text(content, **kwargs):
    t = Text(content, **kwargs)
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    return t

def maya_step_pyramid(height=4, width=5, x=0, y=0, color=JUNGLE):
    """Stepped pyramid silhouette — Maya temple."""
    steps = 5
    blocks = VGroup()
    for i in range(steps):
        frac = 1 - i / steps
        w = width * frac
        h = height / steps
        block = Rectangle(width=w, height=h, fill_color=color, fill_opacity=0.8,
                          stroke_color=JUNGLE_LIGHT, stroke_width=1)
        block.move_to(np.array([x, y + i * h, 0]))
        blocks.add(block)
    # Top temple
    temple = Rectangle(width=width*0.15, height=height*0.15, fill_color=color,
                       fill_opacity=0.9, stroke_color=JUNGLE_LIGHT, stroke_width=1)
    temple.move_to(np.array([x, y + height + height*0.075, 0]))
    blocks.add(temple)
    return blocks


# ================================================================
# SCENE 1: THE HOOK (0.0–6.2s = 6.20s)
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 5.8
    def construct(self):
        self.add(gradient_bg(), star_field(20, seed=1))
        t = 0

        pill = label_pill("THE MAYA", color=JADE, fs=26)
        pill.move_to(UP * 7)

        vanished = safe_text("VANISHED.", font="Bebas Neue", font_size=120, color=RED)
        vanished.move_to(UP * 3.5)

        millions = safe_text("Millions of people,", font="DM Serif Display",
                            font_size=46, color=WHITE_SOFT)
        millions.move_to(UP * 1.5)
        gone = safe_text("gone.", font="Bebas Neue", font_size=90, color=DEAD_GRAY)
        gone.move_to(DOWN * 0)

        div = section_div(5, MUTED).move_to(DOWN * 1.8)

        thats = safe_text("That is what every", font="DM Serif Display",
                         font_size=42, color=MUTED)
        thats.move_to(DOWN * 3)
        doc = safe_text("documentary says.", font="DM Serif Display",
                       font_size=44, color=MUTED)
        doc.move_to(DOWN * 4.1)

        # ── Timing: 6.20s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(vanished, scale=1.2), run_time=0.7); t += 0.7
        self.play(Flash(vanished.get_center(), color=RED,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=1.4

        # VTT 2.36: "Millions of people, gone."
        self.wait(0.66); t += 0.66
        self.play(FadeIn(millions, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(gone, scale=1.1), run_time=0.5); t += 0.5

        # VTT 4.48: "That is what every documentary says."
        self.wait(1.02); t += 1.02
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(thats, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(FadeIn(doc, shift=UP * 0.06), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 5.8)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 2: THE BLAME (6.2–14.0s = 7.80s)
# ================================================================
class Scene2_Blame(Scene):
    DURATION = 7.3
    def construct(self):
        self.add(gradient_bg("#080A08"), star_field(12, seed=7))
        t = 0

        pill = label_pill("THE BLAME", color=FLAME, fs=28)
        pill.move_to(UP * 7)

        # Pyramid being swallowed
        pyramid = maya_step_pyramid(3, 4, 0, 3)
        pyramid.set_opacity(0.5)

        blamed = safe_text("Historians blamed:", font="DM Serif Display",
                          font_size=44, color=MUTED)
        blamed.move_to(UP * 0.5)

        items = [
            ("DROUGHT.", DOWN * 1, FLAME),
            ("WAR.", DOWN * 2.3, RED),
            ("COLLAPSE.", DOWN * 3.6, RED),
        ]
        item_groups = []
        for txt, pos, col in items:
            lbl = safe_text(txt, font="Bebas Neue", font_size=80, color=col)
            lbl.move_to(pos)
            item_groups.append(lbl)

        div = section_div(5, JUNGLE).move_to(DOWN * 5)
        jungle_txt = safe_text("The jungle swallowed the cities.", font="DM Serif Display",
                              font_size=38, color=JUNGLE_LIGHT)
        jungle_txt.move_to(DOWN * 6)
        disappeared = safe_text("The people just disappeared.", font="DM Serif Display",
                               font_size=38, color=DEAD_GRAY)
        disappeared.move_to(DOWN * 7)

        # ── Timing: 7.80s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(pyramid, scale=0.9), run_time=0.5); t += 0.5

        # VTT 0.86: "Historians blamed drought."
        self.play(FadeIn(blamed, shift=UP * 0.04), run_time=0.4); t += 0.4
        self.play(FadeIn(item_groups[0], shift=LEFT * 0.1), run_time=0.5); t += 0.5

        # VTT 2.66: "War. Collapse."
        self.wait(0.66); t += 0.66
        self.play(FadeIn(item_groups[1], shift=LEFT * 0.1), run_time=0.4); t += 0.4
        self.play(FadeIn(item_groups[2], shift=LEFT * 0.1), run_time=0.5); t += 0.5

        # VTT 4.50: "They said the jungle swallowed the cities"
        self.wait(0.94); t += 0.94
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(jungle_txt, shift=UP * 0.04), run_time=0.6); t += 0.6

        # VTT 5.92: "and the people just disappeared."
        self.wait(0.52); t += 0.52
        self.play(FadeIn(disappeared, shift=UP * 0.04), run_time=0.6); t += 0.6
        target = getattr(self.__class__, 'DURATION', 7.3)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 3: THE TRUTH (14.0–22.5s = 8.50s)
# ================================================================
class Scene3_Truth(Scene):
    DURATION = 7.9
    def construct(self):
        self.add(gradient_bg(g="#0A1A0A"), star_field(15, seed=13))
        t = 0

        pill = label_pill("THE TRUTH", color=JADE, fs=28)
        pill.move_to(UP * 7)

        did_not = safe_text("THE MAYA", font="Bebas Neue", font_size=90, color=JADE)
        did_not.move_to(UP * 5)
        did_not2 = safe_text("DID NOT VANISH.", font="Bebas Neue", font_size=70, color=WHITE_SOFT)
        did_not2.move_to(UP * 3.5)

        div1 = section_div(5, JADE).move_to(UP * 2.2)

        spanish = safe_text("When the Spanish arrived,", font="DM Serif Display",
                           font_size=40, color=MUTED)
        spanish.move_to(UP * 1)
        found = safe_text("they found millions.", font="DM Serif Display",
                         font_size=46, color=WHITE_SOFT)
        found.move_to(DOWN * 0.2)

        # What they found — rapid-fire
        items = [
            ("Living in cities.", DOWN * 1.8, JADE),
            ("Speaking their language.", DOWN * 3, JADE),
            ("Writing books.", DOWN * 4.2, GOLD),
        ]
        item_groups = []
        for txt, pos, col in items:
            lbl = safe_text(txt, font="DM Serif Display", font_size=44, color=col)
            lbl.move_to(pos)
            item_groups.append(lbl)

        # ── Timing: 8.50s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.40: "But the Maya did not vanish."
        self.play(FadeIn(did_not, scale=1.1), run_time=0.6); t += 0.6
        self.play(FadeIn(did_not2, scale=1.05), run_time=0.5); t += 0.5
        self.play(Flash(did_not.get_center(), color=JADE,
                        line_length=0.4, num_lines=8, run_time=0.3))        # t=1.7

        # VTT 2.76: "When the Spanish arrived,"
        self.wait(0.76); t += 0.76
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(spanish, shift=UP * 0.06), run_time=0.5); t += 0.5

        # VTT 4.20: "they found millions of them."
        self.wait(0.64); t += 0.64
        self.play(FadeIn(found, shift=UP * 0.06), run_time=0.6); t += 0.6

        # VTT 5.62: "Living in cities."
        self.wait(0.82); t += 0.82
        self.play(FadeIn(item_groups[0], shift=UP * 0.06), run_time=0.5); t += 0.5

        # VTT 6.78: "Speaking their language."
        self.wait(0.66); t += 0.66
        self.play(FadeIn(item_groups[1], shift=UP * 0.06), run_time=0.5); t += 0.5

        # VTT 7.96: "Writing books."
        self.wait(0.68); t += 0.68
        self.play(FadeIn(item_groups[2], shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(Flash(item_groups[2].get_center(), color=GOLD,
                        line_length=0.3, num_lines=6, run_time=0.2))        # t=8.36
        target = getattr(self.__class__, 'DURATION', 7.9)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 4: THE ERASURE (22.5–30.0s = 7.50s)
# ================================================================
class Scene4_Erasure(Scene):
    DURATION = 7.0
    def construct(self):
        self.add(gradient_bg("#0A0808"), star_field(8, seed=44))
        t = 0

        pill = label_pill("THE ERASURE", color=RED, fs=28)
        pill.move_to(UP * 7)

        burned = safe_text("THE SPANISH BURNED", font="Bebas Neue", font_size=65, color=RED)
        burned.move_to(UP * 5)
        every = safe_text("every Maya book", font="DM Serif Display",
                         font_size=46, color=WHITE_SOFT)
        every.move_to(UP * 3.5)
        could = safe_text("they could find.", font="DM Serif Display",
                         font_size=46, color=MUTED)
        could.move_to(UP * 2.4)

        div1 = section_div(5, RED).move_to(UP * 1)

        out_of = safe_text("Out of thousands,", font="DM Serif Display",
                          font_size=42, color=MUTED)
        out_of.move_to(DOWN * 0.2)

        four = safe_text("4", font="Bebas Neue", font_size=220, color=GOLD)
        four.move_to(DOWN * 2.5)
        survived = safe_text("SURVIVED.", font="Bebas Neue", font_size=70, color=GOLD)
        survived.move_to(DOWN * 4.5)

        div2 = section_div(5, MUTED).move_to(DOWN * 5.5)
        souls = safe_text("They called it saving souls.", font="DM Serif Display",
                         font_size=40, color=DEAD_GRAY)
        souls.move_to(DOWN * 6.5)

        # ── Timing: 7.50s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.64: "The Spanish burned every Maya book..."
        self.play(FadeIn(burned, scale=1.05), run_time=0.5); t += 0.5
        self.play(FadeIn(every, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(FadeIn(could, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(Flash(burned.get_center(), color=RED,
                        line_length=0.4, num_lines=8, run_time=0.3))        # t=2.1
        self.play(Create(div1), run_time=0.3); t += 0.3

        # VTT 3.80: "Out of thousands,"
        self.wait(1.1); t += 1.1
        self.play(FadeIn(out_of, shift=UP * 0.04), run_time=0.5); t += 0.5

        # VTT 5.00: "four survived."
        self.wait(0.7); t += 0.7
        self.play(FadeIn(four, scale=1.3), run_time=0.6); t += 0.6
        self.play(Flash(four.get_center(), color=GOLD,
                        line_length=0.6, num_lines=12, run_time=0.3))      # t=5.6
        self.play(FadeIn(survived), run_time=0.4); t += 0.4

        # VTT 6.22: "They called it saving souls."
        self.play(Create(div2), run_time=0.22); t += 0.22
        self.play(FadeIn(souls, shift=UP * 0.04), run_time=0.6); t += 0.6
        target = getattr(self.__class__, 'DURATION', 7.0)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 5: THE LIVING (30.0–35.6s = 5.60s)
# ================================================================
class Scene5_Living(Scene):
    DURATION = 5.2
    def construct(self):
        self.add(gradient_bg(g="#0A1A0A"), star_field(15, seed=55))
        t = 0

        pill = label_pill("THE LIVING", color=JADE, fs=28)
        pill.move_to(UP * 7)

        six_mil = safe_text("6 MILLION", font="Bebas Neue", font_size=120, color=JADE)
        six_mil.move_to(UP * 4)
        maya = safe_text("MAYA ARE ALIVE TODAY.", font="Bebas Neue", font_size=60, color=WHITE_SOFT)
        maya.move_to(UP * 2.2)

        div1 = section_div(5, JADE).move_to(UP * 0.8)

        langs = safe_text("30", font="Bebas Neue", font_size=100, color=GOLD)
        langs.move_to(DOWN * 0.8)
        languages = safe_text("LANGUAGES", font="Inter", font_size=36,
                             color=WHITE_SOFT, weight="BOLD")
        languages.move_to(DOWN * 2)

        div2 = section_div(5, GOLD).move_to(DOWN * 3.2)

        never = safe_text("They never left.", font="Bebas Neue",
                         font_size=80, color=GOLD)
        never.move_to(DOWN * 4.5)

        # ── Timing: 5.60s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.80: "Six million Maya are alive today."
        self.wait(0.2); t += 0.2
        self.play(FadeIn(six_mil, scale=1.2), run_time=0.6); t += 0.6
        self.play(Flash(six_mil.get_center(), color=JADE,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=1.4
        self.play(FadeIn(maya), run_time=0.5); t += 0.5
        self.play(Create(div1), run_time=0.3); t += 0.3

        # VTT 3.22: "They speak 30 languages."
        self.wait(0.72); t += 0.72
        self.play(FadeIn(langs, scale=1.1), run_time=0.5); t += 0.5
        self.play(FadeIn(languages), run_time=0.3); t += 0.3

        # VTT 4.92: "They never left."
        self.wait(0.9); t += 0.9
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(never, scale=1.08), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 5.2)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 6: THE PUNCH (35.6–44.0s = 8.40s)
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 7.8
    def construct(self):
        self.add(gradient_bg("#050508"))
        t = 0

        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP * (8 - bh/2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN * (8 - bh/2)),
        )
        self.add(star_field(12, seed=99))

        # Ghost pyramid
        ghost = maya_step_pyramid(5, 6, 0, 0)
        ghost.set_opacity(0.04)
        self.add(ghost)

        div1 = section_div(4, JADE).move_to(UP * 1.5)

        line1 = safe_text("The Maya did not", font="DM Serif Display",
                          font_size=44, color=WHITE_SOFT)
        line1.move_to(UP * 0.2)
        line2 = safe_text("disappear.", font="Bebas Neue", font_size=80, color=JADE)
        line2.move_to(DOWN * 1)

        div2 = section_div(4, MUTED).move_to(DOWN * 2.3)

        line3 = safe_text("We just stopped looking.", font="DM Serif Display",
                          font_size=42, color=MUTED)
        line3.move_to(DOWN * 3.5)

        div3 = section_div(4, GOLD).move_to(DOWN * 4.8)

        mystery = safe_text("And then we called it", font="DM Serif Display",
                           font_size=40, color=WHITE_SOFT)
        mystery.move_to(DOWN * 5.8)
        a_mystery = safe_text("a mystery.", font="Bebas Neue", font_size=80, color=GOLD)
        a_mystery.move_to(DOWN * 6.8)

        glow = Circle(radius=2.5, fill_color=GOLD, fill_opacity=0.04, stroke_width=0)
        glow.move_to(a_mystery)

        # ── Timing: 8.40s ──
        # VTT 0.60: "The Maya did not disappear."
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(line1, shift=UP * 0.08), run_time=0.6); t += 0.6
        self.play(FadeIn(line2, scale=1.08), run_time=0.7); t += 0.7

        # VTT 2.34: "We just stopped looking."
        self.wait(0.44); t += 0.44
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(line3, shift=UP * 0.06), run_time=0.7); t += 0.7

        # VTT 3.78: "And then we called it a mystery."
        self.wait(0.44); t += 0.44
        self.play(Create(div3), run_time=0.3); t += 0.3
        self.play(FadeIn(mystery, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(glow), FadeIn(a_mystery, scale=1.08), run_time=0.8); t += 0.8

        # 3s hold + fade
        target = getattr(self.__class__, 'DURATION', 7.8)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5


# ── Infra ─────────────────────────────────────────────────────
def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_Blame, Scene3_Truth,
          Scene4_Erasure, Scene5_Living, Scene6_Punch]
    config.output_file = f"maya_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"maya_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    sc = [Scene1_Hook, Scene2_Blame, Scene3_Truth,
          Scene4_Erasure, Scene5_Living, Scene6_Punch]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(sc):
        n = f"maya_scene_{i+1}"; print(f"  Preview {n}...")
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

    names = ["Scene1_Hook","Scene2_Blame","Scene3_Truth",
             "Scene4_Erasure","Scene5_Living","Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_maya.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="maya", audio_path=str(audio))
    final = od / "maya_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
