/**
 * FlowDiagram — cause-to-effect nodes connected by self-drawing arrows.
 *
 * Shows 2-5 nodes with arrows that draw themselves sequentially.
 * Each node appears, then its outgoing arrow draws, then the next node appears.
 * Ideal for causal chains: "diversion → shrinkage → fish death → collapse"
 */
import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';
import { zoneStyle, type ZoneName, SAFE } from '../lib/zones';
import { TKK_WHITE, TKK_GOLD, TKK_SURFACE } from '../lib/colors';
import { FONTS } from '../lib/fonts';
import { FONT_SIZE } from '../lib/typography';
import { useSceneProgress } from '../lib/useSceneProgress';
import { SPRINGS } from '../lib/springs';
import { SVG_LIBRARY } from '../lib/svgLibrary';

interface FlowNode {
  label: string;
  icon?: string;
  color?: string;
}

interface FlowDiagramProps {
  nodes: FlowNode[];
  direction?: 'vertical' | 'horizontal';
  arrowColor?: string;
  zone?: ZoneName;
}

export const FlowDiagram: React.FC<FlowDiagramProps> = ({
  nodes,
  direction = 'vertical',
  arrowColor = TKK_GOLD,
  zone = 'MID',
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const { exit } = useSceneProgress();

  const n = nodes.length;
  // Each node + arrow pair gets an equal time slice
  const totalSteps = n * 2 - 1; // n nodes + (n-1) arrows
  const framesPerStep = Math.floor((durationInFrames * 0.75) / totalSteps);

  const exitOpacity = interpolate(exit, [0, 1], [1, 0], { extrapolateRight: 'clamp' });
  const exitScale = interpolate(exit, [0, 1], [1, 0.9], { extrapolateRight: 'clamp' });

  const isVertical = direction === 'vertical';
  // Scale down for more nodes to prevent overflow
  const nodeSize = isVertical
    ? Math.min(100, Math.floor(600 / n))
    : Math.min(90, Math.floor((SAFE.width - 40) / n * 0.5));
  const spacing = isVertical
    ? Math.min(160, Math.floor(700 / n))
    : Math.min(180, Math.floor((SAFE.width - 60) / n));
  const arrowLen = Math.max(20, spacing - nodeSize - 10);

  // For vertical layouts with 3+ nodes, expand to fill more vertical space
  const expandVertical = isVertical && n >= 3;
  const baseStyle = zoneStyle(zone);
  const containerStyle: React.CSSProperties = expandVertical
    ? {
        ...baseStyle,
        // Override zone height to span UPPER through LOWER
        top: SAFE.top + 80,
        height: SAFE.bottom - SAFE.top - 120,
      }
    : baseStyle;

  return (
    <div style={{
      ...containerStyle,
      flexDirection: isVertical ? 'column' : 'row',
      alignItems: 'center',
      justifyContent: 'space-evenly',
      gap: 0,
      opacity: exitOpacity,
      transform: `scale(${exitScale})`,
    }}>
      {nodes.map((node, i) => {
        const nodeStep = i * 2;
        const nodeStartFrame = nodeStep * framesPerStep;
        const nodeFrame = Math.max(0, frame - nodeStartFrame);

        const nodeScale = spring({ frame: nodeFrame, fps, config: SPRINGS.dramatic });
        const nodeOpacity = interpolate(nodeFrame, [0, 8], [0, 1], { extrapolateRight: 'clamp' });

        // Arrow (between nodes)
        const arrowStep = i * 2 + 1;
        const arrowStartFrame = arrowStep * framesPerStep;
        const arrowFrame = Math.max(0, frame - arrowStartFrame);
        const arrowProgress = interpolate(arrowFrame, [0, framesPerStep], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });

        const IconComponent = node.icon ? SVG_LIBRARY[node.icon] : null;
        const nodeColor = node.color ?? TKK_GOLD;

        // Float motion while holding
        const floatY = Math.sin(frame * 0.04 + i * 1.5) * 4;

        return (
          <React.Fragment key={i}>
            {/* Node */}
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 8,
              opacity: nodeOpacity,
              transform: `scale(${nodeScale}) translateY(${floatY}px)`,
            }}>
              <div style={{
                width: nodeSize,
                height: nodeSize,
                borderRadius: 16,
                backgroundColor: TKK_SURFACE,
                border: `3px solid ${nodeColor}55`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: `0 0 20px ${nodeColor}22`,
              }}>
                {IconComponent ? (
                  <IconComponent color={nodeColor} size={nodeSize * 0.55} />
                ) : (
                  <div style={{
                    fontFamily: FONTS.headline,
                    fontSize: FONT_SIZE.caption,
                    color: nodeColor,
                    fontWeight: 'bold',
                  }}>
                    {i + 1}
                  </div>
                )}
              </div>
              <div style={{
                fontFamily: FONTS.body,
                fontSize: FONT_SIZE.caption,
                fontWeight: 'bold',
                color: TKK_WHITE,
                textAlign: 'center',
                maxWidth: nodeSize + 40,
                lineHeight: 1.2,
              }}>
                {node.label}
              </div>
            </div>

            {/* Arrow between nodes */}
            {i < n - 1 && (
              <svg
                width={isVertical ? 30 : arrowLen}
                height={isVertical ? arrowLen : 30}
                style={{ flexShrink: 0 }}
              >
                {isVertical ? (
                  <>
                    <line
                      x1="15" y1="5"
                      x2="15" y2={5 + (arrowLen - 15) * arrowProgress}
                      stroke={arrowColor}
                      strokeWidth={3}
                      strokeLinecap="round"
                      opacity={0.8}
                    />
                    {arrowProgress > 0.8 && (
                      <polygon
                        points={`10,${arrowLen - 10} 15,${arrowLen} 20,${arrowLen - 10}`}
                        fill={arrowColor}
                        opacity={interpolate(arrowProgress, [0.8, 1], [0, 0.8], { extrapolateRight: 'clamp' })}
                      />
                    )}
                  </>
                ) : (
                  <>
                    <line
                      x1="5" y1="15"
                      x2={5 + (arrowLen - 15) * arrowProgress} y2="15"
                      stroke={arrowColor}
                      strokeWidth={3}
                      strokeLinecap="round"
                      opacity={0.8}
                    />
                    {arrowProgress > 0.8 && (
                      <polygon
                        points={`${arrowLen - 10},10 ${arrowLen},15 ${arrowLen - 10},20`}
                        fill={arrowColor}
                        opacity={interpolate(arrowProgress, [0.8, 1], [0, 0.8], { extrapolateRight: 'clamp' })}
                      />
                    )}
                  </>
                )}
              </svg>
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};
