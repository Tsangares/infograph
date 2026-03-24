# TKK Project Status

**Last updated**: 2026-03-24
**Working directory**: `/opt/tkk/`

---

## What Is TKK

TikTok short-form video production pipeline. Generates mystery-arc narrated videos (TikTok/Reels/Shorts) with animated graphics. 48+ videos rendered, first TikTok upload completed 2026-03-18.

## Infrastructure

| Component | Location | Notes |
|-----------|----------|-------|
| Render engine | **Remotion** (React/TypeScript) | Only renderer |
| TTS primary | **Fish Audio** (ELITE voice) | API key in `.env` |
| TTS fallback | **edge-tts** (en-US-ChristopherNeural) | Free, word-level VTT timestamps |
| Dashboard | **clips.applesauce.chat** (port 8020) | Library, editor, studio chat |
| MCP server | `/opt/tkk/vidgen/mcp_server.py` | Pipeline exposed as Claude Code tools |
| Local dev | **diort** | All rendering runs here |
| Encoding | libx264 CPU local | — |

## Workflow (CURRENT)

Single Claude Code session using MCP tools:

```
1. Write manifest (word-triggered JSON, mystery arc)
2. Fish Audio generates TTS mp3
3. Word triggers resolved from Whisper timestamps
4. Preview PNGs rendered for all scenes
5. QA checks previews (layout + readability)
6. Full render (Remotion → ffmpeg → _final.mp4)
7. Manual TikTok upload
```

## OpenClaw Agents (DISCONTINUED 2026-03-19)

The 3-agent system (tkk-lead, tkk-writer, tkk-engineer) has been retired. Reasons:
- 4-day prioritization delays, no notification mechanism
- ~2M tokens per video across agents
- Single Claude Code session is faster and cheaper

See `/opt/tkk/archive/OPENCLAW-POSTMORTEM.md` for full details.
Agent workspaces archived in `/opt/tkk/archive/workspaces-2026-03-19.tar.gz`.

## Rules (Non-Negotiable)

1. **Remotion only** — All new videos use Remotion manifests.
2. **Fish Audio TTS** — Primary voice. edge-tts as fallback only.
3. **No SFX** — No whoosh, impact, or transition sounds. Voice only.
4. **Preview before render** — Every scene gets a PNG preview, QA'd before full animation.
5. **Mystery arc structure** — hook → wrong answer → contradiction → proof → betrayal → punch.

## Key Files

```
/opt/tkk/
├── vidgen/
│   ├── remotion/src/manifests/    # Remotion manifests (word-triggered JSON)
│   ├── generate_tts.py            # Fish Audio TTS generation
│   ├── resolve_word_triggers.py   # Whisper-based word trigger resolution
│   ├── mcp_server.py              # MCP server for Claude Code
│   ├── qa_layout.py               # Layout QA
│   ├── qa_readability.py          # Readability QA
│   ├── qa_remotion_sync.py        # Remotion sync QA
│   ├── PRODUCTION_GUIDE.md        # Canonical production reference
│   └── MANIM_ARCHIVE.md           # Legacy Manim reference
├── clips/                         # Dashboard (clips.applesauce.chat)
├── archive/                       # Archived agent workspaces + deprecated code
└── CLAUDE.md                      # Project context for Claude Code
```
