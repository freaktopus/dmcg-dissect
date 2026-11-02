# 04: Interaction and motion

**How this was observed:**
- read from the CSS and JS bundles;
- rendered in headless Chromium;
- a scripted hover → click → settle sequence captured over CDP (`tools/cdp_frames.mjs`), with frames in `../screenshots/transition-*.jpg`.

Code excerpts are short quotes from the minified production bundles, so the variable names are the minifier's.

**Toolkit.** Motion (the framer-motion API) handles anything driven by state or physics. Plain CSS transitions and keyframes handle reveals and hovers. The Web Animations API covers a couple of one-shot effects, and hand-written `requestAnimationFrame` loops drive the embeds. There's **no GSAP, no smooth-scroll library and no WebGL**. Scrolling is native, inside overflow containers with `overscroll-behavior: contain`.

**Signature easing.** `cubic-bezier(.22,1,.36,1)`, an "ease-out-quint"-style curve, appears 34 times. `cubic-bezier(.4,0,.2,1)` (Material standard) is used for hover crossfades. **Signature effect:** *blur-to-sharp*. Almost every entrance animates `filter: blur(Npx) → none` together with opacity, sometimes with a tiny scale settle (1.012 → 1).

## 1. Intro sequence (page load)

`main.portfolio` starts with `data-intro="pending"`, which hides the thumbnails, then switches to `"revealing"`:

```css
.portfolio[data-intro=revealing] .case-widget--home .project-thumbnail-wrap{
  --intro-blur:12px;--intro-delay:calc(min(var(--intro-order,0), 4) * .14s);
  animation:site-intro-focus 1.1s cubic-bezier(.22,1,.36,1) var(--intro-delay) backwards,
            site-intro-fade .9s ease var(--intro-delay) backwards,
            site-intro-settle 1.3s cubic-bezier(.22,1,.36,1) var(--intro-delay) backwards}
@keyframes site-intro-focus{0%{filter:blur(var(--intro-blur))}}
@keyframes site-intro-settle{0%{scale:1.012}}
```

- **Thumbnails** focus in, staggered by 140ms and capped at the 5th item so the sequence never drags.
- **Header items** use the same focus and fade at 6px blur, staggered 0 / .12 / .17 / .22 / .28s from the outside edges in.
- **Without JavaScript,** `<noscript><style>.portfolio[data-intro] .project-thumbnail-wrap{opacity:1!important}</style></noscript>` keeps the page visible.
- The whole block sits inside `@media (prefers-reduced-motion:no-preference)`.

## 2. Thumbnail hover: still → video

Each card holds a poster `<img>` and a `<video preload="none" muted playsInline>`. On hover the video starts and crossfades in **through blur**:

```css
.project-thumbnail-video{--thumbnail-hover-blur:14px;--thumbnail-hover-ease:cubic-bezier(.4,0,.2,1)}
.project-thumbnail-video video{opacity:0;filter:blur(var(--thumbnail-hover-blur));mix-blend-mode:plus-lighter;…}
.project-thumbnail-video[data-active=true] video{opacity:1;filter:blur();transition:opacity .12s linear,filter}
```

- **Blend mode.** `plus-lighter` makes the overlapping still and video add up during the crossfade, so there's no dip in brightness.
- **Exit modes.** A per-card `data-hover-out="fade|blur|both"` (set in the CMS) picks how the video leaves.
- **When video loads.** It loads only when the card intersects the viewport *and* `window.matchMedia("(any-hover: hover)")` matches, checked inside an `IntersectionObserver` callback.
- **Mobile.** On screens ≤900px the hover layer is hidden and only the poster shows.

## 3. Project open: the "genie" dock (the signature transition)

Clicking a project doesn't navigate in the usual sense. **All eight thumbnails are sucked along a curve into a dock pill at the top centre**, like the macOS Dock "genie" effect. The pill then becomes the case-study navigator, and the case study fades and focuses in underneath. Captured frames:

- `transition-1-genie-120ms.jpg`: the cards are mid-flight in a diagonal stream, shrinking toward the empty dock pill.
- `transition-2-docked-370ms.jpg`: all eight are docked as small icons and the background has switched to the project's ground colour.
- `transition-3-case-open.jpg`: the case-study hero and text are revealed. The dock gains a close (×) button and a resize handle.

Implementation (module exporting `DockGenieArtwork`, `DockGenieSurface`, `useDockClip`, `DOCK_MOTION_DURATION: .68`):

```js
let s=e=>Math.max(0,Math.min(1,e)),u=e=>{let t=s(e);return t*t*(3-2*t)};          // clamp + smoothstep
function d(e,t,r,a){ … n=u((a-.38*(1-i))/(.62-.1*i)), … c=Math.sin(Math.PI*i)*Math.sin(Math.PI*a)*e.height*.1;
  return{x:o+(e.targetX-o)*n, y:l+(e.targetY-l)*n+c+r*e.height/2*d, thickness:d, absorption:n}}
```

- **Per-column delay.** `d()` maps each point of a card (its normalised column `t`, row `r` and progress `a`) toward the dock target. Columns further along start later (`.38*(1-i)`), which is what makes the card *pour* in rather than shrink uniformly. A `sin·sin` term adds a sideways bulge.
- **Card artwork.** `DockGenieArtwork` samples `d()` at three nearby columns to get local stretch and slope. It applies them as Motion values `x, y, scaleX, scaleY, skewY, opacity, filter: blur(5·h px)`, using `useTransform`.
- **Card silhouette.** `DockGenieSurface` and `useDockClip` build a 32-segment SVG path for the warped outline, with squircle-ish corners from `sign(x)·|x|^0.5`. It's used both as an `<svg class="case-study-dock__liquid">` surface and as `clip-path: path("…")`. Paths are memoised per progress value in a `WeakMap`.
- **Closing.** The cards flow back out, and the "Projects" switcher does a jelly squish:

  ```css
  @keyframes project-link-liquid-absorb{0%,48%{transform:scale(1)}70%{filter:blur(.25px);transform:scaleX(1.055)scaleY(.96)}86%{transform:scaleX(.985)scaleY(1.015)}to{transform:scale(1)}}
  ```

- **Switcher highlight.** The view-mode switcher's highlight pill animates through Motion values (initial `0.86`/`0.92` scale) in sync with dock phases: `closed → arriving → opening → open → closing`. The phases are exposed as `data-project-dock-phase` on `.portfolio` so CSS can react.

## 4. Case-study scroll reveal

The reveal settings come from the CMS: `caseStudyMotion:{duration:520, blur:7, zoom:1.2, stagger:110, maxWait:1200}`. Each block starts in a pending state:

```css
.case-study-media__surface[data-reveal=pending]{filter:blur(var(--case-reveal-blur,7px));opacity:0;transform:scale(var(--case-reveal-scale,1.012))}
transition: filter var(--case-reveal-duration,.52s) cubic-bezier(.22,1,.36,1),
            opacity calc(var(--case-reveal-duration,.52s) * .81) ease,
            transform calc(var(--case-reveal-duration,.52s) * 1.19) cubic-bezier(.22,1,.36,1)
```

- **Reveal queue.** A small class (`stagger`, `maxWait`, a `blocks` Map, one shared `IntersectionObserver` rooted on the case-study scroller) releases blocks one at a time. A block goes once it's *both* loaded and in view, at least 110ms after the previous one, and never later than 1.2s after becoming eligible. This avoids revealing half-loaded images while keeping a rhythm.
- **Text blocks** blur at 0.86× the media blur.
- **Video blocks** keep the poster up until the first frame is ready: `[data-revealed=true] .case-study-video__poster{opacity:0}`.

## 5. Springs and micro-interactions (Motion)

| Use | Settings |
|---|---|
| Snappy UI (pills, highlights) | `{type:"spring",stiffness:620,damping:39,mass:.56,restDelta:.01}` |
| Bouncy element | `{type:"spring",stiffness:340,damping:14,mass:.85}` |
| Slow catalog drift | `animate(p,1,{type:"spring",stiffness:64,damping:15,mass:1,delay:e})`, with delay staggered by order and capped at 40 |
| Sound-toggle press | `scale:1.18` over 90ms, then `{type:"spring",visualDuration:.42,bounce:.5}` back to 1 |
| Press feedback (WAAPI) | `e.animate([{scale:t,easing:"ease-out"},{scale:.88*t,offset:.35,…}])` |

## 6. Soft edges (progressive blur)

At the top and bottom of the scrolling tray, content melts under the header rather than being cut off. `SoftEdge` stacks three `backdrop-filter` layers with increasing blur (1.5px, 5px, 14px). Each layer is masked to a different band of the edge, and a `color-mix` gradient wash of the page colour sits on top:

```js
o=`linear-gradient(${"top"===e?"to top":"to bottom"}, transparent ${a}%, #000 ${a+i}%, #000 ${a+2*i}%, transparent ${a+3*i}%)`;
… style:{backdropFilter:`blur(${r}px)`, maskImage:o}
```

This is the now-common "progressive blur" technique, done without images or canvas.

## 7. Contact pill

"Contact" is a `<button>` that **copies `office@dmcg.co`** instead of opening a mailto link. A hidden `.contact-pill__measure` element sizes the pill first. The pill then grows from `scale(0.6)`/`width:0` with text de-blurring from `blur(3px)`. "Copy" swaps to "Copied ✓", the sr-only `role="status"` region announces it, and a sound plays (`contact.copy` → "Felt reveal" recipe).

## 8. UI sound design (Web Audio)

The site plays **synthesised** clicks and chimes. There are no audio files: every sound is rendered from a parameter "recipe" stored in the CMS.

```json
{"interaction":"project.open","title":"Dial step","recipe":{"voice":"tick","pitch":1760,"duration":30,"brightness":55,"body":10,"variation":10,"volume":13,…}}
{"interaction":"contact.copy","title":"Felt reveal","recipe":{"voice":"soft","pitch":440,"duration":320,"space":35,"notes":3,…}}
{"interaction":"sound.on","title":"Bright chime rise","recipe":{"voice":"chime","pitch":2093,"duration":420,"notes":3,…}}
```

- **Rendering.** `SoundPlayer` is a lazily imported 17 KB chunk. It pre-renders each recipe into a buffer with `new OfflineAudioContext(1, …, 48e3)` and normalises the peak.
- **Unlocking.** It unlocks on the first trusted `pointerdown`/`keydown` and keeps the context awake on activity.
- **Triggering.** Sounds fire on a custom `SITE_SOUND_EVENT`.
- **Mapped interactions:** `project.open/close`, `dock.open/close/hover`, `nav.hover`, `view.change`, `page.navigate`, `archive.open/branch`, `contact.copy` and `sound.on`. Master volume is 20.
- **Off switches.** **Safari is excluded** by UA test (`/Version\/[\d.]+.*Safari\//`). There's a visible mute toggle (`aria-label="Mute interaction sounds"`), persisted in `localStorage["dmcg:ui-sound-muted:v1"]`, and nothing plays while `document.hidden`.

## 9. Other views

- **About overlay.** A centred text panel over a large soft radial grey "glow", with an `--about-blur` variable driving a focus-in.
- **Catalog.** A tree layout where curves fan out from "Catalog 106" to the Logo/Digital/Physical nodes and on to the project thumbnails. Filter rows enter with `constellation-row-in` (opacity, blur 3px, translateY 6px, .46s). Hover rings on the letter index slide with `transition: translate .56s cubic-bezier(.22,1,.36,1)`.
- **Incubator.** A horizontal card rail. Each card enters with `incubator-card-in .9s cubic-bezier(.22,1,.36,1) calc(.12s + index*70ms)` from `translate: 32px`. **[inferred]** The rAF `scrollLeft` easing in chunk `1731z5xiqdj0x.js` (`n.scrollLeft=r, … requestAnimationFrame(l)`) drives programmatic rail scrolling.

## 10. Embedded heroes (vanilla JS)

- **`/embeds/archiv-hero/`.** An SVG scene with the ARCHIV wordmark. Ten object photos (WebP, with titles such as "Braun SK 410 Radio-Phonograph by Dieter Rams…") cycle *over* the logo every 750ms, crossfading through blur: `const STEP = 750; const FADE = 140; const BLUR = 4;`. It uses WAAPI keyframes per object and decodes every image before starting.
- **`/embeds/hedroom-hero/`.** The HEDROOM™ wordmark with 21 user "artifacts" flicking by at `FLICK = 0.135`s each, with a 70ms blurred crossfade, driven by its own rAF clock.
- **Shared behaviour.** Both pause when the iframe is hidden or off-screen, honour `prefers-reduced-motion` by showing a still frame, and post `dmcg:case-study-embed-ready` to the parent so the reveal queue can show them.

## 11. Reduced motion and accessibility of motion

- **CSS:** 8 `prefers-reduced-motion` blocks. Intro animations are wrapped in `no-preference`, and thumbnail blur transitions drop to `filter:none; transition:none`.
- **JS:** Motion's `useReducedMotion()` is checked in each animated component:
  - the view-switcher highlight shortens its timing (`c?.12:.26`) rather than dropping the transition;
  - the dock's per-card warp is switched off (`f=a&&!p`);
  - video loops pause, and the embeds freeze on a still frame.
- **Missing:** there's no separate control for the *sound* tied to reduced motion. Sound is its own toggle.

## Not present

There are no custom cursors, no page-transition library, no WebGL or shaders, no scroll-jacking, no scroll-linked parallax (`animation-timeline`/`view-timeline` are unused) and no loader screen. The intro reveal stands in for a loader.
