#!/usr/bin/env python3
"""Child Already Knew — Visual-first per PRODUCTION_GUIDE.md.

6 scenes, ~40s total.
Domain shapes: block_tower, spiral_step, bookshelf, child_figure.
Visual throughline: the block_tower appears in EVERY scene.

VTT cues (absolute -> relative):
  Scene 1 (0.0-6.5s):   0.0 We come back... 3.0 child beneath layers...
  Scene 2 (6.5-13.5s):  6.5 The philosophical journey... 10.0 seven levels...
  Scene 3 (13.5-19.5s): 13.5 The assumption... 16.0 bookshelf grows...
  Scene 4 (19.5-26.5s): 19.5 The bookshelf topples... 22.0 tower is the point...
  Scene 5 (26.5-33.5s): 26.5 The child's tower... 29.0 building equals point...
  Scene 6 (33.5-40.0s): 33.5 She finishes... 36.0 knocks it down, starts again...
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """We come back to the child. She's still there beneath the layers. She didn't want success. She wanted to see how high the tower could go. The deconstruction, the critique, the reclamation — all the long way around to what she already knew. The tower is the point. Not the height. I may build something that lasts or collapses by Tuesday. But the building was mine, the minutes were mine. No yardstick can measure what it meant to spend them."""

from manim import (
    Scene, Text, Group, VGroup, Rectangle, RoundedRectangle, Circle,
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
WHITE_SOFT = "#F0F0F0"; GOLD = "#FFD700"
CHILD_AMBER = "#F59E0B"; TOWER_BLUE = "#3B82F6"
BOOK_TEAL = "#14B8A6"; PHILO_VIOLET = "#8B5CF6"
MUTED = "#475569"; DIM = "#334155"; DEAD_GRAY = "#4A5568"
SAFE_W = 8.0

ZONE_TITLE = 6.2; ZONE_UPPER = 3.5; ZONE_MID = 0.0
ZONE_LOWER = -3.5; ZONE_FOOTER = -6.0


# -- Core helpers -----------------------------------------------------

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


# -- Domain shapes (4 required) ---------------------------------------

def block_tower(height=2.0, n_blocks=5):
    """Child's block tower -- stacked colorful rectangles, freeform."""
    blocks = VGroup()
    colors = [TOWER_BLUE, CHILD_AMBER, BOOK_TEAL, PHILO_VIOLET, GOLD]
    widths = [0.9, 0.7, 0.8, 0.5, 0.6]
    y = -height * 0.4
    for i in range(min(n_blocks, 5)):
        bh = height * 0.16
        b = Rectangle(width=widths[i], height=bh, fill_color=colors[i],
                      fill_opacity=0.7, stroke_color=WHITE_SOFT, stroke_width=0.8)
        b.move_to(UP * y + RIGHT * ((-1)**i) * 0.04)
        blocks.add(b)
        y += bh + 0.02
    return blocks

def spiral_step(height=6.0, n_steps=7, color=PHILO_VIOLET):
    """Descending spiral staircase -- concentric arcs stepping down."""
    steps = VGroup()
    for i in range(n_steps):
        r = height * 0.08 * (n_steps - i)
        y_off = height * 0.35 - i * (height * 0.1)
        arc = Arc(radius=r, start_angle=(40 + i * 30) * DEGREES,
                  angle=200 * DEGREES, color=color, stroke_width=2.5)
        arc.set_opacity(0.8 - i * 0.08)
        arc.move_to(UP * y_off)
        steps.add(arc)
    return steps

def bookshelf(height=5.0, color=BOOK_TEAL):
    """Tall bookshelf with spines of varying widths."""
    shelf = VGroup()
    frame_l = Line(DOWN * height * 0.5, UP * height * 0.5, color=color,
                   stroke_width=2).shift(LEFT * 1.2)
    frame_r = Line(DOWN * height * 0.5, UP * height * 0.5, color=color,
                   stroke_width=2).shift(RIGHT * 1.2)
    shelf.add(frame_l, frame_r)
    shelf_colors = [BOOK_TEAL, PHILO_VIOLET, TOWER_BLUE, CHILD_AMBER, GOLD]
    for row in range(5):
        sy = -height * 0.4 + row * height * 0.2
        shelf_line = Line(LEFT * 1.2 + UP * sy, RIGHT * 1.2 + UP * sy,
                          color=color, stroke_width=1.5, stroke_opacity=0.6)
        shelf.add(shelf_line)
        x = -1.0
        for b in range(4):
            bw = 0.3 + np.random.RandomState(row * 10 + b).random() * 0.2
            bh = height * 0.17
            book = Rectangle(width=bw, height=bh, fill_color=shelf_colors[(row + b) % 5],
                             fill_opacity=0.4, stroke_color=shelf_colors[(row + b) % 5],
                             stroke_width=1)
            book.move_to(RIGHT * x + UP * (sy + bh * 0.5 + 0.03))
            shelf.add(book)
            x += bw + 0.08
    return shelf

def child_figure(height=2.0, color=CHILD_AMBER):
    """Simple stick-figure child -- circle head + body + limbs."""
    h = height
    head = Circle(radius=h * 0.1, fill_color=color, fill_opacity=0.8, stroke_width=0)
    head.move_to(UP * h * 0.35)
    body = Line(UP * h * 0.25, DOWN * h * 0.1, color=color, stroke_width=2.5)
    arm_l = Line(UP * h * 0.15, LEFT * h * 0.15 + UP * h * 0.05,
                 color=color, stroke_width=2)
    arm_r = Line(UP * h * 0.15, RIGHT * h * 0.15 + UP * h * 0.05,
                 color=color, stroke_width=2)
    leg_l = Line(DOWN * h * 0.1, LEFT * h * 0.1 + DOWN * h * 0.35,
                 color=color, stroke_width=2)
    leg_r = Line(DOWN * h * 0.1, RIGHT * h * 0.1 + DOWN * h * 0.35,
                 color=color, stroke_width=2)
    return VGroup(head, body, arm_l, arm_r, leg_l, leg_r)


# ================================================================
# SCENE 1: THE HOOK (0.0-6.5s)
# Child building blocks, ghostly philosophers above
# Zones: TITLE, UPPER, MID, LOWER, FOOTER
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 6.7
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE
        pill = label_pill("SHE ALREADY KNEW", color=CHILD_AMBER)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_MID -- child + tower
        child = child_figure(height=2.5, color=CHILD_AMBER)
        child.move_to(LEFT * 1.0 + UP * ZONE_MID)
        tower = block_tower(height=2.0, n_blocks=4)
        tower.move_to(RIGHT * 0.8 + UP * ZONE_MID)

        # ZONE_UPPER -- ghostly philosopher silhouettes
        philo_data = [
            (-3.0, ZONE_UPPER + 0.5, "NIETZSCHE"),
            (-1.0, ZONE_UPPER + 1.2, "SARTRE"),
            (1.0, ZONE_UPPER + 0.8, "CAMUS"),
            (3.0, ZONE_UPPER + 1.5, "LAOZI"),
        ]
        philos = VGroup()
        philo_labels = VGroup()
        for x, y, name in philo_data:
            ghost = Circle(radius=0.5, fill_color=PHILO_VIOLET, fill_opacity=0.1,
                           stroke_color=PHILO_VIOLET, stroke_width=1, stroke_opacity=0.3)
            ghost.move_to(RIGHT * x + UP * y)
            philos.add(ghost)
            lb = safe_text(name, font="Inter", font_size=16, color=PHILO_VIOLET)
            lb.set_opacity(0.4)
            lb.next_to(ghost, DOWN, buff=0.1)
            philo_labels.add(lb)

        # ZONE_LOWER -- floor line with scattered old blocks
        floor = Line(LEFT * 4, RIGHT * 4, color=MUTED, stroke_width=1,
                     stroke_opacity=0.3).move_to(UP * ZONE_LOWER + UP * 1.0)
        old_blocks = VGroup()
        for bx, by, rot, col in [(-2.5, -3.0, 20, TOWER_BLUE), (-1, -3.4, -15, GOLD),
                                  (0.5, -2.8, 35, BOOK_TEAL), (2, -3.2, -25, PHILO_VIOLET),
                                  (3.2, -3.6, 10, CHILD_AMBER)]:
            b = Rectangle(width=0.35, height=0.2, fill_color=col, fill_opacity=0.25,
                          stroke_color=col, stroke_width=0.6)
            b.rotate(rot * DEGREES).move_to(RIGHT * bx + UP * by)
            old_blocks.add(b)

        # ZONE_FOOTER
        caption = safe_text("2,500 YEARS OF THOUGHT", font="Inter",
                            font_size=22, color=MUTED)
        caption.move_to(UP * ZONE_FOOTER)

        # -- Animations --
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(child, scale=0.9), FadeIn(floor), run_time=0.5); t += 0.5

        # Tower blocks appear one by one
        for block in tower:
            self.play(FadeIn(block, shift=DOWN * 0.2), run_time=0.2); t += 0.2

        # Old blocks scatter in below
        self.play(
            LaggedStart(*[FadeIn(b, scale=0.5) for b in old_blocks], lag_ratio=0.05),
            run_time=0.4,
        )                                                                 # t=2.1

        # Philosophers fade in above -- ghostly, arguing
        self.play(
            LaggedStart(*[FadeIn(p, scale=0.8) for p in philos], lag_ratio=0.1),
            LaggedStart(*[FadeIn(l, shift=UP*0.1) for l in philo_labels], lag_ratio=0.1),
            run_time=1.0,
        )                                                                 # t=3.1

        # Debate lines between philosophers
        debate_lines = VGroup()
        for i in range(len(philos) - 1):
            dl = DashedLine(philos[i].get_right(), philos[i+1].get_left(),
                            color=PHILO_VIOLET, stroke_width=0.8, dash_length=0.1)
            dl.set_opacity(0.3)
            debate_lines.add(dl)
        self.play(
            LaggedStart(*[Create(dl) for dl in debate_lines], lag_ratio=0.1),
            run_time=0.6,
        )                                                                 # t=3.7

        # Philosophers pulse gently while child stays still
        self.play(
            *[p.animate.scale(1.15).set_opacity(0.15) for p in philos],
            run_time=0.5,
        )                                                                 # t=4.2

        self.play(FadeIn(caption, shift=UP * 0.1), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 6.7)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE MYSTERY (6.5-13.5s)
# Spiral staircase descending through philosophical levels
# Zones: TITLE, UPPER, MID, LOWER, FOOTER
# ================================================================
class Scene2_Mystery(Scene):
    DURATION = 7.3
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE
        pill = label_pill("THE LONG WAY DOWN", color=PHILO_VIOLET)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER + MID -- spiral staircase spanning full height
        spiral = spiral_step(height=8.0, n_steps=7, color=PHILO_VIOLET)
        spiral.move_to(LEFT * 1.5 + UP * ZONE_MID)

        # Level labels on the right side spanning UPPER to LOWER
        level_data = [
            (ZONE_UPPER + 1.5, "GOLD STAR", GOLD),
            (ZONE_UPPER + 0.0, "BROKEN COMPASS", TOWER_BLUE),
            (ZONE_UPPER - 1.5, "RIGGED SCALE", MUTED),
            (ZONE_MID, "NIHILISM", DEAD_GRAY),
            (ZONE_MID - 1.5, "EXISTENTIALISM", PHILO_VIOLET),
            (ZONE_LOWER + 2.0, "TAO", BOOK_TEAL),
            (ZONE_LOWER + 0.5, "ABSURDISM", CHILD_AMBER),
        ]
        level_labels = VGroup()
        level_dots = VGroup()
        for y, txt, col in level_data:
            dot = Dot(radius=0.08, color=col).move_to(RIGHT * 1.0 + UP * y)
            lb = safe_text(txt, font="Inter", font_size=18, color=col)
            lb.next_to(dot, RIGHT, buff=0.2)
            level_dots.add(dot)
            level_labels.add(lb)

        # ZONE_LOWER -- playroom floor with tiny tower
        playroom = Rectangle(width=6, height=0.8, fill_color=CHILD_AMBER,
                             fill_opacity=0.1, stroke_color=CHILD_AMBER,
                             stroke_width=1, stroke_opacity=0.4)
        playroom.move_to(UP * ZONE_LOWER)
        tiny_tower = block_tower(height=0.8, n_blocks=3)
        tiny_tower.move_to(playroom.get_center())

        # Descending arrow alongside spiral
        desc_arrow = Arrow(UP * (ZONE_UPPER + 1.5) + LEFT * 3.5,
                           UP * (ZONE_LOWER - 0.5) + LEFT * 3.5,
                           color=PHILO_VIOLET, stroke_width=1.5,
                           max_tip_length_to_length_ratio=0.05)
        desc_arrow.set_opacity(0.4)

        # ZONE_FOOTER
        caption = safe_text("SEVEN LEVELS TO ONE ANSWER", font="Inter",
                            font_size=22, color=MUTED)
        caption.move_to(UP * ZONE_FOOTER)

        # -- Animations --
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4

        # Spiral appears with grow
        self.play(GrowFromCenter(spiral), run_time=0.6); t += 0.6

        # Descending arrow draws
        self.play(GrowArrow(desc_arrow), run_time=0.4); t += 0.4

        # Level labels cascade down with stagger
        self.play(
            LaggedStart(*[AnimationGroup(FadeIn(dot), FadeIn(lb, shift=LEFT * 0.2))
                          for dot, lb in zip(level_dots, level_labels)],
                        lag_ratio=0.12),
            run_time=1.8,
        )                                                                 # t=3.2

        # Playroom at bottom -- the destination
        self.play(FadeIn(playroom, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(tiny_tower, scale=0.8), run_time=0.4); t += 0.4
        self.play(Flash(tiny_tower.get_center(), color=CHILD_AMBER,
                        line_length=0.3, num_lines=6, run_time=0.3))     # t=4.3

        # Spiral fades slightly to emphasize the bottom
        self.play(
            spiral.animate.set_opacity(0.3),
            FadeIn(caption, shift=UP * 0.1),
            run_time=0.5,
        )                                                                 # t=4.8
        target = getattr(self.__class__, 'DURATION', 7.3)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: THE WRONG ANSWER (13.5-19.5s)
# Towering bookshelf -- the assumption that answers need sophistication
# Zones: TITLE, UPPER, MID, LOWER, FOOTER
# ================================================================
class Scene3_WrongAnswer(Scene):
    DURATION = 6.2
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE
        pill = label_pill("THE WRONG ANSWER", color=BOOK_TEAL)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER + MID -- bookshelf at center
        shelf = bookshelf(height=5.0, color=BOOK_TEAL)
        shelf.move_to(UP * ZONE_MID + UP * 0.5)

        # Magnifying glass searching through the books
        lens_ring = Circle(radius=0.5, stroke_color=WHITE_SOFT, stroke_width=2,
                           fill_opacity=0)
        lens_handle = Line(ORIGIN, DOWN * 0.4 + RIGHT * 0.3, color=WHITE_SOFT,
                           stroke_width=2.5)
        lens = VGroup(lens_ring, lens_handle)
        lens.move_to(UP * ZONE_UPPER + LEFT * 0.5)

        # "NEXT BOOK" labels at various heights
        next_labels = VGroup()
        positions = [UP * ZONE_UPPER + RIGHT * 2.5,
                     UP * ZONE_MID + RIGHT * 2.8,
                     UP * ZONE_LOWER + UP * 1.5 + RIGHT * 2.3]
        for pos in positions:
            lb = safe_text("NEXT BOOK", font="Inter", font_size=20, color=BOOK_TEAL)
            lb.set_opacity(0.6)
            lb.move_to(pos)
            next_labels.add(lb)

        # ZONE_LOWER -- height arrow showing the shelf growing
        height_arrow = Arrow(UP * (ZONE_LOWER - 0.5) + LEFT * 3.5,
                             UP * (ZONE_UPPER + 1.0) + LEFT * 3.5,
                             color=MUTED, stroke_width=1.5,
                             max_tip_length_to_length_ratio=0.08)
        height_label = safe_text("MORE\nTHEORY", font="Inter", font_size=18, color=MUTED)
        height_label.next_to(height_arrow, LEFT, buff=0.15)

        # ZONE_LOWER -- small child figure dwarfed by the shelf
        tiny_child = child_figure(height=1.2, color=CHILD_AMBER)
        tiny_child.set_opacity(0.5)
        tiny_child.move_to(RIGHT * 3 + UP * ZONE_LOWER)

        # ZONE_FOOTER
        caption = safe_text("THE ANSWER ISN'T AT THE TOP", font="Inter",
                            font_size=22, color=MUTED)
        caption.move_to(UP * ZONE_FOOTER)

        # -- Animations --
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(shelf, scale=0.9), run_time=0.6); t += 0.6

        # Magnifying glass scans downward through shelf
        self.play(FadeIn(lens, scale=0.8), run_time=0.3); t += 0.3
        self.play(lens.animate.move_to(UP * ZONE_MID + LEFT * 0.3),
                  run_time=0.6)                                           # t=1.9
        self.play(lens.animate.move_to(UP * ZONE_LOWER + UP * 1.5 + RIGHT * 0.2),
                  run_time=0.6)                                           # t=2.5

        # "NEXT BOOK" labels appear
        self.play(
            LaggedStart(*[FadeIn(l, shift=LEFT * 0.2) for l in next_labels],
                        lag_ratio=0.2),
            run_time=0.8,
        )                                                                 # t=3.3

        # Bookshelf grows taller -- stretching upward
        self.play(
            shelf.animate.scale(1.15).shift(UP * 0.3),
            GrowArrow(height_arrow),
            FadeIn(height_label, shift=RIGHT * 0.1),
            run_time=0.8,
        )                                                                 # t=4.1

        # Tiny child appears -- dwarfed
        self.play(FadeIn(tiny_child, scale=0.7), run_time=0.3); t += 0.3

        self.play(FadeIn(caption, shift=UP * 0.1), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 6.2)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE CONTRADICTION (19.5-26.5s)
# Bookshelf topples, child revealed underneath still building
# Zones: TITLE, UPPER, MID, LOWER, FOOTER
# ================================================================
class Scene4_Contradiction(Scene):
    DURATION = 7.3
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE
        pill = label_pill("THE CONTRADICTION", color=CHILD_AMBER)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER -- scattered fallen books
        fallen_books = VGroup()
        book_positions = [
            (-3, ZONE_UPPER + 1.0, 25), (-1.5, ZONE_UPPER + 1.5, -15),
            (0.5, ZONE_UPPER + 0.7, 40), (2, ZONE_UPPER + 1.8, -30),
            (3.5, ZONE_UPPER + 0.5, 10), (-2.5, ZONE_UPPER, -20),
            (1, ZONE_UPPER + 0.3, 35), (3, ZONE_UPPER - 0.3, -10),
        ]
        book_colors = [BOOK_TEAL, PHILO_VIOLET, TOWER_BLUE, GOLD,
                       BOOK_TEAL, PHILO_VIOLET, TOWER_BLUE, CHILD_AMBER]
        for (x, y, rot), col in zip(book_positions, book_colors):
            b = Rectangle(width=0.4, height=0.6, fill_color=col, fill_opacity=0.3,
                          stroke_color=col, stroke_width=1)
            b.rotate(rot * DEGREES)
            b.move_to(RIGHT * x + UP * y)
            fallen_books.add(b)

        # ZONE_MID -- child + her tower, the focal point
        child = child_figure(height=3.0, color=CHILD_AMBER)
        child.move_to(LEFT * 1.0 + UP * ZONE_MID)

        tower = block_tower(height=2.5, n_blocks=5)
        tower.move_to(RIGHT * 1.2 + UP * ZONE_MID)

        # Glow ring around tower
        glow = Circle(radius=1.8, fill_color=CHILD_AMBER, fill_opacity=0.06,
                      stroke_color=CHILD_AMBER, stroke_width=1, stroke_opacity=0.3)
        glow.move_to(tower.get_center())

        # ZONE_LOWER -- philosophy labels that converge on the tower
        orbit_data = [
            (LEFT * 3 + UP * (ZONE_LOWER + 1.5), "CRITIQUE"),
            (RIGHT * 3 + UP * (ZONE_LOWER + 1.5), "SURRENDER"),
            (LEFT * 3 + UP * (ZONE_LOWER - 0.5), "REBELLION"),
            (RIGHT * 3 + UP * (ZONE_LOWER - 0.5), "RECLAMATION"),
        ]
        orbit_labels = VGroup()
        orbit_arrows = VGroup()
        for pos, txt in orbit_data:
            lb = safe_text(txt, font="Inter", font_size=18, color=PHILO_VIOLET)
            lb.set_opacity(0.5)
            lb.move_to(pos)
            orbit_labels.add(lb)
            arr = Arrow(pos, tower.get_center(), color=PHILO_VIOLET, stroke_width=1,
                        buff=1.5, max_tip_length_to_length_ratio=0.15)
            arr.set_opacity(0.3)
            orbit_arrows.add(arr)

        # ZONE_FOOTER
        caption = safe_text("THE TOWER IS THE POINT", font="DM Serif Display",
                            font_size=26, color=CHILD_AMBER)
        caption.move_to(UP * ZONE_FOOTER)

        # -- Animations --
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4

        # Books scatter/fall in from above
        self.play(
            LaggedStart(*[FadeIn(b, shift=DOWN * 0.5, scale=0.5) for b in fallen_books],
                        lag_ratio=0.04),
            run_time=0.6,
        )                                                                 # t=1.0

        self.wait(0.4); t += 0.4

        # Child revealed underneath
        self.play(FadeIn(child, scale=0.9), run_time=0.5); t += 0.5
        self.play(FadeIn(tower, scale=0.8), FadeIn(glow, scale=0.5),
                  run_time=0.5)                                           # t=2.4

        # Tower pulses with warmth
        self.play(glow.animate.scale(1.3).set_opacity(0.12), run_time=0.4); t += 0.4
        self.play(glow.animate.scale(1/1.3).set_opacity(0.06), run_time=0.3); t += 0.3

        # Orbit labels converge from ZONE_LOWER
        self.play(
            LaggedStart(*[FadeIn(l, shift=UP*0.2) for l in orbit_labels], lag_ratio=0.08),
            run_time=0.6,
        )                                                                 # t=3.7
        self.play(
            LaggedStart(*[GrowArrow(a) for a in orbit_arrows], lag_ratio=0.08),
            run_time=0.6,
        )                                                                 # t=4.3

        self.play(FadeIn(caption, shift=UP * 0.1), run_time=0.4); t += 0.4

        # Books fade -- philosophy fades, child remains
        self.play(
            fallen_books.animate.set_opacity(0.08),
            orbit_labels.animate.set_opacity(0.2),
            glow.animate.scale(1.15),
            run_time=0.6,
        )                                                                 # t=5.3
        target = getattr(self.__class__, 'DURATION', 7.3)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE PROOF (26.5-33.5s)
# Tower at center, philosophical positions orbit and converge
# Zones: TITLE, UPPER, MID, LOWER, FOOTER
# ================================================================
class Scene5_Proof(Scene):
    DURATION = 7.3
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE
        pill = label_pill("THE PROOF", color=GOLD)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_MID -- central tower, large, glowing
        tower = block_tower(height=3.5, n_blocks=5)
        tower.move_to(UP * ZONE_MID + UP * 0.5)
        tower_glow = Circle(radius=2.5, fill_color=CHILD_AMBER, fill_opacity=0.05,
                            stroke_width=0)
        tower_glow.move_to(tower.get_center())

        # ZONE_UPPER + MID -- orbiting philosophical positions
        orbit_data = [
            (-3.0, ZONE_UPPER, "NAIVE BELIEF", GOLD),
            (3.0, ZONE_UPPER, "NIHILISM", DEAD_GRAY),
            (-3.0, ZONE_MID - 1.5, "EXISTENTIALISM", PHILO_VIOLET),
            (3.0, ZONE_MID - 1.5, "ABSURDISM", CHILD_AMBER),
        ]
        orbit_groups = VGroup()
        for x, y, txt, col in orbit_data:
            dot = Dot(radius=0.15, color=col)
            dot.move_to(RIGHT * x + UP * y)
            lb = safe_text(txt, font="Inter", font_size=18, color=col, weight="BOLD")
            lb.next_to(dot, DOWN, buff=0.15)
            line = DashedLine(dot.get_center(), tower.get_center(),
                              color=col, stroke_width=1, dash_length=0.15)
            line.set_opacity(0.3)
            orbit_groups.add(VGroup(dot, lb, line))

        # ZONE_LOWER -- the equation
        eq_text = safe_text("THE BUILDING = THE POINT", font="Bebas Neue",
                            font_size=56, color=GOLD)
        eq_text.move_to(UP * ZONE_LOWER + UP * 0.5)

        # Sub-labels below equation
        sub_items = ["NOT THE HEIGHT", "NOT THE METRIC", "NOT THE AUDIENCE"]
        sub_group = VGroup()
        for i, txt in enumerate(sub_items):
            lbl = safe_text(txt, font="Inter", font_size=20, color=MUTED)
            lbl.move_to(UP * ZONE_LOWER + DOWN * (0.3 + i * 0.5))
            sub_group.add(lbl)

        # ZONE_FOOTER
        footer = safe_text("ALL ROADS LEAD HERE", font="Inter",
                           font_size=20, color=DIM)
        footer.move_to(UP * ZONE_FOOTER)

        # -- Animations --
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(tower_glow), FadeIn(tower, scale=0.8),
                  run_time=0.6)                                           # t=1.0

        # Orbiting positions appear with stagger
        for grp in orbit_groups:
            dot, lb, line = grp
            self.play(FadeIn(dot, scale=1.2), FadeIn(lb, shift=UP*0.1),
                      run_time=0.3)
            self.play(Create(line), run_time=0.2); t += 0.2
                                                                          # t=3.0

        # All converge -- lines brighten, glow pulses
        self.play(
            *[grp[2].animate.set_opacity(0.7) for grp in orbit_groups],
            tower_glow.animate.scale(1.2).set_opacity(0.1),
            run_time=0.6,
        )                                                                 # t=3.6

        # Equation appears with flash
        self.play(FadeIn(eq_text, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(eq_text.get_center(), color=GOLD,
                        line_length=0.4, num_lines=8, run_time=0.3))     # t=4.4

        # Sub-labels cascade in
        self.play(
            LaggedStart(*[FadeIn(s, shift=UP*0.1) for s in sub_group], lag_ratio=0.15),
            run_time=0.6,
        )                                                                 # t=5.0

        self.play(FadeIn(footer, shift=UP * 0.1), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 7.3)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE GUT PUNCH (33.5-40.0s)
# Child finishes tower, smiles, knocks it down, starts again
# Zones: TITLE, UPPER, MID, LOWER, FOOTER
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 6.7
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE
        pill = label_pill("THE HANDS WERE MINE", color=CHILD_AMBER)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER -- warm ambient glow
        warm_glow = Circle(radius=3, fill_color=CHILD_AMBER, fill_opacity=0.04,
                           stroke_width=0)
        warm_glow.move_to(UP * ZONE_UPPER - UP * 1.0)

        # ZONE_MID -- child + completed tower
        child = child_figure(height=3.5, color=CHILD_AMBER)
        child.move_to(LEFT * 1.5 + UP * ZONE_MID + UP * 0.5)

        tower = block_tower(height=3.0, n_blocks=5)
        tower.move_to(RIGHT * 1.5 + UP * ZONE_MID + UP * 0.5)

        # ZONE_LOWER -- scattered blocks from previous knock-down
        scattered = VGroup()
        scatter_data = [
            (-2.5, ZONE_LOWER + 0.5, 15, TOWER_BLUE),
            (-0.5, ZONE_LOWER, -20, GOLD),
            (1, ZONE_LOWER + 0.8, 30, BOOK_TEAL),
            (2.5, ZONE_LOWER - 0.2, -10, PHILO_VIOLET),
            (-1.5, ZONE_LOWER - 1.0, 40, CHILD_AMBER),
            (0.5, ZONE_LOWER - 1.3, -25, TOWER_BLUE),
        ]
        for x, y, rot, col in scatter_data:
            b = Rectangle(width=0.4, height=0.25, fill_color=col, fill_opacity=0.3,
                          stroke_color=col, stroke_width=0.8)
            b.rotate(rot * DEGREES)
            b.move_to(RIGHT * x + UP * y)
            scattered.add(b)

        # New starting block -- she begins again
        new_block = Rectangle(width=0.7, height=0.3, fill_color=CHILD_AMBER,
                              fill_opacity=0.8, stroke_color=WHITE_SOFT, stroke_width=1)
        new_block.move_to(RIGHT * 1.5 + UP * ZONE_LOWER + UP * 1.5)

        # ZONE_FOOTER -- final words
        quote = safe_text("NO YARDSTICK CAN MEASURE", font="DM Serif Display",
                          font_size=28, color=WHITE_SOFT)
        quote.move_to(UP * ZONE_FOOTER + UP * 0.3)
        quote2 = safe_text("WHAT IT MEANT TO SPEND THEM", font="DM Serif Display",
                           font_size=26, color=CHILD_AMBER)
        quote2.move_to(UP * ZONE_FOOTER - UP * 0.3)

        # -- Animations --
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(warm_glow), run_time=0.3); t += 0.3
        self.play(FadeIn(child, scale=0.9), FadeIn(tower, scale=0.9),
                  run_time=0.6)                                           # t=1.3

        # Tower glows briefly -- pride moment
        self.play(warm_glow.animate.scale(1.15).set_opacity(0.07),
                  run_time=0.4)                                           # t=1.7

        self.wait(0.3); t += 0.3

        # Tower topples -- blocks scatter downward
        self.play(
            tower.animate.set_opacity(0).shift(DOWN * 0.5),
            run_time=0.4,
        )                                                                 # t=2.4
        self.play(
            LaggedStart(*[FadeIn(b, shift=DOWN * 0.3, scale=0.5) for b in scattered],
                        lag_ratio=0.04),
            run_time=0.5,
        )                                                                 # t=2.9

        # Warm glow contracts after collapse
        self.play(warm_glow.animate.scale(0.7).set_opacity(0.03),
                  run_time=0.3)                                           # t=3.2

        # New block appears -- she starts again
        self.play(FadeIn(new_block, shift=UP * 0.2), run_time=0.4); t += 0.4
        self.play(Flash(new_block.get_center(), color=CHILD_AMBER,
                        line_length=0.2, num_lines=4, run_time=0.3))     # t=3.9

        # Glow re-expands -- joy returns
        self.play(warm_glow.animate.scale(1.3).set_opacity(0.06),
                  run_time=0.4)                                           # t=4.3

        # Final quote
        self.play(FadeIn(quote, shift=UP * 0.1), run_time=0.5); t += 0.5
        self.play(FadeIn(quote2, shift=UP * 0.1), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 6.7)
        self.wait(max(0.1, target - t - 0.8))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# -- Infra -------------------------------------------------------------
def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_Mystery, Scene3_WrongAnswer,
          Scene4_Contradiction, Scene5_Proof, Scene6_Punch]
    config.output_file = f"child_already_knew_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"child_already_knew_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    sc = [Scene1_Hook, Scene2_Mystery, Scene3_WrongAnswer,
          Scene4_Contradiction, Scene5_Proof, Scene6_Punch]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(sc):
        n = f"child_already_knew_scene_{i+1}"; print(f"  Preview {n}...")
        config.output_file = n; config.save_last_frame = True; config.format = "png"
        S().render()
        for p in Path(config.media_dir).rglob(f"{n}*"):
            if p.suffix == ".png":
                dst = d / f"{n}.png"; shutil.copy2(str(p), str(dst))
                print(f"  OK: {dst} ({dst.stat().st_size//1024} KB)"); break
    config.save_last_frame = False; config.format = None
    print(f"\nAll 6 previews -> {d}/")

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

    names = ["Scene1_Hook","Scene2_Mystery","Scene3_WrongAnswer",
             "Scene4_Contradiction","Scene5_Proof","Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_child_already_knew.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="child_already_knew", audio_path=str(audio))
    final = od / "child_already_knew_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
