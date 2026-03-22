/**
 * CauseEffect — domino-style chain reaction visualization.
 *
 * 3-6 labeled dominoes topple sequentially, each triggering the next.
 * Visual grammar of inevitability: "one thing led to another."
 */
import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';
import { zoneStyle, type ZoneName } from '../lib/zones';
import { TKK_WHITE, TKK_GOLD, TKK_SURFACE } from '../lib/colors';
import { FONTS } from '../lib/fonts';
import { FONT_SIZE } from '../lib/typography';
import { useSceneProgress } from '../lib/useSceneProgress';
import { SPRINGS } from '../lib/springs';
import { SVG_LIBRARY } from '../lib/svgLibrary';

interface Domino {
  label: string;
  icon?: string;
  color?: string;
}

interface CauseEffectProps {
  dominoes: Domino[];
  zone?: ZoneName;
  chainSpeed?: number;
}

export const CauseEffect: React.FC<CauseEffectProps> = ({
  dominoes,
  zone = 'MID',
  chainSpeed = 0.12,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const { exit } = useSceneProgress();

  const n = dominoes.length;
  const chainFrames = Math.round(chainSpeed * fps);

  // First domino starts falling after 20% of scene
  const firstFallFrame = Math.round(durationInFrames * 0.2);

  // Entrance
  const enterOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const enterScale = spring({ frame, fps, config: SPRINGS.snappy });

  // Exit
  const exitOpacity = interpolate(exit, [0, 1], [1, 0], { extrapolateRight: 'clamp' });

  const dominoWidth = Math.min(120, 780 / n);
  const dominoHeight = dominoWidth * 2.2;
  const spacing = Math.min(160, 800 / n);

  return (
    <div style={{
      ...zoneStyle(zone),
      flexDirection: 'row',
      alignItems: 'flex-end',
      justifyContent: 'center',
      gap: spacing - dominoWidth,
      opacity: enterOpacity * exitOpacity,
      transform: `scale(${enterScale})`,
      overflow: 'visible',
      paddingLeft: 20,
      paddingRight: 20,
    }}>
      {dominoes.map((domino, i) => {
        const fallStart = firstFallFrame + i * chainFrames;
        const fallFrame = Math.max(0, frame - fallStart);
        const fallProgress = spring({ frame: fallFrame, fps, config: { damping: 12, stiffness: 120, mass: 1 } });

        // Domino tilts forward (0° upright → 60° fallen)
        const rotation = fallProgress * 60;
        const isFalling = frame >= fallStart;
        const isFallen = fallProgress > 0.9;

        const color = domino.color ?? TKK_GOLD;
        const IconComponent = domino.icon ? SVG_LIBRARY[domino.icon] : null;

        // Pre-fall: slight sway
        const preSway = !isFalling ? Math.sin(frame * 0.06 + i * 2) * 1.5 : 0;

        // Impact flash when domino hits the next one
        const impactOpacity = (isFalling && !isFallen)
          ? Math.sin(fallProgress * Math.PI) * 0.3
          : 0;

        return (
          <div key={i} style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 8,
            zIndex: isFallen ? 1 : n - i + 5,
            overflow: 'visible',
          }}>
            {/* Domino piece */}
            <div style={{
              width: dominoWidth,
              height: dominoHeight,
              borderRadius: 8,
              backgroundColor: TKK_SURFACE,
              border: `2px solid ${color}44`,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 6,
              transformOrigin: 'bottom center',
              transform: `rotate(${rotation + preSway}deg)`,
              boxShadow: `0 0 ${impactOpacity * 30}px ${color}`,
            }}>
              {IconComponent && (
                <IconComponent color={color} size={dominoWidth * 0.45} />
              )}
              {!IconComponent && (
                <div style={{
                  width: dominoWidth * 0.35,
                  height: dominoWidth * 0.35,
                  borderRadius: '50%',
                  backgroundColor: color + '44',
                  border: `2px solid ${color}`,
                }} />
              )}
            </div>

            {/* Label */}
            <div style={{
              fontFamily: FONTS.body,
              fontSize: Math.min(FONT_SIZE.caption, dominoWidth * 0.36),
              fontWeight: 'bold',
              color: isFallen ? color : TKK_WHITE + 'CC',
              textAlign: 'center',
              maxWidth: dominoWidth + 20,
              lineHeight: 1.2,
              opacity: interpolate(frame, [0, 20 + i * 3], [0, 1], { extrapolateRight: 'clamp' }),
            }}>
              {domino.label}
            </div>
          </div>
        );
      })}
    </div>
  );
};
