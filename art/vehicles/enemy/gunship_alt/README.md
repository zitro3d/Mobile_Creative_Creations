# AERIAL THIEF · GUNSHIP ALT (variant 1)

Heavier sibling of the standard gunship. Same role — drops a magnetic
claw on a cable to snatch the player's cargo — but a longer, blockier
silhouette with a blunt front bumper instead of a swept nose.

![reference](reference.png)

## Spec

| Field | Value |
|---|---|
| Canvas size       | **132 × 56 px** (in-game render resolution + 4 px margin) |
| Background        | Transparent (alpha = 0) |
| Pixel scale       | 1× (game native — sprite renders at this size on screen) |
| Facing direction  | LEFT (negative X — chases the rig from behind) |
| Anchor (pivot)    | Body center — slice `center` at **(66, 28)** |
| Active sprite bbox | Roughly **x=4..128, y=4..50** inside the canvas |

## Required Aseprite tags

| Tag | Frames | When game uses it |
|---|---|---|
| `idle`     | 1+ | Cruising / hovering pose |

Single frame is fine. Cable extension, claw closing, retreat motion
are all procedural in code.

## What to draw

- **Blunt front bumper** at the front-left (no swept nose — this is
  what distinguishes the alt from variant 0)
- Long boxy hull
- Skull-and-crossbones decal on the flank (already in code, you can
  redesign it freely)
- Hot-rod painted flame strips along the top edge
- Battle damage spots (scorch marks, dings)
- Engine intakes / vents at the rear
- Red running lights
- A couple of white nav-light dots

## What NOT to draw

- The cable extending downward from the belly
- The magnetic claw at the cable tip
- The glowing energy field around the claw
- Engine exhaust trail
- Stun / damage effects

All procedural in the game.

## Palette

Stay inside `art/palette/dlx-master-palette.gpl`. Dedicated sections:
**AERIAL THIEF** for the body, **OUTLINE / DARKS** for shadows, plus
the warm orange / red / yellow ember tones for the painted flame strips
and skull decal.

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

Or `File → Save As → gunship_alt.png` for single frame.

Commit both `.aseprite` + `.png` together, or DM the team.
</parameter>
