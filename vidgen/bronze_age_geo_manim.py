#!/usr/bin/env python3
"""Bronze Age Collapse — GEO-ACCURATE hybrid (satellite map + manim infographic).

Uses geo_utils.GeoMap for verified lat/lon → manim coordinate conversion.
Map scenes use cropped eastern_med region from earth_topo.jpg.

Audio: tts_bronze_age.mp3 (46.3s, ELITE voice)
VTT: tts_bronze_age.vtt
"""

import os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Geo coordinate system
sys.path.insert(0, str(Path(__file__).parent))
from geo_utils import GeoMap
from geo_locations import LOCATIONS

from manim import (
    Scene, Text, VGroup, Rectangle, RoundedRectangle, Circle,
    Line, Arrow, DashedLine, Dot, Polygon, Ellipse, Square,
    FadeIn, FadeOut, GrowFromCenter, Write, Create, DrawBorderThenFill,
    AnimationGroup, LaggedStart, Flash, GrowArrow, ImageMobject,
    config, UP, DOWN, LEFT, RIGHT, ORIGIN,
    WHITE, BLACK, rate_functions, DEGREES, PI,
)
import numpy as np

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.frame_width = 9
config.frame_height = 16
config.background_color = "#050810"
config.disable_caching = True

BG = "#050810"; SURFACE = "#0C1420"
RED = "#E63946"; GOLD = "#FFD700"; GOLD_DIM = "#B8960F"
WHITE_SOFT = "#F0F0F0"; MUTED = "#7B8DA0"; DEAD_GRAY = "#4A5568"
BRONZE = "#CD7F32"; BRONZE_DIM = "#8B5A2B"; BRONZE_LIGHT = "#DDA15E"
FLAME = "#FF6B35"; ASH = "#6B6B6B"
SAFE_W = 8.0

# Initialize geo coordinate system
geo = GeoMap("eastern_med")

# Pre-compute all empire positions from real lat/lon
HATTUSA = geo.latlon_to_manim(*LOCATIONS["hattusa"])
MYCENAE = geo.latlon_to_manim(*LOCATIONS["mycenae"])
MEMPHIS = geo.latlon_to_manim(*LOCATIONS["memphis_egypt"])
BABYLON = geo.latlon_to_manim(*LOCATIONS["babylon"])
CYPRUS  = geo.latlon_to_manim(*LOCATIONS["cyprus"])
UGARIT  = geo.latlon_to_manim(*LOCATIONS["ugarit"])
TROY    = geo.latlon_to_manim(*LOCATIONS["troy"])

EMPIRES = {
    "HITTITES": {"pos": HATTUSA, "color": BRONZE},
    "MYCENAE":  {"pos": MYCENAE, "color": GOLD},
    "EGYPT":    {"pos": MEMPHIS, "color": GOLD_DIM},
    "BABYLON":  {"pos": BABYLON, "color": BRONZE_LIGHT},
}


def gradient_bg(c=BG):
    return Rectangle(width=12, height=20, fill_color=c, fill_opacity=1, stroke_width=0)

def dark_overlay(opacity=0.5):
    return Rectangle(width=12, height=20, fill_color=BG, fill_opacity=opacity, stroke_width=0)

def map_image():
    return geo.get_image_mobject(opacity=0.65)

def empire_marker(name, pos, color, radius=0.2):
    dot = Circle(radius=radius, fill_color=color, fill_opacity=0.85,
                 stroke_color=color, stroke_width=2)
    dot.move_to(pos)
    glow = Circle(radius=radius*2.5, fill_color=color, fill_opacity=0.10, stroke_width=0)
    glow.move_to(pos)
    lbl = Text(name, font="Inter", font_size=18, color=color, weight="BOLD")
    lbl.next_to(dot, DOWN, buff=0.12)
    if lbl.width > 1.8:
        lbl.scale(1.8 / lbl.width)
    return VGroup(glow, dot, lbl)

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

def ship_silhouette(width=0.7, color=MUTED):
    w, h = width, width * 0.6
    hull = Polygon(
        np.array([-w/2, 0, 0]), np.array([-w/3, -h*0.25, 0]),
        np.array([w/3, -h*0.25, 0]), np.array([w/2, 0, 0]),
        fill_color=color, fill_opacity=0.8, stroke_color=color, stroke_width=1)
    mast = Line(np.array([0, 0, 0]), np.array([0, h*0.5, 0]), color=color, stroke_width=1.5)
    sail = Polygon(np.array([0, h*0.45, 0]), np.array([w*0.25, h*0.2, 0]),
                   np.array([0, h*0.1, 0]), fill_color=color, fill_opacity=0.6, stroke_width=0)
    return VGroup(hull, mast, sail)


# ================================================================
# SCENE 1: THE HOOK — Geo-accurate map + empire markers (0.0–6.4s)
# ================================================================
class Scene1_Hook(Scene):
    def construct(self):
        self.add(gradient_bg())
        img = map_image()
        self.add(img)
        self.add(dark_overlay(0.35))

        pill = label_pill("1177 BC", color=RED, fs=32)
        pill.move_to(UP * 7.8 + RIGHT * 2.5)

        markers = {n: empire_marker(n, d["pos"], d["color"]) for n, d in EMPIRES.items()}

        # Additional markers for context
        ugarit_m = empire_marker("UGARIT", UGARIT, FLAME, 0.15)
        troy_m = empire_marker("TROY", TROY, MUTED, 0.15)

        pulse = Circle(radius=3.5, fill_color=RED, fill_opacity=0.0,
                       stroke_color=RED, stroke_width=3, stroke_opacity=0.5)
        pulse.move_to(geo.latlon_to_manim(34, 33))  # center of Eastern Med

        div = section_div(5, RED).move_to(DOWN * 2)
        collapsed = safe_text("COLLAPSED", font="Bebas Neue", font_size=100, color=RED)
        collapsed.move_to(DOWN * 3.5)
        same_time = safe_text("at the same time.", font="DM Serif Display",
                             font_size=44, color=WHITE_SOFT)
        same_time.move_to(DOWN * 5)

        # ── Timing: 6.40s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.5)
        self.play(
            LaggedStart(*[FadeIn(markers[n], scale=0.5) for n in EMPIRES],
                         lag_ratio=0.12),
            run_time=0.8,
        )
        self.play(FadeIn(ugarit_m, scale=0.5), FadeIn(troy_m, scale=0.5), run_time=0.4)
        self.wait(0.5)

        # Red pulse — simultaneous collapse
        self.play(FadeIn(pulse, scale=0.3), run_time=0.4)
        self.play(
            *[Flash(markers[n][1].get_center(), color=RED,
                    line_length=0.25, num_lines=6, run_time=0.3) for n in EMPIRES],
        )
        self.play(FadeOut(pulse), run_time=0.3)

        self.play(Create(div), run_time=0.3)
        self.play(FadeIn(collapsed, scale=1.15), run_time=0.7)
        self.play(Flash(collapsed.get_center(), color=RED,
                        line_length=0.5, num_lines=12, run_time=0.3))
        self.play(FadeIn(same_time, shift=UP * 0.06), run_time=0.6)
        self.wait(0.9)  # t=6.40


# ================================================================
# SCENE 2: SEA PEOPLES — Ships approaching from west (6.4–13.2s)
# ================================================================
class Scene2_SeaPeoples(Scene):
    def construct(self):
        self.add(gradient_bg())
        img = map_image()
        self.add(img)
        self.add(dark_overlay(0.45))

        pill = label_pill("THE SEA PEOPLES", color=FLAME, fs=26)
        pill.move_to(UP * 7.8 + RIGHT * 2.5)

        # Ships approaching from the west Mediterranean (left side of map)
        # Position them west of Greece, coming eastward
        ships = VGroup()
        west_sea = geo.latlon_to_manim(36, 15)  # west of Greece
        for dx, dy, w in [(-0.5, 0.3, 0.8), (0.2, 0.8, 0.6), (-0.8, -0.4, 0.7),
                          (0.5, -0.2, 0.5), (-1.0, 0.6, 0.6)]:
            s = ship_silhouette(w, "#6A4040")
            s.move_to(west_sea + np.array([dx, dy, 0]))
            ships.add(s)

        qmarks = VGroup()
        for s in ships:
            q = Text("?", font="Bebas Neue", font_size=26, color=FLAME)
            q.move_to(s.get_center() + UP * 0.4)
            qmarks.add(q)

        blame = safe_text("Textbooks blame them.", font="DM Serif Display",
                         font_size=42, color=MUTED)
        blame.move_to(DOWN * 0.5)
        div1 = section_div(5, FLAME).move_to(DOWN * 1.8)
        raiders = safe_text("Raiders who burned everything.", font="DM Serif Display",
                           font_size=40, color=FLAME)
        raiders.move_to(DOWN * 3)
        div2 = section_div(5, MUTED).move_to(DOWN * 4.3)
        nobody = safe_text("But no one knows", font="DM Serif Display",
                          font_size=44, color=WHITE_SOFT)
        nobody.move_to(DOWN * 5.5)
        who = safe_text("who they actually were.", font="DM Serif Display",
                       font_size=44, color=DEAD_GRAY)
        who.move_to(DOWN * 6.5)

        # ── Timing: 6.80s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3)
        self.play(FadeIn(blame, shift=UP * 0.04), run_time=0.5)
        self.play(
            LaggedStart(*[FadeIn(s, shift=RIGHT * 0.5) for s in ships], lag_ratio=0.08),
            run_time=0.8,
        )
        self.play(
            LaggedStart(*[FadeIn(q, scale=0.5) for q in qmarks], lag_ratio=0.06),
            run_time=0.4,
        )
        self.play(Create(div1), run_time=0.3)
        self.play(FadeIn(raiders, shift=UP * 0.06), run_time=0.6)
        self.wait(1.5)
        self.play(Create(div2), run_time=0.3)
        self.play(FadeIn(nobody, shift=UP * 0.06), run_time=0.6)
        self.play(FadeIn(who, shift=UP * 0.06), run_time=0.6)
        self.wait(0.9)  # t=6.80


# ================================================================
# SCENE 3: THE CHAIN — Supply chain + trade routes (13.2–20.9s)
# ================================================================
class Scene3_Chain(Scene):
    def construct(self):
        self.add(gradient_bg())
        img = map_image()
        self.add(img)
        self.add(dark_overlay(0.55))

        pill = label_pill("THE CHAIN", color=GOLD, fs=28)
        pill.move_to(UP * 7.8 + RIGHT * 2.5)

        # Empire names over their geographic positions
        emp_labels = []
        for name, data in [("HITTITES", EMPIRES["HITTITES"]),
                           ("MYCENAE", EMPIRES["MYCENAE"]),
                           ("EGYPT", EMPIRES["EGYPT"]),
                           ("BABYLON", EMPIRES["BABYLON"])]:
            t = Text(name, font="Bebas Neue", font_size=28, color=data["color"], weight="BOLD")
            t.move_to(data["pos"] + UP * 0.3)
            if t.width > 1.5: t.scale(1.5 / t.width)
            emp_labels.append(t)

        # Trade route arrows with geo positions
        cyprus_copper = geo.latlon_to_manim(*LOCATIONS["cyprus_copper"])
        egypt_grain = geo.latlon_to_manim(*LOCATIONS["egypt_grain"])

        # Trade lines connecting the network
        trade_lines = VGroup()
        connections = [
            (MYCENAE, UGARIT, GOLD_DIM),
            (UGARIT, BABYLON, BRONZE_LIGHT),
            (MEMPHIS, UGARIT, GOLD_DIM),
            (HATTUSA, UGARIT, BRONZE),
            (cyprus_copper, UGARIT, BRONZE),
        ]
        for start, end, col in connections:
            line = DashedLine(start, end, color=col, stroke_width=1.5, dash_length=0.15)
            trade_lines.add(line)

        # "ALL FELL" text
        fell = safe_text("ALL FELL WITHIN 50 YEARS.", font="Bebas Neue", font_size=55, color=RED)
        fell.move_to(DOWN * 1)

        div = section_div(5, MUTED).move_to(DOWN * 2.2)
        no_inv = safe_text("No single invader could do that.", font="DM Serif Display",
                          font_size=38, color=DEAD_GRAY)
        no_inv.move_to(DOWN * 3.2)

        # Resource labels below
        div2 = section_div(5, GOLD).move_to(DOWN * 4.2)
        resources = [
            ("TIN → Afghanistan", DOWN * 5.2, BRONZE),
            ("COPPER → Cyprus", DOWN * 6, BRONZE_LIGHT),
            ("GRAIN → Egypt", DOWN * 6.8, GOLD),
        ]
        res_texts = []
        for txt, pos, col in resources:
            t = safe_text(txt, font="Inter", font_size=28, color=col, weight="BOLD")
            t.move_to(pos)
            res_texts.append(t)

        # ── Timing: 7.70s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3)
        self.play(
            LaggedStart(*[FadeIn(e) for e in emp_labels], lag_ratio=0.1),
            run_time=0.6,
        )
        self.play(
            LaggedStart(*[Create(tl) for tl in trade_lines], lag_ratio=0.08),
            run_time=0.8,
        )
        self.wait(0.4)
        self.play(FadeIn(fell, scale=1.1), run_time=0.5)
        self.play(Flash(fell.get_center(), color=RED,
                        line_length=0.3, num_lines=8, run_time=0.3))
        self.play(Create(div), run_time=0.3)
        self.play(FadeIn(no_inv, shift=UP * 0.04), run_time=0.5)
        self.play(Create(div2), run_time=0.3)
        self.wait(0.4)
        for rt in res_texts:
            self.play(FadeIn(rt, shift=LEFT * 0.1), run_time=0.4)
        self.wait(1.1)  # t=7.70


# ================================================================
# SCENE 4: COLLAPSE — Map darkening, dark age (20.9–30.4s)
# ================================================================
class Scene4_Collapse(Scene):
    def construct(self):
        self.add(gradient_bg())
        img = map_image()
        self.add(img)
        self.add(dark_overlay(0.5))

        pill = label_pill("THE COLLAPSE", color=RED, fs=28)
        pill.move_to(UP * 7.8 + RIGHT * 2.5)

        one_break = safe_text("ONE BREAK", font="Bebas Neue", font_size=80, color=RED)
        one_break.move_to(DOWN * 0.5)
        starved = safe_text("and everything starved.", font="DM Serif Display",
                           font_size=42, color=WHITE_SOFT)
        starved.move_to(DOWN * 1.8)

        div1 = section_div(5, ASH).move_to(DOWN * 3)
        writing = safe_text("WRITING DISAPPEARED", font="Bebas Neue", font_size=60, color=ASH)
        writing.move_to(DOWN * 4.2)
        four_hundred = safe_text("for 400 years.", font="DM Serif Display",
                                font_size=44, color=DEAD_GRAY)
        four_hundred.move_to(DOWN * 5.3)
        languages = safe_text("Entire languages were lost.", font="DM Serif Display",
                             font_size=38, color=DEAD_GRAY)
        languages.move_to(DOWN * 6.3)
        forgot = safe_text("The world forgot how to build.", font="DM Serif Display",
                          font_size=38, color=DEAD_GRAY)
        forgot.move_to(DOWN * 7.3)

        # ── Timing: 9.50s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3)
        self.play(FadeIn(one_break, scale=1.15), run_time=0.7)
        self.play(Flash(one_break.get_center(), color=RED,
                        line_length=0.4, num_lines=10, run_time=0.3))
        self.play(FadeIn(starved, shift=UP * 0.06), run_time=0.6)

        # Map fading darker
        self.play(FadeIn(dark_overlay(0.3)), run_time=0.5)
        self.wait(0.76)

        self.play(Create(div1), run_time=0.3)
        self.play(FadeIn(writing, shift=LEFT * 0.1), run_time=0.6)
        self.play(FadeIn(four_hundred, shift=UP * 0.04), run_time=0.5)
        self.wait(0.94)
        self.play(FadeIn(languages, shift=UP * 0.04), run_time=0.6)
        self.wait(0.9)
        self.play(FadeIn(forgot, shift=UP * 0.04), run_time=0.6)
        self.wait(1.9)  # t=9.50


# ================================================================
# SCENE 5: THE PUNCH — Cinematic text closer (30.4–46.3s)
# ================================================================
class Scene5_Punch(Scene):
    def construct(self):
        self.add(gradient_bg())

        pill = label_pill("3,000 YEARS LATER", color=BRONZE, fs=24)
        pill.move_to(UP * 7.2)

        took = safe_text("3,000", font="Bebas Neue", font_size=120, color=BRONZE)
        took.move_to(UP * 4.5)
        years_txt = safe_text("YEARS", font="Inter", font_size=40, color=WHITE_SOFT, weight="BOLD")
        years_txt.move_to(UP * 3)
        figure = safe_text("to figure out what happened.", font="DM Serif Display",
                          font_size=38, color=MUTED)
        figure.move_to(UP * 1.8)

        div1 = section_div(5, MUTED).move_to(UP * 0.5)
        glob1 = safe_text("A globalized system", font="DM Serif Display",
                          font_size=42, color=WHITE_SOFT)
        glob1.move_to(DOWN * 0.8)
        glob2 = safe_text("so connected that", font="DM Serif Display",
                          font_size=42, color=MUTED)
        glob2.move_to(DOWN * 1.8)
        glob3 = safe_text("when one part failed,", font="DM Serif Display",
                          font_size=44, color=WHITE_SOFT)
        glob3.move_to(DOWN * 2.9)

        div2 = section_div(5, RED).move_to(DOWN * 4)
        everything = safe_text("everything fell.", font="Bebas Neue", font_size=80, color=RED)
        everything.move_to(DOWN * 5.3)

        div3 = section_div(5, GOLD).move_to(DOWN * 6.3)
        familiar = safe_text("Sound familiar?", font="Bebas Neue", font_size=80, color=GOLD)
        familiar.move_to(DOWN * 7.3)
        glow = Circle(radius=2.5, fill_color=GOLD, fill_opacity=0.04, stroke_width=0)
        glow.move_to(familiar)

        # ── Timing: 15.90s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3)
        self.play(FadeIn(took, scale=1.2), run_time=0.6)
        self.play(Flash(took.get_center(), color=BRONZE,
                        line_length=0.4, num_lines=8, run_time=0.3))
        self.play(FadeIn(years_txt), run_time=0.3)
        self.play(FadeIn(figure, shift=UP * 0.04), run_time=0.6)
        self.wait(4.0)

        self.play(Create(div1), run_time=0.3)
        self.play(FadeIn(glob1, shift=UP * 0.08), run_time=0.7)
        self.play(FadeIn(glob2, shift=UP * 0.08), run_time=0.7)
        self.play(FadeIn(glob3, shift=UP * 0.08), run_time=0.7)
        self.wait(2.8)

        self.play(Create(div2), run_time=0.3)
        self.play(FadeIn(everything, scale=1.1), run_time=0.7)
        self.play(Flash(everything.get_center(), color=RED,
                        line_length=0.4, num_lines=10, run_time=0.3))
        self.wait(0.7)
        self.play(Create(div3), run_time=0.3)
        self.play(FadeIn(glow), FadeIn(familiar, scale=1.08), run_time=0.8)
        self.wait(1.5)  # t=15.90


# ================================================================
# SCENE 6: HOLD + FADE (3s)
# ================================================================
class Scene6_Hold(Scene):
    def construct(self):
        self.add(gradient_bg())
        self.wait(1.5)
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5)


# ── Infra ─────────────────────────────────────────────────────
SCENE_CLASSES = [Scene1_Hook, Scene2_SeaPeoples, Scene3_Chain,
                 Scene4_Collapse, Scene5_Punch, Scene6_Hold]

def render_single_scene(idx):
    config.output_file = f"ba_geo_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    SCENE_CLASSES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"ba_geo_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENE_CLASSES):
        n = f"ba_geo_scene_{i+1}"; print(f"  Preview {n}...")
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

    names = [S.__name__ for S in SCENE_CLASSES]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_bronze_age.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="ba_geo", audio_path=str(audio))
    final = od / "bronze_age_geo_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
