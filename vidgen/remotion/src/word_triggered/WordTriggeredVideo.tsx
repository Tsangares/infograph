/**
 * WordTriggeredVideo — top-level composition using word-level timestamps.
 * Drop-in replacement for Video.tsx when using resolved manifests.
 */
import React from 'react';
import { AbsoluteFill, Audio, measureSpring, useVideoConfig } from 'remotion';
import { TransitionSeries, springTiming } from '@remotion/transitions';
import { fade } from '@remotion/transitions/fade';
import { staticFile } from '../lib/static';
import { fontFaces } from '../lib/fonts';
import { SPRINGS } from '../lib/springs';
import { WordTriggeredScene } from './WordTriggeredScene';
import type { ResolvedManifest } from './types';

interface WordTriggeredVideoProps {
  manifest: ResolvedManifest;
  audioSrc?: string;
}

export const WordTriggeredVideo: React.FC<WordTriggeredVideoProps> = ({
  manifest,
  audioSrc,
}) => {
  const { fps } = useVideoConfig();

  const transitionFrames = measureSpring({ fps, config: SPRINGS.gentle });
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
                  presentation={fade()}
                  timing={springTiming({ config: SPRINGS.gentle })}
                />
              )}
            </React.Fragment>
          );
        })}
      </TransitionSeries>
    </AbsoluteFill>
  );
};
