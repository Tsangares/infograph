# Manim Archive

Manim Community v0.20.1 was the original render engine for TKK videos.

- **48+ videos** were produced with Manim between January–March 2026
- **Replaced by Remotion** (React/TypeScript) in March 2026 for better component reuse, design tokens, and word-triggered timing
- The unit coordinate system (-8 to +8 y-range, 16 units tall) lives on in `remotion/src/lib/zones.ts` as `unitToPixelY()`

## Legacy Files (on disk, gitignored)

Manim screenplays and helpers remain on disk but are excluded from version control:

- `*_manim.py` — 60 screenplay files (~600 lines each)
- `anim_primitives.py` — shared animation components
- `scene_templates.py` — base scene classes
- `anim_assets.py`, `geo_utils.py`, `geo_locations.py` — helper modules
- `enhance_animations.py`, `migrate_duration.py` — tooling
- `*_bible.json` — story arc planning documents
