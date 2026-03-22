import React from 'react';
import { useCurrentFrame, interpolate, useVideoConfig, Img } from 'remotion';
import { staticFile } from '../lib/static';
import { zoneStyle, type ZoneName, WIDTH } from '../lib/zones';
import { useSceneProgress } from '../lib/useSceneProgress';

interface KenBurnsProps {
  image: string;
  startScale?: number;
  endScale?: number;
  panX?: number;
  panY?: number;
  zone?: ZoneName;
}

export const KenBurns: React.FC<KenBurnsProps> = ({
  image,
  startScale = 1.2,
  endScale = 1.0,
  panX = 0,
  panY = 0,
  zone = 'MID',
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const { exit } = useSceneProgress();

  const scale = interpolate(frame, [0, durationInFrames], [startScale, endScale], {
    extrapolateRight: 'clamp',
  });
  const translateX = interpolate(frame, [0, durationInFrames], [0, panX], {
    extrapolateRight: 'clamp',
  });
  const translateY = interpolate(frame, [0, durationInFrames], [0, panY], {
    extrapolateRight: 'clamp',
  });
  const opacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });

  // Exit: fade out
  const exitOpacity = interpolate(exit, [0, 1], [1, 0], { extrapolateRight: 'clamp' });

  const style = zoneStyle(zone);

  return (
    <div style={{
      ...style,
      overflow: 'hidden',
      borderRadius: 12,
      opacity: opacity * exitOpacity,
    }}>
      <Img
        src={staticFile(image)}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          transform: `scale(${scale}) translate(${translateX}px, ${translateY}px)`,
        }}
      />
    </div>
  );
};
