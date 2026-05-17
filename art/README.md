# DLX Garbage Hauler — Art Pipeline

Every sprite in the game lives in this folder. You work in
[Aseprite](https://www.aseprite.org/) on the `.aseprite` files; the
exported `.png` (and the `.json` if it's multi-frame) is what the game
actually loads at runtime.

## Folder structure

```
art/
  README.md                  ← this file
  palette/                   ← shared color palette — every sprite stays inside this
    dlx-master-palette.gpl       Aseprite-importable palette
    dlx-master-palette.txt       human-readable hex listing
  vehicles/                  ← player rigs + enemy vehicles
    hero/
      roadkill/                  current player rig
        roadkill.aseprite          working file (you own this)
        roadkill.png               exported game sprite
        roadkill.json              metadata (frames, tags, slices)
        reference.png              snapshot from current in-game code
        reference_smashed.png      snapshot of the damage variant
        README.md                  anchor + state notes
      spark/                     future YELLOW nimble rig
      anvil/                     future HEAVY rig
      ghost/                     future STEALTH rig
      volt/                      future ENDURANCE rig
    enemy/
      gunship/                   aerial thief variant 1
      harpooner/                 aerial thief variant 2
      drone/                     anti-magnet drone
      bandit_truck/              bandit pickup with hook
      scrap_magnet/              scrapyard crane
  creatures/                 ← organic enemies + bosses
  pickups/                   ← cogs, fuel, magnet box, power-ups
  cargo/                     ← cargo crate variants
  obstacles/                 ← projectiles, hazards
  environments/              ← landmarks, scenery, biome reference sheets
  hud/                       ← future HUD upgrades
```

Empty categories get created when we add sprites. Don't worry if a
folder isn't there yet.

## Adding a new sprite

1. Find the right folder (or make one matching the structure above).
2. Open the `reference.png` — that's the current in-game version.
   Starting point + ground truth.
3. Open or create `<sprite>.aseprite` next to it.
4. Load the shared palette: `Palette → Presets → Load…` → pick
   `art/palette/dlx-master-palette.gpl`.
5. Work at 1× native scale. Aseprite has its own zoom (`Ctrl+=` /
   `Ctrl+-`), so don't pre-scale the canvas — use `View → Pixel Grid`
   when you're zoomed in.
6. Tag animation frames if you have any: `idle` (loop), `damaged`
   (one-shot), etc. The tag name = the state the game looks up.
7. Mark anchor points with slices: `center` (the pivot point) and
   `attach_*` (where things connect, like the cargo chain).
8. Export:
   - Single frame: `File → Save As → <sprite>.png`, transparent BG,
     1× scale.
   - Multi-frame or tagged: `File → Export Sprite Sheet`
     - Output File: `<sprite>.png`
     - Data File: `<sprite>.json` (check "JSON Data")
     - Sheet Type: `Packed`
     - Layout: Include all tags
9. Commit the `.aseprite` source + the exported `.png` (+ `.json` if
   multi-frame) together. Both files in the same folder.

## Conventions

- **Canvas size**: see the per-sprite README. Each sprite has a fixed
  in-game size — stick to those exact dimensions.
- **Background**: transparent (alpha = 0). No checker, no grid baked in.
- **Scale**: 1× native. Don't render at 2× or 4×; that's a viewing zoom.
- **Palette**: stay inside `palette/dlx-master-palette.gpl`. Want a
  new shade? Send it over with what it's for — we'll wire it in.
- **What NOT to draw**: a lot of effects are done in code (engine
  flames, exhaust, antenna sway, sparks, shield/ghost/magnet halos,
  cargo bonds, explosions, etc.). Each sprite's README lists what's
  on you vs. what we handle.

## Delivery

**For the first couple of sprites**, just text or DM the `.aseprite`
+ `.png` to the team. We commit them and your art shows up in the
live game within minutes. Hard-refresh to bypass cache.

**Once we've shipped a few**, set up
[GitHub Desktop](https://desktop.github.com/) and we'll add you as a
collaborator on the repo. ~20 minutes of one-time setup; after that
you push directly.

## Regenerating reference PNGs

If the in-game code drifts from what's in `reference.png`, run:

```bash
node bin/render-references.mjs
```

That re-reads the current sprite-draw functions from the game source
and re-renders every `reference.png` and `reference_smashed.png`.
Commit the updated files.
