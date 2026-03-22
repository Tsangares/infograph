#!/usr/bin/env python3
"""Easter Island 'Ecocide Myth' — History Arc (Manim version).

6 scenes, 42s total, word-level sync to tts_easter_history.vtt.
Style: v16 template (gradient_bg, star_field, moai_side, etc.)

Scene timing (from VTT):
  1. THE WRONG ANSWER    (0.0–8.5s)   8.50s
  2. THE CONTRADICTION   (8.5–14.3s)  5.80s
  3. THE ORAL TRADITION  (14.3–20.8s) 6.50s
  4. THE PROOF           (20.8–29.2s) 8.40s
  5. THE SCALE           (29.2–34.8s) 5.60s
  6. THE PUNCH           (34.8–42.0s) 7.20s
"""

import json, os
import sys
import subprocess
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from manim import (
    Scene, Text, VGroup, VMobject, Group, Rectangle, RoundedRectangle, Circle,
    Line, Arrow, DashedLine, Dot, Polygon, Arc, Ellipse,
    ImageMobject, Triangle, Square,
    FadeIn, FadeOut, GrowFromCenter, Write, Create, DrawBorderThenFill,
    AnimationGroup, LaggedStart,
    Flash, GrowArrow,
    config, UP, DOWN, LEFT, RIGHT, ORIGIN, UL, UR, DL, DR,
    WHITE, BLACK,
    rate_functions,
    DEGREES, PI,
)
import numpy as np

ASSETS = "assets"

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.frame_width = 9
config.frame_height = 16
config.background_color = "#0B0F18"
config.disable_caching = True

# Palette (from v16)
GOLD = "#FFD700"
GOLD_DIM = "#B8960F"
RED = "#E63946"
WHITE_SOFT = "#F0F0F0"
MUTED = "#7B8DA0"
BG = "#0B0F18"
SURFACE = "#141C2B"
SURFACE2 = "#1A2538"
BORDER = "#2A3A50"
TEAL = "#2EC4B6"
AMBER = "#D4920A"
OCEAN = "#1B3A5C"
BROWN = "#8B6914"
DARK_BROWN = "#5A3E0A"
STONE = "#9A8B70"
STONE_DARK = "#6B5E48"
BLOOD = "#8B0000"

SAFE_W = 7.2


# ── Helpers (from v16) ──────────────────────────────────────────

def gradient_bg():
    bg = Rectangle(width=12, height=20, fill_color=BG, fill_opacity=1, stroke_width=0)
    glow = Circle(radius=5, fill_color=OCEAN, fill_opacity=0.10, stroke_width=0).move_to(UP * 2)
    return VGroup(bg, glow)


def star_field(n=30, seed=42):
    np.random.seed(seed)
    stars = VGroup()
    for _ in range(n):
        x = np.random.uniform(-4.5, 4.5)
        y = np.random.uniform(-8, 8)
        r = np.random.uniform(0.015, 0.035)
        op = np.random.uniform(0.15, 0.45)
        stars.add(Dot(point=np.array([x, y, 0]), radius=r, color=WHITE).set_opacity(op))
    return stars


def moai_side(height=3.0, color=STONE, stroke_color=None, stroke_w=2):
    h = height
    w = h * 0.5
    pts = [
        np.array([-w*0.35, h*0.45, 0]), np.array([-w*0.30, h*0.50, 0]),
        np.array([w*0.05, h*0.50, 0]), np.array([w*0.20, h*0.45, 0]),
        np.array([w*0.35, h*0.32, 0]), np.array([w*0.38, h*0.28, 0]),
        np.array([w*0.28, h*0.22, 0]), np.array([w*0.25, h*0.16, 0]),
        np.array([w*0.40, h*0.14, 0]), np.array([w*0.50, h*0.02, 0]),
        np.array([w*0.42, h*-0.02, 0]), np.array([w*0.22, h*-0.06, 0]),
        np.array([w*0.20, h*-0.10, 0]), np.array([w*0.25, h*-0.13, 0]),
        np.array([w*0.30, h*-0.18, 0]), np.array([w*0.25, h*-0.22, 0]),
        np.array([w*0.15, h*-0.28, 0]), np.array([w*0.25, h*-0.32, 0]),
        np.array([w*0.25, h*-0.50, 0]), np.array([-w*0.30, h*-0.50, 0]),
        np.array([-w*0.30, h*-0.32, 0]), np.array([-w*0.20, h*-0.28, 0]),
        np.array([-w*0.32, h*-0.15, 0]), np.array([-w*0.40, h*-0.05, 0]),
        np.array([-w*0.38, h*0.10, 0]), np.array([-w*0.30, h*0.18, 0]),
        np.array([-w*0.35, h*0.30, 0]),
    ]
    sc = stroke_color or STONE_DARK
    moai = Polygon(*pts, fill_color=color, fill_opacity=1.0,
                   stroke_color=sc, stroke_width=stroke_w)
    eye = Ellipse(width=h*0.06, height=h*0.035,
                  fill_color=WHITE_SOFT, fill_opacity=0.7, stroke_width=0)
    eye.move_to(moai.get_center() + RIGHT * w * 0.28 + UP * h * 0.19)
    return VGroup(moai, eye)


def section_div(width=5, color=GOLD):
    l = Line(LEFT * width/2, LEFT * 0.12, color=color, stroke_width=1.5)
    r = Line(RIGHT * 0.12, RIGHT * width/2, color=color, stroke_width=1.5)
    d = Square(side_length=0.1, color=color, fill_color=color, fill_opacity=1).rotate(45 * DEGREES)
    return VGroup(l, d, r)


def label_pill(txt, color=GOLD, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W:
        t.scale(SAFE_W / t.width)
    p = RoundedRectangle(
        width=t.width + 0.5, height=t.height + 0.3,
        corner_radius=0.18, fill_color=bg, fill_opacity=0.95,
        stroke_color=color, stroke_width=1.5,
    ).move_to(t)
    return VGroup(p, t)


def safe_text(content, **kwargs):
    t = Text(content, **kwargs)
    if t.width > SAFE_W:
        t.scale(SAFE_W / t.width)
    return t


# ── New helpers for History video ─────────────────────────────

def ship_silhouette(width=2.0, color=MUTED):
    """Simple sailing ship silhouette — hull + mast + sail."""
    w, h = width, width * 0.8
    # Hull
    hull = Polygon(
        np.array([-w/2, 0, 0]),
        np.array([-w/2.5, -h*0.25, 0]),
        np.array([w/2.5, -h*0.25, 0]),
        np.array([w/2, 0, 0]),
        np.array([w/1.8, h*0.05, 0]),
        np.array([-w/1.8, h*0.05, 0]),
        fill_color=color, fill_opacity=1, stroke_color=color, stroke_width=1.5,
    )
    # Mast
    mast = Line(
        np.array([0, 0, 0]),
        np.array([0, h*0.7, 0]),
        color=color, stroke_width=2,
    )
    # Sail
    sail = Polygon(
        np.array([0, h*0.65, 0]),
        np.array([w*0.35, h*0.35, 0]),
        np.array([0, h*0.15, 0]),
        fill_color=color, fill_opacity=0.7, stroke_color=color, stroke_width=1,
    )
    return VGroup(hull, mast, sail)


def chain_link(x, y, size=0.15, color=MUTED):
    """Small chain link — oval."""
    return Ellipse(
        width=size, height=size * 1.6,
        stroke_color=color, stroke_width=2, fill_opacity=0,
    ).move_to(np.array([x, y, 0]))


def population_bar(value, max_val, x, width=1.2, max_height=5.0, color=GOLD):
    """Vertical bar for population chart."""
    h = (value / max_val) * max_height
    bar = Rectangle(
        width=width, height=h,
        fill_color=color, fill_opacity=0.9,
        stroke_color=color, stroke_width=1,
    )
    bar.move_to(np.array([x, -3 + h/2, 0]))
    lbl = safe_text(f"{value:,}", font="Bebas Neue", font_size=36, color=WHITE_SOFT)
    lbl.next_to(bar, UP, buff=0.15)
    return VGroup(bar, lbl)


def moai_row_silhouette(n=5, spacing=1.5, height=2.5, color=STONE):
    """Row of moai silhouettes — the iconic "textbook" image."""
    row = VGroup()
    for i in range(n):
        m = moai_side(height=height, color=color, stroke_w=1)
        m.set_opacity(0.6 + 0.08 * i)
        m.move_to(LEFT * ((n-1)/2 * spacing) + RIGHT * i * spacing)
        row.add(m)
    return row


# ================================================================
# SCENE 1: THE WRONG ANSWER (0.0–8.5s = 8.50s)
# VTT: "For decades..." @ 0.1s, "A civilization..." @ 4.48s
# Visual: Row of moai + "CAUTIONARY TALE" + textbook framing
# ================================================================
class Scene1_WrongAnswer(Scene):
    DURATION = 8.5
    def construct(self):
        self.add(gradient_bg(), star_field(12, seed=1))
        t = 0

        # Moai row — the iconic textbook image
        row = moai_row_silhouette(5, spacing=1.4, height=2.8, color=STONE)
        row.move_to(UP * 3)

        # Ground line
        ground = Line(LEFT * 4.5, RIGHT * 4.5, color=BORDER, stroke_width=2)
        ground.move_to(UP * 1.2)

        # Label pill
        pill = label_pill("THE TEXTBOOK STORY", color=MUTED, fs=26)
        pill.move_to(UP * 6.5)

        # Decorative frame where photo would go — programmatic
        frame = RoundedRectangle(
            width=5.5, height=3.5,
            corner_radius=0.15, stroke_color=BORDER, stroke_width=2,
            fill_color=SURFACE, fill_opacity=0.6,
        ).move_to(DOWN * 1.2)
        frame_label = safe_text("EASTER ISLAND", font="Inter", font_size=24, color=MUTED)
        frame_label.move_to(frame.get_center())

        # Main text — "CAUTIONARY TALE"
        title = safe_text("CAUTIONARY", font="Bebas Neue", font_size=100, color=GOLD)
        title.move_to(DOWN * 4.2)
        title2 = safe_text("TALE.", font="Bebas Neue", font_size=100, color=GOLD)
        title2.move_to(DOWN * 5.4)

        # Animate — synced to narration
        # 0.0s scene start, VTT line 1 at 0.1s: "For decades, scientists called..."
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.add(ground)
        self.play(
            LaggedStart(*[FadeIn(m, scale=0.9) for m in row], lag_ratio=0.06),
            run_time=0.8,
        )
        self.play(FadeIn(frame), FadeIn(frame_label), run_time=0.4); t += 0.4

        # "cautionary tale" lands ~2.5s into narration
        self.wait(0.6); t += 0.6
        self.play(FadeIn(title, scale=1.12), run_time=0.4); t += 0.4
        self.play(FadeIn(title2, scale=1.12), run_time=0.4); t += 0.4
        self.play(Flash(title.get_center(), color=GOLD, line_length=0.3, num_lines=8, run_time=0.3)); t += 0.3

        # 4.48s: "A civilization that collapsed..."
        self.wait(1.0); t += 1.0

        # Second beat — "destroyed its own environment"
        collapse_text = safe_text("They destroyed themselves.", font="Inter",
                                  font_size=38, color=RED, weight="BOLD")
        collapse_text.move_to(DOWN * 6.8)

        # "WRONG" stamp over the whole narrative
        wrong = safe_text("WRONG", font="Bebas Neue", font_size=70, color=RED)
        wrong_border = RoundedRectangle(
            width=wrong.width + 0.5, height=wrong.height + 0.35,
            corner_radius=0.08,
            stroke_color=RED, stroke_width=5, fill_opacity=0,
        ).move_to(wrong)
        stamp = VGroup(wrong_border, wrong).rotate(12 * DEGREES)
        stamp.move_to(DOWN * 1.2)  # Over the frame

        self.play(FadeIn(collapse_text, shift=UP * 0.08), run_time=0.5); t += 0.5
        self.wait(0.8); t += 0.8
        self.play(FadeIn(stamp, scale=1.4), run_time=0.2); t += 0.2
        self.play(Flash(stamp.get_center(), color=RED, line_length=0.3, num_lines=8, run_time=0.3)); t += 0.3
        # Hold to fill 8.50s total (current 7.3s, need +1.2s)
        target = getattr(self.__class__, 'DURATION', 8.5)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 2: THE CONTRADICTION (8.5–14.3s = 5.80s)
# VTT: "But there's a problem." @ 8.5s (0.0s), "The Rapa Nui survived..." @ 10.215s (1.7s)
# Visual: Timeline diagram showing survival after deforestation
# ================================================================
class Scene2_Contradiction(Scene):
    DURATION = 5.8
    def construct(self):
        self.add(gradient_bg(), star_field(12, seed=7))
        t = 0

        # "THE PROBLEM" label
        pill = label_pill("THE CONTRADICTION", color=RED, fs=28)
        pill.move_to(UP * 7)

        # Problem statement
        problem = safe_text("But there's a problem.", font="Inter",
                           font_size=48, color=RED, weight="BOLD")
        problem.move_to(UP * 5.2)

        # Timeline diagram — the core visual
        timeline = Line(LEFT * 3.5, RIGHT * 3.5, color=MUTED, stroke_width=2)
        timeline.move_to(UP * 1.5)

        # Date markers
        dates = [("1400s", -3.0), ("1600s", -1.0), ("1722", 0.5), ("1860s", 2.5)]
        date_labels = VGroup()
        date_ticks = VGroup()
        for txt, x in dates:
            tick = Line(UP * 0.15, DOWN * 0.15, color=MUTED, stroke_width=1.5)
            tick.move_to(timeline.get_center() + RIGHT * x)
            date_ticks.add(tick)
            lbl = safe_text(txt, font="Inter", font_size=22, color=MUTED)
            lbl.next_to(tick, DOWN, buff=0.15)
            date_labels.add(lbl)

        # Deforestation zone (red bar, early)
        deforest_bar = Rectangle(
            width=2.0, height=0.4,
            fill_color=RED, fill_opacity=0.3,
            stroke_color=RED, stroke_width=1.5,
        ).move_to(timeline.get_center() + LEFT * 2 + UP * 0.6)
        deforest_lbl = safe_text("FORESTS GONE", font="Inter", font_size=20, color=RED, weight="BOLD")
        deforest_lbl.next_to(deforest_bar, UP, buff=0.1)

        # Survival zone (gold bar, extends centuries past)
        survive_bar = Rectangle(
            width=5.5, height=0.4,
            fill_color=GOLD, fill_opacity=0.2,
            stroke_color=GOLD, stroke_width=1.5,
        ).move_to(timeline.get_center() + RIGHT * 0.25 + DOWN * 0.6)
        survive_lbl = safe_text("RAPA NUI THRIVED", font="Inter", font_size=20, color=GOLD, weight="BOLD")
        survive_lbl.next_to(survive_bar, DOWN, buff=0.1)

        # Arrow showing the gap = contradiction
        gap_arrow = Arrow(
            deforest_bar.get_right() + DOWN * 0.3,
            survive_bar.get_right() + UP * 0.3,
            color=WHITE_SOFT, stroke_width=2, buff=0.1,
        )
        gap_lbl = safe_text("CENTURIES", font="Bebas Neue", font_size=36, color=WHITE_SOFT)
        gap_lbl.next_to(gap_arrow, RIGHT, buff=0.2)

        # Big payoff text
        div = section_div(5, RED).move_to(DOWN * 2.5)
        survived = safe_text("They survived.", font="Bebas Neue", font_size=80, color=GOLD)
        survived.move_to(DOWN * 3.8)
        sub = safe_text("For centuries after the forests fell.", font="Inter",
                       font_size=34, color=WHITE_SOFT, weight="BOLD")
        sub.move_to(DOWN * 5.0)

        # Moai silhouette instead of photo (saves RAM)
        lone_moai = moai_side(height=2.5, color=STONE, stroke_w=1)
        lone_moai.set_opacity(0.5)
        lone_moai.move_to(DOWN * 6.8)

        # Animate
        # 0.0s: "But there's a problem"
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(problem, scale=1.05), run_time=0.4); t += 0.4

        # Build timeline
        self.play(Create(timeline), run_time=0.3); t += 0.3
        self.play(
            LaggedStart(*[FadeIn(t) for t in date_ticks], lag_ratio=0.05),
            LaggedStart(*[FadeIn(l) for l in date_labels], lag_ratio=0.05),
            run_time=0.4,
        )

        # 1.7s: "The Rapa Nui survived..."
        self.play(FadeIn(deforest_bar), FadeIn(deforest_lbl), run_time=0.3); t += 0.3
        self.play(FadeIn(survive_bar), FadeIn(survive_lbl), run_time=0.3); t += 0.3
        self.play(GrowArrow(gap_arrow), FadeIn(gap_lbl), run_time=0.3); t += 0.3

        # Payoff
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(survived, scale=1.1), run_time=0.4); t += 0.4
        self.play(FadeIn(sub, shift=UP * 0.06), run_time=0.3); t += 0.3
        self.play(FadeIn(lone_moai, scale=0.9), run_time=0.3); t += 0.3

        # Hold to fill 5.80s (current 4.6s, need +1.2s)
        target = getattr(self.__class__, 'DURATION', 5.8)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 3: THE ORAL TRADITION (14.3–20.8s = 6.50s)
# VTT: "Their oral history..." @ 14.3s (0.0s), "Ships came." @ 17.1s (2.8s),
#      "Then people disappeared." @ 18.7s (4.4s)
# Visual: Moai watching ship silhouettes appear on horizon
# ================================================================
class Scene3_OralTradition(Scene):
    DURATION = 6.5
    def construct(self):
        self.add(gradient_bg())
        t = 0

        # Darker ocean atmosphere
        ocean = Rectangle(width=12, height=6, fill_color="#0A1528", fill_opacity=0.6, stroke_width=0)
        ocean.move_to(UP * 3)
        self.add(ocean)
        self.add(star_field(10, seed=13))

        # Lone moai silhouette — watching the sea
        moai = moai_side(height=5.0, color=STONE, stroke_w=1)
        moai.set_opacity(0.7)
        moai.move_to(LEFT * 2.5 + UP * 2)

        # Horizon line
        horizon = Line(LEFT * 4.5, RIGHT * 4.5, color=OCEAN, stroke_width=2)
        horizon.move_to(UP * 4.5)

        # Ships — will appear on the horizon
        ship1 = ship_silhouette(1.2, color="#4A5568")
        ship1.move_to(RIGHT * 1.5 + UP * 5.2)
        ship2 = ship_silhouette(0.9, color="#3A4558")
        ship2.move_to(RIGHT * 3.0 + UP * 5.0)
        ship3 = ship_silhouette(0.7, color="#2A3548")
        ship3.move_to(RIGHT * 0.0 + UP * 5.4)

        # Label
        pill = label_pill("THE ORAL TRADITION", color=GOLD, fs=26)
        pill.move_to(UP * 7)

        # Reverent text
        oral = safe_text("Their oral history tells", font="DM Serif Display",
                        font_size=44, color=WHITE_SOFT)
        oral.move_to(DOWN * 1.5)
        oral2 = safe_text("a different story.", font="DM Serif Display",
                         font_size=44, color=GOLD)
        oral2.move_to(DOWN * 2.5)

        # "Ships came." — dramatic
        ships_text = safe_text("Ships came.", font="Bebas Neue", font_size=90, color=RED)
        ships_text.move_to(DOWN * 4.5)

        # "Then people disappeared."
        vanished = safe_text("Then people disappeared.", font="DM Serif Display",
                            font_size=40, color=MUTED)
        vanished.move_to(DOWN * 6.0)

        # Moai signature
        div = section_div(4, GOLD).move_to(DOWN * 7.2)

        # Animate
        # 0.0s: "Their oral history tells a different story."
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.add(horizon)
        self.play(FadeIn(moai, scale=0.95), run_time=0.6); t += 0.6
        self.play(FadeIn(oral, shift=UP * 0.08), run_time=0.5); t += 0.5
        self.play(FadeIn(oral2, shift=UP * 0.08), run_time=0.5); t += 0.5

        # 2.8s: "Ships came." — ships materialize on horizon
        self.wait(0.4); t += 0.4
        self.play(
            FadeIn(ship1, shift=LEFT * 0.3),
            FadeIn(ship2, shift=LEFT * 0.2),
            FadeIn(ship3, shift=LEFT * 0.4),
            run_time=0.6,
        )
        self.play(FadeIn(ships_text, scale=1.15), run_time=0.4); t += 0.4
        self.play(Flash(ships_text.get_center(), color=RED, line_length=0.4, num_lines=10, run_time=0.3)); t += 0.3

        # 4.4s: "Then people disappeared."
        self.wait(0.3); t += 0.3
        self.play(FadeIn(vanished, shift=UP * 0.06), run_time=0.5); t += 0.5
        self.play(Create(div), run_time=0.3); t += 0.3

        # Hold to fill 6.50s (current 5.8s, need +0.7s)
        target = getattr(self.__class__, 'DURATION', 6.5)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 4: THE PROOF (20.8–29.2s = 8.40s)
# VTT: "In 1863..." @ 20.8s (0.0s), "Smallpox..." @ 26.6s (5.75s)
# Visual: Ship silhouettes + chains + "1863" date stamp + numbers
# ================================================================
class Scene4_Proof(Scene):
    DURATION = 8.4
    def construct(self):
        self.add(gradient_bg())
        t = 0

        # Dark, oppressive atmosphere
        dark_overlay = Rectangle(width=12, height=20, fill_color="#050810", fill_opacity=0.4, stroke_width=0)
        self.add(dark_overlay)
        self.add(star_field(8, seed=44))

        # Label
        pill = label_pill("THE PROOF", color=RED, fs=28)
        pill.move_to(UP * 7)

        # Giant date stamp
        date = safe_text("1863", font="Bebas Neue", font_size=160, color=RED)
        date.move_to(UP * 5)

        # Ship fleet — larger, more menacing
        ships = VGroup()
        ship_data = [(-2.0, 3.2, 1.5), (0.5, 3.5, 1.8), (2.8, 3.0, 1.3)]
        for x, y, w in ship_data:
            s = ship_silhouette(w, color="#4A2020")
            s.move_to(np.array([x, y, 0]))
            ships.add(s)

        # Chain decoration across the middle
        chains = VGroup()
        for i in range(12):
            x = -3.3 + i * 0.6
            chains.add(chain_link(x, 1.5, size=0.2, color="#6B4040"))

        # "SEIZED" text block
        seized_pre = safe_text("Peruvian slave ships seized", font="Inter",
                              font_size=36, color=WHITE_SOFT, weight="BOLD")
        seized_pre.move_to(DOWN * 0.2)

        seized_num = safe_text("1,400 PEOPLE", font="Bebas Neue", font_size=100, color=GOLD)
        seized_num.move_to(DOWN * 1.6)

        seized_post = safe_text("in a single raid.", font="Inter",
                               font_size=36, color=MUTED, weight="BOLD")
        seized_post.move_to(DOWN * 2.8)

        # Divider
        div = section_div(5, RED).move_to(DOWN * 3.8)

        # "Smallpox killed the survivors."
        smallpox = safe_text("Smallpox killed", font="Bebas Neue", font_size=70, color=RED)
        smallpox.move_to(DOWN * 5.0)
        survivors = safe_text("the survivors.", font="Bebas Neue", font_size=70, color=RED)
        survivors.move_to(DOWN * 6.0)

        # Animate — synced to narration
        # 0.0s: "In 1863, Peruvian slave ships seized fourteen hundred people"
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(date, scale=1.3), run_time=0.4); t += 0.4
        self.play(Flash(date.get_center(), color=RED, line_length=0.5, num_lines=10, run_time=0.3)); t += 0.3

        # Ships appear
        self.play(
            LaggedStart(*[FadeIn(s, shift=DOWN * 0.2) for s in ships], lag_ratio=0.1),
            run_time=0.6,
        )

        # Chains
        self.play(
            LaggedStart(*[FadeIn(c, scale=0.5) for c in chains], lag_ratio=0.02),
            run_time=0.4,
        )

        # Text — "seized 1,400 people in a single raid"
        self.play(FadeIn(seized_pre, shift=UP * 0.06), run_time=0.4); t += 0.4
        self.play(FadeIn(seized_num, scale=1.15), run_time=0.4); t += 0.4
        self.play(Flash(seized_num.get_center(), color=GOLD, line_length=0.4, num_lines=8, run_time=0.3)); t += 0.3
        self.play(FadeIn(seized_post, shift=UP * 0.06), run_time=0.3); t += 0.3

        # Linger on the number
        self.wait(1.5); t += 1.5

        # 5.75s: "Smallpox killed the survivors."
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(smallpox, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(survivors, scale=1.05), run_time=0.4); t += 0.4
        self.play(Flash(smallpox.get_center(), color=RED, line_length=0.3, num_lines=8, run_time=0.3)); t += 0.3

        # Hold to fill 8.40s (current 7.5s, need +0.9s)
        target = getattr(self.__class__, 'DURATION', 8.4)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 5: THE SCALE (29.2–34.8s = 5.60s)
# VTT: "The population fell..." @ 29.2s (0.0s), "In less than a decade." @ 32.9s (3.7s)
# Visual: Population bar chart — 3,000 → 111
# ================================================================
class Scene5_Scale(Scene):
    DURATION = 5.6
    def construct(self):
        self.add(gradient_bg(), star_field(10, seed=55))
        t = 0

        # Label
        pill = label_pill("THE SCALE", color=GOLD, fs=28)
        pill.move_to(UP * 7)

        # Population chart — two bars
        # Bar 1: 3,000 (tall, gold)
        bar_before = Rectangle(
            width=2.0, height=6.0,
            fill_color=GOLD, fill_opacity=0.8,
            stroke_color=GOLD, stroke_width=1.5,
        )
        bar_before.move_to(LEFT * 2 + UP * 1)

        lbl_before = safe_text("3,000", font="Bebas Neue", font_size=60, color=GOLD)
        lbl_before.next_to(bar_before, UP, buff=0.2)
        yr_before = safe_text("1862", font="Inter", font_size=24, color=MUTED)
        yr_before.next_to(bar_before, DOWN, buff=0.2)

        # Bar 2: 111 (tiny, red)
        bar_after_h = 6.0 * (111 / 3000)  # proportional
        bar_after = Rectangle(
            width=2.0, height=bar_after_h,
            fill_color=RED, fill_opacity=0.9,
            stroke_color=RED, stroke_width=1.5,
        )
        bar_after.move_to(RIGHT * 2 + DOWN * 2 + UP * bar_after_h / 2)

        lbl_after = safe_text("111", font="Bebas Neue", font_size=60, color=RED)
        lbl_after.next_to(bar_after, UP, buff=0.2)
        yr_after = safe_text("1877", font="Inter", font_size=24, color=MUTED)
        yr_after.next_to(bar_after, DOWN, buff=0.2)

        # Arrow between
        drop_arrow = Arrow(
            lbl_before.get_right() + RIGHT * 0.3,
            lbl_after.get_left() + LEFT * 0.3,
            color=RED, stroke_width=3, buff=0,
        )

        # Percentage
        pct = safe_text("−96%", font="Bebas Neue", font_size=50, color=RED)
        pct.next_to(drop_arrow, UP, buff=0.15)

        # Ground line
        ground = Line(LEFT * 4, RIGHT * 4, color=BORDER, stroke_width=1.5)
        ground.move_to(DOWN * 2)

        # "In less than a decade."
        div = section_div(5, RED).move_to(DOWN * 4)
        decade = safe_text("In less than a decade.", font="Bebas Neue",
                          font_size=70, color=WHITE_SOFT)
        decade.move_to(DOWN * 5.5)

        # Stick figures to show scale
        figs_before = VGroup()
        for i in range(15):
            r, c = divmod(i, 5)
            fig = Dot(radius=0.06, color=GOLD).set_opacity(0.5)
            fig.move_to(LEFT * 2 + DOWN * 3.5 + RIGHT * c * 0.35 + DOWN * r * 0.35)
            figs_before.add(fig)

        fig_after = Dot(radius=0.08, color=RED).set_opacity(0.8)
        fig_after.move_to(RIGHT * 2 + DOWN * 3.5)

        # Animate
        # 0.0s: "The population fell from three thousand..."
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.add(ground)

        # Build chart
        self.play(
            FadeIn(bar_before, shift=UP * 0.3),
            FadeIn(lbl_before),
            FadeIn(yr_before),
            run_time=0.5,
        )
        self.play(
            FadeIn(bar_after, shift=UP * 0.1),
            FadeIn(lbl_after),
            FadeIn(yr_after),
            run_time=0.5,
        )
        self.play(GrowArrow(drop_arrow), FadeIn(pct, scale=1.1), run_time=0.4); t += 0.4
        self.play(Flash(pct.get_center(), color=RED, line_length=0.3, num_lines=6, run_time=0.3)); t += 0.3

        # Figures
        self.play(
            LaggedStart(*[FadeIn(f, scale=0.3) for f in figs_before], lag_ratio=0.02),
            run_time=0.3,
        )
        self.play(FadeIn(fig_after, scale=0.5), run_time=0.2); t += 0.2

        # 3.7s: "In less than a decade."
        self.wait(0.5); t += 0.5
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(decade, scale=1.08), run_time=0.5); t += 0.5
        self.play(Flash(decade.get_center(), color=WHITE_SOFT, line_length=0.3, num_lines=8, run_time=0.3)); t += 0.3

        # Hold to fill 5.60s (current 4.9s, need +0.7s)
        target = getattr(self.__class__, 'DURATION', 5.6)
        self.wait(max(0.1, target - t - 0.3))


# ================================================================
# SCENE 6: THE PUNCH (34.8–42.0s = 7.20s)
# VTT: "We spent a century..." @ 34.8s (0.0s), "The real cause..." @ 38.2s (3.4s),
#      "It was us." @ 40.4s (5.6s)
# Visual: Letterbox, lone moai ghost, cinematic closer
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 7.2
    def construct(self):
        self.add(gradient_bg())
        t = 0

        # Letterbox bars
        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1, stroke_width=0).move_to(UP * (8 - bh/2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1, stroke_width=0).move_to(DOWN * (8 - bh/2)),
        )

        # Ghost moai — large, faint
        ghost = moai_side(height=10, color=GOLD, stroke_w=0)
        ghost.set_opacity(0.05)
        ghost.move_to(UP * 0.5)
        self.add(ghost)

        stars = star_field(15, seed=99)
        stars.set_opacity(0.2)
        self.add(stars)

        # Divider 1
        div1 = section_div(4, GOLD).move_to(UP * 1)

        # "We spent a century blaming them"
        line1 = safe_text("We spent a century", font="DM Serif Display",
                         font_size=42, color=WHITE_SOFT)
        line1.move_to(DOWN * 0.2)
        line2 = safe_text("blaming them for their", font="DM Serif Display",
                         font_size=42, color=WHITE_SOFT)
        line2.move_to(DOWN * 1.2)
        line3 = safe_text("own extinction.", font="DM Serif Display",
                         font_size=46, color=GOLD)
        line3.move_to(DOWN * 2.3)

        # Divider 2
        div2 = section_div(4, MUTED).move_to(DOWN * 3.3)

        # "The real cause had a name."
        cause = safe_text("The real cause had a name.", font="DM Serif Display",
                         font_size=36, color=MUTED)
        cause.move_to(DOWN * 4.5)

        # "It was us." — the closer
        closer = safe_text("It was us.", font="Bebas Neue", font_size=90, color=WHITE_SOFT)
        closer.move_to(DOWN * 6.2)
        glow = Circle(radius=2.5, fill_color=WHITE_SOFT, fill_opacity=0.04, stroke_width=0)
        glow.move_to(closer)

        # Moai signature
        sig = moai_side(height=0.5, color=GOLD, stroke_w=0).set_opacity(0.4)
        sig.move_to(DOWN * 7.5)

        # Animate — synced to narration (7.20s total)
        # 0.0s: "We spent a century blaming them for their own extinction."
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(line1, shift=UP * 0.08), run_time=0.5); t += 0.5
        self.play(FadeIn(line2, shift=UP * 0.08), run_time=0.5); t += 0.5
        self.play(FadeIn(line3, shift=UP * 0.08), run_time=0.6); t += 0.6

        self.wait(0.3); t += 0.3
        self.play(Create(div2), run_time=0.3); t += 0.3

        # 3.4s: "The real cause had a name."
        self.wait(0.4); t += 0.4
        self.play(FadeIn(cause, shift=UP * 0.06), run_time=0.6); t += 0.6

        # 5.6s: "It was us."
        self.wait(0.8); t += 0.8
        self.play(FadeIn(glow), FadeIn(closer, scale=1.08), run_time=0.8); t += 0.8
        self.play(FadeIn(sig, scale=0.8), run_time=0.2); t += 0.2

        # Fade to black (current 6.6s, need 7.2s → +0.6s)
        target = getattr(self.__class__, 'DURATION', 7.2)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=0.8); t += 0.8


# ── Per-scene render (called via subprocess to isolate memory) ──
def render_single_scene(scene_idx):
    """Render one scene by index. Called as subprocess to free RAM between scenes."""
    scene_classes = [
        Scene1_WrongAnswer,
        Scene2_Contradiction,
        Scene3_OralTradition,
        Scene4_Proof,
        Scene5_Scale,
        Scene6_Punch,
    ]
    SC = scene_classes[scene_idx]
    output_dir = Path(__file__).parent
    config.output_file = f"history_v2_scene_{scene_idx + 1}"
    config.media_dir = str(output_dir / "media")
    SC().render()
    for mp4 in Path(config.media_dir).rglob(f"history_v2_scene_{scene_idx + 1}.mp4"):
        print(f"SCENE_FILE:{mp4}")
        return


# ── MAIN ──────────────────────────────────────────────────────
if __name__ == "__main__":
    import time
    import gc

    output_dir = Path(__file__).parent

    # If --scene N is passed, render just that scene (subprocess mode)
    if "--scene" in sys.argv:
        idx = int(sys.argv[sys.argv.index("--scene") + 1])
        timings_json = os.environ.get("TKK_SCENE_TIMINGS")
        if timings_json:
            import json as _json
            # Override DURATION on the scene class
            _durs = _json.loads(timings_json)
            # Find scene classes
            _scene_classes = [v for k, v in sorted(globals().items()) if k.startswith("Scene") and isinstance(v, type)]
            if idx < len(_scene_classes) and idx < len(_durs):
                _scene_classes[idx].DURATION = _durs[idx]
        render_single_scene(idx)
        sys.exit(0)

    # Otherwise, orchestrate all 6 scenes via subprocesses
    scene_names = [
        "Scene1_WrongAnswer",
        "Scene2_Contradiction",
        "Scene3_OralTradition",
        "Scene4_Proof",
        "Scene5_Scale",
        "Scene6_Punch",
    ]

    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = output_dir / "tts_easter_history.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="history_v2", audio_path=str(audio))
    final = output_dir / "easter_island_history_v2.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
