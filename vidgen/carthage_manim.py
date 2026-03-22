#!/usr/bin/env python3
"""Carthage — 'Written Over the Dead' (Manim). Roman erasure arc.

6 scenes, ~53.9s (50.9s audio + 3s hold).

VTT cues (absolute → relative):
  Scene 1 (0.0–6.2s = 6.20s):
    0.360 (0.36) Rome destroyed Carthage so completely that
    2.840 (2.84) we only know Carthage through Roman eyes.
  Scene 2 (6.2–13.5s = 7.30s):
    6.240 (0.04) Rome said Carthage was barbaric.
    8.460 (2.26) They sacrificed children.
    10.280 (4.08) They could not be trusted.
    12.020 (5.82) Every Roman schoolboy learned this.
  Scene 3 (13.5–23.6s = 10.10s):
    14.340 (0.84) But Carthage controlled the Mediterranean for 700 years.
    18.720 (5.22) They invented the alphabet we use today.
    21.300 (7.80) Their trade routes reached Britain.
  Scene 4 (23.6–33.2s = 9.60s):
    23.660 (0.06) After the third war,
    25.180 (1.58) Rome burned Carthage for 17 days.
    27.900 (4.30) They sold 50,000 people into slavery.
    30.860 (7.26) Then they plowed the ruins into the earth.
  Scene 5 (33.2–41.6s = 8.40s):
    33.460 (0.26) Rome rewrote every Carthaginian text.
    36.680 (3.48) Every treaty.
    37.680 (4.48) Every history.
    38.740 (5.54) They did not just win the war.
    40.620 (7.42) They won the story.
  Scene 6 (41.6–53.9s = 12.30s):
    42.240 (0.64) Everything you think you know about Carthage
    44.540 (2.94) was written by the people who destroyed it.
    47.040 (5.44) History is not written by the victors.
    49.260 (7.66) It is written over the dead.
    + 3s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """Rome destroyed Carthage so completely that
we only know Carthage through Roman eyes.
Rome said Carthage was barbaric.
They sacrificed children.
They could not be trusted.
Every Roman schoolboy learned this.
But Carthage controlled the Mediterranean for 700 years.
They invented the alphabet we use today.
Their trade routes reached Britain.
After the third war,
Rome burned Carthage for 17 days.
They sold 50,000 people into slavery.
Then they plowed the ruins into the earth.
Rome rewrote every Carthaginian text.
Every treaty.
Every history.
They did not just win the war.
They won the story.
Everything you think you know about Carthage
was written by the people who destroyed it.
History is not written by the victors.
It is written over the dead."""

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
ROME_RED = "#8B0000"; ROME_GOLD = "#DAA520"
ASH = "#6B6B6B"; FLAME = "#FF6B35"
PUNIC = "#D4A574"; PUNIC_DIM = "#A0784A"
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
    DURATION = 5.8
    def construct(self):
        self.add(gradient_bg(g="#1A0A0A"), star_field(20, seed=1))
        t = 0
        pill = label_pill("CARTHAGE", color=PUNIC, fs=26)
        pill.move_to(UP * 7)

        destroyed = safe_text("DESTROYED", font="Bebas Neue", font_size=110, color=RED)
        destroyed.move_to(UP * 4)
        so = safe_text("so completely that", font="DM Serif Display", font_size=44, color=MUTED)
        so.move_to(UP * 2.5)

        div = section_div(5, MUTED).move_to(UP * 1)
        only = safe_text("we only know Carthage", font="DM Serif Display", font_size=44, color=WHITE_SOFT)
        only.move_to(DOWN * 0.3)
        through = safe_text("through Roman eyes.", font="DM Serif Display", font_size=48, color=ROME_RED)
        through.move_to(DOWN * 1.5)

        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(destroyed, scale=1.2), run_time=0.7); t += 0.7
        self.play(Flash(destroyed.get_center(), color=RED, line_length=0.5, num_lines=10, run_time=0.3)); t += 0.3
        self.play(FadeIn(so, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(Create(div), run_time=0.3); t += 0.3
        self.wait(0.44); t += 0.44
        self.play(FadeIn(only, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(through, shift=UP * 0.06), run_time=0.6); t += 0.6
        target = getattr(self.__class__, 'DURATION', 5.8)
        self.wait(max(0.1, target - t - 0.3))


class Scene2_Propaganda(Scene):
    DURATION = 6.9
    def construct(self):
        self.add(gradient_bg(), star_field(12, seed=7))
        t = 0
        pill = label_pill("THE PROPAGANDA", color=ROME_RED, fs=28)
        pill.move_to(UP * 7)

        rome_said = safe_text("ROME SAID:", font="Inter", font_size=32, color=MUTED, weight="BOLD")
        rome_said.move_to(UP * 5.5)

        items = [
            ("BARBARIC.", UP * 3.5, ROME_RED),
            ("CHILD SACRIFICE.", UP * 1.8, RED),
            ("CANNOT BE TRUSTED.", UP * 0.1, RED),
        ]
        item_groups = []
        for txt, pos, col in items:
            lbl = safe_text(txt, font="Bebas Neue", font_size=70, color=col)
            lbl.move_to(pos)
            item_groups.append(lbl)

        div = section_div(5, MUTED).move_to(DOWN * 1.8)
        schoolboy = safe_text("Every Roman schoolboy", font="DM Serif Display", font_size=42, color=MUTED)
        schoolboy.move_to(DOWN * 3)
        learned = safe_text("learned this.", font="DM Serif Display", font_size=46, color=DEAD_GRAY)
        learned.move_to(DOWN * 4.1)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(rome_said), run_time=0.3); t += 0.3
        self.play(FadeIn(item_groups[0], shift=LEFT * 0.1), run_time=0.5); t += 0.5
        self.wait(0.86); t += 0.86
        self.play(FadeIn(item_groups[1], shift=LEFT * 0.1), run_time=0.5); t += 0.5
        self.wait(1.32); t += 1.32
        self.play(FadeIn(item_groups[2], shift=LEFT * 0.1), run_time=0.5); t += 0.5
        self.wait(1.24); t += 1.24
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(schoolboy, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(FadeIn(learned, shift=UP * 0.06), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 6.9)
        self.wait(max(0.1, target - t - 0.3))


class Scene3_Truth(Scene):
    DURATION = 9.5
    def construct(self):
        self.add(gradient_bg(g="#1A1A0A"), star_field(15, seed=13))
        t = 0
        pill = label_pill("THE TRUTH", color=GOLD, fs=28)
        pill.move_to(UP * 7)

        but = safe_text("BUT CARTHAGE", font="Bebas Neue", font_size=80, color=GOLD)
        but.move_to(UP * 5)

        controlled = safe_text("controlled the Mediterranean", font="DM Serif Display", font_size=42, color=WHITE_SOFT)
        controlled.move_to(UP * 3.3)

        big_700 = safe_text("700", font="Bebas Neue", font_size=180, color=GOLD)
        big_700.move_to(UP * 0.5)
        years = safe_text("YEARS", font="Inter", font_size=40, color=WHITE_SOFT, weight="BOLD")
        years.move_to(DOWN * 1.2)

        div1 = section_div(5, PUNIC).move_to(DOWN * 2.5)

        alpha = safe_text("Invented the alphabet", font="DM Serif Display", font_size=44, color=PUNIC)
        alpha.move_to(DOWN * 3.8)
        we_use = safe_text("we use today.", font="DM Serif Display", font_size=44, color=WHITE_SOFT)
        we_use.move_to(DOWN * 4.9)

        div2 = section_div(5, GOLD).move_to(DOWN * 6)
        trade = safe_text("Trade routes reached Britain.", font="DM Serif Display", font_size=40, color=MUTED)
        trade.move_to(DOWN * 7)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.wait(0.24); t += 0.24
        self.play(FadeIn(but, scale=1.1), run_time=0.6); t += 0.6
        self.play(FadeIn(controlled, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(big_700, scale=1.3), run_time=0.7); t += 0.7
        self.play(Flash(big_700.get_center(), color=GOLD, line_length=0.5, num_lines=12, run_time=0.3)); t += 0.3
        self.play(FadeIn(years), run_time=0.4); t += 0.4
        self.wait(1.78); t += 1.78
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(alpha, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(we_use, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.wait(1.18); t += 1.18
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(trade, shift=UP * 0.04), run_time=0.6); t += 0.6
        target = getattr(self.__class__, 'DURATION', 9.5)
        self.wait(max(0.1, target - t - 0.3))


class Scene4_Destruction(Scene):
    DURATION = 9.1
    def construct(self):
        self.add(gradient_bg("#0A0606"), star_field(8, seed=44))
        t = 0
        pill = label_pill("THE DESTRUCTION", color=FLAME, fs=26)
        pill.move_to(UP * 7)

        after = safe_text("AFTER THE THIRD WAR", font="Inter", font_size=28, color=MUTED, weight="BOLD")
        after.move_to(UP * 5.5)

        burned = safe_text("BURNED", font="Bebas Neue", font_size=100, color=FLAME)
        burned.move_to(UP * 3.8)
        days = safe_text("FOR 17 DAYS.", font="Bebas Neue", font_size=80, color=RED)
        days.move_to(UP * 2.3)

        div1 = section_div(5, RED).move_to(UP * 0.8)

        sold = safe_text("50,000", font="Bebas Neue", font_size=120, color=RED)
        sold.move_to(DOWN * 0.8)
        slavery = safe_text("sold into slavery.", font="DM Serif Display", font_size=44, color=WHITE_SOFT)
        slavery.move_to(DOWN * 2.2)

        div2 = section_div(5, ASH).move_to(DOWN * 3.5)
        plowed = safe_text("Then they plowed the ruins", font="DM Serif Display", font_size=40, color=ASH)
        plowed.move_to(DOWN * 4.7)
        earth = safe_text("into the earth.", font="DM Serif Display", font_size=44, color=DEAD_GRAY)
        earth.move_to(DOWN * 5.8)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(after), run_time=0.3); t += 0.3
        self.wait(0.68); t += 0.68
        self.play(FadeIn(burned, scale=1.15), run_time=0.6); t += 0.6
        self.play(FadeIn(days, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(burned.get_center(), color=FLAME, line_length=0.4, num_lines=10, run_time=0.3)); t += 0.3
        self.wait(1.32); t += 1.32
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(sold, scale=1.2), run_time=0.6); t += 0.6
        self.play(Flash(sold.get_center(), color=RED, line_length=0.5, num_lines=10, run_time=0.3)); t += 0.3
        self.play(FadeIn(slavery, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.wait(1.26); t += 1.26
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(plowed, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(earth, shift=UP * 0.06), run_time=0.6); t += 0.6
        target = getattr(self.__class__, 'DURATION', 9.1)
        self.wait(max(0.1, target - t - 0.3))


class Scene5_Erasure(Scene):
    DURATION = 7.9
    def construct(self):
        self.add(gradient_bg(), star_field(10, seed=55))
        t = 0
        pill = label_pill("THE ERASURE", color=MUTED, fs=28)
        pill.move_to(UP * 7)

        rewrote = safe_text("ROME REWROTE", font="Bebas Neue", font_size=80, color=WHITE_SOFT)
        rewrote.move_to(UP * 5)

        items = [
            ("EVERY TEXT.", UP * 3, MUTED),
            ("EVERY TREATY.", UP * 1.5, MUTED),
            ("EVERY HISTORY.", DOWN * 0, DEAD_GRAY),
        ]
        item_groups = []
        for txt, pos, col in items:
            lbl = safe_text(txt, font="Bebas Neue", font_size=70, color=col)
            lbl.move_to(pos)
            item_groups.append(lbl)

        div1 = section_div(5, RED).move_to(DOWN * 1.8)
        not_just = safe_text("They did not just win the war.", font="DM Serif Display", font_size=40, color=MUTED)
        not_just.move_to(DOWN * 3)

        div2 = section_div(5, GOLD).move_to(DOWN * 4.2)
        won = safe_text("THEY WON", font="Bebas Neue", font_size=90, color=GOLD)
        won.move_to(DOWN * 5.5)
        story = safe_text("THE STORY.", font="Bebas Neue", font_size=90, color=GOLD)
        story.move_to(DOWN * 6.8)

        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(rewrote, scale=1.05), run_time=0.6); t += 0.6
        self.wait(2.28); t += 2.28
        self.play(FadeIn(item_groups[0], shift=LEFT * 0.1), run_time=0.5); t += 0.5
        self.wait(0.5); t += 0.5
        self.play(FadeIn(item_groups[1], shift=LEFT * 0.1), run_time=0.5); t += 0.5
        self.wait(0.5); t += 0.5
        self.play(FadeIn(item_groups[2], shift=LEFT * 0.1), run_time=0.5); t += 0.5

        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(not_just, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.wait(0.54); t += 0.54
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(won, scale=1.1), run_time=0.4); t += 0.4
        self.play(FadeIn(story, scale=1.1), run_time=0.4); t += 0.4
        self.play(Flash(story.get_center(), color=GOLD, line_length=0.4, num_lines=8, run_time=0.2)); t += 0.2
        target = getattr(self.__class__, 'DURATION', 7.9)
        self.wait(max(0.1, target - t - 0.3))


class Scene6_Punch(Scene):
    DURATION = 11.6
    def construct(self):
        self.add(gradient_bg("#050508"))
        t = 0
        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1, stroke_width=0).move_to(UP*(8-bh/2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1, stroke_width=0).move_to(DOWN*(8-bh/2)),
        )
        self.add(star_field(12, seed=99))

        div1 = section_div(4, MUTED).move_to(UP * 3)
        everything = safe_text("Everything you think you know", font="DM Serif Display", font_size=38, color=WHITE_SOFT)
        everything.move_to(UP * 1.8)
        about = safe_text("about Carthage", font="DM Serif Display", font_size=40, color=PUNIC)
        about.move_to(UP * 0.7)

        div2 = section_div(4, RED).move_to(DOWN * 0.5)
        written_by = safe_text("was written by the people", font="DM Serif Display", font_size=38, color=MUTED)
        written_by.move_to(DOWN * 1.7)
        who_destroyed = safe_text("who destroyed it.", font="DM Serif Display", font_size=42, color=RED)
        who_destroyed.move_to(DOWN * 2.8)

        div3 = section_div(4, GOLD).move_to(DOWN * 4)
        not_victors = safe_text("History is not written", font="DM Serif Display", font_size=40, color=MUTED)
        not_victors.move_to(DOWN * 5.2)
        by_victors = safe_text("by the victors.", font="DM Serif Display", font_size=42, color=MUTED)
        by_victors.move_to(DOWN * 6)

        over_dead = safe_text("Over the dead.", font="Bebas Neue", font_size=80, color=WHITE_SOFT)
        over_dead.move_to(DOWN * 7.2)
        glow = Circle(radius=2.5, fill_color=WHITE_SOFT, fill_opacity=0.03, stroke_width=0)
        glow.move_to(over_dead)

        # ── Timing: 12.30s ──
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(everything, shift=UP * 0.08), run_time=0.7); t += 0.7
        self.play(FadeIn(about, shift=UP * 0.08), run_time=0.7); t += 0.7
        self.wait(0.94); t += 0.94
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(written_by, shift=UP * 0.06), run_time=0.7); t += 0.7
        self.play(FadeIn(who_destroyed, shift=UP * 0.06), run_time=0.7); t += 0.7
        self.wait(0.8); t += 0.8
        self.play(Create(div3), run_time=0.3); t += 0.3
        self.play(FadeIn(not_victors, shift=UP * 0.06), run_time=0.7); t += 0.7
        self.play(FadeIn(by_victors, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.wait(0.62); t += 0.62
        self.play(FadeIn(glow), FadeIn(over_dead, scale=1.08), run_time=0.9); t += 0.9

        # 3s hold + fade
        target = getattr(self.__class__, 'DURATION', 11.6)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5


# ── Infra ─────────────────────────────────────────────────────
def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_Propaganda, Scene3_Truth,
          Scene4_Destruction, Scene5_Erasure, Scene6_Punch]
    config.output_file = f"carthage_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"carthage_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    sc = [Scene1_Hook, Scene2_Propaganda, Scene3_Truth,
          Scene4_Destruction, Scene5_Erasure, Scene6_Punch]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(sc):
        n = f"carthage_scene_{i+1}"; print(f"  Preview {n}...")
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

    names = ["Scene1_Hook","Scene2_Propaganda","Scene3_Truth",
             "Scene4_Destruction","Scene5_Erasure","Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_carthage.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="carthage", audio_path=str(audio))
    final = od / "carthage_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
