// Renders the Wondrous Grid favicon as PNGs at 32×32, 64×64, and
// 180×180 (Apple home-screen). Hand-drawn via node-canvas — no SVG
// parsing required. Matches the SVG version exactly.
import { createCanvas } from 'canvas';
import { writeFileSync } from 'node:fs';

function drawIcon(ctx, size) {
  // Scale so the SVG's 32-unit viewBox fills the requested size.
  const s = size / 32;
  ctx.imageSmoothingEnabled = false;
  // Background — dark, rounded corners (we just paint a flat fill since
  // ICO/PNG favicons don't need rounded corners at small sizes; rounded
  // matters only for big touch icons where we'll mask via the iOS shape).
  ctx.fillStyle = '#1a1a1c';
  ctx.fillRect(0, 0, size, size);

  // 3×3 grid of brand-color cells
  const cells = [
    ['#3aa8b8', 5, 5],   ['#ffd060', 13, 5],  ['#c83828', 21, 5],
    ['#5a9028', 5, 13],  ['#ffffff', 13, 13], ['#7c4abe', 21, 13],
    ['#e87028', 5, 21],  ['#7ed4dc', 13, 21], ['#ffd060', 21, 21],
  ];
  for (const [hex, x, y] of cells) {
    ctx.fillStyle = hex;
    ctx.fillRect(x * s, y * s, 6 * s, 6 * s);
  }

  // Outer yellow frame
  ctx.strokeStyle = '#ffd060';
  ctx.lineWidth = Math.max(1, 1.5 * s);
  ctx.strokeRect(1 * s + ctx.lineWidth / 2, 1 * s + ctx.lineWidth / 2,
                 30 * s - ctx.lineWidth, 30 * s - ctx.lineWidth);

  // Highlight ring on the center cell
  ctx.strokeStyle = '#ffd060';
  ctx.lineWidth = Math.max(1, 1 * s);
  ctx.strokeRect(12 * s + ctx.lineWidth / 2, 12 * s + ctx.lineWidth / 2,
                 8 * s - ctx.lineWidth, 8 * s - ctx.lineWidth);
}

for (const size of [32, 64, 180]) {
  const cvs = createCanvas(size, size);
  const ctx = cvs.getContext('2d');
  drawIcon(ctx, size);
  const path = `assets/wondrous-grid-icon-${size}.png`;
  writeFileSync(path, cvs.toBuffer('image/png'));
  console.log(`✓ ${path}  (${size}×${size})`);
}
