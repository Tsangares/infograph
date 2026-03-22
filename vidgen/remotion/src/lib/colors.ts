/**
 * TKK color palette — matches anim_primitives.py exactly.
 */

// Core palette
export const TKK_BG = '#080A10';
export const TKK_BG_WARM = '#0A0A10';
export const TKK_GOLD = '#FFD700';
export const TKK_RED = '#EF4444';
export const TKK_GREEN = '#22C55E';
export const TKK_WHITE = '#F0F0F0';
export const TKK_DIM = '#334155';
export const TKK_MUTED = '#475569';
export const TKK_ACCENT = '#3B82F6';

// Surface & grid
export const TKK_SURFACE = '#15192A';
export const TKK_GRID = '#1A2030';

// WCAG contrast ratio utility
function hexToLuminance(hex: string): number {
  const h = hex.replace('#', '');
  const r = parseInt(h.slice(0, 2), 16) / 255;
  const g = parseInt(h.slice(2, 4), 16) / 255;
  const b = parseInt(h.slice(4, 6), 16) / 255;
  const toLinear = (c: number) => c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  return 0.2126 * toLinear(r) + 0.7152 * toLinear(g) + 0.0722 * toLinear(b);
}

export function contrastRatio(fg: string, bg: string): number {
  const l1 = hexToLuminance(fg);
  const l2 = hexToLuminance(bg);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

// Semantic aliases
export const COLORS = {
  bg: TKK_BG,
  bgWarm: TKK_BG_WARM,
  gold: TKK_GOLD,
  red: TKK_RED,
  green: TKK_GREEN,
  white: TKK_WHITE,
  dim: TKK_DIM,
  muted: TKK_MUTED,
  accent: TKK_ACCENT,
  surface: TKK_SURFACE,
  grid: TKK_GRID,
} as const;
