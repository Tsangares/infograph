#!/usr/bin/env python3
"""Khmer Empire — Angkor Wat (Manim). Water infrastructure collapse arc.

6 scenes, ~52.7s (49.7s audio + 3s hold).

VTT cues (absolute → relative):
  Scene 1 (0.0–6.7s = 6.70s):
    0.200 (0.20) Angkor Wat was the largest city on Earth.
    3.420 (3.42) Then the jungle swallowed it for 400 years.
  Scene 2 (6.7–14.7s = 8.00s):
    6.700 (0.00) Historians said the Thai army sacked it in 1431.
    11.560 (4.86) The city was abandoned.
  Scene 3 (14.7–22.5s = 7.80s):
    12.980 (-1.72→0.0 padded) But Angkor was not just a city.
    15.000 (0.30) It was an engineering system.
    16.800 (2.10) A thousand reservoirs.
    18.540 (3.84) Canals longer than rivers.
    20.120 (5.42) It controlled every drop of monsoon water.
  Scene 4 (22.5–31.5s = 9.00s):
    23.140 (0.64) NASA satellite scans showed it.
    25.120 (2.62) The canal network failed.
    26.680 (4.18) Two mega droughts.
    27.800 (5.30) Then a mega flood.
    29.160 (6.66) The water system that built the empire destroyed it.
  Scene 5 (31.5–41.1s = 9.60s):
    32.180 (0.68) At its peak, Angkor held 750,000 people.
    36.360 (4.86) Bigger than London.
    37.280 (5.78) The most complex water system built before the industrial age.
    40.800 (9.30) Gone.
  Scene 6 (41.1–52.7s = 11.60s):
    41.540 (0.44) The Khmer did not lose a war.
    43.660 (2.56) They built the most advanced infrastructure on Earth.
    46.620 (5.52) And when the climate changed,
    48.120 (7.02) it became the thing that killed them.
    + 3s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """Angkor Wat was the largest city on Earth.
Then the jungle swallowed it for 400 years.
Historians said the Thai army sacked it in 1431.
The city was abandoned.
It was an engineering system.
A thousand reservoirs.
Canals longer than rivers.
It controlled every drop of monsoon water.
NASA satellite scans showed it.
The canal network failed.
Two mega droughts.
Then a mega flood.
The water system that built the empire destroyed it.
At its peak, Angkor held 750,000 people.
Bigger than London.
The most complex water system built before the industrial age.
Gone.
The Khmer did not lose a war.
They built the most advanced infrastructure on Earth.
And when the climate changed,
it became the thing that killed them."""

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
WATER = "#3498DB"; WATER_DIM = "#2471A3"; WATER_DARK = "#1A5276"
JUNGLE = "#27AE60"; JUNGLE_DIM = "#1E8449"
STONE = "#A0937D"; STONE_DIM = "#7D7163"
SAFE_W = 8.0


def gradient_bg(c=BG, g="#0A1A20"):
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


class Scene1_Hook(Scene):
    DURATION = 6.3
    def construct(self):
        self.add(gradient_bg(g="#0A1A10"), star_field(20, seed=1))
        t = 0
        pill = label_pill("ANGKOR WAT", color=STONE, fs=26)
        pill.move_to(UP * 7)

        largest = safe_text("THE LARGEST CITY", font="Bebas Neue", font_size=80, color=GOLD)
        largest.move_to(UP * 4.5)
        on_earth = safe_text("ON EARTH.", font="Bebas Neue", font_size=90, color=GOLD)
        on_earth.move_to(UP * 3)

        div = section_div(5, JUNGLE).move_to(UP * 1.5)
        jungle = safe_text("The jungle swallowed it", font="DM Serif Display", font_size=44, color=JUNGLE)
        jungle.move_to(UP * 0.2)

        big_400 = safe_text("400", font="Bebas Neue", font_size=180, color=JUNGLE)
        big_400.move_to(DOWN * 2.5)
        yrs = safe_text("YEARS", font="Inter", font_size=40, color=WHITE_SOFT, weight="BOLD")
        yrs.move_to(DOWN * 4.2)

        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(largest, scale=1.1), run_time=0.6); t += 0.6
        self.play(FadeIn(on_earth, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(on_earth.get_center(), color=GOLD, line_length=0.5, num_lines=10, run_time=0.3)); t += 0.3
        self.play(Create(div), run_time=0.3); t += 0.3
        self.wait(0.82); t += 0.82
        self.play(FadeIn(jungle, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(big_400, scale=1.3), run_time=0.7); t += 0.7
        self.play(Flash(big_400.get_center(), color=JUNGLE, line_length=0.5, num_lines=10, run_time=0.3)); t += 0.3
        self.play(FadeIn(yrs), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 6.3)
        self.wait(max(0.1, target - t - 0.3))


class Scene2_Blame(Scene):
    DURATION = 7.5
    def construct(self):
        self.add(gradient_bg(), star_field(12, seed=7))
        t = 0
        pill = label_pill("THE BLAME", color=RED, fs=28)
        pill.move_to(UP * 7)

        thai = safe_text("THE THAI ARMY", font="Bebas Neue", font_size=80, color=RED)
        thai.move_to(UP * 5)
        sacked = safe_text("sacked it in 1431.", font="DM Serif Display", font_size=46, color=WHITE_SOFT)
        sacked.move_to(UP * 3.5)
        khmer = safe_text("The Khmer fled.", font="DM Serif Display", font_size=44, color=MUTED)
        khmer.move_to(UP * 2.2)

        div = section_div(5, DEAD_GRAY).move_to(UP * 0.8)
        abandoned = safe_text("ABANDONED.", font="Bebas Neue", font_size=100, color=DEAD_GRAY)
        abandoned.move_to(DOWN * 0.8)
        thats = safe_text("That is the textbook story.", font="DM Serif Display", font_size=40, color=DEAD_GRAY)
        thats.move_to(DOWN * 2.2)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(thai, scale=1.1), run_time=0.6); t += 0.6
        self.play(FadeIn(sacked, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(FadeIn(khmer, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.wait(2.56); t += 2.56
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(abandoned, scale=1.1), run_time=0.6); t += 0.6
        self.play(Flash(abandoned.get_center(), color=DEAD_GRAY, line_length=0.3, num_lines=8, run_time=0.3)); t += 0.3
        self.play(FadeIn(thats, shift=UP * 0.04), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 7.5)
        self.wait(max(0.1, target - t - 0.3))


class Scene3_Truth(Scene):
    DURATION = 7.3
    def construct(self):
        self.add(gradient_bg(g="#0A1520"), star_field(15, seed=13))
        t = 0
        pill = label_pill("THE TRUTH", color=WATER, fs=28)
        pill.move_to(UP * 7)

        not_just = safe_text("NOT JUST A CITY.", font="Bebas Neue", font_size=80, color=WATER)
        not_just.move_to(UP * 5)
        eng = safe_text("An engineering system.", font="DM Serif Display", font_size=46, color=WHITE_SOFT)
        eng.move_to(UP * 3.5)

        items = [
            ("1,000 RESERVOIRS", UP * 1.5, WATER),
            ("CANALS LONGER THAN RIVERS", DOWN * 0, WATER_DIM),
        ]
        item_groups = []
        for txt, pos, col in items:
            lbl = safe_text(txt, font="Bebas Neue", font_size=60, color=col)
            lbl.move_to(pos)
            item_groups.append(lbl)

        div = section_div(5, WATER).move_to(DOWN * 1.8)
        controlled = safe_text("Controlled every drop", font="DM Serif Display", font_size=44, color=WHITE_SOFT)
        controlled.move_to(DOWN * 3)
        monsoon = safe_text("of monsoon water.", font="DM Serif Display", font_size=46, color=WATER)
        monsoon.move_to(DOWN * 4.1)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(not_just, scale=1.1), run_time=0.6); t += 0.6
        self.play(Flash(not_just.get_center(), color=WATER, line_length=0.4, num_lines=8, run_time=0.3)); t += 0.3
        self.play(FadeIn(eng, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.wait(0.8); t += 0.8
        self.play(FadeIn(item_groups[0], shift=LEFT * 0.1), run_time=0.5); t += 0.5
        self.wait(1.04); t += 1.04
        self.play(FadeIn(item_groups[1], shift=LEFT * 0.1), run_time=0.5); t += 0.5
        self.wait(1.28); t += 1.28
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(controlled, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(monsoon, shift=UP * 0.06), run_time=0.6); t += 0.6
        target = getattr(self.__class__, 'DURATION', 7.3)
        self.wait(max(0.1, target - t - 0.3))


class Scene4_Collapse(Scene):
    DURATION = 8.5
    def construct(self):
        self.add(gradient_bg("#080808"), star_field(8, seed=44))
        t = 0
        pill = label_pill("THE COLLAPSE", color=RED, fs=28)
        pill.move_to(UP * 7)

        nasa = safe_text("NASA SATELLITE SCANS", font="Inter", font_size=28, color=MUTED, weight="BOLD")
        nasa.move_to(UP * 5.5)
        showed = safe_text("showed it.", font="DM Serif Display", font_size=46, color=WHITE_SOFT)
        showed.move_to(UP * 4.3)

        div1 = section_div(5, RED).move_to(UP * 3)
        failed = safe_text("THE CANAL NETWORK", font="Bebas Neue", font_size=70, color=RED)
        failed.move_to(UP * 1.8)
        failed2 = safe_text("FAILED.", font="Bebas Neue", font_size=90, color=RED)
        failed2.move_to(UP * 0.4)

        items = [
            ("TWO MEGA DROUGHTS.", DOWN * 1.5, GOLD_DIM),
            ("THEN A MEGA FLOOD.", DOWN * 3, WATER),
        ]
        item_groups = []
        for txt, pos, col in items:
            lbl = safe_text(txt, font="Bebas Neue", font_size=60, color=col)
            lbl.move_to(pos)
            item_groups.append(lbl)

        div2 = section_div(5, MUTED).move_to(DOWN * 4.5)
        water_sys = safe_text("The water system that built", font="DM Serif Display", font_size=38, color=MUTED)
        water_sys.move_to(DOWN * 5.7)
        destroyed = safe_text("the empire destroyed it.", font="DM Serif Display", font_size=40, color=RED)
        destroyed.move_to(DOWN * 6.8)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.wait(0.04); t += 0.04
        self.play(FadeIn(nasa), run_time=0.3); t += 0.3
        self.play(FadeIn(showed, shift=UP * 0.04), run_time=0.4); t += 0.4
        self.wait(1.28); t += 1.28
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(failed, scale=1.05), run_time=0.5); t += 0.5
        self.play(FadeIn(failed2, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(failed2.get_center(), color=RED, line_length=0.4, num_lines=10, run_time=0.3)); t += 0.3
        self.wait(0.78); t += 0.78
        self.play(FadeIn(item_groups[0], shift=LEFT * 0.1), run_time=0.5); t += 0.5
        self.wait(0.62); t += 0.62
        self.play(FadeIn(item_groups[1], shift=LEFT * 0.1), run_time=0.5); t += 0.5
        self.wait(1.06); t += 1.06
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(water_sys, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(destroyed, shift=UP * 0.06), run_time=0.6); t += 0.6
        target = getattr(self.__class__, 'DURATION', 8.5)
        self.wait(max(0.1, target - t - 0.3))


class Scene5_Scale(Scene):
    DURATION = 9.0
    def construct(self):
        self.add(gradient_bg(g="#0A1A10"), star_field(10, seed=55))
        t = 0
        pill = label_pill("THE SCALE", color=GOLD, fs=28)
        pill.move_to(UP * 7)

        at_peak = safe_text("AT ITS PEAK", font="Inter", font_size=28, color=MUTED, weight="BOLD")
        at_peak.move_to(UP * 5.5)

        big_750 = safe_text("750,000", font="Bebas Neue", font_size=140, color=GOLD)
        big_750.move_to(UP * 3.5)
        people = safe_text("PEOPLE", font="Inter", font_size=40, color=WHITE_SOFT, weight="BOLD")
        people.move_to(UP * 1.8)

        div1 = section_div(5, STONE).move_to(UP * 0.5)
        bigger = safe_text("Bigger than London.", font="DM Serif Display", font_size=46, color=STONE)
        bigger.move_to(DOWN * 0.8)

        div2 = section_div(5, WATER).move_to(DOWN * 2)
        most = safe_text("The most complex water system", font="DM Serif Display", font_size=36, color=WATER)
        most.move_to(DOWN * 3.2)
        before = safe_text("built before the industrial age.", font="DM Serif Display", font_size=36, color=MUTED)
        before.move_to(DOWN * 4.2)

        div3 = section_div(5, RED).move_to(DOWN * 5.5)
        gone = safe_text("GONE.", font="Bebas Neue", font_size=120, color=RED)
        gone.move_to(DOWN * 6.8)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(at_peak), run_time=0.3); t += 0.3
        self.play(FadeIn(big_750, scale=1.3), run_time=0.7); t += 0.7
        self.play(Flash(big_750.get_center(), color=GOLD, line_length=0.5, num_lines=12, run_time=0.3)); t += 0.3
        self.play(FadeIn(people), run_time=0.3); t += 0.3
        self.wait(2.86); t += 2.86
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(bigger, shift=UP * 0.04), run_time=0.5); t += 0.5
        self.wait(0.58); t += 0.58
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(most, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(before, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.wait(1.0); t += 1.0
        self.play(Create(div3), run_time=0.3); t += 0.3
        self.play(FadeIn(gone, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(gone.get_center(), color=RED, line_length=0.5, num_lines=10, run_time=0.3)); t += 0.3
        target = getattr(self.__class__, 'DURATION', 9.0)
        self.wait(max(0.1, target - t - 0.3))


class Scene6_Punch(Scene):
    DURATION = 10.9
    def construct(self):
        self.add(gradient_bg("#050508"))
        t = 0
        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1, stroke_width=0).move_to(UP*(8-bh/2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1, stroke_width=0).move_to(DOWN*(8-bh/2)),
        )
        self.add(star_field(12, seed=99))

        div1 = section_div(4, MUTED).move_to(UP * 2.5)
        did_not = safe_text("The Khmer did not", font="DM Serif Display", font_size=44, color=WHITE_SOFT)
        did_not.move_to(UP * 1.2)
        lose = safe_text("lose a war.", font="DM Serif Display", font_size=46, color=MUTED)
        lose.move_to(UP * 0.1)

        div2 = section_div(4, GOLD).move_to(DOWN * 1.2)
        built = safe_text("They built the most advanced", font="DM Serif Display", font_size=38, color=WHITE_SOFT)
        built.move_to(DOWN * 2.4)
        infra = safe_text("infrastructure on Earth.", font="DM Serif Display", font_size=40, color=GOLD)
        infra.move_to(DOWN * 3.4)

        div3 = section_div(4, RED).move_to(DOWN * 4.6)
        climate = safe_text("And when the climate changed,", font="DM Serif Display", font_size=38, color=MUTED)
        climate.move_to(DOWN * 5.8)
        killed = safe_text("it became the thing", font="DM Serif Display", font_size=40, color=WHITE_SOFT)
        killed.move_to(DOWN * 6.8)
        them = safe_text("that killed them.", font="Bebas Neue", font_size=70, color=RED)
        them.move_to(DOWN * 7.8)
        glow = Circle(radius=2.5, fill_color=RED, fill_opacity=0.04, stroke_width=0)
        glow.move_to(them)

        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(did_not, shift=UP * 0.08), run_time=0.7); t += 0.7
        self.play(FadeIn(lose, shift=UP * 0.08), run_time=0.6); t += 0.6
        self.wait(0.86); t += 0.86
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(built, shift=UP * 0.06), run_time=0.7); t += 0.7
        self.play(FadeIn(infra, shift=UP * 0.06), run_time=0.7); t += 0.7
        self.wait(1.62); t += 1.62
        self.play(Create(div3), run_time=0.3); t += 0.3
        self.play(FadeIn(climate, shift=UP * 0.06), run_time=0.7); t += 0.7
        self.wait(0.72); t += 0.72
        self.play(FadeIn(killed, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(glow), FadeIn(them, scale=1.08), run_time=0.8); t += 0.8
        self.play(Flash(them.get_center(), color=RED, line_length=0.4, num_lines=8, run_time=0.3)); t += 0.3
        target = getattr(self.__class__, 'DURATION', 10.9)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5


# ── Infra ─────────────────────────────────────────────────────
def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_Blame, Scene3_Truth,
          Scene4_Collapse, Scene5_Scale, Scene6_Punch]
    config.output_file = f"khmer_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"khmer_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    sc = [Scene1_Hook, Scene2_Blame, Scene3_Truth,
          Scene4_Collapse, Scene5_Scale, Scene6_Punch]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(sc):
        n = f"khmer_scene_{i+1}"; print(f"  Preview {n}...")
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
             "Scene4_Collapse","Scene5_Scale","Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_khmer.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="khmer", audio_path=str(audio))
    final = od / "khmer_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
