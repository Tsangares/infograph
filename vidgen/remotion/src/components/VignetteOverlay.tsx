/**
 * VignetteOverlay — darkens edges for cinematic depth and focus.
 * Draws the eye to the center of the frame.
 */
import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate } from 'remotion';
import { WIDTH, HEIGHT } from '../lib/zones';

interface VignetteOverlayProps {
  /** How dark the edges get (0-1, default 0.4) */
  intensity?: number;
  /** How far in the vignette reaches (0-1, default 0.3) */
  spread?: number;
  /** Animate: pulse the vignette slightly for breathing feel */
  animate?: boolean;
}

export const VignetteOverlay: React.FC<VignetteOverlayProps> = ({
  intensity = 0.4,
  spread = 0.3,
  animate = true,
}) => {
  const frame = useCurrentFrame();

  // Subtle breathing animation on vignette
  const breathe = animate
    ? intensity + Math.sin(frame * 0.03) * 0.05
    : intensity;

  return (
    <AbsoluteFill style={{ pointerEvents: 'none' }}>
      <div style={{
        width: WIDTH,
        height: HEIGHT,
        background: `radial-gradient(ellipse at center, transparent ${(1 - spread) * 100}%, rgba(0,0,0,${breathe}) 100%)`,
      }} />
    </AbsoluteFill>
  );
};
