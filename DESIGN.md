# DESIGN.md — DLX HAULER

Visual system. All values OKLCH where possible (with hex fallbacks). Tinted neutrals only — never `#000` or `#fff`.

## Color

### Strategy: COMMITTED

DLX orange-red carries 30–50% of the home-page surface. This is the brand's identity color — diluting it produces generic AI palettes. The wasteland dark is the backdrop the orange burns through.

### Roles

| Role | Token | OKLCH | Hex | Use |
|---|---|---|---|---|
| Brand primary | `--dlx-orange` | `oklch(0.66 0.20 38)` | `#f06030` | DLX badge, CTA, accents |
| Brand deep | `--dlx-red` | `oklch(0.45 0.19 30)` | `#c52a18` | CTA shadow, secondary accents |
| Brand bright | `--dlx-amber` | `oklch(0.85 0.16 86)` | `#ffd060` | Stars, highlights, gold trim |
| Brand glow | `--dlx-flame` | `oklch(0.78 0.20 60)` | `#ffb030` | Hazard chevrons, warnings |
| Wasteland deep | `--bg-deep` | `oklch(0.13 0.02 320)` | `#120a18` | Page background |
| Wasteland mid | `--bg-mid` | `oklch(0.20 0.04 310)` | `#1d1330` | Card surfaces |
| Wasteland tint | `--bg-rim` | `oklch(0.27 0.05 305)` | `#2a1a30` | Borders, dividers |
| Ink | `--ink-1` | `oklch(0.94 0.03 70)` | `#f4e8d8` | Primary text on dark |
| Ink dim | `--ink-2` | `oklch(0.72 0.05 80)` | `#c0a890` | Secondary text |
| Ink ghost | `--ink-3` | `oklch(0.55 0.05 320)` | `#806a90` | Tertiary text, captions |
| Hazard yellow | `--hazard` | `oklch(0.85 0.18 95)` | `#ffe030` | Warning stripes |

Sister-app palette (FREIGHT, future apps): same neutrals, different brand-primary swap. HAULER = orange. FREIGHT = navy `#6abfdc` + gold `#ffd060`.

### Bans

- No `#000` and `#fff`. Tint every neutral toward purple/orange (chroma 0.02–0.05).
- No gradient text (`background-clip: text`). Solid colors only.
- No glassmorphism unless physically motivated.

## Typography

| Role | Family | Weight | Size | Letter-spacing |
|---|---|---|---|---|
| Title (poster) | Impact, 'Arial Black' | 900 | 26–38px | 2–3px |
| Display number | 'Space Mono', monospace | 700 | 18–48px | tabular |
| Headline label | 'Helvetica Neue' | 800 | 9–12px | 2.5–4px |
| Body / blurb | 'Helvetica Neue' | 500 | 11–13px | 0.5px |
| Diegetic label | 'Space Mono' / Impact | 700 | 9–11px | 2px |

**Hierarchy through scale + weight contrast (≥1.25 ratio).** Big poster headers next to tiny diegetic labels. Avoid mid-tier. Body line length cap: 65ch.

## Layout

- **Vary spacing.** No uniform 12px-everywhere rhythm. Hero card breathes; manifest data is tight.
- **No nested cards.** Hero is a card. Things inside it are not also cards.
- **Cards are not the only affordance.** Use background tints, leading numbers, underlines, full borders — not side stripes.
- **Diegetic chrome.** Construction-tape stripes (alternating orange/black) at card tops. Hazard chevrons. Segmented displays for numbers.

## Motion

- **Easing:** `cubic-bezier(0.16, 1, 0.3, 1)` (ease-out-expo) or `cubic-bezier(0.22, 1, 0.36, 1)` (ease-out-quint). Never bounce, never elastic.
- **Don't animate layout properties.** Transform + opacity only.
- **Idle hero motion is purposeful.** Construction-tape doesn't pulse decoratively — it scrolls slowly like a real conveyor. Numbers roll on first-load only.
- **Diegetic motion.** Lights flicker like busted neon. Signal bars climb when "tuning in." LEDs blink at 1.4s heartbeat.

## Components

### DLX badge
Orange-red gradient, 2.5px dark border, gold `DLX` text in Impact, 3px letterspacing. Hex code inset: 9px. Never recolor — sister apps swap secondary lockup, not the badge.

### Construction-tape stripe
4px tall, `repeating-linear-gradient(90deg, #ffb030 0 12px, #1a0a06 12px 18px)`. Brand chrome on hero card tops. Slow scroll on idle (24s loop) — not pulse.

### CTA button (PUNCH IT)
Orange-red gradient, 2px dark inset, 4px deep "depressed" shadow underneath, gold text in Impact. Pressed-down state on tap (translateY 4px, shadow shrinks to 0). Idle: subtle 2.4s ignition glow pulse.

### Stat readout
Space Mono 18–24px, tabular numbers. Optional digital-display segmented frame. Never just "big number / small label" SaaS-template.

### Star pip
3 stars rendered as a route progress bar (rounded rect with star-pin checkpoints), not 3 separate icons. Empty checkpoints are dim outlines, earned ones are gold + glow.
