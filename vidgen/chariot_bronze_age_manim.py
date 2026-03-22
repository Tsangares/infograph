#!/usr/bin/env python3
"""The Chariot Changed Everything — TikTok Mystery/Reveal (Manim).

6 scenes, ~44s total (synced to TTS audio).
Domain shapes: solid_wheel, spoked_wheel, chariot_silhouette, steppe_horizon.
Visual throughline: heavy solid wheel → light spoked wheel — the upgrade that broke history.

VTT cues (from silence-detection on tts_chariot_bronze_age.mp3):
  Scene 1 (0.0–4.5s):    "The wheel changed civilization. Everyone knows that."
  Scene 2 (5.1–10.5s):   "But there's a problem. The wheel existed for 1,500 years before anyone figured out what to really do with it."
  Scene 3 (10.9–21.3s):  "Around 2100 BC, steppe nomads in the Sintashta culture — southern Urals — invented the spoked-wheel chariot. Light. Fast. Devastating."
  Scene 4 (21.6–29.0s):  "Within 500 years, chariots appeared in Egypt, China, Greece, and India. The people who invented them migrated south. They became the Persians."
  Scene 5 (29.5–35.7s):  "One invention. One steppe culture. The Persian Empire. Vedic India. Half of Europe's languages."
  Scene 6 (36.1–44.1s):  "The Bronze Age didn't end because of drought or plague. It ended because some nomads put spokes on a wheel."
"""

TTS_SCRIPT = """
The wheel changed civilization. Everyone knows that.
But there's a problem. The wheel existed for 1,500 years before anyone figured out what to really do with it.
Around 2100 BC, steppe nomads in the Sintashta culture — southern Urals — invented the spoked-wheel chariot. Light. Fast. Devastating.
Within 500 years, chariots appeared in Egypt, China, Greece, and India. The people who invented them migrated south. They became the Persians.
One invention. One steppe culture. The Persian Empire. Vedic India. Half of Europe's languages.
The Bronze Age didn't end because of drought or plague. It ended because some nomads put spokes on a wheel.
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from manim import (
    Scene, Text, VGroup, Group, Rectangle, RoundedRectangle, Circle,
    Line, Arrow, Dot, Polygon,
    FadeIn, FadeOut, GrowFromCenter, Create, GrowArrow,
    LaggedStart, Flash,
    config, UP, DOWN, LEFT, RIGHT, ORIGIN,
    WHITE, BLACK, DEGREES, PI,
)
import numpy as np

config.pixel_width  = 1080
config.pixel_height = 1920
config.frame_rate   = 30
config.frame_width  = 9
config.frame_height = 16
config.background_color = "#080A10"
config.disable_caching  = True

BG         = "#080A10"
GRID       = "#1A2030"
SURFACE    = "#15192A"
WHITE_SOFT = "#F0F0F0"
MUTED      = "#7B8DA0"
DIM        = "#4A5568"
GOLD       = "#FFD700"
GOLD_DIM   = "#B8960F"
RUST       = "#C0532A"   # solid wheel — heavy, old
BLADE      = "#D8D0C0"   # spoked wheel — precise, deadly
STEPPE     = "#8B7355"   # earth tone

SAFE_W    = 8.0
SAFE_TOP  = 7.2
SAFE_BOT  = -6.4

ZONE_TITLE  =  6.2
ZONE_UPPER  =  3.5
ZONE_MID    =  0.0
ZONE_LOWER  = -3.5
ZONE_FOOTER = -6.0


# ── Core helpers ──────────────────────────────────────────────

def gradient_bg(c=BG, g="#121828"):
    bg   = Rectangle(width=12, height=20, fill_color=c, fill_opacity=1, stroke_width=0)
    glow = Circle(radius=5, fill_color=g, fill_opacity=0.08, stroke_width=0).move_to(UP * 2)
    return VGroup(bg, glow)

def grid_lines(opacity=0.04):
    lines = VGroup()
    for i in range(13):
        y = -8 + i * 16 / 12
        lines.add(Line(LEFT*5, RIGHT*5, color=GRID, stroke_width=0.5).move_to(UP*y).set_opacity(opacity))
    for j in range(7):
        x = -4.5 + j * 9 / 6
        lines.add(Line(DOWN*8, UP*8, color=GRID, stroke_width=0.5).move_to(RIGHT*x).set_opacity(opacity))
    return lines

def safe_text(content, **kwargs):
    t = Text(content, **kwargs)
    if t.width > SAFE_W:
        t.scale(SAFE_W / t.width)
    return t

def label_pill(txt, color=GOLD, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W:
        t.scale(SAFE_W / t.width)
    p = RoundedRectangle(width=t.width+0.5, height=t.height+0.3, corner_radius=0.15,
                         fill_color=bg, fill_opacity=0.9, stroke_width=0).move_to(t)
    return VGroup(p, t)


# ── Domain shapes ─────────────────────────────────────────────

def solid_wheel(r=1.5):
    """Primitive solid disk wheel — Mesopotamia, 3500 BC. Heavy. Slow."""
    rim  = Circle(radius=r, fill_color=RUST, fill_opacity=0.85,
                  stroke_color="#8B3A1E", stroke_width=4)
    hub  = Circle(radius=r * 0.13, fill_color="#5A2010", fill_opacity=1,
                  stroke_color="#3A1008", stroke_width=2)
    axle = Circle(radius=r * 0.06, fill_color=BG, fill_opacity=1, stroke_width=0)
    # Radial grain lines — looks like a solid wood disc
    grains = VGroup()
    for i in range(4):
        angle = i * PI / 4
        grain = Line(
            np.array([np.cos(angle), np.sin(angle), 0]) * r * 0.15,
            np.array([np.cos(angle), np.sin(angle), 0]) * r * 0.82,
            color="#8B3A1E", stroke_width=1.5
        )
        grains.add(grain)
    return VGroup(rim, grains, hub, axle)

def spoked_wheel(r=1.5, n=6):
    """Sintashta spoked-wheel — 2100 BC. Light. Fast. Deadly."""
    rim    = Circle(radius=r, fill_color=BG, fill_opacity=0,
                    stroke_color=BLADE, stroke_width=5)
    hub    = Circle(radius=r * 0.13, fill_color=BLADE, fill_opacity=1, stroke_width=0)
    spokes = VGroup()
    for i in range(n):
        angle = i * PI * 2 / n
        end   = np.array([np.cos(angle), np.sin(angle), 0]) * r * 0.90
        spokes.add(Line(ORIGIN, end, color=BLADE, stroke_width=3))
    return VGroup(rim, spokes, hub)

def chariot_silhouette(wheel_r=0.6):
    """Side-view chariot: spoked wheel + platform + harness pole."""
    wheel    = spoked_wheel(r=wheel_r, n=6)
    wheel.move_to(LEFT * 0.4 + DOWN * wheel_r * 0.8)
    platform = Rectangle(width=2.0, height=0.22, fill_color=STEPPE,
                         fill_opacity=0.9, stroke_width=0)
    platform.move_to(RIGHT * 0.2 + DOWN * 0.1)
    pole     = Line(RIGHT * 1.0, RIGHT * 2.6 + DOWN * 0.3, color=STEPPE, stroke_width=2)
    return VGroup(wheel, platform, pole)

def steppe_horizon(width=9.0):
    """Low undulating horizon line — the Eurasian steppe."""
    rng = np.random.default_rng(42)
    pts = [[-width / 2, 0, 0]]
    n_segs = 8
    seg_w  = width / n_segs
    for i in range(n_segs):
        x0  = -width / 2 + i * seg_w
        mid = x0 + seg_w * 0.5
        h   = rng.uniform(0.05, 0.3)
        pts.append([mid, h, 0])
        pts.append([x0 + seg_w, 0, 0])
    pts += [[width / 2, -0.6, 0], [-width / 2, -0.6, 0]]
    return Polygon(*pts, fill_color=STEPPE, fill_opacity=0.45,
                   stroke_color="#6B5540", stroke_width=1)


# ── Scenes ────────────────────────────────────────────────────

class Scene1_WrongAnswer(Scene):
    DURATION = 4.5  # fallback; overridden by TTS timing when available
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # TITLE zone
        pill = label_pill("THE WRONG ANSWER", color=RUST, bg="#1A0A08")
        pill.move_to(UP * ZONE_TITLE)
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4

        # UPPER — date
        date = safe_text("3500 BC", font="Bebas Neue", font_size=54, color=DIM)
        date.move_to(UP * ZONE_UPPER)
        self.play(FadeIn(date, shift=DOWN * 0.2), run_time=0.4); t += 0.4

        # MID — solid disk wheel, the "obvious" answer
        wheel = solid_wheel(r=2.2)
        wheel.move_to(UP * ZONE_MID)
        self.play(GrowFromCenter(wheel), run_time=0.7); t += 0.7

        # Wheel turns slowly — plodding, agricultural
        self.play(wheel.animate.rotate(PI / 5), run_time=1.3); t += 1.3

        # LOWER — place label
        place = safe_text("MESOPOTAMIA", font="Inter", font_size=34,
                          color=MUTED, weight="BOLD")
        place.move_to(UP * ZONE_LOWER)
        self.play(FadeIn(place, shift=UP * 0.2), run_time=0.4); t += 0.4

        # FOOTER — uses
        uses = safe_text("agriculture  ·  trade  ·  pottery", font="Inter",
                         font_size=26, color=DIM)
        uses.move_to(UP * ZONE_FOOTER)
        self.play(FadeIn(uses), run_time=0.3); t += 0.3

        target = getattr(self.__class__, 'DURATION', 4.5)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:])), run_time=0.3)


class Scene2_Contradiction(Scene):
    DURATION = 6.0  # fallback
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # TITLE
        pill = label_pill("THE CONTRADICTION", color=GOLD)
        pill.move_to(UP * ZONE_TITLE)
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4

        # Vertical timeline running UPPER → LOWER
        tl_top = UP * 4.8
        tl_bot = DOWN * 2.8
        tl_line = Line(tl_top, tl_bot, color=DIM, stroke_width=2)
        self.play(Create(tl_line), run_time=0.5); t += 0.5

        # Dot 1 — solid wheel, 3500 BC
        dot1 = Dot(tl_top, radius=0.13, color=RUST)
        lbl1 = safe_text("3500 BC", font="Bebas Neue", font_size=48, color=RUST)
        lbl1.next_to(dot1, RIGHT, buff=0.3)
        w1   = solid_wheel(r=0.5)
        w1.next_to(lbl1, RIGHT, buff=0.3)
        self.play(FadeIn(dot1), FadeIn(lbl1), FadeIn(w1, scale=1.1), run_time=0.4); t += 0.4

        # MID — "1,500 YEARS" gap label
        gap = safe_text("1,500 YEARS", font="Bebas Neue", font_size=84, color=GOLD)
        gap.move_to(UP * ZONE_MID + LEFT * 0.3)
        sub = safe_text("of nothing", font="DM Serif Display", font_size=36, color=MUTED)
        sub.next_to(gap, DOWN, buff=0.15)
        self.wait(0.2); t += 0.2
        self.play(FadeIn(gap, scale=1.05), run_time=0.5); t += 0.5
        self.play(FadeIn(sub, shift=UP * 0.15), run_time=0.4); t += 0.4

        # Dot 2 — spoked wheel, 2100 BC
        dot2 = Dot(tl_bot, radius=0.13, color=BLADE)
        lbl2 = safe_text("2100 BC", font="Bebas Neue", font_size=48, color=BLADE)
        lbl2.next_to(dot2, RIGHT, buff=0.3)
        w2   = spoked_wheel(r=0.5, n=6)
        w2.next_to(lbl2, RIGHT, buff=0.3)
        self.play(FadeIn(dot2), FadeIn(lbl2), FadeIn(w2, scale=1.1), run_time=0.4); t += 0.4

        # FOOTER
        footer = safe_text("SINTASHTA CULTURE", font="Inter", font_size=26,
                           color=DIM, weight="BOLD")
        footer.move_to(UP * ZONE_FOOTER)
        self.play(FadeIn(footer), run_time=0.3); t += 0.3

        target = getattr(self.__class__, 'DURATION', 6.0)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:])), run_time=0.3)


class Scene3_DismissedTruth(Scene):
    DURATION = 10.7  # fallback
    def construct(self):
        self.add(gradient_bg(c="#0A0E18", g="#1A2840"), grid_lines(0.04))
        t = 0

        # TITLE
        pill = label_pill("2100 BC  ·  SOUTHERN URALS", color=BLADE, bg="#0E1520", fs=24)
        pill.move_to(UP * ZONE_TITLE)
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4

        # UPPER — "SINTASHTA"
        name = safe_text("SINTASHTA", font="DM Serif Display", font_size=76, color=GOLD)
        name.move_to(UP * ZONE_UPPER)
        self.play(FadeIn(name, shift=DOWN * 0.2), run_time=0.5); t += 0.5

        # MID — large spoked wheel
        sw = spoked_wheel(r=2.0, n=6)
        sw.move_to(UP * ZONE_MID)
        self.play(GrowFromCenter(sw), run_time=0.6); t += 0.6
        # Spin fast — this thing moves
        self.play(sw.animate.rotate(PI * 0.8), run_time=0.7); t += 0.7

        # LOWER — three bullet words cascade in
        b1 = safe_text("LIGHT",       font="Bebas Neue", font_size=62, color=WHITE_SOFT)
        b2 = safe_text("FAST",        font="Bebas Neue", font_size=62, color=GOLD)
        b3 = safe_text("DEVASTATING", font="Bebas Neue", font_size=62, color=RUST)
        bullets = VGroup(b1, b2, b3).arrange(DOWN, buff=0.2)
        bullets.move_to(UP * ZONE_LOWER)
        self.play(LaggedStart(*[FadeIn(b, scale=1.06) for b in [b1, b2, b3]],
                              lag_ratio=0.25), run_time=0.9); t += 0.9

        # FOOTER — steppe
        horizon = steppe_horizon()
        horizon.move_to(UP * ZONE_FOOTER)
        self.play(FadeIn(horizon), run_time=0.4); t += 0.4

        target = getattr(self.__class__, 'DURATION', 10.7)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:])), run_time=0.3)


class Scene4_Proof(Scene):
    DURATION = 7.4  # fallback
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # TITLE
        pill = label_pill("THE PROOF", color=GOLD)
        pill.move_to(UP * ZONE_TITLE)
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4

        # UPPER — time label
        time_lbl = safe_text("500 YEARS LATER", font="Bebas Neue", font_size=64, color=GOLD_DIM)
        time_lbl.move_to(UP * ZONE_UPPER)
        self.play(FadeIn(time_lbl, shift=DOWN * 0.15), run_time=0.4); t += 0.4

        # MID — origin point with 4 arrows radiating out
        origin_pt  = UP * 1.2
        origin_dot = Dot(origin_pt, radius=0.18, color=BLADE)
        origin_lbl = safe_text("SINTASHTA", font="Inter", font_size=22,
                               color=BLADE, weight="BOLD")
        origin_lbl.next_to(origin_dot, UP, buff=0.15)
        self.play(FadeIn(origin_dot), FadeIn(origin_lbl), run_time=0.3); t += 0.3

        destinations = [
            ("EGYPT",  LEFT  * 3.2 + DOWN * 0.5,  GOLD),
            ("GREECE", LEFT  * 2.0 + DOWN * 2.6,  WHITE_SOFT),
            ("INDIA",  RIGHT * 3.2 + DOWN * 0.5,  GOLD),
            ("CHINA",  RIGHT * 1.8 + DOWN * 2.8,  MUTED),
        ]
        for d_name, offset, color in destinations:
            dest  = origin_pt + offset
            arrow = Arrow(
                origin_pt + offset * 0.12,
                dest * 0.85 + origin_pt * 0.15,
                color=color, stroke_width=2, max_tip_length_to_length_ratio=0.15
            )
            lbl = safe_text(d_name, font="Bebas Neue", font_size=46, color=color)
            lbl.move_to(dest + offset * 0.18)
            self.play(GrowArrow(arrow), FadeIn(lbl), run_time=0.35); t += 0.35

        # LOWER — three chariot silhouettes rolling across
        chariots = VGroup()
        for i in range(3):
            ch = chariot_silhouette(wheel_r=0.38)
            ch.move_to(UP * ZONE_LOWER + LEFT * 2.6 + RIGHT * i * 2.6)
            chariots.add(ch)
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.4) for c in chariots],
                              lag_ratio=0.2), run_time=0.6); t += 0.6

        # FOOTER — punch line
        footer = safe_text("THEY BECAME THE PERSIANS", font="DM Serif Display",
                           font_size=36, color=GOLD)
        footer.move_to(UP * ZONE_FOOTER)
        self.play(FadeIn(footer, scale=1.05), run_time=0.5); t += 0.5

        target = getattr(self.__class__, 'DURATION', 7.4)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:])), run_time=0.3)


class Scene5_Scale(Scene):
    DURATION = 6.6  # fallback
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # TITLE
        pill = label_pill("ONE INVENTION", color=GOLD)
        pill.move_to(UP * ZONE_TITLE)
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4

        # UPPER — spoked wheel rotating
        sw = spoked_wheel(r=1.6, n=8)
        sw.move_to(UP * ZONE_UPPER)
        self.play(GrowFromCenter(sw), run_time=0.5); t += 0.5
        self.play(sw.animate.rotate(PI / 3), run_time=0.5); t += 0.5

        # MID — two civilization names
        civ1 = safe_text("Persian Empire", font="DM Serif Display", font_size=52, color=GOLD)
        civ2 = safe_text("Vedic India",    font="DM Serif Display", font_size=52, color=WHITE_SOFT)
        civs = VGroup(civ1, civ2).arrange(DOWN, buff=0.35)
        civs.move_to(UP * ZONE_MID)
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.2) for c in [civ1, civ2]],
                              lag_ratio=0.4), run_time=0.7); t += 0.7

        # LOWER — "½ of Europe's languages" stat
        half = safe_text("½", font="Bebas Neue", font_size=130, color=GOLD)
        lang = safe_text("OF EUROPE'S LANGUAGES", font="Inter", font_size=28,
                         color=MUTED, weight="BOLD")
        stat = VGroup(half, lang).arrange(RIGHT, buff=0.35)
        stat.move_to(UP * ZONE_LOWER)
        self.play(FadeIn(half, scale=1.1), run_time=0.4); t += 0.4
        self.play(FadeIn(lang, shift=LEFT * 0.2), run_time=0.4); t += 0.4

        # FOOTER
        horizon = steppe_horizon()
        horizon.move_to(UP * ZONE_FOOTER)
        self.play(FadeIn(horizon), run_time=0.3); t += 0.3

        target = getattr(self.__class__, 'DURATION', 6.6)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:])), run_time=0.3)


class Scene6_Punch(Scene):
    DURATION = 8.3  # fallback
    def construct(self):
        self.add(gradient_bg(c="#060810", g="#0D1520"), grid_lines(0.02))
        t = 0

        # TITLE
        pill = label_pill("THE BRONZE AGE ENDED", color=RUST, bg="#180A06", fs=24)
        pill.move_to(UP * ZONE_TITLE)
        self.play(FadeIn(pill, scale=1.05), run_time=0.5); t += 0.5

        # UPPER — crossed-out conventional wisdom
        not_txt = safe_text("NOT DROUGHT.  NOT PLAGUE.", font="DM Serif Display",
                            font_size=40, color=DIM)
        not_txt.move_to(UP * ZONE_UPPER)
        strikethrough = Line(
            not_txt.get_left()  + LEFT  * 0.1,
            not_txt.get_right() + RIGHT * 0.1,
            color=RUST, stroke_width=3
        )
        self.play(FadeIn(not_txt), run_time=0.5); t += 0.5
        self.play(Create(strikethrough), run_time=0.4); t += 0.4

        # MID — large spoked wheel, the real answer
        sw = spoked_wheel(r=2.0, n=6)
        sw.move_to(UP * ZONE_MID)
        self.play(GrowFromCenter(sw), run_time=0.7); t += 0.7
        self.play(sw.animate.rotate(PI / 3), run_time=0.7); t += 0.7

        # LOWER — punch line, two lines slow reveal
        line1 = safe_text("Nomads.", font="DM Serif Display", font_size=56, color=WHITE_SOFT)
        line2 = safe_text("Spokes on a wheel.", font="DM Serif Display", font_size=56, color=GOLD)
        punch = VGroup(line1, line2).arrange(DOWN, buff=0.3)
        punch.move_to(UP * ZONE_LOWER)
        self.play(FadeIn(line1, shift=UP * 0.15), run_time=0.6); t += 0.6
        self.play(FadeIn(line2, shift=UP * 0.15), run_time=0.7); t += 0.7

        # FOOTER — steppe horizon fades in last
        horizon = steppe_horizon()
        horizon.move_to(UP * ZONE_FOOTER)
        self.play(FadeIn(horizon), run_time=0.4); t += 0.4

        target = getattr(self.__class__, 'DURATION', 8.3)
        self.wait(max(0.1, target - t - 0.8))  # 0.8 = fade-to-black run_time

        # Slow fade to black
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=0, stroke_width=0)
        self.add(black)
        self.play(black.animate.set_fill(opacity=1), run_time=0.8)


# ── Infra ──────────────────────────────────────────────────────

SCENES = [
    Scene1_WrongAnswer,
    Scene2_Contradiction,
    Scene3_DismissedTruth,
    Scene4_Proof,
    Scene5_Scale,
    Scene6_Punch,
]

def render_single_scene(idx):
    config.output_file = f"chariot_bronze_age_scene_{idx + 1}"
    config.media_dir   = str(Path(__file__).parent / "media")
    SCENES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"chariot_bronze_age_scene_{idx + 1}.mp4"):
        print(f"SCENE_FILE:{mp4}")
        return

def render_previews():
    d = Path(__file__).parent / "previews"
    d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENES):
        n = f"chariot_bronze_age_scene_{i + 1}"
        print(f"  Preview {n}...")
        config.output_file    = n
        config.save_last_frame = True
        config.format          = "png"
        S().render()
        for p in Path(config.media_dir).rglob(f"{n}*"):
            if p.suffix == ".png":
                dst = d / f"{n}.png"
                shutil.copy2(str(p), str(dst))
                print(f"  OK: {dst} ({dst.stat().st_size // 1024} KB)")
                break
    config.save_last_frame = False
    config.format          = None
    print(f"\nAll 6 previews → {d}/")

if __name__ == "__main__":
    import time, gc
    od = Path(__file__).parent

    if "--preview" in sys.argv:
        render_previews()
        from render_utils import run_preview_qa
        run_preview_qa(od / "previews")
        sys.exit(0)

    if "--scene" in sys.argv:
        idx = int(sys.argv[sys.argv.index("--scene") + 1])
        timings_json = os.environ.get("TKK_SCENE_TIMINGS")
        if timings_json:
            SCENES[idx].DURATION = json.loads(timings_json)[idx]
        render_single_scene(idx)
        sys.exit(0)

    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()

    audio = od / "tts_chariot_bronze_age.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="chariot_bronze_age",
                                   audio_path=str(audio))
    final = od / "chariot_bronze_age_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")

    from render_utils import run_post_render_qa
    run_post_render_qa(str(final), scene_count=6)
