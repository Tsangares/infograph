"""Bronze Age Collapse — 3D Globe Prototype

Tests: 3D camera movement, satellite map imagery, geographic overlays,
animated trade routes, collapse visualization.
"""

from manim import *
import numpy as np

# Colors
GOLD = "#FFD700"
RED_ACCENT = "#FF2D55"
WHITE_SOFT = "#EAEAF0"
BG_DARK = "#0a0a0f"
EMPIRE_COLORS = {
    "hittite": "#FF6B6B",
    "mycenae": "#4ECDC4",
    "egypt": "#FFD93D",
    "babylon": "#6C5CE7",
    "cyprus": "#A8E6CF",
}

def safe_text(content, **kwargs):
    try:
        return Text(content, **kwargs)
    except Exception:
        kwargs.pop("font", None)
        return Text(content, **kwargs)


class Scene1_3DGlobe(ThreeDScene):
    """Opening: 3D globe rotating to Mediterranean, then zoom into the region."""

    def construct(self):
        self.camera.background_color = BG_DARK

        # Create a sphere (globe)
        sphere = Sphere(radius=2, resolution=(32, 32))
        sphere.set_color(BLUE_D)
        sphere.set_opacity(0.8)

        # Add the map as a texture-like overlay
        # Since manim can't texture-map easily, we'll use a flat map approach
        # with 3D camera movement to simulate globe feel

        # Start with the globe
        self.set_camera_orientation(phi=70 * DEGREES, theta=-30 * DEGREES, zoom=0.7)

        # Title
        title = safe_text("1177 BC", font="Bebas Neue", font_size=120, color=RED_ACCENT)
        title.to_edge(UP, buff=0.5)
        self.add_fixed_in_frame_mobjects(title)

        subtitle = safe_text("Every civilization on Earth\ncollapsed at the same time.",
                           font="Inter", font_size=36, color=WHITE_SOFT)
        subtitle.next_to(title, DOWN, buff=0.4)
        self.add_fixed_in_frame_mobjects(subtitle)

        self.play(Create(sphere), run_time=1.0)
        self.play(FadeIn(title), run_time=0.5)
        self.play(FadeIn(subtitle), run_time=0.5)

        # Rotate globe
        self.begin_ambient_camera_rotation(rate=0.3)
        self.wait(1.5)
        self.stop_ambient_camera_rotation()

        # Zoom in
        self.play(
            self.camera.animate.set_euler_angles(phi=60*DEGREES, theta=0),
            sphere.animate.scale(2),
            run_time=1.5,
        )
        self.wait(0.5)


class Scene2_MapWithEmpires(Scene):
    """Mediterranean map with empire locations marked, then collapsing."""

    def construct(self):
        self.camera.background_color = BG_DARK

        # Load map
        try:
            bg_map = ImageMobject("/opt/tkk/vidgen/assets/earth_topo.jpg")
            bg_map.scale_to_fit_width(14)
            bg_map.set_opacity(0.6)
            # Shift to center on Mediterranean
            bg_map.shift(LEFT * 1 + UP * 0.5)
            self.add(bg_map)
        except Exception:
            # Fallback: dark gradient
            bg = Rectangle(width=14, height=25, fill_color=BG_DARK, fill_opacity=1, stroke_width=0)
            self.add(bg)

        # Dark overlay for readability
        overlay = Rectangle(width=14, height=25, fill_color=BLACK, fill_opacity=0.4, stroke_width=0)
        self.add(overlay)

        # Empire markers (approximate positions on a Mediterranean map)
        empires = [
            {"name": "HITTITES", "pos": UP * 1.5 + RIGHT * 1.5, "color": EMPIRE_COLORS["hittite"]},
            {"name": "MYCENAE", "pos": UP * 0.5 + LEFT * 0.5, "color": EMPIRE_COLORS["mycenae"]},
            {"name": "EGYPT", "pos": DOWN * 1.5 + RIGHT * 0.5, "color": EMPIRE_COLORS["egypt"]},
            {"name": "BABYLON", "pos": UP * 0.5 + RIGHT * 3, "color": EMPIRE_COLORS["babylon"]},
        ]

        empire_dots = VGroup()
        empire_labels = VGroup()

        for emp in empires:
            # Glowing dot
            dot = Dot(point=emp["pos"], radius=0.15, color=emp["color"])
            glow = Dot(point=emp["pos"], radius=0.3, color=emp["color"], fill_opacity=0.3)
            label = safe_text(emp["name"], font="Inter", font_size=24, color=emp["color"], weight="BOLD")
            label.next_to(dot, DOWN, buff=0.15)
            empire_dots.add(VGroup(glow, dot))
            empire_labels.add(label)

        # Trade routes (lines between empires)
        routes = VGroup()
        positions = [emp["pos"] for emp in empires]
        for i in range(len(positions)):
            for j in range(i+1, len(positions)):
                line = Line(positions[i], positions[j], stroke_width=1.5, color=GOLD, stroke_opacity=0.4)
                routes.add(line)

        # Animate empire appearance
        self.play(LaggedStart(*[FadeIn(d) for d in empire_dots], lag_ratio=0.2), run_time=1.5)
        self.play(LaggedStart(*[FadeIn(l) for l in empire_labels], lag_ratio=0.15), run_time=1.0)
        self.play(LaggedStart(*[Create(r) for r in routes], lag_ratio=0.1), run_time=1.0)

        # Text overlay
        connected = safe_text("CONNECTED", font="Bebas Neue", font_size=80, color=GOLD)
        connected.to_edge(UP, buff=1)
        self.play(FadeIn(connected), run_time=0.5)
        self.wait(1)

        # COLLAPSE — dots turn red and flash out
        self.play(
            connected.animate.set_color(RED_ACCENT),
            *[d[1].animate.set_color(RED) for d in empire_dots],
            *[r.animate.set_stroke(color=RED, opacity=0.8) for r in routes],
            run_time=0.5,
        )

        # Routes break
        self.play(
            *[FadeOut(r) for r in routes],
            Flash(empire_dots[0][1], color=RED, line_length=0.4, flash_radius=0.5),
            Flash(empire_dots[1][1], color=RED, line_length=0.4, flash_radius=0.5),
            Flash(empire_dots[2][1], color=RED, line_length=0.4, flash_radius=0.5),
            Flash(empire_dots[3][1], color=RED, line_length=0.4, flash_radius=0.5),
            run_time=0.8,
        )

        # Empire dots fade
        collapsed = safe_text("COLLAPSED", font="Bebas Neue", font_size=80, color=RED_ACCENT)
        collapsed.to_edge(UP, buff=1)
        self.play(
            ReplacementTransform(connected, collapsed),
            *[FadeOut(d, shift=DOWN * 0.3) for d in empire_dots],
            *[FadeOut(l) for l in empire_labels],
            run_time=1.0,
        )
        self.wait(1)


class Scene3_TradeRoutes(Scene):
    """Animated trade routes with resources flowing, then breaking."""

    def construct(self):
        self.camera.background_color = BG_DARK

        # Supply chain visualization
        title = safe_text("THE SUPPLY CHAIN", font="Inter", font_size=28, color=WHITE_SOFT, weight="BOLD")
        title.to_edge(UP, buff=1)

        # Three resource nodes
        resources = [
            {"label": "TIN", "sub": "Afghanistan", "pos": LEFT * 3.5 + UP * 0.5, "color": "#A8E6CF"},
            {"label": "COPPER", "sub": "Cyprus", "pos": ORIGIN, "color": "#FFD93D"},
            {"label": "GRAIN", "sub": "Egypt", "pos": RIGHT * 3.5 + UP * 0.5, "color": "#FF6B6B"},
        ]

        nodes = VGroup()
        for res in resources:
            box = RoundedRectangle(
                width=2.5, height=1.2, corner_radius=0.15,
                fill_color=res["color"], fill_opacity=0.15,
                stroke_color=res["color"], stroke_width=2,
            ).move_to(res["pos"])

            label = safe_text(res["label"], font="Bebas Neue", font_size=48, color=res["color"])
            label.move_to(box.get_center() + UP * 0.15)

            sub = safe_text(res["sub"], font="Inter", font_size=20, color=WHITE_SOFT)
            sub.next_to(label, DOWN, buff=0.05)

            nodes.add(VGroup(box, label, sub))

        # Arrows connecting them
        arrow1 = Arrow(resources[0]["pos"] + RIGHT * 1.3, resources[1]["pos"] + LEFT * 1.3,
                       color=GOLD, stroke_width=3, buff=0.1)
        arrow2 = Arrow(resources[1]["pos"] + RIGHT * 1.3, resources[2]["pos"] + LEFT * 1.3,
                       color=GOLD, stroke_width=3, buff=0.1)

        # "ONE BREAK" text
        break_text = safe_text("ONE BREAK", font="Bebas Neue", font_size=90, color=RED_ACCENT)
        break_text.move_to(DOWN * 2)

        starve_text = safe_text("Everything starved.", font="Inter", font_size=36, color=WHITE_SOFT)
        starve_text.next_to(break_text, DOWN, buff=0.3)

        self.play(FadeIn(title), run_time=0.3)
        self.play(LaggedStart(*[FadeIn(n) for n in nodes], lag_ratio=0.3), run_time=1.5)
        self.play(GrowArrow(arrow1), GrowArrow(arrow2), run_time=0.8)
        self.wait(0.5)

        # Break the chain — X through middle
        x_mark = Cross(scale_factor=0.8, stroke_color=RED, stroke_width=8)
        x_mark.move_to(arrow1.get_center())

        self.play(
            Create(x_mark),
            arrow1.animate.set_color(RED).set_opacity(0.3),
            run_time=0.4,
        )
        self.play(
            FadeIn(break_text, scale=1.2),
            nodes[0][0].animate.set_stroke(color=RED, opacity=0.3),
            run_time=0.5,
        )
        self.play(FadeIn(starve_text), run_time=0.5)
        self.wait(1.5)


class Scene4_SoundFamiliar(Scene):
    """The closer — modern parallel. Minimal."""

    def construct(self):
        self.camera.background_color = BG_DARK

        # Letterbox
        top_bar = Rectangle(width=14, height=0.6, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        top_bar.to_edge(UP, buff=0)
        bot_bar = Rectangle(width=14, height=0.6, fill_color=BLACK, fill_opacity=1, stroke_width=0)
        bot_bar.to_edge(DOWN, buff=0)
        self.add(top_bar, bot_bar)

        # Divider
        line = Line(LEFT * 3, RIGHT * 3, stroke_width=1, color=GOLD, stroke_opacity=0.5)
        line.shift(UP * 0.5)

        # Main text
        text1 = safe_text("A globalized system so connected", font="DM Serif Display", font_size=40, color=WHITE_SOFT)
        text2 = safe_text("that when one part failed,", font="DM Serif Display", font_size=40, color=WHITE_SOFT)
        text3 = safe_text("everything fell.", font="DM Serif Display", font_size=48, color=GOLD)

        text_group = VGroup(text1, text2, text3).arrange(DOWN, buff=0.3)
        text_group.move_to(ORIGIN)

        # Sound familiar?
        familiar = safe_text("Sound familiar?", font="Inter", font_size=56, color=RED_ACCENT, weight="BOLD")
        familiar.move_to(DOWN * 2.5)

        self.play(Create(line), run_time=0.8)
        self.play(FadeIn(text1), run_time=0.8)
        self.play(FadeIn(text2), run_time=0.6)
        self.play(FadeIn(text3), run_time=0.8)
        self.wait(1)
        self.play(FadeIn(familiar, shift=UP * 0.3), run_time=0.8)
        self.wait(2)

        # Fade to black
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1.5)
        self.wait(1)


if __name__ == "__main__":
    import subprocess, sys, os
    os.chdir("/opt/tkk/vidgen")

    scenes = ["Scene1_3DGlobe", "Scene2_MapWithEmpires", "Scene3_TradeRoutes", "Scene4_SoundFamiliar"]

    for scene in scenes:
        print(f"Rendering {scene}...", flush=True)
        cmd = [sys.executable, "-m", "manim", "render", "-qh", "--fps", "30",
               "--media_dir", "media", "-o", f"proto_{scene}",
               "bronze_age_3d_prototype.py", scene]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"  FAILED: {result.stderr[-300:]}", flush=True)
        else:
            print(f"  OK", flush=True)

    # Save last frames as previews
    for scene in scenes:
        print(f"Preview {scene}...", flush=True)
        cmd = [sys.executable, "-m", "manim", "render", "-qh", "--fps", "30",
               "--media_dir", "previews", "--save_last_frame", "--write_to_movie", "False",
               "-o", f"proto_{scene}", "bronze_age_3d_prototype.py", scene]
        subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    print("Done!")
