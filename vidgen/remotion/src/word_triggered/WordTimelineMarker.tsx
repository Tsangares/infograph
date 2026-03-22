/**
 * WordTimelineMarker — a single timeline marker entering via word trigger.
 * Renders ONE marker dot + year + label.
 */
import React from 'react';
import { useCurrentFrame, spring, interpolate, useVideoConfig } from 'remotion';
import { zoneStyle, SAFE } from '../lib/zones';
import { TKK_GOLD, TKK_WHITE } from '../lib/colors';
import { FONTS } from '../lib/fonts';
import { FONT_SIZE } from '../lib/typography';

interface WordTimelineMarkerProps {
  year: string;
  label: string;
  color?: string;
  index?: number;
  totalMarkers?: number;
}

export const WordTimelineMarker: React.FC<WordTimelineMarkerProps> = ({
  year,
  label,
  color = TKK_GOLD,
  index = 0,
  totalMarkers = 4,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const scale = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 120 },
  });

  const opacity = interpolate(frame, [0, 8], [0, 1], {
    extrapolateRight: 'clamp',
  });

  const holdProgress = durationInFrames > 0 ? frame / durationInFrames : 0;
  const pulse = 1 + Math.sin(holdProgress * Math.PI * 3 + index * 1.2) * 0.06;

  const exitStart = Math.round(durationInFrames * 0.85);
  const exitOpacity = interpolate(frame, [exitStart, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const pct = totalMarkers === 1 ? 0.5 : index / (totalMarkers - 1);
  const xOffset = (pct - 0.5) * (SAFE.width - 100);

  return (
    <div style={{
      ...zoneStyle('MID'),
      flexDirection: 'column',
      alignItems: 'center',
      opacity: opacity * exitOpacity,
      transform: `translateX(${xOffset}px) scale(${scale})`,
    }}>
      <div style={{
        width: 18,
        height: 18,
        borderRadius: '50%',
        background: color,
        border: `2px solid ${TKK_WHITE}`,
        transform: `scale(${pulse})`,
        marginBottom: 8,
      }} />
      <div style={{
        fontFamily: FONTS.mono,
        fontSize: FONT_SIZE.dataLabel,
        fontWeight: 'bold',
        color,
        whiteSpace: 'nowrap',
      }}>
        {year}
      </div>
      <div style={{
        fontFamily: FONTS.body,
        fontSize: FONT_SIZE.dataValue,
        color: TKK_WHITE + 'BB',
        textAlign: 'center',
        maxWidth: 200,
        lineHeight: 1.2,
      }}>
        {label}
      </div>
    </div>
  );
};
