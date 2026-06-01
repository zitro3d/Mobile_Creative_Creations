#!/usr/bin/env python3
"""Doctor Strange-style mystic portal power-up effect.

100x100 logical -> 5x NEAREST -> 500x500, transparent background.
48 frames @ 24 fps (2.0 s). Build-up -> spin -> fade -> loop.
"""
import math, os
from PIL import Image

W, H, SCALE = 100, 100, 5
TOTAL_FRAMES = 48
FPS = 24
TAU = math.pi * 2
CX, CY = 50, 50

# Warm mystical palette
CORE   = (255, 255, 230)
WHITE  = (255, 245, 200)
YELLOW = (255, 220, 100)
GOLD   = (255, 180, 60)
ORANGE = (240, 130, 40)
DEEP   = (200, 80, 25)
RED    = (140, 50, 20)


def make_put(PX):
    def put(x, y, c, a=255):
        x = int(round(x)); y = int(round(y))
        if not (0 <= x < W and 0 <= y < H): return
        if a >= 255:
            PX[x, y] = (c[0], c[1], c[2], 255); return
        if a <= 0: return
        er, eg, eb, ea = PX[x, y]
        na = a / 255.0
        oa = na + (ea / 255.0) * (1.0 - na)
        if oa <= 0: return
        ow = (ea / 255.0) * (1.0 - na)
        r = (c[0] * na + er * ow) / oa
        g = (c[1] * na + eg * ow) / oa
        b = (c[2] * na + eb * ow) / oa
        PX[x, y] = (int(r), int(g), int(b), int(oa * 255))
    return put


def build_frame(frame):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    put = make_put(img.load())

    # Phase envelope: build (0-14) -> hold (15-36) -> fade (37-47)
    if frame < 14:
        env = frame / 14
    elif frame < 36:
        env = 1.0
    else:
        env = max(0.0, 1.0 - (frame - 36) / 11)

    # ── Central glowing core ─────────────────────────
    core_r = 2 + env * 5
    if env > 0 and core_r > 0:
        for dy in range(-int(core_r) - 1, int(core_r) + 2):
            for dx in range(-int(core_r) - 1, int(core_r) + 2):
                d = math.sqrt(dx * dx + dy * dy)
                if d > core_r: continue
                edge = 1.0 - d / core_r
                if   edge > 0.85: col = CORE
                elif edge > 0.6:  col = WHITE
                elif edge > 0.35: col = YELLOW
                elif edge > 0.15: col = GOLD
                else:             col = ORANGE
                a = int(255 * edge * env)
                if a > 0: put(CX + dx, CY + dy, col, a=a)

    # ── Outer ring: 8 rune segments, spinning clockwise ─
    outer_r = 38 * (0.25 + 0.75 * env)
    outer_rot = frame * 0.045
    N_SEG = 8
    for seg in range(N_SEG):
        seg_center = (seg / N_SEG) * TAU + outer_rot
        arc_span = (TAU / N_SEG) * 0.55
        n_pts = 18
        for i in range(n_pts):
            p = i / (n_pts - 1) - 0.5  # -0.5..0.5
            angle = seg_center + p * arc_span
            rx = CX + outer_r * math.cos(angle)
            ry = CY + outer_r * math.sin(angle)
            a = int(255 * env * 0.95)
            put(rx, ry, GOLD, a=a)
            # thicker arc (inner)
            rx2 = CX + (outer_r - 1) * math.cos(angle)
            ry2 = CY + (outer_r - 1) * math.sin(angle)
            put(rx2, ry2, ORANGE, a=a)
        # Rune dot accent just outside each segment
        dx = (outer_r + 2.5) * math.cos(seg_center)
        dy = (outer_r + 2.5) * math.sin(seg_center)
        put(CX + dx, CY + dy, WHITE, a=int(255 * env))
        put(CX + dx, CY + dy - 1, YELLOW, a=int(255 * env * 0.7))

    # ── Middle ring: continuous sparkles, counter-clockwise ─
    mid_r = 26 * (0.35 + 0.65 * env)
    N_MID = 56
    for i in range(N_MID):
        angle = (i / N_MID) * TAU - frame * 0.075
        rx = CX + mid_r * math.cos(angle)
        ry = CY + mid_r * math.sin(angle)
        wave = (math.cos(angle + frame * 0.18) + 1) / 2
        a = int(255 * env * (0.30 + 0.70 * wave))
        col = WHITE if wave > 0.85 else (YELLOW if wave > 0.5 else GOLD)
        put(rx, ry, col, a=a)

    # ── Inner ring: 4 cross-points (clock face) ────────
    inner_r = 14 * (0.5 + 0.5 * env)
    inner_rot = frame * 0.055
    for i in range(4):
        angle = (i / 4) * TAU + inner_rot
        rx = CX + inner_r * math.cos(angle)
        ry = CY + inner_r * math.sin(angle)
        a = int(255 * env)
        put(rx, ry, WHITE, a=a)
        put(rx + 1, ry, GOLD, a=a)
        put(rx - 1, ry, GOLD, a=a)
        put(rx, ry + 1, GOLD, a=a)
        put(rx, ry - 1, GOLD, a=a)
        # inner glow
        put(rx, ry, CORE, a=min(255, a))

    # ── Embers drifting outward ──────────────────────
    N_EMB = 30
    for i in range(N_EMB):
        off = i * 0.034
        et = ((frame / TOTAL_FRAMES) + off) % 1.0
        if et < 0.15 or et > 0.95: continue
        rng  = ((math.sin(i * 12.9898 + 5) * 43758.5453) % 1 + 1) % 1
        rng2 = ((math.sin(i * 78.233) * 43758.5453) % 1 + 1) % 1
        angle = rng * TAU
        dist = 8 + (et - 0.15) * 60
        sx = CX + dist * math.cos(angle)
        sy = CY + dist * math.sin(angle)
        ea = (1.0 - et) ** 0.6 * env
        col = WHITE if rng2 > 0.75 else (YELLOW if rng2 > 0.45 else GOLD)
        a = int(255 * ea)
        if a > 0:
            put(sx, sy, col, a=a)
            put(sx + 1, sy, col, a=a // 2)
    return img


def main():
    os.makedirs('output', exist_ok=True)
    frames = []
    for f in range(TOTAL_FRAMES):
        img = build_frame(f)
        frames.append(img.resize((W * SCALE, H * SCALE), Image.NEAREST))
    gif_frames = [f.convert('RGBA').quantize(method=Image.FASTOCTREE, dither=Image.NONE)
                  for f in frames]
    gif_frames[0].save(
        'output/powerup_mystic.gif',
        save_all=True, append_images=gif_frames[1:],
        duration=int(round(1000 / FPS)), loop=0, disposal=2,
        transparency=0, optimize=False,
    )
    print('wrote output/powerup_mystic.gif')


if __name__ == '__main__':
    main()
