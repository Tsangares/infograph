/**
 * TKK Remotion Preview CLI — exports scene preview PNGs.
 *
 * Usage: npx tsx preview.mts <topic>
 *   Output: ../previews/{topic}_scene_{N}.png          (primary, 75%)
 *           ../previews/{topic}_scene_{N}_{25,50,75,95}.png
 *
 * Supports both legacy (type-based) and word-triggered manifests.
 */
import { bundle } from '@remotion/bundler';
import { renderStill, selectComposition } from '@remotion/renderer';
import { readFileSync, existsSync, mkdirSync } from 'fs';
import { execSync } from 'child_process';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { ManifestSchema } from './src/schema';

const __dirname = dirname(fileURLToPath(import.meta.url));
const vidgenDir = resolve(__dirname, '..');
const venvPython = resolve(vidgenDir, '.venv/bin/python3');

const topic = process.argv[2];
if (!topic) {
  console.error('Usage: npx tsx preview.mts <topic>');
  process.exit(1);
}

// Load raw manifest
const manifestPath = resolve(__dirname, 'src/manifests', `${topic}.json`);
if (!existsSync(manifestPath)) {
  console.error(`Manifest not found: ${manifestPath}`);
  process.exit(1);
}
const rawManifest = JSON.parse(readFileSync(manifestPath, 'utf-8'));

// Format detection
const isWordTriggered = rawManifest.scenes?.[0]?.scene_anchor != null;

const previewDir = resolve(vidgenDir, 'previews');
mkdirSync(previewDir, { recursive: true });

async function main() {
  console.log('  Bundling...');
  const bundled = await bundle({
    entryPoint: resolve(__dirname, 'src/index.ts'),
    publicDir: resolve(__dirname, 'public'),
  });

  if (isWordTriggered) {
    // ── Word-triggered path ──
    console.log(`  Format: word-triggered`);

    // Load or auto-resolve
    const resolvedPath = resolve(vidgenDir, `${topic}_resolved.json`);
    if (!existsSync(resolvedPath)) {
      console.log('  Resolved JSON not found — running resolver...');
      try {
        execSync(`${venvPython} ${resolve(vidgenDir, 'resolve_word_triggers.py')} ${topic}`, {
          cwd: vidgenDir, encoding: 'utf-8', timeout: 30000,
        });
      } catch (err: any) {
        console.error('  Resolver failed:', err.stdout || err.stderr || err.message);
        process.exit(1);
      }
    }
    if (!existsSync(resolvedPath)) {
      console.error(`  Resolved manifest not found: ${resolvedPath}`);
      process.exit(1);
    }

    const resolvedManifest = JSON.parse(readFileSync(resolvedPath, 'utf-8'));
    const totalFrames = resolvedManifest.total_frames;

    const composition = await selectComposition({
      serveUrl: bundled,
      id: 'word-triggered',
      inputProps: { manifest: resolvedManifest },
    });
    composition.durationInFrames = totalFrames;
    composition.width = 1080;
    composition.height = 1920;

    // Render 4 frames per scene at 25%, 50%, 75%, 95%, accounting for TransitionSeries overlap
    const transitionFrames = 25;
    const capturePoints = [25, 50, 75, 95] as const;
    const primaryPercent = 75; // used for the plain {topic}_scene_{N}.png
    let frameOffset = 0;
    for (let i = 0; i < resolvedManifest.scenes.length; i++) {
      const scene = resolvedManifest.scenes[i];
      const sceneFrames = scene.duration_frames;
      const overlapBefore = Math.min(i, resolvedManifest.scenes.length - 1) * transitionFrames;
      const sceneStart = frameOffset - overlapBefore;

      for (const pct of capturePoints) {
        const captureFrame = sceneStart + Math.round(sceneFrames * pct / 100);
        const clampedFrame = Math.max(0, Math.min(captureFrame, totalFrames - 1));
        const pctPath = resolve(previewDir, `${topic}_scene_${i + 1}_${pct}.png`);

        console.log(`  Scene ${i + 1} @${pct}%: frame ${clampedFrame} (${scene.label}) → ${pctPath}`);
        await renderStill({
          composition,
          serveUrl: bundled,
          frame: clampedFrame,
          output: pctPath,
          inputProps: { manifest: resolvedManifest },
        });

        // Also write the primary preview as the 75% frame
        if (pct === primaryPercent) {
          const primaryPath = resolve(previewDir, `${topic}_scene_${i + 1}.png`);
          await renderStill({
            composition,
            serveUrl: bundled,
            frame: clampedFrame,
            output: primaryPath,
            inputProps: { manifest: resolvedManifest },
          });
        }
      }

      frameOffset += sceneFrames;
    }

    console.log(`\n  All ${resolvedManifest.scenes.length} previews → ${previewDir}/`);

  } else {
    // ── Legacy path (unchanged) ──
    console.log(`  Format: legacy`);
    const manifest = ManifestSchema.parse(rawManifest);

    // Load timings
    const timingsPath = resolve(vidgenDir, `tts_${topic}_timings.json`);
    let sceneDurations: number[];
    if (existsSync(timingsPath)) {
      const timings = JSON.parse(readFileSync(timingsPath, 'utf-8'));
      sceneDurations = timings.scene_durations;

      if (timings.calibrations) {
        for (const [key, cal] of Object.entries(timings.calibrations)) {
          const idx = parseInt(key.replace('scene_', ''));
          const calibration = cal as Record<string, number>;
          if (calibration.countDuration != null && manifest.scenes[idx]?.props) {
            (manifest.scenes[idx].props as any).countDuration = calibration.countDuration;
          }
        }
      }
    } else {
      sceneDurations = manifest.scenes.map(() => 5);
    }

    const totalFrames = sceneDurations.reduce((sum, d) => sum + Math.round(d * 30), 0);

    const composition = await selectComposition({
      serveUrl: bundled,
      id: 'demo',
      inputProps: { manifest, sceneDurations },
    });
    composition.durationInFrames = totalFrames;
    composition.width = 1080;
    composition.height = 1920;

    const transitionFrames = 25;
    const capturePoints = [25, 50, 75, 95] as const;
    const primaryPercent = 75;
    let frameOffset = 0;
    for (let i = 0; i < manifest.scenes.length; i++) {
      const sceneFrames = Math.round(sceneDurations[i] * 30);
      const overlapBefore = Math.min(i, manifest.scenes.length - 1) * transitionFrames;
      const sceneStart = frameOffset - overlapBefore;

      for (const pct of capturePoints) {
        const captureFrame = sceneStart + Math.round(sceneFrames * pct / 100);
        const clampedFrame = Math.max(0, Math.min(captureFrame, totalFrames - 1));
        const pctPath = resolve(previewDir, `${topic}_scene_${i + 1}_${pct}.png`);

        console.log(`  Scene ${i + 1} @${pct}%: frame ${clampedFrame} (offset=${frameOffset}, overlap=${overlapBefore}) → ${pctPath}`);
        await renderStill({
          composition,
          serveUrl: bundled,
          frame: clampedFrame,
          output: pctPath,
          inputProps: { manifest, sceneDurations },
        });

        if (pct === primaryPercent) {
          const primaryPath = resolve(previewDir, `${topic}_scene_${i + 1}.png`);
          await renderStill({
            composition,
            serveUrl: bundled,
            frame: clampedFrame,
            output: primaryPath,
            inputProps: { manifest, sceneDurations },
          });
        }
      }

      frameOffset += sceneFrames;
    }

    console.log(`\n  All ${manifest.scenes.length} previews → ${previewDir}/`);
  }
}

main().catch((err) => {
  console.error('Preview failed:', err);
  process.exit(1);
});
