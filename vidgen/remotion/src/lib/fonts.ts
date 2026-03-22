/**
 * TKK font registration — loads local .ttf files from public/fonts/.
 *
 * In Remotion, fonts are loaded via staticFile() and CSS @font-face.
 */
import { staticFile } from './static';

export const FONTS = {
  headline: 'Bebas Neue',
  body: 'Inter',
  serif: 'DM Serif Display',
  mono: 'Space Mono',
} as const;

/** CSS @font-face declarations. Inject into your Root component or global styles. */
export const fontFaces = `
  @font-face {
    font-family: 'Bebas Neue';
    src: url('${staticFile('fonts/BebasNeue-Regular.ttf')}') format('truetype');
    font-weight: normal;
  }
  @font-face {
    font-family: 'Inter';
    src: url('${staticFile('fonts/Inter-Regular.ttf')}') format('truetype');
    font-weight: normal;
  }
  @font-face {
    font-family: 'Inter';
    src: url('${staticFile('fonts/Inter-Bold.ttf')}') format('truetype');
    font-weight: bold;
  }
  @font-face {
    font-family: 'DM Serif Display';
    src: url('${staticFile('fonts/DMSerifDisplay-Regular.ttf')}') format('truetype');
    font-weight: normal;
  }
  @font-face {
    font-family: 'DM Serif Display';
    src: url('${staticFile('fonts/DMSerifDisplay-Italic.ttf')}') format('truetype');
    font-weight: normal;
    font-style: italic;
  }
  @font-face {
    font-family: 'Space Mono';
    src: url('${staticFile('fonts/SpaceMono-Regular.ttf')}') format('truetype');
    font-weight: normal;
  }
  @font-face {
    font-family: 'Space Mono';
    src: url('${staticFile('fonts/SpaceMono-Bold.ttf')}') format('truetype');
    font-weight: bold;
  }
`;
