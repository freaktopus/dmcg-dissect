# 02: Tech stack

Everything here is **verified** from response headers, HTML and the shipped bundles unless marked **[inferred]**. Evidence files are in `raw/` (gitignored) and can be regenerated with `tools/fetch_site.sh`. Excerpts are short and quoted from minified code.

## Summary

| Layer | Finding | Evidence |
|---|---|---|
| Hosting / CDN | Vercel | `server: Vercel`, `x-vercel-id: bom1::iad1::…` (edge in Mumbai, function in iad1 / Washington DC), `x-vercel-cache` |
| Framework | Next.js **16.2.12**, App Router | `window.next={version:"16.2.12",appDir:!0}` |
| Bundler | **Turbopack** (production build) | `turbopack-1tfsfv25jxxml.js`, `globalThis.TURBOPACK` chunk wrappers, hashed chunk names like `0-y2lzwdwmola.js` |
| React | **19.3.0-canary-3f0b9e61-20260317** | version string in `react-dom` chunk |
| CMS | **Sanity** (project `g94oo1l2`, dataset `production`), Studio embedded at `/CMS` | `cdn.sanity.io/images/g94oo1l2/production/…`, `x-matched-path: /CMS/[[...tool]]`, `data-sanity="id=project-tolan;type=project;path=caseStudy;base=%2FCMS"` |
| Live preview | Sanity Live + Visual Editing (lazy-loaded) | `"SanityLive"` component, lazy chunk exporting `VisualEditing`, RxJS chunks, `@sanity/ui` `ThemeProvider` |
| Asset storage | **Vercel Blob** mirror of Sanity and Cloudinary assets | `jkc1k8w6rhba2uqq.public.blob.vercel-storage.com/sanity/images/…`, `…/cloudinary/fs44x9ca/dmcg/case-studies/<id>/v…/1080.webm` |
| Images | `next/image` optimiser, q=90, served as WebP | `/_next/image?url=…&w=750&q=90` → `content-type: image/webp` |
| Fonts | `next/font/local`: PP Neue Montreal (Pangram Pangram) 400/500/600 | `PPNeueMontreal_Medium-s.p.….woff2` preloaded in `Link` header |
| Animation | **Motion** (framer-motion API) + CSS keyframes + WAAPI | `useMotionValue`, `useTransform`, `AnimatePresence`, `useAnimate`, `useReducedMotion` |
| Audio | Custom Web Audio synth for UI sounds | `new OfflineAudioContext(…)` in the `SoundPlayer` chunk |
| Analytics | Custom first-party, cookieless, `POST /api/v` | `let w="/api/v",v="dmcg:analytics-ignore"` |
| Third-party scripts | **None** on public pages | the only third-party hosts in network logs are `cdn.sanity.io` (favicon), Vercel Blob (media) and `hedroom.fm` (case-study iframes) |

Libraries I looked for and **did not find**: GSAP/ScrollTrigger, Lenis or Locomotive smooth scroll, Three.js/OGL/raw WebGL, Swiper/Embla/Keen, Barba/Swup, Google Analytics/GTM, Meta pixel, Hotjar, Clarity, Segment, PostHog, Plausible and Vercel Analytics. Fingerprinting script: `tools/fingerprint.py`.

## Routing architecture

The app is effectively a **single-page portfolio behind one catch-all route**:

```
x-matched-path: /[[...view]]          # every public page
x-matched-path: /md/[[...path]]       # .md mirrors (x-nextjs-rewritten-path: /md)
x-matched-path: /CMS/[[...tool]]      # Sanity Studio
```

- **Same bundle everywhere.** Every page ships the same 20 JS chunks and one CSS file. Case studies, About, Catalog and Incubator are client-side "views" layered over the home tray. Clicking a project calls `history.pushState`, and the analytics module patches `pushState` to catch it.
- **Whole site embedded in every page.** Each HTML document carries about **540 KB of inline RSC flight data**: 69–71 inline `<script>`s that hold the entire site's content. A unique sentence from the About bio ("Graphite Pencil") and Hedroom copy ("Listening Room") both appear in the *homepage* HTML. That's why any view can open instantly with no fetch. The cost is covered in [06](06-perf-seo-a11y.md).
- **No HTML caching.** HTML responses carry `cache-control: private, no-cache, no-store, max-age=0, must-revalidate` and `x-vercel-cache: MISS`, so pages are rendered dynamically on each request. **[inferred]** That's probably because of draft mode, Sanity Live or `searchParams` use. Static chunks are `public,max-age=31536000,immutable`.

## CMS depth (Sanity)

The Sanity schema controls far more than content. All of the following is serialised in the RSC payload:

- **Typography roles per breakpoint.** `typography.roles.{navigation,office,body,caption,footer,footerName,corner,catalog,incubator*}` each carry `{size,leading,tracking}`, plus `screens.wide(1920)/tablet(1024)/mobile(900)` overrides. The server writes these as CSS variables into `<style id="site-typography">`.
- **Per-project theme:**
  - `pageBackground` and `textColor`;
  - `frameColor`/`frameWidth`;
  - `thumbnailLayout {width, aspectRatio, cropped, zoom, x, y}` and `thumbnailMobile {width}`;
  - `thumbnailSpaceAfter`.

  The home tray is laid out by hand in the CMS: `projectsSpacing:-100`, `projectsStartSpace:-104`, `projectsEndSpace:163`.
- **Motion tokens:** `caseStudyMotion:{duration:520, blur:7, zoom:1.2, stagger:110, maxWait:1200}`.
- **UI sound design:** `settings.assignments[]` maps each interaction (`project.open`, `dock.hover`, `contact.copy`, `sound.on`…) to a synth "recipe" (see [04](04-motion.md)).
- **Case-study block types** (counted on the Hedroom page):
  - `caseStudyText`, `caseStudyFullImage`, `caseStudyFullVideo` and `caseStudyFullEmbed`;
  - `caseStudyMediaPair`/`Triple` and `caseStudyTextColumns`;
  - `caseStudyCanvasItem` and `caseStudyMediaItem`.

  Media blocks carry `cloudinaryVideo`, `appleVideo`, `backgroundColor`, `alignment`, `columns` and `customSpacingBefore`.
- **Custom tooling** (lazy chunks), which shows there's a bespoke admin layer on top of Studio:
  - `ProjectThumbnailEditor` / `AdminIcon`;
  - `ThumbnailsPreviewBridge`, an iframe preview that uses the `?thumbnails-preview` param and accent `#ff7d61`;
  - an `isTypographyPreview()` mode;
  - an "archive corner lab" with slider styles in the CSS.

## Media pipeline

- **Images.** Source PNGs live in Sanity (for example `…-1080x1080.png`). They're mirrored to Vercel Blob and delivered through `/_next/image` as WebP at q=90. `srcset` covers 384–3840w and `sizes="(max-width: 900px) 100vw, 45vw"`. One thumbnail came back as `image/png` (`84259ded…`), probably because it's a PNG with alpha that wasn't converted.
- **Video.** Clips are WebM files with paths like `cloudinary/fs44x9ca/dmcg/case-studies/<publicId>/v<ver>/{1080,1920}.webm`. **[inferred]** They're transcoded by Cloudinary and copied to Vercel Blob to avoid Cloudinary bandwidth costs. Each block also has an `appleVideo`/`appleSrc` field, and the player picks `appleSrc` on Safari. **[inferred]** That field likely holds HEVC-with-alpha for the transparent cut-out thumbnails, since WebM alpha isn't supported in Safari.
- **Video posters.** If no poster exists, a frame is drawn to a canvas and turned into a blob: `getContext("2d").drawImage(a,0,0,e.width,e.height),e.toBlob(…)`.
- **Interactive embeds.** These are small static micro-sites under `/embeds/<name>/index.html`, each just an SVG scene plus a ~3–4 KB vanilla `hero.js`. They're loaded in an iframe and signal readiness to the parent with `parent.postMessage({ type: 'dmcg:case-study-embed-ready' }, '*')`. The Hedroom case study also iframes live artifacts from `https://hedroom.fm/embed/artifact/<uuid>`, with static posters under `/embed-posters/<uuid>-<w>x400.webp`.

## Analytics (custom, first-party)

The analytics module lives in chunk `3_7zqt-_fn-xi.js` and is mounted by a `SiteAnalytics` component. What it does:

- **Transport.** It posts JSON to `/api/v`: `{type, payload:{hostname, language, screen, title, url, name?, data?}, cache}`. On unload it uses `navigator.sendBeacon`, otherwise `fetch(…, {keepalive:true})`. **[inferred]** The `{type,payload,cache}` shape and the returned `cache` token match the **Umami** collector protocol, so `/api/v` is probably a proxy to a self-hosted or cloud Umami. The website ID would be added server-side.
- **Events:**
  - pageview;
  - `read:10…100` scroll-depth milestones, recorded only after 5 s visible on case studies or About;
  - `hover:<slug>`, fired after **1 s** of hover on a thumbnail, fine pointers only;
  - `open:landing|link|back`;
  - `out:<host>` for outbound links, plus where on the page the link was (footer, menu, about, …);
  - `email:mailto` for mailto links, and `email:<location>` when the contact pill copies the address;
  - `sound:on|off`, `menu:open`, `tray:projects`, `catalog:*`, `filter:*` and `not-found`;
  - a `performance` event with LCP/INP/CLS/FCP/TTFB from Next's `useReportWebVitals`.
- **Referrer classification.** Referrers are sorted with regex lists into "Search", "Social", **"Design galleries"** (awwwards, godly.website, siteinspire, minimal.gallery, lapa.ninja, savee, cosmos.so, are.na …), **"AI assistants"** (chatgpt.com, claude.ai, perplexity.ai, gemini …) and "Email & messages". It also maps Android in-app package names (`com.linkedin.android` → linkedin.com) and click IDs (`fbclid`, `gclid`, `li_fat_id` …) to sources. Tracking params are then stripped from the URL with `history.replaceState`.
- **"Quoted" event.** On landing, it reads the URL **text fragment** (`#:~:text=`) from the navigation entry and logs which sentence a search engine or AI deep-linked to. That's a clever way to see what an AI cited.
- **Privacy.** No cookies; no `set-cookie` header appeared in any captured response. Opt-out works via `?notrack` and `localStorage["dmcg:analytics-ignore"]`. It skips iframes and `navigator.webdriver`, and waits out `document.prerendering`.

## Other details

- **Vercel Toolbar hook.** The Turbopack runtime contains the Vercel Live feedback loader (`https://vercel.live/_next-live/feedback/feedback.js`, `data-explicit-opt-in`). It didn't load on production in my tests. **[inferred]** It's for preview deployments only.
- **Security headers.** Only HSTS is set (`max-age=63072000`). There's no CSP, `X-Frame-Options`, `Referrer-Policy` or `Permissions-Policy` on HTML responses.
- **Theme meta.** `theme-color: #FFFFFF` is paired with `color-scheme: dark`, which contradicts the light UI (see [06](06-perf-seo-a11y.md)).
- **Legacy bundle.** A `nomodule` polyfill chunk (`0cz1d0mv5g_q7.js`, 112 KB raw) is referenced for old browsers. Modern browsers skip it.
