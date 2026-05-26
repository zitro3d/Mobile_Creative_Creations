#!/usr/bin/env python3
"""Phase 1 — static magical stone portal (matches the red overlay).

125x250 logical RGBA -> 8x NEAREST -> output/portal_static.png (1000x2000).

Shape follows the red drawing: a WIDE, pointed (gothic) arch in 3/4
perspective. The right pillar is markedly thicker and reads as a
receding 3D column — wrap-around bands + rivet studs run down the
sides. Opening is shifted left so the right inner-wall face shows.
Interior glow uses an edge-distance transform (pink rim hugs the arch,
dark void elongates down the center). One palette color per pixel, no
anti-aliasing.
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

# ── Pointed-arch geometry (WIDE, gothic) ──────────────
O_LEFT, O_RIGHT     = 10, 116        # outer span (wide — fills the frame)
O_SPRING, O_BASE    = 126, 244       # pillars run straight below the spring
O_R                 = 113            # arc radius → pointiness
O_SPAN              = O_RIGHT - O_LEFT

def outer_bounds(y):
    if y > O_BASE:
        return None
    if y >= O_SPRING:
        return (O_LEFT, O_RIGHT)
    dy = y - O_SPRING                 # negative above the spring
    disc = O_R * O_R - dy * dy
    if disc < 0:
        return None
    s = math.sqrt(disc)
    lx = O_LEFT + O_R - s             # left arc (center at right spring + R)
    rx = O_RIGHT - O_R + s            # right arc
    if lx >= rx:
        return None                   # above the apex
    return (lx, rx)

# Inner opening = outer shrunk by stone thickness. Right thickness >>
# left → opening shifted left, right pillar thick (3/4 view).
T_LEFT, T_RIGHT = 16, 27
WALL = 5                              # right inner-wall strip (depth face)

def inner_bounds(y):
    ob = outer_bounds(y)
    if ob is None:
        return None
    il = ob[0] + T_LEFT
    ir = ob[1] - T_RIGHT
    if ir - il < 3:
        return None
    return (il, ir)

def opening_span(y):
    ib = inner_bounds(y)
    if ib is None:
        return None
    il = int(math.ceil(ib[0]))
    ir = int(math.floor(ib[1]))
    if ir - il < 3:
        return None
    return il, ir - WALL, ir          # portal [il, pr], wall (pr, ir]

# ── Stone front face + opening + right inner wall ─────
for y in range(H):
    ob = outer_bounds(y)
    if ob is None:
        continue
    ol, orr = int(math.floor(ob[0])), int(math.ceil(ob[1]))
    sp = opening_span(y)
    for x in range(ol, orr + 1):
        if sp and sp[0] <= x <= sp[2]:
            if x > sp[1]:
                put(x, y, DEEP_PURPLE)        # receding inner wall
        else:
            put(x, y, PURPLE)                 # stone front face

# ── Interior glow — edge-distance transform ───────────
mask = [[False] * W for _ in range(H)]
for y in range(H):
    sp = opening_span(y)
    if sp is None:
        continue
    for x in range(sp[0], sp[1] + 1):
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

# ── LAVENDER highlight on the lit (left) edge ─────────
for y in range(H):
    ob = outer_bounds(y)
    if ob is None:
        continue
    ol = int(math.floor(ob[0]))
    run = 0
    for x in range(ol, ol + 10):
        if get(x, y)[:3] == PURPLE:
            put(x, y, LAVENDER)
            run += 1
            if run >= 2:
                break
        elif run:
            break

# ── Wrap-around bands on the right pillar (cylinder) ──
def draw_band(by):
    ob = outer_bounds(by)
    ib = inner_bounds(by)
    if ob is None or ib is None:
        return
    rs = int(math.ceil(ib[1])) + 1
    re = int(math.ceil(ob[1]))
    width = max(1, re - rs)
    for i, x in enumerate(range(rs, re + 1)):
        drop = int(round((i / width) * 2))     # far side droops (cylinder)
        for yy in range(by + drop, by + 5 + drop):
            if get(x, yy)[3] != 0:
                put(x, yy, LAVENDER)
        put(x, by + 5 + drop, DEEP_PURPLE)
        put(x, by + 6 + drop, DEEP_PURPLE)
        if get(x, by + drop)[3] != 0:
            put(x, by + drop, LAVENDER)
for by in (150, 185, 218):
    draw_band(by)

# ── Rivet studs down both outer edges ─────────────────
def draw_rivets():
    for ry in range(138, 236, 15):
        ob = outer_bounds(ry)
        if ob is None:
            continue
        lx = int(math.floor(ob[0]))
        rx = int(math.ceil(ob[1]))
        # left edge rivet
        put(lx + 2, ry, LAVENDER); put(lx + 3, ry, LAVENDER)
        put(lx + 2, ry + 1, PURPLE); put(lx + 3, ry + 1, DEEP_PURPLE)
        # right edge rivet
        put(rx - 3, ry, LAVENDER); put(rx - 2, ry, LAVENDER)
        put(rx - 3, ry + 1, PURPLE); put(rx - 2, ry + 1, DEEP_PURPLE)
draw_rivets()

# ── Keystone crystal — seated at the arch point ───────
def draw_keystone():
    kx, ky = O_LEFT + O_SPAN // 2, 40
    for dy in range(-5, 6):
        for dx in range(-4, 5):
            if abs(dx) / 4.0 + abs(dy) / 5.0 <= 1.0:
                put(kx + dx, ky + dy, CYAN)
    put(kx - 1, ky - 3, WHITE); put(kx - 2, ky - 1, PALE_CYAN); put(kx - 1, ky - 2, PALE_CYAN)
    put(kx, ky, PALE_CYAN)
    put(kx + 1, ky + 2, DEEP_BLUE); put(kx, ky + 3, DEEP_BLUE); put(kx + 2, ky + 1, DEEP_BLUE)
draw_keystone()

# ── Base flare — mossy stone foot (irregular) ─────────
def draw_base_flare():
    ob = outer_bounds(O_BASE)
    ol, orr = int(math.floor(ob[0])), int(math.ceil(ob[1]))
    profile_l = [2, 4, 6, 7, 6, 5, 4]
    profile_r = [3, 6, 8, 9, 8, 6, 5]
    for i in range(7):
        yy = O_BASE - 1 + i
        if yy >= H:
            break
        extl = profile_l[i] + (1 if (i % 2) else 0)
        extr = profile_r[i] + (1 if (i % 3 == 0) else 0)
        for x in range(ol - extl, ol + 10):
            put(x, yy, DEEP_PURPLE)
        for x in range(orr - 9, orr + extr + 1):
            put(x, yy, DEEP_PURPLE)
draw_base_flare()

# ── Ground light spill ────────────────────────────────
def draw_ground_spill():
    cx, cy = (O_LEFT + O_RIGHT) // 2 - 3, O_BASE + 4
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

# ── Cracks / overgrowth ───────────────────────────────
CRACKS = [
    (20, 90), (24, 130), (18, 170), (22, 205), (28, 60),
    (104, 95), (108, 140), (110, 180), (105, 212), (100, 66),
    (40, 46), (86, 48), (30, 228), (96, 230),
]
MOSS = [
    (22, 110), (26, 150), (106, 120), (102, 195), (90, 60),
    (34, 218), (110, 100), (19, 145),
]
for (x, y) in CRACKS:
    if get(x, y)[3] != 0:
        put(x, y, DEEP_PURPLE)
for (x, y) in MOSS:
    if get(x, y)[3] != 0:
        put(x, y, HOT_PINK)

# ── Upscale + save ────────────────────────────────────
os.makedirs('output', exist_ok=True)
big = img.resize((W * SCALE, H * SCALE), Image.NEAREST)
big.save('output/portal_static.png')
print('wrote output/portal_static.png', big.size)
