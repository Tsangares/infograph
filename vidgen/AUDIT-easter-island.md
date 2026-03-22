# Audit: Easter Island Walking Statues (v1)

**File**: `easter_island_walking_statues.mp4` (28s, 1080x1920, 5.9MB)
**Source**: `easter_island.py`
**Reviewer**: Ape
**Date**: 2026-03-15

---

## HIGH PRIORITY

### Scene 4 (Experiment, 14-19s) — Replace background image
`moai_quarry.jpg` is mostly empty sky with a rock sliver in the bottom-left. Looks like a bad crop. This is the "proof" beat — it needs a strong visual.
- **Best option**: Image of the 2011 Lipo/Hunt experiment (people rocking a replica moai with ropes)
- **Fallback**: Rano Raraku quarry showing unfinished moai in the hillside
- Fetch a new asset and update `"background"` in scene 4

### Scene 4 — Update caption text
Current text ("Experiments proved / the legends true") is too vague for this beat.
- **Replace with**: `"In 2011, 18 people"` / `"walked a 5-ton replica"` (or similar with the specific detail)
- This is the payoff scene — give the viewer the fact

---

## MEDIUM PRIORITY

### Scene 3 (Ropes, 9-14s) — Rewrite caption
Current: `"Moved upright, rocked"` / `"with ropes by Islanders"` — reads choppy and passive.
- **Option A**: `"Teams rocked them forward"` / `"step by step with ropes"`
- **Option B**: `"Islanders rocked them side to side"` / `"like walking a refrigerator"`
- **Option C**: `"Rocked upright and walked forward"` / `"with just ropes and teamwork"`

### Scenes 2, 3, 4 — Break up layout repetition
All three scenes use identical bottom-third black bar + two-line text. Gets monotonous across 15 seconds.
- Move scene 3 text to **top of frame** (position Y ~200-300 instead of 1580-1660, dark bar at top)
- Or try **center-screen** on scene 4 to match the "big reveal" energy
- Keep scene 2 as-is (bottom-third works for the establishing shot)

---

## LOW PRIORITY

### Scene 1 (Title, 0-4s) — Background image invisible
The `#000000BB` overlay on `moai_hillside.jpg` makes the background pure black. Two options:
- Lighten overlay to `#00000077` so moai ghosts through (adds atmosphere)
- Remove the image layer entirely (saves render time, clean black already works)

### Scene 5 (Map, 19-23s) — Word choice
`"Shuffling down ancient roads"` — "shuffling" is weak for 80-ton stone giants.
- Change to `"Rocking down ancient roads"` or `"Swaying down volcanic roads"`

### Scene 6 (Close, 23-28s) — Background image invisible
`#000000AA` overlay on `moai_museum.jpg` makes it near-black. The text-only look actually works as a deliberate style choice for the closer. Either:
- Lighten to `#00000066` to let the image show
- Remove the background image if text-only was intentional

---

## DO NOT CHANGE

- **Scene 1 hook**: "Did Easter Island's / Statues WALK?" — strong open
- **Scene 6 closer**: "The islanders always said / the statues walked. / We just didn't believe them." — best moment in the video

---

## Quick Reference

| Scene | Time | Visual | Text | Priority |
|-------|------|--------|------|----------|
| 1 Title | 0-4s | Fix overlay opacity | Keep | Low |
| 2 Moai | 4-9s | Good | Keep | — |
| 3 Ropes | 9-14s | Move text position | Rewrite | Medium |
| 4 Experiment | 14-19s | **New image** | **Add specifics** | **High** |
| 5 Map | 19-23s | Good | Fix "shuffling" | Low |
| 6 Close | 23-28s | Fix/drop bg | Keep | Low |
