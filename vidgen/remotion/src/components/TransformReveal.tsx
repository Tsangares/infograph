/**
 * TransformReveal — Object A morphs/transforms into Object B.
 *
 * Perfect for mystery arc betrayal moments. Rocket → explosion.
 * Person → skull. Wave → desert. Four effects available.
 */
import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';
import { zoneStyle, type ZoneName } from '../lib/zones';
import { TKK_WHITE, TKK_GOLD } from '../lib/colors';
import { FONTS } from '../lib/fonts';
import { FONT_SIZE } from '../lib/typography';
import { useSceneProgress } from '../lib/useSceneProgress';
import { SPRINGS } from '../lib/springs';
import { SVG_LIBRARY } from '../lib/svgLibrary';

interface TransformItem {
  icon: string;
  label?: string;
  color?: string;
}

interface TransformRevealProps {
  from: TransformItem;
  to: TransformItem;
  effect?: 'crossfade' | 'shatter' | 'shrinkGrow' | 'glitch';
  transformAt?: number;
  zone?: ZoneName;
}

export const TransformReveal: React.FC<TransformRevealProps> = ({
  from,
  to,
  effect = 'crossfade',
  transformAt = 0.5,
  zone = 'MID',
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const { exit } = useSceneProgress();

  const transformFrame = Math.round(durationInFrames * transformAt);
  const transitionDuration = 20; // frames for the morph
  const transformProgress = interpolate(
    frame,
    [transformFrame, transformFrame + transitionDuration],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  const FromIcon = SVG_LIBRARY[from.icon];
  const ToIcon = SVG_LIBRARY[to.icon];

  const enterOpacity = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: 'clamp' });
  const enterScale = spring({ frame, fps, config: SPRINGS.dramatic });
  const exitOpacity = interpolate(exit, [0, 1], [1, 0], { extrapolateRight: 'clamp' });
  const exitScale = interpolate(exit, [0, 1], [1, 0.9], { extrapolateRight: 'clamp' });

  const iconSize = 180;
  const fromColor = from.color ?? TKK_GOLD;
  const toColor = to.color ?? '#EF4444';

  // Effect-specific transforms
  let fromOpacity = 1 - transformProgress;
  let fromScale = 1;
  let fromRotate = 0;
  let toOpacity = transformProgress;
  let toScale = 1;
  let shakeX = 0;
  let shakeY = 0;

  switch (effect) {
    case 'crossfade':
      // Simple cross-dissolve
      break;
    case 'shatter': {
      fromScale = 1 + transformProgress * 0.3;
      fromRotate = transformProgress * 15;
      fromOpacity = 1 - transformProgress;
      toScale = interpolate(transformProgress, [0.3, 1], [0.5, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
      toOpacity = interpolate(transformProgress, [0.3, 1], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
      // Shake during transition
      if (transformProgress > 0 && transformProgress < 1) {
        const intensity = Math.sin(transformProgress * Math.PI) * 8;
        shakeX = Math.sin(frame * 2.5) * intensity;
        shakeY = Math.cos(frame * 3.1) * intensity;
      }
      break;
    }
    case 'shrinkGrow':
      fromScale = 1 - transformProgress;
      fromOpacity = 1 - transformProgress;
      toScale = transformProgress;
      toOpacity = transformProgress;
      break;
    case 'glitch': {
      // Rapid flickering + offset during transition
      const flickerRate = Math.sin(frame * 4) > 0 ? 1 : 0;
      if (transformProgress > 0 && transformProgress < 1) {
        fromOpacity = flickerRate * (1 - transformProgress);
        toOpacity = (1 - flickerRate) * transformProgress + (transformProgress > 0.7 ? 1 : 0);
        shakeX = (Math.sin(frame * 127.1) > 0 ? 1 : -1) * 6 * Math.sin(transformProgress * Math.PI);
      } else {
        fromOpacity = transformProgress < 0.5 ? 1 : 0;
        toOpacity = transformProgress >= 0.5 ? 1 : 0;
      }
      break;
    }
  }

  // Float motion
  const floatY = Math.sin(frame * 0.04) * 6;

  return (
    <div style={{
      ...zoneStyle(zone),
      flexDirection: 'column',
      alignItems: 'center',
      gap: 16,
      opacity: enterOpacity * exitOpacity,
      transform: `scale(${enterScale * exitScale}) translate(${shakeX}px, ${shakeY}px)`,
    }}>
      {/* Icon container */}
      <div style={{
        position: 'relative',
        width: iconSize,
        height: iconSize,
        transform: `translateY(${floatY}px)`,
      }}>
        {/* From icon */}
        {FromIcon && fromOpacity > 0.01 && (
          <div style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            opacity: fromOpacity,
            transform: `scale(${fromScale}) rotate(${fromRotate}deg)`,
            filter: `drop-shadow(0 0 12px ${fromColor}55)`,
          }}>
            <FromIcon color={fromColor} size={iconSize} />
          </div>
        )}

        {/* To icon */}
        {ToIcon && toOpacity > 0.01 && (
          <div style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            opacity: toOpacity,
            transform: `scale(${toScale})`,
            filter: `drop-shadow(0 0 16px ${toColor}66)`,
          }}>
            <ToIcon color={toColor} size={iconSize} />
          </div>
        )}
      </div>

      {/* Labels */}
      <div style={{
        fontFamily: FONTS.body,
        fontSize: FONT_SIZE.body,
        fontWeight: 'bold',
        color: TKK_WHITE,
        textAlign: 'center',
      }}>
        {transformProgress < 0.5 ? (
          <span style={{ color: fromColor }}>{from.label}</span>
        ) : (
          <span style={{ color: toColor }}>{to.label}</span>
        )}
      </div>
    </div>
  );
};
