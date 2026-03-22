import React from 'react';
import { useCurrentFrame, spring, interpolate, useVideoConfig } from 'remotion';
import { zoneStyle, type ZoneName, SAFE } from '../lib/zones';
import { TKK_GOLD, TKK_WHITE, TKK_DIM } from '../lib/colors';
import { FONTS } from '../lib/fonts';
import { FONT_SIZE } from '../lib/typography';
import { useSceneProgress } from '../lib/useSceneProgress';
import { SPRINGS } from '../lib/springs';

interface TimelineMarker {
  year: string;
  label: string;
  color?: string;
}

interface TimelineProps {
  markers: TimelineMarker[];
  zone?: ZoneName;
  axisLabel?: string;
}

export const Timeline: React.FC<TimelineProps> = ({
  markers,
  zone = 'MID',
  axisLabel,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { exit, hold, durationInFrames } = useSceneProgress();

  const lineWidth = spring({
    frame,
    fps,
    config: { damping: 20, stiffness: 60 },
  });

  // Exit: fade + scale
  const exitOpacity = interpolate(exit, [0, 1], [1, 0], { extrapolateRight: 'clamp' });
  const exitScale = interpolate(exit, [0, 1], [1, 0.95], { extrapolateRight: 'clamp' });

  return (
    <div style={{
      ...zoneStyle(zone),
      flexDirection: 'column',
      gap: 0,
      padding: '0 20px',
      opacity: exitOpacity,
      transform: `scale(${exitScale})`,
    }}>
      {/* Horizontal line */}
      <div style={{
        width: `${lineWidth * 100}%`,
        height: 3,
        background: TKK_DIM,
        borderRadius: 2,
        position: 'relative',
      }}>
        {markers.map((m, i) => {
          const pct = markers.length === 1 ? 0.5 : i / (markers.length - 1);
          const baseDelay = Math.max(4, Math.round(durationInFrames * 0.05));
          const stagger = Math.max(4, Math.round(durationInFrames * 0.06));
          const delay = baseDelay + i * stagger;
          const markerFrame = Math.max(0, frame - delay);
          const scale = spring({
            frame: markerFrame,
            fps,
            config: { damping: 12, stiffness: 120 },
          });
          const opacity = interpolate(markerFrame, [0, 8], [0, 1], {
            extrapolateRight: 'clamp',
          });

          // Hold: gentle pulse glow on marker dots
          const pulse = 1 + Math.sin((hold * Math.PI * 3) + i * 1.2) * 0.06;

          return (
            <div key={i} style={{
              position: 'absolute',
              left: `${pct * 100}%`,
              top: -6,
              transform: `translateX(-50%) scale(${scale})`,
              opacity,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}>
              <div style={{
                width: 18,
                height: 18,
                borderRadius: '50%',
                background: m.color ?? TKK_GOLD,
                border: `2px solid ${TKK_WHITE}`,
                transform: `scale(${pulse})`,
              }} />
              <div style={{
                marginTop: 8,
                fontFamily: FONTS.mono,
                fontSize: FONT_SIZE.dataLabel,
                fontWeight: 'bold',
                color: m.color ?? TKK_GOLD,
                whiteSpace: 'nowrap',
              }}>
                {m.year}
              </div>
              <div style={{
                fontFamily: FONTS.body,
                fontSize: FONT_SIZE.dataValue,
                color: TKK_WHITE + 'BB',
                textAlign: 'center',
                maxWidth: 200,
                lineHeight: 1.2,
              }}>
                {m.label}
              </div>
            </div>
          );
        })}
      </div>
      {axisLabel && (
        <div style={{
          fontFamily: FONTS.body,
          fontSize: FONT_SIZE.source,
          color: TKK_WHITE + '80',
          textAlign: 'center',
          marginTop: 8,
        }}>
          {axisLabel}
        </div>
      )}
    </div>
  );
};
