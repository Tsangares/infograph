/**
 * ParallaxLayer — wraps content with a parallax effect relative to scene progress.
 * Background layers use depth < 1 (move less), foreground layers use depth > 1.
 */
import React from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate } from 'remotion';

interface ParallaxLayerProps {
  /** Parallax depth: 0.3 = bg (slow), 1.0 = normal, 1.5 = fg (fast) */
  depth?: number;
  /** Direction of drift: 'up' | 'left' | 'diagonal' */
  direction?: 'up' | 'left' | 'diagonal';
  /** Max pixel travel over the scene */
  distance?: number;
  children: React.ReactNode;
}

export const ParallaxLayer: React.FC<ParallaxLayerProps> = ({
  depth = 0.3,
  direction = 'up',
  distance = 30,
  children,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const progress = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateRight: 'clamp',
  });

  const travel = progress * distance * depth;

  let tx = 0;
  let ty = 0;
  switch (direction) {
    case 'up':
      ty = -travel;
      break;
    case 'left':
      tx = -travel;
      break;
    case 'diagonal':
      tx = -travel * 0.5;
      ty = -travel * 0.7;
      break;
  }

  return (
    <AbsoluteFill style={{ transform: `translate(${tx}px, ${ty}px)` }}>
      {children}
    </AbsoluteFill>
  );
};
