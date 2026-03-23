import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';
import { SPRINGS, type SpringPreset } from '../lib/springs';

/* ------------------------------------------------------------------ */
/*  FadeIn                                                             */
/* ------------------------------------------------------------------ */

interface FadeInProps {
  delay?: number;
  duration?: number;
  children: React.ReactNode;
}

/**
 * Opacity 0→1 over `duration` frames, starting at `delay`.
 * Replaces the repeated `interpolate(frame, [0, 10], [0, 1])` pattern.
 */
export const FadeIn: React.FC<FadeInProps> = ({
  delay = 0,
  duration = 10,
  children,
}) => {
  const frame = useCurrentFrame();
  const adjusted = Math.max(0, frame - delay);
  const opacity = interpolate(adjusted, [0, duration], [0, 1], {
    extrapolateRight: 'clamp',
  });

  return <div style={{ opacity }}>{children}</div>;
};

/* ------------------------------------------------------------------ */
/*  SlideUp                                                            */
/* ------------------------------------------------------------------ */

interface SlideUpProps {
  delay?: number;
  distance?: number;
  springPreset?: SpringPreset;
  children: React.ReactNode;
}

/**
 * Translates from `distance` px below to 0 with opacity fade.
 * Uses spring physics from a named preset.
 */
export const SlideUp: React.FC<SlideUpProps> = ({
  delay = 0,
  distance = 20,
  springPreset = 'snappy',
  children,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const adjusted = Math.max(0, frame - delay);
  const progress = spring({
    frame: adjusted,
    fps,
    config: SPRINGS[springPreset],
  });
  const translateY = interpolate(progress, [0, 1], [distance, 0]);
  const opacity = interpolate(adjusted, [0, 10], [0, 1], {
    extrapolateRight: 'clamp',
  });

  return (
    <div style={{ opacity, transform: `translateY(${translateY}px)` }}>
      {children}
    </div>
  );
};

/* ------------------------------------------------------------------ */
/*  ScalePop                                                           */
/* ------------------------------------------------------------------ */

interface ScalePopProps {
  delay?: number;
  springPreset?: SpringPreset;
  children: React.ReactNode;
}

/**
 * Scales from 0→1 using spring physics. Used for hero stats,
 * counters, headlines landing with impact.
 */
export const ScalePop: React.FC<ScalePopProps> = ({
  delay = 0,
  springPreset = 'dramatic',
  children,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const adjusted = Math.max(0, frame - delay);
  const scale = spring({
    frame: adjusted,
    fps,
    config: SPRINGS[springPreset],
  });
  const opacity = interpolate(adjusted, [0, 8], [0, 1], {
    extrapolateRight: 'clamp',
  });

  return (
    <div style={{ opacity, transform: `scale(${scale})` }}>
      {children}
    </div>
  );
};

/* ------------------------------------------------------------------ */
/*  StaggerChildren                                                    */
/* ------------------------------------------------------------------ */

interface StaggerChildrenProps {
  delay?: number;
  stagger?: number;
  children: React.ReactNode;
}

/**
 * Wraps React.Children, applying incremental delay to each child.
 * `stagger` = frames between each child (default 8).
 * Children receive a CSS transition-delay equivalent via wrapper divs
 * that use FadeIn with staggered delays.
 */
export const StaggerChildren: React.FC<StaggerChildrenProps> = ({
  delay = 0,
  stagger = 8,
  children,
}) => {
  return (
    <>
      {React.Children.map(children, (child, i) => (
        <FadeIn delay={delay + i * stagger}>
          {child}
        </FadeIn>
      ))}
    </>
  );
};

/* ------------------------------------------------------------------ */
/*  SlideIn — directional entrance                                     */
/* ------------------------------------------------------------------ */

interface SlideInProps {
  delay?: number;
  direction?: 'left' | 'right' | 'up' | 'down';
  distance?: number;
  springPreset?: SpringPreset;
  children: React.ReactNode;
}

/**
 * Slides in from any direction with spring physics.
 * More versatile than SlideUp — supports 4 directions.
 */
export const SlideIn: React.FC<SlideInProps> = ({
  delay = 0,
  direction = 'left',
  distance = 60,
  springPreset = 'snappy',
  children,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const adjusted = Math.max(0, frame - delay);
  const progress = spring({ frame: adjusted, fps, config: SPRINGS[springPreset] });
  const opacity = interpolate(adjusted, [0, 10], [0, 1], { extrapolateRight: 'clamp' });

  const dirMap = {
    left: { x: -distance, y: 0 },
    right: { x: distance, y: 0 },
    up: { x: 0, y: -distance },
    down: { x: 0, y: distance },
  };
  const { x, y } = dirMap[direction];
  const tx = interpolate(progress, [0, 1], [x, 0]);
  const ty = interpolate(progress, [0, 1], [y, 0]);

  return (
    <div style={{ opacity, transform: `translate(${tx}px, ${ty}px)` }}>
      {children}
    </div>
  );
};

/* ------------------------------------------------------------------ */
/*  PulseGlow — ambient pulsing glow behind content                    */
/* ------------------------------------------------------------------ */

interface PulseGlowProps {
  color?: string;
  intensity?: number;
  speed?: number;
  children: React.ReactNode;
}

/**
 * Adds an animated glow that pulses behind content.
 * Great for highlighting hero stats or key data points.
 */
export const PulseGlow: React.FC<PulseGlowProps> = ({
  color = '#FFD700',
  intensity = 20,
  speed = 0.08,
  children,
}) => {
  const frame = useCurrentFrame();
  const pulse = Math.sin(frame * speed) * 0.5 + 0.5; // 0→1 oscillation
  const blur = intensity * (0.5 + pulse * 0.5);
  const spread = intensity * 0.3 * pulse;

  return (
    <div style={{
      filter: `drop-shadow(0 0 ${blur}px ${color}${Math.round(pulse * 60 + 20).toString(16).padStart(2, '0')})`,
      transform: `scale(${1 + pulse * 0.015})`,
    }}>
      {children}
    </div>
  );
};

/* ------------------------------------------------------------------ */
/*  RotateIn — rotation entrance with spring                           */
/* ------------------------------------------------------------------ */

interface RotateInProps {
  delay?: number;
  degrees?: number;
  springPreset?: SpringPreset;
  children: React.ReactNode;
}

/**
 * Rotates from `degrees` to 0 with spring physics + fade.
 * Good for domino-like reveals and icon entrances.
 */
export const RotateIn: React.FC<RotateInProps> = ({
  delay = 0,
  degrees = -15,
  springPreset = 'bouncy',
  children,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const adjusted = Math.max(0, frame - delay);
  const progress = spring({ frame: adjusted, fps, config: SPRINGS[springPreset] });
  const rotation = interpolate(progress, [0, 1], [degrees, 0]);
  const opacity = interpolate(adjusted, [0, 8], [0, 1], { extrapolateRight: 'clamp' });
  const scale = interpolate(progress, [0, 1], [0.8, 1]);

  return (
    <div style={{
      opacity,
      transform: `rotate(${rotation}deg) scale(${scale})`,
      transformOrigin: 'center center',
    }}>
      {children}
    </div>
  );
};

/* ------------------------------------------------------------------ */
/*  Typewriter — character-by-character text reveal                     */
/* ------------------------------------------------------------------ */

interface TypewriterProps {
  text: string;
  speed?: number; // frames per character
  delay?: number;
  color?: string;
  fontSize?: number;
  fontFamily?: string;
}

/**
 * Reveals text one character at a time with a blinking cursor.
 * Classic typewriter effect for dramatic reveals.
 */
export const Typewriter: React.FC<TypewriterProps> = ({
  text,
  speed = 2,
  delay = 0,
  color = '#EAEAF0',
  fontSize = 56,
  fontFamily = 'Inter, sans-serif',
}) => {
  const frame = useCurrentFrame();
  const adjusted = Math.max(0, frame - delay);
  const charsVisible = Math.min(text.length, Math.floor(adjusted / speed));
  const cursorVisible = adjusted % 16 < 10; // blink every ~0.5s
  const isDone = charsVisible >= text.length;

  return (
    <div style={{
      fontFamily,
      fontSize,
      color,
      letterSpacing: 1,
      whiteSpace: 'pre-wrap',
      textAlign: 'center',
    }}>
      {text.slice(0, charsVisible)}
      {!isDone && (
        <span style={{ opacity: cursorVisible ? 1 : 0, color }}>▌</span>
      )}
    </div>
  );
};
