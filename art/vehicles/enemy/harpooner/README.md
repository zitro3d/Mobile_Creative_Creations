# AERIAL THIEF · HARPOONER (variant 2)

Specialized aerial thief that doesn't use a downward cable + claw —
instead it carries a top-mounted harpoon launcher and fires an UPWARD
harpoon to snag cargo from below.

![reference](reference.png)

## Spec

| Field | Value |
|---|---|
| Canvas size       | **110 × 60 px** (in-game render resolution + 4 px margin) |
| Background        | Transparent (alpha = 0) |
| Pixel scale       | 1× (game native — sprite renders at this size on screen) |
| Facing direction  | LEFT (negative X — chases the rig from behind) |
| Anchor (pivot)    | Body center — slice `center` at **(55, 36)** |
| Active sprite bbox | Roughly **x=4..106, y=4..56** inside the canvas |

## Required Aseprite tags

These map to the harpooner's in-game state machine. Single frame
`idle` covers everything; the rest are optional polish. Listed so
you can SEE what beats the sprite passes through and (if you want)
draw a unique pose for each.

| Tag | Frames | When game uses it |
|---|---|---|
| `idle`     | 1+ | Cruise — harpoon loaded, charge LED dim, flying horizontally toward the rig |
| `charging` | 1+ | Lock-on hover for ~12 frames before firing (charge LED ramping up — perfect for a multi-frame loop) |
| `firing`   | 1   | Mid-fire pose — harpoon tip stowed because the tip has already extended out of frame (procedural) |
| `retract`  | 1   | Harpoon cable reeling back in (with or without snagged cargo) |
| `retreat`  | 1   | Climbs / flees away after the attempt (slight nose-up tilt works well) |
| `damaged`  | 1   | Optional — sparking launcher / scorched hull / flickering LED (currently we just puff-explode on destruction) |

Single `idle` frame is fine. The harpoon tip mid-flight, cable,
energy field, and engine flames are ALL procedural — your sprite is
just the body + launcher mast + the loaded tip in the cradle.

## What to draw

- **Hull** — boxy main body (similar proportions to the alt thief)
- **Harpoon launcher mast** on top of the hull (the tall vertical
  mount — what distinguishes the harpooner)
- **Loaded harpoon** sitting in the launcher (the bullet-shaped tip)
- **Charge LED indicator** on the launcher base (4 stages — dim → hot)
- **Skull-and-crossbones decal** on the flank
- **Hot-rod flame strips** along the top edge
- **Battle damage** scorch spots
- Two thruster nozzles on the underside (small white-hot flame
  procedural on top — you draw the nozzle housing only)
- Engine intakes / vents at the rear

## What NOT to draw

- The harpoon **tip mid-flight** (procedural — animates outward when firing)
- The **cable** trailing behind the fired harpoon
- The **glowing energy field** around the harpoon when loaded
- Engine flame from the nozzles (thrFlame is procedural)
- Stun / damage effects on hit

## Charge LED states

The launcher has a 4-stage LED that ramps during charging. You can
draw it dim in `idle` and let the game brighten it programmatically,
OR draw multiple frames (one per stage) tagged appropriately.

## Palette

Stay inside `art/palette/dlx-master-palette.gpl`. Sections:
**AERIAL THIEF** for the body, **OUTLINE / DARKS** for shadows, plus
warm flame tones and a couple of cyan / red highlights for the LED
states.

## Variants in code

| Folder | Variant | Distinguishing feature |
|---|---|---|
| `../gunship/`       | 0 | Swept nose, classic silhouette |
| `../gunship_alt/`   | 1 | Blunt front bumper, longer hull |
| `harpooner/` (this) | 2 | Upward harpoon launcher on top |

## Export

```bash
aseprite -b harpooner.aseprite \
  --sheet harpooner.png \
  --data  harpooner.json \
  --sheet-pack --format json-array
```

Or `File → Save As → harpooner.png` for single frame.

Commit both `.aseprite` + `.png` together, or DM the team.
</parameter>
