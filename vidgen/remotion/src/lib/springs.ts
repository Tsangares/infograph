import { measureSpring } from 'remotion';
import { FPS } from './zones';

/**
 * Centralized spring presets for TKK animations.
 * Every component should import from here instead of hardcoding configs.
 */
export const SPRINGS = {
  /** UI entrances — pills, labels, snappy feel */
  snappy: { damping: 20, stiffness: 200, mass: 0.8 },
  /** Backgrounds, fades — slow and smooth */
  gentle: { damping: 200, stiffness: 80, mass: 1 },
  /** Hero stats landing with impact */
  dramatic: { damping: 12, stiffness: 200, mass: 1.2 },
  /** Icons, badges — playful overshoot */
  bouncy: { damping: 8, stiffness: 180, mass: 0.5 },
  /** No-bounce counters, smooth convergence */
  smooth: { damping: 100, stiffness: 100, mass: 1 },

  // Legacy aliases matching existing component configs:
  /** Headline entrance: { damping: 12, stiffness: 80, mass: 0.8 } */
  headline: { damping: 12, stiffness: 80, mass: 0.8 },
  /** Bar chart growth: { damping: 18, stiffness: 80 } */
  bar: { damping: 18, stiffness: 80, mass: 1 },
  /** Map/icon markers: { damping: 12, stiffness: 150 } */
  marker: { damping: 12, stiffness: 150, mass: 1 },
  /** Label pills: { damping: 15, stiffness: 120 } */
  pill: { damping: 15, stiffness: 120, mass: 1 },
  /** Heavy slam — stamp/impact effects with weight */
  heavy: { damping: 8, stiffness: 200, mass: 2 },
  /** Elastic snap — tight bounce for playful impacts */
  elastic: { damping: 5, stiffness: 300, mass: 0.5 },
  /** Scene transitions — quick crossfade so scenes stay visible longer */
  transition: { damping: 30, stiffness: 300, mass: 0.5 },
} as const;

export type SpringPreset = keyof typeof SPRINGS;

/**
 * Measure the duration (in frames) of a named spring preset.
 * Useful for calculating how long an entrance animation takes.
 */
export function measureSpringDuration(
  preset: SpringPreset,
  opts?: { fps?: number; threshold?: number },
): number {
  return measureSpring({
    fps: opts?.fps ?? FPS,
    config: SPRINGS[preset],
    threshold: opts?.threshold,
  });
}
