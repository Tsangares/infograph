#!/usr/bin/env python3
"""TTS generation for vidgen screenplays.

PRIMARY ENGINE: Fish Audio (ELITE voice) — use this for ALL production TTS.
Fallback engines (edge-tts, kokoro, piper) exist but should NOT be used
for final videos. Fish Audio is the TKK standard voice.

Usage:
    python generate_tts.py aral_sea.json                            # Fish Audio (default)
    python generate_tts.py aral_sea.json --engine fish              # explicit
    python generate_tts.py aral_sea.json --engine edge              # fallback only
    python generate_tts.py --text "Hello world" --output test.mp3
    python generate_tts.py --status

Env vars (in /opt/tkk/.env):
    FISH_AUDIO_API_KEY  — API key for Fish Audio
    FISH_AUDIO_VOICE_ID — Voice model ID (default: ELITE)
"""

import argparse
import importlib.util
import logging
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="[tts %(levelname)s] %(message)s")
log = logging.getLogger("tts")

# Load .env from /opt/tkk/.env if it exists
_env_path = Path("/opt/tkk/.env")
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

# Fish Audio config
FISH_API_KEY = os.environ.get("FISH_AUDIO_API_KEY", "")
FISH_VOICE_ID = os.environ.get("FISH_AUDIO_VOICE_ID", "d8a1340984ee4b63ad1ffae27a6a4339")
FISH_API_URL = "https://api.fish.audio/v1/tts"


def _engine_available(name: str) -> bool:
    """Check if a TTS engine is installed/configured."""
    if name == "fish":
        return bool(FISH_API_KEY)
    elif name == "kokoro":
        return importlib.util.find_spec("kokoro") is not None
    elif name == "piper":
        return importlib.util.find_spec("piper") is not None or _which("piper")
    elif name == "edge":
        return importlib.util.find_spec("edge_tts") is not None
    return False


def _which(cmd: str) -> bool:
    """Check if a command exists on PATH."""
    try:
        subprocess.run(["which", cmd], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


# ── Fish Audio TTS (PRIMARY — use for all production) ──

def generate_fish(text: str, output: str, voice_id: str = None,
                  speed: float = 1.0) -> str:
    """Generate TTS audio using Fish Audio API.

    This is the PRIMARY TTS engine for TKK. Use the ELITE voice for all videos.
    Requires FISH_AUDIO_API_KEY in environment or /opt/tkk/.env.
    """
    import requests

    api_key = FISH_API_KEY
    if not api_key:
        log.error("Fish Audio: FISH_AUDIO_API_KEY not set. Check /opt/tkk/.env")
        return ""

    vid = voice_id or FISH_VOICE_ID
    log.info(f"Fish Audio: generating with voice '{vid}', speed {speed}x...")

    payload = {
        "text": text,
        "reference_id": vid,
        "format": "mp3",
        "mp3_bitrate": int(os.environ.get("TKK_FISH_BITRATE", "192")),
        "latency": "normal",
    }
    if speed != 1.0:
        payload["prosody"] = {"speed": speed, "volume": 0}

    try:
        resp = requests.post(
            FISH_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=120,
        )
        if resp.status_code != 200:
            log.error(f"Fish Audio: API error {resp.status_code}: {resp.text[:300]}")
            return ""

        with open(output, "wb") as f:
            f.write(resp.content)

        size_kb = os.path.getsize(output) // 1024
        log.info(f"Fish Audio: saved {output} ({size_kb} KB)")
        return output

    except Exception as e:
        log.error(f"Fish Audio: request failed: {e}")
        return ""


# ── Kokoro TTS (local fallback) ──

def generate_kokoro(text: str, output: str, voice: str = "af_heart",
                    speed: float = 1.0) -> str:
    """Generate TTS audio using Kokoro. Local, CPU-friendly."""
    try:
        from kokoro import KPipeline
    except ImportError:
        log.error("Kokoro not installed. Run: pip install kokoro")
        return ""

    log.info(f"Kokoro: generating with voice '{voice}', speed {speed}x...")

    lang_code = voice[:2] if len(voice) >= 2 else "a"
    lang_map = {"af": "a", "am": "a", "bf": "b", "bm": "b"}
    lang = lang_map.get(lang_code, "a")

    pipeline = KPipeline(lang_code=lang)

    all_audio = []
    for i, (gs, ps, audio) in enumerate(pipeline(text, voice=voice, speed=speed)):
        all_audio.append(audio)

    if not all_audio:
        log.error("Kokoro: no audio generated")
        return ""

    import numpy as np
    import soundfile as sf

    combined = np.concatenate(all_audio)
    wav_path = output.replace(".mp3", ".wav")
    sf.write(wav_path, combined, 24000)

    if output.endswith(".mp3"):
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-i", wav_path, "-codec:a", "libmp3lame",
                 "-b:a", "192k", output],
                capture_output=True, check=True,
            )
            os.remove(wav_path)
            log.info(f"Kokoro: saved {output}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            log.warning("ffmpeg not available for MP3 conversion, keeping WAV")
            output = wav_path
            log.info(f"Kokoro: saved {output}")
    else:
        log.info(f"Kokoro: saved {wav_path}")
        output = wav_path

    return output


# ── Piper TTS (local fallback) ──

def generate_piper(text: str, output: str, model: str = "en_US-lessac-medium",
                   speed: float = 1.0) -> str:
    """Generate TTS audio using Piper (local, fast, robotic)."""
    try:
        wav_path = output.replace(".mp3", ".wav")
        cmd = ["piper", "--model", model, "--output_file", wav_path]
        if speed != 1.0:
            cmd.extend(["--length-scale", str(1.0 / speed)])

        proc = subprocess.run(
            cmd, input=text.encode(), capture_output=True, timeout=120,
        )
        if proc.returncode != 0:
            log.error(f"Piper failed: {proc.stderr.decode()[:200]}")
            return ""

        if output.endswith(".mp3"):
            subprocess.run(
                ["ffmpeg", "-y", "-i", wav_path, "-codec:a", "libmp3lame",
                 "-b:a", "192k", output],
                capture_output=True, check=True,
            )
            os.remove(wav_path)
        else:
            output = wav_path

        log.info(f"Piper: saved {output}")
        return output
    except FileNotFoundError:
        log.error("Piper not found. Install: pip install piper-tts")
        return ""
    except Exception as e:
        log.error(f"Piper failed: {e}")
        return ""


# ── Edge-TTS (Microsoft cloud, free fallback) ──

def generate_edge(text: str, output: str, voice: str = "en-US-GuyNeural",
                  speed: str = "+0%") -> str:
    """Generate TTS audio using Edge-TTS (requires internet)."""
    try:
        import asyncio
        import edge_tts
    except ImportError:
        log.error("edge-tts not installed. Run: pip install edge-tts")
        return ""

    async def _generate():
        communicate = edge_tts.Communicate(text, voice, rate=speed)
        await communicate.save(output)

    log.info(f"Edge-TTS: generating with voice '{voice}'...")
    asyncio.run(_generate())
    log.info(f"Edge-TTS: saved {output}")
    return output


# ── Screenplay parser ──

def extract_tts_script(screenplay_path: str) -> str:
    """Extract TTS_SCRIPT from a screenplay .py/.tsx file or JSON manifest."""
    import json as _json

    # JSON manifest (Remotion): read ttsScript field
    if screenplay_path.endswith('.json'):
        with open(screenplay_path) as f:
            data = _json.load(f)
        return data.get('ttsScript', '')

    with open(screenplay_path) as f:
        content = f.read()

    # TSX/JS template literal: export const TTS_SCRIPT = `...`
    match = re.search(r'(?:export\s+)?(?:const|let|var)\s+TTS_SCRIPT\s*=\s*`(.*?)`', content, re.DOTALL)
    if match:
        return match.group(1).strip()

    match = re.search(r'TTS_SCRIPT\s*=\s*"""(.*?)"""', content, re.DOTALL)
    if match:
        return match.group(1).strip()

    match = re.search(r"TTS_SCRIPT\s*=\s*'''(.*?)'''", content, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Fall back to VTT narration lines in docstring
    narration_lines = re.findall(r'#\s*Scene\s*\d+:\s*"([^"]+)"', content)
    if narration_lines:
        return "\n".join(narration_lines)

    # Try extracting from VTT cue lines in docstring
    vtt_lines = re.findall(r'\d+\.\d+\s+\(\d+\.\d+\)\s+(.+)', content)
    if vtt_lines:
        return "\n".join(vtt_lines)

    log.warning("No TTS_SCRIPT or narration comments found in screenplay")
    return ""


# ── Main ──

def generate_tts(text: str, output: str, engine: str = "auto",
                 voice: str = None, speed: float = 1.0) -> str:
    """Generate TTS audio, auto-selecting the best available engine.

    Priority: fish > edge > kokoro > piper
    Fish Audio (ELITE voice) is the standard for all TKK production videos.
    """
    if engine == "auto":
        if _engine_available("fish"):
            engine = "fish"
        elif _engine_available("edge"):
            engine = "edge"
        elif _engine_available("kokoro"):
            engine = "kokoro"
        elif _engine_available("piper"):
            engine = "piper"
        else:
            log.error("No TTS engine available. Set FISH_AUDIO_API_KEY in /opt/tkk/.env")
            log.error("  or install a fallback: pip install edge-tts")
            return ""

    log.info(f"Using engine: {engine}")

    if engine == "fish":
        return generate_fish(text, output, voice_id=voice, speed=speed)
    elif engine == "kokoro":
        return generate_kokoro(text, output, voice=voice or "af_heart", speed=speed)
    elif engine == "piper":
        return generate_piper(text, output, speed=speed)
    elif engine == "edge":
        return generate_edge(text, output, voice=voice or "en-US-GuyNeural")
    else:
        log.error(f"Unknown engine: {engine}")
        return ""


def print_status():
    """Print TTS engine availability."""
    print("\n=== TTS Engine Status ===\n")

    engines = [
        ("fish", "Fish Audio ELITE (PRODUCTION STANDARD)", "Set FISH_AUDIO_API_KEY in /opt/tkk/.env"),
        ("edge", "Microsoft Edge-TTS, free fallback", "pip install edge-tts"),
        ("kokoro", "Local CPU, good quality", "pip install kokoro"),
        ("piper", "Local, fast, robotic", "pip install piper-tts"),
    ]

    for name, desc, install in engines:
        ready = _engine_available(name)
        marker = "+" if ready else "X"
        label = "READY" if ready else "NOT CONFIGURED"
        print(f"  [{marker}] {name:12s} — {desc} [{label}]")
        if not ready:
            print(f"      Fix: {install}")

    print()
    if _engine_available("fish"):
        print(f"  Fish Audio voice: {FISH_VOICE_ID}")
        print(f"  Fish Audio API: configured")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate TTS audio for vidgen")
    parser.add_argument("screenplay", nargs="?", help="Path to screenplay .py file")
    parser.add_argument("--text", help="Direct text to speak")
    parser.add_argument("--output", "-o", default=None, help="Output file path")
    parser.add_argument("--engine", choices=["auto", "fish", "kokoro", "piper", "edge"],
                        default="auto")
    parser.add_argument("--voice", help="Voice/model ID (engine-specific)")
    parser.add_argument("--speed", type=float, default=1.0, help="Speed multiplier")
    parser.add_argument("--status", action="store_true", help="Print engine availability")

    args = parser.parse_args()

    if args.status:
        print_status()
    elif args.text:
        output = args.output or "tts_output.mp3"
        generate_tts(args.text, output, engine=args.engine,
                     voice=args.voice, speed=args.speed)
    elif args.screenplay:
        script = extract_tts_script(args.screenplay)
        if script:
            sp = Path(args.screenplay)
            # Strip _manim suffix for cleaner output names
            stem = sp.stem.replace("_manim", "")
            # JSON manifests live in remotion/src/manifests/ — output to vidgen root
            if sp.suffix == '.json':
                out_dir = Path(__file__).parent
            else:
                out_dir = sp.parent
            output = args.output or str(out_dir / f"tts_{stem}.mp3")
            log.info(f"Script ({len(script)} chars):\n{script[:200]}...")
            result = generate_tts(script, output, engine=args.engine,
                                  voice=args.voice, speed=args.speed)

            # Auto-generate Whisper alignment for sync QA
            if result and os.path.exists(result):
                try:
                    from narration_sync import whisper_align
                    log.info("Running Whisper alignment for sync QA...")
                    whisper_align(result)
                except Exception as e:
                    log.warning(f"Whisper alignment failed (non-fatal): {e}")

                # Auto-derive timings for Remotion manifests
                if sp.suffix == '.json':
                    import json as _json2
                    with open(args.screenplay) as _mf:
                        _manifest_data = _json2.load(_mf)
                    _is_word_triggered = bool(
                        _manifest_data.get("scenes") and "scene_anchor" in _manifest_data["scenes"][0]
                    )
                    whisper_json = result + ".json"

                    if _is_word_triggered and os.path.exists(whisper_json):
                        try:
                            from resolve_word_triggers import resolve_word_triggers
                            log.info("Word-triggered manifest detected — resolving anchors...")
                            resolved_path = resolve_word_triggers(args.screenplay, whisper_json)
                            log.info(f"Resolved manifest: {resolved_path}")
                        except Exception as e:
                            log.warning(f"Word-trigger resolution failed (non-fatal): {e}")
                    elif os.path.exists(whisper_json):
                        try:
                            from derive_timings import derive_timings
                            log.info("Legacy manifest — deriving scene timings from Whisper data...")
                            derive_timings(args.screenplay, whisper_json)
                        except Exception as e:
                            log.warning(f"Timing derivation failed (non-fatal): {e}")
        else:
            log.error("No narration text found")
    else:
        print_status()
        parser.print_help()
