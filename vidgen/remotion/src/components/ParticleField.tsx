/**
 * ParticleField — floating bokeh dots that drift upward.
 * Adds ambient motion to every scene. Purely decorative.
 */
import React from 'react';
import { useCurrentFrame, useVideoConfig } from 'remotion';
import { WIDTH, HEIGHT } from '../lib/zones';

interface ParticleFieldProps {
  count?: number;
  color?: string;
  speed?: number;
}

// Deterministic pseudo-random using golden angle
const goldenAngle = 137.508;
const makeParticles = (count: number) =>
  Array.from({ length: count }, (_, i) => ({
    // Distribute across frame using golden angle
    x: ((i * goldenAngle * 3.7) % WIDTH),
    y: ((i * goldenAngle * 7.3) % HEIGHT),
    size: 2 + (i * goldenAngle % 4),
    speed: 0.3 + (i * goldenAngle % 0.7),
    opacity: 0.08 + (i * goldenAngle % 0.15),
    drift: (i % 2 === 0 ? 1 : -1) * (0.5 + (i * goldenAngle % 1)),
  }));

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

        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: x,
              top: wrappedY,
              width: p.size,
              height: p.size,
              borderRadius: '50%',
              background: `radial-gradient(circle, ${color}, transparent)`,
              opacity: p.opacity,
            }}
          />
        );
      })}
    </div>
  );
};
