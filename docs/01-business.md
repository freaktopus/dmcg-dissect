# 01: Business context

**Scope:** who runs dmcg.co, what they sell, who it's for, how they position themselves, and the full page inventory.
**Method:** first-party sources (the site's own `llms.txt`, `llms-full.txt`, JSON-LD and page copy, fetched 2 Nov 2026) plus a handful of independent press sources. Each claim is tagged **[site]** (stated by dmcg.co), **[press]** (independent source, linked), or **[inferred]** (my reading).

## Who

- **Name:** "The Design Office of David McGillivray". The legal footer reads "© 2015-2026 Studio DMCG Inc" **[site]**. A 2019 Lovers Magazine interview also lists him as "Creative Director at Studio DMCG" ([spaces.is/loversmagazine](https://spaces.is/loversmagazine/interviews/david-mcgillivray), per search snippet; the page itself returned HTTP 500 when fetched) **[press]**.
- **Principal:** David McGillivray, British-born and trained at Brighton University. In 2011 an experimental iPad app he designed for Taschen won a D&AD New Blood Graphite Pencil, which led to a job at a New York startup the same year. He spent several years leading design in-house at startups and fashion brands, then went independent in 2015. He has been an adjunct professor at Parsons, teaching interaction design **[site, About]**.
- **Location:** "Made in New York" (homepage corner caption). He is "based between New York and the Catskills" **[site]**. Chronogram reports that he moved from Brooklyn to Livingston Manor (Catskills) full-time in 2023 ([Chronogram](https://www.chronogram.com/lifestyle/corners-livingston-manors-new-art-and-design-store-19730649/)) **[press]**.
- **Related ventures** **[site, About + Incubator]**:
  - co-founded the loungewear brand **Offhours** (2018);
  - co-hosts the design podcast **Works But Makes Noises** ([podscan listing](https://podscan.fm/podcasts/works-but-makes-noises));
  - runs **Corners**, an art and design shop at 49 Main St, Livingston Manor, opened Labor Day weekend 2023, which sells ready-to-hang framed art, books and stationery. The building was renovated with architect Michael Groth, which links to the "Groth" case study **[press: Chronogram]**.

## What they sell

The About page publishes **starting fees**, which is unusual for a studio site **[site]**:

| Discipline | Description (site copy, paraphrased) | Starting fee |
|---|---|---|
| Brand | Identity and visual systems for new and evolving ventures | from $40k |
| Web | Digital experiences that combine brand, story and product | from $30k |
| Software | Product design and prototyping with brand coherence | from $45k |

The commercial model is a **flat fee with a fixed scope and timeframe agreed upfront**, and only a few engagements run at once. David leads every project and brings in specialist collaborators as needed **[site]**.

The studio also says it uses **AI tooling**: "AI-native workflows use agentic tools and custom software… Original thinking, creative direction and judgment remain human" **[site, llms.txt]**. The site itself backs this up. It has a CMS-driven typography and sound-design system, custom admin editors and an LLM-oriented Markdown mirror (see [02](02-tech-stack.md)).

## Audience and positioning

- **Stated audience:** "Founders seeking a senior brand designer or hands-on creative director for a technology company, or one design partner across identity, website and digital product" **[site, llms.txt]**.
- **Positioning:** an independent, designer-led senior practice rather than an agency. The pitch is direct access to the principal, the ability to give unfamiliar technology a coherent form, and fixed fees.
- **Proof points:** the featured clients are venture-backed hardware and AI startups. That press coverage exists independently is my own reading **[inferred]**:
  - **Infinite Machine:** Brooklyn EV maker of the P1 seated scooter (~$10k) and the cheaper Olto, with a $9.3M seed led by a16z ([TechSpot](https://www.techspot.com/news/109623-infinite-machine-cybertruck-like-p1-escooter-launching-soon.html), [Infinite Machine newsroom](https://infinitemachine.com/newsroom/infinite-machine-raises-9-3m-in-seed-round-led-by-a16z-to-fuel-non-car-revolution)) **[press]**.
  - **Tolan:** an AI companion app from Portola, launched on iOS in Feb 2025. Portola raised a $20M Series A led by Khosla in July 2025 ([GeekWire](https://www.geekwire.com/2025/ai-companionship-app-tolan-raises-20m-to-help-more-people-grow-with-a-virtual-alien-friend/), [Fast Company](https://www.fastcompany.com/91283982/tolan-adorable-alien-ai-companion)) **[press]**.
  - **Sandbar:** maker of the Stream Ring, a voice-note smart ring from ex-Meta founders ([Wareable](https://www.wareable.com/wearable-tech/sandbar-ai-smart-stream-ring-voice-notes-announcement), [UC Today](https://www.uctoday.com/devices-workspace-tech/sandbar-ai-voice-note-taking-ring/)) **[press]**.
  - **Evara:** a wellness hardware startup founded by ex-SpaceX engineer Courtney Wright **[site]**.
- **Breadth signal:** the Catalog counts "106 pieces of work from 24 projects" across Logo, Digital (Web 48, App 12) and Physical (Print 14, Objects 8) **[site]**. Brands there that have no case study include Nue Co, Highnote, Universe, Format, Momentous, Clever, Usual, Petal, Afina and CPGD.
- **Incubator ("Think With Your Eyes"):** the studio's in-house ventures **[site]**:
  - Corners (retail store);
  - Archiv (iOS app, TestFlight beta);
  - Hedroom (web app, public beta, at hedroom.fm);
  - Soba (macOS Markdown notes app with AI tools, sobanotes.app).

  **[inferred]** The incubator serves two purposes. It shows that the studio builds as well as designs, and it fills the portfolio with software projects it fully controls.

## Sitemap and page inventory

Sources:
- `robots.txt`: `Allow: /`, `Disallow: /CMS`, `Disallow: /api/`, plus a comment pointing AI tools at `/llms.txt`.
- `sitemap.xml`: 12 URLs, with no `lastmod`.
- Navigation: About, Contact, Projects, Catalog, and the sound toggle.

| URL | Title tag | What it is |
|---|---|---|
| `/` | The Design Office of David McGillivray | Project "tray" of 8 cut-out thumbnails, header and corner captions |
| `/work/infinitemachine` | Infinite Machine Web Design by David McGillivray | Case study |
| `/work/archiv` | Archiv iOS App Design by David McGillivray | Case study + interactive embed |
| `/work/tolan` | Tolan Brand Design by David McGillivray | Case study |
| `/work/hedroom` | Hedroom Platform Design by David McGillivray | Case study + embeds (local hero + 3 live hedroom.fm artifacts) |
| `/work/groth` | Groth Brand Design by David McGillivray | Case study |
| `/work/americana` | Americana Brand and App Design by David McGillivray | Case study |
| `/work/sandbar` | Sandbar Stream Ring Web Design by David McGillivray | Case study |
| `/work/evara` | Evara Brand Design by David McGillivray | Case study |
| `/about` | About — The Design Office of David McGillivray | Overlay panel: intro, Approach, Technology, Working Together (fees), bio |
| `/archive` | Catalog — The Design Office of David McGillivray | Node-tree "catalog" of 106 works |
| `/incubator` | Think With Your Eyes — … | Horizontal card rail of 4 ventures |

Other routes I observed but which aren't in the sitemap:

- `/llms.txt`, `/llms-full.txt` (~50 KB, the whole site as Markdown), and `<page>.md` for every page. These are served by an internal rewrite to `/md/[[...path]]`.
- `/CMS`, an embedded Sanity Studio (`x-matched-path: /CMS/[[...tool]]`, HTTP 200).
- `/api/v`, the first-party analytics collector.
- `/embeds/archiv-hero/`, `/embeds/hedroom-hero/` and `/embed-posters/*`, which are static interactive pieces.
- Unknown paths return **307 → `/?from=<path>`**, not a 404 (see [06](06-perf-seo-a11y.md)).
