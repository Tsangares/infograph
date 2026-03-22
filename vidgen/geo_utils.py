"""Geographic coordinate system for TKK video pipeline.

Converts real lat/lon coordinates to accurate manim frame positions
on cropped equirectangular map imagery.

Usage:
    from geo_utils import GeoMap
    from geo_locations import LOCATIONS

    geo = GeoMap("eastern_med")
    pos = geo.latlon_to_manim(*LOCATIONS["hattusa"])
    img = geo.get_image_mobject(opacity=0.65)
    geo.verify_positions({"Hattusa": (40.02, 34.62)}, output="verify.png")
"""

import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = Path(__file__).parent / "assets"
EARTH_TOPO = ASSETS_DIR / "earth_topo.jpg"

# earth_topo.jpg is 2048x1024 equirectangular:
#   lon: -180 (left) to +180 (right)
#   lat: +90 (top) to -90 (bottom)
EARTH_W = 2048
EARTH_H = 1024


@dataclass
class MapRegion:
    name: str
    lon_min: float
    lon_max: float
    lat_min: float  # southern bound
    lat_max: float  # northern bound


class GeoMap:
    def __init__(self, region, earth_topo=None, map_width=7.12, map_center_y=3.5):
        if isinstance(region, str):
            from geo_locations import MAP_REGIONS
            region = MAP_REGIONS[region]
        self.region = region
        self.earth_topo = Path(earth_topo) if earth_topo else EARTH_TOPO
        self.map_width = map_width
        self.map_center_y = map_center_y

        # Compute crop pixel bounds on the 2048x1024 source
        self.crop_x0 = int(EARTH_W * (region.lon_min + 180) / 360)
        self.crop_x1 = int(EARTH_W * (region.lon_max + 180) / 360)
        self.crop_y0 = int(EARTH_H * (90 - region.lat_max) / 180)
        self.crop_y1 = int(EARTH_H * (90 - region.lat_min) / 180)
        self.crop_w = self.crop_x1 - self.crop_x0
        self.crop_h = self.crop_y1 - self.crop_y0

        # Compute how the crop maps to manim units
        # ImageMobject is scaled to map_width, height auto-scales
        self.scale = self.map_width / self.crop_w  # manim units per crop pixel
        self.map_height = self.crop_h * self.scale

    def latlon_to_equirect_px(self, lat, lon):
        """Convert lat/lon to pixel position on the 2048x1024 source."""
        px_x = EARTH_W * (lon + 180) / 360
        px_y = EARTH_H * (90 - lat) / 180
        return px_x, px_y

    def latlon_to_crop_px(self, lat, lon):
        """Convert lat/lon to pixel position within the cropped region."""
        eq_x, eq_y = self.latlon_to_equirect_px(lat, lon)
        return eq_x - self.crop_x0, eq_y - self.crop_y0

    def latlon_to_manim(self, lat, lon):
        """Convert lat/lon to manim frame coordinates (np.array).

        The map image center is at (0, map_center_y) in manim coords.
        """
        crop_x, crop_y = self.latlon_to_crop_px(lat, lon)
        # Manim X: crop center is 0, right is positive
        mx = (crop_x - self.crop_w / 2) * self.scale
        # Manim Y: crop center maps to map_center_y, up is positive
        my = self.map_center_y + (self.crop_h / 2 - crop_y) * self.scale
        return np.array([mx, my, 0.0])

    def crop_map(self, output_path=None):
        """Crop earth_topo.jpg to this region. Returns output path."""
        if output_path is None:
            output_path = ASSETS_DIR / f"{self.region.name}_crop.jpg"
        output_path = Path(output_path)
        img = Image.open(self.earth_topo)
        cropped = img.crop((self.crop_x0, self.crop_y0, self.crop_x1, self.crop_y1))
        # Upscale to at least 1080px wide for quality
        if cropped.width < 1080:
            ratio = 1080 / cropped.width
            cropped = cropped.resize(
                (int(cropped.width * ratio), int(cropped.height * ratio)),
                Image.LANCZOS,
            )
        cropped.save(str(output_path), quality=95)
        return str(output_path)

    def get_image_mobject(self, opacity=0.65):
        """Return a positioned manim ImageMobject for this map region."""
        from manim import ImageMobject, UP
        crop_path = self.crop_map()
        img = ImageMobject(str(crop_path))
        img.width = self.map_width
        img.move_to(UP * self.map_center_y)
        img.set_opacity(opacity)
        return img

    def verify_positions(self, locations, output="geo_verify.png"):
        """Render labeled dots on the map crop and save a QA PNG.

        Args:
            locations: dict of {"Name": (lat, lon), ...}
            output: output PNG path
        """
        img = Image.open(self.earth_topo)
        cropped = img.crop((self.crop_x0, self.crop_y0, self.crop_x1, self.crop_y1))
        # Scale up for readability
        scale = max(1, 1080 // cropped.width)
        cropped = cropped.resize(
            (cropped.width * scale, cropped.height * scale), Image.LANCZOS
        )
        draw = ImageDraw.Draw(cropped)

        # Try to load a font, fall back to default
        try:
            font = ImageFont.truetype("/opt/tkk/vidgen/fonts/Inter-Bold.ttf", 14 * scale)
            font_sm = ImageFont.truetype("/opt/tkk/vidgen/fonts/Inter-Bold.ttf", 10 * scale)
        except Exception:
            font = ImageFont.load_default()
            font_sm = font

        # Draw grid lines every 10 degrees
        for lon in range(int(self.region.lon_min), int(self.region.lon_max) + 1, 10):
            x = (lon - self.region.lon_min) / (self.region.lon_max - self.region.lon_min) * cropped.width
            draw.line([(x, 0), (x, cropped.height)], fill=(255, 255, 255, 60), width=1)
            draw.text((x + 2, 2), f"{lon}°E" if lon >= 0 else f"{-lon}°W",
                      fill=(200, 200, 200), font=font_sm)
        for lat in range(int(self.region.lat_min), int(self.region.lat_max) + 1, 10):
            y = (self.region.lat_max - lat) / (self.region.lat_max - self.region.lat_min) * cropped.height
            draw.line([(0, y), (cropped.width, y)], fill=(255, 255, 255, 60), width=1)
            draw.text((2, y + 2), f"{lat}°N" if lat >= 0 else f"{-lat}°S",
                      fill=(200, 200, 200), font=font_sm)

        # Draw each location marker
        for name, (lat, lon) in locations.items():
            # Position within the cropped image
            x = (lon - self.region.lon_min) / (self.region.lon_max - self.region.lon_min) * cropped.width
            y = (self.region.lat_max - lat) / (self.region.lat_max - self.region.lat_min) * cropped.height

            r = 6 * scale
            # Crosshair
            draw.line([(x - r*2, y), (x + r*2, y)], fill=(255, 50, 50), width=2)
            draw.line([(x, y - r*2), (x, y + r*2)], fill=(255, 50, 50), width=2)
            # Dot
            draw.ellipse([(x - r, y - r), (x + r, y + r)], fill=(255, 215, 0), outline=(255, 50, 50), width=2)
            # Label
            draw.text((x + r + 4, y - r), f"{name}", fill=(255, 255, 255), font=font)
            draw.text((x + r + 4, y + r), f"({lat:.1f}°, {lon:.1f}°)", fill=(180, 180, 180), font=font_sm)

            # Warnings
            warnings = self._check_position(lat, lon, name)
            if warnings:
                for i, w in enumerate(warnings):
                    draw.text((x + r + 4, y + r * 3 + i * 12 * scale), f"⚠ {w}",
                              fill=(255, 100, 100), font=font_sm)

        # Title
        draw.text((10, cropped.height - 20 * scale),
                  f"Region: {self.region.name} | {self.region.lon_min}°-{self.region.lon_max}° lon, {self.region.lat_min}°-{self.region.lat_max}° lat",
                  fill=(200, 200, 200), font=font_sm)

        cropped.save(output)
        return output

    def _check_position(self, lat, lon, name=""):
        """Basic sanity checks on a lat/lon position."""
        warnings = []
        if not (self.region.lat_min <= lat <= self.region.lat_max):
            warnings.append(f"Latitude {lat} outside region [{self.region.lat_min}, {self.region.lat_max}]")
        if not (self.region.lon_min <= lon <= self.region.lon_max):
            warnings.append(f"Longitude {lon} outside region [{self.region.lon_min}, {self.region.lon_max}]")
        if abs(lat) > 90:
            warnings.append("Latitude out of range (-90 to 90)")
        if abs(lon) > 180:
            warnings.append("Longitude out of range (-180 to 180)")
        # Check if lat/lon might be swapped (common error)
        if abs(lat) < 20 and abs(lon) > 30 and "equat" not in name.lower():
            pass  # Low latitude is valid for many places
        return warnings
