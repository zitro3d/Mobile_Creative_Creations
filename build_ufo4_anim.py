#!/usr/bin/env python3
"""Tall, detailed pixel-art saucer with green tractor beam pulling particles up.

Style: chunky pixel-art (no semi-transparency, solid color blocks) but at
higher resolution than ufo3 so portholes and beam stripes read clearly.

Logical 128x240 -> 4x NEAREST -> 512x960. Transparent canvas.
72-frame seamless loop @ 24 fps.

Features:
- Procedurally shaded red dome (3D hemisphere lit from upper-right)
- Tall saucer body with two rows of portholes (top + bottom rim)
- 9 portholes on the top rim arc + 7 on the bottom — all blink in phase-
  offset sequences (top and bottom in counter-phase)
- Bright green emitter spot at the bottom of the underside
- 7 distinct vertical green stripes in the beam (white core through
  outer dark green)
- 14 bright particles streaming UPWARD inside the beam, getting brighter
  as they approach the UFO (suction effect)
- Green floor splash where the beam hits the ground
- Gentle hover bob keeps UFO + beam locked together

Outputs:
  output/ufo4_animated.gif
  output/ufo4_layer_all.gif
  output/ufo4_layer_ufo.gif
  output/ufo4_layer_beam.gif
  output/ufo4_anim_frames/*.png   (per-frame RGBA, VFX-ready)
  output/ufo4_preview.png         (3-up still)
"""
import math, os, shutil
from PIL import Image

W, H, SCALE = 128, 240, 4
TOTAL_FRAMES = 120        # 5 s @ 24 fps — enough for full emerge / beam / absorb cycle
FPS = 24
TAU = math.pi * 2
HCX = W // 2  # 64


def h2r(h):
    return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))


PAL = {
    'x':  None,
    'W':  h2r('#ffffff'),
    'Y':  h2r('#f4d03f'),
    'R':  h2r('#e74c3c'),
    'D':  h2r('#c0392b'),
    'Dd': h2r('#7a1f15'),
    'G1': h2r('#bdc3c7'),
    'G2': h2r('#7f8c8d'),
    'G3': h2r('#34495e'),
    'G4': h2r('#1c2733'),
    'B0': h2r('#d4f7d4'),
    'B1': h2r('#a3f7bf'),
    'B2': h2r('#58d68d'),
    'B3': h2r('#28b463'),
    'B4': h2r('#1e6b3f'),
    # Portal / time-warp palette
    'PH': h2r('#c4f0ff'),   # portal hot (near-white cyan)
    'PB': h2r('#7ec8e3'),   # portal bright (cyan)
    'PL': h2r('#8a6dcc'),   # portal light (blue-purple)
    'PM': h2r('#7232a3'),   # portal mid (purple)
    'PD': h2r('#3a1860'),   # portal dark (deep purple)
}


def put(PX, x, y, key):
    if not (0 <= x < W and 0 <= y < H): return
    # Reveal-radius clipping (used during UFO emergence from portal)
    if _REVEAL_R is not None:
        dx = x - _REVEAL_CX
        dy = y - _REVEAL_CY
        if dx * dx + dy * dy > _REVEAL_R * _REVEAL_R: return
    # Alpha dither (used for fade-in / fade-out)
    if _ALPHA < 0.98:
        if _ALPHA <= 0: return
        threshold = ((x * 17 + y * 23) % 16) / 16.0
        if _ALPHA <= threshold: return
    col = PAL.get(key)
    if col is not None:
        PX[x, y] = col + (255,)


# Module-level state controlling pixel visibility per draw call.
# build_frame sets these before each layer's draw and resets after.
_REVEAL_R = None        # if set, only pixels within this radius of (_REVEAL_CX, _REVEAL_CY) draw
_REVEAL_CX = 0
_REVEAL_CY = 0
_ALPHA = 1.0            # 0..1 — below 1 enables Bayer-like stipple dither


def hover(frame):
    return int(round(math.sin(frame / TOTAL_FRAMES * TAU) * 1))


# ── DOME (large procedurally shaded red hemisphere) ───
DCY_BASE = 28
DR = 14

_Lx, _Ly, _Lz = 0.50, 0.55, 0.67
_Lm = math.sqrt(_Lx * _Lx + _Ly * _Ly + _Lz * _Lz)
LX, LY, LZ = _Lx / _Lm, _Ly / _Lm, _Lz / _Lm


def draw_dome(PX, frame):
    bob = hover(frame)
    cy = DCY_BASE + bob
    for y in range(cy - DR, cy + 1):
        for x in range(HCX - DR, HCX + DR + 1):
            u = (x - HCX) / DR
            v = (cy - y) / DR
            if v < 0: continue
            if u * u + v * v > 1.0: continue
            w = math.sqrt(max(0, 1 - u * u - v * v))
            diff = max(0, u * LX + v * LY + w * LZ)
            glow = 0.45 + 0.15 * w
            i = diff * 0.55 + glow * 0.45
            radial = math.sqrt(u * u + v * v)
            if   radial > 0.96: i *= 0.20
            elif radial > 0.88: i *= 0.55
            elif radial > 0.78: i *= 0.78
            if   i > 0.85: key = 'W'
            elif i > 0.62: key = 'R'
            elif i > 0.38: key = 'D'
            else:          key = 'Dd'
            put(PX, x, y, key)
    # Tiny specular streak on upper-right
    for dx, dy, k in [(4, -10, 'W'), (5, -9, 'W'), (6, -8, 'W'),
                      (7, -6, 'R'), (7, -4, 'R')]:
        put(PX, HCX + dx, cy + dy, k)


# ── SAUCER (tall lens-shape with multiple banded sections) ──
# Rows are y-offset from DCY_BASE
SAUCER_ROWS = [
    # (offset, hw, role)
    (0, 18, 'top_strip'),
    (1, 28, 'top_hi'),
    (2, 36, 'top_hi'),
    (3, 42, 'top_hi'),
    (4, 47, 'rim_top'),
    (5, 50, 'rim_top'),
    (6, 52, 'rim_top'),
    (7, 53, 'rim_max'),
    (8, 53, 'ports_top'),      # top porthole row
    (9, 53, 'seam'),
    (10, 52, 'mid_dark'),
    (11, 50, 'mid_dark'),
    (12, 48, 'ports_bot'),     # bottom porthole row
    (13, 45, 'seam'),
    (14, 41, 'body_bot'),
    (15, 36, 'body_bot'),
    (16, 30, 'under_top'),
    (17, 24, 'under'),
    (18, 18, 'under'),
    (19, 13, 'under_bot'),
    (20, 8,  'under_bot'),
    (21, 5,  'emitter'),
]


def shade_saucer(role, dx, hw):
    rel = dx / max(hw, 1)
    abs_rel = abs(rel)
    if hw > 4 and abs_rel >= 0.96:
        return 'G4'
    if role == 'top_strip':
        return 'G1' if rel > -0.2 else 'G2'
    if role == 'top_hi':
        if rel > 0.4: return 'W'
        if rel > -0.1: return 'G1'
        if rel > -0.5: return 'G2'
        return 'G3'
    if role == 'rim_top':
        if rel > 0.4: return 'G1'
        if rel > -0.3: return 'G2'
        return 'G3'
    if role == 'rim_max':
        if rel > 0.3: return 'G2'
        if rel > -0.3: return 'G3'
        return 'G4'
    if role == 'ports_top':
        return 'G3'
    if role == 'seam':
        return 'G4'
    if role == 'mid_dark':
        if rel > 0.4: return 'G3'
        return 'G4'
    if role == 'ports_bot':
        return 'G3'
    if role == 'body_bot':
        return 'G4'
    if role == 'under_top':
        return 'G4'
    if role == 'under':
        return 'G4'
    if role == 'under_bot':
        return 'G4'
    if role == 'emitter':
        return 'G4'
    return 'G3'


def draw_saucer(PX, frame):
    bob = hover(frame)
    for offset, hw, role in SAUCER_ROWS:
        y = DCY_BASE + offset + bob
        for dx in range(-hw, hw + 1):
            put(PX, HCX + dx, y, shade_saucer(role, dx, hw))

    # ── Top porthole row (9 lights) ──────────────
    blink_t = (frame / TOTAL_FRAMES) % 1.0
    n_top = 9
    rim_rx = 49
    rim_y = DCY_BASE + 8 + bob
    for i in range(n_top):
        theta = math.pi * (i + 0.5) / n_top - math.pi / 2
        px = HCX + int(round(rim_rx * math.sin(theta)))
        phase = (blink_t + i * 0.09) % 1.0
        s = math.sin(phase * TAU)
        if s > 0.6:
            inner, outer = 'W', 'Y'
        elif s > 0.1:
            inner, outer = 'Y', 'D'
        else:
            inner, outer = 'G2', 'G3'
        put(PX, px, rim_y, inner)
        put(PX, px + 1, rim_y, outer)

    # ── Bottom porthole row (7 lights, opposite blink phase) ──
    n_bot = 7
    bot_rx = 42
    bot_y = DCY_BASE + 12 + bob
    for i in range(n_bot):
        theta = math.pi * (i + 0.5) / n_bot - math.pi / 2
        px = HCX + int(round(bot_rx * math.sin(theta)))
        phase = (blink_t + i * 0.12 + 0.5) % 1.0  # offset by half
        s = math.sin(phase * TAU)
        if s > 0.6:
            inner, outer = 'W', 'Y'
        elif s > 0.1:
            inner, outer = 'Y', 'D'
        else:
            inner, outer = 'G3', 'G4'
        put(PX, px, bot_y, inner)
        put(PX, px + 1, bot_y, outer)

    # ── Emitter glow (bright green spot at bottom-center) ──
    emit_cy = DCY_BASE + 22 + bob
    pulse = 0.85 + 0.15 * math.sin(frame / TOTAL_FRAMES * TAU * 3)
    for dy in range(-1, 3):
        hw_e = max(0, int(round(5 * pulse * (1 - max(0, dy) * 0.3))))
        for dx in range(-hw_e, hw_e + 1):
            d = math.sqrt(dx * dx + (dy * 1.5) ** 2)
            if d > hw_e: continue
            edge = 1.0 - d / max(hw_e, 1)
            if edge > 0.75: key = 'W'
            elif edge > 0.45: key = 'B0'
            elif edge > 0.2: key = 'B1'
            else: key = 'B2'
            put(PX, HCX + dx, emit_cy + dy, key)


# ── BEAM (vertical stripes + upward particles + floor splash) ──
BEAM_BOT = 222
HW_TOP = 7
HW_BOT = 40


def draw_beam(PX, frame):
    bob = hover(frame)
    TOP = DCY_BASE + 24 + bob
    max_h = BEAM_BOT - TOP
    if max_h <= 0: return

    # ── Vertical stripe gradient (static pattern, no scrolling) ──
    for y in range(TOP, BEAM_BOT + 1):
        rel = (y - TOP) / max_h
        hw = HW_TOP + rel * (HW_BOT - HW_TOP)
        for dx in range(-int(hw), int(hw) + 1):
            u = dx / hw
            au = abs(u)
            if   au > 0.92: key = 'B4'
            elif au > 0.75: key = 'B3'
            elif au > 0.55: key = 'B2'
            elif au > 0.32: key = 'B1'
            elif au > 0.12: key = 'B0'
            else:           key = 'W'
            put(PX, HCX + dx, y, key)

    # ── Upward-streaming particles (suction effect) ──
    # Two waves: 5 large slow particles (1 traversal/loop), 9 small fast (2/loop)
    def draw_particle(px, py_f, rel_y, big):
        py_i = int(py_f)
        if not (0 <= py_i < H): return
        # Brightness ramps up as the particle approaches the top
        if rel_y < 0.15:
            inner, trail = 'W', 'W'
        elif rel_y < 0.40:
            inner, trail = 'W', 'B0'
        elif rel_y < 0.70:
            inner, trail = 'B0', 'B1'
        else:
            inner, trail = 'B1', 'B2'
        put(PX, px, py_i, inner)
        if big:
            put(PX, px + 1, py_i, inner)
            put(PX, px, py_i + 1, trail)
            put(PX, px + 1, py_i + 1, trail)
            put(PX, px, py_i + 2, trail)
        else:
            put(PX, px, py_i + 1, trail)

    n_large = 5
    for i in range(n_large):
        phase = ((i / n_large) + (frame / TOTAL_FRAMES) * 1.0) % 1.0
        rel_y = 1.0 - phase           # phase 0 = bottom, 1 = top → rel_y inverts
        py = TOP + rel_y * max_h
        hw_here = HW_TOP + rel_y * (HW_BOT - HW_TOP)
        rng = ((math.sin(i * 12.9898 + 4) * 43758.5453) % 1 + 1) % 1
        x_off = (rng - 0.5) * 1.2 * hw_here
        px = HCX + int(round(x_off))
        draw_particle(px, py, rel_y, big=True)

    n_small = 9
    for i in range(n_small):
        phase = ((i / n_small) + (frame / TOTAL_FRAMES) * 2.0) % 1.0
        rel_y = 1.0 - phase
        py = TOP + rel_y * max_h
        hw_here = HW_TOP + rel_y * (HW_BOT - HW_TOP)
        rng = ((math.sin(i * 12.9898 + 78.233) * 43758.5453) % 1 + 1) % 1
        x_off = (rng - 0.5) * 1.6 * hw_here
        px = HCX + int(round(x_off))
        draw_particle(px, py, rel_y, big=False)

    # ── Floor splash (green glow on the ground) ──
    splash_hw = HW_BOT + 6
    for dy in range(0, 5):
        for dx in range(-splash_hw - dy, splash_hw + dy + 1):
            d = math.sqrt(dx * dx + (dy * 2.0) ** 2)
            if d > splash_hw + dy: continue
            fade = 1.0 - d / (splash_hw + dy)
            if fade > 0.7:   key = 'B0'
            elif fade > 0.4: key = 'B1'
            elif fade > 0.2: key = 'B2'
            else:             key = 'B3'
            put(PX, HCX + dx, BEAM_BOT + dy, key)


# ── TIMING (120-frame / 5-second cycle) ───────────────
# Sequence:
#   0-9    portal opens (transition device for the UFO's appearance)
#   10-19  UFO emerges from the portal core (radial reveal grows)
#   20-29  portal closes, UFO fully visible, beam off
#   30-32  beam fades in
#   33-86  beam ON
#   87-89  beam fades out                (30..89 → 60 frames = 2.5 s)
#   90-104 UFO settled, no beam, no portal
#   105-119 UFO fades out (back to empty for the loop reset)
PORTAL_OPEN_END   = 10
PORTAL_HOLD_END   = 20
PORTAL_CLOSE_END  = 30
BEAM_FADEIN_END   = 33
BEAM_FULL_END     = 87
BEAM_FADEOUT_END  = 90
UFO_FADE_START    = 105
UFO_FADE_END      = 120
REVEAL_MAX_R      = 100


def portal_env(frame):
    """Portal envelope — only active during the appearance transition (0..29)."""
    if frame < PORTAL_OPEN_END:
        return frame / PORTAL_OPEN_END
    if frame < PORTAL_HOLD_END:
        return 1.0
    if frame < PORTAL_CLOSE_END:
        return 1.0 - (frame - PORTAL_HOLD_END) / (PORTAL_CLOSE_END - PORTAL_HOLD_END)
    return 0.0


def ufo_reveal_radius(frame):
    """0 → REVEAL_MAX_R during emergence (frames 10..20). Else = no clipping."""
    if frame < PORTAL_OPEN_END:
        return 0.0
    if frame < PORTAL_HOLD_END:
        t = (frame - PORTAL_OPEN_END) / (PORTAL_HOLD_END - PORTAL_OPEN_END)
        return t * REVEAL_MAX_R
    return float('inf')   # no clipping


def ufo_alpha(frame):
    """1.0 for most of the loop, fades 1→0 during the loop's tail (105..120)."""
    if frame < UFO_FADE_START:
        return 1.0
    if frame < UFO_FADE_END:
        return 1.0 - (frame - UFO_FADE_START) / (UFO_FADE_END - UFO_FADE_START)
    return 0.0


def beam_alpha(frame):
    """0 outside beam-on window. Fades in/out at the edges of the 60-frame ON period."""
    if frame < PORTAL_CLOSE_END: return 0.0
    if frame < BEAM_FADEIN_END:
        return (frame - PORTAL_CLOSE_END) / (BEAM_FADEIN_END - PORTAL_CLOSE_END)
    if frame < BEAM_FULL_END: return 1.0
    if frame < BEAM_FADEOUT_END:
        return 1.0 - (frame - BEAM_FULL_END) / (BEAM_FADEOUT_END - BEAM_FULL_END)
    return 0.0


# ── PORTAL (time-warp swirling vortex centered on the UFO) ──────
# Drawn BEHIND the UFO so the saucer reads as emerging through it.
PORTAL_MAX_R = 56


def draw_portal(PX, frame):
    bob = hover(frame)
    PCX = HCX
    PCY = DCY_BASE + 8 + bob       # centered on the saucer body

    env = portal_env(frame)
    if env < 0.02: return
    r_outer = PORTAL_MAX_R * env
    rotation = frame * 0.13

    # 1. Soft outer halo ring (the portal's outer boundary)
    if r_outer > 4:
        n_pts = int(r_outer * 4)
        for i in range(n_pts):
            theta = (i / n_pts) * TAU + rotation * 0.35
            px = PCX + r_outer * math.cos(theta)
            py = PCY + r_outer * math.sin(theta)
            put(PX, int(round(px)), int(round(py)), 'PM')

    # 2. Swirling spiral arms (4 logarithmic spiral arms)
    n_arms = 4
    n_segs = max(20, int(r_outer * 1.4))
    for arm in range(n_arms):
        base_angle = arm * (TAU / n_arms) + rotation
        for s in range(n_segs):
            t = s / n_segs                  # 0 at center, 1 at edge
            r = r_outer * (0.05 + t * 0.95)
            theta = base_angle + t * 4.8    # 4.8 radians of swirl
            px = PCX + r * math.cos(theta)
            py = PCY + r * math.sin(theta)
            if   t < 0.18: key = 'W'
            elif t < 0.38: key = 'PH'
            elif t < 0.58: key = 'PB'
            elif t < 0.78: key = 'PL'
            elif t < 0.92: key = 'PM'
            else:          key = 'PD'
            put(PX, int(round(px)), int(round(py)), key)

    # 3. Inner bright core (where UFO appears to emerge)
    core_r = max(1, int(round(8 * env)))
    for dy in range(-core_r - 1, core_r + 2):
        for dx in range(-core_r - 1, core_r + 2):
            d = math.sqrt(dx * dx + dy * dy)
            if d > core_r: continue
            edge = 1.0 - d / max(core_r, 1)
            if   edge > 0.78: key = 'W'
            elif edge > 0.55: key = 'PH'
            elif edge > 0.30: key = 'PB'
            elif edge > 0.10: key = 'PL'
            else:             key = 'PM'
            put(PX, PCX + dx, PCY + dy, key)

    # 4. Energy sparks orbiting and pulsing outward
    n_sparks = 28
    for i in range(n_sparks):
        spark_phase = ((frame / TOTAL_FRAMES) * 2 + i / n_sparks) % 1.0
        if spark_phase > 0.85: continue
        theta_off = (math.sin(i * 9.27) * 100) % TAU
        theta = spark_phase * TAU + theta_off + rotation * 0.3
        # Radius sweeps outward as the spark ages
        r = r_outer * (0.25 + spark_phase * 0.75)
        px = PCX + r * math.cos(theta)
        py = PCY + r * math.sin(theta)
        if   spark_phase < 0.25: key = 'W'
        elif spark_phase < 0.55: key = 'PH'
        elif spark_phase < 0.75: key = 'PB'
        else:                    key = 'PL'
        put(PX, int(round(px)), int(round(py)), key)
        # Tiny trail pixel just behind it
        if spark_phase > 0.10 and spark_phase < 0.7:
            tr = r * 0.92
            tx = PCX + tr * math.cos(theta)
            ty = PCY + tr * math.sin(theta)
            put(PX, int(round(tx)), int(round(ty)), 'PM')


def build_frame(frame, layers=frozenset({'ufo', 'beam'})):
    global _REVEAL_R, _REVEAL_CX, _REVEAL_CY, _ALPHA
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    PX = img.load()

    # Reset reveal/alpha (no clipping by default)
    _REVEAL_R = None
    _ALPHA = 1.0

    # Portal first (behind), only during its active window
    if 'portal' in layers and portal_env(frame) > 0.02:
        draw_portal(PX, frame)

    # Beam — only during its on-window, with edge fades
    if 'beam' in layers:
        b = beam_alpha(frame)
        if b > 0.02:
            _ALPHA = b
            draw_beam(PX, frame)
            _ALPHA = 1.0

    # UFO — radial reveal during emergence, alpha fade at the tail
    if 'ufo' in layers:
        r = ufo_reveal_radius(frame)
        a = ufo_alpha(frame)
        if a > 0.02 and r > 0.5:
            if not math.isinf(r):
                _REVEAL_R = r
                _REVEAL_CX = HCX
                _REVEAL_CY = DCY_BASE + 8
            _ALPHA = a
            draw_saucer(PX, frame)
            draw_dome(PX, frame)
            _REVEAL_R = None
            _ALPHA = 1.0

    return img


def render_layer_gif(name, layers, save_frames=False):
    frames = []
    if save_frames:
        # Per-layer frame folder — VFX-ready PNG sequence
        out_dir = ('output/ufo4_anim_frames' if name == 'all'
                   else f'output/ufo4_layer_{name}_frames')
        os.makedirs(out_dir, exist_ok=True)
    for f in range(TOTAL_FRAMES):
        img = build_frame(f, layers=layers)
        big = img.resize((W * SCALE, H * SCALE), Image.NEAREST)
        frames.append(big)
        if save_frames:
            big.save(f'{out_dir}/frame_{f:03d}.png')
    gif_frames = [f.convert('RGBA').quantize(method=Image.FASTOCTREE, dither=Image.NONE)
                  for f in frames]
    gif_frames[0].save(
        f'output/ufo4_layer_{name}.gif',
        save_all=True, append_images=gif_frames[1:],
        duration=int(round(1000 / FPS)), loop=0, disposal=2,
        transparency=0, optimize=False,
    )
    print(f'wrote output/ufo4_layer_{name}.gif')
    return frames


def main():
    os.makedirs('output', exist_ok=True)
    # Combined composite includes the portal layer
    all_frames    = render_layer_gif('all',    {'ufo', 'beam', 'portal'}, save_frames=True)
    shutil.copy('output/ufo4_layer_all.gif', 'output/ufo4_animated.gif')
    print('wrote output/ufo4_animated.gif')
    # Per-layer GIFs + per-frame PNG sequences for VFX compositing
    ufo_frames    = render_layer_gif('ufo',    {'ufo'},    save_frames=True)
    beam_frames   = render_layer_gif('beam',   {'beam'},   save_frames=True)
    portal_frames = render_layer_gif('portal', {'portal'}, save_frames=True)

    # 4-up preview: each layer at a frame where it's at peak.
    # All composite during beam-on (frame 50), UFO mid-beam, beam mid-on,
    # portal at its peak (frame 15 — UFO mid-emergence).
    cols = [all_frames[50], ufo_frames[50], beam_frames[50], portal_frames[15]]
    sheet = Image.new('RGBA', (W * SCALE * len(cols), H * SCALE), (28, 28, 32, 255))
    for i, s in enumerate(cols):
        sheet.paste(s, (i * W * SCALE, 0), s)
    sheet.save('output/ufo4_preview.png')
    print('wrote output/ufo4_preview.png')


if __name__ == '__main__':
    main()
