#!/usr/bin/env python3
"""Asset generation pipeline for vidgen screenplays.

Sources (in priority order):
1. Gemini 2.0 Flash (free tier) — illustrations, stylized backgrounds
2. SVG generation — diagrams, scale comparisons, abstract art
3. Wikimedia Commons API — real photos when needed
4. Pillow programmatic art — gradients, geometric, stylized overlays

Usage:
    python generate_assets.py easter_island.py
    python generate_assets.py easter_island.py --scene 4
    python generate_assets.py easter_island.py --source wikimedia --query "moai experiment"

Env vars:
    GEMINI_API_KEY — free key from aistudio.google.com/apikey
"""

import argparse
import importlib.util
import io
import json
import logging
import os
import re
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

logging.basicConfig(level=logging.INFO, format="[assets %(levelname)s] %(message)s")
log = logging.getLogger("assets")

ASSETS_DIR = Path(__file__).parent / "assets"
ASSETS_DIR.mkdir(exist_ok=True)


# ── Gemini Flash (free tier) ──

def gemini_available() -> bool:
    try:
        from google import genai
        return bool(os.environ.get("GEMINI_API_KEY"))
    except ImportError:
        return False


def gemini_generate_image(prompt: str, filename: str, width: int = 1080, height: int = 1920) -> str:
    """Generate an image via Gemini 2.0 Flash free tier.

    Get a free API key at: https://aistudio.google.com/apikey
    Install: pip install google-genai
    """
    try:
        from google import genai
    except ImportError:
        log.error("google-genai not installed. Run: pip install google-genai")
        return ""

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        log.error("GEMINI_API_KEY not set. Get a free key at https://aistudio.google.com/apikey")
        return ""

    client = genai.Client(api_key=api_key)

    # Enhance prompt for video frame assets
    full_prompt = (
        f"Generate an image for a TikTok video frame. "
        f"Aspect ratio: {width}x{height} (vertical/portrait). "
        f"Style: clean, high contrast, suitable for text overlay. "
        f"Dark backgrounds preferred. No text in the image. "
        f"\n\nScene description: {prompt}"
    )

    log.info(f"Gemini: generating '{filename}'...")
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=full_prompt,
            config={"response_modalities": ["image", "text"]},
        )

        # Extract image from response
        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                img_data = part.inline_data.data
                img = Image.open(io.BytesIO(img_data))
                output_path = ASSETS_DIR / filename
                img.save(str(output_path))
                log.info(f"Gemini: saved {output_path} ({img.width}x{img.height})")
                return str(output_path)

        log.warning("Gemini: no image in response")
        return ""
    except Exception as e:
        log.error(f"Gemini generation failed: {e}")
        return ""


# ── Wikimedia Commons search ──

def wikimedia_search(query: str, count: int = 5) -> list:
    """Search Wikimedia Commons for images. Returns list of dicts with url, title, thumb."""
    import requests

    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f"filetype:bitmap {query}",
        "gsrnamespace": 6,  # File namespace
        "gsrlimit": count,
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": 1080,
    }

    log.info(f"Wikimedia: searching '{query}'...")
    try:
        resp = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            timeout=10,
            headers={"User-Agent": "TkkVideoGen/1.0 (tkk@applesauce.chat)"},
        )
        resp.raise_for_status()
        data = resp.json()

        results = []
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            info = page.get("imageinfo", [{}])[0]
            results.append({
                "title": page.get("title", ""),
                "url": info.get("url", ""),
                "thumb": info.get("thumburl", ""),
                "width": info.get("width", 0),
                "height": info.get("height", 0),
                "mime": info.get("mime", ""),
            })

        log.info(f"Wikimedia: found {len(results)} results")
        return results
    except Exception as e:
        log.error(f"Wikimedia search failed: {e}")
        return []


def wikimedia_download(url: str, filename: str) -> str:
    """Download an image from Wikimedia Commons to assets/."""
    import requests

    output_path = ASSETS_DIR / filename
    log.info(f"Wikimedia: downloading to {output_path}...")
    try:
        resp = requests.get(
            url, timeout=30,
            headers={"User-Agent": "TkkVideoGen/1.0 (tkk@applesauce.chat)"},
        )
        resp.raise_for_status()
        output_path.write_bytes(resp.content)

        # Verify it's a valid image
        img = Image.open(output_path)
        log.info(f"Wikimedia: saved {output_path} ({img.width}x{img.height})")
        return str(output_path)
    except Exception as e:
        log.error(f"Wikimedia download failed: {e}")
        return ""


# ── SVG generation ──

def save_svg(svg_content: str, filename: str) -> str:
    """Save SVG content to assets/ and return path."""
    output_path = ASSETS_DIR / filename
    output_path.write_text(svg_content)
    log.info(f"SVG: saved {output_path}")
    return str(output_path)


def svg_to_png(svg_path: str, output_filename: str, width: int = 1080, height: int = 1920) -> str:
    """Convert SVG to PNG at target resolution."""
    try:
        import cairosvg
    except ImportError:
        log.error("cairosvg not installed. Run: pip install cairosvg")
        return ""

    output_path = ASSETS_DIR / output_filename
    cairosvg.svg2png(url=svg_path, write_to=str(output_path),
                     output_width=width, output_height=height)
    log.info(f"SVG→PNG: saved {output_path} ({width}x{height})")
    return str(output_path)


# ── Pillow programmatic art ──

def generate_gradient(filename: str, colors: list, width: int = 1080, height: int = 1920,
                      direction: str = "vertical") -> str:
    """Generate a gradient background image."""
    img = Image.new("RGBA", (width, height))

    def hex_to_rgba(h):
        h = h.lstrip("#")
        if len(h) == 8:
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4, 6))
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (255,)

    c1 = hex_to_rgba(colors[0])
    c2 = hex_to_rgba(colors[-1])

    for i in range(height if direction == "vertical" else width):
        t = i / max(1, (height if direction == "vertical" else width) - 1)
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        a = int(c1[3] + (c2[3] - c1[3]) * t)
        draw = ImageDraw.Draw(img)
        if direction == "vertical":
            draw.line([(0, i), (width, i)], fill=(r, g, b, a))
        else:
            draw.line([(i, 0), (i, height)], fill=(r, g, b, a))

    output_path = ASSETS_DIR / filename
    img.save(str(output_path))
    log.info(f"Gradient: saved {output_path}")
    return str(output_path)


def stylize_photo(input_path: str, output_filename: str,
                  desaturate: float = 0.0, posterize: int = 0,
                  tint: str = None, blur: float = 0.0,
                  darken: float = 0.0) -> str:
    """Apply stylization effects to an existing photo.

    Args:
        desaturate: 0.0 (full color) to 1.0 (grayscale)
        posterize: 0 (off) or 2-8 (color levels)
        tint: hex color to overlay (e.g. "#FF000033")
        blur: Gaussian blur radius
        darken: 0.0-1.0 how much to darken
    """
    img = Image.open(input_path).convert("RGBA")

    if blur > 0:
        img = img.filter(ImageFilter.GaussianBlur(radius=blur))

    if desaturate > 0:
        gray = img.convert("L").convert("RGBA")
        img = Image.blend(img, gray, desaturate)

    if posterize and 2 <= posterize <= 8:
        from PIL import ImageOps
        rgb = img.convert("RGB")
        rgb = ImageOps.posterize(rgb, posterize)
        img = rgb.convert("RGBA")

    if tint:
        h = tint.lstrip("#")
        if len(h) == 8:
            tint_rgba = tuple(int(h[i:i+2], 16) for i in (0, 2, 4, 6))
        else:
            tint_rgba = tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (80,)
        overlay = Image.new("RGBA", img.size, tint_rgba)
        img = Image.alpha_composite(img, overlay)

    if darken > 0:
        dark = Image.new("RGBA", img.size, (0, 0, 0, int(255 * darken)))
        img = Image.alpha_composite(img, dark)

    output_path = ASSETS_DIR / output_filename
    img.save(str(output_path))
    log.info(f"Stylize: saved {output_path}")
    return str(output_path)


def generate_silhouette(input_path: str, output_filename: str,
                        threshold: int = 128, color: str = "#FFFFFF") -> str:
    """Convert image to silhouette (threshold + fill color)."""
    img = Image.open(input_path).convert("L")
    # Threshold to binary
    img = img.point(lambda x: 255 if x < threshold else 0)
    img = img.convert("RGBA")

    # Apply color
    h = color.lstrip("#")
    fill = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    r, g, b, a = img.split()
    colored = Image.merge("RGBA", (
        r.point(lambda _: fill[0]),
        g.point(lambda _: fill[1]),
        b.point(lambda _: fill[2]),
        a,
    ))

    output_path = ASSETS_DIR / output_filename
    colored.save(str(output_path))
    log.info(f"Silhouette: saved {output_path}")
    return str(output_path)


# ── Screenplay parser ──

def extract_scene_descriptions(screenplay_path: str) -> list:
    """Extract visual direction comments from a screenplay .py file."""
    scenes = []
    with open(screenplay_path) as f:
        content = f.read()

    # Find comment blocks between === markers
    # Format: # ====...
    #         # Scene N: TITLE (timing)
    #         # "narration text"
    #         # Visual: description
    #         # Purpose: why
    #         # ====...
    blocks = re.findall(
        r'#\s*={5,}\s*\n'
        r'((?:\s*#[^\n]*\n)+?)'
        r'\s*#\s*={5,}',
        content,
    )

    for block in blocks:
        lines = [l.strip() for l in block.strip().split("\n")]
        # Strip leading # and whitespace from each line
        lines = [re.sub(r'^#\s*', '', l) for l in lines]
        scene = {
            "title": "",
            "visual": "",
            "purpose": "",
            "note": "",
            "narration": "",
        }
        for line in lines:
            if re.match(r'Scene\s*\d', line):
                scene["title"] = line
            elif line.startswith("Visual:"):
                scene["visual"] = line[7:].strip()
            elif line.startswith("Purpose:"):
                scene["purpose"] = line[8:].strip()
            elif line.startswith("Note:"):
                scene["note"] = line[5:].strip()
            elif line.startswith('"') or line.startswith("'"):
                scene["narration"] = line.strip('"').strip("'")
        scenes.append(scene)

    return scenes


# ── Main pipeline ──

def generate_for_screenplay(screenplay_path: str, scene_num: int = None,
                            source: str = "auto", query: str = None):
    """Generate assets for a screenplay file.

    Args:
        screenplay_path: Path to screenplay .py file
        scene_num: Specific scene to generate for (1-indexed), or None for all
        source: "gemini", "wikimedia", "svg", "pillow", or "auto"
        query: Override search query for wikimedia
    """
    scenes = extract_scene_descriptions(screenplay_path)
    if not scenes:
        log.warning("No scene descriptions found in screenplay. Add comment blocks with Visual: directions.")
        return

    log.info(f"Found {len(scenes)} scenes in {screenplay_path}")

    for i, scene in enumerate(scenes):
        if scene_num and (i + 1) != scene_num:
            continue

        log.info(f"\n{'='*50}")
        log.info(f"Scene {i+1}: {scene['title']}")
        log.info(f"Visual: {scene['visual']}")
        log.info(f"{'='*50}")

        if not scene["visual"]:
            log.warning(f"Scene {i+1}: No visual direction — skipping")
            continue

        visual = scene["visual"]

        # Auto source selection
        if source == "auto":
            if any(kw in visual.lower() for kw in ["diagram", "vector", "illustration", "scale comparison", "infographic"]):
                if gemini_available():
                    _source = "gemini"
                else:
                    _source = "svg"
                    log.info("Gemini unavailable — using SVG fallback")
            elif any(kw in visual.lower() for kw in ["photo", "painting", "historical", "real"]):
                _source = "wikimedia"
            elif gemini_available():
                _source = "gemini"
            else:
                _source = "wikimedia"
        else:
            _source = source

        filename = f"scene_{i+1}_{scene['title'].split(':')[0].strip().lower().replace(' ', '_')[:30]}"

        if _source == "gemini":
            result = gemini_generate_image(visual, f"{filename}.png")
            if result:
                log.info(f"Scene {i+1}: Generated via Gemini → {result}")
            else:
                log.warning(f"Scene {i+1}: Gemini failed, trying wikimedia fallback")
                _wikimedia_fallback(visual, query, filename)

        elif _source == "wikimedia":
            _wikimedia_fallback(visual, query, filename)

        elif _source == "svg":
            log.info(f"Scene {i+1}: SVG source selected — write SVG manually or use Gemini")
            log.info(f"  Hint: save SVG to assets/{filename}.svg, then run:")
            log.info(f"  python -c \"from generate_assets import svg_to_png; svg_to_png('assets/{filename}.svg', '{filename}.png')\"")

        elif _source == "pillow":
            log.info(f"Scene {i+1}: Pillow source — use generate_gradient() or stylize_photo() directly")


def _wikimedia_fallback(visual: str, query: str, filename: str):
    """Search Wikimedia and download best result."""
    search_query = query or visual
    results = wikimedia_search(search_query, count=5)
    if results:
        # Pick the best (largest) image
        best = max(results, key=lambda r: r.get("width", 0) * r.get("height", 0))
        log.info(f"  Best match: {best['title']} ({best['width']}x{best['height']})")
        ext = best.get("mime", "image/jpeg").split("/")[-1]
        ext = ext.replace("jpeg", "jpg")
        result = wikimedia_download(best["url"], f"{filename}.{ext}")
        if result:
            log.info(f"  Downloaded → {result}")
    else:
        log.warning(f"  No Wikimedia results for '{search_query}'")


# ── CLI ──

def print_status():
    """Print current tool availability."""
    print("\n=== Asset Generation Pipeline Status ===\n")

    # Gemini
    try:
        from google import genai
        has_sdk = True
    except ImportError:
        has_sdk = False

    has_key = bool(os.environ.get("GEMINI_API_KEY"))

    if has_sdk and has_key:
        print("  Gemini Flash:  READY")
    elif has_sdk:
        print("  Gemini Flash:  SDK installed, needs GEMINI_API_KEY")
        print("                 Get free key: https://aistudio.google.com/apikey")
    else:
        print("  Gemini Flash:  NOT AVAILABLE")
        print("                 Install: pip install google-genai")
        print("                 Get free key: https://aistudio.google.com/apikey")

    # CairoSVG
    try:
        import cairosvg
        print("  CairoSVG:      READY")
    except ImportError:
        print("  CairoSVG:      NOT AVAILABLE (pip install cairosvg)")

    # Wikimedia
    try:
        import requests
        print("  Wikimedia:     READY")
    except ImportError:
        print("  Wikimedia:     NOT AVAILABLE (pip install requests)")

    # Pillow
    try:
        from PIL import Image
        print("  Pillow:        READY")
    except ImportError:
        print("  Pillow:        NOT AVAILABLE (pip install Pillow)")

    # Kokoro TTS
    try:
        import kokoro
        print("  Kokoro TTS:    READY")
    except ImportError:
        print("  Kokoro TTS:    NOT AVAILABLE (pip install kokoro)")

    print(f"\n  Assets dir:    {ASSETS_DIR}")
    asset_count = len(list(ASSETS_DIR.glob("*")))
    print(f"  Assets count:  {asset_count}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate assets for vidgen screenplays")
    parser.add_argument("screenplay", nargs="?", help="Path to screenplay .py file")
    parser.add_argument("--scene", type=int, help="Generate for specific scene (1-indexed)")
    parser.add_argument("--source", choices=["auto", "gemini", "wikimedia", "svg", "pillow"],
                        default="auto", help="Asset source")
    parser.add_argument("--query", help="Override search query for wikimedia")
    parser.add_argument("--status", action="store_true", help="Print tool availability")

    # Direct tool commands
    parser.add_argument("--search", help="Search Wikimedia Commons")
    parser.add_argument("--download", nargs=2, metavar=("URL", "FILENAME"),
                        help="Download from URL to assets/")
    parser.add_argument("--gradient", nargs="+", metavar="COLOR",
                        help="Generate gradient (e.g. --gradient '#111117' '#2a1a3a')")
    parser.add_argument("--stylize", nargs=2, metavar=("INPUT", "OUTPUT"),
                        help="Stylize a photo")
    parser.add_argument("--desaturate", type=float, default=0.0)
    parser.add_argument("--tint", default=None)
    parser.add_argument("--darken", type=float, default=0.0)
    parser.add_argument("--blur", type=float, default=0.0)

    args = parser.parse_args()

    if args.status:
        print_status()
    elif args.search:
        results = wikimedia_search(args.search)
        for r in results:
            print(f"  {r['title']}")
            print(f"    {r['url']}")
            print(f"    {r['width']}x{r['height']} {r['mime']}")
            print()
    elif args.download:
        wikimedia_download(args.download[0], args.download[1])
    elif args.gradient:
        generate_gradient("gradient_bg.png", args.gradient)
    elif args.stylize:
        stylize_photo(args.stylize[0], args.stylize[1],
                      desaturate=args.desaturate, tint=args.tint,
                      darken=args.darken, blur=args.blur)
    elif args.screenplay:
        generate_for_screenplay(args.screenplay, scene_num=args.scene,
                                source=args.source, query=args.query)
    else:
        print_status()
        parser.print_help()
