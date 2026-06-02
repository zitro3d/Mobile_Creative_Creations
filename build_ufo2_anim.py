#!/usr/bin/env python3
"""Classic flying saucer with green tractor beam (VFX-comp ready).

Style match: small red glowing dome on top, dark teal-green hull with a
band of light portholes around the rim, curved underside, wide saturated
green beam casting downward.

Logical 240x360 -> 3x NEAREST -> 720x1080. 72-frame seamless loop @ 24 fps.
Transparent canvas, no background — drop straight into a plate.

Outputs:
  output/ufo2_animated.gif        (full composite)
  output/ufo2_layer_all.gif
  output/ufo2_layer_ufo.gif       (saucer only)
  output/ufo2_layer_beam.gif      (beam only)
  output/ufo2_anim_frames/*.png   (per-frame RGBA for VFX import)
  output/ufo2_preview.png         (3-up still preview)
"""
import math, os, shutil
from PIL import Image

W, H, SCALE = 240, 360, 3
TOTAL_FRAMES = 72
FPS = 24
TAU = math.pi * 2
HCX = 120

# ── Dome — small bright RED-orange ───────────────────
DOME_CORE  = (255, 255, 230)
DOME_HOT   = (255, 200, 130)
DOME_BR    = (255, 130, 80)
DOME_L     = (235, 75, 45)
DOME_M     = (185, 45, 30)
DOME_D     = (125, 30, 20)
DOME_DEEP  = (75, 18, 14)

# ── Hull — dark teal-green metallic ──────────────────
HULL_VL = (135, 165, 150)   # very light highlight
HULL_HI = (95, 125, 115)
HULL_L  = (60, 85, 78)
HULL_M  = (40, 60, 55)
HULL_D  = (25, 42, 38)
HULL_DD = (15, 28, 25)
HULL_O  = (6, 14, 12)        # outline / deepest shadow

# ── Portholes — pale gray-blue with white centers ────
PORT_W   = (235, 245, 250)
PORT_HI  = (165, 190, 200)
PORT_M   = (95, 120, 135)
PORT_D   = (45, 65, 80)

# ── Green tractor / scan beam ────────────────────────
BEAM_CORE = (215, 255, 215)
BEAM_HOT  = (145, 255, 155)
BEAM_BR   = (85, 235, 105)
BEAM_MID  = (50, 195, 75)
BEAM_D    = (30, 145, 55)
BEAM_DD   = (20, 95, 40)


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


def hover(frame):
    return int(round(math.sin(frame / TOTAL_FRAMES * TAU) * 2))


# ── DOME geometry (small red dome sitting on top, viewed from below) ──
# Looking up at the UFO, only the front-upper portion of the dome shows;
# the back of the rim curves up around it.
DCY_BASE = 64
DR = 13

# Lighting for dome (light from upper-right, like the reference)
_Lx, _Ly, _Lz = 0.42, 0.55, 0.72
_Lm = math.sqrt(_Lx * _Lx + _Ly * _Ly + _Lz * _Lz)
LX, LY, LZ = _Lx / _Lm, _Ly / _Lm, _Lz / _Lm


def draw_dome(put, frame):
    bob = hover(frame)
    cy_base = DCY_BASE + bob
    for y in range(cy_base - DR, cy_base + 1):
        for x in range(HCX - DR, HCX + DR + 1):
            u = (x - HCX) / DR
            v = (cy_base - y) / DR
            if v < 0: continue
            if u * u + v * v > 1.0: continue
            w = math.sqrt(max(0, 1 - u * u - v * v))
            diff = max(0, u * LX + v * LY + w * LZ)
            glow = 0.55 + 0.12 * w
            i = diff * 0.50 + glow * 0.45
            radial = math.sqrt(u * u + v * v)
            if   radial > 0.95: i *= 0.25
            elif radial > 0.88: i *= 0.55
            elif radial > 0.78: i *= 0.78
            if   i > 0.94: col = DOME_CORE
            elif i > 0.80: col = DOME_HOT
            elif i > 0.65: col = DOME_BR
            elif i > 0.48: col = DOME_L
            elif i > 0.32: col = DOME_M
            elif i > 0.18: col = DOME_D
            else:          col = DOME_DEEP
            put(x, y, col)
    # Tiny specular streak on upper-right of dome
    for dx, dy, c in [(4, -9, DOME_CORE), (5, -8, DOME_CORE), (6, -7, DOME_HOT),
                      (7, -6, DOME_HOT), (7, -4, DOME_BR)]:
        put(HCX + dx, cy_base + dy, c)


# ── SAUCER body rows — viewed from below-front, rim back-arc curves up
# around the dome and the underside takes up most of the silhouette.
SAUCER_ROWS = [
    # Back arc of the rim peeking out behind/around the dome.
    # Drawn first, the dome will overwrite the central part — leaving
    # the "wings" of the back arc visible to the left/right of the dome.
    (53, 14, 'back_arc'),
    (54, 18, 'back_arc'),
    (55, 24, 'back_arc'),
    (56, 30, 'back_arc'),
    (57, 36, 'back_arc'),
    (58, 42, 'back_arc'),
    (59, 48, 'back_arc'),
    (60, 54, 'back_arc'),
    (61, 60, 'back_arc'),
    (62, 65, 'back_arc'),
    (63, 70, 'back_arc'),
    (64, 74, 'back_arc'),
    # Rim sides reaching widest
    (65, 77, 'rim_edge'),
    (66, 79, 'rim_edge'),
    (67, 81, 'rim_edge'),
    (68, 82, 'rim_edge'),
    # Porthole band (the front-bottom of the rim ellipse, where lights are)
    (69, 82, 'ports'),
    (70, 82, 'ports'),
    (71, 82, 'ports'),
    (72, 82, 'ports'),
    (73, 81, 'ports_bot'),
    # Front rim curving down (lower half of rim ellipse)
    (74, 79, 'rim_front'),
    (75, 76, 'rim_front'),
    (76, 72, 'rim_front'),
    (77, 67, 'rim_front'),
    # Underside (the big visible bowl)
    (78, 62, 'under_top'),
    (79, 57, 'under_top'),
    (80, 52, 'under'),
    (81, 47, 'under'),
    (82, 42, 'under'),
    (83, 37, 'under'),
    (84, 32, 'under'),
    (85, 27, 'under'),
    (86, 22, 'under'),
    (87, 17, 'under_end'),
    (88, 13, 'under_end'),
    (89, 9,  'emitter'),
    (90, 7,  'emitter'),
]


def shade_saucer(role, dx, hw):
    rel = dx / max(hw, 1)
    if abs(dx) == hw and hw > 3: return HULL_O
    if abs(dx) >= hw - 1 and hw > 6: return HULL_DD
    if role == 'back_arc':
        # Top of rim catches light from above
        if rel > 0.3:   return HULL_VL
        if rel > -0.2:  return HULL_HI
        if rel > -0.5:  return HULL_L
        return HULL_M
    if role == 'rim_edge':
        if rel > 0.4:   return HULL_VL
        if rel > -0.1:  return HULL_HI
        if rel > -0.5:  return HULL_L
        return HULL_M
    if role == 'ports':
        # Background for portholes — mid hull; lights drawn on top
        if rel > 0.4:   return HULL_M
        if rel > -0.4:  return HULL_D
        return HULL_DD
    if role == 'ports_bot':
        # Thin seam below porthole band
        return HULL_O
    if role == 'rim_front':
        # In shadow — we see the underside of the front rim
        if rel > 0.3:   return HULL_D
        if rel > -0.3:  return HULL_DD
        return HULL_O
    if role == 'under_top':
        # Just below the rim — darkest shadow band
        if rel > 0.3:   return HULL_DD
        if rel > -0.3:  return HULL_O
        return HULL_O
    if role == 'under':
        # Curved underside in shadow
        if rel > 0.4:   return HULL_DD
        if rel > -0.4:  return HULL_O
        return HULL_O
    if role == 'under_end':
        return HULL_O
    if role == 'emitter':
        # Emitter point gets overwritten by green glow
        return HULL_O
    return HULL_M


def draw_saucer(put, frame):
    bob = hover(frame)
    for y, hw, role in SAUCER_ROWS:
        ys = y + bob
        for dx in range(-hw, hw + 1):
            put(HCX + dx, ys, shade_saucer(role, dx, hw))

    # ── Porthole row — pale gray-blue lights along the rim arc ─
    blink_t = (frame / TOTAL_FRAMES) % 1.0
    n_ports = 9
    rim_rx = 73
    rim_cy = 71 + bob
    rim_ry = 2  # subtle vertical perspective curve
    for i in range(n_ports):
        theta = math.pi * (i + 0.5) / n_ports - math.pi / 2
        px = HCX + int(round(rim_rx * math.sin(theta)))
        py = rim_cy + int(round(rim_ry * math.cos(theta)))
        phase = (blink_t + i * 0.11) % 1.0
        bright = 0.65 + 0.35 * math.sin(phase * TAU)
        if bright > 0.8:
            inner, outer = PORT_W, PORT_HI
        elif bright > 0.5:
            inner, outer = PORT_HI, PORT_M
        else:
            inner, outer = PORT_M, PORT_D
        put(px, py, inner)
        put(px + 1, py, outer)
        put(px, py + 1, outer)
        put(px + 1, py + 1, PORT_D)

    # Bright greenish emitter glow at the bottom-center of the underside
    pulse = 0.85 + 0.15 * math.sin(frame / TOTAL_FRAMES * TAU * 3)
    eg_cx, eg_cy = HCX, 90 + bob
    for dy in range(-3, 4):
        for dx in range(-6, 7):
            d = math.sqrt(dx * dx + (dy * 1.6) ** 2)
            if d > 5.5: continue
            edge = (1.0 - d / 5.5) * pulse
            if   edge > 0.85: col = BEAM_CORE
            elif edge > 0.55: col = BEAM_HOT
            elif edge > 0.30: col = BEAM_BR
            else:             col = BEAM_MID
            a = int(255 * max(0, edge))
            if a > 0: put(eg_cx + dx, eg_cy + dy, col, a=a)


def draw_beam(put, frame):
    """Wide green tractor beam — continuous, glowing, soft-edged."""
    bob = hover(frame)
    TOP = 91 + bob
    BOT = 348
    HW_TOP = 8
    HW_BOT = 64
    max_h = BOT - TOP

    pulse = 0.88 + 0.12 * math.sin(frame / TOTAL_FRAMES * TAU * 3)

    for y in range(TOP, BOT + 1):
        rel = (y - TOP) / max_h
        hw = HW_TOP + rel * (HW_BOT - HW_TOP)
        for dx in range(-int(hw) - 2, int(hw) + 3):
            u = dx / hw
            if abs(u) > 1.08: continue
            edge = 1.0 - min(1.0, abs(u) ** 1.5)
            vfade = 1.0 - rel * 0.40
            a_base = edge * vfade * pulse
            if abs(u) < 0.22:
                col = BEAM_CORE; alpha = int(235 * a_base)
            elif abs(u) < 0.48:
                col = BEAM_HOT;  alpha = int(195 * a_base)
            elif abs(u) < 0.75:
                col = BEAM_BR;   alpha = int(150 * a_base)
            elif abs(u) < 1.0:
                col = BEAM_MID;  alpha = int(95 * a_base)
            else:
                col = BEAM_D;    alpha = int(55 * a_base)
            put(HCX + dx, y, col, a=min(255, max(0, alpha)))

    # Subtle inner glow particles drifting downward
    n_pts = 12
    for i in range(n_pts):
        rng  = ((math.sin(i * 12.9898 + 78.233) * 43758.5453) % 1 + 1) % 1
        rng2 = ((math.sin(i * 9.7777 + 22.111) * 12345.6789) % 1 + 1) % 1
        prog = ((frame * 1.5 + i * (TOTAL_FRAMES / n_pts)) % TOTAL_FRAMES) / TOTAL_FRAMES
        py = TOP + prog * max_h
        rel_y = (py - TOP) / max_h
        hw_here = HW_TOP + rel_y * (HW_BOT - HW_TOP)
        x_off = (rng - 0.5) * 1.4 * hw_here
        px = HCX + int(round(x_off))
        a = int(200 * (1 - rel_y * 0.6))
        col = BEAM_CORE if rng2 > 0.5 else BEAM_HOT
        put(px, int(py), col, a=a)
        put(px, int(py) + 1, BEAM_BR, a=a // 2)

    # Soft floor splash
    splash_hw = HW_BOT + 6
    for dy in range(0, 4):
        for dx in range(-splash_hw - dy * 2, splash_hw + dy * 2 + 1):
            d = math.sqrt(dx * dx + (dy * 2.5) ** 2)
            if d > splash_hw + dy * 2: continue
            fade = 1.0 - d / (splash_hw + dy * 2)
            a = int(110 * fade * (1.0 - dy / 5))
            put(HCX + dx, BOT + dy, BEAM_HOT, a=a)


def build_frame(frame, layers=frozenset({'ufo', 'beam'})):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    put = make_put(img.load())
    if 'beam' in layers:
        draw_beam(put, frame)
    if 'ufo' in layers:
        draw_saucer(put, frame)
        draw_dome(put, frame)   # dome drawn LAST so it covers the back-arc center
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
