#!/usr/bin/env python3
"""Split the portal into two compositing layers.

  output/portal_arch.png   -> static stone arch only (opening transparent)
  output/portal_vortex.gif -> animated vortex glow + sparks + ground spill
                              + vein/rivet pulses (everything else transparent)

Both layers are 1280x2000 RGBA on full transparency, so they composite
exactly:  vortex (back) -> character -> arch (front).
"""
import os, math
from collections import deque
from PIL import Image

W, H, SCALE = 160, 250, 8
N_FRAMES, FPS = 24, 12
TAU = 2 * math.pi

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
LADDER = [DARK_VOID, DEEP_BLUE, CYAN, PALE_CYAN, SOFT_PINK, HOT_PINK, WHITE]

# ── Geometry (mirrors build_animation.py) ─────────────
Y_S, Y_BOT = 96, 238
LO = (40, 30); LI = (58, 50); RI = (104, 112); RO = (132, 144)
CX_O, A_O, B_O = 86, 46, 58
CX_I, A_I, B_I = 81, 23, 46
TOP_REV, R_REV, L_REV = 19, 16, 3

def leg_x(p, y):
    t = (y - Y_S) / (Y_BOT - Y_S)
    return p[0] + (p[1] - p[0]) * t

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

# ── Build the arch (stone only, opening transparent) ──
arch = Image.new('RGBA', (W, H), (0, 0, 0, 0))
APX = arch.load()

def aput(x, y, c):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H:
        APX[x, y] = c + (255,)

def aget(x, y):
    if 0 <= x < W and 0 <= y < H:
        return APX[x, y]
    return (0, 0, 0, 0)

def ais3(x, y, c):
    return aget(x, y)[:3] == c

front = [[False] * W for _ in range(H)]
for y in range(H):
    ob = outer_b(y)
    if ob is None:
        continue
    ol, orr = int(math.floor(ob[0])), int(math.ceil(ob[1]))
    ib = inner_b(y)
    if ib is None:
        for x in range(ol, orr + 1):
            aput(x, y, PURPLE)
        continue
    ilo, iro = int(math.ceil(ib[0])), int(math.floor(ib[1]))
    for x in range(ol, orr + 1):
        if x < ilo or x > iro:
            aput(x, y, PURPLE)
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
        if d:
            aput(x, y, LAVENDER if d <= 1 else PURPLE if d <= 4 else DEEP_PURPLE)

# Right-pillar shadow strip
for y in range(Y_S, Y_BOT + 1):
    ro = leg_x(RO, y)
    for x in range(int(round(ro)) - 5, int(round(ro)) + 1):
        if ais3(x, y, PURPLE):
            aput(x, y, DEEP_PURPLE)
for y in range(38, Y_S):
    ob = outer_b(y)
    if ob is None:
        continue
    for x in range(int(round(ob[1])) - 5, int(round(ob[1])) + 1):
        if ais3(x, y, PURPLE):
            aput(x, y, DEEP_PURPLE)

# Silhouette outline
for (x, y) in [(x, y) for y in range(H) for x in range(W) if ais3(x, y, PURPLE)]:
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if aget(x + dx, y + dy)[3] == 0:
            aput(x, y, DEEP_PURPLE)
            break

# LAVENDER lit edge on the left outer
for y in range(H):
    ob = outer_b(y)
    if ob is None:
        continue
    ol = int(math.floor(ob[0]))
    run = 0
    for x in range(ol, ol + 16):
        if ais3(x, y, PURPLE):
            aput(x, y, LAVENDER); run += 1
            if run >= 3:
                break
        elif run:
            break

# Bands on the right pillar
def draw_band(cy):
    ri, ro = leg_x(RI, cy), leg_x(RO, cy)
    sx = int(round(ri)) + R_REV - 1
    ex = int(round(ro)) + 9
    half = 4
    span = max(1, ex - sx)
    for x in range(sx, ex + 1):
        f = (x - sx) / span
        drop = int(round(f * 3))
        h = half if f < 0.9 else half - 1
        for yy in range(cy - h + drop, cy + h + drop + 1):
            if aget(x, yy)[3] != 0 or x > int(round(ro)):
                aput(x, yy, PURPLE)
        aput(x, cy - h + drop, LAVENDER)
        aput(x, cy - h + 1 + drop, LAVENDER)
        aput(x, cy + h + drop, DEEP_PURPLE)
        aput(x, cy + h + 1 + drop, DEEP_PURPLE)
for cy in (128, 165, 202):
    draw_band(cy)

# Capstone + orb + spandrel + top outline cleanup
def draw_capstone():
    x0, y0, x1, y1 = 58, 30, 118, 38
    bar_bottom = {}
    span = x1 - x0
    for x in range(x0, x1 + 1):
        f = (x - x0) / span
        cy = int(round(y0 + f * (y1 - y0)))
        h = 4 if 0.06 < f < 0.94 else 3
        for yy in range(cy - h, cy + h + 1):
            aput(x, yy, PURPLE)
        aput(x, cy - h, LAVENDER); aput(x, cy - h + 1, LAVENDER)
        aput(x, cy + h, DEEP_PURPLE)
        bar_bottom[x] = cy + h
    for x in range(x0, x1 + 1):
        y = bar_bottom[x] + 1
        while y < 68 and aget(x, y)[3] == 0:
            aput(x, y, PURPLE); y += 1
    ox, oy, r = 60, 46, 7
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                c = PURPLE
                if dx + dy <= -3: c = LAVENDER
                elif dx + dy >= 5: c = DEEP_PURPLE
                aput(ox + dx, oy + dy, c)
    aput(ox - 3, oy - 3, PALE_CYAN); aput(ox - 2, oy - 4, WHITE)
draw_capstone()
for y in range(0, 70):
    for x in range(W):
        if ais3(x, y, PURPLE):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if aget(x + dx, y + dy)[3] == 0:
                    aput(x, y, DEEP_PURPLE); break

# Feet
for (pa, pb) in ((LO, LI), (RI, RO)):
    a, b = sorted((int(round(leg_x(pa, Y_BOT))), int(round(leg_x(pb, Y_BOT)))))
    for yy in range(Y_BOT - 1, H):
        for x in range(a - 2, b + 3):
            aput(x, yy, DEEP_PURPLE)

# Rivets — static studs (track glow ones for pulse overlay in vortex layer)
glow_studs = []
def stud(cx, cy, glow):
    body, hi, lo = (CYAN, PALE_CYAN, DEEP_BLUE) if glow else (PURPLE, LAVENDER, DEEP_PURPLE)
    if glow:
        glow_studs.append((cx, cy))
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            if abs(dx) + abs(dy) <= 2:
                aput(cx + dx, cy + dy, body)
    aput(cx - 1, cy - 1, hi); aput(cx, cy - 1, hi)
    aput(cx + 1, cy + 1, lo); aput(cx, cy + 1, lo)
    aput(cx, cy, LAVENDER if not glow else WHITE)
i = 0
for y in range(48, 232, 10):
    ob = outer_b(y)
    if ob is None:
        continue
    stud(int(math.floor(ob[0])) + 3, y, glow=(i % 4 == 2))
    stud(int(math.ceil(ob[1])) - 4, y, glow=(i % 4 == 0))
    i += 1

# Static veins (collect ordered pixels for pulse overlay)
VEINS = [
    [(46,72),(43,86),(48,100),(42,116),(46,132),(40,148)],
    [(34,162),(30,176),(35,190),(31,206)],
    [(120,78),(127,92),(121,108),(128,124),(122,140)],
    [(141,150),(135,166),(142,182),(137,198),(143,214)],
    [(82,46),(76,54),(84,62),(78,70)],
    [(112,60),(118,72),(113,84)],
]
vein_px = []
for path in VEINS:
    pts = []
    for k in range(len(path) - 1):
        x0, y0 = path[k]; x1, y1 = path[k + 1]
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for s in range(steps + 1):
            x = int(round(x0 + (x1 - x0) * s / steps))
            y = int(round(y0 + (y1 - y0) * s / steps))
            if ais3(x, y, PURPLE) or ais3(x, y, LAVENDER) or ais3(x, y, DEEP_PURPLE):
                if (x, y) not in pts:
                    pts.append((x, y))
    n = max(1, len(pts) - 1)
    for j, (x, y) in enumerate(pts):
        vein_px.append((x, y, j / n))
        aput(x, y, HOT_PINK)

# Save arch (no vortex/glow/sparks/spill)
os.makedirs('output', exist_ok=True)
arch.resize((W * SCALE, H * SCALE), Image.NEAREST).save('output/portal_arch.png')
print('wrote output/portal_arch.png')

# ── Vortex layer: animated, transparent everywhere else ─
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
y_top_v, y_bot_v = min(p[1] for p in void_px), max(p[1] for p in void_px)

def bidx(d):
    if d <= 4:  return 5
    if d <= 8:  return 4
    if d <= 14: return 3
    if d <= 22: return 2
    return 1

precomp = [(x, y, bidx(dist[y][x]), math.atan2(y - vy0, x - vx0), dist[y][x])
           for (x, y) in void_px]

SPARK_SEED = [(78, 0.0), (84, 0.25), (80, 0.55), (86, 0.1),
              (76, 0.7), (82, 0.4), (79, 0.85), (88, 0.6)]
ARMS, SWIRL = 2.0, 0.42


def render_vortex(t, fi):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    PX = img.load()

    def put(x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < W and 0 <= y < H:
            PX[x, y] = c + (255,)

    # Vortex glow into the back cells
    for (x, y, b, ang, d) in precomp:
        swirl = math.sin(ARMS * ang + SWIRL * d - TAU * 2 * t)
        pulse = math.sin(TAU * t - d * 0.07)
        shift = int(round(1.3 * swirl + 0.55 * pulse))
        idx = b + shift
        idx = 0 if idx < 0 else 5 if idx > 5 else idx
        put(x, y, LADDER[idx])
    # rim shimmer
    for (x, y, b, ang, d) in precomp:
        if d <= 3 and math.sin(5 * ang - TAU * 2 * t) > 0.86:
            put(x, y, WHITE)

    # Travelling vein pulse — only the bright phase (arch shows base HOT_PINK)
    for (x, y, ord_f) in vein_px:
        wave = math.sin(TAU * (t - ord_f))
        if wave > 0.55:
            put(x, y, WHITE)
        elif wave > 0.0:
            put(x, y, SOFT_PINK)

    # Cyan rivet core pulse (on top of arch's static stud)
    for (cx, cy) in glow_studs:
        if math.sin(TAU * t * 2 + cx * 0.3) > 0:
            put(cx, cy, WHITE)
            put(cx - 1, cy, PALE_CYAN); put(cx + 1, cy, PALE_CYAN)

    # Sparks rising in the void
    span = max(1, y_bot_v - y_top_v)
    for (sx, ph) in SPARK_SEED:
        prog = (ph - t) % 1.0
        sy = int(round(y_bot_v - prog * span))
        if 0 <= sy < H and back[sy][sx]:
            put(sx, sy, WHITE)
            if back[sy - 1][sx]:
                put(sx, sy - 1, PALE_CYAN)
            if back[sy][sx + 1]:
                put(sx + 1, sy, PALE_CYAN)

    # Ground light spill (only where the arch is transparent)
    breath = math.sin(TAU * t)
    cx, cy = 81, 243
    rw, rh = 36 + 5 * breath, 4
    for dy in range(-int(rh) - 1, int(rh) + 2):
        for dx in range(-int(rw) - 1, int(rw) + 2):
            nd = (dx / rw) ** 2 + (dy / rh) ** 2
            if nd > 1.0:
                continue
            if nd > 0.45 and ((dx + dy + int(t * 4)) % 2 == 0):
                continue
            if aget(cx + dx, cy + dy)[3] == 0:
                put(cx + dx, cy + dy, PALE_CYAN)
    return img


# ── Transparent palette GIF export ────────────────────
TRANSP = 0
flat = [0, 0, 0]
cidx = {}
for n, c in enumerate(PALETTE):
    cidx[c] = n + 1
    flat += list(c)
flat += [0, 0, 0] * (256 - len(PALETTE) - 1)

def nearest(c):
    return min(PALETTE, key=lambda p: sum((a - b) ** 2 for a, b in zip(p, c)))

def to_p(rgba):
    p = Image.new('P', (W, H))
    p.putpalette(flat)
    out = bytearray(W * H)
    for n, px in enumerate(rgba.getdata()):
        out[n] = TRANSP if px[3] == 0 else (cidx.get(px[:3]) or cidx[nearest(px[:3])])
    p.frombytes(bytes(out))
    return p.resize((W * SCALE, H * SCALE), Image.NEAREST)

os.makedirs('output/vortex_frames', exist_ok=True)
frames = []
for f in range(N_FRAMES):
    rgba = render_vortex(f / N_FRAMES, f)
    rgba.resize((W * SCALE, H * SCALE), Image.NEAREST).save('output/vortex_frames/frame_%02d.png' % f)
    frames.append(to_p(rgba))
frames[0].save('output/portal_vortex.gif', save_all=True, append_images=frames[1:],
               duration=int(1000 / FPS), loop=0, transparency=TRANSP, disposal=2, optimize=False)
print('wrote output/portal_vortex.gif', N_FRAMES, 'frames', (W * SCALE, H * SCALE))
