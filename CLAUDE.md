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

## Wondrous Grid (commercial product)
- Single-file editor: `wondrous-grid.html` (~9000+ lines)
- Owned by **Everything Wondrous Inc.** (Delaware-form corporation; company name registered as a trademark; product name "Wondrous Grid" trademark filing in progress)
- Production domain: **wondrousgrid.com** (registered at GoDaddy, transferring to Cloudflare Registrar after 60-day ICANN lock)
- Role-based email forwarders (to be set up via Cloudflare Email Routing): `legal@`, `privacy@`, `support@`, `contact@wondrousgrid.com`
- Legal docs at repo root: `LICENSE` (proprietary), `TERMS.md`, `PRIVACY.md`
- In-app About / legal modal links to `./TERMS.md`, `./PRIVACY.md`, `./LICENSE` (relative paths — must ship alongside the HTML) plus `https://wondrousgrid.com`
- **Hosting plan in motion:** moving from this public repo onto a dedicated **private GitHub repo** deployed via **Cloudflare Pages** at `wondrousgrid.com`. Once that migration completes, `wondrous-grid.html` and its legal docs leave this repo. The DLX game stays here on GitHub Pages.
- Until migration completes, edits still land in this repo on the `claude/flappy-bird-game-3rmbH` branch and follow the same merge-to-main flow above.

## Delivery levels (Ship 1+ foundation)
- `DELIVERY_LEVELS` config defined alongside the daily-mode globals; `currentDeliveryLevel` drives the per-level renderers (sky, ground band, labels). Each new level = new entry in this object.
- Foundation refactor in progress: future ships extract horizon palette, terrain palette, ambient field, terrain profile, obstacle weights into the same config.
- First new level after foundation: THE LEVIATHAN (organic interior of a colossal creature).
