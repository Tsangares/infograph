#!/usr/bin/env python3
"""
narration_sync.py — Extract word-level timestamps from edge-tts narration.

Generates TTS audio WITH word boundary metadata, producing a timing map
that video scenes consume instead of hardcoded durations.

Usage:
    from narration_sync import generate_synced_audio, load_timing

    # Generate audio + timing data
    generate_synced_audio(script, "narration.mp3")

    # Load timing in video script
    timing = load_timing("narration.mp3.json")
    timing.time_of("887 statues")  # -> 26.3 (seconds)
    timing.scene_at(19.5)          # -> "18 people. 3 ropes."
"""

import asyncio
import json
import re
import logging
from pathlib import Path

log = logging.getLogger("narration_sync")
if not log.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("[sync %(levelname)s] %(message)s"))
    log.addHandler(_h)
    log.setLevel(logging.INFO)


def generate_synced_audio(text: str, output: str,
                          voice: str = "en-US-ChristopherNeural",
                          speed: str = "+0%") -> str:
    """Generate TTS audio with word-level timing metadata.

    Produces:
      - {output}          — the audio file (mp3)
      - {output}.json     — word-level timing data

    Returns path to the timing JSON.
    """
    import edge_tts

    metadata_path = output + ".json"
    word_boundaries = []

    async def _generate():
        communicate = edge_tts.Communicate(text, voice, rate=speed,
                                            boundary='WordBoundary')
        # Collect word boundaries during generation
        with open(output, "wb") as audio_file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    # edge-tts offsets are in 100-nanosecond ticks (SSML units)
                    # 10,000,000 ticks = 1 second
                    TICKS_PER_SEC = 10_000_000
                    word_boundaries.append({
                        "text": chunk["text"],
                        "offset_ticks": chunk["offset"],
                        "duration_ticks": chunk["duration"],
                        "offset_s": chunk["offset"] / TICKS_PER_SEC,
                        "end_s": (chunk["offset"] + chunk["duration"]) / TICKS_PER_SEC,
                    })

    log.info(f"Generating synced audio: {voice}")
    asyncio.run(_generate())

    # Save timing data
    timing_data = {
        "voice": voice,
        "speed": speed,
        "words": word_boundaries,
        "script": text,
    }
    with open(metadata_path, "w") as f:
        json.dump(timing_data, f, indent=2)

    log.info(f"Audio: {output}")
    log.info(f"Timing: {metadata_path} ({len(word_boundaries)} words)")
    return metadata_path


class NarrationTiming:
    """Query interface for narration timing data."""

    def __init__(self, timing_path: str):
        with open(timing_path) as f:
            data = json.load(f)
        self.words = data["words"]
        self.script = data.get("script", "")

    def time_of(self, phrase: str) -> float:
        """Get the start time (seconds) of a phrase in the narration.

        Searches for the phrase (case-insensitive) in the word sequence.
        Returns the offset of the first word of the match.
        """
        phrase_lower = phrase.lower().strip()
        phrase_words = phrase_lower.split()

        for i in range(len(self.words)):
            # Check if phrase_words match starting at position i
            match = True
            for j, pw in enumerate(phrase_words):
                if i + j >= len(self.words):
                    match = False
                    break
                # Strip punctuation for comparison, keep digits
                word_text = re.sub(r'[^\w\d]', '', self.words[i + j]["text"].lower())
                pw_clean = re.sub(r'[^\w\d]', '', pw)
                # Handle edge-tts combining words like "In 2011" -> single token
                if len(phrase_words) == 1 or (j == 0 and ' ' in self.words[i]["text"]):
                    # Check if the full token contains our search
                    if pw_clean in word_text:
                        continue
                if word_text != pw_clean:
                    match = False
                    break
            if match:
                return self.words[i]["offset_s"]

        # Fuzzy fallback: find first word that matches
        first_word = re.sub(r'[^\w]', '', phrase_words[0])
        for w in self.words:
            if re.sub(r'[^\w]', '', w["text"].lower()) == first_word:
                return w["offset_s"]

        log.warning(f"Phrase not found: '{phrase}'")
        return 0.0

    def end_of(self, phrase: str) -> float:
        """Get the end time (seconds) of a phrase."""
        phrase_lower = phrase.lower().strip()
        phrase_words = phrase_lower.split()

        for i in range(len(self.words)):
            match = True
            for j, pw in enumerate(phrase_words):
                if i + j >= len(self.words):
                    match = False
                    break
                word_text = re.sub(r'[^\w]', '', self.words[i + j]["text"].lower())
                pw_clean = re.sub(r'[^\w]', '', pw)
                if word_text != pw_clean:
                    match = False
                    break
            if match and i + len(phrase_words) - 1 < len(self.words):
                last = self.words[i + len(phrase_words) - 1]
                return last["end_s"]

        return self.time_of(phrase) + 1.0  # fallback

    def duration_between(self, phrase_start: str, phrase_end: str) -> float:
        """Get duration between two phrases."""
        return self.time_of(phrase_end) - self.time_of(phrase_start)

    def scene_duration(self, start_phrase: str, end_phrase: str) -> float:
        """Get scene duration from start of one phrase to start of another."""
        return self.time_of(end_phrase) - self.time_of(start_phrase)

    def print_timeline(self):
        """Print the full word timeline."""
        for w in self.words:
            print(f"  {w['offset_s']:6.2f}s  {w['text']}")

    def print_phrases(self, phrases: list):
        """Print timing for specific phrases."""
        for p in phrases:
            t = self.time_of(p)
            e = self.end_of(p)
            print(f"  {t:6.2f}s - {e:6.2f}s  \"{p}\"")


def whisper_align(audio_path: str, script: str = None) -> str:
    """Extract word timestamps from any MP3 using Whisper forced alignment.

    Saves {audio_path}.json in narration_sync format so NarrationTiming works on it.
    Returns path to the timing JSON.
    """
    import whisper

    audio_path = str(audio_path)
    metadata_path = audio_path + ".json"

    log.info(f"Running Whisper alignment on {audio_path}")
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, word_timestamps=True, language="en")

    word_boundaries = []
    for segment in result.get("segments", []):
        for w in segment.get("words", []):
            word_boundaries.append({
                "text": w["word"].strip(),
                "offset_s": round(w["start"], 3),
                "end_s": round(w["end"], 3),
            })

    timing_data = {
        "source": "whisper",
        "model": "base",
        "words": word_boundaries,
        "script": script or result.get("text", ""),
    }
    with open(metadata_path, "w") as f:
        json.dump(timing_data, f, indent=2)

    log.info(f"Whisper alignment: {metadata_path} ({len(word_boundaries)} words)")
    return metadata_path


def load_timing(path: str) -> NarrationTiming:
    """Load timing data from JSON file."""
    return NarrationTiming(path)


if __name__ == "__main__":
    import sys

    script = """For decades, scientists said Easter Island's statues were dragged on wooden sleds.
But there's a problem. The island had almost no trees.
The Rapa Nui people always had a different answer. The statues walked.
In 2011, archaeologists tested it. 18 people. 3 ropes. A 5-ton replica. It walked.
887 statues. Moved up to 18 km. All by walking.
The Rapa Nui told us the truth for centuries. We just didn't listen."""

    output = "tts_narration_synced.mp3"

    # Generate
    timing_path = generate_synced_audio(script, output)

    # Print timeline
    timing = load_timing(timing_path)
    print("\n=== Full Timeline ===")
    timing.print_timeline()

    print("\n=== Scene Beats ===")
    timing.print_phrases([
        "For decades",
        "dragged on wooden sleds",
        "But there's a problem",
        "almost no trees",
        "The Rapa Nui people",
        "The statues walked",
        "In 2011",
        "18 people",
        "3 ropes",
        "A 5-ton replica",
        "It walked",
        "887 statues",
        "Moved up to 18 km",
        "All by walking",
        "The Rapa Nui told us",
        "the truth for centuries",
        "We just didn't listen",
    ])
