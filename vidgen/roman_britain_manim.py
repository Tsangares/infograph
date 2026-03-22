#!/usr/bin/env python3
"""You're On Your Own — Roman Britain collapse (Manim). Entropy/decay arc.

6 scenes, ~37.0s (34.0s audio + 3s hold).

VTT cues (absolute → relative):
  Scene 1 (0.0–5.0s = 5.00s):
    0.100 (0.10) In 410 AD, Britain sent a letter to Rome begging for help.
    2.500 (2.50) Rome wrote back:
    3.500 (3.50) You're on your own.
  Scene 2 (5.0–10.0s = 5.00s):
    5.100 (0.10) Textbooks say the Anglo-Saxons invaded
    6.500 (1.50) and destroyed Roman Britain.
    7.800 (2.80) Warriors from Germany swept in and smashed everything.
  Scene 3 (10.0–15.5s = 5.50s):
    10.100 (0.10) But there's almost no evidence of mass invasion.
    12.000 (2.00) What the archaeology shows is stranger.
    13.200 (3.20) The buildings just stopped being maintained.
    14.200 (4.20) The roads crumbled. The baths went cold.
  Scene 4 (15.5–21.0s = 5.50s):
    15.600 (0.10) Within one generation, pottery wheels stopped turning.
    17.200 (1.70) Coin use ended. Literacy vanished.
    18.800 (3.30) People forgot how to make a roof that didn't leak.
    19.800 (4.30) Technology regressed a thousand years.
  Scene 5 (21.0–27.0s = 6.00s):
    21.100 (0.10) Britain had been Roman for 367 years.
    22.800 (1.80) Heated floors. Glass windows. Running water.
    24.500 (3.50) Then Rome left.
    25.500 (4.50) And within 50 years, none of it remained.
  Scene 6 (27.0–37.0s = 10.00s):
    27.100 (0.10) The Romans didn't destroy Britain when they left.
    29.500 (2.50) They just stopped maintaining it.
    31.500 (4.50) And it turns out
    32.500 (5.50) that was enough.
    + 3s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """In 410 AD, Britain begged Rome for help. Rome wrote back: you're on your own. Textbooks say Anglo-Saxons invaded. There's almost no evidence of mass invasion. The buildings just stopped being maintained. Roads crumbled. Baths went cold. Within one generation, pottery wheels stopped. Literacy vanished. People forgot how to make a roof that didn't leak. Britain had been Roman for 367 years. Heated floors. Glass windows. Then Rome left. Within fifty years, none of it remained."""

from manim import (
    Scene, Text, Group, VGroup, Rectangle, RoundedRectangle, Circle,
    Line, Arrow, DashedLine, Dot, Polygon, Ellipse, Square, Arc,
    FadeIn, FadeOut, GrowFromCenter, Write, Create, DrawBorderThenFill,
    AnimationGroup, LaggedStart, Flash, GrowArrow,
    config, UP, DOWN, LEFT, RIGHT, ORIGIN, UL, UR, DL, DR,
    WHITE, BLACK, rate_functions, DEGREES, PI,
)
import numpy as np

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.frame_width = 9
config.frame_height = 16
config.background_color = "#0A0A10"
config.disable_caching = True

BG = "#0A0A10"; SURFACE = "#12121C"; SURFACE2 = "#1A1A26"
BORDER = "#2A2A3A"; GRID = "#14141C"
ROMAN_RED = "#8B1A1A"; STONE_GRAY = "#9E9E8A"
RUIN_BROWN = "#6B4423"; COLD_BLUE = "#3A5A7C"
DECAY_GREEN = "#4A5C3A"
WHITE_SOFT = "#F0F0F0"; MUTED = "#7B8DA0"; DIM = "#404050"
DEAD_GRAY = "#4A5568"; GOLD = "#FFD700"
SAFE_W = 8.0

ZONE_TITLE  = 6.2
ZONE_UPPER  = 3.5
ZONE_MID    = 0.0
ZONE_LOWER  = -3.5
ZONE_FOOTER = -6.0


def gradient_bg(c=BG, g="#0A0A12"):
    bg = Rectangle(width=12, height=20, fill_color=c, fill_opacity=1, stroke_width=0)
    glow = Circle(radius=5, fill_color=g, fill_opacity=0.10, stroke_width=0).move_to(UP * 2)
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

def label_pill(txt, color=STONE_GRAY, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    p = RoundedRectangle(width=t.width+0.5, height=t.height+0.3, corner_radius=0.18,
                         fill_color=bg, fill_opacity=0.95, stroke_color=color, stroke_width=1.5).move_to(t)
    return VGroup(p, t)

def safe_text(content, **kwargs):
    t = Text(content, **kwargs)
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    return t


# ── Domain Shape Helpers ──────────────────────────────────────

def roman_arch(height=3.0, width=2.5, color=STONE_GRAY):
    """Roman arch — semicircular top + two pillars + capstone."""
    sc = height / 3.0
    l_pillar = Rectangle(width=0.4*sc, height=1.8*sc, fill_color=color, fill_opacity=0.8,
                         stroke_color=RUIN_BROWN, stroke_width=1.2)
    l_pillar.move_to(LEFT * 0.8*sc + DOWN * 0.3*sc)
    r_pillar = l_pillar.copy().move_to(RIGHT * 0.8*sc + DOWN * 0.3*sc)
    arch_top = Arc(radius=0.8*sc, start_angle=0, angle=PI,
                   color=color, stroke_width=4*sc)
    arch_top.move_to(UP * 0.6*sc)
    cap = Rectangle(width=2.0*sc, height=0.2*sc, fill_color=color, fill_opacity=0.9,
                    stroke_color=RUIN_BROWN, stroke_width=1)
    cap.move_to(UP * 1.5*sc)
    return VGroup(l_pillar, r_pillar, arch_top, cap)

def letter_scroll(color=STONE_GRAY, h=2.5):
    """Letter/scroll with wax seal."""
    sc = h / 2.5
    body = Rectangle(width=1.8*sc, height=2.2*sc, fill_color=color, fill_opacity=0.15,
                     stroke_color=color, stroke_width=1.5)
    fold = DashedLine(LEFT * 0.7*sc, RIGHT * 0.7*sc, color=color,
                      stroke_width=1, dash_length=0.1*sc)
    fold.move_to(DOWN * 0.4*sc)
    seal = Circle(radius=0.2*sc, fill_color=ROMAN_RED, fill_opacity=0.9,
                  stroke_color=RUIN_BROWN, stroke_width=1)
    seal.move_to(DOWN * 0.8*sc)
    # Curled edges at top/bottom
    top_curl = Arc(radius=0.3*sc, start_angle=0, angle=PI,
                   color=color, stroke_width=2).move_to(UP * 1.15*sc)
    bot_curl = Arc(radius=0.3*sc, start_angle=PI, angle=PI,
                   color=color, stroke_width=2).move_to(DOWN * 1.15*sc)
    return VGroup(body, fold, seal, top_curl, bot_curl)

def broken_road(width=7.0, color=STONE_GRAY):
    """Roman road with cracks — deteriorating surface."""
    sc = width / 7.0
    road = Rectangle(width=7.0*sc, height=0.6*sc, fill_color=color, fill_opacity=0.6,
                     stroke_color=RUIN_BROWN, stroke_width=1)
    # Stone block lines
    blocks = VGroup()
    for i in range(6):
        x = -3.0*sc + i * 1.2*sc
        blocks.add(Line(
            np.array([x, 0.3*sc, 0]), np.array([x, -0.3*sc, 0]),
            color=RUIN_BROWN, stroke_width=0.8
        ).set_opacity(0.4))
    cracks = VGroup()
    np.random.seed(42)
    for i in range(5):
        x_start = -3.0*sc + i * 1.5*sc + np.random.uniform(-0.3, 0.3)*sc
        crack = Line(
            np.array([x_start, 0.3*sc, 0]),
            np.array([x_start + np.random.uniform(-0.3, 0.3)*sc, -0.3*sc, 0]),
            color=RUIN_BROWN, stroke_width=1.5
        )
        cracks.add(crack)
    cracks.set_opacity(0)
    return VGroup(road, blocks, cracks)

def hypocaust(rows=3, cols=4, color=ROMAN_RED):
    """Underfloor heating cross-section — grid of pillar rectangles with heat glow."""
    pillars = VGroup()
    for r in range(rows):
        for c in range(cols):
            p = Rectangle(width=0.25, height=0.5, fill_color=color, fill_opacity=0.7,
                          stroke_color=RUIN_BROWN, stroke_width=0.8)
            p.move_to(np.array([-0.6 + c * 0.4, -0.4 + r * 0.5, 0]))
            pillars.add(p)
    floor = Rectangle(width=cols * 0.4 + 0.3, height=0.15,
                      fill_color=STONE_GRAY, fill_opacity=0.8, stroke_width=0.8,
                      stroke_color=RUIN_BROWN)
    floor.move_to(UP * (rows * 0.5 - 0.15))
    ground = Line(LEFT * (cols * 0.2 + 0.2), RIGHT * (cols * 0.2 + 0.2),
                  color=RUIN_BROWN, stroke_width=2)
    ground.move_to(DOWN * 0.7)
    # Heat waves between pillars
    waves = VGroup()
    for c in range(cols - 1):
        wave = Arc(radius=0.15, start_angle=0, angle=PI,
                   color=ROMAN_RED, stroke_width=1.5).set_opacity(0.5)
        wave.move_to(np.array([-0.4 + c * 0.4, -0.15, 0]))
        waves.add(wave)
    return VGroup(pillars, floor, ground, waves)


# ================================================================
# SCENE 1: THE HOOK (0.0–5.0s = 5.00s)
# "Britain sent a letter to Rome. Rome wrote back: You're on your own."
# Zones: TITLE(pill) UPPER(410 AD) MID(scroll) LOWER(reply text) FOOTER(label)
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 5.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("ROMAN BRITAIN", color=ROMAN_RED, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        yr_410 = safe_text("410 AD", font="Bebas Neue", font_size=140, color=ROMAN_RED)
        yr_410.move_to(UP * ZONE_UPPER)

        scroll = letter_scroll(STONE_GRAY, h=3.0)
        scroll.move_to(UP * ZONE_MID)

        # Decorative line between scroll and reply zone
        div = Line(LEFT * 2.5, RIGHT * 2.5, color=MUTED, stroke_width=1.5)
        div.move_to(DOWN * 1.8)

        # Seal pulse glow behind scroll
        seal_glow = Circle(radius=0.8, fill_color=ROMAN_RED, fill_opacity=0.06, stroke_width=0)
        seal_glow.move_to(scroll.get_center() + DOWN * 0.8)

        on_your_own = safe_text("YOU'RE ON YOUR OWN.", font="Bebas Neue",
                               font_size=85, color=COLD_BLUE)
        on_your_own.move_to(DOWN * ZONE_LOWER)

        # Small arch silhouettes flanking the main text — LOWER zone
        l_arch = roman_arch(1.2, 1.0, DEAD_GRAY).set_opacity(0.25)
        l_arch.move_to(LEFT * 3.2 + DOWN * ZONE_LOWER)
        r_arch = roman_arch(1.2, 1.0, DEAD_GRAY).set_opacity(0.25)
        r_arch.move_to(RIGHT * 3.2 + DOWN * ZONE_LOWER)

        footer = safe_text("RESCRIPT OF HONORIUS", font="Inter",
                          font_size=22, color=DEAD_GRAY, weight="BOLD")
        footer.move_to(DOWN * abs(ZONE_FOOTER))

        # ── Timing: 5.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "In 410 AD, Britain sent a letter to Rome."
        self.play(FadeIn(yr_410, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(yr_410.get_center(), color=ROMAN_RED,
                        line_length=0.5, num_lines=8, run_time=0.3))       # t=1.1
        self.play(FadeIn(scroll, scale=0.9), FadeIn(seal_glow), run_time=0.5); t += 0.5

        # Scroll drifts subtly while we wait
        self.play(scroll.animate.shift(UP * 0.15), run_time=0.6); t += 0.6

        # VTT 2.50: "Rome wrote back:"
        self.play(Create(div), run_time=0.3); t += 0.3

        # VTT 3.50: "You're on your own."
        target = getattr(self.__class__, 'DURATION', 5.0)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeIn(on_your_own, scale=1.15), run_time=0.5); t += 0.5
        self.play(
            Flash(on_your_own.get_center(), color=COLD_BLUE,
                  line_length=0.4, num_lines=10, run_time=0.3),
            FadeIn(l_arch, scale=0.9),
            FadeIn(r_arch, scale=0.9),
        )                                                                   # t=3.8
        self.play(FadeIn(footer), run_time=0.3); t += 0.3

        # Gentle drift on 410 text while holding
        self.play(yr_410.animate.shift(DOWN * 0.1).set_opacity(0.7),
                  run_time=0.9)                                             # t=5.0

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE WRONG ANSWER (5.0–10.0s = 5.00s)
# "Anglo-Saxons invaded. Warriors from Germany smashed everything."
# Zones: TITLE(pill) UPPER(INVADED) MID(arrows→britain) LOWER(ANGLO-SAXONS) FOOTER(label)
# ================================================================
class Scene2_WrongAnswer(Scene):
    DURATION = 5.0
    def construct(self):
        self.add(gradient_bg("#080808"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE TEXTBOOK", color=ROMAN_RED, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        invaded = safe_text("INVADED.", font="Bebas Neue", font_size=110, color=ROMAN_RED)
        invaded.move_to(UP * ZONE_UPPER)

        # Britain shape — simplified island outline at MID zone
        britain = VGroup(
            Rectangle(width=2.0, height=3.5, fill_color=STONE_GRAY,
                      fill_opacity=0.15, stroke_color=STONE_GRAY, stroke_width=1.5),
            # Rough coastline texture dots
            *[Dot(point=np.array([np.random.uniform(-0.9, 0.9),
                                   np.random.uniform(-1.5, 1.5), 0]),
                  radius=0.04, color=STONE_GRAY).set_opacity(0.3)
              for _ in range(12)]
        )
        np.random.seed(22)
        britain.move_to(LEFT * 1.5 + UP * ZONE_MID)
        brit_label = safe_text("BRITAIN", font="Inter", font_size=20,
                              color=STONE_GRAY, weight="BOLD")
        brit_label.move_to(LEFT * 1.5 + UP * ZONE_MID)

        # Invasion arrows — staggered from right
        arrows = VGroup()
        for i in range(4):
            a = Arrow(RIGHT * 3.5, RIGHT * 0.3, color=ROMAN_RED, stroke_width=3, buff=0.1)
            a.move_to(RIGHT * 1.8 + UP * (1.0 - i * 0.7))
            arrows.add(a)

        # Sword shapes flanking — domain visual
        swords = VGroup()
        for x_pos in [LEFT * 3.5, RIGHT * 3.5]:
            blade = Rectangle(width=0.12, height=1.8, fill_color=STONE_GRAY,
                              fill_opacity=0.6, stroke_width=0.8, stroke_color=MUTED)
            guard = Rectangle(width=0.6, height=0.1, fill_color=RUIN_BROWN,
                              fill_opacity=0.7, stroke_width=0.8, stroke_color=MUTED)
            guard.next_to(blade, DOWN, buff=0)
            grip = Rectangle(width=0.1, height=0.4, fill_color=RUIN_BROWN,
                             fill_opacity=0.6, stroke_width=0.5)
            grip.next_to(guard, DOWN, buff=0)
            sword = VGroup(blade, guard, grip).move_to(x_pos + UP * ZONE_MID)
            swords.add(sword)

        anglo = safe_text("ANGLO-SAXONS", font="Bebas Neue", font_size=70, color=ROMAN_RED)
        anglo.move_to(DOWN * abs(ZONE_LOWER) + UP * 0.5)

        smashed = safe_text("\"Smashed everything.\"", font="DM Serif Display",
                           font_size=38, color=MUTED)
        smashed.move_to(DOWN * 4.5)

        footer = safe_text("THE TEXTBOOK VERSION", font="Inter",
                          font_size=22, color=DEAD_GRAY, weight="BOLD")
        footer.move_to(DOWN * abs(ZONE_FOOTER))

        # ── Timing: 5.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "Textbooks say the Anglo-Saxons invaded"
        self.play(FadeIn(invaded, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(invaded.get_center(), color=ROMAN_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=1.1

        # VTT 1.50: "and destroyed Roman Britain."
        self.play(FadeIn(britain), FadeIn(brit_label), run_time=0.4); t += 0.4
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows],
                              lag_ratio=0.12), run_time=0.6)               # t=2.1

        # VTT 2.80: "Warriors from Germany swept in."
        self.play(LaggedStart(*[FadeIn(s, shift=DOWN * 0.3) for s in swords],
                              lag_ratio=0.15), run_time=0.4)               # t=2.5

        # Britain flashes red on impact
        self.play(britain[0].animate.set_color(ROMAN_RED).set_opacity(0.3),
                  run_time=0.3)                                             # t=2.8

        self.play(FadeIn(anglo, scale=1.05), run_time=0.5); t += 0.5
        self.play(FadeIn(smashed, shift=UP * 0.04), run_time=0.5); t += 0.5
        self.play(FadeIn(footer), run_time=0.3); t += 0.3

        # Slow drift on arrows while holding
        self.play(*[a.animate.shift(LEFT * 0.3) for a in arrows],
                  run_time=0.9); t += 0.9                                  # t=5.0

        target = getattr(self.__class__, 'DURATION', 5.0)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:])), run_time=0.3)


# ================================================================
# SCENE 3: THE CONTRADICTION (10.0–15.5s = 5.50s)
# "No evidence of invasion. Buildings stopped being maintained."
# Zones: TITLE(pill) UPPER(NO EVIDENCE) MID(arch crumbling) LOWER(road cracks) FOOTER(label)
# ================================================================
class Scene3_Contradiction(Scene):
    DURATION = 5.5
    def construct(self):
        self.add(gradient_bg(g="#0A0A0A"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE CONTRADICTION", color=COLD_BLUE, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        no_ev = safe_text("NO EVIDENCE.", font="Bebas Neue", font_size=90, color=COLD_BLUE)
        no_ev.move_to(UP * ZONE_UPPER)

        # Roman arch — hero at ZONE_MID
        arch = roman_arch(2.8, 2.2, STONE_GRAY)
        arch.move_to(UP * ZONE_MID)

        # Crack lines on arch (start invisible)
        arch_cracks = VGroup()
        crack_data = [
            (LEFT * 0.6 + UP * 0.8, LEFT * 0.3 + UP * 0.2),
            (RIGHT * 0.5 + UP * 1.0, RIGHT * 0.7 + UP * 0.4),
            (UP * 1.2, UP * 0.6 + RIGHT * 0.2),
            (LEFT * 0.2 + DOWN * 0.1, LEFT * 0.5 + DOWN * 0.6),
        ]
        for start, end in crack_data:
            c = Line(start, end, color=RUIN_BROWN, stroke_width=2)
            c.set_opacity(0)
            arch_cracks.add(c)

        # Broken pottery shards — flanking arch
        pottery_shards = VGroup()
        shard_data = [
            (LEFT * 2.8 + UP * 0.5,  PI * 0.6,  0),
            (LEFT * 3.1 + DOWN * 0.4, PI * 0.75, 40),
            (RIGHT * 2.6 + UP * 0.2, PI * 0.6,  110),
            (RIGHT * 3.0 + DOWN * 0.5, PI * 0.8, 60),
        ]
        for pos, angle, rot in shard_data:
            shard = Arc(radius=0.38, start_angle=np.radians(rot), angle=angle,
                        color=RUIN_BROWN, stroke_width=3.5,
                        fill_color=RUIN_BROWN, fill_opacity=0.30)
            shard.move_to(pos)
            pottery_shards.add(shard)

        # Scattered coins — between MID and LOWER
        coins = VGroup()
        coin_positions = [
            LEFT * 2.8 + DOWN * 2.0, LEFT * 1.5 + DOWN * 2.4,
            ORIGIN + DOWN * 2.1,
            RIGHT * 1.6 + DOWN * 2.5, RIGHT * 3.0 + DOWN * 2.0,
        ]
        for pos in coin_positions:
            coin = Circle(radius=0.20, fill_color=GOLD, fill_opacity=0.65,
                          stroke_color=RUIN_BROWN, stroke_width=1.8)
            coin.move_to(pos)
            coins.add(coin)

        # Broken road — ZONE_LOWER
        road = broken_road(6.5, STONE_GRAY)
        road.move_to(DOWN * 3.5)

        # Fallen column pieces at LOWER zone
        fallen_cols = VGroup()
        for i, x in enumerate([-2.5, 0.5, 3.0]):
            col_piece = Rectangle(width=0.3, height=0.8 + i * 0.2,
                                  fill_color=STONE_GRAY, fill_opacity=0.4,
                                  stroke_color=RUIN_BROWN, stroke_width=1)
            col_piece.rotate(np.radians(15 + i * 25))
            col_piece.move_to(np.array([x, -4.5, 0]))
            fallen_cols.add(col_piece)

        footer = safe_text("ENTROPY.", font="Inter",
                          font_size=22, color=DEAD_GRAY, weight="BOLD")
        footer.move_to(DOWN * abs(ZONE_FOOTER))

        # ── Timing: 5.50s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "But there's almost no evidence of mass invasion."
        self.play(FadeIn(no_ev, scale=1.08), run_time=0.5); t += 0.5

        # VTT 2.00: "What the archaeology shows is stranger."
        self.wait(0.9); t += 0.9
        self.play(FadeIn(arch, scale=0.9), run_time=0.5); t += 0.5
        self.play(
            LaggedStart(*[FadeIn(s, scale=0.85) for s in pottery_shards], lag_ratio=0.08),
            run_time=0.4,
        )                                                                   # t=2.6

        # VTT 3.20: "The buildings just stopped being maintained."
        self.wait(0.3); t += 0.3
        self.add(arch_cracks)
        self.play(
            *[c.animate.set_opacity(0.9) for c in arch_cracks],
            arch.animate.set_opacity(0.5),
            run_time=0.5,
        )                                                                   # t=3.4

        # Arch sags slightly — visual decay
        self.play(arch.animate.shift(DOWN * 0.15).scale(0.97),
                  run_time=0.3)                                             # t=3.7

        # VTT 4.20: "The roads crumbled. The baths went cold."
        self.play(FadeIn(road), run_time=0.3); t += 0.3
        road_cracks = road[2]  # index 2 now (road, blocks, cracks)
        self.play(
            LaggedStart(*[FadeIn(c, scale=0.9) for c in coins], lag_ratio=0.06),
            *[c.animate.set_opacity(0.8) for c in road_cracks],
            run_time=0.4,
        )                                                                   # t=4.4
        self.play(
            LaggedStart(*[FadeIn(fc, scale=0.8) for fc in fallen_cols], lag_ratio=0.1),
            run_time=0.3,
        )                                                                   # t=4.7
        self.play(FadeIn(footer), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 5.5)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE PROOF (15.5–21.0s = 5.50s)
# "Pottery, coins, literacy, roofs — all lost. 1,000 years regression."
# Zones: TITLE(pill) UPPER(ONE GENERATION) MID(4 icons crossed) LOWER(1000 YRS) FOOTER(label)
# ================================================================
class Scene4_Proof(Scene):
    DURATION = 5.5
    def construct(self):
        self.add(gradient_bg("#080808"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE REGRESSION", color=RUIN_BROWN, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        one_gen = safe_text("ONE GENERATION.", font="Bebas Neue", font_size=80,
                           color=STONE_GRAY)
        one_gen.move_to(UP * ZONE_UPPER)

        # 4 domain-shape icons in 2x2 grid at ZONE_MID — each gets crossed out
        # Pottery wheel
        pottery = VGroup(
            Circle(radius=0.55, fill_color="#2E2E50", fill_opacity=0.9,
                   stroke_color=RUIN_BROWN, stroke_width=2),
            Circle(radius=0.25, fill_color=RUIN_BROWN, fill_opacity=0.4,
                   stroke_color=RUIN_BROWN, stroke_width=1),
            # Spokes
            *[Line(ORIGIN, UP * 0.5, color=RUIN_BROWN, stroke_width=1).rotate(i * PI / 3)
              for i in range(6)]
        )
        # Coin
        coin_icon = VGroup(
            Circle(radius=0.5, fill_color="#2E2E50", fill_opacity=0.9,
                   stroke_color=GOLD, stroke_width=2),
            Circle(radius=0.35, fill_color=GOLD, fill_opacity=0.3,
                   stroke_color=GOLD, stroke_width=1),
            safe_text("S", font="Bebas Neue", font_size=28, color=GOLD),
        )
        # Tablet (literacy)
        tablet = VGroup(
            Rectangle(width=0.7, height=0.9, fill_color="#2E2E50", fill_opacity=0.9,
                      stroke_color=STONE_GRAY, stroke_width=2),
            *[Line(LEFT * 0.2, RIGHT * 0.2, color=STONE_GRAY, stroke_width=1)
              .move_to(UP * (0.2 - i * 0.2)) for i in range(3)]
        )
        # Roof
        roof = VGroup(
            Polygon(LEFT * 0.6, RIGHT * 0.6, UP * 0.5,
                    fill_color="#2E2E50", fill_opacity=0.9,
                    stroke_color=RUIN_BROWN, stroke_width=2),
            Rectangle(width=0.9, height=0.5, fill_color="#2E2E50", fill_opacity=0.7,
                      stroke_color=RUIN_BROWN, stroke_width=1.5).move_to(DOWN * 0.35),
        )

        icon_data = [
            (pottery,   "POTTERY",  LEFT * 2 + UP * 0.3),
            (coin_icon, "COINS",    RIGHT * 2 + UP * 0.3),
            (tablet,    "LITERACY", LEFT * 2 + DOWN * 1.5),
            (roof,      "ROOFS",    RIGHT * 2 + DOWN * 1.5),
        ]

        icon_groups = []
        icon_crosses = []
        for shape, txt, pos in icon_data:
            shape.move_to(pos)
            shape.scale_to_fit_height(1.1)
            shape.move_to(pos)
            label = safe_text(txt, font="Inter", font_size=20, color=WHITE_SOFT, weight="BOLD")
            label.move_to(pos + DOWN * 0.9)
            icon_groups.append(VGroup(shape, label))

            x1 = Line(pos + LEFT * 0.45 + UP * 0.45, pos + RIGHT * 0.45 + DOWN * 0.45,
                      color=ROMAN_RED, stroke_width=4)
            x2 = Line(pos + RIGHT * 0.45 + UP * 0.45, pos + LEFT * 0.45 + DOWN * 0.45,
                      color=ROMAN_RED, stroke_width=4)
            icon_crosses.append(VGroup(x1, x2))

        thousand = safe_text("1,000 YEARS", font="Bebas Neue", font_size=100,
                            color=ROMAN_RED)
        thousand.move_to(DOWN * 3.8)

        regressed = safe_text("OF REGRESSION", font="Inter", font_size=28,
                             color=MUTED, weight="BOLD")
        regressed.move_to(DOWN * 5.0)

        footer = safe_text("TECHNOLOGY LOST", font="Inter",
                          font_size=22, color=DEAD_GRAY, weight="BOLD")
        footer.move_to(DOWN * abs(ZONE_FOOTER))

        # ── Timing: 5.50s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "Within one generation, pottery wheels stopped."
        self.play(FadeIn(one_gen, scale=1.05), run_time=0.4); t += 0.4

        self.play(LaggedStart(*[FadeIn(p, scale=0.9) for p in icon_groups],
                              lag_ratio=0.12), run_time=0.6)               # t=1.3

        # VTT 1.70: "Coin use ended. Literacy vanished."
        self.wait(0.2); t += 0.2
        self.play(Create(icon_crosses[0]), run_time=0.25); t += 0.25
        self.play(Create(icon_crosses[1]), run_time=0.25); t += 0.25

        # Icons dim after being crossed
        self.play(
            icon_groups[0].animate.set_opacity(0.35),
            icon_groups[1].animate.set_opacity(0.35),
            run_time=0.3,
        )                                                                   # t=2.3

        # VTT 3.30: "People forgot how to make a roof."
        self.wait(0.7); t += 0.7
        self.play(Create(icon_crosses[2]), run_time=0.25); t += 0.25
        self.play(Create(icon_crosses[3]), run_time=0.25); t += 0.25
        self.play(
            icon_groups[2].animate.set_opacity(0.35),
            icon_groups[3].animate.set_opacity(0.35),
            run_time=0.3,
        )                                                                   # t=3.8

        # VTT 4.30: "Technology regressed a thousand years."
        self.play(FadeIn(thousand, scale=1.15), run_time=0.5); t += 0.5
        self.play(Flash(thousand.get_center(), color=ROMAN_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=4.6
        self.play(FadeIn(regressed), FadeIn(footer), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 5.5)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE SCALE (21.0–27.0s = 6.00s)
# "367 years Roman. 50 years: gone."
# Zones: TITLE(pill) UPPER(367 YRS) MID(hypocaust+amenities) LOWER(50 YRS) FOOTER(none remained)
# ================================================================
class Scene5_Scale(Scene):
    DURATION = 6.0
    def construct(self):
        self.add(gradient_bg(g="#0A0A08"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE SCALE", color=STONE_GRAY, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        three67 = safe_text("367 YEARS", font="Bebas Neue", font_size=100,
                           color=WHITE_SOFT)
        three67.move_to(UP * ZONE_UPPER)
        roman_l = safe_text("ROMAN BRITAIN", font="Inter", font_size=28,
                           color=WHITE_SOFT, weight="BOLD")
        roman_l.move_to(UP * 2.0)

        # Hypocaust cross-section at MID — domain shape showing heated floors
        hyp = hypocaust(3, 4, ROMAN_RED)
        hyp.scale(1.8)
        hyp.move_to(LEFT * 2.2 + UP * ZONE_MID)

        # Glass window shape
        window = VGroup(
            Rectangle(width=0.8, height=1.2, fill_color=COLD_BLUE, fill_opacity=0.2,
                      stroke_color=COLD_BLUE, stroke_width=1.5),
            Line(UP * 0.6, DOWN * 0.6, color=COLD_BLUE, stroke_width=1),
            Line(LEFT * 0.4, RIGHT * 0.4, color=COLD_BLUE, stroke_width=1),
            # Pane shimmer
            Rectangle(width=0.15, height=0.4, fill_color=COLD_BLUE, fill_opacity=0.15,
                      stroke_width=0).move_to(LEFT * 0.15 + UP * 0.2),
        )
        window.move_to(RIGHT * 0.5 + UP * ZONE_MID)

        # Aqueduct (running water) — arched channel
        aqueduct = VGroup(
            # Channel
            Rectangle(width=2.0, height=0.15, fill_color=COLD_BLUE, fill_opacity=0.5,
                      stroke_color=STONE_GRAY, stroke_width=1).move_to(UP * 0.6),
            # Support arches
            *[VGroup(
                Arc(radius=0.3, start_angle=0, angle=PI, color=STONE_GRAY, stroke_width=2)
                    .move_to(LEFT * 0.7 + RIGHT * i * 0.7),
                Line(LEFT * 0.7 + RIGHT * i * 0.7 + LEFT * 0.3,
                     LEFT * 0.7 + RIGHT * i * 0.7 + LEFT * 0.3 + DOWN * 0.5,
                     color=STONE_GRAY, stroke_width=1.5),
                Line(LEFT * 0.7 + RIGHT * i * 0.7 + RIGHT * 0.3,
                     LEFT * 0.7 + RIGHT * i * 0.7 + RIGHT * 0.3 + DOWN * 0.5,
                     color=STONE_GRAY, stroke_width=1.5),
            ) for i in range(3)]
        )
        aqueduct.move_to(RIGHT * 2.8 + UP * ZONE_MID)

        # Labels under each amenity
        hyp_label = safe_text("HEATED FLOORS", font="Inter", font_size=16,
                              color=MUTED, weight="BOLD")
        hyp_label.next_to(hyp, DOWN, buff=0.2)
        win_label = safe_text("GLASS", font="Inter", font_size=16,
                              color=MUTED, weight="BOLD")
        win_label.next_to(window, DOWN, buff=0.2)
        aq_label = safe_text("WATER", font="Inter", font_size=16,
                             color=MUTED, weight="BOLD")
        aq_label.next_to(aqueduct, DOWN, buff=0.2)

        amenity_all = VGroup(hyp, window, aqueduct, hyp_label, win_label, aq_label)

        fifty = safe_text("50 YEARS", font="Bebas Neue", font_size=120, color=COLD_BLUE)
        fifty.move_to(DOWN * ZONE_LOWER + DOWN * 0.3)

        # Decay dust particles at LOWER zone
        dust = VGroup()
        np.random.seed(88)
        for _ in range(15):
            d = Dot(point=np.array([np.random.uniform(-3.5, 3.5),
                                     np.random.uniform(-5.0, -2.5), 0]),
                    radius=np.random.uniform(0.02, 0.06),
                    color=RUIN_BROWN).set_opacity(np.random.uniform(0.2, 0.5))
            dust.add(d)

        footer_text = safe_text("NONE REMAINED.", font="Inter",
                               font_size=22, color=DEAD_GRAY, weight="BOLD")
        footer_text.move_to(DOWN * abs(ZONE_FOOTER))

        # ── Timing: 6.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "Britain had been Roman for 367 years."
        self.play(FadeIn(three67, scale=1.1), run_time=0.5); t += 0.5
        self.play(FadeIn(roman_l), run_time=0.3); t += 0.3

        # VTT 1.80: "Heated floors. Glass windows. Running water."
        self.wait(0.4); t += 0.4
        self.play(FadeIn(hyp, scale=0.9), FadeIn(hyp_label), run_time=0.4); t += 0.4
        self.play(FadeIn(window, scale=0.95), FadeIn(win_label), run_time=0.4); t += 0.4
        self.play(FadeIn(aqueduct, scale=0.95), FadeIn(aq_label), run_time=0.4); t += 0.4

        # Amenities glow pulse
        self.play(
            hyp.animate.set_opacity(1.0),
            window.animate.set_opacity(1.0),
            run_time=0.3,
        )                                                                   # t=3.0

        # VTT 3.50: "Then Rome left."
        self.wait(0.2); t += 0.2
        # Everything fades — Rome leaves
        self.play(
            amenity_all.animate.set_opacity(0.15),
            three67.animate.set_opacity(0.35),
            roman_l.animate.set_opacity(0.35),
            run_time=0.8,
        )                                                                   # t=4.0

        # VTT 4.50: "And within 50 years, none of it remained."
        self.play(
            FadeIn(fifty, scale=1.2),
            LaggedStart(*[FadeIn(d) for d in dust], lag_ratio=0.03),
            run_time=0.5,
        )                                                                   # t=4.5
        self.play(Flash(fifty.get_center(), color=COLD_BLUE,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=4.8

        # Dust drifts downward
        self.play(
            *[d.animate.shift(DOWN * 0.4) for d in dust],
            FadeIn(footer_text),
            run_time=0.5,
        )                                                                   # t=5.3
        target = getattr(self.__class__, 'DURATION', 6.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE PUNCH (27.0–37.0s = 10.00s)
# "They didn't destroy it. They just stopped maintaining it. That was enough."
# Zones: TITLE(letterbox) UPPER(arch decaying) MID(divider) LOWER(maintaining) FOOTER(enough)
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 10.0
    def construct(self):
        self.add(gradient_bg("#050508"), grid_lines(0.02))
        t = 0

        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP * (8 - bh/2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN * (8 - bh/2)),
        )

        # Standing arch — ZONE_UPPER, will slowly decay
        arch = roman_arch(3.5, 3.0, STONE_GRAY)
        arch.move_to(UP * ZONE_UPPER + DOWN * 0.5)

        # Rubble beneath arch — small scattered rectangles
        rubble = VGroup()
        np.random.seed(66)
        for _ in range(8):
            piece = Rectangle(
                width=np.random.uniform(0.15, 0.4),
                height=np.random.uniform(0.1, 0.25),
                fill_color=STONE_GRAY, fill_opacity=0.4,
                stroke_color=RUIN_BROWN, stroke_width=0.8,
            )
            piece.rotate(np.random.uniform(0, PI))
            piece.move_to(np.array([
                np.random.uniform(-1.5, 1.5),
                np.random.uniform(0.5, 1.5),
                0
            ]))
            rubble.add(piece)

        slow_cracks = VGroup()
        crack_points = [
            (LEFT * 0.9 + UP * 4.5, LEFT * 0.4 + UP * 3.5),
            (RIGHT * 0.7 + UP * 4.3, RIGHT * 1.0 + UP * 3.3),
            (UP * 5.0, UP * 4.0 + LEFT * 0.3),
            (LEFT * 0.3 + UP * 3.0, LEFT * 0.6 + UP * 2.3),
        ]
        for s, e in crack_points:
            c = Line(s, e, color=RUIN_BROWN, stroke_width=2)
            c.set_opacity(0)
            slow_cracks.add(c)
        self.add(slow_cracks)

        div1 = Line(LEFT * 2, RIGHT * 2, color=MUTED, stroke_width=1.5)
        div1.move_to(UP * ZONE_MID + DOWN * 0.2)

        div2 = Line(LEFT * 2, RIGHT * 2, color=COLD_BLUE, stroke_width=1.5)
        div2.move_to(DOWN * 2.5)

        maintaining = safe_text("MAINTAINING.", font="Bebas Neue", font_size=80,
                               color=COLD_BLUE)
        maintaining.move_to(DOWN * ZONE_LOWER)

        enough = safe_text("ENOUGH.", font="Bebas Neue",
                          font_size=70, color=STONE_GRAY)
        enough.move_to(DOWN * abs(ZONE_FOOTER) + UP * 0.3)

        glow = Circle(radius=2.5, fill_color=COLD_BLUE, fill_opacity=0.04, stroke_width=0)
        glow.move_to(maintaining)

        # ── Timing: 10.00s ──
        # VTT 0.10: "The Romans didn't destroy Britain when they left."
        self.play(FadeIn(arch, scale=0.95), run_time=0.6); t += 0.6

        self.play(
            *[c.animate.set_opacity(0.6) for c in slow_cracks[:2]],
            run_time=0.8,
        )                                                                   # t=1.4
        self.play(Create(div1), run_time=0.3); t += 0.3

        # VTT 2.50: "They just stopped maintaining it."
        self.wait(0.6); t += 0.6
        self.play(
            *[c.animate.set_opacity(0.8) for c in slow_cracks[2:]],
            arch.animate.set_opacity(0.4),
            run_time=0.6,
        )                                                                   # t=2.9

        # Rubble falls from the arch
        self.play(
            LaggedStart(*[FadeIn(r, shift=DOWN * 0.5) for r in rubble], lag_ratio=0.05),
            run_time=0.4,
        )                                                                   # t=3.3

        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(FadeIn(glow), FadeIn(maintaining, scale=1.08), run_time=0.7); t += 0.7

        # VTT 4.50/5.50: "And it turns out that was enough."
        self.wait(0.7); t += 0.7
        self.play(FadeIn(enough, shift=UP * 0.06), run_time=0.6); t += 0.6

        # Slow decay: arch fades further, rubble drifts
        self.play(
            arch.animate.set_opacity(0.15),
            *[r.animate.shift(DOWN * 0.3).set_opacity(0.2) for r in rubble],
            run_time=1.4,
        )                                                                   # t=7.0

        # Final hold
        self.wait(1.0); t += 1.0

        # Fade to black
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5
        target = getattr(self.__class__, 'DURATION', 10.0)
        self.wait(max(0.1, target - t - 0.8))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ── Infra ─────────────────────────────────────────────────────
def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_WrongAnswer, Scene3_Contradiction,
          Scene4_Proof, Scene5_Scale, Scene6_Punch]
    config.output_file = f"roman_britain_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"roman_britain_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    sc = [Scene1_Hook, Scene2_WrongAnswer, Scene3_Contradiction,
          Scene4_Proof, Scene5_Scale, Scene6_Punch]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(sc):
        n = f"roman_britain_scene_{i+1}"; print(f"  Preview {n}...")
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
            _classes = sorted([v for k,v in globals().items() if k.startswith("Scene") and len(k) > 5 and k[5].isdigit() and isinstance(v, type)], key=lambda c: c.__name__); _classes[_idx].DURATION = json.loads(timings_json)[_idx]
        render_single_scene(int(sys.argv[sys.argv.index("--scene")+1])); sys.exit(0)

    names = ["Scene1_Hook","Scene2_WrongAnswer","Scene3_Contradiction",
             "Scene4_Proof","Scene5_Scale","Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_roman_britain.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="roman_britain", audio_path=str(audio))
    final = od / "roman_britain_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
