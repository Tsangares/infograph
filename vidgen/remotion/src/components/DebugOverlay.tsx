/**
 * DebugOverlay — renders zone boundaries, safe areas, and frame counter
 * for visual debugging during development. Enable via prop.
 */
import React from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from 'remotion';
import { WIDTH, HEIGHT, ZONES, SAFE, type ZoneName } from '../lib/zones';

interface DebugOverlayProps {
  enabled?: boolean;
}

const ZONE_COLORS: Record<ZoneName, string> = {
  TITLE: '#FF6B6B',
  UPPER: '#4ECDC4',
  MID: '#FFE66D',
  LOWER: '#95E1D3',
  FOOTER: '#F38181',
};

export const DebugOverlay: React.FC<DebugOverlayProps> = ({ enabled = true }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  if (!enabled) return null;

  const timeS = (frame / fps).toFixed(2);
  const progress = ((frame / durationInFrames) * 100).toFixed(1);

  return (
    <AbsoluteFill style={{ pointerEvents: 'none', zIndex: 999 }}>
      {/* Zone bands */}
      {(Object.entries(ZONES) as [ZoneName, typeof ZONES[ZoneName]][]).map(([name, zone]) => {
        const top = zone.range[0];
        const height = zone.range[1] - zone.range[0];
        const color = ZONE_COLORS[name];
        return (
          <React.Fragment key={name}>
            {/* Zone fill */}
            <div style={{
              position: 'absolute',
              top,
              left: 0,
              width: WIDTH,
              height,
              backgroundColor: `${color}12`,
              borderTop: `2px solid ${color}55`,
              borderBottom: `2px solid ${color}55`,
            }} />
            {/* Zone label */}
            <div style={{
              position: 'absolute',
              top: top + 4,
              left: 8,
              fontFamily: 'monospace',
              fontSize: 14,
              color: `${color}CC`,
              fontWeight: 'bold',
              textShadow: '0 0 4px #000',
            }}>
              {name} ({Math.round(top)}-{Math.round(top + height)}px)
            </div>
          </React.Fragment>
        );
      })}

      {/* Safe area rectangle */}
      <div style={{
        position: 'absolute',
        top: SAFE.top,
        left: SAFE.left,
        width: SAFE.width,
        height: SAFE.height,
        border: '2px dashed #FFFFFF44',
        borderRadius: 4,
      }} />
      {/* Safe area label */}
      <div style={{
        position: 'absolute',
        top: SAFE.top - 18,
        left: SAFE.left,
        fontFamily: 'monospace',
        fontSize: 12,
        color: '#FFFFFF66',
      }}>
        SAFE AREA ({SAFE.width}×{SAFE.height})
      </div>

      {/* Danger zones — platform UI overlap areas */}
      {/* Top danger */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: WIDTH,
        height: SAFE.top,
        backgroundColor: '#FF000010',
        borderBottom: '1px solid #FF000033',
      }} />
      {/* Bottom danger */}
      <div style={{
        position: 'absolute',
        top: SAFE.bottom,
        left: 0,
        width: WIDTH,
        height: HEIGHT - SAFE.bottom,
        backgroundColor: '#FF000010',
        borderTop: '1px solid #FF000033',
      }} />
      {/* Right danger */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: SAFE.right,
        width: WIDTH - SAFE.right,
        height: HEIGHT,
        backgroundColor: '#FF000008',
        borderLeft: '1px solid #FF000022',
      }} />

      {/* Center crosshair */}
      <div style={{
        position: 'absolute',
        top: HEIGHT / 2 - 20,
        left: WIDTH / 2 - 1,
        width: 2,
        height: 40,
        backgroundColor: '#FFFFFF22',
      }} />
      <div style={{
        position: 'absolute',
        top: HEIGHT / 2 - 1,
        left: WIDTH / 2 - 20,
        width: 40,
        height: 2,
        backgroundColor: '#FFFFFF22',
      }} />

      {/* Frame counter — top right (inside danger zone intentionally) */}
      <div style={{
        position: 'absolute',
        top: 10,
        right: 10,
        fontFamily: 'monospace',
        fontSize: 16,
        color: '#FFFFFF88',
        backgroundColor: '#00000088',
        padding: '4px 8px',
        borderRadius: 4,
        textShadow: '0 0 4px #000',
        lineHeight: 1.4,
      }}>
        <div>F: {frame}/{durationInFrames}</div>
        <div>T: {timeS}s</div>
        <div>P: {progress}%</div>
      </div>
    </AbsoluteFill>
  );
};
