/**
 * Manifest QA — static analysis on manifest JSON to catch quality issues.
 *
 * Usage: npx tsx src/qa_manifest.ts <topic>
 *        npx tsx src/qa_manifest.ts manifests/tunguska.json
 */
import { readFileSync, existsSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { ManifestSchema } from './schema';
import { SAFE } from './lib/zones';

const __dirname = dirname(fileURLToPath(import.meta.url));

// WCAG luminance
function hexToLum(hex: string): number {
  const h = hex.replace('#', '');
  if (h.length < 6) return 0.5;
  const r = parseInt(h.slice(0, 2), 16) / 255;
  const g = parseInt(h.slice(2, 4), 16) / 255;
  const b = parseInt(h.slice(4, 6), 16) / 255;
  const lin = (c: number) => c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
}
function contrast(fg: string, bg: string): number {
  const l1 = hexToLum(fg), l2 = hexToLum(bg);
  return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
}

interface Warning {
  scene: number;
  check: string;
  severity: 'warn' | 'fail';
  message: string;
}

// Resolve topic
let input = process.argv[2];
if (!input) {
  console.error('Usage: npx tsx src/qa_manifest.ts <topic|path>');
  process.exit(1);
}

// Accept topic name or full path
let manifestPath: string;
if (input.endsWith('.json')) {
  manifestPath = resolve(input);
} else {
  manifestPath = resolve(__dirname, 'manifests', `${input}.json`);
}

if (!existsSync(manifestPath)) {
  console.error(`Manifest not found: ${manifestPath}`);
  process.exit(1);
}

const raw = JSON.parse(readFileSync(manifestPath, 'utf-8'));
const manifest = ManifestSchema.parse(raw);
const bg = manifest.colors.bg;
const warnings: Warning[] = [];

// Load timings if available
const vidgenDir = resolve(__dirname, '../..');
const timingsPath = resolve(vidgenDir, `tts_${manifest.topic}_timings.json`);
let sceneDurations: number[] | null = null;
if (existsSync(timingsPath)) {
  const t = JSON.parse(readFileSync(timingsPath, 'utf-8'));
  sceneDurations = t.scene_durations;
}

manifest.scenes.forEach((scene, i) => {
  const sceneNum = i + 1;
  const dur = sceneDurations?.[i] ?? 5;

  // Check 1: Contrast
  if (scene.type === 'illustration') {
    for (const el of scene.props.elements) {
      if (el.color) {
        const cr = contrast(el.color, bg);
        if (cr < 3) {
          warnings.push({
            scene: sceneNum,
            check: 'contrast',
            severity: 'fail',
            message: `Icon "${el.svg}" color ${el.color} has contrast ratio ${cr.toFixed(1)}:1 against bg ${bg} (need 3:1+)`,
          });
        }
      }
    }
  }

  // Check 2: Text contrast
  if (scene.text) {
    for (const t of scene.text) {
      const tc = t.color ?? '#F0F0F0';
      const cr = contrast(tc, bg);
      if (cr < 4.5) {
        warnings.push({
          scene: sceneNum,
          check: 'text-contrast',
          severity: cr < 3 ? 'fail' : 'warn',
          message: `Text "${t.content.slice(0, 30)}..." color ${tc} contrast ${cr.toFixed(1)}:1 (need 4.5:1)`,
        });
      }
    }
  }

  // Check 3: Animation density
  let animatedCount = 0;
  if (scene.type === 'illustration') {
    animatedCount = scene.props.elements.length;
  } else if (scene.type === 'barChart') {
    animatedCount = scene.props.bars.length;
  } else if (scene.type === 'timeline') {
    animatedCount = scene.props.markers.length;
  } else if (scene.type === 'counter' || scene.type === 'populationDrop') {
    animatedCount = 1;
  } else if (scene.type === 'headline') {
    animatedCount = 1;
  }
  if (animatedCount < 2 && (scene.text?.length ?? 0) < 1) {
    warnings.push({
      scene: sceneNum,
      check: 'animation-density',
      severity: 'warn',
      message: `Only ${animatedCount} animated element(s) and no text overlays — may feel empty`,
    });
  }

  // Check 4: Dead time (scene > 4s with no animate/holdMotion on illustration)
  if (scene.type === 'illustration' && dur > 4) {
    const hasMotion = scene.props.elements.some(
      el => el.animate || el.shake || (el.holdMotion && el.holdMotion !== 'none')
    );
    // Default holdMotion is 'float', so only warn if explicitly set to 'none' on all
    const allNone = scene.props.elements.every(el => el.holdMotion === 'none');
    if (allNone && !hasMotion) {
      warnings.push({
        scene: sceneNum,
        check: 'dead-time',
        severity: 'warn',
        message: `${dur.toFixed(1)}s scene with all holdMotion='none' and no animate props — will feel static`,
      });
    }
  }

  // Check 5: Text overflow estimation
  if (scene.text) {
    for (const t of scene.text) {
      const fontSize = t.fontSize ?? 48;
      const estimatedWidth = t.content.length * fontSize * 0.55;
      if (estimatedWidth > SAFE.width) {
        warnings.push({
          scene: sceneNum,
          check: 'text-overflow',
          severity: 'warn',
          message: `Text "${t.content.slice(0, 25)}..." estimated at ${Math.round(estimatedWidth)}px, safe width is ${SAFE.width}px`,
        });
      }
    }
  }

  // Check 6: Zone overlap — two text elements in same zone
  if (scene.text && scene.text.length > 1) {
    const zones = scene.text.map(t => t.zone);
    const dupes = zones.filter((z, idx) => zones.indexOf(z) !== idx);
    if (dupes.length > 0) {
      warnings.push({
        scene: sceneNum,
        check: 'zone-overlap',
        severity: 'warn',
        message: `Multiple text elements in zone ${dupes[0]} — may overlap`,
      });
    }
  }
});

// Output
console.log(`\n=== Manifest QA: ${manifest.topic} (${manifest.scenes.length} scenes) ===\n`);

if (warnings.length === 0) {
  console.log('  All checks passed.\n');
} else {
  const fails = warnings.filter(w => w.severity === 'fail');
  const warns = warnings.filter(w => w.severity === 'warn');

  for (const w of warnings) {
    const icon = w.severity === 'fail' ? '[X]' : '[!]';
    console.log(`  ${icon} Scene ${w.scene} (${w.check}): ${w.message}`);
  }

  console.log(`\n  Result: ${fails.length} fails, ${warns.length} warns\n`);
  if (fails.length > 0) process.exit(1);
}
