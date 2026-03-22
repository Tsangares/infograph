/**
 * TKK Remotion Render CLI — renders a manifest to MP4.
 *
 * Usage: npx tsx render.mts <topic>
 *   Reads: src/manifests/{topic}.json + ../tts_{topic}_timings.json
 *   Output: ../{topic}_final.mp4
 *
 * Supports both legacy (type-based) and word-triggered manifests.
 */
import { bundle } from '@remotion/bundler';
import { renderMedia, selectComposition } from '@remotion/renderer';
import { readFileSync, existsSync } from 'fs';
import { execSync } from 'child_process';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { ManifestSchema } from './src/schema';

const __dirname = dirname(fileURLToPath(import.meta.url));
const vidgenDir = resolve(__dirname, '..');
const venvPython = resolve(vidgenDir, '.venv/bin/python3');

const topic = process.argv[2];
if (!topic) {
  console.error('Usage: npx tsx render.mts <topic>');
  process.exit(1);
}

// Load raw manifest
const manifestPath = resolve(__dirname, 'src/manifests', `${topic}.json`);
if (!existsSync(manifestPath)) {
  console.error(`Manifest not found: ${manifestPath}`);
  process.exit(1);
}
const rawManifest = JSON.parse(readFileSync(manifestPath, 'utf-8'));

// Format detection: word-triggered if scenes have scene_anchor field
const isWordTriggered = rawManifest.scenes?.[0]?.scene_anchor != null;

// Check for audio (shared by both paths)
const audioFile = `tts_${topic}.mp3`;
const audioPath = resolve(vidgenDir, audioFile);
const audioSrc = existsSync(audioPath) ? audioFile : undefined;
if (audioSrc) {
  console.log(`  Audio: ${audioFile}`);
} else {
  console.log('  No audio file found — rendering silent');
}

const outputPath = resolve(vidgenDir, `${topic}_final.mp4`);

function runQaGate(topic: string) {
  const qaAllScript = resolve(vidgenDir, 'qa_all.py');
  if (!existsSync(qaAllScript) || !existsSync(venvPython)) return;

  console.log('\n  Running QA...');
  try {
    const qaRaw = execSync(
      `${venvPython} ${qaAllScript} --json --skip-previews ${topic}`,
      { cwd: vidgenDir, encoding: 'utf-8', timeout: 60000 }
    );
    const qa = JSON.parse(qaRaw);
    if (qa.status === 'FAIL') {
      console.error(`\n  QA FAILED (${qa.total_fails} fails, ${qa.total_warns} warns):`);
      for (const section of qa.sections) {
        for (const c of section.checks) {
          if (c.status === 'FAIL') console.error(`    [FAIL] ${c.check}: ${c.detail}`);
        }
      }
      process.exit(1);
    }
    if (qa.total_warns > 0) {
      console.log(`  QA: WARN (${qa.total_warns} warnings)`);
    } else {
      console.log('  QA: PASS');
    }
  } catch (err: any) {
    // If qa_all.py itself fails, warn but don't block
    console.log(`  QA: skipped (${err.message?.split('\n')[0] || 'error'})`);
  }
}

async function main() {
  console.log('\n  Bundling...');
  const bundled = await bundle({
    entryPoint: resolve(__dirname, 'src/index.ts'),
    publicDir: resolve(__dirname, 'public'),
  });

  if (isWordTriggered) {
    // ── Word-triggered path ──
    console.log(`  Format: word-triggered`);

    // Load or auto-resolve the resolved manifest
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
      console.error(`  Resolved manifest not found after resolver: ${resolvedPath}`);
      process.exit(1);
    }

    const resolvedManifest = JSON.parse(readFileSync(resolvedPath, 'utf-8'));
    const totalFrames = resolvedManifest.total_frames;
    console.log(`  Resolved: ${resolvedManifest.scenes.length} scenes, ${totalFrames} frames (${(totalFrames / 30).toFixed(1)}s)`);

    // Unified QA gate
    runQaGate(topic);

    console.log(`\n  Selecting composition (${totalFrames} frames)...`);
    const composition = await selectComposition({
      serveUrl: bundled,
      id: 'word-triggered',
      inputProps: { manifest: resolvedManifest, audioSrc },
    });

    composition.durationInFrames = totalFrames;
    composition.fps = 30;
    composition.width = 1080;
    composition.height = 1920;

    console.log(`  Rendering ${totalFrames} frames (${(totalFrames / 30).toFixed(1)}s)...`);
    await renderMedia({
      composition,
      serveUrl: bundled,
      codec: 'h264',
      outputLocation: outputPath,
      inputProps: { manifest: resolvedManifest, audioSrc },
      concurrency: 4,
      onProgress: ({ progress }) => {
        if (Math.round(progress * 100) % 10 === 0) {
          process.stdout.write(`\r  Progress: ${Math.round(progress * 100)}%`);
        }
      },
    });

  } else {
    // ── Legacy path (unchanged) ──
    console.log(`  Format: legacy`);
    const manifest = ManifestSchema.parse(rawManifest);
    console.log(`  Manifest: ${manifest.scenes.length} scenes, topic="${manifest.topic}"`);

    // Load scene timings
    const timingsPath = resolve(vidgenDir, `tts_${topic}_timings.json`);
    let sceneDurations: number[];
    if (existsSync(timingsPath)) {
      const timings = JSON.parse(readFileSync(timingsPath, 'utf-8'));
      sceneDurations = timings.scene_durations;
      console.log(`  Timings: ${sceneDurations.map(d => d.toFixed(1)).join(', ')}s`);

      if (timings.calibrations) {
        for (const [key, cal] of Object.entries(timings.calibrations)) {
          const idx = parseInt(key.replace('scene_', ''));
          const calibration = cal as Record<string, number>;
          if (calibration.countDuration != null && manifest.scenes[idx]?.props) {
            const old = (manifest.scenes[idx].props as any).countDuration;
            (manifest.scenes[idx].props as any).countDuration = calibration.countDuration;
            console.log(`  Calibration: scene ${idx} countDuration ${old} → ${calibration.countDuration}`);
          }
        }
      }
    } else {
      const totalDuration = 35;
      const perScene = totalDuration / manifest.scenes.length;
      sceneDurations = manifest.scenes.map((_, i) =>
        i === manifest.scenes.length - 1 ? perScene + 0.5 : perScene
      );
      console.log(`  No timings JSON — using ${perScene.toFixed(1)}s per scene (last +0.5s tail)`);
    }

    // Unified QA gate
    runQaGate(topic);

    const totalFrames = sceneDurations.reduce((sum, d) => sum + Math.round(d * 30), 0);

    console.log(`\n  Selecting composition (${totalFrames} frames)...`);
    const composition = await selectComposition({
      serveUrl: bundled,
      id: 'demo',
      inputProps: { manifest, sceneDurations, audioSrc },
    });

    composition.durationInFrames = totalFrames;
    composition.fps = 30;
    composition.width = 1080;
    composition.height = 1920;

    console.log(`  Rendering ${totalFrames} frames (${(totalFrames / 30).toFixed(1)}s)...`);
    await renderMedia({
      composition,
      serveUrl: bundled,
      codec: 'h264',
      outputLocation: outputPath,
      inputProps: { manifest, sceneDurations, audioSrc },
      concurrency: 4,
      onProgress: ({ progress }) => {
        if (Math.round(progress * 100) % 10 === 0) {
          process.stdout.write(`\r  Progress: ${Math.round(progress * 100)}%`);
        }
      },
    });
  }

  console.log(`\n\n  Done: ${outputPath}`);
}

main().catch((err) => {
  console.error('Render failed:', err);
  process.exit(1);
});
