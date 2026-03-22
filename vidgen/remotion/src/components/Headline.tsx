import React from 'react';
import { useCurrentFrame, spring, interpolate, useVideoConfig } from 'remotion';
import { zoneStyle, type ZoneName } from '../lib/zones';
import { TKK_WHITE } from '../lib/colors';
import { FONTS } from '../lib/fonts';
import { FONT_SIZE } from '../lib/typography';
import { useSceneProgress } from '../lib/useSceneProgress';
import { SPRINGS } from '../lib/springs';

interface HeadlineProps {
  title: string;
  subtitle?: string;
  zone?: ZoneName;
  color?: string;
}

export const Headline: React.FC<HeadlineProps> = ({
  title,
  subtitle,
  zone = 'MID',
  color = TKK_WHITE,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { exit, hold, durationInFrames } = useSceneProgress();

  const scale = spring({ frame, fps, config: SPRINGS.headline });
  const fadeIn = Math.round(durationInFrames * 0.08);
  const opacity = interpolate(frame, [0, Math.max(fadeIn, 4)], [0, 1], { extrapolateRight: 'clamp' });

  const subtitleDelay = Math.round(durationInFrames * 0.08);
  const subtitleEnd = Math.round(durationInFrames * 0.15);
  const subtitleOpacity = interpolate(frame, [subtitleDelay, Math.max(subtitleEnd, subtitleDelay + 4)], [0, 1], { extrapolateRight: 'clamp' });
  const subtitleY = spring({
    frame: Math.max(0, frame - subtitleDelay),
    fps,
    config: { damping: 18, stiffness: 100 },
  });

  // Hold: gentle breathe
  const breathe = 1 + Math.sin(hold * Math.PI * 2) * 0.015;

  // Exit: scale down + fade
  const exitScale = interpolate(exit, [0, 1], [1, 0.92], { extrapolateRight: 'clamp' });
  const exitOpacity = interpolate(exit, [0, 1], [1, 0], { extrapolateRight: 'clamp' });

  return (
    <div style={{
      ...zoneStyle(zone),
      flexDirection: 'column',
      gap: 16,
    }}>
      <div style={{
        fontFamily: FONTS.headline,
        fontSize: FONT_SIZE.headline,
        color,
        textAlign: 'center',
        letterSpacing: 3,
        lineHeight: 1.1,
        opacity: opacity * exitOpacity,
        transform: `scale(${scale * exitScale * breathe})`,
      }}>
        {title}
      </div>
      {subtitle && (
        <div style={{
          fontFamily: FONTS.body,
          fontSize: FONT_SIZE.subtitle,
          color: color + 'AA',
          textAlign: 'center',
          opacity: subtitleOpacity * exitOpacity,
          transform: `translateY(${interpolate(subtitleY, [0, 1], [15, 0])}px)`,
        }}>
          {subtitle}
        </div>
      )}
    </div>
  );
};
