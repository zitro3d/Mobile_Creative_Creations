#!/usr/bin/env python3
"""Outdoor wood/bamboo arch gateway — 128x128 RGBA, transparent inside.

A freestanding walk-through arch (garden-arch / torii variant), NOT a
fantasy portal: the opening is empty/transparent. U-shape — two straight
vertical legs joined by a WIDE ROUNDED top. 3/4 perspective: the thin
left leg is bare; the thicker right leg carries three plank/binding
details that stick out to the right. A horizontal crossbar lies flat
across the very top, with small round joint knobs where the arch meets
it. One palette color per pixel, no anti-aliasing.
"""
import os, math
from PIL import Image

W = H = 128
VIEW = 6                                  # preview upscale only

# ── Wood palette (3 tones) ────────────────────────────
WOOD_DARK  = (74, 48, 30)                 # shadow / outline
WOOD       = (138, 92, 52)                # body
WOOD_LIGHT = (186, 140, 92)              # lit edge (light from upper-left)

img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
PX = img.load()

def put(x, y, c):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H:
        PX[x, y] = c if len(c) == 4 else c + (255,)

def get(x, y):
    if 0 <= x < W and 0 <= y < H:
        return PX[x, y]
    return (0, 0, 0, 0)

def opaque(x, y):
    return get(x, y)[3] != 0

# ── Geometry ──────────────────────────────────────────
Y_S = 42          # springline: legs below, rounded crown above
Y_BOT = 122

# Straight legs (slight lean): (x_top@Y_S, x_bot@Y_BOT)
LO = (36, 30)     # left outer
LI = (48, 42)     # left inner
RI = (78, 84)     # right inner
RO = (94, 104)    # right outer  (thicker leg, widens downward)

def leg_x(pair, y):
    t = (y - Y_S) / (Y_BOT - Y_S)
    return pair[0] + (pair[1] - pair[0]) * t

# Rounded crown ellipses (endpoints meet the leg tops at Y_S)
CX_O, A_O, B_O = 65, 29, 29   # outer dome, apex y = Y_S - B_O = 13
CX_I, A_I, B_I = 63, 15, 16   # inner dome, apex y = Y_S - B_I = 26

def crown(cx, a, b, y):
    dy = Y_S - y
    if dy < 0 or dy > b:
        return None
    s = a * math.sqrt(max(0.0, 1 - (dy / b) ** 2))
    return (cx - s, cx + s)

def bounds(y):
    """Return (ol, il, ir, orr); il/ir None where the frame is solid."""
    if y >= Y_S:
        return (leg_x(LO, y), leg_x(LI, y), leg_x(RI, y), leg_x(RO, y))
    o = crown(CX_O, A_O, B_O, y)
    if o is None:
        return None
    i = crown(CX_I, A_I, B_I, y)
    if i is None:
        return (o[0], None, None, o[1])
    return (o[0], i[0], i[1], o[1])

# ── Fill the frame (legs + rounded crown), leave hole empty ─
for y in range(H):
    b = bounds(y)
    if b is None:
        continue
    ol, il, ir, orr = b
    a, d = int(math.floor(ol)), int(math.ceil(orr))
    if il is None:
        for x in range(a, d + 1):
            put(x, y, WOOD)
    else:
        le = int(round(il))
        re = int(round(ir))
        for x in range(a, le + 1):
            put(x, y, WOOD)
        for x in range(re, d + 1):
            put(x, y, WOOD)

# ── Three plank/binding details on the right leg (stick out) ─
def draw_plank(cy):
    ri = leg_x(RI, cy)
    ro = leg_x(RO, cy)
    sx = int(round(ri)) + 4               # bite into the leg
    ex = int(round(ro)) + 9               # protrude to the right
    span = max(1, ex - sx)
    half = 3
    for x in range(sx, ex + 1):
        f = (x - sx) / span
        drop = int(round(f * 2))          # slight downward tilt (perspective)
        h = half if f < 0.9 else half - 1
        for yy in range(cy - h + drop, cy + h + drop + 1):
            put(x, yy, WOOD)
    # shadow cast on the leg just below the plank
    for x in range(int(round(ri)), int(round(ro)) + 1):
        put(x, cy + half + 1, WOOD_DARK)
for cy in (60, 86, 112):
    draw_plank(cy)

# ── Crossbar laid flat across the very top ────────────
def draw_crossbar():
    x0, x1 = 45, 86
    yc, tilt, h = 9, 2, 3
    span = x1 - x0
    for x in range(x0, x1 + 1):
        f = (x - x0) / span
        cy = int(round(yc + f * tilt))
        hh = h if 0.07 < f < 0.93 else h - 1
        for yy in range(cy - hh, cy + hh + 1):
            put(x, yy, WOOD)
draw_crossbar()

# ── Round joint knobs where the arch meets the crossbar ─
def draw_knob(ox, oy, r):
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                put(ox + dx, oy + dy, WOOD)
draw_knob(48, 17, 4)                      # left shoulder knob
draw_knob(82, 16, 3)                      # right shoulder knob (smaller)

# ── Fill any fully-enclosed transparent pockets ───────
# Flood from the border over transparent pixels; whatever it can't reach
# is an enclosed hole (the big walk-through opening reaches the bottom
# edge, so it stays transparent).
from collections import deque
outside = [[False] * W for _ in range(H)]
dq = deque()
for x in range(W):
    for y in (0, H - 1):
        if not opaque(x, y) and not outside[y][x]:
            outside[y][x] = True
            dq.append((x, y))
for y in range(H):
    for x in (0, W - 1):
        if not opaque(x, y) and not outside[y][x]:
            outside[y][x] = True
            dq.append((x, y))
while dq:
    x, y = dq.popleft()
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < W and 0 <= ny < H and not opaque(nx, ny) and not outside[ny][nx]:
            outside[ny][nx] = True
            dq.append((nx, ny))
for y in range(H):
    for x in range(W):
        if not opaque(x, y) and not outside[y][x]:
            put(x, y, WOOD)

# ── Shading: shadow on right/bottom edges, light on left/top ─
opaque_cells = [(x, y) for y in range(H) for x in range(W) if opaque(x, y)]
for (x, y) in opaque_cells:               # shadow pass
    if not opaque(x + 1, y) or not opaque(x, y + 1):
        put(x, y, WOOD_DARK)
for (x, y) in opaque_cells:               # light pass (overrides on top-left)
    if not opaque(x - 1, y) or not opaque(x, y - 1):
        put(x, y, WOOD_LIGHT)

# ── Save (native 128 + a 6x preview for viewing) ──────
os.makedirs('output', exist_ok=True)
img.save('output/arch_gate.png')
img.resize((W * VIEW, H * VIEW), Image.NEAREST).save('output/arch_gate_view.png')
print('wrote output/arch_gate.png', img.size)
