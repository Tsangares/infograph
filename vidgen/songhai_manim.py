#!/usr/bin/env python3
"""The Library at the End of the World — Songhai Empire (Manim). Erasure arc.

6 scenes, ~37.0s (34.0s audio + 3s hold).

VTT cues (absolute → relative):
  Scene 1 (0.0–5.5s = 5.50s):
    0.200 (0.20) In the 1500s, the richest man on Earth wasn't European.
    2.500 (2.50) He was West African.
    3.500 (3.50) And his library held more books than most of Europe combined.
  Scene 2 (5.5–11.0s = 5.50s):
    5.700 (0.20) History says Africa had no great civilizations.
    7.500 (2.00) No written tradition. No centers of learning.
    9.000 (3.50) That's what colonial textbooks taught for 400 years.
  Scene 3 (11.0–17.0s = 6.00s):
    11.200 (0.20) Timbuktu had a university before Oxford.
    12.800 (1.80) 25,000 students.
    13.800 (2.80) Scholars came from Baghdad, Cairo, and Andalusia.
    15.000 (4.00) They studied astronomy, law, and medicine.
  Scene 4 (17.0–22.5s = 5.50s):
    17.200 (0.20) The Songhai Empire stretched across West Africa.
    18.800 (1.80) It controlled the gold and salt trade.
    20.500 (3.50) At its peak, Timbuktu held 700,000 manuscripts.
  Scene 5 (22.5–28.0s = 5.50s):
    22.700 (0.20) In 1591, Morocco invaded with cannons.
    24.200 (1.70) The scholars scattered.
    25.200 (2.70) The manuscripts were buried, burned,
    26.200 (3.70) or smuggled out in camel bags.
  Scene 6 (28.0–37.0s = 9.00s):
    28.200 (0.20) Timbuktu became a punchline. A word for nowhere.
    30.500 (2.50) The richest library in Africa was erased so thoroughly
    32.500 (4.50) that the world forgot it existed.
    34.000 (6.00) And then said it never did.
    + 3s hold + fade
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TTS_SCRIPT = """In the 1500s, the richest man on Earth wasn't European. He was West African. History says Africa had no written tradition. Timbuktu had a university before Oxford. 25,000 students. The Songhai Empire held 700,000 manuscripts. In 1591, Morocco invaded. Scholars scattered. Manuscripts buried, burned, or smuggled in camel bags. Timbuktu became a punchline — a word for nowhere. The richest library in Africa, erased so thoroughly the world said it never existed."""

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

BG = "#0A0A10"; SURFACE = "#12121C"; SURFACE2 = "#1A1A26"
BORDER = "#2A2A3A"; GRID = "#14141C"
SONGHAI_GOLD = "#C8962A"; SAHARA_TAN = "#D4A853"
MANUSCRIPT_CREAM = "#F5E8C0"; FIRE_ORANGE = "#FF6B35"
ERASURE_GRAY = "#404040"; WHITE_SOFT = "#F0F0F0"; MUTED = "#7B8DA0"

SAFE_W = 8.0
SAFE_TOP = 7.2
SAFE_BOT = -6.4
ZONE_TITLE  = 6.2
ZONE_UPPER  = 3.5
ZONE_MID    = 0.0
ZONE_LOWER  = -3.5
ZONE_FOOTER = -6.0


def gradient_bg(c=BG, g="#0A0F0A"):
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

def label_pill(txt, color=SONGHAI_GOLD, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    p = RoundedRectangle(width=t.width+0.5, height=t.height+0.3, corner_radius=0.18,
                         fill_color=bg, fill_opacity=0.95, stroke_color=color, stroke_width=1.5).move_to(t)
    return VGroup(p, t)

def section_div(width=5, color=SONGHAI_GOLD):
    l = Line(LEFT*width/2, LEFT*0.12, color=color, stroke_width=1.5)
    r = Line(RIGHT*0.12, RIGHT*width/2, color=color, stroke_width=1.5)
    d = Square(side_length=0.1, color=color, fill_color=color, fill_opacity=1).rotate(45*DEGREES)
    return VGroup(l, d, r)


# ── Domain Shape Helpers ──────────────────────────────────────

def mosque_silhouette(height=4.0, color=SONGHAI_GOLD):
    """Djinguereber Mosque — Sudano-Sahelian tower with pointed top + base."""
    sc = height / 4.0
    tower = Rectangle(width=1.2*sc, height=3.0*sc, fill_color=color, fill_opacity=0.8,
                      stroke_color=SAHARA_TAN, stroke_width=1.2)
    tower.move_to(UP * 0.5*sc)
    top = Polygon(
        np.array([-0.6*sc, 2.0*sc, 0]),
        np.array([0.6*sc, 2.0*sc, 0]),
        np.array([0, 3.0*sc, 0]),
        fill_color=color, fill_opacity=0.9, stroke_color=SAHARA_TAN, stroke_width=1
    )
    base = Rectangle(width=3.5*sc, height=1.2*sc, fill_color=color, fill_opacity=0.6,
                     stroke_color=SAHARA_TAN, stroke_width=1)
    base.move_to(DOWN * 1.1*sc)
    side_l = Rectangle(width=0.5*sc, height=1.8*sc, fill_color=color, fill_opacity=0.7,
                       stroke_width=0.8, stroke_color=SAHARA_TAN)
    side_l.move_to(LEFT * 1.3*sc + UP * 0.1*sc)
    side_r = side_l.copy().move_to(RIGHT * 1.3*sc + UP * 0.1*sc)
    tip_l = Polygon(
        np.array([-0.25*sc, 1.0*sc, 0]),
        np.array([0.25*sc, 1.0*sc, 0]),
        np.array([0, 1.5*sc, 0]),
        fill_color=color, fill_opacity=0.8, stroke_width=0
    ).move_to(LEFT * 1.3*sc + UP * 1.4*sc)
    tip_r = tip_l.copy().move_to(RIGHT * 1.3*sc + UP * 1.4*sc)
    return VGroup(base, tower, top, side_l, side_r, tip_l, tip_r)

def scroll_stack(n=5, color=MANUSCRIPT_CREAM, h=0.6):
    """Pile of manuscripts — overlapping tilted rectangles."""
    sc = h / 0.6
    scrolls = VGroup()
    np.random.seed(88)
    for i in range(n):
        s = Rectangle(width=0.8*sc, height=0.25*sc, fill_color=color,
                      fill_opacity=0.85, stroke_color=SONGHAI_GOLD, stroke_width=0.6)
        angle = np.random.uniform(-15, 15) * DEGREES
        s.rotate(angle)
        s.shift(UP * i * 0.12*sc + RIGHT * np.random.uniform(-0.1, 0.1)*sc)
        scrolls.add(s)
    return scrolls

def camel_fig(color=SAHARA_TAN, h=1.2):
    """Simplified camel silhouette — body oval + hump + neck + legs."""
    sc = h / 1.2
    body = Ellipse(width=1.2*sc, height=0.5*sc, fill_color=color, fill_opacity=0.85,
                   stroke_width=0.8, stroke_color=SONGHAI_GOLD)
    hump = Ellipse(width=0.4*sc, height=0.3*sc, fill_color=color, fill_opacity=0.9,
                   stroke_width=0).move_to(UP * 0.3*sc + LEFT * 0.1*sc)
    neck = Line(LEFT * 0.4*sc + UP * 0.1*sc, LEFT * 0.6*sc + UP * 0.6*sc,
                color=color, stroke_width=3*sc)
    head = Circle(radius=0.1*sc, fill_color=color, fill_opacity=1, stroke_width=0)
    head.move_to(LEFT * 0.6*sc + UP * 0.7*sc)
    legs = VGroup()
    for x_off in [-0.3, -0.1, 0.1, 0.3]:
        leg = Line(np.array([x_off*sc, -0.25*sc, 0]),
                   np.array([x_off*sc, -0.6*sc, 0]),
                   color=color, stroke_width=2*sc)
        legs.add(leg)
    return VGroup(body, hump, neck, head, legs)

def map_west_africa(color=SONGHAI_GOLD, opacity=0.25):
    """Rough West Africa bulge outline — Polygon."""
    pts = [
        np.array([-3.5, 1.0, 0]), np.array([-2.0, 2.0, 0]),
        np.array([0.0, 2.5, 0]), np.array([2.0, 2.0, 0]),
        np.array([3.5, 1.0, 0]), np.array([3.0, -0.5, 0]),
        np.array([1.5, -1.5, 0]), np.array([-0.5, -2.0, 0]),
        np.array([-2.5, -1.5, 0]), np.array([-3.5, -0.5, 0]),
    ]
    return Polygon(*pts, fill_color=color, fill_opacity=opacity,
                   stroke_color=color, stroke_width=1.5)

def cannon_shape(color=FIRE_ORANGE, h=1.0):
    """Stylised cannon — barrel + trapezoid base + wheels."""
    sc = h / 1.0
    barrel = Rectangle(width=2.0*sc, height=0.4*sc, fill_color=color,
                       fill_opacity=0.9, stroke_color=WHITE_SOFT, stroke_width=1)
    base = Polygon(
        np.array([-0.8*sc, -0.1*sc, 0]), np.array([0.8*sc, -0.1*sc, 0]),
        np.array([0.6*sc, -0.4*sc, 0]), np.array([-0.6*sc, -0.4*sc, 0]),
        fill_color=ERASURE_GRAY, fill_opacity=0.8, stroke_width=0.8, stroke_color=MUTED
    )
    wl = Circle(radius=0.2*sc, fill_color=ERASURE_GRAY, fill_opacity=0.7,
                stroke_color=MUTED, stroke_width=1).move_to(LEFT * 0.5*sc + DOWN * 0.5*sc)
    wr = wl.copy().move_to(RIGHT * 0.5*sc + DOWN * 0.5*sc)
    return VGroup(barrel, base, wl, wr)


# ================================================================
# SCENE 1: THE HOOK (0.0–5.5s = 5.50s)
# "Richest man on Earth wasn't European. He was West African."
# Visual: Map + gold figure radiating light + gold bars lower
# ================================================================
class Scene1_Hook(Scene):
    DURATION = 5.5
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        # ZONE_TITLE — pill
        pill = label_pill("THE RICHEST MAN", color=SONGHAI_GOLD, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER — Map of West Africa ghost bg
        africa = map_west_africa(SONGHAI_GOLD, opacity=0.12)
        africa.scale(0.8).move_to(UP * ZONE_UPPER)

        # ZONE_MID — Gold figure (hero)
        fig_head = Circle(radius=0.25, fill_color=SONGHAI_GOLD, fill_opacity=1, stroke_width=0)
        fig_head.move_to(UP * 1.3)
        fig_body = Line(UP * 1.05, DOWN * 0.2, color=SONGHAI_GOLD, stroke_width=3)
        fig_arms = Line(LEFT * 0.45 + UP * 0.6, RIGHT * 0.45 + UP * 0.6,
                       color=SONGHAI_GOLD, stroke_width=3)
        fig_ll = Line(DOWN * 0.2, DOWN * 0.8 + LEFT * 0.25, color=SONGHAI_GOLD, stroke_width=3)
        fig_rl = Line(DOWN * 0.2, DOWN * 0.8 + RIGHT * 0.25, color=SONGHAI_GOLD, stroke_width=3)
        figure = VGroup(fig_head, fig_body, fig_arms, fig_ll, fig_rl)
        figure.move_to(UP * ZONE_MID)

        # Radiating glow behind figure
        glow = Circle(radius=2.5, fill_color=SONGHAI_GOLD, fill_opacity=0.06, stroke_width=0)
        glow.move_to(UP * ZONE_MID)

        div = section_div(5, MUTED).move_to(DOWN * 1.8)

        # ZONE_LOWER — "NOT EUROPEAN" / "WEST AFRICAN"
        not_euro = safe_text("NOT EUROPEAN.", font="Bebas Neue", font_size=80, color=MUTED)
        not_euro.move_to(DOWN * 2.8)

        west_af = safe_text("WEST AFRICAN.", font="Bebas Neue", font_size=90,
                           color=SONGHAI_GOLD)
        west_af.move_to(DOWN * 4.3)

        # ZONE_FOOTER — scroll motif
        footer_scrolls = VGroup()
        for i in range(7):
            s = scroll_stack(2, MANUSCRIPT_CREAM, h=0.35)
            s.move_to(LEFT * 3 + RIGHT * i * 1.0 + DOWN * ZONE_FOOTER)
            s.set_opacity(0.4)
            footer_scrolls.add(s)

        # ── Timing: 5.50s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.20: "In the 1500s, the richest man on Earth wasn't European."
        self.play(FadeIn(africa, scale=0.95), run_time=0.4); t += 0.4
        self.play(FadeIn(glow), FadeIn(figure, scale=1.1), run_time=0.5); t += 0.5
        self.play(Flash(fig_head.get_center(), color=SONGHAI_GOLD,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=1.5

        # pulse glow outward
        self.play(glow.animate.scale(1.15).set_opacity(0.03), run_time=0.5); t += 0.5

        # VTT 2.50: "He was West African."
        self.play(Create(div), run_time=0.3); t += 0.3
        self.play(FadeIn(not_euro, shift=UP * 0.06), run_time=0.4); t += 0.4
        self.play(FadeIn(west_af, scale=1.08), run_time=0.5); t += 0.5
        self.play(Flash(west_af.get_center(), color=SONGHAI_GOLD,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=3.5

        # VTT 3.50: "And his library held more books than most of Europe."
        self.play(LaggedStart(*[FadeIn(s, shift=UP * 0.1) for s in footer_scrolls],
                              lag_ratio=0.06), run_time=0.6)               # t=4.1
        # gentle drift on map
        self.play(africa.animate.shift(DOWN * 0.15).set_opacity(0.08), run_time=1.1); t += 1.1
        target = getattr(self.__class__, 'DURATION', 5.5)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 2: THE WRONG ANSWER (5.5–11.0s = 5.50s)
# "History says Africa had no great civilizations. 400 years of lies."
# Visual: Crossed-out book + "400 YEARS" huge + quote fragments
# ================================================================
class Scene2_WrongAnswer(Scene):
    DURATION = 5.5
    def construct(self):
        self.add(gradient_bg("#080808"), grid_lines(0.02))
        t = 0

        # ZONE_TITLE
        pill = label_pill("THE LIE", color=FIRE_ORANGE, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER — Book shape (will be crossed out)
        book = Rectangle(width=2.5, height=3.5, fill_color=ERASURE_GRAY, fill_opacity=0.6,
                         stroke_color=MUTED, stroke_width=1.5)
        book_spine = Line(book.get_left() + RIGHT * 0.3 + UP * 1.5,
                         book.get_left() + RIGHT * 0.3 + DOWN * 1.5,
                         color=MUTED, stroke_width=1)
        book_lines = VGroup()
        for i in range(4):
            bl = Line(LEFT * 0.6, RIGHT * 0.6, color=ERASURE_GRAY, stroke_width=1.5)
            bl.move_to(book.get_center() + UP * 0.8 + DOWN * i * 0.5 + RIGHT * 0.2)
            book_lines.add(bl)
        book_group = VGroup(book, book_spine, book_lines)
        book_group.move_to(UP * ZONE_UPPER)

        # Red X over book
        cross1 = Line(book.get_corner(UL), book.get_corner(DR),
                      color=FIRE_ORANGE, stroke_width=4)
        cross2 = Line(book.get_corner(UR), book.get_corner(DL),
                      color=FIRE_ORANGE, stroke_width=4)

        div = section_div(5, FIRE_ORANGE).move_to(UP * 1.0)

        # ZONE_MID/LOWER — "400 YEARS"
        four_hundred = safe_text("400 YEARS", font="Bebas Neue", font_size=130,
                                color=FIRE_ORANGE)
        four_hundred.move_to(DOWN * 0.8)

        of_lies = safe_text("OF COLONIAL TEXTBOOKS", font="Inter", font_size=28,
                           color=MUTED, weight="BOLD")
        of_lies.move_to(DOWN * 2.3)

        div2 = section_div(5, ERASURE_GRAY).move_to(DOWN * 3.2)

        # ZONE_LOWER — gray struck-through fragments
        frag1 = safe_text("\"No civilizations.\"", font="DM Serif Display",
                          font_size=40, color=ERASURE_GRAY)
        frag1.move_to(DOWN * 4.2)
        strike1 = Line(frag1.get_left() + LEFT * 0.1, frag1.get_right() + RIGHT * 0.1,
                       color=FIRE_ORANGE, stroke_width=2)
        strike1.move_to(frag1)

        frag2 = safe_text("\"No written tradition.\"", font="DM Serif Display",
                          font_size=40, color=ERASURE_GRAY)
        frag2.move_to(DOWN * 5.3)
        strike2 = Line(frag2.get_left() + LEFT * 0.1, frag2.get_right() + RIGHT * 0.1,
                       color=FIRE_ORANGE, stroke_width=2)
        strike2.move_to(frag2)

        # ZONE_FOOTER
        footer = safe_text("ERASURE", font="Inter", font_size=22,
                          color=FIRE_ORANGE, weight="BOLD")
        footer.move_to(DOWN * ZONE_FOOTER)
        footer.set_opacity(0.5)

        # ── Timing: 5.50s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.20: "History says Africa had no great civilizations."
        self.play(FadeIn(book_group, scale=0.9), run_time=0.5); t += 0.5
        self.play(FadeIn(frag1, shift=UP * 0.04), run_time=0.4); t += 0.4

        # VTT 2.00: "No written tradition. No centers of learning."
        self.wait(0.5); t += 0.5
        self.play(FadeIn(frag2, shift=UP * 0.04), run_time=0.4); t += 0.4

        # VTT 3.50: "That's what colonial textbooks taught for 400 years."
        self.wait(1.1); t += 1.1
        self.play(Create(cross1), Create(cross2), run_time=0.3); t += 0.3
        # strike-through the quotes
        self.play(Create(strike1), Create(strike2), run_time=0.2); t += 0.2
        self.play(Create(div), run_time=0.2); t += 0.2
        self.play(FadeIn(four_hundred, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(four_hundred.get_center(), color=FIRE_ORANGE,
                        line_length=0.5, num_lines=10, run_time=0.3))      # t=4.7
        self.play(Create(div2), FadeIn(of_lies), FadeIn(footer), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 5.5)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 3: THE CONTRADICTION (11.0–17.0s = 6.00s)
# "Timbuktu had a university before Oxford. 25,000 students."
# Visual: Mosque + date comparison + scholar dots + subjects
# ================================================================
class Scene3_Contradiction(Scene):
    DURATION = 6.0
    def construct(self):
        self.add(gradient_bg(g="#0A0F05"), grid_lines(0.03))
        t = 0

        # ZONE_TITLE
        pill = label_pill("THE TRUTH", color=SONGHAI_GOLD, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER — Mosque silhouette
        mosque = mosque_silhouette(2.5, color=SONGHAI_GOLD)
        mosque.move_to(UP * ZONE_UPPER)

        div1 = section_div(5, SONGHAI_GOLD).move_to(UP * 1.8)

        # ZONE_MID — Date comparison
        timb_yr = safe_text("1327", font="Bebas Neue", font_size=100, color=SONGHAI_GOLD)
        timb_yr.move_to(LEFT * 2 + UP * 0.5)
        timb_label = safe_text("TIMBUKTU", font="Inter", font_size=24,
                              color=SONGHAI_GOLD, weight="BOLD")
        timb_label.move_to(LEFT * 2 + DOWN * 0.5)

        vs = safe_text("vs", font="DM Serif Display", font_size=36, color=MUTED)
        vs.move_to(UP * 0.5)

        ox_yr = safe_text("1167", font="Bebas Neue", font_size=80, color=ERASURE_GRAY)
        ox_yr.move_to(RIGHT * 2 + UP * 0.5)
        ox_label = safe_text("OXFORD", font="Inter", font_size=24,
                            color=ERASURE_GRAY, weight="BOLD")
        ox_label.move_to(RIGHT * 2 + DOWN * 0.5)

        div2 = section_div(5, SONGHAI_GOLD).move_to(DOWN * 1.5)

        # ZONE_LOWER — "25,000" + scholar dots
        students = safe_text("25,000", font="Bebas Neue", font_size=120,
                            color=MANUSCRIPT_CREAM)
        students.move_to(DOWN * 2.5)
        students_l = safe_text("STUDENTS", font="Inter", font_size=28,
                              color=WHITE_SOFT, weight="BOLD")
        students_l.move_to(DOWN * 3.5)

        # Scholar dots — rows of small circles to represent scale
        scholar_dots = VGroup()
        for row in range(3):
            for col in range(12):
                d = Dot(radius=0.06, color=SONGHAI_GOLD, fill_opacity=0.6)
                d.move_to(LEFT * 3.3 + RIGHT * col * 0.55 + DOWN * 4.3 + DOWN * row * 0.4)
                scholar_dots.add(d)

        # ZONE_FOOTER — Subjects
        subjects = safe_text("ASTRONOMY  ·  LAW  ·  MEDICINE", font="Inter",
                            font_size=24, color=SAHARA_TAN, weight="BOLD")
        subjects.move_to(DOWN * ZONE_FOOTER)

        # ── Timing: 6.00s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.20: "Timbuktu had a university before Oxford."
        self.play(FadeIn(mosque, scale=0.9), run_time=0.5); t += 0.5
        self.play(Create(div1), run_time=0.2); t += 0.2
        self.play(FadeIn(timb_yr, scale=1.1), FadeIn(timb_label), run_time=0.4); t += 0.4
        self.play(FadeIn(vs), run_time=0.2); t += 0.2
        self.play(FadeIn(ox_yr), FadeIn(ox_label), run_time=0.3); t += 0.3

        # VTT 1.80: "25,000 students."
        self.play(Create(div2), run_time=0.2); t += 0.2
        self.play(FadeIn(students, scale=1.15), run_time=0.5); t += 0.5
        self.play(Flash(students.get_center(), color=MANUSCRIPT_CREAM,
                        line_length=0.4, num_lines=10, run_time=0.3))      # t=2.9
        self.play(FadeIn(students_l), run_time=0.3); t += 0.3

        # VTT 2.80: "Scholars came from Baghdad, Cairo, and Andalusia."
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in scholar_dots],
                              lag_ratio=0.01), run_time=0.6)               # t=3.8

        # VTT 4.00: "They studied astronomy, law, and medicine."
        target = getattr(self.__class__, 'DURATION', 6.0)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeIn(subjects, shift=UP * 0.05), run_time=0.4); t += 0.4

        # gentle mosque glow pulse
        mosque_glow = Circle(radius=2.0, fill_color=SONGHAI_GOLD,
                            fill_opacity=0.04, stroke_width=0).move_to(mosque)
        self.play(FadeIn(mosque_glow), run_time=0.4); t += 0.4
        self.play(mosque_glow.animate.scale(1.3).set_opacity(0.01), run_time=1.2); t += 1.2

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 4: THE SCALE (17.0–22.5s = 5.50s)
# "Songhai Empire. Gold and salt trade. 700,000 manuscripts."
# Visual: Map + scrolls flooding the frame + huge number
# ================================================================
class Scene4_Scale(Scene):
    DURATION = 5.5
    def construct(self):
        self.add(gradient_bg("#080A05"), grid_lines(0.03))
        t = 0

        # ZONE_TITLE
        pill = label_pill("THE EMPIRE", color=SONGHAI_GOLD, fs=28)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER — Map
        africa = map_west_africa('#8B7D3C', opacity=0.5)
        africa.move_to(UP * ZONE_UPPER)
        africa.scale(0.7)

        # Trade route lines across map
        route1 = DashedLine(LEFT * 2 + UP * 4.5, RIGHT * 2 + UP * 2.5,
                           color=SAHARA_TAN, stroke_width=1.5, dash_length=0.15)
        route2 = DashedLine(LEFT * 1 + UP * 4, RIGHT * 1.5 + UP * 3,
                           color=SAHARA_TAN, stroke_width=1.5, dash_length=0.15)

        trade = safe_text("GOLD  ·  SALT", font="Inter", font_size=28,
                         color=SAHARA_TAN, weight="BOLD")
        trade.move_to(UP * 1.5)

        div1 = section_div(5, SONGHAI_GOLD).move_to(UP * 0.6)

        # ZONE_MID — "700,000" hero number
        seven_hundred_k = safe_text("700,000", font="Bebas Neue", font_size=160,
                                   color=MANUSCRIPT_CREAM)
        seven_hundred_k.move_to(DOWN * 0.8)
        manuscripts = safe_text("MANUSCRIPTS", font="Inter", font_size=32,
                               color=SONGHAI_GOLD, weight="BOLD")
        manuscripts.move_to(DOWN * 2.2)

        div2 = section_div(5, MANUSCRIPT_CREAM).move_to(DOWN * 3.0)

        # ZONE_LOWER — Scrolls flooding the bottom
        scrolls = VGroup()
        np.random.seed(44)
        for row in range(3):
            for col in range(7):
                s = scroll_stack(3, MANUSCRIPT_CREAM, h=0.35)
                x = -3.0 + col * 0.9 + np.random.uniform(-0.12, 0.12)
                y = -4.0 - row * 0.7 + np.random.uniform(-0.08, 0.08)
                s.move_to(np.array([x, y, 0]))
                scrolls.add(s)

        # ZONE_FOOTER — era label
        empire_stats = safe_text("1464–1591 CE", font="Inter",
                                 font_size=24, color=SAHARA_TAN, weight="BOLD")
        empire_stats.move_to(DOWN * ZONE_FOOTER)

        # ── Timing: 5.50s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.20: "The Songhai Empire stretched across West Africa."
        self.play(FadeIn(africa, scale=0.9), run_time=0.5); t += 0.5

        # VTT 1.80: "It controlled the gold and salt trade."
        self.wait(0.7); t += 0.7
        self.play(Create(route1), Create(route2), run_time=0.3); t += 0.3
        self.play(FadeIn(trade), run_time=0.3); t += 0.3
        self.play(Create(div1), run_time=0.2); t += 0.2

        # VTT 3.50: "At its peak, Timbuktu held 700,000 manuscripts."
        self.wait(0.9); t += 0.9
        self.play(FadeIn(seven_hundred_k, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(seven_hundred_k.get_center(), color=MANUSCRIPT_CREAM,
                        line_length=0.6, num_lines=12, run_time=0.3))      # t=4.0
        self.play(FadeIn(manuscripts), run_time=0.3); t += 0.3
        self.play(Create(div2), FadeIn(empire_stats), run_time=0.2); t += 0.2

        # Scrolls flood in from bottom
        self.play(LaggedStart(*[FadeIn(s, shift=UP * 0.2) for s in scrolls],
                              lag_ratio=0.02), run_time=0.7)               # t=5.2
        target = getattr(self.__class__, 'DURATION', 5.5)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 5: THE DESTRUCTION (22.5–28.0s = 5.50s)
# "1591. Morocco invaded. Manuscripts buried, burned, smuggled."
# Visual: Cannon fires, scrolls scatter/burn, camel flees
# ================================================================
class Scene5_Destruction(Scene):
    DURATION = 5.5
    def construct(self):
        self.add(gradient_bg("#0A0505"), grid_lines(0.02))
        t = 0

        # ZONE_TITLE
        pill = label_pill("THE DESTRUCTION", color=FIRE_ORANGE, fs=26)
        pill.move_to(UP * ZONE_TITLE)

        # ZONE_UPPER — Date stamp
        yr_1591 = safe_text("1591", font="Bebas Neue", font_size=120, color=FIRE_ORANGE)
        yr_1591.move_to(UP * ZONE_UPPER + UP * 0.5)

        div1 = section_div(5, FIRE_ORANGE).move_to(UP * 2.0)

        # ZONE_MID — Cannon + scrolls
        cannon = cannon_shape(FIRE_ORANGE, h=1.0)
        cannon.move_to(LEFT * 2.5 + UP * ZONE_MID + UP * 0.5)

        # Scrolls that will scatter — clustered at mid-right
        scatter_scrolls = VGroup()
        np.random.seed(91)
        for i in range(10):
            s = Rectangle(width=0.6, height=0.2, fill_color=MANUSCRIPT_CREAM,
                         fill_opacity=0.8, stroke_width=0.5, stroke_color=SONGHAI_GOLD)
            s.rotate(np.random.uniform(-30, 30) * DEGREES)
            s.move_to(RIGHT * 1.5 + np.array([np.random.uniform(-1, 1),
                      np.random.uniform(-0.8, 0.8), 0]))
            scatter_scrolls.add(s)

        # Cannon flash — burst circle
        cannon_flash = Circle(radius=0.4, fill_color=FIRE_ORANGE,
                             fill_opacity=0.8, stroke_width=0)
        cannon_flash.move_to(cannon.get_right() + RIGHT * 0.2)

        div2 = section_div(5, SAHARA_TAN).move_to(DOWN * 1.8)

        # ZONE_LOWER — Camel smuggling manuscripts
        camel = camel_fig(SAHARA_TAN, h=1.2)
        camel.move_to(RIGHT * 2 + DOWN * ZONE_LOWER)

        camel_scroll = scroll_stack(2, MANUSCRIPT_CREAM, h=0.3)
        camel_scroll.move_to(camel.get_top() + UP * 0.15)

        actions = safe_text("BURIED  ·  BURNED  ·  SMUGGLED", font="Inter",
                           font_size=26, color=FIRE_ORANGE, weight="BOLD")
        actions.move_to(DOWN * 5.0)

        # ZONE_FOOTER
        footer = safe_text("THE UNIVERSITY NEVER REOPENED", font="Inter",
                         font_size=22, color=ERASURE_GRAY, weight="BOLD")
        footer.move_to(DOWN * ZONE_FOOTER)

        # ── Timing: 5.50s ──
        self.play(FadeIn(pill, scale=1.05), run_time=0.3); t += 0.3

        # VTT 0.20: "In 1591, Morocco invaded with cannons."
        self.play(FadeIn(yr_1591, scale=1.15), run_time=0.5); t += 0.5
        self.play(Flash(yr_1591.get_center(), color=FIRE_ORANGE,
                        line_length=0.5, num_lines=8, run_time=0.3))       # t=1.1
        self.play(Create(div1), run_time=0.2); t += 0.2
        self.play(FadeIn(cannon, shift=RIGHT * 0.3), run_time=0.3); t += 0.3

        # cannon fires — flash + scrolls appear
        self.play(FadeIn(cannon_flash, scale=0.3),
                  FadeIn(scatter_scrolls), run_time=0.2)                   # t=1.8
        self.play(FadeOut(cannon_flash), run_time=0.1); t += 0.1

        # VTT 1.70: "The scholars scattered."
        # Scrolls scatter in all directions
        self.play(
            *[s.animate.shift(
                np.array([np.random.uniform(-3.5, 3.5), np.random.uniform(-3, 3), 0])
            ).set_opacity(0.2).rotate(np.random.uniform(-1, 1)) for s in scatter_scrolls[:5]],
            run_time=0.5,
        )                                                                   # t=2.4

        # VTT 2.70: "The manuscripts were buried, burned,"
        self.play(
            *[s.animate.set_color(FIRE_ORANGE).set_opacity(0.6).scale(0.5) for s in scatter_scrolls[5:]],
            run_time=0.5,
        )                                                                   # t=2.9
        self.play(Create(div2), run_time=0.2); t += 0.2

        # VTT 3.70: "or smuggled out in camel bags."
        self.play(FadeIn(camel, shift=LEFT * 0.5), FadeIn(camel_scroll), run_time=0.4); t += 0.4
        # camel walks right
        self.play(camel.animate.shift(RIGHT * 1.0),
                  camel_scroll.animate.shift(RIGHT * 1.0), run_time=0.5)   # t=4.0

        self.play(FadeIn(actions, shift=UP * 0.05), run_time=0.4); t += 0.4
        self.play(FadeIn(footer, shift=UP * 0.04), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 5.5)
        self.wait(max(0.1, target - t - 0.3))

        self.play(FadeOut(Group(*self.mobjects[2:]), run_time=0.3)); t += 0.3


# ================================================================
# SCENE 6: THE PUNCH (28.0–37.0s = 9.00s)
# "Timbuktu became a punchline. The world forgot it existed."
# Visual: Mosque dissolving to dust, "NOWHERE" → gold reveal
# ================================================================
class Scene6_Punch(Scene):
    DURATION = 9.0
    def construct(self):
        self.add(gradient_bg("#050508"), grid_lines(0.02))
        t = 0

        # Letterbox bars — cinematic
        bh = 0.8
        top_bar = Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                  stroke_width=0).move_to(UP * (8 - bh/2))
        bot_bar = Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1,
                  stroke_width=0).move_to(DOWN * (8 - bh/2))
        self.add(top_bar, bot_bar)

        # ZONE_UPPER — Ghost mosque (fading relic)
        mosque = mosque_silhouette(3.0, color=SONGHAI_GOLD)
        mosque.move_to(UP * ZONE_UPPER)
        mosque.set_opacity(0.2)
        self.add(mosque)

        # "NOWHERE" — appears at ZONE_UPPER over mosque
        nowhere = safe_text("NOWHERE.", font="Bebas Neue", font_size=100,
                           color=ERASURE_GRAY)
        nowhere.move_to(UP * ZONE_UPPER)

        div1 = section_div(4, ERASURE_GRAY).move_to(UP * 1.5)

        # ZONE_MID — mosque dust particles (debris of erasure)
        dust = VGroup()
        np.random.seed(66)
        for _ in range(20):
            d = Dot(radius=np.random.uniform(0.02, 0.06),
                    color=SONGHAI_GOLD, fill_opacity=np.random.uniform(0.1, 0.3))
            d.move_to(np.array([np.random.uniform(-3, 3),
                       np.random.uniform(-1.5, 1.5), 0]))
            dust.add(d)

        div2 = section_div(4, SONGHAI_GOLD).move_to(DOWN * 1.5)

        # ZONE_LOWER — scroll remnants scattered and faded
        remnant_scrolls = VGroup()
        np.random.seed(77)
        for i in range(8):
            s = Rectangle(width=0.5, height=0.15, fill_color=MANUSCRIPT_CREAM,
                         fill_opacity=0.15, stroke_width=0.3, stroke_color=ERASURE_GRAY)
            s.rotate(np.random.uniform(-40, 40) * DEGREES)
            s.move_to(np.array([np.random.uniform(-3, 3), -3.5 + np.random.uniform(-1, 1), 0]))
            remnant_scrolls.add(s)

        div3 = section_div(4, FIRE_ORANGE).move_to(DOWN * 4.8)

        # ZONE_FOOTER — final gold reveal
        it_never = safe_text("IT NEVER DID.", font="Bebas Neue", font_size=80,
                            color=SONGHAI_GOLD)
        it_never.move_to(DOWN * ZONE_FOOTER + UP * 0.2)

        glow = Circle(radius=2.5, fill_color=SONGHAI_GOLD, fill_opacity=0.04, stroke_width=0)
        glow.move_to(it_never)

        # ── Timing: 9.00s ──
        # VTT 0.20: "Timbuktu became a punchline. A word for nowhere."
        self.play(FadeIn(nowhere, scale=1.1), run_time=0.6); t += 0.6

        # Mosque fades to ghost
        self.play(mosque.animate.set_opacity(0.05), run_time=0.5); t += 0.5
        self.play(Create(div1), run_time=0.3); t += 0.3

        # dust particles drift in
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in dust],
                              lag_ratio=0.02), run_time=0.5)               # t=1.9

        # VTT 2.50: "The richest library in Africa was erased so thoroughly"
        self.wait(0.3); t += 0.3
        # remnant scrolls appear — scattered and broken
        self.play(LaggedStart(*[FadeIn(s) for s in remnant_scrolls],
                              lag_ratio=0.04), run_time=0.5)               # t=2.7

        # dust drifts downward slowly (erasure happening)
        self.play(
            *[d.animate.shift(DOWN * np.random.uniform(0.3, 0.8)).set_opacity(0.05)
              for d in dust],
            run_time=1.0,
        )                                                                   # t=3.7
        self.play(Create(div2), run_time=0.3); t += 0.3

        # VTT 4.50: "that the world forgot it existed."
        # remnant scrolls fade further
        self.play(
            *[s.animate.set_opacity(0.04) for s in remnant_scrolls],
            run_time=0.8,
        )                                                                   # t=4.8

        # VTT 6.00: "And then said it never did."
        target = getattr(self.__class__, 'DURATION', 9.0)
        self.wait(max(0.1, target - t - 0.8))
        self.play(Create(div3), run_time=0.3); t += 0.3
        self.play(FadeIn(glow), FadeIn(it_never, scale=1.08), run_time=0.7); t += 0.7
        self.play(Flash(it_never.get_center(), color=SONGHAI_GOLD,
                        line_length=0.4, num_lines=8, run_time=0.3))       # t=7.0

        # Hold — nowhere fades, gold lingers
        self.play(nowhere.animate.set_opacity(0.1), run_time=0.5); t += 0.5

        # Fade to black
        black = Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        self.play(FadeIn(black), run_time=1.5); t += 1.5


# ── Infra ─────────────────────────────────────────────────────
def render_single_scene(idx):
    sc = [Scene1_Hook, Scene2_WrongAnswer, Scene3_Contradiction,
          Scene4_Scale, Scene5_Destruction, Scene6_Punch]
    config.output_file = f"songhai_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    sc[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"songhai_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    sc = [Scene1_Hook, Scene2_WrongAnswer, Scene3_Contradiction,
          Scene4_Scale, Scene5_Destruction, Scene6_Punch]
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(sc):
        n = f"songhai_scene_{i+1}"; print(f"  Preview {n}...")
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
             "Scene4_Scale","Scene5_Destruction","Scene6_Punch"]
    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_songhai.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="songhai", audio_path=str(audio))
    final = od / "songhai_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
