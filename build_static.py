#!/usr/bin/env python3
"""Phase 1 — static magical stone portal (recessed archway, WIDE, polished).

160x250 logical RGBA -> 8x NEAREST -> output/portal_static.png (1280x2000).

A production-clean asymmetric stone archway in 3/4 perspective:
  * straight vertical legs joined by a TRUE elliptical rounded crown
    (no needle apex);
  * single light source from the upper-left — lit edges LAVENDER, the
    shadow/receding side DEEP_PURPLE;
  * thin left pillar, thick right pillar shaded as a receding 3D column;
  * the opening is a RECESSED doorway: a lit front lip steps back to a
    shaded soffit (top) + thick right jamb (the receding inner wall),
    then the magical glow sits deepest;
  * tilted capstone + orb cap the crown; three clean banded rings wrap
    the right pillar.
One palette color per pixel, no anti-aliasing. Transparent background,
ready for compositing.
"""
import os, math
from collections import deque
from PIL import Image

W, H, SCALE = 160, 250, 8

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

def is3(x, y, c):
    return get(x, y)[:3] == c

# ── Geometry: straight legs + elliptical rounded crown ─
Y_S   = 96         # springline: legs below, rounded crown above
Y_BOT = 238        # legs end here (small feet drawn below)

# Legs as (x_top@Y_S, x_bot@Y_BOT); slight lean = perspective.
LO = (40, 30)      # left outer  (thin pillar)
LI = (58, 50)      # left inner
RI = (104, 112)    # right inner
RO = (132, 144)    # right outer (thick pillar)

def leg_x(p, y):
    t = (y - Y_S) / (Y_BOT - Y_S)
    return p[0] + (p[1] - p[0]) * t

# Crown ellipses meet the leg tops at Y_S (seamless junction).
CX_O, A_O, B_O = 86, 46, 58   # outer dome, apex y = Y_S-B_O = 38
CX_I, A_I, B_I = 81, 23, 46   # inner dome, apex y = Y_S-B_I = 50 (opening shifted left)

def dome(cx, a, b, y):
    dy = Y_S - y
    if dy < 0 or dy > b:
        return None
    s = a * math.sqrt(max(0.0, 1 - (dy / b) ** 2))
    return (cx - s, cx + s)

def outer_b(y):
    return (leg_x(LO, y), leg_x(RO, y)) if y >= Y_S else dome(CX_O, A_O, B_O, y)

def inner_b(y):
    return (leg_x(LI, y), leg_x(RI, y)) if y >= Y_S else dome(CX_I, A_I, B_I, y)

# ── Recess depth (gives the 3D feel) ──────────────────
TOP_REV = 19       # soffit depth across the top (vertical)
R_REV   = 16       # right jamb depth — thick, faces us
L_REV   = 3        # left jamb faces away → barely shows

# ── Front stone face + the arched hole ────────────────
front = [[False] * W for _ in range(H)]
for y in range(H):
    ob = outer_b(y)
    if ob is None:
        continue
    ol, orr = int(math.floor(ob[0])), int(math.ceil(ob[1]))
    ib = inner_b(y)
    if ib is None:
        for x in range(ol, orr + 1):          # solid crown
            put(x, y, PURPLE)
        continue
    ilo, iro = int(math.ceil(ib[0])), int(math.floor(ib[1]))
    for x in range(ol, orr + 1):
        if x < ilo or x > iro:
            put(x, y, PURPLE)
        else:
            front[y][x] = True

# topmost open row per column (front-top rim — the soffit springs here)
top_y = [None] * W
for x in range(W):
    for y in range(H):
        if front[y][x]:
            top_y[x] = y
            break

# ── Split the hole into reveal (receding walls) + void ─
back = [[False] * W for _ in range(H)]
reveal_depth = [[0] * W for _ in range(H)]
for y in range(H):
    ib = inner_b(y)
    if ib is None:
        continue
    ilo, iro = int(math.ceil(ib[0])), int(math.floor(ib[1]))
    for x in range(ilo, iro + 1):
        if not front[y][x]:
            continue
        dr = iro - x
        dl = x - ilo
        dt = y - top_y[x]
        if dr >= R_REV and dl >= L_REV and dt >= TOP_REV:
            back[y][x] = True
        else:
            reveal_depth[y][x] = min(dr, dl, dt) + 1

for y in range(H):
    for x in range(W):
        d = reveal_depth[y][x]
        if d == 0:
            continue
        if d <= 1:
            put(x, y, LAVENDER)       # lit front lip
        elif d <= 4:
            put(x, y, PURPLE)
        else:
            put(x, y, DEEP_PURPLE)    # deep in the recess

# ── Interior glow — edge-distance transform on the void ─
INF = 10 ** 9
dist = [[INF] * W for _ in range(H)]
dq = deque()
for y in range(H):
    for x in range(W):
        if not back[y][x]:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= W or ny < 0 or ny >= H or not back[ny][nx]:
                dist[y][x] = 1
                dq.append((x, y))
                break
while dq:
    x, y = dq.popleft()
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < W and 0 <= ny < H and back[ny][nx] and dist[ny][nx] == INF:
            dist[ny][nx] = dist[y][x] + 1
            dq.append((nx, ny))

def ring_by_dist(d):
    if d <= 4:  return HOT_PINK
    if d <= 8:  return SOFT_PINK
    if d <= 14: return PALE_CYAN
    if d <= 22: return CYAN
    return DEEP_BLUE          # broad calm core — no thin dark needle

for y in range(H):
    for x in range(W):
        if back[y][x]:
            put(x, y, ring_by_dist(dist[y][x]))

# ── Round the right pillar: shadow strip on the outer face ─
for y in range(Y_S, Y_BOT + 1):
    ro = leg_x(RO, y)
    for x in range(int(round(ro)) - 5, int(round(ro)) + 1):
        if is3(x, y, PURPLE):
            put(x, y, DEEP_PURPLE)
for y in range(38, Y_S):                       # crown right shoulder shadow
    ob = outer_b(y)
    if ob is None:
        continue
    orr = ob[1]
    for x in range(int(round(orr)) - 5, int(round(orr)) + 1):
        if is3(x, y, PURPLE):
            put(x, y, DEEP_PURPLE)

# ── Stone outline against transparency ────────────────
stone = [(x, y) for y in range(H) for x in range(W) if is3(x, y, PURPLE)]
for (x, y) in stone:
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if get(x + dx, y + dy)[3] == 0:
            put(x, y, DEEP_PURPLE)
            break

# ── LAVENDER highlight on the lit (left) outer edge ───
for y in range(H):
    ob = outer_b(y)
    if ob is None:
        continue
    ol = int(math.floor(ob[0]))
    run = 0
    for x in range(ol, ol + 16):
        if is3(x, y, PURPLE):
            put(x, y, LAVENDER)
            run += 1
            if run >= 3:
                break
        elif run:
            break

# ── Three clean banded rings on the right pillar ──────
def draw_band(cy):
    ri = leg_x(RI, cy)
    ro = leg_x(RO, cy)
    sx = int(round(ri)) + R_REV - 1        # bite into the jamb edge
    ex = int(round(ro)) + 9                # protrude past the outer edge
    span = max(1, ex - sx)
    half = 4
    for x in range(sx, ex + 1):
        f = (x - sx) / span
        drop = int(round(f * 3))           # tilt down toward far end (perspective)
        h = half if f < 0.9 else half - 1
        top = cy - h + drop
        bot = cy + h + drop
        for yy in range(top, bot + 1):
            if get(x, yy)[3] != 0 or x > int(round(ro)):
                put(x, yy, PURPLE)
        put(x, top, LAVENDER)
        put(x, top + 1, LAVENDER)
        put(x, bot, DEEP_PURPLE)
        put(x, bot + 1, DEEP_PURPLE)
    # tuck the inner end under the front face cleanly
    put(sx, cy - half + 1, DEEP_PURPLE)
for cy in (128, 165, 202):
    draw_band(cy)

# ── Tilted capstone + orb, seated solidly on the crown ─
def draw_capstone():
    x0, y0 = 58, 30
    x1, y1 = 118, 38
    span = x1 - x0
    bar_bottom = {}
    for x in range(x0, x1 + 1):
        f = (x - x0) / span
        cy = int(round(y0 + f * (y1 - y0)))
        h = 4 if 0.06 < f < 0.94 else 3
        for yy in range(cy - h, cy + h + 1):
            put(x, yy, PURPLE)
        put(x, cy - h, LAVENDER)
        put(x, cy - h + 1, LAVENDER)
        put(x, cy + h, DEEP_PURPLE)
        bar_bottom[x] = cy + h
    # Fill the spandrel gap between the flat bar and the rounded crown so
    # the top reads as one solid mass (no floating pieces).
    for x in range(x0, x1 + 1):
        y = bar_bottom[x] + 1
        while y < 68 and get(x, y)[3] == 0:
            put(x, y, PURPLE)
            y += 1
    # Clean spherical orb on the left shoulder, bridging bar to arch.
    ox, oy, r = 60, 46, 7
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                c = PURPLE
                if dx + dy <= -3:
                    c = LAVENDER
                elif dx + dy >= 5:
                    c = DEEP_PURPLE
                put(ox + dx, oy + dy, c)
    put(ox - 3, oy - 3, PALE_CYAN)
    put(ox - 2, oy - 4, WHITE)
draw_capstone()

# Re-clean the top silhouette after seating the capstone/orb/spandrel.
for y in range(0, 70):
    for x in range(W):
        if is3(x, y, PURPLE):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if get(x + dx, y + dy)[3] == 0:
                    put(x, y, DEEP_PURPLE)
                    break

# ── Pillar feet ───────────────────────────────────────
def draw_feet():
    for (pa, pb) in ((LO, LI), (RI, RO)):
        a, b = sorted((int(round(leg_x(pa, Y_BOT))), int(round(leg_x(pb, Y_BOT)))))
        for yy in range(Y_BOT - 1, H):
            for x in range(a - 2, b + 3):
                put(x, yy, DEEP_PURPLE)
draw_feet()

# ── Rivets / studs — dense rows down both outer edges ──
def stud(cx, cy, glow=False):
    if glow:
        body, hi, lo, core = CYAN, PALE_CYAN, DEEP_BLUE, WHITE
    else:
        body, hi, lo, core = PURPLE, LAVENDER, DEEP_PURPLE, LAVENDER
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            if abs(dx) + abs(dy) <= 2:
                put(cx + dx, cy + dy, body)
    put(cx - 1, cy - 1, hi)
    put(cx, cy - 1, hi)
    put(cx + 1, cy + 1, lo)
    put(cx, cy + 1, lo)
    put(cx, cy, core)

i = 0
for y in range(48, 232, 10):
    ob = outer_b(y)
    if ob is None:
        continue
    stud(int(math.floor(ob[0])) + 3, y, glow=(i % 4 == 2))   # left edge
    stud(int(math.ceil(ob[1])) - 4, y, glow=(i % 4 == 0))    # right edge
    i += 1

# ── Alien energy veins glowing through the stone ──────
VEINS = [
    [(46,72),(43,86),(48,100),(42,116),(46,132),(40,148)],   # left pillar
    [(34,162),(30,176),(35,190),(31,206)],
    [(120,78),(127,92),(121,108),(128,124),(122,140)],       # right pillar
    [(141,150),(135,166),(142,182),(137,198),(143,214)],
    [(82,46),(76,54),(84,62),(78,70)],                       # crown
    [(112,60),(118,72),(113,84)],
]
def draw_vein(path):
    first = True
    for k in range(len(path) - 1):
        x0, y0 = path[k]
        x1, y1 = path[k + 1]
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for s in range(steps + 1):
            x = int(round(x0 + (x1 - x0) * s / steps))
            y = int(round(y0 + (y1 - y0) * s / steps))
            if get(x, y)[:3] in (PURPLE, LAVENDER, DEEP_PURPLE):
                put(x, y, HOT_PINK)
                if first:
                    put(x, y, SOFT_PINK)   # bright source nearest the arch
                    first = False
for v in VEINS:
    draw_vein(v)

# ── Intensify the glow — hot core + sparks (alien) ────
for y in range(H):
    xs = [x for x in range(W) if back[y][x]]
    if not xs:
        continue
    cx = sum(xs) // len(xs)
    if dist[y][cx] >= 16:
        put(cx, y, PALE_CYAN)
        put(cx - 1, y, PALE_CYAN)
        if dist[y][cx] >= 22 and y % 3 == 0:
            put(cx, y, WHITE)
SPARKS = [(78,108),(84,150),(80,188),(86,120),(76,168),(82,214),(80,90)]
for (x, y) in SPARKS:
    if back[y][x]:
        put(x, y, WHITE)
        put(x + 1, y, PALE_CYAN)
        put(x, y + 1, PALE_CYAN)

# ── Ground light spill below the opening ──────────────
def draw_ground_spill():
    cx, cy = 81, 243
    rw, rh = 38, 4
    for dy in range(-rh, rh + 1):
        for dx in range(-rw, rw + 1):
            nd = (dx / rw) ** 2 + (dy / rh) ** 2
            if nd > 1.0:
                continue
            if nd > 0.5 and ((dx + dy) % 2 == 0):
                continue
            if get(cx + dx, cy + dy)[3] == 0:
                put(cx + dx, cy + dy, PALE_CYAN)
draw_ground_spill()

# ── Subtle texture: a few clean cracks + moss (on stone) ─
CRACKS = [(22,150),(18,195),(26,80),(140,150),(146,195),(150,120),(120,60)]
MOSS   = [(20,170),(143,170),(60,52),(24,120),(148,150)]
for (x, y) in CRACKS:
    if is3(x, y, PURPLE) or is3(x, y, LAVENDER):
        put(x, y, DEEP_PURPLE)
for (x, y) in MOSS:
    if get(x, y)[:3] in (PURPLE, LAVENDER, DEEP_PURPLE):
        put(x, y, HOT_PINK)

# ── Upscale + save ────────────────────────────────────
os.makedirs('output', exist_ok=True)
big = img.resize((W * SCALE, H * SCALE), Image.NEAREST)
big.save('output/portal_static.png')
print('wrote output/portal_static.png', big.size)
