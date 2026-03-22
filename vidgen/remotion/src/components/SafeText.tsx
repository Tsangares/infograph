import React from 'react';
import { useCurrentFrame, interpolate, spring, useVideoConfig } from 'remotion';
import { zoneStyle, type ZoneName } from '../lib/zones';
import { TKK_WHITE } from '../lib/colors';
import { FONTS } from '../lib/fonts';
import { FONT_SIZE } from '../lib/typography';
import { useSceneProgress } from '../lib/useSceneProgress';
import { SPRINGS } from '../lib/springs';

type Entrance = 'fade' | 'typewriter' | 'wordByWord';

interface SafeTextProps {
  children: string;
  zone?: ZoneName;
  color?: string;
  fontSize?: number;
  style?: 'headline' | 'caption' | 'stat' | 'label';
  delay?: number;
  entrance?: Entrance;
}

const STYLE_MAP = {
  headline: { fontFamily: FONTS.headline, fontSize: FONT_SIZE.headline, fontWeight: 'normal' as const, letterSpacing: 2 },
  caption: { fontFamily: FONTS.body, fontSize: FONT_SIZE.body, fontWeight: 'normal' as const, letterSpacing: 0.5 },
  stat: { fontFamily: FONTS.mono, fontSize: FONT_SIZE.stat, fontWeight: 'bold' as const, letterSpacing: 4 },
  label: { fontFamily: FONTS.body, fontSize: FONT_SIZE.caption, fontWeight: 'bold' as const, letterSpacing: 1.5 },
};

const BASE_DELAY_S = 0.5;

export const SafeText: React.FC<SafeTextProps> = ({
  children,
  zone = 'MID',
  color = TKK_WHITE,
  fontSize,
  style = 'caption',
  delay = 0,
  entrance = 'fade',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { exit } = useSceneProgress();

  const delayFrames = Math.round((BASE_DELAY_S + delay) * fps);
  const adjustedFrame = Math.max(0, frame - delayFrames);

  // Exit: fade + slide down
  const exitOpacity = interpolate(exit, [0, 1], [1, 0], { extrapolateRight: 'clamp' });
  const exitY = interpolate(exit, [0, 1], [0, 10], { extrapolateRight: 'clamp' });

  // Gentle float during hold
  const floatY = Math.sin(frame * 0.03) * 2;

  const styleConfig = STYLE_MAP[style];

  const baseStyle: React.CSSProperties = {
    ...styleConfig,
    fontSize: fontSize ?? styleConfig.fontSize,
    color,
    textAlign: 'center',
    lineHeight: 1.2,
  };

  let content: React.ReactNode;

  if (entrance === 'wordByWord') {
    const words = children.split(' ');
    content = (
      <span style={baseStyle}>
        {words.map((word, wi) => {
          const wordFrame = Math.max(0, adjustedFrame - wi * 3);
          const wordOpacity = interpolate(wordFrame, [0, 6], [0, 1], { extrapolateRight: 'clamp' });
          const wordY = interpolate(wordFrame, [0, 8], [8, 0], { extrapolateRight: 'clamp' });
          // Brief scale bump for the most recently appeared word
          const isActive = wordFrame > 0 && wordFrame < 12;
          const wordScale = isActive ? interpolate(wordFrame, [0, 6, 12], [1.05, 1.05, 1], { extrapolateRight: 'clamp' }) : 1;
          return (
            <span key={wi} style={{
              display: 'inline-block',
              opacity: wordOpacity,
              transform: `translateY(${wordY}px) scale(${wordScale})`,
              marginRight: '0.25em',
            }}>
              {word}
            </span>
          );
        })}
      </span>
    );
  } else if (entrance === 'typewriter') {
    const charsPerFrame = 2;
    const visibleChars = Math.min(children.length, Math.floor(adjustedFrame * charsPerFrame));
    const visible = children.slice(0, visibleChars);
    const hidden = children.slice(visibleChars);
    content = (
      <span style={baseStyle}>
        {visible}
        <span style={{ opacity: 0 }}>{hidden}</span>
      </span>
    );
  } else {
    // Default fade entrance
    const opacity = interpolate(adjustedFrame, [0, 10], [0, 1], { extrapolateRight: 'clamp' });
    const y = spring({
      frame: adjustedFrame,
      fps,
      config: { damping: 18, stiffness: 100 },
    });
    const translateY = interpolate(y, [0, 1], [20, 0]);
    content = (
      <span style={{
        ...baseStyle,
        opacity,
        transform: `translateY(${translateY}px)`,
        display: 'block',
      }}>
        {children}
      </span>
    );
  }

  return (
    <div style={{
      ...zoneStyle(zone),
      flexDirection: 'column',
      textAlign: 'center',
      opacity: exitOpacity,
      transform: `translateY(${exitY + floatY}px)`,
      zIndex: 20,
    }}>
      {content}
    </div>
  );
};
