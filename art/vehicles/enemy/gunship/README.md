# AERIAL THIEF · DLX GUNSHIP

Enemy aircraft that drops a magnetic claw on a cable to snatch the
player's cargo. This sprite is the **gunship body only** — the cable
and claw are procedural.

![reference](reference.png)

## Spec

| Field | Value |
|---|---|
| Canvas size       | **100 × 44 px** (in-game render resolution + 2 px margin all sides) |
| Background        | Transparent (alpha = 0) |
| Pixel scale       | 1× (game native — sprite renders at this size on screen) |
| Facing direction  | LEFT (negative X — chases the rig from behind) |
| Anchor (pivot)    | Body center — slice `center` at **(50, 22)** |
| Active sprite bbox | Roughly **x=2..96, y=2..42** inside the canvas (border is intentional padding) |

## Required Aseprite tags

| Tag | Frames | When game uses it |
|---|---|---|
| `idle`     | 1+ | Cruising / hovering pose |

Single frame is fine. The function-level animation (cable extending,
claw closing, retreat) is all procedural — your sprite is just the
static body.

## What to draw

- Swept nose at the front-left (the gunship faces LEFT)
- Main hull (the chunky 40-wide body)
- Tail at the back-right
- Engine intakes / nozzles
- Two red running lights (under the nose + at the rear)
- Two white nav-light dots on the underside
- Cockpit / canopy if you want one

## What NOT to draw

- The cable extending downward from the belly
- The magnetic claw at the cable tip
- The glowing energy field around the claw when extended
- Engine exhaust trail
- Stun / damage effects

All four are added procedurally in the game.

## SMASHED variant (when destroyed)

We don't have a damage variant yet — the gunship currently just
disappears in a puff of explosion when destroyed. If you'd like to add
a `damaged` tagged frame (e.g. cracked canopy, flickering lights, smoke
trail), it's optional polish.

## Palette

Stay inside `art/palette/dlx-master-palette.gpl`. The dedicated section
is **AERIAL THIEF**. You can also pull from the universal **OUTLINE /
DARKS** section for shadows and silhouette.

## Variants

The game already has TWO gunship variants in code:

- **Variant 1 — Gunship** (this one — claw on a cable)
- **Variant 2 — Harpooner** (fires an UPWARD harpoon instead)

If/when we ship the harpooner sprite, it'll live in
`art/vehicles/enemy/harpooner/`. For now, focus on the gunship.

## Export

When ready:

```bash
aseprite -b gunship.aseprite \
  --sheet gunship.png \
  --data  gunship.json \
  --sheet-pack --format json-array
```

Or `File → Save As → gunship.png` for single frame.

Commit both `.aseprite` + `.png` together, or DM the team.
</parameter>
