#!/usr/bin/env python3
"""Animated UFO — spinning rim lights, blinking windows, pulsing dome interior,
breathing plasma jet, and a translucent tractor beam pulling a cow upward.

Logical 192x360 -> 3x NEAREST -> 576x1080. Transparent background.
72-frame seamless loop at 24 fps (3.0 s).

Outputs:
  output/ufo_animated.gif         (animated GIF with 1-bit transparency)
  output/ufo_anim_frames/         (individual RGBA frames, full alpha)
"""
import math, os
from PIL import Image

W, H, SCALE = 192, 360, 3
TOTAL_FRAMES = 72
FPS = 24
TAU = math.pi * 2

# ── Palette (mirrors build_ufo.py) ──────────────────
SHINE = (255, 252, 235); HOT = (255, 240, 175); BRIGHT = (255, 215, 110)
LIGHT = (252, 175, 70); ORANGE = (235, 125, 45); RED = (180, 70, 30)
DEEP_R = (110, 35, 18); DARK_R = (60, 18, 10)

DOME_SHINE = (240, 255, 255); DOME_HOT = (180, 240, 255); DOME_BRIGHT = (105, 215, 250)
DOME_LIGHT = (55, 175, 225); DOME_MID = (35, 130, 195); DOME_DARK = (25, 85, 155)
DOME_DEEP = (18, 55, 110); DOME_VOID = (12, 32, 70)

HULL_VL = (200, 215, 230); HULL_HI = (155, 175, 205); HULL_L = (115, 135, 168)
HULL_M = (78, 95, 128); HULL_D = (50, 62, 90); HULL_DD = (30, 38, 60)
HULL_O = (12, 16, 30)

WIN_O = (255, 145, 55); WIN_Y = (255, 220, 110); WIN_W = (255, 245, 200)

PLASMA_SHINE = (255, 255, 255); PLASMA_HOT = (200, 230, 255); PLASMA_BRIGHT = (130, 195, 255)
PLASMA_LIGHT = (140, 120, 255); PLASMA_MID = (190, 80, 240); PLASMA_DARK = (145, 35, 195)
PLASMA_DEEP = (90, 18, 130)

UCX = HCX = 96
DCX = UCX
DCY_BASE = 145
DR = 38

# Lighting vector (3D world coords)
Lx, Ly, Lz = 0.50, 0.55, 0.67
_Lmag = math.sqrt(Lx*Lx + Ly*Ly + Lz*Lz)
Lx /= _Lmag; Ly /= _Lmag; Lz /= _Lmag


def make_putter(PX):
    """Returns put(x, y, c, a=255) with alpha-over compositing onto PX."""
    def put(x, y, c, a=255):
        x = int(round(x)); y = int(round(y))
        if not (0 <= x < W and 0 <= y < H): return
        if a >= 255:
            PX[x, y] = (c[0], c[1], c[2], 255)
            return
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


# ── Saucer row data (33-row disc) ───────────────────
SAUCER_ROWS = [
    (146, 44, 'rim_flare'), (147, 58, 'rim_flare'), (148, 70, 'rim_flare'),
    (149, 80, 'rim_flare'), (150, 86, 'rim_top'), (151, 90, 'rim_top'),
    (152, 92, 'body_hi'),   (153, 93, 'body_hi'),  (154, 94, 'body_hi'),
    (155, 94, 'body_hi'),   (156, 94, 'seam'),     (157, 94, 'body_lights'),
    (158, 94, 'body_lights'),(159, 93, 'body_lights'),(160, 93, 'body_lights'),
    (161, 92, 'seam'),      (162, 91, 'body_dark'),(163, 90, 'body_dark'),
    (164, 88, 'body_dark'), (165, 86, 'body_dark'),(166, 84, 'body_dark'),
    (167, 82, 'seam'),      (168, 80, 'body_lights2'),(169, 78, 'body_lights2'),
    (170, 76, 'body_lights2'),(171, 73, 'body_lights2'),(172, 70, 'seam'),
    (173, 66, 'taper'),     (174, 61, 'taper'),    (175, 55, 'taper'),
    (176, 48, 'taper'),     (177, 40, 'taper'),    (178, 32, 'taper'),
    (179, 25, 'lower_panel'),(180, 21, 'lower_panel'),(181, 18, 'lower_lights'),
    (182, 16, 'lower_dark'),(183, 13, 'neck'),     (184, 11, 'neck'),
    (185, 9, 'neck'),       (186, 8, 'neck'),
]


def shade_saucer(role, dx, hw):
    rel = dx / max(hw, 1)
    if abs(dx) == hw and hw > 3: return HULL_O
    if abs(dx) >= hw - 1 and hw > 6: return HULL_DD
    if role == 'rim_flare':
        if rel > 0.4: return HULL_VL
        if rel > 0.0: return HULL_HI
        if rel > -0.4: return HULL_L
        return HULL_M
    if role == 'rim_top':
        if rel > 0.4: return HULL_VL
        if rel > -0.1: return HULL_HI
        if rel > -0.5: return HULL_L
        return HULL_M
    if role == 'body_hi':
        if rel > 0.3: return HULL_HI
        if rel > -0.2: return HULL_L
        if rel > -0.6: return HULL_M
        return HULL_D
    if role == 'seam': return HULL_O
    if role == 'body_lights':
        if rel > 0.4: return HULL_L
        if rel > -0.3: return HULL_M
        return HULL_D
    if role == 'body_lights2':
        if rel > 0.3: return HULL_M
        if rel > -0.3: return HULL_D
        return HULL_DD
    if role == 'body_dark':
        if rel > 0.3: return HULL_M
        if rel > -0.3: return HULL_D
        return HULL_DD
    if role == 'taper':
        if rel > 0.3: return HULL_M
        if rel > -0.3: return HULL_D
        return HULL_DD
    if role == 'lower_panel':
        if rel > 0.3: return HULL_L
        if rel > -0.3: return HULL_M
        return HULL_D
    if role == 'lower_lights': return HULL_M
    if role == 'lower_dark': return HULL_D
    if role == 'neck':
        if dx > 0: return HULL_M
        if dx > -2: return HULL_D
        return HULL_DD
    return HULL_M


def draw_saucer_static(put):
    for y, hw, role in SAUCER_ROWS:
        for dx in range(-hw, hw + 1):
            put(HCX + dx, y, shade_saucer(role, dx, hw))
    # External tapered neck below dict's neck (transitions into plume origin)
    for y in range(187, 193):
        hw = 4 if y < 191 else 6
        for dx in range(-hw, hw + 1):
            x = HCX + dx
            if abs(dx) == hw: col = HULL_O
            elif dx > 1:      col = HULL_M
            elif dx > -2:     col = HULL_D
            else:             col = HULL_DD
            put(x, y, col)


def draw_dome_static(put):
    for y in range(DCY_BASE - DR, DCY_BASE + 1):
        for x in range(DCX - DR, DCX + DR + 1):
            u = (x - DCX) / DR
            v = (DCY_BASE - y) / DR
            if v < 0: continue
            if u*u + v*v > 1.0: continue
            w = math.sqrt(max(0.0, 1.0 - u*u - v*v))
            diff = max(0.0, u*Lx + v*Ly + w*Lz)
            glow = 0.55 + 0.10 * w
            i = diff * 0.55 + glow * 0.40
            radial = math.sqrt(u*u + v*v)
            if   radial > 0.96: i *= 0.20
            elif radial > 0.90: i *= 0.50
            elif radial > 0.82: i *= 0.75
            if   i > 0.95: col = DOME_SHINE
            elif i > 0.82: col = DOME_HOT
            elif i > 0.68: col = DOME_BRIGHT
            elif i > 0.54: col = DOME_LIGHT
            elif i > 0.40: col = DOME_MID
            elif i > 0.25: col = DOME_DARK
            elif i > 0.10: col = DOME_DEEP
            else:          col = DOME_VOID
            put(x, y, col)
    # Diagonal specular streak (static)
    streak = [
        (DCX+12, DCY_BASE-34, DOME_HOT), (DCX+13, DCY_BASE-33, DOME_SHINE),
        (DCX+14, DCY_BASE-32, DOME_SHINE),(DCX+15, DCY_BASE-31, DOME_SHINE),
        (DCX+16, DCY_BASE-30, DOME_SHINE),(DCX+17, DCY_BASE-28, DOME_SHINE),
        (DCX+18, DCY_BASE-26, DOME_SHINE),(DCX+19, DCY_BASE-24, DOME_HOT),
        (DCX+20, DCY_BASE-22, DOME_HOT), (DCX+21, DCY_BASE-19, DOME_HOT),
        (DCX+22, DCY_BASE-16, DOME_BRIGHT),(DCX+22, DCY_BASE-13, DOME_BRIGHT),
        (DCX+23, DCY_BASE-10, DOME_LIGHT),
    ]
    for x, y, c in streak:
        put(x, y, c)


def draw_dome_slits(put, frame):
    """Pulsing warm interior lights on the dome's left side."""
    slits = [
        (DCX-19, DCY_BASE-18, DCY_BASE-5, 0.0),
        (DCX-13, DCY_BASE-24, DCY_BASE-4, 0.33),
        (DCX-7,  DCY_BASE-28, DCY_BASE-3, 0.66),
    ]
    for sx, ys, ye, phase in slits:
        # Pulse: each slit has its own phase, completes 2 cycles per loop
        t = (frame / TOTAL_FRAMES + phase) % 1.0
        pulse = 0.55 + 0.45 * math.sin(t * TAU * 2)
        # Glow color depending on pulse strength
        if pulse > 0.85:    glow_col = WIN_W
        elif pulse > 0.55:  glow_col = WIN_Y
        else:                glow_col = WIN_O
        mid = (ys + ye) // 2
        for y in range(ys, ye + 1):
            put(sx, y, DOME_VOID)
            if mid - 2 <= y <= mid + 2:
                put(sx, y, glow_col)


def draw_rotating_lights(put, frame):
    """Scrolling rim lights — gives the saucer the feel of spinning."""
    phase = (frame / TOTAL_FRAMES) * TAU
    # Top-rim band (row 158-159), wide arc
    N_TOP = 28
    R_TOP = 90
    for i in range(N_TOP):
        theta = (i / N_TOP) * TAU
        alpha = theta + phase
        ca = math.cos(alpha)
        if ca <= 0.05: continue  # hidden behind disc
        sa = math.sin(alpha)
        x = HCX + int(round(R_TOP * sa))
        # Brightness: brighter when light is near front-center (ca close to 1)
        if   ca > 0.80: put(x, 158, WIN_W); put(x, 159, WIN_Y)
        elif ca > 0.55: put(x, 158, WIN_Y); put(x, 159, WIN_O)
        elif ca > 0.30: put(x, 158, WIN_O); put(x, 159, ORANGE)
        elif ca > 0.10: put(x, 158, ORANGE); put(x, 159, RED)
        else:           put(x, 158, RED)
    # Second band (row 169-170)
    N_MID = 20
    R_MID = 74
    for i in range(N_MID):
        theta = (i / N_MID) * TAU
        alpha = theta + phase  # same direction
        ca = math.cos(alpha)
        if ca <= 0.05: continue
        sa = math.sin(alpha)
        x = HCX + int(round(R_MID * sa))
        if   ca > 0.70: put(x, 169, WIN_Y); put(x, 170, WIN_O)
        elif ca > 0.40: put(x, 169, WIN_O); put(x, 170, ORANGE)
        elif ca > 0.15: put(x, 169, ORANGE); put(x, 170, RED)
        else:           put(x, 169, RED)
    # Lower panel small lights (row 181)
    N_LOW = 9
    R_LOW = 16
    for i in range(N_LOW):
        theta = (i / N_LOW) * TAU
        alpha = theta - phase * 1.5  # spins opposite, slightly faster
        ca = math.cos(alpha)
        if ca <= 0.05: continue
        sa = math.sin(alpha)
        x = HCX + int(round(R_LOW * sa))
        if   ca > 0.55: put(x, 181, WIN_Y)
        elif ca > 0.25: put(x, 181, WIN_O)
        else:           put(x, 181, ORANGE)


def draw_cabin_windows(put, frame):
    """Larger forward windows that blink in a sequence."""
    blink_t = (frame * 3) % TOTAL_FRAMES / TOTAL_FRAMES
    cabins = [(-44, 0.0), (-26, 0.2), (-10, 0.4), (10, 0.6), (26, 0.8), (44, 1.0)]
    for dxc, off in cabins:
        t = (blink_t + off) % 1.0
        # Blink: 75% on bright, 25% dim
        if t < 0.75:
            inner = WIN_W; outer = WIN_Y
        else:
            inner = WIN_O; outer = ORANGE
        x = HCX + dxc
        put(x, 158, inner); put(x + 1, 158, outer)
        put(x, 159, outer); put(x + 1, 159, WIN_O)


def draw_plume(put, frame):
    """Energy plume at the emission origin — pulses width and brightness."""
    breath = math.sin(frame / TOTAL_FRAMES * TAU)
    pulse = 0.92 + 0.18 * breath
    base_shape = [
        (193, 2), (194, 3), (195, 3), (196, 4), (197, 5),
        (198, 6), (199, 7), (200, 8), (201, 9), (202, 10),
        (203, 11), (204, 12), (205, 13), (206, 14),
    ]
    plume_top = base_shape[0][0]
    plume_bot = base_shape[-1][0]
    plume_h = plume_bot - plume_top
    for y, hw_base in base_shape:
        hw = max(1, int(round(hw_base * pulse)))
        rel_y = (y - plume_top) / plume_h
        for dx in range(-hw, hw + 1):
            u = dx / max(hw, 1)
            i = (1.0 - abs(u) * 0.60) * (1.0 - rel_y * 0.55) * pulse
            if   i > 0.88: col = PLASMA_SHINE
            elif i > 0.72: col = PLASMA_HOT
            elif i > 0.56: col = PLASMA_BRIGHT
            elif i > 0.42: col = PLASMA_LIGHT
            elif i > 0.28: col = PLASMA_MID
            elif i > 0.14: col = PLASMA_DARK
            else:          col = PLASMA_DEEP
            put(HCX + dx, y, col)


# Beam-cycle phase frames (72-frame loop):
#   [0, 14)  extend   — beam shoots down from nothing to full length
#   [14, 36) hold     — beam fully extended, suction particles streaming up
#   [36, 50) retract  — beam pulls back up; intense upward suction
#   [50, 72) pause    — beam gone, nothing visible at the emitter
BEAM_EXTEND_END  = 14
BEAM_HOLD_END    = 36
BEAM_RETRACT_END = 50


def beam_state(frame):
    """Return (length_frac, intensity, phase, suction_strength)."""
    if frame < BEAM_EXTEND_END:
        t = frame / BEAM_EXTEND_END
        t_eased = 1.0 - (1.0 - t) ** 2  # ease-out
        return (t_eased, 0.4 + 0.6 * t_eased, 'extend', 0.0)
    if frame < BEAM_HOLD_END:
        return (1.0, 1.0, 'hold', 0.7)
    if frame < BEAM_RETRACT_END:
        t = (frame - BEAM_HOLD_END) / (BEAM_RETRACT_END - BEAM_HOLD_END)
        t_eased = t * t  # ease-in (accelerating retraction)
        return (1.0 - t_eased, 1.0 - 0.2 * t_eased, 'retract', 1.6)
    return (0.0, 0.0, 'pause', 0.0)


def draw_tractor_beam(put, frame):
    """Translucent downward beam with upward suction particles.

    Cycles through extend → hold → retract → pause.  Always emanates from
    the saucer emitter point and expands at the same cone angle.
    """
    TOP = 207
    MAX_BOT = 332
    HW_TOP = 12
    MAX_HW_BOT = 44
    max_h = MAX_BOT - TOP

    length_frac, intensity, phase, suction = beam_state(frame)
    if length_frac <= 0.001 or intensity <= 0.001:
        return  # pause phase — emitter is quiet

    cur_bot = TOP + length_frac * max_h
    cur_bot_i = int(round(cur_bot))
    leading_y = cur_bot_i  # the moving edge of the beam

    pulse = 0.85 + 0.15 * math.sin(frame / TOTAL_FRAMES * TAU * 4)

    # Beam body
    for y in range(TOP, cur_bot_i + 1):
        rel_full = (y - TOP) / max_h            # for cone angle (constant)
        hw = HW_TOP + rel_full * (MAX_HW_BOT - HW_TOP)
        rel_local = (y - TOP) / max(cur_bot - TOP, 1)
        # Leading edge brightening (during extend especially) — a bright tip
        edge_boost = 0.0
        dist_from_edge = leading_y - y
        if dist_from_edge < 5:
            edge_boost = (1.0 - dist_from_edge / 5.0) * 0.4
        for dx in range(-int(hw) - 1, int(hw) + 2):
            u = dx / hw
            if abs(u) > 1.05: continue
            edge = 1.0 - min(1.0, abs(u) ** 1.4)
            vfade = 1.0 - rel_local * 0.30
            a_base = edge * vfade * pulse * intensity * (1.0 + edge_boost * (1.0 - abs(u) * 0.6))
            if abs(u) < 0.18:
                col = PLASMA_HOT;    alpha = int(220 * a_base)
            elif abs(u) < 0.45:
                col = PLASMA_BRIGHT; alpha = int(170 * a_base)
            elif abs(u) < 0.75:
                col = PLASMA_LIGHT;  alpha = int(120 * a_base)
            else:
                col = PLASMA_MID;    alpha = int(70 * a_base)
            put(HCX + dx, y, col, a=min(255, max(0, alpha)))

    # Inner upward-scrolling streak lines — speed up during retract
    line_speed = 3.0 if phase != 'retract' else 7.0
    N_LINES = 4
    for li in range(N_LINES):
        offset_frac = (li / N_LINES) - 0.5 + 0.125
        line_phase = (frame * 2 + li * 18) % TOTAL_FRAMES
        for y in range(TOP, cur_bot_i + 1):
            rel_full = (y - TOP) / max_h
            hw = HW_TOP + rel_full * (MAX_HW_BOT - HW_TOP)
            scroll_y = (y - TOP - line_phase * (max_h / TOTAL_FRAMES) * line_speed) % max_h
            if scroll_y > 6: continue
            wob = math.sin((y / 8.0) + frame / TOTAL_FRAMES * TAU) * 0.08
            dx = int(round((offset_frac + wob) * hw * 1.6))
            a = int(180 * (1 - scroll_y / 6.0) * intensity)
            put(HCX + dx, y, PLASMA_HOT, a=a)

    # Upward-streaming bright suction particles (only during hold/retract)
    if suction > 0.01:
        N_PART = 28
        speed_mult = 2.5 if phase == 'hold' else 6.0  # fast retract = vigorous suck
        for i in range(N_PART):
            rng  = (math.sin(i * 12.9898 + 78.233) * 43758.5453) % 1.0
            rng2 = (math.sin(i * 9.7777 + 22.111) * 12345.6789) % 1.0
            progress = ((frame * speed_mult + i * (TOTAL_FRAMES / N_PART)) % TOTAL_FRAMES) / TOTAL_FRAMES
            # Y moves upward from the current bottom edge to the top
            py = cur_bot - progress * (cur_bot - TOP)
            rel_y = (py - TOP) / max_h
            if rel_y < 0 or rel_y > 1: continue
            if py > cur_bot: continue  # don't draw past current beam edge
            hw = HW_TOP + rel_y * (MAX_HW_BOT - HW_TOP)
            x_offset = (rng - 0.5) * 2 * hw * (0.85 - 0.5 * (1 - rel_y))
            px = HCX + int(round(x_offset))
            a = int(245 * (0.4 + 0.6 * (1 - rel_y)) * suction)
            col = PLASMA_SHINE if rng2 > 0.6 else PLASMA_HOT
            put(px, int(py), col, a=min(255, a))
            put(px, int(py) + 1, PLASMA_BRIGHT, a=min(255, a // 2))


def build_frame(frame, layers=frozenset({'ufo', 'plume', 'beam'}), transparent_bg=True):
    bg = (0, 0, 0, 0) if transparent_bg else (4, 4, 10, 255)
    img = Image.new('RGBA', (W, H), bg)
    PX = img.load()
    put = make_putter(PX)

    # Beam first so UFO + plume sit on top of it when combined
    if 'beam' in layers:
        draw_tractor_beam(put, frame)
    if 'ufo' in layers:
        draw_saucer_static(put)
        draw_rotating_lights(put, frame)
        draw_cabin_windows(put, frame)
        draw_dome_static(put)
        draw_dome_slits(put, frame)
    if 'plume' in layers:
        draw_plume(put, frame)
    return img


def render_layer_gif(name, layers, save_frames=False):
    """Render the animation with only `layers` enabled and save an animated GIF."""
    frames = []
    for f in range(TOTAL_FRAMES):
        img = build_frame(f, layers=layers, transparent_bg=True)
        big = img.resize((W * SCALE, H * SCALE), Image.NEAREST)
        frames.append(big)
        if save_frames:
            frame_dir = f'output/ufo_layer_{name}_frames'
            os.makedirs(frame_dir, exist_ok=True)
            big.save(f'{frame_dir}/frame_{f:03d}.png')
    duration_ms = int(round(1000 / FPS))
    gif_frames = [f.convert('RGBA').quantize(method=Image.FASTOCTREE, dither=Image.NONE)
                  for f in frames]
    gif_frames[0].save(
        f'output/ufo_layer_{name}.gif',
        save_all=True,
        append_images=gif_frames[1:],
        duration=duration_ms,
        loop=0,
        disposal=2,
        transparency=0,
        optimize=False,
    )
    print(f'wrote output/ufo_layer_{name}.gif')
    return frames


def main():
    import shutil
    os.makedirs('output', exist_ok=True)

    # Combined ("all") animation — drives output/ufo_animated.gif and per-frame PNGs
    all_frames = render_layer_gif('all', {'ufo', 'plume', 'beam'})
    shutil.copy('output/ufo_layer_all.gif', 'output/ufo_animated.gif')
    print('wrote output/ufo_animated.gif (alias of layer_all)')

    # Per-layer animations
    ufo_frames   = render_layer_gif('ufo',   {'ufo'})
    plume_frames = render_layer_gif('plume', {'plume'})
    beam_frames  = render_layer_gif('beam',  {'beam'})

    # 4-up preview at a representative hold-phase frame
    hold_frame = (BEAM_EXTEND_END + BEAM_HOLD_END) // 2
    cols = [all_frames[hold_frame], ufo_frames[hold_frame],
            plume_frames[hold_frame], beam_frames[hold_frame]]
    sheet = Image.new('RGBA', (W * SCALE * len(cols), H * SCALE), (28, 28, 32, 255))
    for i, s in enumerate(cols):
        sheet.paste(s, (i * W * SCALE, 0), s)
    sheet.save('output/ufo_layer_preview.png')
    print('wrote output/ufo_layer_preview.png')


if __name__ == '__main__':
    main()
