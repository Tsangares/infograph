#!/usr/bin/env python3
"""
SVG Asset Tools for TKK Video Pipeline

Manages the SVG icon ecosystem:
- Indexes all available SVGs (Font Awesome, custom, svgLibrary inline)
- Searches by keyword, category, or tag
- Imports Font Awesome icons into svgLibrary.tsx
- Generates new custom SVG assets from descriptions

Sources:
  /opt/tkk/assets/icons/solid/     — Font Awesome 6.7 (1,402 solid icons)
  /opt/tkk/assets/icons/regular/   — Font Awesome 6.7 (163 regular icons)
  /opt/tkk/vidgen/svg_assets/      — Custom + downloaded SVGs (26 files)
  svgLibrary.tsx inline            — 70+ hand-coded icons (already in Remotion)

Usage:
    python svg_tools.py search <query>          # search all sources
    python svg_tools.py list-library            # list icons currently in svgLibrary.tsx
    python svg_tools.py list-fa [query]         # list Font Awesome icons
    python svg_tools.py import-fa <name> [alias]  # import FA icon into svgLibrary.tsx
    python svg_tools.py generate <description>  # generate custom SVG from text description
    python svg_tools.py build-index             # rebuild the search index
"""

import json
import os
import re
import sys
from pathlib import Path

VIDGEN_DIR = Path(__file__).parent
FA_DIR = Path("/opt/tkk/assets/icons")
SVG_ASSETS_DIR = VIDGEN_DIR / "svg_assets"
SVG_LIBRARY_PATH = VIDGEN_DIR / "remotion" / "src" / "lib" / "svgLibrary.tsx"
INDEX_PATH = VIDGEN_DIR / "svg_index.json"

# Category mappings for Font Awesome icons (partial, covers common TKK topics)
FA_CATEGORIES = {
    "people": ["person", "user", "people", "child", "baby", "skull", "head", "face", "hand"],
    "medical": ["syringe", "pills", "capsules", "hospital", "stethoscope", "heart-pulse", "virus",
                "bacteria", "dna", "microscope", "flask", "vial", "lungs", "brain", "tooth"],
    "science": ["atom", "flask", "microscope", "dna", "vial", "radiation", "biohazard", "magnet",
                "temperature", "thermometer", "satellite", "rocket", "meteor"],
    "nature": ["tree", "leaf", "seedling", "mountain", "water", "fish", "fire", "sun", "moon",
               "cloud", "wind", "snowflake", "volcano", "hurricane", "wave", "globe"],
    "warfare": ["bomb", "explosion", "shield", "sword", "gun", "crosshairs", "jet-fighter",
                "helicopter", "tank", "skull-crossbones", "land-mine"],
    "history": ["landmark", "monument", "church", "mosque", "synagogue", "torii-gate", "kaaba",
                "crown", "scroll", "book", "quill", "feather", "chess"],
    "building": ["building", "house", "city", "industry", "factory", "warehouse", "store",
                 "hospital", "school", "university", "church", "hotel"],
    "transport": ["car", "truck", "bus", "train", "plane", "ship", "boat", "bicycle", "motorcycle",
                  "rocket", "helicopter", "jet"],
    "money": ["dollar", "coins", "money", "wallet", "piggy-bank", "chart", "arrow-trend"],
    "law": ["gavel", "scale", "handcuffs", "jail", "section", "paragraph"],
    "food": ["utensils", "burger", "pizza", "apple", "lemon", "carrot", "bread", "wine", "beer",
             "mug", "cup", "bowl"],
    "tech": ["computer", "laptop", "phone", "tablet", "microchip", "robot", "database", "server",
             "wifi", "satellite", "signal", "code", "terminal"],
    "media": ["camera", "video", "film", "music", "microphone", "radio", "tv", "newspaper",
              "podcast", "photo"],
}


def _parse_library_names() -> set[str]:
    """Extract icon names currently in svgLibrary.tsx."""
    if not SVG_LIBRARY_PATH.exists():
        return set()
    content = SVG_LIBRARY_PATH.read_text()
    return set(re.findall(r'^\s+(\w+):\s*(?:icon|strokeIcon)\(', content, re.MULTILINE))


def _list_fa_icons() -> dict[str, dict]:
    """List all Font Awesome icons with metadata."""
    icons = {}
    for style_dir in ["solid", "regular", "brands"]:
        d = FA_DIR / style_dir
        if not d.exists():
            continue
        for f in sorted(d.glob("*.svg")):
            name = f.stem
            cats = []
            for cat, keywords in FA_CATEGORIES.items():
                if any(kw in name for kw in keywords):
                    cats.append(cat)
            icons[f"fa-{style_dir}/{name}"] = {
                "name": name,
                "style": f"fa-{style_dir}",
                "path": str(f),
                "categories": cats,
            }
    return icons


def _list_lucide_icons() -> dict[str, dict]:
    """List all Lucide icons."""
    icons = {}
    d = FA_DIR / "lucide"
    if not d.exists():
        return icons
    for f in sorted(d.glob("*.svg")):
        name = f.stem
        cats = []
        for cat, keywords in FA_CATEGORIES.items():
            if any(kw in name for kw in keywords):
                cats.append(cat)
        icons[f"lucide/{name}"] = {
            "name": name,
            "style": "lucide",
            "path": str(f),
            "categories": cats,
        }
    return icons


def _list_feather_icons() -> dict[str, dict]:
    """List all Feather icons."""
    icons = {}
    d = FA_DIR / "feather"
    if not d.exists():
        return icons
    for f in sorted(d.glob("*.svg")):
        name = f.stem
        icons[f"feather/{name}"] = {
            "name": name,
            "style": "feather",
            "path": str(f),
            "categories": [],
        }
    return icons


def _list_custom_svgs() -> dict[str, dict]:
    """List custom/downloaded SVGs."""
    icons = {}
    for subdir in [SVG_ASSETS_DIR, SVG_ASSETS_DIR / "downloaded"]:
        if not subdir.exists():
            continue
        for f in sorted(subdir.glob("*.svg")):
            icons[f"custom/{f.stem}"] = {
                "name": f.stem,
                "style": "custom",
                "path": str(f),
                "categories": [],
            }
    return icons


def _all_external_icons() -> dict[str, dict]:
    """Merge all external icon sources."""
    icons = {}
    icons.update(_list_fa_icons())
    icons.update(_list_lucide_icons())
    icons.update(_list_feather_icons())
    icons.update(_list_custom_svgs())
    return icons


def build_index() -> dict:
    """Build a unified searchable index of all SVG sources."""
    library_names = _parse_library_names()
    all_external = _all_external_icons()

    fa_count = sum(1 for k in all_external if k.startswith("fa-"))
    lucide_count = sum(1 for k in all_external if k.startswith("lucide/"))
    feather_count = sum(1 for k in all_external if k.startswith("feather/"))
    custom_count = sum(1 for k in all_external if k.startswith("custom/"))

    stats = {
        "library_count": len(library_names),
        "fontawesome_count": fa_count,
        "lucide_count": lucide_count,
        "feather_count": feather_count,
        "custom_count": custom_count,
        "total_available": len(library_names) + len(all_external),
    }

    INDEX_PATH.write_text(json.dumps(stats, indent=2))
    return {"stats": stats}


def search(query: str, limit: int = 30) -> list[dict]:
    """Search all SVG sources by keyword."""
    query_lower = query.lower()
    results = []

    # Search svgLibrary first (already usable)
    for name in sorted(_parse_library_names()):
        if query_lower in name.lower():
            results.append({"name": name, "source": "svgLibrary", "usable": True, "match": "name"})

    # Search all external sources
    for key, info in _all_external_icons().items():
        source = info["style"]
        if query_lower in info["name"]:
            results.append({
                "name": info["name"],
                "source": source,
                "usable": False,
                "match": "name",
                "path": info["path"],
                "import_cmd": f"python svg_tools.py import {source} {info['name']}",
            })
        elif any(query_lower in cat for cat in info.get("categories", [])):
            results.append({
                "name": info["name"],
                "source": source,
                "usable": False,
                "match": "category",
                "path": info["path"],
                "import_cmd": f"python svg_tools.py import {source} {info['name']}",
            })

    return results[:limit]


def _extract_fa_path_data(svg_path: Path) -> tuple[str, str]:
    """Extract viewBox and path data from a Font Awesome SVG file."""
    content = svg_path.read_text()
    vb_match = re.search(r'viewBox="([^"]+)"', content)
    viewbox = vb_match.group(1) if vb_match else "0 0 512 512"
    # Extract all path d attributes
    paths = re.findall(r'<path d="([^"]+)"', content)
    return viewbox, paths


def _extract_svg_elements(svg_path: Path) -> tuple[str, list[str], bool]:
    """Extract viewBox, inner elements, and whether it's stroke-based from an SVG file."""
    content = svg_path.read_text()
    vb_match = re.search(r'viewBox="([^"]+)"', content)
    viewbox = vb_match.group(1) if vb_match else "0 0 24 24"
    # Extract all path/circle/rect/line/polyline/polygon elements
    elements = re.findall(r'<(path|circle|rect|line|polyline|polygon|ellipse)\s[^>]*/?>', content)
    # Check if stroke-based (Lucide/Feather style) vs fill-based (FA style)
    is_stroke = 'fill="none"' in content or 'stroke-linecap' in content
    # Extract full element tags
    tags = re.findall(r'<(?:path|circle|rect|line|polyline|polygon|ellipse)\s[^>]*/?\s*>', content)
    return viewbox, tags, is_stroke


def import_icon(source: str, name: str, alias: str = None) -> str:
    """Import an icon from any source into svgLibrary.tsx.

    Args:
        source: Source library ("fa-solid", "fa-regular", "lucide", "feather", or "custom")
        name: Icon name (e.g. "flask", "skull-crossbones", "activity")
        alias: Optional camelCase alias for the library key

    Returns:
        Status message
    """
    # Find the icon file
    if source.startswith("fa"):
        style = source.replace("fa-", "") if "-" in source else "solid"
        svg_path = FA_DIR / style / f"{name}.svg"
    elif source == "lucide":
        svg_path = FA_DIR / "lucide" / f"{name}.svg"
    elif source == "feather":
        svg_path = FA_DIR / "feather" / f"{name}.svg"
    elif source == "custom":
        svg_path = SVG_ASSETS_DIR / f"{name}.svg"
        if not svg_path.exists():
            svg_path = SVG_ASSETS_DIR / "downloaded" / f"{name}.svg"
    else:
        svg_path = None

    if not svg_path or not svg_path.exists():
        return f"Error: Icon '{name}' not found in {source}"

    # camelCase key
    if not alias:
        parts = name.split("-")
        lib_key = parts[0] + "".join(p.capitalize() for p in parts[1:])
    else:
        lib_key = alias

    existing = _parse_library_names()
    if lib_key in existing:
        return f"Icon '{lib_key}' already exists in svgLibrary.tsx"

    viewbox, tags, is_stroke = _extract_svg_elements(svg_path)
    if not tags:
        return f"Error: No SVG elements found in {svg_path}"

    helper = "strokeIcon" if is_stroke else "icon"
    comment_source = source

    # Clean tags for JSX: remove fill/stroke attrs that would override the component props
    cleaned_tags = []
    for tag in tags:
        # Remove explicit fill/stroke color values (keep "none" and "currentColor")
        t = re.sub(r'\s+fill="(?!none|currentColor)[^"]*"', '', tag)
        t = re.sub(r'\s+stroke="(?!none|currentColor)[^"]*"', '', t)
        # Convert stroke-* to camelCase for JSX
        t = t.replace('stroke-width', 'strokeWidth')
        t = t.replace('stroke-linecap', 'strokeLinecap')
        t = t.replace('stroke-linejoin', 'strokeLinejoin')
        # Self-close if not already
        if not t.rstrip().endswith('/>'):
            t = t.rstrip('>') + ' />'
        cleaned_tags.append(t)

    if len(cleaned_tags) == 1:
        jsx = f"  {lib_key}: {helper}('{viewbox}', {cleaned_tags[0]}),"
    else:
        elems = "\n    ".join(cleaned_tags)
        jsx = f"  {lib_key}: {helper}('{viewbox}', <>\n    {elems}\n  </>),"

    content = SVG_LIBRARY_PATH.read_text()
    # Find the }; that closes SVG_LIBRARY (followed by export type line)
    closing_match = re.search(r'\n};\s*\nexport type SvgIconName', content)
    if not closing_match:
        return "Error: Could not find SVG_LIBRARY closing }; in svgLibrary.tsx"

    insert_pos = closing_match.start()
    new_content = content[:insert_pos] + f"\n\n  // {comment_source}: {name}\n{jsx}\n" + content[insert_pos:]
    SVG_LIBRARY_PATH.write_text(new_content)

    return f"Imported '{name}' as '{lib_key}' ({helper}) into svgLibrary.tsx from {source}"


def import_fa(name: str, alias: str = None) -> str:
    """Import a Font Awesome icon (backward-compatible wrapper)."""
    return import_icon("fa-solid", name, alias)


def generate_svg(description: str) -> str:
    """Generate a custom SVG icon from a text description.

    Creates a simple geometric SVG based on the description.
    For complex illustrations, use an external tool and import.

    Returns the SVG markup string.
    """
    # This is a template-based generator for common shapes.
    # Complex custom art should use external tools (Figma, AI image gen → trace).
    desc_lower = description.lower()

    templates = {
        "jar": '''<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <rect x="25" y="15" width="50" height="10" rx="2" fill="currentColor" opacity="0.7"/>
  <rect x="20" y="25" width="60" height="55" rx="8" fill="currentColor" opacity="0.9"/>
  <rect x="20" y="80" width="60" height="8" rx="4" fill="currentColor" opacity="0.7"/>
  <ellipse cx="50" cy="52" rx="15" ry="12" fill="currentColor" opacity="0.3"/>
</svg>''',
        "needle": '''<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <rect x="45" y="10" width="10" height="60" rx="2" fill="currentColor"/>
  <polygon points="50,75 42,90 58,90" fill="currentColor"/>
  <rect x="35" y="5" width="30" height="12" rx="3" fill="currentColor" opacity="0.7"/>
  <line x1="50" y1="20" x2="50" y2="55" stroke="currentColor" stroke-width="1" opacity="0.3"/>
</svg>''',
        "cell": '''<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="50" cy="50" rx="35" ry="30" fill="currentColor" opacity="0.3" stroke="currentColor" stroke-width="2"/>
  <ellipse cx="45" cy="45" rx="12" ry="10" fill="currentColor" opacity="0.6"/>
  <circle cx="42" cy="43" r="4" fill="currentColor" opacity="0.9"/>
  <ellipse cx="60" cy="55" rx="6" ry="5" fill="currentColor" opacity="0.4"/>
  <ellipse cx="35" cy="58" rx="4" ry="3" fill="currentColor" opacity="0.4"/>
</svg>''',
        "grave": '''<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <rect x="30" y="20" width="40" height="55" rx="20" ry="20" fill="currentColor" opacity="0.8"/>
  <rect x="35" y="70" width="30" height="15" fill="currentColor" opacity="0.6"/>
  <line x1="50" y1="35" x2="50" y2="55" stroke="currentColor" stroke-width="4" opacity="0.4"/>
  <line x1="40" y1="45" x2="60" y2="45" stroke="currentColor" stroke-width="4" opacity="0.4"/>
  <rect x="20" y="85" width="60" height="5" rx="2" fill="currentColor" opacity="0.5"/>
</svg>''',
        "test_tube": '''<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <rect x="40" y="10" width="20" height="60" rx="2" fill="currentColor" opacity="0.3" stroke="currentColor" stroke-width="2"/>
  <rect x="40" y="50" width="20" height="25" rx="0" fill="currentColor" opacity="0.5"/>
  <ellipse cx="50" cy="75" rx="10" ry="12" fill="currentColor" opacity="0.5"/>
  <rect x="35" y="8" width="30" height="6" rx="2" fill="currentColor" opacity="0.7"/>
  <line x1="35" y1="30" x2="40" y2="30" stroke="currentColor" stroke-width="1.5" opacity="0.5"/>
  <line x1="35" y1="40" x2="40" y2="40" stroke="currentColor" stroke-width="1.5" opacity="0.5"/>
</svg>''',
    }

    # Match against templates
    for key, svg in templates.items():
        if key in desc_lower:
            return svg

    # Default: return a placeholder with the description
    return f'''<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <!-- Custom shape: {description} -->
  <!-- Replace with actual SVG paths -->
  <circle cx="50" cy="50" r="35" fill="currentColor" opacity="0.3" stroke="currentColor" stroke-width="2"/>
  <text x="50" y="55" text-anchor="middle" font-size="10" fill="currentColor">{description[:15]}</text>
</svg>'''


def add_custom_svg(name: str, svg_markup: str) -> str:
    """Add a custom SVG to svgLibrary.tsx from raw SVG markup.

    Args:
        name: Library key name (camelCase)
        svg_markup: Raw SVG string with viewBox and path elements

    Returns:
        Status message
    """
    existing = _parse_library_names()
    if name in existing:
        return f"Icon '{name}' already exists in svgLibrary.tsx"

    # Extract viewBox
    vb_match = re.search(r'viewBox="([^"]+)"', svg_markup)
    viewbox = vb_match.group(1) if vb_match else "0 0 100 100"

    # Extract all inner elements (paths, circles, rects, etc.)
    # Remove the outer <svg> wrapper
    inner = re.sub(r'<svg[^>]*>', '', svg_markup)
    inner = re.sub(r'</svg>', '', inner).strip()
    # Remove comments
    inner = re.sub(r'<!--.*?-->', '', inner, flags=re.DOTALL).strip()
    # Replace #000/#000000 fills/strokes with dark-but-visible color (invisible on #080A10 bg)
    inner = re.sub(r'fill="#(?:000000|000)"', 'fill="#1a1a2e"', inner)
    inner = re.sub(r'stroke="#(?:000000|000)"', 'stroke="#1a1a2e"', inner)
    # currentColor works because icon() sets style={{ color }} on the svg element

    jsx = f'  {name}: icon(\'{viewbox}\', <>\n    {inner}\n  </>),'

    content = SVG_LIBRARY_PATH.read_text()
    closing_match = re.search(r'\n};\s*\nexport type SvgIconName', content)
    if not closing_match:
        return "Error: Could not find SVG_LIBRARY closing }; in svgLibrary.tsx"

    insert_pos = closing_match.start()
    new_content = content[:insert_pos] + f"\n\n  // Custom: {name}\n{jsx}\n" + content[insert_pos:]
    SVG_LIBRARY_PATH.write_text(new_content)

    return f"Added custom icon '{name}' to svgLibrary.tsx (viewBox={viewbox})"


def list_library() -> list[str]:
    """List all icons currently available in svgLibrary.tsx."""
    return sorted(_parse_library_names())


def format_search_results(results: list[dict]) -> str:
    """Format search results for display."""
    if not results:
        return "No results found."

    lines = []
    usable = [r for r in results if r.get("usable")]
    importable = [r for r in results if not r.get("usable")]

    if usable:
        lines.append(f"\n  READY TO USE ({len(usable)} in svgLibrary.tsx):")
        for r in usable:
            lines.append(f"    {r['name']}")

    if importable:
        lines.append(f"\n  AVAILABLE TO IMPORT ({len(importable)}):")
        for r in importable:
            cmd = r.get("import_cmd", "")
            lines.append(f"    {r['name']:30s} [{r['source']}] {cmd}")

    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "search" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        results = search(query)
        print(format_search_results(results))

    elif cmd == "list-library":
        names = list_library()
        print(f"\nsvgLibrary.tsx: {len(names)} icons\n")
        for name in names:
            print(f"  {name}")

    elif cmd == "list-fa":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        fa = _list_fa_icons()
        matches = {k: v for k, v in fa.items() if query.lower() in v["name"]} if query else fa
        print(f"\nFont Awesome: {len(matches)} icons" + (f" matching '{query}'" if query else ""))
        for key, info in list(matches.items())[:50]:
            cats = ", ".join(info["categories"]) if info["categories"] else ""
            print(f"  {info['name']:35s} [{info['style']}] {cats}")
        if len(matches) > 50:
            print(f"  ... and {len(matches) - 50} more")

    elif cmd == "import-fa" and len(sys.argv) > 2:
        name = sys.argv[2]
        alias = sys.argv[3] if len(sys.argv) > 3 else None
        print(import_fa(name, alias))

    elif cmd == "import" and len(sys.argv) > 3:
        source = sys.argv[2]  # fa-solid, lucide, feather, custom
        name = sys.argv[3]
        alias = sys.argv[4] if len(sys.argv) > 4 else None
        print(import_icon(source, name, alias))

    elif cmd == "stats":
        index = build_index()
        for k, v in index["stats"].items():
            print(f"  {k}: {v}")

    elif cmd == "generate" and len(sys.argv) > 2:
        desc = " ".join(sys.argv[2:])
        svg = generate_svg(desc)
        print(svg)

    elif cmd == "build-index":
        index = build_index()
        print(f"Index built: {index['stats']}")

    else:
        print(__doc__)
