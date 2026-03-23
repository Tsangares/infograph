/**
 * SvgMorph — animates morphing between two SVG shapes.
 * Interpolates path data point-by-point for smooth shape transitions.
 * Both paths must have the same number of commands for smooth morphing.
 * If they don't match, falls back to crossfade.
 */
import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';
import { zoneStyle, type ZoneName } from '../lib/zones';
import { SPRINGS } from '../lib/springs';

interface SvgMorphProps {
  /** SVG path "d" attribute for starting shape */
  fromPath: string;
  /** SVG path "d" attribute for ending shape */
  toPath: string;
  viewBox?: string;
  size?: number;
  zone?: ZoneName;
  /** Fraction of scene when morph starts (default 0.3) */
  morphAt?: number;
  /** Fraction of scene for morph duration (default 0.3) */
  morphDuration?: number;
  fromColor?: string;
  toColor?: string;
  strokeWidth?: number;
  /** Whether to fill or just stroke */
  filled?: boolean;
}

/**
 * Extract numeric values from an SVG path string.
 * Keeps commands as-is and interpolates only the numbers.
 */
function extractNumbers(pathD: string): { template: string[]; numbers: number[] } {
  const template: string[] = [];
  const numbers: number[] = [];
  // Split on numbers (including negatives and decimals)
  const parts = pathD.split(/(-?\d+\.?\d*)/g);
  for (const part of parts) {
    const num = parseFloat(part);
    if (!isNaN(num) && part.trim() !== '') {
      template.push('\0'); // placeholder
      numbers.push(num);
    } else {
      template.push(part);
    }
  }
  return { template, numbers };
}

function interpolatePath(fromD: string, toD: string, progress: number): string {
  const from = extractNumbers(fromD);
  const to = extractNumbers(toD);

  // If different number of values, can't interpolate — use "to" when past halfway
  if (from.numbers.length !== to.numbers.length) {
    return progress < 0.5 ? fromD : toD;
  }

  const interpolatedNumbers = from.numbers.map((fromN, i) =>
    fromN + (to.numbers[i] - fromN) * progress
  );

  let result = '';
  let numIdx = 0;
  for (const part of from.template) {
    if (part === '\0') {
      result += interpolatedNumbers[numIdx].toFixed(2);
      numIdx++;
    } else {
      result += part;
    }
  }
  return result;
}

function interpolateColor(from: string, to: string, progress: number): string {
  // Simple hex interpolation
  const parseHex = (hex: string) => {
    const h = hex.replace('#', '');
    return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
  };
  try {
    const [r1, g1, b1] = parseHex(from);
    const [r2, g2, b2] = parseHex(to);
    const r = Math.round(r1 + (r2 - r1) * progress);
    const g = Math.round(g1 + (g2 - g1) * progress);
    const b = Math.round(b1 + (b2 - b1) * progress);
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
  } catch {
    return progress < 0.5 ? from : to;
  }
}

export const SvgMorph: React.FC<SvgMorphProps> = ({
  fromPath,
  toPath,
  viewBox = '0 0 200 200',
  size = 250,
  zone = 'MID',
  morphAt = 0.3,
  morphDuration = 0.3,
  fromColor = '#FFD700',
  toColor = '#EF4444',
  strokeWidth = 3,
  filled = false,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const morphStartFrame = Math.round(durationInFrames * morphAt);
  const morphFrames = Math.round(durationInFrames * morphDuration);

  // Entry animation
  const entryProgress = spring({ frame, fps, config: SPRINGS.dramatic });
  const entryScale = interpolate(entryProgress, [0, 1], [0.5, 1]);
  const entryOpacity = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: 'clamp' });

  // Morph progress with spring
  const morphFrame = Math.max(0, frame - morphStartFrame);
  const morphProgress = morphFrame > 0
    ? spring({ frame: morphFrame, fps, config: SPRINGS.smooth, durationInFrames: morphFrames })
    : 0;

  // Interpolate path and color
  const currentPath = interpolatePath(fromPath, toPath, morphProgress);
  const currentColor = interpolateColor(fromColor, toColor, morphProgress);

  // Hold: subtle breathing
  const breathe = 1 + Math.sin(frame * 0.04) * 0.01;

  // Glow effect during morph
  const morphGlow = morphProgress > 0 && morphProgress < 1
    ? `drop-shadow(0 0 ${15 * Math.sin(morphFrame * 0.2)}px ${currentColor}66)`
    : `drop-shadow(0 0 8px ${currentColor}22)`;

  // Exit
  const exitStart = durationInFrames - 12;
  const exitOpacity = interpolate(frame, [exitStart, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div style={{
      ...zoneStyle(zone),
      flexDirection: 'column',
      alignItems: 'center',
      opacity: entryOpacity * exitOpacity,
      transform: `scale(${entryScale * breathe})`,
    }}>
      <svg
        viewBox={viewBox}
        width={size}
        height={size}
        style={{ filter: morphGlow, overflow: 'visible' }}
      >
        <path
          d={currentPath}
          stroke={currentColor}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeLinejoin="round"
          fill={filled ? currentColor : 'none'}
          fillOpacity={filled ? 0.15 : 0}
        />
      </svg>
    </div>
  );
};
