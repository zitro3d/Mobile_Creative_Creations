// Render preview PNGs of the v2 roaring fire (single hero flame) to /tmp
// so we can eyeball it without launching a browser. Mirrors the draw
// logic from metapixel/index.html — keep in sync.

import { writeFileSync } from 'node:fs';
import { PNG } from 'pngjs';

// ── Software canvas ─────────────────────────────────────────────────
function makeCanvas(W, H) {
  const data = Buffer.alloc(W * H * 4, 0);
  return {
    W, H, data,
    fill(color, x, y, w, h) {
      const [r, g, b, a] = parseColor(color);
      x |= 0; y |= 0; w = (w || 1) | 0; h = (h || 1) | 0;
      for (let yy = y; yy < y + h; yy++) {
        if (yy < 0 || yy >= H) continue;
        for (let xx = x; xx < x + w; xx++) {
          if (xx < 0 || xx >= W) continue;
          const i = (yy * W + xx) * 4;
          data[i] = r; data[i + 1] = g; data[i + 2] = b; data[i + 3] = a;
        }
      }
    },
  };
}
function parseColor(hex) {
  return [parseInt(hex.slice(1, 3), 16), parseInt(hex.slice(3, 5), 16), parseInt(hex.slice(5, 7), 16), 255];
}
function px(cv, color, x, y, w, h) { cv.fill(color, x, y, w, h); }
function upscale(src, factor) {
  const W = src.W * factor, H = src.H * factor;
  const out = makeCanvas(W, H);
  for (let y = 0; y < src.H; y++) {
    for (let x = 0; x < src.W; x++) {
      const i = (y * src.W + x) * 4;
      const r = src.data[i], g = src.data[i+1], b = src.data[i+2], a = src.data[i+3];
      for (let dy = 0; dy < factor; dy++) {
        for (let dx = 0; dx < factor; dx++) {
          const j = ((y * factor + dy) * W + (x * factor + dx)) * 4;
          out.data[j] = r; out.data[j+1] = g; out.data[j+2] = b; out.data[j+3] = a;
        }
      }
    }
  }
  return out;
}
function savePng(cv, path) {
  const png = new PNG({ width: cv.W, height: cv.H });
  cv.data.copy(png.data);
  writeFileSync(path, PNG.sync.write(png));
}

// ── Fire logic (mirrors metapixel/index.html) ───────────────────────
const FIRE_FRAMES = 30;
const FIRE_NATIVE = 64;
const FIRE_TAU = (Math.PI * 2) / FIRE_FRAMES;

const FIRE = {
  OUTLINE: '#D95738',
  BODY:    '#F16E32',
  CORE:    '#F7A833',
  HOT:     '#FFF7A4',
};

function leftSCurveX(u, t) {
  const sCurve = Math.sin(u * Math.PI * 2) * 4;
  const hook = u > 0.82 ? Math.sin((u - 0.82) * Math.PI / 0.18) * 2.2 : 0;
  const wobble = Math.sin(t * FIRE_TAU + u * 1.5) * 0.45;
  return sCurve + hook + wobble;
}
function leftSCurveW(u) {
  if (u < 0.15) return 3.0;
  if (u < 0.55) return 3.0 - (u - 0.15) * 1.5;
  if (u < 0.85) return 2.4 - (u - 0.55) * 4.2;
  return Math.max(0.4, 1.14 - (u - 0.85) * 5.5);
}
function rightStepX(u, t) {
  let step;
  if      (u < 0.10) step = u * 25;
  else if (u < 0.40) step = 2.5 + (u - 0.10) * 7;
  else if (u < 0.75) step = 4.6 - (u - 0.40) * 9;
  else                step = 1.45 - (u - 0.75) * 6;
  const wobble = Math.sin(t * FIRE_TAU + u * 1.5 + 1.7) * 0.45;
  return step + wobble;
}
function rightStepW(u) {
  if (u < 0.20) return 3.2;
  if (u < 0.60) return 3.2 - (u - 0.20) * 2.0;
  if (u < 0.88) return 2.4 - (u - 0.60) * 5.2;
  return Math.max(0.4, 0.95 - (u - 0.88) * 5.0);
}
function spireX(u, t, seed) {
  const jitter = Math.sin(u * 8.4 + seed) * 0.55;
  const wobble = Math.sin(t * FIRE_TAU + seed * 2.1) * 0.45;
  return jitter + wobble;
}
function spireW(u) {
  if (u < 0.20) return 2.1;
  if (u < 0.70) return 2.1 - (u - 0.20) * 1.5;
  return Math.max(0.4, 1.35 - (u - 0.70) * 4.5);
}

const TENDRILS = [
  { name: 'left-S',       baseX: 23, baseY: 52, height: 42,
    xOff: leftSCurveX,    width: leftSCurveW, seed: 0 },
  { name: 'right-step',   baseX: 41, baseY: 52, height: 38,
    xOff: rightStepX,     width: rightStepW,  seed: 0 },
  { name: 'center-left',  baseX: 29, baseY: 51, height: 22,
    xOff: spireX,         width: spireW,      seed: 1.9 },
  { name: 'center-right', baseX: 35, baseY: 51, height: 26,
    xOff: spireX,         width: spireW,      seed: 3.7 },
];

const FIRE_LAYERS = [
  { color: FIRE.OUTLINE, inset: -1, topTrim: 0.00, cap: true  },
  { color: FIRE.BODY,    inset:  0, topTrim: 0.00, cap: false },
  { color: FIRE.CORE,    inset:  1, topTrim: 0.20, cap: false },
  { color: FIRE.HOT,     inset:  2, topTrim: 0.55, cap: false },
];

function paintTendril(cv, tendril, t, layer) {
  const { baseX, baseY, height, xOff, width, seed } = tendril;
  const maxR = Math.floor(height * (1 - layer.topTrim));
  for (let r = 0; r <= maxR; r++) {
    const u = r / height;
    const xc = baseX + xOff(u, t, seed);
    const halfW = width(u) - layer.inset;
    if (halfW < 0.4) continue;
    const y  = baseY - r;
    const x0 = Math.round(xc - halfW);
    const x1 = Math.round(xc + halfW);
    px(cv, layer.color, x0, y, x1 - x0 + 1, 1);
  }
  if (layer.cap) {
    const u = 1;
    const xc = baseX + xOff(u, t, seed);
    const y  = baseY - height - 1;
    px(cv, layer.color, Math.round(xc), y, 1, 1);
  }
}

const BASE_CX = 32;
const BASE_ROWS = [
  [49, 11, true ],
  [50, 13, true ],
  [51, 14, true ],
  [52, 14, true ],
  [53, 13, true ],
  [54, 11, true ],
  [55,  9, false],
];

function drawBase(cv, t) {
  const breath = Math.sin(t * FIRE_TAU) * 0.4;
  for (const [y, halfW, hasOuter] of BASE_ROWS) {
    const w = halfW + (hasOuter ? Math.round(breath) : 0);
    if (hasOuter) {
      px(cv, FIRE.OUTLINE, BASE_CX - w,     y, 1, 1);
      px(cv, FIRE.OUTLINE, BASE_CX + w,     y, 1, 1);
      px(cv, FIRE.BODY,    BASE_CX - w + 1, y, 1, 1);
      px(cv, FIRE.BODY,    BASE_CX + w - 1, y, 1, 1);
      if (w >= 4) {
        px(cv, FIRE.CORE,  BASE_CX - w + 2, y, 1, 1);
        px(cv, FIRE.CORE,  BASE_CX + w - 2, y, 1, 1);
        px(cv, FIRE.HOT,   BASE_CX - w + 3, y, (w - 3) * 2 + 1, 1);
      } else {
        px(cv, FIRE.HOT,   BASE_CX - w + 2, y, (w - 2) * 2 + 1, 1);
      }
    } else {
      px(cv, FIRE.OUTLINE, BASE_CX - w,     y, 1, 1);
      px(cv, FIRE.OUTLINE, BASE_CX + w,     y, 1, 1);
      px(cv, FIRE.HOT,     BASE_CX - w + 1, y, (w - 1) * 2 + 1, 1);
    }
  }
}

const SPARKS = [
  [11, 28, 10, FIRE.OUTLINE,  0,  'dot'],
  [14, 22,  8, FIRE.BODY,     6,  'dot'],
  [22, 20,  9, FIRE.OUTLINE,  12, 'h2' ],
  [33, 16, 10, FIRE.OUTLINE,  18, 'dot'],
  [42, 18,  9, FIRE.BODY,     24, 'v2' ],
  [49, 24, 10, FIRE.OUTLINE,  3,  'dot'],
  [53, 30,  8, FIRE.OUTLINE,  21, 'dot'],
];

function drawSparks(cv, t) {
  for (const [x, baseY, rise, color, phase, shape] of SPARKS) {
    const localT = ((t + phase) % FIRE_FRAMES) / FIRE_FRAMES;
    if (localT < 0.10 || localT > 0.85) continue;
    const visU = (localT - 0.10) / 0.75;
    const y = Math.round(baseY - visU * rise);
    if (shape === 'dot')      px(cv, color, x, y, 1, 1);
    else if (shape === 'h2')  px(cv, color, x, y, 2, 1);
    else                       px(cv, color, x, y, 1, 2);
  }
}

function drawFireScene(cv, t) {
  cv.fill('#ffffff', 0, 0, cv.W, cv.H);
  drawBase(cv, t);
  for (const layer of FIRE_LAYERS) {
    for (const tendril of TENDRILS) {
      paintTendril(cv, tendril, t, layer);
    }
  }
  drawSparks(cv, t);
}

// ── Render 4 sample frames ──────────────────────────────────────────
const sampleFrames = [0, 8, 15, 22];
for (const f of sampleFrames) {
  const cv = makeCanvas(FIRE_NATIVE, FIRE_NATIVE);
  drawFireScene(cv, f);
  const big = upscale(cv, 8);
  savePng(big, `/tmp/fire-frame-${String(f).padStart(2, '0')}.png`);
  console.log(`wrote /tmp/fire-frame-${String(f).padStart(2, '0')}.png`);
}
