import React from 'react';
import { useCurrentFrame, interpolate, useVideoConfig, OffthreadVideo } from 'remotion';
import { staticFile } from '../lib/static';
import { zoneStyle, type ZoneName } from '../lib/zones';
import { useSceneProgress } from '../lib/useSceneProgress';

interface VideoClipProps {
  src: string;
  startFrom?: number;
  endAt?: number;
  objectFit?: 'cover' | 'contain';
  zone?: ZoneName;
}

export const VideoClip: React.FC<VideoClipProps> = ({
  src,
  startFrom = 0,
  endAt,
  objectFit = 'cover',
  zone = 'MID',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { exit } = useSceneProgress();

  const opacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const exitOpacity = interpolate(exit, [0, 1], [1, 0], { extrapolateRight: 'clamp' });

  return (
    <div style={{
      ...zoneStyle(zone),
      overflow: 'hidden',
      borderRadius: 12,
      opacity: opacity * exitOpacity,
    }}>
      <OffthreadVideo
        src={staticFile(src)}
        startFrom={Math.round(startFrom * fps)}
        endAt={endAt ? Math.round(endAt * fps) : undefined}
        style={{ width: '100%', height: '100%', objectFit }}
      />
    </div>
  );
};
