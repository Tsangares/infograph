import React from 'react';
import { AbsoluteFill, Audio, measureSpring, useVideoConfig } from 'remotion';
import { TransitionSeries, springTiming } from '@remotion/transitions';
import { fade } from '@remotion/transitions/fade';
import { staticFile } from './lib/static';
import type { Manifest } from './schema';
import { SceneRouter } from './components/SceneRouter';
import { fontFaces } from './lib/fonts';
import { SPRINGS } from './lib/springs';

interface VideoProps {
  manifest: Manifest;
  sceneDurations: number[];
  audioSrc?: string;
}

/**
 * Main TKK video component. Renders each scene inside a
 * TransitionSeries with fade transitions between scenes.
 *
 * TransitionSeries overlaps adjacent scenes during fade transitions,
 * so the total visual duration = sum(sceneDurations) - (N-1)*transitionFrames.
 * To prevent black frames at the end while narration continues, we extend
 * the last scene by the total overlap so visual content fills the full composition.
 */
export const Video: React.FC<VideoProps> = ({
  manifest,
  sceneDurations,
  audioSrc,
}) => {
  const { fps } = useVideoConfig();

  // Compute total transition overlap so we can extend the last scene
  const transitionFrames = measureSpring({ fps, config: SPRINGS.gentle });
  const numTransitions = Math.max(0, manifest.scenes.length - 1);
  const totalOverlapFrames = numTransitions * transitionFrames;

  return (
    <AbsoluteFill>
      {/* Inject font faces */}
      <style dangerouslySetInnerHTML={{ __html: fontFaces }} />

      {/* Audio track */}
      {audioSrc && <Audio src={staticFile(audioSrc)} />}

      {/* Scene sequences with fade transitions */}
      <TransitionSeries>
        {manifest.scenes.map((scene, i) => {
          const duration = sceneDurations[i] ?? 5;
          let durationInFrames = Math.round(duration * fps);

          // Extend the last scene to compensate for all transition overlaps.
          // Without this, the last ~4s of the composition would be black
          // while narration continues playing.
          if (i === manifest.scenes.length - 1) {
            durationInFrames += totalOverlapFrames;
          }

          return (
            <React.Fragment key={i}>
              <TransitionSeries.Sequence durationInFrames={durationInFrames}>
                <SceneRouter scene={scene} bgColor={manifest.colors.bg} accentColor={manifest.colors.accent} secondaryColor={manifest.colors.secondary} />
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
