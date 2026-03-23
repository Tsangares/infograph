/**
 * EmphasisLine — animated underline/highlight that draws across.
 * Use under key text or stats for visual emphasis.
 */
import React from 'react';
import { useCurrentFrame, useVideoConfig, spring } from 'remotion';
import { zoneStyle, type ZoneName } from '../lib/zones';
import { SPRINGS } from '../lib/springs';

const SAFE_LEFT = 120;
const SAFE_W = 820;

interface EmphasisLineProps {
  color?: string;
  zone?: ZoneName;
  /** Thickness of the line (default 4) */
  thickness?: number;
  /** Width as fraction of safe area (default 0.6) */
  width?: number;
  /** Delay in frames before drawing starts */
  delay?: number;
  /** Style: 'underline' draws left-to-right, 'strike' draws center-out */
  style?: 'underline' | 'strike';
}

export const EmphasisLine: React.FC<EmphasisLineProps> = ({
  color = '#FFD700',
  zone = 'MID',
  thickness = 4,
  width = 0.6,
  delay = 0,
  style = 'underline',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const adjusted = Math.max(0, frame - delay);
  const progress = spring({
    frame: adjusted,
    fps,
    config: SPRINGS.snappy,
  });

  const lineWidth = SAFE_W * width;

  // Glow after draw
  const glowOpacity = adjusted > 15 ? Math.sin(adjusted * 0.06) * 0.3 + 0.5 : 0;

  if (style === 'strike') {
    // Center-out: grows from center in both directions
    const currentWidth = lineWidth * progress;
    return (
      <div style={{
        ...zoneStyle(zone),
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <div style={{
          width: currentWidth,
          height: thickness,
          backgroundColor: color,
          borderRadius: thickness / 2,
          boxShadow: `0 0 ${12 * glowOpacity}px ${color}66`,
          marginTop: 20,
        }} />
      </div>
    );
  }

  // Underline: draws left to right
  const currentWidth = lineWidth * progress;
  return (
    <div style={{
      ...zoneStyle(zone),
      alignItems: 'center',
      justifyContent: 'flex-start',
      paddingLeft: (SAFE_W - lineWidth) / 2 + SAFE_LEFT,
    }}>
      <div style={{
        width: currentWidth,
        height: thickness,
        backgroundColor: color,
        borderRadius: thickness / 2,
        boxShadow: `0 0 ${12 * glowOpacity}px ${color}66`,
        marginTop: 20,
      }} />
    </div>
  );
};
