// Renders canonical reference PNGs for the artist by reading the live
// sprite-draw functions out of the main HTML file, evaluating them in
// a fake canvas context, and writing the resulting pixel data to PNGs
// in art/. Run with `node bin/render-references.mjs` whenever a sprite's
// in-game source changes and you want the artist reference to match.

import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname } from 'node:path';
import { PNG } from 'pngjs';

const HTML_PATH = 'dlx-garbage-hauler-pixel.html';
const html = readFileSync(HTML_PATH, 'utf8');

// ─── Extract the PXC palette object literal ────────────────────────────
const pxcMatch = html.match(/const PXC = (\{[\s\S]*?\n  \});/);
if (!pxcMatch) throw new Error('PXC palette not found in HTML');
const PXC = eval('(' + pxcMatch[1] + ')');

// ─── Extract a top-level function declaration by name ──────────────────
// Counts braces to find the matching closing brace. Skips comments and
// strings so braces inside them don't confuse depth tracking.
function extractFn(src, name) {
  const startIdx = src.indexOf(`function ${name}(`);
  if (startIdx < 0) throw new Error(`function ${name} not found`);
  let depth = 0, inFn = false, end = -1;
  let i = startIdx;
  while (i < src.length) {
    const c = src[i], n = src[i + 1];
    if (c === '/' && n === '/') {
      while (i < src.length && src[i] !== '\n') i++;
      continue;
    }
    if (c === '/' && n === '*') {
      i += 2;
      while (i < src.length - 1 && !(src[i] === '*' && src[i + 1] === '/')) i++;
      i += 2;
      continue;
    }
    if (c === '\'' || c === '"' || c === '`') {
      const q = c;
      i++;
      while (i < src.length && src[i] !== q) {
        if (src[i] === '\\') i++;
        i++;
      }
      i++;
      continue;
    }
    if (c === '{') { depth++; inFn = true; }
    else if (c === '}') {
      depth--;
      if (inFn && depth === 0) { end = i + 1; break; }
    }
    i++;
  }
  if (end < 0) throw new Error(`couldn't find end of ${name}`);
  return src.slice(startIdx, end);
}

const pxRoadkillRigSrc            = extractFn(html, 'pxRoadkillRig');
const drawPixelDailyThiefSrc      = extractFn(html, 'drawPixelDailyThief');
const drawPixelDailyThiefAltSrc   = extractFn(html, 'drawPixelDailyThiefAlt');
const drawPixelDailyThiefHarpoonerSrc = extractFn(html, 'drawPixelDailyThiefHarpooner');

// ─── FakeCanvas + 2D context just enough for sprite-draw functions ─────
function parseColor(s) {
  s = s.trim();
  if (s[0] === '#') {
    const hex = s.slice(1);
    if (hex.length === 3) return [
      parseInt(hex[0] + hex[0], 16),
      parseInt(hex[1] + hex[1], 16),
      parseInt(hex[2] + hex[2], 16),
      255,
    ];
    if (hex.length === 6) return [
      parseInt(hex.slice(0, 2), 16),
      parseInt(hex.slice(2, 4), 16),
      parseInt(hex.slice(4, 6), 16),
      255,
    ];
    if (hex.length === 8) return [
      parseInt(hex.slice(0, 2), 16),
      parseInt(hex.slice(2, 4), 16),
      parseInt(hex.slice(4, 6), 16),
      parseInt(hex.slice(6, 8), 16),
    ];
  }
  const m = s.match(/rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+))?\s*\)/);
  if (m) {
    return [
      parseInt(m[1]),
      parseInt(m[2]),
      parseInt(m[3]),
      Math.round((m[4] != null ? parseFloat(m[4]) : 1) * 255),
    ];
  }
  return [0, 0, 0, 255];
}

class FakeCtx {
  constructor(width, height) {
    this.width = width;
    this.height = height;
    this.data = Buffer.alloc(width * height * 4, 0);
    this.transform = { tx: 0, ty: 0, sx: 1, sy: 1 };
    this.stack = [];
    this.imageSmoothingEnabled = true;
    this._fillStyle = '#000000';
  }
  get fillStyle() { return this._fillStyle; }
  set fillStyle(v) { this._fillStyle = v; }
  save() { this.stack.push({ ...this.transform }); }
  restore() { if (this.stack.length) this.transform = this.stack.pop(); }
  translate(x, y) {
    this.transform.tx += x * this.transform.sx;
    this.transform.ty += y * this.transform.sy;
  }
  scale(x, y) {
    this.transform.sx *= x;
    this.transform.sy *= y;
  }
  fillRect(x, y, w, h) {
    const wx = this.transform.tx + x * this.transform.sx;
    const wy = this.transform.ty + y * this.transform.sy;
    const ww = w * this.transform.sx;
    const wh = h * this.transform.sy;
    const [r, g, b, a] = parseColor(this._fillStyle);
    const x0 = Math.max(0, Math.floor(wx));
    const y0 = Math.max(0, Math.floor(wy));
    const x1 = Math.min(this.width, Math.ceil(wx + ww));
    const y1 = Math.min(this.height, Math.ceil(wy + wh));
    for (let py = y0; py < y1; py++) {
      for (let px = x0; px < x1; px++) {
        const idx = (py * this.width + px) * 4;
        if (a === 255) {
          this.data[idx]     = r;
          this.data[idx + 1] = g;
          this.data[idx + 2] = b;
          this.data[idx + 3] = 255;
        } else if (a > 0) {
          const sA = a / 255;
          const dA = this.data[idx + 3] / 255;
          const oA = sA + dA * (1 - sA);
          if (oA > 0) {
            this.data[idx]     = Math.round((r * sA + this.data[idx]     * dA * (1 - sA)) / oA);
            this.data[idx + 1] = Math.round((g * sA + this.data[idx + 1] * dA * (1 - sA)) / oA);
            this.data[idx + 2] = Math.round((b * sA + this.data[idx + 2] * dA * (1 - sA)) / oA);
            this.data[idx + 3] = Math.round(oA * 255);
          }
        }
      }
    }
  }
}

// ─── Build the sprite-draw functions from the extracted source ─────────
// Each factory takes PXC via closure; the resulting function looks up
// `ctx` and `frame` from globalThis (non-strict scope inside new Function).
const buildFn = (name, src) => new Function('PXC', `${src}\nreturn ${name};`)(PXC);

const pxRoadkillRig                 = buildFn('pxRoadkillRig',                 pxRoadkillRigSrc);
const drawPixelDailyThief           = buildFn('drawPixelDailyThief',           drawPixelDailyThiefSrc);
const drawPixelDailyThiefAlt        = buildFn('drawPixelDailyThiefAlt',        drawPixelDailyThiefAltSrc);
const drawPixelDailyThiefHarpooner  = buildFn('drawPixelDailyThiefHarpooner',  drawPixelDailyThiefHarpoonerSrc);

// ─── Save a FakeCtx as a PNG ───────────────────────────────────────────
function savePng(fctx, path) {
  const png = new PNG({ width: fctx.width, height: fctx.height });
  png.data = fctx.data;
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, PNG.sync.write(png));
  console.log(`✓ ${path}  (${fctx.width}×${fctx.height})`);
}

globalThis.frame = 0;   // frame=0 → hover offset = 0 = stable static pose

// ─── HERO RIG · ROAD KILL (clean) ───────────────────────────────────────
{
  const fctx = new FakeCtx(58, 52);
  pxRoadkillRig(fctx, 0, 0, globalThis.frame, false);
  savePng(fctx, 'art/vehicles/hero/roadkill/reference.png');
}

// ─── HERO RIG · ROAD KILL (smashed B-alt) ──────────────────────────────
{
  const fctx = new FakeCtx(58, 52);
  pxRoadkillRig(fctx, 0, 0, globalThis.frame, true);
  savePng(fctx, 'art/vehicles/hero/roadkill/reference_smashed.png');
}

// ─── AERIAL THIEF · DLX gunship (variant 0 — swept-nose / cable + claw) ──
// drawPixelDailyThief() reads `ctx` + `frame` from globalThis. Applies
// ctx.translate(tf.x, tf.y) + ctx.scale(2, 2) + ctx.translate(-26, -23):
//   world_x = tf.x + (mockup_x - 26) * 2
//   world_y = tf.y + (mockup_y - 23) * 2
// Mockup extents: x = -1..46 (94 px world), y = 11..31 (40 px world).
// Canvas 100 × 44 with tf.x=56, tf.y=26 leaves a 2-px border.
{
  const fctx = new FakeCtx(100, 44);
  globalThis.ctx = fctx;
  drawPixelDailyThief({
    x: 56, y: 26, vx: -1, vy: 0, cableLen: 0,
    state: 'cruise', stateFrames: 0, variant: 0,
  });
  savePng(fctx, 'art/vehicles/enemy/gunship/reference.png');
}

// ─── AERIAL THIEF · variant 1 (blunt-front gunship) ────────────────────
// Same translate offset (-26, -23) as variant 0 but a longer / blockier
// silhouette: extents x = 0..62 (124 px world), y = 9..32 (46 px world).
// Canvas 132 × 56 with tf.x=58, tf.y=34 leaves a 4-px border all around.
{
  const fctx = new FakeCtx(132, 56);
  globalThis.ctx = fctx;
  drawPixelDailyThiefAlt({
    x: 58, y: 34, vx: -1, vy: 0, cableLen: 0,
    state: 'cruise', stateFrames: 0, variant: 1,
  });
  savePng(fctx, 'art/vehicles/enemy/gunship_alt/reference.png');
}

// ─── AERIAL THIEF · variant 2 (harpooner — upward harpoon launcher) ────
// Different translate offset (-28, -35), with a launcher mast that
// extends UPWARD above the hull.
//   world_x = tf.x + (mockup_x - 28) * 2
//   world_y = tf.y + (mockup_y - 35) * 2
// Mockup extents: x = 4..55 (102 px world), y = 16..42 (52 px world).
// Canvas 110 × 60 with tf.x=52, tf.y=42 leaves a 4-px border all around.
{
  const fctx = new FakeCtx(110, 60);
  globalThis.ctx = fctx;
  drawPixelDailyThiefHarpooner({
    x: 52, y: 42, vx: -1, vy: 0, cableLen: 0,
    state: 'cruise', stateFrames: 0, variant: 2,
  });
  savePng(fctx, 'art/vehicles/enemy/harpooner/reference.png');
}
