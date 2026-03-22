#!/usr/bin/env python3
"""Thomas Midgley Jr. v3 — using anim_assets library.

Compound animations: person_sequence_die, coverup_sequence, ozone_hole, etc.
6 scenes, ~47.8s (44.8s audio + 3s hold). Visual-first, minimal text.
"""

import os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from manim import *
from anim_primitives import (
    headline, big_number_reveal, divider, scene_label, flash_transition,
    fact_callout, load_svg, safe_text,
    TKK_BG, TKK_RED, TKK_GOLD, TKK_WHITE, TKK_DIM, TKK_MUTED, TKK_ACCENT,
)
from anim_assets import (
    person_grid, person_grid_poison, person_sequence_die,
    warning_pulse, ozone_hole,
    stamp_slam, award_reveal, coverup_sequence,
    make_person,
)

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.frame_width = 9
config.frame_height = 16
config.background_color = TKK_BG
config.disable_caching = True


# ================================================================
# SCENE 1: HOOK (0.0–5.6s)
# ================================================================
class Scene1_Hook(Scene):
    def construct(self):
        lbl = scene_label("THOMAS MIDGLEY JR.", color=TKK_ACCENT)
        self.add(lbl)  # INSTANT

        # big_number_reveal — instant, no sentence text
        reveal = big_number_reveal("1", label_below="MAN",
                                   number_color=TKK_RED, number_size=220,
                                   label_color=TKK_WHITE, label_size=60)
        reveal.move_to(UP * 1.5)
        self.play(FadeIn(reveal, scale=1.15), run_time=0.3)
        self.play(Flash(reveal[0].get_center(), color=TKK_RED,
                        line_length=0.7, num_lines=14, run_time=0.3))

        # warning_pulse behind
        warn = warning_pulse(self, position=UP * 1.5, scale=5, color=TKK_RED, pulses=2)

        # Skull icon below
        try:
            skull = load_svg("skull.svg", color=TKK_RED, height=2.5)
        except FileNotFoundError:
            skull = Circle(radius=1, color=TKK_RED, stroke_width=2)
        skull.set_opacity(0.25).move_to(DOWN * 4)
        self.play(FadeIn(skull, scale=0.8), run_time=0.4)
        self.wait(2.0)  # t≈5.6


# ================================================================
# SCENE 2: FIRST INVENTION (5.6–13.6s = 8.0s)
# ================================================================
class Scene2_FirstInvention(Scene):
    def construct(self):
        lbl = scene_label("1921", color=TKK_GOLD)
        self.add(lbl)

        # Headline
        name = headline("THOMAS MIDGLEY", color=TKK_WHITE, size=55)
        name.move_to(UP * 5.5)
        d = divider(color=TKK_GOLD)
        d.move_to(UP * 4.2)

        self.play(FadeIn(name, shift=UP * 0.06), run_time=0.5)
        self.play(Create(d), run_time=0.3)

        self.wait(2.9)  # wait for VTT "hallucinating" @ ~10.08

        # person_sequence_die — compound animation
        person_sequence_die(
            self, count=3,
            position=UP * 1,
            spacing=2.0,
            labels=["HALLUCINATING", "CONVULSING", "DYING"],
            label_colors=[TKK_WHITE, TKK_WHITE, TKK_RED],
        )

        self.wait(0.5)  # t≈8.0


# ================================================================
# SCENE 3: COVERUP (13.6–23.1s = 9.5s)
# ================================================================
class Scene3_Coverup(Scene):
    def construct(self):
        lbl = scene_label("THE COVERUP", color=TKK_ACCENT)
        self.add(lbl)

        # coverup_sequence — person at podium → stamp SAFE → disappear
        self.wait(0.3)
        group, s = coverup_sequence(self, "SAFE", "1 YEAR", position=UP * 1)

        # Divider
        d = divider(color=TKK_RED)
        d.move_to(DOWN * 2)
        self.play(Create(d), run_time=0.3)

        # big_number_reveal for "1 YEAR" recovery
        fc = fact_callout("1", "YEAR", "", number_color=TKK_RED)
        fc.move_to(DOWN * 4)
        self.play(FadeIn(fc[0], scale=1.2), run_time=0.5)
        self.play(Flash(fc[0][0].get_center(), color=TKK_RED,
                        line_length=0.3, num_lines=6, run_time=0.3))

        self.wait(5.5)  # t≈9.5


# ================================================================
# SCENE 4: SECOND INVENTION (23.1–29.8s = 6.7s)
# ================================================================
class Scene4_SecondInvention(Scene):
    def construct(self):
        lbl = scene_label("NOT DONE", color=TKK_ACCENT)
        self.add(lbl)

        self.wait(0.5)

        # headline("FREON")
        freon = headline("FREON", color=TKK_GOLD, size=120)
        freon.move_to(UP * 5.5)
        self.play(FadeIn(freon, scale=1.3), run_time=0.5)
        self.play(Flash(freon.get_center(), color=TKK_GOLD,
                        line_length=0.5, num_lines=12, run_time=0.3))

        self.wait(1.0)

        # ozone_hole — Earth with hole tearing open
        ozone = ozone_hole(self, position=UP * 0.5, radius=2.5)

        # warning_pulse below
        warn = warning_pulse(self, position=DOWN * 4, scale=2, color=TKK_RED, pulses=1)

        self.wait(1.8)  # t≈6.7


# ================================================================
# SCENE 5: SCALE (29.8–38.4s = 8.6s)
# ================================================================
class Scene5_Scale(Scene):
    def construct(self):
        lbl = scene_label("THE SCALE", color=TKK_ACCENT)
        self.add(lbl)

        # person_grid — 54 people in top half
        grid = person_grid(rows=6, cols=9, height=0.55, spacing=0.1)
        grid.move_to(UP * 4)
        self.play(FadeIn(grid), run_time=0.5)
        self.wait(0.3)

        # person_grid_poison — all turn red
        person_grid_poison(self, grid, stagger=0.02, color=TKK_RED)

        # big_number_reveal "70 YEARS"
        d1 = divider(color=TKK_RED)
        d1.move_to(DOWN * 0.5)
        self.play(Create(d1), run_time=0.3)

        big70 = big_number_reveal("70", label_below="YEARS",
                                  number_color=TKK_RED, number_size=130,
                                  label_color=TKK_WHITE, label_size=50)
        big70.move_to(DOWN * 2.5)
        self.play(FadeIn(big70, scale=1.2), run_time=0.5)
        self.play(Flash(big70[0].get_center(), color=TKK_RED,
                        line_length=0.5, num_lines=10, run_time=0.3))

        # "One man, two inventions"
        self.wait(1.5)
        d2 = divider(color=TKK_GOLD)
        d2.move_to(DOWN * 5)
        self.play(Create(d2), run_time=0.3)

        one_two = big_number_reveal("1", label_above="ONE MAN",
                                    label_below="TWO INVENTIONS",
                                    number_color=TKK_RED, number_size=90,
                                    label_color=TKK_WHITE, label_size=32)
        one_two.move_to(DOWN * 6.5)
        self.play(FadeIn(one_two, scale=1.1), run_time=0.5)
        self.play(Flash(one_two[1].get_center(), color=TKK_RED,
                        line_length=0.3, num_lines=8, run_time=0.3))
        self.wait(0.7)  # t≈8.6


# ================================================================
# SCENE 6: PUNCH (38.4–47.8s = 9.4s)
# ================================================================
class Scene6_Punch(Scene):
    def construct(self):
        # Letterbox
        top = Rectangle(width=12, height=1.2, fill_color=BLACK, fill_opacity=1,
                        stroke_width=0).to_edge(UP, buff=0)
        bot = Rectangle(width=12, height=1.2, fill_color=BLACK, fill_opacity=1,
                        stroke_width=0).to_edge(DOWN, buff=0)
        self.play(FadeIn(top), FadeIn(bot), run_time=0.4)

        d1 = divider(color=TKK_DIM)
        d1.move_to(UP * 2)
        self.play(Create(d1), run_time=0.3)

        # "ORGANISM" — the word
        organism = headline("ORGANISM", color=TKK_WHITE, size=90)
        organism.move_to(UP * 0.3)
        self.play(FadeIn(organism, scale=1.08), run_time=0.8)
        self.play(Flash(organism.get_center(), color=TKK_WHITE,
                        line_length=0.4, num_lines=10, run_time=0.3))

        self.wait(2.5)

        d2 = divider(color=TKK_RED)
        d2.move_to(DOWN * 1.5)
        self.play(Create(d2), run_time=0.3)

        # award_reveal — two trophies (the irony)
        awards = award_reveal(self, position=DOWN * 3.5, count=2, color=TKK_GOLD)

        # 3s hold + fade
        self.wait(2.0)
        black = Rectangle(width=12, height=20, fill_color=BLACK,
                          fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5)  # t≈9.4


# ── Infra ─────────────────────────────────────────────────────
SCENES = [Scene1_Hook, Scene2_FirstInvention, Scene3_Coverup,
          Scene4_SecondInvention, Scene5_Scale, Scene6_Punch]

def render_single_scene(idx):
    config.output_file = f"midgley_v3_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    SCENES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"midgley_v3_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENES):
        n = f"midgley_v3_scene_{i+1}"; print(f"  Preview {n}...")
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
        render_single_scene(int(sys.argv[sys.argv.index("--scene")+1])); sys.exit(0)

    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_midgley.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="midgley_v3", audio_path=str(audio))
    final = od / "midgley_v3_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
