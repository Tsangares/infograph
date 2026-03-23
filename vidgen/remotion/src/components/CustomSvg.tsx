/**
 * CustomSvg — renders inline SVG paths authored by the LLM.
 *
 * Unlike svgLibrary icons (pre-built lookups), this accepts raw path data
 * in the manifest, letting the LLM draw topic-specific illustrations:
 * explosion shockwaves, crater cross-sections, landscape silhouettes, etc.
 */
import React from 'react';

interface SvgPath {
  d: string;
  fill?: string;
  stroke?: string;
  strokeWidth?: number;
  opacity?: number;
  fillRule?: 'nonzero' | 'evenodd';
}

interface CustomSvgProps {
  viewBox: string;
  paths: SvgPath[];
  color?: string;
  size?: number;
}

export const CustomSvg: React.FC<CustomSvgProps> = ({
  viewBox,
  paths,
  color = '#ffffff',
  size = 200,
}) => (
  <svg
    width={size}
    height={size}
    viewBox={viewBox}
    xmlns="http://www.w3.org/2000/svg"
    style={{ color }}
  >
    {paths.map((p, i) => (
      <path
        key={i}
        d={p.d}
        fill={p.fill ?? color}
        stroke={p.stroke ?? 'none'}
        strokeWidth={p.strokeWidth ?? 0}
        opacity={p.opacity ?? 1}
        fillRule={p.fillRule ?? 'nonzero'}
      />
    ))}
  </svg>
);
