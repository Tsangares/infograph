/**
 * WordTriggeredVideo — top-level composition using word-level timestamps.
 * Drop-in replacement for Video.tsx when using resolved manifests.
 *
 * Uses varied transitions (fade, slide, wipe, clockWipe) for visual variety
 * instead of uniform crossfades.
 */
import React from 'react';
import { AbsoluteFill, Audio, measureSpring, useVideoConfig } from 'remotion';
import { TransitionSeries, springTiming } from '@remotion/transitions';
import { fade } from '@remotion/transitions/fade';
import { slide } from '@remotion/transitions/slide';
import { wipe } from '@remotion/transitions/wipe';
import { clockWipe } from '@remotion/transitions/clock-wipe';
import { staticFile } from '../lib/static';
import { WIDTH, HEIGHT } from '../lib/zones';
import { fontFaces } from '../lib/fonts';
import { SPRINGS } from '../lib/springs';
import { WordTriggeredScene } from './WordTriggeredScene';
import type { ResolvedManifest } from './types';

interface WordTriggeredVideoProps {
  manifest: ResolvedManifest;
  audioSrc?: string;
}

/**
 * Deterministic transition selection based on scene index.
 * Cycles through different transition types for visual variety:
 * - Scene 0→1: slide (strong opening momentum)
 * - Scene 1→2: wipe (reveal feel for contradiction)
 * - Scene 2→3: clockWipe (dramatic proof reveal)
 * - Scene 3→4: slide from bottom (betrayal hits different)
 * - Scene 4→5: fade (clean close for the punch)
 * Wraps around for videos with more scenes.
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function getTransitionPresentation(index: number): any {
  const cycle = index % 5;
  switch (cycle) {
    case 0:
      return slide({ direction: 'from-left' });
    case 1:
      return wipe({ direction: 'from-left' });
    case 2:
      return clockWipe({ width: WIDTH, height: HEIGHT });
    case 3:
      return slide({ direction: 'from-bottom' });
    case 4:
    default:
      return fade();
  }
}

export const WordTriggeredVideo: React.FC<WordTriggeredVideoProps> = ({
  manifest,
  audioSrc,
}) => {
  const { fps } = useVideoConfig();

  const transitionFrames = measureSpring({ fps, config: SPRINGS.transition });
  const numTransitions = Math.max(0, manifest.scenes.length - 1);
  const totalOverlapFrames = numTransitions * transitionFrames;

  return (
    <AbsoluteFill>
      <style dangerouslySetInnerHTML={{ __html: fontFaces }} />

      {audioSrc && <Audio src={staticFile(audioSrc)} />}

      <TransitionSeries>
        {manifest.scenes.map((scene, i) => {
          let durationInFrames = scene.duration_frames;

          if (i === manifest.scenes.length - 1) {
            durationInFrames += totalOverlapFrames;
          }

          return (
            <React.Fragment key={scene.id}>
              <TransitionSeries.Sequence durationInFrames={durationInFrames}>
                <WordTriggeredScene
                  scene={scene}
                  bgColor={manifest.colors.bg}
                  accentColor={manifest.colors.accent}
                  secondaryColor={manifest.colors.secondary}
                />
              </TransitionSeries.Sequence>
              {i < manifest.scenes.length - 1 && (
                <TransitionSeries.Transition
                  presentation={getTransitionPresentation(i)}
                  timing={springTiming({ config: SPRINGS.transition })}
                />
              )}
            </React.Fragment>
          );
        })}
      </TransitionSeries>
    </AbsoluteFill>
  );
};
