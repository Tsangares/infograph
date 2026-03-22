import React from 'react';
import { useCurrentFrame, spring, interpolate, useVideoConfig } from 'remotion';
import { zoneStyle, type ZoneName, SAFE } from '../lib/zones';
import { TKK_GOLD, TKK_WHITE } from '../lib/colors';
import { FONTS } from '../lib/fonts';
import { FONT_SIZE } from '../lib/typography';
import { useSceneProgress } from '../lib/useSceneProgress';
import { SPRINGS } from '../lib/springs';

interface Bar {
  label: string;
  value: number;
  color?: string;
}

interface BarChartProps {
  bars: Bar[];
  maxValue?: number;
  zone?: ZoneName;
  xLabel?: string;
  yLabel?: string;
}

export const BarChart: React.FC<BarChartProps> = ({
  bars,
  maxValue,
  zone = 'MID',
  xLabel,
  yLabel,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { exit, hold, durationInFrames } = useSceneProgress();

  const max = maxValue ?? Math.max(...bars.map(b => b.value));
  const barHeight = 44;
  const gap = 12;
  const maxLabelChars = Math.max(...bars.map(b => b.label.length));
  const labelWidth = Math.min(SAFE.width * 0.35, Math.max(120, maxLabelChars * 18));

  // Exit: fade + scale
  const exitOpacity = interpolate(exit, [0, 1], [1, 0], { extrapolateRight: 'clamp' });
  const exitScale = interpolate(exit, [0, 1], [1, 0.95], { extrapolateRight: 'clamp' });

  return (
    <div style={{
      ...zoneStyle(zone),
      flexDirection: 'column',
      alignItems: 'flex-start',
      justifyContent: 'center',
      gap,
      padding: '0 20px',
      opacity: exitOpacity,
      transform: `scale(${exitScale})`,
    }}>
      {/* Y-axis label */}
      {yLabel && (
        <div style={{
          position: 'absolute',
          left: -20,
          top: '50%',
          transform: 'rotate(-90deg) translateX(-50%)',
          transformOrigin: '0 0',
          fontFamily: FONTS.body,
          fontSize: FONT_SIZE.source,
          color: TKK_WHITE + '80',
          whiteSpace: 'nowrap',
        }}>
          {yLabel}
        </div>
      )}
      {bars.map((bar, i) => {
        const delay = i * Math.max(2, Math.round(durationInFrames * 0.03));
        const barFrame = Math.max(0, frame - delay);
        const width = spring({
          frame: barFrame,
          fps,
          config: SPRINGS.bar,
        });
        const labelFadeStart = Math.max(4, Math.round(durationInFrames * 0.05));
        const labelFadeEnd = Math.max(labelFadeStart + 4, Math.round(durationInFrames * 0.1));
        const labelOpacity = interpolate(barFrame, [labelFadeStart, labelFadeEnd], [0, 1], {
          extrapolateRight: 'clamp',
        });

        // Hold: subtle shimmer per bar
        const shimmer = 1 + Math.sin((hold * Math.PI * 2) + i * 0.8) * 0.015;

        const barWidth = (bar.value / max) * (SAFE.width - labelWidth - 40);

        return (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12, width: '100%' }}>
            <div style={{
              fontFamily: FONTS.body,
              fontSize: FONT_SIZE.dataValue,
              color: TKK_WHITE + 'CC',
              width: labelWidth,
              textAlign: 'right',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              opacity: labelOpacity,
            }}>
              {bar.label}
            </div>
            <div style={{
              height: barHeight,
              width: barWidth * width * shimmer,
              background: bar.color ?? TKK_GOLD,
              borderRadius: barHeight / 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'flex-end',
              paddingRight: 12,
            }}>
              <span style={{
                fontFamily: FONTS.mono,
                fontSize: FONT_SIZE.dataValue,
                color: '#000',
                fontWeight: 'bold',
                opacity: labelOpacity,
              }}>
                {bar.value.toLocaleString()}
              </span>
            </div>
          </div>
        );
      })}
      {/* X-axis label */}
      {xLabel && (
        <div style={{
          fontFamily: FONTS.body,
          fontSize: FONT_SIZE.source,
          color: TKK_WHITE + '80',
          textAlign: 'center',
          width: '100%',
          marginTop: 8,
        }}>
          {xLabel}
        </div>
      )}
    </div>
  );
};
