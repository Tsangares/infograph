/**
 * Render CLI for word-triggered TKK videos.
 *
 * Usage: npx tsx render_word_triggered.mts <topic>
 *
 * Reads a pre-resolved manifest from the prototype directory
 * and renders using the word-triggered Remotion composition.
 */
import { bundle } from '@remotion/bundler';
import { renderMedia, selectComposition } from '@remotion/renderer';
import { readFileSync, existsSync } from 'fs';
import { execSync } from 'child_process';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const protoDir = resolve('/home/wil/.openclaw/workspace-ape/tkk-prototype');

const topic = process.argv[2];
if (!topic) {
  console.error('Usage: npx tsx render_word_triggered.mts <topic>');
  process.exit(1);
}

// Step 1: Resolve word triggers
console.log(`\n  Step 1: Resolving word triggers for '${topic}'...`);
const resolverScript = resolve(protoDir, 'resolve_word_triggers.py');
try {
  const result = execSync(`python3 ${resolverScript} ${topic}`, {
    cwd: protoDir,
    encoding: 'utf-8',
    timeout: 30000,
  });
  // Print just the summary lines
  for (const line of result.split('\n')) {
    if (line.trim()) console.log(`  ${line.trim()}`);
  }
} catch (err: any) {
  console.error('Failed to resolve word triggers:', err.stderr || err.message);
  process.exit(1);
}

// Step 2: Load resolved manifest
const resolvedPath = resolve(protoDir, `${topic}_resolved.json`);
if (!existsSync(resolvedPath)) {
  console.error(`Resolved manifest not found: ${resolvedPath}`);
  process.exit(1);
}

const manifest = JSON.parse(readFileSync(resolvedPath, 'utf-8'));
console.log(`\n  Resolved: ${manifest.scenes.length} scenes, ${manifest.total_frames} frames (${manifest.total_duration_s}s)`);

// Check for audio
const audioFile = `tts_${topic}.mp3`;
const audioPath = resolve(__dirname, audioFile);
const audioSrc = existsSync(audioPath) ? audioFile : undefined;
console.log(audioSrc ? `  Audio: ${audioFile}` : '  No audio — rendering silent');

const outputPath = resolve(__dirname, `${topic}_word_triggered.mp4`);

async function main() {
  const remotionDir = resolve(__dirname, 'remotion');
  console.log('\n  Step 2: Bundling...');
  const bundled = await bundle({
    entryPoint: resolve(remotionDir, 'src/index.ts'),
    publicDir: resolve(remotionDir, 'public'),
  });

  console.log(`  Selecting composition (${manifest.total_frames} frames)...`);
  const composition = await selectComposition({
    serveUrl: bundled,
    id: 'word-triggered',
    inputProps: { manifest, audioSrc },
  });

  composition.durationInFrames = manifest.total_frames;
  composition.fps = manifest.fps;
  composition.width = 1080;
  composition.height = 1920;

  console.log(`  Rendering ${manifest.total_frames} frames (${manifest.total_duration_s}s)...`);
  await renderMedia({
    composition,
    serveUrl: bundled,
    codec: 'h264',
    outputLocation: outputPath,
    inputProps: { manifest, audioSrc },
    concurrency: 4,
    onProgress: ({ progress }) => {
      if (Math.round(progress * 100) % 10 === 0) {
        process.stdout.write(`\r  Progress: ${Math.round(progress * 100)}%`);
      }
    },
  });

  console.log(`\n\n  Done: ${outputPath}`);
}

main().catch((err) => {
  console.error('Render failed:', err);
  process.exit(1);
});
