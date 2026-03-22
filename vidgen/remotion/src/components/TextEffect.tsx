/**
 * TextEffect — dramatic text reveals with visual effects.
 *
 * glitch: random characters resolve to real text
 * stamp: slams in from 3x scale with screen shake
 * shake: vibrates with decreasing amplitude
 * redacted: black bars fade away to reveal words
 * colorShift: cycles through colors before landing
 */
import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';
import { zoneStyle, type ZoneName } from '../lib/zones';
import { TKK_WHITE, TKK_GOLD, TKK_RED } from '../lib/colors';
import { FONTS } from '../lib/fonts';
import { FONT_SIZE } from '../lib/typography';
import { useSceneProgress } from '../lib/useSceneProgress';
import { SPRINGS } from '../lib/springs';

interface TextEffectProps {
  text: string;
  effect?: 'glitch' | 'stamp' | 'shake' | 'redacted' | 'colorShift';
  color?: string;
  zone?: ZoneName;
  effectDuration?: number;
}

const GLITCH_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%&*';

// Deterministic pseudo-random for Remotion (no Math.random in render)
function seededChar(seed: number): string {
  const idx = Math.abs(Math.floor(Math.sin(seed * 127.1) * 43758.5453)) % GLITCH_CHARS.length;
  return GLITCH_CHARS[idx];
}

export const TextEffect: React.FC<TextEffectProps> = ({
  text,
  effect = 'stamp',
  color = TKK_GOLD,
  zone = 'MID',
  effectDuration = 0.4,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const { exit } = useSceneProgress();

  const effectFrames = Math.round(durationInFrames * effectDuration);

  // Exit
  const exitOpacity = interpolate(exit, [0, 1], [1, 0], { extrapolateRight: 'clamp' });
  const exitScale = interpolate(exit, [0, 1], [1, 0.9], { extrapolateRight: 'clamp' });

  const effectProgress = interpolate(frame, [0, effectFrames], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  let content: React.ReactNode;
  let containerTransform = '';
  let containerOpacity = 1;

  switch (effect) {
    case 'glitch': {
      const chars = text.split('');
      content = (
        <span>
          {chars.map((char, i) => {
            // Each character resolves at a staggered time
            const charResolveAt = (i / chars.length) * 0.8 + 0.1;
            const isResolved = effectProgress >= charResolveAt;
            const displayChar = isResolved || char === ' '
              ? char
              : seededChar(frame * 13 + i * 7);
            const charColor = isResolved ? color : TKK_WHITE + '88';
            return (
              <span key={i} style={{ color: charColor }}>
                {displayChar}
              </span>
            );
          })}
        </span>
      );
      containerOpacity = interpolate(frame, [0, 5], [0, 1], { extrapolateRight: 'clamp' });
      break;
    }

    case 'stamp': {
      const stampProgress = spring({ frame, fps, config: SPRINGS.heavy });
      const scale = interpolate(stampProgress, [0, 1], [3, 1]);
      containerOpacity = interpolate(frame, [0, 3], [0, 1], { extrapolateRight: 'clamp' });

      // Screen shake after impact
      let shakeX = 0;
      let shakeY = 0;
      if (frame > 0 && frame < 18) {
        const decay = Math.max(0, 1 - frame / 18);
        shakeX = Math.sin(frame * 2.5) * 10 * decay;
        shakeY = Math.cos(frame * 3.1) * 6 * decay;
      }

      containerTransform = `scale(${scale}) translate(${shakeX}px, ${shakeY}px)`;
      content = text;
      break;
    }

    case 'shake': {
      containerOpacity = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: 'clamp' });
      const amplitude = interpolate(frame, [0, effectFrames], [15, 0], {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      });
      const shakeX = Math.sin(frame * 1.7) * amplitude;
      const shakeY = Math.cos(frame * 2.3) * amplitude * 0.6;
      containerTransform = `translate(${shakeX}px, ${shakeY}px)`;
      content = text;
      break;
    }

    case 'redacted': {
      const words = text.split(' ');
      content = (
        <span>
          {words.map((word, i) => {
            const revealAt = (i / words.length) * 0.7 + 0.15;
            const wordProgress = interpolate(effectProgress, [revealAt, revealAt + 0.15], [0, 1], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            });
            return (
              <span key={i} style={{ position: 'relative', display: 'inline-block', margin: '0 6px' }}>
                <span style={{ opacity: wordProgress }}>{word}</span>
                <span style={{
                  position: 'absolute',
                  inset: '-4px -2px',
                  backgroundColor: TKK_WHITE,
                  opacity: 1 - wordProgress,
                  borderRadius: 4,
                }} />
              </span>
            );
          })}
        </span>
      );
      containerOpacity = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: 'clamp' });
      break;
    }

    case 'colorShift': {
      const colors = [TKK_RED, '#3B82F6', TKK_GOLD, '#22C55E', color];
      const isDone = effectProgress >= 1;
      const colorIndex = isDone
        ? colors.length - 1
        : Math.floor(frame * 0.3) % (colors.length - 1);
      const currentColor = isDone ? color : colors[colorIndex];

      containerOpacity = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: 'clamp' });
      content = <span style={{ color: currentColor }}>{text}</span>;
      break;
    }
  }

  // Hold: subtle breathe
  const holdBreath = frame > effectFrames
    ? 1 + Math.sin(frame * 0.04) * 0.01
    : 1;

  return (
    <div style={{
      ...zoneStyle(zone),
      flexDirection: 'column',
      alignItems: 'center',
      opacity: containerOpacity * exitOpacity,
      transform: `${containerTransform} scale(${exitScale * holdBreath})`.trim(),
    }}>
      <div style={{
        fontFamily: FONTS.headline,
        fontSize: FONT_SIZE.headline,
        fontWeight: 'bold',
        color: effect !== 'glitch' && effect !== 'colorShift' ? color : undefined,
        textAlign: 'center',
        letterSpacing: 4,
        textTransform: 'uppercase',
        textShadow: `0 0 30px ${color}33`,
        lineHeight: 1.2,
        maxWidth: 750,
      }}>
        {content}
      </div>
    </div>
  );
};
