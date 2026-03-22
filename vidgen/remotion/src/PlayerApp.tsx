import React, { useEffect, useState } from 'react';
import { Player } from '@remotion/player';
import { Video } from './Video';
import { WIDTH, HEIGHT, FPS } from './lib/zones';
import type { Manifest } from './schema';

// Signal to staticFile wrapper that we're in player mode
window.__TKK_PLAYER__ = true;

interface PlayerState {
  manifest: Manifest;
  sceneDurations: number[];
  audioSrc?: string;
}

export const PlayerApp: React.FC = () => {
  const [state, setState] = useState<PlayerState | null>(null);

  useEffect(() => {
    const handler = (e: MessageEvent) => {
      if (e.data?.type === 'tkk:load-manifest') {
        const { manifest, sceneDurations, audioSrc } = e.data;
        setState({ manifest, sceneDurations, audioSrc });
      }
    };
    window.addEventListener('message', handler);
    return () => window.removeEventListener('message', handler);
  }, []);

  if (!state) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: '100%',
        height: '100%',
        background: '#080A10',
        color: '#666',
        fontFamily: 'Inter, system-ui, sans-serif',
        fontSize: 13,
      }}>
        Waiting for manifest...
      </div>
    );
  }

  const totalFrames = state.sceneDurations.reduce(
    (sum, d) => sum + Math.round(d * FPS), 0
  );

  return (
    <Player
      component={Video}
      inputProps={{
        manifest: state.manifest,
        sceneDurations: state.sceneDurations,
        audioSrc: state.audioSrc,
      }}
      durationInFrames={Math.max(1, totalFrames)}
      compositionWidth={WIDTH}
      compositionHeight={HEIGHT}
      fps={FPS}
      controls
      clickToPlay
      style={{ width: '100%', height: '100%' }}
    />
  );
};
