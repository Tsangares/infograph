/**
 * ParticleField — floating particles with variety: dots, lines, diamonds.
 * Adds ambient motion to every scene. Purely decorative.
 * Enhanced: shape variety, glow pulses, size variation.
 */
import React from 'react';
import { useCurrentFrame } from 'remotion';
import { WIDTH, HEIGHT } from '../lib/zones';

interface ParticleFieldProps {
  count?: number;
  color?: string;
  speed?: number;
}

type ParticleShape = 'circle' | 'diamond' | 'line';

interface Particle {
  x: number;
  y: number;
  size: number;
  speed: number;
  opacity: number;
  drift: number;
  shape: ParticleShape;
  rotation: number;
  pulsePhase: number;
}

// Deterministic pseudo-random using golden angle
const goldenAngle = 137.508;

const SHAPES: ParticleShape[] = ['circle', 'circle', 'circle', 'diamond', 'line'];

const makeParticles = (count: number): Particle[] =>
  Array.from({ length: count }, (_, i) => ({
    x: ((i * goldenAngle * 3.7) % WIDTH),
    y: ((i * goldenAngle * 7.3) % HEIGHT),
    size: 2 + (i * goldenAngle % 6),
    speed: 0.3 + (i * goldenAngle % 0.7),
    opacity: 0.06 + (i * goldenAngle % 0.18),
    drift: (i % 2 === 0 ? 1 : -1) * (0.5 + (i * goldenAngle % 1)),
    shape: SHAPES[i % SHAPES.length],
    rotation: (i * goldenAngle) % 360,
    pulsePhase: (i * goldenAngle * 2.3) % (Math.PI * 2),
  }));

const renderParticle = (shape: ParticleShape, size: number, color: string, rotation: number) => {
  switch (shape) {
    case 'diamond':
      return {
        width: size,
        height: size,
        borderRadius: 1,
        background: color,
        transform: `rotate(45deg)`,
      };
    case 'line':
      return {
        width: size * 3,
        height: 1.5,
        borderRadius: 1,
        background: color,
        transform: `rotate(${rotation}deg)`,
      };
    case 'circle':
    default:
      return {
        width: size,
        height: size,
        borderRadius: '50%',
        background: `radial-gradient(circle, ${color}, transparent)`,
      };
  }
};

export const ParticleField: React.FC<ParticleFieldProps> = ({
  count = 20,
  color = '#ffffff',
  speed = 1,
}) => {
  const frame = useCurrentFrame();
  const particles = React.useMemo(() => makeParticles(count), [count]);

  return (
    <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none', overflow: 'hidden' }}>
      {particles.map((p, i) => {
        const y = (p.y - frame * p.speed * speed * 1.5) % HEIGHT;
        const wrappedY = y < 0 ? y + HEIGHT : y;
        const x = p.x + Math.sin(frame * 0.02 * p.drift + i) * 30;

        // Per-particle glow pulse
        const pulse = Math.sin(frame * 0.04 + p.pulsePhase) * 0.5 + 0.5;
        const currentOpacity = p.opacity * (0.7 + pulse * 0.3);
        const glowSize = p.shape === 'circle' ? p.size * (1 + pulse * 0.4) : p.size;

        const shapeStyle = renderParticle(p.shape, glowSize, color, p.rotation + frame * 0.3);

        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: x,
              top: wrappedY,
              opacity: currentOpacity,
              ...shapeStyle,
            }}
          />
        );
      })}
    </div>
  );
};
