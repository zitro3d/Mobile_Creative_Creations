#!/usr/bin/env python3
"""Render the same 64x128 grid as a preview PNG (mirrors the React HTML)."""
import os
from PIL import Image

W, H, SCALE = 64, 128, 10

PALETTE = [
    None,
    (0, 0, 0),
    (23, 15, 38),
    (52, 30, 84),
    (106, 53, 122),
    (255, 89, 179),
    (78, 226, 236),
    (162, 240, 117),
    (255, 217, 71),
    (255, 246, 204),
]

g = [[0] * W for _ in range(H)]

def s(r, c, v):
    if 0 <= r < H and 0 <= c < W:
        g[r][c] = v

def f(r1, c1, r2, c2, v):
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            s(r, c, v)

# Black void
f(16, 19, 115, 44, 1)

# Pink rim (2 px thick)
f(14, 17, 15, 46, 5)
f(14, 17, 115, 18, 5)
f(14, 45, 115, 46, 5)

# Left pillar
for r in range(14, 116):
    if r <= 24:    p = [2,3,3,4,4,7,7,7,8,8,8,9,9]
    elif r <= 50:  p = [2,3,3,4,4,4,7,7,7,8,8,9,8]
    elif r <= 75:  p = [2,3,3,3,4,4,7,7,7,7,8,8,7]
    elif r <= 100: p = [2,3,3,3,4,4,4,4,7,7,7,4,4]
    else:          p = [2,2,3,3,3,4,4,4,4,3,3,3,3]
    for i in range(13):
        s(r, 4 + i, p[i])

# Right pillar (mirror)
for r in range(14, 116):
    if r <= 24:    p = [2,3,3,4,4,7,7,7,8,8,8,9,9]
    elif r <= 50:  p = [2,3,3,4,4,4,7,7,7,8,8,9,8]
    elif r <= 75:  p = [2,3,3,3,4,4,7,7,7,7,8,8,7]
    elif r <= 100: p = [2,3,3,3,4,4,4,4,7,7,7,4,4]
    else:          p = [2,2,3,3,3,4,4,4,4,3,3,3,3]
    for i in range(13):
        s(r, 47 + i, p[12 - i])

# Left crystal
crystal = [
    [60, [0,0,0,6,0,0,0]],
    [61, [0,0,6,6,6,0,0]],
    [62, [0,6,6,6,6,6,0]],
    [63, [6,6,6,6,6,6,6]],
    [64, [6,6,9,9,9,6,6]],
    [65, [6,9,9,9,9,9,6]],
    [66, [6,6,9,9,9,6,6]],
    [67, [6,6,6,6,6,6,6]],
    [68, [0,6,6,6,6,6,0]],
    [69, [0,0,6,6,6,0,0]],
    [70, [0,0,0,6,0,0,0]],
]
for r, row in crystal:
    for c in range(len(row)):
        if row[c] != 0:
            s(r, c, row[c])
# Right crystal
for r, row in crystal:
    for c in range(len(row)):
        if row[c] != 0:
            s(r, 63 - c, row[c])

# Crown body
f(5, 4, 13, 59, 3)
f(5, 4, 5, 59, 2)
f(6, 4, 13, 4, 2)
f(6, 59, 13, 59, 2)
f(13, 4, 13, 59, 2)
# Decorations
for r in range(7, 12):
    for c in range(6, 58):
        if (r * 3 + c) % 9 == 0:
            g[r][c] = 4
for r, c in [(7,12),(7,51),(8,18),(8,45),(9,22),(9,41),(10,9),(10,54),(11,15),(11,48),(8,30),(8,33),(10,27),(10,36)]:
    s(r, c, 8)
for r, c in [(7,8),(7,55),(8,14),(8,49),(9,18),(9,45),(10,11),(10,52),(6,22),(6,41)]:
    s(r, c, 9)

# Corner flares
f(4, 0, 4, 7, 3); s(4,0,2); s(4,7,2)
f(3, 1, 3, 6, 3); s(3,1,2); s(3,6,2)
f(2, 2, 2, 5, 3); s(2,2,2); s(2,5,2)
f(1, 3, 1, 4, 2)
s(3,3,8); s(3,4,8); s(2,3,9); s(2,4,9)

f(4, 56, 4, 63, 3); s(4,56,2); s(4,63,2)
f(3, 57, 3, 62, 3); s(3,57,2); s(3,62,2)
f(2, 58, 2, 61, 3); s(2,58,2); s(2,61,2)
f(1, 59, 1, 60, 2)
s(3,59,8); s(3,60,8); s(2,59,9); s(2,60,9)

# Flame crest
s(0,31,9); s(0,32,9)
s(1,30,8); s(1,31,9); s(1,32,9); s(1,33,8)
f(2,29,2,34,8); s(2,30,9); s(2,31,9); s(2,32,9); s(2,33,9)
f(3,28,3,35,8); s(3,30,9); s(3,31,9); s(3,32,9); s(3,33,9)
f(4,27,4,36,8); s(4,30,9); s(4,31,9); s(4,32,9); s(4,33,9)

# Pedestal
def ped_ext(r):
    if r == 116: return 0
    if r <= 118: return 1
    if r <= 120: return 2
    if r <= 122: return 3
    if r <= 124: return 4
    return 5

for r in range(116, 128):
    ext = ped_ext(r)
    lL = max(0, 4 - ext); lR = 16
    for c in range(lL, lR + 1):
        if c == lL or c == lR: s(r, c, 2)
        else: s(r, c, 3)
    rL = 47; rR = min(W - 1, 59 + ext)
    for c in range(rL, rR + 1):
        if c == rL or c == rR: s(r, c, 2)
        else: s(r, c, 3)

f(116, 5, 116, 15, 4)
f(116, 48, 116, 58, 4)

# Golden drips
f(116, 8, 117, 12, 8); s(118,9,8); s(118,10,8); s(118,11,8); s(119,10,8)
s(116,10,9); s(117,10,9)
f(116, 51, 117, 55, 8); s(118,52,8); s(118,53,8); s(118,54,8); s(119,53,8)
s(116,53,9); s(117,53,9)

# Gold pool
f(120, 22, 121, 41, 8)
f(122, 20, 123, 43, 8)
f(124, 19, 127, 44, 8)
f(125, 24, 125, 39, 9)
f(126, 27, 126, 36, 9)
s(122,19,4); s(122,44,4); s(124,19,4); s(124,44,4)

# Sparkles
f(20,1,21,2,5); s(33,2,8); s(45,1,6); f(82,2,83,3,8); s(95,1,5); s(105,2,6)
s(8,2,8); s(13,1,6); s(28,0,5)
f(25,61,26,62,6); s(40,62,8); s(52,61,5); f(75,60,76,61,5); s(90,62,8); s(102,60,6)
s(8,61,5); s(15,62,8); s(35,63,6)
s(2,14,8); s(3,22,6); s(2,44,6); s(3,50,8); s(0,10,5); s(0,53,5)
s(58,0,5); s(72,0,8); s(58,63,5); s(72,63,8)

# Render
img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
PX = img.load()
for r in range(H):
    for c in range(W):
        idx = g[r][c]
        if idx == 0: continue
        PX[c, r] = PALETTE[idx] + (255,)

os.makedirs('output', exist_ok=True)
img.resize((W * SCALE, H * SCALE), Image.NEAREST).save('output/magical_portal_hd.png')
print('wrote output/magical_portal_hd.png', (W * SCALE, H * SCALE))
