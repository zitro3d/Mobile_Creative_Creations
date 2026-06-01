#!/usr/bin/env python3
"""TR-3B style triangular craft with searchlight scan beam.

Logical 240x360 -> 3x NEAREST -> 720x1080. 72-frame seamless loop @ 24 fps.
Transparent canvas, no background stars — ready to composite over a plate.

Outputs:
  output/ufo2_animated.gif        (full composite, 1-bit alpha)
  output/ufo2_layer_all.gif
  output/ufo2_layer_ufo.gif       (craft only, no beam)
  output/ufo2_layer_beam.gif      (beam only, no craft)
  output/ufo2_anim_frames/*.png   (per-frame RGBA with full alpha, VFX-ready)
  output/ufo2_preview.png         (3-up still preview)
"""
import math, os, shutil
from PIL import Image

W, H, SCALE = 240, 360, 3
TOTAL_FRAMES = 72
FPS = 24
TAU = math.pi * 2
HCX = 120

# ── Triangular craft palette (dark, military matte) ────
HULL_O   = (6, 8, 14)        # silhouette outline
HULL_BLK = (18, 20, 28)      # body base
HULL_D   = (32, 36, 46)      # mid body
HULL_M   = (52, 58, 74)      # subtle inner highlight
HULL_HI  = (110, 122, 150)   # top edge spec

# Underbelly engine glow (white-blue plasma)
ENG_W    = (255, 255, 250)
ENG_HOT  = (215, 240, 255)
ENG_BR   = (140, 200, 255)
ENG_L    = (75, 150, 230)
ENG_D    = (35, 90, 180)
ENG_DEEP = (20, 50, 130)

# Running lights
RED_HOT  = (255, 90, 75)
RED_DIM  = (175, 40, 25)
GRN_HOT  = (105, 255, 130)
GRN_DIM  = (40, 175, 65)
LIGHT_W  = (245, 250, 255)

# Searchlight beam (white-cyan)
BEAM_CORE = (250, 252, 255)
BEAM_HOT  = (200, 230, 255)
BEAM_BR   = (150, 200, 255)
BEAM_MID  = (90, 160, 230)
BEAM_D    = (40, 100, 180)


def make_put(PX):
    def put(x, y, c, a=255):
        x = int(round(x)); y = int(round(y))
        if not (0 <= x < W and 0 <= y < H): return
        if a >= 255:
            PX[x, y] = (c[0], c[1], c[2], 255); return
        if a <= 0: return
        er, eg, eb, ea = PX[x, y]
        na = a / 255.0
        oa = na + (ea / 255.0) * (1.0 - na)
        if oa <= 0: return
        ow = (ea / 255.0) * (1.0 - na)
        r = (c[0] * na + er * ow) / oa
        g = (c[1] * na + eg * ow) / oa
        b = (c[2] * na + eb * ow) / oa
        PX[x, y] = (int(r), int(g), int(b), int(oa * 255))
    return put


def hover_offset(frame):
    """Gentle vertical bob for the craft."""
    return int(round(math.sin(frame / TOTAL_FRAMES * TAU) * 2.5))


def draw_triangle_ufo(put, frame):
    bob = hover_offset(frame)
    TOP_Y = 60 + bob
    BOT_Y = 122 + bob
    HW_TOP = 86
    h = BOT_Y - TOP_Y

    # Triangle body rows
    for y in range(TOP_Y, BOT_Y + 1):
        rel = (y - TOP_Y) / h
        hw = int(round(HW_TOP * (1 - rel)))
        if hw < 1: continue
        for dx in range(-hw, hw + 1):
            x = HCX + dx
            u = abs(dx) / max(hw, 1)
            if abs(dx) == hw:
                col = HULL_O
            elif abs(dx) >= hw - 1:
                col = HULL_BLK
            elif rel < 0.08:
                col = HULL_D if dx > 0 else HULL_BLK
            elif u > 0.65:
                col = HULL_BLK
            elif u < 0.35:
                col = HULL_D
            else:
                col = HULL_BLK
            put(x, y, col)

    # Top edge highlight (catching light from above-back)
    for dx in range(-HW_TOP + 2, HW_TOP - 1):
        x = HCX + dx
        # Highlight fades from right (bright) to left
        falloff = (dx + HW_TOP) / (2 * HW_TOP)
        a = int(180 * falloff)
        put(x, TOP_Y, HULL_HI, a=a)
        if dx > -HW_TOP + 6 and dx < HW_TOP - 5:
            put(x, TOP_Y + 1, HULL_M, a=int(80 * falloff))

    # Subtle panel seam line down the middle (front-to-back)
    for y in range(TOP_Y + 4, BOT_Y - 3):
        put(HCX, y, HULL_O, a=120)

    # ── Underbelly engine glow ────────────────────────
    eng_cx = HCX
    eng_cy = TOP_Y + int(h * 0.55)
    eng_r = 11
    pulse = 0.88 + 0.12 * math.sin(frame / TOTAL_FRAMES * TAU * 3)
    for dy in range(-eng_r - 1, eng_r + 2):
        for dx in range(-eng_r - 1, eng_r + 2):
            d = math.sqrt(dx * dx + dy * dy)
            if d > eng_r + 0.5: continue
            edge = 1.0 - d / eng_r
            edge *= pulse
            if   edge > 0.88: col = ENG_W
            elif edge > 0.65: col = ENG_HOT
            elif edge > 0.42: col = ENG_BR
            elif edge > 0.20: col = ENG_L
            elif edge > 0.05: col = ENG_D
            else:             col = ENG_DEEP
            a = int(255 * max(0, edge))
            if a > 0: put(eng_cx + dx, eng_cy + dy, col, a=a)

    # ── Corner running lights ────────────────────────
    # Red (back-left), Green (back-right) — blink alternately
    blink = (math.sin(frame / TOTAL_FRAMES * TAU * 2) + 1) / 2  # 0..1
    red_on = blink > 0.45
    grn_on = blink < 0.55  # opposite blink phase

    # Red light cluster
    rx, ry = HCX - HW_TOP + 3, TOP_Y + 2
    if red_on:
        put(rx, ry, LIGHT_W)
        put(rx + 1, ry, RED_HOT)
        put(rx, ry + 1, RED_HOT)
        put(rx + 1, ry + 1, RED_HOT)
        # Halo
        for hx, hy in [(rx - 1, ry), (rx + 2, ry), (rx, ry - 1), (rx, ry + 2), (rx + 1, ry + 2), (rx + 2, ry + 1)]:
            put(hx, hy, RED_DIM, a=200)
    else:
        put(rx, ry, RED_DIM)
        put(rx + 1, ry + 1, RED_DIM)

    # Green light cluster
    gx, gy = HCX + HW_TOP - 4, TOP_Y + 2
    if grn_on:
        put(gx, gy, LIGHT_W)
        put(gx + 1, gy, GRN_HOT)
        put(gx, gy + 1, GRN_HOT)
        put(gx + 1, gy + 1, GRN_HOT)
        for hx, hy in [(gx - 1, gy), (gx + 2, gy), (gx, gy - 1), (gx, gy + 2), (gx + 1, gy + 2), (gx - 1, gy + 1)]:
            put(hx, hy, GRN_DIM, a=200)
    else:
        put(gx, gy, GRN_DIM)
        put(gx + 1, gy + 1, GRN_DIM)

    # Front white nav light (bright at the point — emitter)
    fx, fy = HCX, BOT_Y - 1
    put(fx, fy, ENG_W)
    put(fx - 1, fy, ENG_HOT)
    put(fx + 1, fy, ENG_HOT)
    put(fx, fy - 1, ENG_HOT)


def draw_searchlight(put, frame):
    """Continuous searchlight beam from the front emitter — always on.

    Narrower than the saucer's tractor beam, with horizontal scan lines
    moving downward to convey "scanning the ground".
    """
    bob = hover_offset(frame)
    TOP = 123 + bob
    BOT = 340
    HW_TOP = 4
    MAX_HW_BOT = 26
    max_h = BOT - TOP

    pulse = 0.88 + 0.12 * math.sin(frame / TOTAL_FRAMES * TAU * 4)

    # Beam body — continuous, focused
    for y in range(TOP, BOT + 1):
        rel = (y - TOP) / max_h
        hw = HW_TOP + rel * (MAX_HW_BOT - HW_TOP)
        for dx in range(-int(hw) - 1, int(hw) + 2):
            u = dx / hw
            if abs(u) > 1.05: continue
            edge = 1.0 - min(1.0, abs(u) ** 1.6)
            vfade = 1.0 - rel * 0.45      # fades more toward the bottom
            a_base = edge * vfade * pulse
            if abs(u) < 0.22:
                col = BEAM_CORE; alpha = int(230 * a_base)
            elif abs(u) < 0.50:
                col = BEAM_HOT;  alpha = int(160 * a_base)
            elif abs(u) < 0.80:
                col = BEAM_BR;   alpha = int(100 * a_base)
            else:
                col = BEAM_MID;  alpha = int(55 * a_base)
            put(HCX + dx, y, col, a=min(255, max(0, alpha)))

    # Horizontal scan lines moving DOWNWARD — gives "scanning ground" feel
    N_SCANS = 4
    for s in range(N_SCANS):
        scan_phase = (frame * 3 + s * (TOTAL_FRAMES // N_SCANS)) % TOTAL_FRAMES
        scan_progress = scan_phase / TOTAL_FRAMES
        scan_y = TOP + scan_progress * max_h
        if scan_y > BOT: continue
        rel_y = (scan_y - TOP) / max_h
        hw = HW_TOP + rel_y * (MAX_HW_BOT - HW_TOP)
        # Bright scan bar
        for dx in range(-int(hw), int(hw) + 1):
            put(HCX + dx, int(scan_y), BEAM_CORE, a=210)
            put(HCX + dx, int(scan_y) + 1, BEAM_HOT, a=140)
            put(HCX + dx, int(scan_y) - 1, BEAM_HOT, a=80)

    # Soft floor splash where the beam hits the ground
    floor_y = BOT
    splash_hw = MAX_HW_BOT + 4
    for dy in range(0, 3):
        for dx in range(-splash_hw - dy * 2, splash_hw + dy * 2 + 1):
            d = math.sqrt(dx * dx + (dy * 3) ** 2)
            if d > splash_hw + dy * 2: continue
            fade = 1.0 - d / (splash_hw + dy * 2)
            a = int(120 * fade * (1.0 - dy / 4))
            put(HCX + dx, floor_y + dy, BEAM_HOT, a=a)


def build_frame(frame, layers=frozenset({'ufo', 'beam'})):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    put = make_put(img.load())
    if 'beam' in layers: draw_searchlight(put, frame)
    if 'ufo' in layers:  draw_triangle_ufo(put, frame)
    return img


def render_layer_gif(name, layers, save_frames=False):
    frames = []
    for f in range(TOTAL_FRAMES):
        img = build_frame(f, layers=layers)
        big = img.resize((W * SCALE, H * SCALE), Image.NEAREST)
        frames.append(big)
        if save_frames:
            frame_dir = 'output/ufo2_anim_frames'
            os.makedirs(frame_dir, exist_ok=True)
            big.save(f'{frame_dir}/frame_{f:03d}.png')
    gif_frames = [f.convert('RGBA').quantize(method=Image.FASTOCTREE, dither=Image.NONE)
                  for f in frames]
    gif_frames[0].save(
        f'output/ufo2_layer_{name}.gif',
        save_all=True, append_images=gif_frames[1:],
        duration=int(round(1000 / FPS)), loop=0, disposal=2,
        transparency=0, optimize=False,
    )
    print(f'wrote output/ufo2_layer_{name}.gif')
    return frames


def main():
    os.makedirs('output', exist_ok=True)
    all_frames  = render_layer_gif('all', {'ufo', 'beam'}, save_frames=True)
    shutil.copy('output/ufo2_layer_all.gif', 'output/ufo2_animated.gif')
    print('wrote output/ufo2_animated.gif')
    ufo_frames  = render_layer_gif('ufo',  {'ufo'})
    beam_frames = render_layer_gif('beam', {'beam'})

    # Preview sheet (3-up)
    snap = 18
    cols = [all_frames[snap], ufo_frames[snap], beam_frames[snap]]
    sheet = Image.new('RGBA', (W * SCALE * len(cols), H * SCALE), (28, 28, 32, 255))
    for i, s in enumerate(cols):
        sheet.paste(s, (i * W * SCALE, 0), s)
    sheet.save('output/ufo2_preview.png')
    print('wrote output/ufo2_preview.png')


if __name__ == '__main__':
    main()
