/**
 * StackedAccumulation — icons drop and pile up with physics bounce.
 *
 * Skulls piling, coins stacking, bodies accumulating.
 * Each icon drops from above with bouncy spring and stacks in a pyramid layout.
 */
import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';
import { zoneStyle, type ZoneName } from '../lib/zones';
import { TKK_WHITE, TKK_GOLD } from '../lib/colors';
import { FONTS } from '../lib/fonts';
import { FONT_SIZE } from '../lib/typography';
import { useSceneProgress } from '../lib/useSceneProgress';
import { SPRINGS } from '../lib/springs';
import { SVG_LIBRARY } from '../lib/svgLibrary';

interface StackedAccumulationProps {
  icon: string;
  count: number;
  label?: string;
  displayValue?: string;
  color?: string;
  zone?: ZoneName;
}

// Deterministic pyramid layout positions
function computePositions(count: number, itemSize: number): { x: number; y: number }[] {
  const positions: { x: number; y: number }[] = [];
  let remaining = count;
  let row = 0;
  const spacing = itemSize * 1.05;

  while (remaining > 0) {
    // Bottom rows are wider
    const maxPerRow = Math.min(remaining, 6 - Math.min(row, 3));
    const rowCount = Math.min(remaining, maxPerRow);
    const rowWidth = (rowCount - 1) * spacing;

    for (let col = 0; col < rowCount; col++) {
      positions.push({
        x: -rowWidth / 2 + col * spacing,
        y: -row * spacing,
      });
    }

    remaining -= rowCount;
    row++;
  }

  return positions;
}

export const StackedAccumulation: React.FC<StackedAccumulationProps> = ({
  icon,
  count,
  label,
  displayValue,
  color = TKK_GOLD,
  zone = 'MID',
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const { exit } = useSceneProgress();

  const IconComponent = SVG_LIBRARY[icon];
  if (!IconComponent) return null;

  const clampedCount = Math.min(count, 30);
  const itemSize = clampedCount <= 4 ? 120 : clampedCount <= 8 ? 90 : clampedCount <= 15 ? 70 : 55;
  const positions = computePositions(clampedCount, itemSize);

  // Each item drops at staggered intervals across ~60% of scene
  const dropWindow = Math.round(durationInFrames * 0.6);
  const staggerDelay = dropWindow / clampedCount;

  // Exit
  const exitOpacity = interpolate(exit, [0, 1], [1, 0], { extrapolateRight: 'clamp' });
  const exitScale = interpolate(exit, [0, 1], [1, 0.85], { extrapolateRight: 'clamp' });

  // Entrance fade
  const enterOpacity = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <div style={{
      ...zoneStyle(zone),
      flexDirection: 'column',
      alignItems: 'center',
      gap: 16,
      opacity: enterOpacity * exitOpacity,
      transform: `scale(${exitScale})`,
    }}>
      {/* Pile container */}
      <div style={{
        position: 'relative',
        width: 700,
        height: 200,
        display: 'flex',
        alignItems: 'flex-end',
        justifyContent: 'center',
        overflow: 'hidden',
      }}>
        {positions.map((pos, i) => {
          const itemStart = Math.round(i * staggerDelay);
          const itemFrame = Math.max(0, frame - itemStart);

          const dropProgress = spring({ frame: itemFrame, fps, config: SPRINGS.bouncy });
          const itemOpacity = interpolate(itemFrame, [0, 4], [0, 1], { extrapolateRight: 'clamp' });

          // Drop from above
          const dropY = interpolate(dropProgress, [0, 1], [-200, 0]);

          // Slight wobble once landed
          const isLanded = itemFrame > 15;
          const wobble = isLanded ? Math.sin(frame * 0.06 + i * 1.3) * 2 : 0;

          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                left: `calc(50% + ${pos.x}px)`,
                bottom: pos.y + 20,
                transform: `translate(-50%, 0) translateY(${dropY + wobble}px)`,
                opacity: itemOpacity,
              }}
            >
              <IconComponent color={color} size={itemSize} />
            </div>
          );
        })}
      </div>

      {/* Display value overlay */}
      {displayValue && (
        <div style={{
          fontFamily: FONTS.mono,
          fontSize: FONT_SIZE.headline,
          fontWeight: 'bold',
          color,
          textAlign: 'center',
          textShadow: `0 0 20px ${color}44`,
          opacity: interpolate(frame, [dropWindow, dropWindow + 15], [0, 1], { extrapolateRight: 'clamp' }),
        }}>
          {displayValue}
        </div>
      )}

      {label && (
        <div style={{
          fontFamily: FONTS.body,
          fontSize: FONT_SIZE.caption,
          color: TKK_WHITE + 'CC',
          textAlign: 'center',
          opacity: interpolate(frame, [dropWindow, dropWindow + 15], [0, 1], { extrapolateRight: 'clamp' }),
        }}>
          {label}
        </div>
      )}
    </div>
  );
};
