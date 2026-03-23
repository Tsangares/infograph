/**
 * AnimatedPieChart — pie/donut chart with spring-driven segment growth.
 * Segments grow sequentially for dramatic reveal.
 */
import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';
import { zoneStyle, type ZoneName } from '../lib/zones';
import { SPRINGS } from '../lib/springs';
import { FONTS } from '../lib/fonts';
import { FONT_SIZE } from '../lib/typography';

interface PieSegment {
  value: number;
  label: string;
  color: string;
}

interface AnimatedPieChartProps {
  segments: PieSegment[];
  zone?: ZoneName;
  size?: number;
  /** Inner radius for donut style (0 = full pie, 0.6 = donut) */
  innerRadius?: number;
  /** Center label text */
  centerLabel?: string;
  /** Center value text */
  centerValue?: string;
  /** Show percentage labels on segments */
  showLabels?: boolean;
}

function polarToCartesian(cx: number, cy: number, r: number, angleDeg: number) {
  const rad = ((angleDeg - 90) * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

function describeArc(cx: number, cy: number, r: number, startAngle: number, endAngle: number) {
  const start = polarToCartesian(cx, cy, r, endAngle);
  const end = polarToCartesian(cx, cy, r, startAngle);
  const largeArc = endAngle - startAngle <= 180 ? 0 : 1;
  return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 0 ${end.x} ${end.y}`;
}

export const AnimatedPieChart: React.FC<AnimatedPieChartProps> = ({
  segments,
  zone = 'MID',
  size = 280,
  innerRadius = 0.55,
  centerLabel,
  centerValue,
  showLabels = true,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const total = segments.reduce((sum, s) => sum + s.value, 0);
  const cx = size / 2;
  const cy = size / 2;
  const outerR = size / 2 - 10;
  const innerR = outerR * innerRadius;
  const midR = (outerR + innerR) / 2;

  // Entry
  const entryOpacity = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: 'clamp' });
  const entryScale = spring({ frame, fps, config: SPRINGS.dramatic });

  // Exit
  const exitStart = durationInFrames - 12;
  const exitOpacity = interpolate(frame, [exitStart, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Stagger each segment
  const growDuration = Math.round(durationInFrames * 0.5);
  const segmentDelay = growDuration / (segments.length + 1);

  let currentAngle = 0;
  const arcs = segments.map((seg, i) => {
    const targetAngle = (seg.value / total) * 360;
    const segFrame = Math.max(0, frame - Math.round(segmentDelay * i));
    const segProgress = spring({
      frame: segFrame,
      fps,
      config: SPRINGS.smooth,
      durationInFrames: Math.round(segmentDelay * 2),
    });

    const animatedAngle = targetAngle * segProgress;
    const startAngle = currentAngle;
    const endAngle = currentAngle + Math.max(0.1, animatedAngle);
    currentAngle += targetAngle;

    // Label position at midpoint of arc
    const labelAngle = startAngle + animatedAngle / 2;
    const labelPos = polarToCartesian(cx, cy, midR + 30, labelAngle);
    const pct = Math.round((seg.value / total) * 100);

    return { seg, startAngle, endAngle: Math.min(endAngle, startAngle + 359.9), labelPos, pct, segProgress, i };
  });

  // Glow pulse on hold
  const holdGlow = Math.sin(frame * 0.05) * 0.3 + 0.7;

  // Center label entry
  const centerFrame = Math.max(0, frame - growDuration);
  const centerOpacity = interpolate(centerFrame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <div style={{
      ...zoneStyle(zone),
      flexDirection: 'column',
      alignItems: 'center',
      gap: 16,
      opacity: entryOpacity * exitOpacity,
      transform: `scale(${entryScale})`,
    }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ overflow: 'visible' }}>
        {/* Background circle */}
        <circle cx={cx} cy={cy} r={outerR} fill="none" stroke="#EAEAF015" strokeWidth={outerR - innerR} />

        {/* Animated segments */}
        {arcs.map(({ seg, startAngle, endAngle, labelPos, pct, segProgress, i }) => (
          <React.Fragment key={i}>
            {/* Segment arc */}
            <path
              d={innerRadius > 0
                ? `${describeArc(cx, cy, outerR, startAngle, endAngle)} L ${polarToCartesian(cx, cy, innerR, endAngle).x} ${polarToCartesian(cx, cy, innerR, endAngle).y} ${describeArc(cx, cy, innerR, endAngle, startAngle).replace('M', 'A').replace(/A\s/, '')} Z`
                : `${describeArc(cx, cy, outerR, startAngle, endAngle)} L ${cx} ${cy} Z`
              }
              fill={seg.color}
              fillOpacity={0.8 + holdGlow * 0.2}
              stroke="#080A10"
              strokeWidth={2}
            />

            {/* Percentage label */}
            {showLabels && segProgress > 0.5 && pct >= 5 && (
              <text
                x={labelPos.x}
                y={labelPos.y}
                textAnchor="middle"
                dominantBaseline="middle"
                fill="#EAEAF0"
                fontSize={24}
                fontFamily="Inter, sans-serif"
                fontWeight="bold"
                opacity={interpolate(segProgress, [0.5, 0.8], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })}
              >
                {pct}%
              </text>
            )}
          </React.Fragment>
        ))}

        {/* Center text */}
        {(centerLabel || centerValue) && (
          <g opacity={centerOpacity}>
            {centerValue && (
              <text
                x={cx} y={centerLabel ? cy - 10 : cy}
                textAnchor="middle" dominantBaseline="middle"
                fill="#EAEAF0" fontSize={36} fontFamily="Bebas Neue, sans-serif" fontWeight="bold"
              >
                {centerValue}
              </text>
            )}
            {centerLabel && (
              <text
                x={cx} y={centerValue ? cy + 20 : cy}
                textAnchor="middle" dominantBaseline="middle"
                fill="#EAEAF088" fontSize={18} fontFamily="Inter, sans-serif"
              >
                {centerLabel}
              </text>
            )}
          </g>
        )}
      </svg>

      {/* Legend below chart */}
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', justifyContent: 'center', maxWidth: 600 }}>
        {segments.map((seg, i) => (
          <div key={i} style={{
            display: 'flex', alignItems: 'center', gap: 6,
            opacity: interpolate(Math.max(0, frame - i * 8), [0, 12], [0, 1], { extrapolateRight: 'clamp' }),
          }}>
            <div style={{ width: 10, height: 10, borderRadius: '50%', backgroundColor: seg.color }} />
            <span style={{ fontFamily: 'Inter, sans-serif', fontSize: 22, color: '#EAEAF0CC' }}>{seg.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
