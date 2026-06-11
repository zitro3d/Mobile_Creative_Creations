# THE AURORA ENGINE — Level 10 environment brief

The cosmic endgame biome. The rig has broken through the icecave
ceiling into the void where the Engine hangs. Distinct silhouette
language is mandatory — no mountains, no derricks, no cave spikes.

## Background art (currently procedural — replace later)
The level renders entirely procedurally today (see
`drawAuroraHorizon()` in the main HTML). Once we want hand-painted
sprite reference, drop the following PNGs in this folder:

- `monolith.png` — a single engine monolith (tall dark pylon with
  brass-lit accent strip + 2–3 rotating brass rings). The horizon
  composes 4 of these at varying scales.
- `core_glow.png` — distant brass core radial (soft sun-like halo,
  brand brass at center fading to violet edge).
- `cable_anchor.png` — top finial where the suspended catenary
  cables tie into a monolith. Optional.
- `debris_sheet.png` — small drifting cosmic debris (asteroid
  chunks, brass shards, broken tiles) at 1×, packed sheet.

## Palette
Stay inside `art/palette/dlx-master-palette.gpl`. Aurora-specific
swatches that ship in code today (add as new palette rows if you
want them in the .gpl):

| Hex       | Use                                  |
|-----------|--------------------------------------|
| `#04020c` | cosmic void (sky floor + monolith)   |
| `#1c0838` | ground band                          |
| `#46286a` | violet sky midtone                   |
| `#ffd060` | brass core (brand)                   |
| `#ffe28a` | brass highlight (brand)              |
| `#ff64dc` | aurora ribbon — magenta              |
| `#64dcff` | aurora ribbon — cyan                 |
| `#b478ff` | aurora ribbon — violet midtone       |

## Silhouette rules
- Vertical, monumental — pillars not mountains
- Floating, with cables suggesting suspension
- Brass-lit accents always face the camera (no full-shadow rims)
- Engine rings spin slowly — telegraph through frame phase, not
  blur

## Foreground / parallax debris
- 22 drifting fragments today, 3 depth bands (far/mid/near)
- Shapes: small circle, streak, diamond, asteroid chunk
- Movement: pure left scroll at fractional speed of PIPE_SPEED_BASE

## Obstacles (pillars)
Aurora-unique obstacle types — no more reusing sunset's cargo/junk
crates. Both render entirely in code today; sprite hand-off later.

- `engineorb` — tapered cosmic pylon with a brass-lit central seam,
  rivet pips, and a glowing brass orb cap at the gap-facing tip
  (radial gold halo). Echoes the horizon engine monoliths.
- `monolithchunk` — jagged fractured monolith piece with a
  brass-lit broken edge along the fracture, embedded star
  pinpricks, and a half-broken brass ring fragment on taller
  chunks.

## Pickups (loose loot)
Aurora-unique `debrisSet`. All render in code today.

- `brass_shard` — pointed brass triangle, bright facet + pip
- `gear_ring` — 6-notched brass gear with hollow violet centre
- `plasma_shard` — vertical magenta-cyan plasma fragment on a dark
  spine, soft halo
- `engine_coil` — dark brass spring with 5 windings + end-cap pips

## What NOT to draw
- Mountain silhouettes (this was the v429 bug — aurora was falling
  through to sunset's mountains; fixed in v434)
- Aurora ribbons themselves — those are gradient-based and live in
  `bgCache.aurora` (computed at theme switch)
- Star field — handled by the global theme stars
- Generic cargo/junk crates — replaced by engineorb / monolithchunk
- Boss — see `art/creatures/maker/`

## Procedural FX in code
- Brass core pulse
- Aurora ribbon wave (sin + phase)
- Debris drift + rotation
- Monolith ring rotation
- Cap blinker pulse on top of each monolith
