#!/usr/bin/env python3
"""Phase 2 — looping vortex animation of the alien stone portal.

Renders the static stone/rivets/capstone/veins ONCE as a base, then
animates the interior across N seamless frames:
  * swirling vortex + breathing rings in the void;
  * pink energy pulses travelling along the stone veins;
  * white sparks drifting up through the glow;
  * cyan rivet studs pulsing;
  * a flickering ground-light spill.

Output: output/portal_loop.gif (looping, transparent) + output/frames/.
Logical 160x250 -> 8x NEAREST -> 1280x2000. One palette color per pixel.
"""
import os, math
from collections import deque
from PIL import Image

W, H, SCALE = 160, 250, 8
N_FRAMES = 24
FPS = 12

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

PALETTE = [DEEP_PURPLE, PURPLE, LAVENDER, HOT_PINK, SOFT_PINK,
           CYAN, PALE_CYAN, DEEP_BLUE, DARK_VOID, WHITE]

# Glow brightness ladder (dark core → bright rim) for the vortex.
LADDER = [DARK_VOID, DEEP_BLUE, CYAN, PALE_CYAN, SOFT_PINK, HOT_PINK, WHITE]

base = Image.new('RGBA', (W, H), (0, 0, 0, 0))
BPX = base.load()

def bput(x, y, c):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H:
        BPX[x, y] = c if len(c) == 4 else c + (255,)

def bget(x, y):
    if 0 <= x < W and 0 <= y < H:
        return BPX[x, y]
    return (0, 0, 0, 0)

def is3(x, y, c):
    return bget(x, y)[:3] == c

# ── Geometry (identical to the static build) ──────────
Y_S, Y_BOT = 96, 238
LO = (40, 30); LI = (58, 50); RI = (104, 112); RO = (132, 144)

def leg_x(p, y):
    t = (y - Y_S) / (Y_BOT - Y_S)
    return p[0] + (p[1] - p[0]) * t

CX_O, A_O, B_O = 86, 46, 58
CX_I, A_I, B_I = 81, 23, 46

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

TOP_REV, R_REV, L_REV = 19, 16, 3

# ── Static base: front face + arched hole ─────────────
front = [[False] * W for _ in range(H)]
for y in range(H):
    ob = outer_b(y)
    if ob is None:
        continue
    ol, orr = int(math.floor(ob[0])), int(math.ceil(ob[1]))
    ib = inner_b(y)
    if ib is None:
        for x in range(ol, orr + 1):
            bput(x, y, PURPLE)
        continue
    ilo, iro = int(math.ceil(ib[0])), int(math.floor(ib[1]))
    for x in range(ol, orr + 1):
        if x < ilo or x > iro:
            bput(x, y, PURPLE)
        else:
            front[y][x] = True

top_y = [None] * W
for x in range(W):
    for y in range(H):
        if front[y][x]:
            top_y[x] = y
            break

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
        dr, dl, dt = iro - x, x - ilo, y - top_y[x]
        if dr >= R_REV and dl >= L_REV and dt >= TOP_REV:
            back[y][x] = True
        else:
            reveal_depth[y][x] = min(dr, dl, dt) + 1

for y in range(H):
    for x in range(W):
        d = reveal_depth[y][x]
        if d == 0:
            continue
        bput(x, y, LAVENDER if d <= 1 else PURPLE if d <= 4 else DEEP_PURPLE)

# ── Void edge-distance (radial structure of the glow) ─
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

void_px = [(x, y) for y in range(H) for x in range(W) if back[y][x]]
vx0 = sum(p[0] for p in void_px) / len(void_px)
vy0 = sum(p[1] for p in void_px) / len(void_px)
y_void_top = min(p[1] for p in void_px)
y_void_bot = max(p[1] for p in void_px)

def base_idx(d):
    if d <= 4:  return 5
    if d <= 8:  return 4
    if d <= 14: return 3
    if d <= 22: return 2
    return 1

# Fill a static glow so any stray void pixel looks right under the base.
for (x, y) in void_px:
    bput(x, y, LADDER[base_idx(dist[y][x])])

# ── Right-pillar shadow strip, outline, lit edge ──────
for y in range(Y_S, Y_BOT + 1):
    ro = leg_x(RO, y)
    for x in range(int(round(ro)) - 5, int(round(ro)) + 1):
        if is3(x, y, PURPLE):
            bput(x, y, DEEP_PURPLE)
for y in range(38, Y_S):
    ob = outer_b(y)
    if ob is None:
        continue
    for x in range(int(round(ob[1])) - 5, int(round(ob[1])) + 1):
        if is3(x, y, PURPLE):
            bput(x, y, DEEP_PURPLE)

for (x, y) in [(x, y) for y in range(H) for x in range(W) if is3(x, y, PURPLE)]:
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if bget(x + dx, y + dy)[3] == 0:
            bput(x, y, DEEP_PURPLE)
            break

for y in range(H):
    ob = outer_b(y)
    if ob is None:
        continue
    ol = int(math.floor(ob[0]))
    run = 0
    for x in range(ol, ol + 16):
        if is3(x, y, PURPLE):
            bput(x, y, LAVENDER)
            run += 1
            if run >= 3:
                break
        elif run:
            break

# ── Banded rings on the right pillar ──────────────────
def draw_band(cy):
    ri, ro = leg_x(RI, cy), leg_x(RO, cy)
    sx = int(round(ri)) + R_REV - 1
    ex = int(round(ro)) + 9
    span = max(1, ex - sx)
    half = 4
    for x in range(sx, ex + 1):
        f = (x - sx) / span
        drop = int(round(f * 3))
        h = half if f < 0.9 else half - 1
        for yy in range(cy - h + drop, cy + h + drop + 1):
            if bget(x, yy)[3] != 0 or x > int(round(ro)):
                bput(x, yy, PURPLE)
        bput(x, cy - h + drop, LAVENDER)
        bput(x, cy - h + 1 + drop, LAVENDER)
        bput(x, cy + h + drop, DEEP_PURPLE)
        bput(x, cy + h + 1 + drop, DEEP_PURPLE)
for cy in (128, 165, 202):
    draw_band(cy)

# ── Capstone + orb, seated on the crown ───────────────
def draw_capstone():
    x0, y0, x1, y1 = 58, 30, 118, 38
    span = x1 - x0
    bar_bottom = {}
    for x in range(x0, x1 + 1):
        f = (x - x0) / span
        cy = int(round(y0 + f * (y1 - y0)))
        h = 4 if 0.06 < f < 0.94 else 3
        for yy in range(cy - h, cy + h + 1):
            bput(x, yy, PURPLE)
        bput(x, cy - h, LAVENDER); bput(x, cy - h + 1, LAVENDER)
        bput(x, cy + h, DEEP_PURPLE)
        bar_bottom[x] = cy + h
    for x in range(x0, x1 + 1):
        y = bar_bottom[x] + 1
        while y < 68 and bget(x, y)[3] == 0:
            bput(x, y, PURPLE); y += 1
    ox, oy, r = 60, 46, 7
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                c = PURPLE
                if dx + dy <= -3: c = LAVENDER
                elif dx + dy >= 5: c = DEEP_PURPLE
                bput(ox + dx, oy + dy, c)
    bput(ox - 3, oy - 3, PALE_CYAN); bput(ox - 2, oy - 4, WHITE)
draw_capstone()

for y in range(0, 70):
    for x in range(W):
        if is3(x, y, PURPLE):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if bget(x + dx, y + dy)[3] == 0:
                    bput(x, y, DEEP_PURPLE); break

# ── Feet ──────────────────────────────────────────────
for (pa, pb) in ((LO, LI), (RI, RO)):
    a, b = sorted((int(round(leg_x(pa, Y_BOT))), int(round(leg_x(pb, Y_BOT)))))
    for yy in range(Y_BOT - 1, H):
        for x in range(a - 2, b + 3):
            bput(x, yy, DEEP_PURPLE)

# ── Rivets (static body) — collect glowing studs to pulse ─
glow_studs = []
def stud(cx, cy, glow):
    if glow:
        body, hi, lo = CYAN, PALE_CYAN, DEEP_BLUE
        glow_studs.append((cx, cy))
    else:
        body, hi, lo = PURPLE, LAVENDER, DEEP_PURPLE
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            if abs(dx) + abs(dy) <= 2:
                bput(cx + dx, cy + dy, body)
    bput(cx - 1, cy - 1, hi); bput(cx, cy - 1, hi)
    bput(cx + 1, cy + 1, lo); bput(cx, cy + 1, lo)
    bput(cx, cy, LAVENDER if not glow else WHITE)

i = 0
for y in range(48, 232, 10):
    ob = outer_b(y)
    if ob is None:
        continue
    stud(int(math.floor(ob[0])) + 3, y, glow=(i % 4 == 2))
    stud(int(math.ceil(ob[1])) - 4, y, glow=(i % 4 == 0))
    i += 1

# ── Veins — collect ordered pixels so a pulse can travel ─
VEINS = [
    [(46,72),(43,86),(48,100),(42,116),(46,132),(40,148)],
    [(34,162),(30,176),(35,190),(31,206)],
    [(120,78),(127,92),(121,108),(128,124),(122,140)],
    [(141,150),(135,166),(142,182),(137,198),(143,214)],
    [(82,46),(76,54),(84,62),(78,70)],
    [(112,60),(118,72),(113,84)],
]
vein_px = []   # list of (x, y, order_fraction)
for path in VEINS:
    pts = []
    for k in range(len(path) - 1):
        x0, y0 = path[k]; x1, y1 = path[k + 1]
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for s in range(steps + 1):
            x = int(round(x0 + (x1 - x0) * s / steps))
            y = int(round(y0 + (y1 - y0) * s / steps))
            if is3(x, y, PURPLE) or is3(x, y, LAVENDER) or is3(x, y, DEEP_PURPLE):
                if (x, y) not in pts:
                    pts.append((x, y))
    n = max(1, len(pts) - 1)
    for j, (x, y) in enumerate(pts):
        vein_px.append((x, y, j / n))
        bput(x, y, HOT_PINK)   # static look in the base

# ── Animation helpers ─────────────────────────────────
TAU = 2 * math.pi
ARMS = 2.0
SWIRL = 0.42

precomp = []   # (x, y, base_index, angle)
for (x, y) in void_px:
    ang = math.atan2(y - vy0, x - vx0)
    precomp.append((x, y, base_idx(dist[y][x]), ang, dist[y][x]))

# Drifting sparks: each wraps exactly once over the loop (seamless).
SPARK_SEED = [(78, 0.0), (84, 0.25), (80, 0.55), (86, 0.1),
              (76, 0.7), (82, 0.4), (79, 0.85), (88, 0.6)]

def render_frame(t):
    """t in [0,1). Returns an RGBA logical image."""
    fr = base.copy()
    PX = fr.load()

    def put(x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < W and 0 <= y < H:
            PX[x, y] = c if len(c) == 4 else c + (255,)

    breath = math.sin(TAU * t)
    # Vortex glow
    for (x, y, bidx, ang, d) in precomp:
        swirl = math.sin(ARMS * ang + SWIRL * d - TAU * 2 * t)
        pulse = math.sin(TAU * t - d * 0.07)
        shift = int(round(1.3 * swirl + 0.55 * pulse))
        idx = bidx + shift
        idx = 0 if idx < 0 else 5 if idx > 5 else idx   # reserve WHITE for sparks/rim
        put(x, y, LADDER[idx])
    # Rim shimmer — bright flecks racing around the edge
    for (x, y, bidx, ang, d) in precomp:
        if d <= 3 and math.sin(5 * ang - TAU * 2 * t) > 0.86:
            put(x, y, WHITE)

    # Travelling vein pulses
    for (x, y, fr_order) in vein_px:
        wave = math.sin(TAU * (t - fr_order))
        if wave > 0.55:
            put(x, y, WHITE)
        elif wave > 0.0:
            put(x, y, SOFT_PINK)
        else:
            put(x, y, HOT_PINK)

    # Pulsing cyan rivet studs
    for (cx, cy) in glow_studs:
        bright = math.sin(TAU * t * 2 + cx * 0.3) > 0
        put(cx, cy, WHITE if bright else PALE_CYAN)
        if bright:
            put(cx - 1, cy, PALE_CYAN); put(cx + 1, cy, PALE_CYAN)

    # Sparks drifting upward through the void
    span = max(1, y_void_bot - y_void_top)
    for (sx, ph) in SPARK_SEED:
        prog = (ph - t) % 1.0
        sy = int(round(y_void_bot - prog * span))
        if 0 <= sy < H and back[sy][sx]:
            put(sx, sy, WHITE)
            if back[sy - 1][sx]:
                put(sx, sy - 1, PALE_CYAN)
            if back[sy][sx + 1]:
                put(sx + 1, sy, PALE_CYAN)

    # Ground light spill — breathes with the portal
    cx, cy = 81, 243
    rw, rh = 36 + 5 * breath, 4
    for dy in range(-int(rh) - 1, int(rh) + 2):
        for dx in range(-int(rw) - 1, int(rw) + 2):
            nd = (dx / rw) ** 2 + (dy / rh) ** 2
            if nd > 1.0:
                continue
            if nd > 0.45 and ((dx + dy + int(t * 4)) % 2 == 0):
                continue
            if bget(cx + dx, cy + dy)[3] == 0:
                put(cx + dx, cy + dy, PALE_CYAN)
    return fr

# ── Build a transparent palette for crisp GIF export ──
TRANSP = 0
flat = [0, 0, 0]
color_index = {}
for n, c in enumerate(PALETTE):
    color_index[c] = n + 1
    flat += list(c)
flat += [0, 0, 0] * (256 - len(PALETTE) - 1)

def nearest(c):
    return min(PALETTE, key=lambda p: sum((a - b) ** 2 for a, b in zip(p, c)))

def to_p(rgba):
    p = Image.new('P', (W, H))
    p.putpalette(flat)
    out = bytearray(W * H)
    for n, px in enumerate(rgba.getdata()):
        if px[3] == 0:
            out[n] = TRANSP
        else:
            rgb = px[:3]
            out[n] = color_index.get(rgb) or color_index[nearest(rgb)]
    p.frombytes(bytes(out))
    return p.resize((W * SCALE, H * SCALE), Image.NEAREST)

# ── Render all frames, save PNGs + looping GIF ────────
os.makedirs('output/frames', exist_ok=True)
gif_frames = []
for f in range(N_FRAMES):
    t = f / N_FRAMES
    rgba = render_frame(t)
    big_rgba = rgba.resize((W * SCALE, H * SCALE), Image.NEAREST)
    big_rgba.save('output/frames/frame_%02d.png' % f)
    gif_frames.append(to_p(rgba))
    print('frame', f)

gif_frames[0].save(
    'output/portal_loop.gif', save_all=True, append_images=gif_frames[1:],
    duration=int(1000 / FPS), loop=0, transparency=TRANSP, disposal=2, optimize=False)
print('wrote output/portal_loop.gif', N_FRAMES, 'frames', (W * SCALE, H * SCALE))
