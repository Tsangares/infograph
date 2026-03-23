/**
 * NumberTicker — slot-machine style digit ticker.
 * Each digit column spins independently to its target value.
 * Much more engaging than simple counter interpolation.
 */
import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';
import { zoneStyle, type ZoneName } from '../lib/zones';
import { SPRINGS } from '../lib/springs';
import { FONTS } from '../lib/fonts';

interface NumberTickerProps {
  /** Target number to tick to */
  value: number;
  /** Optional prefix (e.g. "$", "€") */
  prefix?: string;
  /** Optional suffix (e.g. "%", "M", "B") */
  suffix?: string;
  /** Unit label below the number */
  unit?: string;
  color?: string;
  zone?: ZoneName;
  /** Delay before ticking starts */
  delay?: number;
  /** Number of decimal places */
  decimals?: number;
}

const DIGITS = '0123456789';
const DIGIT_HEIGHT = 160;

const DigitColumn: React.FC<{
  target: number;
  delay: number;
  fps: number;
  color: string;
}> = ({ target, delay, fps, color }) => {
  const frame = useCurrentFrame();
  const adjusted = Math.max(0, frame - delay);

  // Each digit spins through 0-9 multiple times before landing
  const spins = 2; // full rotations before target
  const totalTravel = spins * 10 + target;

  const progress = spring({
    frame: adjusted,
    fps,
    config: { damping: 18, stiffness: 120, mass: 1.2 },
  });

  const currentPosition = totalTravel * progress;
  const displayDigit = Math.round(currentPosition) % 10;

  // Vertical offset for scroll effect
  const fractional = currentPosition - Math.floor(currentPosition);
  const yOffset = -fractional * DIGIT_HEIGHT;

  // Show current and next digit for smooth scrolling
  const currentIdx = Math.floor(currentPosition) % 10;
  const nextIdx = (currentIdx + 1) % 10;

  const opacity = interpolate(adjusted, [0, 8], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <div style={{
      width: 90,
      height: DIGIT_HEIGHT,
      overflow: 'hidden',
      position: 'relative',
      opacity,
    }}>
      <div style={{
        position: 'absolute',
        top: yOffset,
        width: '100%',
        transition: 'none',
      }}>
        <div style={{
          height: DIGIT_HEIGHT,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontFamily: FONTS.headline,
          fontSize: 140,
          fontWeight: 'bold',
          color,
          textShadow: `0 0 20px ${color}44`,
        }}>
          {DIGITS[currentIdx]}
        </div>
        <div style={{
          height: DIGIT_HEIGHT,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontFamily: FONTS.headline,
          fontSize: 140,
          fontWeight: 'bold',
          color,
          textShadow: `0 0 20px ${color}44`,
        }}>
          {DIGITS[nextIdx]}
        </div>
      </div>
    </div>
  );
};

export const NumberTicker: React.FC<NumberTickerProps> = ({
  value,
  prefix = '',
  suffix = '',
  unit,
  color = '#FFD700',
  zone = 'MID',
  delay = 0,
  decimals = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const formatted = value.toFixed(decimals);
  const digits = formatted.replace('.', '').split('').map(Number);
  const dotIndex = formatted.indexOf('.');

  // Entry
  const entryScale = spring({ frame: Math.max(0, frame - delay), fps, config: SPRINGS.dramatic });
  const entryOpacity = interpolate(Math.max(0, frame - delay), [0, 8], [0, 1], { extrapolateRight: 'clamp' });

  // Exit
  const exitStart = durationInFrames - 12;
  const exitOpacity = interpolate(frame, [exitStart, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div style={{
      ...zoneStyle(zone),
      flexDirection: 'column',
      alignItems: 'center',
      gap: 12,
      opacity: entryOpacity * exitOpacity,
      transform: `scale(${entryScale})`,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 0 }}>
        {/* Prefix */}
        {prefix && (
          <div style={{
            fontFamily: FONTS.headline,
            fontSize: 80,
            color: `${color}88`,
            marginRight: 4,
            opacity: entryOpacity,
          }}>
            {prefix}
          </div>
        )}

        {/* Digit columns */}
        {digits.map((digit, i) => {
          // Insert decimal point
          const needsDot = dotIndex > 0 && i === dotIndex;
          const staggerDelay = delay + i * 3; // 3-frame stagger per digit

          return (
            <React.Fragment key={i}>
              {needsDot && (
                <div style={{
                  fontFamily: FONTS.headline,
                  fontSize: 140,
                  color,
                  lineHeight: 1,
                  marginTop: -10,
                }}>.</div>
              )}
              <DigitColumn target={digit} delay={staggerDelay} fps={fps} color={color} />
            </React.Fragment>
          );
        })}

        {/* Suffix */}
        {suffix && (
          <div style={{
            fontFamily: FONTS.headline,
            fontSize: 80,
            color: `${color}88`,
            marginLeft: 4,
            opacity: entryOpacity,
          }}>
            {suffix}
          </div>
        )}
      </div>

      {/* Unit label */}
      {unit && (
        <div style={{
          fontFamily: FONTS.body,
          fontSize: 36,
          color: '#EAEAF0',
          letterSpacing: 4,
          textTransform: 'uppercase',
          opacity: interpolate(Math.max(0, frame - delay - 15), [0, 10], [0, 0.7], { extrapolateRight: 'clamp' }),
        }}>
          {unit}
        </div>
      )}
    </div>
  );
};
