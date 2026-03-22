#!/usr/bin/env python3
"""Zoroaster & the Steppe — 'Your Religion Came from the Steppe' (Manim).

6 scenes, ~29s. Mystery/reveal arc.
Custom domain shapes: fire_altar, timeline_bar, religion_symbol, steppe_horizon.

VTT cues (absolute → relative):
  Scene 1 (0.0–4.5s = 4.50s):  THE WRONG ANSWER
    0.000 (0.00) Everyone knows where heaven and hell came from.
    2.200 (2.20) The Bible.
  Scene 2 (4.5–9.0s = 4.50s):  THE CONTRADICTION
    4.500 (0.00) But there's a problem.
    5.800 (1.30) Zoroastrianism described heaven, hell, and a final judgment
    7.500 (3.00) a thousand years before the Bible.
  Scene 3 (9.0–14.0s = 5.00s):  THE DISMISSED TRUTH
    9.000 (0.00) Zoroaster was a steppe prophet from Central Eurasia.
   10.800 (1.80) One god. Heaven. Hell. Judgment day.
   12.500 (3.50) He wrote it first.
  Scene 4 (14.0–19.0s = 5.00s):  THE PROOF
   14.000 (0.00) In 539 BC, Cyrus freed the Jews from Babylon.
   16.000 (2.00) Before Babylon, the Hebrew scriptures had no heaven or hell.
   18.000 (4.00) After — they did.
  Scene 5 (19.0–23.5s = 4.50s):  THE SCALE
   19.000 (0.00) Four billion people.
   20.200 (1.20) Judaism. Christianity. Islam.
   21.800 (2.80) All carrying Zoroastrian DNA.
  Scene 6 (23.5–29.0s = 5.50s):  THE PUNCH
   23.500 (0.00) Every time someone tells you about heaven or hell,
   25.500 (2.00) you're hearing an echo
   27.000 (3.50) from the Central Eurasian steppe.
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

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

# ── TTS Script ────────────────────────────────────────────────
TTS_SCRIPT = """Everyone knows where heaven and hell came from. The Bible. But Zoroastrianism described heaven, hell, and final judgment a thousand years earlier. Zoroaster was a steppe prophet. One god. Judgment day. He wrote it first. In 539 BC, Cyrus freed the Jews from Babylon. Before Babylon, Hebrew scriptures had no afterlife. After — they did. Four billion people carrying Zoroastrian ideas. Every mention of heaven or hell is an echo from the steppe."""

# ── Palette (Zoroastrian: warm golds, deep blues, fire oranges) ──
BG = "#080A10"; GRID = "#1A2030"; SURFACE = "#15192A"
GOLD = "#FFD700"; GOLD_DIM = "#B8960F"; GOLD_WARM = "#E8B830"
FIRE = "#FF6B2B"; FIRE_DIM = "#CC4400"; EMBER = "#FF4500"
DEEP_BLUE = "#1E3A6E"; NIGHT = "#0C1425"
RED = "#E63946"; RED_DIM = "#A01020"
SAND = "#C4A06A"; SAND_DIM = "#8B7355"
WHITE_SOFT = "#F0F0F0"; MUTED = "#7B8DA0"; DIM_TEXT = "#6B7B90"
PARCHMENT = "#E8D5A8"; BROWN = "#5C3D1E"

SAFE_W = 8.0
SAFE_TOP = 7.2
SAFE_BOT = -6.4

# Vertical layout zones — USE THESE for all positioning
ZONE_TITLE  = 6.2    # y 5.5–7.0  — scene label pills
ZONE_UPPER  = 3.5    # y 1.5–5.5  — hero visual top portion
ZONE_MID    = 0.0    # y -1.5–1.5 — central focal point, big numbers
ZONE_LOWER  = -3.5   # y -5.5–-1.5 — supporting visuals, bars, icons
ZONE_FOOTER = -6.0   # y -6.4–-5.5 — captions, source labels


# ── Core helpers ──────────────────────────────────────────────

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


# ── Domain shapes ─────────────────────────────────────────────

def fire_altar(scale=1.0, flame_color=FIRE, base_color=GOLD_DIM):
    """Zoroastrian fire altar — pedestal with eternal flame."""
    # Pedestal base
    base = Rectangle(width=1.6*scale, height=0.3*scale, fill_color=base_color,
                     fill_opacity=0.8, stroke_color=GOLD, stroke_width=1.5*scale)
    base.move_to(DOWN * 0.3 * scale)
    # Pedestal column
    col = Rectangle(width=0.6*scale, height=1.0*scale, fill_color=base_color,
                    fill_opacity=0.6, stroke_color=GOLD, stroke_width=1*scale)
    col.move_to(UP * 0.2 * scale)
    # Bowl
    bowl = Arc(radius=0.5*scale, start_angle=PI, angle=PI, color=GOLD,
               stroke_width=2*scale)
    bowl.move_to(UP * 0.75 * scale)
    # Flame (three layered teardrop shapes)
    flames = VGroup()
    for dx, h, op in [(0, 0.8, 0.9), (-0.15, 0.5, 0.6), (0.15, 0.5, 0.6)]:
        flame = Polygon(
            np.array([dx*scale, 0.9*scale, 0]),
            np.array([(dx-0.12)*scale, (0.9+h*0.3)*scale, 0]),
            np.array([dx*scale, (0.9+h)*scale, 0]),
            np.array([(dx+0.12)*scale, (0.9+h*0.3)*scale, 0]),
            fill_color=flame_color, fill_opacity=op, stroke_width=0,
        )
        flames.add(flame)
    return VGroup(base, col, bowl, flames)

def timeline_bar(width=7.0, y=0, left_label="1500 BC", right_label="500 BC",
                 gap_label="1,000 YEARS", left_color=GOLD, right_color=DIM_TEXT):
    """Horizontal timeline showing the 1000-year gap."""
    line = Line(LEFT*width/2, RIGHT*width/2, color=MUTED, stroke_width=2)
    line.move_to(UP * y)
    # Left marker (Zoroaster)
    l_dot = Dot(LEFT*width/2 + UP*y, radius=0.12, color=left_color)
    l_text = safe_text(left_label, font="Bebas Neue", font_size=32, color=left_color)
    l_text.next_to(l_dot, DOWN, buff=0.25)
    # Right marker (Bible)
    r_dot = Dot(RIGHT*width/2 + UP*y, radius=0.12, color=right_color)
    r_text = safe_text(right_label, font="Bebas Neue", font_size=32, color=right_color)
    r_text.next_to(r_dot, DOWN, buff=0.25)
    # Gap label
    gap = safe_text(gap_label, font="Bebas Neue", font_size=44, color=RED)
    gap.move_to(UP * y + UP * 0.5)
    # Arrow spanning
    arr = Arrow(LEFT*width/2 + UP*y + UP*0.15, RIGHT*width/2 + UP*y + UP*0.15,
                color=RED, stroke_width=2, buff=0.2, max_tip_length_to_length_ratio=0.05)
    return VGroup(line, l_dot, l_text, r_dot, r_text, gap, arr)

def religion_symbol(name="judaism", size=0.8, color=GOLD):
    """Simple geometric religion symbols."""
    if name == "judaism":
        # Star of David — two overlapping triangles
        t1 = Polygon(UP*size, LEFT*size*0.85+DOWN*size*0.5, RIGHT*size*0.85+DOWN*size*0.5,
                      color=color, stroke_width=2, fill_opacity=0)
        t2 = Polygon(DOWN*size, LEFT*size*0.85+UP*size*0.5, RIGHT*size*0.85+UP*size*0.5,
                      color=color, stroke_width=2, fill_opacity=0)
        return VGroup(t1, t2)
    elif name == "christianity":
        # Cross
        v = Line(UP*size, DOWN*size*0.6, color=color, stroke_width=3)
        h = Line(LEFT*size*0.5 + UP*size*0.3, RIGHT*size*0.5 + UP*size*0.3,
                 color=color, stroke_width=3)
        return VGroup(v, h)
    elif name == "islam":
        # Crescent + star
        outer = Arc(radius=size*0.7, start_angle=30*DEGREES, angle=300*DEGREES,
                    color=color, stroke_width=3)
        star = Dot(RIGHT*size*0.4 + UP*size*0.3, radius=0.06, color=color)
        return VGroup(outer, star)
    return Circle(radius=size*0.5, color=color, stroke_width=2)

def steppe_horizon(width=10, y=-3.5, sky_color=NIGHT, ground_color=SAND_DIM):
    """Layered steppe landscape silhouette — rolling hills against dark sky."""
    # Sky glow
    sky = Rectangle(width=width, height=4, fill_color=sky_color, fill_opacity=0.3,
                    stroke_width=0).move_to(UP*(y+3))
    # Rolling hills (polygon)
    pts = [np.array([-width/2, y-1, 0])]
    for i in range(20):
        x = -width/2 + i * width / 19
        h = y + 0.3 * np.sin(i * 0.8) + 0.15 * np.sin(i * 2.1) + 0.1
        pts.append(np.array([x, h, 0]))
    pts.append(np.array([width/2, y-1, 0]))
    hills = Polygon(*pts, fill_color=ground_color, fill_opacity=0.4,
                    stroke_color=SAND, stroke_width=1)
    # Distant ridge (behind, higher)
    pts2 = [np.array([-width/2, y-0.5, 0])]
    for i in range(20):
        x = -width/2 + i * width / 19
        h = y + 0.5 * np.sin(i * 0.5 + 1) + 0.6
        pts2.append(np.array([x, h, 0]))
    pts2.append(np.array([width/2, y-0.5, 0]))
    ridge = Polygon(*pts2, fill_color=ground_color, fill_opacity=0.2,
                    stroke_width=0)
    return VGroup(sky, ridge, hills)


# ================================================================
# SCENE 1: THE WRONG ANSWER (0.0–4.5s)
# "Everyone knows where heaven and hell came from. The Bible."
# Warm gold scroll/bible visual. Familiar, authoritative.
# Zones: TITLE, UPPER, MID, LOWER, FOOTER
# ================================================================
class Scene1_WrongAnswer(Scene):
    DURATION = 4.5
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # TITLE zone — scene pill
        pill = label_pill("THE WRONG ANSWER", color=GOLD)
        pill.move_to(UP * ZONE_TITLE)                                       # t=0.0

        # UPPER zone — scroll/parchment visual
        scroll = RoundedRectangle(width=5, height=3.5, corner_radius=0.3,
                                  fill_color=BROWN, fill_opacity=0.3,
                                  stroke_color=GOLD_DIM, stroke_width=2)
        scroll.move_to(UP * ZONE_UPPER)
        # Text lines on scroll
        scroll_lines = VGroup()
        for i in range(5):
            ln = Line(LEFT*1.8, RIGHT*1.8, color=PARCHMENT, stroke_width=1)
            ln.move_to(UP*ZONE_UPPER + UP*0.9 + DOWN*i*0.45).set_opacity(0.3)
            scroll_lines.add(ln)
        scroll_glow = Circle(radius=1.5, fill_color=GOLD, fill_opacity=0.06,
                             stroke_width=0).move_to(UP * ZONE_UPPER)

        # MID zone — "Heaven & Hell" big text (labels only, not narration)
        heaven = safe_text("Heaven & Hell", font="Bebas Neue", font_size=80, color=GOLD)
        heaven.move_to(UP * ZONE_MID)
        underline = Line(LEFT*2.5, RIGHT*2.5, color=GOLD, stroke_width=2)
        underline.move_to(UP * ZONE_MID + DOWN * 0.5)

        # LOWER zone — small fire altar as visual anchor
        altar_small = fire_altar(scale=0.6, flame_color=GOLD_WARM, base_color=GOLD_DIM)
        altar_small.move_to(UP * ZONE_LOWER)
        altar_glow = Circle(radius=1.0, fill_color=GOLD, fill_opacity=0.04,
                            stroke_width=0).move_to(UP * ZONE_LOWER)

        # FOOTER zone — "The Bible." label
        the_bible = safe_text("The Bible.", font="Bebas Neue", font_size=56, color=GOLD_WARM)
        the_bible.move_to(UP * ZONE_FOOTER)

        # ── Timing: 4.5s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(scroll_glow), FadeIn(scroll), run_time=0.4); t += 0.4
        self.play(LaggedStart(*[FadeIn(l) for l in scroll_lines], lag_ratio=0.08),
                  run_time=0.4)                                            # t=1.1
        self.play(FadeIn(heaven, scale=1.1), Create(underline),
                  run_time=0.5)                                            # t=1.6
        self.play(FadeIn(altar_glow), GrowFromCenter(altar_small),
                  run_time=0.5)                                            # t=2.1
        self.wait(0.6); t += 0.6
        self.play(FadeIn(the_bible, scale=1.15), run_time=0.4); t += 0.4
        self.play(Flash(the_bible.get_center(), color=GOLD,
                        line_length=0.3, num_lines=8, run_time=0.3))       # t=3.4
        target = getattr(self.__class__, 'DURATION', 4.5)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE CONTRADICTION (4.5–9.0s)
# "Zoroastrianism described heaven, hell, and a final judgment
#  a thousand years before the Bible."
# Timeline showing 1000-year gap. Red tension.
# Zones: TITLE, UPPER, MID, LOWER, FOOTER
# ================================================================
class Scene2_Contradiction(Scene):
    DURATION = 4.5
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # TITLE zone
        pill = label_pill("THE CONTRADICTION", color=RED)
        pill.move_to(UP * ZONE_TITLE)

        # UPPER zone — fire altar (Zoroastrian) vs scroll (Biblical)
        fire = fire_altar(scale=0.7, flame_color=FIRE)
        fire.move_to(LEFT * 2.5 + UP * ZONE_UPPER)

        scroll_icon = RoundedRectangle(width=1.0, height=1.4, corner_radius=0.1,
                                       fill_color=DIM_TEXT, fill_opacity=0.3,
                                       stroke_color=DIM_TEXT, stroke_width=1.5)
        scroll_icon.move_to(RIGHT * 2.5 + UP * ZONE_UPPER)
        # Question mark between them
        q_mark = safe_text("?", font="Bebas Neue", font_size=80, color=RED)
        q_mark.move_to(UP * ZONE_UPPER)

        # MID zone — timeline bar showing gap
        tl = timeline_bar(width=6.5, y=ZONE_MID, left_label="~1500 BC",
                          right_label="~500 BC", gap_label="1,000 YEARS",
                          left_color=GOLD, right_color=DIM_TEXT)

        # LOWER zone — "1,000 YEARS EARLIER" big reveal
        thousand = safe_text("1,000 YEARS", font="Bebas Neue", font_size=64, color=GOLD)
        thousand.move_to(UP * ZONE_LOWER)

        # FOOTER — source context
        src = safe_text("Zoroaster · Central Eurasia", font="Inter",
                        font_size=24, color=MUTED)
        src.move_to(UP * ZONE_FOOTER)

        # ── Timing: 4.5s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(GrowFromCenter(fire), FadeIn(scroll_icon),
                  run_time=0.4)                                            # t=0.7
        self.play(FadeIn(q_mark, scale=1.3), run_time=0.3); t += 0.3
        self.wait(0.3); t += 0.3
        # Timeline builds
        self.play(Create(tl[0]), run_time=0.3); t += 0.3
        self.play(FadeIn(tl[1]), FadeIn(tl[2]), run_time=0.3); t += 0.3
        self.play(FadeIn(tl[3]), FadeIn(tl[4]), run_time=0.3); t += 0.3
        self.play(GrowArrow(tl[6]), FadeIn(tl[5], scale=1.1),
                  run_time=0.4)                                            # t=2.6 (gap + arrow)
        self.wait(0.4); t += 0.4
        self.play(FadeIn(thousand, scale=1.15), run_time=0.4); t += 0.4
        self.play(Flash(thousand.get_center(), color=GOLD,
                        line_length=0.3, num_lines=8, run_time=0.3))       # t=3.7
        self.play(FadeIn(src), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 4.5)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: THE DISMISSED TRUTH (9.0–14.0s)
# "Zoroaster was a steppe prophet from Central Eurasia.
#  One god. Heaven. Hell. Judgment day. He wrote it first."
# Fire altar. Steppe horizon. Reverent gold tones.
# Zones: TITLE, UPPER, MID, LOWER, FOOTER
# ================================================================
class Scene3_DismissedTruth(Scene):
    DURATION = 5.0
    def construct(self):
        self.add(gradient_bg("#0A0C14"), grid_lines(0.03))
        t = 0

        # TITLE zone
        pill = label_pill("THE DISMISSED TRUTH", color=GOLD)
        pill.move_to(UP * ZONE_TITLE)

        # UPPER zone — "Zoroaster." name
        name = safe_text("Zoroaster.", font="Bebas Neue", font_size=72, color=GOLD)
        name.move_to(UP * 4.0)
        subtitle = safe_text("Steppe Prophet", font="Inter",
                             font_size=30, color=MUTED)
        subtitle.move_to(UP * 3.2)

        # MID zone — fire altar (larger, centered hero visual)
        altar = fire_altar(scale=1.2, flame_color=FIRE, base_color=GOLD_DIM)
        altar.move_to(UP * 0.5)
        # Glow behind altar
        altar_glow = Circle(radius=2, fill_color=FIRE, fill_opacity=0.04,
                            stroke_width=0).move_to(UP * 0.5)

        # LOWER zone — doctrine items appearing one by one
        items = ["One God", "Heaven", "Hell", "Judgment Day"]
        item_mobs = VGroup()
        for i, txt in enumerate(items):
            lbl = safe_text(txt, font="Inter", font_size=38, color=GOLD_WARM, weight="BOLD")
            x = -2.5 + i * 1.7
            lbl.move_to(np.array([x, ZONE_LOWER, 0]))
            item_mobs.add(lbl)
        # Separator dots between items
        dots = VGroup()
        for i in range(3):
            d = Dot(np.array([-2.5 + (i+1)*1.7 - 0.85, ZONE_LOWER, 0]),
                    radius=0.05, color=MUTED)
            dots.add(d)

        # FOOTER — steppe horizon at bottom + "He wrote it first."
        horizon = steppe_horizon(width=10, y=ZONE_FOOTER, ground_color=SAND_DIM)
        first = safe_text("He wrote it first.", font="Bebas Neue", font_size=44,
                          color=WHITE_SOFT)
        first.move_to(UP * (ZONE_LOWER - 1.5))

        # ── Timing: 5.0s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.add(horizon)
        self.play(FadeIn(name, shift=DOWN*0.2), run_time=0.4); t += 0.4
        self.play(FadeIn(subtitle), run_time=0.3); t += 0.3
        self.play(FadeIn(altar_glow), GrowFromCenter(altar), run_time=0.6); t += 0.6
        self.wait(0.2); t += 0.2
        # Doctrine items stagger in
        self.play(
            LaggedStart(*[FadeIn(t, scale=1.1) for t in item_mobs], lag_ratio=0.15),
            LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.2),
            run_time=1.0,
        )                                                                  # t=2.8
        self.wait(0.7); t += 0.7
        self.play(FadeIn(first, shift=UP*0.2), run_time=0.5); t += 0.5
        self.play(Flash(first.get_center(), color=GOLD,
                        line_length=0.2, num_lines=6, run_time=0.2))       # t=4.2
        target = getattr(self.__class__, 'DURATION', 5.0)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE PROOF (14.0–19.0s)
# "In 539 BC, Cyrus freed the Jews from Babylon.
#  Before Babylon: no heaven or hell. After — they did."
# Big "539 BC". Before/After split.
# Zones: TITLE, UPPER, MID, LOWER, FOOTER
# ================================================================
class Scene4_Proof(Scene):
    DURATION = 5.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # TITLE zone
        pill = label_pill("THE PROOF", color=GOLD)
        pill.move_to(UP * ZONE_TITLE)

        # UPPER zone — "539 BC" massive
        bc = safe_text("539 BC", font="Bebas Neue", font_size=120, color=GOLD)
        bc.move_to(UP * ZONE_UPPER)

        # MID zone — Before/After split with divider
        divider = DashedLine(UP*1.5, DOWN*1.5, color=MUTED, stroke_width=1.5,
                             dash_length=0.15).move_to(UP * ZONE_MID)

        # Before panel (left)
        before_label = safe_text("BEFORE", font="Bebas Neue", font_size=40, color=DIM_TEXT)
        before_label.move_to(LEFT*2.5 + UP*1.0)
        # X marks for "no heaven, no hell"
        x1 = safe_text("X", font="Bebas Neue", font_size=60, color=RED)
        x1.move_to(LEFT*2.5 + UP * ZONE_MID).set_opacity(0.5)
        x2 = x1.copy()
        x2.move_to(LEFT*2.5 + DOWN*0.6).set_opacity(0.5)

        # After panel (right)
        after_label = safe_text("AFTER", font="Bebas Neue", font_size=40, color=GOLD)
        after_label.move_to(RIGHT*2.5 + UP*1.0)
        # Checkmarks for "heaven, hell gained"
        check1 = safe_text("Heaven", font="Inter", font_size=34, color=GOLD_WARM)
        check1.move_to(RIGHT*2.5 + UP * ZONE_MID)
        check2 = safe_text("Hell", font="Inter", font_size=34, color=GOLD_WARM)
        check2.move_to(RIGHT*2.5 + DOWN*0.6)

        # LOWER zone — small fire altar to tie back to Zoroaster
        proof_altar = fire_altar(scale=0.5, flame_color=FIRE)
        proof_altar.move_to(UP * ZONE_LOWER)
        # Arrow from altar toward the "AFTER" side
        proof_arrow = Arrow(UP * ZONE_LOWER + UP * 1.0, UP * ZONE_MID + DOWN * 1.5,
                            color=GOLD, stroke_width=2, buff=0.2,
                            max_tip_length_to_length_ratio=0.08)

        # FOOTER
        source = safe_text("Babylonian Exile · 586-539 BC", font="Inter",
                           font_size=24, color=MUTED)
        source.move_to(UP * ZONE_FOOTER)

        # ── Timing: 5.0s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(bc, scale=1.15), run_time=0.4); t += 0.4
        self.play(Flash(bc.get_center(), color=GOLD,
                        line_length=0.4, num_lines=10, run_time=0.3))      # t=1.0
        self.wait(0.7); t += 0.7
        # Before/After split
        self.play(Create(divider), run_time=0.3); t += 0.3
        self.play(FadeIn(before_label), FadeIn(after_label), run_time=0.3); t += 0.3
        self.play(FadeIn(x1), FadeIn(x2), run_time=0.3); t += 0.3
        self.wait(0.4); t += 0.4
        # "After" reveal
        self.play(FadeIn(check1, shift=LEFT*0.2),
                  FadeIn(check2, shift=LEFT*0.2), run_time=0.3)            # t=3.3
        self.wait(0.3); t += 0.3
        self.play(GrowFromCenter(proof_altar), GrowArrow(proof_arrow),
                  run_time=0.4)                                            # t=4.0
        self.play(FadeIn(source), run_time=0.2); t += 0.2
        target = getattr(self.__class__, 'DURATION', 5.0)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE SCALE (19.0–23.5s)
# "Four billion people. Judaism. Christianity. Islam.
#  All carrying Zoroastrian DNA."
# Big counter. Three religion symbols.
# Zones: TITLE, UPPER, MID, LOWER, FOOTER
# ================================================================
class Scene5_Scale(Scene):
    DURATION = 4.5
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # TITLE zone
        pill = label_pill("THE SCALE", color=GOLD)
        pill.move_to(UP * ZONE_TITLE)

        # UPPER zone — big "4 BILLION" number
        four_b = safe_text("4,000,000,000", font="Bebas Neue", font_size=80, color=GOLD)
        four_b.move_to(UP * 3.8)
        people = safe_text("PEOPLE", font="Bebas Neue", font_size=48, color=GOLD_DIM)
        people.move_to(UP * 2.8)

        # MID zone — three religion symbols in a row
        sym_judaism = religion_symbol("judaism", size=0.7, color=GOLD_WARM)
        sym_judaism.move_to(LEFT * 2.5 + UP * ZONE_MID)
        lbl_j = safe_text("Judaism", font="Inter", font_size=28, color=WHITE_SOFT)
        lbl_j.move_to(LEFT * 2.5 + DOWN * 1.0)

        sym_christianity = religion_symbol("christianity", size=0.7, color=GOLD_WARM)
        sym_christianity.move_to(UP * ZONE_MID)
        lbl_c = safe_text("Christianity", font="Inter", font_size=28, color=WHITE_SOFT)
        lbl_c.move_to(DOWN * 1.0)

        sym_islam = religion_symbol("islam", size=0.7, color=GOLD_WARM)
        sym_islam.move_to(RIGHT * 2.5 + UP * ZONE_MID)
        lbl_i = safe_text("Islam", font="Inter", font_size=28, color=WHITE_SOFT)
        lbl_i.move_to(RIGHT * 2.5 + DOWN * 1.0)

        # Connecting lines from each symbol downward to LOWER zone
        conn_lines = VGroup()
        for x in [-2.5, 0, 2.5]:
            cl = DashedLine(np.array([x, -1.4, 0]), np.array([x, ZONE_LOWER + 0.8, 0]),
                            color=GOLD, stroke_width=1, dash_length=0.15).set_opacity(0.4)
            conn_lines.add(cl)

        # LOWER zone — fire altar showing Zoroastrian origin
        origin_altar = fire_altar(scale=0.6, flame_color=FIRE)
        origin_altar.move_to(UP * ZONE_LOWER)
        origin_glow = Circle(radius=1.2, fill_color=FIRE, fill_opacity=0.04,
                             stroke_width=0).move_to(UP * ZONE_LOWER)

        # FOOTER — source label
        footer_src = safe_text("Zoroastrian DNA", font="Bebas Neue",
                               font_size=40, color=GOLD_DIM)
        footer_src.move_to(UP * ZONE_FOOTER)

        # ── Timing: 4.5s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(four_b, scale=1.1), run_time=0.4); t += 0.4
        self.play(FadeIn(people), run_time=0.2); t += 0.2
        self.wait(0.3); t += 0.3
        # Symbols appear
        self.play(
            GrowFromCenter(sym_judaism), FadeIn(lbl_j),
            run_time=0.3,
        )                                                                  # t=1.5
        self.play(
            GrowFromCenter(sym_christianity), FadeIn(lbl_c),
            run_time=0.3,
        )                                                                  # t=1.8
        self.play(
            GrowFromCenter(sym_islam), FadeIn(lbl_i),
            run_time=0.3,
        )                                                                  # t=2.1
        self.play(LaggedStart(*[Create(c) for c in conn_lines], lag_ratio=0.1),
                  run_time=0.3)                                            # t=2.4
        self.wait(0.3); t += 0.3
        self.play(FadeIn(origin_glow), GrowFromCenter(origin_altar),
                  run_time=0.4)                                            # t=3.1
        self.play(FadeIn(footer_src, shift=UP*0.1), run_time=0.3); t += 0.3
        self.play(Flash(origin_altar.get_center(), color=FIRE,
                        line_length=0.3, num_lines=8, run_time=0.3))       # t=3.7
        target = getattr(self.__class__, 'DURATION', 4.5)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE PUNCH (23.5–29.0s)
# "Every time someone tells you about heaven or hell,
#  you're hearing an echo from the Central Eurasian steppe."
# Steppe horizon. Cinematic letterbox. Quiet, final.
# Zones: TITLE, UPPER, MID, LOWER, FOOTER
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 5.5
    def construct(self):
        self.add(gradient_bg("#0A0A08"), grid_lines(0.02))
        t = 0

        # Letterbox bars for cinematic feel
        bh = 0.8
        top_bar = Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                            stroke_width=0).move_to(UP*(8-bh/2))
        bot_bar = Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                            stroke_width=0).move_to(DOWN*(8-bh/2))
        self.add(top_bar, bot_bar)

        # UPPER zone — distant steppe horizon spanning full width
        horizon = steppe_horizon(width=10, y=ZONE_UPPER - 2, sky_color=NIGHT,
                                 ground_color=SAND_DIM)

        # MID zone — solitary fire altar on the horizon
        distant_fire = fire_altar(scale=0.5, flame_color=FIRE)
        distant_fire.move_to(UP * (ZONE_MID + 0.2))
        fire_glow = Circle(radius=1.5, fill_color=FIRE, fill_opacity=0.03,
                           stroke_width=0).move_to(UP * (ZONE_MID + 0.2))

        # LOWER zone — decorative line
        dec_line = Line(LEFT*2, RIGHT*2, color=GOLD, stroke_width=1.5)
        dec_line.move_to(UP * (ZONE_LOWER + 1.0))

        # "The Steppe" — final label
        steppe_label = safe_text("The Steppe.", font="Bebas Neue", font_size=60,
                                 color=GOLD_DIM)
        steppe_label.move_to(UP * ZONE_LOWER)

        # FOOTER zone — quiet closer
        closer = safe_text("an echo.", font="Inter", font_size=34, color=MUTED)
        closer.move_to(UP * ZONE_FOOTER)

        # ── Timing: 5.5s ──
        self.play(FadeIn(horizon), run_time=0.6); t += 0.6
        self.play(FadeIn(fire_glow), GrowFromCenter(distant_fire),
                  run_time=0.5)                                            # t=1.1
        self.wait(1.2); t += 1.2
        self.play(Create(dec_line), run_time=0.4); t += 0.4
        self.play(FadeIn(steppe_label, shift=UP*0.2), run_time=0.6); t += 0.6
        self.wait(0.5); t += 0.5
        self.play(FadeIn(closer, shift=UP*0.05), run_time=0.5); t += 0.5

        # Hold — let the silence land
        target = getattr(self.__class__, 'DURATION', 5.5)
        self.wait(max(0.1, target - t - 0.8))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3
        # Fade to black
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1,
                          stroke_width=0)
        self.play(FadeIn(black), run_time=0.4); t += 0.4


# ── Infra ─────────────────────────────────────────────────────
SCENES = [Scene1_WrongAnswer, Scene2_Contradiction, Scene3_DismissedTruth,
          Scene4_Proof, Scene5_Scale, Scene6_Punch]

def render_single_scene(idx):
    config.output_file = f"zoroaster_steppe_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    SCENES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"zoroaster_steppe_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENES):
        n = f"zoroaster_steppe_scene_{i+1}"; print(f"  Preview {n}...")
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
    audio = od / "tts_zoroaster_steppe.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="zoroaster_steppe", audio_path=str(audio))
    final = od / "zoroaster_steppe_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")

    from render_utils import run_post_render_qa
    run_post_render_qa(str(final), scene_count=6)

    from render_utils import make_short
    scene_ends = [4.5, 9.0, 14.0, 19.0, 23.5, 29.0]
    short, dur = make_short(str(final), scene_ends)
    print(f"  SHORT: {short} ({Path(short).stat().st_size/1024/1024:.1f} MB, {dur:.1f}s)")
