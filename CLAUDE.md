# Mobile Creative Creations — Claude Instructions

## Deploy workflow
After every commit to the feature branch, always merge to `main` and push so changes go live on GitHub Pages immediately:

```
git push -u origin claude/flappy-bird-game-3rmbH
git checkout main
git merge claude/flappy-bird-game-3rmbH --no-edit
git push origin main
git checkout claude/flappy-bird-game-3rmbH
```

If merge conflicts occur on `main`, take the feature branch version (`git checkout --theirs`).

Bump the version on every shipped change: `DLX_BUILD = 'vNNN'` near the top of the HTML and `CACHE = 'dlx-hauler-vNNN'` in `sw.js` must move together so installed PWAs pick up the new build.

## Project
- Single-file game: `dlx-garbage-hauler-v2.html` (DLX Garbage Hauler — daily-delivery cargo run)
- Vanilla canvas2D, no framework
- Feature branch: `claude/flappy-bird-game-3rmbH`
- GitHub Pages deploys from `main` only
- Service worker: `sw.js` (network-first for HTML, cache-first for assets)

## Wondrous Grid (moved out — separate repo)
- Wondrous Grid (the commercial pixel-art studio) has moved to its own **private** repo: `zitro3d/wondrous-grid`, deployed via **Cloudflare Pages** at `wondrousgrid.com`.
- Its files (`wondrous-grid.html`, `LICENSE`, `TERMS.md`, `PRIVACY.md`, brand icons) were removed from this public repo on the cleanup pass — do NOT re-add them here.
- DLX vehicle reference art under `art/vehicles/` + `art/palette/` stays here as game design reference; copies also live in the WG repo at `projects/dlx/`.
- For Wondrous Grid work, use a session connected to `zitro3d/wondrous-grid` (and optionally this repo too, for asset hand-offs into the game).

## Delivery levels (Ship 1+ foundation)
- `DELIVERY_LEVELS` config defined alongside the daily-mode globals; `currentDeliveryLevel` drives the per-level renderers (sky, ground band, labels). Each new level = new entry in this object.
- Foundation refactor in progress: future ships extract horizon palette, terrain palette, ambient field, terrain profile, obstacle weights into the same config.
- First new level after foundation: THE LEVIATHAN (organic interior of a colossal creature).
