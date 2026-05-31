#!/usr/bin/env python3
"""16-bit pixel-art UFO matching the reference silhouette.

Logical 192x256 → 4x NEAREST → 768x1024.

Silhouette layers, top to bottom:
  - Hemisphere glowing dome with vertical light slits + diagonal specular streak
  - Curved top rim band catching highlight
  - Upper saucer body with row of orange light slits
  - Dark seams between panel layers
  - Tapered lower hull
  - Second smaller panel band with another row of lights
  - Narrow engine neck
  - Round glowing engine pod hanging below
  - Falling sparks
"""
import math, os
from PIL import Image

W, H, SCALE = 192, 256, 4

img = Image.new('RGBA', (W, H), (4, 4, 10, 255))
PX = img.load()

def put(x, y, c):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H:
        PX[x, y] = c + (255,) if len(c) == 3 else c

# ── Palette ─────────────────────────────────────────
SHINE  = (255, 252, 235)
HOT    = (255, 240, 175)
BRIGHT = (255, 215, 110)
LIGHT  = (252, 175, 70)
ORANGE = (235, 125, 45)
RED    = (180, 70, 30)
DEEP_R = (110, 35, 18)
DARK_R = (60, 18, 10)

HULL_VL = (200, 215, 230)
HULL_HI = (155, 175, 205)
HULL_L  = (115, 135, 168)
HULL_M  = (78, 95, 128)
HULL_D  = (50, 62, 90)
HULL_DD = (30, 38, 60)
HULL_O  = (12, 16, 30)

WIN_O = (255, 145, 55)
WIN_Y = (255, 220, 110)
WIN_W = (255, 245, 200)

STAR1 = (240, 235, 210)
STAR2 = (255, 200, 120)
STAR3 = (180, 160, 220)
STAR4 = (220, 180, 130)

# ── Sparse colored stars ────────────────────────────
stars = [
    (28, 30, STAR1), (34, 35, STAR1),  # dim cluster top-left
    (135, 22, STAR3),                   # purple star top
    (152, 48, STAR1), (35, 80, STAR2),
    (155, 92, STAR1), (15, 105, STAR3),
    (78, 110, STAR1), (110, 88, STAR2),
    (172, 130, STAR1), (60, 50, STAR4),
]
for x, y, c in stars:
    put(x, y, c)

UCX = HCX = 96

# ── DOME — hemisphere ───────────────────────────────
DCX = UCX
DCY_BASE = 145
DR = 38

Lx, Ly, Lz = 0.50, 0.55, 0.67
Lmag = math.sqrt(Lx*Lx + Ly*Ly + Lz*Lz)
Lx /= Lmag; Ly /= Lmag; Lz /= Lmag

for y in range(DCY_BASE - DR, DCY_BASE + 1):
    for x in range(DCX - DR, DCX + DR + 1):
        u = (x - DCX) / DR
        v = (DCY_BASE - y) / DR
        if v < 0: continue
        if u*u + v*v > 1.0: continue
        w = math.sqrt(max(0.0, 1.0 - u*u - v*v))
        # Unit sphere normal is (u, v, w)
        diff = max(0.0, u*Lx + v*Ly + w*Lz)
        # Warm uniform interior glow — keeps the dome looking lit from within
        # but without a blinding bright spot at the center.
        glow = 0.55 + 0.10 * w
        i = diff * 0.55 + glow * 0.40
        radial = math.sqrt(u*u + v*v)
        if   radial > 0.96: i *= 0.20
        elif radial > 0.90: i *= 0.50
        elif radial > 0.82: i *= 0.75
        if   i > 0.95: col = SHINE
        elif i > 0.82: col = HOT
        elif i > 0.68: col = BRIGHT
        elif i > 0.54: col = LIGHT
        elif i > 0.40: col = ORANGE
        elif i > 0.25: col = RED
        elif i > 0.10: col = DEEP_R
        else:          col = DARK_R
        put(x, y, col)

# Specular streak on upper-right of dome (diagonal swoop)
streak = [
    (DCX + 12, DCY_BASE - 34, HOT),
    (DCX + 13, DCY_BASE - 33, SHINE),
    (DCX + 14, DCY_BASE - 32, SHINE),
    (DCX + 15, DCY_BASE - 31, SHINE),
    (DCX + 16, DCY_BASE - 30, SHINE),
    (DCX + 17, DCY_BASE - 28, SHINE),
    (DCX + 18, DCY_BASE - 26, SHINE),
    (DCX + 19, DCY_BASE - 24, HOT),
    (DCX + 20, DCY_BASE - 22, HOT),
    (DCX + 21, DCY_BASE - 19, HOT),
    (DCX + 22, DCY_BASE - 16, BRIGHT),
    (DCX + 22, DCY_BASE - 13, BRIGHT),
    (DCX + 23, DCY_BASE - 10, LIGHT),
]
for x, y, c in streak:
    put(x, y, c)

# Vertical light slits on the LEFT side of the dome
slit_positions = [
    (DCX - 19, DCY_BASE - 18, DCY_BASE - 5),
    (DCX - 13, DCY_BASE - 24, DCY_BASE - 4),
    (DCX - 7,  DCY_BASE - 28, DCY_BASE - 3),
]
for sx, ys, ye in slit_positions:
    mid = (ys + ye) // 2
    for y in range(ys, ye + 1):
        put(sx, y, DARK_R)
        if mid - 2 <= y <= mid + 2:
            put(sx, y, WIN_O)

# ── SAUCER ──────────────────────────────────────────
saucer_rows = [
    # y, hw, role  — 33 rows of disc (146-178), then lower panel/neck below
    (146, 44, 'rim_flare'),
    (147, 58, 'rim_flare'),
    (148, 70, 'rim_flare'),
    (149, 80, 'rim_flare'),
    (150, 86, 'rim_top'),
    (151, 90, 'rim_top'),
    (152, 92, 'body_hi'),
    (153, 93, 'body_hi'),
    (154, 94, 'body_hi'),
    (155, 94, 'body_hi'),
    (156, 94, 'seam'),
    (157, 94, 'body_lights'),
    (158, 94, 'body_lights'),
    (159, 93, 'body_lights'),
    (160, 93, 'body_lights'),
    (161, 92, 'seam'),
    (162, 91, 'body_dark'),
    (163, 90, 'body_dark'),
    (164, 88, 'body_dark'),
    (165, 86, 'body_dark'),
    (166, 84, 'body_dark'),
    (167, 82, 'seam'),
    (168, 80, 'body_lights2'),
    (169, 78, 'body_lights2'),
    (170, 76, 'body_lights2'),
    (171, 73, 'body_lights2'),
    (172, 70, 'seam'),
    (173, 66, 'taper'),
    (174, 61, 'taper'),
    (175, 55, 'taper'),
    (176, 48, 'taper'),
    (177, 40, 'taper'),
    (178, 32, 'taper'),
    (179, 25, 'lower_panel'),
    (180, 21, 'lower_panel'),
    (181, 18, 'lower_lights'),
    (182, 16, 'lower_dark'),
    (183, 13, 'neck'),
    (184, 11, 'neck'),
    (185, 9,  'neck'),
    (186, 8,  'neck'),
]

def shade(role, dx, hw):
    rel = dx / max(hw, 1)
    if abs(dx) == hw and hw > 3:
        return HULL_O
    if abs(dx) >= hw - 1 and hw > 6:
        return HULL_DD
    if role == 'rim_flare':
        if rel > 0.4:   return HULL_VL
        if rel > 0.0:   return HULL_HI
        if rel > -0.4:  return HULL_L
        return HULL_M
    if role == 'rim_top':
        if rel > 0.4:   return HULL_VL
        if rel > -0.1:  return HULL_HI
        if rel > -0.5:  return HULL_L
        return HULL_M
    if role == 'body_hi':
        if rel > 0.3:   return HULL_HI
        if rel > -0.2:  return HULL_L
        if rel > -0.6:  return HULL_M
        return HULL_D
    if role == 'seam':
        return HULL_O
    if role == 'body_lights':
        if rel > 0.4:   return HULL_L
        if rel > -0.3:  return HULL_M
        return HULL_D
    if role == 'body_lights2':
        if rel > 0.3:   return HULL_M
        if rel > -0.3:  return HULL_D
        return HULL_DD
    if role == 'body_dark':
        if rel > 0.3:   return HULL_M
        if rel > -0.3:  return HULL_D
        return HULL_DD
    if role == 'taper':
        if rel > 0.3:   return HULL_M
        if rel > -0.3:  return HULL_D
        return HULL_DD
    if role == 'lower_panel':
        if rel > 0.3:   return HULL_L
        if rel > -0.3:  return HULL_M
        return HULL_D
    if role == 'lower_lights':
        return HULL_M
    if role == 'lower_dark':
        return HULL_D
    if role == 'neck':
        if dx > 0:      return HULL_M
        if dx > -2:     return HULL_D
        return HULL_DD
    return HULL_M

for y, hw, role in saucer_rows:
    for dx in range(-hw, hw + 1):
        put(HCX + dx, y, shade(role, dx, hw))

# ── LIGHT SLITS along the body (orange/red rectangles) ─
# Arc the lights across the rim — they appear smaller toward the edges
n_lights = 16
for i in range(n_lights):
    theta = math.pi * (i + 0.5) / n_lights - math.pi / 2  # -pi/2 .. +pi/2
    lx = HCX + int(round(90 * math.sin(theta)))
    edge_dim = abs(math.sin(theta))
    if edge_dim < 0.6:
        put(lx, 158, WIN_Y)
        put(lx, 159, WIN_O)
    else:
        put(lx, 158, ORANGE)
        put(lx, 159, RED)

# Brighter front-cluster windows (cabin lights) on main body row
for dxc in (-44, -26, -10, 10, 26, 44):
    x = HCX + dxc
    put(x, 158, WIN_W)
    put(x + 1, 158, WIN_Y)
    put(x, 159, WIN_Y)
    put(x + 1, 159, WIN_O)

# Second row of lights on the second body band
n_mid = 12
for i in range(n_mid):
    theta = math.pi * (i + 0.5) / n_mid - math.pi / 2
    lx = HCX + int(round(76 * math.sin(theta)))
    edge_dim = abs(math.sin(theta))
    if edge_dim < 0.6:
        put(lx, 169, WIN_O)
        put(lx, 170, ORANGE)
    else:
        put(lx, 169, ORANGE)
        put(lx, 170, RED)

# Third row of small lights on lower panel band
n_lower = 7
for i in range(n_lower):
    theta = math.pi * (i + 0.5) / n_lower - math.pi / 2
    lx = HCX + int(round(17 * math.sin(theta)))
    put(lx, 181, WIN_O)

# ── ENGINE NECK + POD ───────────────────────────────
# Tight neck just above the pod
for y in range(187, 193):
    hw = 4 if y < 191 else 6
    for dx in range(-hw, hw + 1):
        x = HCX + dx
        if abs(dx) == hw:    col = HULL_O
        elif dx > 1:         col = HULL_M
        elif dx > -2:        col = HULL_D
        else:                col = HULL_DD
        put(x, y, col)

# Engine pod (small round sphere with glowing core)
POD_CX = HCX
POD_CY = 201
POD_R = 12

for y in range(POD_CY - POD_R, POD_CY + POD_R + 1):
    for x in range(POD_CX - POD_R, POD_CX + POD_R + 1):
        u = (x - POD_CX) / POD_R
        v = (y - POD_CY) / POD_R
        d = math.sqrt(u*u + v*v)
        if d > 1.0: continue
        if   d > 0.92: col = HULL_O
        elif d > 0.80: col = HULL_DD
        elif d > 0.65: col = ORANGE
        elif d > 0.48: col = LIGHT
        elif d > 0.32: col = BRIGHT
        elif d > 0.18: col = HOT
        else:          col = SHINE
        put(x, y, col)

# Specular dot on engine pod
put(POD_CX + 3, POD_CY - 4, SHINE)
put(POD_CX + 4, POD_CY - 3, SHINE)

# ── FALLING SPARKS ──────────────────────────────────
sparks = [
    (HCX, 217, ORANGE),
    (HCX - 2, 220, WIN_O),
    (HCX + 1, 223, ORANGE),
    (HCX,     226, ORANGE),
    (HCX + 2, 229, WIN_O),
    (HCX - 1, 233, ORANGE),
    (HCX,     237, WIN_O),
    (HCX + 1, 241, ORANGE),
    (HCX - 2, 245, ORANGE),
]
for x, y, c in sparks:
    put(x, y, c)

os.makedirs('output', exist_ok=True)
img.resize((W * SCALE, H * SCALE), Image.NEAREST).save('output/ufo.png')
print('wrote output/ufo.png', (W * SCALE, H * SCALE))
