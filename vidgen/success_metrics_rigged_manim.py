#!/usr/bin/env python3
"""Success Metrics Rigged — Visual-first per PRODUCTION_GUIDE.md.

6 scenes, ~40s (37s audio + 3s hold).
Domain shapes: game_piece, measuring_ruler, river_channel, stacked_boards.
Visual throughline: the game board / ruler appears across scenes, revealing hidden bias.

VTT cues (absolute → relative):
  Scene 1 (0.0–5.5s = 5.50s):
    0.30 (0.30) If success metrics are collective,
    1.80 (1.80) who shapes the collective?
    3.50 (3.50) Not everyone equally.
  Scene 2 (5.5–13.0s = 7.50s):
    5.60 (0.10) Wealth measures success,
    7.20 (1.70) and wealth accrues to those
    8.80 (3.30) whose families already had it.
    10.50 (5.00) Educational prestige marks achievement,
  Scene 3 (13.0–19.0s = 6.00s):
    13.10 (0.10) and prestige flows through channels
    14.80 (1.80) carved along class lines
    16.50 (3.50) generations ago.
  Scene 4 (19.0–25.0s = 6.00s):
    19.10 (0.10) The professions that count
    20.80 (1.80) were defined by the people
    22.20 (3.20) already occupying them.
    23.50 (4.50) This isn't conspiracy.
  Scene 5 (25.0–31.0s = 6.00s):
    25.10 (0.10) It's something more mundane and more durable.
    27.00 (2.00) Success metrics reproduce
    28.50 (3.50) the conditions of their own creation.
  Scene 6 (31.0–40.0s = 9.00s):
    31.10 (0.10) They are self-perpetuating,
    33.00 (2.00) like rivers carving deeper
    34.50 (3.50) into channels that already exist.
    36.00 (5.00) The game was set up before you sat down.
    + 3s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """If success metrics are collective, who shapes the collective? Wealth measures success, and wealth accrues to families who already had it. Educational prestige flows through channels carved along class lines generations ago. The professions that count were defined by those already in them. Success metrics reproduce the conditions of their creation. Self-perpetuating, like rivers carving deeper into existing channels. The game was set up before you sat down. The rules favor those who wrote them."""

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

# ── Color palette ────────────────────────────────────────────
BG = "#080A10"
GRID = "#1A2030"
SURFACE = "#15192A"
WHITE_SOFT = "#F0F0F0"
GOLD = "#FFD700"
BOARD_TEAL = "#1ABC9C"
PIECE_BRIGHT = "#3498DB"
RULER_AMBER = "#E67E22"
RIVER_BLUE = "#2980B9"
CRACK_RED = "#E74C3C"
MUTED = "#475569"
INHERIT_PURPLE = "#8E44AD"

SAFE_W = 8.0
SAFE_TOP = 7.2
SAFE_BOT = -6.4

ZONE_TITLE  = 6.2
ZONE_UPPER  = 3.5
ZONE_MID    = 0.0
ZONE_LOWER  = -3.5
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


# ── Domain shapes (4 required) ───────────────────────────────

def game_piece(height=1.0, color=PIECE_BRIGHT):
    """Chess-like game piece — circular head on tapered body."""
    head = Circle(radius=height*0.18, fill_color=color, fill_opacity=0.9, stroke_width=0)
    head.move_to(UP * height * 0.3)
    neck = Rectangle(width=height*0.08, height=height*0.15,
                     fill_color=color, fill_opacity=0.8, stroke_width=0)
    neck.move_to(UP * height * 0.15)
    body = Polygon(
        np.array([-height*0.22, 0, 0]),
        np.array([height*0.22, 0, 0]),
        np.array([height*0.15, -height*0.3, 0]),
        np.array([-height*0.15, -height*0.3, 0]),
        fill_color=color, fill_opacity=0.7, stroke_width=0,
    )
    base = RoundedRectangle(width=height*0.45, height=height*0.1, corner_radius=0.03,
                            fill_color=color, fill_opacity=0.9, stroke_width=0)
    base.move_to(DOWN * height * 0.35)
    return VGroup(head, neck, body, base).scale_to_fit_height(height)

def measuring_ruler(height=4.0, color=RULER_AMBER, ticks=8):
    """Vertical ruler with tick marks — represents success metrics."""
    bar = Rectangle(width=0.35, height=height,
                    fill_color=color, fill_opacity=0.3,
                    stroke_color=color, stroke_width=1.5)
    marks = VGroup()
    for i in range(ticks + 1):
        y = -height/2 + i * height / ticks
        tick_w = 0.3 if i % 2 == 0 else 0.15
        tick = Line(LEFT*tick_w, RIGHT*tick_w, color=color, stroke_width=1.5)
        tick.move_to(bar.get_center() + UP * y)
        marks.add(tick)
    return VGroup(bar, marks)

def river_channel(width=7.0, height=2.0, color=RIVER_BLUE, depth=3):
    """Winding river carved into terrain — shows self-reinforcing channels."""
    terrain_top = Rectangle(width=width, height=height*0.3,
                            fill_color="#2C3E50", fill_opacity=0.5, stroke_width=0)
    terrain_top.move_to(UP * height * 0.35)
    channel = VGroup()
    points = []
    for i in range(depth + 1):
        x = -width/2 + i * width / depth
        y_off = 0.3 * ((-1)**i)
        points.append(np.array([x, y_off, 0]))
    for i in range(len(points)-1):
        seg = Line(points[i], points[i+1], color=color, stroke_width=3 + i*1.5)
        seg.set_opacity(0.6 + i * 0.1)
        channel.add(seg)
    bank_l = Line(LEFT*width/2 + UP*height*0.15, LEFT*width/2 + DOWN*height*0.15,
                  color=MUTED, stroke_width=1)
    bank_r = Line(RIGHT*width/2 + UP*height*0.15, RIGHT*width/2 + DOWN*height*0.15,
                  color=MUTED, stroke_width=1)
    return VGroup(terrain_top, channel, bank_l, bank_r)

def stacked_boards(count=3, width=5.0, height=0.4, spacing=0.6):
    """Layered game boards — each generation's rules built on the last."""
    boards = VGroup()
    for i in range(count):
        y = -i * spacing
        alpha = 0.9 - i * 0.2
        board = RoundedRectangle(
            width=width - i*0.3, height=height,
            corner_radius=0.08,
            fill_color=BOARD_TEAL if i == 0 else MUTED,
            fill_opacity=alpha,
            stroke_color=BOARD_TEAL if i == 0 else MUTED,
            stroke_width=1.5 if i == 0 else 0.8,
        )
        board.move_to(UP * y)
        grid_marks = VGroup()
        for j in range(5):
            x = -width/2 + 0.5 + j * (width - 1) / 4
            gridline = Line(UP*height*0.4, DOWN*height*0.4,
                           color=WHITE_SOFT, stroke_width=0.3).set_opacity(0.3 - i*0.08)
            gridline.move_to(board.get_center() + RIGHT * (x + i*0.15))
            grid_marks.add(gridline)
        boards.add(VGroup(board, grid_marks))
    return boards


# ================================================================
# SCENE 1: THE HOOK (0.0–5.5s)
# Game board with pieces — some squares glow, rigged from the start
# Zones: TITLE, MID (board), LOWER (new piece arrival), FOOTER
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 3.8
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # TITLE zone — pill
        pill = label_pill("THE GAME WAS RIGGED", color=CRACK_RED)
        pill.move_to(UP * ZONE_TITLE)

        # MID zone — 4x4 game board
        board = VGroup()
        sq_size = 1.1
        for r in range(4):
            for c in range(4):
                x = -1.65 + c * sq_size
                y = 1.5 - r * sq_size
                sq = Square(side_length=sq_size * 0.9,
                           fill_color=SURFACE, fill_opacity=0.6,
                           stroke_color=BOARD_TEAL, stroke_width=0.8)
                sq.move_to(np.array([x, y, 0]))
                board.add(sq)
        board.move_to(UP * (ZONE_MID + 0.5))

        # Gold "winning" pieces already placed
        winners = VGroup()
        win_positions = [3, 6, 9]
        for idx in win_positions:
            p = game_piece(height=0.7, color=GOLD)
            p.move_to(board[idx].get_center())
            winners.add(p)

        # LOWER zone — new piece enters from below
        new_piece = game_piece(height=0.8, color=PIECE_BRIGHT)
        new_piece.move_to(UP * ZONE_LOWER)

        # Bias indicators
        boost_indices = [3, 6, 9, 5]
        drag_indices = [0, 12, 13, 8]

        # FOOTER zone
        footer = safe_text("Who shapes the collective?", font="Inter",
                          font_size=24, color=MUTED)
        footer.move_to(UP * ZONE_FOOTER)

        # --- Animations ---
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(board, scale=0.95), run_time=0.5); t += 0.5
        self.play(LaggedStart(*[FadeIn(w, scale=1.3) for w in winners],
                              lag_ratio=0.1), run_time=0.5)             # t=1.4

        # New piece rises from bottom into board area
        self.play(FadeIn(new_piece, shift=UP*0.5), run_time=0.4); t += 0.4
        self.play(new_piece.animate.move_to(board[12].get_center()),
                  run_time=0.5)                                         # t=2.3

        # Squares reveal hidden bias — boost glow teal, drag glow red
        self.wait(0.2); t += 0.2
        boost_anims = [board[i].animate.set_fill(BOARD_TEAL, opacity=0.4) for i in boost_indices]
        drag_anims = [board[i].animate.set_fill(CRACK_RED, opacity=0.3) for i in drag_indices]
        self.play(*boost_anims, *drag_anims, run_time=0.6); t += 0.6

        # New piece shakes on the red square
        for _ in range(2):
            self.play(new_piece.animate.shift(RIGHT*0.1), run_time=0.08); t += 0.08
            self.play(new_piece.animate.shift(LEFT*0.2), run_time=0.08); t += 0.08
            self.play(new_piece.animate.shift(RIGHT*0.1), run_time=0.08); t += 0.08

        self.play(FadeIn(footer, shift=UP*0.2), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 3.8)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE WRONG ANSWER (5.5–13.0s)
# Balance scale tilts under hidden weight; rulers measure the wrong things
# Zones: TITLE, UPPER (merit label), MID (scale), LOWER (metric rulers), FOOTER
# ================================================================
class Scene2_WrongAnswer(Scene):
    DURATION = 1.9
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # TITLE zone
        pill = label_pill("MERITOCRACY", color=GOLD)
        pill.move_to(UP * ZONE_TITLE)

        # UPPER zone — MERIT label
        merit = safe_text("MERIT", font="Bebas Neue", font_size=52, color=GOLD)
        merit.move_to(UP * ZONE_UPPER)

        # MID zone — balance scale
        fulcrum = Polygon(
            np.array([0, -0.3, 0]), np.array([-0.4, -0.9, 0]),
            np.array([0.4, -0.9, 0]),
            fill_color=MUTED, fill_opacity=0.7, stroke_width=0,
        )
        fulcrum.move_to(UP * (ZONE_MID + 0.3))
        beam = Line(LEFT*2.5, RIGHT*2.5, color=WHITE_SOFT, stroke_width=3)
        beam.move_to(fulcrum.get_top() + UP*0.05)
        pan_l = Arc(radius=0.8, start_angle=PI, angle=PI,
                    color=WHITE_SOFT, stroke_width=2)
        pan_l.move_to(beam.get_left() + DOWN*0.5)
        pan_r = Arc(radius=0.8, start_angle=PI, angle=PI,
                    color=WHITE_SOFT, stroke_width=2)
        pan_r.move_to(beam.get_right() + DOWN*0.5)
        scale = VGroup(fulcrum, beam, pan_l, pan_r)

        effort_label = safe_text("EFFORT", font="Inter", font_size=24, color=WHITE_SOFT)
        effort_label.move_to(pan_l.get_center() + UP*0.2)
        reward_label = safe_text("REWARD", font="Inter", font_size=24, color=GOLD)
        reward_label.move_to(pan_r.get_center() + UP*0.2)

        # LOWER zone — three vertical rulers with metric labels
        ruler_group = VGroup()
        metric_data = [("WEALTH", -2.8, GOLD), ("GPA", 0, BOARD_TEAL), ("TITLE", 2.8, RULER_AMBER)]
        for txt, x, color in metric_data:
            r = measuring_ruler(height=2.5, color=color, ticks=6)
            r.move_to(np.array([x, ZONE_LOWER, 0]))
            lbl = safe_text(txt, font="Inter", font_size=20, color=color, weight="BOLD")
            lbl.move_to(np.array([x, ZONE_LOWER - 1.8, 0]))
            ruler_group.add(VGroup(r, lbl))

        # FOOTER zone
        footer = safe_text("Wealth accrues to those who had it", font="Inter",
                          font_size=22, color=MUTED)
        footer.move_to(UP * ZONE_FOOTER)

        # --- Animations ---
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(merit, scale=1.1), run_time=0.4); t += 0.4
        self.play(FadeIn(scale, scale=0.9), run_time=0.5); t += 0.5
        self.play(FadeIn(effort_label), FadeIn(reward_label), run_time=0.4); t += 0.4

        self.wait(0.6); t += 0.6

        # Rulers grow from bottom
        self.play(LaggedStart(*[GrowFromCenter(rg) for rg in ruler_group],
                              lag_ratio=0.15), run_time=0.8)            # t=3.1

        # Scale starts tilting — hidden weight on reward side
        self.wait(0.4); t += 0.4
        hidden_weight = Circle(radius=0.3, fill_color=INHERIT_PURPLE,
                              fill_opacity=0.6, stroke_width=0)
        hidden_weight.move_to(pan_r.get_center() + DOWN*0.1)
        self.play(FadeIn(hidden_weight, scale=0.5), run_time=0.3); t += 0.3
        self.play(
            beam.animate.rotate(-10 * DEGREES, about_point=fulcrum.get_top()),
            pan_l.animate.shift(UP*0.3),
            effort_label.animate.shift(UP*0.3),
            pan_r.animate.shift(DOWN*0.3),
            reward_label.animate.shift(DOWN*0.3),
            hidden_weight.animate.shift(DOWN*0.3),
            run_time=0.6,
        )                                                                # t=4.4

        self.play(FadeIn(footer, shift=UP*0.2), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 1.9)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: THE CONTRADICTION (13.0–19.0s)
# MERIT cracks to reveal INHERITANCE; river channel below
# Zones: TITLE, UPPER (merit/inherit), MID (tilted scale), LOWER (river), FOOTER
# ================================================================
class Scene3_Contradiction(Scene):
    DURATION = 16.9
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # TITLE zone
        pill = label_pill("THE HIDDEN WEIGHT", color=CRACK_RED)
        pill.move_to(UP * ZONE_TITLE)

        # UPPER zone — MERIT label that cracks
        merit = safe_text("MERIT", font="Bebas Neue", font_size=64, color=GOLD)
        merit.move_to(UP * ZONE_UPPER)

        # INHERITANCE label hidden underneath
        inherit = safe_text("INHERITANCE", font="Bebas Neue", font_size=52, color=INHERIT_PURPLE)
        inherit.move_to(UP * ZONE_UPPER)
        inherit.set_opacity(0)

        # MID zone — tilted scale (already broken)
        fulcrum = Polygon(
            np.array([0, -0.3, 0]), np.array([-0.4, -0.9, 0]),
            np.array([0.4, -0.9, 0]),
            fill_color=MUTED, fill_opacity=0.7, stroke_width=0,
        )
        fulcrum.move_to(UP * (ZONE_MID + 0.5))
        beam = Line(LEFT*2.5, RIGHT*2.5, color=WHITE_SOFT, stroke_width=3)
        beam.move_to(fulcrum.get_top() + UP*0.05)
        scale = VGroup(fulcrum, beam)

        # Crack lines radiating from MERIT
        cracks = VGroup()
        crack_angles = [0.3, 0.9, 1.6, 2.2, 2.8, 3.4, 4.0, 4.8, 5.5]
        for angle in crack_angles:
            length = 0.5 + np.random.random() * 0.6
            end_pt = np.array([np.cos(angle) * length, np.sin(angle) * length, 0])
            crack = Line(ORIGIN, end_pt, color=CRACK_RED, stroke_width=1.5)
            crack.move_to(merit.get_center())
            crack.shift(end_pt * 0.5)
            cracks.add(crack)

        # LOWER zone — river channel
        river = river_channel(width=7.0, height=1.8, color=RIVER_BLUE)
        river.move_to(UP * ZONE_LOWER)

        # Class line arrows flowing into river
        class_arrows = VGroup()
        for x_off in [-2.5, -0.8, 0.8, 2.5]:
            arr = Arrow(
                np.array([x_off, ZONE_MID - 1.0, 0]),
                np.array([x_off * 0.6, ZONE_LOWER + 1.0, 0]),
                color=RIVER_BLUE, stroke_width=1.5, buff=0.1,
                max_tip_length_to_length_ratio=0.15,
            )
            arr.set_opacity(0.4)
            class_arrows.add(arr)

        # FOOTER zone
        caption = safe_text("Channels carved generations ago", font="Inter",
                           font_size=22, color=MUTED)
        caption.move_to(UP * ZONE_FOOTER)

        # --- Animations ---
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(scale), FadeIn(merit), run_time=0.5); t += 0.5

        # Scale tilts
        self.wait(0.4); t += 0.4
        self.play(beam.animate.rotate(-15 * DEGREES, about_point=fulcrum.get_top()),
                  run_time=0.5)                                          # t=1.8

        # MERIT cracks and shatters
        self.play(LaggedStart(*[Create(c) for c in cracks], lag_ratio=0.03),
                  run_time=0.3)                                          # t=2.1
        self.play(merit.animate.set_opacity(0.15).set_color(CRACK_RED),
                  run_time=0.3)                                          # t=2.4

        # INHERITANCE revealed with flash
        self.play(inherit.animate.set_opacity(1), run_time=0.4); t += 0.4
        self.play(Flash(inherit.get_center(), color=INHERIT_PURPLE,
                       flash_radius=1.2, line_length=0.25), run_time=0.2)  # t=3.0

        # River and class arrows flow in
        self.play(LaggedStart(*[GrowArrow(a) for a in class_arrows],
                              lag_ratio=0.08), run_time=0.5)            # t=3.5
        self.play(FadeIn(river, shift=UP*0.3), run_time=0.5); t += 0.5
        self.play(FadeIn(caption, shift=UP*0.2), run_time=0.3); t += 0.3

        target = getattr(self.__class__, 'DURATION', 16.9)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE PROOF (19.0–25.0s)
# Three bars with feedback loop arrows — self-perpetuating metrics
# Zones: TITLE, MID (bar tops), LOWER (bar bodies), FOOTER
# ================================================================
class Scene4_Proof(Scene):
    DURATION = 4.4
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # TITLE zone
        pill = label_pill("SELF-PERPETUATING", color=INHERIT_PURPLE)
        pill.move_to(UP * ZONE_TITLE)

        # Bars spanning MID to LOWER zones (grow from y_base=-5.5 upward)
        bar_data = [
            ("WEALTH", GOLD, -2.8),
            ("PRESTIGE", BOARD_TEAL, 0.0),
            ("PROFESSION", RULER_AMBER, 2.8),
        ]
        bars = VGroup()
        labels = VGroup()
        arrows = VGroup()
        y_base = -5.5

        for txt, color, x in bar_data:
            bar_h = 6.5
            bar = Rectangle(width=1.6, height=bar_h,
                           fill_color=color, fill_opacity=0.5,
                           stroke_color=color, stroke_width=1.5)
            bar.move_to(np.array([x, y_base + bar_h/2, 0]))
            bars.add(bar)

            lbl = safe_text(txt, font="Inter", font_size=22, color=color, weight="BOLD")
            lbl.move_to(np.array([x, y_base - 0.4, 0]))
            labels.add(lbl)

            # Feedback loop arrow — curves from top back to base
            arrow = Arrow(
                bar.get_top() + RIGHT*0.3,
                bar.get_bottom() + RIGHT*0.6,
                color=color, stroke_width=2,
                buff=0.1,
                max_tip_length_to_length_ratio=0.1,
            )
            arrows.add(arrow)

        # Connecting arrows between bars at UPPER zone — showing interconnection
        cross_arrows = VGroup()
        positions = [-2.8, 0.0, 2.8]
        for i in range(len(positions) - 1):
            arr = Arrow(
                np.array([positions[i] + 0.9, ZONE_UPPER, 0]),
                np.array([positions[i+1] - 0.9, ZONE_UPPER, 0]),
                color=WHITE_SOFT, stroke_width=1.5, buff=0.05,
                max_tip_length_to_length_ratio=0.15,
            )
            arr.set_opacity(0.5)
            cross_arrows.add(arr)

        # FOOTER zone
        footer = safe_text("Not conspiracy. Architecture.", font="Inter",
                          font_size=24, color=MUTED)
        footer.move_to(UP * ZONE_FOOTER)

        # --- Animations ---
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4

        # Bars grow up from base
        for bar in bars:
            bar.save_state()
            bar.stretch(0.01, 1, about_edge=DOWN)
        self.play(LaggedStart(*[bar.animate.restore() for bar in bars],
                              lag_ratio=0.15), run_time=0.8)            # t=1.2

        self.play(LaggedStart(*[FadeIn(l, shift=UP*0.2) for l in labels],
                              lag_ratio=0.1), run_time=0.5)             # t=1.7

        # Cross-connecting arrows
        self.play(LaggedStart(*[GrowArrow(a) for a in cross_arrows],
                              lag_ratio=0.2), run_time=0.4)             # t=2.1

        # Feedback arrows appear
        self.wait(0.4); t += 0.4
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows],
                              lag_ratio=0.15), run_time=0.8)            # t=3.3

        # Bars pulse brighter to show self-reinforcement
        self.play(
            *[bar.animate.set_fill(opacity=0.75) for bar in bars],
            run_time=0.4,
        )                                                                # t=3.7
        self.play(
            *[bar.animate.set_fill(opacity=0.5) for bar in bars],
            run_time=0.3,
        )                                                                # t=4.0

        self.play(FadeIn(footer, shift=UP*0.2), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 4.4)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE MECHANISM (25.0–31.0s)
# River carving deeper — self-reinforcing channels across generations
# Zones: TITLE, UPPER/MID/LOWER (three generation channels), FOOTER
# ================================================================
class Scene5_Mechanism(Scene):
    DURATION = 11.1
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # TITLE zone
        pill = label_pill("THE RIVER EFFECT", color=RIVER_BLUE)
        pill.move_to(UP * ZONE_TITLE)

        # Three generations of channels spanning UPPER → LOWER
        channels = VGroup()
        gen_labels = ["GEN 1", "GEN 2", "GEN 3"]
        gen_widths = [1.5, 2.5, 4.0]
        gen_strokes = [2, 4, 7]
        gen_y_centers = [ZONE_UPPER, ZONE_MID, ZONE_LOWER]

        for i, (label, w, sw, y_center) in enumerate(zip(gen_labels, gen_widths, gen_strokes, gen_y_centers)):
            # Channel line — gets wider and deeper each generation
            pts = []
            segs = 8
            for j in range(segs + 1):
                x = -3.5 + j * 7.0 / segs
                y_off = 0.3 * np.sin(j * 1.2 + i * 0.5)
                pts.append(np.array([x, y_center + y_off, 0]))
            ch = VGroup()
            for j in range(len(pts)-1):
                seg = Line(pts[j], pts[j+1], color=RIVER_BLUE, stroke_width=sw)
                seg.set_opacity(0.5 + i * 0.15)
                ch.add(seg)

            # Banks (terrain on either side)
            bank_top = Line(pts[0] + UP*0.5, pts[-1] + UP*0.5,
                           color=MUTED, stroke_width=0.8).set_opacity(0.3)
            bank_bot = Line(pts[0] + DOWN*0.5, pts[-1] + DOWN*0.5,
                           color=MUTED, stroke_width=0.8).set_opacity(0.3)

            # Generation label
            gen_lbl = safe_text(label, font="Inter", font_size=20, color=MUTED)
            gen_lbl.move_to(np.array([3.8, y_center, 0]))

            channels.add(VGroup(ch, bank_top, bank_bot, gen_lbl))

        # Depth indicator — vertical arrow showing "deeper"
        depth_arrow = Arrow(
            np.array([-4.2, ZONE_UPPER, 0]),
            np.array([-4.2, ZONE_LOWER, 0]),
            color=RIVER_BLUE, stroke_width=2, buff=0,
        )
        depth_label = safe_text("DEEPER", font="Inter", font_size=20, color=RIVER_BLUE)
        depth_label.next_to(depth_arrow, LEFT, buff=0.15).rotate(90*DEGREES)

        # Particle dots drifting along channels (ambient motion)
        particles = VGroup()
        for _ in range(6):
            dot = Dot(radius=0.05, color=RIVER_BLUE, fill_opacity=0.6)
            x_start = -3.5 + np.random.random() * 7
            y_pick = gen_y_centers[np.random.randint(0, 3)]
            dot.move_to(np.array([x_start, y_pick, 0]))
            particles.add(dot)

        # FOOTER zone
        footer = safe_text("More durable than conspiracy", font="Inter",
                          font_size=22, color=MUTED)
        footer.move_to(UP * ZONE_FOOTER)

        # --- Animations ---
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4

        # Channels appear one by one — each generation deeper
        for i, ch_group in enumerate(channels):
            self.play(LaggedStart(*[Create(seg) for seg in ch_group[0]],
                                  lag_ratio=0.05),
                      FadeIn(ch_group[1]), FadeIn(ch_group[2]),
                      FadeIn(ch_group[3]),
                      run_time=0.6)                                      # t=1.0, 1.6, 2.2
            self.wait(0.2); t += 0.2

        # Depth arrow
        self.play(GrowArrow(depth_arrow), FadeIn(depth_label),
                  run_time=0.4)                                          # t=2.8

        # Particles drift right (ambient motion)
        self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in particles],
                              lag_ratio=0.05), run_time=0.3)            # t=3.1
        self.play(*[p.animate.shift(RIGHT * (1.0 + np.random.random())) for p in particles],
                  run_time=0.8)                                          # t=3.9

        self.play(FadeIn(footer, shift=UP*0.2), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 11.1)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE PUNCH (31.0–40.0s)
# Stacked boards — layers of inherited rules, asterisk reveal
# Zones: TITLE, UPPER (game board + piece), MID (YOU CAN WIN*), LOWER (layers), FOOTER
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 2.8
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # TITLE zone
        pill = label_pill("THE ARCHITECTURE", color=WHITE_SOFT)
        pill.move_to(UP * ZONE_TITLE)

        # UPPER zone — game board from Scene 1, now ghostly
        board_top = VGroup()
        sq_size = 0.9
        for r in range(4):
            for c in range(4):
                x = -1.35 + c * sq_size
                y = 1.5 - r * sq_size
                sq = Square(side_length=sq_size * 0.85,
                           fill_color=BOARD_TEAL, fill_opacity=0.15,
                           stroke_color=BOARD_TEAL, stroke_width=0.5)
                sq.move_to(np.array([x, y, 0]))
                board_top.add(sq)
        board_top.move_to(UP * ZONE_UPPER)

        # Game piece on board
        piece = game_piece(height=0.8, color=PIECE_BRIGHT)
        piece.move_to(board_top.get_center())

        # MID zone — "YOU CAN WIN*"
        win_text = safe_text("YOU CAN WIN*", font="Bebas Neue", font_size=64, color=GOLD)
        win_text.move_to(UP * ZONE_MID)

        # LOWER zone — stacked boards (layers of inherited rules)
        layers = stacked_boards(count=4, width=5.0, height=0.35, spacing=0.7)
        layers.move_to(UP * ZONE_LOWER)

        # Layer labels next to each board
        layer_labels = VGroup()
        era_names = ["YOUR GAME", "PARENTS'", "GRANDPARENTS'", "FOUNDERS'"]
        for i, name in enumerate(era_names):
            lbl = safe_text(name, font="Inter", font_size=18, color=MUTED)
            lbl.move_to(layers[i].get_center() + RIGHT * 3.5)
            layer_labels.add(lbl)

        # Connecting lines between board and layers — show inheritance
        connect_lines = VGroup()
        for side in [-1, 1]:
            ln = DashedLine(
                board_top.get_bottom() + RIGHT * side * 1.5,
                layers[0].get_top() + RIGHT * side * 1.2,
                color=MUTED, stroke_width=1, dash_length=0.15,
            )
            ln.set_opacity(0.4)
            connect_lines.add(ln)

        # FOOTER zone — asterisk
        asterisk = safe_text("*within a framework designed by others",
                            font="Inter", font_size=20, color=MUTED)
        asterisk.move_to(UP * ZONE_FOOTER)

        # --- Animations ---
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(board_top, scale=0.95), run_time=0.5); t += 0.5
        self.play(FadeIn(piece, scale=1.3), run_time=0.3); t += 0.3

        # Layers fade in from bottom with stagger
        self.wait(0.3); t += 0.3
        self.play(LaggedStart(*[FadeIn(layer, shift=UP*0.3) for layer in layers],
                              lag_ratio=0.12), run_time=0.7)            # t=2.2
        self.play(LaggedStart(*[FadeIn(l, shift=LEFT*0.3) for l in layer_labels],
                              lag_ratio=0.1), run_time=0.5)             # t=2.7

        # Connection lines show link between current game and history
        self.play(LaggedStart(*[Create(ln) for ln in connect_lines],
                              lag_ratio=0.15), run_time=0.4)            # t=3.1

        # "YOU CAN WIN*" slams in
        self.wait(0.4); t += 0.4
        self.play(FadeIn(win_text, scale=1.15), run_time=0.5); t += 0.5
        self.play(Flash(win_text.get_center(), color=GOLD,
                       flash_radius=1.5, line_length=0.3), run_time=0.3)  # t=4.3

        # Piece slowly drifts down toward layers — pulled by gravity of history
        self.play(piece.animate.shift(DOWN * 1.0).set_opacity(0.5),
                  run_time=0.7)                                          # t=5.0

        # Asterisk
        self.play(FadeIn(asterisk, shift=UP*0.2), run_time=0.4); t += 0.4

        target = getattr(self.__class__, 'DURATION', 2.8)
        self.wait(max(0.1, target - t - 0.8))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ── Render helpers ───────────────────────────────────────────

def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_WrongAnswer, Scene3_Contradiction,
          Scene4_Proof, Scene5_Mechanism, Scene6_Punch]
    config.output_file = f"success_metrics_rigged_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"success_metrics_rigged_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    sc = [Scene1_Hook, Scene2_WrongAnswer, Scene3_Contradiction,
          Scene4_Proof, Scene5_Mechanism, Scene6_Punch]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(sc):
        n = f"success_metrics_rigged_scene_{i+1}"; print(f"  Preview {n}...")
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
            _classes = sorted([v for k,v in globals().items() if k.startswith("Scene") and len(k) > 5 and k[5].isdigit() and isinstance(v, type)], key=lambda c: c.__name__); _classes[_idx].DURATION = json.loads(timings_json)[_idx]
        render_single_scene(int(sys.argv[sys.argv.index("--scene")+1])); sys.exit(0)

    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_success_metrics_rigged.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="success_metrics_rigged", audio_path=str(audio))
    final = od / "success_metrics_rigged_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")

    from render_utils import run_post_render_qa
    run_post_render_qa(str(final), scene_count=6)

    from render_utils import make_short
    scene_ends = [5.5, 13.0, 19.0, 25.0, 31.0, 40.0]
    short, dur = make_short(str(final), scene_ends)
    print(f"  SHORT: {short} ({Path(short).stat().st_size/1024/1024:.1f} MB, {dur:.1f}s)")
