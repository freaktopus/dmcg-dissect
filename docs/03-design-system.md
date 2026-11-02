# 03: Design system

**Sources:**
- the single production stylesheet `3k3yyhwzkzxln.css` (92 KB raw / 19 KB br), summarised with `tools/css_tokens.py`;
- the CMS-injected `<style id="site-typography">`;
- the RSC theme objects;
- computed styles from headless Chromium.

Screenshots: `../screenshots/`.

## The idea in one line

The type is tiny and uniform, set in one grotesk. The imagery is large, cut out and floating, on near-white or warm-neutral grounds. Hierarchy comes from **space, position and motion, not type size**. The home page has no headline at all: the header lockup and two corner captions frame a column of product renders.

## Colour

Everything is a handful of neutrals. Each case study tints the whole page with its own ground and ink, set in the CMS.

| Role | Value | Where |
|---|---|---|
| Page ground (home, about, catalog, incubator) | `#FFFFFF` | CMS theme (`:root{--page-background:#FFFFFF;--page-foreground:#000000}` injected in `<body>`) |
| Ink | `#000000` | same |
| CSS fallback ground / "constellation" catalog | `#7b776d` (warm grey) with `#f6f6f6` ink and alpha variants (`#f6f6f640`, `#f6f6f673`, `#f6f6f6b3`) | `:root{…--page-background:#7b776d;--page-foreground:#f6f6f6}` |
| Case-study default | `#DCDCDC` ground / `#404040` ink, 15px/22px | `.case-study-page{--case-page-background:#dcdcdc;--case-page-color:#404040…}` |
| Hairlines / outlines | `#e5e5e5` | `var(--site-header-outline,#e5e5e5)` on nav pills, catalog nodes |
| Quiet text | `#b3afaf` | `.incubator-page{--incubator-quiet:#b3afaf}` (status labels) |
| Text selection | `#fffb00` on `#000` | `body:not(:has(#sanity)) ::selection{color:#000;background:#fffb00}` |
| Accent (admin only) | `#ff7d61`, `#d8e8c9` | thumbnail-preview bridge, "archive corner lab" |

Per-project themes from the RSC payload (`pageBackground` / `textColor`):

| Project | Ground | Ink |
|---|---|---|
| Infinite Machine, Hedroom, Americana | `#DCDCDC` | `#404040` |
| Tolan | `#F7F6E5` | `#585550` |
| Sandbar | `#DAD4C4` | `#585550` |
| Evara | `#ECEAE5` | `#404040` |
| Archiv | `#F1EFEC` | `#827A6D` |
| Groth | `#625F4A` | `#E0DBD1` |

The catalog cards use muted swatches such as `#666b68`, `#685f52`, `#71766f`, `#727d67` and `#88735f`. Colour mixing relies heavily on `color-mix(in srgb, …)` (about 40 uses), for example in edge "washes" and alpha tints of `currentColor`. There's no dark mode and no `prefers-color-scheme` query.

## Typography

- **One family:** **PP Neue Montreal** (Pangram Pangram), self-hosted through `next/font/local` in two families:
  - `neueMontreal` 500 (Medium), which is preloaded and used almost everywhere;
  - `neueMontrealWeights` 400 and 600, used for body text and bold labels.
- **Fallback:** a metric-matched local face, `"neueMontreal Fallback"` with `size-adjust:97.68%; ascent-override:98.07%`, which is why CLS is about 0. `font-display: swap`.
- **Stack:** `var(--font-neue-montreal-weights), var(--font-neue-montreal), "Helvetica Neue", Helvetica, Arial, sans-serif`.
- **Rendering:** `-webkit-font-smoothing: antialiased` on all text, and tracking is opened up to **+0.04em** almost everywhere. This loose tracking is the key typographic "voice".

Type roles come from the CMS (`--type-<role>-{size,leading,tracking}`):

| Role | Desktop | ≤900px |
|---|---|---|
| navigation / office (lockup) / corner | 14 / 16, +0.04em | 12 / 16 |
| body | 14 / 22, +0.04em | 12 / 18 |
| case-study body | 15 / 22, +0.01em (CSS) | — |
| caption | 11.2 / 16, +0.045em | same |
| catalog | `max(11px, 0.578947vw)` / `max(14px, 0.736842vw)` | same |
| incubator intro / name / text / details | 17.1/21.1 · 25/16 · 15/18 · 12/16 | same |

In practice the scale runs only from **11px to 25px**. The largest "display" type on the site is the hand-drawn "THINK WITH YOUR EYES" wordmark (an image) and the logos inside the project imagery. The site lockup is three centred lines, "The / Design Office / of David McGillivray", at 14px Medium.

## Spacing, grid and layout

- **Frame.** `.portfolio` is a fixed full-viewport stage (`position:fixed; inset:0; height:100dvh; overflow:hidden; border-radius:.5556vw`). Every view scrolls inside its own container: `.case-widget--home`, `.case-study-page`, `.about-overlay__scroller`, `.incubator-page`. The document itself never scrolls on desktop. Below 900px it switches to `position:relative; min-height:100svh` with normal document scroll.
- **Viewport-relative edges:**
  - `--site-edge: 2.2222vw`, which is 32px at 1440 wide;
  - `--site-edge-top: 1.8519vw`, about 26.7px at 1440;
  - `--dock-centre: 2.338vw`.

  Many desktop sizes are written in `vw` (`.7639vw`, `.9028vw`, `1.1806vw`), so the composition scales with the viewport rather than reflowing.
- **No grid on the home page.** Project cards are `position:absolute` and placed by JS from per-project CMS values (`thumbnailLayout.width` 305–476px, `x/y`, spacing). The result is a hand-composed vertical column, not a responsive grid. Grids do appear in case-study blocks (`repeat(2|3, minmax(0,1fr))`, `var(--case-columns,…)`) and the header (`1fr auto 1fr`).
- **Breakpoints.**
  - **One layout breakpoint at 900px.** There's no other width query in the CSS: `(max-width:900px)` ×5, `(min-width:901px)` ×1.
  - The CMS also defines wide (1920) and tablet (1024) screens, but only for type.
  - Input-capability queries: `(hover:hover)` ×7, `(hover:none),(pointer:coarse)`, `(any-pointer:coarse)`.
  - Short-viewport queries: `(max-height:700px)` and `(max-height:640px)`.
  - `(prefers-reduced-motion)` ×8.
- **Modern CSS in use:**
  - `:has()` ×7;
  - `@property` ×2;
  - `container-type` ×3;
  - `dvh/svh` ×9;
  - `mask-image` ×24;
  - `backdrop-filter` ×22;
  - `filter: blur()` ×50;
  - `mix-blend-mode: plus-lighter`;
  - `scale`/`translate` as standalone properties;
  - `@supports (corner-shape: superellipse(2))`.

## Components (as named in the CSS)

| Component | Notes |
|---|---|
| `.site-header` | Left: About, Contact. Centre: office lockup (link home). Right: `.view-mode-switcher` (Projects / Catalog, `aria-pressed`), `.site-sound-toggle` |
| `.contact-pill` | "Contact" button that expands into a pill showing `office@dmcg.co` + "Copy" → "Copied ✓"; `role="status"` sr-only announcer |
| `.project-grid-card` / `.project-thumbnail` | Poster image + hover video; `data-thumbnail-label=<slug>` used by analytics |
| `.case-study-dock` | Top-centre dock of mini project thumbnails, with a close button and a **resize handle** (`title="Drag to resize · double-click to reset"`, `aria-valuemax="140"`) |
| `.case-study-page` | Article with `h1` title, sections (`case-study-section--small/--full`), `figure.case-study-media`, footer (Twitter, LinkedIn, copy-email, legal) |
| `.about-overlay` / `.about-panel` | Centred text panel on a large soft radial grey glow (see `about-desktop.png`) |
| Catalog: `.node-grid`, `.node-pill`, `.constellation__*` | Tree diagram Catalog → Logo/Digital/Physical → thumbnails, connected by thin curves; grid/tree toggle at bottom (`catalog-desktop.png`) |
| `.incubator-card` | Image, name, type + green status dot + quiet status text, description, link with ↗ |
| `.mobile-nav` | Hamburger and "projects" toggles, tray with `--mobile-tray-blur` backdrop |
| `.home-edge` | Top/bottom progressive-blur + colour-wash bands that fade content under the header and corner captions |
| `.browser-tint` | 12px fixed bars at the top and bottom at 12% opacity, touch devices only **[inferred: tints mobile browser chrome/safe areas]** |

**Shape language: squircles.** Pills and buttons use `border-radius: calc(.5714em * var(--squircle-radius))` together with `corner-shape: superellipse(2)`. A `--squircle-radius: 1.841` multiplier keeps the visual size consistent whether or not the browser supports `corner-shape`. Hover outlines are 1px `#e5e5e5` rings drawn on `::after` and faded in.

## Iconography

There's very little. Two first-party SVGs, `/icons/copied-check.svg` and `/icons/sound-on.svg` (plus an off state), the hamburger/close/projects icons drawn in CSS spans, and "↗" text arrows. Sanity UI icons appear only in the admin chunks.

## Imagery and video

- **Home:** square 1080×1080 transparent PNG **cut-outs** of each project's hero artefact: the scooter, the phone, the Tolan card, a chrome knot, the Groth wordmark, the Americana card, the ring and the Evara device. They float on white with no frames or captions. On hover each still is replaced by a short WebM loop.
- **Case studies:** large rounded-corner media (`--case-frame-radius`) on the project's tinted ground. Content is a mix of polished renders, UI screens in device frames, product photography and inline video. Text columns are narrow (about 530px), sitting between full-width media.
- **Photography** appears mainly in the incubator (the Corners storefront at dusk, a phone on wood under leaf shadows).
