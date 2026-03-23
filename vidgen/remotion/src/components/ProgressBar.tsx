/**
 * ProgressBar — thin animated bar showing video progress.
 * Common TikTok engagement pattern that increases watch time.
 * Renders at the bottom safe zone.
 */
import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate } from 'remotion';
import { WIDTH } from '../lib/zones';

interface ProgressBarProps {
  /** Bar color (default accent gold) */
  color?: string;
  /** Height in pixels (default 3) */
  height?: number;
  /** Y position from top (default 1540 — just below safe zone) */
  y?: number;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  color = '#FFD700',
  height = 3,
  y = 1540,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const progress = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // Glow pulse
  const glow = Math.sin(frame * 0.1) * 0.3 + 0.7;

  return (
    <div style={{
      position: 'absolute',
      top: y,
      left: 0,
      width: WIDTH,
      height,
      backgroundColor: `${color}15`,
      overflow: 'hidden',
      zIndex: 50,
    }}>
      <div style={{
        width: `${progress * 100}%`,
        height: '100%',
        backgroundColor: color,
        boxShadow: `0 0 ${8 * glow}px ${color}88, 0 0 ${16 * glow}px ${color}44`,
        borderRadius: `0 ${height / 2}px ${height / 2}px 0`,
        transition: 'none',
      }} />
    </div>
  );
};
