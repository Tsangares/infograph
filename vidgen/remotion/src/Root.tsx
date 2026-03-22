import React from 'react';
import { Composition, staticFile } from 'remotion';
import { Video } from './Video';
import { WordTriggeredVideo } from './word_triggered/WordTriggeredVideo';
import { ManifestSchema } from './schema';
import { WIDTH, HEIGHT, FPS } from './lib/zones';
import type { ResolvedManifest } from './word_triggered/types';

/**
 * TKK Remotion Root — registers compositions from manifest files.
 *
 * For the Remotion preview/studio, we load a demo manifest.
 * For CLI rendering, the manifest is passed via inputProps.
 */

// Demo manifest for preview (loaded at build time)
const DEMO_MANIFEST = {
  topic: 'demo',
  ttsScript: 'This is a demo video.',
  colors: { bg: '#080A10', accent: '#FFD700', secondary: '#3B82F6' },
  scenes: [
    {
      type: 'headline' as const,
      label: 'THE HOOK',
      props: { title: 'TKK REMOTION', subtitle: 'Manifest-driven video engine', zone: 'MID' as const },
    },
    {
      type: 'counter' as const,
      label: 'THE DATA',
      props: { start: 0, end: 1080, unit: 'px', description: 'Portrait width', zone: 'MID' as const },
    },
    {
      type: 'barChart' as const,
      label: 'THE PROOF',
      props: {
        bars: [
          { label: 'Manim', value: 550, color: '#EF4444' },
          { label: 'Remotion', value: 50, color: '#22C55E' },
        ],
        zone: 'MID' as const,
      },
      text: [{ content: 'Lines of code per video', zone: 'FOOTER' as const, style: 'caption' as const }],
    },
    {
      type: 'headline' as const,
      label: 'THE PUNCH',
      props: { title: 'MANIFEST > CODE', zone: 'MID' as const, color: '#FFD700' },
    },
  ],
};

const DEMO_DURATIONS = [4, 5, 5, 4];

export const RemotionRoot: React.FC = () => {
  const totalFrames = DEMO_DURATIONS.reduce((sum, d) => sum + Math.round(d * FPS), 0);

  return (
    <>
      <Composition
        id="demo"
        component={Video}
        durationInFrames={totalFrames}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
        defaultProps={{
          manifest: DEMO_MANIFEST,
          sceneDurations: DEMO_DURATIONS,
        }}
      />
      {/* Word-triggered composition — uses resolved manifests from resolve_word_triggers.py */}
      <Composition
        id="word-triggered"
        component={WordTriggeredVideo}
        durationInFrames={300}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
        defaultProps={{
          manifest: {
            topic: 'demo',
            colors: { bg: '#080A10', accent: '#4ADE80', secondary: '#EF4444' },
            fps: FPS,
            total_duration_s: 10,
            total_frames: 300,
            scene_durations: [5, 5],
            scenes: [
              {
                id: 'hook',
                label: 'WORD TRIGGERED',
                type: 'headline',
                start_s: 0,
                end_s: 5,
                duration_s: 5,
                duration_frames: 150,
                elements: [{
                  type: 'text' as const,
                  content: 'WORD TRIGGERED DEMO',
                  zone: 'MID' as const,
                  style: 'headline' as const,
                  color: '#4ADE80',
                  enter: 'fade',
                  _resolved: { delay_frames: 0, delay_s: 0, anchor_word: 'demo', anchor_time_s: 0, absolute_frame: 0, absolute_s: 0 },
                }],
              },
              {
                id: 'punch',
                label: 'THE RESULT',
                type: 'headline',
                start_s: 5,
                end_s: 10,
                duration_s: 5,
                duration_frames: 150,
                elements: [{
                  type: 'text' as const,
                  content: 'SYNC BY WORDS',
                  zone: 'MID' as const,
                  style: 'headline' as const,
                  color: '#4ADE80',
                  enter: 'fade',
                  _resolved: { delay_frames: 15, delay_s: 0.5, anchor_word: 'sync', anchor_time_s: 5.5, absolute_frame: 165, absolute_s: 5.5 },
                }],
              },
            ],
          } satisfies ResolvedManifest,
        }}
      />
    </>
  );
};
