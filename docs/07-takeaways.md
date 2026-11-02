# 07: Takeaways

## Worth learning from

1. **Restraint as the brand.**
   - One typeface (PP Neue Montreal), effectively one text size (14px, +0.04em tracking), neutral grounds, and no headline on the home page.
   - The work, shown as floating cut-out objects, carries all the visual weight.
   - That makes the site feel like a gallery or shop window rather than an agency pitch. The lesson is about *subtraction*: every element left on screen is deliberate.
2. **One signature interaction, engineered properly.**
   - Opening a project pours all the thumbnails into a dock with a custom genie warp (smoothstep, per-column delay, SVG clip paths and Motion values).
   - The effect is memorable, and it also does a job: the dock becomes the project navigator, so you never need "next project" links.
   - A single great transition is worth more than ten scroll effects.
3. **A small, consistent motion vocabulary.**
   - Nearly everything uses *blur-to-sharp plus fade* on one easing curve, `cubic-bezier(.22,1,.36,1)`.
   - The intro stagger is capped (`min(order, 4) * .14s`), so it never drags.
   - The case-study reveal queue waits for *loaded and in view* before revealing, with a 110ms rhythm and a 1.2s maximum wait. It's a clean pattern for avoiding half-loaded reveals.
4. **A CMS that controls design tokens, not just content.**
   - Type roles per breakpoint, per-project ground and ink colours, thumbnail placement, motion timing and even UI sound recipes all live in Sanity.
   - The designer can tune the site without a deploy.
   - Custom admin tools (thumbnail editor, typography preview, preview bridge) show the CMS was treated as a design tool.
5. **Synthesised UI sound.** Short Web Audio "recipes" (tick, tap, soft, chime) are rendered with `OfflineAudioContext`, so there are no audio files. They're opt-out, persisted, off in Safari, and silent when the tab is hidden. It's a tasteful, low-cost layer of tactility.
6. **Built for AI and answer engines.**
   - `llms.txt` and `llms-full.txt`, `.md` twins for every page, and `Accept: text/markdown` negotiation with a canonical `Link` header and a token-count header.
   - The analytics buckets AI-assistant referrers and logs `#:~:text=` deep-link quotes.
   - This is ahead of most studio sites, and it's cheap to copy.
7. **Privacy-respecting, decision-oriented analytics.**
   - Cookieless and first-party, with no third-party scripts.
   - It still measures what matters for a portfolio: hover dwell per project, read depth, outbound clicks, email copies, referrer *category* (including design galleries) and Web Vitals.
8. **Commercial honesty.** Published starting fees (from $30k, $40k and $45k), a flat-fee model and explicit credit for collaborators. It pre-qualifies leads and builds trust.
9. **Craft details.** Metric-matched font fallback (CLS of about 0), progressive-blur soft edges, a `plus-lighter` crossfade so there's no brightness dip on hover, squircles via `corner-shape: superellipse()` with a fallback multiplier, a yellow `::selection`, and `<noscript>` visibility fallbacks.

## What's weak

1. **Everything is inlined on every page.** About 540 KB of RSC data (172 KB Brotli) ships with every HTML response, and HTML is never edge-cached. A search visitor landing on one case study downloads the whole site's content.
2. **Heavy JS for a gallery.** 355 KB Brotli of JS, on a React *canary* build in production.
3. **Over-eager image loading.** Eight preloaded and eager hero images, at `q=90` WebP with no AVIF. Mobile LCP was 3.5 s even unthrottled.
4. **Semantics.**
   - No `h1` on home, About or Catalog, and an empty `h1` on the incubator.
   - About section titles aren't headings.
   - *Every* case-study image has `alt=""`.
   - For a design portfolio, the work itself is inaccessible to screen readers and to image search.
5. **Contrast and size.** Quiet text at 2.17:1, Archiv body at 3.53:1, 12px body text on mobile, and `vw`-sized catalog text that ignores user font settings.
6. **Soft 404s.** Unknown URLs redirect (`307`) to the home page instead of returning a 404.
7. **Discoverability of work.** The home page has no visible project names. That's charming, but first-time visitors on touch devices (no hover) see eight unlabelled objects. The incubator also has no header link.
8. **Small inconsistencies.** `meta color-scheme="dark"` on a light site, `http://` social links, no `lastmod` in the sitemap, and no CSP or other security headers.

## How to build a comparable (original) site

The aim is to take the *principles* (restraint, one signature transition, tokens in the CMS, AI-readable content), not the look. Don't reuse their typeface pairing, cut-out-column layout, dock or genie effect, copy or sound recipes. Invent your own signature.

### Stack

| Need | Suggested choice | Why |
|---|---|---|
| Framework | Next.js (App Router, **stable** release) or Astro with React islands | Static-first; Astro ships less JS for a mostly static gallery |
| Rendering | Static generation + on-demand revalidation (Sanity webhook → `revalidateTag`) | Edge-cached HTML instead of `no-store` |
| CMS | Sanity (or Payload) with a **design-tokens document**: type roles, per-project ground and ink, motion timing | Lets the designer tune without deploys, as DMCG does |
| Data per page | Fetch only the current view's content; keep a light project index (slug, title, thumbnail) for instant navigation; prefetch neighbours on hover | Avoids the 540 KB-everywhere problem |
| Motion | Motion (or `motion/mini` for size), CSS transitions for reveals, the View Transitions API for cross-view morphs where supported | One library, plus native features |
| Images and video | `next/image` with `formats: ['image/avif','image/webp']`, `quality: 75–80`; preload **only** the LCP image; Mux or Cloudinary for adaptive video with a poster; HEVC-alpha + WebM-alpha only where transparency is needed | |
| Analytics | Umami, Plausible or a tiny self-hosted collector, proxied first-party; custom events for hover dwell, read depth and contact | |
| AI readability | `llms.txt`, `llms-full.txt`, `.md` routes or `Accept: text/markdown` via middleware, JSON-LD `CreativeWork` per project | Cheap and future-proof |

### Build plan

1. **Define the system first.**
   - Pick a typeface with a licence that allows the web.
   - Write 4–6 type roles as CSS variables and choose one easing curve and three durations.
   - Pick a neutral ground plus per-project tint tokens. Check every ground/ink pair with a contrast tool before shipping (aim for 4.5:1 or better).
2. **Choose one signature transition** that also solves a navigation problem. A few original directions:
   - project cards that fold into a timeline scrubber;
   - a shared-element morph from thumbnail to hero using View Transitions;
   - a stack that fans out into an index.

   Prototype it in isolation, give it a reduced-motion variant that keeps the spatial logic, and cap any stagger.
3. **Semantic skeleton before polish.**
   - Give every view an `h1`, even a visually hidden one, and make section titles `h2`.
   - Write meaningful `alt` for every project image (it can be a CMS field that's required to publish).
   - Return a real 404 status.
4. **Performance budget.** Aim for under 150 KB of JS (Brotli) on first load, one preloaded image, AVIF, lazy video behind posters and edge-cached HTML. Test with Lighthouse mobile throttling, not just a fast connection.
5. **Content.** Write case studies as a series of design decisions with their reasons, credit collaborators, and consider publishing starting fees if the business model suits it.
6. **Instrumentation.** Use cookieless events for hover dwell, read depth, contact actions and referrer category, and include an AI-assistant bucket.
7. **Optional delight.** Add subtle UI sound, opt-in or easy to mute, and silent by default when the user prefers reduced motion. Use original synth parameters or recorded foley.

### Effort estimate **[inferred]**

For a single designer-developer working from an existing design:
- the system and CMS schema take about 1 week;
- the signature transition takes 1–2 weeks of prototyping;
- views, case-study blocks and the catalog take 2–3 weeks;
- performance, a11y and SEO hardening plus the LLM routes take about 1 week.

The genie-style dock alone represents most of the craft risk. Budget for it, or choose a simpler signature.
