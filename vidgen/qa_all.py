#!/usr/bin/env python3
"""
Unified QA Runner for TKK Video Pipeline

Single entry point that detects manifest format and runs all applicable checks.
Returns a structured report with overall PASS/WARN/FAIL.

Usage:
    python qa_all.py <topic>
    python qa_all.py --all
    python qa_all.py --json <topic>
    python qa_all.py --skip-previews <topic>
"""

import json
import sys
from pathlib import Path

VIDGEN_DIR = Path(__file__).parent
MANIFESTS_DIR = VIDGEN_DIR / "remotion" / "src" / "manifests"


def detect_format(topic: str) -> str:
    """Detect manifest format: 'word-triggered', 'legacy', or 'manim'."""
    manifest_path = MANIFESTS_DIR / f"{topic}.json"
    if manifest_path.exists():
        data = json.loads(manifest_path.read_text())
        if data.get("scenes") and "scene_anchor" in data["scenes"][0]:
            return "word-triggered"
        return "legacy"
    if (VIDGEN_DIR / f"{topic}_manim.py").exists():
        return "manim"
    return "unknown"


def _section(name: str, status: str, checks: list, fail_count: int = 0, warn_count: int = 0) -> dict:
    """Build a QA section result."""
    return {
        "name": name,
        "status": status,
        "checks": checks,
        "fail_count": fail_count,
        "warn_count": warn_count,
    }


def _run_manifest_validation(topic: str) -> dict:
    """Run validate_manifest.py checks."""
    try:
        from validate_manifest import validate_manifest
        result = validate_manifest(topic)
        return _section("manifest", result["status"], result["checks"],
                        result["fail_count"], result["warn_count"])
    except Exception as e:
        return _section("manifest", "WARN", [{"check": "manifest_validation", "status": "WARN", "detail": f"Error: {e}"}], 0, 1)


def _run_layout_qa(topic: str) -> dict:
    """Run qa_layout.py on preview PNGs."""
    preview_dir = VIDGEN_DIR / "previews"
    previews = sorted(preview_dir.glob(f"{topic}_scene_*.png")) if preview_dir.exists() else []
    if not previews:
        return _section("layout", "WARN", [{"check": "previews", "status": "WARN", "detail": "No preview PNGs found"}], 0, 1)

    try:
        from qa_layout import analyze_preview
        checks = []
        fails = 0
        warns = 0
        for png in previews:
            result = analyze_preview(str(png))
            for c in result["checks"]:
                entry = {"check": f"layout_{c['name']}", "status": c["status"],
                         "detail": f"{Path(result['file']).name}: {c['detail']}"}
                checks.append(entry)
                if c["status"] == "FAIL":
                    fails += 1
                elif c["status"] == "WARN":
                    warns += 1

        status = "FAIL" if fails else "WARN" if warns else "PASS"
        return _section("layout", status, checks, fails, warns)
    except Exception as e:
        return _section("layout", "WARN", [{"check": "layout", "status": "WARN", "detail": f"Error: {e}"}], 0, 1)


def _run_visibility_qa(topic: str) -> dict:
    """Run qa_visibility.py on preview PNGs to detect dark-on-dark elements."""
    preview_dir = VIDGEN_DIR / "previews"
    previews = sorted(preview_dir.glob(f"{topic}_scene_*.png")) if preview_dir.exists() else []
    if not previews:
        return _section("visibility", "WARN", [{"check": "previews", "status": "WARN", "detail": "No preview PNGs found"}], 0, 1)

    try:
        from qa_visibility import check_visibility
        checks = []
        fails = 0
        warns = 0
        for png in previews:
            result = check_visibility(str(png))
            entry = {"check": "visibility", "status": result["status"], "detail": result["detail"]}
            checks.append(entry)
            if result["status"] == "FAIL":
                fails += 1
            elif result["status"] == "WARN":
                warns += 1

        status = "FAIL" if fails else "WARN" if warns else "PASS"
        return _section("visibility", status, checks, fails, warns)
    except Exception as e:
        return _section("visibility", "WARN", [{"check": "visibility", "status": "WARN", "detail": f"Error: {e}"}], 0, 1)


def _run_remotion_sync(topic: str) -> dict:
    """Run qa_remotion_sync.py for legacy Remotion manifests."""
    try:
        from qa_remotion_sync import run_sync_qa
        result = run_sync_qa(topic)
        return _section("remotion_sync", result["status"], result["checks"],
                        result["fail_count"], result["warn_count"])
    except Exception as e:
        return _section("remotion_sync", "WARN", [{"check": "sync", "status": "WARN", "detail": f"Error: {e}"}], 0, 1)


def _run_word_triggered_audits(topic: str) -> dict:
    """Run audit_timeline.py + collision_audit.py for word-triggered manifests."""
    resolved_path = VIDGEN_DIR / f"{topic}_resolved.json"
    if not resolved_path.exists():
        return _section("word_triggered_audit", "WARN",
                        [{"check": "resolved_json", "status": "WARN", "detail": f"{topic}_resolved.json not found — run resolver first"}], 0, 1)

    checks = []
    fails = 0
    warns = 0

    # Timeline audit (suppress stdout — audit() prints verbose output)
    try:
        import io, contextlib
        from audit_timeline import audit
        f_buf = io.StringIO()
        with contextlib.redirect_stdout(f_buf):
            issues = audit(resolved_path, interval_s=2.0)
        if issues:
            for issue in issues:
                checks.append({"check": "timeline", "status": "WARN", "detail": issue})
                warns += 1
        else:
            checks.append({"check": "timeline", "status": "PASS", "detail": "No timeline issues"})
    except Exception as e:
        checks.append({"check": "timeline", "status": "WARN", "detail": f"Error: {e}"})
        warns += 1

    # Collision audit (suppress stdout)
    try:
        import io, contextlib
        from collision_audit import audit_collisions
        f_buf = io.StringIO()
        with contextlib.redirect_stdout(f_buf):
            collisions = audit_collisions(resolved_path, interval_s=0.5)
        critical = [c for c in collisions if c["severity"] == "CRITICAL"]
        warn_items = [c for c in collisions if c["severity"] == "WARN"]

        if critical:
            for c in critical:
                checks.append({"check": "collision", "status": "FAIL",
                              "detail": f"CRITICAL: t={c['time']:.1f}s {c['scene']} \"{c['a']}\" <-> \"{c['b']}\""})
                fails += 1
        if warn_items:
            for c in warn_items:
                checks.append({"check": "collision", "status": "WARN",
                              "detail": f"t={c['time']:.1f}s {c['scene']} \"{c['a']}\" <-> \"{c['b']}\""})
                warns += 1
        if not critical and not warn_items:
            checks.append({"check": "collision", "status": "PASS", "detail": "No collisions detected"})
    except Exception as e:
        checks.append({"check": "collision", "status": "WARN", "detail": f"Error: {e}"})
        warns += 1

    status = "FAIL" if fails else "WARN" if warns else "PASS"
    return _section("word_triggered_audit", status, checks, fails, warns)


def _run_raycast_qa(topic: str) -> dict:
    """Run pixel-level raycasting QA on preview PNGs."""
    preview_dir = VIDGEN_DIR / "previews"
    previews = sorted(preview_dir.glob(f"{topic}_scene_*.png")) if preview_dir.exists() else []
    if not previews:
        return _section("raycast", "WARN", [{"check": "previews", "status": "WARN", "detail": "No preview PNGs for raycasting"}], 0, 1)

    try:
        from qa_raycast import analyze_scene
        checks = []
        fails = 0
        warns = 0
        for png in previews:
            scene_num = int(png.stem.split('_scene_')[1])
            result = analyze_scene(str(png), scene_num)
            for c in result['checks']:
                checks.append(c)
                if c['status'] == 'FAIL':
                    fails += 1
                elif c['status'] == 'WARN':
                    warns += 1
        status = "FAIL" if fails else "WARN" if warns else "PASS"
        return _section("raycast", status, checks, fails, warns)
    except Exception as e:
        return _section("raycast", "WARN", [{"check": "raycast", "status": "WARN", "detail": f"Raycast QA error: {e}"}], 0, 1)


def run_all_qa(topic: str, skip_previews: bool = False) -> dict:
    """Run all applicable QA checks for a topic. Returns unified report."""
    fmt = detect_format(topic)
    sections = []

    if fmt == "unknown":
        return {
            "topic": topic,
            "format": "unknown",
            "status": "FAIL",
            "sections": [_section("detection", "FAIL",
                                  [{"check": "format", "status": "FAIL", "detail": f"No manifest or screenplay found for '{topic}'"}], 1, 0)],
            "total_fails": 1,
            "total_warns": 0,
        }

    # Manifest validation (Remotion only)
    if fmt in ("legacy", "word-triggered"):
        sections.append(_run_manifest_validation(topic))

    # Preview-based checks
    if not skip_previews:
        sections.append(_run_layout_qa(topic))
        sections.append(_run_visibility_qa(topic))
        sections.append(_run_raycast_qa(topic))

    # Format-specific sync checks
    if fmt == "legacy":
        sections.append(_run_remotion_sync(topic))
    elif fmt == "word-triggered":
        sections.append(_run_word_triggered_audits(topic))

    # Aggregate
    total_fails = sum(s["fail_count"] for s in sections)
    total_warns = sum(s["warn_count"] for s in sections)
    overall = "FAIL" if total_fails else "WARN" if total_warns else "PASS"

    return {
        "topic": topic,
        "format": fmt,
        "status": overall,
        "sections": sections,
        "total_fails": total_fails,
        "total_warns": total_warns,
    }


def format_report(result: dict) -> str:
    """Format a QA result as human-readable text."""
    lines = [f"\n{'='*60}",
             f"QA REPORT: {result['topic']} ({result['format']})",
             f"{'='*60}"]

    for section in result["sections"]:
        lines.append(f"\n  [{section['status']}] {section['name']}")
        for c in section["checks"]:
            lines.append(f"    [{c['status']}] {c.get('check', '?')}: {c['detail']}")

    lines.append(f"\n{'='*60}")
    lines.append(f"Overall: [{result['status']}] {result['total_fails']} fails, {result['total_warns']} warns")
    return "\n".join(lines)


if __name__ == "__main__":
    use_json = "--json" in sys.argv
    skip_previews = "--skip-previews" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if "--all" in sys.argv:
        # All Remotion manifests + all Manim screenplays
        topics = set()
        for m in MANIFESTS_DIR.glob("*.json"):
            topics.add(m.stem)
        for s in VIDGEN_DIR.glob("*_manim.py"):
            topics.add(s.stem.replace("_manim", ""))
        topics = sorted(topics)
    elif args:
        topics = args
    else:
        print("Usage: python qa_all.py <topic> [--all] [--json] [--skip-previews]")
        sys.exit(1)

    all_results = []
    for topic in topics:
        result = run_all_qa(topic, skip_previews=skip_previews)
        all_results.append(result)
        if use_json:
            print(json.dumps(result, indent=2))
        else:
            print(format_report(result))

    if not use_json and len(topics) > 1:
        total_f = sum(r["total_fails"] for r in all_results)
        total_w = sum(r["total_warns"] for r in all_results)
        overall = "FAIL" if total_f else "WARN" if total_w else "PASS"
        print(f"\n{'='*60}")
        print(f"Fleet QA: [{overall}] {len(topics)} topics, {total_f} fails, {total_w} warns")
