/**
 * GradientBg — animated background with slowly drifting color orbs.
 * Uses manifest accent/secondary colors at low opacity for ambient motion.
 */
import React from 'react';
import { AbsoluteFill, useCurrentFrame } from 'remotion';
import { TKK_BG } from '../lib/colors';
import { WIDTH, HEIGHT } from '../lib/zones';

interface GradientBgProps {
  color?: string;
  accentColor?: string;
  secondaryColor?: string;
}

export const GradientBg: React.FC<GradientBgProps> = ({
  color = TKK_BG,
  accentColor = '#FFD700',
  secondaryColor = '#3B82F6',
}) => {
  const frame = useCurrentFrame();

  // Slow drifting orbs — different frequencies create organic motion
  const orb1X = WIDTH * 0.25 + Math.sin(frame * 0.012) * 80;
  const orb1Y = HEIGHT * 0.2 + Math.cos(frame * 0.008) * 60;
  const orb2X = WIDTH * 0.7 + Math.sin(frame * 0.015 + 2) * 70;
  const orb2Y = HEIGHT * 0.6 + Math.cos(frame * 0.01 + 1) * 90;
  const orb3X = WIDTH * 0.4 + Math.sin(frame * 0.009 + 4) * 100;
  const orb3Y = HEIGHT * 0.85 + Math.cos(frame * 0.013 + 3) * 50;

  const orbStyle = (x: number, y: number, orbColor: string, size: number): React.CSSProperties => ({
    position: 'absolute',
    left: x - size / 2,
    top: y - size / 2,
    width: size,
    height: size,
    borderRadius: '50%',
    background: `radial-gradient(circle, ${orbColor}18 0%, transparent 70%)`,
    filter: 'blur(60px)',
    pointerEvents: 'none',
  });

  return (
    <AbsoluteFill>
      <div style={{ width: WIDTH, height: HEIGHT, background: color }} />
      <div style={orbStyle(orb1X, orb1Y, accentColor, 500)} />
      <div style={orbStyle(orb2X, orb2Y, secondaryColor, 450)} />
      <div style={orbStyle(orb3X, orb3Y, accentColor, 400)} />
    </AbsoluteFill>
  );
};
