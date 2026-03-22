"""TKK Scene Templates.

Pre-built full scene layouts that the engineer calls with data.
Each template is a function that constructs a complete manim Scene.

Usage in a video file:
    from scene_templates import HookScene, CascadeScene, PunchScene

    class Scene1(HookScene):
        LABEL = "THE HOOK"
        HEADLINE = "3,000 → 111"
        SUBTEXT = "In less than a decade."
        HEADLINE_COLOR = TKK_GOLD
"""

import numpy as np
from manim import *
from anim_primitives import *  # includes safe_place, ZONE_* constants


class TKKBaseScene(Scene):
    """Base scene with standard TKK setup."""
    BG_COLOR = TKK_BG
    LABEL = ""
    DURATION = 5.0  # total scene duration
    PROGRESS = 0.0  # 0-1, position in the overall video

    def setup(self):
        super().setup()
        setup_portrait_scene(self, self.BG_COLOR)
        if self.PROGRESS > 0:
            add_progress_bar(self, self.PROGRESS)

    def add_label(self):
        if self.LABEL:
            label = scene_label(self.LABEL)
            self.play(FadeIn(label, shift=DOWN * 0.2), run_time=0.3)
            return label
        return None


class VisualSceneBase(TKKBaseScene):
    """Base scene for visual-first (v2+) videos.

    Provides SVG loading, icon grid builder, and standard dark background setup.
    Don't template specific visual patterns — each topic is unique.
    Just make the SVG workflow easier.

    Usage:
        class Scene1_Hook(VisualSceneBase):
            LABEL = "THE HOOK"
            DURATION = 5.0

            def construct(self):
                self.setup_bg()
                factory = self.svg("factory.svg", height=4)
                workers = self.icon_grid("person.svg", 3, 5, height=1.5)
                ...
    """
    GRID_OPACITY = 0.03

    def setup_bg(self, grid_opacity=None):
        """Add gradient background + grid lines. Call at start of construct()."""
        from anim_primitives import TKK_BG
        bg = Rectangle(width=12, height=20, fill_color=TKK_BG, fill_opacity=1,
                        stroke_width=0)
        glow = Circle(radius=5, fill_color="#121828", fill_opacity=0.08,
                       stroke_width=0).move_to(UP * 2)
        self.add(VGroup(bg, glow))

        opacity = grid_opacity or self.GRID_OPACITY
        lines = VGroup()
        grid_color = "#1A2030"
        for i in range(13):
            y = -8 + i * 16 / 12
            lines.add(Line(LEFT*5, RIGHT*5, color=grid_color, stroke_width=0.5
                           ).move_to(UP*y).set_opacity(opacity))
        for j in range(7):
            x = -4.5 + j * 9 / 6
            lines.add(Line(DOWN*8, UP*8, color=grid_color, stroke_width=0.5
                           ).move_to(RIGHT*x).set_opacity(opacity))
        self.add(lines)

    def svg(self, filename, color=None, height=2.0):
        """Load SVG from assets library. Shorthand for load_svg()."""
        return load_svg(filename, color=color, height=height)

    def icon_grid(self, svg_file, rows, cols, color=TKK_WHITE, height=0.7,
                  spacing_x=1.0, spacing_y=1.0, opacity=0.5):
        """Build a grid of repeated SVG icons. Shorthand for svg_grid()."""
        return svg_grid(svg_file, rows, cols, color=color, icon_height=height,
                        spacing_x=spacing_x, spacing_y=spacing_y, opacity=opacity)


class HookScene(TKKBaseScene):
    """Scene 1 pattern: Big headline + subtext. The scroll-stopper.

    Override: HEADLINE, SUBTEXT, HEADLINE_COLOR
    """
    HEADLINE = "HEADLINE"
    SUBTEXT = "Subtext goes here."
    HEADLINE_COLOR = TKK_GOLD
    SUBTEXT_COLOR = TKK_DIM

    def construct(self):
        label = self.add_label()

        h = headline(self.HEADLINE, color=self.HEADLINE_COLOR, size=90)
        safe_place(h, "MID")  # Center of frame, not pushed to top
        self.play(FadeIn(h, scale=1.1), run_time=0.5)

        d = divider()
        d.next_to(h, DOWN, buff=0.6)
        self.play(Create(d), run_time=0.4)

        sub = caption(self.SUBTEXT, color=self.SUBTEXT_COLOR, size=40)
        safe_place(sub, "LOWER", x=0)  # Push subtext to lower zone
        self.play(FadeIn(sub, shift=UP * 0.3), run_time=0.5)

        self.wait(max(0.1, self.DURATION - 1.7))


class StatScene(TKKBaseScene):
    """Big number reveal with context.

    Override: NUMBER, UNIT, DESCRIPTION
    """
    NUMBER = "0"
    UNIT = ""
    DESCRIPTION = ""
    NUMBER_COLOR = TKK_GOLD

    def construct(self):
        label = self.add_label()

        fc = fact_callout(self.NUMBER, self.UNIT, self.DESCRIPTION,
                          number_color=self.NUMBER_COLOR)
        safe_place(fc, "MID")  # Center of frame
        self.play(FadeIn(fc[0], scale=1.2), run_time=0.5)
        self.play(FadeIn(fc[1], shift=UP * 0.2), run_time=0.4)

        self.wait(max(0.1, self.DURATION - 1.2))


class CascadeScene(TKKBaseScene):
    """Rapid-fire stacking list — each item slams in.

    Override: ITEMS, ITEM_COLORS, HEADER
    """
    HEADER = ""
    ITEMS = []
    ITEM_COLORS = None
    STAGGER = 0.35

    def construct(self):
        label = self.add_label()

        if self.HEADER:
            h = caption(self.HEADER, color=TKK_WHITE, size=44)
            safe_place(h, "UPPER")
            self.play(FadeIn(h), run_time=0.3)

        cl, anims = cascade_list(self.ITEMS, self.ITEM_COLORS, size=36)
        safe_place(cl, "LOWER")  # Lists in lower zone, not center
        for anim in anims:
            self.play(anim, run_time=self.STAGGER)

        self.wait(max(0.1, self.DURATION - len(anims) * self.STAGGER - 0.3))


class CompareScene(TKKBaseScene):
    """Split-screen comparison.

    Override: LEFT_TEXT, RIGHT_TEXT, LEFT_LABEL, RIGHT_LABEL
    """
    LEFT_TEXT = ""
    RIGHT_TEXT = ""
    LEFT_LABEL = ""
    RIGHT_LABEL = ""
    LEFT_COLOR = TKK_DIM
    RIGHT_COLOR = TKK_RED

    def construct(self):
        label = self.add_label()

        comp = split_compare(self.LEFT_TEXT, self.RIGHT_TEXT,
                             self.LEFT_LABEL, self.RIGHT_LABEL,
                             self.LEFT_COLOR, self.RIGHT_COLOR)
        comp.move_to(ORIGIN)
        self.play(FadeIn(comp, lag_ratio=0.3), run_time=0.8)

        self.wait(max(0.1, self.DURATION - 1.1))


class DropScene(TKKBaseScene):
    """Population/value dramatic drop visualization.

    Override: START_VAL, END_VAL, DROP_LABEL
    """
    START_VAL = 100
    END_VAL = 10
    DROP_LABEL = ""

    def construct(self):
        label = self.add_label()

        pd = population_drop(self.START_VAL, self.END_VAL,
                             label=self.DROP_LABEL)
        pd.move_to(ORIGIN)
        self.play(FadeIn(pd[0], shift=UP * 0.5), run_time=0.4)  # start bar
        self.play(FadeIn(pd[2]), run_time=0.3)  # start label
        self.play(GrowArrow(pd[4]), run_time=0.4)  # arrow
        self.play(FadeIn(pd[1], shift=DOWN * 0.3), FadeIn(pd[3]),
                  run_time=0.4)  # end bar + label
        if len(pd) > 5:
            self.play(FadeIn(pd[5]), run_time=0.3)  # drop label

        self.wait(max(0.1, self.DURATION - 2.1))


class TimelineScene(TKKBaseScene):
    """Timeline with dated markers.

    Override: START_YEAR, END_YEAR, MARKERS, COMMENTARY
    """
    START_YEAR = 1800
    END_YEAR = 2000
    MARKERS = []
    COMMENTARY = ""

    def construct(self):
        label = self.add_label()

        tl = timeline(self.START_YEAR, self.END_YEAR, self.MARKERS)
        tl.move_to(UP * 1)
        self.play(Create(tl[0]), run_time=0.5)  # line
        self.play(FadeIn(tl[1]), FadeIn(tl[2]), run_time=0.3)  # year labels

        # Markers one by one
        for i in range(3, len(tl), 3):
            if i + 2 < len(tl):
                self.play(FadeIn(tl[i]), FadeIn(tl[i+1]),
                          FadeIn(tl[i+2]), run_time=0.4)

        if self.COMMENTARY:
            c = caption(self.COMMENTARY, color=TKK_WHITE, size=36)
            c.next_to(tl, DOWN, buff=1.0)
            self.play(FadeIn(c, shift=UP * 0.2), run_time=0.5)

        self.wait(max(0.1, self.DURATION - 2.0))


class PunchScene(TKKBaseScene):
    """Cinematic closer — letterboxed, slow reveal.

    Override: LINES, LINE_COLORS, LINE_SIZES
    """
    LINES = [""]
    LINE_COLORS = None
    LINE_SIZES = None
    HOLD = 3.0

    def construct(self):
        closer = letterbox_closer(self.LINES, self.LINE_COLORS, self.LINE_SIZES)
        bars = VGroup(closer[0], closer[1])
        texts = closer[2]

        self.play(FadeIn(bars), run_time=0.5)

        for text_mob in texts:
            self.play(FadeIn(text_mob, shift=UP * 0.2), run_time=0.8)
            self.wait(0.3)

        self.wait(self.HOLD)
        # Fade everything out
        all_mobs = [m for m in self.mobjects if isinstance(m, VMobject)]
        if all_mobs:
            self.play(*[FadeOut(m) for m in all_mobs], run_time=1.2)


class StampScene(TKKBaseScene):
    """Text reveal followed by a rubber stamp.

    Override: CONTEXT, STAMP_TEXT, STAMP_COLOR
    """
    CONTEXT = ""
    STAMP_TEXT = ""
    STAMP_COLOR = TKK_RED

    def construct(self):
        label = self.add_label()

        if self.CONTEXT:
            ctx = caption(self.CONTEXT, color=TKK_WHITE, size=40)
            ctx.move_to(UP * 2)
            self.play(FadeIn(ctx), run_time=0.5)

        s = stamp(self.STAMP_TEXT, color=self.STAMP_COLOR, size=56)
        s.move_to(DOWN * 1)
        self.play(FadeIn(s, scale=2.0), run_time=0.3)
        flash_transition(self, opacity=0.08, duration=0.08)

        self.wait(max(0.1, self.DURATION - 1.2))
