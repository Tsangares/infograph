/**
 * GaugeMeter — semicircular arc gauge with color zones.
 *
 * Replaces Counter for threshold/percentage stories.
 * Sweeps from min to target value with spring physics.
 * Color zones (green → yellow → red) show danger levels.
 */
import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';
import { zoneStyle, type ZoneName } from '../lib/zones';
import { TKK_GOLD, TKK_WHITE, TKK_GREEN, TKK_RED } from '../lib/colors';
import { FONTS } from '../lib/fonts';
import { FONT_SIZE } from '../lib/typography';
import { useSceneProgress } from '../lib/useSceneProgress';
import { SPRINGS } from '../lib/springs';

interface GaugeZone {
  from: number;
  to: number;
  color: string;
}

interface GaugeMeterProps {
  value: number;
  maxValue?: number;
  unit?: string;
  label?: string;
  zones?: GaugeZone[];
  zone?: ZoneName;
  sweepDuration?: number;
  color?: string;
}

const ARC_START = Math.PI;        // left side (180°)
const ARC_END = 0;                // right side (0°)
const RADIUS = 260;
const STROKE_WIDTH = 40;
const CX = 350;
const CY = 310;

function describeArc(startAngle: number, endAngle: number, r: number): string {
  const start = { x: CX + r * Math.cos(startAngle), y: CY - r * Math.sin(startAngle) };
  const end = { x: CX + r * Math.cos(endAngle), y: CY - r * Math.sin(endAngle) };
  const diff = startAngle - endAngle;
  const largeArc = Math.abs(diff) > Math.PI ? 1 : 0;
  // Sweep clockwise (0) since we go from left to right
  return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 0 ${end.x} ${end.y}`;
}

export const GaugeMeter: React.FC<GaugeMeterProps> = ({
  value,
  maxValue = 100,
  unit = '',
  label,
  zones,
  zone = 'MID',
  sweepDuration = 0.6,
  color = TKK_GOLD,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const { exit } = useSceneProgress();

  const sweepFrames = Math.round(durationInFrames * sweepDuration);
  const progress = spring({ frame: Math.min(frame, sweepFrames), fps, config: SPRINGS.smooth });

  const fraction = (value / maxValue) * progress;
  const needleAngle = ARC_START - fraction * Math.PI;

  const currentValue = interpolate(frame, [0, Math.max(1, sweepFrames)], [0, value], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Needle tremble after sweep completes
  const isDone = frame > sweepFrames;
  const trembleOffset = isDone ? Math.sin(frame * 0.4) * 0.015 : 0;
  const needleAngleFinal = needleAngle + trembleOffset;

  const needleX = CX + (RADIUS - 20) * Math.cos(needleAngleFinal);
  const needleY = CY - (RADIUS - 20) * Math.sin(needleAngleFinal);

  // Entrance
  const opacity = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: 'clamp' });
  const scale = spring({ frame, fps, config: SPRINGS.snappy });

  // Exit
  const exitOpacity = interpolate(exit, [0, 1], [1, 0], { extrapolateRight: 'clamp' });
  const exitScale = interpolate(exit, [0, 1], [1, 0.9], { extrapolateRight: 'clamp' });

  const formatted = Math.abs(currentValue) >= 1000
    ? Math.round(currentValue).toLocaleString()
    : Number.isInteger(value) ? Math.round(currentValue).toString() : currentValue.toFixed(1);

  // Default zones if none provided
  const defaultZones: GaugeZone[] = zones ?? [
    { from: 0, to: maxValue * 0.5, color: TKK_GREEN },
    { from: maxValue * 0.5, to: maxValue * 0.75, color: '#F59E0B' },
    { from: maxValue * 0.75, to: maxValue, color: TKK_RED },
  ];

  // Expand vertically to give the gauge room
  const baseStyle = zoneStyle(zone);
  const expandedStyle: React.CSSProperties = {
    ...baseStyle,
    top: (baseStyle.top as number) - 80,
    height: (baseStyle.height as number) + 160,
  };

  return (
    <div style={{
      ...expandedStyle,
      flexDirection: 'column',
      gap: 8,
      opacity: opacity * exitOpacity,
      transform: `scale(${scale * exitScale})`,
    }}>
      <svg viewBox="40 20 620 380" style={{ width: '100%', maxWidth: 800 }}>
        {/* Background track */}
        <path
          d={describeArc(ARC_START, ARC_END, RADIUS)}
          fill="none"
          stroke="#1A2030"
          strokeWidth={STROKE_WIDTH}
          strokeLinecap="round"
        />

        {/* Color zone arcs */}
        {defaultZones.map((z, i) => {
          const zStart = ARC_START - (z.from / maxValue) * Math.PI;
          const zEnd = ARC_START - (Math.min(z.to, value * progress) / maxValue) * Math.PI;
          if (z.from >= value * progress) return null;
          return (
            <path
              key={i}
              d={describeArc(zStart, zEnd, RADIUS)}
              fill="none"
              stroke={z.color}
              strokeWidth={STROKE_WIDTH}
              strokeLinecap="round"
              opacity={0.85}
            />
          );
        })}

        {/* Needle */}
        <line
          x1={CX}
          y1={CY}
          x2={needleX}
          y2={needleY}
          stroke={color}
          strokeWidth={6}
          strokeLinecap="round"
        />
        <circle cx={CX} cy={CY} r={14} fill={color} />

        {/* Glow on needle tip */}
        {isDone && (
          <circle
            cx={needleX}
            cy={needleY}
            r={8 + Math.sin(frame * 0.1) * 3}
            fill={color}
            opacity={0.3 + Math.sin(frame * 0.1) * 0.15}
          />
        )}

        {/* Value inside the gauge arc */}
        <text
          x={CX}
          y={CY + 65}
          textAnchor="middle"
          fontFamily={FONTS.mono}
          fontSize={80}
          fontWeight="bold"
          fill={color}
          letterSpacing={3}
        >
          {formatted}{unit}
        </text>
      </svg>

      {label && (
        <div style={{
          fontFamily: FONTS.body,
          fontSize: FONT_SIZE.body,
          color: TKK_WHITE + 'CC',
          textAlign: 'center',
          marginTop: 4,
        }}>
          {label}
        </div>
      )}
    </div>
  );
};
