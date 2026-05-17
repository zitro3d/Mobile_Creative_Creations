# Vehicles

All player rigs (`hero/`) and enemy vehicles (`enemy/`) live in this
folder. Each vehicle gets its own subfolder with the standard layout:

```
<vehicle_name>/
  <vehicle_name>.aseprite       working file (artist owns)
  <vehicle_name>.png            exported game sprite
  <vehicle_name>.json           metadata (optional, multi-frame only)
  reference.png                 snapshot from current code
  reference_<variant>.png       additional variants (damaged, etc.)
  README.md                     sprite-specific anchor + state notes
```

## Vehicle conventions

- **Pixel grid**: every vehicle is drawn at 1× game-pixel resolution.
  Aseprite zoom is for viewing only — don't scale the canvas itself.
- **Anchor point**: by default, the vehicle pivots around the center
  of its hull. Override with an Aseprite slice named `center` if your
  visual center differs.
- **Direction**: vehicles face RIGHT (positive X). The game flips them
  in code if needed for opposite-direction motion.
- **State tags** (Aseprite tags inside the .aseprite file):
  - `idle` (required, can be 1 frame) — default flight pose
  - `damaged` (optional, 1 frame) — hit-state variant
  - `boost` (optional, 1-3 frame loop) — accelerating pose
  - Custom tags are fine; the game can read any tag name.

## What's procedural (don't draw)

Every vehicle in the game has these effects layered ON TOP at runtime;
leave the canvas transparent where they should appear:

- **Engine flame** — blue chevron jet out the back
- **Engine swirl particles** — white-cyan motes near the nozzle
- **Exhaust trail** — gray smoke puffs
- **Antenna sway** — the antenna BASE can be drawn, but the tip
  animates procedurally; keep the antenna as a static vertical line
- **Sparks** on collision
- **Shield bubble**, **ghost aura**, **magnet ring** — overlay sprites
- **Cargo bond / chain** — connects to the rig procedurally
- **Explosion / impact** — fully procedural
- **Stun crackle arcs** — when stung by a jellyfish

For enemy vehicles specifically:
- **Cable + claw** on the aerial thief — only draw the gunship BODY,
  not the dangling cable or magnetic claw at the tip
- **Bandit truck hook** — same idea, body only
- **Drone beam** — the drone's body, no zap beam

## Future hero rigs

The game already has stat profiles for 5 player rigs: `roadkill`
(default), `spark`, `anvil`, `ghost`, `volt`. Only `roadkill` is
visually built today. The others will eventually need sprites in
their own subfolders.

Suggested visual personalities (rough — riff freely):

- **spark**:  small, yellow, agile — like a hopped-up scooter
- **anvil**:  big, dark gray, heavy — slow but tanky
- **ghost**:  pale, translucent-looking, slim — ethereal vibe
- **volt**:   yellow + black, longer body — endurance rig

When the time comes, ping the team and we'll spec the dimensions.
</parameter>
