#!/usr/bin/env python3
"""Rainbow portal — single static frame matching the reference exactly.

Flat-frontal RECTANGULAR doorway with a separate crown bar at top, a
DITHERED/textured rainbow gradient flowing down the legs (red crown →
green/cyan middle → blue/purple/magenta feet), a HOT_PINK neon rim
around the empty opening, a small flame-gem on the crown, cyan diamond
crystals embedded mid-leg, gold puddles dripping at each foot, dark
rocks at the base corners, and many scattered sparkle stars.
Logical 80x110 -> 12x NEAREST -> 960x1320, transparent background.
"""
import os, random
from PIL import Image

W, H, SCALE = 80, 110, 12
random.seed(42)

# ── Palette ───────────────────────────────────────────
BLACK         = (12, 8, 18)
RED           = (240, 60, 70)
ORANGE        = (250, 130, 60)
YELLOW        = (255, 220, 80)
GREEN         = (120, 220, 100)
CYAN          = (80, 220, 235)
BLUE          = (90, 130, 245)
PURPLE        = (170, 90, 240)
MAGENTA       = (230, 95, 200)
PINK          = (255, 130, 210)
HOT_PINK      = (255, 70, 175)
SOFT_PINK     = (255, 170, 215)
DARK_RED      = (140, 30, 55)
DARK_ORANGE   = (180, 80, 30)
DARK_YELLOW   = (180, 140, 30)
DARK_GREEN    = (50, 130, 55)
DARK_CYAN     = (40, 130, 160)
DARK_BLUE     = (40, 60, 160)
DARK_PURPLE   = (90, 40, 140)
DARK_MAGENTA  = (160, 50, 130)
DARK_PINK     = (180, 60, 130)
PALE_RED      = (255, 150, 150)
PALE_ORANGE   = (255, 200, 150)
PALE_YELLOW   = (255, 245, 160)
PALE_GREEN    = (180, 240, 170)
PALE_CYAN     = (180, 245, 250)
PALE_BLUE     = (180, 200, 255)
PALE_PURPLE   = (215, 180, 255)
PALE_PINK     = (255, 200, 230)
GOLD_HI       = (255, 230, 120)
GOLD_MID      = (240, 185, 70)
GOLD_DARK     = (180, 125, 40)
ROCK_DARK     = (50, 30, 70)
ROCK_MID      = (85, 55, 100)
WHITE         = (255, 255, 255)

RAINBOW      = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, MAGENTA, PINK]
DARK_RAINBOW = [DARK_RED, DARK_ORANGE, DARK_YELLOW, DARK_GREEN, DARK_CYAN, DARK_BLUE, DARK_PURPLE, DARK_MAGENTA, DARK_PINK]
PALE_RAINBOW = [PALE_RED, PALE_ORANGE, PALE_YELLOW, PALE_GREEN, PALE_CYAN, PALE_BLUE, PALE_PURPLE, (255,180,230), PALE_PINK]

img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
PX = img.load()

def put(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        PX[x, y] = c + (255,)

def getc(x, y):
    if 0 <= x < W and 0 <= y < H:
        return PX[x, y]
    return (0, 0, 0, 0)

# ── Geometry: rectangular doorway with separate crown bar ─
FRAME_TOP   = 16
FRAME_BOT   = 90
OUTER_L     = 24
OUTER_R     = 56
INNER_L     = 30
INNER_R     = 50
CROWN_Y     = 11           # vertical centre of the crown bar
CROWN_HALF  = 2
CROWN_L     = 19
CROWN_R     = 61
GEM_CX      = 40
GEM_CY      = 6
CRYSTAL_Y   = 52           # mid-leg cyan crystals
PUDDLE_OFF  = 3            # vertical drop below FRAME_BOT for puddles
LEFT_FOOT   = (OUTER_L + INNER_L) // 2     # 27
RIGHT_FOOT  = (OUTER_R + INNER_R) // 2     # 53

# ── Fill the frame body with a dithered rainbow ───────
def frame_color(x, y):
    # Vertical rainbow on the leg sections, with per-pixel dithering.
    t = (y - FRAME_TOP) / max(1, FRAME_BOT - FRAME_TOP)   # 0..1
    base = t * 8                                          # 0..8 (across RAINBOW)
    r = random.random()
    if   r < 0.55: idx = base + (random.random() - 0.5) * 0.6     # base hue
    elif r < 0.78: idx = base + (random.random() - 0.5) * 2.2     # nearby hue
    elif r < 0.90:
        # dark accent
        i = max(0, min(8, int(base + (random.random() - 0.5))))
        return DARK_RAINBOW[i]
    elif r < 0.96:
        # bright/pale accent
        i = max(0, min(8, int(base + (random.random() - 0.5))))
        return PALE_RAINBOW[i]
    else:
        return BLACK                                       # speckle wear
    i = max(0, min(8, int(idx)))
    return RAINBOW[i]

for y in range(FRAME_TOP, FRAME_BOT + 1):
    for x in range(OUTER_L, OUTER_R + 1):
        if INNER_L < x < INNER_R:                          # leave the opening empty
            continue
        put(x, y, frame_color(x, y))

# ── Hot-pink neon rim around the entire opening ───────
for y in range(FRAME_TOP, FRAME_BOT + 1):
    put(INNER_L, y, HOT_PINK)
    put(INNER_R, y, HOT_PINK)
for x in range(INNER_L, INNER_R + 1):
    put(x, FRAME_TOP, HOT_PINK)
# soft pink secondary glow line, one pixel inside
for y in range(FRAME_TOP + 1, FRAME_BOT + 1):
    put(INNER_L + 1, y, PINK)
    put(INNER_R - 1, y, PINK)
for x in range(INNER_L + 1, INNER_R):
    put(x, FRAME_TOP + 1, PINK)

# ── Crown bar on top (wider than the frame, with knob ends) ─
for y in range(CROWN_Y - CROWN_HALF, CROWN_Y + CROWN_HALF + 1):
    for x in range(CROWN_L, CROWN_R + 1):
        if abs(x - GEM_CX) <= 3 and y < CROWN_Y + 1:       # carve out gem area
            continue
        h_pos = (x - CROWN_L) / max(1, CROWN_R - CROWN_L)
        i = int(h_pos * 8)
        r = random.random()
        if   r < 0.55: col = RAINBOW[max(0, min(8, i))]
        elif r < 0.78: col = DARK_RAINBOW[max(0, min(8, i))]
        elif r < 0.92: col = PALE_RAINBOW[max(0, min(8, i))]
        else:          col = BLACK
        put(x, y, col)

# Decorative magenta knobs at the ends of the crown bar
for kx in (CROWN_L - 2, CROWN_R + 2):
    put(kx, CROWN_Y - 1, PINK)
    put(kx, CROWN_Y,     MAGENTA)
    put(kx, CROWN_Y + 1, HOT_PINK)
    put(kx + (1 if kx == CROWN_L - 2 else -1), CROWN_Y, PINK)

# ── Flame gem on the crown ────────────────────────────
def draw_gem():
    # small flame/teardrop shape, red/orange/yellow
    put(GEM_CX,     GEM_CY - 2, YELLOW)
    put(GEM_CX,     GEM_CY - 1, ORANGE)
    put(GEM_CX - 1, GEM_CY - 1, RED)
    put(GEM_CX + 1, GEM_CY - 1, RED)
    put(GEM_CX - 1, GEM_CY,     ORANGE)
    put(GEM_CX,     GEM_CY,     YELLOW)
    put(GEM_CX + 1, GEM_CY,     ORANGE)
    put(GEM_CX - 1, GEM_CY + 1, RED)
    put(GEM_CX,     GEM_CY + 1, RED)
    put(GEM_CX + 1, GEM_CY + 1, RED)
    put(GEM_CX,     GEM_CY + 2, DARK_RED)
    # tiny black silhouette inside (the reference shows a small figure)
    put(GEM_CX,     GEM_CY + 3, BLACK)
draw_gem()

# ── Cyan diamond crystals embedded mid-leg ────────────
def draw_crystal(cx, cy):
    put(cx,     cy - 2, CYAN)
    put(cx - 1, cy - 1, CYAN); put(cx,     cy - 1, PALE_CYAN); put(cx + 1, cy - 1, CYAN)
    put(cx - 2, cy,     CYAN); put(cx - 1, cy,     PALE_CYAN); put(cx, cy, WHITE)
    put(cx + 1, cy,     PALE_CYAN); put(cx + 2, cy,     CYAN)
    put(cx - 1, cy + 1, CYAN); put(cx,     cy + 1, PALE_CYAN); put(cx + 1, cy + 1, CYAN)
    put(cx,     cy + 2, CYAN)
    # small dark outline points
    put(cx,     cy - 3, DARK_CYAN)
    put(cx,     cy + 3, DARK_CYAN)
    put(cx - 3, cy,     DARK_CYAN)
    put(cx + 3, cy,     DARK_CYAN)

draw_crystal((OUTER_L + INNER_L) // 2, CRYSTAL_Y)
draw_crystal((OUTER_R + INNER_R) // 2, CRYSTAL_Y)

# ── Gold puddles dripping at the base of each leg ─────
def puddle(cx, cy):
    for dy in range(-1, 4):
        for dx in range(-5, 6):
            ndx = abs(dx) / 5
            ndy = (dy + 0.5) / 3
            if ndx * ndx + ndy * ndy * 0.7 > 1:
                continue
            col = GOLD_HI if (ndx < 0.4 and dy < 2) else \
                  GOLD_MID if ndx < 0.75 else GOLD_DARK
            put(cx + dx, cy + dy, col)

puddle(LEFT_FOOT,  FRAME_BOT + PUDDLE_OFF)
puddle(RIGHT_FOOT, FRAME_BOT + PUDDLE_OFF)

# small drip pattern between the two puddles
drip_y = FRAME_BOT + PUDDLE_OFF + 1
for dx in range(LEFT_FOOT + 6, RIGHT_FOOT - 5, 3):
    put(dx,     drip_y,     GOLD_HI)
    put(dx + 1, drip_y,     GOLD_MID)

# ── Dark rocks at the outer base corners ──────────────
def rock(cx, cy):
    pts = [(0,0),(1,0),(-1,0),(2,0),(0,1),(1,1),(-1,1),(2,1),(3,1),
           (1,-1),(0,-1),(-1,-1)]
    for dx, dy in pts:
        put(cx + dx, cy + dy, ROCK_MID if dy < 0 else ROCK_DARK)
rock(OUTER_L - 4, FRAME_BOT + PUDDLE_OFF + 1)
rock(OUTER_R + 4, FRAME_BOT + PUDDLE_OFF + 1)

# ── Many sparkles scattered in the void around the portal ─
sparkles = [
    # (x, y, colour, plus/star)
    ( 6,16, YELLOW, 1), (74,14, YELLOW, 1), ( 4,28, CYAN, 1), (76,30, CYAN, 1),
    (10,42, PALE_CYAN, 0), (70,44, PALE_CYAN, 0), ( 6,56, HOT_PINK, 0),
    (74,58, HOT_PINK, 0), (12,70, YELLOW, 1), (68,72, YELLOW, 1),
    ( 2,82, PINK, 0), (78,84, MAGENTA, 0), (20, 2, YELLOW, 1), (60, 2, CYAN, 1),
    (12, 6, MAGENTA, 0), (68, 7, PINK, 0), (15,96, CYAN, 0), (65,98, YELLOW, 1),
    ( 3,50, WHITE, 0), (77,68, WHITE, 0), ( 8,100, PINK, 0), (72,102, CYAN, 0),
    (15,22, RED, 0), (65,25, ORANGE, 0), (16,86, MAGENTA, 0), (64,88, HOT_PINK, 0),
    ( 9,38, WHITE, 0), (71,52, WHITE, 0), (14,12, ORANGE, 0), (66,11, GREEN, 0),
    (18, 8, CYAN, 0), (62, 9, YELLOW, 0), (11,76, WHITE, 0), (69,79, PINK, 0),
    (22,90, YELLOW, 0), (58,90, CYAN, 0), ( 5,72, HOT_PINK, 0), (75,75, MAGENTA, 0),
]
for x, y, col, plus in sparkles:
    if getc(x, y)[3] != 0:
        continue
    put(x, y, col)
    if plus:                                                # 4-point star
        if getc(x + 1, y)[3] == 0: put(x + 1, y, col)
        if getc(x - 1, y)[3] == 0: put(x - 1, y, col)
        if getc(x, y + 1)[3] == 0: put(x, y + 1, col)
        if getc(x, y - 1)[3] == 0: put(x, y - 1, col)

# ── Save ──────────────────────────────────────────────
os.makedirs('output', exist_ok=True)
img.resize((W * SCALE, H * SCALE), Image.NEAREST).save('output/rainbow_portal.png')
print('wrote output/rainbow_portal.png', (W * SCALE, H * SCALE))
