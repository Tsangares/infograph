/**
 * AnimatedBarRace — racing/sorting bar chart with spring-driven growth.
 * Bars grow to their values and can re-sort by size for dramatic effect.
 */
import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';
import { zoneStyle, type ZoneName } from '../lib/zones';
import { SPRINGS } from '../lib/springs';
import { FONTS } from '../lib/fonts';

interface BarItem {
  label: string;
  value: number;
  color: string;
}

interface AnimatedBarRaceProps {
  bars: BarItem[];
  zone?: ZoneName;
  /** Sort bars by value after growth (default true) */
  sortAfterGrow?: boolean;
  /** Show value numbers on bars */
  showValues?: boolean;
  /** Unit suffix for values (e.g. "M", "%") */
  unit?: string;
  /** Maximum bar width in pixels */
  maxBarWidth?: number;
}

export const AnimatedBarRace: React.FC<AnimatedBarRaceProps> = ({
  bars,
  zone = 'MID',
  sortAfterGrow = true,
  showValues = true,
  unit = '',
  maxBarWidth = 600,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const maxValue = Math.max(...bars.map(b => b.value));
  const growPhase = 0.5; // first half = grow
  const growFrames = Math.round(durationInFrames * growPhase);

  // Entry
  const entryOpacity = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: 'clamp' });

  // Exit
  const exitStart = durationInFrames - 12;
  const exitOpacity = interpolate(frame, [exitStart, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Compute each bar's animated width
  const barHeight = Math.min(50, Math.max(30, 500 / bars.length));
  const gap = 10;

  const animatedBars = bars.map((bar, i) => {
    const staggerDelay = i * 5;
    const barFrame = Math.max(0, frame - staggerDelay);
    const growProgress = spring({
      frame: barFrame,
      fps,
      config: SPRINGS.bar,
      durationInFrames: growFrames,
    });
    const width = (bar.value / maxValue) * maxBarWidth * growProgress;
    const displayValue = Math.round(bar.value * growProgress);

    return { ...bar, width, displayValue, originalIndex: i };
  });

  // Sort phase: after bars finish growing, sort by value
  let sortedBars = animatedBars;
  if (sortAfterGrow) {
    const sortFrame = Math.max(0, frame - growFrames);
    const sortProgress = spring({
      frame: sortFrame,
      fps,
      config: SPRINGS.smooth,
    });

    // Create sorted order
    const sorted = [...animatedBars].sort((a, b) => b.value - a.value);
    const sortedIndices = sorted.map(b => b.originalIndex);

    // Interpolate positions between original and sorted
    sortedBars = animatedBars.map((bar) => {
      const originalPos = bar.originalIndex;
      const sortedPos = sortedIndices.indexOf(bar.originalIndex);
      const currentPos = originalPos + (sortedPos - originalPos) * sortProgress;
      return { ...bar, yPos: currentPos * (barHeight + gap) };
    });
  } else {
    sortedBars = animatedBars.map((bar) => ({
      ...bar,
      yPos: bar.originalIndex * (barHeight + gap),
    }));
  }

  const totalHeight = bars.length * (barHeight + gap);

  return (
    <div style={{
      ...zoneStyle(zone),
      overflow: 'visible',
      flexDirection: 'column',
      alignItems: 'flex-start',
      opacity: entryOpacity * exitOpacity,
      paddingLeft: 140,
    }}>
      <div style={{
        position: 'relative',
        width: maxBarWidth + 200,
        height: totalHeight,
      }}>
        {sortedBars.map((bar, i) => {
          const shimmer = Math.sin(frame * 0.06 + i) * 0.5 + 0.5;

          return (
            <div
              key={bar.originalIndex}
              style={{
                position: 'absolute',
                top: (bar as any).yPos ?? i * (barHeight + gap),
                left: 0,
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                transition: 'none',
              }}
            >
              {/* Label */}
              <div style={{
                width: 120,
                textAlign: 'right',
                fontFamily: FONTS.body,
                fontSize: 22,
                color: '#EAEAF0CC',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
              }}>
                {bar.label}
              </div>

              {/* Bar */}
              <div style={{
                width: bar.width,
                height: barHeight,
                backgroundColor: bar.color,
                borderRadius: `${barHeight / 2}px`,
                boxShadow: `0 0 ${8 * shimmer}px ${bar.color}44`,
                minWidth: 4,
              }} />

              {/* Value */}
              {showValues && bar.displayValue > 0 && (
                <div style={{
                  fontFamily: FONTS.headline,
                  fontSize: 26,
                  color: bar.color,
                  fontWeight: 'bold',
                  opacity: interpolate(bar.width, [0, 20], [0, 1], { extrapolateRight: 'clamp' }),
                }}>
                  {bar.displayValue.toLocaleString()}{unit}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
