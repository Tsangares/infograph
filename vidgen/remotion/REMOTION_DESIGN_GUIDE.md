# Remotion architecture for agent-driven vertical video infographics

**The core problem is not Remotion—it's that web-native defaults produce web-sized output.** Your Manim pipeline encoded visual design knowledge (200px stat numbers, full-frame layouts, decorative accents) directly into code. Remotion, being React, defaults to web conventions: 16px body text, centered content blocks, no ornamentation. The fix requires embedding mobile-video design rules into your component system, theme tokens, and manifest schema so the AI agent's JSON output automatically produces TikTok-quality frames. This guide provides the complete architecture: design tokens calibrated for 1080×1920 mobile viewing, animation primitives driven by `useCurrentFrame()` and `spring()`, a TTS-keyed timing system that reflows automatically, and a Zod-validated manifest schema constrained enough for reliable AI generation.

---

## The typography gap: web pixels versus video pixels

The single most impactful change is font sizing. Research from the German Blind and Visually Impaired Association establishes that for full HD video viewed on smartphones, **minimum body text is 40–58px**—roughly 3× what web conventions suggest. Your Manim videos got this right with 200px+ stat numbers. The Remotion output uses web-scale text that vanishes on a phone screen.

Here are the calibrated sizes for a 1080×1920 vertical canvas:

| Element | Recommended size | Rationale |
|---|---|---|
| Hero stat numbers | **160–220px** | Dominates the frame; focal point of each beat |
| Section headlines | **80–120px** | Readable even in thumbnail previews |
| Subheadings | **56–72px** | Clear hierarchy below headlines |
| Body / descriptions | **40–56px** | Minimum for smartphone legibility at glance speed |
| Labels / captions | **32–40px** | Bold weight required at this size |
| Source citations | **24–32px** | Not critical for glance reading |

Encode these as design tokens, not inline values. Build a centralized theme file that every component references:

```typescript
export const theme = {
  fontSize: {
    heroStat: 200, headline: 96, subheading: 64,
    body: 48, label: 36, caption: 28,
  },
  colors: {
    background: '#0A0E1A', surface: '#141828',
    primary: '#4ECDC4', accent: '#FF6B6B',
    text: '#FFFFFF', textMuted: 'rgba(255,255,255,0.5)',
  },
  spacing: {
    safeTop: 200, safeBottom: 400, safeSide: 120, safeRight: 140,
    sectionGap: 48, elementGap: 24,
  },
  canvas: { width: 1080, height: 1920 },
};
```

Use React Context (`const { fontSize } = useTheme()`) so a single token change propagates everywhere. Remotion renders in Chromium, so CSS custom properties also work—change a variable and every component updates instantly in Studio preview.

Typography best practices for video specifically: use **sans-serif fonts** (Inter, Montserrat, Noto Sans) in **medium or bold weights**. Thin fonts blur under TikTok's compression. Keep lines under **30 characters** with **1.3–1.5× line height**. Every text block on screen needs a minimum **1 second per 13 characters** of dwell time.

---

## Safe zones and full-height layout strategy

Platform UI overlays consume significant frame real estate. The universal cross-platform safe zone for content targeting TikTok, Reels, and Shorts simultaneously:

- **Top**: 200px (username, sound label, Shorts title)
- **Bottom**: 400px (caption bar, CTA, description—TikTok's is deepest at ~480px)
- **Right**: 140px (like/comment/share/profile buttons)
- **Left**: 120px (caption text overflow)
- **Usable area**: approximately **820×1320px** centered in the 1080×1920 frame

Your Manim videos used the full 1920px height with 3–4 stacked content layers. The Remotion output clusters everything in the upper-middle. The fix is a **zone-based layout system** that divides the safe area into distinct content blocks:

```
Zone 1 (200–530px):   Title/hook + branding + decorative divider
Zone 2 (530–960px):   Primary stat or key data visualization
Zone 3 (960–1300px):  Secondary data, comparison, or supporting evidence
Zone 4 (1300–1520px): Source citation, conclusion, or CTA
```

The critical CSS pattern is `flexDirection: 'column'` with `justifyContent: 'space-between'` on an `AbsoluteFill`. This distributes content across the full height rather than clustering it. Each zone communicates **one idea**—one stat, one chart, one comparison. Alternate between large stat numbers and smaller explanatory text to create visual rhythm.

The layered rendering approach stacks multiple `AbsoluteFill` elements: a gradient/textured background layer, a vignette overlay, decorative elements (corner accents, geometric shapes), and finally the content layer. This creates visual depth that flat-background Remotion output currently lacks.

---

## Animation primitives that replace static slides

Every Manim element had entrance/exit animations. Building equivalent capability in Remotion requires a small library of reusable wrapper components, all driven by `useCurrentFrame()` and `spring()`. **Never use CSS transitions, `setInterval`, or third-party animation libraries**—they cause flickering during Remotion's multi-threaded headless rendering.

The foundational wrappers are `FadeIn`, `SlideUp`, `ScalePop`, and `StaggerChildren`. Each reads `useCurrentFrame()`, computes a `spring()` progress value (0→1), and maps it to CSS transforms via `interpolate()`. Inside a `<Sequence>`, `useCurrentFrame()` returns frames **relative to the sequence start**, making all animations automatically scene-relative without hardcoded frame numbers.

Spring configurations control animation feel. Calibrate these per beat type:

```typescript
const springs = {
  snappy:   { damping: 20, stiffness: 200, mass: 0.8 },  // UI entrances
  gentle:   { damping: 200, stiffness: 80, mass: 1 },     // backgrounds, fades
  dramatic: { damping: 12, stiffness: 200, mass: 1.2 },   // hero stats landing
  bouncy:   { damping: 8, stiffness: 180, mass: 0.5 },    // icons, badges
  smooth:   { damping: 100, stiffness: 100, mass: 1 },    // no-bounce counters
};
```

Use `measureSpring()` to calculate exact frame durations for each configuration, which feeds into `Sequence` duration calculations. The Remotion timing editor at `remotion.dev/timing-editor` lets you visually design curves.

For **scene transitions**, `@remotion/transitions` provides `TransitionSeries` with built-in presentations: `fade()`, `slide()`, `wipe()`, `clockWipe()`, `iris()`, and `flip()`. The pattern replaces hard cuts:

```tsx
<TransitionSeries>
  <TransitionSeries.Sequence durationInFrames={scene1Frames}>
    <Scene1 />
  </TransitionSeries.Sequence>
  <TransitionSeries.Transition
    timing={springTiming({ config: { damping: 200 } })}
    presentation={fade()}
  />
  <TransitionSeries.Sequence durationInFrames={scene2Frames}>
    <Scene2 />
  </TransitionSeries.Sequence>
</TransitionSeries>
```

Transitions overlap adjacent scenes, shortening total duration by the transition length. Custom presentations are straightforward—a function returning a component that receives `presentationProgress` (0→1) and `presentationDirection` ("entering"/"exiting").

---

## TTS-driven timing: the automated sync pipeline

The pipeline eliminates manual timing work through automated derivation and calibration. **Nothing in the manifest contains frame numbers or timestamps** — all timing is derived from Whisper word-level alignment of the TTS audio.

### How it works

Running `generate_tts.py` on a Remotion manifest triggers the full chain:

1. **Fish Audio TTS** → `tts_{topic}.mp3`
2. **Whisper alignment** → `tts_{topic}.mp3.json` (word-level timestamps)
3. **`derive_timings.py`** → `tts_{topic}_timings.json` (scene boundaries + calibrations)

`derive_timings.py` reads the manifest's `ttsScript` and scene content, matches narration segments to Whisper word timestamps, and computes:
- **`scene_durations`**: how long each scene should last (derived from narration boundaries)
- **`boundaries`**: cumulative timestamps where scenes transition
- **`calibrations`**: per-scene animation parameter overrides (e.g., `countDuration` for Counter scenes)

### Counter calibration

For `counter` scenes, `derive_timings.py` finds when the narrator says the target number (e.g., "two billion") in the Whisper transcript and computes what fraction of the scene that moment falls at. This becomes `countDuration` — so the counter animation reaches its target value exactly when the narrator says the number.

```json
{
  "calibrations": {
    "scene_0": { "countDuration": 0.15 },
    "scene_3": { "countDuration": 0.85 }
  }
}
```

Calibrations live in the timings sidecar, not the manifest. `render.mts` reads them and overrides manifest defaults at render time.

### TransitionSeries overlap compensation

`TransitionSeries` overlaps adjacent scenes during fade transitions (~25 frames per transition). Without compensation, the last ~4s of the composition would be black while narration plays. `Video.tsx` extends the last scene's duration by the total overlap to fill the full composition.

### Pre-render QA gate

`render.mts` runs `qa_remotion_sync.py` before rendering. If any check returns FAIL, the render is blocked. Checks include:
- **Counter sync**: does the counter show the right number when the narrator says it?
- **Timeline/bar chart sync**: do visual labels appear near when they're narrated?
- **AV duration**: does visual content cover the full narration?
- **Scene text sync**: do on-screen numbers match narration timing?

### Re-recording TTS

If you re-record TTS (new voice, speed change, script edit), just re-run `generate_tts.py`. All three output files regenerate automatically and the next render picks up the new timings.

---

## Manifest schema designed for constrained AI generation

The manifest must be constrained enough that Claude reliably generates valid JSON, but flexible enough for visual variety. The key principle: **the agent picks from menus of enums, never writes CSS or frame numbers**. Zod schemas enforce this at validation time, and Remotion natively supports Zod on `<Composition>` via the `schema` prop, enabling auto-generated Studio UI controls.

The schema architecture uses three layers of constrained choice:

**Beat types** map to visual treatment presets. The agent selects `"hook"`, `"proof"`, `"betrayal"`, etc., and the component system applies appropriate animation intensity, color temperature, and layout emphasis automatically. Hook scenes get aggressive springs (damping: 8), proof scenes get smooth data visualization reveals, punch scenes get long dramatic springs.

**Layout variants** control positioning without CSS. The agent picks `"centered"`, `"split"`, `"stacked"`, `"data-focus"`, or `"full-bleed"`. Each maps to a React layout component that handles flexbox, spacing, and safe zones. A `SceneRenderer` routes `scene.layout` to the appropriate layout component and `scene.beat` to a beat-specific overlay treatment.

**Animation presets** are enum values (`"fade-in"`, `"slide-up"`, `"scale-up"`, `"count-up"`, `"typewriter"`, `"shake-reveal"`) that map to the wrapper components. The agent assigns these to individual visual elements or to animation cues tied to trigger words.

The visual elements schema supports typed content blocks: `"headline"`, `"stat"` (with `numericValue` and `unit` for count-up animation), `"body-text"`, `"chart"` (with `chartType` and `chartData`), `"source-tag"`, and `"icon"`. Each type has specific optional fields—stats have numeric values, charts have data arrays—while sharing common fields like `animation` and `emphasis`.

```typescript
const SceneSchema = z.object({
  id: z.string(),
  beat: z.enum(['hook','wrong-answer','contradiction','proof','betrayal','punch']),
  layout: z.enum(['centered','left-aligned','split','full-bleed','stacked','data-focus']),
  narration: z.object({ id: z.string(), text: z.string() }),
  visuals: z.array(VisualElement),
  animationCues: z.array(z.object({
    triggerWord: z.string(),
    targetVisual: z.number(),
    animation: AnimationPreset,
  })).optional(),
  background: BackgroundSchema.optional(),
});
```

Validate manifests with Zod **before TTS generation** to catch bad schemas before expensive operations. The separation of concerns is strict: the agent writes content + layout choices, the TTS pipeline fills in `audioFile` and `durationMs`, and the build step resolves animation cue timestamps.

---

## Component rewrites that close the visual gap

**Vertical bar chart**: The current horizontal-bars-left-aligned implementation must flip to vertical bars spanning the full 1080px width. Calculate bar width as `(availableWidth - gaps) / barCount`, use `spring()` with staggered delays (`i * 8 frames`) to grow bars upward from the baseline. Apply `linear-gradient(to top, baseColor, lighterColor)` and `box-shadow: 0 0 20px color44` for gradient fills with glow. Place value labels above bars and category labels below, both at **28–36px** minimum. An SVG-based variant using `<linearGradient>` defs gives finer gradient control.

**Stat callout**: The hero component. A **180px** animated number using `spring()` to count from 0 to target (with `fontVariantNumeric: 'tabular-nums'` to prevent layout shifts), a **100px** unit label, and a **42px** subtitle that fades in 15 frames later. Apply gradient text via `background: linear-gradient(); WebkitBackgroundClip: text; WebkitTextFillColor: transparent` combined with `filter: drop-shadow(0 0 40px color)` for glow that works with background-clip. The scale entrance uses a dramatic spring (damping: 12, stiffness: 100).

**Decorative dividers**: SVG diamond-accented dividers (`───◆───`) with animated line extension via `spring()` and a delayed diamond scale-pop. Accent bars use `linear-gradient(90deg, transparent, color, transparent)` with spring-animated width. Corner decorations are absolute-positioned SVG L-shapes at 0.4 opacity.

**Rich backgrounds**: Layer three `AbsoluteFill` elements—a radial gradient (`radial-gradient(ellipse at 30% 20%, #1a2040 0%, #0a0e1a 70%)`), an SVG noise texture using inline `feTurbulence` filter at 0.25 opacity with `mix-blend-mode: soft-light`, and a vignette (`box-shadow: inset 0 0 300px rgba(0,0,0,0.6)`). Add subtle animated gradient orbs (large divs with `filter: blur(100px)`) that drift slowly using frame-based position interpolation.

**Maps**: For geography-heavy infographics, avoid Mapbox GL JS (requires GPU, breaks on Lambda). Use either the **Mapbox Static Images API** (build a URL, render with `<Img>`, supports markers and GeoJSON overlays, max 1280×1280 base) or **react-simple-maps** for pure SVG country highlighting that works perfectly in headless rendering. Both are deterministic and require no WebGL.

---

## Putting it together: the complete pipeline architecture

```
AI Agent (Claude)          → JSON manifest (Zod-validated)
  ↓                           topic, ttsScript, colors, scenes[]
generate_tts.py            → tts_{topic}.mp3 (Fish Audio)
  ↓                         → tts_{topic}.mp3.json (Whisper word timestamps)
derive_timings.py          → tts_{topic}_timings.json
  ↓                           scene_durations, boundaries, calibrations
render.mts                 → Applies calibrations to manifest props
  ↓                         → Runs qa_remotion_sync.py (blocks on FAIL)
  ↓                         → Bundles + renders via Remotion
Video.tsx                  → TransitionSeries with fade transitions
                              last scene extended by total overlap
```

The five specific visual problems map to five architectural fixes. Text too small → design tokens with video-calibrated sizes enforced by theme context. Bottom half empty → zone-based flex layout with `space-between` distribution. No decorative elements → layered `AbsoluteFill` background system with gradient, noise, vignette, and accent components. Wrong bar chart orientation → full-width vertical bar component with spring-animated growth. No animations → `spring()`-powered wrapper components triggered by resolved narration cues.

## Conclusion

The path from static web-style slides to Manim-quality output does not require abandoning Remotion's architecture—it requires encoding video design knowledge into the component system. The three highest-leverage changes are: increasing all font sizes by **3–4×** via design tokens, implementing `flex-direction: column` with `space-between` for full-height layouts, and adding `spring()`-driven animation wrappers to every visual element. The narration-keyed timing system (`triggerWord` → resolved `triggerMs` → frame-relative `Sequence`) eliminates the hardcoded-frame-number fragility that plagues most programmatic video pipelines. And by constraining the manifest schema to beat enums, layout variants, and animation presets, the AI agent generates visually rich video without writing a single line of CSS—it simply fills in a well-designed form.

---

## Word-Triggered Architecture

The word-triggered system is an evolution of the narration-keyed timing concept. Instead of heuristically guessing scene boundaries from keywords (`derive_timings.py`), each scene and element explicitly declares which narration word triggers it.

### Pipeline

```
Manifest (JSON)  +  Whisper alignment (JSON)
        ↓                    ↓
    resolve_word_triggers.py
        ↓
  {topic}_resolved.json  →  Remotion (word-triggered composition)
        ↓
  WordTriggeredVideo  →  TransitionSeries of WordTriggeredScenes
        ↓
  Each element: <Sequence from={delayFrames}> wraps entrance animation
```

### Resolved JSON format

`resolve_word_triggers.py` reads the manifest + Whisper word timestamps, then outputs:

```json
{
  "topic": "henrietta",
  "colors": { ... },
  "fps": 30,
  "total_duration_s": 38.5,
  "total_frames": 1155,
  "scene_durations": [4.2, 5.1, ...],
  "scenes": [
    {
      "id": "hook",
      "label": "THE HOOK",
      "type": "illustration",
      "start_s": 0.0,
      "end_s": 4.2,
      "duration_s": 4.2,
      "duration_frames": 126,
      "elements": [
        {
          "type": "text",
          "content": "STOLEN CELLS",
          "zone": "UPPER",
          "style": "headline",
          "_resolved": {
            "delay_frames": 0,
            "delay_s": 0.0,
            "anchor_word": "Henrietta",
            "anchor_time_s": 0.0,
            "absolute_frame": 0,
            "absolute_s": 0.0
          }
        }
      ]
    }
  ]
}
```

### Component hierarchy

- **`WordTriggeredVideo`** (`src/word_triggered/WordTriggeredVideo.tsx`): Top-level composition. Wraps scenes in TransitionSeries with fade transitions. Handles audio overlay.
- **`WordTriggeredScene`** (`src/word_triggered/WordTriggeredScene.tsx`): Renders one scene. Each element is wrapped in `<Sequence from={element._resolved.delay_frames}>` for precise timing.
- **`WordBar`** (`src/word_triggered/WordBar.tsx`): Bar chart element with spring-animated growth.
- **`WordTimelineMarker`** (`src/word_triggered/WordTimelineMarker.tsx`): Timeline marker with dot + year + label.
- **Types** (`src/word_triggered/types.ts`): `ResolvedManifest`, `ResolvedScene`, `ResolvedElement`, `ResolvedTiming`.

### QA tools

- **`validate_manifest.py`**: Pre-render manifest validation. Checks SVG names exist in `svgLibrary.tsx`, anchor words exist in `ttsScript`, text length vs style thresholds, zone density.
- **`audit_timeline.py`**: Frame-by-frame audit of zone occupancy. Detects empty frames, zone overlap conflicts, and dead time.
- **`collision_audit.py`**: Pixel-level bounding box collision detection. Estimates text/counter/SVG sizes using font metrics from `typography.ts` and zone coordinates from `zones.ts`. Detects text overflow (content exceeding zone height).
- **`qa_all.py`**: Unified QA runner. Auto-detects format and runs all applicable checks (manifest validation, layout, sync, audits). Returns structured PASS/WARN/FAIL.

`render.mts` calls `qa_all.py --json` as a pre-render gate for both word-triggered and legacy manifests. FAIL blocks the render.