/**
 * SvgPathDraw — animates SVG paths being "drawn" with stroke-dasharray/offset.
 * Creates the effect of lines being drawn in real-time.
 *
 * Usage in manifests:
 *   { type: "path_draw", paths: [...], viewBox: "0 0 400 400", zone: "MID" }
 */
import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';
import { zoneStyle, type ZoneName } from '../lib/zones';
import { SPRINGS } from '../lib/springs';

interface PathDef {
  d: string;
  stroke?: string;
  strokeWidth?: number;
  fill?: string;
  /** Delay before this path starts drawing (0-1, fraction of drawDuration) */
  delay?: number;
}

interface SvgPathDrawProps {
  paths: PathDef[];
  viewBox?: string;
  size?: number;
  zone?: ZoneName;
  /** Fraction of scene duration used for drawing (default 0.6) */
  drawDuration?: number;
  /** Color applied to all paths if individual stroke not set */
  color?: string;
}

export const SvgPathDraw: React.FC<SvgPathDrawProps> = ({
  paths,
  viewBox = '0 0 400 400',
  size = 300,
  zone = 'MID',
  drawDuration = 0.6,
  color = '#FFD700',
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const drawFrames = Math.round(durationInFrames * drawDuration);

  // Entry fade
  const entryOpacity = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: 'clamp' });

  // Exit fade
  const exitStart = durationInFrames - 15;
  const exitOpacity = interpolate(frame, [exitStart, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Hold glow
  const holdGlow = frame > drawFrames
    ? 0.3 + Math.sin(frame * 0.06) * 0.15
    : 0;

  return (
    <div style={{
      ...zoneStyle(zone),
      flexDirection: 'column',
      alignItems: 'center',
      opacity: entryOpacity * exitOpacity,
    }}>
      <svg
        viewBox={viewBox}
        width={size}
        height={size}
        style={{
          filter: holdGlow > 0 ? `drop-shadow(0 0 ${12 * holdGlow}px ${color}66)` : undefined,
        }}
      >
        {paths.map((path, i) => {
          // Stagger each path's draw start
          const pathDelay = (path.delay ?? i * 0.15) * drawFrames;
          const pathFrame = Math.max(0, frame - pathDelay);

          // Use spring for organic draw feel
          const drawProgress = spring({
            frame: pathFrame,
            fps,
            config: SPRINGS.smooth,
            durationInFrames: drawFrames - pathDelay,
          });

          // Approximate path length (use a large number — dasharray handles it)
          const pathLength = 2000;
          const dashOffset = pathLength * (1 - drawProgress);

          return (
            <path
              key={i}
              d={path.d}
              stroke={path.stroke ?? color}
              strokeWidth={path.strokeWidth ?? 3}
              fill={path.fill ?? 'none'}
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeDasharray={pathLength}
              strokeDashoffset={dashOffset}
              style={{
                opacity: interpolate(pathFrame, [0, 5], [0, 1], { extrapolateRight: 'clamp' }),
              }}
            />
          );
        })}
      </svg>
    </div>
  );
};
