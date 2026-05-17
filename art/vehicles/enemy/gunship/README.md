# AERIAL THIEF · DLX GUNSHIP

Enemy aircraft. Drops a magnetic claw on a cable to snatch the
player's cargo. **Body only** — the cable + claw are drawn in code.

![reference](reference.png)

## Spec

| Field | Value |
|---|---|
| Canvas size       | **100 × 44 px** (render resolution + 2 px padding) |
| Background        | Transparent (alpha = 0) |
| Pixel scale       | 1× native |
| Facing direction  | LEFT (negative X — chases the rig from behind) |
| Anchor (pivot)    | Body center — slice `center` at **(50, 22)** |
| Active sprite bbox | Roughly **x=2..96, y=2..42** (border is padding) |

## Aseprite tags

These map to the gunship's in-game state machine. One `idle` frame
covers the whole sprite; the rest is polish. Listed so you can see
the full beat-by-beat of the animation, even if you only ship `idle`.

| Tag | Frames | When game uses it |
|---|---|---|
| `idle`     | 1+ | Cruise. Flying horizontally toward the rig from off-screen right. |
| `lock_on`  | 1+ | Hovers in place over the cargo for ~12 frames before the drop. Brighter running lights is a nice touch. |
| `dropping` | 1   | Mid-drop pose while the cable extends. Cable + claw are drawn in code — body just holds steady. |
| `retreat`  | 1   | Climbs / flees away after a grab attempt. Slight nose-up tilt works well. |
| `damaged`  | 1   | Optional. Cracked canopy, flickering lights, smoke trail. Right now we just puff-explode on destruction. |

The cable extension, claw closing, energy field, and engine flame
are all done in code — you don't have to draw any of them. The extra
tags just let the game pick a different pose per state if you ship
multiple frames.

## What to draw

- Swept nose at the front-left (faces LEFT)
- Main hull (the chunky 40-wide body)
- Tail at the back-right
- Engine intakes / nozzles
- Two red running lights (under the nose + at the rear)
- Two white nav-light dots on the underside
- Cockpit / canopy if you want one

## What NOT to draw

- The cable hanging from the belly
- The magnetic claw at the cable tip
- The glowing energy field around the claw
- Engine exhaust trail
- Stun / damage effects

## SMASHED variant

No damage variant yet — the gunship puff-explodes on destruction.
A `damaged` frame (cracked canopy, flickering lights, smoke trail)
would be nice polish if you want to take it.

## Palette

Stay inside `art/palette/dlx-master-palette.gpl`. Use the
**AERIAL THIEF** section for the body and **OUTLINE / DARKS** for
shadows + silhouette.

## Variants in code

| Folder | Variant | Distinguishing feature |
|---|---|---|
| `gunship/` (this)   | 0 | Swept nose, classic silhouette |
| `../gunship_alt/`   | 1 | Blunt front bumper, longer hull |
| `../harpooner/`     | 2 | Upward harpoon launcher on top |

## Export

```bash
aseprite -b gunship.aseprite \
  --sheet gunship.png \
  --data  gunship.json \
  --sheet-pack --format json-array
```

Or `File → Save As → gunship.png` for a single frame.

Commit `.aseprite` + `.png` together.
