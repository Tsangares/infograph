#!/usr/bin/env python3
"""Animation Enhancement Engine — Template-based fillers for dead time.

Provides a menu of proven-safe animation enhancements that can be inserted
into scenes with dead time (animation ends before scene's audio share).

Key design: template-based, not freeform LLM code generation. Each enhancement
is a parameterized template that generates valid manim code. The LLM picks
which enhancements to use; the templates guarantee they render.

Enhancement Menu:
    slow_zoom     (1-4s)  — Gentle scale on existing visual
    pulse_glow    (1-3s)  — Glowing circle behind key element
    pan_drift     (2-5s)  — Slow camera-like shift of scene content
    secondary_label (1-3s) — Fade in an annotation/label
    count_up      (2-4s)  — Animated number counter
    bar_grow      (2-3s)  — Bar chart animation
    icon_cascade  (2-5s)  — Staggered icon appearances
    emphasis_line (1-2s)  — Animated underline under key text
    color_shift   (1-3s)  — Gradual color change on element
    particle_drift (2-5s) — Ambient dots floating
"""

import json
import re
import subprocess
import sys
import textwrap
from pathlib import Path

VIDGEN = Path(__file__).parent

# Enhancement templates — each generates valid manim code
ENHANCEMENT_MENU = {
    "slow_zoom": {
        "time_range": (1.0, 4.0),
        "description": "Gentle scale on existing visual element",
        "params": {"target_var": "str — variable name of mobject to zoom", "scale_factor": "float — 1.05 to 1.2"},
    },
    "pulse_glow": {
        "time_range": (1.0, 3.0),
        "description": "Glowing circle fades in behind key element then fades out",
        "params": {"target_var": "str — variable name to glow behind", "color": "str — hex color"},
    },
    "pan_drift": {
        "time_range": (2.0, 5.0),
        "description": "Slow camera-like horizontal/vertical shift of a group",
        "params": {"target_var": "str — variable name to drift", "direction": "str — LEFT/RIGHT/UP/DOWN", "distance": "float — 0.3 to 1.0"},
    },
    "secondary_label": {
        "time_range": (1.0, 3.0),
        "description": "Fade in a small annotation label at a zone",
        "params": {"text": "str — label content (3-6 words max)", "zone": "str — UPPER/MID/LOWER/FOOTER", "color": "str — hex color"},
    },
    "count_up": {
        "time_range": (2.0, 4.0),
        "description": "Animated number counter from start to end value",
        "params": {"start": "int", "end": "int", "suffix": "str — optional suffix", "zone": "str — zone name"},
    },
    "bar_grow": {
        "time_range": (2.0, 3.0),
        "description": "Simple bar chart grows from zero",
        "params": {"values": "list[int]", "labels": "list[str]", "colors": "list[str] — hex colors"},
    },
    "icon_cascade": {
        "time_range": (2.0, 5.0),
        "description": "Staggered appearance of small icons/shapes",
        "params": {"count": "int — 3 to 8", "shape": "str — circle/square/dot", "color": "str — hex color", "zone": "str — zone name"},
    },
    "emphasis_line": {
        "time_range": (1.0, 2.0),
        "description": "Animated underline under an existing text element",
        "params": {"target_var": "str — variable name of text to underline", "color": "str — hex color"},
    },
    "color_shift": {
        "time_range": (1.0, 3.0),
        "description": "Gradual color change on an existing element",
        "params": {"target_var": "str — variable name", "to_color": "str — hex color"},
    },
    "particle_drift": {
        "time_range": (2.0, 5.0),
        "description": "Ambient dots floating across the scene",
        "params": {"count": "int — 5 to 20", "color": "str — hex color", "zone": "str — zone name"},
    },
}

# Zone Y positions (matching anim_primitives.py)
_ZONE_MAP = {
    "TITLE": 6.2, "UPPER": 3.5, "MID": 0.0, "LOWER": -3.5, "FOOTER": -6.0,
}


def _ffprobe_duration(filepath: Path) -> float | None:
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(filepath)],
            capture_output=True, text=True, timeout=10,
        )
        return float(r.stdout.strip())
    except Exception:
        return None


def _parse_scene_code(content: str) -> list[dict]:
    """Parse scene classes to extract timing info."""
    classes = re.findall(r'class\s+(Scene\d+\w*)\(Scene\):', content)
    sections = re.split(r'class\s+Scene\d+\w*\(Scene\):', content)[1:]
    results = []
    for cls, section in zip(classes, sections):
        dur_match = re.search(r'DURATION\s*=\s*([\d.]+)', section)
        coded_duration = float(dur_match.group(1)) if dur_match else None

        run_times = [float(r) for r in re.findall(r'run_time\s*=\s*([\d.]+)', section)]
        waits = [float(w) for w in re.findall(r'self\.wait\s*\(\s*([\d.]+)', section)]
        anim_time = sum(run_times)
        wait_time = sum(waits)

        # Detect which zones are used (by searching for zone constants or y positions)
        used_zones = set()
        if re.search(r'ZONE_TITLE|UP\s*\*\s*[56]|y.*[56]', section):
            used_zones.add("TITLE")
        if re.search(r'ZONE_UPPER|UP\s*\*\s*[34]|y.*[34]', section):
            used_zones.add("UPPER")
        if re.search(r'ZONE_MID|ORIGIN|move_to\(.*0', section):
            used_zones.add("MID")
        if re.search(r'ZONE_LOWER|DOWN\s*\*\s*[34]|y.*-[34]', section):
            used_zones.add("LOWER")
        if re.search(r'ZONE_FOOTER|DOWN\s*\*\s*[56]|y.*-[56]', section):
            used_zones.add("FOOTER")

        # Find variable names of mobjects for enhancement targeting
        var_names = re.findall(r'(\w+)\s*=\s*(?:safe_text|headline|Text|VGroup|load_svg|Rectangle|Circle)', section)

        results.append({
            "class": cls,
            "coded_duration": coded_duration,
            "anim_time": round(anim_time, 2),
            "wait_time": round(wait_time, 2),
            "total_coded": round(anim_time + wait_time, 2),
            "used_zones": sorted(used_zones),
            "var_names": var_names,
            "code": section,
        })
    return results


def _parse_docstring_scenes(content: str) -> list[dict]:
    """Parse VTT cues from docstring to get target durations."""
    m = re.search(r'^"""(.*?)"""', content, re.DOTALL)
    if not m:
        return []
    doc = m.group(1)
    scenes = []
    pattern = r'Scene\s+(\d+)\s+(\w[^(]*)\(([^)]+)\):'
    for match in re.finditer(pattern, doc, re.DOTALL):
        num, label, timing_str = match.groups()
        dur_match = re.search(r'=\s*([\d.]+)s', timing_str)
        if dur_match:
            duration = float(dur_match.group(1))
        else:
            range_match = re.search(r'([\d.]+)\s*[–-]\s*([\d.]+)', timing_str)
            duration = float(range_match.group(2)) - float(range_match.group(1)) if range_match else 0
        scenes.append({"num": int(num), "label": label.strip(), "duration": duration})
    return scenes


def _get_scene_durations(stem: str, content: str) -> list[float] | None:
    """Get scene durations from timings sidecar or docstring."""
    timings_file = VIDGEN / f"tts_{stem}_timings.json"
    if timings_file.exists():
        data = json.loads(timings_file.read_text())
        return data.get("scene_durations")
    scenes = _parse_docstring_scenes(content)
    if scenes:
        return [s["duration"] for s in scenes]
    return None


def analyze_dead_time(screenplay_path: Path, tts_path: Path = None) -> list[dict]:
    """Per-scene dead time analysis with enhancement suggestions.

    Returns list of scene reports with dead_seconds and suggested enhancements.
    """
    content = screenplay_path.read_text()
    stem = screenplay_path.stem.replace("_manim", "")

    if tts_path is None:
        tts_path = VIDGEN / f"tts_{stem}.mp3"

    scene_durs = _get_scene_durations(stem, content)
    code_scenes = _parse_scene_code(content)
    doc_scenes = _parse_docstring_scenes(content)

    if not scene_durs or not code_scenes:
        return []

    results = []
    for i, code in enumerate(code_scenes):
        if i >= len(scene_durs):
            break

        target = scene_durs[i]
        total_coded = code["total_coded"]
        dead = max(0, target - total_coded)

        scene_label = doc_scenes[i]["label"] if i < len(doc_scenes) else code["class"]

        # Determine which zones are unused (opportunities for fill)
        all_zones = {"TITLE", "UPPER", "MID", "LOWER", "FOOTER"}
        unused_zones = sorted(all_zones - set(code["used_zones"]))

        # Suggest enhancements based on dead time and available space
        suggestions = []
        if dead >= 1.0:
            remaining = dead

            # If there are existing mobjects, suggest zoom/glow/color on them
            if code["var_names"] and remaining >= 1.0:
                suggestions.append({
                    "type": "slow_zoom",
                    "fill_time": min(remaining, 3.0),
                    "params": {"target_var": code["var_names"][0], "scale_factor": 1.1},
                    "reason": f"Gentle zoom on '{code['var_names'][0]}' fills {min(remaining, 3.0):.1f}s",
                })
                remaining -= min(remaining, 3.0)

            # If unused zones exist, suggest adding content there
            if remaining >= 1.5 and unused_zones:
                zone = unused_zones[0]
                suggestions.append({
                    "type": "secondary_label",
                    "fill_time": min(remaining, 2.0),
                    "params": {"text": "...", "zone": zone, "color": "#8A8A9A"},
                    "reason": f"Add label in unused {zone} zone",
                })
                remaining -= min(remaining, 2.0)

            # For longer dead time, suggest particle effects
            if remaining >= 2.0:
                suggestions.append({
                    "type": "particle_drift",
                    "fill_time": min(remaining, 4.0),
                    "params": {"count": 10, "color": "#55556A",
                               "zone": unused_zones[-1] if unused_zones else "LOWER"},
                    "reason": f"Ambient particles fill {min(remaining, 4.0):.1f}s",
                })
                remaining -= min(remaining, 4.0)

            # Emphasis line if there are text vars
            if remaining >= 1.0 and len(code["var_names"]) > 1:
                suggestions.append({
                    "type": "emphasis_line",
                    "fill_time": min(remaining, 1.5),
                    "params": {"target_var": code["var_names"][1], "color": "#FFD700"},
                    "reason": f"Underline '{code['var_names'][1]}'",
                })

        results.append({
            "scene_idx": i,
            "scene_name": scene_label,
            "class": code["class"],
            "dead_seconds": round(dead, 2),
            "coded_duration": round(total_coded, 2),
            "target_duration": round(target, 2),
            "used_zones": code["used_zones"],
            "unused_zones": unused_zones,
            "var_names": code["var_names"],
            "suggested_enhancements": suggestions,
        })

    return results


def generate_enhancement(enhancement_type: str, params: dict, run_time: float = None) -> str:
    """Generate manim code snippet for one enhancement. Guaranteed to render.

    Returns a string of Python code that can be inserted into a scene's construct().
    """
    if enhancement_type not in ENHANCEMENT_MENU:
        return f"# ERROR: Unknown enhancement type '{enhancement_type}'"

    menu = ENHANCEMENT_MENU[enhancement_type]
    if run_time is None:
        run_time = menu["time_range"][0]
    # Clamp to valid range
    run_time = max(menu["time_range"][0], min(run_time, menu["time_range"][1]))

    if enhancement_type == "slow_zoom":
        target = params.get("target_var", "group")
        scale = params.get("scale_factor", 1.1)
        return (f"        # Enhancement: slow zoom on {target}\n"
                f"        self.play({target}.animate.scale({scale}), run_time={run_time})")

    elif enhancement_type == "pulse_glow":
        target = params.get("target_var", "group")
        color = params.get("color", '"#FFD700"')
        if not color.startswith('"'):
            color = f'"{color}"'
        return (f"        # Enhancement: pulse glow behind {target}\n"
                f"        _glow = Circle(radius={target}.width * 0.6, "
                f"color={color}, fill_opacity=0.15, stroke_width=0)\n"
                f"        _glow.move_to({target}.get_center())\n"
                f"        self.play(FadeIn(_glow), run_time={run_time * 0.4:.1f})\n"
                f"        self.play(FadeOut(_glow), run_time={run_time * 0.6:.1f})")

    elif enhancement_type == "pan_drift":
        target = params.get("target_var", "group")
        direction = params.get("direction", "RIGHT")
        distance = params.get("distance", 0.5)
        return (f"        # Enhancement: pan drift\n"
                f"        self.play({target}.animate.shift({direction} * {distance}), "
                f"run_time={run_time})")

    elif enhancement_type == "secondary_label":
        text = params.get("text", "...")
        zone = params.get("zone", "FOOTER")
        color = params.get("color", '"#8A8A9A"')
        if not color.startswith('"'):
            color = f'"{color}"'
        y = _ZONE_MAP.get(zone, -6.0)
        return (f"        # Enhancement: secondary label at {zone}\n"
                f"        _label = safe_text(\"{text}\", font=\"Inter\", "
                f"font_size=24, color={color})\n"
                f"        _label.move_to(UP * {y})\n"
                f"        self.play(FadeIn(_label, shift=UP * 0.2), run_time={run_time})")

    elif enhancement_type == "count_up":
        start = params.get("start", 0)
        end = params.get("end", 100)
        suffix = params.get("suffix", "")
        zone = params.get("zone", "MID")
        y = _ZONE_MAP.get(zone, 0)
        return (f"        # Enhancement: count up {start} to {end}\n"
                f"        _counter = Integer({start}, color=\"#FFD700\", font_size=80)\n"
                f"        _counter.move_to(UP * {y})\n"
                f"        self.add(_counter)\n"
                f"        self.play(ChangeDecimalToValue(_counter, {end}), "
                f"run_time={run_time})")

    elif enhancement_type == "bar_grow":
        values = params.get("values", [3, 7, 5])
        labels = params.get("labels", [])
        colors = params.get("colors", ['"#FFD700"'] * len(values))
        # Generate inline bar chart code
        lines = [
            "        # Enhancement: bar chart grow",
            f"        _bar_vals = {values}",
            "        _bars = VGroup()",
            "        _bar_max = max(_bar_vals)",
            "        for _bi, _bv in enumerate(_bar_vals):",
            "            _bh = (_bv / _bar_max) * 4.0",
            '            _bar = Rectangle(width=0.8, height=_bh, fill_color="#FFD700", '
            "fill_opacity=0.8, stroke_width=0)",
            "            _bar.move_to(RIGHT * (_bi * 1.1 - len(_bar_vals) * 0.55) + DOWN * 4)",
            "            _bar.align_to(DOWN * 6, DOWN)",
            "            _bars.add(_bar)",
            f"        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in _bars], "
            f"lag_ratio=0.15), run_time={run_time})",
        ]
        return "\n".join(lines)

    elif enhancement_type == "icon_cascade":
        count = params.get("count", 5)
        shape = params.get("shape", "dot")
        color = params.get("color", '"#55556A"')
        if not color.startswith('"'):
            color = f'"{color}"'
        zone = params.get("zone", "LOWER")
        y = _ZONE_MAP.get(zone, -3.5)
        shape_code = {
            "dot": f"Dot(radius=0.08, color={color})",
            "circle": f"Circle(radius=0.15, color={color}, stroke_width=1)",
            "square": f"Square(side_length=0.2, color={color}, stroke_width=1)",
        }.get(shape, f"Dot(radius=0.08, color={color})")
        return (f"        # Enhancement: icon cascade at {zone}\n"
                f"        _icons = VGroup(*[\n"
                f"            {shape_code}.move_to(\n"
                f"                RIGHT * (i * 1.2 - {count} * 0.6) + UP * {y}\n"
                f"            ) for i in range({count})\n"
                f"        ])\n"
                f"        self.play(LaggedStart(*[FadeIn(ic, scale=0.5) "
                f"for ic in _icons], lag_ratio=0.1), run_time={run_time})")

    elif enhancement_type == "emphasis_line":
        target = params.get("target_var", "text")
        color = params.get("color", '"#FFD700"')
        if not color.startswith('"'):
            color = f'"{color}"'
        return (f"        # Enhancement: emphasis underline on {target}\n"
                f"        _underline = Line(\n"
                f"            {target}.get_left() + DOWN * 0.15,\n"
                f"            {target}.get_right() + DOWN * 0.15,\n"
                f"            color={color}, stroke_width=2\n"
                f"        )\n"
                f"        self.play(Create(_underline), run_time={run_time})")

    elif enhancement_type == "color_shift":
        target = params.get("target_var", "group")
        to_color = params.get("to_color", '"#FF4444"')
        if not to_color.startswith('"'):
            to_color = f'"{to_color}"'
        return (f"        # Enhancement: color shift on {target}\n"
                f"        self.play({target}.animate.set_color({to_color}), "
                f"run_time={run_time})")

    elif enhancement_type == "particle_drift":
        count = params.get("count", 10)
        color = params.get("color", '"#55556A"')
        if not color.startswith('"'):
            color = f'"{color}"'
        zone = params.get("zone", "LOWER")
        y = _ZONE_MAP.get(zone, -3.5)
        return (f"        # Enhancement: ambient particle drift\n"
                f"        import random as _rnd\n"
                f"        _particles = VGroup(*[\n"
                f"            Dot(radius=_rnd.uniform(0.02, 0.06), color={color},\n"
                f"                fill_opacity=_rnd.uniform(0.2, 0.5)).move_to(\n"
                f"                RIGHT * _rnd.uniform(-4, 4) + UP * ({y} + _rnd.uniform(-1, 1))\n"
                f"            ) for _ in range({count})\n"
                f"        ])\n"
                f"        self.play(\n"
                f"            LaggedStart(*[FadeIn(p, scale=0.3) for p in _particles], "
                f"lag_ratio=0.05),\n"
                f"            run_time={run_time * 0.3:.1f}\n"
                f"        )\n"
                f"        self.play(\n"
                f"            *[p.animate.shift(UP * 0.5 + RIGHT * _rnd.uniform(-0.3, 0.3)) "
                f"for p in _particles],\n"
                f"            run_time={run_time * 0.7:.1f}\n"
                f"        )")

    return f"# ERROR: Unhandled enhancement type '{enhancement_type}'"


def build_enhanced_scene(original_code: str, enhancements: list[dict]) -> str:
    """Insert enhancement code into a scene's construct() method.

    Appends after the last self.play() call, before the FadeOut cleanup.
    Each enhancement dict: {"type": str, "params": dict, "run_time": float}
    """
    # Find the last self.play(FadeOut... line (scene cleanup)
    lines = original_code.split("\n")
    insert_idx = None

    # Look for the FadeOut cleanup pattern from the end
    for i in range(len(lines) - 1, -1, -1):
        if "FadeOut" in lines[i] and "self.play" in lines[i]:
            insert_idx = i
            break

    if insert_idx is None:
        # No FadeOut cleanup found — append before last line
        insert_idx = len(lines) - 1

    # Generate enhancement code
    enhancement_code = []
    for enh in enhancements:
        code = generate_enhancement(
            enh["type"],
            enh.get("params", {}),
            enh.get("run_time"),
        )
        enhancement_code.append("")
        enhancement_code.append(code)

    # Insert
    result_lines = lines[:insert_idx] + enhancement_code + [""] + lines[insert_idx:]
    return "\n".join(result_lines)


def list_enhancements() -> dict:
    """Return the full enhancement menu for display."""
    return ENHANCEMENT_MENU


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] == "--help":
        print(__doc__)
        print("\nAvailable enhancements:")
        for name, info in ENHANCEMENT_MENU.items():
            print(f"  {name:<18} ({info['time_range'][0]}-{info['time_range'][1]}s) "
                  f"— {info['description']}")
        sys.exit(0)

    if args[0] == "--menu":
        print(json.dumps(ENHANCEMENT_MENU, indent=2))
        sys.exit(0)

    # Analyze a screenplay
    path = VIDGEN / args[0]
    if not path.exists():
        path = VIDGEN / f"{args[0]}_manim.py"
    if not path.exists():
        print(f"Not found: {args[0]}", file=sys.stderr)
        sys.exit(1)

    results = analyze_dead_time(path)
    json_mode = "--json" in args

    if json_mode:
        print(json.dumps(results, indent=2, default=str))
    else:
        print(f"\n{'='*60}")
        print(f"  DEAD TIME ANALYSIS — {path.stem}")
        print(f"{'='*60}\n")

        for r in results:
            if r["dead_seconds"] < 1.0:
                status = "\033[92mOK\033[0m"
            elif r["dead_seconds"] < 3.0:
                status = "\033[93mMINOR\033[0m"
            else:
                status = "\033[91mDEAD\033[0m"

            print(f"  [{status}] {r['class']} — {r['dead_seconds']:.1f}s dead "
                  f"(coded={r['coded_duration']:.1f}s target={r['target_duration']:.1f}s)")
            print(f"       Zones used: {', '.join(r['used_zones']) or 'none detected'}")

            if r["suggested_enhancements"]:
                print(f"       Suggestions:")
                for s in r["suggested_enhancements"]:
                    print(f"         - {s['type']} ({s['fill_time']:.1f}s): {s['reason']}")
            print()
