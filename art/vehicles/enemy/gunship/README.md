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

These map to the gunship's in-game state machine. Single frame `idle`
covers everything — the others are optional polish. We list them so
you can SEE what beats the sprite passes through and (if you want)
draw a unique pose for each.

| Tag | Frames | When game uses it |
|---|---|---|
| `idle`     | 1+ | Cruise — flying horizontally toward the rig from off-screen right (default pose) |
| `lock_on`  | 1+ | Hovers in place over the cargo for ~12 frames before the drop (running lights brighter is a nice option) |
| `dropping` | 1   | Mid-drop pose while the cable extends downward (cable + claw are procedural — body just holds steady) |
| `retreat`  | 1   | Climbs / flees away after a grab attempt (slight nose-up tilt works well here) |
| `damaged`  | 1   | Optional — cracked canopy / flickering lights / smoke trail (currently we just puff-explode the sprite on destruction) |

Single `idle` frame is fine. The cable extension, claw closing,
energy field, and engine flame are ALL procedural — your sprite is
just the body. The extra tags above just tell the engine "use this
pose during this state" so the gunship reads more alive if you
choose to draw them.

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
