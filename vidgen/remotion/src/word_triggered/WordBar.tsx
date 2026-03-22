/**
 * WordBar — a single bar chart bar that enters via word trigger.
 * Renders ONE bar. Multiple are composed by the scene renderer,
 * each in its own <Sequence> timed to its anchor word.
 */
import React from 'react';
import { useCurrentFrame, spring, interpolate, useVideoConfig } from 'remotion';
import { zoneStyle, SAFE } from '../lib/zones';
import { TKK_GOLD, TKK_WHITE } from '../lib/colors';
import { FONTS } from '../lib/fonts';
import { FONT_SIZE } from '../lib/typography';
import { SPRINGS } from '../lib/springs';

interface WordBarProps {
  label: string;
  value: number;
  maxValue?: number;
  color?: string;
  index?: number;
  totalBars?: number;
}

export const WordBar: React.FC<WordBarProps> = ({
  label,
  value,
  maxValue = 4000,
  color = TKK_GOLD,
  index = 0,
  totalBars = 3,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const barHeight = 44;
  const labelWidth = 260;
  const barMaxWidth = SAFE.width - labelWidth - 60;

  const width = spring({ frame, fps, config: SPRINGS.bar });

  const labelOpacity = interpolate(frame, [4, 12], [0, 1], {
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  });

  const holdProgress = durationInFrames > 0 ? frame / durationInFrames : 0;
  const shimmer = 1 + Math.sin(holdProgress * Math.PI * 2 + index * 0.8) * 0.015;

  const exitStart = Math.round(durationInFrames * 0.85);
  const exitOpacity = interpolate(frame, [exitStart, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const barWidth = (value / maxValue) * barMaxWidth;
  const barSpacing = barHeight + 16;
  const totalHeight = totalBars * barSpacing;
  const yOffset = index * barSpacing - totalHeight / 2 + barHeight / 2;

  return (
    <div style={{
      ...zoneStyle('MID'),
      flexDirection: 'row',
      alignItems: 'center',
      gap: 12,
      opacity: exitOpacity,
      transform: `translateY(${yOffset}px)`,
    }}>
      <div style={{
        fontFamily: FONTS.body,
        fontSize: FONT_SIZE.dataValue,
        color: TKK_WHITE + 'CC',
        width: labelWidth,
        textAlign: 'right',
        whiteSpace: 'nowrap',
        opacity: labelOpacity,
      }}>
        {label}
      </div>
      <div style={{
        height: barHeight,
        width: barWidth * width * shimmer,
        background: color,
        borderRadius: barHeight / 2,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'flex-end',
        paddingRight: 12,
      }}>
        <span style={{
          fontFamily: FONTS.mono,
          fontSize: FONT_SIZE.dataValue,
          color: '#000',
          fontWeight: 'bold',
          opacity: labelOpacity,
        }}>
          {value.toLocaleString()}
        </span>
      </div>
    </div>
  );
};
