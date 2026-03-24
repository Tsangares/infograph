/**
 * TKK vertical zone system — pixel coordinates for 1080×1920 portrait.
 *
 * The zone system uses a unit coordinate system where y ranges from -8 to +8
 * (16 units tall). Convert: pixel_y = (8 - unit_y) / 16 * 1920
 */

export const WIDTH = 1080;
export const HEIGHT = 1920;
export const FPS = 30;

/** Convert unit y-coordinate (-8 to +8 range) to pixel y (top-down). */
export function unitToPixelY(unitY: number): number {
  return ((8 - unitY) / 16) * HEIGHT;
}

/** Named vertical zones for content layout. */
export const ZONES = {
  TITLE:  { y: unitToPixelY(6.2),  range: [unitToPixelY(7.0), unitToPixelY(5.5)] },
  UPPER:  { y: unitToPixelY(3.5),  range: [unitToPixelY(5.5), unitToPixelY(1.5)] },
  MID:    { y: unitToPixelY(0.0),  range: [unitToPixelY(1.5), unitToPixelY(-1.5)] },
  LOWER:  { y: unitToPixelY(-3.5), range: [unitToPixelY(-1.5), unitToPixelY(-5.5)] },
  FOOTER: { y: unitToPixelY(-6.0), range: [unitToPixelY(-5.5), unitToPixelY(-6.4)] },
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
