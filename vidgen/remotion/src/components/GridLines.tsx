/**
 * GridLines — subtle animated background grid with pulse and scan line.
 */
import React from 'react';
import { AbsoluteFill, useCurrentFrame } from 'remotion';
import { WIDTH, HEIGHT } from '../lib/zones';
import { TKK_GRID } from '../lib/colors';

export const GridLines: React.FC<{ opacity?: number }> = ({ opacity = 0.04 }) => {
  const frame = useCurrentFrame();
  const hLines = 13;
  const vLines = 7;

  // Gentle opacity pulse
  const pulseOpacity = opacity + Math.sin(frame * 0.05) * 0.015;

  // Scan line sweeps top to bottom
  const scanY = (frame * 2.5) % HEIGHT;

  return (
    <AbsoluteFill style={{ pointerEvents: 'none' }}>
      <svg width={WIDTH} height={HEIGHT} style={{ opacity: pulseOpacity }}>
        {Array.from({ length: hLines }, (_, i) => {
          const y = (i / (hLines - 1)) * HEIGHT;
          return <line key={`h${i}`} x1={0} y1={y} x2={WIDTH} y2={y} stroke={TKK_GRID} strokeWidth={1} />;
        })}
        {Array.from({ length: vLines }, (_, j) => {
          const x = (j / (vLines - 1)) * WIDTH;
          return <line key={`v${j}`} x1={x} y1={0} x2={x} y2={HEIGHT} stroke={TKK_GRID} strokeWidth={1} />;
        })}
        {/* Scan line */}
        <line
          x1={0} y1={scanY} x2={WIDTH} y2={scanY}
          stroke={TKK_GRID} strokeWidth={2} opacity={0.15}
        />
      </svg>
    </AbsoluteFill>
  );
};
