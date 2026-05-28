#!/usr/bin/env python3
"""Rainbow portal — single static frame matching the reference exactly.

Flat-frontal rectangular doorway with a slightly curved top, rainbow
gradient flowing around the frame perimeter (red crown → yellow/green
sides → blue/purple legs), bright HOT-PINK neon rim around the empty
black opening, small red gem on the crown, gold puddle and dark rocks
at the base, scattered sparkles around the portal. Pixel art, no
anti-aliasing.

Logical 80x100 -> 12x NEAREST -> 960x1200, transparent background.
"""
import math, os
from PIL import Image

W, H, SCALE = 80, 100, 12

# ── Palette ───────────────────────────────────────────
BLACK      = (10, 6, 16)
RED        = (235, 60, 75)
ORANGE     = (245, 130, 60)
YELLOW     = (250, 215, 80)
GREEN      = (110, 215, 100)
CYAN       = (80, 220, 230)
BLUE       = (90, 130, 240)
PURPLE     = (165, 90, 235)
MAGENTA    = (225, 95, 195)
HOT_PINK   = (255, 80, 180)
SOFT_PINK  = (255, 170, 215)
GOLD_HI    = (255, 230, 120)
GOLD_MID   = (240, 185, 70)
GOLD_DARK  = (180, 125, 40)
ROCK_DARK  = (50, 30, 65)
ROCK_MID   = (85, 55, 100)
WHITE      = (255, 255, 255)
GEM_RED    = (215, 55, 75)
GEM_HI     = (255, 195, 195)

img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
PX = img.load()

def put(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        PX[x, y] = c + (255,)

def getc(x, y):
    if 0 <= x < W and 0 <= y < H:
        return PX[x, y]
    return (0, 0, 0, 0)

# ── Geometry: flat-frontal U-shape doorway ────────────
CX = 40
Y_OUTER_TOP = 6        # outer crown apex
Y_INNER_TOP = 14       # inner crown apex
Y_SPRING    = 26       # crown ends, straight legs begin
Y_BOTTOM    = 88       # bottom of frame (legs end at floor level)
OUTER_HW    = 30       # outer half-width
INNER_HW    = 18       # inner half-width (opening)

def outer_hw(y):
    if y < Y_OUTER_TOP: return None
    if y >= Y_SPRING:   return OUTER_HW
    dy = Y_SPRING - y
    b  = Y_SPRING - Y_OUTER_TOP
    if dy > b: return None
    return OUTER_HW * math.sqrt(1 - (dy / b) ** 2)

def inner_hw(y):
    if y < Y_INNER_TOP: return None
    if y >= Y_SPRING:   return INNER_HW
    dy = Y_SPRING - y
    b  = Y_SPRING - Y_INNER_TOP
    if dy > b: return None
    return INNER_HW * math.sqrt(1 - (dy / b) ** 2)

def rainbow_at(x, y, dx):
    """Rainbow colour for a frame pixel, picked by position around the arch."""
    if y < Y_SPRING:
        # Crown: angle from the top apex (CX, Y_SPRING)
        ang = math.atan2(Y_SPRING - y, dx)              # 0..π (right=0, top=π/2, left=π)
        phi = abs(ang - math.pi / 2) / (math.pi / 2)     # 0 at top → 1 at sides
        if phi < 0.18: return RED
        if phi < 0.42: return ORANGE
        if phi < 0.70: return YELLOW
        return GREEN
    # Legs: hue from y position
    t = (y - Y_SPRING) / (Y_BOTTOM - Y_SPRING)           # 0..1
    if t < 0.18: return GREEN
    if t < 0.38: return CYAN
    if t < 0.60: return BLUE
    if t < 0.82: return PURPLE
    return MAGENTA

# ── Fill the frame (rainbow) + black opening ──────────
for y in range(Y_OUTER_TOP, Y_BOTTOM + 1):
    ohw = outer_hw(y)
    if ohw is None: continue
    ihw = inner_hw(y)
    iohw = int(round(ohw))
    iihw = int(round(ihw)) if ihw is not None else None
    for dx in range(-iohw, iohw + 1):
        x = CX + dx
        if iihw is not None and -iihw <= dx <= iihw:
            put(x, y, BLACK)                             # opening
        else:
            put(x, y, rainbow_at(x, y, dx))              # rainbow frame

# ── Hot-pink neon rim around the entire opening ───────
for y in range(Y_INNER_TOP, Y_BOTTOM + 1):
    ihw = inner_hw(y)
    if ihw is None: continue
    iihw = int(round(ihw))
    # vertical edges of the opening (innermost black column gets pink)
    for dx in (-iihw, iihw):
        x = CX + dx
        if getc(x, y)[:3] == BLACK:
            put(x, y, HOT_PINK)
    # arched top of opening: any black pixel with rainbow above it
    if y < Y_SPRING + 2:
        for dx in range(-iihw, iihw + 1):
            x = CX + dx
            if getc(x, y)[:3] == BLACK and getc(x, y - 1)[3] == 255 \
               and getc(x, y - 1)[:3] != BLACK and getc(x, y - 1)[:3] != HOT_PINK:
                put(x, y, HOT_PINK)

# ── Red gem on the crown ──────────────────────────────
gem_cx, gem_cy, gem_r = CX, 4, 2
for dy in range(-gem_r, gem_r + 1):
    for dx in range(-gem_r, gem_r + 1):
        if dx * dx + dy * dy <= gem_r * gem_r:
            put(gem_cx + dx, gem_cy + dy, GEM_RED)
put(gem_cx - 1, gem_cy - 1, GEM_HI)
put(gem_cx,     gem_cy - 1, WHITE)
put(gem_cx + 2, gem_cy,     GOLD_MID)
put(gem_cx - 2, gem_cy,     GOLD_MID)
put(gem_cx,     gem_cy + 2, GOLD_MID)

# ── Gold puddle pooling at the base ───────────────────
puddle_cy = Y_BOTTOM + 1
puddle_w, puddle_h = 26, 5
for dy in range(-1, puddle_h + 2):
    for dx in range(-puddle_w, puddle_w + 1):
        ndx = dx / puddle_w
        ndy = (dy + 0.5) / puddle_h
        if ndx * ndx + ndy * ndy * 0.55 > 1:
            continue
        col = GOLD_HI if (abs(ndx) < 0.45 and ndy < 0.6) else \
              GOLD_MID if abs(ndx) < 0.78 else GOLD_DARK
        put(CX + dx, puddle_cy + dy, col)

# ── Dark rocks at the base corners ────────────────────
def rock(cx, cy):
    pts = [(0,0),(1,0),(-1,0),(2,0),(-2,0),(3,1),(-3,1),
           (0,1),(1,1),(-1,1),(2,1),(-2,1),(1,-1),(-1,-1),(0,-1),(2,-1)]
    for dx, dy in pts:
        put(cx + dx, cy + dy, ROCK_MID if dy < 0 else ROCK_DARK)
rock(CX - 24, Y_BOTTOM + 2)
rock(CX + 24, Y_BOTTOM + 2)

# ── Sparkles scattered around the portal ──────────────
sparkles = [
    (6, 18, YELLOW), (74, 16, YELLOW), (4, 38, CYAN), (76, 40, CYAN),
    (8, 60, SOFT_PINK), (72, 62, SOFT_PINK), (12, 80, WHITE), (68, 82, WHITE),
    (26, 4, YELLOW), (54, 4, YELLOW), (32, 94, CYAN), (48, 94, CYAN),
    (2, 30, WHITE), (78, 70, WHITE), (15, 92, SOFT_PINK), (65, 92, YELLOW),
    (10, 8, CYAN), (70, 8, SOFT_PINK), (5, 52, YELLOW), (75, 50, WHITE),
]
for x, y, col in sparkles:
    if getc(x, y)[3] != 0:
        continue
    put(x, y, col)
    if col in (YELLOW, WHITE):                            # 4-point star
        if getc(x + 1, y)[3] == 0: put(x + 1, y, col)
        if getc(x - 1, y)[3] == 0: put(x - 1, y, col)
        if getc(x, y + 1)[3] == 0: put(x, y + 1, col)
        if getc(x, y - 1)[3] == 0: put(x, y - 1, col)

# ── Save ──────────────────────────────────────────────
os.makedirs('output', exist_ok=True)
img.resize((W * SCALE, H * SCALE), Image.NEAREST).save('output/rainbow_portal.png')
print('wrote output/rainbow_portal.png', (W * SCALE, H * SCALE))
