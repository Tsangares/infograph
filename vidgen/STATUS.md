# Video Engineer Status — 2026-03-15

## What Exists

### Engine: `/opt/tkk/vidgen/vidgen.py`
Python video generation engine. Renders frames with Pillow, encodes with FFmpeg.

**Layer types:** text, image, svg, shape (rect/circle/line/polyline)

**Animations (14 total):**
- Entrance: `fade_in`, `slide_up/down/left/right`, `scale_in`, `typewriter`, `wipe_right`, `bounce_in`
- TikTok-style: `pop` (1.2x→1.0x bounce), `pop_up` (bubble up + bounce), `word_pop` (word-by-word stagger), `slam` (1.6x→1.0x punch)
- Special: `draw_on` (animated polyline/path), `fade_out`, `fade_in_out`
- Exit: any layer can have `exit_animation` + `exit_duration`

**Background features:**
- Solid color, gradient, image (cover-fit)
- Ken Burns with directional pan (`kb_direction`: left/right/up/down, `kb_zoom`: [start, end])

**Text features:**
- Word wrap (`max_width`), line spacing (`line_height`)
- Background pill (`bg_color`, `bg_padding`, `bg_radius`)
- Shadow, stroke/outline
- Per-layer `opacity` (0.0-1.0, multiplies with animation alpha)

**Image effects:** `blur`, `desaturate`, `tint`

**Post-processing (scene-level):** `vignette`, `letterbox`, `grain`

**Other:**
- `parallax` property for depth
- `validate_screenplay()` — pre-checks all assets/fonts before render
- `preview_grid()` — thumbnail grid of all scenes at 50% res
- `preview_frame()` — single frame at any timestamp
- Image caching (avoids re-reading from disk every frame)

### Encoding
- **Default:** NVENC on `llama` (Tailscale, SSH user `wil`) — RTX 3060 + 3060 Ti
- **Fallback:** CPU libx264 on diort
- Auto-detection: checks if llama is reachable, falls back silently
- Override: `encoder="nvenc"` or `encoder="cpu"`
- Full timing logs for frame render, transfer, encode, total

### NVENC Benchmark (840 frames, 28s @ 1080x1920)
| Step | CPU (diort) | NVENC (llama) |
|------|------------|---------------|
| Encode | 51.5s | 3.6s |
| Transfer | — | ~30s |
| Speed | 1.5x realtime | 8.8x realtime |

Note: llama was down during recent renders. When it's up, total pipeline is ~35s encode vs ~50s CPU.

### Fonts: `/opt/tkk/vidgen/fonts/`
DM Serif Display (Regular, Italic), Bebas Neue, Inter (Regular, Bold), Space Mono (Regular, Bold)

### Venv: `/opt/tkk/vidgen/.venv/`
Python packages: Pillow, moviepy, svgwrite, cairosvg, pydub, edge-tts, numpy

---

## Current Video: Easter Island "Walking Statues"

### Source
TKK source/1 — "Fall of Civilizations" Easter Island podcast. Segment 1 scored 10.0.

### Screenplay: `easter_island.py`
v3 mystery-arc structure (6 scenes, 29s):

| # | Scene | Time | Animation | Background |
|---|-------|------|-----------|------------|
| 1 | THE WRONG ANSWER | 0-4.5s | slam + word_pop | moai_row.jpg (ghosted) |
| 2 | THE CONTRADICTION | 4.5-9s | slam | moai_hillside.jpg (Ken Burns) |
| 3 | THE ORAL TRADITION | 9-14s | fade_in + pop | moai_painting.jpg (Ken Burns) |
| 4 | THE PROOF | 14-19s | pop + slam | walking_technique.png (SVG diagram) |
| 5 | THE SCALE | 19-23.5s | slam + fade_in | easter_island_map.png (Ken Burns) |
| 6 | THE PUNCH | 23.5-29s | fade_in + wipe | moai_hillside2.jpg (Ken Burns) |

### TTS: `tts_narration_v3.mp3`
Generated with edge-tts, `en-US-GuyNeural` voice, +30% rate. 31s duration.

### Assets: `/opt/tkk/vidgen/assets/`
| File | Source | Used in |
|------|--------|---------|
| moai_row.jpg | Wikimedia (Ahu Tongariki) | Scene 1, 2 |
| moai_hillside.jpg | Wikimedia (Rano Raraku) | Scene 2 |
| moai_hillside2.jpg | Wikimedia (Rano Raraku alt) | Scene 6 |
| moai_painting.jpg | Wikimedia (Hodges painting) | Scene 3 |
| moai_quarry.jpg | Wikimedia (Rano Raraku quarry) | unused (replaced) |
| moai_museum.jpg | Wikimedia (museum moai) | unused (replaced) |
| easter_island_map.png | Wikimedia (topo map) | Scene 5 |
| walking_technique.svg | Created by agent | Scene 4 (source) |
| walking_technique.png | Pre-rendered from SVG | Scene 4 (background) |
| moai_unfinished.jpg | Wikimedia (Te Tokanga) | unused (replaced by SVG) |

### SVG Diagram: `assets/walking_technique.svg`
3-rope walking technique diagram. Shows:
- Moai standing upright with pukao (red hat)
- Two red pull ropes to left/right teams (3 stick figures each side)
- Gold stabilizer rope behind with 2-person team
- Rocking motion arrows, forward direction arrow
- Legend box at bottom
- Dark technical background with grid pattern
- Ground plane with road markings

### Output Files
| File | Version | Size | Notes |
|------|---------|------|-------|
| easter_island_v3.mp4 | v3 (latest) | 3.7 MB | Pop/slam animations, SVG diagram |
| easter_island_walking_statues_v2.mp4 | v2 | 12.3 MB | Audit v1 fixes applied |
| easter_island_walking_statues.mp4 | v1 | 5.9 MB | First render |
| demo_output.mp4 | demo | 0.3 MB | Toolkit test video |

---

## Known Issues

### Asset Problems (from AUDIT-easter-island-v2.md)
- **Scene 3** (moai_painting.jpg): Shows statues on a platform, not walking. Needs walking technique image or diagram.
- **Scene 5** (easter_island_map.png): Generic topo map, doesn't show moai transport routes. Low-res for 1080x1920.
- **Scene 6** (moai_hillside2.jpg): Same quarry image as scene 2, not cinematic enough. Needs sunset/golden hour shot.
- **2011 experiment photo**: Not on Wikimedia Commons. It's a National Geographic image. Astron was flagged — need them to source it or approve generating one.

### Rendering Speed
- Frame rendering is the bottleneck: ~2.4 fps on diort (CPU-bound Pillow)
- 29s video = ~365s to render frames + ~24s encode = ~389s total
- Ken Burns scenes are slowest (resize + crop every frame)
- Image caching helps (~20% improvement) but not enough
- Potential optimization: skip re-rendering static frames after animations settle (ticket P3 item 12)

### NVENC
- llama was unreachable during last 3 renders (fell back to CPU each time)
- When working: 3.6s encode vs 51.5s CPU = 14x faster
- Transfer overhead (~30s rsync) means net benefit is only ~20s saved
- Could optimize: pipe frames directly over SSH instead of rsync-then-encode

---

## Tickets (in `/opt/tkk/vidgen/`)

| File | Status | Summary |
|------|--------|---------|
| TICKET-vidgen-engine-v2.md | **Done** | SVG layers, pop animations, opacity, Ken Burns pan, exit anims, word wrap, validation, preview grid |
| TICKET-writer-easter-island-v3.md | **Done** | Mystery-arc screenplay rewrite |
| AUDIT-easter-island.md | **Done** | v1 text/layout audit — all fixed |
| AUDIT-easter-island-v2.md | **Partial** | v2 asset audit — SVG created for scene 4, scenes 3/5/6 still have wrong images |
| TICKET-lead-v4.md | Unread | From lead, not yet reviewed |
| TICKET-video-engineer-v4.md | Unread | From lead, not yet reviewed |
| TICKET-writer-v4.md | Unread | From lead, not yet reviewed |

---

## Infrastructure

### Machines
| Machine | Role | Access |
|---------|------|--------|
| diort | Frame rendering, Pillow, edge-tts | Local |
| llama | NVENC encoding (RTX 3060 + 3060 Ti) | `ssh wil@llama` (Tailscale) |
| fabian | TKK app server (port 8007) | `ssh root@fabian` |

### Key Paths
| Path | What |
|------|------|
| `/opt/tkk/vidgen/` | Video engine, screenplays, assets, output |
| `/opt/tkk/vidgen/.venv/` | Python venv |
| `/opt/tkk/vidgen/assets/` | Images, SVGs |
| `/opt/tkk/vidgen/fonts/` | TTF fonts |
| `/opt/tkk/` | TKK app (app.py, content.py, assembler.py, db.py) |
| `/opt/tkk/tkk.db` | TKK database with sources/segments |

### User Preferences (from Astron)
- Work in `/opt/` not workspace-ape
- Use local systems first (diort before cloud/API)
- No OpenAI API calls without explicit permission
- No Co-Authored-By on commits
- Use subagents aggressively for parallelism

---

## Next Steps (Recommended)

1. **Read unread tickets** — TICKET-lead-v4.md, TICKET-video-engineer-v4.md, TICKET-writer-v4.md
2. **Fix remaining assets** — scenes 3, 5, 6 still have wrong/weak images
3. **Frame render speed** — currently 2.4 fps, could be 5-10x with static frame caching
4. **Send video to Astron** — they asked for it over Discord but we can't attach files. Need to either serve via URL or find another delivery method.
