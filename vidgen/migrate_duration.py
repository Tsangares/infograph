#!/usr/bin/env python3
"""Migrate screenplays to DURATION adaptive timing pattern.

For each scene class:
1. Add DURATION = X.X class attribute (from timings JSON or VTT docstring)
2. Add t = 0 after self.add(gradient_bg()...)
3. Append ; t += {run_time} after every self.play(..., run_time=X) call
4. Append ; t += {wait} after every self.wait(X) call
5. Replace final self.wait(N) with adaptive padding:
     target = getattr(self.__class__, 'DURATION', X.X)
     self.wait(max(0.1, target - t - 0.3))
   (Scene 6 uses 0.8 instead of 0.3 for fade-to-black)

Usage:
    python3 migrate_duration.py --dry-run ambition_installed_manim.py
    python3 migrate_duration.py ambition_installed_manim.py
    python3 migrate_duration.py --all
"""

import ast
import json
import os
import re
import sys
from pathlib import Path

VIDGEN = Path(__file__).parent


def get_scene_durations(stem: str, content: str) -> list[float] | None:
    """Get scene durations from timings JSON, or parse VTT docstring."""
    timings_file = VIDGEN / f"tts_{stem}_timings.json"
    if timings_file.exists():
        data = json.loads(timings_file.read_text())
        return data.get("scene_durations")

    # Parse VTT docstring
    m = re.search(r'"""(.*?)"""', content, re.DOTALL)
    if not m:
        return None
    doc = m.group(1)
    durations = []
    # Try "= X.XXs" format first (most specific)
    for match in re.finditer(r'Scene\s+\d+.*?=\s*([\d.]+)s', doc):
        durations.append(float(match.group(1)))
    if not durations:
        # Try range format: (X.X–Y.Xs) or (X.X-Y.Xs)
        for match in re.finditer(r'Scene\s+\d+.*?\(.*?([\d.]+)\s*[–-]\s*([\d.]+)s?\s*(?:=\s*[\d.]+s)?\)', doc):
            start, end = float(match.group(1)), float(match.group(2))
            durations.append(round(end - start, 3))
    if not durations:
        # Try standalone duration at end of scene lines: "X.XXs" at end of line
        # Matches "Scene N ...", "N. THE ...", or numbered lines with timing
        for match in re.finditer(r'^\s*(?:(?:Scene|SCENE)\s+)?\d+\.?\s+.*?([\d.]+)s\s*$', doc, re.MULTILINE):
            durations.append(float(match.group(1)))
    return durations if durations else None


def find_scene_classes(content: str) -> list[tuple[str, int, int]]:
    """Find scene class names and their line ranges (0-indexed start, exclusive end)."""
    lines = content.split("\n")
    classes = []
    for i, line in enumerate(lines):
        m = re.match(r'^class (Scene\d+\w*)\(\w+\):', line)
        if m:
            classes.append((m.group(1), i))

    # Determine end of each class
    result = []
    for idx, (name, start) in enumerate(classes):
        if idx + 1 < len(classes):
            end = classes[idx + 1][1]
        else:
            # Find end: next top-level definition or SCENES = [...]
            end = len(lines)
            for j in range(start + 1, len(lines)):
                if re.match(r'^(?:class |def |SCENES\s*=|# ──)', lines[j]):
                    end = j
                    break
        result.append((name, start, end))
    return result


def is_last_scene(cls_name: str, all_classes: list) -> bool:
    """Check if this is the last scene class."""
    return cls_name == all_classes[-1][0]


def migrate_scene_block(lines: list[str], duration: float, is_final: bool) -> list[str]:
    """Add DURATION + t tracking + adaptive padding to a scene class block."""
    result = []
    in_construct = False
    construct_indent = ""
    found_add_gradient = False
    t_inserted = False
    last_wait_idx = None  # track last self.wait() line for replacement
    play_wait_lines = []  # indices of self.play / self.wait lines in result

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Add DURATION after class definition
        if re.match(r'^class Scene\d+\w*\(\w+\):', stripped):
            result.append(line)
            indent = re.match(r'^(\s*)', line).group(1)
            result.append(f"{indent}    DURATION = {duration}")
            continue

        # Detect construct method
        if re.match(r'\s*def construct\(self\):', stripped):
            in_construct = True
            construct_indent = re.match(r'^(\s*)', line).group(1) + "    "
            result.append(line)
            continue

        if not in_construct:
            result.append(line)
            continue

        # Detect end of construct (next method or class)
        if stripped and not stripped.startswith("#") and not stripped.startswith("'") and not stripped.startswith('"'):
            # Check dedent
            if line.strip() and not line.startswith(construct_indent) and not line.startswith(construct_indent.rstrip()):
                if re.match(r'\s*def ', stripped) or re.match(r'^class ', stripped):
                    in_construct = False
                    result.append(line)
                    continue

        # Insert t = 0 after self.add(gradient_bg...) line
        if not t_inserted and "self.add(" in stripped and "gradient_bg" in stripped:
            result.append(line)
            result.append(f"{construct_indent}t = 0")
            t_inserted = True
            found_add_gradient = True
            continue

        # If no gradient_bg found, insert t=0 after first non-comment line in construct
        if not t_inserted and in_construct and stripped and not stripped.startswith("#"):
            if not re.match(r'\s*def construct', stripped):
                result.append(line)
                result.append(f"{construct_indent}t = 0")
                t_inserted = True
                continue

        # Track self.play() with run_time
        rt_match = re.search(r'run_time\s*=\s*([\d.]+)', stripped)
        if "self.play(" in stripped and rt_match:
            rt = rt_match.group(1)
            # Check if line already has t +=
            if "t +=" not in stripped:
                # Strip trailing comment, insert t +=, re-add comment
                comment_match = re.search(r'(\s*#.*)$', line)
                if comment_match:
                    code_part = line[:comment_match.start()]
                    result.append(f"{code_part}; t += {rt}")
                else:
                    result.append(f"{line}; t += {rt}")
            else:
                result.append(line)
            play_wait_lines.append(len(result) - 1)
            continue

        # Track self.wait() with duration
        wait_match = re.match(r'(\s*)self\.wait\s*\(\s*([\d.]+)\s*\)(.*)', line)
        if wait_match:
            indent_w = wait_match.group(1)
            wait_dur = wait_match.group(2)
            if "t +=" not in line:
                result.append(f"{indent_w}self.wait({wait_dur}); t += {wait_dur}")
            else:
                result.append(line)
            last_wait_idx = len(result) - 1
            play_wait_lines.append(last_wait_idx)
            continue

        result.append(line)

    # Now replace the last self.wait() with adaptive padding
    if last_wait_idx is not None and t_inserted:
        old_line = result[last_wait_idx]
        indent_match = re.match(r'^(\s*)', old_line)
        indent = indent_match.group(1) if indent_match else construct_indent

        # For final scene, use 0.8 margin (fade-to-black); otherwise 0.3
        margin = "0.8" if is_final else "0.3"

        # Replace with adaptive padding
        result[last_wait_idx] = (
            f"{indent}target = getattr(self.__class__, 'DURATION', {duration})\n"
            f"{indent}self.wait(max(0.1, target - t - {margin}))"
        )

    return result


def migrate_file(filepath: Path, dry_run: bool = False) -> bool:
    """Migrate a single screenplay file. Returns True if changes were made."""
    content = filepath.read_text()
    stem = filepath.stem.replace("_manim", "")

    # Skip if already migrated
    if "target - t" in content or "target-t" in content:
        print(f"  SKIP {filepath.name} — already has adaptive padding")
        return False

    # Get durations
    durations = get_scene_durations(stem, content)
    if not durations:
        print(f"  SKIP {filepath.name} — no timing data available")
        return False

    # Find scene classes
    classes = find_scene_classes(content)
    if not classes:
        print(f"  SKIP {filepath.name} — no scene classes found")
        return False

    if len(durations) < len(classes):
        print(f"  WARN {filepath.name} — {len(durations)} durations for {len(classes)} scenes, padding with last")
        while len(durations) < len(classes):
            durations.append(durations[-1])

    lines = content.split("\n")
    new_lines = []
    class_idx = 0
    i = 0

    while i < len(lines):
        # Check if this line starts a scene class
        if class_idx < len(classes) and i == classes[class_idx][1]:
            name, start, end = classes[class_idx]
            dur = round(durations[class_idx], 1) if class_idx < len(durations) else 5.0
            is_final = (class_idx == len(classes) - 1)

            block = lines[start:end]
            migrated = migrate_scene_block(block, dur, is_final)
            new_lines.extend(migrated)
            i = end
            class_idx += 1
            continue

        new_lines.append(lines[i])
        i += 1

    # Ensure json import exists (needed for TKK_SCENE_TIMINGS in __main__)
    has_json_import = any("import json" in line for line in new_lines[:30])
    if not has_json_import:
        # Add json to the first import line
        for idx, line in enumerate(new_lines):
            if re.match(r'^import os', line):
                if "json" not in line:
                    new_lines[idx] = "import json, " + line[len("import "):]
                break

    new_content = "\n".join(new_lines)

    if dry_run:
        print(f"  DRY-RUN {filepath.name} — {len(classes)} scenes, durations: {[round(d,1) for d in durations[:len(classes)]]}")
        return True

    filepath.write_text(new_content)
    print(f"  OK {filepath.name} — {len(classes)} scenes migrated")
    return True


def verify_file(filepath: Path) -> bool:
    """Verify a migrated file passes syntax check."""
    try:
        ast.parse(filepath.read_text())
        return True
    except SyntaxError as e:
        print(f"  SYNTAX ERROR {filepath.name}: {e}")
        return False


if __name__ == "__main__":
    os.chdir(VIDGEN)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry_run = "--dry-run" in sys.argv
    do_all = "--all" in sys.argv
    verify_only = "--verify" in sys.argv

    if do_all:
        files = sorted(VIDGEN.glob("*_manim.py"))
    elif args:
        files = []
        for a in args:
            p = VIDGEN / a
            if not p.exists():
                p = VIDGEN / f"{a}_manim.py"
            if p.exists():
                files.append(p)
            else:
                print(f"Not found: {a}", file=sys.stderr)
    else:
        print("Usage: python3 migrate_duration.py [--dry-run] [--all] [--verify] <file.py>...")
        sys.exit(1)

    if verify_only:
        ok = fail = 0
        for f in files:
            if verify_file(f):
                ok += 1
            else:
                fail += 1
        print(f"\nVerified {ok + fail} files: {ok} OK, {fail} FAILED")
        sys.exit(1 if fail else 0)

    migrated = skipped = errors = 0
    for f in files:
        try:
            if migrate_file(f, dry_run=dry_run):
                migrated += 1
                if not dry_run and not verify_file(f):
                    errors += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ERROR {f.name}: {e}")
            errors += 1

    print(f"\nMigration complete: {migrated} migrated, {skipped} skipped, {errors} errors")
