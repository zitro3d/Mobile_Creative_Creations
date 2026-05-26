#!/usr/bin/env python3
"""Medieval sword — single pixel-art frame, transparent background.

Vertical knightly sword matching the reference: tapered steel blade with
a chiselled tip and a bright fuller highlight, a gold crossguard with
rounded knob ends, a wrapped brown leather grip, and a round gold pommel
set with a red gem. Light reads from the upper-left. One palette colour
per pixel, no anti-aliasing. Logical 37x132 -> 8x NEAREST -> 296x1056.
"""
import os, math
from PIL import Image

W, H, SCALE = 37, 132, 8
CX = 18

# ── Palette ───────────────────────────────────────────
OUTLINE      = (33, 28, 40)
BLADE_DARK   = (108, 110, 140)
BLADE_MID    = (150, 153, 185)
BLADE_LIGHT  = (196, 200, 228)
BLADE_HI     = (234, 238, 252)
GOLD_DARK    = (150, 108, 38)
GOLD_MID     = (214, 168, 66)
GOLD_LIGHT   = (248, 220, 120)
HAND_DARK    = (72, 46, 30)
HAND_MID     = (112, 72, 46)
HAND_LIGHT   = (146, 98, 62)
GEM_DARK     = (120, 32, 40)
GEM_MID      = (190, 58, 60)
GEM_HI       = (236, 124, 110)

img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
PX = img.load()

def put(x, y, c):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H:
        PX[x, y] = c + (255,)

def get(x, y):
    if 0 <= x < W and 0 <= y < H:
        return PX[x, y]
    return (0, 0, 0, 0)

# ── Blade ─────────────────────────────────────────────
TIP_Y, SHOULDER_Y, BASE_Y = 6, 21, 81

def blade_hw(y):
    if y < TIP_Y or y > BASE_Y:
        return None
    if y < SHOULDER_Y:
        f = (y - TIP_Y) / (SHOULDER_Y - TIP_Y)
        return 0.4 + f * 5.1
    f = (y - SHOULDER_Y) / (BASE_Y - SHOULDER_Y)
    return 5.5 + f * 1.0

for y in range(TIP_Y, BASE_Y + 1):
    hw = blade_hw(y)
    ihw = int(round(hw))
    for c in range(-ihw, ihw + 1):
        if c <= -ihw + 1:
            col = BLADE_LIGHT          # lit left edge
        elif c >= ihw - 1:
            col = BLADE_DARK           # shadow right edge
        else:
            col = BLADE_MID
        put(CX + c, y, col)
    # central fuller highlight (the bright streak)
    if ihw >= 3 and y > TIP_Y + 3:
        put(CX - 1, y, BLADE_HI)
        put(CX, y, BLADE_LIGHT)

# ── Crossguard (gold bar, rounded knob ends) ──────────
GY0, GY1 = 82, 89
for x in range(3, W - 3):
    for y in range(GY0 + 1, GY1):
        put(x, y, GOLD_MID)
# rounded knob ends
for (ex, sgn) in ((4, 1), (W - 5, -1)):
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            if dx * dx + dy * dy <= 9:
                put(ex + dx, (GY0 + GY1) // 2 + dy, GOLD_MID)
# central mount block where blade seats
for x in range(CX - 6, CX + 7):
    for y in range(GY0 - 1, GY1 + 2):
        put(x, y, GOLD_MID)
# gold shading (light top, shadow bottom)
for x in range(0, W):
    for y in range(GY0 - 1, GY1 + 2):
        if get(x, y)[:3] == GOLD_MID:
            if get(x, y - 1)[3] == 0 or get(x, y - 1)[:3] not in (GOLD_MID, GOLD_LIGHT, GOLD_DARK):
                put(x, y, GOLD_LIGHT)
            elif get(x, y + 1)[3] == 0:
                put(x, y, GOLD_DARK)

# ── Grip (wrapped leather) ────────────────────────────
GRIP_TOP, GRIP_BOT = GY1 + 1, 113
for y in range(GRIP_TOP, GRIP_BOT + 1):
    hw = 4 if y < GRIP_BOT - 1 else 3
    for c in range(-hw, hw + 1):
        if c <= -hw + 1:
            col = HAND_LIGHT
        elif c >= hw:
            col = HAND_DARK
        else:
            col = HAND_MID
        # diagonal wrap grooves
        if (y - c) % 3 == 0:
            col = HAND_DARK
        put(CX + c, y, col)

# ── Pommel (gold disc + diamond frame + red gem) ──────
PCX, PCY, PR = CX, 121, 9
for dy in range(-PR, PR + 1):
    for dx in range(-PR, PR + 1):
        if dx * dx + dy * dy <= PR * PR:
            c = GOLD_MID
            if dx + dy <= -4:
                c = GOLD_LIGHT
            elif dx + dy >= 5:
                c = GOLD_DARK
            put(PCX + dx, PCY + dy, c)
# diamond frame accent
for d in range(-5, 6):
    put(PCX + d, PCY - 5 + abs(d), GOLD_LIGHT if d <= 0 else GOLD_DARK)
    put(PCX + d, PCY + 5 - abs(d), GOLD_DARK)
# red gem
GR = 4
for dy in range(-GR, GR + 1):
    for dx in range(-GR, GR + 1):
        if dx * dx + dy * dy <= GR * GR:
            c = GEM_MID
            if dx + dy <= -3:
                c = GEM_HI
            elif dx + dy >= 4:
                c = GEM_DARK
            put(PCX + dx, PCY + dy, c)
put(PCX - 2, PCY - 2, GEM_HI)
put(PCX - 1, PCY - 2, (255, 200, 190))

# ── Black outline around the whole silhouette ─────────
opaque = [(x, y) for y in range(H) for x in range(W) if get(x, y)[3] != 0]
edge = []
for (x, y) in opaque:
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
        if get(x + dx, y + dy)[3] == 0:
            edge.append((x, y))
            break
for (x, y) in edge:
    put(x, y, OUTLINE)

# ── Save ──────────────────────────────────────────────
os.makedirs('output', exist_ok=True)
big = img.resize((W * SCALE, H * SCALE), Image.NEAREST)
big.save('output/sword.png')
print('wrote output/sword.png', big.size)
