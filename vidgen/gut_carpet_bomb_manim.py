#!/usr/bin/env python3
"""Gut Carpet Bomb — How antibiotics destroy your microbiome permanently.

6 scenes, ~43.0s (40.0s audio + 3s hold).
Domain shapes: gut_cross_section, bacteria_dot_field, pill_shape, shockwave_ring.

VTT cues (absolute → relative):
  Scene 1 (0.0–6.5s):   0.30 your gut contains... 2.40 over a thousand... 4.20 weighs two to three
  Scene 2 (6.5–12.0s):  6.80 when you swallow... 8.60 carpet-bomb... 10.40 bounces back
  Scene 3 (12.0–18.0s): 12.40 researchers followed... 14.80 six weeks... 16.40 mostly normal
  Scene 4 (18.0–25.0s): 18.40 six months... 20.60 nine species... 23.00 different ecosystem
  Scene 5 (25.0–32.0s): 25.40 not all antibiotics... 27.60 clindamycin... 30.00 doxycycline
  Scene 6 (32.0–40.0s): 32.40 here's what makes... 34.80 seventeen courses... 37.60 five-day prescription
"""

TTS_SCRIPT = """Your gut holds a hundred trillion bacteria. A thousand species. When you swallow a broad-spectrum antibiotic, you carpet-bomb it. Researchers tracked twelve men after a four-day course. At six months, nine species were still gone. The gut didn't recover. It became a different ecosystem. American children receive seventeen antibiotic courses before age twenty. Each one strips more species. Each time, the gut recovers less. A five-day prescription reshapes what took years to build."""

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

BG = "#080A10"; GRID = "#1A2030"; SURFACE = "#15192A"
WHITE_SOFT = "#F0F0F0"; GOLD = "#FFD700"
GUT_PINK = "#EC4899"; BACTERIA_TEAL = "#14B8A6"; BACTERIA_GREEN = "#22C55E"
BACTERIA_PURPLE = "#A855F7"; BACTERIA_ORANGE = "#F97316"; BACTERIA_BLUE = "#3B82F6"
PILL_WHITE = "#E2E8F0"; PILL_RED = "#EF4444"; DANGER_RED = "#EF4444"
SHOCKWAVE_BLUE = "#60A5FA"; MUTED = "#475569"; DIM = "#334155"
RECOVER_GREEN = "#4ADE80"; DEAD_GRAY = "#374151"

# Safe zone / layout constants
SAFE_W = 8.0; SAFE_TOP = 7.2; SAFE_BOT = -6.4

# Vertical layout zones — USE THESE for all positioning
ZONE_TITLE  = 6.2    # y 5.5–7.0  — scene label pills
ZONE_UPPER  = 3.5    # y 1.5–5.5  — hero visual top portion
ZONE_MID    = 0.0    # y -1.5–1.5 — central focal point, big numbers
ZONE_LOWER  = -3.5   # y -5.5–-1.5 — supporting visuals, bars, icons
ZONE_FOOTER = -6.0   # y -6.4–-5.5 — captions, source labels


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


# ── Domain shapes ────────────────────────────────────────────

def gut_cross_section(width=7.0, height=3.0, color=GUT_PINK):
    """Simplified gut lining cross-section — wavy rectangle with villi bumps on top."""
    # Base tissue wall
    wall = Rectangle(width=width, height=height * 0.5, fill_color=color,
                     fill_opacity=0.15, stroke_color=color, stroke_width=1.5)
    wall.move_to(DOWN * height * 0.15)
    # Villi bumps along the top
    villi = VGroup()
    num_villi = 14
    for i in range(num_villi):
        x = -width * 0.45 + i * (width * 0.9 / (num_villi - 1))
        h = height * 0.25 + np.random.uniform(-0.1, 0.1) * height
        villus = RoundedRectangle(width=width * 0.04, height=h, corner_radius=width * 0.015,
                                  fill_color=color, fill_opacity=0.25, stroke_color=color,
                                  stroke_width=1)
        villus.move_to(np.array([x, height * 0.15, 0]))
        villi.add(villus)
    # Inner lumen space
    lumen = Rectangle(width=width * 0.9, height=height * 0.15, fill_color=color,
                      fill_opacity=0.05, stroke_width=0)
    lumen.move_to(UP * height * 0.35)
    return VGroup(wall, villi, lumen)

def bacteria_dot_field(count=40, colors=None, width=6.0, height=2.5):
    """Grid/scatter of colorful dots representing microbiome diversity."""
    if colors is None:
        colors = [BACTERIA_TEAL, BACTERIA_GREEN, BACTERIA_PURPLE,
                  BACTERIA_ORANGE, BACTERIA_BLUE, GUT_PINK]
    dots = VGroup()
    for i in range(count):
        x = np.random.uniform(-width / 2, width / 2)
        y = np.random.uniform(-height / 2, height / 2)
        r = np.random.uniform(0.06, 0.12)
        c = colors[i % len(colors)]
        dot = Dot(radius=r, color=c, fill_opacity=0.8)
        dot.move_to(np.array([x, y, 0]))
        dots.add(dot)
    return dots

def pill_shape(height=1.5, color_top=PILL_WHITE, color_bot=PILL_RED):
    """Simple capsule — two rounded halves."""
    w = height * 0.35
    top = RoundedRectangle(width=w, height=height * 0.5, corner_radius=height * 0.12,
                           fill_color=color_top, fill_opacity=0.9, stroke_width=0)
    top.move_to(UP * height * 0.22)
    bot = RoundedRectangle(width=w, height=height * 0.5, corner_radius=height * 0.12,
                           fill_color=color_bot, fill_opacity=0.9, stroke_width=0)
    bot.move_to(DOWN * height * 0.22)
    band = Rectangle(width=w * 1.05, height=height * 0.04, fill_color=WHITE_SOFT,
                     fill_opacity=0.3, stroke_width=0)
    return VGroup(top, bot, band)

def shockwave_ring(radius=0.5, color=SHOCKWAVE_BLUE):
    """Expanding circle for the antibiotic blast effect."""
    ring = Circle(radius=radius, stroke_color=color, stroke_width=3,
                  fill_color=color, fill_opacity=0.08)
    return ring


# ================================================================
# SCENE 1: THE HOOK (0.0–6.5s)
# Lush gut ecosystem, 100 TRILLION number, "YOUR OTHER ORGAN"
# Zones filled: TITLE, UPPER, MID, LOWER, FOOTER
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 6.5
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # TITLE zone
        pill_label = label_pill("YOUR OTHER ORGAN", color=GUT_PINK)
        pill_label.move_to(UP * ZONE_TITLE)

        # UPPER zone — giant number
        trillion = safe_text("100 TRILLION", font="Bebas Neue", font_size=140, color=BACTERIA_TEAL)
        trillion.move_to(UP * ZONE_UPPER)

        # MID zone — gut cross section as hero visual
        gut = gut_cross_section(width=7.5, height=3.0, color=GUT_PINK)
        gut.move_to(UP * ZONE_MID)

        # Bacteria field living on the gut lining (overlapping MID)
        np.random.seed(42)
        field = bacteria_dot_field(count=50, width=6.5, height=2.0)
        field.move_to(UP * (ZONE_MID + 1.0))

        # LOWER zone — species count and weight
        species = safe_text("1,000+ SPECIES", font="Bebas Neue", font_size=70, color=BACTERIA_GREEN)
        species.move_to(UP * (ZONE_LOWER + 1.0))

        weight_line = safe_text("2-3 LBS", font="Bebas Neue", font_size=80, color=GOLD)
        weight_line.move_to(UP * ZONE_LOWER)
        weight_sub = safe_text("same as your brain", font="Inter", font_size=22, color=MUTED)
        weight_sub.move_to(UP * (ZONE_LOWER - 1.0))

        # FOOTER zone
        footer = safe_text("the human microbiome", font="Inter", font_size=18, color=MUTED)
        footer.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(gut, shift=UP * 0.2), run_time=0.5); t += 0.5
        self.play(LaggedStart(*[FadeIn(d, scale=2) for d in field],
                              lag_ratio=0.02), run_time=0.8)              # t=1.7
        self.play(FadeIn(trillion, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(trillion.get_center(), color=BACTERIA_TEAL,
                        line_length=0.4, num_lines=8, run_time=0.3))      # t=2.5
        self.play(FadeIn(species, shift=UP * 0.2), run_time=0.4); t += 0.4
        self.wait(0.8); t += 0.8
        self.play(FadeIn(weight_line, scale=1.05), run_time=0.4); t += 0.4
        self.play(FadeIn(weight_sub), run_time=0.3); t += 0.3
        self.play(FadeIn(footer), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 6.5)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE BLAST (6.5–12.0s)
# Pill drops in, blue shockwave, bacteria dying
# Zones filled: TITLE, MID, LOWER, FOOTER
# ================================================================
class Scene2_Blast(Scene):
    DURATION = 5.5
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # TITLE zone
        pill_label = label_pill("CARPET BOMB", color=DANGER_RED)
        pill_label.move_to(UP * ZONE_TITLE)

        # MID zone — gut cross section backdrop
        gut = gut_cross_section(width=7.5, height=2.5, color=GUT_PINK)
        gut.move_to(UP * ZONE_MID)

        # Bacteria field around MID
        np.random.seed(99)
        field = bacteria_dot_field(count=45, width=6.5, height=2.5)
        field.move_to(UP * (ZONE_MID + 0.5))

        # Pill dropping from above
        pill = pill_shape(height=2.0, color_top=PILL_WHITE, color_bot=SHOCKWAVE_BLUE)
        pill.move_to(UP * 7)

        # Shockwave rings at MID
        wave1 = shockwave_ring(radius=0.3, color=SHOCKWAVE_BLUE)
        wave2 = shockwave_ring(radius=0.3, color=SHOCKWAVE_BLUE)
        wave3 = shockwave_ring(radius=0.3, color=SHOCKWAVE_BLUE)
        for w in [wave1, wave2, wave3]:
            w.move_to(UP * (ZONE_MID + 0.5))

        # LOWER zone — "BROAD-SPECTRUM" label
        broad = safe_text("BROAD-SPECTRUM", font="Bebas Neue", font_size=60, color=DANGER_RED)
        broad.move_to(UP * ZONE_LOWER)

        # FOOTER zone
        footer = safe_text("indiscriminate bacterial kill", font="Inter", font_size=18, color=MUTED)
        footer.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(gut, shift=UP * 0.2), run_time=0.3); t += 0.3
        self.play(LaggedStart(*[FadeIn(d, scale=2) for d in field],
                              lag_ratio=0.01), run_time=0.5)              # t=1.1

        # Pill drops to MID
        self.play(pill.animate.move_to(UP * (ZONE_MID + 0.5)), run_time=0.6); t += 0.6

        # Shockwave blast — three expanding rings
        self.play(FadeOut(pill, scale=0.5),
                  GrowFromCenter(wave1), run_time=0.3)                    # t=2.0
        self.play(wave1.animate.scale(8).set_opacity(0),
                  GrowFromCenter(wave2), run_time=0.4)                    # t=2.4
        self.play(wave2.animate.scale(8).set_opacity(0),
                  GrowFromCenter(wave3), run_time=0.4)                    # t=2.8

        # Bacteria die — turn gray and shrink
        self.play(
            *[d.animate.set_color(DEAD_GRAY).set_opacity(0.15).scale(0.3)
              for d in field],
            wave3.animate.scale(6).set_opacity(0),
            run_time=0.8,
        )                                                                   # t=3.6

        # Gut lining damaged
        self.play(gut.animate.set_opacity(0.3), run_time=0.3); t += 0.3
        self.play(FadeIn(broad, scale=1.1), run_time=0.4); t += 0.4
        self.play(Flash(broad.get_center(), color=DANGER_RED,
                        line_length=0.3, num_lines=6, run_time=0.3))      # t=4.6
        self.play(FadeIn(footer), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 5.5)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: QUICK RECOVERY? (12.0–18.0s)
# Fast-forward clock, bacteria repopulate. "2 WEEKS" myth.
# Zones filled: TITLE, UPPER, MID, LOWER, FOOTER
# ================================================================
class Scene3_QuickRecovery(Scene):
    DURATION = 6.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # TITLE zone
        pill_label = label_pill("QUICK RECOVERY?", color=RECOVER_GREEN)
        pill_label.move_to(UP * ZONE_TITLE)

        # UPPER zone — clock face
        clock_face = Circle(radius=1.5, stroke_color=WHITE_SOFT, stroke_width=2,
                            fill_color=SURFACE, fill_opacity=0.3)
        clock_face.move_to(UP * ZONE_UPPER)
        # Hour markers
        markers = VGroup()
        for h in range(12):
            angle = h * 30 * PI / 180
            m = Line(ORIGIN, UP * 0.15, color=WHITE_SOFT, stroke_width=2)
            m.move_to(clock_face.get_center() + np.array([
                np.sin(angle) * 1.3, np.cos(angle) * 1.3, 0]))
            m.rotate(-angle)
            markers.add(m)
        # Clock hand
        hand = Line(ORIGIN, UP * 1.0, color=GOLD, stroke_width=3)
        hand.move_to(clock_face.get_center(), aligned_edge=DOWN)
        clock_group = VGroup(clock_face, markers, hand)

        # MID zone — "2 WEEKS" — what people imagine
        two_weeks = safe_text("2 WEEKS", font="Bebas Neue", font_size=120, color=RECOVER_GREEN)
        two_weeks.move_to(UP * ZONE_MID)

        # Between MID and LOWER — bacteria coming back
        np.random.seed(77)
        recovering = bacteria_dot_field(count=25, width=6.0, height=1.5)
        recovering.move_to(UP * ((ZONE_MID + ZONE_LOWER) / 2))

        # Cross-out lines over "2 WEEKS"
        cross_line1 = Line(LEFT * 2.5 + UP * 0.8, RIGHT * 2.5 + DOWN * 0.2,
                           color=DANGER_RED, stroke_width=4)
        cross_line1.move_to(two_weeks.get_center())
        cross_line2 = Line(LEFT * 2.5 + DOWN * 0.2, RIGHT * 2.5 + UP * 0.8,
                           color=DANGER_RED, stroke_width=4)
        cross_line2.move_to(two_weeks.get_center())

        # LOWER zone — "MYTH"
        myth_label = safe_text("MYTH", font="Bebas Neue", font_size=70, color=DANGER_RED)
        myth_label.move_to(UP * ZONE_LOWER)

        # FOOTER zone
        footer = safe_text("what most people believe", font="Inter", font_size=18, color=MUTED)
        footer.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(clock_group), run_time=0.4); t += 0.4

        # Clock hand spins fast (fast-forward)
        self.play(hand.animate.rotate(-4 * PI, about_point=clock_face.get_center()),
                  run_time=1.0)                                            # t=1.7

        # "2 WEEKS" appears
        self.play(FadeIn(two_weeks, scale=1.1), run_time=0.4); t += 0.4

        # Bacteria slowly return
        self.play(LaggedStart(*[FadeIn(d, scale=2) for d in recovering],
                              lag_ratio=0.04), run_time=0.8)              # t=2.9
        self.wait(0.6); t += 0.6

        # Cross it out — myth
        self.play(Create(cross_line1), Create(cross_line2), run_time=0.4); t += 0.4
        self.play(FadeIn(myth_label, scale=1.2), run_time=0.4); t += 0.4
        self.play(Flash(myth_label.get_center(), color=DANGER_RED,
                        line_length=0.3, num_lines=6, run_time=0.3))      # t=4.6
        self.play(FadeIn(footer), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 6.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE TRUTH (18.0–25.0s)
# Real timeline. 6 weeks OK, 6 months still missing 9 species.
# Zones filled: TITLE, UPPER, MID, LOWER, FOOTER
# ================================================================
class Scene4_Truth(Scene):
    DURATION = 7.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # TITLE zone
        pill_label = label_pill("THE TRUTH", color=GOLD)
        pill_label.move_to(UP * ZONE_TITLE)

        # UPPER zone — timeline bar
        tl = Line(LEFT * 3.5, RIGHT * 3.5, color=MUTED, stroke_width=2)
        tl.move_to(UP * ZONE_UPPER)

        # Timeline markers
        t_start = Dot(radius=0.1, color=DANGER_RED).move_to(LEFT * 3.5 + UP * ZONE_UPPER)
        t_6wk = Dot(radius=0.1, color=RECOVER_GREEN).move_to(RIGHT * 0 + UP * ZONE_UPPER)
        t_6mo = Dot(radius=0.1, color=DANGER_RED).move_to(RIGHT * 3.5 + UP * ZONE_UPPER)

        lbl_start = safe_text("DAY 0", font="Inter", font_size=18, color=MUTED)
        lbl_start.next_to(t_start, DOWN, buff=0.2)
        lbl_6wk = safe_text("6 WEEKS", font="Inter", font_size=18, color=RECOVER_GREEN)
        lbl_6wk.next_to(t_6wk, DOWN, buff=0.2)
        lbl_6mo = safe_text("6 MONTHS", font="Inter", font_size=18, color=DANGER_RED)
        lbl_6mo.next_to(t_6mo, DOWN, buff=0.2)

        # MID zone — "LOOKS NORMAL" then "9 SPECIES"
        looks_ok = safe_text("LOOKS NORMAL", font="Bebas Neue", font_size=60, color=RECOVER_GREEN)
        looks_ok.move_to(UP * (ZONE_MID + 0.5))

        nine_gone = safe_text("9 SPECIES", font="Bebas Neue", font_size=140, color=DANGER_RED)
        nine_gone.move_to(UP * ZONE_MID)
        gone_label = safe_text("STILL GONE", font="Bebas Neue", font_size=60, color=DANGER_RED)
        gone_label.move_to(UP * (ZONE_MID - 1.5))

        # LOWER zone — missing species grid
        missing_dots = VGroup()
        for i in range(9):
            x = -3.5 + i * 0.875
            box = Square(side_length=0.6, fill_color=DEAD_GRAY, fill_opacity=0.3,
                         stroke_color=DANGER_RED, stroke_width=1.5)
            box.move_to(UP * ZONE_LOWER + RIGHT * x)
            cross = safe_text("X", font="Inter", font_size=16, color=DANGER_RED)
            cross.move_to(box)
            missing_dots.add(VGroup(box, cross))

        # Between LOWER and FOOTER
        diff_eco = safe_text("DIFFERENT ECOSYSTEM", font="Inter", font_size=26,
                             color=GOLD, weight="BOLD")
        diff_eco.move_to(UP * ((ZONE_LOWER + ZONE_FOOTER) / 2))

        # FOOTER zone
        footer = safe_text("12 subjects, 4-day course", font="Inter", font_size=18, color=MUTED)
        footer.move_to(UP * ZONE_FOOTER)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3
        self.play(Create(tl), run_time=0.4); t += 0.4
        self.play(FadeIn(t_start), FadeIn(lbl_start), run_time=0.3); t += 0.3

        # 6 weeks looks normal
        self.play(FadeIn(t_6wk), FadeIn(lbl_6wk), run_time=0.3); t += 0.3
        self.play(FadeIn(looks_ok, shift=UP * 0.2), run_time=0.4); t += 0.4
        self.wait(0.8); t += 0.8

        # But at 6 months...
        self.play(FadeOut(looks_ok, shift=UP * 0.3), run_time=0.3); t += 0.3
        self.play(FadeIn(t_6mo), FadeIn(lbl_6mo), run_time=0.3); t += 0.3

        # 9 species gone
        self.play(FadeIn(nine_gone, scale=1.15), run_time=0.5); t += 0.5
        self.play(Flash(nine_gone.get_center(), color=DANGER_RED,
                        line_length=0.5, num_lines=10, run_time=0.3))     # t=3.9
        self.play(FadeIn(gone_label, shift=UP * 0.2), run_time=0.3); t += 0.3

        # Missing species grid
        self.play(LaggedStart(*[FadeIn(d, scale=1.2) for d in missing_dots],
                              lag_ratio=0.06), run_time=0.6)              # t=4.8

        self.play(FadeIn(diff_eco, shift=UP * 0.1), run_time=0.3); t += 0.3
        self.play(FadeIn(footer), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 7.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE SCALE (25.0–32.0s)
# Bar chart: C. diff risk by antibiotic. "17 COURSES BY AGE 20"
# Zones filled: TITLE, UPPER, MID, LOWER, FOOTER
# ================================================================
class Scene5_Scale(Scene):
    DURATION = 7.0
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # TITLE zone
        pill_label = label_pill("NOT EQUAL", color=GOLD)
        pill_label.move_to(UP * ZONE_TITLE)

        # Subtitle below TITLE
        subtitle = safe_text("C. DIFF RISK", font="Inter", font_size=24,
                             color=MUTED, weight="BOLD")
        subtitle.move_to(UP * (ZONE_TITLE - 1.0))

        # Bar chart — bars grow up from FOOTER base
        chart_base_y = ZONE_FOOTER + 0.5  # y = -5.5
        bar_data = [
            ("CLINDA-\nMYCIN", 8.81, DANGER_RED),
            ("CEPHALO-\nSPORINS", 5.86, BACTERIA_ORANGE),
            ("FLUORO-\nQUINOLONES", 4.05, GOLD),
            ("DOXY-\nCYCLINE", 1.0, RECOVER_GREEN),
        ]

        bars = VGroup()
        bar_labels = VGroup()
        bar_values = VGroup()
        max_val = 8.81
        max_bar_h = 9.0  # tall bars to fill frame

        for i, (name, val, color) in enumerate(bar_data):
            x = -2.7 + i * 1.8
            h = (val / max_val) * max_bar_h
            bar = Rectangle(width=1.3, height=h, fill_color=color, fill_opacity=0.7,
                            stroke_width=0)
            bar.move_to(RIGHT * x + UP * (chart_base_y + h / 2))
            bars.add(bar)

            lbl = safe_text(name, font="Inter", font_size=16, color=WHITE_SOFT)
            lbl.move_to(RIGHT * x + UP * (chart_base_y - 0.5))
            bar_labels.add(lbl)

            val_txt = safe_text(f"{val}x", font="Bebas Neue", font_size=40, color=color)
            val_txt.next_to(bar, UP, buff=0.15)
            bar_values.add(val_txt)

        # UPPER zone — "17 COURSES" call-out
        seventeen = safe_text("17", font="Bebas Neue", font_size=120, color=DANGER_RED)
        seventeen.move_to(UP * ZONE_UPPER)
        seventeen_sub = safe_text("COURSES BY AGE 20", font="Inter", font_size=26,
                                  color=MUTED, weight="BOLD")
        seventeen_sub.move_to(UP * (ZONE_UPPER - 1.5))

        # FOOTER zone
        footer = safe_text("average American child", font="Inter", font_size=18, color=MUTED)
        footer.move_to(UP * ZONE_FOOTER)

        # Baseline
        base_line = Line(LEFT * 3.8 + UP * chart_base_y, RIGHT * 3.8 + UP * chart_base_y,
                         color=MUTED, stroke_width=1)

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(subtitle), run_time=0.2); t += 0.2
        self.play(Create(base_line), run_time=0.3); t += 0.3

        # Bars grow up
        self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.3) for b in bars],
                              lag_ratio=0.12), run_time=1.0)              # t=1.8

        # Labels and values
        self.play(LaggedStart(*[FadeIn(l) for l in bar_labels],
                              lag_ratio=0.08), run_time=0.5)              # t=2.3
        self.play(LaggedStart(*[FadeIn(v, scale=1.1) for v in bar_values],
                              lag_ratio=0.08), run_time=0.5)              # t=2.8

        # Flash the worst one
        self.play(Flash(bars[0].get_top(), color=DANGER_RED,
                        line_length=0.4, num_lines=6, run_time=0.3))      # t=3.1

        # 17 courses
        self.wait(0.4); t += 0.4
        self.play(FadeIn(seventeen, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(seventeen.get_center(), color=DANGER_RED,
                        line_length=0.5, num_lines=8, run_time=0.3))      # t=4.3
        self.play(FadeIn(seventeen_sub, shift=UP * 0.1), run_time=0.3); t += 0.3
        self.play(FadeIn(footer), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 7.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: PERMANENT LOSS (32.0–40.0s)
# Repeated courses strip species. Ecosystem degrades. Fade to black.
# Zones filled: TITLE, UPPER, MID, LOWER, FOOTER
# ================================================================
class Scene6_PermanentLoss(Scene):
    DURATION = 8.0
    def construct(self):
        self.add(gradient_bg("#0A0E18"), grid_lines(0.02))
        t = 0

        # TITLE zone
        pill_label = label_pill("PERMANENT LOSS", color=DANGER_RED)
        pill_label.move_to(UP * ZONE_TITLE)

        # UPPER zone — child stick figure
        head = Circle(radius=0.3, stroke_color=WHITE_SOFT, stroke_width=2,
                      fill_color=SURFACE, fill_opacity=0.3)
        head.move_to(UP * (ZONE_UPPER + 1.0))
        body = Line(UP * (ZONE_UPPER + 0.7), UP * (ZONE_UPPER - 0.3), color=WHITE_SOFT, stroke_width=2)
        arm_l = Line(UP * (ZONE_UPPER + 0.4), UP * ZONE_UPPER + LEFT * 0.5, color=WHITE_SOFT, stroke_width=2)
        arm_r = Line(UP * (ZONE_UPPER + 0.4), UP * ZONE_UPPER + RIGHT * 0.5, color=WHITE_SOFT, stroke_width=2)
        leg_l = Line(UP * (ZONE_UPPER - 0.3), UP * (ZONE_UPPER - 0.9) + LEFT * 0.3, color=WHITE_SOFT, stroke_width=2)
        leg_r = Line(UP * (ZONE_UPPER - 0.3), UP * (ZONE_UPPER - 0.9) + RIGHT * 0.3, color=WHITE_SOFT, stroke_width=2)
        child = VGroup(head, body, arm_l, arm_r, leg_l, leg_r)

        # MID zone — pills representing 17 courses
        pills = VGroup()
        for i in range(6):
            p = pill_shape(height=0.8, color_top=PILL_WHITE, color_bot=SHOCKWAVE_BLUE)
            p.move_to(LEFT * 2.5 + RIGHT * i * 1.0 + UP * (ZONE_MID + 0.5))
            pills.add(p)

        # LOWER zone — ecosystem degradation rows
        row_colors = [
            [BACTERIA_TEAL, BACTERIA_GREEN, BACTERIA_PURPLE, BACTERIA_ORANGE,
             BACTERIA_BLUE, GUT_PINK, BACTERIA_TEAL, BACTERIA_GREEN],
            [BACTERIA_TEAL, BACTERIA_GREEN, BACTERIA_PURPLE, BACTERIA_ORANGE,
             BACTERIA_BLUE, GUT_PINK],
            [BACTERIA_TEAL, BACTERIA_GREEN, BACTERIA_PURPLE, BACTERIA_ORANGE],
            [BACTERIA_TEAL, BACTERIA_GREEN],
            [BACTERIA_TEAL],
        ]
        row_labels_text = ["BIRTH", "AGE 5", "AGE 10", "AGE 15", "AGE 20"]
        row_groups = VGroup()

        for row_i, (colors, lbl_txt) in enumerate(zip(row_colors, row_labels_text)):
            y = ZONE_MID - 1.0 - row_i * 1.1
            row_lbl = safe_text(lbl_txt, font="Inter", font_size=18, color=MUTED)
            row_lbl.move_to(LEFT * 3.8 + UP * y)
            dots = VGroup()
            for j, c in enumerate(colors):
                dot = Dot(radius=0.12, color=c, fill_opacity=0.8)
                dot.move_to(LEFT * 1.5 + RIGHT * j * 0.5 + UP * y)
                dots.add(dot)
            row_groups.add(VGroup(row_lbl, dots))

        # FOOTER zone — "NEVER COMES BACK"
        never = safe_text("NEVER COMES BACK", font="Bebas Neue", font_size=70, color=DANGER_RED)
        never.move_to(UP * (ZONE_FOOTER + 0.5))

        footer = safe_text("years to build, days to destroy", font="Inter",
                           font_size=18, color=MUTED)
        footer.move_to(UP * (ZONE_FOOTER - 0.3))

        self.play(FadeIn(pill_label, scale=1.05), run_time=0.3); t += 0.3
        self.play(FadeIn(child, shift=DOWN * 0.2), run_time=0.4); t += 0.4

        # Pills rain down
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.3) for p in pills],
                              lag_ratio=0.1), run_time=0.6)               # t=1.3

        # Pills shrink/fade (courses taken)
        self.play(*[p.animate.scale(0.4).set_opacity(0.2) for p in pills],
                  run_time=0.5)                                            # t=1.8

        # Ecosystem rows appear one by one — each smaller
        for i, rg in enumerate(row_groups):
            self.play(FadeIn(rg, shift=RIGHT * 0.2), run_time=0.35); t += 0.35

        self.wait(0.3); t += 0.3

        # "NEVER COMES BACK"
        self.play(FadeIn(never, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(never.get_center(), color=DANGER_RED,
                        line_length=0.4, num_lines=8, run_time=0.3))      # t=5.0
        self.play(FadeIn(footer), run_time=0.3); t += 0.3

        # Hold, then fade to black
        target = getattr(self.__class__, 'DURATION', 8.0)
        self.wait(max(0.1, target - t - 0.8))
        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.2); t += 1.2


# ── Infra ─────────────────────────────────────────────────────
SCENES = [Scene1_Hook, Scene2_Blast, Scene3_QuickRecovery,
          Scene4_Truth, Scene5_Scale, Scene6_PermanentLoss]

def render_single_scene(idx):
    config.output_file = f"gut_carpet_bomb_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    SCENES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"gut_carpet_bomb_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENES):
        n = f"gut_carpet_bomb_scene_{i+1}"; print(f"  Preview {n}...")
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
    audio = od / "tts_gut_carpet_bomb.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="gut_carpet_bomb", audio_path=str(audio))
    final = od / "gut_carpet_bomb_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))
    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
    from render_utils import run_post_render_qa
    run_post_render_qa(str(final), scene_count=6)
    from render_utils import make_short
    scene_ends = [6.5, 12.0, 18.0, 25.0, 32.0, 40.0]
    short, dur = make_short(str(final), scene_ends)
    print(f"  SHORT: {short} ({Path(short).stat().st_size/1024/1024:.1f} MB, {dur:.1f}s)")
