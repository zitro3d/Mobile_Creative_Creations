#!/usr/bin/env python3
"""Rainbow portal — single static frame, stout sturdy doorway.

A SINGLE continuous frame: top horizontal bar + vertical side pillars +
flared bottom pedestals are all one connected silhouette. Smooth
rainbow gradient flows top-down (warm red/pink at the top → green/cyan
across the middle → blue/purple at the base). The interior opening is
SOLID pure black with a hot-pink neon rim. Scattered sparkles around
the frame in the surrounding void.

Logical 100x92 -> 12x NEAREST -> 1200x1104, transparent background.
"""
import os
from PIL import Image

W, H, SCALE = 100, 92, 12

# ── Palette ───────────────────────────────────────────
# 19-step smooth rainbow ladder, warm-on-top → cool-at-base
COLORS = [
    (255, 110, 150),  # pink top
    (255, 75, 100),   # red-pink
    (240, 60, 70),    # red
    (250, 100, 65),   # red-orange
    (250, 140, 60),   # orange
    (252, 185, 70),   # orange-yellow
    (255, 220, 80),   # yellow
    (210, 230, 80),   # yellow-green
    (155, 225, 95),   # light green
    (110, 220, 110),  # green
    (80, 220, 165),   # green-cyan
    (75, 220, 220),   # cyan
    (80, 180, 235),   # cyan-blue
    (90, 130, 240),   # blue
    (120, 90, 235),   # blue-purple
    (160, 80, 230),   # purple
    (130, 60, 180),   # mid-purple
    (80, 40, 130),    # dark-purple
    (50, 25, 80),     # deep-purple (base)
]

BLACK_PURE = (0, 0, 0)
HOT_PINK   = (255, 70, 175)
PINK       = (255, 130, 200)
MAGENTA    = (225, 95, 200)
WHITE      = (255, 255, 255)
YELLOW     = (255, 220, 80)
ORANGE     = (250, 140, 60)
RED        = (240, 60, 70)
DARK_RED   = (140, 30, 55)
CYAN       = (75, 220, 220)
PALE_CYAN  = (180, 245, 250)

# ── Geometry: stout sturdy doorway (wider than tall) ──
FRAME_TOP   = 6
PED_TOP     = 74            # where the leg flares into the pedestal
FRAME_BOT   = 84            # bottom of the pedestals
OUTER_L     = 14            # outer pillar left
OUTER_R     = 86            # outer pillar right
PED_L       = 8             # outermost x of the flared pedestal
PED_R       = 92
INNER_L     = 28            # opening left edge
INNER_R     = 72            # opening right edge
INNER_TOP   = 20            # opening starts under the top bar
GEM_CX      = W // 2
GEM_CY      = FRAME_TOP + 6

img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
PX = img.load()

def put(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        PX[x, y] = c + (255,)

def getc(x, y):
    if 0 <= x < W and 0 <= y < H:
        return PX[x, y]
    return (0, 0, 0, 0)

def frame_outer(y):
    """Outer (left, right) of the frame silhouette at row y. The pedestal
    section linearly flares OUTWARD so it's part of one continuous shape."""
    if y < FRAME_TOP or y > FRAME_BOT:
        return None
    if y >= PED_TOP:
        t  = (y - PED_TOP) / max(1, FRAME_BOT - PED_TOP)
        lo = int(round(OUTER_L - t * (OUTER_L - PED_L)))
        ro = int(round(OUTER_R + t * (PED_R - OUTER_R)))
        return (lo, ro)
    return (OUTER_L, OUTER_R)

def in_opening(x, y):
    return INNER_L <= x <= INNER_R and y >= INNER_TOP

# ── Fill the connected frame body with the smooth rainbow ─
for y in range(FRAME_TOP, FRAME_BOT + 1):
    bounds = frame_outer(y)
    if bounds is None:
        continue
    lo, ro = bounds
    t = (y - FRAME_TOP) / max(1, FRAME_BOT - FRAME_TOP)
    col = COLORS[max(0, min(len(COLORS) - 1, int(t * len(COLORS))))]
    for x in range(lo, ro + 1):
        if in_opening(x, y):
            continue
        put(x, y, col)

# ── Solid pure-black portal void ──────────────────────
for y in range(INNER_TOP, FRAME_BOT + 1):
    for x in range(INNER_L, INNER_R + 1):
        put(x, y, BLACK_PURE)

# ── Hot-pink neon rim around the opening ──────────────
for y in range(INNER_TOP, FRAME_BOT + 1):
    put(INNER_L, y, HOT_PINK)
    put(INNER_R, y, HOT_PINK)
for x in range(INNER_L, INNER_R + 1):
    put(x, INNER_TOP, HOT_PINK)

# ── Small flame gem set into the top bar ──────────────
put(GEM_CX,     GEM_CY - 2, YELLOW)
put(GEM_CX,     GEM_CY - 1, ORANGE)
put(GEM_CX - 1, GEM_CY,     ORANGE)
put(GEM_CX,     GEM_CY,     RED)
put(GEM_CX + 1, GEM_CY,     ORANGE)
put(GEM_CX,     GEM_CY + 1, DARK_RED)

# ── Cyan crystal accents embedded mid-pillar ──────────
def crystal(cx, cy):
    put(cx,     cy - 1, CYAN)
    put(cx - 1, cy,     CYAN)
    put(cx,     cy,     WHITE)
    put(cx + 1, cy,     CYAN)
    put(cx,     cy + 1, CYAN)
crystal((OUTER_L + INNER_L) // 2, 50)
crystal((OUTER_R + INNER_R) // 2, 50)

# ── Sparkles in the surrounding void ──────────────────
sparkles = [
    ( 5,14, YELLOW, 1), (95,12, YELLOW, 1), ( 3,30, CYAN, 1),  (97,32, CYAN, 1),
    ( 6,48, PINK, 0),   (94,46, PINK, 0),   ( 4,64, WHITE, 0), (96,66, WHITE, 0),
    ( 2,78, YELLOW, 0), (98,80, YELLOW, 0), (22, 2, YELLOW, 1),(78, 2, CYAN, 1),
    (40, 2, MAGENTA,0), (60, 2, PINK, 0),   (12,88, WHITE, 0), (88,90, WHITE, 0),
    (45,90, CYAN, 0),   (55,90, MAGENTA,0), ( 2,50, WHITE, 0), (98,22, WHITE, 0),
    (15, 8, MAGENTA,0), (85, 6, PINK, 0),   (10, 2, YELLOW,0), (90, 2, CYAN, 0),
    (50,91, PINK, 0),   ( 8,36, PALE_CYAN,0),(92,38, PALE_CYAN,0),
    (14,70, ORANGE,0),  (86,72, ORANGE,0),  ( 7,22, MAGENTA,0),(93,58, YELLOW,0),
    (50, 0, PALE_CYAN,0),(30, 1, WHITE, 0), (70, 1, WHITE, 0),
]
for x, y, col, plus in sparkles:
    if getc(x, y)[3] != 0:
        continue
    put(x, y, col)
    if plus:
        if getc(x + 1, y)[3] == 0: put(x + 1, y, col)
        if getc(x - 1, y)[3] == 0: put(x - 1, y, col)
        if getc(x, y + 1)[3] == 0: put(x, y + 1, col)
        if getc(x, y - 1)[3] == 0: put(x, y - 1, col)

# ── Save ──────────────────────────────────────────────
os.makedirs('output', exist_ok=True)
img.resize((W * SCALE, H * SCALE), Image.NEAREST).save('output/rainbow_portal.png')
print('wrote output/rainbow_portal.png', (W * SCALE, H * SCALE))
