#!/usr/bin/env python3
"""High-res 16-bit pixel-art UFO — denser pixels, tilted 3/4 top-down perspective.

Logical 240x180 → 4x NEAREST → 960x720, transparent background.
Camera looks slightly down at the UFO: top saucer surface visible as a wide
ellipse, flat glowing dome (oblate cap, not a sphere), windows arc curving
across the front rim.
"""
import math, os, random
from PIL import Image

W, H, SCALE = 240, 180, 4

img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
PX = img.load()

def put(x, y, c):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H:
        PX[x, y] = c + (255,) if len(c) == 3 else c

# ── Palette (expanded for higher resolution) ──────────
SHINE   = (255, 252, 235)
HOT     = (255, 240, 175)
BRIGHT  = (255, 215, 115)
LIGHT   = (252, 175, 70)
ORANGE  = (235, 125, 45)
RED     = (195, 75, 35)
DEEP_R  = (130, 38, 22)
DARK_R  = (78, 22, 12)

HULL_VL = (235, 240, 250)
HULL_HI = (200, 215, 240)
HULL_L  = (160, 180, 215)
HULL_M  = (110, 130, 170)
HULL_D  = (65, 80, 120)
HULL_DD = (40, 50, 80)
HULL_O  = (18, 22, 42)

WIN_O   = (255, 145, 55)
WIN_Y   = (255, 220, 110)
WIN_W   = (255, 245, 200)
SPARK   = (255, 180, 80)
STAR    = (240, 235, 210)
DIM     = (155, 155, 175)

# ── Background stars ──────────────────────────────────
random.seed(42)
for _ in range(48):
    sx = random.randint(2, W - 3)
    sy = random.randint(2, 56)
    if abs(sx - 120) < 60 and 30 < sy: continue
    put(sx, sy, STAR if random.random() > 0.4 else DIM)

UCX = HCX = 120

# ── SAUCER TOP — convex disc, tilted view shows top surface ─
# Ellipse: cx=120, cy=92, rx=103, ry=32, upper portion (y=60-91)
for y in range(60, 92):
    rel = (92 - y) / 32
    if rel >= 1: continue
    hw = int(round(103 * math.sqrt(1 - rel * rel)))
    if hw < 4: continue
    row_frac = 1 - rel  # 0 at narrow top, 1 at widest rim
    for dx in range(-hw, hw + 1):
        x = HCX + dx
        rx_rel = dx / max(hw, 1)
        if abs(dx) == hw:
            col = HULL_O
        elif abs(dx) >= hw - 1:
            col = HULL_DD
        else:
            # Convex top surface, lit from upper-right
            light = rx_rel * 0.42 + (1 - row_frac) * 0.15
            curve_lift = (1 - abs(rx_rel) ** 1.5) * 0.12
            light += curve_lift
            if   light > 0.55: col = HULL_VL
            elif light > 0.35: col = HULL_HI
            elif light > 0.10: col = HULL_L
            elif light > -0.15: col = HULL_M
            elif light > -0.35: col = HULL_D
            else:               col = HULL_DD
        put(x, y, col)

# ── RIM BAND (vertical sides where windows live) ─────
for y in range(92, 96):
    hw = 103
    for dx in range(-hw, hw + 1):
        x = HCX + dx
        if abs(dx) == hw:
            col = HULL_O
        elif abs(dx) >= hw - 1:
            col = HULL_DD
        else:
            r_in = y - 92
            if   r_in == 0: col = HULL_M
            elif r_in == 1: col = HULL_D
            elif r_in == 2: col = HULL_DD
            else:           col = HULL_O
        put(x, y, col)

# ── WINDOWS along front rim arc (perspective curve) ──
n_windows = 22
rim_arc_rx = 98
rim_arc_cy = 93
rim_arc_ry = 2  # foreshortened y curve
for i in range(n_windows):
    theta = math.pi * (i + 0.5) / n_windows - math.pi / 2
    wx = HCX + int(round(rim_arc_rx * math.sin(theta)))
    wy = rim_arc_cy + int(round(rim_arc_ry * math.cos(theta)))
    if HCX - 100 < wx < HCX + 100:
        put(wx, wy, WIN_Y)
        put(wx, wy + 1, WIN_O)

# Cabin / cockpit windows (brighter, larger, on front)
for dxc in (-42, -23, 23, 42):
    x = HCX + dxc
    put(x, 93, WIN_W)
    put(x + 1, 93, WIN_Y)
    put(x, 94, WIN_Y)
    put(x + 1, 94, WIN_O)

# ── BOTTOM HULL — tapered smoothly into the thruster ─
bot_rows = {
    96: 102, 97: 99, 98: 95, 99: 91, 100: 87, 101: 82, 102: 77,
    103: 71, 104: 65, 105: 58, 106: 51, 107: 43, 108: 35, 109: 27,
    110: 19, 111: 12, 112: 8,
}
for y, hw in bot_rows.items():
    row_frac = (y - 96) / 16
    for dx in range(-hw, hw + 1):
        x = HCX + dx
        rx_rel = dx / max(hw, 1)
        if abs(dx) == hw:
            col = HULL_O
        elif abs(dx) >= hw - 1 and hw > 6:
            col = HULL_DD
        else:
            light = rx_rel * 0.30 - row_frac * 0.18
            if   light > 0.25: col = HULL_M
            elif light > 0.0:  col = HULL_D
            elif light > -0.25: col = HULL_DD
            else:               col = HULL_O
        put(x, y, col)

# ── THRUSTER cylinder ───────────────────────────────
for y in range(113, 127):
    if   y <= 115: hw = 8
    elif y <= 119: hw = 8
    elif y <= 123: hw = 7
    else:          hw = 6
    for dx in range(-hw, hw + 1):
        x = HCX + dx
        if   abs(dx) == hw:
            col = HULL_O
        elif abs(dx) == hw - 1:
            col = HULL_DD
        elif dx > 1:
            col = HULL_M
        elif dx > -2:
            col = HULL_D
        else:
            col = HULL_DD
        put(x, y, col)

# ── THRUSTER GLOW — radial bright cluster ───────────
glow_y0 = 127
for dy in range(0, 10):
    y = glow_y0 + dy
    for dx in range(-9, 10):
        dist = math.sqrt(dx * dx + (dy * 1.25) ** 2)
        if dist > 8.5: continue
        if   dist < 1.5: col = SHINE
        elif dist < 2.8: col = WIN_W
        elif dist < 4.2: col = WIN_Y
        elif dist < 5.8: col = WIN_O
        elif dist < 7.5: col = SPARK
        else:            col = SPARK
        put(HCX + dx, y, col)

# ── FALLING SPARKS ──────────────────────────────────
random.seed(7)
for _ in range(34):
    sx = HCX + random.randint(-7, 7)
    sy = 140 + random.randint(0, 38)
    c = SPARK if random.random() > 0.3 else WIN_O
    put(sx, sy, c)

# ── DOME — low, flat oblate cap (drawn LAST, on top) ─
# DRX:DRY = 38:14 ≈ 2.7:1 — flat cap, not a sphere
DCX = UCX
DCY_BASE = 72
DRX = 38
DRY = 14
DRZ = 32

# Light direction in world space (X=right, Y=up, Z=toward camera)
Lx, Ly, Lz = 0.40, 0.55, 0.73
Lmag = math.sqrt(Lx * Lx + Ly * Ly + Lz * Lz)
Lx /= Lmag; Ly /= Lmag; Lz /= Lmag

for y in range(DCY_BASE - DRY, DCY_BASE + 1):
    for x in range(DCX - DRX, DCX + DRX + 1):
        u = (x - DCX) / DRX
        v = (DCY_BASE - y) / DRY
        if v < 0: continue
        if u * u + v * v > 1.0: continue
        w = math.sqrt(max(0.0, 1.0 - u * u - v * v))

        # Inner glow — glass dome lit from within
        glow = w
        # Slight upper-band lift (top of dome a little brighter)
        vert_lift = max(0, v - 0.25) * 0.18
        # Upper-right highlight from the external light
        hr = max(0, u * 0.18 + (v - 0.4) * 0.18)

        i = glow * 0.45 + vert_lift + hr + 0.12

        # Rim darkening — defines silhouette without a "ball" feel
        radial = math.sqrt(u * u + v * v)
        if   radial > 0.93: i *= 0.25
        elif radial > 0.85: i *= 0.55
        elif radial > 0.75: i *= 0.80

        if   i > 0.92: col = SHINE
        elif i > 0.78: col = HOT
        elif i > 0.63: col = BRIGHT
        elif i > 0.48: col = LIGHT
        elif i > 0.32: col = ORANGE
        elif i > 0.18: col = RED
        elif i > 0.06: col = DEEP_R
        else:          col = DARK_R
        put(x, y, col)

# Specular highlight cluster (manual touches on upper-right of dome)
spec = [
    (DCX + 10, DCY_BASE - 11, SHINE),
    (DCX + 11, DCY_BASE - 11, SHINE),
    (DCX + 12, DCY_BASE - 10, SHINE),
    (DCX + 13, DCY_BASE - 9,  HOT),
    (DCX + 14, DCY_BASE - 8,  HOT),
    (DCX + 9,  DCY_BASE - 12, HOT),
]
for x, y, c in spec:
    put(x, y, c)

# Dome-base shadow ring (defines the dome sitting in its saucer socket)
for x in range(DCX - DRX + 2, DCX + DRX - 1):
    u = (x - DCX) / DRX
    if abs(u) < 0.97:
        put(x, DCY_BASE + 1, HULL_DD)

# ── Save ──────────────────────────────────────────────
os.makedirs('output', exist_ok=True)
img.resize((W * SCALE, H * SCALE), Image.NEAREST).save('output/ufo.png')
print('wrote output/ufo.png', (W * SCALE, H * SCALE))
