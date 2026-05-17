// Render preview PNGs of the v3 wide roaring fire (11 tendrils) to /tmp.
// Mirrors the draw logic from metapixel/index.html — keep in sync.

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
const FIRE_NATIVE = 128;
const FIRE_TAU = (Math.PI * 2) / FIRE_FRAMES;

const FIRE = {
  OUTLINE: '#D95738',
  BODY:    '#F16E32',
  CORE:    '#F7A833',
  HOT:     '#FFF7A4',
};

function sCurveOff(u, t, seed, sign, amp) {
  const s    = Math.sin(u * Math.PI * 2) * amp;
  const hook = u > 0.82 ? Math.sin((u - 0.82) * Math.PI / 0.18) * (amp * 0.55) : 0;
  const wob  = Math.sin(t * FIRE_TAU + u * 1.5 + seed * 1.7) * 0.45;
  return (s + hook) * sign + wob;
}
function halfStepOff(u, t, seed, sign, amp) {
  let step;
  if      (u < 0.10) step = u * (amp * 6.25);
  else if (u < 0.40) step = (amp * 0.625) + (u - 0.10) * (amp * 1.75);
  else if (u < 0.75) step = (amp * 1.15)  - (u - 0.40) * (amp * 2.25);
  else                step = (amp * 0.36)  - (u - 0.75) * (amp * 1.5);
  const wob = Math.sin(t * FIRE_TAU + u * 1.5 + seed * 1.7) * 0.45;
  return step * sign + wob;
}
function spireOff(u, t, seed) {
  const jit = Math.sin(u * 8.4 + seed) * 0.55;
  const wob = Math.sin(t * FIRE_TAU + seed * 2.1) * 0.45;
  return jit + wob;
}
function pillarOff(u, t, seed) {
  const m   = Math.sin(u * 3.2 + seed) * 0.8;
  const wob = Math.sin(t * FIRE_TAU + u + seed * 1.7) * 0.5;
  return m + wob;
}
const STYLE = { spire: spireOff, s: sCurveOff, half: halfStepOff, pillar: pillarOff };

function tendrilWidth(u, baseW) {
  if (u < 0.12) return baseW;
  if (u < 0.55) return baseW - (u - 0.12) * (baseW * 0.45);
  if (u < 0.85) return (baseW * 0.81) - (u - 0.55) * (baseW * 1.6);
  return Math.max(0.4, (baseW * 0.33) - (u - 0.85) * (baseW * 2.2));
}

const TENDRILS = [
  { baseX:  10, baseY: 100, height:  8, baseW: 1.4, style: 'spire',  seed: 0.5, mirror: false, amp: 1   },
  { baseX:  22, baseY: 100, height: 16, baseW: 1.7, style: 's',      seed: 1.3, mirror: false, amp: 2   },
  { baseX:  36, baseY: 100, height: 26, baseW: 2.1, style: 's',      seed: 2.1, mirror: false, amp: 2.8 },
  { baseX:  48, baseY: 100, height: 36, baseW: 2.5, style: 's',      seed: 2.9, mirror: false, amp: 3.2 },
  { baseX:  56, baseY: 100, height: 44, baseW: 2.9, style: 's',      seed: 3.7, mirror: false, amp: 3.6 },
  { baseX:  64, baseY: 100, height: 58, baseW: 3.4, style: 'pillar', seed: 0,   mirror: false, amp: 1   },
  { baseX:  72, baseY: 100, height: 44, baseW: 2.9, style: 's',      seed: 4.5, mirror: true,  amp: 3.6 },
  { baseX:  80, baseY: 100, height: 36, baseW: 2.5, style: 'half',   seed: 5.3, mirror: true,  amp: 3.2 },
  { baseX:  92, baseY: 100, height: 26, baseW: 2.1, style: 's',      seed: 6.1, mirror: true,  amp: 2.8 },
  { baseX: 106, baseY: 100, height: 16, baseW: 1.7, style: 's',      seed: 6.9, mirror: true,  amp: 2   },
  { baseX: 118, baseY: 100, height:  8, baseW: 1.4, style: 'spire',  seed: 7.7, mirror: true,  amp: 1   },
];

const FIRE_LAYERS = [
  { color: FIRE.OUTLINE, inset: -1, topTrim: 0.00, cap: true  },
  { color: FIRE.BODY,    inset:  0, topTrim: 0.00, cap: false },
  { color: FIRE.CORE,    inset:  1, topTrim: 0.20, cap: false },
  { color: FIRE.HOT,     inset:  2, topTrim: 0.55, cap: false },
];

function paintTendril(cv, tendril, t, layer) {
  const { baseX, baseY, height, baseW, style, seed, mirror, amp } = tendril;
  const sign = mirror ? -1 : 1;
  const offFn = STYLE[style];
  const maxR = Math.floor(height * (1 - layer.topTrim));
  for (let r = 0; r <= maxR; r++) {
    const u = r / height;
    const xc = baseX + offFn(u, t, seed, sign, amp);
    const halfW = tendrilWidth(u, baseW) - layer.inset;
    if (halfW < 0.4) continue;
    const y  = baseY - r;
    const x0 = Math.round(xc - halfW);
    const x1 = Math.round(xc + halfW);
    px(cv, layer.color, x0, y, x1 - x0 + 1, 1);
  }
  if (layer.cap) {
    const xc = baseX + offFn(1, t, seed, sign, amp);
    px(cv, layer.color, Math.round(xc), baseY - height - 1, 1, 1);
  }
}

const BASE_CX = 64;
const BASE_ROWS = [
  [ 97, 42, true ],
  [ 98, 52, true ],
  [ 99, 56, true ],
  [100, 56, true ],
  [101, 54, true ],
  [102, 48, true ],
  [103, 38, true ],
  [104, 26, false],
];

function drawBase(cv, t) {
  const breath = Math.sin(t * FIRE_TAU) * 0.6;
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
  [  6, 70, 12, FIRE.OUTLINE,  0,  'dot'],
  [ 12, 60, 14, FIRE.BODY,     5,  'dot'],
  [ 20, 52, 12, FIRE.OUTLINE,  10, 'h2' ],
  [ 28, 46, 14, FIRE.OUTLINE,  17, 'dot'],
  [ 40, 38, 16, FIRE.BODY,     22, 'v2' ],
  [ 52, 32, 18, FIRE.OUTLINE,  3,  'dot'],
  [ 64, 28, 18, FIRE.OUTLINE,  14, 'h2' ],
  [ 76, 32, 16, FIRE.BODY,     8,  'dot'],
  [ 88, 40, 14, FIRE.OUTLINE,  19, 'v2' ],
  [100, 48, 14, FIRE.OUTLINE,  26, 'dot'],
  [108, 56, 12, FIRE.BODY,     11, 'dot'],
  [116, 64, 12, FIRE.OUTLINE,  23, 'dot'],
  [122, 72, 10, FIRE.OUTLINE,  6,  'dot'],
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
  const big = upscale(cv, 4);   // 128 × 4 = 512
  savePng(big, `/tmp/fire-frame-${String(f).padStart(2, '0')}.png`);
  console.log(`wrote /tmp/fire-frame-${String(f).padStart(2, '0')}.png`);
}
