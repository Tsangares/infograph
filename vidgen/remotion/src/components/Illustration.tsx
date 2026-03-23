/**
 * Illustration scene — renders animated SVG elements from the icon library.
 *
 * Each element can enter with different animations, move/transform during
 * the hold phase, and has continuous holdMotion (default: float) so nothing
 * sits static while the narrator talks.
 */
import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';
import { zoneStyle, type ZoneName } from '../lib/zones';
import { useSceneProgress } from '../lib/useSceneProgress';
import { SVG_LIBRARY } from '../lib/svgLibrary';
import { SPRINGS } from '../lib/springs';

type EnterAnimation = 'fadeIn' | 'slideLeft' | 'slideRight' | 'slideUp' | 'pop' | 'drop' | 'stamp' | 'grow' | 'shatter';
type HoldMotion = 'float' | 'drift' | 'pulse' | 'breathe' | 'orbit' | 'none' | 'tremble' | 'swing' | 'glow';

interface AnimateProps {
  x?: number;
  y?: number;
  opacity?: number;
  scale?: number;
}

interface IllustrationElement {
  svg: string;
  position?: { x: number; y: number };
  size?: number;
  color?: string;
  delay?: number;
  enter?: EnterAnimation;
  animate?: AnimateProps;
  repeat?: number;
  stagger?: number;
  shake?: boolean;
  holdMotion?: HoldMotion;
}

interface IllustrationProps {
  elements: IllustrationElement[];
  zone?: ZoneName;
}

const AnimatedElement: React.FC<{
  element: IllustrationElement;
  index: number;
  totalElements: number;
}> = ({ element, index }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { exit, hold } = useSceneProgress();

  const IconComponent = SVG_LIBRARY[element.svg];
  if (!IconComponent) return null;

  const delay = element.delay ?? 0;
  const delayFrames = Math.round(delay * fps);
  const entryFrame = Math.max(0, frame - delayFrames);
  const enter = element.enter ?? 'fadeIn';
  const size = element.size ?? 100;
  const pos = element.position ?? { x: 0, y: 0 };
  const motion = element.holdMotion ?? 'float';

  // Entrance animations
  let enterOpacity = 1;
  let enterTranslateX = 0;
  let enterTranslateY = 0;
  let enterScale = 1;

  switch (enter) {
    case 'fadeIn':
      enterOpacity = interpolate(entryFrame, [0, 12], [0, 1], { extrapolateRight: 'clamp' });
      break;
    case 'slideLeft':
      enterOpacity = interpolate(entryFrame, [0, 8], [0, 1], { extrapolateRight: 'clamp' });
      enterTranslateX = interpolate(
        spring({ frame: entryFrame, fps, config: SPRINGS.snappy }),
        [0, 1], [-300, 0]
      );
      break;
    case 'slideRight':
      enterOpacity = interpolate(entryFrame, [0, 8], [0, 1], { extrapolateRight: 'clamp' });
      enterTranslateX = interpolate(
        spring({ frame: entryFrame, fps, config: SPRINGS.snappy }),
        [0, 1], [300, 0]
      );
      break;
    case 'slideUp':
      enterOpacity = interpolate(entryFrame, [0, 8], [0, 1], { extrapolateRight: 'clamp' });
      enterTranslateY = interpolate(
        spring({ frame: entryFrame, fps, config: SPRINGS.snappy }),
        [0, 1], [200, 0]
      );
      break;
    case 'pop':
      enterOpacity = interpolate(entryFrame, [0, 5], [0, 1], { extrapolateRight: 'clamp' });
      enterScale = spring({ frame: entryFrame, fps, config: SPRINGS.dramatic });
      break;
    case 'drop':
      enterOpacity = interpolate(entryFrame, [0, 5], [0, 1], { extrapolateRight: 'clamp' });
      enterTranslateY = interpolate(
        spring({ frame: entryFrame, fps, config: SPRINGS.bouncy }),
        [0, 1], [-300, 0]
      );
      break;
    case 'stamp': {
      enterOpacity = interpolate(entryFrame, [0, 3], [0, 1], { extrapolateRight: 'clamp' });
      const stampProgress = spring({ frame: entryFrame, fps, config: SPRINGS.heavy });
      enterScale = interpolate(stampProgress, [0, 1], [4, 1]);
      // Screen shake effect — rapid decay
      if (entryFrame > 0 && entryFrame < 15) {
        const shakeDecay = Math.max(0, 1 - entryFrame / 15);
        enterTranslateX = Math.sin(entryFrame * 2.5) * 12 * shakeDecay;
        enterTranslateY = Math.cos(entryFrame * 3.1) * 8 * shakeDecay;
      }
      break;
    }
    case 'grow':
      enterOpacity = interpolate(entryFrame, [0, 8], [0, 1], { extrapolateRight: 'clamp' });
      enterScale = interpolate(entryFrame, [0, 30], [0, 1], { extrapolateRight: 'clamp' });
      break;
    case 'shatter': {
      // Assembles from scattered fragments — reverse shatter effect
      enterOpacity = interpolate(entryFrame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
      const assembleProgress = spring({ frame: entryFrame, fps, config: SPRINGS.dramatic });
      enterScale = interpolate(assembleProgress, [0, 1], [0.3, 1]);
      // Rotate while assembling
      enterTranslateX = interpolate(assembleProgress, [0, 1], [(index % 2 === 0 ? 80 : -80), 0]);
      enterTranslateY = interpolate(assembleProgress, [0, 1], [(index % 3 === 0 ? -60 : 40), 0]);
      break;
    }
  }

  // Hold-phase animations (animate props interpolated over hold)
  let animX = 0;
  let animY = 0;
  let animOpacity = 1;
  let animScale = 1;

  if (element.animate) {
    const a = element.animate;
    if (a.x != null) animX = interpolate(hold, [0, 1], [0, a.x], { extrapolateRight: 'clamp' });
    if (a.y != null) animY = interpolate(hold, [0, 1], [0, a.y], { extrapolateRight: 'clamp' });
    if (a.opacity != null) animOpacity = interpolate(hold, [0, 1], [1, a.opacity], { extrapolateRight: 'clamp' });
    if (a.scale != null) animScale = interpolate(hold, [0, 1], [1, a.scale], { extrapolateRight: 'clamp' });
  }

  // Continuous hold motion — keeps elements alive while narrator talks
  let motionX = 0;
  let motionY = 0;
  let motionScale = 1;
  let motionOpacity = 1;

  switch (motion) {
    case 'float':
      motionY = Math.sin(frame * 0.04 + index * 2) * 8;
      break;
    case 'drift':
      motionX = Math.sin(frame * 0.02 + index * 1.3) * 12;
      motionY = Math.cos(frame * 0.03 + index * 0.7) * 6;
      break;
    case 'pulse':
      motionScale = 1 + Math.sin(frame * 0.06 + index * 1.5) * 0.04;
      break;
    case 'breathe':
      motionScale = 1 + Math.sin(frame * 0.04 + index) * 0.02;
      motionOpacity = 0.85 + Math.sin(frame * 0.04 + index) * 0.15;
      break;
    case 'orbit':
      motionX = Math.cos(frame * 0.03 + index * Math.PI) * 15;
      motionY = Math.sin(frame * 0.03 + index * Math.PI) * 10;
      break;
    case 'none':
      break;
    case 'tremble':
      motionX = Math.sin(frame * 0.8 + index * 3) * 3;
      motionY = Math.cos(frame * 1.1 + index * 5) * 2;
      break;
    case 'swing':
      // Pendulum — rotation handled via motionX (applied as visual sway)
      motionX = Math.sin(frame * 0.05 + index * 1.2) * 20;
      break;
    case 'glow':
      // No position change — glow is handled in the style filter below
      break;
  }

  // Shake effect (legacy, adds on top of holdMotion)
  if (element.shake) {
    motionX += Math.sin(frame * 1.7 + index * 3) * 4;
    motionY += Math.cos(frame * 2.1 + index * 5) * 3;
  }

  // Exit
  const exitOpacity = interpolate(exit, [0, 1], [1, 0], { extrapolateRight: 'clamp' });
  const exitScale = interpolate(exit, [0, 1], [1, 0.85], { extrapolateRight: 'clamp' });

  const totalX = pos.x + enterTranslateX + animX + motionX;
  const totalY = pos.y + enterTranslateY + animY + motionY;
  const totalScale = enterScale * animScale * motionScale * exitScale;
  const totalOpacity = enterOpacity * animOpacity * motionOpacity * exitOpacity;

  return (
    <div style={{
      position: 'absolute',
      left: '50%',
      top: '50%',
      transform: `translate(calc(-50% + ${totalX}px), calc(-50% + ${totalY}px)) scale(${totalScale})`,
      opacity: totalOpacity,
      filter: motion === 'glow'
        ? `drop-shadow(0 0 ${12 + Math.sin(frame * 0.08 + index) * 8}px ${element.color ?? '#ffffff'}${Math.round(55 + Math.sin(frame * 0.08 + index) * 40).toString(16).padStart(2, '0')})`
        : `drop-shadow(0 0 8px ${element.color ?? '#ffffff'}55)`,
      willChange: 'transform, opacity',
    }}>
      <IconComponent color={element.color} size={size} />
    </div>
  );
};

export const Illustration: React.FC<IllustrationProps> = ({
  elements,
  zone = 'MID',
}) => {
  // Expand repeated elements
  const expandedElements: { element: IllustrationElement; key: number }[] = [];
  let keyCounter = 0;
  for (const el of elements) {
    const count = el.repeat ?? 1;
    const stagger = el.stagger ?? 0.15;
    for (let i = 0; i < count; i++) {
      const iconSize = Math.max(40, el.size ?? 100); // minimum 40px for visibility
      const spacingStep = Math.max(80, iconSize * 1.2); // minimum 80px between icons
      const spacing = count > 1 ? (i - (count - 1) / 2) * spacingStep : 0;
      expandedElements.push({
        key: keyCounter++,
        element: {
          ...el,
          delay: (el.delay ?? 0) + i * stagger,
          position: {
            x: (el.position?.x ?? 0) + spacing,
            y: el.position?.y ?? 0,
          },
          repeat: undefined,
        },
      });
    }
  }

  return (
    <div style={{
      ...zoneStyle(zone),
      overflow: 'visible',
    }}>
      {expandedElements.map(({ element, key }, i) => (
        <AnimatedElement
          key={key}
          element={element}
          index={i}
          totalElements={expandedElements.length}
        />
      ))}
    </div>
  );
};
