#!/usr/bin/env python3
"""Chunky 16-bit pixel-art saucer with green tractor beam.

Style match: based on a user-supplied 64x64 HTML reference. Same 10-color
palette (red dome, metallic gray hull, green striped beam) but extended
vertically so the beam can reach a target, and animated.

Logical 64x128 -> 8x NEAREST -> 512x1024. Transparent background.
72-frame seamless loop @ 24 fps.

Outputs:
  output/ufo3_animated.gif
  output/ufo3_layer_all.gif
  output/ufo3_layer_ufo.gif
  output/ufo3_layer_beam.gif
  output/ufo3_anim_frames/*.png   (per-frame RGBA, VFX-ready)
  output/ufo3_preview.png         (3-up still)
"""
import math, os, shutil
from PIL import Image

W, H, SCALE = 64, 128, 8
TOTAL_FRAMES = 72
FPS = 24
TAU = math.pi * 2


def h2r(h):
    return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))


PAL = {
    'x': None,
    'W': h2r('#ffffff'),
    'R': h2r('#e74c3c'),
    'D': h2r('#c0392b'),
    'G1': h2r('#bdc3c7'),
    'G2': h2r('#7f8c8d'),
    'G3': h2r('#34495e'),
    'B1': h2r('#a3f7bf'),
    'B2': h2r('#58d68d'),
    'B3': h2r('#28b463'),
}


def put(PX, x, y, key):
    if not (0 <= x < W and 0 <= y < H): return
    col = PAL.get(key)
    if col:
        PX[x, y] = col + (255,)


def fill_row(PX, y, cells):
    """cells is a list of (x, key) tuples or a dict-like."""
    for x, k in cells:
        put(PX, x, y, k)


# ── UFO sprite construction ─────────────────────────
def make_ufo_rows(frame):
    """Return list of (y, [keys...]) representing the UFO sprite at this frame.

    Animation: dome interior shimmers on the cycle, portholes blink in
    sequence. UFO sits at the top of the canvas.

    Layout (relative to base_y):
      0-4   dome (5 rows, proper hemisphere — 1/3/5/7/9 wide, centered)
      5     top hull
      6     hull mid (highlight)
      7     hull mid (wider)
      8     porthole row
      9     dark rim band
      10-11 underside taper
      12    emitter
    """
    rows = []
    base_y = 4  # leave 4 rows of headroom

    # ── Dome (5 rows, proper centered half-dome) ──
    # Apex/upper rows get a "shimmer" pulse via the highlight pixel
    pulse = (math.sin(frame / TOTAL_FRAMES * TAU * 2) + 1) / 2  # 0..1
    apex_hl = 'W' if pulse > 0.65 else 'R'
    rows.append((base_y + 0, ['x']*31 + ['D', apex_hl, 'D'] + ['x']*30))
    rows.append((base_y + 1, ['x']*30 + ['D','R','R','R','D'] + ['x']*29))
    rows.append((base_y + 2, ['x']*29 + ['D','R','W','W','W','R','D'] + ['x']*28))
    rows.append((base_y + 3, ['x']*28 + ['D','R','W','W','W','W','W','R','D'] + ['x']*27))
    rows.append((base_y + 4, ['x']*28 + ['D','R','R','R','R','R','R','R','D'] + ['x']*27))

    # ── Top hull (light gray catching highlight) ──
    rows.append((base_y + 5, ['x']*18 + ['G2'] + ['G1']*27 + ['G2'] + ['x']*17))
    rows.append((base_y + 6, ['x']*14 + ['G2'] + ['G1']*2 + ['W','W'] + ['G1']*30 + ['G2'] + ['x']*14))
    rows.append((base_y + 7, ['x']*10 + ['G2','G1','G1','W','W'] + ['G1']*4 + ['G2']*20 + ['G1']*13 + ['G2'] + ['x']*9))

    # ── Porthole row (with blinking lights) ───────
    n_ports = 5
    port_t = (frame / TOTAL_FRAMES) % 1.0
    port_lights = []
    for p in range(n_ports):
        phase = (port_t + p * 0.20) % 1.0
        port_lights.append('W' if phase < 0.6 else 'G3')

    rim_row = ['x']*7 + ['G3'] + ['G2']*9 + ['G3','G3']
    for p in range(n_ports):
        rim_row += [port_lights[p], port_lights[p], 'G3', 'G3']
    rim_row += ['G2']*19 + ['G3']
    while len(rim_row) < W:
        rim_row.append('x')
    rim_row = rim_row[:W]
    rows.append((base_y + 8, rim_row))

    # ── Wide dark hull rim band ───────────────────
    rows.append((base_y + 9, ['x']*5 + ['G3']*54 + ['x']*5))

    # ── Underside taper (narrowing) ───────────────
    rows.append((base_y + 10, ['x']*9 + ['G3']*46 + ['x']*9))
    rows.append((base_y + 11, ['x']*20 + ['G3']*24 + ['x']*20))

    # ── Emitter row (green bright spot) ───────────
    rows.append((base_y + 12, ['x']*22 + ['B3','B2'] + ['B1']*18 + ['B2','B3'] + ['x']*22))

    return rows, base_y


# ── Beam construction ───────────────────────────────
def draw_beam(PX, frame, beam_top_y):
    """Draw the widening green beam below the UFO with scrolling white stripes."""
    beam_rows = H - beam_top_y
    if beam_rows <= 0: return
    # Beam pulse — slightly brighter occasionally
    pulse = (math.sin(frame / TOTAL_FRAMES * TAU * 3) + 1) / 2
    for i in range(beam_rows):
        y = beam_top_y + i
        progress = i / max(beam_rows, 1)
        half_w = int(10 + progress * 14)
        center = W // 2
        for dx in range(-half_w, half_w + 1):
            j = center + dx
            if not (0 <= j < W): continue
            dist = abs(dx)
            ratio = dist / max(half_w, 1)
            # Scrolling white stripe — moves DOWN over frames
            stripe_phase = (i + frame * 2) % 6
            if ratio < 0.4:
                # Hot white-green core with vertical stripe scroll
                if (j % 3 == 0 and stripe_phase < 2):
                    key = 'W'
                else:
                    key = 'B1'
            elif ratio < 0.75:
                key = 'B2'
            else:
                key = 'B3'
            put(PX, j, y, key)
    # Pulse glow brightening — flash a few core pixels brighter occasionally
    if pulse > 0.85:
        for i in range(0, beam_rows, 4):
            y = beam_top_y + i
            put(PX, W // 2, y, 'W')


def build_frame(frame, layers=frozenset({'ufo', 'beam'})):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    PX = img.load()

    # Hover bob — shift everything down/up by a pixel
    bob = int(round(math.sin(frame / TOTAL_FRAMES * TAU) * 1))

    ufo_rows, base_y = make_ufo_rows(frame)
    # Beam starts just below the UFO's emitter row
    beam_top_y = base_y + 13 + bob

    if 'beam' in layers:
        draw_beam(PX, frame, beam_top_y)
    if 'ufo' in layers:
        for y, row in ufo_rows:
            ys = y + bob
            for x, key in enumerate(row):
                put(PX, x, ys, key)
    return img


def render_layer_gif(name, layers, save_frames=False):
    frames = []
    for f in range(TOTAL_FRAMES):
        img = build_frame(f, layers=layers)
        big = img.resize((W * SCALE, H * SCALE), Image.NEAREST)
        frames.append(big)
        if save_frames:
            os.makedirs('output/ufo3_anim_frames', exist_ok=True)
            big.save(f'output/ufo3_anim_frames/frame_{f:03d}.png')
    gif_frames = [f.convert('RGBA').quantize(method=Image.FASTOCTREE, dither=Image.NONE)
                  for f in frames]
    gif_frames[0].save(
        f'output/ufo3_layer_{name}.gif',
        save_all=True, append_images=gif_frames[1:],
        duration=int(round(1000 / FPS)), loop=0, disposal=2,
        transparency=0, optimize=False,
    )
    print(f'wrote output/ufo3_layer_{name}.gif')
    return frames


def main():
    os.makedirs('output', exist_ok=True)
    all_frames = render_layer_gif('all', {'ufo', 'beam'}, save_frames=True)
    shutil.copy('output/ufo3_layer_all.gif', 'output/ufo3_animated.gif')
    print('wrote output/ufo3_animated.gif')
    ufo_frames = render_layer_gif('ufo', {'ufo'})
    beam_frames = render_layer_gif('beam', {'beam'})

    snap = 18
    cols = [all_frames[snap], ufo_frames[snap], beam_frames[snap]]
    sheet = Image.new('RGBA', (W * SCALE * len(cols), H * SCALE), (28, 28, 32, 255))
    for i, s in enumerate(cols):
        sheet.paste(s, (i * W * SCALE, 0), s)
    sheet.save('output/ufo3_preview.png')
    print('wrote output/ufo3_preview.png')


if __name__ == '__main__':
    main()
