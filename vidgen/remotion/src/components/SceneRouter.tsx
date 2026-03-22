import React from 'react';
import { AbsoluteFill } from 'remotion';
import type { SceneConfig } from '../schema';
import { GradientBg } from './GradientBg';
import { GridLines } from './GridLines';
import { LabelPill } from './LabelPill';
import { SafeText } from './SafeText';
import { Headline } from './Headline';
import { Counter } from './Counter';
import { BarChart } from './BarChart';
import { Timeline } from './Timeline';
import { KenBurns } from './KenBurns';
import { MapView } from './MapView';
import { VideoClip } from './VideoClip';
import { SplitCompare } from './SplitCompare';
import { IconRow } from './IconRow';
import { PopulationDrop } from './PopulationDrop';
import { Illustration } from './Illustration';
import { GaugeMeter } from './GaugeMeter';
import { FlowDiagram } from './FlowDiagram';
import { ScaleComparison } from './ScaleComparison';
import { ProgressRing } from './ProgressRing';
import { StackedAccumulation } from './StackedAccumulation';
import { TransformReveal } from './TransformReveal';
import { CauseEffect } from './CauseEffect';
import { TextEffect } from './TextEffect';
import { ParticleField } from './ParticleField';

interface SceneRouterProps {
  scene: SceneConfig;
  bgColor?: string;
  accentColor?: string;
  secondaryColor?: string;
}

/** Routes a manifest scene entry to the corresponding pre-built component. */
export const SceneRouter: React.FC<SceneRouterProps> = ({ scene, bgColor, accentColor, secondaryColor }) => {
  const content = (() => {
    switch (scene.type) {
      case 'headline':
        return <Headline title={scene.props.title} subtitle={scene.props.subtitle} zone={scene.props.zone} color={scene.props.color} />;
      case 'counter':
        return <Counter start={scene.props.start} end={scene.props.end} unit={scene.props.unit} description={scene.props.description} color={scene.props.color} zone={scene.props.zone} countDuration={scene.props.countDuration} />;
      case 'barChart':
        return <BarChart bars={scene.props.bars} maxValue={scene.props.maxValue} zone={scene.props.zone} xLabel={scene.props.xLabel} yLabel={scene.props.yLabel} />;
      case 'timeline':
        return <Timeline markers={scene.props.markers} zone={scene.props.zone} axisLabel={scene.props.axisLabel} />;
      case 'kenburns':
        return <KenBurns image={scene.props.image} startScale={scene.props.startScale} endScale={scene.props.endScale} panX={scene.props.panX} panY={scene.props.panY} zone={scene.props.zone} />;
      case 'map':
        return <MapView image={scene.props.image} markers={scene.props.markers} zone={scene.props.zone} />;
      case 'videoClip':
        return <VideoClip src={scene.props.src} startFrom={scene.props.startFrom} endAt={scene.props.endAt} objectFit={scene.props.objectFit} zone={scene.props.zone} />;
      case 'splitCompare':
        return <SplitCompare leftImage={scene.props.leftImage} rightImage={scene.props.rightImage} leftLabel={scene.props.leftLabel} rightLabel={scene.props.rightLabel} />;
      case 'iconRow':
        return <IconRow icons={scene.props.icons} zone={scene.props.zone} staggerDelay={scene.props.staggerDelay} />;
      case 'populationDrop':
        return <PopulationDrop startValue={scene.props.startValue} endValue={scene.props.endValue} unit={scene.props.unit} label={scene.props.label} color={scene.props.color} />;
      case 'illustration':
        return <Illustration elements={scene.props.elements} zone={scene.props.zone} />;
      case 'gaugeMeter':
        return <GaugeMeter value={scene.props.value} maxValue={scene.props.maxValue} unit={scene.props.unit} label={scene.props.label} zones={scene.props.zones} zone={scene.props.zone} sweepDuration={scene.props.sweepDuration} color={scene.props.color} />;
      case 'flowDiagram':
        return <FlowDiagram nodes={scene.props.nodes} direction={scene.props.direction} arrowColor={scene.props.arrowColor} zone={scene.props.zone} />;
      case 'scaleComparison':
        return <ScaleComparison left={scene.props.left} right={scene.props.right} unit={scene.props.unit} zone={scene.props.zone} />;
      case 'progressRing':
        return <ProgressRing rings={scene.props.rings} unit={scene.props.unit} zone={scene.props.zone} fillDuration={scene.props.fillDuration} />;
      case 'stackedAccumulation':
        return <StackedAccumulation icon={scene.props.icon} count={scene.props.count} label={scene.props.label} displayValue={scene.props.displayValue} color={scene.props.color} zone={scene.props.zone} />;
      case 'transformReveal':
        return <TransformReveal from={scene.props.from} to={scene.props.to} effect={scene.props.effect} transformAt={scene.props.transformAt} zone={scene.props.zone} />;
      case 'causeEffect':
        return <CauseEffect dominoes={scene.props.dominoes} zone={scene.props.zone} chainSpeed={scene.props.chainSpeed} />;
      case 'textEffect':
        return <TextEffect text={scene.props.text} effect={scene.props.effect} color={scene.props.color} zone={scene.props.zone} effectDuration={scene.props.effectDuration} />;
      default:
        return null;
    }
  })();

  return (
    <AbsoluteFill>
      <div style={{ position: 'absolute', inset: 0, zIndex: 0 }}><GradientBg color={bgColor} accentColor={accentColor} secondaryColor={secondaryColor} /></div>
      <div style={{ position: 'absolute', inset: 0, zIndex: 1 }}><GridLines /></div>
      <div style={{ position: 'absolute', inset: 0, zIndex: 2 }}><ParticleField color={accentColor} /></div>
      <LabelPill text={scene.label} />
      <div style={{ position: 'absolute', inset: 0, zIndex: 10 }}>{content}</div>
      {/* Render additional text elements from manifest */}
      {scene.text?.map((t, i) => (
        <SafeText key={i} zone={t.zone} style={t.style} color={t.color} fontSize={t.fontSize} delay={i * 0.2} entrance={t.entrance}>
          {t.content}
        </SafeText>
      ))}
    </AbsoluteFill>
  );
};
