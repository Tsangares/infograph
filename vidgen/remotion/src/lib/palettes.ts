/**
 * Semantic color palettes for TKK videos.
 *
 * Instead of the LLM choosing hex codes (which it's bad at),
 * it picks a palette name and assigns semantic roles to elements.
 * Every palette is pre-validated for contrast against its own bg.
 *
 * Usage in manifests:
 *   "colors": { "palette": "electric" }
 *   Element: { "colorRole": "negative" }
 *
 * Usage in code:
 *   import { getPalette, resolveColor } from '../lib/palettes';
 *   const palette = getPalette('electric');
 *   const color = resolveColor(palette, 'negative'); // → '#FF6B6B'
 */

export interface Palette {
  name: string;
  bg: string;
  accent: string;       // Primary data, hero numbers, first series
  secondary: string;    // Second data series, supporting elements
  highlight: string;    // Callouts, emphasis, key moments
  negative: string;     // Decline, loss, danger, death
  positive: string;     // Growth, gain, success, life
  neutral: string;      // Axes, gridlines, secondary text
  text: string;         // Primary text
  textMuted: string;    // Labels, captions, sources
}

export type ColorRole = keyof Omit<Palette, 'name'>;

export const PALETTES: Record<string, Palette> = {
  // Gold on dark — classic TKK look
  gold: {
    name: 'gold',
    bg: '#080A10',
    accent: '#FFD700',
    secondary: '#3B82F6',
    highlight: '#F59E0B',
    negative: '#EF4444',
    positive: '#22C55E',
    neutral: '#8A8A9A',
    text: '#EAEAF0',
    textMuted: '#94A3B8',
  },

  // Electric — vibrant, high energy
  electric: {
    name: 'electric',
    bg: '#0A0A14',
    accent: '#FF6B35',
    secondary: '#4ECDC4',
    highlight: '#FFE66D',
    negative: '#FF6B6B',
    positive: '#95E77E',
    neutral: '#9CA3AF',
    text: '#F0F0F5',
    textMuted: '#A0A0B0',
  },

  // Ocean — cool, scientific, medical
  ocean: {
    name: 'ocean',
    bg: '#0B1120',
    accent: '#22D3EE',
    secondary: '#818CF8',
    highlight: '#67E8F9',
    negative: '#FB7185',
    positive: '#34D399',
    neutral: '#94A3B8',
    text: '#E2E8F0',
    textMuted: '#93A3B8',
  },

  // Blood — intense, war, disaster
  blood: {
    name: 'blood',
    bg: '#0F0A0A',
    accent: '#EF4444',
    secondary: '#F97316',
    highlight: '#FBBF24',
    negative: '#DC2626',
    positive: '#4ADE80',
    neutral: '#9CA3AF',
    text: '#FEE2E2',
    textMuted: '#FCA5A5',
  },

  // Neon — cyberpunk, tech, modern
  neon: {
    name: 'neon',
    bg: '#0A0A1A',
    accent: '#A855F7',
    secondary: '#06B6D4',
    highlight: '#F472B6',
    negative: '#F43F5E',
    positive: '#10B981',
    neutral: '#6B7280',
    text: '#E5E7EB',
    textMuted: '#9CA3AF',
  },

  // Earth — historical, ancient, natural
  earth: {
    name: 'earth',
    bg: '#0F0E0A',
    accent: '#D4A017',
    secondary: '#7C3AED',
    highlight: '#F59E0B',
    negative: '#DC2626',
    positive: '#65A30D',
    neutral: '#A8A29E',
    text: '#F5F5F4',
    textMuted: '#A8A29E',
  },

  // Frost — cold, space, isolation
  frost: {
    name: 'frost',
    bg: '#0C1222',
    accent: '#60A5FA',
    secondary: '#A78BFA',
    highlight: '#93C5FD',
    negative: '#F87171',
    positive: '#6EE7B7',
    neutral: '#94A3B8',
    text: '#E2E8F0',
    textMuted: '#94A3B8',
  },

  // Ember — warm, industrial, decay
  ember: {
    name: 'ember',
    bg: '#110A08',
    accent: '#F97316',
    secondary: '#EAB308',
    highlight: '#FB923C',
    negative: '#EF4444',
    positive: '#84CC16',
    neutral: '#A8A29E',
    text: '#FEF3C7',
    textMuted: '#D6D3D1',
  },
};

/**
 * Get a palette by name. Falls back to 'gold' if not found.
 */
export function getPalette(name: string): Palette {
  return PALETTES[name] ?? PALETTES.gold;
}

/**
 * Resolve a color role to a hex value from a palette.
 */
export function resolveColor(palette: Palette, role: ColorRole): string {
  return palette[role];
}

/**
 * Convert a manifest's color config to resolved hex values.
 * Supports both old format { bg, accent, secondary } and new { palette }.
 */
export function resolveManifestColors(colors: Record<string, string>): {
  bg: string;
  accent: string;
  secondary: string;
  palette?: Palette;
} {
  if (colors.palette) {
    const p = getPalette(colors.palette);
    return { bg: p.bg, accent: p.accent, secondary: p.secondary, palette: p };
  }
  return { bg: colors.bg, accent: colors.accent, secondary: colors.secondary };
}
