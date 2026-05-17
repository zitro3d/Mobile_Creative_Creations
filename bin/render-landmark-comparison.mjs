// Renders BEFORE (smooth-art) and AFTER (pixel-art) PNGs for each of
// the 5 Sunset Wastes roadside landmarks. The BEFORE versions are
// extracted from the v451G snapshot of dlx-garbage-hauler-pixel.html
// (a temp copy at /tmp/before-html.html), the AFTER versions are read
// from the current HEAD. Uses node-canvas so the smooth-art arcs,
// quadraticCurveTo, strokes, and rotated rects all render with their
// original anti-aliasing — exactly what the BEFORE comparison needs.

import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname } from 'node:path';
import { createCanvas } from 'canvas';

const beforeHtml = readFileSync('/tmp/before-html.html', 'utf8');
const afterHtml  = readFileSync('dlx-garbage-hauler-pixel.html', 'utf8');

function extractFn(src, name) {
  const startIdx = src.indexOf(`function ${name}(`);
  if (startIdx < 0) throw new Error(`function ${name} not found`);
  let depth = 0, inFn = false, end = -1, i = startIdx;
  while (i < src.length) {
    const c = src[i], n = src[i + 1];
    if (c === '/' && n === '/') { while (i < src.length && src[i] !== '\n') i++; continue; }
    if (c === '/' && n === '*') { i += 2; while (i < src.length - 1 && !(src[i] === '*' && src[i + 1] === '/')) i++; i += 2; continue; }
    if (c === '\'' || c === '"' || c === '`') {
      const q = c; i++;
      while (i < src.length && src[i] !== q) { if (src[i] === '\\') i++; i++; }
      i++; continue;
    }
    if (c === '{') { depth++; inFn = true; }
    else if (c === '}') { depth--; if (inFn && depth === 0) { end = i + 1; break; } }
    i++;
  }
  if (end < 0) throw new Error(`couldn't find end of ${name}`);
  return src.slice(startIdx, end);
}

// Build a function in a sandbox where `ctx` and `frame` resolve to
// global vars. For dependencies between functions (drawLandmarkSphinx,
// drawLandmarkDriveIn → drawDriveInCar etc.) just pass an array of
// helper source bodies that get defined before the main one.
function buildFromSources(mainName, helperNames, srcDoc) {
  const helpers = helperNames.map(n => extractFn(srcDoc, n)).join('\n');
  const main = extractFn(srcDoc, mainName);
  return new Function(`
    ${helpers}
    ${main}
    return ${mainName};
  `)();
}

function renderToFile(width, height, anchorX, anchorY, drawFn, outPath) {
  const cvs = createCanvas(width, height);
  const cx = cvs.getContext('2d');
  // Transparent background
  cx.clearRect(0, 0, width, height);
  cx.imageSmoothingEnabled = false;
  globalThis.ctx = cx;
  globalThis.frame = 100;
  drawFn(anchorX, anchorY);
  mkdirSync(dirname(outPath), { recursive: true });
  writeFileSync(outPath, cvs.toBuffer('image/png'));
  console.log(`✓ ${outPath}  (${width}×${height})`);
}

// ─── Landmark spec table ───────────────────────────────────────────
// Each landmark renders at anchor (anchorX, anchorY) which is the
// "ground/base point" of the sprite. Canvas width/height + anchor
// chosen so the sprite fits with margin.
const LANDMARKS = [
  { name: 'fromBurger',     fn: 'drawLandmarkFromBurger', helpers: [],
    w: 56, h: 80, ax: 28, ay: 76 },
  { name: 'arches',         fn: 'drawLandmarkArches',     helpers: [],
    w: 88, h: 56, ax: 44, ay: 52 },
  { name: 'drive_in',       fn: 'drawLandmarkDriveIn',    helpers: ['drawDriveInCar'],
    w: 76, h: 64, ax: 38, ay: 60 },
  { name: 'sphinx',         fn: 'drawLandmarkSphinx',     helpers: [],
    w: 100, h: 76, ax: 50, ay: 72 },
  { name: 'office',         fn: 'drawLandmarkOffice',     helpers: [],
    w: 96, h: 128, ax: 56, ay: 124 },
];

for (const lm of LANDMARKS) {
  const before = buildFromSources(lm.fn, lm.helpers, beforeHtml);
  const after  = buildFromSources(lm.fn, lm.helpers, afterHtml);
  renderToFile(lm.w, lm.h, lm.ax, lm.ay, before, `assets/refs/landmarks/${lm.name}_before.png`);
  renderToFile(lm.w, lm.h, lm.ax, lm.ay, after,  `assets/refs/landmarks/${lm.name}_after.png`);
}
