# Vehicles

Player rigs (`hero/`) and enemy vehicles (`enemy/`) live here. Each
vehicle is its own subfolder:

```
<vehicle_name>/
  <vehicle_name>.aseprite       working file (you own this)
  <vehicle_name>.png            exported game sprite
  <vehicle_name>.json           metadata (multi-frame only)
  reference.png                 snapshot from current code
  reference_<variant>.png       additional variants (damaged, etc.)
  README.md                     anchor + state notes for that sprite
```

## Conventions

- **Pixel grid**: 1× game-pixel resolution. Aseprite zoom is for
  viewing — don't scale the canvas itself.
- **Anchor point**: vehicles pivot around the hull center by default.
  Add an Aseprite slice named `center` if your visual center differs.
- **Direction**: vehicles face RIGHT (positive X). The game flips them
  in code if a sprite needs to face the other way.
- **State tags**: each vehicle's README lists the full state machine
  the game drives it through, so you can see every beat in the
  animation even if you only ship one frame. Common shared tags:
  - `idle` (required, 1 frame is fine) — default flight pose
  - `damaged` (optional) — hit-state variant or destroyed
  - `lock_on` / `charging` (optional) — pre-attack hover or windup
  - `dropping` / `firing` (optional) — attack pose
  - `retract` / `retreat` (optional) — post-attack reel-back or flee
  - Custom tag names are fine — the game reads them by name.

## What's procedural (don't draw)

These effects get layered on top of your sprite at runtime — leave
the canvas transparent where they should appear:

- **Engine flame** — blue chevron jet out the back
- **Engine swirl particles** — white-cyan motes near the nozzle
- **Exhaust trail** — gray smoke puffs
- **Antenna sway** — you can draw the antenna BASE; the tip animates
  in code, so just leave a static vertical line
- **Sparks** on collision
- **Shield bubble**, **ghost aura**, **magnet ring** — overlay sprites
- **Cargo bond / chain** — connects to the rig in code
- **Explosion / impact** — fully procedural
- **Stun crackle arcs** — when stung by a jellyfish

For enemies specifically:
- **Cable + claw** on the aerial thief — body only
- **Bandit truck hook** — body only
- **Drone beam** — body only

## Future hero rigs

The game has stat profiles for 5 player rigs: `roadkill` (the one
that's built), `spark`, `anvil`, `ghost`, `volt`. The other four
will need sprites eventually, in their own subfolders.

Rough visual personalities — riff freely:

- **spark**: small, yellow, agile — hopped-up scooter
- **anvil**: big, dark gray, heavy — slow but tanky
- **ghost**: pale, translucent, slim — ethereal vibe
- **volt**: yellow + black, longer body — endurance rig
