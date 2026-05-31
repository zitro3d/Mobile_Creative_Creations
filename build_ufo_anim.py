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

# Cow palette
COW_W = (245, 240, 230); COW_S = (180, 165, 140); COW_O = (50, 35, 25)
COW_PINK = (220, 130, 130)

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


def draw_tractor_beam(put, frame):
    """Translucent downward beam with particles streaming UP (suction)."""
    BEAM_TOP_Y = 207
    BEAM_BOT_Y = 332
    BEAM_TOP_HW = 12
    BEAM_BOT_HW = 44
    beam_h = BEAM_BOT_Y - BEAM_TOP_Y

    # Pulse intensity
    pulse = 0.85 + 0.15 * math.sin(frame / TOTAL_FRAMES * TAU * 2)

    # Body of the beam (semi-transparent cyan-white gradient)
    for y in range(BEAM_TOP_Y, BEAM_BOT_Y + 1):
        rel_y = (y - BEAM_TOP_Y) / beam_h
        hw = BEAM_TOP_HW + rel_y * (BEAM_BOT_HW - BEAM_TOP_HW)
        for dx in range(-int(hw) - 1, int(hw) + 2):
            u = dx / hw
            if abs(u) > 1.05: continue
            # Edge alpha falls off, brighter center
            edge = 1.0 - min(1.0, abs(u) ** 1.4)
            # Vertical fade: stays mostly bright with subtle dim near bottom
            vfade = 1.0 - rel_y * 0.30
            a_base = edge * vfade * pulse
            # Inner core color (brighter near center)
            if abs(u) < 0.18:
                col = PLASMA_HOT
                alpha = int(220 * a_base)
            elif abs(u) < 0.45:
                col = PLASMA_BRIGHT
                alpha = int(170 * a_base)
            elif abs(u) < 0.75:
                col = PLASMA_LIGHT
                alpha = int(120 * a_base)
            else:
                col = PLASMA_MID
                alpha = int(70 * a_base)
            put(HCX + dx, y, col, a=alpha)

    # Inner "swirl" lines that move upward — gives suction feel
    N_LINES = 4
    for li in range(N_LINES):
        # Each line at a horizontal offset (relative to local hw at that y)
        offset_frac = (li / N_LINES) - 0.5 + 0.125  # spread across beam
        line_phase = (frame * 2 + li * 18) % TOTAL_FRAMES
        # Snake the line slightly as it moves
        for y in range(BEAM_TOP_Y, BEAM_BOT_Y + 1):
            rel_y = (y - BEAM_TOP_Y) / beam_h
            hw = BEAM_TOP_HW + rel_y * (BEAM_BOT_HW - BEAM_TOP_HW)
            # Vertical scroll — visible only on certain rows
            scroll_y = (y - BEAM_TOP_Y - line_phase * (beam_h / TOTAL_FRAMES) * 3) % beam_h
            if scroll_y > 6: continue
            wob = math.sin((y / 8.0) + frame / TOTAL_FRAMES * TAU) * 0.08
            dx = int(round((offset_frac + wob) * hw * 1.6))
            a = int(180 * (1 - scroll_y / 6.0))
            put(HCX + dx, y, PLASMA_HOT, a=a)

    # Upward-streaming bright particles (the "suction" effect)
    N_PART = 24
    for i in range(N_PART):
        # Pseudo-random horizontal offset within beam at this frame's row
        rng = (math.sin(i * 12.9898 + 78.233) * 43758.5453) % 1.0
        rng2 = (math.sin(i * 9.7777 + 22.111) * 12345.6789) % 1.0
        # Y moves UPWARD over time (frame +): subtract from bottom
        progress = ((frame * 2.5 + i * (TOTAL_FRAMES / N_PART)) % TOTAL_FRAMES) / TOTAL_FRAMES
        py = BEAM_BOT_Y - progress * beam_h
        rel_y = (py - BEAM_TOP_Y) / beam_h
        if rel_y < 0 or rel_y > 1: continue
        hw = BEAM_TOP_HW + rel_y * (BEAM_BOT_HW - BEAM_TOP_HW)
        # Sit at fraction of hw, slight horizontal drift toward center as it rises
        x_offset = (rng - 0.5) * 2 * hw * (0.85 - 0.5 * (1 - rel_y))
        px = HCX + int(round(x_offset))
        # Brighter near the top of its trajectory
        a = int(245 * (0.4 + 0.6 * (1 - rel_y)))
        col = PLASMA_SHINE if rng2 > 0.6 else PLASMA_HOT
        put(px, int(py), col, a=a)
        # Trailing dim pixel below
        put(px, int(py) + 1, PLASMA_BRIGHT, a=a // 2)


# Cow sprite (22 wide × 14 tall). Legend:
#   #  white body
#   .  black spot
#   O  black outline
#   P  pink udder
#   e  black eye
#   p  pink ear inside
COW = [
    "....OO..........OO....",
    "...OppO........OppO...",
    "...O##O........O##O...",
    "..O####OOOOOOOO####O..",
    ".O####OO########..#O..",
    "O###eOO############OPP",
    "O####O############O.PP",
    "O##.#O##.########O..PP",
    "O##############O.....P",
    "O##.#####.##O.........",
    "OO##OO#OO#OO..........",
    ".O##O.O##O.O##O.......",
    ".O##O.O##O.O##O.......",
    "..OO...OO...OO........",
]


def draw_cow(put, frame):
    """A cow being lifted up by the beam — bobs gently and rises slightly."""
    bob = int(round(math.sin(frame / TOTAL_FRAMES * TAU * 2) * 1.5))
    rise = int(round(math.sin(frame / TOTAL_FRAMES * TAU) * 2))
    cw = len(COW[0])
    cx = HCX
    cy_top = 318 + bob - rise
    for dy, row in enumerate(COW):
        for dx, ch in enumerate(row):
            x = cx - cw // 2 + dx
            y = cy_top + dy
            if   ch == '#': put(x, y, COW_W)
            elif ch == '.': put(x, y, COW_O)
            elif ch == 'O': put(x, y, COW_O)
            elif ch == 'P': put(x, y, COW_PINK)
            elif ch == 'p': put(x, y, COW_PINK)
            elif ch == 'e': put(x, y, COW_O)


def build_frame(frame, transparent_bg=True):
    bg = (0, 0, 0, 0) if transparent_bg else (4, 4, 10, 255)
    img = Image.new('RGBA', (W, H), bg)
    PX = img.load()
    put = make_putter(PX)

    # Tractor beam goes FIRST so other things sit on top of it visually
    draw_tractor_beam(put, frame)
    # Cow at the bottom (drawn over the beam)
    draw_cow(put, frame)
    # Saucer hull and disc
    draw_saucer_static(put)
    # Rotating lights and blinking windows
    draw_rotating_lights(put, frame)
    draw_cabin_windows(put, frame)
    # Dome
    draw_dome_static(put)
    draw_dome_slits(put, frame)
    # Plasma plume at the emission origin
    draw_plume(put, frame)
    return img


def main():
    os.makedirs('output', exist_ok=True)
    os.makedirs('output/ufo_anim_frames', exist_ok=True)

    # Render all frames
    frames = []
    for f in range(TOTAL_FRAMES):
        img = build_frame(f, transparent_bg=True)
        big = img.resize((W * SCALE, H * SCALE), Image.NEAREST)
        big.save(f'output/ufo_anim_frames/frame_{f:03d}.png')
        frames.append(big)
        if f % 12 == 0:
            print(f'  rendered frame {f}/{TOTAL_FRAMES}')

    # Animated GIF (1-bit transparency — beam will alpha-clip but still reads)
    duration_ms = int(round(1000 / FPS))
    # Convert each frame to a palette with transparency
    gif_frames = []
    for f in frames:
        # PIL.Image.quantize handles this; ensure transparent pixels stay transparent
        q = f.convert('RGBA').quantize(method=Image.FASTOCTREE, dither=Image.NONE)
        gif_frames.append(q)
    gif_frames[0].save(
        'output/ufo_animated.gif',
        save_all=True,
        append_images=gif_frames[1:],
        duration=duration_ms,
        loop=0,
        disposal=2,
        transparency=0,
        optimize=False,
    )
    print('wrote output/ufo_animated.gif')

    # Save a stills sheet for previewing (3 frames in a row)
    stills = [frames[0], frames[TOTAL_FRAMES // 3], frames[2 * TOTAL_FRAMES // 3]]
    sheet = Image.new('RGBA', (W * SCALE * 3, H * SCALE), (32, 32, 32, 255))
    for i, s in enumerate(stills):
        sheet.paste(s, (i * W * SCALE, 0), s)
    sheet.save('output/ufo_anim_preview.png')
    print('wrote output/ufo_anim_preview.png')


if __name__ == '__main__':
    main()
