#!/usr/bin/env python3
"""Thomas Midgley Jr. — 'The Man Who Poisoned the Planet Twice' (Manim).

Uses anim_primitives + scene_templates toolkit.
6 scenes, ~43.6s (40.6s audio + 3s hold).
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from manim import *
from anim_primitives import *
from scene_templates import TKKBaseScene, PunchScene

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.frame_width = 9
config.frame_height = 16
config.background_color = TKK_BG
config.disable_caching = True


# ================================================================
# SCENE 1: THE HOOK (0.0–5.3s = 5.30s)
# "One man caused more environmental damage than any organism in Earth's history"
# FAST: label + headline appear instantly. Caption fades.
# ================================================================
class Scene1_Hook(TKKBaseScene):
    DURATION = 9.7
    LABEL = "THOMAS MIDGLEY JR."
    DURATION = 5.30

    def construct(self):
        # INSTANT — label + rule line visible from frame 1
        lbl = scene_label(self.LABEL, color=TKK_ACCENT)
        t = 0
        rule = Line(LEFT * 4.5, RIGHT * 4.5, color=TKK_MUTED, stroke_width=0.5,
                    stroke_opacity=0.3).move_to(UP * 6.5)
        self.add(lbl, rule)

        # Big number reveal: "1 MAN"
        reveal = big_number_reveal("1", label_above="", label_below="MAN",
                                   number_color=TKK_RED, number_size=200,
                                   label_color=TKK_WHITE, label_size=60)
        reveal.move_to(UP * 2)
        self.play(FadeIn(reveal, scale=1.15), run_time=0.5); t += 0.5
        self.play(Flash(reveal[0].get_center(), color=TKK_RED,
                        line_length=0.6, num_lines=12, run_time=0.3))      # t=0.8

        d = divider(color=TKK_RED)
        d.move_to(DOWN * 1)
        self.play(Create(d), run_time=0.3); t += 0.3

        # Caption lines
        c1 = caption("More environmental damage", color=TKK_WHITE, size=42)
        c1.move_to(DOWN * 2.5)
        c2 = caption("than any organism", color=TKK_DIM, size=42)
        c2.move_to(DOWN * 3.5)
        c3 = caption("in Earth's history.", color=TKK_DIM, size=42)
        c3.move_to(DOWN * 4.5)

        self.play(FadeIn(c1, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(FadeIn(c2, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(FadeIn(c3, shift=UP * 0.06), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 9.7)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 2: FIRST INVENTION (5.3–12.0s = 6.70s)
# "1921... Thomas Midgley... lead to gasoline... hallucinating, convulsing, dying"
# ================================================================
class Scene2_FirstInvention(TKKBaseScene):
    DURATION = 3.6
    LABEL = "FIRST INVENTION"
    DURATION = 6.70

    def construct(self):
        lbl = scene_label(self.LABEL, color=TKK_ACCENT)
        t = 0
        self.add(lbl)

        # "1921" date slam
        date = headline("1921", color=TKK_GOLD, size=120)
        date.move_to(UP * 5.5)
        self.play(FadeIn(date, scale=1.3), run_time=0.5); t += 0.5
        self.play(Flash(date.get_center(), color=TKK_GOLD,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=0.8

        name = headline("THOMAS MIDGLEY", color=TKK_WHITE, size=60)
        name.move_to(UP * 3.5)
        self.play(FadeIn(name, shift=UP * 0.06), run_time=0.5); t += 0.5

        added = caption("added lead to gasoline.", color=TKK_DIM, size=40)
        added.move_to(UP * 2.3)
        self.play(FadeIn(added, shift=UP * 0.06), run_time=0.5); t += 0.5

        d = divider(color=TKK_RED)
        d.move_to(UP * 1)
        self.play(Create(d), run_time=0.3); t += 0.3

        # Cascade: hallucinating / convulsing / dying
        items = ["HALLUCINATING", "CONVULSING", "DYING"]
        colors = [TKK_WHITE, TKK_WHITE, TKK_RED]
        cl, anims = cascade_list(items, colors, size=50)
        cl.move_to(DOWN * 1.5)

        # VTT: hallucinating @3.72 (relative), convulsing @5.34, dying @5.88
        self.wait(1.32); t += 1.32
        self.play(anims[0], run_time=0.4); t += 0.4
        self.wait(1.22); t += 1.22
        self.play(anims[1], run_time=0.3); t += 0.3
        self.wait(0.24); t += 0.24
        self.play(anims[2], run_time=0.3); t += 0.3
        self.play(Flash(cl[2].get_center(), color=TKK_RED,
                        line_length=0.3, num_lines=8, run_time=0.3))       # t=6.18
        target = getattr(self.__class__, 'DURATION', 3.6)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 3: THE COVERUP (12.0–20.4s = 8.40s)
# "Press conference... washed hands... called it safe... disappeared for a year"
# ================================================================
class Scene3_Coverup(TKKBaseScene):
    DURATION = 11.0
    LABEL = "THE COVERUP"
    DURATION = 8.40

    def construct(self):
        lbl = scene_label(self.LABEL, color=TKK_ACCENT)
        t = 0
        self.add(lbl)

        # "He held a press conference."
        press = caption("He held a press conference.", color=TKK_WHITE, size=42)
        press.move_to(UP * 5)
        self.play(FadeIn(press, shift=UP * 0.06), run_time=0.5); t += 0.5

        # "Washed his hands in leaded gasoline."
        washed = caption("Washed his hands", color=TKK_WHITE, size=44)
        washed.move_to(UP * 3.2)
        gasoline = caption("in leaded gasoline.", color=TKK_GOLD, size=46)
        gasoline.move_to(UP * 2.1)
        on_cam = caption("On camera.", color=TKK_DIM, size=38)
        on_cam.move_to(UP * 1)

        self.wait(1.1); t += 1.1
        self.play(FadeIn(washed, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(FadeIn(gasoline, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(FadeIn(on_cam, shift=UP * 0.06), run_time=0.4); t += 0.4

        # "SAFE" stamp — the share trigger
        # VTT: "Called it safe" @ 16.4 - 12.0 = 4.4s
        self.wait(1.1); t += 1.1
        s = stamp("SAFE", color=TKK_RED, size=70)
        s.move_to(DOWN * 0.5)
        self.play(FadeIn(s, scale=2.0), run_time=0.3); t += 0.3
        flash_transition(self, opacity=0.1, duration=0.1)                  # t=4.5

        # Divider
        d = divider(color=TKK_DIM)
        d.move_to(DOWN * 2)
        self.play(Create(d), run_time=0.3); t += 0.3

        # VTT: "Then disappeared for a year..." @ 17.24 - 12.0 = 5.24
        # fact_callout for the ironic punchline
        fc = fact_callout("1", "YEAR", "to recover from lead poisoning",
                          number_color=TKK_RED, desc_color=TKK_DIM)
        fc.move_to(DOWN * 4)
        self.wait(0.14); t += 0.14
        self.play(FadeIn(fc[0], scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(fc[0][0].get_center(), color=TKK_RED,
                        line_length=0.3, num_lines=6, run_time=0.3))       # t=5.74
        self.play(FadeIn(fc[1], shift=UP * 0.2), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 11.0)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 4: SECOND INVENTION (20.4–26.7s = 6.30s)
# "He was not done. His next invention was Freon. Ozone layer."
# ================================================================
class Scene4_SecondInvention(TKKBaseScene):
    DURATION = 2.4
    LABEL = "SECOND INVENTION"
    DURATION = 6.30

    def construct(self):
        lbl = scene_label(self.LABEL, color=TKK_ACCENT)
        t = 0
        self.add(lbl)

        # "He was not done." — ominous
        not_done = headline("HE WASN'T DONE.", color=TKK_WHITE, size=70)
        not_done.move_to(UP * 5)
        self.play(FadeIn(not_done, scale=1.05), run_time=0.6); t += 0.6
        self.wait(0.74); t += 0.74

        # VTT: "His next invention was Freon" @ 21.74-20.4 = 1.34
        d1 = divider(color=TKK_GOLD)
        d1.move_to(UP * 3.2)
        self.play(Create(d1), run_time=0.3); t += 0.3

        freon = headline("FREON", color=TKK_GOLD, size=120)
        freon.move_to(UP * 1)
        self.play(FadeIn(freon, scale=1.3), run_time=0.6); t += 0.6
        self.play(Flash(freon.get_center(), color=TKK_GOLD,
                        line_length=0.5, num_lines=12, run_time=0.3))      # t=2.54

        # VTT: "The chemical that tore a hole in the ozone layer" @ 23.74-20.4 = 3.34
        d2 = divider(color=TKK_RED)
        d2.move_to(DOWN * 1.2)
        self.wait(0.5); t += 0.5
        self.play(Create(d2), run_time=0.3); t += 0.3

        tore = caption("The chemical that tore a hole", color=TKK_WHITE, size=40)
        tore.move_to(DOWN * 2.5)
        ozone = headline("IN THE OZONE LAYER.", color=TKK_RED, size=55)
        ozone.move_to(DOWN * 3.8)

        self.play(FadeIn(tore, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(ozone, scale=1.05), run_time=0.6); t += 0.6
        self.play(Flash(ozone.get_center(), color=TKK_RED,
                        line_length=0.3, num_lines=8, run_time=0.3))       # t=4.84
        target = getattr(self.__class__, 'DURATION', 2.4)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 5: THE SCALE (26.7–35.0s = 8.30s)
# "Every human on Earth for 70 years... atmosphere... one man, two inventions"
# ================================================================
class Scene5_Scale(TKKBaseScene):
    DURATION = 9.4
    LABEL = "THE SCALE"
    DURATION = 8.30

    def construct(self):
        lbl = scene_label(self.LABEL, color=TKK_ACCENT)
        t = 0
        self.add(lbl)

        # VTT: "Leaded gas poisoned every human on Earth for 70 years"
        fc70 = fact_callout("70", "YEARS", "every human on Earth poisoned",
                            number_color=TKK_RED, desc_color=TKK_DIM,
                            number_size=100)
        fc70.move_to(UP * 4.5)
        self.play(FadeIn(fc70[0], scale=1.2), run_time=0.6); t += 0.6
        self.play(Flash(fc70[0][0].get_center(), color=TKK_RED,
                        line_length=0.4, num_lines=10, run_time=0.3))      # t=0.9
        self.play(FadeIn(fc70[1], shift=UP * 0.2), run_time=0.5); t += 0.5

        # VTT: "Freon nearly destroyed the atmosphere" @ 30.6-26.7 = 3.9
        d1 = divider(color=TKK_RED)
        d1.move_to(UP * 1.5)
        self.wait(2.2); t += 2.2
        self.play(Create(d1), run_time=0.3); t += 0.3
        atm = caption("Freon nearly destroyed the atmosphere.", color=TKK_WHITE, size=38)
        atm.move_to(UP * 0.3)
        self.play(FadeIn(atm, shift=UP * 0.06), run_time=0.6); t += 0.6

        # VTT: "One man. Two inventions." @ 33.24-26.7 = 6.54
        d2 = divider(color=TKK_GOLD)
        d2.move_to(DOWN * 1.2)
        self.wait(1.74); t += 1.74
        self.play(Create(d2), run_time=0.3); t += 0.3

        # big_number_reveal "1 MAN / 2 INVENTIONS"
        reveal = big_number_reveal("1", label_above="ONE MAN", label_below="TWO INVENTIONS",
                                   number_color=TKK_RED, number_size=120,
                                   label_color=TKK_WHITE, label_size=40)
        reveal.move_to(DOWN * 3.5)
        self.play(FadeIn(reveal, scale=1.1), run_time=0.6); t += 0.6
        self.play(Flash(reveal[1].get_center(), color=TKK_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=7.44
        target = getattr(self.__class__, 'DURATION', 9.4)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 6: THE PUNCH (35.0–43.6s = 8.60s)
# "Most destructive organism... won awards for both."
# ================================================================
class Scene6_Punch(TKKBaseScene):
    DURATION = 8.7
    LABEL = ""
    DURATION = 8.60

    def construct(self):
        t = 0
        # Letterbox bars
        top_bar = Rectangle(width=12, height=1.2, fill_color=BLACK,
                            fill_opacity=1, stroke_width=0).to_edge(UP, buff=0)
        bot_bar = Rectangle(width=12, height=1.2, fill_color=BLACK,
                            fill_opacity=1, stroke_width=0).to_edge(DOWN, buff=0)
        self.play(FadeIn(top_bar), FadeIn(bot_bar), run_time=0.4); t += 0.4

        d1 = divider(color=TKK_DIM)
        d1.move_to(UP * 2)
        self.play(Create(d1), run_time=0.3); t += 0.3

        # "Historians called him the most destructive"
        historians = caption("Historians called him the most destructive",
                            color=TKK_DIM, size=36)
        historians.move_to(UP * 0.5)
        self.play(FadeIn(historians, shift=UP * 0.08), run_time=0.7); t += 0.7

        # "ORGANISM" — not person, organism
        organism = headline("ORGANISM", color=TKK_WHITE, size=80)
        organism.move_to(DOWN * 1)
        sub = caption("in the history of the planet.", color=TKK_DIM, size=36)
        sub.move_to(DOWN * 2.2)
        self.play(FadeIn(organism, scale=1.08), run_time=0.7); t += 0.7
        self.play(FadeIn(sub, shift=UP * 0.06), run_time=0.5); t += 0.5

        # VTT: "He won awards for both." @ 39.12-35.0 = 4.12
        d2 = divider(color=TKK_RED)
        d2.move_to(DOWN * 3.5)
        self.wait(1.22); t += 1.22
        self.play(Create(d2), run_time=0.3); t += 0.3

        awards = caption("He won awards", color=TKK_RED, size=44)
        awards.move_to(DOWN * 4.8)
        both = headline("FOR BOTH.", color=TKK_RED, size=70)
        both.move_to(DOWN * 6)

        self.play(FadeIn(awards, shift=UP * 0.06), run_time=0.6); t += 0.6
        self.play(FadeIn(both, scale=1.08), run_time=0.7); t += 0.7
        self.play(Flash(both.get_center(), color=TKK_RED,
                        line_length=0.4, num_lines=10, run_time=0.3))      # t=5.72

        # 3s hold + fade
        target = getattr(self.__class__, 'DURATION', 8.7)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK,
                          fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5


# ── Infra ─────────────────────────────────────────────────────
SCENES = [Scene1_Hook, Scene2_FirstInvention, Scene3_Coverup,
          Scene4_SecondInvention, Scene5_Scale, Scene6_Punch]

def render_single_scene(idx):
    config.output_file = f"midgley_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    SCENES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"midgley_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENES):
        n = f"midgley_scene_{i+1}"; print(f"  Preview {n}...")
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
            SCENES[_idx].DURATION = json.loads(timings_json)[_idx]
        render_single_scene(int(sys.argv[sys.argv.index("--scene")+1])); sys.exit(0)

    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_midgley.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="midgley", audio_path=str(audio))
    final = od / "midgley_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
