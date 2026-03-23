/**
 * SlowZoom — subtle camera-like zoom during scene hold.
 * Wraps children with a slow scale animation to prevent static frames.
 */
import React from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate } from 'remotion';

interface SlowZoomProps {
  /** Starting scale (default 1.0) */
  from?: number;
  /** Ending scale (default 1.08) */
  to?: number;
  children: React.ReactNode;
}

export const SlowZoom: React.FC<SlowZoomProps> = ({
  from = 1.0,
  to = 1.08,
  children,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const scale = interpolate(frame, [0, durationInFrames], [from, to], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ transform: `scale(${scale})`, transformOrigin: 'center center' }}>
      {children}
    </AbsoluteFill>
  );
};
