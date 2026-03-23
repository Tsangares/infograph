/**
 * MapHighlight — simplified map with animated location highlights.
 * Shows geographic context with pulsing pin markers.
 * Uses simplified SVG paths for world regions (no external maps needed).
 */
import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';
import { zoneStyle, type ZoneName } from '../lib/zones';
import { SPRINGS } from '../lib/springs';
import { FONTS } from '../lib/fonts';

interface MapPin {
  /** X position as fraction (0-1) of map width */
  x: number;
  /** Y position as fraction (0-1) of map height */
  y: number;
  label: string;
  color?: string;
  /** Delay in frames before this pin appears */
  delay?: number;
}

interface MapHighlightProps {
  pins: MapPin[];
  zone?: ZoneName;
  size?: number;
  /** Color of the map outline */
  mapColor?: string;
  /** Accent color for pins (overridden by individual pin colors) */
  accentColor?: string;
  /** Show connecting lines between pins */
  connectPins?: boolean;
}

// Simplified world map continents as SVG paths (1000x500 viewBox)
const WORLD_PATHS = [
  // North America (simplified)
  'M 120 120 C 140 90 200 80 240 95 L 260 110 C 270 130 265 160 250 180 L 220 200 C 200 210 180 220 160 210 L 130 180 C 115 160 110 140 120 120 Z',
  // South America (simplified)
  'M 200 230 C 210 225 230 230 240 250 L 250 290 C 255 320 250 350 235 370 L 220 380 C 210 375 200 360 195 340 L 190 300 C 188 270 192 245 200 230 Z',
  // Europe (simplified)
  'M 440 90 C 460 85 490 90 500 100 L 510 120 C 515 135 510 150 500 155 L 480 160 C 465 155 450 145 445 130 L 440 110 C 438 100 438 95 440 90 Z',
  // Africa (simplified)
  'M 450 170 C 465 165 490 170 500 185 L 510 220 C 515 260 510 300 500 330 L 485 350 C 475 355 460 350 455 335 L 445 290 C 440 250 442 210 450 170 Z',
  // Asia (simplified)
  'M 520 80 C 560 70 620 75 670 85 L 700 100 C 720 115 730 140 720 160 L 690 180 C 660 190 620 185 590 175 L 550 155 C 530 140 520 120 520 100 L 520 80 Z',
  // Australia (simplified)
  'M 700 300 C 720 295 750 300 765 310 L 775 325 C 778 340 770 355 755 360 L 730 355 C 715 350 705 340 700 325 L 698 310 C 698 305 700 300 700 300 Z',
];

export const MapHighlight: React.FC<MapHighlightProps> = ({
  pins,
  zone = 'MID',
  size = 400,
  mapColor = '#EAEAF015',
  accentColor = '#FFD700',
  connectPins = false,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const mapW = 1000;
  const mapH = 500;
  const aspect = mapW / mapH;
  const displayW = size;
  const displayH = size / aspect;

  // Entry
  const entryOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const entryScale = spring({ frame, fps, config: SPRINGS.gentle });

  // Exit
  const exitStart = durationInFrames - 12;
  const exitOpacity = interpolate(frame, [exitStart, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Map draw-in animation
  const mapDrawProgress = spring({ frame, fps, config: SPRINGS.smooth, durationInFrames: 30 });

  return (
    <div style={{
      ...zoneStyle(zone),
      flexDirection: 'column',
      alignItems: 'center',
      opacity: entryOpacity * exitOpacity,
      transform: `scale(${entryScale})`,
    }}>
      <svg
        viewBox={`0 0 ${mapW} ${mapH}`}
        width={displayW}
        height={displayH}
        style={{ overflow: 'visible' }}
      >
        {/* Map outlines */}
        {WORLD_PATHS.map((path, i) => (
          <path
            key={`map-${i}`}
            d={path}
            fill={mapColor}
            stroke="#EAEAF020"
            strokeWidth={1.5}
            strokeDasharray={3000}
            strokeDashoffset={3000 * (1 - mapDrawProgress)}
          />
        ))}

        {/* Connecting lines */}
        {connectPins && pins.length > 1 && pins.map((pin, i) => {
          if (i === 0) return null;
          const prev = pins[i - 1];
          const lineDelay = Math.max(pin.delay ?? 0, prev.delay ?? 0) + 10;
          const lineFrame = Math.max(0, frame - lineDelay);
          const lineProgress = spring({ frame: lineFrame, fps, config: SPRINGS.smooth });

          const x1 = prev.x * mapW;
          const y1 = prev.y * mapH;
          const x2 = pin.x * mapW;
          const y2 = pin.y * mapH;

          return (
            <line
              key={`line-${i}`}
              x1={x1} y1={y1}
              x2={x1 + (x2 - x1) * lineProgress}
              y2={y1 + (y2 - y1) * lineProgress}
              stroke={`${accentColor}44`}
              strokeWidth={1.5}
              strokeDasharray="6 4"
            />
          );
        })}

        {/* Pin markers */}
        {pins.map((pin, i) => {
          const pinDelay = pin.delay ?? i * 12;
          const pinFrame = Math.max(0, frame - pinDelay);
          const pinColor = pin.color ?? accentColor;

          // Pin drop animation
          const dropProgress = spring({ frame: pinFrame, fps, config: SPRINGS.bouncy });
          const pinOpacity = interpolate(pinFrame, [0, 5], [0, 1], { extrapolateRight: 'clamp' });
          const pinScale = interpolate(dropProgress, [0, 1], [2.5, 1]);

          // Pulse ring
          const pulseFrame = Math.max(0, pinFrame - 15);
          const pulseScale = 1 + (pulseFrame * 0.05) % 2;
          const pulseOpacity = Math.max(0, 0.5 - ((pulseFrame * 0.05) % 2) * 0.25);

          const px = pin.x * mapW;
          const py = pin.y * mapH;

          return (
            <g key={`pin-${i}`} opacity={pinOpacity}>
              {/* Pulse ring */}
              {pinFrame > 15 && (
                <circle
                  cx={px} cy={py}
                  r={12 * pulseScale}
                  fill="none"
                  stroke={pinColor}
                  strokeWidth={1.5}
                  opacity={pulseOpacity}
                />
              )}

              {/* Pin dot */}
              <circle
                cx={px} cy={py}
                r={8}
                fill={pinColor}
                stroke="#080A10"
                strokeWidth={2}
                transform={`translate(0, ${(1 - dropProgress) * -30})`}
                style={{ transformOrigin: `${px}px ${py}px` }}
              />

              {/* Glow */}
              <circle
                cx={px} cy={py}
                r={15}
                fill={`${pinColor}22`}
                transform={`scale(${pinScale})`}
                style={{ transformOrigin: `${px}px ${py}px` }}
              />

              {/* Label */}
              <text
                x={px}
                y={py - 22}
                textAnchor="middle"
                fill="#EAEAF0"
                fontSize={16}
                fontFamily="Inter, sans-serif"
                fontWeight="bold"
                opacity={interpolate(pinFrame, [8, 20], [0, 1], { extrapolateRight: 'clamp' })}
              >
                {pin.label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};
