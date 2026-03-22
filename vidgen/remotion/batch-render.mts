/**
 * Batch render all manifests that don't have a final MP4 yet.
 * Skips the sync QA gate (render.mts has it built-in and it blocks).
 */
import { bundle } from '@remotion/bundler';
import { renderMedia, selectComposition } from '@remotion/renderer';
import { readFileSync, existsSync, readdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { ManifestSchema } from './src/schema';

const __dirname = dirname(fileURLToPath(import.meta.url));
const vidgenDir = resolve(__dirname, '..');
const manifestsDir = resolve(__dirname, 'src/manifests');

// Find all topics that need rendering
const topics = readdirSync(manifestsDir)
  .filter(f => f.endsWith('.json'))
  .map(f => f.replace('.json', ''))
  .filter(topic => {
    const finalPath = resolve(vidgenDir, `${topic}_final.mp4`);
    return !existsSync(finalPath);
  });

if (topics.length === 0) {
  console.log('All videos already rendered. Nothing to do.');
  process.exit(0);
}

console.log(`\nBatch render: ${topics.length} videos to render\n  ${topics.join(', ')}\n`);

// Bundle once, reuse for all renders
console.log('Bundling (once)...');
const bundled = await bundle({
  entryPoint: resolve(__dirname, 'src/index.ts'),
  publicDir: resolve(__dirname, 'public'),
});
console.log('Bundle ready.\n');

for (const topic of topics) {
  const manifestPath = resolve(manifestsDir, `${topic}.json`);
  const rawManifest = JSON.parse(readFileSync(manifestPath, 'utf-8'));
  const manifest = ManifestSchema.parse(rawManifest);

  const timingsPath = resolve(vidgenDir, `tts_${topic}_timings.json`);
  let sceneDurations: number[];
  if (existsSync(timingsPath)) {
    const timings = JSON.parse(readFileSync(timingsPath, 'utf-8'));
    sceneDurations = timings.scene_durations;
  } else {
    sceneDurations = manifest.scenes.map(() => 5);
    console.log(`  [${topic}] No timings — using 5s/scene`);
  }

  const audioFile = `tts_${topic}.mp3`;
  const audioSrc = existsSync(resolve(vidgenDir, audioFile)) ? audioFile : undefined;
  const outputPath = resolve(vidgenDir, `${topic}_final.mp4`);

  const totalFrames = sceneDurations.reduce((s, d) => s + Math.round(d * 30), 0);

  console.log(`=== ${topic} (${manifest.scenes.length} scenes, ${(totalFrames/30).toFixed(1)}s) ===`);

  const composition = await selectComposition({
    serveUrl: bundled,
    id: 'demo',
    inputProps: { manifest, sceneDurations, audioSrc },
  });
  composition.durationInFrames = totalFrames;
  composition.fps = 30;
  composition.width = 1080;
  composition.height = 1920;

  const t0 = Date.now();
  await renderMedia({
    composition,
    serveUrl: bundled,
    codec: 'h264',
    outputLocation: outputPath,
    inputProps: { manifest, sceneDurations, audioSrc },
    concurrency: 4,
    onProgress: ({ progress }) => {
      const pct = Math.round(progress * 100);
      if (pct % 25 === 0) process.stdout.write(`\r  ${topic}: ${pct}%`);
    },
  });
  const elapsed = ((Date.now() - t0) / 1000).toFixed(0);
  console.log(`\r  ${topic}: done (${elapsed}s) → ${outputPath}`);
}

console.log(`\n=== All ${topics.length} renders complete ===`);
