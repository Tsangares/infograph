import React from 'react';
import { useCurrentFrame, spring, interpolate, useVideoConfig, Img } from 'remotion';
import { staticFile } from '../lib/static';
import { zoneStyle, type ZoneName } from '../lib/zones';
import { TKK_WHITE } from '../lib/colors';
import { FONTS } from '../lib/fonts';
import { FONT_SIZE } from '../lib/typography';
import { useSceneProgress } from '../lib/useSceneProgress';
import { SPRINGS } from '../lib/springs';

interface Icon {
  image: string;
  label?: string;
}

interface IconRowProps {
  icons: Icon[];
  zone?: ZoneName;
  staggerDelay?: number;
}

export const IconRow: React.FC<IconRowProps> = ({
  icons,
  zone = 'MID',
  staggerDelay = 0.15,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { exit, hold } = useSceneProgress();

  const iconSize = Math.min(120, 800 / icons.length);

  // Exit: fade + scale
  const exitOpacity = interpolate(exit, [0, 1], [1, 0], { extrapolateRight: 'clamp' });
  const exitScale = interpolate(exit, [0, 1], [1, 0.9], { extrapolateRight: 'clamp' });

  return (
    <div style={{
      ...zoneStyle(zone),
      flexWrap: 'wrap',
      gap: 20,
      opacity: exitOpacity,
      transform: `scale(${exitScale})`,
    }}>
      {icons.map((icon, i) => {
        const delayFrames = Math.round(i * staggerDelay * fps);
        const iconFrame = Math.max(0, frame - 8 - delayFrames);
        const scale = spring({
          frame: iconFrame,
          fps,
          config: SPRINGS.marker,
        });
        const opacity = interpolate(iconFrame, [0, 6], [0, 1], {
          extrapolateRight: 'clamp',
        });

        // Hold: gentle float
        const float = Math.sin((hold * Math.PI * 2) + i * 0.9) * 3;

        return (
          <div key={i} style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 8,
            opacity,
            transform: `scale(${scale}) translateY(${float}px)`,
          }}>
            <Img
              src={staticFile(icon.image)}
              style={{ width: iconSize, height: iconSize, objectFit: 'contain' }}
            />
            {icon.label && (
              <span style={{
                fontFamily: FONTS.body,
                fontSize: FONT_SIZE.dataValue,
                color: TKK_WHITE + 'CC',
                textAlign: 'center',
              }}>
                {icon.label}
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
};
