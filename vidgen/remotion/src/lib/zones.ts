/**
 * TKK vertical zone system — pixel coordinates for 1080×1920 portrait.
 *
 * Manim uses a coordinate system where y ranges from -8 to +8 (16 units tall).
 * Convert: pixel_y = (8 - manim_y) / 16 * 1920
 */

export const WIDTH = 1080;
export const HEIGHT = 1920;
export const FPS = 30;

/** Convert Manim y-coordinate to pixel y (top-down). */
export function manimToPixelY(manimY: number): number {
  return ((8 - manimY) / 16) * HEIGHT;
}

/** Named vertical zones matching anim_primitives.py */
export const ZONES = {
  TITLE:  { y: manimToPixelY(6.2),  range: [manimToPixelY(7.0), manimToPixelY(5.5)] },
  UPPER:  { y: manimToPixelY(3.5),  range: [manimToPixelY(5.5), manimToPixelY(1.5)] },
  MID:    { y: manimToPixelY(0.0),  range: [manimToPixelY(1.5), manimToPixelY(-1.5)] },
  LOWER:  { y: manimToPixelY(-3.5), range: [manimToPixelY(-1.5), manimToPixelY(-5.5)] },
  FOOTER: { y: manimToPixelY(-6.0), range: [manimToPixelY(-5.5), manimToPixelY(-6.4)] },
} as const;

export type ZoneName = keyof typeof ZONES;

/**
 * Safe area bounds — avoiding TikTok/Reels/Shorts UI overlays.
 *
 * Top 200px: username, sound label, Shorts title
 * Bottom 400px: caption bar, CTA, description (TikTok deepest at ~480px)
 * Right 140px: like/comment/share/profile buttons
 * Left 120px: caption text overflow
 *
 * Usable area: ~820×1320px centered in 1080×1920.
 * See REMOTION_DESIGN_GUIDE.md for full breakdown.
 */
export const SAFE = {
  top: 200,       // Platform UI: username, sound label
  bottom: 1520,   // Platform UI: caption bar, CTA (400px clearance)
  left: 120,      // Caption text overflow
  right: 940,     // Like/comment/share buttons (140px clearance)
  width: 820,     // Usable width (1080 - 120 - 140)
  height: 1320,   // Usable height (1520 - 200)
} as const;

/**
 * Get absolute style for positioning in a zone.
 * Returns CSS properties for absolute positioning centered in the zone.
 */
export function zoneStyle(zone: ZoneName): React.CSSProperties {
  const z = ZONES[zone];
  const height = z.range[1] - z.range[0];
  return {
    position: 'absolute',
    top: z.range[0],
    left: SAFE.left,
    width: SAFE.width,
    height,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  };
}

/** Get the pixel height of a named zone. */
export function zoneHeight(zone: ZoneName): number {
  const z = ZONES[zone];
  return z.range[1] - z.range[0];
}
