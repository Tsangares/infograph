#!/usr/bin/env python3
"""Radium Girls — HYBRID SVG visual storytelling (Manim).

Custom SVGs for animated parts, downloaded SVGs for decoration.
6 scenes, ~44.4s (41.4s audio + 3s hold).
"""

import os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from manim import (
    Scene, Text, VGroup, Rectangle, RoundedRectangle, Circle,
    Line, Arrow, DashedLine, Dot, Polygon, Ellipse, Square, Arc,
    FadeIn, FadeOut, GrowFromCenter, Write, Create, DrawBorderThenFill,
    AnimationGroup, LaggedStart, Flash, MoveToTarget,
    SVGMobject,
    config, UP, DOWN, LEFT, RIGHT, ORIGIN,
    WHITE, BLACK, rate_functions, DEGREES, PI,
)
import numpy as np

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.frame_width = 9
config.frame_height = 16
config.background_color = "#1A1410"
config.disable_caching = True

BG = "#1A1410"; BG2 = "#241E14"
CREAM = "#F5E6C8"; SEPIA = "#D4B896"; SEPIA_DARK = "#8B7355"
RADIUM = "#39FF14"; RADIUM_DIM = "#1A8A0A"; RADIUM_FAINT = "#1A4A0A"
GOLD = "#FFD700"; GOLD_DIM = "#B8960F"
RED = "#FF4444"; RED_DARK = "#8B2222"
WHITE_SOFT = "#F0F0F0"; MUTED = "#7B6B55"; DEAD_GRAY = "#4A4038"
SAFE_W = 8.0

SVG_CUSTOM = "svg_assets"
SVG_DL = "svg_assets/downloaded"


def warm_bg():
    bg = Rectangle(width=12, height=20, fill_color=BG, fill_opacity=1, stroke_width=0)
    glow = Circle(radius=6, fill_color=BG2, fill_opacity=0.3, stroke_width=0).move_to(UP * 2)
    return VGroup(bg, glow)

def safe_text(c, **kw):
    t = Text(c, **kw)
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    return t

def section_div(w=5, color=GOLD):
    l = Line(LEFT*w/2, LEFT*0.12, color=color, stroke_width=1.5)
    r = Line(RIGHT*0.12, RIGHT*w/2, color=color, stroke_width=1.5)
    d = Square(side_length=0.1, color=color, fill_color=color, fill_opacity=1).rotate(45*DEGREES)
    return VGroup(l, d, r)

def label_pill(txt, color=RADIUM, bg="#12100C", fs=22):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    p = RoundedRectangle(width=t.width+0.5, height=t.height+0.3, corner_radius=0.18,
                         fill_color=bg, fill_opacity=0.9, stroke_color=color, stroke_width=1.5).move_to(t)
    return VGroup(p, t)

def load_svg(path, height=2, color=None):
    """Load SVG, scale to height, optionally recolor."""
    svg = SVGMobject(path)
    svg.set_height(height)
    if color:
        svg.set_color(color)
    return svg

def paint_jar(x=0, y=0, r=0.6):
    jar = RoundedRectangle(width=r*2, height=r*2.5, corner_radius=r*0.2,
                           fill_color="#1A2A0A", fill_opacity=0.9,
                           stroke_color=RADIUM_DIM, stroke_width=2).move_to(np.array([x, y, 0]))
    surface = Ellipse(width=r*1.5, height=r*0.5, fill_color=RADIUM_FAINT,
                      fill_opacity=0.6, stroke_width=0).move_to(jar.get_top() + DOWN * r * 0.4)
    glow = Circle(radius=r*1.8, fill_color=RADIUM, fill_opacity=0.06, stroke_width=0).move_to(jar)
    lbl = Text("Ra-226", font="Inter", font_size=14, color=RADIUM_DIM).next_to(jar, DOWN, buff=0.1)
    return VGroup(glow, jar, surface, lbl)


# ================================================================
# SCENE 1: THE HOOK (0.0–5.5s)
# ================================================================
class Scene1_Hook(Scene):
    def construct(self):
        self.add(warm_bg())
        pill = label_pill("THE RADIUM GIRLS", color=RADIUM, fs=22)
        pill.move_to(UP * 7.5)

        # Downloaded warning triangle (background, faint)
        warn = load_svg(f"{SVG_DL}/warning.svg", height=4, color=RED)
        warn.set_opacity(0.08).move_to(UP * 3)
        self.add(warn)

        # Custom paintbrush
        brush = load_svg(f"{SVG_CUSTOM}/paintbrush.svg", height=3)
        brush.move_to(RIGHT * 2.5 + UP * 4)

        # Paint jar
        jar = paint_jar(0, 2.5, 0.8)

        # Lips
        lip_c = UP * 6 + LEFT * 1
        lip_upper = Arc(radius=0.4, start_angle=PI*0.1, angle=PI*0.8, color=SEPIA, stroke_width=2).move_to(lip_c + UP*0.05)
        lip_lower = Arc(radius=0.35, start_angle=-PI*0.8, angle=PI*0.6, color=SEPIA, stroke_width=2).move_to(lip_c + DOWN*0.1)
        lips = VGroup(lip_upper, lip_lower)

        safe_lbl = safe_text('"Safe."', font="Bebas Neue", font_size=80, color=RADIUM)
        safe_lbl.move_to(DOWN * 1.5)
        they_said = safe_text("They said it was safe.", font="DM Serif Display", font_size=38, color=DEAD_GRAY)
        they_said.move_to(DOWN * 3)

        self.play(FadeIn(pill), run_time=0.3)
        self.play(FadeIn(jar, scale=0.8), run_time=0.5)
        self.play(FadeIn(brush, shift=DOWN * 0.3), run_time=0.4)

        # Brush dips into jar
        brush.generate_target()
        brush.target.move_to(np.array([0, 3.2, 0]))
        self.play(MoveToTarget(brush), run_time=0.4)

        # Brush to lips
        self.play(FadeIn(lips), run_time=0.3)
        brush.generate_target()
        brush.target.move_to(lip_c + DOWN * 0.5)
        self.play(MoveToTarget(brush), run_time=0.5)
        self.play(Flash(lip_c, color=RADIUM, line_length=0.2, num_lines=6, run_time=0.3))

        self.wait(0.5)
        self.play(FadeIn(safe_lbl, scale=1.2), run_time=0.5)
        self.play(Flash(safe_lbl.get_center(), color=RADIUM, line_length=0.3, num_lines=8, run_time=0.3))
        self.play(FadeIn(they_said, shift=UP * 0.04), run_time=0.4)
        self.wait(0.4)  # t≈5.50


# ================================================================
# SCENE 2: THE METHOD (5.5–14.2s) — watch dial painting
# ================================================================
class Scene2_Method(Scene):
    def construct(self):
        self.add(warm_bg())
        pill = label_pill("THE METHOD", color=MUTED, fs=20)
        pill.move_to(UP * 7.5)
        self.add(pill)

        # Downloaded vintage clock as dial base
        clock = load_svg(f"{SVG_DL}/svgrepo-vintage-clock.svg", height=5.5)
        clock.set_color(SEPIA_DARK).set_opacity(0.3).move_to(UP * 2.5)
        self.add(clock)

        # Dial overlay
        dial_r = 2.5; dial_c = UP * 2.5
        dial_face = Circle(radius=dial_r, fill_color=CREAM, fill_opacity=0.08,
                           stroke_color=SEPIA, stroke_width=2).move_to(dial_c)
        self.add(dial_face)

        # Custom paintbrush for animation
        brush = load_svg(f"{SVG_CUSTOM}/paintbrush.svg", height=1.5)
        brush.move_to(UP * 6)

        pot_c = DOWN * 1 + RIGHT * 2.5
        pot = paint_jar(pot_c[0], pot_c[1], 0.4)
        lip_c = UP * 6 + LEFT * 1.5
        lip_upper = Arc(radius=0.3, start_angle=PI*0.1, angle=PI*0.8, color=SEPIA, stroke_width=2).move_to(lip_c)
        lips = VGroup(lip_upper)

        dial_glow = Circle(radius=dial_r*1.1, fill_color=RADIUM, fill_opacity=0.0, stroke_width=0).move_to(dial_c)
        counter_pos = DOWN * 4.5 + RIGHT * 2.5

        self.play(FadeIn(pot, scale=0.8), FadeIn(lips), FadeIn(brush, shift=DOWN * 0.2), run_time=0.4)
        self.add(dial_glow)

        nums = [("12",0),("3",3),("6",6),("9",9),("1",1),("2",2),("4",4),("5",5)]

        def paint_num(idx, speed):
            nt, ai = nums[idx]
            brush.generate_target(); brush.target.move_to(lip_c + DOWN*0.5)
            self.play(MoveToTarget(brush), run_time=speed)
            brush.generate_target(); brush.target.move_to(pot_c + UP*0.5)
            self.play(MoveToTarget(brush), run_time=speed)
            a = PI/2 - ai*2*PI/12
            pos = dial_c + dial_r*0.55*np.array([np.cos(a), np.sin(a), 0])
            brush.generate_target(); brush.target.move_to(pos + UP*0.3)
            self.play(MoveToTarget(brush), run_time=speed*0.8)
            glow = Circle(radius=0.25, fill_color=RADIUM, fill_opacity=0.12, stroke_width=0).move_to(pos)
            txt = Text(nt, font="Inter", font_size=28, color=RADIUM, weight="BOLD").move_to(pos)
            self.play(FadeIn(VGroup(glow, txt), scale=0.5), run_time=speed*0.6)

        # 3 cycles accelerating
        for i in range(2): paint_num(i, 0.22)
        c1 = Text("2", font="Bebas Neue", font_size=36, color=RADIUM_DIM).move_to(counter_pos)
        self.play(FadeIn(c1), run_time=0.1)

        for i in range(2, 5): paint_num(i, 0.13)
        self.remove(c1)
        c2 = Text("47", font="Bebas Neue", font_size=40, color=RADIUM_DIM).move_to(counter_pos)
        self.play(FadeIn(c2, scale=1.2), run_time=0.1)
        self.play(dial_glow.animate.set_opacity(0.04), run_time=0.2)

        for i in range(5, 8): paint_num(i, 0.07)
        self.remove(c2)
        c3 = Text("186", font="Bebas Neue", font_size=44, color=RADIUM).move_to(counter_pos)
        self.play(FadeIn(c3, scale=1.3), run_time=0.1)
        self.play(dial_glow.animate.set_opacity(0.08), run_time=0.2)

        self.remove(c3)
        hundreds = Text("HUNDREDS", font="Bebas Neue", font_size=48, color=RADIUM).move_to(counter_pos)
        self.play(FadeIn(hundreds, scale=1.2), run_time=0.2)
        final_txt = safe_text("Hundreds of times a day.", font="DM Serif Display",
                             font_size=36, color=SEPIA).move_to(DOWN * 6)
        self.play(dial_glow.animate.set_opacity(0.15), FadeIn(final_txt), run_time=0.4)
        self.play(dial_glow.animate.set_opacity(0.08), run_time=0.3)
        self.play(dial_glow.animate.set_opacity(0.18), run_time=0.3)
        self.wait(0.5)  # t≈8.70


# ================================================================
# SCENE 3: THE HORROR (14.2–20.4s) — SVG jaw with teeth falling
# ================================================================
class Scene3_Horror(Scene):
    def construct(self):
        self.add(warm_bg())
        pill = label_pill("THE HORROR", color=RED, fs=20)
        pill.move_to(UP * 7.5)

        # Downloaded skull as faint background echo
        bg_skull = load_svg(f"{SVG_DL}/svgrepo-skull.svg", height=8)
        bg_skull.set_color(RADIUM).set_opacity(0.03).move_to(UP * 3)
        self.add(bg_skull)

        # Custom jaw_teeth SVG — fully animatable parts
        jaw = SVGMobject(f"{SVG_CUSTOM}/jaw_teeth.svg")
        jaw.set_height(6).move_to(UP * 3)
        # Submobjects: 0=skull outline, 1=left eye, 2=right eye, 3=nose,
        #              4-9=teeth (6 rects), 10=jaw bone, 11-12=crack lines

        skull_outline = jaw[0]
        eyes = VGroup(jaw[1], jaw[2])
        nose = jaw[3]
        teeth = VGroup(*[jaw[i] for i in range(4, 10)])
        jaw_bone = jaw[10]
        cracks = VGroup(*[jaw[i] for i in range(11, min(13, len(jaw)))])

        bone_glow = Circle(radius=3.5, fill_color=RADIUM, fill_opacity=0.0, stroke_width=0).move_to(UP * 3)

        div = section_div(5, RED).move_to(DOWN * 1.5)
        fine = safe_text("The company told them", font="DM Serif Display", font_size=38, color=DEAD_GRAY)
        fine.move_to(DOWN * 2.8)
        fine2 = safe_text("they were fine.", font="DM Serif Display", font_size=42, color=WHITE_SOFT)
        fine2.move_to(DOWN * 3.8)

        # ── Animate ──
        self.play(FadeIn(pill), run_time=0.2)
        self.play(FadeIn(VGroup(skull_outline, eyes, nose, teeth, jaw_bone)), run_time=0.5)

        # Show cracks appearing
        if len(cracks) > 0:
            self.play(LaggedStart(*[Create(c) for c in cracks], lag_ratio=0.2), run_time=0.4)
        self.wait(0.3)

        # Teeth fall out one by one
        for i in range(0, len(teeth), 2):
            self.play(teeth[i].animate.shift(DOWN * 4).set_opacity(0), run_time=0.2)
        for i in range(1, len(teeth), 2):
            self.play(teeth[i].animate.shift(DOWN * 4.5).set_opacity(0), run_time=0.15)

        # Jaw crumbles
        self.play(jaw_bone.animate.set_stroke(opacity=0.15).shift(DOWN * 0.4), run_time=0.4)

        # Bones glow green
        self.add(bone_glow)
        self.play(
            skull_outline.animate.set_color(RADIUM),
            eyes.animate.set_color(RADIUM),
            nose.animate.set_color(RADIUM),
            bone_glow.animate.set_opacity(0.12),
            bg_skull.animate.set_opacity(0.06),
            run_time=0.6,
        )
        self.play(Flash(skull_outline.get_center(), color=RADIUM,
                        line_length=0.4, num_lines=10, run_time=0.3))

        # Company told them they were fine
        self.wait(0.5)
        self.play(Create(div), run_time=0.3)
        self.play(FadeIn(fine, shift=UP * 0.04), run_time=0.5)
        self.play(FadeIn(fine2, shift=UP * 0.04), run_time=0.5)
        self.wait(1.0)  # t≈6.20


# ================================================================
# SCENE 4: THE COVERUP (20.4–28.7s)
# ================================================================
class Scene4_Coverup(Scene):
    def construct(self):
        self.add(warm_bg())
        pill = label_pill("THE COVERUP", color=RED, fs=20)
        pill.move_to(UP * 7.5)

        split = DashedLine(UP * 6.5, DOWN * 0.5, color=DEAD_GRAY, stroke_width=1.5)

        # LEFT: Downloaded shield + scientists
        shield_icon = load_svg(f"{SVG_DL}/shield.svg", height=3)
        shield_icon.set_color("#90A4AE").set_opacity(0.5).move_to(LEFT * 2.2 + UP * 4)
        sci_label = Text("SCIENTISTS", font="Inter", font_size=18, color="#90A4AE", weight="BOLD")
        sci_label.move_to(LEFT * 2.2 + UP * 1.5)
        pb_txt = Text("Pb", font="Inter", font_size=40, color="#B0BEC5", weight="BOLD")
        pb_txt.move_to(shield_icon)

        # RIGHT: Custom woman_figure x3 with radium dots
        women = VGroup()
        for i, x in enumerate([1.3, 2.2, 3.0]):
            w = load_svg(f"{SVG_CUSTOM}/woman_figure.svg", height=1.8)
            w.move_to(np.array([x, 3.5, 0]))
            women.add(w)
        green_dots = VGroup()
        for w in women:
            d = Dot(w.get_center() + DOWN * 0.3, radius=0.08, color=RADIUM).set_opacity(0.7)
            green_dots.add(d)
        worker_label = Text("WORKERS", font="Inter", font_size=18, color=SEPIA, weight="BOLD")
        worker_label.move_to(RIGHT * 2.2 + UP * 1.5)

        # Medical report + SYPHILIS stamp
        div = section_div(5, RED).move_to(DOWN * 1.5)
        report = RoundedRectangle(width=5, height=3, corner_radius=0.1,
                                  fill_color="#1A1410", fill_opacity=0.9,
                                  stroke_color=DEAD_GRAY, stroke_width=1.5).move_to(DOWN * 3.5)
        report_title = Text("MEDICAL REPORT", font="Inter", font_size=20, color=DEAD_GRAY)
        report_title.move_to(report.get_top() + DOWN * 0.4)
        diagnosis = Text("DIAGNOSIS:", font="Inter", font_size=22, color=MUTED)
        diagnosis.move_to(report.get_center() + UP * 0.3)

        stamp_txt = Text("SYPHILIS", font="Bebas Neue", font_size=55, color=RED)
        stamp_border = RoundedRectangle(width=stamp_txt.width+0.4, height=stamp_txt.height+0.3,
                                        corner_radius=0.08, stroke_color=RED, stroke_width=4,
                                        fill_opacity=0).move_to(stamp_txt)
        stamp = VGroup(stamp_border, stamp_txt).rotate(12*DEGREES).move_to(report.get_center() + DOWN * 0.3)

        self.play(FadeIn(pill), run_time=0.2)
        self.play(Create(split), run_time=0.3)
        self.play(FadeIn(shield_icon), FadeIn(pb_txt), FadeIn(sci_label), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(w, shift=UP * 0.1) for w in women], lag_ratio=0.08),
                  run_time=0.5)
        self.play(FadeIn(green_dots), FadeIn(worker_label), run_time=0.3)
        self.wait(1.5)
        self.play(Create(div), run_time=0.3)
        self.play(FadeIn(report), FadeIn(report_title), FadeIn(diagnosis), run_time=0.5)
        self.wait(1.2)
        self.play(FadeIn(stamp, scale=1.4), run_time=0.3)
        self.play(Flash(stamp.get_center(), color=RED, line_length=0.3, num_lines=8, run_time=0.3))
        self.wait(1.8)  # t≈8.30


# ================================================================
# SCENE 5: THE FIGHT (28.7–34.6s)
# ================================================================
class Scene5_Fight(Scene):
    def construct(self):
        self.add(warm_bg())
        pill = label_pill("THE FIGHT", color=GOLD, fs=20)
        pill.move_to(UP * 7.5)

        # 5 custom woman figures
        women = VGroup()
        for i, x in enumerate([-2, -1, 0, 1, 2]):
            w = load_svg(f"{SVG_CUSTOM}/woman_figure.svg", height=1.5)
            if i == 2: w.set_color(GOLD)
            else: w.set_color(SEPIA)
            w.move_to(np.array([x, 5, 0]))
            women.add(w)

        five_txt = Text("5", font="Bebas Neue", font_size=100, color=GOLD).move_to(UP * 2.5)
        sued = safe_text("women sued.", font="DM Serif Display", font_size=44, color=WHITE_SOFT).move_to(UP * 1.2)

        # Downloaded scales of justice
        scales = load_svg(f"{SVG_DL}/scales.svg", height=2)
        scales.set_color(GOLD_DIM).set_opacity(0.3).move_to(DOWN * 0.5)

        # LIARS stamp crossed out
        liars = Text("LIARS", font="Bebas Neue", font_size=70, color=RED)
        liars_border = RoundedRectangle(width=liars.width+0.4, height=liars.height+0.3,
                                        corner_radius=0.08, stroke_color=RED, stroke_width=4,
                                        fill_opacity=0).move_to(liars)
        liars_stamp = VGroup(liars_border, liars).rotate(-8*DEGREES).move_to(DOWN * 0.5)
        cross1 = Line(liars_stamp.get_corner(LEFT+UP), liars_stamp.get_corner(RIGHT+DOWN), color=GOLD, stroke_width=4)
        cross2 = Line(liars_stamp.get_corner(RIGHT+UP), liars_stamp.get_corner(LEFT+DOWN), color=GOLD, stroke_width=4)

        # Downloaded gavel
        gavel = load_svg(f"{SVG_DL}/gavel.svg", height=1.5)
        gavel.set_color(SEPIA_DARK).move_to(DOWN * 3)

        trial = safe_text("The case went to trial.", font="DM Serif Display", font_size=42, color=WHITE_SOFT).move_to(DOWN * 4.8)
        anyway = Text("ANYWAY.", font="Bebas Neue", font_size=70, color=GOLD).move_to(DOWN * 6)

        self.play(FadeIn(pill), run_time=0.2)
        self.play(LaggedStart(*[FadeIn(w, shift=UP * 0.2) for w in women], lag_ratio=0.06), run_time=0.6)
        self.play(FadeIn(five_txt, scale=1.3), FadeIn(sued), run_time=0.5)
        self.play(Flash(five_txt.get_center(), color=GOLD, line_length=0.3, num_lines=8, run_time=0.3))

        self.add(scales)
        self.wait(0.3)
        self.play(FadeIn(liars_stamp, scale=1.3), run_time=0.3)
        self.wait(0.3)
        self.play(Create(cross1), Create(cross2), run_time=0.3)

        self.wait(0.2)
        self.play(FadeIn(gavel, shift=DOWN * 0.5), run_time=0.3)
        self.play(gavel.animate.shift(UP * 0.3), run_time=0.1)
        self.play(gavel.animate.shift(DOWN * 0.3), run_time=0.08)
        self.play(Flash(gavel.get_center(), color=GOLD, line_length=0.2, num_lines=6, run_time=0.2))

        self.play(FadeIn(trial, shift=UP * 0.04), run_time=0.4)
        self.play(FadeIn(anyway, scale=1.08), run_time=0.4)
        self.wait(0.5)  # t≈5.90


# ================================================================
# SCENE 6: THE PUNCH (34.6–44.4s) — legacy spreading
# ================================================================
class Scene6_Punch(Scene):
    def construct(self):
        self.add(Rectangle(width=12, height=20, fill_color="#100C08", fill_opacity=1, stroke_width=0))
        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1, stroke_width=0).move_to(UP*(8-bh/2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1, stroke_width=0).move_to(DOWN*(8-bh/2)),
        )

        # 5 custom woman figures
        figures = VGroup()
        for x in [-2, -1, 0, 1, 2]:
            w = load_svg(f"{SVG_CUSTOM}/woman_figure.svg", height=1.5)
            w.set_color(GOLD).move_to(np.array([x, 3.5, 0]))
            figures.add(w)

        # Golden root lines
        roots = VGroup()
        np.random.seed(42)
        for i in range(15):
            sx = np.random.uniform(-2.5, 2.5); sy = 2.5
            ex = sx + np.random.uniform(-2, 2); ey = np.random.uniform(-2, -5)
            roots.add(Line(np.array([sx,sy,0]), np.array([ex,ey,0]),
                          color=GOLD, stroke_width=1.5).set_opacity(0.4))

        # Downloaded shield icon — protection
        shield = load_svg(f"{SVG_DL}/shield.svg", height=3)
        shield.set_color(GOLD).set_opacity(0.4).move_to(DOWN * 2)

        # Small crowd (downloaded person icons)
        crowd = VGroup()
        for i in range(10):
            p = load_svg(f"{SVG_DL}/person.svg", height=0.6)
            p.set_color(WHITE_SOFT).set_opacity(0.3)
            p.move_to(np.array([-2.5 + i * 0.55, np.random.uniform(-5, -4.5), 0]))
            crowd.add(p)

        every = safe_text("Every American today.", font="DM Serif Display", font_size=42, color=GOLD)
        every.move_to(DOWN * 6.5)
        glow = Circle(radius=4, fill_color=GOLD, fill_opacity=0.03, stroke_width=0).move_to(DOWN * 2)

        # ── Timing: 9.80s ──
        self.play(LaggedStart(*[FadeIn(f, shift=UP * 0.1) for f in figures], lag_ratio=0.06), run_time=0.6)
        self.wait(0.8)
        # Figures fade to outlines
        self.play(figures.animate.set_opacity(0.15), run_time=0.8)
        self.wait(0.5)
        # Golden roots spread
        self.play(LaggedStart(*[Create(r) for r in roots], lag_ratio=0.04), run_time=1.0)
        self.play(FadeIn(shield), run_time=0.4)
        self.add(glow)
        self.play(glow.animate.set_opacity(0.06), run_time=0.3)
        # Crowd appears
        self.play(LaggedStart(*[FadeIn(c, scale=0.5) for c in crowd], lag_ratio=0.03), run_time=0.6)
        self.play(FadeIn(every, shift=UP * 0.04), run_time=0.6)
        # Hold + fade
        self.wait(2.6)
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5)


# ── Infra ─────────────────────────────────────────────────────
SCENES = [Scene1_Hook, Scene2_Method, Scene3_Horror,
          Scene4_Coverup, Scene5_Fight, Scene6_Punch]

def render_single_scene(idx):
    config.output_file = f"radium_svg_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    SCENES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"radium_svg_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENES):
        n = f"radium_svg_scene_{i+1}"; print(f"  Preview {n}...")
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
    audio = od / "tts_radium.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="radium_svg", audio_path=str(audio))
    final = od / "radium_svg_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
