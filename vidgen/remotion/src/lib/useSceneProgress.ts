import { useCurrentFrame, useVideoConfig } from 'remotion';

/**
 * Hook providing scene lifecycle phases for animation choreography.
 *
 * Enter/exit phases scale proportionally with scene duration (10% each),
 * clamped to min 8 frames (0.27s) and max 20 frames (0.67s).
 *
 * - enter: 0→1 over the enter phase (fade in)
 * - hold:  0→1 over the middle phase (ambient motion)
 * - exit:  0→1 over the exit phase (fade out, 0 = visible, 1 = gone)
 * - progress: 0→1 over the entire scene
 */
export function useSceneProgress() {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // Proportional enter/exit: 10% of scene, clamped [8, 20] frames
  const enterFrames = Math.max(8, Math.min(20, Math.round(durationInFrames * 0.1)));
  const exitFrames = Math.max(8, Math.min(20, Math.round(durationInFrames * 0.1)));

  const exitStart = Math.max(enterFrames, durationInFrames - exitFrames);
  const holdDuration = exitStart - enterFrames;

  return {
    frame,
    enter: Math.min(1, Math.max(0, frame / enterFrames)),
    hold: holdDuration > 0
      ? Math.max(0, Math.min(1, (frame - enterFrames) / holdDuration))
      : 0,
    exit: Math.max(0, Math.min(1, (frame - exitStart) / exitFrames)),
    progress: durationInFrames > 0 ? frame / durationInFrames : 0,
    durationInFrames,
  };
}
