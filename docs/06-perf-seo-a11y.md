# 06: Performance, SEO and accessibility

**Method.** Headless Chromium (desktop build, `--headless=new`) driven over CDP by `tools/cdp_netlog.mjs`, with the cache cleared before each load. The run was **unthrottled**, from India, and Vercel served the requests from its `bom1` edge. These are *field-style observations, not a Lighthouse score*. On a throttled 4G/mid-tier mobile profile the LCP numbers would be considerably worse. Raw logs are in `raw/misc/net-*.json`.

## Page weight and requests

| Page (viewport) | Requests | Transferred | Breakdown | FCP | LCP (element) | CLS |
|---|---|---|---|---|---|---|
| `/` 1440×900 | 36 | **783 KB** | HTML 172 KB · JS 20 files 355 KB · CSS 19 KB · font 53 KB · 11 images 202 KB | 1.54 s* | 2.17 s (`img.project-thumbnail-video__still`) | 0.0001 |
| `/` 390×844 @3x, touch | 38 | 844 KB | images 13 / 257 KB | 0.92 s | 3.48 s | 0 |
| `/about` 1440×900 | 42 | 841 KB | 2 fonts (500 + 600) 105 KB | 0.94 s | 0.99 s | 0.0002 |
| `/archive` 1440×900 | 184 | 969 KB | 130 of the requests are inline `data:image/svg+xml` URIs; 24 WebP | 0.58 s | 1.79 s | 0.0002 |
| `/work/hedroom` 1440×900, scrolled to end | 100 | **7.4 MB** | 12 media requests (6 WebM) 4.3 MB · 49 images 2.5 MB · 3 `hedroom.fm` iframes | 0.72 s | n/a† | 0.0001 |

\* First run, which included a cold serverless function: TTFB 279 ms. Later runs had TTFB of about 76 ms.
† The LCP entry kept updating during the scripted scroll, ending at 13.7 s on a video poster. That's an artefact of scrolling, not a real LCP.

### What's good

- **Images.** Images go through `next/image` as WebP with a full `srcset`, so the browser picked `w=750` at 1440 wide for `45vw` cards. Case-study media below the fold are lazy and progressive: the server HTML holds placeholders (`case-study-media__asset-placeholder`, `data-load-state="pending"`). For example, `/work/infinitemachine` has `data-media-count="10"` but only 3 `<img>` in the server HTML.
- **Video.** Clips are `preload="none"` and load only on hover (desktop) or near the viewport. Resolution is chosen per viewport (`1080.webm` vs `1920.webm`).
- **Fonts.** Only one 53 KB WOFF2 is needed on most pages, and it's preloaded through the `Link:` header. The metric-matched fallback brings CLS to about 0.
- **Caching and compression.** Static chunks are `immutable` for a year, and everything is Brotli-compressed. The `nomodule` polyfill chunk (112 KB) is correctly skipped by modern browsers.
- **Third parties.** There are no third-party JS or tag managers, and analytics is a single 120-byte `fetch`.

### What's costly

1. **The whole site is inlined into every HTML response.** About 540 KB of inline RSC flight data makes up 622 KB of raw HTML, or **172 KB Brotli** on every page. That's more than the CSS, fonts and all home images combined. It buys instant view switches, but every landing page (including a deep-linked case study from search) pays for all the other case studies' text and metadata up front.
2. **No HTML caching.** Responses are `cache-control: private, no-cache, no-store` with `x-vercel-cache: MISS`, so every visit is a dynamic render. With ISR or static generation plus on-demand revalidation from a Sanity webhook, the HTML could come from the edge.
3. **JavaScript: 355 KB Brotli** (about 1.1 MB raw) for what is visually a gallery. The main contributors are react-dom 19 canary (66 KB br), Next runtime (40 KB), Motion (53 KB br chunk), the Sanity image and URL helpers, and bespoke view code. Sanity Live and Visual Editing are correctly lazy, but the stega `data-sanity` attributes still ship in production HTML.
4. **Eight preloaded hero images.** The homepage sends 8 `<link rel="preload" as="image">` plus `loading="eager"` for all eight posters. Only one or two are in the first viewport. Preloading all eight competes with the LCP image for bandwidth and probably accounts for the 3.5 s mobile LCP.
5. **Image quality and format.** `q=90` is high for photographic WebP; 75–80 is usually indistinguishable. AVIF isn't enabled (`images.formats` left at default). One alpha PNG is served as PNG (`84259ded…`, 4.8 KB, so the cost is trivial).
6. **Case-study weight.** Heavy case studies reach 7 MB or more once fully scrolled. That's acceptable for a portfolio because it's demand-driven, but the WebM loops (up to 2.2 MB each at 1080) could use lower bitrates or shorter loops.

## SEO

| Check | Result |
|---|---|
| `<title>` | Descriptive on case studies ("Tolan Brand Design by David McGillivray"); **generic on home** ("The Design Office of David McGillivray"); "About — …", "Catalog — …" |
| Meta description | Present on all pages; home's is thin ("Brand and software design by David McGillivray.") |
| Canonical | Present on every page (`https://dmcg.co`, `https://dmcg.co/work/tolan`, …) |
| Open Graph / Twitter | Complete, including `og:image:alt`. **Per-project 1200×630 OG images** cropped through the Sanity CDN (`…?w=1200&h=630&fit=crop`); home, about, archive and incubator share `/share-image.png` |
| Structured data | JSON-LD `@graph`: `Organization` (with `founder` Person, email, `sameAs`), `WebSite`, `WebPage`; case studies add `CreativeWork` (`creator`, `keywords`, `image`) as `mainEntity` |
| Server rendering | All case-study text is server-rendered (an `h1` plus 12 sections in the Infinite Machine HTML) |
| `robots.txt` / sitemap | Allow-all except `/CMS` and `/api/`; sitemap of 12 URLs with **no `lastmod`** |
| Headings | **No `<h1>` on home, About or Catalog.** Case studies have only an `h1` (section labels are paragraphs). Incubator has an **empty `<h1>`** (the hand-lettered wordmark) plus `h2`s for ventures |
| 404 handling | Unknown URLs return **`307` → `/?from=<path>`**, with a `not-found` analytics event. Search engines will treat these as soft 404s; a real `404` status with the same UI would be better |
| Image SEO | Every server-rendered case-study `<img>` has `alt=""` (all 8 case studies, 2–5 images each), so image search gets nothing |
| Minor | `sameAs` and footer use `http://x.com/dmcgco` (not https); `meta color-scheme="dark"` on a light site |

### AI and answer-engine readiness (a standout)

The site is unusually well prepared for LLM crawlers and agents:

- **`robots.txt` points AI tools at `/llms.txt`.** That file is a curated summary of positioning, services, fit and every page.
- **`/llms-full.txt`** (~50 KB) is the whole site as Markdown.
- **Every page has a Markdown twin** at `<url>.md`.
- **Content negotiation:**
  - `GET /work/tolan` with `Accept: text/markdown` returns Markdown;
  - the response carries `vary: Accept` and `link: <https://dmcg.co/work/tolan>; rel="canonical"`;
  - it also sends an `x-markdown-tokens: 1199` header estimating its token cost.
- **The analytics closes the loop.** It buckets AI-assistant referrers separately and logs the `#:~:text=` fragment that an AI or search engine deep-linked to (see [02](02-tech-stack.md)).

## Accessibility

### Strengths

- `<html lang="en">`. Every icon-only control is labelled: "Open menu", "Show catalog view", "Mute interaction sounds" and "Contact: copy office@dmcg.co".
- **State is exposed.** The switcher uses `aria-pressed`, the mobile nav uses `aria-expanded`/`aria-controls`, the copy confirmation goes through a live `role="status"` region, and decorative layers carry `aria-hidden`.
- **Visible focus.** There are 48 `:focus-visible` rules. Header controls show the same squircle ring on focus as on hover.
- **Reduced motion is respected everywhere:**
  - CSS intro, hover blur and reveals;
  - JS Motion components;
  - the video loops;
  - both embeds, which show a still frame.
- **Embeds and fallbacks.** The embeds are `role="img"` SVGs with `<title>`/`<desc>`. `<noscript>` styles keep content visible without JS.
- **Clipboard fallback.** If the clipboard write fails, the contact action falls back to `mailto:`.

### Issues

| Issue | Evidence | Impact |
|---|---|---|
| Missing heading structure | No `h1` on `/`, `/about`, `/archive`; About's "Approach / Technology / Working Together" are bold `<p>`/spans; incubator `h1` is empty | Screen-reader users can't navigate by headings; weak document outline |
| Empty alt on content images | All server-rendered case-study images `alt=""`, including heroes such as the Tolan app-icon artwork | The work itself is invisible to non-sighted users. Home tray stills *do* have good alts ("Infinite Machine scooter", "ARCHIV mobile product interface") |
| Low contrast: incubator status text | `#b3afaf` on `#FFFFFF` = **2.17:1** (`tools/contrast.py`) | Fails AA at 12px |
| Low contrast: Archiv case-study ink | `#827A6D` on `#F1EFEC` = **3.53:1** | Fails AA for 15px body text |
| Low contrast: catalog "constellation" muted hub | `#f6f6f6` at 40% alpha on `#7b776d` ≈ 1.9:1 **[computed by alpha blend, approximate]** | Fails, though it's an inactive state |
| Passing pairs | `#404040` on `#DCDCDC` 7.56:1, `#585550` on `#F7F6E5` 6.81:1, `#E0DBD1` on `#625F4A` 4.68:1, black on white | Pass |
| Small type | Body text is 14px desktop and **12px mobile**. Catalog is 11px, in `vw` on some elements (`.7639vw` = 11px at 1440, smaller below) | Readability; vw units don't respond to user font-size preferences |
| Dock resize handle | `tabindex="-1"` with `aria-valuetext`, so it isn't keyboard-operable | Minor (enhancement only) |
| Audio on interaction | Synth clicks are on by default (volume 20) except in Safari; mute toggle present | The sounds are short (<0.5 s), so WCAG 1.4.2 isn't triggered, but they may surprise screen-reader or keyboard users. The default could respect reduced motion |
| Fixed stage + nested scrollers | `body` doesn't scroll on desktop; content scrolls in `.case-widget--home` (`tabindex="0"`) and `.case-study-page` | Works with keyboard once focused. Browser features that assume document scroll (find-in-page scroll, some extensions, scroll restoration) behave differently |
| `color-scheme: dark` meta | `<meta name="color-scheme" content="dark">` on a white UI | Can render dark scrollbars or form controls and a dark flash before CSS |

## Lighthouse-style checklist

| Area | Observation | Rough grade |
|---|---|---|
| Performance | Fast TTFB/FCP on a good network, CLS about 0, but heavy HTML/JS and eight preloads. Expect a mobile Lighthouse score in the 60s–70s **[inferred]** | B– |
| Accessibility | Labels, focus and reduced motion are excellent; headings, alt text and some contrast are poor **[inferred score 80s]** | B– |
| Best practices | HTTPS + HSTS, no third-party cookies, no console errors (one iframe `allow`/`allowfullscreen` warning); missing CSP and other security headers | B |
| SEO | Rich metadata, JSON-LD, SSR, LLM mirrors; let down by missing `h1`s, soft 404s and empty alts | B+ |
