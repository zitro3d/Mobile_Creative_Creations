#!/usr/bin/env python3
"""Phase 1 — static magical stone portal (traced to the red drawing).

125x250 logical RGBA -> 8x NEAREST -> output/portal_static.png (1000x2000).

Shape follows the red sketch: an ASYMMETRIC, leaning archway seen in
3/4 perspective so you can feel the 3D depth. The opening is a RECESSED
doorway — the front stone face has an arched hole, and through it you
look into the wall's thickness: a lit front lip steps back to a shaded
soffit (top) and a thick right jamb (the receding inner wall), then the
magical glow sits deepest. The left jamb faces away and barely shows.
The left pillar is thin and near-vertical; the right pillar is much
thicker with three banded rings that protrude outward. A tilted capstone
cylinder and a round orb cap the arch point. One palette color per
pixel, no anti-aliasing.
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
# Rounded gothic arch that leans right. Vertical-ish legs curve smoothly
# over the top into a rounded crown (not a sharp point).
# Left outer — thin leg, near-vertical, curves over at the top:
LO = [(60,32),(52,38),(44,48),(36,64),(30,92),(27,130),(26,170),(27,206),(29,236)]
# Front-face inner edges of the arched opening (rounded crown):
LI = [(58,48),(54,52),(50,60),(45,76),(40,100),(37,135),(35,170),(34,200),(35,236)]
RI = [(66,48),(70,52),(74,60),(77,76),(79,100),(80,135),(80,170),(80,200),(79,236)]
# Right outer — thick leg that bows far out and leans right:
RO = [(70,32),(80,40),(92,56),(103,80),(112,112),(116,148),(117,180),(115,208),(112,236)]

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

# ── Recess depth (the reveal that gives 3D feel) ──────
TOP_REV = 15      # soffit depth across the top (receding ceiling)
R_REV   = 14      # right jamb depth — thick, faces us, most visible
L_REV   = 4       # left jamb faces away → barely shows

# ── Front stone face + the arched hole ────────────────
front = [[False] * W for _ in range(H)]   # opening (front rim inward)
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
        if x < ilo or x > iro:
            put(x, y, PURPLE)            # front stone face
        else:
            front[y][x] = True           # inside the hole

# topmost open row per column (front-top rim — the soffit springs here)
top_y = [None] * W
for x in range(W):
    for y in range(H):
        if front[y][x]:
            top_y[x] = y
            break

# ── Split the hole into reveal (receding walls) + void ─
back = [[False] * W for _ in range(H)]    # deepest opening → glow
reveal_depth = [[0] * W for _ in range(H)]
for y in range(H):
    li = edge(LI, y)
    ri = edge(RI, y)
    if li is None or ri is None:
        continue
    ilo = int(math.ceil(li))
    iro = int(math.floor(ri))
    for x in range(ilo, iro + 1):
        if not front[y][x]:
            continue
        dr = iro - x            # 0 at front-right rim
        dl = x - ilo            # 0 at front-left rim
        dt = y - top_y[x]       # 0 at front-top rim
        # is this pixel still inside the recessed back opening?
        if dr >= R_REV and dl >= L_REV and dt >= TOP_REV:
            back[y][x] = True
        else:
            reveal_depth[y][x] = min(dr, dl, dt) + 1   # 1 = lit front lip

# Reveal shading: lit lip steps back into shadow (strong recession cue)
def reveal_color(d):
    if d <= 1:  return LAVENDER      # front lip catches the light
    if d <= 3:  return PURPLE        # face turning away
    if d <= 7:  return DEEP_PURPLE   # in shadow
    return DARK_VOID                 # deepest part of the recess
for y in range(H):
    for x in range(W):
        d = reveal_depth[y][x]
        if d:
            put(x, y, reveal_color(d))

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
    if d <= 2:  return HOT_PINK
    if d <= 4:  return SOFT_PINK
    if d <= 7:  return PALE_CYAN
    if d <= 12: return CYAN
    if d <= 19: return DEEP_BLUE
    return DARK_VOID

for y in range(H):
    for x in range(W):
        if back[y][x]:
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

# ── Binding bands on the thick right leg (protrude out) ─
def draw_right_band(cy):
    ri = edge(RI, cy)
    ro = edge(RO, cy)
    if ri is None or ro is None:
        return
    sx = int(math.floor(ri)) + R_REV     # start past the recessed jamb
    ex = int(math.ceil(ro)) + 7          # stick out past the outer edge
    span = max(1, ex - sx)
    half = 4
    for x in range(sx, ex + 1):
        f = (x - sx) / span
        drop = int(round(f * 3))         # tilt down toward the far end
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
        put(x, top + 1, LAVENDER)
        put(x, bot, DEEP_PURPLE)
        put(x, bot + 1, DEEP_PURPLE)
for cy in (78, 140, 202):               # three evenly spaced bands
    draw_right_band(cy)

# ── Binding wraps on the thin left leg (subtle, protrude a touch) ─
def draw_left_wrap(cy):
    lo = edge(LO, cy)
    li = edge(LI, cy)
    if lo is None or li is None:
        return
    sx = int(math.floor(lo)) - 2         # nudge out past the outer edge
    ex = int(math.ceil(li)) - 1          # stop before the opening
    if ex - sx < 3:
        return
    for x in range(sx, ex + 1):
        for yy in range(cy - 3, cy + 3):
            base = get(x, yy)
            if base[3] != 0 or x < int(math.floor(lo)):
                put(x, yy, PURPLE)
        put(x, cy - 3, LAVENDER)
        put(x, cy + 2, DEEP_PURPLE)
        put(x, cy + 3, DEEP_PURPLE)
for cy in (78, 130, 182, 222):
    draw_left_wrap(cy)

# ── Crossbar cylinder + round joints at each shoulder ─
def draw_crossbar():
    x0, y0 = 46, 25
    x1, y1 = 80, 32                       # tilted: right end lower
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

def draw_joint(ox, oy, orad):
    for dy in range(-orad, orad + 1):
        for dx in range(-orad, orad + 1):
            r2 = dx * dx + dy * dy
            if r2 <= orad * orad:
                put(ox + dx, oy + dy, PURPLE)
                if dx + dy < -2:
                    put(ox + dx, oy + dy, LAVENDER)
                elif dx + dy > 3:
                    put(ox + dx, oy + dy, DEEP_PURPLE)

draw_joint(43, 37, 6)                    # left shoulder knot (prominent)
draw_joint(74, 36, 4)                    # right shoulder knot (smaller)
draw_crossbar()
put(41, 34, PALE_CYAN)                   # tiny glint on the left knot

# ── Pillar feet — small mossy stone base ──────────────
def draw_feet():
    for (pa, pb) in ((LO, LI), (RI, RO)):
        ea = edge(pa, 235)
        eb = edge(pb, 235)
        if ea is None or eb is None:
            continue
        a, b = sorted((int(round(ea)), int(round(eb))))
        for yy in range(234, H):
            for x in range(a - 2, b + 3):
                put(x, yy, DEEP_PURPLE)
draw_feet()

# ── Ground light spill below the opening ──────────────
def draw_ground_spill():
    cx, cy = 57, 243
    rw, rh = 24, 4
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
CRACKS = [(24,90),(20,140),(18,180),(20,210),(30,55),
          (95,90),(105,130),(110,170),(106,205),(70,42),
          (26,68),(80,48),(22,228),(108,232)]
MOSS = [(19,118),(17,165),(106,115),(110,195),(76,46),
        (24,215),(112,98),(18,150)]
for (x, y) in CRACKS:
    if get(x, y)[:3] in (PURPLE, LAVENDER):
        put(x, y, DEEP_PURPLE)
for (x, y) in MOSS:
    if get(x, y)[:3] in (PURPLE, LAVENDER, DEEP_PURPLE):
        put(x, y, HOT_PINK)

# ── Upscale + save ────────────────────────────────────
os.makedirs('output', exist_ok=True)
big = img.resize((W * SCALE, H * SCALE), Image.NEAREST)
big.save('output/portal_static.png')
print('wrote output/portal_static.png', big.size)
