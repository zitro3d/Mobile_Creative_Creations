// Test render of the ported drawLandmarkTruckStop function.
// Extracts helpers + the function, stubs game globals, renders to PNG.
import { createCanvas } from 'canvas';
import { readFileSync, writeFileSync } from 'node:fs';

const src = readFileSync('dlx-garbage-hauler-pixel.html', 'utf8');

function extractFn(s, name) {
  const start = s.indexOf('function ' + name + '(');
  if (start < 0) throw new Error('fn not found: ' + name);
  let depth = 0, inFn = false, end = -1, i = start;
  while (i < s.length) {
    const c = s[i], n = s[i + 1];
    if (c === '/' && n === '/') { while (i < s.length && s[i] !== '\n') i++; continue; }
    if (c === '/' && n === '*') { i += 2; while (i < s.length - 1 && !(s[i] === '*' && s[i + 1] === '/')) i++; i += 2; continue; }
    if (c === '\'' || c === '"' || c === '`') {
      const q = c; i++;
      while (i < s.length && s[i] !== q) { if (s[i] === '\\') i++; i++; }
      i++; continue;
    }
    if (c === '{') { depth++; inFn = true; }
    else if (c === '}') { depth--; if (inFn && depth === 0) { end = i + 1; break; } }
    i++;
  }
  return s.slice(start, end);
}

function extractConst(s, name) {
  const m = new RegExp('const ' + name + ' = \\{[\\s\\S]*?\\};').exec(s);
  if (!m) throw new Error('const not found: ' + name);
  return m[0];
}

const TSC      = extractConst(src, 'TSC');
const TS_GLYPHS= extractConst(src, 'TS_GLYPHS');
const px       = extractFn(src, 'px');
const pxDisc   = extractFn(src, 'pxDisc');
const pxBlockPuff = extractFn(src, 'pxBlockPuff');
const pxFlame  = extractFn(src, 'pxFlame');
const drawLetter5x7 = extractFn(src, 'drawLetter5x7');
const drawString    = extractFn(src, 'drawString');
const drawTS   = extractFn(src, 'drawLandmarkTruckStop');

// Stubs for game globals the function references
const stubs = `
const PLAY_H = 176;
const currentDeliveryLevel = { obstacleTheme: 'sunset' };
let frame = 30;
let ctx;
`;

const fn = new Function('cx', 'fr', `
  ${stubs}
  ctx = cx;
  frame = fr;
  ${TSC}
  ${TS_GLYPHS}
  ${px}
  ${pxDisc}
  ${pxBlockPuff}
  ${pxFlame}
  ${drawLetter5x7}
  ${drawString}
  ${drawTS}
  // Landmark anchor — center horizontally, plant at standard dock altitude
  drawLandmarkTruckStop(180, PLAY_H / 2 + 28);
`);

const W = 320, H = 200;
const cvs = createCanvas(W, H);
const cx = cvs.getContext('2d');
cx.imageSmoothingEnabled = false;
// Solid sunset-ish background so transparent pixels are visible
cx.fillStyle = '#3a1818';
cx.fillRect(0, 0, W, H);
fn(cx, 30);
writeFileSync('/tmp/truckstop-port-test.png', cvs.toBuffer('image/png'));
console.log('OK');
