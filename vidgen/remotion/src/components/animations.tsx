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
