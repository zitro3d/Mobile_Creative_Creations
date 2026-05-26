#!/usr/bin/env python3
"""Phase 1 — static magical stone portal (traced to the red drawing).

125x250 logical RGBA -> 8x NEAREST -> output/portal_static.png (1000x2000).

Shape follows the red sketch: an ASYMMETRIC, leaning archway. The left
pillar is thin and nearly straight; the right pillar is much thicker and
reads as a receding 3D column in 3/4 perspective, with three banded
rings that protrude outward to the right. A tilted capstone cylinder and
a round orb cap the arch point. The pointed opening widens slightly down
to the floor. Interior glow uses an edge-distance transform (pink rim
hugs the arch, dark void elongates down the center). One palette color
per pixel, no anti-aliasing.
"""
import os, math
from collections import deque
from PIL import Image

W, H, SCALE = 125, 250, 8

# ── Locked palette ────────────────────────────────────
DEEP_PURPLE = (58, 38, 75)
PURPLE      = (92, 64, 110)
LAVENDER    = (140, 105, 155)
HOT_PINK    = (235, 110, 180)
SOFT_PINK   = (255, 170, 215)
CYAN        = (130, 200, 245)
PALE_CYAN   = (200, 235, 255)
DEEP_BLUE   = (60, 75, 165)
DARK_VOID   = (35, 40, 95)
WHITE       = (255, 255, 255)

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

# ── Traced edges (x, y), top→bottom; piecewise-linear ──
# Left outer (thin pillar, leans in then near-vertical):
LO = [(53,33),(48,38),(42,44),(36.5,62),(31,88),(28,119),
      (26.7,156),(26,194),(27,222),(29,236)]
# Left inner (left side of the opening):
LI = [(58,55),(53,61),(46,81),(42,112),(39.6,150),(38.5,188),(39,216),(40,236)]
# Right inner (right side of the opening):
RI = [(60,55),(63,58),(67,81),(71,119),(74,156),(76,194),(77.5,222),(79,236)]
# Right outer (thick pillar, sweeps out, leans right):
RO = [(64,33),(71,34.5),(81,53),(92,81),(97,112),(99,150),
      (100,188),(102,225),(102,236)]

def edge(pts, y):
    if y < pts[0][1] or y > pts[-1][1]:
        return None
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        if y0 <= y <= y1:
            if y1 == y0:
                return x0
            t = (y - y0) / (y1 - y0)
            return x0 + t * (x1 - x0)
    return None

CROWN_TOP = 33
WALL = 4                              # right inner-wall reveal (depth face)

# ── Stone front face + opening + right inner wall ─────
for y in range(H):
    lo = edge(LO, y)
    ro = edge(RO, y)
    if lo is None or ro is None:
        continue
    ol, orr = int(math.floor(lo)), int(math.ceil(ro))
    li = edge(LI, y)
    ri = edge(RI, y)
    if li is None or ri is None:
        for x in range(ol, orr + 1):     # solid arch crown / sill
            put(x, y, PURPLE)
        continue
    ilo = int(math.ceil(li))
    iro = int(math.floor(ri))
    for x in range(ol, orr + 1):
        if x < ilo:
            put(x, y, PURPLE)            # left wall (front face)
        elif x > iro:
            if x <= iro + WALL:
                put(x, y, DEEP_PURPLE)   # receding inner-wall reveal
            else:
                put(x, y, PURPLE)        # right wall (front face)
        # opening (ilo..iro) left for the glow pass

# ── Interior glow — edge-distance transform ───────────
mask = [[False] * W for _ in range(H)]
for y in range(H):
    li = edge(LI, y)
    ri = edge(RI, y)
    if li is None or ri is None:
        continue
    for x in range(int(math.ceil(li)), int(math.floor(ri)) + 1):
        if 0 <= x < W:
            mask[y][x] = True

INF = 10 ** 9
dist = [[INF] * W for _ in range(H)]
dq = deque()
for y in range(H):
    for x in range(W):
        if not mask[y][x]:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= W or ny < 0 or ny >= H or not mask[ny][nx]:
                dist[y][x] = 1
                dq.append((x, y))
                break
while dq:
    x, y = dq.popleft()
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < W and 0 <= ny < H and mask[ny][nx] and dist[ny][nx] == INF:
            dist[ny][nx] = dist[y][x] + 1
            dq.append((nx, ny))

def ring_by_dist(d):
    if d <= 2:  return HOT_PINK
    if d <= 4:  return SOFT_PINK
    if d <= 7:  return PALE_CYAN
    if d <= 12: return CYAN
    if d <= 19: return DEEP_BLUE
    return DARK_VOID

for y in range(H):
    for x in range(W):
        if mask[y][x]:
            put(x, y, ring_by_dist(dist[y][x]))

# ── Stone outline against transparency ────────────────
stone = [(x, y) for y in range(H) for x in range(W) if get(x, y) == PURPLE + (255,)]
for (x, y) in stone:
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if get(x + dx, y + dy)[3] == 0:
            put(x, y, DEEP_PURPLE)
            break

# ── LAVENDER highlight on the lit (left) outer edge ───
for y in range(H):
    lo = edge(LO, y)
    if lo is None:
        continue
    ol = int(math.floor(lo))
    run = 0
    for x in range(ol, ol + 12):
        if get(x, y)[:3] == PURPLE:
            put(x, y, LAVENDER)
            run += 1
            if run >= 2:
                break
        elif run:
            break

# ── Banded rings on the thick right pillar (protrude) ─
def draw_band(cy):
    ri = edge(RI, cy)
    ro = edge(RO, cy)
    if ri is None or ro is None:
        return
    sx = int(math.floor(ri)) + 1
    ex = int(math.ceil(ro)) + 7          # stick out past the outer edge
    span = max(1, ex - sx)
    half = 3
    for x in range(sx, ex + 1):
        f = (x - sx) / span
        drop = int(round(f * 3))         # tilt down toward the far end
        # rounded ends
        h = half if f < 0.85 else half - 1
        if x == ex:
            h = half - 2
        top = cy - h + drop
        bot = cy + h + drop
        for yy in range(top, bot + 1):
            base = get(x, yy)
            stick_out = x > int(math.ceil(ro))
            if base[3] != 0 or stick_out:
                put(x, yy, PURPLE)
        put(x, top, LAVENDER)
        put(x, bot, DEEP_PURPLE)
        put(x, bot + 1, DEEP_PURPLE)
for cy in (76, 133, 194):
    draw_band(cy)

# ── Faint banding ticks down the left pillar edge ─────
for ty in range(70, 232, 20):
    lo = edge(LO, ty)
    li = edge(LI, ty)
    if lo is None or li is None:
        continue
    ol = int(math.floor(lo))
    il = int(math.ceil(li))
    for x in range(ol + 1, il):
        if get(x, ty)[:3] in (PURPLE, LAVENDER):
            put(x, ty, DEEP_PURPLE)
        if get(x, ty - 1)[:3] == PURPLE:
            put(x, ty - 1, LAVENDER)

# ── Capstone cylinder + orb, seated on the arch point ─
def draw_capstone():
    x0, y0 = 51, 30
    x1, y1 = 79, 35                       # tilted: right end lower
    span = x1 - x0
    for x in range(x0, x1 + 1):
        f = (x - x0) / span
        cyf = y0 + f * (y1 - y0)
        h = 4 if 0.08 < f < 0.92 else 3
        cy = int(round(cyf))
        for yy in range(cy - h, cy + h + 1):
            put(x, yy, PURPLE)
        put(x, cy - h, LAVENDER)
        put(x, cy - h + 1, LAVENDER)
        put(x, cy + h, DEEP_PURPLE)
        put(x, cy + h + 1, DEEP_PURPLE)
    # round orb tucked at the upper-left of the capstone
    ox, oy, orad = 46, 40, 6
    for dy in range(-orad, orad + 1):
        for dx in range(-orad, orad + 1):
            if dx * dx + dy * dy <= orad * orad:
                put(ox + dx, oy + dy, PURPLE)
    for dy in range(-orad, orad + 1):
        for dx in range(-orad, orad + 1):
            r2 = dx * dx + dy * dy
            if r2 <= orad * orad and dx + dy < -3:
                put(ox + dx, oy + dy, LAVENDER)
            elif r2 <= orad * orad and dx + dy > 4:
                put(ox + dx, oy + dy, DEEP_PURPLE)
    put(ox - 2, oy - 3, PALE_CYAN)
draw_capstone()

# ── Pillar feet — small mossy stone base ──────────────
def draw_feet():
    for (pts_o, pts_i) in ((LO, LI), (RI, RO)):
        eo = edge(pts_o, 235)
        ei = edge(pts_i, 235)
        if eo is None or ei is None:
            continue
        a, b = sorted((int(round(eo)), int(round(ei))))
        for yy in range(234, H):
            for x in range(a - 2, b + 3):
                put(x, yy, DEEP_PURPLE)
draw_feet()

# ── Ground light spill below the opening ──────────────
def draw_ground_spill():
    cx, cy = 58, 240
    rw, rh = 20, 4
    for dy in range(-rh, rh + 1):
        for dx in range(-rw, rw + 1):
            nd = (dx / rw) ** 2 + (dy / rh) ** 2
            if nd > 1.0:
                continue
            if nd > 0.5 and ((dx + dy) % 2 == 0):
                continue
            put(cx + dx, cy + dy, PALE_CYAN)
draw_ground_spill()

# ── Cracks / overgrowth (hand-placed) ─────────────────
CRACKS = [(33,100),(30,150),(28,190),(31,210),(40,60),
          (96,95),(99,140),(101,175),(99,205),(72,45),
          (35,70),(85,55),(34,228),(98,232)]
MOSS = [(31,118),(29,168),(98,120),(100,198),(78,50),
        (33,218),(101,100),(27,145)]
for (x, y) in CRACKS:
    if get(x, y)[3] != 0 and get(x, y)[:3] in (PURPLE, LAVENDER):
        put(x, y, DEEP_PURPLE)
for (x, y) in MOSS:
    if get(x, y)[3] != 0 and get(x, y)[:3] in (PURPLE, LAVENDER, DEEP_PURPLE):
        put(x, y, HOT_PINK)

# ── Upscale + save ────────────────────────────────────
os.makedirs('output', exist_ok=True)
big = img.resize((W * SCALE, H * SCALE), Image.NEAREST)
big.save('output/portal_static.png')
print('wrote output/portal_static.png', big.size)
