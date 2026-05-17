# HERO RIG · ROAD KILL

The current player rig. DLX-branded mid-haul cargo hauler.

![reference](reference.png)
![smashed B-alt](reference_smashed.png)

## Spec

| Field | Value |
|---|---|
| Canvas size       | **58 × 52 px** |
| Background        | Transparent (alpha = 0) |
| Pixel scale       | 1× native |
| Facing direction  | RIGHT (positive X) |
| Anchor (pivot)    | Center of hull — slice `center` at **(29, 26)** |

## Aseprite tags

The tags map to the rig's in-game state machine. A single `idle`
frame + a single `damaged` frame covers everything; the rest is
polish. Listed here so you can see what the game does with the
sprite even if you only ship the basics.

| Tag | Frames | When game uses it |
|---|---|---|
| `idle`        | 1+ | Default flight pose. Drawn every frame during STATE_PLAY. |
| `idle_flap`   | 2–3 | Optional. Subtle 1-pixel "breathing" loop at ~100 ms/frame (engine pulse, antenna twitch). |
| `flap_up`     | 1   | Optional. Cockpit pitched UP a degree, fin slightly raised. Played during a tap when the rig is climbing. |
| `flap_down`   | 1   | Optional. Cockpit pitched DOWN a degree. Played when the rig is falling between taps. |
| `damaged`     | 1   | Replaces `idle` during STATE_OVER. Front-right third of the hull destroyed (see SMASHED below). |
| `victory`     | 1+  | Optional. Celebratory pose at the truck-stop dock after delivery — headlights flashing, antenna extended, etc. |

Everything else — engine flame, antenna sway, shield/ghost/magnet
halos, force-field, stun crackle, sparks, exhaust, cargo chain,
score floaters — is drawn in code on top of your sprite, so you
don't need to redraw the rig for any of those.

## Optional slices

| Slice name | Position (px) | What it's for |
|---|---|---|
| `center`         | (29, 26) | Pivot point for rotation/scaling |
| `attach_chain`   | ( 2, 30) | Where the cargo bond chain anchors |
| `attach_driver`  | (32, 16) | Where the cockpit driver sits (future characters) |

No slices = we hardcode the positions in code. Slices let us tweak
the anchors without touching the source.

## What to draw

- Hull — the teal body
- Cockpit dome + glass + driver
- Front grille + 3 headlights
- Single wing fin on the back-left
- Engine pod silhouette (the gray cylinder slung below)
- Chain anchor port (the small bead at the back-left of the body)
- Antenna BASE — a static vertical line up from the body. The tip
  animates in code, so don't sway it.

## What NOT to draw

All handled in code on top of your sprite:

- Engine flame (blue jet out the back)
- Engine swirl particles (white-cyan motes near the nozzle)
- Antenna tip sway
- Exhaust trail / smoke
- Sparks on collision
- Shield bubble (cyan ring)
- Ghost aura (mint halo)
- Magnet ring (pink orbital)
- Force-field bubble (amber halo)
- Stun crackle (cyan lightning) when stung
- Cargo bond / chain to the cargo crate
- Score floaters, damage flashes

## SMASHED (damaged) variant

Same canvas size (58 × 52). The right third of the rig is destroyed:

- Front grille gone entirely (cols ~48–56 empty)
- Right end of the body chewed up with a jagged broken outline
- Charred dark interior visible (`#1a0a06` / `#0a0408`)
- 3 headlights are dark sockets, no light
- Cockpit glass cracked (`#0a0a14`)
- Hot embers in the breakage — static ember pixels in the warm
  palette. We add the flicker animation on top.
- Exposed wire spark (cyan pixel) somewhere in the wreckage
- Scorch streaks on the surviving body

See `reference_smashed.png` for the current take. Deviate if you
want — brief is "front 30% is wrecked".

## Palette

Stay inside `art/palette/dlx-master-palette.gpl`. The relevant
sections for this sprite are HULL, COCKPIT, ENGINE POD, ACCENTS,
and DAMAGE / EMBERS for the smashed variant.

## Export

```bash
aseprite -b roadkill.aseprite \
  --sheet roadkill.png \
  --data  roadkill.json \
  --sheet-pack --format json-array
```

Or just `File → Save As → roadkill.png` (transparent, 1× scale) for
a single frame.

Commit the `.aseprite` source + the exported `.png` (+ `.json` if
multi-frame). DM them over if you don't have GitHub access yet — we'll
commit on your behalf.
