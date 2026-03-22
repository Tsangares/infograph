/**
 * ScaleComparison — two objects side by side, one grows dramatically larger.
 *
 * Shows relative magnitude viscerally. "6-cent O-ring vs $2B shuttle."
 * Both start at equal size, then the larger one inflates via spring.
 */
import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';
import { zoneStyle, type ZoneName } from '../lib/zones';
import { TKK_WHITE, TKK_GOLD, TKK_RED, TKK_SURFACE } from '../lib/colors';
import { FONTS } from '../lib/fonts';
import { FONT_SIZE } from '../lib/typography';
import { useSceneProgress } from '../lib/useSceneProgress';
import { SPRINGS } from '../lib/springs';
import { SVG_LIBRARY } from '../lib/svgLibrary';

interface ComparisonItem {
  label: string;
  icon?: string;
  value: number;
  color?: string;
}

interface ScaleComparisonProps {
  left: ComparisonItem;
  right: ComparisonItem;
  unit?: string;
  zone?: ZoneName;
}

export const ScaleComparison: React.FC<ScaleComparisonProps> = ({
  left,
  right,
  unit = '',
  zone = 'MID',
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const { exit } = useSceneProgress();

  // Determine which is bigger
  const maxVal = Math.max(left.value, right.value);
  const minVal = Math.min(left.value, right.value);
  const ratio = Math.min(maxVal / Math.max(0.001, minVal), 3); // cap at 3x visual to prevent overflow

  // Phase 1: both appear equal (first 30% of scene)
  // Phase 2: larger one grows (30-70%)
  const growStart = Math.round(durationInFrames * 0.3);
  const growFrame = Math.max(0, frame - growStart);
  const growProgress = spring({ frame: growFrame, fps, config: SPRINGS.dramatic });

  const baseSize = 120;
  const leftIsLarger = left.value >= right.value;
  const leftScale = leftIsLarger ? 1 + (ratio - 1) * growProgress : 1;
  const rightScale = !leftIsLarger ? 1 + (ratio - 1) * growProgress : 1;

  // Entrance
  const enterOpacity = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: 'clamp' });
  const enterScale = spring({ frame, fps, config: SPRINGS.snappy });

  // Exit
  const exitOpacity = interpolate(exit, [0, 1], [1, 0], { extrapolateRight: 'clamp' });

  const LeftIcon = left.icon ? SVG_LIBRARY[left.icon] : null;
  const RightIcon = right.icon ? SVG_LIBRARY[right.icon] : null;

  const formatValue = (v: number) =>
    v >= 1_000_000_000 ? `$${(v / 1_000_000_000).toFixed(0)}B` :
    v >= 1_000_000 ? `${(v / 1_000_000).toFixed(1)}M` :
    v >= 1_000 ? `${(v / 1_000).toFixed(v >= 10_000 ? 0 : 1)}K` :
    v < 1 ? `${v}` :
    v.toLocaleString();

  const renderItem = (
    item: ComparisonItem,
    IconComp: React.FC<{ color?: string; size?: number }> | null,
    scale: number,
  ) => {
    const color = item.color ?? TKK_GOLD;
    const float = Math.sin(frame * 0.04) * 4;
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 12,
        maxWidth: 350,
      }}>
        {/* Icon scales, text doesn't */}
        <div style={{
          width: baseSize,
          height: baseSize,
          borderRadius: 20,
          backgroundColor: TKK_SURFACE,
          border: `3px solid ${color}44`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: `0 0 ${16 + scale * 8}px ${color}${Math.round(Math.min(scale * 15, 255)).toString(16).padStart(2, '0')}`,
          transform: `scale(${scale}) translateY(${float}px)`,
        }}>
          {IconComp ? (
            <IconComp color={color} size={baseSize * 0.6} />
          ) : (
            <div style={{
              fontFamily: FONTS.mono,
              fontSize: FONT_SIZE.subtitle,
              color,
              fontWeight: 'bold',
            }}>
              {formatValue(item.value)}
            </div>
          )}
        </div>
        <div style={{
          fontFamily: FONTS.mono,
          fontSize: FONT_SIZE.body,
          fontWeight: 'bold',
          color,
          textAlign: 'center',
        }}>
          {formatValue(item.value)}{unit}
        </div>
        <div style={{
          fontFamily: FONTS.body,
          fontSize: FONT_SIZE.caption,
          color: TKK_WHITE + 'CC',
          textAlign: 'center',
          fontWeight: 'bold',
          maxWidth: 200,
        }}>
          {item.label}
        </div>
      </div>
    );
  };

  return (
    <div style={{
      ...zoneStyle(zone),
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-around',
      opacity: enterOpacity * exitOpacity,
      transform: `scale(${enterScale})`,
    }}>
      {renderItem(left, LeftIcon, leftScale)}

      {/* VS divider */}
      <div style={{
        fontFamily: FONTS.headline,
        fontSize: FONT_SIZE.subtitle,
        color: TKK_WHITE + '55',
        opacity: interpolate(frame, [15, 25], [0, 1], { extrapolateRight: 'clamp' }),
      }}>
        VS
      </div>

      {renderItem(right, RightIcon, rightScale)}
    </div>
  );
};
