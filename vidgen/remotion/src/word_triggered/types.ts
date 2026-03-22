/**
 * Types for the word-triggered manifest system.
 * These represent the resolved output from resolve_word_triggers.py.
 */

export interface ResolvedTiming {
  delay_frames: number;
  delay_s: number;
  anchor_word: string;
  anchor_time_s: number;
  absolute_frame: number;
  absolute_s: number;
}

export interface ResolvedElement {
  type: 'text' | 'counter' | 'svg' | 'timeline_marker' | 'bar' | 'gauge' | 'text_effect' | 'transform' | 'progress_ring';
  _resolved: ResolvedTiming;

  // Text props
  content?: string;
  zone?: 'TITLE' | 'UPPER' | 'MID' | 'LOWER' | 'FOOTER';
  style?: 'headline' | 'caption' | 'stat' | 'label';
  color?: string;
  fontSize?: number;
  enter?: string;
  hold?: string;
  replaces_zone?: boolean;

  // Counter props
  start?: number;
  end?: number;
  unit?: string;
  description?: string;
  count_end_anchor?: string;
  _count_end_s?: number;
  _count_duration_s?: number;

  // SVG / Illustration props
  svg?: string;
  position?: { x: number; y: number };
  size?: number;
  animate?: { x?: number; y?: number; opacity?: number; scale?: number };
  repeat?: number;
  stagger?: number;
  shake?: boolean;
  holdMotion?: string;

  // Timeline marker props
  year?: string;
  label?: string;

  // Bar props
  value?: number;

  // Gauge props
  maxValue?: number;
  sweepDuration?: number;
  gauge_zones?: Array<{ from: number; to: number; color: string }>;

  // TextEffect props
  text?: string;
  effect?: string;
  effectDuration?: number;

  // TransformReveal props
  from_icon?: string;
  from_label?: string;
  from_color?: string;
  to_icon?: string;
  to_label?: string;
  to_color?: string;
  transformAt?: number;

  // ProgressRing props
  rings?: Array<{ value: number; maxValue?: number; label: string; color?: string }>;

  // Common
  anchor?: string;
  attack?: number;
}

export interface ResolvedScene {
  id: string;
  label: string;
  type: string;
  start_s: number;
  end_s: number;
  duration_s: number;
  duration_frames: number;
  elements: ResolvedElement[];
}

export interface ResolvedManifest {
  topic: string;
  colors: {
    bg: string;
    accent: string;
    secondary: string;
  };
  fps: number;
  total_duration_s: number;
  total_frames: number;
  scene_durations: number[];
  scenes: ResolvedScene[];
}
