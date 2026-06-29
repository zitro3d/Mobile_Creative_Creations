# Dumplord X-Press — DLX Hauler (Daily Drop) · Handoff

> Read this first. It's the single source of truth for working on the
> **Dumplord X-Press** game. Start a new chat by pasting the "Starter
> prompt" at the bottom.

## What it is
A mobile, one-button **flappy-style cargo-run game**. You fly the DLX rig
left-to-right across a long pixel-art wasteland, dodge obstacles, protect
your tethered cargo crate, and dock at the GOOD BUDDY TRUCK STOP for a
payout. Worn-terminal "dispatch console" UI. Vanilla canvas2D, no
framework, **everything in one file**.

- **Live:** https://zitro3d.github.io/Mobile_Creative_Creations/dumplord-daily.html?level=sunsetWastesPixel
- **Repo:** https://github.com/zitro3d/Mobile_Creative_Creations
- **Game file:** `dumplord-daily.html` (~42k lines — the whole game: HTML + CSS + one big `<script>`)
- **Service worker:** `sw.js` (network-first for HTML, cache-first for assets)
- **Current build:** `DLX_BUILD = 'DXP-DAILY-v71'` · `CACHE = 'dlx-hauler-v535'`
- **Feature branch:** `claude/flappy-bird-game-3rmbH` (GitHub Pages deploys from `main`)
- Only one level ships today: **`sunsetWastesPixel`** (the `?level=` param).

## Deploy workflow (do this on every shipped change)
1. Bump BOTH version markers together (installed PWAs only update when these move):
   - `DLX_BUILD = 'DXP-DAILY-vNN'` near the top of `dumplord-daily.html`
   - `CACHE = 'dlx-hauler-vNNN'` in `sw.js`
2. Commit to the feature branch, then merge to `main` and push (Pages serves `main`):
   ```
   git add -A && git commit -m "..."
   git push -u origin claude/flappy-bird-game-3rmbH
   git checkout main && git merge claude/flappy-bird-game-3rmbH --no-edit
   git push origin main && git checkout claude/flappy-bird-game-3rmbH
   ```

## How to test (headless, no device)
The repo uses self-hosted fonts + a `fetch()` for the rig sprite, so test
over HTTP, not `file://`:
```
python3 -m http.server 8731          # from repo root
# then drive a headless Chromium (playwright-core, chromium at
# /opt/pw-browsers/chromium-1194/chrome-linux/chrome) against
# http://localhost:8731/dumplord-daily.html?level=sunsetWastesPixel
```
Parse-check the inline JS before every deploy:
```
node -e "s=require('fs').readFileSync('dumplord-daily.html','utf8');i=s.indexOf('<script>');j=s.lastIndexOf('</script>');new Function(s.slice(i+8,j));console.log('JS OK')"
```
Caveat: drones/late hazards/high speed need ~30s+ of real play to appear —
headless can verify boot + HUD + menus, not deep gameplay tuning.

## Architecture (find things by FUNCTION NAME — line numbers drift)
- **`loop(t)`** — fixed-timestep accumulator (sim tuned to 60fps; runs the
  right number of `update()` steps for real elapsed time so it isn't
  slow-mo on slow phones / 2x on 120Hz). Then `render()`.
- **`update()`** — master sim step. The daily branch (`if (isDaily)`) holds
  the obstacle/hazard spawners + cargo logic (~lines 8600–11200).
- **`render()`** — master draw. Daily draw calls + HUD near the end.
- **`collide()`** — master collision → returns true on a lethal hit
  (shield absorbs, else death). Daily section covers terrain, air
  obstacles, thieves, lava balls, **drones / bandits / ground-rival cab**
  (enemy vehicle bodies), gated by force-field / tunnel-zone / ghost.
- **`currentPipeSpeed()`** — world scroll speed. Daily = distance-based.
- **`DELIVERY_LEVELS`** — per-level config (`sunsetWastesPixel`, etc.):
  palettes, horizon style, `obstacleSet` flags, dock label.
- **HUD draw fns:** `drawScore` (SCORE panel, safe-area aware via
  `safeTopUnits()`), `drawCargoMeter`, `drawComboHud`, `drawSpeedFx`.
- **Intensity layer:** `updateDailyIntensity` + `checkNearMiss` (near-miss
  bonus, speed streaks, cargo payout meter, steal consequence).
- **End of run:** `triggerDeliverySuccess` → `showVictory`; share card =
  `buildDailyShareText`.
- **Banners:** `setLevelBanner` / `setShortBanner` / `drawLevelBanner` —
  currently SUPPRESSED during active play (player preference); they expire
  silently and results show on the end screens.

## Key tunables + current values
| Thing | Where | Value |
|---|---|---|
| Level length (docking) | `dailyScrollX >= 16800` | truck stop worldX **17000**, no-spawn after **16400**, approach gate **16200** |
| Speed ramp (daily) | `currentPipeSpeed` daily branch | distance-based: `2.1 → 3.5` over `dailyScrollX/14000`, ×1.5 with `blitz` mod |
| Stages | `DAILY_STAGES` (distance thresholds) | `0 / 4400 / 8800 / 13200`; advance by `dailyScrollX` |
| Air-obstacle spacing | `baseGap` by stage in the air-obstacle spawner | `435 / 325 / 270 / 216` (+ up to 200 jitter) |
| Tentacle cap (sunset) | `tentCap` | 6 (organic levels = 8) |
| Cargo payout | `updateDailyIntensity` | ~+1 / 30 frames (~2/sec), cap 99; banked on delivery; **stolen = wipe + −5 + red vignette + sound** |
| Near-miss bonus | `checkNearMiss` | gap clearance `< 13px` → `+5`, cyan floater |
| Cargo re-grab radius | cargo re-magnetize | **48px** centre-to-centre |
| Run timer / cargo meter start | `flap()` launch branch | begins on the **first tap** (not while parked) |

## Recent feature log (v48 → v71, newest last)
- Self-hosted fonts (Press Start 2P + VT323); PWA installable.
- Terminal-style result screens (Game Over / Pause / Victory), Confirm
  Purchase modal, Score HUD; tabbed Garage (RIGS/UPGRADES/SKINS/TRAILS/HAZARDS).
- Fixed-timestep loop (fixes slow-mo). Share card rebrand → straight-line
  divider + 📦 icon. Victory copy/colors honest (cargo lost vs intact),
  confetti = 2 logo colors, only on a clean win.
- Enemy vehicles lethal on impact; bigger cargo re-grab.
- Intensity layer: near-miss "CLOSE CALL", speed streaks (air-only),
  cargo payout meter + steal consequence.
- Top HUD redesign: labelled SCORE panel, safe-area aware (no longer hides
  behind the battery), combo readout = stamped "COMBO x2+".
- Longer level + distance-based speed/stage stretch; banners off during play.

## Open threads / things to playtest
- Full-length feel: can't verify the back half headlessly — confirm hazard
  density holds late-game.
- Speed ceiling (~3.5) and level length (~17000) — tune to taste.
- Token chip ("+N") could use a label; near-miss window (13px) tunable.
- Next planned level after the foundation: **THE LEVIATHAN** (organic interior).

## Local / offline build
A self-contained copy can be produced by inlining the rig sprite JSON into
the HTML and disabling the service worker, then zipping `dumplord-daily.html`
+ `fonts/` + the used `assets/` + `audio/` + `art/vehicles/hero/lomax/throttle.json`.
(Ask and I'll regenerate the zip.)

---
### Starter prompt for the new chat
> We're working on **Dumplord X-Press / DLX Hauler**, the single-file
> canvas2D game in `dumplord-daily.html` (current build DXP-DAILY-v71).
> Read `DUMPLORD-XPRESS.md` first for architecture, tunables, and the
> deploy workflow. Live at the GitHub Pages `dumplord-daily.html?level=sunsetWastesPixel`.
> Today I want to work on: <your goal>.
