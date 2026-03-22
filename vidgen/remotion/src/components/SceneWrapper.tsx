import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, useVideoConfig } from 'remotion';

const CROSSFADE = 10; // frames (~0.33s at 30fps)

interface SceneWrapperProps {
  children: React.ReactNode;
  isFirst?: boolean;
  isLast?: boolean;
}

/**
 * Wraps a scene with crossfade enter/exit opacity.
 * First scene skips the enter fade, last scene skips the exit fade.
 */
export const SceneWrapper: React.FC<SceneWrapperProps> = ({
  children,
  isFirst = false,
  isLast = false,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const enterOpacity = isFirst
    ? 1
    : interpolate(frame, [0, CROSSFADE], [0, 1], { extrapolateRight: 'clamp' });

  const exitOpacity = isLast
    ? 1
    : interpolate(
        frame,
        [durationInFrames - CROSSFADE, durationInFrames],
        [1, 0],
        { extrapolateLeft: 'clamp' },
      );

  return (
    <AbsoluteFill style={{ opacity: Math.min(enterOpacity, exitOpacity) }}>
      {children}
    </AbsoluteFill>
  );
};

export { CROSSFADE };
