/**
 * Build the standalone Remotion player bundle for embedding in the workbench.
 * Uses esbuild (available as a transitive dep of @remotion/bundler).
 *
 * Output: /opt/tkk/clips/static/remotion-player/player.js
 */
import { build } from 'esbuild';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const outdir = resolve('/opt/tkk/clips/static/remotion-player');

await build({
  entryPoints: [resolve(__dirname, 'src/player-entry.tsx')],
  bundle: true,
  outfile: resolve(outdir, 'player.js'),
  format: 'esm',
  platform: 'browser',
  target: 'es2020',
  jsx: 'automatic',
  jsxImportSource: 'react',
  define: {
    'process.env.NODE_ENV': '"production"',
  },
  // Remotion internals reference some node builtins — stub them out
  alias: {
    // OffthreadVideo uses this in render mode only; player doesn't need it
    'node:crypto': resolve(__dirname, 'src/stubs/empty.ts'),
  },
  logLevel: 'info',
  minify: true,
});

console.log(`Player bundle built → ${outdir}/player.js`);
