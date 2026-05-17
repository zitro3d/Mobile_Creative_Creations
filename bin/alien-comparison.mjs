// Render side-by-side comparison of the alien greeter rendered two ways:
//   LEFT  = direct draw-instruction style (~150 px() calls, animated)
//   RIGHT = 2D matrix/palette style (single static string array)
// Outputs an animated GIF.
import { createCanvas } from 'canvas';
import gifenc from 'gifenc';
const { GIFEncoder, quantize, applyPalette } = gifenc;
import { readFileSync, writeFileSync } from 'node:fs';

const html = readFileSync('mockup-sunset-wastes-v7.html', 'utf8');

// ── Extract helper functions from the mockup ────────────────
function extractFn(src, name) {
  const startIdx = src.indexOf('function ' + name + '(');
  if (startIdx < 0) throw new Error('fn not found: ' + name);
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
  return src.slice(startIdx, end);
}

const Cdef = html.match(/const C = \{[\s\S]*?\};/)[0];
const pxFn = extractFn(html, 'px');

// ── Pull the alien-rendering block out of drawDock ──────────
// It runs from "// ── 6-ARMED ALIEN GREETER" until the close of drawDock.
const drawDockSrc = extractFn(html, 'drawDock');
const alienStartMarker = '// ── 6-ARMED ALIEN GREETER';
const alienStart = drawDockSrc.indexOf(alienStartMarker);
// The alien block runs to the end of drawDock; trim the closing brace.
let alienBlockSrc = drawDockSrc.slice(alienStart, drawDockSrc.lastIndexOf('}'));
// Strip the embedded `const ax = ..., ay = ...;` line because ax/ay
// are passed as function parameters now.
alienBlockSrc = alienBlockSrc.replace(/const\s+ax\s*=[^;]+;/, '');

// drawString/drawLetter5x7 + G glyph map also live INSIDE drawDock — extract.
const Gmatch = drawDockSrc.match(/const G = \{[\s\S]*?\};/);
const drawLetterMatch = drawDockSrc.match(/const drawLetter5x7 = [\s\S]*?\};/);
const drawStringMatch = drawDockSrc.match(/const drawString = [\s\S]*?\};/);

// Compose a standalone alien renderer.
const drawAlienSrc = `
${Cdef}
${pxFn}
function drawAlien(ctx, ax, ay, t) {
  // Locals usually computed at top of drawDock
  const blink = ((t / 6) | 0) & 1;
  ${Gmatch[0]}
  ${drawLetterMatch[0]}
  ${drawStringMatch[0]}
  ${alienBlockSrc}
}
return drawAlien;
`;
const drawAlien = new Function(drawAlienSrc)();

// ── Build the matrix by rendering the alien once + reading pixels ──
const MAT_W = 36, MAT_H = 56;            // bounding box big enough for waving arms
const MAT_AX = 18, MAT_AY = 28;          // alien position inside the matrix canvas

const matrixCvs = createCanvas(MAT_W, MAT_H);
const matrixCtx = matrixCvs.getContext('2d');
matrixCtx.imageSmoothingEnabled = false;
matrixCtx.clearRect(0, 0, MAT_W, MAT_H);
drawAlien(matrixCtx, MAT_AX, MAT_AY, 0);  // freeze pose at t=0
const matrixImg = matrixCtx.getImageData(0, 0, MAT_W, MAT_H);

// Build palette + char map.
const colorToChar = new Map();
const charToColor = new Map();
const chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&*+';
let nextCharIdx = 0;
const matrix = [];
for (let y = 0; y < MAT_H; y++) {
  let row = '';
  for (let x = 0; x < MAT_W; x++) {
    const idx = (y * MAT_W + x) * 4;
    const r = matrixImg.data[idx], g = matrixImg.data[idx + 1], b = matrixImg.data[idx + 2], a = matrixImg.data[idx + 3];
    if (a < 128) { row += '.'; continue; }
    const key = `${r},${g},${b}`;
    if (!colorToChar.has(key)) {
      const ch = chars[nextCharIdx++];
      colorToChar.set(key, ch);
      charToColor.set(ch, `rgb(${r},${g},${b})`);
    }
    row += colorToChar.get(key);
  }
  matrix.push(row);
}
console.log(`Matrix built: ${MAT_W}×${MAT_H}, ${charToColor.size} colors, ${matrix.length} rows`);

// ── Render the matrix back to a canvas (for the right-hand side) ─
function renderMatrix(ctx, ox, oy) {
  for (let y = 0; y < matrix.length; y++) {
    const row = matrix[y];
    for (let x = 0; x < row.length; x++) {
      const ch = row[x];
      const col = charToColor.get(ch);
      if (col) {
        ctx.fillStyle = col;
        ctx.fillRect(ox + x, oy + y, 1, 1);
      }
    }
  }
}

// ── Compose side-by-side frames ──────────────────────────────
const FRAME_W = 160, FRAME_H = 90;
const CELL_W = FRAME_W / 2;
const LEFT_AX = 36, LEFT_AY = 36;
const RIGHT_OX = FRAME_W / 2 + ((CELL_W - MAT_W) >> 1);
const RIGHT_OY = ((FRAME_H - MAT_H) >> 1) + 4;

function drawFrame(t) {
  const cvs = createCanvas(FRAME_W, FRAME_H);
  const ctx = cvs.getContext('2d');
  ctx.imageSmoothingEnabled = false;

  // Background — flat dark
  ctx.fillStyle = '#1a1a1c';
  ctx.fillRect(0, 0, FRAME_W, FRAME_H);
  // Divider
  ctx.fillStyle = '#3a3a40';
  ctx.fillRect(FRAME_W / 2 - 1, 0, 1, FRAME_H);

  // LEFT — animated draw-instruction alien
  drawAlien(ctx, LEFT_AX, LEFT_AY, t);

  // RIGHT — matrix-rendered alien (static)
  renderMatrix(ctx, RIGHT_OX, RIGHT_OY);

  // Labels (1-px font from drawDock scope — re-use drawAlien's G)
  // Skip labels in the GIF — they'd need yet another extraction.
  // Instead add small color-coded marker bars at the top.
  ctx.fillStyle = '#3aa8b8';  // teal bar = animated draw-instructions
  ctx.fillRect(2, 2, CELL_W - 4, 2);
  ctx.fillStyle = '#c8a060';  // tan bar = static matrix
  ctx.fillRect(FRAME_W / 2 + 2, 2, CELL_W - 4, 2);

  return cvs;
}

// ── Encode the frames as a GIF ───────────────────────────────
const gif = GIFEncoder();
const FRAME_COUNT = 36;
const FRAME_DELAY_MS = 70;

for (let i = 0; i < FRAME_COUNT; i++) {
  const cvs = drawFrame(i);
  const ctx = cvs.getContext('2d');
  const img = ctx.getImageData(0, 0, FRAME_W, FRAME_H);
  const palette = quantize(img.data, 256);
  const indexed = applyPalette(img.data, palette);
  gif.writeFrame(indexed, FRAME_W, FRAME_H, { palette, delay: FRAME_DELAY_MS });
}
gif.finish();
writeFileSync('/tmp/alien-comparison.gif', gif.bytes());
console.log('Wrote /tmp/alien-comparison.gif');

// Also dump the matrix + palette as a JS module — the actual "code"
// the matrix-style version would ship. Lets you see how compact the
// data is compared to ~150 px() calls in the draw-instruction version.
const paletteEntries = [...charToColor.entries()]
  .map(([ch, col]) => `  '${ch}': '${col}'`).join(',\n');
const matrixDump = `// Auto-generated alien sprite — 2D matrix + palette.
// Same character as the draw-instruction version, frozen at t=0.
// To render: for each (y, x), look up palette[matrix[y][x]] and draw a 1×1 pixel.

export const ALIEN_PALETTE = {
${paletteEntries}
};

export const ALIEN_MATRIX = [
${matrix.map(r => `  '${r}',`).join('\n')}
];
`;
writeFileSync('/tmp/alien-matrix.js', matrixDump);
console.log('Wrote /tmp/alien-matrix.js (' + matrixDump.length + ' bytes)');
