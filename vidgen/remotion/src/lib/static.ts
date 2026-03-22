/**
 * staticFile wrapper for dual-mode operation:
 * - Player mode (in-browser via iframe): resolves to /remotion-assets/path
 * - Render mode (Remotion bundler): uses Remotion's native staticFile()
 *
 * Player mode is detected via window.__TKK_PLAYER__ flag set by PlayerApp.
 */
import { staticFile as remotionStaticFile } from 'remotion';

declare global {
  interface Window {
    __TKK_PLAYER__?: boolean;
  }
}

function isPlayerMode(): boolean {
  try {
    return typeof window !== 'undefined' && !!window.__TKK_PLAYER__;
  } catch {
    return false;
  }
}

export function staticFile(path: string): string {
  if (isPlayerMode()) {
    // Strip leading slash if present, then prefix with asset base
    const clean = path.startsWith('/') ? path.slice(1) : path;
    return `/remotion-assets/${clean}`;
  }
  return remotionStaticFile(path);
}
