# DLX Garbage Hauler — Art Pipeline

This folder is the single source of truth for every sprite in the game.
The artist works in [Aseprite](https://www.aseprite.org/) on the `.aseprite`
files; the exported `.png` (and optional `.json`) files are what the game
actually loads at runtime.

## Folder structure

```
art/
  README.md                  ← this file
  palette/                   ← shared color palette (every sprite stays inside this)
    dlx-master-palette.gpl       Aseprite-importable palette
    dlx-master-palette.txt       human-readable hex listing
  vehicles/                  ← player rigs + enemy vehicles
    hero/
      roadkill/                  current player rig
        roadkill.aseprite          working file (artist owns)
        roadkill.png               exported game sprite (auto-loaded)
        roadkill.json              metadata (frames, tags, slices)
        reference.png              ← snapshot from current in-game code
        reference_smashed.png      ← snapshot of the damage variant
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

Empty category folders are created on-demand as we add sprites — don't
worry if a folder doesn't exist yet.

## How to add a new sprite

1. **Find the right folder** (or create one matching the structure above).
2. **Open the `reference.png`** — that's the current in-game version of
   the sprite. Use it as your starting point or as visual ground truth.
3. **Create or open `<sprite>.aseprite`** alongside `reference.png` in
   the same folder.
4. **Load the shared palette**: in Aseprite, `Palette → Presets → Load…`
   → pick `art/palette/dlx-master-palette.gpl`.
5. **Edit at 1× native scale** — Aseprite has its own zoom (`Ctrl+=` /
   `Ctrl+-`), so don't pre-scale the canvas. Use `View → Pixel Grid` to
   see the per-pixel boundaries when zoomed in.
6. **Tag animation frames** if you have any — for example `idle` (loop)
   and `damaged` (one-shot). Tag name = state name the game uses.
7. **Mark anchor points with slices** named `center` (where the sprite
   pivots in-game) and `attach_*` (where things connect, e.g. the chain).
8. **Export**:
   - Single frame, no animation: `File → Save As → <sprite>.png`
     (transparent background, 1× scale).
   - Multi-frame or tagged: `File → Export Sprite Sheet`
     - Output File: `<sprite>.png`
     - Data File: `<sprite>.json` (check "JSON Data")
     - Sheet Type: `Packed`
     - Layout: Include all tags
9. **Commit** the `.aseprite` source + the exported `.png` (+ `.json` if
   present) together — both go in the same folder.

## Sprite conventions

- **Canvas size**: see the per-sprite README. Each sprite has a fixed
  in-game size; stick to those exact pixel dimensions.
- **Background**: fully transparent (alpha = 0), no checker, no grid
  baked in.
- **Scale**: 1× native (don't render the artwork at 2× or 4×; Aseprite's
  zoom handles viewing).
- **Palette**: stay inside `palette/dlx-master-palette.gpl`. If you need
  a new shade, run it past the team first so we keep the palette tight.
- **What NOT to draw**: many effects are procedural in code — engine
  flames, exhaust, antenna sway, sparks, shield/ghost/magnet halos,
  cargo bonds, explosion bursts, etc. The per-sprite README lists what's
  on you vs. what's already handled.

## Delivery workflow

**For the first couple of sprites** (right now): text/DM the
`.aseprite` + `.png` files to the team. We'll commit them. You'll see
your art in the live game within minutes (hard-refresh to bypass cache).

**Going forward** (once the workflow is proven): set up
[GitHub Desktop](https://desktop.github.com/), get added as a
collaborator on the repo, then commit + push directly. About 20 minutes
of one-time setup; after that you're autonomous.

## Regenerating the reference PNGs

If the in-game code changes and a `reference.png` no longer matches the
live art, run:

```bash
node bin/render-references.mjs
```

This re-reads the current sprite-draw functions from
`dlx-garbage-hauler-pixel.html` and re-renders every `reference.png` and
`reference_smashed.png` to disk. Commit the updated files.

## Questions

Ping the team channel. We iterate fast — early small drops are way
better than one big polish pass at the end.
