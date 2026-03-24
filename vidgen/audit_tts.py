#!/usr/bin/env python3
"""TTS Script Audit — Word count, duration analysis, and cut suggestions.

Audits TTS_SCRIPT content in screenplays against the target word budget.
At 150 WPM (measured Fish Audio ELITE average):
  - Target: 70 words = ~28s (TikTok sweet spot)
  - Hard max: 90 words = ~36s
  - FAIL threshold: >90 words
  - WARN threshold: >80 words

Usage:
    python3 audit_tts.py                           # audit all, table output
    python3 audit_tts.py some_topic.json           # audit one with per-sentence breakdown
    python3 audit_tts.py --json                    # JSON output for tooling
"""

import json
import re
import subprocess
import sys
from pathlib import Path

VIDGEN = Path(__file__).parent
WPM = 150.0
TARGET_WORDS = 70
WARN_WORDS = 80
FAIL_WORDS = 90

# Common filler phrases that can often be cut
FILLER_PHRASES = [
    "it's worth noting",
    "it is worth noting",
    "in fact",
    "the reality is",
    "the truth is",
    "as it turns out",
    "what's interesting is",
    "here's the thing",
    "the thing is",
    "believe it or not",
    "you might think",
    "you might not know",
    "what you might not know",
    "as a matter of fact",
    "when you think about it",
    "it turns out",
    "at the end of the day",
    "the bottom line is",
    "to put it simply",
    "in other words",
    "needless to say",
    "interestingly enough",
    "perhaps unsurprisingly",
    "not surprisingly",
    "what's more",
    "more importantly",
]


def _ffprobe_duration(filepath: Path) -> float | None:
    """Get duration of audio file via ffprobe."""
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(filepath)],
            capture_output=True, text=True, timeout=10,
        )
        return float(r.stdout.strip())
    except Exception:
        return None


def _extract_tts_script(content: str) -> str:
    """Extract TTS_SCRIPT from screenplay source."""
    match = re.search(r'TTS_SCRIPT\s*=\s*"""(.*?)"""', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"TTS_SCRIPT\s*=\s*'''(.*?)'''", content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    # Split on sentence-ending punctuation followed by space or end
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in parts if s.strip()]


def audit_one(screenplay_path: Path) -> dict:
    """Audit a single screenplay's TTS script.

    Returns dict with word count, duration estimates, status, and per-sentence breakdown.
    """
    content = screenplay_path.read_text()
    stem = screenplay_path.stem.replace("_manim", "")
    tts_script = _extract_tts_script(content)

    if not tts_script:
        return {
            "stem": stem,
            "filename": screenplay_path.name,
            "word_count": 0,
            "tts_script": "",
            "sentences": [],
            "est_duration": 0.0,
            "actual_duration": None,
            "target_words": TARGET_WORDS,
            "overrun_words": 0,
            "status": "SKIP",
            "detail": "No TTS_SCRIPT found",
        }

    words = tts_script.split()
    word_count = len(words)
    est_duration = word_count / WPM * 60

    # Check for actual TTS audio
    tts_path = VIDGEN / f"tts_{stem}.mp3"
    actual_duration = _ffprobe_duration(tts_path) if tts_path.exists() else None

    # Per-sentence breakdown
    sentences = []
    for s in _split_sentences(tts_script):
        s_words = len(s.split())
        sentences.append({
            "text": s,
            "word_count": s_words,
            "est_seconds": round(s_words / WPM * 60, 1),
            "flag": s_words > 12,
        })

    overrun = max(0, word_count - TARGET_WORDS)
    if word_count > FAIL_WORDS:
        status = "FAIL"
    elif word_count > WARN_WORDS:
        status = "WARN"
    else:
        status = "OK"

    return {
        "stem": stem,
        "filename": screenplay_path.name,
        "word_count": word_count,
        "tts_script": tts_script,
        "sentences": sentences,
        "est_duration": round(est_duration, 1),
        "actual_duration": round(actual_duration, 1) if actual_duration else None,
        "target_words": TARGET_WORDS,
        "overrun_words": overrun,
        "status": status,
    }


def _get_posted_stems() -> set[str]:
    """Return stems of videos marked as posted in video_metadata.json."""
    meta_path = VIDGEN / "video_metadata.json"
    if not meta_path.exists():
        return set()
    try:
        data = json.loads(meta_path.read_text())
    except (json.JSONDecodeError, OSError):
        return set()
    posted = set()
    for filename, info in data.items():
        if info.get("posted"):
            # "topic_final.mp4" -> "topic"
            stem = filename.replace("_final.mp4", "")
            posted.add(stem)
    return posted


def audit_all(include_posted: bool = False) -> list[dict]:
    """Audit every Remotion manifest with a TTS_SCRIPT. Sort by word_count desc.

    Scans remotion/src/manifests/*.json. Also checks *_manim.py for backward compat.
    By default, skips videos marked as posted in video_metadata.json.
    """
    posted = _get_posted_stems() if not include_posted else set()
    manifests_dir = VIDGEN / "remotion" / "src" / "manifests"
    seen_stems = set()
    results = []

    # Primary: Remotion manifests
    if manifests_dir.exists():
        for f in sorted(manifests_dir.glob("*.json")):
            stem = f.stem
            if stem in posted:
                continue
            seen_stems.add(stem)
            # Look for a corresponding screenplay that has TTS_SCRIPT
            screenplay = VIDGEN / f"{stem}_manim.py"
            if screenplay.exists():
                r = audit_one(screenplay)
                if r["status"] != "SKIP":
                    results.append(r)

    # Backward compat: *_manim.py not covered by a manifest
    for f in sorted(VIDGEN.glob("*_manim.py")):
        stem = f.stem.replace("_manim", "")
        if stem in posted or stem in seen_stems:
            continue
        r = audit_one(f)
        if r["status"] != "SKIP":
            results.append(r)

    results.sort(key=lambda r: r["word_count"], reverse=True)
    return results


def suggest_cuts(tts_script: str) -> dict:
    """Analyze script for cuttable content.

    Returns flagged sentences (>12 words), detected filler phrases,
    and word budget info.
    """
    sentences = _split_sentences(tts_script)
    words = tts_script.split()
    word_count = len(words)

    flagged_sentences = []
    for s in sentences:
        s_words = len(s.split())
        if s_words > 12:
            flagged_sentences.append({
                "text": s,
                "word_count": s_words,
                "reason": "Over 12 words — consider tightening",
            })

    # Find filler phrases
    lower_script = tts_script.lower()
    found_fillers = []
    for phrase in FILLER_PHRASES:
        if phrase in lower_script:
            found_fillers.append(phrase)

    return {
        "total_words": word_count,
        "target": TARGET_WORDS,
        "overrun": max(0, word_count - TARGET_WORDS),
        "flagged_sentences": flagged_sentences,
        "filler_phrases": found_fillers,
        "sentence_count": len(sentences),
        "avg_words_per_sentence": round(word_count / max(len(sentences), 1), 1),
    }


def print_table(results: list[dict]):
    """Print fleet audit as a formatted table."""
    if not results:
        print("No screenplays with TTS_SCRIPT found.")
        return

    # Summary stats
    total = len(results)
    ok = sum(1 for r in results if r["status"] == "OK")
    warn = sum(1 for r in results if r["status"] == "WARN")
    fail = sum(1 for r in results if r["status"] == "FAIL")
    avg_words = sum(r["word_count"] for r in results) / total

    print(f"\n{'='*70}")
    print(f"  TTS AUDIT — {total} screenplays")
    print(f"  OK: {ok}  WARN: {warn}  FAIL: {fail}  Avg words: {avg_words:.0f}")
    print(f"  Target: {TARGET_WORDS} words (~{TARGET_WORDS / WPM * 60:.0f}s)  "
          f"Max: {FAIL_WORDS} words (~{FAIL_WORDS / WPM * 60:.0f}s)")
    print(f"{'='*70}\n")

    # Table header
    print(f"  {'Status':<6} {'Words':>5} {'Est':>5} {'Act':>5} {'Over':>5}  {'Screenplay'}")
    print(f"  {'------':<6} {'-----':>5} {'-----':>5} {'-----':>5} {'-----':>5}  {'-'*30}")

    for r in results:
        status = r["status"]
        if status == "FAIL":
            marker = "\033[91mFAIL\033[0m"
        elif status == "WARN":
            marker = "\033[93mWARN\033[0m"
        else:
            marker = "\033[92m OK \033[0m"

        act = f"{r['actual_duration']:.0f}s" if r["actual_duration"] else "  —"
        over = f"+{r['overrun_words']}" if r["overrun_words"] > 0 else "  —"

        print(f"  {marker}  {r['word_count']:>5} {r['est_duration']:>4.0f}s {act:>5} {over:>5}  {r['stem']}")

    print()


def print_detail(result: dict):
    """Print detailed per-sentence breakdown for one screenplay."""
    print(f"\n{'='*70}")
    print(f"  {result['stem']} — {result['word_count']} words "
          f"({result['est_duration']:.0f}s est)")
    if result["actual_duration"]:
        print(f"  Actual TTS duration: {result['actual_duration']:.1f}s")
    print(f"  Status: {result['status']}  "
          f"Target: {TARGET_WORDS} words  Overrun: +{result['overrun_words']}")
    print(f"{'='*70}\n")

    print("  Sentences:")
    for i, s in enumerate(result["sentences"], 1):
        flag = " <<<" if s["flag"] else ""
        print(f"  {i:2d}. [{s['word_count']:2d}w {s['est_seconds']:4.1f}s] {s['text']}{flag}")

    # Suggest cuts
    cuts = suggest_cuts(result["tts_script"])
    if cuts["filler_phrases"]:
        print(f"\n  Filler phrases found:")
        for f in cuts["filler_phrases"]:
            print(f"    - \"{f}\"")

    if cuts["flagged_sentences"]:
        print(f"\n  Long sentences (>12 words) to tighten: {len(cuts['flagged_sentences'])}")

    print()


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a not in ("--json", "--all")]
    json_mode = "--json" in sys.argv
    include_posted = "--all" in sys.argv

    if args:
        # Audit specific file
        path = VIDGEN / args[0]
        if not path.exists():
            path = VIDGEN / f"{args[0]}_manim.py"
        if not path.exists():
            print(f"Not found: {args[0]}", file=sys.stderr)
            sys.exit(1)

        result = audit_one(path)
        if json_mode:
            # Remove tts_script from JSON to keep it manageable
            out = {k: v for k, v in result.items() if k != "tts_script"}
            out["suggest_cuts"] = suggest_cuts(result["tts_script"])
            print(json.dumps(out, indent=2))
        else:
            print_detail(result)
    else:
        # Audit all
        results = audit_all(include_posted=include_posted)
        if json_mode:
            out = [{k: v for k, v in r.items() if k != "tts_script"} for r in results]
            print(json.dumps(out, indent=2))
        else:
            print_table(results)
