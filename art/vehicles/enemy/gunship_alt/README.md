# AERIAL THIEF · GUNSHIP ALT (variant 1)

Heavier sibling of the standard gunship. Same job — drops a magnetic
claw on a cable to snatch the player's cargo — but a longer, blockier
silhouette with a blunt front bumper instead of a swept nose.

![reference](reference.png)

## Spec

| Field | Value |
|---|---|
| Canvas size       | **132 × 56 px** (render resolution + 4 px padding) |
| Background        | Transparent (alpha = 0) |
| Pixel scale       | 1× native |
| Facing direction  | LEFT (negative X — chases the rig from behind) |
| Anchor (pivot)    | Body center — slice `center` at **(66, 28)** |
| Active sprite bbox | Roughly **x=4..128, y=4..50** |

## Aseprite tags

Same state machine as the sleek gunship — both share the
cable-drop behavior. A single `idle` frame covers it; the rest is
polish. Listed so you can see the full beat-by-beat even if you
only ship `idle`.

| Tag | Frames | When game uses it |
|---|---|---|
| `idle`     | 1+ | Cruise. Flying horizontally toward the rig from off-screen right. |
| `lock_on`  | 1+ | Hovers in place over the cargo for ~12 frames before the drop. Brighter running lights is a nice touch. |
| `dropping` | 1   | Mid-drop pose while the cable extends. Cable + claw are drawn in code — body holds steady. |
| `retreat`  | 1   | Climbs / flees after a grab attempt. Slight nose-up tilt works on the blunt bumper. |
| `damaged`  | 1   | Optional. Dented bumper, flickering lights, smoke trail. Right now we just puff-explode on destruction. |

Cable extension, claw closing, energy field, and engine flame all
get drawn in code on top of your body. The extra tags just let the
game pick a different pose per state if you ship more frames.

## What to draw

- **Blunt front bumper** at the front-left — this is what makes the
  alt different from variant 0
- Long boxy hull
- Skull-and-crossbones decal on the flank (you can redesign it freely)
- Hot-rod painted flame strips along the top edge
- Battle damage spots (scorch marks, dings)
- Engine intakes / vents at the rear
- Red running lights
- A couple of white nav-light dots

## What NOT to draw

- The cable hanging from the belly
- The magnetic claw at the cable tip
- The glowing energy field around the claw
- Engine exhaust trail
- Stun / damage effects

## Palette

Stay inside `art/palette/dlx-master-palette.gpl`. Use **AERIAL THIEF**
for the body, **OUTLINE / DARKS** for shadows, plus the warm orange /
red / yellow ember tones for the painted flame strips and skull decal.

## Variants in code

| Folder | Variant | Distinguishing feature |
|---|---|---|
| `../gunship/`       | 0 | Swept nose, classic silhouette |
| `gunship_alt/` (this) | 1 | Blunt front bumper, longer hull |
| `../harpooner/`     | 2 | Upward harpoon launcher on top |

## Export

```bash
aseprite -b gunship_alt.aseprite \
  --sheet gunship_alt.png \
  --data  gunship_alt.json \
  --sheet-pack --format json-array
```

Or `File → Save As → gunship_alt.png` for a single frame.

Commit `.aseprite` + `.png` together.
