#!/usr/bin/env python3
"""Radium Girls Scene 2 — Visual Storytelling Prototype.

Animated watch dial + paintbrush doing "lip, dip, paint" cycle.
Physical motion, minimal text, 1920s factory warmth + radium glow.
"""

import os, sys
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from manim import (
    Scene, Text, VGroup, Rectangle, RoundedRectangle, Circle,
    Line, Arrow, DashedLine, Dot, Polygon, Ellipse, Square, Arc,
    FadeIn, FadeOut, GrowFromCenter, Write, Create, DrawBorderThenFill,
    AnimationGroup, LaggedStart, Flash, Succession,
    MoveAlongPath, MoveToTarget,
    config, UP, DOWN, LEFT, RIGHT, ORIGIN,
    WHITE, BLACK, rate_functions, DEGREES, PI,
    TracedPath,
)
import numpy as np

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.frame_width = 9
config.frame_height = 16
config.background_color = "#1A1610"
config.disable_caching = True

# 1920s factory warmth palette
CREAM = "#F5E6C8"
SEPIA = "#D4B896"
SEPIA_DARK = "#8B7355"
WARM_BG = "#1A1610"
WARM_BG2 = "#241E14"
FACTORY = "#2A2218"

# Radium glow
RADIUM = "#39FF14"
RADIUM_DIM = "#1A8A0A"
RADIUM_GLOW = "#2AE610"
RADIUM_FAINT = "#1A4A0A"

GOLD_WARM = "#D4A84B"
MUTED = "#7B6B55"
SAFE_W = 8.0


def safe_text(content, **kwargs):
    t = Text(content, **kwargs)
    if t.width > SAFE_W: t.scale(SAFE_W / t.width)
    return t


class RadiumVisualScene2(Scene):
    def construct(self):
        # ── Background: warm factory tone ──
        bg = Rectangle(width=12, height=20, fill_color=WARM_BG, fill_opacity=1, stroke_width=0)
        bg2 = Circle(radius=6, fill_color=WARM_BG2, fill_opacity=0.3, stroke_width=0).move_to(UP * 2)
        self.add(bg, bg2)

        # Scene label (tiny, top)
        label = Text("THE METHOD", font="Inter", font_size=20, color=MUTED, weight="BOLD")
        label.move_to(UP * 7.5)
        self.add(label)

        # ══════════════════════════════════════════════
        # WATCH DIAL — cream circle with tick marks
        # ══════════════════════════════════════════════
        dial_r = 2.8
        dial_center = UP * 2.5

        # Dial face
        dial_face = Circle(radius=dial_r, fill_color=CREAM, fill_opacity=0.12,
                           stroke_color=SEPIA, stroke_width=3)
        dial_face.move_to(dial_center)

        # Inner ring
        dial_inner = Circle(radius=dial_r * 0.92, fill_color=CREAM, fill_opacity=0.05,
                            stroke_color=SEPIA_DARK, stroke_width=1)
        dial_inner.move_to(dial_center)

        # Tick marks (12 hour positions)
        ticks = VGroup()
        for i in range(12):
            angle = PI/2 - i * 2*PI/12
            outer = dial_center + dial_r * 0.85 * np.array([np.cos(angle), np.sin(angle), 0])
            inner = dial_center + dial_r * 0.72 * np.array([np.cos(angle), np.sin(angle), 0])
            w = 2.5 if i % 3 == 0 else 1.5
            tick = Line(inner, outer, color=SEPIA_DARK, stroke_width=w)
            ticks.add(tick)

        # Minute ticks (60 positions, very faint)
        min_ticks = VGroup()
        for i in range(60):
            if i % 5 == 0: continue
            angle = PI/2 - i * 2*PI/60
            outer = dial_center + dial_r * 0.85 * np.array([np.cos(angle), np.sin(angle), 0])
            inner = dial_center + dial_r * 0.80 * np.array([np.cos(angle), np.sin(angle), 0])
            min_ticks.add(Line(inner, outer, color=SEPIA_DARK, stroke_width=0.5).set_opacity(0.4))

        # Center dot
        center_dot = Dot(dial_center, radius=0.08, color=SEPIA_DARK)

        dial_group = VGroup(dial_face, dial_inner, min_ticks, ticks, center_dot)

        # ══════════════════════════════════════════════
        # PAINT POT — small glowing green circle below dial
        # ══════════════════════════════════════════════
        pot_center = DOWN * 1.5 + RIGHT * 2
        pot = Circle(radius=0.5, fill_color="#1A2A0A", fill_opacity=0.9,
                     stroke_color=RADIUM_DIM, stroke_width=2)
        pot.move_to(pot_center)
        pot_glow = Circle(radius=0.7, fill_color=RADIUM, fill_opacity=0.08, stroke_width=0)
        pot_glow.move_to(pot_center)
        pot_surface = Circle(radius=0.35, fill_color=RADIUM_FAINT, fill_opacity=0.6,
                             stroke_width=0)
        pot_surface.move_to(pot_center)
        pot_label = Text("Ra-226", font="Inter", font_size=14, color=RADIUM_DIM)
        pot_label.next_to(pot, DOWN, buff=0.15)
        paint_pot = VGroup(pot_glow, pot, pot_surface, pot_label)

        # ══════════════════════════════════════════════
        # LIP position — small mouth shape above dial
        # ══════════════════════════════════════════════
        lip_center = UP * 6 + LEFT * 1
        lip_upper = Arc(radius=0.4, start_angle=PI*0.1, angle=PI*0.8,
                        color=SEPIA, stroke_width=2)
        lip_upper.move_to(lip_center + UP * 0.05)
        lip_lower = Arc(radius=0.35, start_angle=-PI*0.8, angle=PI*0.6,
                        color=SEPIA, stroke_width=2)
        lip_lower.move_to(lip_center + DOWN * 0.1)
        lips = VGroup(lip_upper, lip_lower)

        # ══════════════════════════════════════════════
        # PAINTBRUSH — moves through the cycle
        # ══════════════════════════════════════════════
        brush_len = 1.2

        def make_brush(pos, color=SEPIA_DARK, tip_color=None):
            handle = Rectangle(width=0.1, height=brush_len*0.6,
                               fill_color=color, fill_opacity=1,
                               stroke_color="#5A4A30", stroke_width=1)
            ferrule = Rectangle(width=0.13, height=brush_len*0.08,
                                fill_color="#888", fill_opacity=1, stroke_width=0)
            ferrule.next_to(handle, DOWN, buff=0)
            tc = tip_color or SEPIA_DARK
            tip = Polygon(
                np.array([-0.05, 0, 0]),
                np.array([0.05, 0, 0]),
                np.array([0, -brush_len*0.25, 0]),
                fill_color=tc, fill_opacity=1,
                stroke_color=tc, stroke_width=1,
            )
            tip.next_to(ferrule, DOWN, buff=0)
            grp = VGroup(handle, ferrule, tip)
            grp.move_to(pos)
            return grp

        brush = make_brush(lip_center + DOWN * 0.8)

        # ══════════════════════════════════════════════
        # RADIUM PAINT STROKES on dial — pre-built
        # ══════════════════════════════════════════════
        def number_stroke(num_text, angle_idx, glow_opacity=0.15):
            """A radium-green number painted on the dial."""
            angle = PI/2 - angle_idx * 2*PI/12
            pos = dial_center + dial_r * 0.55 * np.array([np.cos(angle), np.sin(angle), 0])
            txt = Text(num_text, font="Inter", font_size=32, color=RADIUM, weight="BOLD")
            txt.move_to(pos)
            glow = Circle(radius=0.3, fill_color=RADIUM, fill_opacity=glow_opacity, stroke_width=0)
            glow.move_to(pos)
            return VGroup(glow, txt)

        # Numbers to paint in sequence
        numbers_to_paint = [
            ("12", 0), ("3", 3), ("6", 6), ("9", 9),
            ("1", 1), ("2", 2), ("4", 4), ("5", 5),
        ]

        # ══════════════════════════════════════════════
        # COUNTER — bottom corner
        # ══════════════════════════════════════════════
        counter_pos = DOWN * 5.5 + RIGHT * 2.5

        # ══════════════════════════════════════════════
        # RHYTHM TEXT — "Lip. Dip. Paint."
        # ══════════════════════════════════════════════
        rhythm_pos = DOWN * 5

        # ══════════════════════════════════════════════
        # ANIMATION SEQUENCE
        # ══════════════════════════════════════════════

        # Phase 0: Establish scene (0-1.5s)
        self.play(FadeIn(dial_group, scale=0.9), run_time=0.8)            # t=0.8
        self.play(FadeIn(paint_pot, scale=0.8), run_time=0.4)            # t=1.2
        self.play(FadeIn(lips), run_time=0.3)                             # t=1.5
        self.play(FadeIn(brush, shift=DOWN * 0.3), run_time=0.4)         # t=1.9

        # Cumulative glow on dial
        dial_glow = Circle(radius=dial_r * 1.1, fill_color=RADIUM, fill_opacity=0.0,
                           stroke_width=0)
        dial_glow.move_to(dial_center)
        self.add(dial_glow)

        painted_count = 0

        # ── CYCLE 1: Slow (2 numbers) ── ~2s
        for num_idx in range(2):
            num_text, angle_idx = numbers_to_paint[num_idx]

            # LIP — brush moves to lips
            lip_txt = safe_text("Lip.", font="Bebas Neue", font_size=40, color=SEPIA)
            lip_txt.move_to(rhythm_pos)

            brush.generate_target()
            brush.target.move_to(lip_center + DOWN * 0.8)
            self.play(MoveToTarget(brush), run_time=0.25)
            self.play(FadeIn(lip_txt, run_time=0.15))
            self.play(FadeOut(lip_txt, run_time=0.1))

            # DIP — brush moves to pot
            dip_txt = safe_text("Dip.", font="Bebas Neue", font_size=40, color=RADIUM_DIM)
            dip_txt.move_to(rhythm_pos)

            brush.generate_target()
            brush.target.move_to(pot_center + UP * 0.6)
            self.play(MoveToTarget(brush), run_time=0.25)
            # Brush tip turns green
            brush[2].set_fill(RADIUM, opacity=0.9)
            brush[2].set_stroke(RADIUM, width=1)
            self.play(FadeIn(dip_txt, run_time=0.15))
            self.play(FadeOut(dip_txt, run_time=0.1))

            # PAINT — brush moves to dial position and paints number
            paint_txt = safe_text("Paint.", font="Bebas Neue", font_size=40, color=RADIUM)
            paint_txt.move_to(rhythm_pos)

            angle = PI/2 - angle_idx * 2*PI/12
            paint_pos = dial_center + dial_r * 0.55 * np.array([np.cos(angle), np.sin(angle), 0])

            brush.generate_target()
            brush.target.move_to(paint_pos + UP * 0.5)
            self.play(MoveToTarget(brush), run_time=0.2)

            stroke = number_stroke(num_text, angle_idx, 0.12 + num_idx * 0.03)
            self.play(FadeIn(stroke, scale=0.5), FadeIn(paint_txt, run_time=0.15), run_time=0.2)
            self.play(FadeOut(paint_txt, run_time=0.1))

            painted_count += 1

        # Counter update
        count1 = Text(f"{painted_count}", font="Bebas Neue", font_size=36, color=RADIUM_DIM)
        count1.move_to(counter_pos)
        self.play(FadeIn(count1), run_time=0.15)

        # ── CYCLE 2: Medium speed (3 numbers) ── ~1.5s
        for num_idx in range(2, 5):
            num_text, angle_idx = numbers_to_paint[num_idx]
            # LIP
            brush.generate_target()
            brush.target.move_to(lip_center + DOWN * 0.8)
            self.play(MoveToTarget(brush), run_time=0.15)
            # DIP
            brush.generate_target()
            brush.target.move_to(pot_center + UP * 0.6)
            self.play(MoveToTarget(brush), run_time=0.15)
            brush[2].set_fill(RADIUM, opacity=0.9)
            # PAINT
            angle = PI/2 - angle_idx * 2*PI/12
            paint_pos = dial_center + dial_r * 0.55 * np.array([np.cos(angle), np.sin(angle), 0])
            brush.generate_target()
            brush.target.move_to(paint_pos + UP * 0.5)
            self.play(MoveToTarget(brush), run_time=0.12)
            stroke = number_stroke(num_text, angle_idx, 0.12 + num_idx * 0.03)
            self.play(FadeIn(stroke, scale=0.5), run_time=0.12)
            painted_count += 1

        # Counter jump
        self.remove(count1)
        count2 = Text("47", font="Bebas Neue", font_size=40, color=RADIUM_DIM)
        count2.move_to(counter_pos)
        self.play(FadeIn(count2, scale=1.2), run_time=0.15)

        # Glow building
        self.play(dial_glow.animate.set_opacity(0.04), run_time=0.3)

        # ── CYCLE 3: Fast (3 numbers, rapid) ── ~1s
        for num_idx in range(5, 8):
            num_text, angle_idx = numbers_to_paint[num_idx]
            # Rapid cycle — no separate lip/dip, just flash to positions
            brush.generate_target()
            brush.target.move_to(lip_center + DOWN * 0.8)
            self.play(MoveToTarget(brush), run_time=0.08)
            brush.generate_target()
            brush.target.move_to(pot_center + UP * 0.6)
            self.play(MoveToTarget(brush), run_time=0.08)
            brush[2].set_fill(RADIUM, opacity=0.95)
            angle = PI/2 - angle_idx * 2*PI/12
            paint_pos = dial_center + dial_r * 0.55 * np.array([np.cos(angle), np.sin(angle), 0])
            brush.generate_target()
            brush.target.move_to(paint_pos + UP * 0.5)
            self.play(MoveToTarget(brush), run_time=0.06)
            stroke = number_stroke(num_text, angle_idx, 0.15 + num_idx * 0.02)
            self.play(FadeIn(stroke, scale=0.5), run_time=0.06)

        # Counter jump to 186
        self.remove(count2)
        count3 = Text("186", font="Bebas Neue", font_size=44, color=RADIUM)
        count3.move_to(counter_pos)
        self.play(FadeIn(count3, scale=1.3), run_time=0.15)

        # Glow intensifies
        self.play(dial_glow.animate.set_opacity(0.08), run_time=0.3)

        # ── FINALE: dial pulses with radium ──
        self.remove(count3)
        hundreds = Text("HUNDREDS", font="Bebas Neue", font_size=48, color=RADIUM)
        hundreds.move_to(counter_pos)
        self.play(FadeIn(hundreds, scale=1.2), run_time=0.3)

        # Final text
        rhythm_final = safe_text("Hundreds of times a day.", font="DM Serif Display",
                                font_size=38, color=SEPIA)
        rhythm_final.move_to(DOWN * 6.5)

        # Full dial radium pulse
        self.play(
            dial_glow.animate.set_opacity(0.15),
            FadeIn(rhythm_final, shift=UP * 0.04),
            run_time=0.6,
        )

        # Pulse effect — glow breathes
        self.play(dial_glow.animate.set_opacity(0.08), run_time=0.4)
        self.play(dial_glow.animate.set_opacity(0.18), run_time=0.4)
        self.play(dial_glow.animate.set_opacity(0.10), run_time=0.3)

        self.wait(0.7)  # hold


# ── MAIN ──
if __name__ == "__main__":
    import shutil

    output_dir = Path(__file__).parent

    if "--preview" in sys.argv:
        config.save_last_frame = True
        config.format = "png"
        config.output_file = "radium_visual_proto"
        config.media_dir = str(output_dir / "media")
        RadiumVisualScene2().render()
        for p in Path(config.media_dir).rglob("radium_visual_proto*"):
            if p.suffix == ".png":
                dst = output_dir / "previews" / "radium_visual_proto.png"
                dst.parent.mkdir(exist_ok=True)
                shutil.copy2(str(p), str(dst))
                print(f"OK: {dst} ({dst.stat().st_size//1024} KB)")
                break
        sys.exit(0)

    # Render video
    config.output_file = "radium_visual_proto"
    config.media_dir = str(output_dir / "media")
    RadiumVisualScene2().render()

    # Find rendered file and copy to output location
    for mp4 in Path(config.media_dir).rglob("radium_visual_proto.mp4"):
        dst = output_dir / "radium_visual_proto.mp4"
        shutil.copy2(str(mp4), str(dst))
        mb = dst.stat().st_size / 1024 / 1024
        print(f"\nRENDER COMPLETE: {dst} ({mb:.1f} MB)")

        # Also save last frame as preview
        config.save_last_frame = True
        config.format = "png"
        config.output_file = "radium_visual_proto_frame"
        RadiumVisualScene2().render()
        for p in Path(config.media_dir).rglob("radium_visual_proto_frame*"):
            if p.suffix == ".png":
                prev = output_dir / "previews" / "radium_visual_proto.png"
                prev.parent.mkdir(exist_ok=True)
                shutil.copy2(str(p), str(prev))
                print(f"Preview: {prev}")
                break
        break
