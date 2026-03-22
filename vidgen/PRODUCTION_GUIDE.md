# TKK Video Production Guide

This documents the **proven working process** that produced 10+ successful videos on March 17-18, 2026. Do NOT deviate from this pattern without explicit approval.

## Working Architecture

```
Manim screenplay (.py)  →  6 Scene classes  →  FFmpeg concat  →  Audio merge  →  _final.mp4
```

Each video is a **single self-contained Python script** (~550 lines) that:
1. Defines 6 Scene classes (one per story beat)
2. Renders each scene independently via `--scene N`
3. Concatenates with FFmpeg
4. Merges with TTS audio

## Visual-First Rules

Every TKK video must follow these visual-first principles. Voice carries the narration. Visuals SHOW the story.

1. **Voice carries narration** — The narrator tells the story. The screen shows it. Never put narration sentences as text on screen.
2. **Text budget: 3-8 words per scene** — Names, dates, numbers, labels only. "THOMAS MIDGLEY", "1921", "FREON", "18 km" — yes. "More environmental damage than any organism" — NO.
3. **Animate the concept** — Don't describe what happened, SHOW it. Workers shaking → turning red → disappearing. Ozone circle tearing open. Moai rocking side to side.
4. **SVG icons = minimum bar** — Load icons via `load_svg()` from `svg_assets/downloaded/`. Animate their state (color, opacity, position, shake). Reference: `midgley_v2_manim.py`.
5. **Custom domain shapes = gold standard** — Build topic-specific shapes from Polygon/VGroup (moai_side, palm_stump, ice_pick). Reference: `easter_island_v16.py`.
6. **Hierarchy**: custom shapes > SVG icons + animation > geometric primitives > text (last resort).

## Script Structure (MUST follow this order)

```
Lines 1-10:     Shebang, docstring with VTT cues
Lines 11-20:    Venv auto-switch
Lines 21-40:    Imports (manim, numpy, subprocess)
Lines 41-60:    TTS_SCRIPT variable (REQUIRED — full narration text)
Lines 61-80:    Manim config (1080x1920, 30fps, portrait)
Lines 81-100:   Color palette constants
Lines 101-160:  Helper functions (gradient_bg, grid_lines, safe_text, label_pill, domain shapes)
Lines 161-520:  6 Scene classes (Scene1 through Scene6)
Lines 521-end:  Render pipeline (__main__ block with --scene, --preview, concat)
```

## Required Boilerplate

### Venv Switch (lines 11-13)
```python
VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])
```

### Manim Config (lines 41-48)
```python
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.frame_width = 9
config.frame_height = 16
config.background_color = "#080A10"
config.disable_caching = True
```

### Color Palette (define ALL colors as constants)
```python
BG = "#080A10"
GRID = "#1A2030"
SURFACE = "#15192A"
WHITE_SOFT = "#F0F0F0"
GOLD = "#FFD700"
# + 3-5 topic-specific colors
```

### Core Helpers (MUST include)
```python
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

SAFE_W = 8.0    # Max text width before auto-scale
SAFE_TOP = 7.2  # Top 5% — status bar/clock (y must be <= this)
SAFE_BOT = -6.4 # Bottom 10% — TikTok description/buttons (y must be >= this)

# Vertical layout zones — USE THESE for all positioning
# The frame is 16 units tall. You MUST fill the full vertical space.
ZONE_TITLE  = 6.2    # y 5.5–7.0  — scene label pills
ZONE_UPPER  = 3.5    # y 1.5–5.5  — hero visual top portion
ZONE_MID    = 0.0    # y -1.5–1.5 — central focal point, big numbers
ZONE_LOWER  = -3.5   # y -5.5–-1.5 — supporting visuals, bars, icons
ZONE_FOOTER = -6.0   # y -6.4–-5.5 — captions, source labels

def safe_text(content, **kwargs):
    t = Text(content, **kwargs)
    if t.width > SAFE_W:
        t.scale(SAFE_W / t.width)
    return t

def label_pill(txt, color=GOLD, bg=SURFACE, fs=28):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > SAFE_W:
        t.scale(SAFE_W / t.width)
    p = RoundedRectangle(
        width=t.width + 0.5, height=t.height + 0.3,
        corner_radius=0.15, fill_color=bg, fill_opacity=0.9, stroke_width=0
    ).move_to(t)
    return VGroup(p, t)
```

### Domain Shape Helpers (REQUIRED: 2-4 per video)
Each video MUST define topic-specific shape functions. These are the visual vocabulary of the story.

**Required**: At minimum 2 domain shapes per video. Aim for 4.

Examples from shipped videos:
- **Easter Island**: `moai_side()`, `palm_stump()`, `island_outline()`, `stick_fig()` — 4 shapes
- **Radium Girls**: `jaw_teeth()`, `paint_brush()`, `watch_dial()` — 3 shapes
- **Lobotomy**: `ice_pick()`, `nobel_medal()` — 2 shapes minimum
- **Henrietta Lacks**: `cell_cluster()`, `petri_dish()`, `chromosome()` — 3 shapes

These are simple VGroups of Rectangles, Circles, Polygons, Lines. 15-40 lines each.
They must be recognizable at small sizes (0.5-1.0 height) and large (3-5 height).

## Vertical Layout (CRITICAL — Fill the Frame)

The frame is 16 units tall (y: -8 to +8). The safe zone is y: -6.4 to 7.2 = **13.6 usable units**.
You MUST use the full vertical safe zone. **Content crammed to the top half is the #1 layout bug.**

### Named Zones (use for ALL positioning)

| Zone    | Y Center | Y Range       | Use For                          |
|---------|----------|---------------|----------------------------------|
| TITLE   | 6.2      | 5.5 to 7.0   | Scene label pills                |
| UPPER   | 3.5      | 1.5 to 5.5   | Hero visual (top portion)        |
| MID     | 0.0      | -1.5 to 1.5  | Central focal point, big numbers |
| LOWER   | -3.5     | -5.5 to -1.5 | Supporting visual, bars, icons   |
| FOOTER  | -6.0     | -6.4 to -5.5 | Captions, source labels          |

### Rules
1. **Every scene MUST have visual content in at least 3 of the 5 zones.** If your scene only fills TITLE + UPPER, you have a layout bug.
2. **Bar chart y_base should be -5 to -6** (NOT -1 to -2). Bars must start low to fill the frame.
3. **Hero visuals (domain shapes, SVG icons) should CENTER at y=0 to y=1**, NOT y=3 to y=5.
4. **Use `safe_place(mob, "LOWER")` from anim_primitives** instead of `mob.move_to(DOWN * 1)`.
5. **If your content ends above y=-2, you have a layout bug** — push something to ZONE_LOWER or ZONE_FOOTER.
6. Run `python qa_layout.py previews/` after `--preview` render to check vertical distribution.

### Example — Good vs Bad positioning
```
BAD:  pill at y=7, chart at y=2, nothing below → bottom 60% empty
GOOD: pill at y=6.2, hero at y=1, chart at y=-3, caption at y=-6 → full frame used
```

## Scene Pattern

**Every scene class MUST:**
1. Start with `self.add(gradient_bg(), grid_lines(opacity))`
2. Use `safe_text()` for all text (prevents overflow)
3. Track timing with comments: `# t=X.XX`
4. End with `self.play(FadeOut(VGroup(*self.mobjects[2:]), run_time=0.3))`

```python
class Scene1_TheWrongAnswer(Scene):
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))

        pill = label_pill("THE WRONG ANSWER", color=RED)
        pill.move_to(UP * 5.5)
        self.play(FadeIn(pill, scale=1.05), run_time=0.4)      # t=0.4

        # SVG icons that SHOW the concept (not text that SAYS it)
        factory = load_svg("factory.svg", color=TKK_DIM, height=4)
        factory.move_to(UP * 2)
        self.play(FadeIn(factory, scale=0.9), run_time=0.5)     # t=0.9

        # Workers — will animate to show danger
        workers = VGroup()
        for i in range(5):
            w = load_svg("person.svg", color=TKK_WHITE, height=1.5)
            w.move_to(LEFT * 2.5 + RIGHT * i * 1.25 + DOWN * 2)
            workers.add(w)
        self.play(LaggedStart(*[FadeIn(w, shift=UP*0.2) for w in workers],
                              lag_ratio=0.06), run_time=0.5)    # t=1.4

        self.wait(1.5)                                           # t=2.9

        # Workers shake → turn red → disappear (ANIMATE the story)
        for w in workers:
            w.generate_target()
            w.target.shift(RIGHT * 0.1)
        self.play(*[MoveToTarget(w) for w in workers], run_time=0.1)
        for w in workers:
            w.generate_target()
            w.target.shift(LEFT * 0.2)
        self.play(*[MoveToTarget(w) for w in workers], run_time=0.1)

        self.play(*[w.animate.set_color(TKK_RED) for w in workers], run_time=0.3)

        for w in workers:
            self.play(w.animate.shift(DOWN * 2).set_opacity(0), run_time=0.15)

        self.play(FadeOut(VGroup(*self.mobjects[2:]), run_time=0.3))
```

## Font Usage

| Font | Purpose | Size Range |
|------|---------|-----------|
| Bebas Neue | Big numbers, stats, impact | 80-220 |
| DM Serif Display | Narrative body, quotes | 40-50 |
| Inter | Labels, pills, small text | 24-36 |

## Animation Verbs (Proven Safe)

| Animation | Use For | Notes |
|-----------|---------|-------|
| `FadeIn(obj, scale=1.05)` | Most entrances | Most reliable |
| `FadeIn(obj, shift=DOWN*0.3)` | Text lines | Subtle slide |
| `FadeOut(obj)` | Exits | Always use for scene cleanup |
| `Flash(point, color, ...)` | Emphasis on key numbers | Sparingly |
| `Create(line)` | Dividers, underlines | For decorative lines |
| `GrowFromCenter(obj)` | Shapes appearing | Domain objects |
| `LaggedStart(*anims, lag=0.15)` | Lists/groups | Staggered items |
| `Write(text)` | Character-by-character | Slow, use for emphasis only |

**AVOID:** `Succession`, `UpdateFromAlphaFunc`, complex `rate_functions`, `always_redraw`. These cause rendering issues.

## Render Pipeline (__main__ block)

```python
if __name__ == "__main__":
    names = ["Scene1_Name", "Scene2_Name", ..., "Scene6_Name"]

    # Render each scene as separate MP4
    for i, nm in enumerate(names):
        subprocess.run([python, __file__, "--scene", str(i)], timeout=600)

    # FFmpeg concat demuxer
    with open("concat.txt", "w") as f:
        for scene_file in scene_files:
            f.write(f"file '{scene_file}'\n")

    # Merge video + audio
    ffmpeg -y -f concat -safe 0 -i concat.txt -i audio.mp3 \
           -c:v libx264 -crf 23 -preset medium -pix_fmt yuv420p \
           -c:a aac -b:a 128k -map 0:v -map 1:a output_final.mp4
```

## Audio/TTS

- **Every screenplay MUST include a `TTS_SCRIPT` variable** with the full narration text:
  ```python
  TTS_SCRIPT = """First line of narration here.
  Second line. Third line. Full sentences, exactly as the narrator should speak them.
  No abbreviations, no ellipsis, no keywords — write the complete spoken narration."""
  ```
  Place it after the venv switch and before the manim config. `generate_tts.py` extracts this variable to generate audio. **Without it, TTS generation will fail silently.**
- **ALWAYS use Fish Audio** with the ELITE voice for all production TTS
- Command: `python generate_tts.py {topic}_manim.py` (auto-selects Fish Audio)
- Do NOT use edge-tts, kokoro, or piper for final videos — Fish Audio is the standard
- Do NOT install alternative TTS engines — Fish Audio is already configured
- Audio file referenced in render pipeline as `tts_{topic}.mp3`
- VTT timing cues in docstring for manual animation sync
- **Audio is NOT embedded during Manim render** — merged in FFmpeg at the end

### Word Budget (CRITICAL)

Fish Audio ELITE speaks at ~150 WPM. Scripts that are too long cause freeze-frame dead time.

| Category | Words | Duration | Status |
|----------|-------|----------|--------|
| **Target** | 70 | ~28s | OK |
| Acceptable | 71-80 | 28-32s | OK |
| Warning | 81-90 | 32-36s | WARN |
| **Over budget** | >90 | >36s | FAIL |

**Run `python3 audit_tts.py` to check your script.** Single file: `python3 audit_tts.py topic_manim.py`

Tips for concise scripts:
- Cut filler: "it's worth noting", "in fact", "the reality is"
- One idea per sentence, max 12 words
- Lead with the surprising fact, not the setup
- The mystery arc does the engagement work — the words just need to be clear

## Animation Enhancement

When scenes have dead time (animation ends before narration), use the enhancement engine:

```bash
python3 enhance_animations.py topic_manim.py   # analyze dead time per scene
```

Available enhancements (template-based, guaranteed to render):
- `slow_zoom` — gentle scale on existing visual (1-4s)
- `pulse_glow` — glowing circle behind key element (1-3s)
- `pan_drift` — slow camera-like shift (2-5s)
- `secondary_label` — fade in annotation (1-3s)
- `emphasis_line` — animated underline (1-2s)
- `particle_drift` — ambient floating dots (2-5s)

Via MCP: `analyze_enhancements(filename)` for suggestions, `apply_enhancement(...)` to generate code.

### Pipeline Step

Enhancement analysis runs automatically in `produce.py` as Step 2.5 (between TTS and render).
Skip with `--skip-enhance`. The step is informational — it reports dead time but doesn't auto-modify code.

## What NOT To Do

1. **Don't use MarkupText** — only `Text()`
2. **Don't load external images** in Manim — only programmatic shapes
3. **Don't make helper methods on Scene classes** — keep everything in `construct()`
4. **Don't use complex rate functions** — they cause timing drift
5. **Don't skip gradient_bg + grid_lines** — every scene needs them
6. **Don't hardcode colors inline** — always use palette constants
7. **Don't exceed SAFE_W (8.0)** — always use `safe_text()` wrapper
8. **Don't make scenes longer than 10s each** — 6 scenes, 28-45s total
9. **Don't import from vidgen.py** in Manim scripts — they are independent
10. **Don't try to animate audio sync** — timing is manual via wait()
11. **Don't put narration text on screen** — if the narrator says "More environmental damage than any organism," that text must NOT appear on screen. Voice tells, visuals show.
12. **Don't use headline + caption stacks** — the v1 pattern of `headline("BIG TEXT") + caption("smaller text") + divider()` stacked vertically is banned. Use SVG icons and animated shapes instead.
13. **Don't use cascade_list for story text** — `cascade_list` is for data/stats only, never for sentences the narrator is speaking.
14. **Don't leave the bottom half empty** — every scene must have content below y=-2. Use the ZONE_LOWER (-3.5) and ZONE_FOOTER (-6.0) constants. If your preview PNG has the bottom 40%+ empty, it's wrong.
15. **Don't use y_base > -4 for bar charts** — bars must start low (y=-5 to y=-6) to fill the vertical frame. A bar chart crammed above the midline is the most common layout bug.
16. **Don't position hero visuals at y=3 to y=5** — the hero (main visual element) should be at y=0 to y=1 (ZONE_MID), not pushed to the top third.

## Quality Checklist (Before marking _final)

- [ ] All 6 scenes render without errors
- [ ] Total duration matches audio length (within 1s)
- [ ] No text overflow (all text within frame bounds)
- [ ] First frame is visually interesting (not blank)
- [ ] Colors are consistent across scenes
- [ ] FFmpeg concat has no gaps or jumps
- [ ] Audio merged and audible
- [ ] moov atom at front (`-movflags faststart`)
- [ ] File plays on mobile (H.264, yuv420p, AAC)

## Content Format Types

### Type A: Documentary Narration (Current — Working)
- Manim-generated graphics + text overlays
- TTS narration (Fish Audio ELITE voice)
- Mystery structure (6 scenes)
- 28-45 seconds

### Type B: Documentary Edit (Reference: Video 1)
- Real footage clips + big timestamp text
- Ken Burns on historical photos
- Would need: stock footage library, video clip support in vidgen
- **Not yet implemented**

### Type C: Animated Story (Reference: Video 2 — Warhammer 40k)
- Simple cartoon character with expressions
- 3D perspective grid background
- Title card with pill badge, part numbers
- Would need: character SVG system, expression swaps, longer format
- **Not yet implemented**

## Timing Sync Protocol

Animation duration MUST match TTS audio duration (drift < 0.5s). Use the DURATION-based adaptive timing pattern.

### DURATION Pattern (Required for All Scenes)

Every scene class must use this pattern:

```python
class SceneN_Name(Scene):
    DURATION = 4.5  # fallback; overridden by TTS timing at render time
    def construct(self):
        self.add(gradient_bg(), grid_lines(0.03))
        t = 0

        self.play(FadeIn(pill), run_time=0.3); t += 0.3
        # ... more animations, each tracking t ...

        target = getattr(self.__class__, 'DURATION', 4.5)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:])), run_time=0.3)
```

### TKK_SCENE_TIMINGS Env Var (Required in __main__)

All `__main__` blocks must read the `TKK_SCENE_TIMINGS` environment variable to override scene durations at render time:

```python
SCENES = [Scene1_Name, Scene2_Name, ..., Scene6_Name]

if "--scene" in sys.argv:
    idx = int(sys.argv[sys.argv.index("--scene") + 1])
    timings_json = os.environ.get("TKK_SCENE_TIMINGS")
    if timings_json:
        SCENES[idx].DURATION = json.loads(timings_json)[idx]
    render_single_scene(idx)
```

### Workflow

1. Write TTS_SCRIPT first (70-80 words max)
2. Generate TTS audio → get per-scene timings JSON
3. Write animations to fit each scene's audio share
4. Never hardcode `self.wait()` without the adaptive `target - t` pattern
5. Verify: `ffprobe` final MP4 duration matches TTS duration (drift < 0.5s)

### Reference

See `chariot_bronze_age_manim.py` and `language_math_bug_manim.py` for complete working examples.

## New Screenplay Template (Recommended)

New screenplays should use `screenplay_base.py` to eliminate boilerplate. A single `from screenplay_base import *` gives you all manim imports, anim_primitives, zone constants, colors, and the render pipeline.

### Thin Format (~200-400 lines of creative content only)

```python
#!/usr/bin/env python3
"""Topic Title — Brief description.

6 scenes, ~Xs.

VTT cues (absolute → relative):
  Scene 1 (0.0–7.0s = 7.00s): ...
  Scene 2 (7.0–14.0s = 7.00s): ...
  Scene 3 (14.0–20.0s = 6.00s): ...
  Scene 4 (20.0–27.0s = 7.00s): ...
  Scene 5 (27.0–34.0s = 7.00s): ...
  Scene 6 (34.0–40.0s = 6.00s): ...
"""
from screenplay_base import *

TTS_SCRIPT = """First line of narration.
Second line. Third line.
Full sentences as the narrator should speak them."""

configure_manim("#0A0A10")  # optional custom bg color

# Topic-specific colors
TOPIC_BLUE = "#3B82F6"
TOPIC_DARK = "#1E3A5F"

# Domain shapes (2-4 per video)
def my_shape(height=3.0):
    ...

# 6 Scene classes
class Scene1_Hook(Scene):
    DURATION = 7.0
    def construct(self):
        self.add(gradient_bg(), grid_lines())
        t = 0
        pill = label_pill("THE HOOK", color=TKK_RED)
        safe_place(pill, "TITLE")
        self.play(FadeIn(pill, scale=1.05), run_time=0.4); t += 0.4
        # ... animations ...
        target = getattr(self.__class__, 'DURATION', 7.0)
        self.wait(max(0.1, target - t - 0.3))
        self.play(FadeOut(Group(*self.mobjects[2:])), run_time=0.3)

class Scene2_Wrong(Scene): ...
class Scene3_Contradiction(Scene): ...
class Scene4_Proof(Scene): ...
class Scene5_Betrayal(Scene): ...
class Scene6_Punch(Scene): ...

SCENES = [Scene1_Hook, Scene2_Wrong, Scene3_Contradiction,
          Scene4_Proof, Scene5_Betrayal, Scene6_Punch]

if __name__ == "__main__":
    screenplay_main(SCENES, __file__)
```

### What `screenplay_base` provides

- **Venv auto-switch** — runs on import, before manim loads
- **All manim imports** — `Scene`, `VGroup`, `FadeIn`, `config`, `np`, etc.
- **All anim_primitives** — `gradient_bg`, `grid_lines`, `safe_text`, `label_pill`, `headline`, `safe_place`, zone constants, TKK colors, etc.
- **`configure_manim(bg_color)`** — sets 1080x1920, 30fps, 9x16 (called with defaults on import)
- **`screenplay_main(scenes, __file__)`** — handles `--preview`, `--scene N`, full parallel render + concat

### Legacy Format (still works)

All existing screenplays (~50 files) use the self-contained format with inline boilerplate. This still works and requires no changes. The `Script Structure` section below documents it.

## File Naming Convention

- `{topic}_manim.py` — Manim screenplay source
- `{topic}.json` — Remotion manifest (in `remotion/src/manifests/`)
- `{topic}_final.mp4` — shipping video (either framework)
- `tts_{topic}.mp3` — narration audio (shared by both frameworks)
- `{topic}_v{N}.mp4` — iteration (not for publishing)

---

## Remotion Framework (Default for New Work)

Remotion uses React/TypeScript components driven by JSON manifests. The agent writes a manifest; pre-built components render each scene type. **Use Remotion for all new screenplays unless Manim is specifically requested.**

Full architecture reference: `remotion/REMOTION_DESIGN_GUIDE.md`

### Manifest Location & Structure

Manifests live at `remotion/src/manifests/{topic}.json`. Schema validated by Zod in `src/schema.ts`.

```json
{
  "topic": "tunguska",
  "ttsScript": "Full narration text here...",
  "colors": { "bg": "#080A10", "accent": "#FFD700", "secondary": "#3B82F6" },
  "scenes": [
    {
      "type": "headline",
      "label": "The Hook",
      "props": { "title": "TUNGUSKA", "subtitle": "1908", "zone": "MID" }
    },
    {
      "type": "counter",
      "label": "The Scale",
      "props": { "start": 0, "end": 80, "unit": "million trees", "zone": "MID" }
    }
  ]
}
```

### Scene Types Available

| Type | Component | Use |
|------|-----------|-----|
| `headline` | Headline.tsx | Title cards, hook text |
| `counter` | Counter.tsx | Animated number count-up (hero stat) |
| `barChart` | BarChart.tsx | Vertical bar comparison |
| `timeline` | Timeline.tsx | Chronological markers |
| `kenburns` | KenBurns.tsx | Pan/zoom on static image |
| `map` | MapView.tsx | Image map with animated markers |
| `videoClip` | VideoClip.tsx | Embedded video footage |
| `splitCompare` | SplitCompare.tsx | Before/after split |
| `iconRow` | IconRow.tsx | Row of icons with stagger |
| `populationDrop` | PopulationDrop.tsx | Animated population decline |

### Typography — Video Sizes, Not Web Sizes (CRITICAL)

Web defaults produce text that vanishes on phone screens. Minimum body text for 1080x1920 video viewed on smartphones is **40-58px** — roughly 3x web conventions.

| Element | Size (px) | Purpose |
|---------|-----------|---------|
| Hero stat numbers | **160–220** | Dominates frame, focal point |
| Section headlines | **80–120** | Readable in thumbnails |
| Subheadings | **56–72** | Clear hierarchy |
| Body / descriptions | **40–56** | Minimum for phone legibility |
| Labels / captions | **32–40** | Bold weight required |
| Source citations | **24–32** | Not critical for glance reading |

These are defined in `src/lib/typography.ts`. Every component must use them — never inline font sizes.

### Safe Zones — Platform UI Overlays

TikTok, Reels, and Shorts overlay UI elements that consume frame real estate:

| Edge | Clearance | Why |
|------|-----------|-----|
| Top | **200px** | Username, sound label, Shorts title |
| Bottom | **400px** | Caption bar, CTA, description (TikTok deepest at ~480px) |
| Right | **140px** | Like/comment/share/profile buttons |
| Left | **120px** | Caption text overflow |

**Usable area: ~820x1320px** centered in 1080x1920. Defined in `src/lib/zones.ts`.

### Full-Height Layout (Same Rule as Manim)

Content MUST fill the full vertical space. The #1 layout bug is everything crammed into the upper half. Use `flexDirection: 'column'` with `justifyContent: 'space-between'` on `AbsoluteFill` to distribute content.

Zone-based layout for the safe area:
```
Zone 1 (200–530px):   Title/hook + branding
Zone 2 (530–960px):   Primary stat or data viz
Zone 3 (960–1300px):  Secondary data, comparison
Zone 4 (1300–1520px): Source citation, conclusion
```

Each zone communicates **one idea** — one stat, one chart, one comparison.

### Animation Rules

1. **Use `useCurrentFrame()` + `spring()` + `interpolate()` for ALL animations** — never CSS transitions, `setInterval`, or third-party animation libraries (they cause flickering during headless rendering)
2. Inside a `<Sequence>`, `useCurrentFrame()` returns frames relative to sequence start — animations are automatically scene-relative
3. Spring configs per beat type:
   - Snappy (UI entrances): `{ damping: 20, stiffness: 200, mass: 0.8 }`
   - Gentle (backgrounds): `{ damping: 200, stiffness: 80, mass: 1 }`
   - Dramatic (hero stats): `{ damping: 12, stiffness: 200, mass: 1.2 }`
   - Bouncy (icons/badges): `{ damping: 8, stiffness: 180, mass: 0.5 }`
4. Use `TransitionSeries` from `@remotion/transitions` for scene transitions — `fade()`, `slide()`, `wipe()`

### TTS-Driven Timing (Audio-First) + Automated Sync Pipeline

The manifest declares content and narration text — **no frame numbers or timestamps**. Timing is fully automated:

1. Agent writes manifest with `ttsScript` and per-scene narration text
2. `generate_tts.py` produces three files automatically:
   - `tts_{topic}.mp3` — audio
   - `tts_{topic}.mp3.json` — Whisper word-level timestamps
   - `tts_{topic}_timings.json` — derived scene boundaries + calibrations
3. `render.mts` reads timings, applies calibrations, runs QA gate, then renders
4. Re-record TTS → re-run `generate_tts.py` → timings auto-update

**Sync rules:**
- Scene durations MUST come from Whisper alignment, never hand-guessed
- `countDuration` for Counter scenes is auto-calibrated by `derive_timings.py` — don't set it manually
- TransitionSeries transition overlap is compensated in `Video.tsx` (last scene extended)
- `qa_remotion_sync.py` runs as a pre-render gate — renders with FAIL status are blocked
- If you must override a calibration, edit the timings JSON (not the manifest)

### Manifest Constraints for AI Generation

The agent picks from **menus of enums**, never writes CSS or frame numbers:

- **Beat types**: `hook`, `wrong-answer`, `contradiction`, `proof`, `betrayal`, `punch` — each maps to animation intensity and color treatment
- **Layout variants**: `centered`, `split`, `stacked`, `data-focus`, `full-bleed` — each maps to a React layout component
- **Animation presets**: `fade-in`, `slide-up`, `scale-up`, `count-up`, `typewriter`, `shake-reveal`
- **Scene types**: pre-built components (see table above)

### Visual Depth — Layered Backgrounds

Stack multiple `AbsoluteFill` layers:
1. Radial gradient background
2. SVG noise texture (feTurbulence at 0.25 opacity, soft-light blend)
3. Vignette (box-shadow: inset 0 0 300px rgba(0,0,0,0.6))
4. Content layer

### Remotion Pipeline

```bash
# 1. Generate TTS + Whisper align + derive timings (all automatic)
.venv/bin/python3 generate_tts.py remotion/src/manifests/{topic}.json
#    → tts_{topic}.mp3, tts_{topic}.mp3.json, tts_{topic}_timings.json

# 2. Render previews
npx tsx preview.mts {topic}

# 3. Full render (includes pre-render sync QA gate)
npx tsx render.mts {topic}
#    → applies calibrations from timings JSON
#    → runs qa_remotion_sync.py — blocks render on FAIL
```

### What NOT to Do (Remotion)

1. **Don't use web-scale font sizes** — 16px body text is invisible on phones
2. **Don't use CSS transitions or requestAnimationFrame** — use spring() only
3. **Don't hardcode frame numbers in manifests** — derive from audio
4. **Don't use Mapbox GL JS** — requires GPU, breaks on Lambda. Use Static Images API or react-simple-maps
5. **Don't cluster content in upper half** — use full-height zone layout
6. **Don't use thin font weights** — they blur under TikTok compression. Medium/bold minimum
7. **Don't exceed 30 characters per text line** — use 1.3-1.5x line height
8. **Don't skip layered backgrounds** — flat backgrounds look amateur vs Manim's gradient+grid

---

## Word-Triggered Manifest Format (Remotion)

The word-triggered system replaces heuristic timing derivation with anchor-word-based timing. Each scene and element declares an **anchor word** from the TTS narration. `resolve_word_triggers.py` maps anchors to Whisper timestamps, producing exact frame-level timing.

### Manifest structure

```json
{
  "topic": "henrietta",
  "ttsScript": "Full narration text...",
  "colors": { "bg": "#080A10", "accent": "#E879F9", "secondary": "#F59E0B" },
  "scenes": [
    {
      "id": "hook",
      "label": "THE HOOK",
      "type": "illustration",
      "scene_anchor": "Henrietta",
      "scene_end_anchor": "knew.",
      "elements": [
        {
          "type": "text",
          "content": "STOLEN CELLS",
          "zone": "UPPER",
          "style": "headline",
          "color": "#E879F9",
          "anchor": "Henrietta",
          "attack": 0.0,
          "enter": "fade",
          "hold": "until_scene_end"
        }
      ]
    }
  ]
}
```

### Key fields

- **`scene_anchor`** / **`scene_end_anchor`**: Words from `ttsScript` that mark scene start/end
- **`anchor`** (per element): Word that triggers this element's entrance animation
- **`attack`**: Seconds to delay after the anchor word (0.0 = on the word, 0.3 = 300ms after)
- **`hold`**: `"until_scene_end"` (default) or `"until_replaced"` (fades out when next element in same zone has `replaces_zone: true`)
- **`count_end_anchor`**: For counters, the word when counting should finish
- **`enter`**: Animation type — `fade`, `pop`, `slideUp`, `fadeIn`, `wordByWord`, `typewriter`

### Element types

| Type | Zone | Required fields |
|------|------|----------------|
| `text` | any | `content`, `style`, `anchor` |
| `counter` | MID | `start`, `end`, `unit`, `anchor`, `count_end_anchor` |
| `svg` | MID | `svg` (icon name), `size`, `anchor` |
| `bar` | MID | `label`, `value`, `anchor` |
| `timeline_marker` | LOWER | `year`, `label`, `anchor` |

### Workflow

```bash
# 1. Write word-triggered manifest
#    (scenes have scene_anchor/scene_end_anchor, elements have anchor)

# 2. Generate TTS — auto-detects word-triggered format, runs resolver
.venv/bin/python3 generate_tts.py remotion/src/manifests/{topic}.json

# 3. Validate manifest (SVG names, anchors, text lengths, zone density)
.venv/bin/python3 validate_manifest.py {topic}

# 4. Manually re-resolve if needed
.venv/bin/python3 resolve_word_triggers.py {topic}

# 5. Run all QA checks (or individual audits)
.venv/bin/python3 qa_all.py {topic}              # unified runner
.venv/bin/python3 audit_timeline.py {topic}       # timeline visibility
.venv/bin/python3 collision_audit.py {topic}       # pixel collision + text overflow

# 6. Render (render.mts auto-runs qa_all.py as pre-render gate)
npx tsx remotion/preview.mts {topic}
npx tsx remotion/render.mts {topic}
```

### Anchor rules

1. Every anchor word must appear in `ttsScript` exactly as written (case-insensitive, punctuation-stripped)
2. Scene anchors must appear in narration order — scene 1's anchor before scene 2's
3. Element anchors must fall between their scene's start and end anchors
4. Avoid common words ("the", "is") as anchors — use distinctive words for reliable matching
5. If a word appears multiple times in the script, use the first occurrence after the scene start
