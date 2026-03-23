import React from 'react';
import { useCurrentFrame, interpolate, spring, useVideoConfig } from 'remotion';
import { zoneStyle, type ZoneName } from '../lib/zones';
import { TKK_WHITE, TKK_GOLD } from '../lib/colors';
import { FONTS } from '../lib/fonts';
import { FONT_SIZE } from '../lib/typography';
import { useSceneProgress } from '../lib/useSceneProgress';
import { SPRINGS } from '../lib/springs';

interface CounterProps {
  start: number;
  end: number;
  unit?: string;
  description?: string;
  color?: string;
  zone?: ZoneName;
  countDuration?: number;
}

export const Counter: React.FC<CounterProps> = ({
  start,
  end,
  unit = '',
  description,
  color = TKK_GOLD,
  zone = 'MID',
  countDuration = 0.5,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const { exit } = useSceneProgress();

  // Count up during the first half, then hold the final number
  const countFrames = Math.round(durationInFrames * countDuration);
  const value = interpolate(frame, [0, Math.max(1, countFrames)], [start, end], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const countDone = frame >= countFrames;

  // Entry: fade in
  const entryOpacity = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: 'clamp' });
  const entryScale = spring({ frame, fps, config: SPRINGS.snappy });

  // Bloom: spring scale punch when counting finishes
  const bloomFrame = countDone ? frame - countFrames : 0;
  const bloomScale = countDone
    ? spring({ frame: bloomFrame, fps, config: SPRINGS.dramatic })
    : 0;
  // Bloom overshoots to 1.25x then settles back to 1.0
  const bloomEffect = countDone
    ? 1 + interpolate(bloomScale, [0, 1], [0.25, 0], { extrapolateRight: 'clamp' })
    : 1;

  // Bloom glow: brief bright shadow that fades out (brighter & wider)
  const bloomGlow = countDone
    ? interpolate(bloomFrame, [0, 6, 18], [0, 1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })
    : 0;

  // Screen shake on bloom: decaying high-freq oscillation
  const shakeDecay = countDone
    ? interpolate(bloomFrame, [0, 12], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })
    : 0;
  const shakeX = shakeDecay * Math.sin(bloomFrame * 1.8) * 4;
  const shakeY = shakeDecay * Math.cos(bloomFrame * 2.3) * 3;

  // Counting tick: micro-bounce when displayed number changes frame-to-frame
  const prevValue = interpolate(Math.max(0, frame - 1), [0, Math.max(1, countFrames)], [start, end], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const numberChanged = !countDone && Math.round(value) !== Math.round(prevValue);
  const tickBounce = numberChanged ? 1.03 : 1;

  // Exit: scale down + fade
  const exitScale = interpolate(exit, [0, 1], [1, 0.9], { extrapolateRight: 'clamp' });
  const exitOpacity = interpolate(exit, [0, 1], [1, 0], { extrapolateRight: 'clamp' });

  const formatted = Math.abs(value) >= 1000
    ? Math.round(value).toLocaleString()
    : Number.isInteger(end) ? Math.round(value).toString() : value.toFixed(1);

  return (
    <div style={{
      ...zoneStyle(zone),
      flexDirection: 'column',
      gap: 12,
      opacity: entryOpacity * exitOpacity,
      transform: `translate(${shakeX}px, ${shakeY}px) scale(${entryScale * exitScale * bloomEffect * tickBounce})`,
    }}>
      <div style={{
        fontFamily: FONTS.mono,
        fontSize: FONT_SIZE.hero,
        fontWeight: 'bold',
        color,
        textAlign: 'center',
        letterSpacing: 4,
        textShadow: bloomGlow > 0
          ? `0 0 ${50 * bloomGlow}px ${color}, 0 0 ${100 * bloomGlow}px ${color}80, 0 0 ${150 * bloomGlow}px ${color}30`
          : 'none',
      }}>
        {unit && ['$', '€', '£', '¥'].includes(unit) ? (
          <><span style={{ fontSize: FONT_SIZE.subtitle }}>{unit}</span>{formatted}</>
        ) : (
          <>{formatted}{unit && <span style={{ fontSize: FONT_SIZE.subtitle, marginLeft: 8 }}>{unit}</span>}</>
        )}
      </div>
      {description && (
        <div style={{
          fontFamily: FONTS.body,
          fontSize: FONT_SIZE.body,
          color: TKK_WHITE + 'CC',
          textAlign: 'center',
        }}>
          {description}
        </div>
      )}
    </div>
  );
};
