# dmcg.co: site dissection

An end-to-end teardown of **[dmcg.co](https://dmcg.co/)**, the portfolio of *The Design Office of David McGillivray* (Studio DMCG Inc, New York). It covers the business, stack, design system, motion, content, performance, SEO and accessibility. Analysis date: **2 Nov 2026** (Vercel deployment `dpl_9zu448T8ZzHPDdU18AFsr792WwPY`).

Findings are tagged as **verified** (from headers, HTML, bundles or rendered output) or **[inferred]**. Code excerpts are short quotes kept as evidence. No third-party bundles, images or copy are stored in tracked files.

## Executive summary

- **Who and what.** A one-person-led senior studio doing brand, web and software for venture-backed tech founders: Infinite Machine (EV scooters), Tolan (AI companion), Sandbar (voice ring), Evara, and others. It publishes **starting fees** (Brand from $40k, Web from $30k, Software from $45k) and works on flat fees. An in-house incubator, "Think With Your Eyes", runs Archiv, Hedroom, Soba and the Corners store.
- **Stack.**
  - **Next.js 16.2.12** (App Router, **Turbopack** build), **React 19.3 canary**, on **Vercel**;
  - **Sanity** CMS with an embedded Studio at `/CMS`, with assets mirrored to **Vercel Blob**;
  - **Motion** for animation and **Web Audio** for synthesised UI sounds;
  - a custom cookieless analytics endpoint (`/api/v`, Umami-style payload **[inferred]**).
  - No GSAP, Lenis, WebGL or third-party trackers.
- **Architecture.** One catch-all route (`/[[...view]]`) serves every page as a "view" of a single-page portfolio. The whole site's content (~540 KB of RSC data) is inlined in every HTML response, which is why switching views is instant and the first load is heavy.
- **Design.**
  - One typeface: PP Neue Montreal, effectively at 14px with +0.04em tracking.
  - White and warm-neutral grounds, with a CMS-set tint per project.
  - Cut-out product renders floating in a hand-placed column; squircle pills; progressive-blur edges.
  - Hierarchy comes from space and motion rather than type size.
- **Signature motion.** Clicking a project pours all thumbnails into a top-centre **dock** with a custom macOS-style **genie** warp (smoothstep maths, SVG clip paths, Motion values). Elsewhere the vocabulary is consistently *blur-to-sharp* on `cubic-bezier(.22,1,.36,1)`. Case-study reveals are queued on "loaded and in view" (110ms stagger, 1.2s max wait). Reduced motion is respected throughout.
- **Standouts.** **AI readiness**: `llms.txt`, `llms-full.txt`, `.md` twins of every page, `Accept: text/markdown` negotiation and an `x-markdown-tokens` header. Analytics buckets AI-assistant and design-gallery referrers and logs `#:~:text=` deep-link quotes. Design tokens, motion timing and sound recipes all live in the CMS.
- **Weaknesses.**
  - Heavy HTML (172 KB br) and JS (355 KB br) on every page, with HTML never edge-cached.
  - Eight eager or preloaded hero images; mobile LCP ≈3.5 s even unthrottled.
  - **No `h1` on home, About or Catalog**, and every case-study image has `alt=""`.
  - Contrast failures (2.17:1 and 3.53:1).
  - Soft 404s (`307 → /?from=`), and a `color-scheme: dark` meta on a light site.

## Contents

| Doc | Covers |
|---|---|
| [docs/01-business.md](docs/01-business.md) | Who DMCG is, offer and fees, audience, positioning, sources, sitemap and page inventory |
| [docs/02-tech-stack.md](docs/02-tech-stack.md) | Hosting, framework versions, routing, Sanity setup, media pipeline, analytics internals |
| [docs/03-design-system.md](docs/03-design-system.md) | Colour (hex), typography roles, spacing, breakpoints, components, imagery |
| [docs/04-motion.md](docs/04-motion.md) | Intro, hover video, genie dock, scroll reveal, springs, soft edges, UI sound, embeds, reduced motion |
| [docs/05-content-ux.md](docs/05-content-ux.md) | IA, page-by-page structure, copy tone, CTAs and funnel |
| [docs/06-perf-seo-a11y.md](docs/06-perf-seo-a11y.md) | Measured weights and timings, SEO and AI readiness, accessibility audit, contrast ratios |
| [docs/07-takeaways.md](docs/07-takeaways.md) | What to learn, what's weak, how to build a comparable *original* site |

## Screenshots (`screenshots/`, ~1.5 MB total)

| File | What |
|---|---|
| `home-desktop.png` / `home-mobile.png` | Home tray at 1440×900 and 390×844 |
| `transition-1-genie-120ms.jpg` → `transition-2-docked-370ms.jpg` → `transition-3-case-open.jpg` | The project-open genie/dock transition, captured over CDP |
| `case-tolan-desktop.png`, `case-archiv-mobile.png` | Case studies (desktop, mobile) |
| `about-desktop.png`, `catalog-desktop.png`, `incubator-desktop.png` | Other views |

## Tools (`tools/`)

Each script reads saved files as data or drives a sandboxed headless browser. Nothing in `raw/` is ever executed. Run Python with `-I`.

| Script | Purpose |
|---|---|
| `fetch_site.sh` | Politely fetch pages, robots, sitemap, llms files and first-party JS/CSS into `raw/` |
| `html_inventory.py` | Meta/OG/JSON-LD, scripts, images (alt/lazy), headings, ARIA, class frequency for one HTML file |
| `fingerprint.py` | Grep bundles for library signatures (GSAP, Lenis, Three, Motion, Sanity, analytics…) with context excerpts |
| `css_tokens.py` | Custom properties, colours, fonts, sizes, media queries, keyframes, easings, modern-CSS feature counts |
| `css_rules.py` | Print CSS rules matching a keyword (brace-aware, includes @media context) |
| `contrast.py` | WCAG contrast ratio for fg:bg hex pairs |
| `cdp_netlog.mjs` | Load a URL in headless Chromium via CDP; record requests, bytes, console, FCP/LCP/CLS |
| `cdp_frames.mjs` | Script hover → click → settle on the home page and capture transition frames |

Reproduce, assuming `chromium` and Node ≥ 22:

```sh
tools/fetch_site.sh
python3 -I tools/fingerprint.py raw/js
python3 -I tools/css_tokens.py raw/css/*.css
chromium --headless=new --remote-debugging-port=9333 --user-data-dir=/tmp/prof about:blank &
node tools/cdp_netlog.mjs 9333 https://dmcg.co/ 1440 900 0 raw/misc/net-home.json 0
```

## Method notes and gaps

- **Browser.** The Claude-in-Chrome and built-in browser tools weren't available in this session. Rendering, screenshots, network capture and the transition frames came from local headless Chromium over CDP instead. That covers what those tools would have shown, but not the real-device Safari or iOS behaviour: the `appleSrc` video path and the Safari-disabled sound.
- **Timing caveats.** Timings are unthrottled, from India via Vercel's `bom1` edge, so they aren't Lighthouse lab scores. Lighthouse grades in doc 06 are estimates.
- **What I didn't touch.** I didn't log in to or crawl `/CMS` or `/api/` (disallowed in robots.txt). About a dozen headless page loads did send the site's normal `/api/v` analytics beacons, as any visit would. Use `?notrack=1` to avoid that when reproducing.
- **Raw material.** Bulk HTML, JS, CSS and network logs are in `raw/` (gitignored).
