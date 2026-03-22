#!/usr/bin/env python3
"""The Number Zero — banned, feared, foundation of everything.

6 scenes, ~63s (60.7s audio + 2.3s hold).
Domain shapes: cuneiform_tablet, zero_glyph, roman_numeral_block, binary_stream.

VTT cues (absolute):
  Scene 1 (0.0–8.5s):   0.10 every number... 3.82 zero... 8.52 outlawed
  Scene 2 (8.5–19.5s):  12.72 babylonians... 17.30 never called it
  Scene 3 (19.5–33.0s): 21.76 india... 25.89 brahmagupta... 32.82 from nothing
  Scene 4 (33.0–45.0s): 34.50 europe panicked... 39.56 banned... 45.08 roman numerals
  Scene 5 (45.0–57.0s): 46.82 zero won... 50.72 computers... 54.95 binary
  Scene 6 (57.0–63.0s): 56.90 most powerful... means nothing
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
VOID_PURPLE = "#7C3AED"; DANGER_RED = "#EF4444"; INDIA_GOLD = "#FFD700"
BINARY_GREEN = "#22C55E"; CHURCH_GRAY = "#6B7280"; DIM = "#4A5568"
WHITE_SOFT = "#F0F0F0"; MUTED = "#7B8DA0"; WARM_AMBER = "#D97706"
ZERO_BLUE = "#3B82F6"

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

def label_pill(txt, color=INDIA_GOLD, bg=SURFACE, fs=24):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > 3.0: t.scale(3.0/t.width)
    p = RoundedRectangle(width=t.width+0.3, height=t.height+0.2, corner_radius=0.1,
                         fill_color=bg, fill_opacity=0.9, stroke_width=0).move_to(t)
    return VGroup(p, t)

def big_zero(r=2.5, col=VOID_PURPLE):
    return Circle(radius=r, stroke_color=col, stroke_width=6, fill_color=col, fill_opacity=0.05)

def cuneiform_marks(n=5):
    """Stylized cuneiform-like wedge marks."""
    g = VGroup()
    for i in range(n):
        w = Polygon(
            np.array([0, 0.3, 0]), np.array([-0.08, 0, 0]), np.array([0.08, 0, 0]),
            fill_color=WARM_AMBER, fill_opacity=0.7, stroke_width=0
        ).move_to(RIGHT*(i*0.4 - n*0.2))
        g.add(w)
    return g


class Scene1_Hook(Scene):
    DURATION = 8.5
    """Hook: banned number, zero, dangerous."""
    def construct(self):
        self.add(gradient_bg(), grid_lines())
        t = 0
        pill = label_pill("THE BANNED NUMBER", color=DANGER_RED, fs=22); safe_place(pill, "TITLE")

        zero = big_zero(2.0, VOID_PURPLE); safe_place(zero, "UPPER")
        zero_lbl = safe_text("0", font="Bebas Neue", font_size=200, color=VOID_PURPLE)
        zero_lbl.move_to(zero)

        hook = safe_text("BANNED.", font="Bebas Neue", font_size=90, color=DANGER_RED)
        safe_place(hook, "MID")

        sub1 = safe_text("Not a placeholder. Not nothing.", font="Inter", font_size=28, color=MUTED, weight="BOLD")
        safe_place(sub1, "LOWER")

        sub2 = safe_text("Entire civilizations outlawed it.", font="Inter", font_size=26, color=DIM, weight="BOLD")
        safe_place(sub2, "FOOTER")

        self.play(FadeIn(pill), run_time=0.3); t += 0.3
        self.play(GrowFromCenter(zero), run_time=0.6); t += 0.6
        self.play(FadeIn(zero_lbl, scale=1.3), run_time=0.5); t += 0.5
        self.wait(0.8); t += 0.8
        self.play(FadeIn(hook, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(hook.get_center(), color=DANGER_RED, line_length=0.4, num_lines=8, run_time=0.3)); t += 0.3
        self.wait(0.6); t += 0.6
        self.play(FadeIn(sub1, shift=UP*0.04), run_time=0.4); t += 0.4
        self.wait(0.5); t += 0.5
        self.play(FadeIn(sub2, shift=UP*0.04), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 8.5)
        self.wait(max(0.1, target - t - 0.3))
        validate_layout(self)


class Scene2_Babylon(Scene):
    DURATION = 11.0
    """Babylonians had a gap but never named it."""
    def construct(self):
        self.add(gradient_bg(), grid_lines())
        t = 0
        pill = label_pill("THE GAP", color=WARM_AMBER, fs=22); safe_place(pill, "TITLE")

        # Cuneiform number row with a gap
        marks_left = cuneiform_marks(3); marks_left.move_to(LEFT*2.5+UP*ZONE_UPPER)
        gap = DashedVMobject(
            Circle(radius=0.25, stroke_color=WARM_AMBER, stroke_width=2),
            num_dashes=8
        ).move_to(UP*ZONE_UPPER)
        marks_right = cuneiform_marks(2); marks_right.move_to(RIGHT*2.5+UP*ZONE_UPPER)

        date = safe_text("~300 BC", font="Bebas Neue", font_size=60, color=WARM_AMBER)
        safe_place(date, 4.8)

        explain = safe_text("A SPACE.", font="Bebas Neue", font_size=70, color=WHITE_SOFT)
        safe_place(explain, "MID")
        explain_sub = safe_text("Where a number should be.", font="Inter", font_size=28, color=MUTED, weight="BOLD")
        explain_sub.next_to(explain, DOWN, buff=0.3)

        verdict = safe_text("NEVER A NUMBER.", font="Bebas Neue", font_size=60, color=DANGER_RED)
        safe_place(verdict, "LOWER")
        verdict_sub = safe_text("Just a gap in the clay.", font="Inter", font_size=24, color=DIM, weight="BOLD")
        safe_place(verdict_sub, "FOOTER")

        self.play(FadeIn(pill), run_time=0.3); t += 0.3
        self.play(FadeIn(date), run_time=0.4); t += 0.4
        self.play(LaggedStart(FadeIn(marks_left), FadeIn(gap), FadeIn(marks_right), lag_ratio=0.15), run_time=0.6); t += 0.6
        self.wait(1.2); t += 1.2
        self.play(FadeIn(explain, shift=UP*0.1), run_time=0.5); t += 0.5
        self.play(FadeIn(explain_sub), run_time=0.3); t += 0.3
        self.wait(1.5); t += 1.5
        self.play(FadeIn(verdict, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(verdict.get_center(), color=DANGER_RED, line_length=0.3, num_lines=6, run_time=0.2)); t += 0.2
        self.play(FadeIn(verdict_sub, shift=UP*0.04), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 11.0)
        self.wait(max(0.1, target - t - 0.3))
        validate_layout(self)


class Scene3_India(Scene):
    DURATION = 13.5
    """India: Brahmagupta wrote the rules of zero."""
    def construct(self):
        self.add(gradient_bg(), grid_lines())
        t = 0
        pill = label_pill("THE BREAKTHROUGH", color=INDIA_GOLD, fs=22); safe_place(pill, "TITLE")

        date = safe_text("628 AD", font="Bebas Neue", font_size=80, color=INDIA_GOLD)
        safe_place(date, "UPPER")

        name = safe_text("BRAHMAGUPTA", font="Bebas Neue", font_size=65, color=WHITE_SOFT)
        name.next_to(date, DOWN, buff=0.4)

        # Rules of zero
        rules = VGroup()
        rule_data = [("0 + 0 = 0", INDIA_GOLD), ("0 × n = 0", INDIA_GOLD), ("n − n = 0", INDIA_GOLD)]
        for i, (txt, col) in enumerate(rule_data):
            r = safe_text(txt, font="JetBrains Mono", font_size=48, color=col)
            r.move_to(UP*(ZONE_MID + 1 - i*1.2))
            rules.add(r)

        punch = safe_text("A NUMBER FROM NOTHING.", font="Bebas Neue", font_size=50, color=INDIA_GOLD)
        safe_place(punch, "LOWER")
        sub = safe_text("The first time zero had rules.", font="Inter", font_size=24, color=MUTED, weight="BOLD")
        safe_place(sub, "FOOTER")

        self.play(FadeIn(pill), run_time=0.3); t += 0.3
        self.play(FadeIn(date, scale=1.1), run_time=0.5); t += 0.5
        self.play(FadeIn(name, shift=UP*0.1), run_time=0.4); t += 0.4
        self.wait(1.0); t += 1.0
        self.play(LaggedStart(*[FadeIn(r, shift=LEFT*0.2) for r in rules], lag_ratio=0.2), run_time=0.8); t += 0.8
        self.wait(1.5); t += 1.5
        self.play(FadeIn(punch, scale=1.08), run_time=0.5); t += 0.5
        self.play(Flash(punch.get_center(), color=INDIA_GOLD, line_length=0.3, num_lines=8, run_time=0.3)); t += 0.3
        self.play(FadeIn(sub, shift=UP*0.04), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 13.5)
        self.wait(max(0.1, target - t - 0.3))
        validate_layout(self)


class Scene4_Europe(Scene):
    DURATION = 12.0
    """Europe panicked. Church, Florence ban, Roman numerals."""
    def construct(self):
        self.add(gradient_bg(), grid_lines())
        t = 0
        pill = label_pill("THE BAN", color=DANGER_RED, fs=22); safe_place(pill, "TITLE")

        panic = safe_text("EUROPE PANICKED.", font="Bebas Neue", font_size=70, color=DANGER_RED)
        safe_place(panic, "UPPER")

        church = safe_text("The Church called it the void.", font="Inter", font_size=30, color=CHURCH_GRAY, weight="BOLD")
        church.next_to(panic, DOWN, buff=0.5)

        ban_date = safe_text("1299", font="Bebas Neue", font_size=100, color=DANGER_RED)
        safe_place(ban_date, "MID")
        ban_city = safe_text("FLORENCE BANNED ZERO.", font="Inter", font_size=28, color=WHITE_SOFT, weight="BOLD")
        ban_city.next_to(ban_date, DOWN, buff=0.3)

        # Roman numerals comparison
        roman = safe_text("XLVII ÷ IX = ?", font="JetBrains Mono", font_size=44, color=CHURCH_GRAY)
        safe_place(roman, "LOWER")
        taunt = safe_text("Try dividing with Roman numerals.", font="Inter", font_size=26, color=MUTED, weight="BOLD")
        safe_place(taunt, "FOOTER")

        self.play(FadeIn(pill), run_time=0.3); t += 0.3
        self.play(FadeIn(panic, scale=1.1), run_time=0.5); t += 0.5
        self.wait(1.0); t += 1.0
        self.play(FadeIn(church, shift=UP*0.04), run_time=0.4); t += 0.4
        self.wait(1.0); t += 1.0
        self.play(FadeIn(ban_date, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(ban_date.get_center(), color=DANGER_RED, line_length=0.5, num_lines=8, run_time=0.3)); t += 0.3
        self.play(FadeIn(ban_city), run_time=0.3); t += 0.3
        self.wait(1.0); t += 1.0
        self.play(FadeIn(roman, shift=LEFT*0.2), run_time=0.4); t += 0.4
        self.play(FadeIn(taunt, shift=UP*0.04), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 12.0)
        self.wait(max(0.1, target - t - 0.3))
        validate_layout(self)


class Scene5_Victory(Scene):
    DURATION = 12.0
    """Zero won. Calculus, computers, binary."""
    def construct(self):
        self.add(gradient_bg(), grid_lines())
        t = 0
        pill = label_pill("ZERO WON", color=BINARY_GREEN, fs=22); safe_place(pill, "TITLE")

        won = safe_text("ZERO WON.", font="Bebas Neue", font_size=80, color=BINARY_GREEN)
        safe_place(won, "UPPER")

        # Stack: calculus, computers, binary
        items = VGroup()
        item_data = [
            ("CALCULUS REQUIRES IT.", ZERO_BLUE),
            ("COMPUTERS RUN ON IT.", BINARY_GREEN),
            ("EVERY SCREEN. EVERY TRANSACTION.", WHITE_SOFT),
        ]
        for i, (txt, col) in enumerate(item_data):
            lbl = safe_text(txt, font="Bebas Neue", font_size=42, color=col)
            lbl.move_to(UP*(ZONE_MID + 1.2 - i*1.2))
            items.add(lbl)

        # Binary stream
        np.random.seed(42)
        binary_str = "".join([str(np.random.randint(0,2)) for _ in range(30)])
        binary = safe_text(binary_str, font="JetBrains Mono", font_size=32, color=BINARY_GREEN)
        binary.set_opacity(0.6)
        safe_place(binary, "LOWER")

        ones_zeros = safe_text("ONES AND ZEROS.", font="Bebas Neue", font_size=55, color=BINARY_GREEN)
        safe_place(ones_zeros, "FOOTER")

        self.play(FadeIn(pill), run_time=0.3); t += 0.3
        self.play(FadeIn(won, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(won.get_center(), color=BINARY_GREEN, line_length=0.3, num_lines=6, run_time=0.2)); t += 0.2
        self.wait(0.6); t += 0.6
        self.play(LaggedStart(*[FadeIn(t, shift=LEFT*0.15) for t in items], lag_ratio=0.2), run_time=0.8); t += 0.8
        self.wait(1.5); t += 1.5
        self.play(FadeIn(binary, shift=RIGHT*0.3), run_time=0.4); t += 0.4
        self.wait(1.0); t += 1.0
        self.play(FadeIn(ones_zeros, scale=1.08), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 12.0)
        self.wait(max(0.1, target - t - 0.3))
        validate_layout(self)


class Scene6_Punch(Scene):
    DURATION = 6.0
    """The most powerful number means nothing."""
    def construct(self):
        self.add(gradient_bg())
        t = 0
        bh = 1.2
        self.add(Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1, stroke_width=0).to_edge(UP, buff=0),
                 Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1, stroke_width=0).to_edge(DOWN, buff=0))

        zero = big_zero(2.5, VOID_PURPLE); safe_place(zero, "UPPER")
        zero_lbl = safe_text("0", font="Bebas Neue", font_size=250, color=VOID_PURPLE)
        zero_lbl.move_to(zero)

        line1 = safe_text("The most powerful number", font="DM Serif Display", font_size=40, color=WHITE_SOFT)
        safe_place(line1, "MID")
        line2 = safe_text("is the one that means nothing.", font="DM Serif Display", font_size=38, color=MUTED)
        line2.next_to(line1, DOWN, buff=0.4)

        self.play(GrowFromCenter(zero), run_time=0.8); t += 0.8
        self.play(FadeIn(zero_lbl, scale=1.2), run_time=0.6); t += 0.6
        self.wait(0.5); t += 0.5
        self.play(FadeIn(line1, shift=UP*0.04), run_time=0.6); t += 0.6
        self.wait(0.4); t += 0.4
        self.play(FadeIn(line2, shift=UP*0.04), run_time=0.6); t += 0.6
        target = getattr(self.__class__, 'DURATION', 6.0)
        self.wait(max(0.1, target - t - 0.8))
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0); t += 1.0
        self.play(FadeIn(Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)), run_time=0.5); t += 0.5
        validate_layout(self)


SCENES = [Scene1_Hook, Scene2_Babylon, Scene3_India, Scene4_Europe, Scene5_Victory, Scene6_Punch]

def render_single_scene(idx):
    config.output_file = f"zero_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    SCENES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"zero_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENES):
        n = f"zero_scene_{i+1}"; print(f"  Preview {n}...")
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
    audio = od / "tts_zero.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="zero", audio_path=str(audio))
    final = od / "zero_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
    try:
        from render_utils import run_post_render_qa
        run_post_render_qa(str(final), scene_count=6)
    except ImportError: pass
