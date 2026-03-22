import React from 'react';
import { useCurrentFrame, interpolate, spring, useVideoConfig } from 'remotion';
import { ZONES, SAFE, type ZoneName } from '../lib/zones';
import { TKK_GOLD, TKK_SURFACE } from '../lib/colors';
import { FONTS } from '../lib/fonts';
import { FONT_SIZE } from '../lib/typography';
import { useSceneProgress } from '../lib/useSceneProgress';
import { SPRINGS } from '../lib/springs';

interface LabelPillProps {
  text: string;
  zone?: ZoneName;
  color?: string;
  bgColor?: string;
}

export const LabelPill: React.FC<LabelPillProps> = ({
  text,
  zone = 'TITLE',
  color = TKK_GOLD,
  bgColor = TKK_SURFACE,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { exit } = useSceneProgress();

  const scale = spring({ frame, fps, config: SPRINGS.pill });
  const opacity = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: 'clamp' });

  // Exit: scale down + fade
  const exitOpacity = interpolate(exit, [0, 1], [1, 0], { extrapolateRight: 'clamp' });
  const exitScale = interpolate(exit, [0, 1], [1, 0.85], { extrapolateRight: 'clamp' });

  const z = ZONES[zone];

  return (
    <div style={{
      position: 'absolute',
      top: z.y - 20,
      left: 0,
      width: SAFE.width,
      marginLeft: SAFE.left,
      display: 'flex',
      justifyContent: 'center',
      zIndex: 30,
      opacity: opacity * exitOpacity,
      transform: `scale(${scale * exitScale})`,
    }}>
      <div style={{
        background: bgColor,
        borderRadius: 12,
        padding: '8px 24px',
        display: 'inline-flex',
        alignItems: 'center',
      }}>
        <span style={{
          fontFamily: FONTS.body,
          fontWeight: 'bold',
          fontSize: FONT_SIZE.pill,
          color,
          letterSpacing: 2,
          textTransform: 'uppercase',
        }}>
          {text}
        </span>
      </div>
    </div>
  );
};
