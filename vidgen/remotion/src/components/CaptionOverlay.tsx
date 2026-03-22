import React from 'react';
import { useCurrentFrame, useVideoConfig } from 'remotion';
import { ZONES, SAFE } from '../lib/zones';
import { TKK_WHITE, TKK_GOLD } from '../lib/colors';
import { FONTS } from '../lib/fonts';

interface WhisperWord {
  text: string;
  offset_s: number;
  end_s: number;
}

interface CaptionOverlayProps {
  words: WhisperWord[];
  maxWordsPerLine?: number;
  activeColor?: string;
  inactiveColor?: string;
}

/**
 * TikTok-style word-by-word caption overlay.
 * Highlights the current word based on Whisper timestamps.
 */
export const CaptionOverlay: React.FC<CaptionOverlayProps> = ({
  words,
  maxWordsPerLine = 6,
  activeColor = TKK_GOLD,
  inactiveColor = TKK_WHITE + '99',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTime = frame / fps;

  // Find current word index
  const currentIdx = words.findIndex(
    w => currentTime >= w.offset_s && currentTime < w.end_s
  );

  // Group words into lines
  const lines: WhisperWord[][] = [];
  for (let i = 0; i < words.length; i += maxWordsPerLine) {
    lines.push(words.slice(i, i + maxWordsPerLine));
  }

  // Find which line contains the current word
  const currentLineIdx = currentIdx >= 0 ? Math.floor(currentIdx / maxWordsPerLine) : -1;

  // Show current line and maybe the next
  const visibleLines = lines.slice(
    Math.max(0, currentLineIdx),
    Math.max(0, currentLineIdx) + 2
  );

  if (currentIdx < 0 && currentTime > 0) return null;

  return (
    <div style={{
      position: 'absolute',
      top: ZONES.FOOTER.y - 40,
      left: SAFE.left,
      width: SAFE.width,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: 8,
    }}>
      {visibleLines.map((line, lineIdx) => (
        <div key={lineIdx} style={{
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'center',
          gap: 6,
        }}>
          {line.map((word, wordIdx) => {
            const globalIdx = (Math.max(0, currentLineIdx) + lineIdx) * maxWordsPerLine + wordIdx;
            const isActive = globalIdx === currentIdx;
            const isPast = globalIdx < currentIdx;

            return (
              <span key={wordIdx} style={{
                fontFamily: FONTS.body,
                fontWeight: isActive ? 'bold' : 'normal',
                fontSize: 32,
                color: isActive ? activeColor : isPast ? TKK_WHITE : inactiveColor,
                textShadow: '0 2px 8px rgba(0,0,0,0.8)',
                transform: isActive ? 'scale(1.1)' : 'scale(1)',
              }}>
                {word.text}
              </span>
            );
          })}
        </div>
      ))}
    </div>
  );
};
