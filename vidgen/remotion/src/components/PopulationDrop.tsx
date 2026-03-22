import React from 'react';
import { useCurrentFrame, interpolate, spring, useVideoConfig } from 'remotion';
import { ZONES, SAFE } from '../lib/zones';
import { TKK_RED, TKK_WHITE, TKK_DIM } from '../lib/colors';
import { FONTS } from '../lib/fonts';
import { useSceneProgress } from '../lib/useSceneProgress';

interface PopulationDropProps {
  startValue: number;
  endValue: number;
  unit?: string;
  label?: string;
  color?: string;
}

export const PopulationDrop: React.FC<PopulationDropProps> = ({
  startValue,
  endValue,
  unit = '',
  label,
  color = TKK_RED,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const { exit, hold } = useSceneProgress();

  // Dramatic pause at start (proportional), then rapid drop
  const dropStart = Math.round(durationInFrames * 0.15);
  const dropEnd = Math.round(durationInFrames * 0.7);

  const value = interpolate(frame, [dropStart, dropEnd], [startValue, endValue], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const opacity = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: 'clamp' });

  // Bar shrinks to show the drop
  const barPct = (value - endValue) / (startValue - endValue);
  const barWidth = interpolate(barPct, [0, 1], [0.1, 1]);

  // Hold: subtle wobble on the bar after drop
  const dropDone = frame > dropEnd ? 1 : 0;
  const wobble = dropDone * Math.sin(hold * Math.PI * 4) * 0.008;

  // Exit: fade + slight scale
  const exitOpacity = interpolate(exit, [0, 1], [1, 0], { extrapolateRight: 'clamp' });
  const exitScale = interpolate(exit, [0, 1], [1, 0.93], { extrapolateRight: 'clamp' });

  const formatted = Math.round(value).toLocaleString();
  const dropPct = ((startValue - endValue) / startValue * 100).toFixed(0);

  return (
    <div style={{
      position: 'absolute',
      top: ZONES.MID.range[0] - 80,
      left: SAFE.left,
      width: SAFE.width,
      height: ZONES.MID.range[1] - ZONES.MID.range[0] + 160,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 20,
      opacity: opacity * exitOpacity,
      transform: `scale(${exitScale})`,
    }}>
      {/* Main number */}
      <div style={{
        fontFamily: FONTS.mono,
        fontSize: 88,
        fontWeight: 'bold',
        color,
        letterSpacing: 4,
      }}>
        {formatted}{unit && <span style={{ fontSize: 40, marginLeft: 8 }}>{unit}</span>}
      </div>

      {/* Shrinking bar */}
      <div style={{
        width: SAFE.width * 0.8,
        height: 24,
        background: TKK_DIM,
        borderRadius: 12,
        overflow: 'hidden',
      }}>
        <div style={{
          width: `${(barWidth + wobble) * 100}%`,
          height: '100%',
          background: color,
          borderRadius: 12,
        }} />
      </div>

      {/* Label */}
      {label && (
        <div style={{
          fontFamily: FONTS.body,
          fontSize: 28,
          color: TKK_WHITE + 'CC',
          textAlign: 'center',
        }}>
          {label}
        </div>
      )}

      {/* Drop percentage (appears after drop) */}
      {frame > dropEnd && (
        <div style={{
          fontFamily: FONTS.headline,
          fontSize: 48,
          color: color + 'DD',
          opacity: interpolate(frame, [dropEnd, dropEnd + 15], [0, 1], { extrapolateRight: 'clamp' }),
        }}>
          −{dropPct}%
        </div>
      )}
    </div>
  );
};
