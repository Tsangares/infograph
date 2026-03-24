/**
 * WordTriggeredScene — renders a scene where every element's entrance
 * is driven by word-level Whisper timestamps.
 *
 * Each element is wrapped in a <Sequence from={delayFrames}> so its internal
 * useCurrentFrame() starts at 0 when the anchor word is spoken.
 *
 * Zone replacement: elements with hold="until_replaced" end when the next
 * element in the same zone with replaces_zone=true begins.
 */
import React from 'react';
import { AbsoluteFill, Sequence, useVideoConfig } from 'remotion';
import { GradientBg } from '../components/GradientBg';
import { GridLines } from '../components/GridLines';
import { LabelPill } from '../components/LabelPill';
import { ParticleField } from '../components/ParticleField';
import { SafeText } from '../components/SafeText';
import { Counter } from '../components/Counter';
import { Illustration } from '../components/Illustration';
import { GaugeMeter } from '../components/GaugeMeter';
import { TextEffect } from '../components/TextEffect';
import { TransformReveal } from '../components/TransformReveal';
import { ProgressRing } from '../components/ProgressRing';
import { FlowDiagram } from '../components/FlowDiagram';
import { ScaleComparison } from '../components/ScaleComparison';
import { StackedAccumulation } from '../components/StackedAccumulation';
import { CauseEffect } from '../components/CauseEffect';
import { PopulationDrop } from '../components/PopulationDrop';
import { CustomSvg } from '../components/CustomSvg';
import { WordBar } from './WordBar';
import { WordTimelineMarker } from './WordTimelineMarker';
import { SlowZoom } from '../components/SlowZoom';
import { ParallaxLayer } from '../components/ParallaxLayer';
import { SvgPathDraw } from '../components/SvgPathDraw';
import { NoiseOverlay } from '../components/NoiseOverlay';
import { VignetteOverlay } from '../components/VignetteOverlay';
import { EmphasisLine } from '../components/EmphasisLine';
import { SvgMorph } from '../components/SvgMorph';
import { SplitScreenReveal } from '../components/SplitScreenReveal';
import { AnimatedPieChart } from '../components/AnimatedPieChart';
import { NumberTicker } from '../components/NumberTicker';
import { AnimatedBarRace } from '../components/AnimatedBarRace';
import { MapHighlight } from '../components/MapHighlight';
import { DebugOverlay } from '../components/DebugOverlay';
import type { ResolvedScene, ResolvedElement } from './types';

interface WordTriggeredSceneProps {
  scene: ResolvedScene;
  bgColor?: string;
  accentColor?: string;
  secondaryColor?: string;
  debug?: boolean;
}

/**
 * Compute the duration for each element, respecting "until_replaced" holds.
 * Returns a map of element index → durationInFrames.
 */
function computeElementDurations(
  elements: ResolvedElement[],
  sceneDurationFrames: number,
): Map<number, number> {
  const durations = new Map<number, number>();

  // Group elements by zone
  const zoneElements: Map<string, { idx: number; elem: ResolvedElement }[]> = new Map();
  elements.forEach((elem, idx) => {
    const zone = elem.zone ?? 'MID';
    if (!zoneElements.has(zone)) zoneElements.set(zone, []);
    zoneElements.get(zone)!.push({ idx, elem });
  });

  // For each zone, find replacement chains
  for (const [_zone, zoneElems] of zoneElements) {
    // Sort by delay
    const sorted = [...zoneElems].sort((a, b) =>
      a.elem._resolved.delay_frames - b.elem._resolved.delay_frames
    );

    for (let i = 0; i < sorted.length; i++) {
      const { idx, elem } = sorted[i];
      const delayFrames = elem._resolved.delay_frames;
      const defaultDuration = Math.max(30, sceneDurationFrames - delayFrames); // minimum 1s visibility

      if (elem.hold === 'until_replaced') {
        // Find the next element in this zone that replaces
        let replacerFrame = sceneDurationFrames; // default: end of scene
        for (let j = i + 1; j < sorted.length; j++) {
          const next = sorted[j];
          if (next.elem.replaces_zone || next.elem.type === elem.type) {
            replacerFrame = next.elem._resolved.delay_frames;
            break;
          }
        }
        // Duration = from this element's start to the replacer's start
        // Add a tiny fade-out overlap (3 frames = 0.1s) to crossfade
        const dur = Math.max(1, replacerFrame - delayFrames + 3);
        durations.set(idx, Math.min(dur, defaultDuration));
      } else {
        durations.set(idx, defaultDuration);
      }
    }
  }

  return durations;
}

/**
 * Route a resolved element to the right component.
 */
const ElementRenderer: React.FC<{
  elem: ResolvedElement;
  durationInFrames: number;
  barIndex?: number;
  totalBars?: number;
  markerIndex?: number;
  totalMarkers?: number;
  zIndex?: number;
}> = ({ elem, durationInFrames, barIndex, totalBars, markerIndex, totalMarkers, zIndex = 0 }) => {
  const { fps } = useVideoConfig();
  const delayFrames = elem._resolved.delay_frames;

  // Wrap every element in a positioned div with z-index so later elements render in front
  const Wrap: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <div style={{ position: 'absolute', inset: 0, zIndex }}>{children}</div>
  );

  switch (elem.type) {
    case 'text':
      return (
        <Sequence from={delayFrames} durationInFrames={durationInFrames}>
          <Wrap>
            <SafeText
              zone={elem.zone ?? 'MID'}
              style={elem.style ?? 'caption'}
              color={elem.color}
              entrance={elem.enter === 'wordByWord' ? 'wordByWord' : elem.enter === 'typewriter' ? 'typewriter' : 'fade'}
              delay={0}
            >
              {elem.content ?? ''}
            </SafeText>
          </Wrap>
        </Sequence>
      );

    case 'counter': {
      const countDurationS = elem._count_duration_s ?? 2.0;
      const countDurationFrames = Math.round(countDurationS * fps);
      const countDuration = Math.min(0.95, Math.max(0.1, countDurationFrames / durationInFrames));

      return (
        <Sequence from={delayFrames} durationInFrames={durationInFrames}>
          <Wrap>
            <Counter
              start={elem.start ?? 0}
              end={elem.end ?? 100}
              unit={elem.unit}
              description={elem.description}
              color={elem.color}
              zone={elem.zone ?? 'MID'}
              countDuration={countDuration}
            />
          </Wrap>
        </Sequence>
      );
    }

    case 'svg': {
      const illustrationElement = {
        svg: elem.svg!,
        position: elem.position,
        size: elem.size,
        color: elem.color,
        enter: (elem.enter as any) ?? 'fadeIn',
        delay: 0,
        animate: elem.animate,
        repeat: elem.repeat,
        stagger: elem.stagger,
        shake: elem.shake,
        holdMotion: elem.holdMotion as any,
      };

      return (
        <Sequence from={delayFrames} durationInFrames={durationInFrames}>
          <Wrap>
            <Illustration
              elements={[illustrationElement]}
              zone={elem.zone ?? 'MID'}
            />
          </Wrap>
        </Sequence>
      );
    }

    case 'custom_svg': {
      // Register a temporary icon component from inline paths, then render
      // through Illustration so we get the full animation system for free.
      const vb = elem.viewBox ?? '0 0 200 200';
      const ps = elem.paths ?? [];
      const tempKey = `__custom_${Math.random().toString(36).slice(2)}`;

      // Dynamically inject into SVG_LIBRARY for this render
      const { SVG_LIBRARY } = require('../lib/svgLibrary');
      SVG_LIBRARY[tempKey] = ({ color: c = '#ffffff', size: s = 200 }: { color?: string; size?: number }) => (
        <CustomSvg viewBox={vb} paths={ps} color={c} size={s} />
      );

      const illustrationElement = {
        svg: tempKey,
        position: elem.position,
        size: elem.size ?? 200,
        color: elem.color,
        enter: (elem.enter as any) ?? 'fadeIn',
        delay: 0,
        animate: elem.animate,
        repeat: elem.repeat,
        stagger: elem.stagger,
        shake: elem.shake,
        holdMotion: elem.holdMotion as any,
      };

      return (
        <Sequence from={delayFrames} durationInFrames={durationInFrames}>
          <Wrap>
            <Illustration
              elements={[illustrationElement]}
              zone={elem.zone ?? 'MID'}
            />
          </Wrap>
        </Sequence>
      );
    }

    case 'timeline_marker':
      return (
        <Sequence from={delayFrames} durationInFrames={durationInFrames}>
          <Wrap>
            <WordTimelineMarker
              year={elem.year!}
              label={elem.label!}
              color={elem.color}
              index={markerIndex ?? 0}
              totalMarkers={totalMarkers ?? 1}
            />
          </Wrap>
        </Sequence>
      );

    case 'bar':
      return (
        <Sequence from={delayFrames} durationInFrames={durationInFrames}>
          <Wrap>
            <WordBar
              label={elem.label!}
              value={elem.value!}
              color={elem.color}
              index={barIndex ?? 0}
              totalBars={totalBars ?? 1}
            />
          </Wrap>
        </Sequence>
      );

    case 'gauge':
      return (
        <Sequence from={delayFrames} durationInFrames={durationInFrames}>
          <Wrap>
            <GaugeMeter
              value={elem.value ?? 0}
              maxValue={elem.maxValue ?? 100}
              unit={elem.unit}
              label={elem.label}
              color={elem.color}
              zone={elem.zone ?? 'MID'}
              sweepDuration={elem.sweepDuration ?? 0.6}
              zones={elem.gauge_zones}
            />
          </Wrap>
        </Sequence>
      );

    case 'text_effect':
      return (
        <Sequence from={delayFrames} durationInFrames={durationInFrames}>
          <Wrap>
            <TextEffect
              text={elem.text ?? elem.content ?? ''}
              effect={(elem.effect as any) ?? 'stamp'}
              color={elem.color}
              zone={elem.zone ?? 'MID'}
              effectDuration={elem.effectDuration ?? 0.4}
            />
          </Wrap>
        </Sequence>
      );

    case 'transform':
      return (
        <Sequence from={delayFrames} durationInFrames={durationInFrames}>
          <Wrap>
            <TransformReveal
              from={{
                icon: elem.from_icon ?? 'person',
                label: elem.from_label,
                color: elem.from_color,
              }}
              to={{
                icon: elem.to_icon ?? 'skull',
                label: elem.to_label,
                color: elem.to_color,
              }}
              effect={(elem.effect as any) ?? 'crossfade'}
              transformAt={elem.transformAt ?? 0.5}
              zone={elem.zone ?? 'MID'}
            />
          </Wrap>
        </Sequence>
      );

    case 'progress_ring':
      return (
        <Sequence from={delayFrames} durationInFrames={durationInFrames}>
          <Wrap>
            <ProgressRing
              rings={elem.rings ?? [{ value: elem.value ?? 0, label: elem.label ?? '' }]}
              unit={elem.unit}
              zone={elem.zone ?? 'MID'}
            />
          </Wrap>
        </Sequence>
      );

    case 'flow_diagram':
      return (
        <Sequence from={delayFrames} durationInFrames={durationInFrames}>
          <Wrap>
            <FlowDiagram
              nodes={elem.nodes ?? []}
              direction={(elem.direction as any) ?? 'vertical'}
              arrowColor={elem.arrowColor}
              zone={elem.zone ?? 'MID'}
            />
          </Wrap>
        </Sequence>
      );

    case 'scale_comparison':
      return (
        <Sequence from={delayFrames} durationInFrames={durationInFrames}>
          <Wrap>
            <ScaleComparison
              left={elem.left ?? { label: '', value: 0 }}
              right={elem.right ?? { label: '', value: 0 }}
              unit={elem.unit}
              zone={elem.zone ?? 'MID'}
            />
          </Wrap>
        </Sequence>
      );

    case 'stacked_accumulation':
      return (
        <Sequence from={delayFrames} durationInFrames={durationInFrames}>
          <Wrap>
            <StackedAccumulation
              icon={elem.icon ?? 'skull'}
              count={elem.count ?? 10}
              label={elem.label}
              displayValue={elem.displayValue}
              color={elem.color}
              zone={elem.zone ?? 'MID'}
            />
          </Wrap>
        </Sequence>
      );

    case 'cause_effect':
      return (
        <Sequence from={delayFrames} durationInFrames={durationInFrames}>
          <Wrap>
            <CauseEffect
              dominoes={elem.dominoes ?? []}
              zone={elem.zone ?? 'MID'}
              chainSpeed={elem.chainSpeed ?? 0.12}
            />
          </Wrap>
        </Sequence>
      );

    case 'population_drop':
      return (
        <Sequence from={delayFrames} durationInFrames={durationInFrames}>
          <Wrap>
            <PopulationDrop
              startValue={elem.startValue ?? 100}
              endValue={elem.endValue ?? 0}
              unit={elem.unit}
              label={elem.label}
              color={elem.color}
            />
          </Wrap>
        </Sequence>
      );

    case 'path_draw':
      return (
        <Sequence from={delayFrames} durationInFrames={durationInFrames}>
          <Wrap>
            <SvgPathDraw
              paths={elem.paths ?? []}
              viewBox={elem.viewBox ?? '0 0 400 400'}
              size={elem.size ?? 300}
              zone={elem.zone ?? 'MID'}
              drawDuration={elem.drawDuration ?? 0.6}
              color={elem.color}
            />
          </Wrap>
        </Sequence>
      );

    case 'emphasis_line':
      return (
        <Sequence from={delayFrames} durationInFrames={durationInFrames}>
          <Wrap>
            <EmphasisLine
              color={elem.color}
              zone={elem.zone ?? 'MID'}
              width={elem.lineWidth ?? 0.6}
              style={(elem.lineStyle as 'underline' | 'strike') ?? 'underline'}
            />
          </Wrap>
        </Sequence>
      );

    case 'svg_morph':
      return (
        <Sequence from={delayFrames} durationInFrames={durationInFrames}>
          <Wrap>
            <SvgMorph
              fromPath={elem.fromPath ?? ''}
              toPath={elem.toPath ?? ''}
              viewBox={elem.viewBox ?? '0 0 200 200'}
              size={elem.size ?? 250}
              zone={elem.zone ?? 'MID'}
              morphAt={elem.morphAt ?? 0.3}
              morphDuration={elem.morphDuration ?? 0.3}
              fromColor={elem.fromColor ?? elem.color}
              toColor={elem.toColor ?? elem.color}
              filled={elem.filled ?? false}
            />
          </Wrap>
        </Sequence>
      );

    case 'split_screen':
      return (
        <Sequence from={delayFrames} durationInFrames={durationInFrames}>
          <Wrap>
            <SplitScreenReveal
              left={elem.leftPanel ?? { label: '', color: '#FFD700' }}
              right={elem.rightPanel ?? { label: '', color: '#3B82F6' }}
              zone={elem.zone ?? 'MID'}
              direction={(elem.splitDirection as 'horizontal' | 'vertical') ?? 'horizontal'}
            />
          </Wrap>
        </Sequence>
      );

    case 'pie_chart':
      return (
        <Sequence from={delayFrames} durationInFrames={durationInFrames}>
          <Wrap>
            <AnimatedPieChart
              segments={elem.segments ?? []}
              zone={elem.zone ?? 'MID'}
              size={elem.size ?? 280}
              innerRadius={elem.innerRadius ?? 0.55}
              centerLabel={elem.centerLabel}
              centerValue={elem.centerValue}
              showLabels={elem.showLabels ?? true}
            />
          </Wrap>
        </Sequence>
      );

    case 'number_ticker':
      return (
        <Sequence from={delayFrames} durationInFrames={durationInFrames}>
          <Wrap>
            <NumberTicker
              value={elem.tickerValue ?? elem.end ?? 0}
              prefix={elem.prefix}
              suffix={elem.suffix}
              unit={elem.unit}
              color={elem.color}
              zone={elem.zone ?? 'MID'}
              decimals={elem.decimals ?? 0}
            />
          </Wrap>
        </Sequence>
      );

    case 'bar_race':
      return (
        <Sequence from={delayFrames} durationInFrames={durationInFrames}>
          <Wrap>
            <AnimatedBarRace
              bars={elem.raceBars ?? []}
              zone={elem.zone ?? 'MID'}
              sortAfterGrow={elem.sortAfterGrow ?? true}
              showValues={elem.showValues ?? true}
              unit={elem.barUnit ?? ''}
            />
          </Wrap>
        </Sequence>
      );

    case 'map_highlight':
      return (
        <Sequence from={delayFrames} durationInFrames={durationInFrames}>
          <Wrap>
            <MapHighlight
              pins={elem.pins ?? []}
              zone={elem.zone ?? 'MID'}
              size={elem.size ?? 400}
              accentColor={elem.color}
              connectPins={elem.connectPins ?? false}
            />
          </Wrap>
        </Sequence>
      );

    default:
      return null;
  }
};

export const WordTriggeredScene: React.FC<WordTriggeredSceneProps> = ({
  scene,
  bgColor,
  accentColor,
  secondaryColor,
  debug = false,
}) => {
  const { durationInFrames } = useVideoConfig();

  // Compute per-element durations (handles until_replaced)
  const elementDurations = computeElementDurations(scene.elements, durationInFrames);

  // Separate by type for indexing
  const timelineMarkers = scene.elements.filter(e => e.type === 'timeline_marker');
  const bars = scene.elements.filter(e => e.type === 'bar');
  const otherElements = scene.elements.filter(e => e.type !== 'timeline_marker' && e.type !== 'bar');

  // Get original indices for duration lookup
  const getOrigIdx = (elem: ResolvedElement) => scene.elements.indexOf(elem);

  return (
    <SlowZoom from={1.0} to={1.06}>
    <AbsoluteFill>
      {/* Background layers — parallax depth for cinematic feel */}
      <ParallaxLayer depth={0.3} direction="diagonal" distance={25}>
        <div style={{ position: 'absolute', inset: 0, zIndex: 0 }}>
          <GradientBg color={bgColor} accentColor={accentColor} secondaryColor={secondaryColor} />
        </div>
        <div style={{ position: 'absolute', inset: 0, zIndex: 1 }}>
          <GridLines />
        </div>
      </ParallaxLayer>
      <ParallaxLayer depth={0.6} direction="up" distance={20}>
        <div style={{ position: 'absolute', inset: 0, zIndex: 2 }}>
          <ParticleField color={accentColor} count={30} speed={1.5} />
        </div>
      </ParallaxLayer>

      {/* Scene label pill */}
      <LabelPill text={scene.label} />

      {/* Timeline markers with positional indexing */}
      {timelineMarkers.length > 0 && (
        <div style={{ position: 'absolute', inset: 0, zIndex: 10 }}>
          {timelineMarkers.map((elem, i) => (
            <ElementRenderer
              key={`tl-${i}`}
              elem={elem}
              durationInFrames={elementDurations.get(getOrigIdx(elem)) ?? durationInFrames}
              markerIndex={i}
              totalMarkers={timelineMarkers.length}
              zIndex={10 + i}
            />
          ))}
        </div>
      )}

      {/* Bar chart bars with positional indexing */}
      {bars.length > 0 && (
        <div style={{ position: 'absolute', inset: 0, zIndex: 10 }}>
          {bars.map((elem, i) => (
            <ElementRenderer
              key={`bar-${i}`}
              elem={elem}
              durationInFrames={elementDurations.get(getOrigIdx(elem)) ?? durationInFrames}
              barIndex={i}
              totalBars={bars.length}
              zIndex={10 + i}
            />
          ))}
        </div>
      )}

      {/* All other elements — z-index increases with trigger time so later elements render in front */}
      <div style={{ position: 'absolute', inset: 0, zIndex: 15 }}>
        {otherElements.map((elem, i) => (
          <ElementRenderer
            key={`elem-${i}`}
            elem={elem}
            durationInFrames={elementDurations.get(getOrigIdx(elem)) ?? durationInFrames}
            zIndex={20 + i}
          />
        ))}
      </div>

      {/* Cinematic overlays — top layer */}
      <div style={{ position: 'absolute', inset: 0, zIndex: 90 }}>
        <VignetteOverlay intensity={0.35} spread={0.25} />
      </div>
      <div style={{ position: 'absolute', inset: 0, zIndex: 91 }}>
        <NoiseOverlay opacity={0.03} />
      </div>

      {/* Debug overlay — renders zone boundaries, safe areas, frame counter */}
      {debug && <DebugOverlay />}
    </AbsoluteFill>
    </SlowZoom>
  );
};
