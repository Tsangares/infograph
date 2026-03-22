#!/usr/bin/env python3
"""Born to Count — FULL REBUILD with zone layout system.

6 scenes, ~55.7s (52.7s audio + 3s hold).
Uses: safe_place(), validate_layout(), ZONE constants, svg_grid(), icon_state_change().
Every scene fills 3+ vertical zones. Standard patterns: grids, side-by-side, numbers.

VTT cues (absolute → relative):
  Scene 1 (0.0–6.1s):  0.30 Babies can do math... 3.14 born with number sense
  Scene 2 (6.1–12.6s): 6.10 somewhere along the way... 10.78 not math people
  Scene 3 (12.6–24.1s): 12.60 Amazon Piraha... 19.56 hardware universal... 21.30 every brain
  Scene 4 (24.1–37.4s): 24.14 Stanford proved... 26.18 learned not inherited...
                         29.28 told not math people... 34.14 math center shuts down
  Scene 5 (37.4–46.5s): 38.32 millions walk around... 43.46 third grade
  Scene 6 (46.5–55.7s): 46.48 born knowing... 49.88 depends on words
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from manim import *
from anim_primitives import (
    safe_text, headline, caption, divider, scene_label, stamp, flash_transition,
    big_number_reveal, fact_callout, load_svg, svg_grid, icon_state_change,
    safe_place, validate_layout, layout_stack,
    TKK_BG, TKK_RED, TKK_GOLD, TKK_WHITE, TKK_DIM, TKK_MUTED, TKK_ACCENT,
    SAFE_W, SAFE_TOP, SAFE_BOT,
    ZONE_TITLE, ZONE_UPPER, ZONE_MID, ZONE_LOWER, ZONE_FOOTER,
)

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.frame_width = 9
config.frame_height = 16
config.background_color = TKK_BG
config.disable_caching = True

MATH_GOLD = "#FFD700"
FEAR_RED = "#EF4444"
BRAIN_GRAY = "#2D3748"
DIM = "#4A5568"


def setup_bg(scene, opacity=0.03):
    bg = Rectangle(width=12, height=20, fill_color=TKK_BG, fill_opacity=1, stroke_width=0)
    glow = Circle(radius=5, fill_color="#121828", fill_opacity=0.08, stroke_width=0).move_to(UP * 2)
    scene.add(VGroup(bg, glow))
    lines = VGroup()
    for i in range(13):
        y = -8 + i * 16 / 12
        lines.add(Line(LEFT*5, RIGHT*5, color="#1A2030", stroke_width=0.5).move_to(UP*y).set_opacity(opacity))
    for j in range(7):
        x = -4.5 + j * 9 / 6
        lines.add(Line(DOWN*8, UP*8, color="#1A2030", stroke_width=0.5).move_to(RIGHT*x).set_opacity(opacity))
    scene.add(lines)


def dot_grid(rows, cols, color=MATH_GOLD, radius=0.08, spacing=0.5, opacity=0.7, seed=None):
    if seed is not None:
        np.random.seed(seed)
    grid = VGroup()
    for r in range(rows):
        for c in range(cols):
            jx = np.random.uniform(-0.1, 0.1) if seed else 0
            jy = np.random.uniform(-0.1, 0.1) if seed else 0
            d = Dot(np.array([c * spacing + jx, -r * spacing + jy, 0]),
                    radius=radius, color=color).set_opacity(opacity)
            grid.add(d)
    grid.center()
    return grid


class Scene1_Hook(Scene):
    DURATION = 5.8
    def construct(self):
        setup_bg(self)
        t = 0
        pill = scene_label("BORN TO COUNT")
        safe_place(pill, "TITLE")
        dots_8 = dot_grid(2, 4, MATH_GOLD, 0.09, 0.5, seed=11)
        safe_place(dots_8, "UPPER", x=-2)
        lbl_8 = safe_text("8", font="Bebas Neue", font_size=40, color=DIM)
        lbl_8.next_to(dots_8, DOWN, buff=0.3)
        dots_12 = dot_grid(3, 4, MATH_GOLD, 0.09, 0.5, seed=22)
        safe_place(dots_12, "UPPER", x=2)
        lbl_12 = safe_text("12", font="Bebas Neue", font_size=40, color=DIM)
        lbl_12.next_to(dots_12, DOWN, buff=0.3)
        arrow = Arrow(LEFT * 0.5, RIGHT * 1.5, color=MATH_GOLD, stroke_width=3, buff=0.1)
        safe_place(arrow, "MID", x=0.5)
        num_sense = big_number_reveal("100%", label_below="BORN WITH NUMBER SENSE",
                                       number_color=MATH_GOLD, number_size=100,
                                       label_color=TKK_WHITE, label_size=32)
        safe_place(num_sense, "LOWER")
        src = safe_text("Before language. Before counting.", font="Inter", font_size=22, color=DIM)
        safe_place(src, "FOOTER")
        self.play(FadeIn(pill), run_time=0.3); t += 0.3
        self.play(FadeIn(dots_8), FadeIn(lbl_8), FadeIn(dots_12), FadeIn(lbl_12), run_time=0.5); t += 0.5
        self.play(GrowArrow(arrow), run_time=0.4); t += 0.4
        self.play(Flash(dots_12.get_center(), color=MATH_GOLD, line_length=0.3, num_lines=6, run_time=0.3)); t += 0.3
        self.wait(1.3); t += 1.3
        self.play(FadeIn(num_sense, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(num_sense[0].get_center(), color=MATH_GOLD, line_length=0.4, num_lines=8, run_time=0.3)); t += 0.3
        self.play(FadeIn(src), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 5.8)
        self.wait(max(0.1, target - t - 0.3))
        validate_layout(self)


class Scene2_WrongAnswer(Scene):
    DURATION = 6.1
    def construct(self):
        setup_bg(self)
        t = 0
        pill = scene_label("THE LIE")
        safe_place(pill, "TITLE")
        people = svg_grid("person.svg", 4, 6, color=MATH_GOLD, icon_height=0.7,
                          spacing_x=1.0, spacing_y=1.0, opacity=0.6)
        safe_place(people, 1.0)
        s = stamp("NOT A MATH PERSON", color=FEAR_RED, size=44, angle=-0.08)
        safe_place(s, "LOWER")
        damage = safe_text("MILLIONS AFFECTED", font="Bebas Neue", font_size=50, color=FEAR_RED)
        safe_place(damage, "FOOTER")
        self.play(FadeIn(pill), run_time=0.3); t += 0.3
        self.play(LaggedStart(*[FadeIn(p, scale=0.3) for p in people], lag_ratio=0.005), run_time=0.6); t += 0.6
        self.wait(3.0); t += 3.0
        self.play(FadeIn(s, scale=2.0), run_time=0.3); t += 0.3
        flash_transition(self, opacity=0.08, duration=0.06)
        half = list(people)[:12]
        gray_anims = [p.animate.set_color(DIM).set_opacity(0.2) for p in half]
        self.play(LaggedStart(*gray_anims, lag_ratio=0.02), run_time=0.8); t += 0.8
        self.play(FadeIn(damage, scale=1.1), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 6.1)
        self.wait(max(0.1, target - t - 0.3))
        validate_layout(self)


class Scene3_Contradiction(Scene):
    DURATION = 10.9
    def construct(self):
        setup_bg(self)
        t = 0
        pill = scene_label("THE CONTRADICTION")
        safe_place(pill, "TITLE")
        vocab_title = safe_text("VOCABULARY", font="Inter", font_size=22, color=DIM, weight="BOLD")
        safe_place(vocab_title, 5.0, x=-2.2)
        nums = VGroup()
        for i, n in enumerate([1, 2, 3]):
            circle = Circle(radius=0.3, fill_color=MATH_GOLD, fill_opacity=0.3,
                            stroke_color=MATH_GOLD, stroke_width=2)
            txt = Text(str(n), font="Bebas Neue", font_size=32, color=MATH_GOLD)
            txt.move_to(circle)
            grp = VGroup(circle, txt)
            grp.move_to(LEFT * 2.2 + UP * (3.5 - i * 1.0))
            nums.add(grp)
        ellipsis = safe_text("...", font="Bebas Neue", font_size=48, color=DIM)
        ellipsis.move_to(LEFT * 2.2 + UP * 0.5)
        est_title = safe_text("ESTIMATION", font="Inter", font_size=22, color=DIM, weight="BOLD")
        safe_place(est_title, 5.0, x=2.2)
        cluster = dot_grid(4, 5, MATH_GOLD, 0.08, 0.45, seed=33)
        safe_place(cluster, "UPPER", x=2.2)
        equals = safe_text("= SAME RESULT", font="Bebas Neue", font_size=50, color=MATH_GOLD)
        safe_place(equals, "MID")
        universal = safe_text("UNIVERSAL", font="Bebas Neue", font_size=80, color=MATH_GOLD)
        safe_place(universal, "LOWER")
        sub = safe_text("Built into every human brain.", font="Inter", font_size=28, color=DIM)
        sub.next_to(universal, DOWN, buff=0.3)
        source = safe_text("Pirahã people, Amazon Basin", font="Inter", font_size=20, color=DIM)
        safe_place(source, "FOOTER")
        self.play(FadeIn(pill), run_time=0.3); t += 0.3
        self.play(FadeIn(vocab_title), FadeIn(est_title), run_time=0.2); t += 0.2
        self.play(LaggedStart(*[FadeIn(n, scale=0.8) for n in nums], lag_ratio=0.12), run_time=0.5); t += 0.5
        self.play(FadeIn(ellipsis), run_time=0.2); t += 0.2
        self.play(FadeIn(cluster), run_time=0.4); t += 0.4
        self.wait(3.5); t += 3.5
        self.play(FadeIn(equals, scale=1.1), run_time=0.4); t += 0.4
        self.play(FadeIn(source), run_time=0.2); t += 0.2
        self.wait(2.8); t += 2.8
        self.play(FadeIn(universal, scale=1.15), run_time=0.5); t += 0.5
        self.play(Flash(universal.get_center(), color=MATH_GOLD, line_length=0.4, num_lines=10, run_time=0.3)); t += 0.3
        self.play(FadeIn(sub), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 10.9)
        self.wait(max(0.1, target - t - 0.3))
        validate_layout(self)


class Scene4_Proof(Scene):
    DURATION = 12.6
    def construct(self):
        setup_bg(self)
        t = 0
        pill = scene_label("STANFORD, 2012")
        safe_place(pill, "TITLE")
        before_title = safe_text("BEFORE THE LABEL", font="Inter", font_size=22, color=DIM, weight="BOLD")
        safe_place(before_title, 5.0, x=-2)
        brain_gold = Circle(radius=1.2, fill_color=MATH_GOLD, fill_opacity=0.15,
                           stroke_color=MATH_GOLD, stroke_width=2)
        brain_gold.move_to(LEFT * 2 + UP * 3)
        gold_label = safe_text("MATH\nACTIVE", font="Bebas Neue", font_size=36, color=MATH_GOLD)
        gold_label.move_to(brain_gold)
        after_title = safe_text("AFTER THE LABEL", font="Inter", font_size=22, color=DIM, weight="BOLD")
        safe_place(after_title, 5.0, x=2)
        brain_red = Circle(radius=1.2, fill_color=FEAR_RED, fill_opacity=0.15,
                          stroke_color=FEAR_RED, stroke_width=2)
        brain_red.move_to(RIGHT * 2 + UP * 3)
        red_label = safe_text("FEAR\nACTIVE", font="Bebas Neue", font_size=36, color=FEAR_RED)
        red_label.move_to(brain_red)
        div_line = DashedLine(UP * 5, UP * 1.5, color=TKK_MUTED, stroke_width=1, dash_length=0.15)
        arrow_down = Arrow(UP * 1, DOWN * 0.5, color=FEAR_RED, stroke_width=3, buff=0.1)
        safe_place(arrow_down, 0.5)
        label_txt = safe_text("NOT A MATH PERSON", font="Inter", font_size=32, color=FEAR_RED, weight="BOLD")
        label_txt.next_to(arrow_down, DOWN, buff=0.2)
        d = divider(color=FEAR_RED)
        safe_place(d, -2.5)
        learned = safe_text("LEARNED", font="Bebas Neue", font_size=80, color=FEAR_RED)
        safe_place(learned, "LOWER")
        not_inh = safe_text("NOT INHERITED", font="Bebas Neue", font_size=50, color=DIM)
        not_inh.next_to(learned, DOWN, buff=0.3)
        footer = safe_text("Math anxiety is created by words, not genes.", font="Inter", font_size=22, color=DIM)
        safe_place(footer, "FOOTER")
        self.play(FadeIn(pill), run_time=0.3); t += 0.3
        self.play(FadeIn(before_title), run_time=0.2); t += 0.2
        self.play(FadeIn(brain_gold), FadeIn(gold_label), run_time=0.5); t += 0.5
        self.play(Create(div_line), run_time=0.3); t += 0.3
        self.wait(2.7); t += 2.7
        self.play(Create(d), run_time=0.3); t += 0.3
        self.play(FadeIn(learned, scale=1.1), run_time=0.5); t += 0.5
        self.play(FadeIn(not_inh), run_time=0.3); t += 0.3
        self.wait(2.0); t += 2.0
        self.play(FadeIn(after_title), run_time=0.2); t += 0.2
        self.play(FadeIn(arrow_down), FadeIn(label_txt), run_time=0.4); t += 0.4
        self.play(FadeIn(brain_red), FadeIn(red_label), run_time=0.5); t += 0.5
        self.play(Flash(brain_red.get_center(), color=FEAR_RED, line_length=0.3, num_lines=8, run_time=0.3)); t += 0.3
        self.play(brain_gold.animate.set_opacity(0.05), gold_label.animate.set_opacity(0.2), run_time=0.5); t += 0.5
        self.play(FadeIn(footer), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 12.6)
        self.wait(max(0.1, target - t - 0.3))
        validate_layout(self)


class Scene5_Scale(Scene):
    DURATION = 8.6
    def construct(self):
        setup_bg(self)
        t = 0
        pill = scene_label("THE SCALE")
        safe_place(pill, "TITLE")
        people = svg_grid("person.svg", 7, 7, color=MATH_GOLD, icon_height=0.55,
                          spacing_x=0.85, spacing_y=0.85, opacity=0.6)
        safe_place(people, 1.5)
        millions = safe_text("MILLIONS", font="Bebas Neue", font_size=80, color=FEAR_RED)
        safe_place(millions, "LOWER")
        not_brains = safe_text("Not because of their brains.", font="Inter", font_size=28, color=DIM)
        not_brains.next_to(millions, DOWN, buff=0.3)
        origin = safe_text("Because of a sentence in 3rd grade.", font="Inter", font_size=24, color=FEAR_RED)
        safe_place(origin, "FOOTER")
        self.play(FadeIn(pill), run_time=0.3); t += 0.3
        self.play(LaggedStart(*[FadeIn(p, scale=0.3) for p in people], lag_ratio=0.003), run_time=0.6); t += 0.6
        self.wait(0.6); t += 0.6
        gray_half = list(people)[:24]
        anim = icon_state_change(gray_half, DIM, stagger=0.015)
        self.play(anim, run_time=1.5); t += 1.5
        self.wait(1.5); t += 1.5
        self.play(FadeIn(millions, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(millions.get_center(), color=FEAR_RED, line_length=0.4, num_lines=10, run_time=0.3)); t += 0.3
        self.play(FadeIn(not_brains), run_time=0.3); t += 0.3
        self.wait(2.4); t += 2.4
        self.play(FadeIn(origin, shift=UP * 0.1), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 8.6)
        self.wait(max(0.1, target - t - 0.3))
        validate_layout(self)


class Scene6_Punch(Scene):
    DURATION = 8.7
    def construct(self):
        setup_bg(self, opacity=0.02)
        t = 0
        bh = 1.2
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1, stroke_width=0).to_edge(UP, buff=0),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1, stroke_width=0).to_edge(DOWN, buff=0),
        )
        broken = Circle(radius=1.3, fill_color=BRAIN_GRAY, fill_opacity=0.2,
                       stroke_color=DIM, stroke_width=2)
        broken.move_to(LEFT * 2 + UP * 2.5)
        x_l = Line(LEFT * 0.8 + UP * 0.8, RIGHT * 0.8 + DOWN * 0.8, color=FEAR_RED, stroke_width=4).move_to(broken)
        x_r = Line(RIGHT * 0.8 + UP * 0.8, LEFT * 0.8 + DOWN * 0.8, color=FEAR_RED, stroke_width=4).move_to(broken)
        broken_x = VGroup(x_l, x_r)
        broken_lbl = safe_text("LABELED", font="Inter", font_size=22, color=FEAR_RED, weight="BOLD")
        broken_lbl.next_to(broken, DOWN, buff=0.3)
        active = Circle(radius=1.3, fill_color=MATH_GOLD, fill_opacity=0.15,
                       stroke_color=MATH_GOLD, stroke_width=2)
        active.move_to(RIGHT * 2 + UP * 2.5)
        active_lbl = safe_text("UNLABELED", font="Inter", font_size=22, color=MATH_GOLD, weight="BOLD")
        active_lbl.next_to(active, DOWN, buff=0.3)
        d = divider(color=MATH_GOLD)
        safe_place(d, "MID")
        restored_lbl = safe_text("THE LABEL WAS REMOVABLE.", font="Bebas Neue", font_size=50, color=MATH_GOLD)
        safe_place(restored_lbl, "LOWER")
        self.play(FadeIn(broken), FadeIn(broken_x), FadeIn(broken_lbl), run_time=0.5); t += 0.5
        self.play(FadeIn(active), FadeIn(active_lbl), run_time=0.5); t += 0.5
        self.play(Create(d), run_time=0.3); t += 0.3
        self.wait(2.7); t += 2.7
        self.play(FadeOut(broken_x), run_time=0.8); t += 0.8
        self.play(broken.animate.set_stroke(MATH_GOLD).set_fill(MATH_GOLD, opacity=0.15),
                  broken_lbl.animate.set_color(MATH_GOLD), run_time=1.0)
        self.play(broken.animate.set_fill(MATH_GOLD, opacity=0.2),
                  active.animate.set_fill(MATH_GOLD, opacity=0.2), run_time=0.4)
        self.play(FadeIn(restored_lbl, shift=UP * 0.1), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 8.7)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.0); t += 1.0
        validate_layout(self)


SCENES = [Scene1_Hook, Scene2_WrongAnswer, Scene3_Contradiction,
          Scene4_Proof, Scene5_Scale, Scene6_Punch]

def render_single_scene(idx):
    config.output_file = f"born_to_count_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    SCENES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"born_to_count_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENES):
        n = f"born_to_count_scene_{i+1}"; print(f"  Preview {n}...")
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
    if "--preview" in sys.argv:
        render_previews()
        try:
            from render_utils import run_preview_qa
            run_preview_qa(od / "previews")
        except ImportError:
            pass
        sys.exit(0)
    if "--scene" in sys.argv:
        timings_json = os.environ.get("TKK_SCENE_TIMINGS")
        if timings_json:
            _idx = int(sys.argv[sys.argv.index("--scene")+1])
            SCENES[_idx].DURATION = json.loads(timings_json)[_idx]
        render_single_scene(int(sys.argv[sys.argv.index("--scene")+1])); sys.exit(0)

    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_born_to_count.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="born_to_count", audio_path=str(audio))
    final = od / "born_to_count_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
    try:
        from render_utils import run_post_render_qa
        run_post_render_qa(str(final), scene_count=6)
    except ImportError:
        pass
