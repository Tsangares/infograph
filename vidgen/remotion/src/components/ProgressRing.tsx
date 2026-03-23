/**
 * ProgressRing — animated donut rings showing percentages/values.
 *
 * Up to 3 concentric rings for comparison. Visual alternative to Counter.
 * "90% of water lost" as a ring filling to 90% is more visceral than a number ticking.
 */
import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';
import { zoneStyle, type ZoneName } from '../lib/zones';
import { TKK_WHITE, TKK_GOLD } from '../lib/colors';
import { FONTS } from '../lib/fonts';
import { FONT_SIZE } from '../lib/typography';
import { useSceneProgress } from '../lib/useSceneProgress';
import { SPRINGS } from '../lib/springs';

interface RingData {
  value: number;
  maxValue?: number;
  label: string;
  color?: string;
}

interface ProgressRingProps {
  rings: RingData[];
  unit?: string;
  zone?: ZoneName;
  fillDuration?: number;
}

export const ProgressRing: React.FC<ProgressRingProps> = ({
  rings,
  unit = '',
  zone = 'MID',
  fillDuration = 0.5,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const { exit } = useSceneProgress();

  const fillFrames = Math.round(durationInFrames * fillDuration);
  const isDone = frame > fillFrames;

  // Entrance
  const opacity = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: 'clamp' });
  const scale = spring({ frame, fps, config: SPRINGS.snappy });

  // Exit
  const exitOpacity = interpolate(exit, [0, 1], [1, 0], { extrapolateRight: 'clamp' });
  const exitScale = interpolate(exit, [0, 1], [1, 0.9], { extrapolateRight: 'clamp' });

  const cx = 200;
  const cy = 200;
  const baseRadius = 160;
  const strokeWidth = rings.length === 1 ? 36 : rings.length === 2 ? 28 : 22;
  const gap = strokeWidth + 12;

  return (
    <div style={{
      ...zoneStyle(zone),
      flexDirection: 'column',
      alignItems: 'center',
      gap: 16,
      opacity: opacity * exitOpacity,
      transform: `scale(${scale * exitScale})`,
    }}>
      <svg width="400" height="400" viewBox="0 0 400 400">
        {rings.map((ring, i) => {
          const r = baseRadius - i * gap;
          const circumference = 2 * Math.PI * r;
          const maxVal = ring.maxValue ?? 100;
          const fraction = ring.value / maxVal;
          const color = ring.color ?? TKK_GOLD;

          // Stagger each ring slightly
          const staggerFrame = Math.max(0, frame - i * 5);
          const fillProgress = spring({ frame: Math.min(staggerFrame, fillFrames), fps, config: SPRINGS.smooth });
          const offset = circumference * (1 - fraction * fillProgress);

          // Glow pulse when done
          const glowOpacity = isDone ? 0.15 + Math.sin(frame * 0.08 + i * 2) * 0.1 : 0;

          return (
            <React.Fragment key={i}>
              {/* Track */}
              <circle
                cx={cx} cy={cy} r={r}
                fill="none"
                stroke="#1A2030"
                strokeWidth={strokeWidth}
              />
              {/* Filled arc */}
              <circle
                cx={cx} cy={cy} r={r}
                fill="none"
                stroke={color}
                strokeWidth={strokeWidth}
                strokeDasharray={circumference}
                strokeDashoffset={offset}
                strokeLinecap="round"
                transform={`rotate(-90 ${cx} ${cy})`}
                opacity={0.85}
              />
              {/* Glow overlay */}
              {isDone && (
                <circle
                  cx={cx} cy={cy} r={r}
                  fill="none"
                  stroke={color}
                  strokeWidth={strokeWidth + 8}
                  strokeDasharray={circumference}
                  strokeDashoffset={offset}
                  strokeLinecap="round"
                  transform={`rotate(-90 ${cx} ${cy})`}
                  opacity={glowOpacity}
                  style={{ filter: 'blur(6px)' }}
                />
              )}
            </React.Fragment>
          );
        })}

        {/* Center value (show primary ring value) */}
        {rings.length === 1 && (() => {
          const displayVal = Math.round(rings[0].value * spring({ frame: Math.min(frame, fillFrames), fps, config: SPRINGS.smooth }));
          const numStr = displayVal.toLocaleString();
          // Scale font to fit inside ring: ~5 chars at 72px, shrink for longer strings
          const fontSize = Math.min(72, Math.floor(320 / Math.max(numStr.length, 1)));
          const unitSize = Math.min(36, fontSize * 0.5);
          return (
            <>
              <text
                x={cx} y={cy}
                textAnchor="middle"
                dominantBaseline="central"
                fontFamily={FONTS.mono}
                fontSize={fontSize}
                fontWeight="bold"
                fill={rings[0].color ?? TKK_GOLD}
              >
                {numStr}
              </text>
              {unit && (
                <text
                  x={cx} y={cy + fontSize * 0.55}
                  textAnchor="middle"
                  fontFamily={FONTS.body}
                  fontSize={unitSize}
                  fill={TKK_WHITE}
                  opacity={0.7}
                >
                  {unit}
                </text>
              )}
            </>
          );
        })()}
      </svg>

      {/* Labels */}
      <div style={{
        display: 'flex',
        flexDirection: rings.length > 2 ? 'column' : 'row',
        gap: rings.length > 2 ? 8 : 32,
        alignItems: 'center',
      }}>
        {rings.map((ring, i) => {
          const color = ring.color ?? TKK_GOLD;
          const staggerFrame = Math.max(0, frame - i * 5);
          const fillProgress = spring({ frame: Math.min(staggerFrame, fillFrames), fps, config: SPRINGS.smooth });
          const displayVal = Math.round(ring.value * fillProgress);
          return (
            <div key={i} style={{
              display: 'flex',
              alignItems: 'center',
              gap: 10,
            }}>
              <div style={{
                width: 16,
                height: 16,
                borderRadius: 4,
                backgroundColor: color,
                opacity: 0.85,
              }} />
              <div style={{
                fontFamily: FONTS.body,
                fontSize: FONT_SIZE.caption,
                fontWeight: 'bold',
                color: TKK_WHITE,
              }}>
                {ring.label}: <span style={{ color }}>{displayVal.toLocaleString()} {unit}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
