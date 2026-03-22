#!/usr/bin/env python3
"""Thomas Midgley Jr. v2 — VISUAL-FIRST. Minimal text, animated SVG icons.

Voice carries narration. Visuals SHOW the story. Text only for numbers/names.
6 scenes, ~47.8s (44.8s audio + 3s hold).
"""

import os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from manim import *
from anim_primitives import *

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.frame_width = 9
config.frame_height = 16
config.background_color = TKK_BG
config.disable_caching = True

SVG = "svg_assets/downloaded"


# ================================================================
# SCENE 1: THE HOOK (0.0–5.6s)
# Voice: "One man caused more environmental damage than any organism..."
# Visual: Giant "1" with warning icon pulsing. NO sentence text.
# ================================================================
class Scene1_Hook(Scene):
    def construct(self):
        # INSTANT — visible from frame 1
        lbl = scene_label("THOMAS MIDGLEY JR.", color=TKK_ACCENT)
        self.add(lbl)

        # Warning icon pulsing behind
        warn = load_svg("warning.svg", color=TKK_RED, height=6)
        warn.set_opacity(0.08).move_to(UP * 2)
        self.add(warn)

        # Big "1 MAN" — the only text
        reveal = big_number_reveal("1", label_below="MAN",
                                   number_color=TKK_RED, number_size=220,
                                   label_color=TKK_WHITE, label_size=60)
        reveal.move_to(UP * 1.5)
        self.play(FadeIn(reveal, scale=1.15), run_time=0.3)               # t=0.3
        self.play(Flash(reveal[0].get_center(), color=TKK_RED,
                        line_length=0.7, num_lines=14, run_time=0.3))      # t=0.6

        # Warning pulses
        self.play(warn.animate.set_opacity(0.15), run_time=0.4)           # t=1.0
        self.play(warn.animate.set_opacity(0.06), run_time=0.4)           # t=1.4

        # Skull icon fades in below — "organism" visual
        skull = load_svg("skull.svg", color=TKK_RED, height=2.5)
        skull.set_opacity(0.3).move_to(DOWN * 4)
        self.play(FadeIn(skull, scale=0.8), run_time=0.5)                 # t=1.9

        # Second pulse
        self.play(warn.animate.set_opacity(0.12), run_time=0.4)           # t=2.3
        self.play(warn.animate.set_opacity(0.05), run_time=0.4)           # t=2.7
        self.wait(2.9)                                                      # t=5.6


# ================================================================
# SCENE 2: FIRST INVENTION (5.6–13.6s = 8.0s)
# Voice: "1921... Thomas Midgley... lead to gasoline... hallucinating, convulsing, dying"
# Visual: Factory + person icons that shake, turn red, disappear
# ================================================================
class Scene2_FirstInvention(Scene):
    def construct(self):
        lbl = scene_label("1921", color=TKK_GOLD)
        self.add(lbl)

        # Factory icon
        factory = load_svg("factory.svg", color=TKK_DIM, height=4)
        factory.move_to(UP * 4)

        # Name — only text besides year
        name = headline("THOMAS MIDGLEY", color=TKK_WHITE, size=50)
        name.move_to(UP * 1)

        # 5 worker person icons
        workers = VGroup()
        for i in range(5):
            p = load_svg("person.svg", color=TKK_WHITE, height=1.5)
            p.move_to(LEFT * 2.5 + RIGHT * i * 1.25 + DOWN * 2)
            workers.add(p)

        d = divider(color=TKK_GOLD)
        d.move_to(DOWN * 0.2)

        self.play(FadeIn(factory, scale=0.9), run_time=0.5)               # t=0.5
        self.play(FadeIn(name, shift=UP * 0.06), run_time=0.5)            # t=1.0
        self.play(Create(d), run_time=0.3)                                 # t=1.3
        self.play(
            LaggedStart(*[FadeIn(w, shift=UP * 0.2) for w in workers], lag_ratio=0.06),
            run_time=0.5,
        )                                                                   # t=1.8

        self.wait(2.7)                                                      # t=4.5

        # VTT "hallucinating" @10.08-5.6=4.48 — workers start shaking
        for w in workers:
            w.generate_target()
            w.target.shift(RIGHT * 0.1 + UP * 0.05)
        self.play(*[MoveToTarget(w) for w in workers], run_time=0.1)
        for w in workers:
            w.generate_target()
            w.target.shift(LEFT * 0.2 + DOWN * 0.1)
        self.play(*[MoveToTarget(w) for w in workers], run_time=0.1)
        for w in workers:
            w.generate_target()
            w.target.shift(RIGHT * 0.1 + UP * 0.05)
        self.play(*[MoveToTarget(w) for w in workers], run_time=0.1)       # t=4.8

        # VTT "convulsing" @11.94-5.6=6.34 — turn red
        self.wait(1.24)                                                     # t=6.04
        self.play(*[w.animate.set_color(TKK_RED) for w in workers], run_time=0.3)  # t=6.34

        # VTT "dying" @12.62-5.6=7.02 — disappear one by one
        self.wait(0.38)                                                     # t=6.72
        self.play(workers[0].animate.shift(DOWN * 2).set_opacity(0), run_time=0.2)
        self.play(workers[1].animate.shift(DOWN * 2).set_opacity(0), run_time=0.15)
        self.play(workers[2].animate.shift(DOWN * 2).set_opacity(0), run_time=0.15)
        self.play(workers[3].animate.shift(DOWN * 2).set_opacity(0), run_time=0.15)
        self.play(workers[4].animate.shift(DOWN * 2).set_opacity(0), run_time=0.15)  # t=7.52
        self.wait(0.48)                                                     # t=8.0


# ================================================================
# SCENE 3: THE COVERUP (13.6–23.1s = 9.5s)
# Voice: "press conference... washed hands... safe... disappeared for a year"
# Visual: Person at podium → stamp("SAFE") → person fades → "1 YEAR"
# ================================================================
class Scene3_Coverup(Scene):
    def construct(self):
        lbl = scene_label("THE COVERUP", color=TKK_ACCENT)
        self.add(lbl)

        # Person icon at podium
        podium = Rectangle(width=2, height=1.2, fill_color="#2A2A3A", fill_opacity=0.8,
                           stroke_color=TKK_DIM, stroke_width=1.5)
        podium.move_to(UP * 2.5)
        person = load_svg("person.svg", color=TKK_WHITE, height=2.5)
        person.move_to(UP * 4.5)

        # Two hand shapes (simple rectangles) for washing motion
        hand_l = Rectangle(width=0.4, height=0.6, fill_color=TKK_DIM, fill_opacity=0.6,
                           stroke_width=0).move_to(UP * 2.5 + LEFT * 0.3)
        hand_r = Rectangle(width=0.4, height=0.6, fill_color=TKK_DIM, fill_opacity=0.6,
                           stroke_width=0).move_to(UP * 2.5 + RIGHT * 0.3)

        d = divider(color=TKK_DIM)
        d.move_to(UP * 0.5)

        self.play(FadeIn(podium), FadeIn(person, shift=DOWN * 0.2), run_time=0.5)  # t=0.5
        self.wait(1.2)                                                      # t=1.7

        # VTT "Washed his hands" @15.3-13.6=1.7
        self.play(FadeIn(hand_l), FadeIn(hand_r), run_time=0.2)           # t=1.9
        # Washing motion
        self.play(hand_l.animate.shift(RIGHT * 0.3), hand_r.animate.shift(LEFT * 0.3),
                  run_time=0.2)
        self.play(hand_l.animate.shift(LEFT * 0.3), hand_r.animate.shift(RIGHT * 0.3),
                  run_time=0.2)
        self.play(hand_l.animate.shift(RIGHT * 0.2), hand_r.animate.shift(LEFT * 0.2),
                  run_time=0.15)                                            # t=2.45

        self.play(FadeOut(hand_l), FadeOut(hand_r), run_time=0.15)         # t=2.6
        self.play(Create(d), run_time=0.3)                                 # t=2.9

        # VTT "Called it safe" @18.34-13.6=4.74
        self.wait(1.54)                                                     # t=4.44
        s = stamp("SAFE", color=TKK_RED, size=80)
        s.move_to(DOWN * 1.5)
        self.play(FadeIn(s, scale=2.5), run_time=0.3)                     # t=4.74
        flash_transition(self, opacity=0.12, duration=0.1)                 # t=4.84

        # VTT "disappeared for a year" @19.32-13.6=5.72
        self.wait(0.58)                                                     # t=5.42
        # Person slowly fades out (disappearing)
        self.play(person.animate.set_opacity(0).shift(UP * 0.5), run_time=1.0)  # t=6.42

        # "1 YEAR" fact callout
        d2 = divider(color=TKK_RED)
        d2.move_to(DOWN * 4)
        fc = fact_callout("1", "YEAR", "", number_color=TKK_RED)
        fc.move_to(DOWN * 5.5)
        self.play(Create(d2), run_time=0.3)                                # t=6.72
        self.play(FadeIn(fc[0], scale=1.2), run_time=0.5)                 # t=7.22
        self.play(Flash(fc[0][0].get_center(), color=TKK_RED,
                        line_length=0.3, num_lines=6, run_time=0.3))       # t=7.52
        self.wait(1.98)                                                     # t=9.50


# ================================================================
# SCENE 4: SECOND INVENTION (23.1–29.8s = 6.7s)
# Voice: "not done... Freon... ozone layer"
# Visual: "FREON" headline + ozone circle tearing open
# ================================================================
class Scene4_SecondInvention(Scene):
    def construct(self):
        lbl = scene_label("NOT DONE", color=TKK_ACCENT)
        self.add(lbl)

        # "FREON" — the only text
        freon = headline("FREON", color=TKK_GOLD, size=120)
        freon.move_to(UP * 5)

        # Earth/ozone visual — circle representing the ozone layer
        earth = Circle(radius=2.5, fill_color="#1A3A5A", fill_opacity=0.3,
                       stroke_color="#3A8ACA", stroke_width=3)
        earth.move_to(UP * 0.5)
        ozone = Circle(radius=3, fill_color="#3A8ACA", fill_opacity=0.08,
                       stroke_color="#5ABAFF", stroke_width=2)
        ozone.move_to(earth)

        # The "hole" — arc that grows (representing ozone depletion)
        hole = Arc(radius=3, start_angle=PI * 0.3, angle=PI * 0.4,
                   color=TKK_RED, stroke_width=6)
        hole.move_to(earth)
        hole_fill = Arc(radius=2.8, start_angle=PI * 0.3, angle=PI * 0.4,
                        color=TKK_RED, stroke_width=0, fill_color=TKK_RED,
                        fill_opacity=0.15)
        hole_fill.move_to(earth)

        # Warning icon behind
        warn = load_svg("warning.svg", color=TKK_RED, height=2)
        warn.set_opacity(0.15).move_to(DOWN * 4.5)

        self.wait(0.3)                                                      # t=0.3

        # VTT "His next invention was Freon" @24.6-23.1=1.5
        self.wait(0.9)                                                      # t=1.2
        self.play(FadeIn(freon, scale=1.3), run_time=0.5)                 # t=1.7
        self.play(Flash(freon.get_center(), color=TKK_GOLD,
                        line_length=0.5, num_lines=12, run_time=0.3))      # t=2.0

        # Earth appears
        self.play(FadeIn(earth), FadeIn(ozone), run_time=0.5)             # t=2.5

        # VTT "tore a hole in the ozone layer" @26.9-23.1=3.8
        self.wait(1.0)                                                      # t=3.5
        # Hole tears open
        self.play(Create(hole), run_time=0.5)                              # t=4.0
        self.play(FadeIn(hole_fill), run_time=0.3)                        # t=4.3
        # Hole grows larger
        bigger_hole = Arc(radius=3, start_angle=PI * 0.15, angle=PI * 0.7,
                          color=TKK_RED, stroke_width=8).move_to(earth)
        self.play(Transform(hole, bigger_hole), run_time=0.5)             # t=4.8

        self.play(FadeIn(warn), run_time=0.3)                             # t=5.1
        self.play(Flash(earth.get_center(), color=TKK_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=5.4
        self.wait(1.3)                                                      # t=6.7


# ================================================================
# SCENE 5: THE SCALE (29.8–38.4s = 8.6s)
# Voice: "every human... 70 years... one man, two inventions"
# Visual: Grid of person icons all turning red + big numbers
# ================================================================
class Scene5_Scale(Scene):
    def construct(self):
        lbl = scene_label("THE SCALE", color=TKK_ACCENT)
        self.add(lbl)

        # Grid of tiny person icons — representing "every human on Earth"
        people = VGroup()
        for r in range(6):
            for c in range(8):
                p = load_svg("person.svg", color=TKK_WHITE, height=0.7)
                p.move_to(LEFT * 3.5 + RIGHT * c * 1.0 + UP * 5.5 + DOWN * r * 1.0)
                p.set_opacity(0.5)
                people.add(p)

        self.play(
            LaggedStart(*[FadeIn(p, scale=0.3) for p in people], lag_ratio=0.005),
            run_time=0.6,
        )                                                                   # t=0.6

        self.wait(0.4)                                                      # t=1.0

        # All turn red simultaneously — "poisoned every human"
        self.play(*[p.animate.set_color(TKK_RED).set_opacity(0.7) for p in people],
                  run_time=0.5)                                             # t=1.5
        self.play(Flash(ORIGIN + UP * 3, color=TKK_RED,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=1.8

        # "70 YEARS"
        d1 = divider(color=TKK_RED)
        d1.move_to(DOWN * 0.5)
        big70 = big_number_reveal("70", label_below="YEARS",
                                  number_color=TKK_RED, number_size=140,
                                  label_color=TKK_WHITE, label_size=50)
        big70.move_to(DOWN * 2.5)

        self.play(Create(d1), run_time=0.3)                                # t=2.1
        self.play(FadeIn(big70, scale=1.2), run_time=0.5)                 # t=2.6
        self.play(Flash(big70[0].get_center(), color=TKK_RED,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=2.9

        # VTT "Freon nearly destroyed the atmosphere" @33.88-29.8=4.08
        self.wait(0.88)                                                     # t=3.78

        # People fade to dim — atmosphere threat
        self.play(*[p.animate.set_opacity(0.2) for p in people], run_time=0.3)  # t=4.08

        # VTT "One man. Two inventions." @36.38-29.8=6.58
        self.wait(2.2)                                                      # t=6.28

        d2 = divider(color=TKK_GOLD)
        d2.move_to(DOWN * 5.5)
        one_two = big_number_reveal("1", label_above="ONE MAN",
                                    label_below="TWO INVENTIONS",
                                    number_color=TKK_RED, number_size=100,
                                    label_color=TKK_WHITE, label_size=36)
        one_two.move_to(DOWN * 7)

        self.play(Create(d2), run_time=0.3)                                # t=6.58
        self.play(FadeIn(one_two, scale=1.1), run_time=0.5)              # t=7.08
        self.play(Flash(one_two[1].get_center(), color=TKK_RED,
                        line_length=0.3, num_lines=8, run_time=0.3))       # t=7.38
        self.wait(1.22)                                                     # t=8.60


# ================================================================
# SCENE 6: THE PUNCH (38.4–47.8s = 9.4s)
# Voice: "most destructive organism... won awards for both"
# Visual: "ORGANISM" + two trophy/shield icons
# ================================================================
class Scene6_Punch(Scene):
    def construct(self):
        # Letterbox
        top = Rectangle(width=12, height=1.2, fill_color=BLACK, fill_opacity=1,
                        stroke_width=0).to_edge(UP, buff=0)
        bot = Rectangle(width=12, height=1.2, fill_color=BLACK, fill_opacity=1,
                        stroke_width=0).to_edge(DOWN, buff=0)
        self.play(FadeIn(top), FadeIn(bot), run_time=0.4)                 # t=0.4

        # Ghost skull behind
        ghost = load_svg("svgrepo-skull.svg", color=TKK_RED, height=8)
        ghost.set_opacity(0.03).move_to(UP * 1)
        self.add(ghost)

        d1 = divider(color=TKK_DIM)
        d1.move_to(UP * 2)
        self.play(Create(d1), run_time=0.3)                                # t=0.7

        # "ORGANISM" — THE word
        organism = headline("ORGANISM", color=TKK_WHITE, size=90)
        organism.move_to(UP * 0.3)
        self.play(FadeIn(organism, scale=1.08), run_time=0.8)             # t=1.5
        self.play(Flash(organism.get_center(), color=TKK_WHITE,
                        line_length=0.4, num_lines=10, run_time=0.3))      # t=1.8

        # VTT "He won awards for both" @43.34-38.4=4.94
        self.wait(2.84)                                                     # t=4.64

        d2 = divider(color=TKK_RED)
        d2.move_to(DOWN * 1.5)
        self.play(Create(d2), run_time=0.3)                                # t=4.94

        # Two trophy/award icons — the irony
        award1 = load_svg("shield.svg", color=TKK_GOLD, height=2)
        award1.move_to(LEFT * 2 + DOWN * 3.5)
        award2 = load_svg("shield.svg", color=TKK_GOLD, height=2)
        award2.move_to(RIGHT * 2 + DOWN * 3.5)

        lbl1 = safe_text("LEAD", font="Inter", font_size=22, color=TKK_RED,
                         weight="BOLD")
        lbl1.next_to(award1, DOWN, buff=0.2)
        lbl2 = safe_text("FREON", font="Inter", font_size=22, color=TKK_RED,
                         weight="BOLD")
        lbl2.next_to(award2, DOWN, buff=0.2)

        self.play(FadeIn(award1, scale=0.5), FadeIn(lbl1), run_time=0.5)  # t=5.44
        self.play(FadeIn(award2, scale=0.5), FadeIn(lbl2), run_time=0.5)  # t=5.94
        self.play(Flash(award1.get_center(), color=TKK_GOLD,
                        line_length=0.2, num_lines=6, run_time=0.2))       # t=6.14
        self.play(Flash(award2.get_center(), color=TKK_GOLD,
                        line_length=0.2, num_lines=6, run_time=0.2))       # t=6.34

        # 3s hold + fade
        self.wait(1.56)                                                     # t=7.90
        black = Rectangle(width=12, height=20, fill_color=BLACK,
                          fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5)                            # t=9.40


# ── Infra ─────────────────────────────────────────────────────
SCENES = [Scene1_Hook, Scene2_FirstInvention, Scene3_Coverup,
          Scene4_SecondInvention, Scene5_Scale, Scene6_Punch]

def render_single_scene(idx):
    config.output_file = f"midgley_v2_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    SCENES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"midgley_v2_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENES):
        n = f"midgley_v2_scene_{i+1}"; print(f"  Preview {n}...")
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
    files = parallel_render_scenes(__file__, scene_count=6, topic="midgley_v2", audio_path=str(audio))
    final = od / "midgley_v2_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
