/**
 * NoiseOverlay — subtle film grain texture for premium broadcast feel.
 * Deterministic noise that shifts slightly each frame.
 * Renders as a full-screen SVG filter overlay at low opacity.
 */
import React from 'react';
import { AbsoluteFill, useCurrentFrame } from 'remotion';
import { WIDTH, HEIGHT } from '../lib/zones';

interface NoiseOverlayProps {
  /** Opacity of the grain (default 0.035 — very subtle) */
  opacity?: number;
  /** Grain movement speed (default 1) */
  speed?: number;
}

export const NoiseOverlay: React.FC<NoiseOverlayProps> = ({
  opacity = 0.035,
  speed = 1,
}) => {
  const frame = useCurrentFrame();
  // Shift the noise seed each frame for organic feel
  const seed = Math.floor(frame * speed * 0.5) % 1000;

  return (
    <AbsoluteFill style={{ pointerEvents: 'none', mixBlendMode: 'overlay' }}>
      <svg width={WIDTH} height={HEIGHT} style={{ opacity }}>
        <defs>
          <filter id={`grain-${seed}`}>
            <feTurbulence
              type="fractalNoise"
              baseFrequency="0.65"
              numOctaves={3}
              seed={seed}
              stitchTiles="stitch"
            />
            <feColorMatrix type="saturate" values="0" />
          </filter>
        </defs>
        <rect
          width={WIDTH}
          height={HEIGHT}
          filter={`url(#grain-${seed})`}
          opacity={1}
        />
      </svg>
    </AbsoluteFill>
  );
};
