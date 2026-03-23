/**
 * CameraCut — simulates camera movements (zoom punch, pull-back, pan).
 * Wrap around scene content to add cinematographic motion.
 *
 * Supports multiple cuts per scene, each with its own timing and type.
 */
import React from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';
import { SPRINGS } from '../lib/springs';

interface CutDefinition {
  /** Frame at which this cut triggers */
  frame: number;
  /** Type of camera movement */
  type: 'zoomPunch' | 'pullBack' | 'panLeft' | 'panRight' | 'panUp' | 'panDown' | 'shake';
  /** Intensity multiplier (default 1.0) */
  intensity?: number;
  /** Duration in frames (default 20) */
  duration?: number;
}

interface CameraCutProps {
  cuts: CutDefinition[];
  children: React.ReactNode;
}

export const CameraCut: React.FC<CameraCutProps> = ({
  cuts,
  children,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  let totalScale = 1;
  let totalX = 0;
  let totalY = 0;

  for (const cut of cuts) {
    const cutFrame = frame - cut.frame;
    const intensity = cut.intensity ?? 1;
    const duration = cut.duration ?? 20;

    if (cutFrame < 0 || cutFrame > duration * 2) continue;

    switch (cut.type) {
      case 'zoomPunch': {
        // Quick zoom in then ease back
        const zoomIn = spring({
          frame: cutFrame,
          fps,
          config: { damping: 15, stiffness: 300, mass: 0.6 },
        });
        const zoomOut = cutFrame > duration * 0.4
          ? spring({
              frame: cutFrame - Math.round(duration * 0.4),
              fps,
              config: SPRINGS.gentle,
            })
          : 0;
        const zoom = interpolate(zoomIn - zoomOut * 0.7, [0, 1], [0, 0.12 * intensity]);
        totalScale += zoom;
        break;
      }
      case 'pullBack': {
        // Zoom out to reveal more
        const pull = spring({ frame: cutFrame, fps, config: SPRINGS.smooth });
        totalScale -= interpolate(pull, [0, 1], [0, 0.08 * intensity]);
        break;
      }
      case 'panLeft': {
        const pan = spring({ frame: cutFrame, fps, config: SPRINGS.snappy });
        totalX -= interpolate(pan, [0, 1], [0, 30 * intensity]);
        break;
      }
      case 'panRight': {
        const pan = spring({ frame: cutFrame, fps, config: SPRINGS.snappy });
        totalX += interpolate(pan, [0, 1], [0, 30 * intensity]);
        break;
      }
      case 'panUp': {
        const pan = spring({ frame: cutFrame, fps, config: SPRINGS.snappy });
        totalY -= interpolate(pan, [0, 1], [0, 25 * intensity]);
        break;
      }
      case 'panDown': {
        const pan = spring({ frame: cutFrame, fps, config: SPRINGS.snappy });
        totalY += interpolate(pan, [0, 1], [0, 25 * intensity]);
        break;
      }
      case 'shake': {
        if (cutFrame < duration) {
          const decay = Math.max(0, 1 - cutFrame / duration);
          totalX += Math.sin(cutFrame * 2.7) * 8 * decay * intensity;
          totalY += Math.cos(cutFrame * 3.3) * 5 * decay * intensity;
        }
        break;
      }
    }
  }

  return (
    <AbsoluteFill style={{
      transform: `scale(${totalScale}) translate(${totalX}px, ${totalY}px)`,
      transformOrigin: 'center center',
    }}>
      {children}
    </AbsoluteFill>
  );
};
