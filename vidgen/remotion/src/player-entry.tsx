import React from 'react';
// @ts-expect-error — react-dom/client types not installed, works at runtime
import { createRoot } from 'react-dom/client';
import { PlayerApp } from './PlayerApp';

const root = createRoot(document.getElementById('root')!);
root.render(<PlayerApp />);
