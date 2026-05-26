#!/usr/bin/env python3
"""Medieval sword — single pixel-art frame, styled to match the portal.

Long knightly sword in the portal's palette: a glowing cyan/pale crystal
blade with a chiselled tip and white fuller highlight, a purple-stone
crossguard and wrapped grip with lavender highlights (DEEP_PURPLE
outline like the portal stone), and a round pommel set with a hot-pink
gem that echoes the portal's energy. Light reads from the upper-left.
One palette colour per pixel, no anti-aliasing.
Logical 37x180 -> 8x NEAREST -> 296x1440.
"""
import os
from PIL import Image

W, H, SCALE = 37, 180, 8
CX = 18

# ── Portal-matched palette ────────────────────────────
DEEP_PURPLE = (58, 38, 75)
PURPLE      = (92, 64, 110)
LAVENDER    = (140, 105, 155)
HOT_PINK    = (235, 110, 180)
SOFT_PINK   = (255, 170, 215)
CYAN        = (130, 200, 245)
PALE_CYAN   = (200, 235, 255)
DEEP_BLUE   = (60, 75, 165)
WHITE       = (255, 255, 255)

OUTLINE   = DEEP_PURPLE
GRIP_DARK = (40, 26, 52)            # darkest shade for the wrap grooves
GEM_DARK  = (150, 50, 110)

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

# ── Blade (long, glowing crystal) ─────────────────────
TIP_Y, SHOULDER_Y, BASE_Y = 6, 26, 120

def blade_hw(y):
    if y < TIP_Y or y > BASE_Y:
        return None
    if y < SHOULDER_Y:
        f = (y - TIP_Y) / (SHOULDER_Y - TIP_Y)
        return 0.4 + f * 5.2
    f = (y - SHOULDER_Y) / (BASE_Y - SHOULDER_Y)
    return 5.6 + f * 1.0

for y in range(TIP_Y, BASE_Y + 1):
    hw = blade_hw(y)
    ihw = int(round(hw))
    for c in range(-ihw, ihw + 1):
        if c <= -ihw + 1:
            col = PALE_CYAN          # lit left edge
        elif c >= ihw - 1:
            col = DEEP_BLUE          # shadow right edge
        else:
            col = CYAN
        put(CX + c, y, col)
    if ihw >= 3 and y > TIP_Y + 3:   # bright fuller highlight
        put(CX - 1, y, WHITE)
        put(CX, y, PALE_CYAN)

# ── Crossguard (purple stone, lavender-lit, knob ends) ─
GY0, GY1 = 121, 129
for x in range(3, W - 3):
    for y in range(GY0 + 1, GY1):
        put(x, y, PURPLE)
for ex in (4, W - 5):
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            if dx * dx + dy * dy <= 9:
                put(ex + dx, (GY0 + GY1) // 2 + dy, PURPLE)
for x in range(CX - 6, CX + 7):
    for y in range(GY0 - 1, GY1 + 2):
        put(x, y, PURPLE)
for x in range(W):
    for y in range(GY0 - 1, GY1 + 2):
        if get(x, y)[:3] == PURPLE:
            if get(x, y - 1)[:3] not in (PURPLE, LAVENDER, DEEP_PURPLE):
                put(x, y, LAVENDER)
            elif get(x, y + 1)[3] == 0:
                put(x, y, DEEP_PURPLE)

# ── Grip (wrapped, dark purple leather) ───────────────
GRIP_TOP, GRIP_BOT = GY1 + 1, 161        # extends down to plug into the pommel
for y in range(GRIP_TOP, GRIP_BOT + 1):
    if y >= GRIP_BOT - 1:
        hw = 2
    elif y >= GRIP_BOT - 4:
        hw = 3
    else:
        hw = 4
    for c in range(-hw, hw + 1):
        if c <= -hw + 1:
            col = PURPLE             # lit
        elif c >= hw:
            col = GRIP_DARK
        else:
            col = DEEP_PURPLE
        if (y - c) % 3 == 0:         # diagonal wrap grooves
            col = GRIP_DARK
        put(CX + c, y, col)

# ── Pommel (purple disc + diamond frame + pink gem) ───
PCX, PCY, PR = CX, 167, 9
for dy in range(-PR, PR + 1):
    for dx in range(-PR, PR + 1):
        if dx * dx + dy * dy <= PR * PR:
            c = PURPLE
            if dx + dy <= -4:
                c = LAVENDER
            elif dx + dy >= 5:
                c = DEEP_PURPLE
            put(PCX + dx, PCY + dy, c)
for d in range(-5, 6):                    # lower diamond accent only
    put(PCX + d, PCY + 5 - abs(d), DEEP_PURPLE)
GR = 4
for dy in range(-GR, GR + 1):
    for dx in range(-GR, GR + 1):
        if dx * dx + dy * dy <= GR * GR:
            c = HOT_PINK
            if dx + dy <= -3:
                c = SOFT_PINK
            elif dx + dy >= 4:
                c = GEM_DARK
            put(PCX + dx, PCY + dy, c)
put(PCX - 2, PCY - 2, SOFT_PINK)
put(PCX - 1, PCY - 2, WHITE)

# ── DEEP_PURPLE outline around the silhouette ─────────
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
