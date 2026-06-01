#!/usr/bin/env python3
"""Iron Man-style repulsor pulse power-up effect.

100x100 logical -> 5x NEAREST -> 500x500, transparent background.
36 frames @ 24 fps (1.5 s). Plays as a one-shot loop.
"""
import math, os
from PIL import Image

W, H, SCALE = 100, 100, 5
TOTAL_FRAMES = 36
FPS = 24
TAU = math.pi * 2
CX, CY = 50, 50

# Cool tech palette (white core -> cyan-blue) + gold accent
CORE       = (255, 255, 255)
HOT        = (220, 240, 255)
BRIGHT     = (130, 200, 255)
LIGHT_BLUE = (60, 150, 230)
DARK_BLUE  = (30, 80, 170)
GOLD       = (255, 200, 100)
ORANGE     = (255, 140, 60)


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

    # ── Bright core that grows then sustains ─────────
    if frame < 18:
        core_t = frame / 18
        core_radius = 2 + core_t * 10
        core_alpha = 1.0
    else:
        fade_t = (frame - 18) / 18
        core_radius = 12 - fade_t * 8
        core_alpha = max(0, 1.0 - fade_t)
    if core_alpha > 0 and core_radius > 0:
        for dy in range(-int(core_radius) - 1, int(core_radius) + 2):
            for dx in range(-int(core_radius) - 1, int(core_radius) + 2):
                d = math.sqrt(dx * dx + dy * dy)
                if d > core_radius: continue
                edge = 1.0 - d / core_radius
                if   edge > 0.88: col = CORE
                elif edge > 0.65: col = HOT
                elif edge > 0.40: col = BRIGHT
                elif edge > 0.18: col = LIGHT_BLUE
                else:             col = DARK_BLUE
                a = int(255 * edge * core_alpha)
                if a > 0: put(CX + dx, CY + dy, col, a=a)

    # ── Expanding concentric tech rings ──────────────
    N_RINGS = 5
    for r_idx in range(N_RINGS):
        delay = r_idx * 3
        rf = frame - delay
        if rf < 0 or rf > 26: continue
        rt = rf / 26
        radius = rt * 48
        alpha = max(0, 1.0 - rt * 1.1)
        if alpha < 0.05 or radius < 1: continue
        n_pts = max(28, int(radius * 5))
        for i in range(n_pts):
            angle = (i / n_pts) * TAU
            rx = CX + radius * math.cos(angle)
            ry = CY + radius * math.sin(angle)
            col = [HOT, BRIGHT, LIGHT_BLUE, DARK_BLUE, GOLD][r_idx]
            a = int(255 * alpha * 0.85)
            put(rx, ry, col, a=a)

    # ── Cross-beam light spokes ──────────────────────
    if 6 <= frame < 28:
        bt = (frame - 6) / 22
        beam_alpha = max(0, 1.0 - bt * 0.7)
        beam_len = 25 + bt * 22
        rot = frame * 0.05
        for k in range(4):
            angle = k * (TAU / 4) + rot
            for d in range(2, int(beam_len)):
                fade = 1.0 - d / beam_len
                a = int(255 * beam_alpha * fade * 0.7)
                bx = CX + d * math.cos(angle)
                by = CY + d * math.sin(angle)
                if   d < 6:  col = HOT
                elif d < 18: col = BRIGHT
                else:        col = LIGHT_BLUE
                put(bx, by, col, a=a)
                # Make beam slightly thicker
                px = -math.sin(angle); py = math.cos(angle)
                put(bx + px, by + py, col, a=a // 2)

    # ── Gold spark embers flying outward ─────────────
    if frame >= 10:
        N_SPARKS = 36
        for i in range(N_SPARKS):
            off = i * 0.027
            st = ((frame - 10) / 26 + off) % 1.0
            if st < 0.10 or st > 0.95: continue
            rng  = ((math.sin(i * 12.9898 + 78.233) * 43758.5453) % 1 + 1) % 1
            rng2 = ((math.sin(i * 9.7777 + 22.111) * 12345.6789) % 1 + 1) % 1
            angle = rng * TAU
            dist = 5 + (st - 0.1) * 55
            sx = CX + dist * math.cos(angle)
            sy = CY + dist * math.sin(angle)
            sp_alpha = (1.0 - st) ** 0.7 * 0.9
            col = GOLD if rng2 > 0.4 else ORANGE
            a = int(255 * sp_alpha)
            if a > 0:
                put(sx, sy, col, a=a)
                # tiny trail
                tx = CX + (dist - 1) * math.cos(angle)
                ty = CY + (dist - 1) * math.sin(angle)
                put(tx, ty, col, a=a // 2)
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
        'output/powerup_repulsor.gif',
        save_all=True, append_images=gif_frames[1:],
        duration=int(round(1000 / FPS)), loop=0, disposal=2,
        transparency=0, optimize=False,
    )
    print('wrote output/powerup_repulsor.gif')


if __name__ == '__main__':
    main()
