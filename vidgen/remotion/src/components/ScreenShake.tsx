/**
 * ScreenShake — wraps content with a screen-shake effect triggered at a specific frame.
 * Use on impact moments: counter reaching target, stamp reveals, domino chains.
 */
import React from 'react';
import { AbsoluteFill, useCurrentFrame } from 'remotion';

interface ScreenShakeProps {
  /** Frame at which the shake starts (0 = scene start) */
  triggerFrame?: number;
  /** Duration of shake in frames (default 15 = 0.5s) */
  duration?: number;
  /** Maximum pixel displacement (default 12) */
  intensity?: number;
  children: React.ReactNode;
}

export const ScreenShake: React.FC<ScreenShakeProps> = ({
  triggerFrame = 0,
  duration = 15,
  intensity = 12,
  children,
}) => {
  const frame = useCurrentFrame();

  let tx = 0;
  let ty = 0;

  const shakeFrame = frame - triggerFrame;
  if (shakeFrame >= 0 && shakeFrame < duration) {
    const decay = Math.max(0, 1 - shakeFrame / duration);
    // Use different frequencies for x/y to avoid repetitive patterns
    tx = Math.sin(shakeFrame * 2.5 + 0.3) * intensity * decay;
    ty = Math.cos(shakeFrame * 3.1 + 0.7) * intensity * 0.6 * decay;
  }

  return (
    <AbsoluteFill style={{ transform: `translate(${tx}px, ${ty}px)` }}>
      {children}
    </AbsoluteFill>
  );
};
