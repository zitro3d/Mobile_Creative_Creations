#!/usr/bin/env python3
"""Animated magical sword — seamless looping energy, transparent.

Builds the static portal-styled sword once, then animates magical
energy across 24 frames:
  * a bright shimmer sweeping up the blade;
  * a breathing cyan/pink aura hugging the blade edge;
  * energy sparks rising along the blade and wrapping;
  * a pulsing hot-pink gem with a glow halo.
Logical 37x180 -> 8x NEAREST -> 296x1440. Output: output/sword_loop.gif
(+ output/sword_frames/). Seamless (all motion phase-locked to the loop).
"""
import os, math
from collections import deque
from PIL import Image

W, H, SCALE = 37, 180, 8
CX = 18
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
WHITE       = (255, 255, 255)
GRIP_DARK   = (40, 26, 52)
GEM_DARK    = (150, 50, 110)
OUTLINE     = DEEP_PURPLE
PALETTE = [DEEP_PURPLE, PURPLE, LAVENDER, HOT_PINK, SOFT_PINK, CYAN,
           PALE_CYAN, DEEP_BLUE, WHITE, GRIP_DARK, GEM_DARK]

TIP_Y, SHOULDER_Y, BASE_Y = 6, 26, 120
GY0, GY1 = 121, 129
PCX, PCY, PR, GR = CX, 167, 9, 4

# ── Build the static sword base ───────────────────────
base = Image.new('RGBA', (W, H), (0, 0, 0, 0))
BPX = base.load()

def bput(x, y, c):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H:
        BPX[x, y] = c + (255,)

def bget(x, y):
    if 0 <= x < W and 0 <= y < H:
        return BPX[x, y]
    return (0, 0, 0, 0)

def blade_hw(y):
    if y < TIP_Y or y > BASE_Y:
        return None
    if y < SHOULDER_Y:
        return 0.4 + (y - TIP_Y) / (SHOULDER_Y - TIP_Y) * 5.2
    return 5.6 + (y - SHOULDER_Y) / (BASE_Y - SHOULDER_Y) * 1.0

for y in range(TIP_Y, BASE_Y + 1):
    ihw = int(round(blade_hw(y)))
    for c in range(-ihw, ihw + 1):
        col = PALE_CYAN if c <= -ihw + 1 else DEEP_BLUE if c >= ihw - 1 else CYAN
        bput(CX + c, y, col)
    if ihw >= 3 and y > TIP_Y + 3:
        bput(CX - 1, y, WHITE)
        bput(CX, y, PALE_CYAN)

for x in range(3, W - 3):
    for y in range(GY0 + 1, GY1):
        bput(x, y, PURPLE)
for ex in (4, W - 5):
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            if dx * dx + dy * dy <= 9:
                bput(ex + dx, (GY0 + GY1) // 2 + dy, PURPLE)
for x in range(CX - 6, CX + 7):
    for y in range(GY0 - 1, GY1 + 2):
        bput(x, y, PURPLE)
for x in range(W):
    for y in range(GY0 - 1, GY1 + 2):
        if bget(x, y)[:3] == PURPLE:
            if bget(x, y - 1)[:3] not in (PURPLE, LAVENDER, DEEP_PURPLE):
                bput(x, y, LAVENDER)
            elif bget(x, y + 1)[3] == 0:
                bput(x, y, DEEP_PURPLE)

GRIP_TOP, GRIP_BOT = GY1 + 1, 161
for y in range(GRIP_TOP, GRIP_BOT + 1):
    hw = 2 if y >= GRIP_BOT - 1 else 3 if y >= GRIP_BOT - 4 else 4
    for c in range(-hw, hw + 1):
        col = PURPLE if c <= -hw + 1 else GRIP_DARK if c >= hw else DEEP_PURPLE
        if (y - c) % 3 == 0:
            col = GRIP_DARK
        bput(CX + c, y, col)

for dy in range(-PR, PR + 1):
    for dx in range(-PR, PR + 1):
        if dx * dx + dy * dy <= PR * PR:
            c = PURPLE
            if dx + dy <= -4:
                c = LAVENDER
            elif dx + dy >= 5:
                c = DEEP_PURPLE
            bput(PCX + dx, PCY + dy, c)
for d in range(-5, 6):
    bput(PCX + d, PCY + 5 - abs(d), DEEP_PURPLE)
for dy in range(-GR, GR + 1):
    for dx in range(-GR, GR + 1):
        if dx * dx + dy * dy <= GR * GR:
            c = HOT_PINK
            if dx + dy <= -3:
                c = SOFT_PINK
            elif dx + dy >= 4:
                c = GEM_DARK
            bput(PCX + dx, PCY + dy, c)

opaque = [(x, y) for y in range(H) for x in range(W) if bget(x, y)[3] != 0]
for (x, y) in opaque:
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
        if bget(x + dx, y + dy)[3] == 0:
            bput(x, y, OUTLINE)
            break

# ── Masks for the FX ──────────────────────────────────
BLADE = {PALE_CYAN, CYAN, DEEP_BLUE, WHITE}
blade_mask = [[False] * W for _ in range(H)]
for y in range(TIP_Y, BASE_Y + 1):
    for x in range(W):
        if bget(x, y)[:3] in BLADE:
            blade_mask[y][x] = True

# Distance from the blade (for the aura ring just outside the silhouette).
INF = 9999
adist = [[INF] * W for _ in range(H)]
dq = deque()
for y in range(H):
    for x in range(W):
        if blade_mask[y][x]:
            adist[y][x] = 0
            dq.append((x, y))
while dq:
    x, y = dq.popleft()
    if adist[y][x] >= 5:
        continue
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < W and 0 <= ny < H and adist[ny][nx] == INF:
            adist[ny][nx] = adist[y][x] + 1
            dq.append((nx, ny))
aura_cells = [(x, y) for y in range(H) for x in range(W)
              if 2 <= adist[y][x] <= 4 and bget(x, y)[3] == 0 and y <= BASE_Y + 2]

# blade edge x at each row (for sparks to ride)
edge_x = {}
for y in range(TIP_Y + 4, BASE_Y):
    hw = blade_hw(y)
    if hw:
        edge_x[y] = int(round(hw))

SPARKS = [(0.00, -1, 0.0), (0.17, 1, 1.1), (0.34, -1, 2.2), (0.5, 1, 3.0),
          (0.66, -1, 4.0), (0.83, 1, 5.1), (0.42, -1, 0.6), (0.92, 1, 2.7)]


def render(t, fi):
    img = base.copy()
    PX = img.load()

    def put(x, y, c, env=1.0):
        x, y = int(round(x)), int(round(y))
        if not (0 <= x < W and 0 <= y < H):
            return
        if env < 0.95 and ((x * 7 + y * 13 + fi) % 10) / 10.0 > env:
            return
        PX[x, y] = c + (255,)

    # Aura — breathing cyan/pink glow hugging the blade, wave travels up
    for (x, y) in aura_cells:
        d = adist[y][x]
        wave = 0.5 + 0.5 * math.sin(TAU * t - y * 0.06)
        env = wave * (1.0 - (d - 2) / 3.0)
        if env <= 0.05:
            continue
        pink = math.sin(y * 0.09 + TAU * t) > 0.55
        col = (SOFT_PINK if pink else PALE_CYAN) if d == 2 else (HOT_PINK if pink else CYAN) if d == 3 else DEEP_BLUE
        put(x, y, col, env)

    # Shimmer — bright band sweeping up the blade
    sweep = (BASE_Y + 8) - (t * (BASE_Y - TIP_Y + 16))
    for y in range(TIP_Y, BASE_Y + 1):
        dy = abs(y - sweep)
        if dy > 3:
            continue
        ihw = int(round(blade_hw(y)))
        for c in range(-ihw + 1, ihw):
            x = CX + c
            if not blade_mask[y][x]:
                continue
            if dy <= 1:
                put(x, y, WHITE if abs(c) <= 1 else PALE_CYAN)
            elif dy <= 3:
                if abs(c) <= 2:
                    put(x, y, PALE_CYAN, 0.7)

    # Sparks rising along the blade edges, wrapping (seamless)
    span = BASE_Y - (TIP_Y + 6)
    for (ph, side, _w) in SPARKS:
        frac = (t + ph) % 1.0
        env = 1.0 if 0.1 < frac < 0.85 else (frac / 0.1 if frac <= 0.1 else (1 - frac) / 0.15)
        y = int((BASE_Y - 2) - frac * span)
        if y not in edge_x:
            continue
        hw = edge_x[y]
        waver = int(round(1.5 * math.sin(TAU * (t * 2) + y * 0.3)))
        x = CX + side * (hw + 1) + waver
        put(x, y, WHITE, env)
        put(x, y - 1, PALE_CYAN, env * 0.7)
        put(x + side, y, CYAN, env * 0.6)

    # Gem pulse + glow halo on the pommel
    pulse = 0.5 + 0.5 * math.sin(TAU * t * 2)
    if pulse > 0.35:
        for dy in range(-GR, GR + 1):
            for dx in range(-GR, GR + 1):
                if dx * dx + dy * dy <= GR * GR and dx + dy < 1:
                    put(PCX + dx, PCY + dy, SOFT_PINK, pulse)
        put(PCX - 1, PCY - 1, WHITE)
        put(PCX, PCY - 1, WHITE, pulse)
    for dy in range(-PR - 3, PR + 4):       # halo just outside the pommel
        for dx in range(-PR - 3, PR + 4):
            r = math.hypot(dx, dy)
            if PR < r <= PR + 3 and bget(PCX + dx, PCY + dy)[3] == 0:
                put(PCX + dx, PCY + dy, HOT_PINK, pulse * (1 - (r - PR) / 3) * 0.8)
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

os.makedirs('output/sword_frames', exist_ok=True)
frames = []
for f in range(N_FRAMES):
    rgba = render(f / N_FRAMES, f)
    rgba.resize((W * SCALE, H * SCALE), Image.NEAREST).save('output/sword_frames/frame_%02d.png' % f)
    frames.append(to_p(rgba))
frames[0].save('output/sword_loop.gif', save_all=True, append_images=frames[1:],
               duration=int(1000 / FPS), loop=0, transparency=TRANSP, disposal=2, optimize=False)
print('wrote output/sword_loop.gif', N_FRAMES, 'frames', (W * SCALE, H * SCALE))
