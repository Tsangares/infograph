# TKK Manim Video Production Template

## Overview

This is the standard method for producing short-form TikTok/Reels/Shorts videos.
Based on the Easter Island History v4 render (approved by Astron 2026-03-17).

**Reference file**: `easter_island_history_manim_v4.py` (870 lines, the gold standard)

---

## Pipeline (5 Steps)

### Step 1: Script (Writer Agent)

Write a 30-45s narration script using the **mystery arc structure**:

| Beat | Purpose | Example |
|------|---------|---------|
| 1. Wrong Answer | Set up the common belief | "They destroyed themselves." |
| 2. Contradiction | Crack in the narrative | "But they survived centuries after..." |
| 3. Oral Tradition | The dismissed truth | "Ships came. People disappeared." |
| 4. Proof | Hard evidence | "1863. 1,400 people. One raid." |
| 5. Scale | Zoom out, staggering scope | "3,000 to 111. In less than a decade." |
| 6. Punch | Quiet closer that lands | "It was us." |

**Rules**:
- 8-15 words per sentence max
- Ear-first: write for listening, not reading
- Short punchy lines for impact moments
- Final line should be 3-5 words, devastating

**Visual Brief (Required from Writer)**:
The writer must provide a Visual Brief per scene specifying: WHAT WE SEE, KEY OBJECTS, ANIMATION, TEXT ON SCREEN (3-8 words max), and NARRATIVE ROLE. The engineer builds visuals from this brief — if no brief is provided, request one before coding.

### Step 2: TTS Generation (Writer Agent)

Generate narration with word-level timestamps:

```bash
edge-tts \
  --text "FULL SCRIPT HERE" \
  --voice en-US-ChristopherNeural \
  --rate "+10%" \
  --write-media /opt/tkk/vidgen/tts_OUTPUT.mp3 \
  --write-subtitles /opt/tkk/vidgen/tts_OUTPUT.vtt
```

**Voice**: `en-US-ChristopherNeural` at `+10%` speed (NOT faster).
**Output**: `.mp3` + `.vtt` (word-level timing)

Parse the VTT into scene boundaries:
- Each scene starts at the first word of its narration
- Scene duration = next scene start - current scene start
- Last scene gets extra 2-3s hold for the closer to breathe

### Step 3: Manim Screenplay (Engineer Agent)

Build a manim `.py` file using the v4 template structure:

#### Config
```python
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.frame_width = 9
config.frame_height = 16
config.background_color = "#0B0F18"
config.disable_caching = True
```

#### Palette
```python
GOLD = "#FFD700"
GOLD_DIM = "#B8960F"
RED = "#E63946"
WHITE_SOFT = "#F0F0F0"
MUTED = "#7B8DA0"
BG = "#0B0F18"
SURFACE = "#141C2B"
SURFACE2 = "#1A2538"
BORDER = "#2A3A50"
```

#### Safe Margins
```python
SAFE_W = 8.0    # horizontal: 960px usable, 60px margin each side
SAFE_TOP = 7.2  # top 5%: status bar, clock — nothing above y=7.2
SAFE_BOT = -6.4 # bottom 10%: TikTok description, buttons — nothing below y=-6.4
```
ALL text must use `safe_text()` for horizontal. Vertically, keep all content between `SAFE_TOP` (7.2) and `SAFE_BOT` (-6.4). The top has the phone status bar, the bottom has TikTok's description text and interaction buttons.

#### Required Helpers (copy from v4)
- `gradient_bg()` — dark gradient with subtle ocean glow
- `star_field(n, seed)` — scattered dot particles for depth
- `moai_side(height, color)` — programmatic moai silhouette (adapt per topic)
- `section_div(width, color)` — gold diamond divider line
- `label_pill(txt, color, bg, fs)` — rounded pill label for scene titles
- `safe_text(content, **kwargs)` — auto-scaling text within safe margins
- `load_svg(filename, color, height)` — load SVG icon from `svg_assets/downloaded/`
- Domain shape functions (2-4 per video) — topic-specific VGroup constructions (e.g., `moai_side()`, `ice_pick()`, `cell_cluster()`)

#### Scene Structure (one class per scene)
```python
class Scene1_BeatName(Scene):
    def construct(self):
        # 1. Background + ambient elements
        self.add(gradient_bg(), star_field(12, seed=N))

        # 2. Scene-specific programmatic art
        # (silhouettes, diagrams, charts — NEVER stock photos)

        # 3. Text elements keyed to VTT timestamps
        # Animation delay = VTT_time - scene_start_time

        # 4. Animations (FadeIn, Write, LaggedStart, etc.)
        # Duration: 0.8-1.0s for text reveals (NOT 0.3-0.4s)
        # Flash accents: 0.3-0.4s for emphasis

        # 5. Hold for scene duration
        self.wait(remaining_time)
```

#### Animation Timing Rules
- **Text reveals**: 0.8-1.2s (slow enough to read)
- **Flash/emphasis**: 0.3-0.4s
- **Scene holds**: calculate from VTT, include 0.5s buffer
- **Final scene**: 2-3s silence AFTER last word, then 1.2s fade to black
- **ALL delays derived from VTT timestamps** (non-negotiable)

### Step 4: Render (Engineer Agent)

Each scene renders as a separate subprocess (prevents OOM on 15GB RAM):

```python
for i, scene_cls in enumerate(scenes):
    subprocess.run([
        sys.executable, "-m", "manim", "render",
        "-qh", "--fps", "30",
        "--media_dir", "media",
        "-o", f"scene_{i+1}.mp4",
        __file__, scene_cls
    ])
```

Then concatenate with ffmpeg + audio:

```bash
ffmpeg -f concat -i concat.txt -i tts_audio.mp3 \
  -c:v libx264 -crf 22 -preset medium \
  -c:a aac -b:a 128k \
  output.mp4
```

**Target**: under 8MB for Discord delivery.

### Step 5: Review + Deliver

1. Send to Discord for Astron's review
2. Apply feedback (timing, text, art fixes)
3. When approved, post to social media

---

## Hard Rules (Non-Negotiable)

1. **Always use word-by-word VTT timing** — never eyeball animation delays
2. **No SFX** — no whoosh, impact, transition sounds. Voice only.
3. **Manim only** — never use vidgen/Pillow for production renders
4. **Christopher voice at +10%** — not faster
5. **Safe margins** — 60px from each edge minimum, use `safe_text()`
6. **Programmatic art** — generate illustrations with code, don't use stock photos
7. **Mystery arc** — every video follows the 6-beat structure
8. **Slower animations** — text needs 0.8s+ to appear, let it breathe
9. **Visual-first rendering** — SVG icons + animation = minimum bar. Custom domain shapes = gold standard. Text-heavy headline+caption stacks = BANNED.
10. **Domain shapes required** — Every video must define 2-4 topic-specific shape functions (Polygon/VGroup). See `easter_island_v16.py` for examples.
11. **Text budget** — 3-8 words MAX on screen per scene. Names, numbers, labels only. Voice carries narration.

---

## File Structure

```
/opt/tkk/vidgen/
  tts_{topic}.mp3              # TTS audio
  tts_{topic}.vtt              # Word-level timestamps
  scripts/{topic}.py           # vidgen screenplay (for reference/drafts)
  {topic}_manim.py             # Manim source (production)
  {topic}_v{N}.mp4             # Rendered output
  assets/                      # Background images (if needed)
  media/videos/1920p30/        # Manim intermediate renders
```

---

## Delegation

| Role | Agent | Responsibility |
|------|-------|---------------|
| Lead | tkk-lead | Coordinates pipeline, reviews, delivers to Discord/social |
| Writer | tkk-writer | Script, TTS generation, VTT timing, scene cues |
| Engineer | tkk-engineer | Manim code, programmatic art, rendering |
