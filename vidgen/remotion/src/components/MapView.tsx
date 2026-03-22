import React from 'react';
import { useCurrentFrame, interpolate, spring, useVideoConfig, Img } from 'remotion';
import { staticFile } from '../lib/static';
import { zoneStyle, type ZoneName } from '../lib/zones';
import { TKK_RED, TKK_WHITE } from '../lib/colors';
import { FONTS } from '../lib/fonts';
import { FONT_SIZE } from '../lib/typography';
import { useSceneProgress } from '../lib/useSceneProgress';
import { SPRINGS } from '../lib/springs';

interface Marker {
  x: number;
  y: number;
  label: string;
  color?: string;
  delay?: number;
}

interface MapViewProps {
  image: string;
  markers?: Marker[];
  zone?: ZoneName;
}

export const MapView: React.FC<MapViewProps> = ({
  image,
  markers = [],
  zone = 'MID',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { exit, hold } = useSceneProgress();

  const mapOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });

  // Exit: fade
  const exitOpacity = interpolate(exit, [0, 1], [1, 0], { extrapolateRight: 'clamp' });

  return (
    <div style={{
      ...zoneStyle(zone),
      overflow: 'hidden',
      borderRadius: 12,
      opacity: mapOpacity * exitOpacity,
    }}>
      <div style={{ position: 'relative', width: '100%', height: '100%' }}>
        <Img
          src={staticFile(image)}
          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
        />
        {markers.map((marker, i) => {
          const delayFrames = Math.round((marker.delay ?? i * 0.3) * fps);
          const markerFrame = Math.max(0, frame - 15 - delayFrames);
          const markerScale = spring({
            frame: markerFrame,
            fps,
            config: SPRINGS.marker,
          });
          const markerOpacity = interpolate(markerFrame, [0, 5], [0, 1], {
            extrapolateRight: 'clamp',
          });

          // Hold: gentle pulse on pins
          const pulse = 1 + Math.sin((hold * Math.PI * 3) + i * 1.5) * 0.05;

          return (
            <div key={i} style={{
              position: 'absolute',
              left: marker.x,
              top: marker.y,
              transform: `translate(-50%, -100%) scale(${markerScale * pulse})`,
              opacity: markerOpacity,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}>
              {/* Pin */}
              <div style={{
                width: 20,
                height: 20,
                borderRadius: '50%',
                background: marker.color ?? TKK_RED,
                border: `3px solid ${TKK_WHITE}`,
                boxShadow: '0 2px 8px rgba(0,0,0,0.5)',
              }} />
              {/* Label */}
              {marker.label && (
                <div style={{
                  marginTop: 4,
                  background: 'rgba(0,0,0,0.7)',
                  borderRadius: 6,
                  padding: '4px 12px',
                  fontFamily: FONTS.body,
                  fontSize: FONT_SIZE.dataValue,
                  color: TKK_WHITE,
                  whiteSpace: 'nowrap',
                }}>
                  {marker.label}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
