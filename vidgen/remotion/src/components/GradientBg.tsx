/**
 * GradientBg — animated background with drifting color orbs, pulsating sizes,
 * animated gradient base, and rotating light sweep for cinematic depth.
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

  // Animated base gradient — shifts hue subtly
  const gradAngle = 135 + Math.sin(frame * 0.006) * 15;
  const baseBg = `linear-gradient(${gradAngle}deg, ${color} 0%, ${color} 60%, ${secondaryColor}08 100%)`;

  // Pulsating orb sizes
  const pulse1 = 500 + Math.sin(frame * 0.025) * 40;
  const pulse2 = 450 + Math.sin(frame * 0.03 + 1) * 35;
  const pulse3 = 400 + Math.sin(frame * 0.02 + 2) * 50;
  const pulse4 = 350 + Math.sin(frame * 0.035 + 3) * 30;

  // Orb positions — different frequencies for organic motion
  const orb1X = WIDTH * 0.25 + Math.sin(frame * 0.012) * 80;
  const orb1Y = HEIGHT * 0.2 + Math.cos(frame * 0.008) * 60;
  const orb2X = WIDTH * 0.7 + Math.sin(frame * 0.015 + 2) * 70;
  const orb2Y = HEIGHT * 0.6 + Math.cos(frame * 0.01 + 1) * 90;
  const orb3X = WIDTH * 0.4 + Math.sin(frame * 0.009 + 4) * 100;
  const orb3Y = HEIGHT * 0.85 + Math.cos(frame * 0.013 + 3) * 50;
  // New 4th orb — wanders the upper-right
  const orb4X = WIDTH * 0.8 + Math.sin(frame * 0.011 + 5) * 60;
  const orb4Y = HEIGHT * 0.15 + Math.cos(frame * 0.014 + 2) * 70;

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

  // Rotating light sweep — dim conic gradient that rotates slowly
  const sweepAngle = frame * 0.4; // ~12° per second at 30fps
  const sweepOpacity = 0.03 + Math.sin(frame * 0.02) * 0.01;

  return (
    <AbsoluteFill>
      {/* Animated base gradient */}
      <div style={{ width: WIDTH, height: HEIGHT, background: baseBg }} />

      {/* Color orbs with pulsating sizes */}
      <div style={orbStyle(orb1X, orb1Y, accentColor, pulse1)} />
      <div style={orbStyle(orb2X, orb2Y, secondaryColor, pulse2)} />
      <div style={orbStyle(orb3X, orb3Y, accentColor, pulse3)} />
      <div style={orbStyle(orb4X, orb4Y, secondaryColor, pulse4)} />

      {/* Rotating light sweep for subtle cinematic motion */}
      <div style={{
        position: 'absolute',
        width: WIDTH,
        height: HEIGHT,
        background: `conic-gradient(from ${sweepAngle}deg at 50% 50%, transparent 0deg, ${accentColor}06 30deg, transparent 60deg, transparent 360deg)`,
        opacity: sweepOpacity,
        pointerEvents: 'none',
      }} />
    </AbsoluteFill>
  );
};
