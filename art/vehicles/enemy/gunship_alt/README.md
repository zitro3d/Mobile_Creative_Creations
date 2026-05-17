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

These map to the alt-gunship's in-game state machine (same as the
sleek gunship — both variants share the same cable-drop behavior).
Single frame `idle` covers everything; the rest are optional polish.
Listed so you can SEE what beats the sprite passes through and (if
you want) draw a unique pose for each.

| Tag | Frames | When game uses it |
|---|---|---|
| `idle`     | 1+ | Cruise — flying horizontally toward the rig from off-screen right (default pose) |
| `lock_on`  | 1+ | Hovers in place over the cargo for ~12 frames before the drop (running lights brighter is a nice option) |
| `dropping` | 1   | Mid-drop pose while the cable extends downward (cable + claw are procedural — body just holds steady) |
| `retreat`  | 1   | Climbs / flees away after a grab attempt (slight nose-up tilt works well on the blunt bumper) |
| `damaged`  | 1   | Optional — dented bumper / flickering lights / smoke trail (currently we just puff-explode the sprite on destruction) |

Single `idle` frame is fine. The cable extension, claw closing,
energy field, and engine flame are ALL procedural — your sprite is
just the body. The extra tags above just tell the engine "use this
pose during this state" so the gunship reads more alive if you
choose to draw them.

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
