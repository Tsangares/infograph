/**
 * Video-calibrated font sizes for 1080×1920 vertical canvas.
 *
 * These are 3-4× larger than web defaults. Research shows minimum body text
 * for full HD video on smartphones is 40-58px. See REMOTION_DESIGN_GUIDE.md.
 *
 * Previous values (hero: 96, headline: 64, body: 32) were web-scale and
 * vanished on phone screens under TikTok compression.
 */
export const FONT_SIZE = {
  hero: 200,       // ~73px phone — Counter main, dominates frame
  stat: 160,       // ~58px phone — Secondary stat numbers
  headline: 96,    // ~35px phone — Section headlines, readable in thumbnails
  subtitle: 64,    // ~23px phone — Subheadings, clear hierarchy
  body: 48,        // ~17px phone — Descriptions, minimum for legibility
  caption: 36,     // ~13px phone — Labels, captions (bold weight required)
  dataLabel: 36,   // ~13px phone — Timeline years, chart emphasis
  dataValue: 32,   // ~12px phone — Bar values, map/icon labels
  pill: 32,        // ~12px phone — LabelPill
  source: 28,      // ~10px phone — Source citations (not critical for glance)
  min: 28,         // absolute minimum — nothing smaller
} as const;
