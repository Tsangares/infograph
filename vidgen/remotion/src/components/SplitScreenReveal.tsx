/**
 * SplitScreenReveal — animated split-screen comparison.
 * Divider sweeps across to reveal two contrasting panels.
 * Use for before/after, truth/fiction, cause/effect comparisons.
 */
import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';
import { type ZoneName, SAFE } from '../lib/zones';
import { SPRINGS } from '../lib/springs';
import { FONTS } from '../lib/fonts';
import { FONT_SIZE } from '../lib/typography';

interface PanelContent {
  label: string;
  value?: string;
  icon?: string;
  color: string;
  subtext?: string;
}

interface SplitScreenRevealProps {
  left: PanelContent;
  right: PanelContent;
  zone?: ZoneName;
  /** Direction of the divider sweep */
  direction?: 'horizontal' | 'vertical';
  /** When the split animation starts (fraction of scene, default 0.1) */
  splitAt?: number;
}

const SAFE_W = SAFE.right - SAFE.left;
const CONTENT_TOP = SAFE.top + 80;
const CONTENT_BOTTOM = SAFE.bottom - 40;
const CONTENT_H = CONTENT_BOTTOM - CONTENT_TOP;

export const SplitScreenReveal: React.FC<SplitScreenRevealProps> = ({
  left,
  right,
  zone = 'MID',
  direction = 'horizontal',
  splitAt = 0.1,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const splitStartFrame = Math.round(durationInFrames * splitAt);
  const splitFrame = Math.max(0, frame - splitStartFrame);

  // Divider sweep progress
  const splitProgress = spring({
    frame: splitFrame,
    fps,
    config: SPRINGS.dramatic,
  });

  // Left panel slides in from left
  const leftProgress = spring({ frame: splitFrame, fps, config: SPRINGS.snappy });
  const leftX = interpolate(leftProgress, [0, 1], [-100, 0]);
  const leftOpacity = interpolate(splitFrame, [0, 10], [0, 1], { extrapolateRight: 'clamp' });

  // Right panel slides in from right (slight delay)
  const rightFrame = Math.max(0, splitFrame - 8);
  const rightProgress = spring({ frame: rightFrame, fps, config: SPRINGS.snappy });
  const rightX = interpolate(rightProgress, [0, 1], [100, 0]);
  const rightOpacity = interpolate(rightFrame, [0, 10], [0, 1], { extrapolateRight: 'clamp' });

  // Exit
  const exitStart = durationInFrames - 12;
  const exitOpacity = interpolate(frame, [exitStart, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Divider glow
  const dividerGlow = Math.sin(frame * 0.08) * 0.3 + 0.7;

  const isHorizontal = direction === 'horizontal';
  const panelW = isHorizontal ? (SAFE_W - 20) / 2 : SAFE_W;
  const panelH = isHorizontal ? CONTENT_H : (CONTENT_H - 20) / 2;

  const panelStyle = (content: PanelContent, isLeft: boolean): React.CSSProperties => ({
    width: panelW,
    height: panelH,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
    borderRadius: 16,
    backgroundColor: `${content.color}10`,
    border: `1px solid ${content.color}25`,
    transform: `translateX(${isLeft ? leftX : rightX}px)`,
    opacity: isLeft ? leftOpacity : rightOpacity,
    gap: 12,
  });

  const renderPanel = (content: PanelContent, isLeft: boolean) => (
    <div style={panelStyle(content, isLeft)}>
      {content.value && (
        <div style={{
          fontFamily: FONTS.headline,
          fontSize: FONT_SIZE.hero,
          color: content.color,
          fontWeight: 'bold',
          textShadow: `0 0 20px ${content.color}44`,
        }}>
          {content.value}
        </div>
      )}
      <div style={{
        fontFamily: FONTS.headline,
        fontSize: FONT_SIZE.subtitle,
        color: content.color,
        fontWeight: 'bold',
        textTransform: 'uppercase',
        letterSpacing: 3,
        textAlign: 'center',
      }}>
        {content.label}
      </div>
      {content.subtext && (
        <div style={{
          fontFamily: FONTS.body,
          fontSize: FONT_SIZE.body,
          color: '#EAEAF0',
          textAlign: 'center',
          opacity: 0.7,
          maxWidth: panelW - 40,
        }}>
          {content.subtext}
        </div>
      )}
    </div>
  );

  return (
    <div style={{
      position: 'absolute',
      left: SAFE.left,
      top: CONTENT_TOP,
      width: SAFE_W,
      height: CONTENT_H,
      display: 'flex',
      flexDirection: isHorizontal ? 'row' : 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 20,
      opacity: exitOpacity,
    }}>
      {renderPanel(left, true)}

      {/* Animated divider */}
      <div style={{
        width: isHorizontal ? 2 : panelW * splitProgress,
        height: isHorizontal ? panelH * splitProgress : 2,
        backgroundColor: '#EAEAF044',
        boxShadow: `0 0 ${10 * dividerGlow}px #EAEAF022`,
        borderRadius: 1,
        flexShrink: 0,
      }} />

      {renderPanel(right, false)}
    </div>
  );
};
