// Render preview PNGs of the metapixel fire animation to /tmp so we can
// eyeball the result without launching a browser. Mirrors the draw logic
// from metapixel/index.html exactly — keep in sync.

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
  if (hex.length === 7) {
    return [parseInt(hex.slice(1, 3), 16), parseInt(hex.slice(3, 5), 16), parseInt(hex.slice(5, 7), 16), 255];
  }
  throw new Error('unsupported color ' + hex);
}
function px(cv, color, x, y, w, h) { cv.fill(color, x, y, w, h); }

// Scale up nearest-neighbor for export.
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
const FIRE_FRAMES   = 24;
const FIRE_NATIVE   = 64;
const FIRE_LOOP_TAU = (Math.PI * 2) / FIRE_FRAMES;

const FIRE = {
  CORE:    '#fff6c2',
  YELLOW:  '#ffd23f',
  ORANGE:  '#ff8c1a',
  DEEPORG: '#ff5e1f',
  RED:     '#e63a1a',
  DEEPRED: '#8a1f12',
};

const FIRE_SIZES = [
  { w: 3,  h: 5  },
  { w: 4,  h: 8  },
  { w: 5,  h: 12 },
  { w: 7,  h: 17 },
  { w: 9,  h: 22 },
  { w: 11, h: 28 },
];
const FIRE_XS    = [4, 11, 19, 28, 39, 53];
const FIRE_BASE_Y = 60;
const FIRE_SEEDS = [0.0, 1.3, 2.7, 4.1, 5.6, 0.8];

function fireBaseProfile(row, w, h) {
  const u = row / Math.max(1, h - 1);
  let mult;
  if      (u < 0.10) mult = 0.40 + u * 1.0;
  else if (u < 0.30) mult = 0.50 + (u - 0.10) * 0.10;
  else if (u < 0.55) mult = 0.52 - (u - 0.30) * 0.40;
  else if (u < 0.85) mult = 0.42 - (u - 0.55) * 1.10;
  else                mult = 0.09 - (u - 0.85) * 0.55;
  return Math.max(0.5, w * mult);
}
function fireProfile(size, t, seed) {
  const { w, h } = FIRE_SIZES[size];
  const left = new Array(h), right = new Array(h);
  const amp = 0.4 + size * 0.28;
  const f1 = FIRE_LOOP_TAU * 2;
  const f2 = FIRE_LOOP_TAU * 3;
  const f3 = FIRE_LOOP_TAU * 1;
  for (let row = 0; row < h; row++) {
    const u = row / Math.max(1, h - 1);
    const base = fireBaseProfile(row, w, h);
    if (u < 0.30) { left[row] = base; right[row] = base; }
    else {
      const upMix = (u - 0.30) / 0.70;
      const cap = Math.max(0.4, base * 0.55);
      const localAmp = Math.min(amp * (0.35 + upMix * 1.0), cap);
      const phase = u * 4.8;
      const lw = Math.sin(phase + t * f1 + seed) * localAmp
               + Math.sin(phase * 1.7 + t * f2 + seed * 1.3) * (localAmp * 0.55)
               + Math.sin(phase * 0.7 + t * f3 + seed * 0.9) * (localAmp * 0.35);
      const rw = Math.sin(phase + t * f1 + seed + Math.PI) * localAmp
               + Math.sin(phase * 1.7 + t * f2 + seed * 1.3 + 1.9) * (localAmp * 0.55)
               + Math.sin(phase * 0.7 + t * f3 + seed * 0.9 + 2.4) * (localAmp * 0.35);
      left[row]  = Math.max(0.5, base + Math.min(lw, base * 0.3));
      right[row] = Math.max(0.5, base + Math.min(rw, base * 0.3));
    }
  }
  return { left, right, h };
}
function fireTongues(size, t, seed) {
  if (size < 3) return [];
  const { w, h } = FIRE_SIZES[size];
  const count = size >= 5 ? 3 : (size >= 4 ? 2 : 1);
  const tongues = [];
  for (let i = 0; i < count; i++) {
    const slot = count === 1 ? 0.5 : i / (count - 1);
    const drift = Math.sin(t * FIRE_LOOP_TAU + seed + i * 1.7) * 0.4;
    const dx = Math.round((slot - 0.5 + drift * 0.3) * w * 0.45);
    const lift = Math.sin(t * FIRE_LOOP_TAU * 2 + seed * 1.7 + i * 2.1) * 0.5 + 0.5;
    const isCentral = Math.abs(slot - 0.5) < 0.25;
    const maxH = isCentral ? Math.floor(h * 0.22) : Math.floor(h * 0.14);
    const tongueH = Math.max(2, Math.floor(2 + lift * maxH));
    tongues.push({ dx, h: tongueH });
  }
  return tongues;
}
function fireRowPaint(cv, cx, baseY, left, right, h, color, inset, topTrim) {
  const maxRow = h - topTrim;
  for (let row = 0; row < maxRow; row++) {
    const lh = left[row] - inset, rh = right[row] - inset;
    if (lh < 0.5 && rh < 0.5) continue;
    const y = baseY - row;
    const x0 = Math.round(cx - Math.max(0, lh));
    const x1 = Math.round(cx + Math.max(0, rh));
    px(cv, color, x0, y, x1 - x0 + 1, 1);
  }
}
function drawFlame(cv, cx, baseY, size, t, seed) {
  const { left, right, h } = fireProfile(size, t, seed);
  const tongues = fireTongues(size, t, seed);
  for (const tg of tongues) {
    const tx = cx + tg.dx;
    const ty = baseY - h + 1;
    for (let i = 0; i < tg.h; i++) {
      const fromTop = tg.h - 1 - i;
      const halfW = fromTop === 0 ? 0 : 1;
      px(cv, FIRE.DEEPRED, tx - halfW, ty - i, halfW * 2 + 1, 1);
    }
  }
  fireRowPaint(cv, cx, baseY, left, right, h, FIRE.DEEPRED, -1, 0);
  {
    const topRow = h - 1;
    const lh = left[topRow], rh = right[topRow];
    const y = baseY - h;
    const x0 = Math.round(cx - lh);
    const x1 = Math.round(cx + rh);
    px(cv, FIRE.DEEPRED, x0, y, Math.max(1, x1 - x0 + 1), 1);
  }
  fireRowPaint(cv, cx, baseY, left, right, h, FIRE.RED,     0, 0);
  fireRowPaint(cv, cx, baseY, left, right, h, FIRE.DEEPORG, 1, 1);
  fireRowPaint(cv, cx, baseY, left, right, h, FIRE.ORANGE,  2, 2);
  fireRowPaint(cv, cx, baseY, left, right, h, FIRE.YELLOW,  3, 3);
  if (size >= 2) {
    const trim = Math.max(1, Math.floor(h * 0.35));
    fireRowPaint(cv, cx, baseY, left, right, h, FIRE.CORE, 4, trim);
  }
  for (const tg of tongues) {
    const tx = cx + tg.dx;
    const ty = baseY - h + 1;
    for (let i = 0; i < tg.h - 1; i++) {
      const color = i === 0 ? FIRE.YELLOW
                  : (i < tg.h - 2 ? FIRE.ORANGE : FIRE.DEEPORG);
      px(cv, color, tx, ty - i, 1, 1);
    }
  }
}
function drawFireScene(cv, t) {
  cv.fill('#ffffff', 0, 0, cv.W, cv.H);
  for (let i = 0; i < 6; i++) {
    drawFlame(cv, FIRE_XS[i], FIRE_BASE_Y, i, t, FIRE_SEEDS[i]);
  }
}

// ── Render 4 sample frames ──────────────────────────────────────────
const sampleFrames = [0, 6, 12, 18];
for (const f of sampleFrames) {
  const cv = makeCanvas(FIRE_NATIVE, FIRE_NATIVE);
  drawFireScene(cv, f);
  const big = upscale(cv, 8); // 512x512
  savePng(big, `/tmp/fire-frame-${String(f).padStart(2, '0')}.png`);
  console.log(`wrote /tmp/fire-frame-${String(f).padStart(2, '0')}.png`);
}
