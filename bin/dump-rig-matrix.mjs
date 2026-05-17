// Dump the ROAD KILL RIG (pxRoadkillRig) as a matrix + palette JS module.
import { createCanvas } from 'canvas';
import { readFileSync, writeFileSync } from 'node:fs';

const html = readFileSync('mockup-sunset-wastes-v7.html', 'utf8');

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

const PXCdef = html.match(/const PXC = \{[\s\S]*?\};/)[0];
const rigFn = extractFn(html, 'pxRoadkillRig');

const drawRig = new Function(`
  ${PXCdef}
  ${rigFn}
  return pxRoadkillRig;
`)();

// Rig native size 58×52. Add a small margin.
const W = 62, H = 56;
const cvs = createCanvas(W, H);
const ctx = cvs.getContext('2d');
ctx.imageSmoothingEnabled = false;
ctx.clearRect(0, 0, W, H);
drawRig(ctx, 2, 2, 0);  // top-left padded by 2

const img = ctx.getImageData(0, 0, W, H);

// Build palette + char map (with anti-aliased pixels quantized down).
const colorToChar = new Map();
const charToColor = new Map();
const chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&*+=:;<>?@';
let nextCharIdx = 0;
const matrix = [];
for (let y = 0; y < H; y++) {
  let row = '';
  for (let x = 0; x < W; x++) {
    const idx = (y * W + x) * 4;
    const r = img.data[idx], g = img.data[idx + 1], b = img.data[idx + 2], a = img.data[idx + 3];
    if (a < 128) { row += '.'; continue; }
    // Composite semi-transparent pixels over black backdrop
    const af = a / 255;
    const cr = Math.round(r * af), cg = Math.round(g * af), cb = Math.round(b * af);
    const key = `${cr},${cg},${cb}`;
    if (!colorToChar.has(key)) {
      if (nextCharIdx >= chars.length) {
        throw new Error('Out of palette characters: ' + (charToColor.size + 1));
      }
      const ch = chars[nextCharIdx++];
      colorToChar.set(key, ch);
      charToColor.set(ch, `rgb(${cr},${cg},${cb})`);
    }
    row += colorToChar.get(key);
  }
  matrix.push(row);
}

// Trim columns that are entirely transparent for tighter output.
function trimMatrix(mat) {
  let lt = Infinity, rt = -Infinity, tp = Infinity, bt = -Infinity;
  for (let y = 0; y < mat.length; y++) {
    for (let x = 0; x < mat[y].length; x++) {
      if (mat[y][x] !== '.') {
        if (x < lt) lt = x;
        if (x > rt) rt = x;
        if (y < tp) tp = y;
        if (y > bt) bt = y;
      }
    }
  }
  if (lt === Infinity) return mat;
  return mat.slice(tp, bt + 1).map(r => r.slice(lt, rt + 1));
}
const trimmed = trimMatrix(matrix);

const paletteEntries = [...charToColor.entries()]
  .map(([ch, col]) => `  '${ch}': '${col}'`).join(',\n');

const dump = `// Auto-generated ROAD KILL RIG sprite — 2D matrix + palette.
// Native sprite size: ${trimmed[0].length} × ${trimmed.length} (trimmed).
// Faces RIGHT (positive X). Drawn at antenna idle pose (frame 0).
// To render: for each (y, x), look up palette[matrix[y][x]] and
// drawFillRect(ox + x, oy + y, 1, 1). '.' = transparent (skip).

export const ROADKILL_PALETTE = {
${paletteEntries}
};

export const ROADKILL_MATRIX = [
${trimmed.map(r => `  '${r}',`).join('\n')}
];
`;

writeFileSync('/tmp/rig-matrix.js', dump);
console.log('Wrote /tmp/rig-matrix.js (' + dump.length + ' bytes)');
console.log('Matrix: ' + trimmed[0].length + ' × ' + trimmed.length + ', ' + charToColor.size + ' colors');
