import React from 'react';
import { useCurrentFrame, interpolate, spring, useVideoConfig, Img } from 'remotion';
import { staticFile } from '../lib/static';
import { SAFE, ZONES, WIDTH } from '../lib/zones';
import { TKK_WHITE, TKK_DIM } from '../lib/colors';
import { FONTS } from '../lib/fonts';
import { useSceneProgress } from '../lib/useSceneProgress';

interface SplitCompareProps {
  leftImage: string;
  rightImage: string;
  leftLabel?: string;
  rightLabel?: string;
}

export const SplitCompare: React.FC<SplitCompareProps> = ({
  leftImage,
  rightImage,
  leftLabel,
  rightLabel,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const { exit } = useSceneProgress();

  // Divider slides from left to center
  const dividerX = interpolate(frame, [10, 40], [0, 0.5], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const opacity = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: 'clamp' });
  const labelOpacity = interpolate(frame, [30, 45], [0, 1], { extrapolateRight: 'clamp' });

  // Exit: fade + slight scale
  const exitOpacity = interpolate(exit, [0, 1], [1, 0], { extrapolateRight: 'clamp' });
  const exitScale = interpolate(exit, [0, 1], [1, 0.96], { extrapolateRight: 'clamp' });

  const midZone = ZONES.MID;
  const imgHeight = midZone.range[1] - midZone.range[0] + 200;
  const imgTop = midZone.range[0] - 100;

  return (
    <div style={{
      position: 'absolute',
      top: imgTop,
      left: SAFE.left,
      width: SAFE.width,
      height: imgHeight,
      overflow: 'hidden',
      borderRadius: 16,
      opacity: opacity * exitOpacity,
      transform: `scale(${exitScale})`,
    }}>
      {/* Left image (full width, clipped by divider) */}
      <div style={{
        position: 'absolute',
        inset: 0,
        clipPath: `inset(0 ${(1 - dividerX) * 100}% 0 0)`,
      }}>
        <Img src={staticFile(leftImage)} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
      </div>

      {/* Right image */}
      <div style={{
        position: 'absolute',
        inset: 0,
        clipPath: `inset(0 0 0 ${dividerX * 100}%)`,
      }}>
        <Img src={staticFile(rightImage)} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
      </div>

      {/* Divider line */}
      <div style={{
        position: 'absolute',
        left: `${dividerX * 100}%`,
        top: 0,
        bottom: 0,
        width: 4,
        background: TKK_WHITE,
        transform: 'translateX(-50%)',
        boxShadow: '0 0 12px rgba(0,0,0,0.5)',
      }} />

      {/* Labels */}
      {leftLabel && (
        <div style={{
          position: 'absolute',
          bottom: 16,
          left: 16,
          opacity: labelOpacity,
          fontFamily: FONTS.body,
          fontWeight: 'bold',
          fontSize: 28,
          color: TKK_WHITE,
          textShadow: '0 2px 8px rgba(0,0,0,0.8)',
        }}>
          {leftLabel}
        </div>
      )}
      {rightLabel && (
        <div style={{
          position: 'absolute',
          bottom: 16,
          right: 16,
          opacity: labelOpacity,
          fontFamily: FONTS.body,
          fontWeight: 'bold',
          fontSize: 28,
          color: TKK_WHITE,
          textShadow: '0 2px 8px rgba(0,0,0,0.8)',
        }}>
          {rightLabel}
        </div>
      )}
    </div>
  );
};
