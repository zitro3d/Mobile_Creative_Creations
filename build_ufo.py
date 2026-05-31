#!/usr/bin/env python3
"""16-bit pixel art UFO — glowing dome, metallic saucer hull, falling thruster sparks.

Logical 64x80 → 12x NEAREST → 768x960, transparent background.
"""
import math, os
from PIL import Image

W, H, SCALE = 64, 80, 12

img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
PX = img.load()

def put(x, y, c):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H:
        PX[x, y] = c + (255,) if len(c) == 3 else c

# ── 16-bit palette ────────────────────────────────────
# Dome (warm glowing sphere)
SHINE   = (255, 252, 230)
HOT     = (255, 240, 165)
BRIGHT  = (255, 205, 100)
LIGHT   = (250, 165, 60)
ORANGE  = (235, 115, 40)
RED     = (195, 70, 30)
DEEP_R  = (130, 38, 22)
# Hull (cool blue-gray metal)
HULL_HI = (190, 205, 230)
HULL_L  = (135, 152, 185)
HULL_M  = (90, 105, 138)
HULL_D  = (52, 62, 90)
HULL_O  = (24, 28, 48)
# Lights / sparks / stars
WIN_O   = (255, 145, 55)
WIN_Y   = (255, 220, 110)
SPARK   = (255, 180, 80)
STAR    = (240, 235, 210)
DIM     = (155, 155, 175)

# ── Background stars (scattered) ──────────────────────
stars = [(10, 6, STAR), (16, 4, DIM), (40, 7, DIM),
         (52, 10, STAR), (5, 14, DIM), (48, 16, STAR),
         (20, 18, DIM), (58, 21, STAR), (3, 22, DIM)]
for x, y, c in stars:
    put(x, y, c)

# ── DOME — glowing 3D sphere, lit from upper-right ────
DCX, DCY = 32, 30
DRX, DRY = 14, 12
# Light vector in 3D (x: right+, y: down+, z: out of screen)
L = (0.55, -0.55, 0.62)
Ll = math.sqrt(sum(c * c for c in L))
LN = (L[0] / Ll, L[1] / Ll, L[2] / Ll)

for y in range(DCY - DRY, DCY + 3):
    for x in range(DCX - DRX, DCX + DRX + 1):
        dxn = (x - DCX) / DRX
        dyn = (y - DCY) / DRY
        d2 = dxn * dxn + dyn * dyn
        if d2 > 1.0:
            continue
        # Cull bottom half (dome sits on hull, not a full sphere)
        if y > DCY + 1:
            continue
        # Sphere surface normal (already unit length)
        nz = math.sqrt(max(0, 1 - d2))
        # Phong-ish intensity
        i = dxn * LN[0] + dyn * LN[1] + nz * LN[2]
        # Choose colour band
        if   i > 0.92: col = SHINE
        elif i > 0.78: col = HOT
        elif i > 0.58: col = BRIGHT
        elif i > 0.36: col = LIGHT
        elif i > 0.10: col = ORANGE
        elif i > -0.20: col = RED
        else:          col = DEEP_R
        # Rim outline at the silhouette
        if d2 > 0.90 and i < 0.20:
            col = DEEP_R
        put(x, y, col)

# A specular highlight cluster on the upper-right of the dome
specs = [(33, 22, SHINE), (34, 22, SHINE), (33, 23, HOT),
         (34, 23, SHINE), (35, 23, HOT), (35, 24, HOT)]
for x, y, c in specs:
    put(x, y, c)

# ── HULL — saucer disc with rim & windows ─────────────
# Hand-picked half-widths per row so the silhouette is exactly right.
HCX = 32
hull_rows = {
    # row : (half_width, role)
    32: (12, 'top'),
    33: (15, 'top'),
    34: (19, 'top'),
    35: (23, 'rim_top'),
    36: (26, 'rim_top'),
    37: (27, 'rim'),
    38: (27, 'rim_lights'),
    39: (26, 'rim'),
    40: (22, 'taper'),
    41: (17, 'taper'),
    42: (11, 'taper'),
    43: (6,  'thruster_base'),
}
for y, (hw, role) in hull_rows.items():
    for dx in range(-hw, hw + 1):
        x = HCX + dx
        # Edge outline
        if dx <= -hw + 1 or dx >= hw - 1 or y == 43:
            col = HULL_O
        elif role == 'top':
            # Top surface of saucer — gradient light to dark
            if dx > hw * 0.45:   col = HULL_HI
            elif dx > 0:         col = HULL_L
            elif dx > -hw * 0.5: col = HULL_M
            else:                col = HULL_D
        elif role == 'rim_top':
            # Upper rim — highlight band
            if dx > hw * 0.45:   col = HULL_HI
            elif dx > -hw * 0.4: col = HULL_L
            else:                col = HULL_M
        elif role == 'rim':
            # Vertical side wall
            if dx > hw * 0.40:   col = HULL_M
            elif dx > -hw * 0.4: col = HULL_D
            else:                col = HULL_D
        elif role == 'rim_lights':
            # Window light row — mostly dark with bright dashes
            col = HULL_D
        elif role == 'taper':
            # Bottom taper — keep mostly dark
            if dx > hw * 0.4:    col = HULL_M
            else:                col = HULL_D
        elif role == 'thruster_base':
            col = HULL_D
        put(x, y, col)

# Window lights along the rim (row 38)
for wp in (-23, -18, -12, -6, 0, 6, 12, 18, 23):
    x = HCX + wp
    if -27 < wp < 27:
        put(x, 38, WIN_O)
# A couple brighter "cabin" windows on left (matches reference)
for x, y in [(20, 36), (21, 36), (22, 36)]:
    put(x, y, HULL_O)            # darker cockpit framing
put(20, 37, WIN_O); put(21, 37, WIN_O); put(22, 37, WIN_O)
# Decorative trim line just under the rim highlight (row 36)
for x in range(HCX - 25, HCX + 26):
    cur = PX[x, 36]
    if cur and cur[3] == 255 and cur[:3] in (HULL_M, HULL_L):
        # leave as-is
        pass

# ── Centre seam between top and bottom hull halves ────
for dx in range(-26, 27):
    x = HCX + dx
    if PX[x, 39][3]:
        put(x, 39, HULL_O if dx % 4 == 0 else HULL_D)

# ── THRUSTER + GLOW ───────────────────────────────────
# narrow rectangle below the hull
for y in range(44, 51):
    if   y <= 45: hw = 5
    elif y <= 47: hw = 4
    elif y <= 49: hw = 4
    else:         hw = 3
    for dx in range(-hw, hw + 1):
        x = HCX + dx
        if dx == -hw or dx == hw:
            col = HULL_O
        elif dx > 0:
            col = HULL_M
        else:
            col = HULL_D
        put(x, y, col)

# Glow at the thruster mouth
put(HCX - 2, 51, WIN_O)
put(HCX - 1, 51, WIN_Y)
put(HCX,     51, SHINE)
put(HCX + 1, 51, WIN_Y)
put(HCX + 2, 51, WIN_O)
put(HCX - 1, 52, WIN_O)
put(HCX,     52, WIN_Y)
put(HCX + 1, 52, WIN_O)
put(HCX,     53, SPARK)

# Falling sparks beneath the thruster
sparks = [
    (HCX,     55, SPARK),
    (HCX - 1, 57, SPARK),
    (HCX + 1, 58, SPARK),
    (HCX,     60, WIN_O),
    (HCX + 2, 62, SPARK),
    (HCX - 2, 64, SPARK),
    (HCX,     65, SPARK),
    (HCX - 1, 68, WIN_O),
    (HCX + 1, 71, SPARK),
]
for x, y, c in sparks:
    put(x, y, c)

# ── Save ──────────────────────────────────────────────
os.makedirs('output', exist_ok=True)
img.resize((W * SCALE, H * SCALE), Image.NEAREST).save('output/ufo.png')
print('wrote output/ufo.png', (W * SCALE, H * SCALE))
