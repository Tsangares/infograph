#!/usr/bin/env python3
"""The Calculus War — Newton vs Leibniz.

6 scenes, ~53s (50.7s audio + 2.3s hold).

VTT cues (absolute):
  Scene 1 (0.0–6.2s):   0.10 two men... 2.80 destroy each other
  Scene 2 (6.2–13.5s):  6.19 newton... 11.35 hid his work
  Scene 3 (13.5–22.0s): 13.47 leibniz... 19.64 cleaner... 21.96 easier
  Scene 4 (22.0–33.7s): 21.96 furious... 29.44 investigation... 33.68 wrote verdict
  Scene 5 (33.7–43.0s): 33.68 leibniz died... 37.57 alone... 41.05 no one else
  Scene 6 (43.0–53.0s): 42.84 twist... 46.53 leibniz notation... 50.65 won the future
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from manim import *
import numpy as np

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.frame_width = 9
config.frame_height = 16
config.background_color = "#080A10"
config.disable_caching = True

BG = "#080A10"; GRID_COL = "#1A2030"; SURFACE = "#15192A"
NEWTON_BLUE = "#3B82F6"; LEIBNIZ_GOLD = "#FFD700"; ANGER_RED = "#EF4444"
VERDICT_GREEN = "#22C55E"; DIM = "#4A5568"; MUTED = "#7B8DA0"
WHITE_SOFT = "#F0F0F0"; ROYAL_PURPLE = "#7C3AED"; DEATH_GRAY = "#6B7280"

SAFE_W = 8.0; SAFE_TOP = 7.2; SAFE_BOT = -6.4
ZONE_TITLE = 6.2; ZONE_UPPER = 3.5; ZONE_MID = 0.0
ZONE_LOWER = -3.5; ZONE_FOOTER = -6.0

def gradient_bg():
    bg = Rectangle(width=12, height=20, fill_color=BG, fill_opacity=1, stroke_width=0)
    glow = Circle(radius=5, fill_color="#121828", fill_opacity=0.08, stroke_width=0).move_to(UP*2)
    return VGroup(bg, glow)

def grid_lines(op=0.04):
    lines = VGroup()
    for i in range(13):
        y = -8 + i*16/12
        lines.add(Line(LEFT*5, RIGHT*5, color=GRID_COL, stroke_width=0.5).move_to(UP*y).set_opacity(op))
    for j in range(7):
        x = -4.5 + j*9/6
        lines.add(Line(DOWN*8, UP*8, color=GRID_COL, stroke_width=0.5).move_to(RIGHT*x).set_opacity(op))
    return lines

def safe_text(c, **kw):
    t = Text(c, **kw)
    if t.width > SAFE_W: t.scale(SAFE_W/t.width)
    return t

_ZONES = {"TITLE":ZONE_TITLE,"UPPER":ZONE_UPPER,"MID":ZONE_MID,"LOWER":ZONE_LOWER,"FOOTER":ZONE_FOOTER}
def safe_place(mob, zone, x=0):
    y = _ZONES[zone] if isinstance(zone, str) else float(zone)
    mob.move_to(np.array([float(x), y, 0]))
    if mob.width > SAFE_W: mob.scale(SAFE_W/mob.width)
    if mob.get_top()[1] > SAFE_TOP: mob.shift(DOWN*(mob.get_top()[1]-SAFE_TOP))
    if mob.get_bottom()[1] < SAFE_BOT: mob.shift(UP*(SAFE_BOT-mob.get_bottom()[1]))
    return mob

def validate_layout(sc):
    ys = [m.get_center()[1] for m in sc.mobjects[2:] if hasattr(m,'get_center') and m.width>0.01]
    if ys and min(ys) > -1.5:
        print(f"  LAYOUT WARN: lowest y={min(ys):.1f}")

def label_pill(txt, color=LEIBNIZ_GOLD, bg=SURFACE, fs=24):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > 3.5: t.scale(3.5/t.width)
    p = RoundedRectangle(width=t.width+0.3, height=t.height+0.2, corner_radius=0.1,
                         fill_color=bg, fill_opacity=0.9, stroke_width=0).move_to(t)
    return VGroup(p, t)

def versus_line():
    return Line(UP*1.5, DOWN*1.5, color=MUTED, stroke_width=2)


class Scene1_Hook(Scene):
    DURATION = 6.2
    """Two men invented calculus. Then tried to destroy each other."""
    def construct(self):
        self.add(gradient_bg(), grid_lines())
        t = 0
        pill = label_pill("THE CALCULUS WAR", color=ANGER_RED, fs=22); safe_place(pill, "TITLE")

        n_name = safe_text("NEWTON", font="Bebas Neue", font_size=80, color=NEWTON_BLUE)
        n_name.move_to(LEFT*2.2+UP*ZONE_UPPER)
        vs = safe_text("VS", font="Bebas Neue", font_size=50, color=ANGER_RED)
        vs.move_to(UP*ZONE_UPPER)
        l_name = safe_text("LEIBNIZ", font="Bebas Neue", font_size=80, color=LEIBNIZ_GOLD)
        l_name.move_to(RIGHT*2.2+UP*ZONE_UPPER)

        hook = safe_text("SAME INVENTION.", font="Bebas Neue", font_size=65, color=WHITE_SOFT)
        safe_place(hook, "MID")
        hook2 = safe_text("SAME TIME.", font="Bebas Neue", font_size=65, color=WHITE_SOFT)
        hook2.next_to(hook, DOWN, buff=0.4)

        war = safe_text("Then they tried to destroy each other.", font="Inter", font_size=28, color=ANGER_RED, weight="BOLD")
        safe_place(war, "LOWER")

        self.play(FadeIn(pill), run_time=0.3); t += 0.3
        self.play(FadeIn(n_name, shift=RIGHT*0.3), FadeIn(l_name, shift=LEFT*0.3), run_time=0.5); t += 0.5
        self.play(FadeIn(vs, scale=1.3), run_time=0.3); t += 0.3
        self.wait(1.5); t += 1.5
        self.play(FadeIn(hook, shift=UP*0.1), run_time=0.4); t += 0.4
        self.play(FadeIn(hook2, shift=UP*0.1), run_time=0.4); t += 0.4
        self.wait(1.5); t += 1.5
        self.play(FadeIn(war, shift=UP*0.04), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 6.2)
        self.wait(max(0.1, target - t - 0.3))
        validate_layout(self)


class Scene2_Newton(Scene):
    DURATION = 7.3
    """Newton figured it out in 1666 but hid it."""
    def construct(self):
        self.add(gradient_bg(), grid_lines())
        t = 0
        pill = label_pill("THE SECRET", color=NEWTON_BLUE, fs=22); safe_place(pill, "TITLE")

        name = safe_text("ISAAC NEWTON", font="Bebas Neue", font_size=70, color=NEWTON_BLUE)
        safe_place(name, "UPPER")

        date = safe_text("1666", font="Bebas Neue", font_size=120, color=NEWTON_BLUE)
        safe_place(date, "MID")
        date_sub = safe_text("Figured it out first.", font="Inter", font_size=28, color=MUTED, weight="BOLD")
        date_sub.next_to(date, DOWN, buff=0.3)

        secret = safe_text("TOLD NO ONE.", font="Bebas Neue", font_size=65, color=ANGER_RED)
        safe_place(secret, "LOWER")
        secret_sub = safe_text("Hid his work for decades.", font="Inter", font_size=26, color=DIM, weight="BOLD")
        safe_place(secret_sub, "FOOTER")

        self.play(FadeIn(pill), run_time=0.3); t += 0.3
        self.play(FadeIn(name, shift=UP*0.1), run_time=0.4); t += 0.4
        self.wait(1.0); t += 1.0
        self.play(FadeIn(date, scale=1.1), run_time=0.5); t += 0.5
        self.play(FadeIn(date_sub), run_time=0.3); t += 0.3
        self.wait(2.0); t += 2.0
        self.play(FadeIn(secret, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(secret.get_center(), color=ANGER_RED, line_length=0.3, num_lines=6, run_time=0.2)); t += 0.2
        self.play(FadeIn(secret_sub, shift=UP*0.04), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 7.3)
        self.wait(max(0.1, target - t - 0.3))
        validate_layout(self)


class Scene3_Leibniz(Scene):
    DURATION = 8.5
    """Leibniz published in 1684. Cleaner notation."""
    def construct(self):
        self.add(gradient_bg(), grid_lines())
        t = 0
        pill = label_pill("THE PUBLICATION", color=LEIBNIZ_GOLD, fs=22); safe_place(pill, "TITLE")

        name = safe_text("GOTTFRIED LEIBNIZ", font="Bebas Neue", font_size=60, color=LEIBNIZ_GOLD)
        safe_place(name, "UPPER")

        date = safe_text("1684", font="Bebas Neue", font_size=120, color=LEIBNIZ_GOLD)
        safe_place(date, "MID")
        date_sub = safe_text("Published his version.", font="Inter", font_size=28, color=MUTED, weight="BOLD")
        date_sub.next_to(date, DOWN, buff=0.3)

        # Notation comparison
        leibniz_n = safe_text("dy/dx", font="JetBrains Mono", font_size=55, color=LEIBNIZ_GOLD)
        leibniz_n.move_to(LEFT*2+UP*ZONE_LOWER)
        newton_n = safe_text("\u1e8b", font="JetBrains Mono", font_size=55, color=NEWTON_BLUE)
        newton_n.move_to(RIGHT*2+UP*ZONE_LOWER)
        lbl_l = safe_text("CLEANER", font="Inter", font_size=22, color=VERDICT_GREEN, weight="BOLD")
        lbl_l.next_to(leibniz_n, DOWN, buff=0.2)
        lbl_n = safe_text("HARDER", font="Inter", font_size=22, color=ANGER_RED, weight="BOLD")
        lbl_n.next_to(newton_n, DOWN, buff=0.2)
        div = versus_line(); div.move_to(UP*ZONE_LOWER)

        self.play(FadeIn(pill), run_time=0.3); t += 0.3
        self.play(FadeIn(name, shift=UP*0.1), run_time=0.4); t += 0.4
        self.wait(1.0); t += 1.0
        self.play(FadeIn(date, scale=1.1), run_time=0.5); t += 0.5
        self.play(FadeIn(date_sub), run_time=0.3); t += 0.3
        self.wait(1.5); t += 1.5
        self.play(Create(div), run_time=0.2); t += 0.2
        self.play(FadeIn(leibniz_n, shift=RIGHT*0.2), FadeIn(newton_n, shift=LEFT*0.2), run_time=0.4); t += 0.4
        self.play(FadeIn(lbl_l), FadeIn(lbl_n), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 8.5)
        self.wait(max(0.1, target - t - 0.3))
        validate_layout(self)


class Scene4_War(Scene):
    DURATION = 11.7
    """Newton accused Leibniz, rigged the investigation."""
    def construct(self):
        self.add(gradient_bg(), grid_lines())
        t = 0
        pill = label_pill("THE ACCUSATION", color=ANGER_RED, fs=22); safe_place(pill, "TITLE")

        fury = safe_text("NEWTON WAS FURIOUS.", font="Bebas Neue", font_size=60, color=ANGER_RED)
        safe_place(fury, "UPPER")

        accuse = safe_text("Accused Leibniz of theft.", font="Inter", font_size=30, color=WHITE_SOFT, weight="BOLD")
        accuse.next_to(fury, DOWN, buff=0.5)

        # Royal Society "investigation"
        rs_box = RoundedRectangle(width=6, height=2.5, corner_radius=0.15,
                                   fill_color=SURFACE, fill_opacity=0.9,
                                   stroke_color=ROYAL_PURPLE, stroke_width=2).move_to(UP*ZONE_MID)
        rs_title = safe_text("ROYAL SOCIETY", font="Bebas Neue", font_size=40, color=ROYAL_PURPLE)
        rs_title.move_to(rs_box.get_top()+DOWN*0.5)
        rs_verdict = safe_text("VERDICT: NEWTON", font="Bebas Neue", font_size=35, color=VERDICT_GREEN)
        rs_verdict.move_to(rs_box.get_center()+DOWN*0.2)

        kicker = safe_text("NEWTON WROTE IT HIMSELF.", font="Bebas Neue", font_size=45, color=ANGER_RED)
        safe_place(kicker, "LOWER")
        kicker_sub = safe_text("He stacked the jury. Then wrote the verdict.", font="Inter", font_size=22, color=DIM, weight="BOLD")
        safe_place(kicker_sub, "FOOTER")

        self.play(FadeIn(pill), run_time=0.3); t += 0.3
        self.play(FadeIn(fury, scale=1.1), run_time=0.5); t += 0.5
        self.wait(0.8); t += 0.8
        self.play(FadeIn(accuse, shift=UP*0.04), run_time=0.4); t += 0.4
        self.wait(1.5); t += 1.5
        self.play(FadeIn(rs_box), FadeIn(rs_title), run_time=0.5); t += 0.5
        self.wait(2.0); t += 2.0
        self.play(FadeIn(rs_verdict, scale=1.1), run_time=0.4); t += 0.4
        self.wait(1.2); t += 1.2
        self.play(FadeIn(kicker, scale=1.08), run_time=0.5); t += 0.5
        self.play(Flash(kicker.get_center(), color=ANGER_RED, line_length=0.3, num_lines=8, run_time=0.3)); t += 0.3
        self.play(FadeIn(kicker_sub, shift=UP*0.04), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 11.7)
        self.wait(max(0.1, target - t - 0.3))
        validate_layout(self)


class Scene5_Death(Scene):
    DURATION = 9.3
    """Leibniz died alone, discredited."""
    def construct(self):
        self.add(gradient_bg(), grid_lines())
        t = 0
        pill = label_pill("THE COST", color=DEATH_GRAY, fs=22); safe_place(pill, "TITLE")

        name = safe_text("LEIBNIZ", font="Bebas Neue", font_size=80, color=DEATH_GRAY)
        safe_place(name, "UPPER")

        date = safe_text("1716", font="Bebas Neue", font_size=100, color=DEATH_GRAY)
        safe_place(date, "MID")

        alone = safe_text("DIED ALONE.", font="Bebas Neue", font_size=65, color=ANGER_RED)
        alone.next_to(date, DOWN, buff=0.5)

        discredited = safe_text("DISCREDITED.", font="Bebas Neue", font_size=55, color=ANGER_RED)
        discredited.next_to(alone, DOWN, buff=0.3)

        funeral = safe_text("His funeral: one secretary. No one else.", font="Inter", font_size=26, color=DIM, weight="BOLD")
        safe_place(funeral, "FOOTER")

        self.play(FadeIn(pill), run_time=0.3); t += 0.3
        self.play(FadeIn(name), run_time=0.4); t += 0.4
        self.wait(0.8); t += 0.8
        self.play(FadeIn(date, scale=1.1), run_time=0.5); t += 0.5
        self.wait(1.2); t += 1.2
        self.play(FadeIn(alone, shift=UP*0.1), run_time=0.5); t += 0.5
        self.play(FadeIn(discredited, shift=UP*0.1), run_time=0.4); t += 0.4
        self.wait(1.5); t += 1.5
        self.play(FadeIn(funeral, shift=UP*0.04), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 9.3)
        self.wait(max(0.1, target - t - 0.3))
        validate_layout(self)


class Scene6_Twist(Scene):
    DURATION = 10.0
    """Every textbook uses Leibniz's notation. He won the future."""
    def construct(self):
        self.add(gradient_bg(), grid_lines())
        t = 0
        pill = label_pill("THE TWIST", color=LEIBNIZ_GOLD, fs=22); safe_place(pill, "TITLE")

        # Big notation — Leibniz won
        notation = safe_text("dy/dx", font="JetBrains Mono", font_size=120, color=LEIBNIZ_GOLD)
        safe_place(notation, "UPPER")
        every = safe_text("EVERY TEXTBOOK. TODAY.", font="Bebas Neue", font_size=50, color=WHITE_SOFT)
        every.next_to(notation, DOWN, buff=0.4)

        # Newton's notation crossed out
        newton_n = safe_text("\u1e8b", font="JetBrains Mono", font_size=80, color=NEWTON_BLUE)
        safe_place(newton_n, "MID")
        newton_n.set_opacity(0.5)
        strike = Line(newton_n.get_left()+LEFT*0.3, newton_n.get_right()+RIGHT*0.3,
                      color=ANGER_RED, stroke_width=4).move_to(newton_n)

        # Punchline — stays on screen, no fade to black
        punch = safe_text("The man who lost the war", font="DM Serif Display", font_size=38, color=WHITE_SOFT)
        safe_place(punch, "LOWER")
        punch2 = safe_text("won the future.", font="DM Serif Display", font_size=42, color=LEIBNIZ_GOLD)
        punch2.next_to(punch, DOWN, buff=0.3)

        self.play(FadeIn(pill), run_time=0.3); t += 0.3
        self.play(FadeIn(notation, scale=1.2), run_time=0.6); t += 0.6
        self.play(FadeIn(every, shift=UP*0.1), run_time=0.4); t += 0.4
        self.wait(1.5); t += 1.5
        self.play(FadeIn(newton_n), run_time=0.3); t += 0.3
        self.play(Create(strike), run_time=0.3); t += 0.3
        self.wait(1.2); t += 1.2
        self.play(FadeIn(punch, shift=UP*0.04), run_time=0.5); t += 0.5
        self.play(FadeIn(punch2, shift=UP*0.04), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 10.0)
        self.wait(max(0.1, target - t - 0.8))
        validate_layout(self)


SCENES = [Scene1_Hook, Scene2_Newton, Scene3_Leibniz, Scene4_War, Scene5_Death, Scene6_Twist]

def render_single_scene(idx):
    config.output_file = f"calculus_war_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    SCENES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"calculus_war_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENES):
        n = f"calculus_war_scene_{i+1}"; print(f"  Preview {n}...")
        config.output_file = n; config.save_last_frame = True; config.format = "png"
        S().render()
        for p in Path(config.media_dir).rglob(f"{n}*"):
            if p.suffix == ".png":
                dst = d / f"{n}.png"; shutil.copy2(str(p), str(dst))
                print(f"  OK: {dst} ({dst.stat().st_size//1024} KB)"); break
    config.save_last_frame = False; config.format = None

if __name__ == "__main__":
    import time, gc
    od = Path(__file__).parent
    if "--preview" in sys.argv:
        render_previews()
        try:
            from render_utils import run_preview_qa
            run_preview_qa(od / "previews")
        except ImportError: pass
        sys.exit(0)
    if "--scene" in sys.argv:
        timings_json = os.environ.get("TKK_SCENE_TIMINGS")
        if timings_json:
            _idx = int(sys.argv[sys.argv.index("--scene")+1])
            SCENES[_idx].DURATION = json.loads(timings_json)[_idx]
        render_single_scene(int(sys.argv[sys.argv.index("--scene")+1])); sys.exit(0)

    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_calculus_war.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="calculus_war", audio_path=str(audio))
    final = od / "calculus_war_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
    try:
        from render_utils import run_post_render_qa
        run_post_render_qa(str(final), scene_count=6)
    except ImportError: pass
