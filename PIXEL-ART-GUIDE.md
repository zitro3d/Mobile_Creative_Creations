# Neo-16-Bit Pixel Art — Personal Learning Guide

A self-paced roadmap for learning HTML5 canvas pixel art, kept separate from the DLX Garbage Hauler game work so the two don't interfere.

---

## The mental model

Every pixel art sprite is just one operation repeated thousands of times:

1. Pick a color
2. Pick a coordinate (x, y)
3. Paint a 1×1 rectangle
4. Repeat

That's it. The complexity is in **where** you put the rectangles and **how** you use math to animate them.

---

## Setup — pick one

### Easiest: CodePen (free, web-based)
- Go to **codepen.io** → New Pen
- Three panels: **HTML**, **CSS**, **JS**
- **IMPORTANT**: Click the ⚙️ gear next to "JS" and set **Preprocessor → None**. Otherwise CodePen tries to parse your code as CoffeeScript and you'll get a `Parse error on line 1: Unexpected 'DEDENT'`.

### Better long-term: VS Code (free desktop editor)
- Download from **code.visualstudio.com**
- Install the **Live Server** extension
- Save your file as `whatever.html`, right-click → **Open with Live Server**
- Edit and save — the browser auto-reloads

### Zero install: Browser DevTools
- Open any HTML file in your browser
- Press **F12** → **Sources** tab → edit JS live → **Ctrl/Cmd+S** to apply
- Great for quick experiments; changes are lost on refresh

---

## The minimal canvas setup

```html
<canvas id="cv" width="128" height="128"
        style="width: 512px; height: 512px;
               image-rendering: pixelated;"></canvas>
```

Two sizes are at play:
- `width="128" height="128"` — the **native** canvas resolution (128 actual pixels)
- `width: 512px` (CSS) — the **display** size (4× scaled up)
- `image-rendering: pixelated` — keeps the pixels sharp during the upscale (without this you get blurry pixel art)

In JavaScript:

```js
const cv = document.getElementById('cv');
const ctx = cv.getContext('2d');
ctx.imageSmoothingEnabled = false; // CRITICAL — disables AA
```

---

## The one helper you need

```js
function px(color, x, y, w, h) {
  ctx.fillStyle = color;
  ctx.fillRect(x | 0, y | 0, (w || 1) | 0, (h || 1) | 0);
}
```

Every pixel sprite in this entire codebase is built from `px(...)` calls. The `| 0` is a fast way to floor-to-integer so you never paint at sub-pixel coordinates (which would soften the edge).

---

## Layering — how every sprite gets depth

A **3-step shading** recipe per material:

1. **Outline** (darkest color, 1 pixel wider than the shape)
2. **Body fill** (mid color)
3. **Highlight** (lightest, top edge or sun-catch side only)

For more depth, add:

4. **Shadow** (between outline and body, on the opposite side from the highlight)
5. **Specular pip** (a single bright pixel — the "shiny spot")

Bottom layers paint first; brighter accents go on top.

---

## The animation loop

```js
let frame = 0;
function loop() {
  ctx.clearRect(0, 0, 128, 128);   // wipe last frame
  drawWhatever(frame);              // paint new frame
  frame++;
  requestAnimationFrame(loop);      // browser calls this ~60 times per sec
}
loop();
```

That's the entire animation engine.

---

## The five animation tricks

Once you have the loop, every motion is one of these patterns:

### 1. Smooth bob with sin

```js
const yOffset = Math.round(Math.sin(t * 0.05) * 2);
ctx.translate(0, yOffset);
```

- `* 0.05` controls speed (smaller = slower)
- `* 2` controls amplitude (in pixels)

### 2. Discrete phase cycle (for flicker / flap)

```js
const phase = ((t / 2) | 0) & 3;  // 0,0,1,1,2,2,3,3,0,0,1,1...
```

Use `phase` (0-3) to pick between pre-baked poses.

### 3. Conditional events (blink, mouth-open)

```js
if ((t % 180) >= 176) {
  // fire the rare event for 4 frames every 180 frames
}
```

### 4. Particle systems (sparks, dust)

```js
for (let i = 0; i < 10; i++) {
  const particleT = (t + i * 7) % 30;
  const x = baseX + Math.sin(t * 0.2 + i) * 2;
  const y = baseY - particleT * 1.5;
  px(color, x, y);
}
```

Each particle gets its own phase via `i * 7`, so they don't move in lockstep.

### 5. Chain / tail wobble

```js
const wob = (i) => Math.sin(t * 0.04 + i * 0.7) * 3;
// then offset each tail segment by wob(segmentIndex)
```

The `i * 0.7` makes the wave **travel** along the tail length.

---

## Making it loop seamlessly (for GIFs)

For a clean GIF, every animation's period must divide the GIF's frame count evenly.

If your GIF is **80 frames**:
- A sin cycle of period 80 → 1 cycle per loop ✓
- A flicker of period 8 → 10 cycles per loop ✓
- A particle of period 20 → 4 cycles per loop ✓
- A blink at frame 60 → fires once per loop ✓

So when you pick speeds, work backward from your loop length. Use divisors.

To get sin to return cleanly to 0 over N frames: `speed = 2 * Math.PI / N`.

---

## The "learn by reverse-engineering" path

This repo's **`angel-devil-pixel-art.html`** is the simplest reference page — open it in a browser, then **View Source** (Ctrl/Cmd+U) and search for these functions:

| Function | What it teaches |
|---|---|
| `drawHoverFlame(t)` | Smallest example. Stacked color rows + flicker phases + rising particles. |
| `drawDevil(t)` | Full character composition — each body part is its own `drawXxx()`. |
| `drawAngel(t)` | Multi-axis animation (body bob + halo undulation + wing flap + blink + fairy dust all in one). |
| `drawAngelReveal(t)` | Multi-phase entrance effect — 5 visual layers overlapping in time. |

Start with `drawHoverFlame` (smallest). Then peek at `drawDevil` to see how a full character is composed.

---

## Exercises to build up

In order of difficulty:

### Beginner
1. **Single static sprite** — Draw a heart, a star, an apple. Just outline + fill.
2. **Add 3-step shading** — outline, mid, highlight on a simple shape.
3. **One-axis bob** — make your sprite float up and down with sin.

### Intermediate
4. **Eye blink** — eyes that close briefly every N frames.
5. **Particle burst** — sparks expanding outward from a center point.
6. **Mouth open/close** — alternate between two mouth shapes on a cycle.
7. **Multi-layer character** — head + body + arms, each its own draw function. Z-order matters.

### Advanced
8. **Walk cycle** — 4-phase leg animation that loops cleanly.
9. **Multi-particle scene** — fairy dust + steam + sparkles all running simultaneously.
10. **Composable scenes** — separate "background", "character", "foreground" draw functions.
11. **GIF export** — record N frames to an animated GIF using **gif.js**.

---

## Reference: useful values

These are the constants worth memorizing:

```
Speed → approximate period (frames)
  0.05  → ~125 frames per cycle  (slow drift / breath)
  0.10  → ~63  frames per cycle  (medium hover)
  0.20  → ~31  frames per cycle  (fast wobble)
  0.40  → ~16  frames per cycle  (rapid flicker)

Common amplitudes
  1 px  — subtle "alive" wobble
  2 px  — gentle hover / breath
  3 px  — pronounced sway
  4-6   — exaggerated motion

Math helpers
  Math.sin(t)     → -1 to +1, smooth wave
  Math.cos(t)     → -1 to +1, 90° offset from sin
  (t / N) | 0     → integer step, changes every N frames
  t % N           → repeating cycle 0..N-1
  i & 1           → boolean "is odd?" (faster than i % 2)
  Math.round(x)   → nearest integer (use this for pixel coords)
```

---

## When you're ready for the next level

After you've reverse-engineered a few sprites and built a few of your own:

- **Tilesets** — building game backgrounds from small repeating tiles
- **Spritesheets** — packing multiple poses into a single image, drawing slices via `drawImage(src, sx, sy, sw, sh, dx, dy, dw, dh)`
- **Color palette discipline** — pick 8-16 colors total, never use any others. Forces visual consistency.
- **Animation easing** — instead of linear sin, use `easeInOutCubic` etc. for snappier motion
- **Procedural sprites** — generating characters from rules (randomized monsters, dungeon tiles)
- **Real-time game loop** — input handling, physics, collision (the DLX game uses this same canvas approach for everything)

---

## External resources

- **lospec.com** — palette library + community tutorials, the pixel art hub. Great for "what colors should I use?"
- **r/PixelArt** subreddit — feedback + daily inspiration
- **Aseprite** — the standard pixel-art drawing tool (paid, ~$20). Best for designing sprites visually before transcribing to code.
- **Piskel** (piskelapp.com) — free web-based pixel editor. Drag, draw, animate frames in the browser.
- **OpenGameArt.org** — public-domain sprite/tile resources to study (and reuse)

---

## Save your experiments

Every experiment you do should become its own CodePen pen. Pin the good ones to your CodePen profile so they're searchable later. You'll build a portfolio without trying.

If you want to graduate from CodePen, the natural progression is:

1. **CodePen pens** → quick experiments, easy to share
2. **A folder of .html files on your computer** → group related work
3. **A GitHub repo** → version-control your progress; push to GitHub Pages to host
4. **Your own static site** → a personal gallery of your pixel art

---

## The artistic eye — design methodology

Technical pixel-pushing is half the job. The other half is the **decisions**: what to draw, what to throw away, what makes a sprite "feel right" instead of just "exist." This section captures the design instincts used throughout the DLX project so you can train the same reflexes.

### 1. Style rules as a creative cage

The DLX game runs on **six Neo-16-bit rules**, treated as non-negotiable:

1. **Orthographic side-view** — flat profiles, no perspective tricks
2. **Strict 3-step shading** — outline + body + highlight, no gradients
3. **Greebling** — every large surface gets small mechanical details (rivets, vents, plates)
4. **Geometric energy effects** — sparks/flames are blocky shapes, never blurred
5. **Hard edges, zero softness** — no anti-aliasing, no feathered glows
6. **High contrast against void** — bold silhouettes that pop against the dark backdrop

**Why the cage?** Constraints prevent decision paralysis. When everything is allowed, every decision is hard. When the rules are fixed, design becomes "fit the idea into the rules" — which is faster and more cohesive.

**The lesson:** Define your style rules before you draw. Write them down. Treat them like physics — break them only if you have a specific reason.

### 2. Mockup-first workflow

Before any new feature ships in-game, it gets a **hero-shot mockup** — a static frame showing the sprite as a poster, isolated, big. Multiple variants side-by-side.

Why mockups beat in-engine iteration:
- **Faster feedback** — you can see 10 ideas in 20 minutes vs. 1 idea in 2 hours
- **No engine friction** — no spawn logic, no collision, no physics to debug
- **Pure design judgment** — does it look right? does it read at a glance?
- **Stakeholder review** — the creative director can react to a poster long before the gameplay catches up

The cycle:
1. Mockup variant A, B, C as separate canvases
2. Director picks one (or asks for D)
3. Mockup gets refined in isolation
4. Only then does the chosen variant get wired into the game

### 3. The iteration loop

Every sprite gets shipped **terrible** the first time. That's the point.

```
v1: Rough block-out — proportions and silhouette only, ugly
v2: Director feedback ("too tall", "more menacing", "needs a hat")
v3: Tighten — shading, color choice, detail pass
v4: Director feedback ("the eyes are too creepy")
v5: Polish — final greebling, specular pips, color tuning
```

Five passes is normal. Ten is fine. The trick is to **ship v1 fast** rather than polish it before showing anyone. You can't iterate on a sprite that doesn't exist yet.

### 4. Reference-driven, not reference-copying

When designing something complex (a vehicle, a creature), the workflow is:

1. **Gather references** — real-world photos, 3D renders, other pixel artists' work
2. **Identify the essence** — what makes the reference *that thing*? The proportions? A signature shape? A color combo?
3. **Translate to pixels** — preserve the essence, but obey the style rules
4. **Throw away realism** — pixel art is not 1:1 reality. It's a **stylized abstraction** of reality

A truck in DLX isn't trying to look like a real truck. It's trying to look like *the idea of a truck* in a Neo-16-bit world. Less detail than reality, but every kept detail is intentional.

### 5. Z-order and composition

A scene is built **back to front**, like a stage:

1. **Sky / void** — the backdrop
2. **Distant background** — horizon, far structures
3. **Mid background** — terrain, dunes
4. **Foreground obstacles** — what the player navigates
5. **Player character** — always on top of obstacles in their layer
6. **HUD / particles / energy** — top of everything

Each layer paints over what's behind it. This means **planning the silhouettes** before the details — the shape against the layer below must read clearly.

A common mistake: making a sprite that looks amazing in isolation but **disappears against its background**. The fix is to test sprites *in their final layer context* before polishing.

### 6. Variant design — siblings vs. cousins vs. strangers

When you need many of a thing (obstacles, NPCs, debris), decide where on the variation spectrum each design sits:

- **Siblings** — same family, small differences (color swap, one detail changed). Use when you want variety without confusion. *"Three slightly different bone towers."*
- **Cousins** — clearly related but distinct silhouettes. Use for fleet variety. *"Three different sizes of garbage truck."*
- **Strangers** — fundamentally different designs. Use when the gameplay role is different. *"A bone tower vs. a tentacle vs. a lava ball."*

The DLX obstacle set uses all three: siblings (color variants within a tunnel type), cousins (different tower silhouettes), strangers (towers vs. tentacles vs. wrecks).

### 7. The "does it read?" test

The single most important question when reviewing a sprite:

> **At gameplay speed and gameplay size, can the player instantly tell what it is and what it does?**

If a sprite is gorgeous but unreadable at speed, it fails. Tests to apply:
- **Squint test** — blur your eyes. Does the silhouette still communicate?
- **Speed test** — fast-forward the game. Does the sprite still register?
- **Stranger test** — show it to someone who hasn't seen it. Can they identify it in 1 second?

Beauty serves clarity, not the other way around.

### 8. Color discipline

The DLX game uses a **fixed palette per biome**. Inside that palette, every color has a job:

- **Sky stops** — vertical gradient, sets mood
- **Terrain stops** — ground band, never invades sky band
- **Obstacle colors** — chosen to contrast against both sky and terrain
- **Player colors** — always pop against everything
- **Energy / highlight** — saturated accents, used sparingly

When you add a new sprite, ask: *does this need a new color, or can I express this with the existing palette?* The answer is almost always "use existing." A small palette forces creative shading.

### 9. The "designer ↔ director" dynamic

This project runs on a tight loop between two roles:

- **Creative director (the human)** — vision, taste, "yes / no / not quite," story sense, what feels right
- **Game designer (the AI)** — execution, options, "here are 3 ways to do this," technical reality

The handoffs:
1. Director sets the goal ("the devil needs to feel like he's hovering")
2. Designer proposes options ("we could bob him, dangle his legs, sway his tail, add a flame — recommend all four")
3. Director picks ("yes to all, but the flame should be its own layer")
4. Designer ships v1 ("here it is")
5. Director reacts ("the legs need more dangle")
6. Loop

What makes this work:
- **The director doesn't need to know how** — they just need to know what feels right
- **The designer offers options, not orders** — multiple paths, with a recommendation
- **Both sides commit to speed** — ship rough, iterate fast, polish only what survived iteration

### 10. Knowing when to stop

A sprite is done when:
- It passes the "does it read?" test at gameplay speed
- It fits the style rules
- It has at least one **delight detail** — a specular pip, an animation flourish, a clever silhouette twist
- Adding more would *subtract* from clarity

The trap is **over-polish** — adding detail until the sprite becomes noise. The discipline is to recognize "good enough" and move on to the next sprite. **You'll get more done by shipping 20 good sprites than by polishing 5 perfect ones.**

### The taste loop

Everything above is in service of one thing: **building taste**. You can't read your way to taste. You build it by:

1. Drawing a lot
2. Comparing your work to references you admire
3. Shipping things and getting reactions
4. Noticing what works and what doesn't
5. Adjusting next time

After enough cycles, "what looks right" becomes instinct rather than decision. That's the goal. Until then, lean on the rules above as scaffolding.

---

## Final notes

Pixel art is one of those skills where **100 small experiments** will teach you more than 10 hours of reading. The mental shift is:

- You don't have to be a great artist — every shape is just rectangles
- You don't have to know advanced math — `sin`, `cos`, and `%` cover 95% of motion
- You don't have to optimize — modern browsers can paint 50,000+ rectangles per frame

Have fun, and don't worry about "messing it up." Every sprite in this repo started as something that looked terrible, then got iterated 5-10 times. That's just how it works.

— Built alongside DLX Garbage Hauler, but living its own life from here on. 🎨
