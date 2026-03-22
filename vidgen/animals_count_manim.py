#!/usr/bin/env python3
"""Animals Can Count — Manim screenplay.

6 scenes, ~59.6s (56.6s audio + 3s hold).

VTT cues (absolute → relative):
  Scene 1 THE HOOK (0.0–7.6s = 7.60s):
    0.100 (0.10) A parrot understood zero.
    2.250 (2.25) A chimpanzee beat humans at math.
    5.090 (5.09) Honeybees can add and subtract.
  Scene 2 ALEX (7.6–19.0s = 11.40s):
    7.636 (0.04) Alex the African Grey Parrot could count to 6.
    11.011 (3.41) Ask him 'what color six?' with mixed objects, and he'd answer correctly.
    15.954 (8.35) Ask for zero, and he'd say 'none.'
  Scene 3 AYUMU (19.0–30.8s = 11.80s):
    18.954 (0.00) A chimp named Ayumu memorized the positions of digits 1 through 9.
    23.999 (5.05) They flashed for a fifth of a second.
    26.579 (7.63) He recalled them perfectly.
    28.715 (9.76) Faster than any human.
  Scene 4 THE WEIRD ONES (30.8–39.1s = 8.30s):
    30.795 (0.00) Honeybees do arithmetic.
    32.999 (2.20) Newborn chicks count from left to right.
    35.761 (4.96) Desert ants count their own steps to navigate home.
  Scene 5 THE SCALE (39.1–52.1s = 13.00s):
    39.113 (0.01) Over 1,000 species can count.
    41.886 (2.79) Insects, fish, birds, mammals.
    45.420 (6.32) Either it evolved once, billions of years ago.
    48.752 (9.65) Or it keeps evolving because counting is that important.
  Scene 6 THE PUNCH (52.1–59.6s = 7.50s):
    52.136 (0.04) Counting isn't a human invention.
    54.545 (2.45) We just gave it names.
    + 3s hold + fade to black
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """A parrot understood zero. A chimp beat humans at math. Honeybees add and subtract. Alex the African Grey counted to six and understood none. A chimp named Ayumu memorized digits flashed for a fifth of a second. Faster than any human tested. Newborn chicks count left to right. Desert ants count their own steps home. Over a thousand species can count. Counting isn't a human invention. We just gave it names."""

from manim import (
    Scene, Text, Group, VGroup, Rectangle, RoundedRectangle, Circle,
    Line, Arrow, DashedLine, Dot, Polygon, Ellipse, Square,
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

# -- Color Palette -----------------------------------------------------
BG = "#0A0A10"; SURFACE = "#12121C"; SURFACE2 = "#1A1A26"
BORDER = "#2A2A3A"; GRID = "#14141C"
PARROT_GRAY = "#8B8B8B"; PARROT_RED = "#CC3333"
CHIMP_BROWN = "#6B4226"
BEE_GOLD = "#FFD700"; BEE_BLACK = "#1A1A1A"
ANT_BROWN = "#8B5E3C"
ACCENT_CYAN = "#22CCFF"
MUTED = "#7B8DA0"; DIM = "#404050"
WHITE_SOFT = "#F0F0F0"
SAFE_W = 8.0

ZONE_TITLE  = 6.2
ZONE_UPPER  = 3.5
ZONE_MID    = 0.0
ZONE_LOWER  = -3.5
ZONE_FOOTER = -6.0


# -- Core helpers ------------------------------------------------------

def gradient_bg(c=BG, g="#0A1218"):
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

def safe_text(content, **kwargs):
    t = Text(content, **kwargs)
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    return t

def label_pill(txt, color=ACCENT_CYAN, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    p = RoundedRectangle(width=t.width+0.5, height=t.height+0.3, corner_radius=0.18,
                         fill_color=bg, fill_opacity=0.95, stroke_color=color, stroke_width=1.5).move_to(t)
    return VGroup(p, t)

def section_div(width=5, color=ACCENT_CYAN):
    l = Line(LEFT*width/2, LEFT*0.12, color=color, stroke_width=1.5)
    r = Line(RIGHT*0.12, RIGHT*width/2, color=color, stroke_width=1.5)
    d = Square(side_length=0.1, color=color, fill_color=color, fill_opacity=1).rotate(45*DEGREES)
    return VGroup(l, d, r)


# -- Domain shapes -----------------------------------------------------

def parrot_shape(height=3.0, color=PARROT_GRAY, tail_color=PARROT_RED):
    """African grey parrot silhouette -- head, beak, body, tail."""
    s = height / 3.0
    body = Ellipse(width=1.6*s, height=2.4*s, fill_color=color, fill_opacity=0.85,
                   stroke_color=color, stroke_width=1.5)
    body.move_to(DOWN * 0.2 * s)
    head = Circle(radius=0.55*s, fill_color=color, fill_opacity=0.9,
                  stroke_color=color, stroke_width=1.5)
    head.move_to(UP * 1.3 * s)
    eye = Dot(point=UP * 1.4 * s + RIGHT * 0.15 * s, radius=0.08 * s, color=BEE_GOLD)
    beak = Polygon(
        np.array([0.45*s, 1.3*s, 0]),
        np.array([0.85*s, 1.15*s, 0]),
        np.array([0.45*s, 1.05*s, 0]),
        fill_color="#333333", fill_opacity=1, stroke_width=0,
    )
    tail = Polygon(
        np.array([-0.3*s, -1.4*s, 0]),
        np.array([0.3*s, -1.4*s, 0]),
        np.array([0.15*s, -2.2*s, 0]),
        np.array([-0.15*s, -2.2*s, 0]),
        fill_color=tail_color, fill_opacity=0.9, stroke_width=0,
    )
    return VGroup(body, head, eye, beak, tail)

def chimp_hand_shape(height=2.5, color=CHIMP_BROWN):
    """Chimp hand/fist reaching for a screen -- palm + fingers from rectangles."""
    s = height / 2.5
    palm = RoundedRectangle(width=1.2*s, height=1.0*s, corner_radius=0.2*s,
                            fill_color=color, fill_opacity=0.85, stroke_color=color, stroke_width=1.5)
    palm.move_to(DOWN * 0.3 * s)
    fingers = VGroup()
    for i in range(4):
        f = RoundedRectangle(width=0.22*s, height=0.8*s, corner_radius=0.08*s,
                             fill_color=color, fill_opacity=0.85, stroke_color=color, stroke_width=1)
        x = -0.36*s + i * 0.24*s
        f.move_to(np.array([x, 0.55*s, 0]))
        fingers.add(f)
    thumb = RoundedRectangle(width=0.24*s, height=0.6*s, corner_radius=0.08*s,
                             fill_color=color, fill_opacity=0.85, stroke_color=color, stroke_width=1)
    thumb.move_to(LEFT * 0.72*s + DOWN * 0.1*s)
    thumb.rotate(-30 * DEGREES)
    return VGroup(palm, fingers, thumb)

def honeybee_shape(height=1.5, body_color=BEE_GOLD, stripe_color=BEE_BLACK):
    """Bee body + wings + stripes from ellipses."""
    s = height / 1.5
    body = Ellipse(width=1.4*s, height=0.7*s, fill_color=body_color, fill_opacity=0.9,
                   stroke_color=body_color, stroke_width=1.5)
    stripes = VGroup()
    for i in range(3):
        stripe = Rectangle(width=0.18*s, height=0.65*s, fill_color=stripe_color,
                           fill_opacity=0.8, stroke_width=0)
        stripe.move_to(LEFT * 0.25*s + RIGHT * i * 0.25*s)
        stripes.add(stripe)
    head = Circle(radius=0.25*s, fill_color=body_color, fill_opacity=0.9,
                  stroke_color=body_color, stroke_width=1)
    head.move_to(RIGHT * 0.9*s)
    wing1 = Ellipse(width=0.7*s, height=0.35*s, fill_color=WHITE_SOFT, fill_opacity=0.25,
                    stroke_color=WHITE_SOFT, stroke_width=0.8)
    wing1.move_to(UP * 0.5*s + LEFT * 0.1*s).rotate(15*DEGREES)
    wing2 = Ellipse(width=0.5*s, height=0.28*s, fill_color=WHITE_SOFT, fill_opacity=0.2,
                    stroke_color=WHITE_SOFT, stroke_width=0.8)
    wing2.move_to(UP * 0.4*s + RIGHT * 0.3*s).rotate(-10*DEGREES)
    stinger = Polygon(
        np.array([-0.7*s, 0.06*s, 0]),
        np.array([-0.7*s, -0.06*s, 0]),
        np.array([-0.95*s, 0, 0]),
        fill_color=stripe_color, fill_opacity=1, stroke_width=0,
    )
    return VGroup(body, stripes, head, wing1, wing2, stinger)

def ant_shape(height=1.0, color=ANT_BROWN):
    """Desert ant with body segments + legs from lines."""
    s = height / 1.0
    head = Circle(radius=0.15*s, fill_color=color, fill_opacity=0.9, stroke_width=0)
    head.move_to(RIGHT * 0.45*s)
    thorax = Ellipse(width=0.3*s, height=0.2*s, fill_color=color, fill_opacity=0.9, stroke_width=0)
    thorax.move_to(RIGHT * 0.15*s)
    abdomen = Ellipse(width=0.45*s, height=0.3*s, fill_color=color, fill_opacity=0.9, stroke_width=0)
    abdomen.move_to(LEFT * 0.2*s)
    legs = VGroup()
    for i in range(3):
        x = -0.05*s + i * 0.15*s
        l1 = Line(np.array([x, 0, 0]), np.array([x - 0.2*s, -0.3*s, 0]),
                  color=color, stroke_width=1.5*s)
        l2 = Line(np.array([x, 0, 0]), np.array([x + 0.2*s, -0.3*s, 0]),
                  color=color, stroke_width=1.5*s)
        legs.add(l1, l2)
    a1 = Line(np.array([0.5*s, 0.1*s, 0]), np.array([0.7*s, 0.3*s, 0]),
              color=color, stroke_width=1.2*s)
    a2 = Line(np.array([0.5*s, 0.1*s, 0]), np.array([0.65*s, 0.35*s, 0]),
              color=color, stroke_width=1.2*s)
    return VGroup(abdomen, thorax, head, legs, a1, a2)

def chick_shape(height=1.0, color="#FFEE88"):
    """Simple newborn chick silhouette."""
    s = height / 1.0
    body = Ellipse(width=0.6*s, height=0.5*s, fill_color=color, fill_opacity=0.9, stroke_width=0)
    head = Circle(radius=0.2*s, fill_color=color, fill_opacity=0.9, stroke_width=0)
    head.move_to(UP * 0.35*s + RIGHT * 0.1*s)
    beak = Polygon(
        np.array([0.3*s, 0.35*s, 0]),
        np.array([0.5*s, 0.32*s, 0]),
        np.array([0.3*s, 0.28*s, 0]),
        fill_color="#FF8800", fill_opacity=1, stroke_width=0,
    )
    eye = Dot(point=UP * 0.38*s + RIGHT * 0.15*s, radius=0.04*s, color=BEE_BLACK)
    legs = VGroup(
        Line(DOWN*0.22*s + LEFT*0.08*s, DOWN*0.42*s + LEFT*0.12*s, color="#FF8800", stroke_width=1.5),
        Line(DOWN*0.22*s + RIGHT*0.08*s, DOWN*0.42*s + RIGHT*0.12*s, color="#FF8800", stroke_width=1.5),
    )
    return VGroup(body, head, beak, eye, legs)

def fish_shape(height=0.8, color=ACCENT_CYAN):
    """Simple fish silhouette."""
    s = height / 0.8
    body = Ellipse(width=0.8*s, height=0.4*s, fill_color=color, fill_opacity=0.8, stroke_width=0)
    tail = Polygon(
        np.array([-0.4*s, 0, 0]),
        np.array([-0.7*s, 0.2*s, 0]),
        np.array([-0.7*s, -0.2*s, 0]),
        fill_color=color, fill_opacity=0.7, stroke_width=0,
    )
    eye = Dot(point=RIGHT * 0.15*s + UP * 0.05*s, radius=0.04*s, color=WHITE_SOFT)
    return VGroup(body, tail, eye)

def mammal_shape(height=0.8, color=CHIMP_BROWN):
    """Simple quadruped mammal silhouette."""
    s = height / 0.8
    body = Ellipse(width=0.8*s, height=0.4*s, fill_color=color, fill_opacity=0.8, stroke_width=0)
    head = Circle(radius=0.18*s, fill_color=color, fill_opacity=0.85, stroke_width=0)
    head.move_to(RIGHT * 0.45*s + UP * 0.1*s)
    legs = VGroup()
    for x in [-0.2*s, 0.2*s]:
        legs.add(Line(np.array([x, -0.18*s, 0]), np.array([x - 0.05*s, -0.45*s, 0]),
                      color=color, stroke_width=2))
        legs.add(Line(np.array([x + 0.1*s, -0.18*s, 0]), np.array([x + 0.15*s, -0.45*s, 0]),
                      color=color, stroke_width=2))
    return VGroup(body, head, legs)


# ================================================================
# SCENE 1: THE HOOK (0.0-7.6s = 7.60s)
# Visual: Three domain shapes appear in sequence -- parrot, chimp hand, bee
# Zones: TITLE(pill) UPPER(parrot+label) MID(chimp+label) LOWER(bee+label) FOOTER(div)
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 7.6
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        pill = label_pill("ANIMALS CAN COUNT", color=ACCENT_CYAN, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # Parrot at UPPER
        parrot = parrot_shape(2.5, PARROT_GRAY, PARROT_RED)
        parrot.move_to(UP * ZONE_UPPER)
        p_label = safe_text("ZERO", font="Bebas Neue", font_size=60, color=PARROT_GRAY)
        p_label.move_to(UP * 1.8)

        # Chimp hand at MID
        chimp = chimp_hand_shape(2.0, CHIMP_BROWN)
        chimp.move_to(UP * ZONE_MID)
        c_label = safe_text("MATH", font="Bebas Neue", font_size=60, color=CHIMP_BROWN)
        c_label.move_to(DOWN * 1.5)

        # Bee at LOWER
        bee = honeybee_shape(2.5, BEE_GOLD, BEE_BLACK)
        bee.move_to(DOWN * 3.0)
        b_label = safe_text("ADD + SUBTRACT", font="Bebas Neue", font_size=50, color=BEE_GOLD)
        b_label.move_to(DOWN * 4.8)

        div = section_div(5, ACCENT_CYAN).move_to(DOWN * ZONE_FOOTER)

        # -- Timing: 7.60s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.10: "A parrot understood zero."
        self.play(GrowFromCenter(parrot), run_time=0.6); t += 0.6
        self.play(FadeIn(p_label, shift=UP*0.15), run_time=0.4); t += 0.4
        # Parrot bobs gently
        self.play(parrot.animate.shift(UP * 0.15), run_time=0.35); t += 0.35
        self.play(parrot.animate.shift(DOWN * 0.15), run_time=0.35); t += 0.35

        # VTT 2.25: "A chimpanzee beat humans at math."
        self.play(GrowFromCenter(chimp), run_time=0.5); t += 0.5
        self.play(FadeIn(c_label, shift=LEFT*0.15), run_time=0.4); t += 0.4
        # Chimp hand reaches up slightly
        self.play(chimp.animate.shift(UP * 0.2), run_time=0.3); t += 0.3
        self.wait(1.6); t += 1.6

        # VTT 5.09: "Honeybees can add and subtract."
        self.play(GrowFromCenter(bee), run_time=0.5); t += 0.5
        self.play(FadeIn(b_label, shift=UP*0.15), run_time=0.4); t += 0.4
        # Bee wing flutter -- quick left-right shimmer
        self.play(bee.animate.shift(RIGHT * 0.12), run_time=0.12); t += 0.12
        self.play(bee.animate.shift(LEFT * 0.24), run_time=0.12); t += 0.12
        self.play(bee.animate.shift(RIGHT * 0.12), run_time=0.12); t += 0.12
        self.play(Create(div), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 7.6)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: ALEX (7.6-19.0s = 11.40s)
# Visual: Large parrot at MID. Numbers 1-6 around it. 'NONE' flash at LOWER.
# Zones: TITLE(pill) UPPER(numbers arc) MID(parrot) LOWER(NONE flash) FOOTER(label)
# ================================================================
class Scene2_Alex(Scene):
    DURATION = 11.4
    def construct(self):
        self.add(gradient_bg("#080A0C"), grid_lines(0.03))
        t = 0

        pill = label_pill("ALEX", color=PARROT_GRAY, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # Large parrot centered at MID-upper
        parrot = parrot_shape(4.0, PARROT_GRAY, PARROT_RED)
        parrot.move_to(UP * 1.5)

        # Numbers 1-6 arranged in an arc around parrot
        numbers = VGroup()
        num_positions = [
            (LEFT*2.8 + UP*4.5), (LEFT*0.5 + UP*5.2), (RIGHT*2.5 + UP*4.8),
            (LEFT*3.2 + UP*2.0), (RIGHT*3.2 + UP*2.0), (RIGHT*0.5 + UP*5.0),
        ]
        for i, pos in enumerate(num_positions):
            n = safe_text(str(i+1), font="Bebas Neue", font_size=70, color=ACCENT_CYAN)
            n.move_to(pos)
            numbers.add(n)

        # Color objects -- small colored dots representing objects Alex sorted
        colored_dots = VGroup()
        colors = ["#FF4444", "#44FF44", "#4444FF", "#FFFF44", "#FF44FF"]
        for i, col in enumerate(colors):
            d = Circle(radius=0.22, fill_color=col, fill_opacity=0.8, stroke_width=0)
            d.move_to(LEFT * 2 + RIGHT * i * 1.0 + DOWN * 1.2)
            colored_dots.add(d)

        answer_label = safe_text("COLOR SIX?", font="Bebas Neue", font_size=55, color=MUTED)
        answer_label.move_to(DOWN * 2.2)

        div = section_div(5, PARROT_GRAY).move_to(DOWN * 3.0)

        # NONE -- the zero concept, big and gold at LOWER
        none_text = safe_text("NONE.", font="Bebas Neue", font_size=130, color=BEE_GOLD)
        none_text.move_to(DOWN * 4.0)

        # Glow ring behind NONE for emphasis
        none_glow = Circle(radius=2.0, fill_color=BEE_GOLD, fill_opacity=0.04, stroke_width=0)
        none_glow.move_to(DOWN * 4.0)

        footer_label = safe_text("UNDERSTOOD ZERO", font="Inter", font_size=26,
                                 color=MUTED, weight="BOLD")
        footer_label.move_to(DOWN * ZONE_FOOTER)

        # -- Timing: 11.40s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.04: "Alex the African Grey Parrot could count to 6."
        self.play(GrowFromCenter(parrot), run_time=0.8); t += 0.8
        self.play(LaggedStart(*[FadeIn(n, scale=1.3) for n in numbers],
                              lag_ratio=0.1), run_time=1.0)                # t=2.1
        self.wait(1.0); t += 1.0

        # VTT 3.41: "Ask him 'what color six?' with mixed objects"
        self.play(LaggedStart(*[FadeIn(d, scale=0.8) for d in colored_dots],
                              lag_ratio=0.08), run_time=0.6)               # t=3.7
        self.play(FadeIn(answer_label, shift=UP*0.15), run_time=0.5); t += 0.5
        # Flash the number 6 and pulse it
        self.play(Flash(numbers[5].get_center(), color=ACCENT_CYAN,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=4.5
        self.play(numbers[5].animate.scale(1.4), run_time=0.2); t += 0.2
        self.play(numbers[5].animate.scale(1/1.4), run_time=0.2); t += 0.2
        self.wait(2.8); t += 2.8

        # VTT 8.35: "Ask for zero, and he'd say 'none.'"
        # Fade out numbers + dots to clear space for NONE reveal
        self.play(FadeOut(colored_dots), FadeOut(answer_label),
                  *[n.animate.set_opacity(0.2) for n in numbers],
                  run_time=0.3)                                             # t=8.0
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(none_glow), FadeIn(none_text, scale=1.3),
                  run_time=0.7)                                             # t=9.0
        self.play(Flash(none_text.get_center(), color=BEE_GOLD,
                        line_length=0.5, num_lines=10, run_time=0.4))      # t=9.4
        # Pulse the NONE text
        self.play(none_text.animate.scale(1.08), run_time=0.25); t += 0.25
        self.play(none_text.animate.scale(1/1.08), run_time=0.25); t += 0.25
        self.play(FadeIn(footer_label, shift=UP*0.05), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 11.4)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: AYUMU (19.0-30.8s = 11.80s)
# Visual: Screen grid with digits, flash/disappear, chimp hand taps, speed label
# Zones: TITLE(pill) UPPER(screen grid) MID(chimp hand) LOWER(FASTER text) FOOTER(label)
# ================================================================
class Scene3_Ayumu(Scene):
    DURATION = 11.8
    def construct(self):
        self.add(gradient_bg("#080808"), grid_lines(0.03))
        t = 0

        pill = label_pill("AYUMU", color=CHIMP_BROWN, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # Screen -- rounded rectangle at UPPER
        screen = RoundedRectangle(width=6, height=5.5, corner_radius=0.3,
                                  fill_color="#111118", fill_opacity=0.95,
                                  stroke_color="#333355", stroke_width=2)
        screen.move_to(UP * 2.8)

        # 3x3 grid of digits 1-9 inside screen
        digits = VGroup()
        digit_positions = []
        np.random.seed(7)
        grid_vals = list(range(1, 10))
        np.random.shuffle(grid_vals)
        for row in range(3):
            for col in range(3):
                idx = row * 3 + col
                x = -1.6 + col * 1.6 + screen.get_center()[0]
                y = 1.6 - row * 1.6 + screen.get_center()[1]
                d = safe_text(str(grid_vals[idx]), font="Bebas Neue", font_size=65,
                              color=ACCENT_CYAN)
                d.move_to(np.array([x, y, 0]))
                digits.add(d)
                digit_positions.append(np.array([x, y, 0]))

        # Blank placeholders (white squares) after digits disappear
        blanks = VGroup()
        for pos in digit_positions:
            sq = Square(side_length=0.5, fill_color="#222233", fill_opacity=0.6,
                        stroke_color="#444466", stroke_width=1)
            sq.move_to(pos)
            blanks.add(sq)

        # Flash timing label
        flash_label = safe_text("0.2 SEC", font="Bebas Neue", font_size=50, color=MUTED)
        flash_label.move_to(UP * (ZONE_MID - 0.3))

        # Chimp hand at MID reaching toward screen
        chimp = chimp_hand_shape(2.5, CHIMP_BROWN)
        chimp.move_to(DOWN * 0.5)

        # Speed text at ZONE_LOWER -- big and red
        faster = safe_text("FASTER THAN", font="Bebas Neue", font_size=85, color=WHITE_SOFT)
        faster.move_to(DOWN * 2.8)
        any_human = safe_text("ANY HUMAN.", font="Bebas Neue", font_size=95, color="#FF4444")
        any_human.move_to(DOWN * 4.0)

        div = section_div(5, CHIMP_BROWN).move_to(DOWN * 5.0)

        footer = safe_text("PERFECT RECALL", font="Inter", font_size=26,
                           color=MUTED, weight="BOLD")
        footer.move_to(DOWN * ZONE_FOOTER)

        # -- Timing: 11.80s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.00: "A chimp named Ayumu memorized the positions of digits 1 through 9."
        self.play(FadeIn(screen, scale=0.95), run_time=0.5); t += 0.5
        self.play(LaggedStart(*[FadeIn(d, scale=1.1) for d in digits],
                              lag_ratio=0.06), run_time=0.8)               # t=1.6
        self.wait(3.1); t += 3.1

        # VTT 5.05: "They flashed for a fifth of a second." -- digits vanish
        self.play(FadeIn(flash_label, shift=UP*0.1), run_time=0.3); t += 0.3
        self.wait(0.3); t += 0.3
        # Screen flashes white then digits become blanks
        screen_flash = Rectangle(width=5.6, height=5.1, fill_color=WHITE,
                                 fill_opacity=0.15, stroke_width=0).move_to(screen)
        self.play(FadeIn(screen_flash, run_time=0.1)); t += 0.1
        self.play(FadeOut(screen_flash), FadeOut(digits), run_time=0.2); t += 0.2
        self.play(LaggedStart(*[FadeIn(b, scale=0.9) for b in blanks],
                              lag_ratio=0.04), run_time=0.4)               # t=6.0

        # VTT 7.63: "He recalled them perfectly." -- chimp hand reaches up
        self.play(GrowFromCenter(chimp), run_time=0.5); t += 0.5
        self.play(chimp.animate.shift(UP * 0.3), run_time=0.3); t += 0.3
        # Blanks light up in sequence as chimp "taps" them
        for i, b in enumerate(blanks[:5]):
            self.play(b.animate.set_fill(ACCENT_CYAN, opacity=0.5),
                      run_time=0.1)                                        # t=6.9-7.4
        self.wait(1.6); t += 1.6

        # VTT 9.76: "Faster than any human."
        self.play(FadeIn(faster, scale=1.1), run_time=0.5); t += 0.5
        self.play(FadeIn(any_human, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(any_human.get_center(), color="#FF4444",
                        line_length=0.5, num_lines=10, run_time=0.4))     # t=10.4
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(footer, shift=UP*0.05), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 11.8)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE WEIRD ONES (30.8-39.1s = 8.30s)
# Visual: Three creatures stacked -- bee+arithmetic, chick+L->R, ant+path
# Zones: TITLE(pill) UPPER(bee+math) MID(chick+arrow) LOWER(ant+path) FOOTER(div)
# ================================================================
class Scene4_WeirdOnes(Scene):
    DURATION = 8.3
    def construct(self):
        self.add(gradient_bg("#0A0A08"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE WEIRD ONES", color=BEE_GOLD, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # -- UPPER: Bee doing arithmetic --
        bee = honeybee_shape(2.0, BEE_GOLD, BEE_BLACK)
        bee.move_to(UP * 4.0 + LEFT * 1.5)
        # Math symbols appear sequentially
        num2 = safe_text("2", font="Bebas Neue", font_size=70, color=BEE_GOLD)
        num2.move_to(UP * 4.0 + RIGHT * 0.2)
        plus_sign = safe_text("+", font="Bebas Neue", font_size=70, color=BEE_GOLD)
        plus_sign.move_to(UP * 4.0 + RIGHT * 1.0)
        num3 = safe_text("3", font="Bebas Neue", font_size=70, color=BEE_GOLD)
        num3.move_to(UP * 4.0 + RIGHT * 1.8)
        equals_sign = safe_text("= 5", font="Bebas Neue", font_size=70, color=BEE_GOLD)
        equals_sign.move_to(UP * 4.0 + RIGHT * 3.0)
        bee_label = safe_text("ARITHMETIC", font="Bebas Neue", font_size=40, color=BEE_GOLD)
        bee_label.move_to(UP * 2.5)

        # -- MID: Chick counting left to right --
        chicks = VGroup()
        for i in range(4):
            ch = chick_shape(0.8, "#FFEE88")
            ch.move_to(LEFT * 2.0 + RIGHT * i * 1.3 + UP * 0.3)
            chicks.add(ch)
        # Number labels under each chick
        chick_nums = VGroup()
        for i in range(4):
            cn = safe_text(str(i+1), font="Inter", font_size=24, color=ACCENT_CYAN)
            cn.move_to(LEFT * 2.0 + RIGHT * i * 1.3 + DOWN * 0.4)
            chick_nums.add(cn)
        lr_arrow = Arrow(LEFT * 2.5, RIGHT * 2.5, color=ACCENT_CYAN, stroke_width=3,
                         buff=0.1)
        lr_arrow.move_to(DOWN * 1.0)
        chick_label = safe_text("LEFT TO RIGHT", font="Bebas Neue", font_size=40, color=ACCENT_CYAN)
        chick_label.move_to(DOWN * 1.8)

        # -- LOWER: Ant with animated dashed path home --
        ant = ant_shape(2.0, ANT_BROWN)
        ant.move_to(DOWN * ZONE_LOWER + LEFT * 2.5)
        # Step count dots along the path
        step_dots = VGroup()
        for i in range(8):
            sd = Dot(point=np.array([-1.5 + i * 0.65, -3.5, 0]),
                     radius=0.06, color=ANT_BROWN).set_opacity(0.6)
            step_dots.add(sd)
        # Home marker -- triangle house shape
        home = Polygon(
            np.array([2.8, -2.8, 0]),
            np.array([3.6, -2.8, 0]),
            np.array([3.2, -2.3, 0]),
            fill_color=ANT_BROWN, fill_opacity=0.7, stroke_color=ANT_BROWN, stroke_width=1.5,
        )
        home_base = Rectangle(width=0.7, height=0.4, fill_color=ANT_BROWN, fill_opacity=0.5,
                               stroke_width=0).move_to(DOWN * 3.0 + RIGHT * 3.2)
        home_label = safe_text("HOME", font="Inter", font_size=28, color=ANT_BROWN, weight="BOLD")
        home_label.move_to(DOWN * 2.2 + RIGHT * 3.2)
        ant_label = safe_text("COUNT THEIR STEPS", font="Bebas Neue", font_size=45, color=ANT_BROWN)
        ant_label.move_to(DOWN * 5.0)

        div = section_div(5, BEE_GOLD).move_to(DOWN * ZONE_FOOTER)

        # -- Timing: 8.30s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.00: "Honeybees do arithmetic."
        self.play(GrowFromCenter(bee), run_time=0.5); t += 0.5
        self.play(FadeIn(num2, scale=1.2), run_time=0.15); t += 0.15
        self.play(FadeIn(plus_sign, scale=1.2), run_time=0.15); t += 0.15
        self.play(FadeIn(num3, scale=1.2), run_time=0.15); t += 0.15
        self.play(FadeIn(equals_sign, scale=1.3), run_time=0.25); t += 0.25
        self.play(FadeIn(bee_label, shift=UP*0.1), run_time=0.3); t += 0.3
        self.wait(0.2); t += 0.2

        # VTT 2.20: "Newborn chicks count from left to right."
        self.play(LaggedStart(*[FadeIn(ch, scale=0.9) for ch in chicks],
                              lag_ratio=0.1), run_time=0.6)                # t=2.6
        self.play(LaggedStart(*[FadeIn(cn, shift=UP*0.1) for cn in chick_nums],
                              lag_ratio=0.1), run_time=0.4)                # t=3.0
        self.play(GrowArrow(lr_arrow), run_time=0.4); t += 0.4
        self.play(FadeIn(chick_label, shift=UP*0.1), run_time=0.3); t += 0.3
        self.wait(1.0); t += 1.0

        # VTT 4.96: "Desert ants count their own steps to navigate home."
        self.play(GrowFromCenter(ant), run_time=0.4); t += 0.4
        # Animate step dots appearing one by one (ant counting steps)
        self.play(LaggedStart(*[FadeIn(sd, scale=1.5) for sd in step_dots],
                              lag_ratio=0.08), run_time=0.6)               # t=5.7
        self.play(FadeIn(home, scale=1.1), FadeIn(home_base),
                  FadeIn(home_label, shift=DOWN*0.1), run_time=0.4)       # t=6.1
        self.play(FadeIn(ant_label, shift=UP*0.1), run_time=0.3); t += 0.3
        self.play(Create(div), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 8.3)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE SCALE (39.1-52.1s = 13.00s)
# Visual: Big 1000+ number, creature silhouettes, evolution timeline
# Zones: TITLE(pill) UPPER(1000+) MID(creature silhouettes) LOWER(evolution) FOOTER(label)
# ================================================================
class Scene5_Scale(Scene):
    DURATION = 13.0
    def construct(self):
        self.add(gradient_bg("#080A10"), grid_lines(0.03))
        t = 0

        pill = label_pill("THE SCALE", color=ACCENT_CYAN, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # Big number at UPPER
        thousand = safe_text("1,000+", font="Bebas Neue", font_size=160, color=ACCENT_CYAN)
        thousand.move_to(UP * ZONE_UPPER)
        species_lbl = safe_text("SPECIES CAN COUNT", font="Inter", font_size=30,
                                color=WHITE_SOFT, weight="BOLD")
        species_lbl.move_to(UP * 2.0)

        div1 = section_div(5, ACCENT_CYAN).move_to(UP * 1.2)

        # Four creature silhouettes at MID with labels
        insect = honeybee_shape(1.2, BEE_GOLD, BEE_BLACK)
        insect.move_to(LEFT * 2.8 + UP * ZONE_MID)
        insect_lbl = safe_text("INSECTS", font="Inter", font_size=20, color=BEE_GOLD, weight="BOLD")
        insect_lbl.move_to(LEFT * 2.8 + DOWN * 1.0)

        fish = fish_shape(1.0, ACCENT_CYAN)
        fish.move_to(LEFT * 0.8 + UP * ZONE_MID)
        fish_lbl = safe_text("FISH", font="Inter", font_size=20, color=ACCENT_CYAN, weight="BOLD")
        fish_lbl.move_to(LEFT * 0.8 + DOWN * 1.0)

        bird = parrot_shape(1.5, PARROT_GRAY, PARROT_RED)
        bird.move_to(RIGHT * 1.2 + UP * ZONE_MID)
        bird_lbl = safe_text("BIRDS", font="Inter", font_size=20, color=PARROT_GRAY, weight="BOLD")
        bird_lbl.move_to(RIGHT * 1.2 + DOWN * 1.0)

        mammal = mammal_shape(1.0, CHIMP_BROWN)
        mammal.move_to(RIGHT * 3.2 + UP * ZONE_MID)
        mammal_lbl = safe_text("MAMMALS", font="Inter", font_size=20, color=CHIMP_BROWN, weight="BOLD")
        mammal_lbl.move_to(RIGHT * 3.2 + DOWN * 1.0)

        creatures = VGroup(insect, fish, bird, mammal)
        creature_labels = VGroup(insect_lbl, fish_lbl, bird_lbl, mammal_lbl)

        div2 = section_div(5, MUTED).move_to(DOWN * 1.8)

        # Evolution timeline at LOWER
        tl = Line(LEFT * 3.5 + DOWN * 2.8, RIGHT * 3.5 + DOWN * 2.8,
                  color=MUTED, stroke_width=2)
        # Time markers
        time_dots = VGroup()
        for i in range(4):
            x = -3.5 + i * (7.0 / 3)
            d = Dot(point=np.array([x, -2.8, 0]), radius=0.08, color=ACCENT_CYAN)
            time_dots.add(d)

        evo_label1 = safe_text("EVOLVED ONCE?", font="Bebas Neue", font_size=55, color=MUTED)
        evo_label1.move_to(DOWN * 3.8)

        evo_label2 = safe_text("OR KEEPS EVOLVING.", font="Bebas Neue", font_size=55, color=ACCENT_CYAN)
        evo_label2.move_to(DOWN * 3.8)

        important = safe_text("COUNTING IS THAT IMPORTANT.", font="Bebas Neue",
                              font_size=48, color=BEE_GOLD)
        important.move_to(DOWN * 5.0)

        footer = safe_text("UNIVERSAL ABILITY", font="Inter", font_size=24,
                           color=MUTED, weight="BOLD")
        footer.move_to(DOWN * ZONE_FOOTER)

        # -- Timing: 13.00s --
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.01: "Over 1,000 species can count."
        self.play(FadeIn(thousand, scale=1.3), run_time=0.7); t += 0.7
        self.play(Flash(thousand.get_center(), color=ACCENT_CYAN,
                        line_length=0.6, num_lines=12, run_time=0.3))      # t=1.3
        self.play(FadeIn(species_lbl, shift=UP*0.05), run_time=0.4); t += 0.4
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.wait(0.5); t += 0.5

        # VTT 2.79: "Insects, fish, birds, mammals."
        self.play(LaggedStart(*[GrowFromCenter(c) for c in creatures],
                              lag_ratio=0.15), run_time=1.2)               # t=3.7
        self.play(LaggedStart(*[FadeIn(l, shift=UP*0.05) for l in creature_labels],
                              lag_ratio=0.1), run_time=0.8)                # t=4.5
        # Gentle float on creatures
        self.play(creatures.animate.shift(UP * 0.12), run_time=0.5); t += 0.5
        self.play(creatures.animate.shift(DOWN * 0.12), run_time=0.5); t += 0.5
        self.wait(0.5); t += 0.5

        # VTT 6.32: "Either it evolved once, billions of years ago."
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.play(Create(tl), run_time=0.5); t += 0.5
        self.play(LaggedStart(*[FadeIn(d, scale=1.2) for d in time_dots],
                              lag_ratio=0.1), run_time=0.4)                # t=7.2
        self.play(FadeIn(evo_label1, shift=UP*0.1), run_time=0.5); t += 0.5
        self.wait(1.8); t += 1.8

        # VTT 9.65: "Or it keeps evolving because counting is that important."
        self.play(FadeOut(evo_label1, run_time=0.3)); t += 0.3
        self.play(FadeIn(evo_label2, scale=1.1), run_time=0.5); t += 0.5
        self.play(FadeIn(important, scale=1.05), run_time=0.6); t += 0.6
        self.play(Flash(important.get_center(), color=BEE_GOLD,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=11.2
        self.play(FadeIn(footer, shift=UP*0.05), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 13.0)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE PUNCH (52.1-59.6s = 7.50s)
# Visual: Cinematic letterbox. Ghost parrot. Big text centered.
# Zones: TITLE(div) MID(NOT AN INVENTION) LOWER(WE JUST GAVE IT NAMES) FOOTER(div)
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 7.5
    def construct(self):
        self.add(gradient_bg("#050508"), grid_lines(0.02))
        t = 0

        # Cinematic letterbox bars
        bh = 0.8
        top_bar = Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                            stroke_width=0).move_to(UP * (8 - bh/2))
        bot_bar = Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                            stroke_width=0).move_to(DOWN * (8 - bh/2))
        self.add(top_bar, bot_bar)

        # Ghost parrot -- barely visible watermark
        ghost = parrot_shape(5, PARROT_GRAY, PARROT_RED)
        ghost.move_to(DOWN * 1)
        ghost.set_opacity(0.04)
        self.add(ghost)

        div1 = section_div(4, ACCENT_CYAN).move_to(UP * 2.0)

        # "NOT AN INVENTION." at MID
        line1 = safe_text("NOT AN", font="Bebas Neue", font_size=90, color=WHITE_SOFT)
        line1.move_to(UP * 0.5)
        line2 = safe_text("INVENTION.", font="Bebas Neue", font_size=100, color=ACCENT_CYAN)
        line2.move_to(DOWN * 1.0)

        div2 = section_div(4, MUTED).move_to(DOWN * 2.3)

        # "WE JUST GAVE IT NAMES." at LOWER
        names_text = safe_text("WE JUST GAVE IT NAMES.", font="Bebas Neue",
                               font_size=60, color=BEE_GOLD)
        names_text.move_to(DOWN * ZONE_LOWER)

        glow = Circle(radius=2.5, fill_color=ACCENT_CYAN, fill_opacity=0.04, stroke_width=0)
        glow.move_to(line2)

        footer = section_div(3, MUTED).move_to(DOWN * 5.0)

        # Subtle creature silhouettes flanking the final text
        ghost_bee = honeybee_shape(1.0, BEE_GOLD, BEE_BLACK)
        ghost_bee.move_to(LEFT * 3.0 + DOWN * 5.5).set_opacity(0.08)
        ghost_chimp = chimp_hand_shape(0.8, CHIMP_BROWN)
        ghost_chimp.move_to(RIGHT * 3.0 + DOWN * 5.5).set_opacity(0.08)

        # -- Timing: 7.50s --
        # VTT 0.04: "Counting isn't a human invention."
        self.play(Create(div1), run_time=0.3); t += 0.3
        self.play(FadeIn(line1, shift=UP*0.1), run_time=0.6); t += 0.6
        self.play(FadeIn(glow), FadeIn(line2, scale=1.1), run_time=0.7); t += 0.7
        self.play(Flash(line2.get_center(), color=ACCENT_CYAN,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=1.9

        # VTT 2.45: "We just gave it names."
        self.play(Create(div2), run_time=0.3); t += 0.3
        self.wait(0.3); t += 0.3
        self.play(FadeIn(names_text, scale=1.05), run_time=0.6); t += 0.6
        self.play(Flash(names_text.get_center(), color=BEE_GOLD,
                        line_length=0.3, num_lines=6, run_time=0.3))       # t=3.4
        self.play(Create(footer), run_time=0.3); t += 0.3
        # Fade in ghost creatures
        self.play(FadeIn(ghost_bee), FadeIn(ghost_chimp), run_time=0.3); t += 0.3

        # 3s hold + fade to black
        target = getattr(self.__class__, 'DURATION', 7.5)
        self.wait(max(0.1, target - t - 0.8))
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5


# -- Infra -------------------------------------------------------------
def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_Alex, Scene3_Ayumu,
          Scene4_WeirdOnes, Scene5_Scale, Scene6_Punch]
    config.output_file = f"animals_count_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"animals_count_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

if __name__ == "__main__":
    import time, gc
    od = Path(__file__).parent
    if "--scene" in sys.argv:
        timings_json = os.environ.get("TKK_SCENE_TIMINGS")
        if timings_json:
            _idx = int(sys.argv[sys.argv.index("--scene")+1])
            _classes = sorted([v for k,v in globals().items() if k.startswith("Scene") and len(k) > 5 and k[5].isdigit() and isinstance(v, type)], key=lambda c: c.__name__); _classes[_idx].DURATION = json.loads(timings_json)[_idx]
        render_single_scene(int(sys.argv[sys.argv.index("--scene")+1])); sys.exit(0)

    names = ["Scene1_Hook","Scene2_Alex","Scene3_Ayumu",
             "Scene4_WeirdOnes","Scene5_Scale","Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_animals_count.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="animals_count", audio_path=str(audio))
    final = od / "animals_count_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
