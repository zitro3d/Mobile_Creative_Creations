#!/usr/bin/env python3
"""Separate "emergence" FX layer for the portal — sparkles + energy
trails streaming OUT of the opening, as if a figure just stepped
through and is dragging the portal's magic with them.

Standalone TRANSPARENT layer, same canvas as the portal (160x250 logical
-> 8x -> 1280x2000) so it composites directly on top. Matches the vortex
palette (pink/cyan/white). Seamless 24-frame loop @ 12fps.

Output: output/portal_emerge.gif (transparent, looping) + output/emerge_frames/.
"""
import os, math, random
from PIL import Image

W, H, SCALE = 160, 250, 8
N_FRAMES = 24
FPS = 12
TAU = 2 * math.pi

# ── Palette (FX subset of the locked portal palette) ──
HOT_PINK  = (235, 110, 180)
SOFT_PINK = (255, 170, 215)
CYAN      = (130, 200, 245)
PALE_CYAN = (200, 235, 255)
DEEP_BLUE = (60, 75, 165)
WHITE     = (255, 255, 255)
PALETTE   = [HOT_PINK, SOFT_PINK, CYAN, PALE_CYAN, DEEP_BLUE, WHITE]

# Emission origin = the portal mouth (lower-centre of the opening).
OX, OY = 80, 150

# ── Sparkle particles: spiral out of the mouth with comet trails ─
random.seed(7)
PARTICLES = []
for _ in range(64):
    PARTICLES.append(dict(
        phase=random.random(),
        sx=OX + random.uniform(-9, 9),
        sy=random.uniform(120, 205),          # born along the glowing opening
        ang=random.uniform(0, TAU),
        swirl=random.uniform(-2.2, 2.2),       # spiral tightness (matches vortex)
        reach=random.uniform(55, 105),
        big=random.random() < 0.55,
    ))

# Trailing ribbon lines that undulate out of the mouth (the "lines follow").
RIBBONS = [
    dict(x=72, amp=7,  waves=2.0, phase=0.0,  length=92),
    dict(x=80, amp=5,  waves=2.6, phase=1.7,  length=104),
    dict(x=88, amp=8,  waves=1.8, phase=3.3,  length=88),
    dict(x=84, amp=4,  waves=3.0, phase=5.0,  length=98),
]

TRAIL = [(0.00, WHITE), (0.045, PALE_CYAN), (0.09, CYAN),
         (0.14, SOFT_PINK), (0.19, HOT_PINK), (0.24, HOT_PINK)]


def particle_pos(p, frac, t):
    ang = p['ang'] + p['swirl'] * frac + 0.7 * math.sin(TAU * t)
    r = p['reach'] * (frac ** 0.85)
    x = p['sx'] + math.cos(ang) * r * 0.6
    y = p['sy'] + math.sin(ang) * r * 0.55 + 0.55 * r   # net downward / forward
    return x, y


def envelope(frac):
    """Fade in at birth, fade out at death → seamless loop, no pop."""
    if frac < 0.06:
        return frac / 0.06
    if frac > 0.82:
        return max(0.0, (1.0 - frac) / 0.18)
    return 1.0


def render_frame(t, frame_idx):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    PX = img.load()

    def put(x, y, c, env=1.0):
        x, y = int(round(x)), int(round(y))
        if not (0 <= x < W and 0 <= y < H):
            return
        # Pixel-art "alpha" via ordered dither when the element is fading.
        if env < 0.95:
            thr = (x * 7 + y * 13 + frame_idx) % 10 / 10.0
            if thr > env:
                return
        PX[x, y] = c + (255,)

    def blob(x, y, c, env=1.0, r=1):
        # filled round-ish blob of radius r (r=1 -> plus, r=2 -> 13px disc)
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r + (1 if r > 1 else 0):
                    put(x + dx, y + dy, c, env)

    # Undulating ribbon lines streaming out of the mouth
    for rb in RIBBONS:
        steps = rb['length']
        for s in range(steps):
            f = s / steps
            yy = OY - 8 + f * rb['length']
            xx = (rb['x'] + rb['amp'] * math.sin(f * rb['waves'] * TAU + TAU * t + rb['phase'])
                  + 6 * math.sin(TAU * t) * f)
            if f < 0.18:
                c = SOFT_PINK
            elif f < 0.45:
                c = HOT_PINK
            elif f < 0.72:
                c = CYAN
            else:
                c = DEEP_BLUE
            env = (min(1.0, f / 0.08)) * max(0.0, 1.0 - (f - 0.45) / 0.55)
            put(xx, yy, c, env)
            if rb['amp'] >= 7 and f < 0.5:        # thicken the bright base
                put(xx + 1, yy, c, env * 0.7)

    # Sparkle particles with thick comet trails
    for p in PARTICLES:
        frac = (t + p['phase']) % 1.0
        env = envelope(frac)
        if env <= 0.02:
            continue
        base_r = 2 if p['big'] else 1
        for k, (lag, col) in enumerate(TRAIL):
            tf = frac - lag
            if tf < 0:
                break
            x, y = particle_pos(p, tf, t)
            e = env * (1.0 - k / (len(TRAIL) + 1))
            # Trail tapers: fat near the head, thinner toward the tail.
            r = base_r + 1 if k == 0 else base_r if k <= 2 else max(1, base_r - 1)
            blob(x, y, col, e, r)
        # Bright sparkle head on top: glow halo then solid white core.
        hx, hy = particle_pos(p, frac, t)
        blob(hx, hy, PALE_CYAN, env * 0.8, base_r + 1)
        blob(hx, hy, WHITE, env, base_r)
    return img


# ── Transparent-palette GIF export ────────────────────
TRANSP = 0
flat = [0, 0, 0]
cidx = {}
for n, c in enumerate(PALETTE):
    cidx[c] = n + 1
    flat += list(c)
flat += [0, 0, 0] * (256 - len(PALETTE) - 1)


def to_p(rgba):
    p = Image.new('P', (W, H))
    p.putpalette(flat)
    out = bytearray(W * H)
    for n, px in enumerate(rgba.getdata()):
        out[n] = TRANSP if px[3] == 0 else cidx.get(px[:3], TRANSP)
    p.frombytes(bytes(out))
    return p.resize((W * SCALE, H * SCALE), Image.NEAREST)


os.makedirs('output/emerge_frames', exist_ok=True)
gif_frames = []
for f in range(N_FRAMES):
    t = f / N_FRAMES
    rgba = render_frame(t, f)
    rgba.resize((W * SCALE, H * SCALE), Image.NEAREST).save('output/emerge_frames/frame_%02d.png' % f)
    gif_frames.append(to_p(rgba))

gif_frames[0].save(
    'output/portal_emerge.gif', save_all=True, append_images=gif_frames[1:],
    duration=int(1000 / FPS), loop=0, transparency=TRANSP, disposal=2, optimize=False)
print('wrote output/portal_emerge.gif', N_FRAMES, 'frames', (W * SCALE, H * SCALE))
