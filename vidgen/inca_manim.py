#!/usr/bin/env python3
"""Inca Empire — 'The Real Killer' (Manim). Conquest/disease revelation.

6 scenes, ~50.0s (47.0s audio + 3s hold).

VTT cues (absolute → relative):
  Scene 1 (0.0–7.8s = 7.80s):
    0.520 (0.52) Francisco Pizarro conquered the Inca Empire with
    3.450 (3.45) 168 men against an army of 80,000.
    7.780 (7.78) Historians said Spanish steel and horses won the battle. [straddles]
  Scene 2 (7.8–14.4s = 6.60s):
    11.620 (3.82) Superior technology against primitive weapons.
  Scene 3 (14.4–22.8s = 8.40s):
    14.380 (0.0)  But 168 men cannot hold an empire of 10 million people.
    19.140 (4.74) Horses do not conquer mountain cities.
    21.560 (7.16) Something else broke the Inca.
  Scene 4 (22.8–32.6s = 9.80s):
    23.620 (0.82) Smallpox reached Peru before Pizarro did.
    26.480 (3.68) It killed the emperor and his heir.
    28.580 (5.78) The empire split into civil war.
    31.020 (8.22) Pizarro walked into the wreckage.
  Scene 5 (32.6–41.2s = 8.60s):
    33.160 (0.56) Within 50 years,
    34.560 (1.96) 90 percent of the Inca population was dead.
    37.480 (4.88) Not from swords.
    38.700 (6.10) From disease the Spanish carried and never saw.
  Scene 6 (41.2–50.0s = 8.80s):
    41.780 (0.58) Pizarro did not defeat the Inca.
    43.940 (2.74) He just showed up after the real killer had already finished.
    + 3s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """Francisco Pizarro conquered the Inca Empire with
168 men against an army of 80,000.
Historians said Spanish steel and horses won the battle. [straddles]
Superior technology against primitive weapons.
But 168 men cannot hold an empire of 10 million people.
Horses do not conquer mountain cities.
Something else broke the Inca.
Smallpox reached Peru before Pizarro did.
It killed the emperor and his heir.
The empire split into civil war.
Pizarro walked into the wreckage.
Within 50 years,
90 percent of the Inca population was dead.
Not from swords.
From disease the Spanish carried and never saw.
Pizarro did not defeat the Inca.
He just showed up after the real killer had already finished."""

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
INCA_GOLD = "#DAA520"; INCA_DIM = "#8B6914"
STEEL = "#B0BEC5"; BLOOD = "#8B0000"
PLAGUE = "#6B8E23"; PLAGUE_DIM = "#4A6118"
SAFE_W = 8.0


def gradient_bg(c=BG, g="#12122A"):
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
    DURATION = 7.3
    def construct(self):
        self.add(gradient_bg(g="#1A1008"), star_field(20, seed=1))
        t = 0
        pill = label_pill("THE INCA EMPIRE", color=INCA_GOLD, fs=24)
        pill.move_to(UP * 7)

        big_168 = safe_text("168", font="Bebas Neue", font_size=180, color=STEEL)
        big_168.move_to(UP * 3.5)
        vs = safe_text("VS", font="Inter", font_size=40, color=MUTED, weight="BOLD")
        vs.move_to(UP * 1.5)
        big_80k = safe_text("80,000", font="Bebas Neue", font_size=140, color=INCA_GOLD)
        big_80k.move_to(DOWN * 0.5)

        div = section_div(5, STEEL).move_to(DOWN * 2.2)
        steel = safe_text("Spanish steel and horses.", font="DM Serif Display",
                         font_size=44, color=STEEL)
        steel.move_to(DOWN * 3.5)
        won = safe_text("That is what they taught.", font="DM Serif Display",
                       font_size=40, color=MUTED)
        won.move_to(DOWN * 4.6)

        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(big_168, scale=1.3), run_time=0.7); t += 0.7
        self.play(Flash(big_168.get_center(), color=STEEL,
                        line_length=0.5, num_lines=10, run_time=0.3))
        self.play(FadeIn(vs), run_time=0.3); t += 0.3
        self.play(FadeIn(big_80k, scale=1.2), run_time=0.7); t += 0.7
        self.play(Flash(big_80k.get_center(), color=INCA_GOLD,
                        line_length=0.5, num_lines=12, run_time=0.3))
        self.wait(1.3); t += 1.3
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(steel, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(won, shift=UP * 0.06), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 7.3)
        self.wait(max(0.1, target - t - 0.3))


class Scene2_Problem(Scene):
    DURATION = 6.2
    def construct(self):
        self.add(gradient_bg(), star_field(12, seed=7))
        t = 0
        pill = label_pill("THE PROBLEM", color=RED, fs=28)
        pill.move_to(UP * 7)

        sup = safe_text("SUPERIOR TECHNOLOGY", font="Bebas Neue", font_size=70, color=STEEL)
        sup.move_to(UP * 5)
        against = safe_text("against primitive weapons.", font="DM Serif Display",
                           font_size=42, color=MUTED)
        against.move_to(UP * 3.5)

        div = section_div(5, RED).move_to(UP * 2)
        but = safe_text("But 168 men cannot hold", font="DM Serif Display",
                       font_size=44, color=WHITE_SOFT)
        but.move_to(UP * 0.7)
        empire = safe_text("an empire of", font="DM Serif Display",
                          font_size=44, color=WHITE_SOFT)
        empire.move_to(DOWN * 0.3)
        ten_m = safe_text("10 MILLION.", font="Bebas Neue", font_size=100, color=RED)
        ten_m.move_to(DOWN * 2)

        div2 = section_div(5, MUTED).move_to(DOWN * 3.5)
        horses = safe_text("Horses do not conquer", font="DM Serif Display",
                          font_size=42, color=MUTED)
        horses.move_to(DOWN * 4.7)
        mountains = safe_text("mountain cities.", font="DM Serif Display",
                             font_size=46, color=DEAD_GRAY)
        mountains.move_to(DOWN * 5.8)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(sup, scale=1.05), run_time=0.6); t += 0.6
        self.play(FadeIn(against, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.wait(0.82); t += 0.82
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(but, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(FadeIn(empire, shift=UP * 0.06), run_time=0.4); t += 0.4
        self.play(FadeIn(ten_m, scale=1.15), run_time=0.6); t += 0.6
        self.play(Flash(ten_m.get_center(), color=RED,
                        line_length=0.4, num_lines=10, run_time=0.3))
        self.wait(0.42); t += 0.42
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(horses, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(FadeIn(mountains, shift=UP * 0.06), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 6.2)
        self.wait(max(0.1, target - t - 0.3))


class Scene3_Crack(Scene):
    DURATION = 7.9
    def construct(self):
        self.add(gradient_bg(g="#0A1A0A"), star_field(15, seed=13))
        t = 0
        pill = label_pill("THE CRACK", color=INCA_GOLD, fs=28)
        pill.move_to(UP * 7)

        cannot = safe_text("168 men cannot hold", font="DM Serif Display",
                          font_size=44, color=WHITE_SOFT)
        cannot.move_to(UP * 5)
        emp = safe_text("an empire of 10 million.", font="DM Serif Display",
                       font_size=44, color=INCA_GOLD)
        emp.move_to(UP * 3.8)

        div1 = section_div(5, MUTED).move_to(UP * 2.2)
        horses2 = safe_text("Horses do not conquer", font="DM Serif Display",
                           font_size=44, color=MUTED)
        horses2.move_to(UP * 0.8)
        mtn = safe_text("mountain cities.", font="DM Serif Display",
                        font_size=46, color=DEAD_GRAY)
        mtn.move_to(DOWN * 0.3)

        div2 = section_div(5, RED).move_to(DOWN * 1.8)

        something = safe_text("SOMETHING ELSE", font="Bebas Neue", font_size=90, color=RED)
        something.move_to(DOWN * 3.2)
        broke = safe_text("broke the Inca.", font="DM Serif Display",
                         font_size=50, color=WHITE_SOFT)
        broke.move_to(DOWN * 4.6)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(cannot, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(emp, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.wait(1.24); t += 1.24
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(horses2, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(mtn, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.wait(1.86); t += 1.86
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(something, scale=1.15), run_time=0.7); t += 0.7
        self.play(Flash(something.get_center(), color=RED,
                        line_length=0.4, num_lines=10, run_time=0.3))
        self.play(FadeIn(broke, shift=UP * 0.06), run_time=0.6); t += 0.6
        target = getattr(self.__class__, 'DURATION', 7.9)
        self.wait(max(0.1, target - t - 0.3))


class Scene4_Truth(Scene):
    DURATION = 9.2
    def construct(self):
        self.add(gradient_bg("#080808"), star_field(8, seed=44))
        t = 0
        pill = label_pill("THE TRUTH", color=PLAGUE, fs=28)
        pill.move_to(UP * 7)

        smallpox = safe_text("SMALLPOX", font="Bebas Neue", font_size=100, color=PLAGUE)
        smallpox.move_to(UP * 5)
        reached = safe_text("reached Peru before Pizarro did.", font="DM Serif Display",
                           font_size=38, color=WHITE_SOFT)
        reached.move_to(UP * 3.3)

        div1 = section_div(5, RED).move_to(UP * 2)
        killed_emp = safe_text("It killed the emperor", font="DM Serif Display",
                              font_size=44, color=RED)
        killed_emp.move_to(UP * 0.8)
        and_heir = safe_text("and his heir.", font="DM Serif Display",
                            font_size=46, color=RED)
        and_heir.move_to(DOWN * 0.2)

        div2 = section_div(5, INCA_GOLD).move_to(DOWN * 1.5)
        civil = safe_text("The empire split", font="DM Serif Display",
                         font_size=44, color=WHITE_SOFT)
        civil.move_to(DOWN * 2.7)
        war = safe_text("into civil war.", font="DM Serif Display",
                       font_size=46, color=INCA_GOLD)
        war.move_to(DOWN * 3.8)

        div3 = section_div(5, MUTED).move_to(DOWN * 5)
        walked = safe_text("Pizarro walked into", font="DM Serif Display",
                          font_size=42, color=MUTED)
        walked.move_to(DOWN * 6.2)
        wreckage = safe_text("the wreckage.", font="Bebas Neue", font_size=70, color=DEAD_GRAY)
        wreckage.move_to(DOWN * 7.2)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.wait(0.22); t += 0.22
        self.play(FadeIn(smallpox, scale=1.15), run_time=0.7); t += 0.7
        self.play(Flash(smallpox.get_center(), color=PLAGUE,
                        line_length=0.5, num_lines=10, run_time=0.3))
        self.play(FadeIn(reached, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.wait(1.28); t += 1.28
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(killed_emp, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(and_heir, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.wait(0.78); t += 0.78
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(civil, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(war, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.wait(1.62); t += 1.62
        self.play(Create(div3), run_time=0.3); t += 0.3
        self.play(FadeIn(walked, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(FadeIn(wreckage, scale=1.05), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 9.2)
        self.wait(max(0.1, target - t - 0.3))


class Scene5_Scale(Scene):
    DURATION = 8.1
    def construct(self):
        self.add(gradient_bg("#0A0808"), star_field(10, seed=55))
        t = 0
        pill = label_pill("THE SCALE", color=RED, fs=28)
        pill.move_to(UP * 7)

        within = safe_text("WITHIN 50 YEARS", font="Inter", font_size=30,
                          color=MUTED, weight="BOLD")
        within.move_to(UP * 5.5)

        ninety = safe_text("90%", font="Bebas Neue", font_size=200, color=RED)
        ninety.move_to(UP * 2.5)
        dead = safe_text("DEAD.", font="Bebas Neue", font_size=90, color=RED)
        dead.move_to(UP * 0.2)

        div1 = section_div(5, STEEL).move_to(DOWN * 1.5)
        not_swords = safe_text("Not from swords.", font="DM Serif Display",
                              font_size=46, color=STEEL)
        not_swords.move_to(DOWN * 2.8)

        strike = Line(not_swords.get_left() + LEFT * 0.2,
                     not_swords.get_right() + RIGHT * 0.2,
                     color=STEEL, stroke_width=3)
        strike.move_to(not_swords)

        div2 = section_div(5, PLAGUE).move_to(DOWN * 4.2)
        disease = safe_text("From disease", font="DM Serif Display",
                           font_size=46, color=WHITE_SOFT)
        disease.move_to(DOWN * 5.4)
        carried = safe_text("the Spanish carried", font="DM Serif Display",
                           font_size=44, color=MUTED)
        carried.move_to(DOWN * 6.4)
        never_saw = safe_text("and never saw.", font="DM Serif Display",
                             font_size=46, color=DEAD_GRAY)
        never_saw.move_to(DOWN * 7.4)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(within), run_time=0.3); t += 0.3
        self.wait(0.96); t += 0.96
        self.play(FadeIn(ninety, scale=1.3), run_time=0.7); t += 0.7
        self.play(Flash(ninety.get_center(), color=RED,
                        line_length=0.6, num_lines=12, run_time=0.3))
        self.play(FadeIn(dead, scale=1.1), run_time=0.5); t += 0.5
        self.wait(1.48); t += 1.48
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(not_swords, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(Create(strike), run_time=0.3); t += 0.3
        self.wait(0.62); t += 0.62
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(disease, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(carried, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(FadeIn(never_saw, shift=UP * 0.06), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 8.1)
        self.wait(max(0.1, target - t - 0.3))


class Scene6_Punch(Scene):
    DURATION = 8.3
    def construct(self):
        self.add(gradient_bg("#050508"))
        t = 0
        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP*(8-bh/2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN*(8-bh/2)),
        )
        self.add(star_field(12, seed=99))

        div1 = section_div(4, MUTED).move_to(UP * 2)
        did_not = safe_text("Pizarro did not", font="DM Serif Display",
                           font_size=44, color=WHITE_SOFT)
        did_not.move_to(UP * 0.8)
        defeat = safe_text("defeat the Inca.", font="DM Serif Display",
                          font_size=46, color=MUTED)
        defeat.move_to(DOWN * 0.2)

        div2 = section_div(4, GOLD).move_to(DOWN * 1.5)
        showed = safe_text("He just showed up", font="DM Serif Display",
                          font_size=42, color=WHITE_SOFT)
        showed.move_to(DOWN * 2.8)
        after = safe_text("after the real killer", font="DM Serif Display",
                         font_size=42, color=MUTED)
        after.move_to(DOWN * 3.9)
        finished = safe_text("had already finished.", font="Bebas Neue",
                            font_size=70, color=GOLD)
        finished.move_to(DOWN * 5.2)
        glow = Circle(radius=2.5, fill_color=GOLD, fill_opacity=0.04, stroke_width=0)
        glow.move_to(finished)

        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(did_not, shift=UP * 0.08), run_time=0.7); t += 0.7
        self.play(FadeIn(defeat, shift=UP * 0.08), run_time=0.6); t += 0.6
        self.wait(0.84); t += 0.84
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(showed, shift=UP * 0.06), run_time=0.7); t += 0.7
        self.play(FadeIn(after, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(glow), FadeIn(finished, scale=1.08), run_time=0.8); t += 0.8
        self.play(Flash(finished.get_center(), color=GOLD,
                        line_length=0.4, num_lines=8, run_time=0.3))
        target = getattr(self.__class__, 'DURATION', 8.3)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5


# ── Infra ─────────────────────────────────────────────────────
def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_Problem, Scene3_Crack,
          Scene4_Truth, Scene5_Scale, Scene6_Punch]
    config.output_file = f"inca_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"inca_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    sc = [Scene1_Hook, Scene2_Problem, Scene3_Crack,
          Scene4_Truth, Scene5_Scale, Scene6_Punch]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(sc):
        n = f"inca_scene_{i+1}"; print(f"  Preview {n}...")
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

    names = ["Scene1_Hook","Scene2_Problem","Scene3_Crack",
             "Scene4_Truth","Scene5_Scale","Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_inca.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="inca", audio_path=str(audio))
    final = od / "inca_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
