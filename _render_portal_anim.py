#!/usr/bin/env python3
"""Render the animated portal as a looping GIF (mirrors the React HTML animation)."""
import os
from PIL import Image

# Canvas is bigger than the portal so the burst particles can travel.
# Portal proper is built in the original 64x128 grid then composited into
# the larger canvas (192x256) at offset (64, 64).
PORTAL_W, PORTAL_H = 64, 128
W, H, SCALE, FRAMES, FPS = 192, 256, 4, 36, 12
COL_OFF, ROW_OFF = (W - PORTAL_W) // 2, (H - PORTAL_H) // 2

PALETTE = [
    (0, 0, 0, 0),       # transparent
    (0, 0, 0),
    (23, 15, 38),
    (52, 30, 84),
    (106, 53, 122),
    (255, 89, 179),
    (78, 226, 236),
    (162, 240, 117),
    (255, 217, 71),
    (255, 246, 204),
]


def build(frame):
    # Portal grid (64x128) — every line of the existing build code below
    # references these dims, no changes needed inside the build.
    g = [[0] * PORTAL_W for _ in range(PORTAL_H)]
    def s(r, c, v):
        if 0 <= r < PORTAL_H and 0 <= c < PORTAL_W:
            g[r][c] = v
    def f(r1, c1, r2, c2, v):
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                s(r, c, v)

    # Void
    f(16, 19, 115, 44, 1)

    # Swirling vortex inside the doorway: 3 spiral arms, twisted by depth,
    # rotating over the loop. Same 3 cool colours (cream/cyan/plum).
    import math as _math
    VCX, VCY = 32, 65
    HALF_W, HALF_H = 12.5, 49.5
    N_ARMS = 3
    TWIST = 5
    t = frame / FRAMES
    rotation = t * 2 * _math.pi
    TAU = 2 * _math.pi

    for r in range(16, 116):
        for c in range(19, 45):
            dy = (r - VCY) / HALF_H
            dx = (c - VCX) / HALF_W
            d = _math.sqrt(dx * dx + dy * dy)
            if d < 0.10:
                s(r, c, 9)
                continue
            theta = _math.atan2(dy, dx)
            arg = N_ARMS * theta + TWIST * d + rotation
            phase = ((arg / TAU) % 1 + 1) % 1
            if   phase < 0.34: color = 9
            elif phase < 0.67: color = 6
            else:              color = 3
            s(r, c, color)

    tw = frame % 3
    if tw == 0: s(VCY - 1, VCX, 6)
    if tw == 1: s(VCY, VCX + 1, 6)
    if tw == 2: s(VCY + 1, VCX, 6)

    # Rim
    f(14, 17, 15, 46, 5)
    f(14, 17, 115, 18, 5)
    f(14, 45, 115, 46, 5)
    # Pillars
    for r in range(14, 116):
        if r <= 24:    p = [2,3,3,4,4,7,7,7,8,8,8,9,9]
        elif r <= 50:  p = [2,3,3,4,4,4,7,7,7,8,8,9,8]
        elif r <= 75:  p = [2,3,3,3,4,4,7,7,7,7,8,8,7]
        elif r <= 100: p = [2,3,3,3,4,4,4,4,7,7,7,4,4]
        else:          p = [2,2,3,3,3,4,4,4,4,3,3,3,3]
        for i in range(13):
            s(r, 4 + i, p[i])
            s(r, 47 + i, p[12 - i])

    # Pillar pulses (animated cream travelling down inner edge)
    pulse_y1 = 14 + ((frame * 4) % 104)
    pulse_y2 = 14 + ((frame * 4 + 52) % 104)
    for py in (pulse_y1, pulse_y2):
        if 14 <= py <= 113:
            if g[py][15]: s(py, 15, 9)
            if g[py][16]: s(py, 16, 9)
            if g[py][47]: s(py, 47, 9)
            if g[py][48]: s(py, 48, 9)

    # Crystals (animated pulse)
    crystal_shapes = [
        [(60,[0,0,0,6,0,0,0]),(61,[0,0,6,6,6,0,0]),(62,[0,6,6,6,6,6,0]),(63,[6,6,6,6,6,6,6]),
         (64,[6,6,9,9,9,6,6]),(65,[6,9,9,9,9,9,6]),(66,[6,6,9,9,9,6,6]),(67,[6,6,6,6,6,6,6]),
         (68,[0,6,6,6,6,6,0]),(69,[0,0,6,6,6,0,0]),(70,[0,0,0,6,0,0,0])],
        [(60,[0,0,0,6,0,0,0]),(61,[0,0,6,6,6,0,0]),(62,[0,6,6,9,6,6,0]),(63,[6,6,9,9,9,6,6]),
         (64,[6,9,9,9,9,9,6]),(65,[9,9,9,9,9,9,9]),(66,[6,9,9,9,9,9,6]),(67,[6,6,9,9,9,6,6]),
         (68,[0,6,6,9,6,6,0]),(69,[0,0,6,6,6,0,0]),(70,[0,0,0,6,0,0,0])],
        [(60,[0,0,0,9,0,0,0]),(61,[0,0,6,9,6,0,0]),(62,[0,6,9,9,9,6,0]),(63,[6,9,9,9,9,9,6]),
         (64,[9,9,9,9,9,9,9]),(65,[9,9,9,9,9,9,9]),(66,[9,9,9,9,9,9,9]),(67,[6,9,9,9,9,9,6]),
         (68,[0,6,9,9,9,6,0]),(69,[0,0,6,9,6,0,0]),(70,[0,0,0,9,0,0,0])],
        [(60,[0,0,0,6,0,0,0]),(61,[0,0,6,6,6,0,0]),(62,[0,6,6,9,6,6,0]),(63,[6,6,9,9,9,6,6]),
         (64,[6,9,9,9,9,9,6]),(65,[9,9,9,9,9,9,9]),(66,[6,9,9,9,9,9,6]),(67,[6,6,9,9,9,6,6]),
         (68,[0,6,6,9,6,6,0]),(69,[0,0,6,6,6,0,0]),(70,[0,0,0,6,0,0,0])],
    ]
    crystal = crystal_shapes[(frame // 4) % 4]
    for r, row in crystal:
        for c in range(len(row)):
            if row[c]: s(r, c, row[c])
            if row[c]: s(r, 63 - c, row[c])

    # Crown
    f(5, 4, 13, 59, 3)
    f(5, 4, 5, 59, 2)
    f(6, 4, 13, 4, 2)
    f(6, 59, 13, 59, 2)
    f(13, 4, 13, 59, 2)
    for r in range(7, 12):
        for c in range(6, 58):
            if (r * 3 + c) % 9 == 0: g[r][c] = 4
    for r, c in [(7,12),(7,51),(8,18),(8,45),(9,22),(9,41),(10,9),(10,54),(11,15),(11,48),(8,30),(8,33),(10,27),(10,36)]:
        s(r, c, 8)
    for r, c in [(7,8),(7,55),(8,14),(8,49),(9,18),(9,45),(10,11),(10,52),(6,22),(6,41)]:
        s(r, c, 9)
    # Blinking stars
    for r, c, v in [(7,15,9),(8,22,9),(9,33,8),(10,41,9),(11,28,8),(7,48,9),(6,30,9),(6,38,8)]:
        if (frame + r * 5 + c * 3) % 9 < 5: s(r, c, v)

    # Corner flares
    f(4, 0, 4, 7, 3); s(4,0,2); s(4,7,2)
    f(3, 1, 3, 6, 3); s(3,1,2); s(3,6,2)
    f(2, 2, 2, 5, 3); s(2,2,2); s(2,5,2)
    f(1, 3, 1, 4, 2)
    s(3,3,8); s(3,4,8); s(2,3,9); s(2,4,9)
    f(4, 56, 4, 63, 3); s(4,56,2); s(4,63,2)
    f(3, 57, 3, 62, 3); s(3,57,2); s(3,62,2)
    f(2, 58, 2, 61, 3); s(2,58,2); s(2,61,2)
    f(1, 59, 1, 60, 2)
    s(3,59,8); s(3,60,8); s(2,59,9); s(2,60,9)

    # Flame (3-state flicker)
    fp = frame % 3
    if fp == 0:
        s(0,31,9); s(0,32,9)
        s(1,30,8); s(1,31,9); s(1,32,9); s(1,33,8)
        f(2,29,2,34,8); s(2,30,9); s(2,31,9); s(2,32,9); s(2,33,9)
        f(3,28,3,35,8); s(3,30,9); s(3,31,9); s(3,32,9); s(3,33,9)
        f(4,27,4,36,8); s(4,30,9); s(4,31,9); s(4,32,9); s(4,33,9)
    elif fp == 1:
        s(0,30,9); s(0,31,9)
        s(1,29,8); s(1,30,9); s(1,31,9); s(1,32,8)
        f(2,28,2,33,8); s(2,29,9); s(2,30,9); s(2,31,9); s(2,32,9)
        f(3,27,3,34,8); s(3,28,9); s(3,29,9); s(3,30,9); s(3,31,9); s(3,32,9)
        f(4,27,4,36,8); s(4,28,9); s(4,29,9); s(4,30,9); s(4,31,9); s(4,32,9)
    else:
        s(0,32,9); s(0,33,9)
        s(1,31,8); s(1,32,9); s(1,33,9); s(1,34,8)
        f(2,30,2,35,8); s(2,31,9); s(2,32,9); s(2,33,9); s(2,34,9)
        f(3,29,3,36,8); s(3,31,9); s(3,32,9); s(3,33,9); s(3,34,9); s(3,35,9)
        f(4,27,4,36,8); s(4,31,9); s(4,32,9); s(4,33,9); s(4,34,9); s(4,35,9)

    # Pedestal
    def pe(r):
        if r == 116: return 0
        if r <= 118: return 1
        if r <= 120: return 2
        if r <= 122: return 3
        if r <= 124: return 4
        return 5
    for r in range(116, 128):
        ext = pe(r)
        lL = max(0, 4 - ext); lR = 16
        for c in range(lL, lR + 1):
            s(r, c, 2 if c == lL or c == lR else 3)
        rL = 47; rR = min(W - 1, 59 + ext)
        for c in range(rL, rR + 1):
            s(r, c, 2 if c == rL or c == rR else 3)
    f(116, 5, 116, 15, 4)
    f(116, 48, 116, 58, 4)

    # Gold pool
    f(120, 22, 121, 41, 8)
    f(122, 20, 123, 43, 8)
    f(124, 19, 127, 44, 8)
    s(122,19,4); s(122,44,4); s(124,19,4); s(124,44,4)
    # Ripples
    for w in range(2):
        wave_pos = ((frame * 2 + w * 18) % 30) - 5
        for dx in range(3):
            x = 19 + wave_pos + dx
            if 19 <= x <= 44:
                s(125, x, 9)
                if dx == 1: s(126, x, 9)
    s(127, 28, 9); s(127, 35, 9)

    # Drips at pillar bases
    f(116, 8, 117, 12, 8)
    f(116, 51, 117, 55, 8)
    s(116,10,9); s(117,10,9); s(116,53,9); s(117,53,9)
    f(118, 9, 118, 11, 8); f(118, 52, 118, 54, 8)
    # Falling drops
    dropL = frame % 8
    if 1 <= dropL <= 5:
        s(118 + dropL, 10, 8)
        if dropL >= 3: s(118 + dropL - 1, 10, 4)
    dropR = (frame + 4) % 8
    if 1 <= dropR <= 5:
        s(118 + dropR, 53, 8)
        if dropR >= 3: s(118 + dropR - 1, 53, 4)

    # Rim energy pulses
    for p in range(3):
        oL = ((frame * 3) + p * 36) % 108
        yL = 14 + oL
        if 14 <= yL <= 113:
            s(yL, 17, 9)
            if yL + 1 <= 115: s(yL + 1, 17, 8)
        oR = ((frame * 3) + p * 36 + 18) % 108
        yR = 14 + oR
        if 14 <= yR <= 113:
            s(yR, 46, 9)
            if yR + 1 <= 115: s(yR + 1, 46, 8)

    # Twinkling sparkles
    for r, c, v in [
        (20,1,5),(21,2,5),(33,2,8),(45,1,6),
        (82,2,8),(83,3,8),(95,1,5),(105,2,6),
        (8,2,8),(13,1,6),(28,0,5),
        (25,61,6),(26,62,6),(40,62,8),(52,61,5),
        (75,60,5),(76,61,5),(90,62,8),(102,60,6),
        (8,61,5),(15,62,8),(35,63,6),
        (2,14,8),(3,22,6),(2,44,6),(3,50,8),(0,10,5),(0,53,5),
        (58,0,5),(72,0,8),(58,63,5),(72,63,8),
    ]:
        if (frame + r * 7 + c * 11) % 12 < 8:
            if g[r][c] == 0: s(r, c, v)

    # ── Composite portal (64x128) → bigger canvas (192x256) ──
    big = [[0] * W for _ in range(H)]
    for r in range(PORTAL_H):
        for c in range(PORTAL_W):
            v = g[r][c]
            if v: big[r + ROW_OFF][c + COL_OFF] = v
    def sb(r, c, v):
        if 0 <= r < H and 0 <= c < W:
            big[r][c] = v

    # ── 32 particles, forward bias, wider cone, 3-stamp trails ──
    VCX = 32 + COL_OFF       # portal centre in canvas coords
    VCY = 65 + ROW_OFF
    NUM_PARTICLES = 32
    t = frame / FRAMES
    GOLDEN = 2.39996
    FORWARD = _math.pi / 2     # downward — out of the doorway, toward the camera
    CONE = 0.85                # forward bias + wider arc
    MAX_DIST = 105
    TAU = 2 * _math.pi
    TRAIL_COLORS = [0, 8, 6, 3]   # gold, cyan, plum behind the head

    def stamp(cx, cy, sz, col):
        if sz < 0: return
        for dr in range(-sz, sz + 1):
            for dc in range(-sz, sz + 1):
                if abs(dr) + abs(dc) <= sz:
                    sb(cy + dr, cx + dc, col)

    for i in range(NUM_PARTICLES):
        phase = (t + i / NUM_PARTICLES) % 1
        if phase < 0.05: continue
        raw = (i * GOLDEN + t * TAU * 0.25) % TAU
        off = raw - FORWARD
        while off >  _math.pi: off -= TAU
        while off < -_math.pi: off += TAU
        angle = FORWARD + off * CONE
        dist = (phase ** 0.85) * MAX_DIST
        px = round(VCX + _math.cos(angle) * dist)
        py = round(VCY + _math.sin(angle) * dist)
        if   phase < 0.16: size = 0
        elif phase < 0.36: size = 1
        elif phase < 0.62: size = 2
        elif phase < 0.86: size = 3
        else:              size = 2
        if   phase < 0.22: color = 6
        elif phase < 0.46: color = 9
        elif phase < 0.70: color = 8
        elif phase < 0.92: color = 5
        else:              color = 4
        # Trails first so the head overlays on top
        for trail in (3, 2, 1):
            tp = phase - trail * 0.022
            if tp < 0.02: continue
            td = (tp ** 0.85) * MAX_DIST
            tpx = round(VCX + _math.cos(angle) * td)
            tpy = round(VCY + _math.sin(angle) * td)
            tsz = max(0, size - trail)
            stamp(tpx, tpy, tsz, TRAIL_COLORS[trail])
        stamp(px, py, size, color)
        if size >= 2: sb(py, px, 9)

    return big


# Build palette for GIF
PAL_LIST = []
for c in PALETTE:
    PAL_LIST.extend(c[:3])
PAL_LIST.extend([0] * (256 * 3 - len(PAL_LIST)))

frames = []
for fr in range(FRAMES):
    g = build(fr)
    img = Image.new('P', (W, H), 0)
    img.putpalette(PAL_LIST)
    px = img.load()
    for r in range(H):
        for c in range(W):
            px[c, r] = g[r][c]
    # Upscale with NEAREST
    big = img.resize((W * SCALE, H * SCALE), Image.NEAREST)
    big.info['transparency'] = 0
    frames.append(big)

os.makedirs('output', exist_ok=True)
frames[0].save(
    'output/magical_portal_animated.gif',
    save_all=True,
    append_images=frames[1:],
    duration=int(1000 / FPS),
    loop=0,
    transparency=0,
    disposal=2,
    optimize=False,
)
print('wrote output/magical_portal_animated.gif',
      (W * SCALE, H * SCALE), FRAMES, 'frames')
