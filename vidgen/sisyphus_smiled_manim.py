#!/usr/bin/env python3
"""Sisyphus Was Smiling — Why the absurd hero laughs.

6 scenes, ~45.0s (42.0s audio + 3s hold).
Domain shapes: boulder_round, hill_slope, figure_push, treasure_chest.

VTT cues (absolute → relative):
  Scene 1 (0.0–7.0s):   0.30 having peeled back... 3.50 you arrive... 5.50 laughter
  Scene 2 (7.0–14.0s):  7.20 not bitter... 9.40 elaborate machinery... 12.00 chooses to live
  Scene 3 (14.0–21.0s): 14.20 absurd hero sees... 16.80 all meaning... 19.00 story we tell
  Scene 4 (21.0–28.0s): 21.20 picks up rock... 24.00 carries it... 26.50 not because
  Scene 5 (28.0–35.0s): 28.80 because she is alive... 31.50 alive is what... 33.50 imagine
  Scene 6 (35.0–45.0s): 35.20 sisyphus smiling... 38.00 not because he found... 40.50 stopped needing
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """Having peeled back every layer — acceptance, critique, refusal, reclamation — you arrive at laughter. Not bitter. The laugh of someone who sees the machinery of success and chooses to live anyway. All measurement is human. All meaning constructed. All success a story. She picks up the rock again. Not because it has meaning. Because she's alive. Imagine Sisyphus smiling. Not because he found a reason. Because he stopped needing one."""

from manim import (
    Scene, Text, Group, VGroup, Group, Rectangle, RoundedRectangle, Circle,
    Line, Arrow, DashedLine, Dot, Polygon, Ellipse, Square, Arc,
    FadeIn, FadeOut, GrowFromCenter, Write, Create, DrawBorderThenFill,
    AnimationGroup, LaggedStart, Flash, GrowArrow, MoveToTarget,
    config, UP, DOWN, LEFT, RIGHT, ORIGIN,
    WHITE, BLACK, rate_functions, DEGREES, PI,
)
import numpy as np

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.frame_width = 9
config.frame_height = 16
config.background_color = "#080A10"
config.disable_caching = True

BG = "#080A10"; GRID = "#1A2030"; SURFACE = "#15192A"
WHITE_SOFT = "#F0F0F0"; GOLD = "#FFD700"; MUTED = "#475569"
STONE_GREY = "#8B8B8B"; HILL_BROWN = "#5C4033"; WARM_AMBER = "#FFBF00"
DEFIANCE_BLUE = "#3B82F6"; ALIVE_GREEN = "#22C55E"; CHEST_GOLD = "#C4A747"
MIRROR_CYAN = "#67E8F9"; DEEP_RED = "#DC2626"
SAFE_W = 8.0

ZONE_TITLE = 6.2
ZONE_UPPER = 3.5
ZONE_MID = 0.0
ZONE_LOWER = -3.5
ZONE_FOOTER = -6.0


# ── Core helpers ─────────────────────────────────────────────

def gradient_bg(c=BG, g="#121828"):
    bg = Rectangle(width=12, height=20, fill_color=c, fill_opacity=1, stroke_width=0)
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
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    return t

def label_pill(txt, color=GOLD, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    p = RoundedRectangle(width=t.width+0.5, height=t.height+0.3, corner_radius=0.15,
                         fill_color=bg, fill_opacity=0.9, stroke_width=0).move_to(t)
    return VGroup(p, t)


# ── Domain shapes (4 required) ──────────────────────────────

def boulder_round(radius=1.2, color=STONE_GREY):
    """Heavy boulder — rough circle with texture lines."""
    body = Circle(radius=radius, fill_color=color, fill_opacity=0.85,
                  stroke_color="#6B6B6B", stroke_width=2.5)
    cracks = VGroup()
    for angle, length in [(30, 0.6), (150, 0.5), (250, 0.4), (80, 0.35)]:
        rad = angle * PI / 180
        start = np.array([np.cos(rad) * radius * 0.3, np.sin(rad) * radius * 0.3, 0])
        end = start + np.array([np.cos(rad + 0.4) * length, np.sin(rad + 0.4) * length, 0])
        cracks.add(Line(start, end, color="#6B6B6B", stroke_width=1.5).set_opacity(0.5))
    return VGroup(body, cracks)

def hill_slope(width=8, height=6, color=HILL_BROWN):
    """Steep hill — a filled triangle slope."""
    slope = Polygon(
        np.array([-width/2, -height/2, 0]),
        np.array([width/2, -height/2, 0]),
        np.array([width * 0.3, height/2, 0]),
        fill_color=color, fill_opacity=0.3, stroke_color=color, stroke_width=1.5,
    )
    ridges = VGroup()
    for frac in [0.25, 0.5, 0.75]:
        x_start = -width/2 + width * frac * 0.5
        y_start = -height/2 + height * frac
        x_end = width/2 - width * (1 - frac) * 0.3
        y_end = -height/2 + height * frac * 0.6
        ridges.add(Line(
            np.array([x_start, y_start, 0]), np.array([x_end, y_end, 0]),
            color=color, stroke_width=0.8,
        ).set_opacity(0.3))
    return VGroup(slope, ridges)

def figure_push(height=2.0, color=WHITE_SOFT, lean=True):
    """Stick figure in pushing posture — head, torso, arms forward, legs braced."""
    h = height
    head = Circle(radius=h * 0.08, fill_color=color, fill_opacity=0.9, stroke_width=0)
    head.move_to(UP * h * 0.38 + (LEFT * h * 0.05 if lean else ORIGIN))
    torso = Line(
        np.array([-h*0.03, h*0.3, 0]) if lean else np.array([0, h*0.3, 0]),
        np.array([h*0.05, -h*0.05, 0]) if lean else np.array([0, -h*0.05, 0]),
        color=color, stroke_width=2.5,
    )
    arm = Line(
        np.array([-h*0.01, h*0.2, 0]),
        np.array([-h*0.25, h*0.25, 0]) if lean else np.array([-h*0.2, h*0.1, 0]),
        color=color, stroke_width=2,
    )
    leg_l = Line(np.array([h*0.05, -h*0.05, 0]), np.array([h*0.18, -h*0.45, 0]),
                 color=color, stroke_width=2)
    leg_r = Line(np.array([h*0.05, -h*0.05, 0]), np.array([-h*0.08, -h*0.45, 0]),
                 color=color, stroke_width=2)
    return VGroup(head, torso, arm, leg_l, leg_r)

def treasure_chest(width=2.5, height=1.8, color=CHEST_GOLD):
    """Treasure chest — box with arched lid."""
    base = Rectangle(width=width, height=height * 0.5, fill_color=color,
                     fill_opacity=0.7, stroke_color="#8B6914", stroke_width=2)
    base.move_to(DOWN * height * 0.15)
    lid = Arc(radius=width * 0.52, angle=PI, fill_color=color,
              fill_opacity=0.6, stroke_color="#8B6914", stroke_width=2)
    lid.move_to(UP * height * 0.1)
    lock = Circle(radius=height * 0.06, fill_color="#8B6914", fill_opacity=0.9,
                  stroke_width=0)
    lock.move_to(base.get_top())
    band_l = Line(base.get_left() + RIGHT * width * 0.25 + DOWN * height * 0.25,
                  lid.get_top() + LEFT * width * 0.1,
                  color="#8B6914", stroke_width=1.5).set_opacity(0.5)
    band_r = Line(base.get_right() + LEFT * width * 0.25 + DOWN * height * 0.25,
                  lid.get_top() + RIGHT * width * 0.1,
                  color="#8B6914", stroke_width=1.5).set_opacity(0.5)
    return VGroup(base, lid, lock, band_l, band_r)


# ================================================================
# SCENE 1: THE HOOK (0.0–7.0s)
# Figure pushing boulder up hill — camera reveals they're smiling
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 2.1
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("SISYPHUS WAS SMILING", color=WARM_AMBER)
        pill.move_to(UP * ZONE_TITLE)

        # Hill slope behind everything — fills lower frame
        hill = hill_slope(width=9, height=10, color=HILL_BROWN)
        hill.move_to(DOWN * 1)

        # Figure pushing — centered at MID
        fig = figure_push(height=2.2, color=WHITE_SOFT)
        fig.move_to(LEFT * 0.8 + UP * ZONE_MID)

        # Boulder — large, pressing against the figure
        rock = boulder_round(radius=1.4, color=STONE_GREY)
        rock.move_to(LEFT * 2.8 + UP * (ZONE_MID + 0.5))

        # Sweat drops — animated falling
        drops = VGroup()
        for dx, dy in [(0.3, 0.8), (0.5, 0.6), (0.15, 0.5)]:
            d = Dot(radius=0.05, color=DEFIANCE_BLUE).set_opacity(0.6)
            d.move_to(fig.get_top() + RIGHT * dx + UP * dy)
            drops.add(d)

        # Smile arc — revealed later
        smile = Arc(radius=0.25, angle=-PI * 0.6, color=WARM_AMBER,
                    stroke_width=3).move_to(fig[0].get_center() + DOWN * 0.05)
        smile.set_opacity(0)

        # Layer count at footer — the journey recap
        layers = VGroup()
        layer_names = ["ACCEPTANCE", "CRITIQUE", "REFUSAL", "RECLAMATION"]
        layer_colors = [MUTED, MUTED, MUTED, MUTED]
        for i, (nm, col) in enumerate(zip(layer_names, layer_colors)):
            lbl = safe_text(nm, font="Inter", font_size=20, color=col)
            lbl.move_to(LEFT * 3.5 + RIGHT * i * 2.3 + UP * ZONE_FOOTER)
            layers.add(lbl)

        self.play(FadeIn(hill, scale=1.02), run_time=0.4); t += 0.4
        self.play(FadeIn(fig, shift=RIGHT * 0.2), run_time=0.5); t += 0.5
        self.play(FadeIn(rock, scale=0.9), run_time=0.5); t += 0.5

        # Sweat drops fall
        self.play(LaggedStart(*[FadeIn(d, shift=DOWN * 0.3) for d in drops],
                              lag_ratio=0.15), run_time=0.6)                  # t=2.0

        # Figure strains — boulder and figure shift slightly uphill
        self.play(fig.animate.shift(UP * 0.3 + LEFT * 0.15),
                  rock.animate.shift(UP * 0.2 + LEFT * 0.1),
                  run_time=1.2)                                               # t=3.2

        # Drops drift down and fade
        self.play(*[d.animate.shift(DOWN * 0.5).set_opacity(0) for d in drops],
                  run_time=0.5)                                               # t=3.7

        # Reveal: the smile
        self.play(smile.animate.set_opacity(1), run_time=0.4); t += 0.4
        self.play(Flash(smile.get_center(), color=WARM_AMBER,
                        line_length=0.2, num_lines=8, run_time=0.3))         # t=4.4

        # Pill fades in
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4

        # Layer labels at footer
        self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.1) for l in layers],
                              lag_ratio=0.08), run_time=0.6)                  # t=5.4

        # Strikethrough each layer — peeled back
        strikes = VGroup()
        for lbl in layers:
            strike = Line(lbl.get_left(), lbl.get_right(),
                         color=WARM_AMBER, stroke_width=1.5)
            strikes.add(strike)
        self.play(LaggedStart(*[Create(s) for s in strikes],
                              lag_ratio=0.08), run_time=0.6)                  # t=6.0

        target = getattr(self.__class__, 'DURATION', 2.1)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE JOURNEY (7.0–14.0s)
# Philosophical path — signposts up a winding mountain
# ================================================================
class Scene2_Journey(Scene):
    DURATION = 8.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE LONG WAY UP", color=GOLD)
        pill.move_to(UP * ZONE_TITLE)
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # Winding path — series of connected segments going up
        path_points = [
            np.array([-2, -5.5, 0]), np.array([1.5, -4, 0]),
            np.array([-1, -2.5, 0]), np.array([2, -1, 0]),
            np.array([-0.5, 0.5, 0]), np.array([1.5, 2, 0]),
            np.array([0, 3.5, 0]),
        ]
        path_lines = VGroup()
        for i in range(len(path_points) - 1):
            seg = Line(path_points[i], path_points[i+1],
                       color=MUTED, stroke_width=2).set_opacity(0.5)
            path_lines.add(seg)

        self.play(LaggedStart(*[Create(seg) for seg in path_lines],
                              lag_ratio=0.12), run_time=1.5)                  # t=1.8

        # Signposts at each station
        stations = [
            ("NAIVE BELIEF", WARM_AMBER, path_points[1]),
            ("CRITIQUE", GOLD, path_points[2]),
            ("NIHILISM", DEEP_RED, path_points[3]),
            ("EXISTENTIALISM", DEFIANCE_BLUE, path_points[4]),
            ("SURRENDER", ALIVE_GREEN, path_points[5]),
        ]

        signs = VGroup()
        for txt, col, pos in stations:
            sign_txt = safe_text(txt, font="Inter", font_size=22, color=col, weight="BOLD")
            sign_bg = RoundedRectangle(width=sign_txt.width + 0.3, height=sign_txt.height + 0.2,
                                        corner_radius=0.1, fill_color=SURFACE,
                                        fill_opacity=0.85, stroke_width=0)
            sign_bg.move_to(sign_txt)
            sign = VGroup(sign_bg, sign_txt).move_to(pos + RIGHT * 1.8)
            post = Line(pos, sign.get_left(), color=col, stroke_width=1).set_opacity(0.4)
            signs.add(VGroup(post, sign))

        self.play(LaggedStart(*[FadeIn(s, shift=RIGHT * 0.2) for s in signs],
                              lag_ratio=0.2), run_time=2.0)                   # t=3.8

        # Small figure climbing the path
        climber = figure_push(height=1.0, color=WHITE_SOFT, lean=True)
        climber.move_to(path_points[0])
        self.play(FadeIn(climber, scale=0.8), run_time=0.3); t += 0.3

        # Climber moves up the path
        self.play(climber.animate.move_to(path_points[3]), run_time=1.2); t += 1.2

        # Question mark at the top
        q_mark = safe_text("?", font="Bebas Neue", font_size=120, color=GOLD)
        q_mark.move_to(path_points[-1] + UP * 1)
        self.play(FadeIn(q_mark, scale=1.3), run_time=0.5); t += 0.5
        self.play(Flash(q_mark.get_center(), color=GOLD,
                        line_length=0.4, num_lines=10, run_time=0.3))        # t=6.1

        target = getattr(self.__class__, 'DURATION', 8.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: THE WRONG ANSWER (14.0–21.0s)
# Treasure chest at the summit — cracks open to reveal nothing
# ================================================================
class Scene3_WrongAnswer(Scene):
    DURATION = 1.7
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE WRONG FRAME", color=DEEP_RED)
        pill.move_to(UP * ZONE_TITLE)
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # Mountain peak at upper zone
        peak = Polygon(
            np.array([-3, -2, 0]), np.array([3, -2, 0]), np.array([0, 3.5, 0]),
            fill_color=HILL_BROWN, fill_opacity=0.25, stroke_color=HILL_BROWN,
            stroke_width=1.5,
        )
        peak.move_to(UP * ZONE_UPPER)
        self.play(FadeIn(peak, scale=0.95), run_time=0.4); t += 0.4

        # Treasure chest at peak
        chest = treasure_chest(width=2.2, height=1.6, color=CHEST_GOLD)
        chest.move_to(UP * (ZONE_UPPER + 1.5))
        self.play(GrowFromCenter(chest), run_time=0.5); t += 0.5

        # Glowing label above chest
        meaning_lbl = safe_text("MEANING", font="Bebas Neue",
                                font_size=40, color=CHEST_GOLD)
        meaning_lbl.move_to(chest.get_top() + UP * 0.5)
        self.play(FadeIn(meaning_lbl, shift=DOWN * 0.1), run_time=0.4); t += 0.4

        # Small figure climbing toward it
        climber = figure_push(height=1.2, color=WHITE_SOFT)
        climber.move_to(UP * ZONE_MID + LEFT * 1)
        self.play(FadeIn(climber, shift=UP * 0.2), run_time=0.4); t += 0.4

        # Climber moves upward toward chest
        self.play(climber.animate.shift(UP * 2 + RIGHT * 0.5), run_time=1.2); t += 1.2

        # Chest shakes — empty
        for _ in range(3):
            self.play(chest.animate.shift(RIGHT * 0.1), run_time=0.06); t += 0.06
            self.play(chest.animate.shift(LEFT * 0.2), run_time=0.06); t += 0.06
            self.play(chest.animate.shift(RIGHT * 0.1), run_time=0.06); t += 0.06

        # Chest fades to grey — empty
        self.play(chest.animate.set_opacity(0.3),
                  meaning_lbl.animate.set_color(MUTED), run_time=0.5)        # t=4.2

        # Philosophy labels at bottom — each tried to crack the chest
        philosophies = VGroup()
        names = ["NIHILISM", "EXISTENTIALISM", "RELIGION"]
        colors = [DEEP_RED, DEFIANCE_BLUE, WARM_AMBER]
        for i, (name, col) in enumerate(zip(names, colors)):
            lbl = safe_text(name, font="Inter", font_size=24, color=col, weight="BOLD")
            lbl.move_to(LEFT * 3 + RIGHT * i * 3 + UP * ZONE_LOWER)
            philosophies.add(lbl)

        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in philosophies],
                              lag_ratio=0.15), run_time=0.8)                  # t=5.0

        # X marks over each — all wrong frame
        x_marks = VGroup()
        for p in philosophies:
            x = safe_text("X", font="Bebas Neue", font_size=40, color=DEEP_RED)
            x.move_to(p.get_center() + UP * 0.5)
            x_marks.add(x)

        self.play(LaggedStart(*[FadeIn(x, scale=1.3) for x in x_marks],
                              lag_ratio=0.1), run_time=0.5)                   # t=5.5

        # Source label at footer
        src = safe_text("CAMUS, 1942", font="Inter", font_size=20, color=MUTED)
        src.move_to(UP * ZONE_FOOTER)
        self.play(FadeIn(src, shift=UP * 0.04), run_time=0.3); t += 0.3

        target = getattr(self.__class__, 'DURATION', 1.7)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE CONTRADICTION (21.0–28.0s)
# Chest opens → mirror inside → posture shift from strain to dance
# ================================================================
class Scene4_Contradiction(Scene):
    DURATION = 21.8
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("THE MIRROR", color=MIRROR_CYAN)
        pill.move_to(UP * ZONE_TITLE)
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # Chest (will open)
        chest = treasure_chest(width=2.5, height=1.8, color=CHEST_GOLD)
        chest.move_to(UP * ZONE_UPPER)
        self.play(FadeIn(chest, scale=0.95), run_time=0.4); t += 0.4

        # Mirror — oval, cyan glow
        mirror_frame = Ellipse(width=2.0, height=2.8, stroke_color=MIRROR_CYAN,
                               stroke_width=3, fill_color=MIRROR_CYAN, fill_opacity=0.1)
        mirror_frame.move_to(UP * ZONE_MID)

        # Figure reflection inside mirror
        reflection = figure_push(height=1.5, color=MIRROR_CYAN, lean=False)
        reflection.move_to(mirror_frame.get_center())
        reflection.set_opacity(0.6)

        mirror_group = VGroup(mirror_frame, reflection)

        # Chest dissolves, mirror appears
        self.wait(0.8); t += 0.8
        self.play(FadeOut(chest), GrowFromCenter(mirror_group), run_time=0.8); t += 0.8

        self.play(Flash(mirror_frame.get_center(), color=MIRROR_CYAN,
                        line_length=0.5, num_lines=10, run_time=0.3))        # t=2.6

        # Glow ring pulses around mirror
        glow_ring = Circle(radius=1.8, stroke_color=MIRROR_CYAN, stroke_width=1.5,
                           fill_opacity=0).set_opacity(0.3)
        glow_ring.move_to(mirror_frame.get_center())
        self.play(GrowFromCenter(glow_ring), run_time=0.4); t += 0.4

        # Below mirror: two postures side by side
        # Left: straining figure (burden)
        strain_fig = figure_push(height=1.8, color=DEEP_RED, lean=True)
        strain_fig.move_to(LEFT * 2.5 + UP * ZONE_LOWER)
        strain_lbl = safe_text("BURDEN", font="Inter", font_size=22,
                               color=DEEP_RED, weight="BOLD")
        strain_lbl.move_to(strain_fig.get_bottom() + DOWN * 0.4)

        # Right: upright figure (dance)
        dance_fig = figure_push(height=1.8, color=ALIVE_GREEN, lean=False)
        dance_fig.move_to(RIGHT * 2.5 + UP * ZONE_LOWER)
        dance_lbl = safe_text("DANCE", font="Inter", font_size=22,
                              color=ALIVE_GREEN, weight="BOLD")
        dance_lbl.move_to(dance_fig.get_bottom() + DOWN * 0.4)

        # Arrow between them
        arrow = Arrow(LEFT * 0.8, RIGHT * 0.8, color=GOLD, stroke_width=2.5)
        arrow.move_to(UP * ZONE_LOWER)

        self.play(FadeIn(strain_fig), FadeIn(strain_lbl), run_time=0.4); t += 0.4
        self.wait(0.6); t += 0.6
        self.play(GrowArrow(arrow), run_time=0.4); t += 0.4
        self.play(FadeIn(dance_fig), FadeIn(dance_lbl), run_time=0.4); t += 0.4

        # Boulder icon between footer labels — the thing that stays the same
        small_rock = boulder_round(radius=0.4, color=STONE_GREY)
        small_rock.move_to(UP * ZONE_FOOTER)
        self.play(FadeIn(small_rock, scale=0.8), run_time=0.3); t += 0.3

        # Gentle pulse on mirror glow
        self.play(glow_ring.animate.scale(1.15).set_opacity(0.1), run_time=0.9); t += 0.9

        target = getattr(self.__class__, 'DURATION', 21.8)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE PROOF (28.0–35.0s)
# Figure picks up boulder again — alive meter fills
# ================================================================
class Scene5_Proof(Scene):
    DURATION = 5.1
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("DEFIANCE", color=DEFIANCE_BLUE)
        pill.move_to(UP * ZONE_TITLE)
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # Figure with boulder — now upright, walking
        fig = figure_push(height=2.5, color=WHITE_SOFT, lean=False)
        fig.move_to(LEFT * 2 + UP * (ZONE_MID + 0.5))

        rock = boulder_round(radius=1.0, color=STONE_GREY)
        rock.move_to(fig.get_top() + LEFT * 0.8 + UP * 0.5)

        # Smile on figure
        smile = Arc(radius=0.3, angle=-PI * 0.6, color=WARM_AMBER,
                    stroke_width=3)
        smile.move_to(fig[0].get_center() + DOWN * 0.06)

        self.play(FadeIn(fig), FadeIn(rock), FadeIn(smile), run_time=0.5); t += 0.5

        # Vertical alive meter on right — builds from empty to full
        meter_bg = RoundedRectangle(width=1.0, height=6.0, corner_radius=0.15,
                                     fill_color="#1A1A2A", fill_opacity=0.8,
                                     stroke_color=MUTED, stroke_width=1.5)
        meter_bg.move_to(RIGHT * 3 + UP * (ZONE_MID - 0.5))

        meter_lbl = safe_text("ALIVE", font="Bebas Neue", font_size=50,
                              color=DEFIANCE_BLUE)
        meter_lbl.move_to(meter_bg.get_top() + UP * 0.5)

        self.play(FadeIn(meter_bg), FadeIn(meter_lbl), run_time=0.4); t += 0.4

        # Fill the meter in stages with growing rectangles
        fill_stages = [0.25, 0.5, 0.75, 1.0]
        fill_colors = [DEFIANCE_BLUE, DEFIANCE_BLUE, ALIVE_GREEN, ALIVE_GREEN]
        prev_fill = None
        for frac, col in zip(fill_stages, fill_colors):
            fill_h = max(0.05, 6.0 * 0.9 * frac)
            new_fill = Rectangle(width=0.7, height=fill_h, fill_color=col,
                                 fill_opacity=0.8, stroke_width=0)
            new_fill.align_to(meter_bg, DOWN).shift(UP * 6.0 * 0.04)
            if prev_fill:
                self.play(FadeOut(prev_fill), FadeIn(new_fill), run_time=0.4); t += 0.4
            else:
                self.play(FadeIn(new_fill), run_time=0.4); t += 0.4
            prev_fill = new_fill

        # t~2.8
        self.play(Flash(meter_lbl.get_center(), color=ALIVE_GREEN,
                        line_length=0.3, num_lines=8, run_time=0.3))         # t~3.1

        # Figure steps forward with boulder — showing motion
        self.play(fig.animate.shift(RIGHT * 0.4),
                  rock.animate.shift(RIGHT * 0.4),
                  smile.animate.shift(RIGHT * 0.4),
                  run_time=0.8)                                               # t~3.9

        # Philosophy labels below — each approach
        labels_data = [
            ("BELIEF", WARM_AMBER),
            ("NIHILISM", DEEP_RED),
            ("ABSURDISM", ALIVE_GREEN),
        ]
        label_group = VGroup()
        for i, (name, col) in enumerate(labels_data):
            n = safe_text(name, font="Inter", font_size=24, color=col, weight="BOLD")
            n.move_to(LEFT * 3 + RIGHT * i * 3 + UP * ZONE_LOWER)
            label_group.add(n)

        self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.1) for l in label_group],
                              lag_ratio=0.2), run_time=0.8)                   # t~4.7

        # Highlight absurdism — the one that sticks
        highlight = RoundedRectangle(width=label_group[2].width + 0.4,
                                      height=label_group[2].height + 0.25,
                                      corner_radius=0.1, stroke_color=ALIVE_GREEN,
                                      stroke_width=2, fill_opacity=0)
        highlight.move_to(label_group[2])
        self.play(Create(highlight), run_time=0.4); t += 0.4

        # Tiny boulder icon at footer as motif
        tiny_rock = boulder_round(radius=0.3, color=STONE_GREY)
        tiny_rock.move_to(UP * ZONE_FOOTER)
        self.play(FadeIn(tiny_rock, scale=0.8), run_time=0.3); t += 0.3

        target = getattr(self.__class__, 'DURATION', 5.1)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE PUNCH (35.0–45.0s)
# Hill is circular — boulder rolls back — figure walks after it
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 5.7
    def construct(self):
        self.add(gradient_bg("#0A0E18"))
        t = 0

        # Letterbox
        bh = 0.8
        self.add(
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(UP*(8-bh/2)),
            Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                      stroke_width=0).move_to(DOWN*(8-bh/2)),
        )
        self.add(grid_lines(0.02))

        # Circular hill — a large ring showing the path is eternal
        circle_path = Circle(radius=3.5, stroke_color=HILL_BROWN, stroke_width=3,
                             fill_opacity=0).set_opacity(0.5)
        circle_path.move_to(UP * ZONE_MID)

        # Figure walking — upright, calm
        fig = figure_push(height=1.8, color=WHITE_SOFT, lean=False)
        fig.move_to(circle_path.get_bottom() + DOWN * 0.3)

        # Boulder at bottom of circle
        rock = boulder_round(radius=0.8, color=STONE_GREY)
        rock.move_to(circle_path.get_bottom() + LEFT * 1.5 + DOWN * 0.5)

        # Smile
        smile = Arc(radius=0.2, angle=-PI * 0.6, color=WARM_AMBER,
                    stroke_width=3)
        smile.move_to(fig[0].get_center() + DOWN * 0.04)

        self.play(Create(circle_path), run_time=1.0); t += 1.0
        self.play(FadeIn(fig), FadeIn(smile), run_time=0.4); t += 0.4
        self.play(FadeIn(rock, shift=DOWN * 0.3), run_time=0.4); t += 0.4

        # Boulder rolls down the circle
        self.play(rock.animate.shift(LEFT * 1 + DOWN * 0.5),
                  run_time=1.0)                                               # t=2.8

        # Figure walks after it — not defeated
        self.play(fig.animate.shift(LEFT * 1 + DOWN * 0.3),
                  smile.animate.shift(LEFT * 1 + DOWN * 0.3),
                  run_time=1.0)                                               # t=3.8

        # Ambient glow dots — life particles drifting up
        particles = VGroup()
        for _ in range(12):
            p = Dot(radius=0.04, color=WARM_AMBER).set_opacity(0.3)
            x = np.random.uniform(-3.5, 3.5)
            y = np.random.uniform(ZONE_LOWER, ZONE_UPPER)
            p.move_to(np.array([x, y, 0]))
            particles.add(p)
        self.play(LaggedStart(*[FadeIn(p) for p in particles],
                              lag_ratio=0.03), run_time=0.5)                  # t=4.3

        # Particles drift upward slowly
        self.play(*[p.animate.shift(UP * np.random.uniform(0.5, 1.5)).set_opacity(0)
                    for p in particles], run_time=1.5)                        # t=5.8

        # Title card — "SIMPLY DOING" at upper zone
        doing = safe_text("SIMPLY DOING", font="Bebas Neue", font_size=80,
                          color=WARM_AMBER)
        doing.move_to(UP * ZONE_UPPER + UP * 1)
        self.play(FadeIn(doing, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(doing.get_center(), color=WARM_AMBER,
                        line_length=0.4, num_lines=10, run_time=0.3))        # t=6.6

        # Hold — stillness
        target = getattr(self.__class__, 'DURATION', 5.7)
        self.wait(max(0.1, target - t - 0.8))

        black = Rectangle(width=12, height=20, fill_color=BLACK,
                          fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5


# ── Infra ─────────────────────────────────────────────────────
SCENES = [Scene1_Hook, Scene2_Journey, Scene3_WrongAnswer,
          Scene4_Contradiction, Scene5_Proof, Scene6_Punch]

def render_single_scene(idx):
    config.output_file = f"sisyphus_smiled_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    SCENES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"sisyphus_smiled_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENES):
        n = f"sisyphus_smiled_scene_{i+1}"; print(f"  Preview {n}...")
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
        from render_utils import run_preview_qa
        run_preview_qa(od / "previews")
        sys.exit(0)
    if "--scene" in sys.argv:
        timings_json = os.environ.get("TKK_SCENE_TIMINGS")
        if timings_json:
            _idx = int(sys.argv[sys.argv.index("--scene")+1])
            SCENES[_idx].DURATION = json.loads(timings_json)[_idx]
        render_single_scene(int(sys.argv[sys.argv.index("--scene")+1])); sys.exit(0)

    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_sisyphus_smiled.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="sisyphus_smiled", audio_path=str(audio))
    final = od / "sisyphus_smiled_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")

    from render_utils import run_post_render_qa
    run_post_render_qa(str(final), scene_count=6)
