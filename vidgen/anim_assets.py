"""TKK Animation Assets Library.

General-purpose, reusable ANIMATED sequences built from SVG icons + manim motion.
These are not static primitives — they are pre-built animation sequences
that the engineer calls to SHOW the story instead of TELLING it with text.

Each asset is a function that takes a scene and plays animations.
They are annotated so the engineer knows when to use each one.

Usage:
    from anim_assets import person_grid_poison, ozone_hole, stamp_slam

Categories:
    - People: person_grid, person_dies, crowd_affected, figures_stand
    - Danger: warning_pulse, poison_spread, explosion_flash
    - Institutional: stamp_slam, document_reveal, gavel_strike, award_reveal
    - Environmental: ozone_hole, earth_pulse, pollution_spread
    - Data: counter_up, bar_grow, timeline_fill
    - Motion: shake_object, pulse_object, orbit_around
"""

import numpy as np
from manim import *
from anim_primitives import (
    load_svg, safe_text, headline, divider, stamp, flash_transition,
    TKK_BG, TKK_RED, TKK_GOLD, TKK_GREEN, TKK_WHITE, TKK_DIM, TKK_MUTED, TKK_ACCENT,
)


# ============================================================
# PEOPLE ANIMATIONS
# ============================================================

def make_person(color=TKK_DIM, height=0.8):
    """Create a single person icon. Returns SVGMobject."""
    try:
        p = load_svg("person.svg", color=color, height=height)
    except FileNotFoundError:
        # Fallback: simple stick figure
        body = Line(UP * 0.3, DOWN * 0.3, color=color, stroke_width=2)
        head = Circle(radius=0.1, color=color, stroke_width=2).next_to(body, UP, buff=0.02)
        arms = Line(LEFT * 0.2, RIGHT * 0.2, color=color, stroke_width=2).move_to(body.get_top() + DOWN * 0.15)
        legs = VGroup(
            Line(ORIGIN, DOWN * 0.25 + LEFT * 0.15, color=color, stroke_width=2),
            Line(ORIGIN, DOWN * 0.25 + RIGHT * 0.15, color=color, stroke_width=2),
        ).move_to(body.get_bottom())
        p = VGroup(head, body, arms, legs)
        p.scale_to_fit_height(height)
    return p


def person_grid(rows=6, cols=9, color=TKK_DIM, height=0.6, spacing=0.15):
    """Grid of person icons. Returns VGroup.

    Use for: "every human on Earth", "12,000 people a year", mass scale.
    Animate by changing colors: grid[i].set_color(RED) or FadeOut(grid[i])
    """
    grid = VGroup()
    for r in range(rows):
        for c in range(cols):
            p = make_person(color=color, height=height)
            p.move_to(RIGHT * (c - cols/2 + 0.5) * (height + spacing) +
                      DOWN * (r - rows/2 + 0.5) * (height + spacing))
            grid.add(p)
    return grid


def person_grid_poison(scene, grid, stagger=0.03, color=TKK_RED):
    """Animate a person grid turning red one by one — "everyone was poisoned."

    Use for: mass poisoning, global effect, epidemic.
    """
    anims = [p.animate.set_color(color) for p in grid]
    scene.play(LaggedStart(*anims, lag_ratio=stagger), run_time=2.0)


def person_dies(scene, person, direction=DOWN):
    """Animate a person icon dying — shifts down and fades.

    Use for: individual death, worker dying, casualty.
    """
    scene.play(
        person.animate.shift(direction * 0.5).set_opacity(0.2),
        run_time=0.4,
    )


def figures_stand(count=5, color=TKK_DIM, highlight_index=None,
                  highlight_color=TKK_GOLD, height=1.2, spacing=0.4):
    """Row of standing figures, optionally one highlighted.

    Use for: "five women sued", "a group of people", witnesses.
    """
    figures = VGroup()
    for i in range(count):
        c = highlight_color if i == highlight_index else color
        p = make_person(color=c, height=height)
        figures.add(p)
    figures.arrange(RIGHT, buff=spacing)
    return figures


# ============================================================
# DANGER / WARNING ANIMATIONS
# ============================================================

def warning_pulse(scene, position=ORIGIN, scale=3.0, color=TKK_RED, pulses=2):
    """Pulsing warning triangle.

    Use for: danger, toxic, hazard, alerting the viewer.
    """
    try:
        warn = load_svg("warning.svg", color=color, height=scale)
    except FileNotFoundError:
        warn = Triangle(color=color, fill_opacity=0.3, stroke_width=3)
        warn.scale(scale / 2)
    warn.move_to(position).set_opacity(0.3)
    scene.add(warn)
    for _ in range(pulses):
        scene.play(warn.animate.set_opacity(0.7).scale(1.05), run_time=0.3)
        scene.play(warn.animate.set_opacity(0.3).scale(1/1.05), run_time=0.3)
    return warn


def shake_object(scene, mobject, intensity=0.15, shakes=4, run_time=0.5):
    """Shake an object back and forth — for unease, instability, poisoning.

    Use for: hallucinating, earthquake, instability.
    """
    original = mobject.get_center()
    for i in range(shakes):
        direction = RIGHT if i % 2 == 0 else LEFT
        scene.play(
            mobject.animate.shift(direction * intensity),
            run_time=run_time / (shakes * 2),
        )
        scene.play(
            mobject.animate.move_to(original),
            run_time=run_time / (shakes * 2),
        )


def pulse_object(scene, mobject, scale_factor=1.15, pulses=2, run_time=0.8):
    """Pulse an object larger and back — for emphasis, glow, heartbeat.

    Use for: emphasis on a key element, "this is important."
    """
    for _ in range(pulses):
        scene.play(mobject.animate.scale(scale_factor),
                   run_time=run_time / (pulses * 2))
        scene.play(mobject.animate.scale(1/scale_factor),
                   run_time=run_time / (pulses * 2))


# ============================================================
# INSTITUTIONAL ANIMATIONS
# ============================================================

def stamp_slam(scene, text, position=ORIGIN, color=TKK_RED, size=56):
    """Slam a rubber stamp onto the scene with a flash.

    Use for: bureaucratic decisions, labels, verdicts, coverups.
    Returns the stamp VGroup.
    """
    s = stamp(text, color=color, size=size)
    s.move_to(position)
    scene.play(FadeIn(s, scale=2.5), run_time=0.2)
    flash_transition(scene, opacity=0.1, duration=0.06)
    return s


def gavel_strike(scene, position=ORIGIN):
    """Animated gavel striking — for courtroom, judgement, verdict.

    Use for: trial, legal decision, sentencing.
    """
    try:
        gavel = load_svg("gavel.svg", color=TKK_GOLD, height=2.0)
    except FileNotFoundError:
        gavel = Rectangle(width=0.3, height=1.5, color=TKK_GOLD,
                          fill_opacity=0.7, stroke_width=1)
    gavel.move_to(position + UP * 1.5)
    scene.play(FadeIn(gavel), run_time=0.2)
    scene.play(gavel.animate.shift(DOWN * 1.5), run_time=0.15)
    flash_transition(scene, opacity=0.08, duration=0.05)
    scene.play(gavel.animate.shift(UP * 0.3), run_time=0.1)
    return gavel


def award_reveal(scene, position=ORIGIN, count=2, color=TKK_GOLD):
    """Trophy/award icons appearing — for ironic awards, recognition.

    Use for: "won awards", Nobel Prize, medals — often used ironically.
    """
    awards = VGroup()
    for i in range(count):
        try:
            trophy = load_svg("lucide-scale.svg", color=color, height=1.5)
        except FileNotFoundError:
            trophy = Star(color=color, fill_opacity=0.7).scale(0.5)
        trophy.move_to(position + RIGHT * (i - count/2 + 0.5) * 2)
        awards.add(trophy)
    scene.play(LaggedStart(*[FadeIn(a, scale=1.5) for a in awards],
               lag_ratio=0.3), run_time=0.8)
    return awards


def document_reveal(scene, title="MEDICAL REPORT", position=ORIGIN,
                    width=4, height=5, color=TKK_DIM):
    """Animated document/form appearing.

    Use for: official documents, reports, forms, bureaucratic elements.
    """
    doc = VGroup(
        Rectangle(width=width, height=height, color=color,
                  fill_color=color, fill_opacity=0.08, stroke_width=1),
        safe_text(title, font="Space Mono", font_size=20,
                  color=color).move_to(UP * (height/2 - 0.4)),
    )
    # Fake form lines
    for i in range(4):
        line = Line(LEFT * (width/2 - 0.3), RIGHT * (width/2 - 0.3),
                    color=color, stroke_width=0.5, stroke_opacity=0.3)
        line.move_to(UP * (height/2 - 1.0 - i * 0.6))
        doc.add(line)

    doc.move_to(position)
    scene.play(FadeIn(doc, shift=UP * 0.3), run_time=0.5)
    return doc


# ============================================================
# ENVIRONMENTAL ANIMATIONS
# ============================================================

def ozone_hole(scene, position=ORIGIN, radius=2.5):
    """Animated ozone layer with a hole tearing open.

    Use for: Freon, atmosphere damage, environmental destruction.
    Returns the VGroup.
    """
    # Earth circle
    earth = Circle(radius=radius, color="#1a3a5a",
                   fill_color="#0d2137", fill_opacity=0.8,
                   stroke_width=1)
    # Ozone layer (outer ring)
    ozone = Circle(radius=radius + 0.3, color="#4488cc",
                   stroke_width=2, fill_opacity=0)

    # The hole — a red arc that represents damage
    hole = Arc(radius=radius + 0.3, start_angle=-PI/3, angle=PI*2/3,
               color=TKK_RED, stroke_width=4)
    # Dark fill behind the hole
    hole_fill = AnnularSector(inner_radius=radius - 0.1,
                               outer_radius=radius + 0.5,
                               start_angle=-PI/3, angle=PI*2/3,
                               color=TKK_RED, fill_opacity=0.15,
                               stroke_width=0)

    group = VGroup(earth, ozone).move_to(position)
    scene.play(FadeIn(group), run_time=0.4)

    hole.move_to(position)
    hole_fill.move_to(position)
    scene.play(Create(hole), FadeIn(hole_fill), run_time=0.8)
    group.add(hole, hole_fill)
    return group


def pollution_spread(scene, center=ORIGIN, radius=3, color=TKK_RED,
                     rings=3, run_time=1.5):
    """Expanding rings from a center — poison spreading outward.

    Use for: contamination, pollution, radiation, disease spread.
    """
    for i in range(rings):
        ring = Circle(radius=0.1, color=color, stroke_width=2,
                      stroke_opacity=0.6 - i * 0.15)
        ring.move_to(center)
        target = Circle(radius=radius * (i + 1) / rings, color=color,
                        stroke_width=1, stroke_opacity=0.1)
        target.move_to(center)
        scene.play(Transform(ring, target),
                   run_time=run_time / rings)


# ============================================================
# DATA ANIMATIONS
# ============================================================

def counter_up(scene, start, end, position=ORIGIN, color=TKK_GOLD,
               size=100, duration=1.5, prefix="", suffix=""):
    """Animated counting number on screen.

    Use for: statistics, growing numbers, escalating counts.
    """
    num = Integer(start, color=color, font_size=size)
    num.move_to(position)
    scene.add(num)
    scene.play(ChangeDecimalToValue(num, end, run_time=duration))
    return num


# ============================================================
# COMPOUND ANIMATIONS (multi-step sequences)
# ============================================================

def person_sequence_die(scene, count=3, position=ORIGIN, spacing=1.2,
                        labels=None, label_colors=None, stagger=0.4):
    """Multiple person icons that shake then die one by one.

    Use for: "hallucinating, convulsing, and dying" — the sequence.
    labels: words that appear as each person dies.
    """
    if labels is None:
        labels = [None] * count
    if label_colors is None:
        label_colors = [TKK_RED] * count

    persons = VGroup()
    for i in range(count):
        p = make_person(color=TKK_WHITE, height=1.2)
        p.move_to(position + RIGHT * (i - count/2 + 0.5) * spacing)
        persons.add(p)

    scene.play(FadeIn(persons), run_time=0.3)

    for i, (person, label, lcolor) in enumerate(zip(persons, labels, label_colors)):
        # Shake
        shake_object(scene, person, intensity=0.1, shakes=3, run_time=0.3)
        # Turn red
        scene.play(person.animate.set_color(TKK_RED), run_time=0.15)
        # Show label if provided
        if label:
            lbl = safe_text(label, font="Bebas Neue", font_size=40, color=lcolor)
            lbl.next_to(person, DOWN, buff=0.3)
            scene.play(FadeIn(lbl), run_time=0.2)
        # Die
        person_dies(scene, person)

    return persons


def coverup_sequence(scene, safe_text_content="SAFE", disappear_duration="1 YEAR",
                     position=ORIGIN):
    """Press conference → stamp SAFE → person disappears.

    Use for: corporate coverup, public denial followed by private consequences.
    """
    # Person at podium
    person = make_person(color=TKK_WHITE, height=1.5)
    podium = Rectangle(width=1.5, height=0.8, color=TKK_DIM,
                       fill_color=TKK_DIM, fill_opacity=0.15,
                       stroke_width=1)
    podium.next_to(person, DOWN, buff=0.05)
    group = VGroup(person, podium).move_to(position + UP * 2)

    scene.play(FadeIn(group), run_time=0.3)

    # Stamp SAFE
    s = stamp_slam(scene, safe_text_content, position=position)

    scene.wait(0.3)

    # Person fades (disappeared for a year)
    scene.play(person.animate.set_opacity(0.1).shift(RIGHT * 2),
               run_time=0.8)

    return group, s
