/**
 * TKK Manifest Schema — Zod validation for screenplay manifests.
 *
 * Claude generates JSON matching this schema. Pre-built components render each scene type.
 */
import { z } from 'zod';

const ZoneName = z.enum(['TITLE', 'UPPER', 'MID', 'LOWER', 'FOOTER']);
const TextStyle = z.enum(['headline', 'caption', 'stat', 'label']);

const TextElement = z.object({
  content: z.string(),
  zone: ZoneName,
  style: TextStyle.default('caption'),
  color: z.string().optional(),
  fontSize: z.number().optional(),
  entrance: z.enum(['fade', 'typewriter', 'wordByWord']).default('fade').optional(),
});

const SceneBase = z.object({
  label: z.string(),
  text: z.array(TextElement).optional(),
});

// ── Scene Types ─────────────────────────────────────────────

export const HeadlineScene = SceneBase.extend({
  type: z.literal('headline'),
  props: z.object({
    title: z.string(),
    subtitle: z.string().optional(),
    zone: ZoneName.default('MID'),
    color: z.string().optional(),
  }),
});

export const CounterScene = SceneBase.extend({
  type: z.literal('counter'),
  props: z.object({
    start: z.number(),
    end: z.number(),
    unit: z.string().optional(),
    description: z.string().optional(),
    color: z.string().optional(),
    zone: ZoneName.default('MID'),
    countDuration: z.number().min(0.1).max(0.95).default(0.6),
  }),
});

export const BarChartScene = SceneBase.extend({
  type: z.literal('barChart'),
  props: z.object({
    bars: z.array(z.object({
      label: z.string(),
      value: z.number(),
      color: z.string().optional(),
    })),
    maxValue: z.number().optional(),
    zone: ZoneName.default('MID'),
    xLabel: z.string().optional(),
    yLabel: z.string().optional(),
  }),
});

export const TimelineScene = SceneBase.extend({
  type: z.literal('timeline'),
  props: z.object({
    markers: z.array(z.object({
      year: z.string(),
      label: z.string(),
      color: z.string().optional(),
    })),
    zone: ZoneName.default('MID'),
    axisLabel: z.string().optional(),
  }),
});

export const KenBurnsScene = SceneBase.extend({
  type: z.literal('kenburns'),
  props: z.object({
    image: z.string(),
    startScale: z.number().default(1.2),
    endScale: z.number().default(1.0),
    panX: z.number().default(0),
    panY: z.number().default(0),
    zone: ZoneName.default('MID'),
  }),
});

export const MapScene = SceneBase.extend({
  type: z.literal('map'),
  props: z.object({
    image: z.string(),
    markers: z.array(z.object({
      x: z.number(),
      y: z.number(),
      label: z.string(),
      color: z.string().optional(),
      delay: z.number().default(0),
    })).optional(),
    zone: ZoneName.default('MID'),
  }),
});

export const VideoClipScene = SceneBase.extend({
  type: z.literal('videoClip'),
  props: z.object({
    src: z.string(),
    startFrom: z.number().default(0),
    endAt: z.number().optional(),
    objectFit: z.enum(['cover', 'contain']).default('cover'),
    zone: ZoneName.default('MID'),
  }),
});

export const SplitCompareScene = SceneBase.extend({
  type: z.literal('splitCompare'),
  props: z.object({
    leftImage: z.string(),
    rightImage: z.string(),
    leftLabel: z.string().optional(),
    rightLabel: z.string().optional(),
  }),
});

export const IconRowScene = SceneBase.extend({
  type: z.literal('iconRow'),
  props: z.object({
    icons: z.array(z.object({
      image: z.string(),
      label: z.string().optional(),
    })),
    zone: ZoneName.default('MID'),
    staggerDelay: z.number().default(0.15),
  }),
});

export const PopulationDropScene = SceneBase.extend({
  type: z.literal('populationDrop'),
  props: z.object({
    startValue: z.number(),
    endValue: z.number(),
    unit: z.string().optional(),
    label: z.string().optional(),
    color: z.string().optional(),
  }),
});

const IllustrationElementSchema = z.object({
  svg: z.string(),
  position: z.object({ x: z.number(), y: z.number() }).optional(),
  size: z.number().optional(),
  color: z.string().optional(),
  delay: z.number().optional(),
  enter: z.enum(['fadeIn', 'slideLeft', 'slideRight', 'slideUp', 'pop', 'drop', 'stamp', 'grow', 'shatter']).optional(),
  animate: z.object({
    x: z.number().optional(),
    y: z.number().optional(),
    opacity: z.number().optional(),
    scale: z.number().optional(),
  }).optional(),
  repeat: z.number().optional(),
  stagger: z.number().optional(),
  shake: z.boolean().optional(),
  holdMotion: z.enum(['float', 'drift', 'pulse', 'breathe', 'orbit', 'none', 'tremble', 'swing', 'glow']).default('float').optional(),
});

export const IllustrationScene = SceneBase.extend({
  type: z.literal('illustration'),
  props: z.object({
    elements: z.array(IllustrationElementSchema),
    zone: ZoneName.default('MID'),
  }),
});

// ── New Scene Types (Visual Library Expansion) ──────────────

export const GaugeMeterScene = SceneBase.extend({
  type: z.literal('gaugeMeter'),
  props: z.object({
    value: z.number(),
    maxValue: z.number().default(100),
    unit: z.string().optional(),
    label: z.string().optional(),
    color: z.string().optional(),
    zones: z.array(z.object({
      from: z.number(),
      to: z.number(),
      color: z.string(),
    })).optional(),
    zone: ZoneName.default('MID'),
    sweepDuration: z.number().min(0.1).max(0.95).default(0.6),
  }),
});

export const FlowDiagramScene = SceneBase.extend({
  type: z.literal('flowDiagram'),
  props: z.object({
    nodes: z.array(z.object({
      label: z.string(),
      icon: z.string().optional(),
      color: z.string().optional(),
    })).min(2).max(5),
    direction: z.enum(['vertical', 'horizontal']).default('vertical'),
    arrowColor: z.string().optional(),
    zone: ZoneName.default('MID'),
  }),
});

export const ScaleComparisonScene = SceneBase.extend({
  type: z.literal('scaleComparison'),
  props: z.object({
    left: z.object({
      label: z.string(),
      icon: z.string().optional(),
      value: z.number(),
      color: z.string().optional(),
    }),
    right: z.object({
      label: z.string(),
      icon: z.string().optional(),
      value: z.number(),
      color: z.string().optional(),
    }),
    unit: z.string().optional(),
    zone: ZoneName.default('MID'),
  }),
});

export const ProgressRingScene = SceneBase.extend({
  type: z.literal('progressRing'),
  props: z.object({
    rings: z.array(z.object({
      value: z.number(),
      maxValue: z.number().default(100),
      label: z.string(),
      color: z.string().optional(),
    })).min(1).max(3),
    unit: z.string().optional(),
    zone: ZoneName.default('MID'),
    fillDuration: z.number().min(0.1).max(0.95).default(0.5),
  }),
});

export const StackedAccumulationScene = SceneBase.extend({
  type: z.literal('stackedAccumulation'),
  props: z.object({
    icon: z.string(),
    count: z.number().min(1).max(30),
    label: z.string().optional(),
    displayValue: z.string().optional(),
    color: z.string().optional(),
    zone: ZoneName.default('MID'),
  }),
});

export const TransformRevealScene = SceneBase.extend({
  type: z.literal('transformReveal'),
  props: z.object({
    from: z.object({
      icon: z.string(),
      label: z.string().optional(),
      color: z.string().optional(),
    }),
    to: z.object({
      icon: z.string(),
      label: z.string().optional(),
      color: z.string().optional(),
    }),
    effect: z.enum(['crossfade', 'shatter', 'shrinkGrow', 'glitch']).default('crossfade'),
    transformAt: z.number().min(0.1).max(0.9).default(0.5),
    zone: ZoneName.default('MID'),
  }),
});

export const CauseEffectScene = SceneBase.extend({
  type: z.literal('causeEffect'),
  props: z.object({
    dominoes: z.array(z.object({
      label: z.string(),
      icon: z.string().optional(),
      color: z.string().optional(),
    })).min(2).max(6),
    zone: ZoneName.default('MID'),
    chainSpeed: z.number().default(0.12),
  }),
});

export const TextEffectScene = SceneBase.extend({
  type: z.literal('textEffect'),
  props: z.object({
    text: z.string(),
    effect: z.enum(['glitch', 'stamp', 'shake', 'redacted', 'colorShift']).default('stamp'),
    color: z.string().optional(),
    zone: ZoneName.default('MID'),
    effectDuration: z.number().min(0.1).max(0.95).default(0.4),
  }),
});

// ── Discriminated Union ─────────────────────────────────────

export const SceneSchema = z.discriminatedUnion('type', [
  HeadlineScene,
  CounterScene,
  BarChartScene,
  TimelineScene,
  KenBurnsScene,
  MapScene,
  VideoClipScene,
  SplitCompareScene,
  IconRowScene,
  PopulationDropScene,
  IllustrationScene,
  GaugeMeterScene,
  FlowDiagramScene,
  ScaleComparisonScene,
  ProgressRingScene,
  StackedAccumulationScene,
  TransformRevealScene,
  CauseEffectScene,
  TextEffectScene,
]);

export type SceneConfig = z.infer<typeof SceneSchema>;

// ── Full Manifest ───────────────────────────────────────────

export const ManifestSchema = z.object({
  topic: z.string(),
  ttsScript: z.string(),
  colors: z.object({
    bg: z.string().default('#080A10'),
    accent: z.string().default('#FFD700'),
    secondary: z.string().default('#3B82F6'),
  }),
  scenes: z.array(SceneSchema).min(1).max(8),
});

export type Manifest = z.infer<typeof ManifestSchema>;
