#!/usr/bin/env python3
"""Norse Greenland — 'They Chose to Die' (Manim). Identity vs survival arc.

6 scenes, ~50.4s (47.4s audio + 3s hold).

VTT cues (absolute → relative):
  Scene 1 (0.0–6.3s = 6.30s):
    0.180 (0.18) The Norse colony in Greenland starved to death
    2.820 (2.82) surrounded by the most abundant fishing waters on Earth.
  Scene 2 (6.3–12.5s = 6.20s):
    6.420 (0.12) Historians said the climate killed them.
    8.480 (2.18) The Little Ice Age froze their farms.
    10.760 (4.46) They could not grow food anymore.
  Scene 3 (12.5–20.5s = 8.00s):
    12.480 (0.0)  But the Inuit survived the same climate.
    14.980 (2.48) Right next to them.
    16.160 (3.66) For centuries.
    17.340 (4.84) The Inuit ate fish and seal.
    19.620 (7.12) The Norse refused.
  Scene 4 (20.5–30.5s = 10.00s):
    21.220 (0.72) Archaeologists tested their bones.
    23.660 (3.16) After 500 years in Greenland,
    26.260 (5.76) Norse diets were still 80 percent cattle.
    28.920 (8.42) Almost no seafood.
  Scene 5 (30.5–39.5s = 9.00s):
    30.540 (0.04) They chose to starve.
    31.960 (1.46) They were Europeans.
    33.160 (2.66) Farmers.
    33.860 (3.36) Christians.
    34.660 (4.16) Eating fish and seal meant becoming something else.
    37.280 (6.78) It meant admitting Greenland had beaten them.
  Scene 6 (39.5–50.4s = 10.90s):
    40.120 (0.62) The last Norse in Greenland had a choice.
    42.740 (3.24) Adapt and survive,
    44.260 (4.76) or stay who they were and die.
    46.440 (6.94) They chose to die.
    + 3s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """The Norse colony in Greenland starved to death
surrounded by the most abundant fishing waters on Earth.
Historians said the climate killed them.
The Little Ice Age froze their farms.
They could not grow food anymore.
But the Inuit survived the same climate.
Right next to them.
For centuries.
The Inuit ate fish and seal.
The Norse refused.
Archaeologists tested their bones.
After 500 years in Greenland,
Norse diets were still 80 percent cattle.
Almost no seafood.
They chose to starve.
They were Europeans.
Farmers.
Christians.
Eating fish and seal meant becoming something else.
It meant admitting Greenland had beaten them.
The last Norse in Greenland had a choice.
Adapt and survive,
or stay who they were and die.
They chose to die."""

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
config.background_color = "#080A10"
config.disable_caching = True

BG = "#080A10"; SURFACE = "#101820"; SURFACE2 = "#182028"
BORDER = "#2A3A48"; GRID = "#141C24"
RED = "#E63946"; GOLD = "#FFD700"; GOLD_DIM = "#B8960F"
WHITE_SOFT = "#F0F0F0"; MUTED = "#7B8DA0"; DEAD_GRAY = "#4A5568"
ICE_BLUE = "#A8D8EA"; ICE_DIM = "#5B9BBF"; ICE_DARK = "#2C5F7C"
FROST = "#D6EAF8"; WARM_FIRE = "#E67E22"
NORSE = "#C49A6C"; NORSE_DIM = "#8B6B3D"
SAFE_W = 8.0


def gradient_bg(c=BG, g="#0A1420"):
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


# ================================================================
# SCENE 1: THE HOOK (0.0–6.3s)
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 5.9
    def construct(self):
        self.add(gradient_bg(g="#081828"), star_field(20, seed=1))
        t = 0

        pill = label_pill("NORSE GREENLAND", color=ICE_BLUE, fs=24)
        pill.move_to(UP * 7)

        starved = safe_text("STARVED", font="Bebas Neue", font_size=110, color=RED)
        starved.move_to(UP * 4)
        to_death = safe_text("TO DEATH.", font="Bebas Neue", font_size=90, color=RED)
        to_death.move_to(UP * 2.5)

        div = section_div(5, ICE_BLUE).move_to(UP * 1)

        surrounded = safe_text("Surrounded by", font="DM Serif Display",
                              font_size=44, color=WHITE_SOFT)
        surrounded.move_to(DOWN * 0.3)
        abundant = safe_text("the most abundant", font="DM Serif Display",
                            font_size=44, color=ICE_BLUE)
        abundant.move_to(DOWN * 1.4)
        fishing = safe_text("fishing waters on Earth.", font="DM Serif Display",
                           font_size=44, color=ICE_BLUE)
        fishing.move_to(DOWN * 2.5)

        # ── Timing: 6.30s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(starved, scale=1.2), run_time=0.6); t += 0.6
        self.play(FadeIn(to_death, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(starved.get_center(), color=RED,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=1.8
        self.play(Create(div), run_time=0.3); t += 0.3

        # VTT 2.82: "surrounded by the most abundant fishing waters..."
        self.wait(0.42); t += 0.42
        self.play(FadeIn(surrounded, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(abundant, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(fishing, shift=UP * 0.06), run_time=0.6); t += 0.6
        target = getattr(self.__class__, 'DURATION', 5.9)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 2: THE BLAME (6.3–12.5s)
# ================================================================
class Scene2_Blame(Scene):
    DURATION = 5.8
    def construct(self):
        self.add(gradient_bg(), star_field(12, seed=7))
        t = 0

        pill = label_pill("THE BLAME", color=FROST, fs=28)
        pill.move_to(UP * 7)

        climate = safe_text("THE CLIMATE", font="Bebas Neue", font_size=90, color=FROST)
        climate.move_to(UP * 4.5)
        killed = safe_text("killed them.", font="DM Serif Display", font_size=48, color=MUTED)
        killed.move_to(UP * 3)

        div1 = section_div(5, ICE_BLUE).move_to(UP * 1.5)

        little = safe_text("THE LITTLE ICE AGE", font="Bebas Neue", font_size=70, color=ICE_BLUE)
        little.move_to(UP * 0)
        froze = safe_text("froze their farms.", font="DM Serif Display",
                         font_size=44, color=WHITE_SOFT)
        froze.move_to(DOWN * 1.2)

        div2 = section_div(5, DEAD_GRAY).move_to(DOWN * 2.5)

        no_food = safe_text("They could not grow food", font="DM Serif Display",
                           font_size=42, color=DEAD_GRAY)
        no_food.move_to(DOWN * 3.5)
        anymore = safe_text("anymore.", font="DM Serif Display", font_size=46, color=DEAD_GRAY)
        anymore.move_to(DOWN * 4.5)

        # ── Timing: 6.20s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(climate, scale=1.1), run_time=0.6); t += 0.6
        self.play(FadeIn(killed, shift=UP * 0.04), run_time=0.5); t += 0.5

        # VTT 2.18: "The Little Ice Age froze their farms."
        self.wait(0.48); t += 0.48
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(little, scale=1.05), run_time=0.6); t += 0.6
        self.play(FadeIn(froze, shift=UP * 0.06), run_time=0.5); t += 0.5

        # VTT 4.46: "They could not grow food anymore."
        self.wait(0.88); t += 0.88
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(no_food, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(anymore, shift=UP * 0.06), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 5.8)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 3: THE CONTRADICTION (12.5–20.5s)
# ================================================================
class Scene3_Contradiction(Scene):
    DURATION = 7.5
    def construct(self):
        self.add(gradient_bg(g="#0A1A20"), star_field(15, seed=13))
        t = 0

        pill = label_pill("THE CONTRADICTION", color=RED, fs=28)
        pill.move_to(UP * 7)

        inuit = safe_text("THE INUIT", font="Bebas Neue", font_size=90, color=ICE_BLUE)
        inuit.move_to(UP * 5)
        survived = safe_text("survived the same climate.", font="DM Serif Display",
                            font_size=42, color=WHITE_SOFT)
        survived.move_to(UP * 3.5)

        next_to = safe_text("Right next to them.", font="DM Serif Display",
                           font_size=44, color=ICE_BLUE)
        next_to.move_to(UP * 2)
        centuries = safe_text("For centuries.", font="Bebas Neue", font_size=70, color=ICE_BLUE)
        centuries.move_to(UP * 0.6)

        div = section_div(5, GOLD).move_to(DOWN * 0.8)

        ate = safe_text("The Inuit ate", font="DM Serif Display", font_size=44, color=WHITE_SOFT)
        ate.move_to(DOWN * 2)
        fish_seal = safe_text("FISH AND SEAL.", font="Bebas Neue", font_size=80, color=ICE_BLUE)
        fish_seal.move_to(DOWN * 3.3)

        div2 = section_div(5, RED).move_to(DOWN * 4.6)

        refused = safe_text("THE NORSE REFUSED.", font="Bebas Neue", font_size=70, color=RED)
        refused.move_to(DOWN * 5.8)

        # ── Timing: 8.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.0: "But the Inuit survived the same climate."
        self.play(FadeIn(inuit, scale=1.1), run_time=0.6); t += 0.6
        self.play(FadeIn(survived, shift=UP * 0.06), run_time=0.5); t += 0.5

        # VTT 2.48: "Right next to them."
        self.wait(0.78); t += 0.78
        self.play(FadeIn(next_to, shift=UP * 0.06), run_time=0.5); t += 0.5

        # VTT 3.66: "For centuries."
        self.wait(0.68); t += 0.68
        self.play(FadeIn(centuries, scale=1.05), run_time=0.5); t += 0.5

        # VTT 4.84: "The Inuit ate fish and seal."
        self.wait(0.68); t += 0.68
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(ate, shift=UP * 0.06), run_time=0.4); t += 0.4
        self.play(FadeIn(fish_seal, scale=1.05), run_time=0.5); t += 0.5

        # VTT 7.12: "The Norse refused."
        self.wait(1.08); t += 1.08
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(refused, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(refused.get_center(), color=RED,
                        line_length=0.3, num_lines=8, run_time=0.3))        # t=7.92
        target = getattr(self.__class__, 'DURATION', 7.5)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 4: THE PROOF (20.5–30.5s)
# ================================================================
class Scene4_Proof(Scene):
    DURATION = 9.4
    def construct(self):
        self.add(gradient_bg(), star_field(10, seed=44))
        t = 0

        pill = label_pill("THE PROOF", color=GOLD, fs=28)
        pill.move_to(UP * 7)

        bones = safe_text("TESTED THEIR BONES.", font="Bebas Neue", font_size=65, color=WHITE_SOFT)
        bones.move_to(UP * 5)

        div1 = section_div(5, GOLD).move_to(UP * 3.5)

        after = safe_text("After 500 years", font="DM Serif Display", font_size=46, color=GOLD)
        after.move_to(UP * 2.2)
        in_gl = safe_text("in Greenland:", font="DM Serif Display", font_size=46, color=MUTED)
        in_gl.move_to(UP * 1)

        # Bar chart: 80% cattle vs ~0% seafood
        cattle_bar = Rectangle(width=3.5, height=0.8, fill_color=NORSE, fill_opacity=0.8,
                               stroke_color=NORSE_DIM, stroke_width=2)
        cattle_bar.move_to(LEFT * 0.5 + DOWN * 0.5)
        cattle_lbl = safe_text("80% CATTLE", font="Bebas Neue", font_size=50, color=NORSE)
        cattle_lbl.move_to(cattle_bar.get_center())

        sea_bar = Rectangle(width=0.4, height=0.8, fill_color=ICE_BLUE, fill_opacity=0.5,
                            stroke_color=ICE_DIM, stroke_width=2)
        sea_bar.move_to(RIGHT * 3 + DOWN * 0.5)
        sea_lbl = safe_text("~0%", font="Bebas Neue", font_size=40, color=ICE_DIM)
        sea_lbl.next_to(sea_bar, RIGHT, buff=0.2)

        div2 = section_div(5, RED).move_to(DOWN * 2.5)

        no_sea = safe_text("ALMOST NO SEAFOOD.", font="Bebas Neue", font_size=70, color=RED)
        no_sea.move_to(DOWN * 3.8)

        five_hundred = safe_text("500 years.", font="DM Serif Display",
                                font_size=50, color=DEAD_GRAY)
        five_hundred.move_to(DOWN * 5.2)
        still = safe_text("Still eating cattle.", font="DM Serif Display",
                         font_size=44, color=DEAD_GRAY)
        still.move_to(DOWN * 6.2)

        # ── Timing: 10.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.72: "Archaeologists tested their bones."
        self.play(FadeIn(bones, scale=1.05), run_time=0.6); t += 0.6

        # VTT 3.16: "After 500 years in Greenland,"
        self.wait(1.96); t += 1.96
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(after, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(in_gl, shift=UP * 0.06), run_time=0.5); t += 0.5

        # VTT 5.76: "Norse diets were still 80 percent cattle."
        self.wait(1.2); t += 1.2
        self.play(FadeIn(cattle_bar), FadeIn(cattle_lbl), run_time=0.6); t += 0.6
        self.play(FadeIn(sea_bar), FadeIn(sea_lbl), run_time=0.4); t += 0.4

        # VTT 8.42: "Almost no seafood."
        self.wait(1.66); t += 1.66
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(no_sea, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(no_sea.get_center(), color=RED,
                        line_length=0.3, num_lines=8, run_time=0.3))        # t=9.22
        self.play(FadeIn(five_hundred, shift=UP * 0.04), run_time=0.4); t += 0.4
        self.play(FadeIn(still, shift=UP * 0.04), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 9.4)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 5: THE IDENTITY (30.5–39.5s)
# ================================================================
class Scene5_Identity(Scene):
    DURATION = 8.5
    def construct(self):
        self.add(gradient_bg("#0A0808"), star_field(8, seed=55))
        t = 0

        pill = label_pill("THE IDENTITY", color=WARM_FIRE, fs=28)
        pill.move_to(UP * 7)

        chose = safe_text("CHOSE TO STARVE.", font="Bebas Neue", font_size=80, color=RED)
        chose.move_to(UP * 5)

        # Identity markers
        items = [
            ("EUROPEANS.", UP * 2.8, NORSE),
            ("FARMERS.", UP * 1.4, NORSE),
            ("CHRISTIANS.", UP * 0, NORSE),
        ]
        item_groups = []
        for txt, pos, col in items:
            lbl = safe_text(txt, font="Bebas Neue", font_size=70, color=col)
            lbl.move_to(pos)
            item_groups.append(lbl)

        div = section_div(5, MUTED).move_to(DOWN * 1.5)

        eating = safe_text("Eating fish and seal meant", font="DM Serif Display",
                          font_size=38, color=MUTED)
        eating.move_to(DOWN * 2.7)
        becoming = safe_text("becoming something else.", font="DM Serif Display",
                            font_size=40, color=WHITE_SOFT)
        becoming.move_to(DOWN * 3.8)

        div2 = section_div(5, RED).move_to(DOWN * 5)

        admitting = safe_text("Admitting Greenland", font="DM Serif Display",
                             font_size=42, color=WHITE_SOFT)
        admitting.move_to(DOWN * 6.2)
        beaten = safe_text("had beaten them.", font="DM Serif Display",
                          font_size=44, color=RED)
        beaten.move_to(DOWN * 7.2)

        # ── Timing: 9.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.04: "They chose to starve."
        self.play(FadeIn(chose, scale=1.1), run_time=0.6); t += 0.6
        self.play(Flash(chose.get_center(), color=RED,
                        line_length=0.4, num_lines=8, run_time=0.3))        # t=1.2

        # VTT 1.46: "They were Europeans."
        self.play(FadeIn(item_groups[0], shift=LEFT * 0.1), run_time=0.4); t += 0.4

        # VTT 2.66: "Farmers."
        self.wait(0.76); t += 0.76
        self.play(FadeIn(item_groups[1], shift=LEFT * 0.1), run_time=0.4); t += 0.4

        # VTT 3.36: "Christians."
        self.wait(0.3); t += 0.3
        self.play(FadeIn(item_groups[2], shift=LEFT * 0.1), run_time=0.4); t += 0.4

        # VTT 4.16: "Eating fish and seal meant becoming something else."
        self.wait(0.4); t += 0.4
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(eating, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(becoming, shift=UP * 0.06), run_time=0.6); t += 0.6

        # VTT 6.78: "It meant admitting Greenland had beaten them."
        self.wait(1.12); t += 1.12
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(admitting, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(beaten, shift=UP * 0.06), run_time=0.6); t += 0.6
        target = getattr(self.__class__, 'DURATION', 8.5)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 6: THE PUNCH (39.5–50.4s)
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 10.2
    def construct(self):
        self.add(gradient_bg("#050810"))
        t = 0

        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP * (8 - bh/2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN * (8 - bh/2)),
        )
        self.add(star_field(12, seed=99))

        div1 = section_div(4, MUTED).move_to(UP * 2.5)

        had = safe_text("The last Norse had a choice.", font="DM Serif Display",
                       font_size=42, color=WHITE_SOFT)
        had.move_to(UP * 1.2)

        # The two choices
        div2 = section_div(4, ICE_BLUE).move_to(DOWN * 0.2)

        adapt = safe_text("Adapt and survive,", font="DM Serif Display",
                         font_size=44, color=ICE_BLUE)
        adapt.move_to(DOWN * 1.5)

        div3 = section_div(4, RED).move_to(DOWN * 2.8)

        stay = safe_text("or stay who they were", font="DM Serif Display",
                        font_size=42, color=MUTED)
        stay.move_to(DOWN * 4)
        and_die = safe_text("and die.", font="Bebas Neue", font_size=80, color=RED)
        and_die.move_to(DOWN * 5.2)

        # The answer
        chose = safe_text("They chose to die.", font="Bebas Neue",
                         font_size=80, color=WHITE_SOFT)
        chose.move_to(DOWN * 6.8)

        glow = Circle(radius=2.5, fill_color=WHITE_SOFT, fill_opacity=0.03, stroke_width=0)
        glow.move_to(chose)

        # ── Timing: 10.90s ──
        # VTT 0.62: "The last Norse in Greenland had a choice."
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(had, shift=UP * 0.08), run_time=0.7); t += 0.7
        self.wait(1.94); t += 1.94

        # VTT 3.24: "Adapt and survive,"
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(adapt, shift=UP * 0.06), run_time=0.7); t += 0.7

        # VTT 4.76: "or stay who they were and die."
        self.wait(0.52); t += 0.52
        self.play(Create(div3), run_time=0.3); t += 0.3
        self.play(FadeIn(stay, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(and_die, scale=1.1), run_time=0.6); t += 0.6
        self.play(Flash(and_die.get_center(), color=RED,
                        line_length=0.4, num_lines=8, run_time=0.3))        # t=6.26

        # VTT 6.94: "They chose to die."
        self.wait(0.38); t += 0.38
        self.play(FadeIn(glow), FadeIn(chose, scale=1.08), run_time=0.8); t += 0.8

        # 3s hold + fade
        target = getattr(self.__class__, 'DURATION', 10.2)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5


# ── Infra ─────────────────────────────────────────────────────
def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_Blame, Scene3_Contradiction,
          Scene4_Proof, Scene5_Identity, Scene6_Punch]
    config.output_file = f"greenland_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"greenland_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    sc = [Scene1_Hook, Scene2_Blame, Scene3_Contradiction,
          Scene4_Proof, Scene5_Identity, Scene6_Punch]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(sc):
        n = f"greenland_scene_{i+1}"; print(f"  Preview {n}...")
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

    names = ["Scene1_Hook","Scene2_Blame","Scene3_Contradiction",
             "Scene4_Proof","Scene5_Identity","Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_greenland.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="greenland", audio_path=str(audio))
    final = od / "greenland_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
