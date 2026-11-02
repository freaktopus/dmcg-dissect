# 05: Content and UX

**Sources:** the rendered pages (screenshots in `../screenshots/`), the server HTML, and the site's own Markdown mirror (`/llms-full.txt`). Copy is quoted only in short excerpts.

## Information architecture

```
/ (Projects tray) ──click──▶ /work/<slug> (case study, opened in place; dock keeps all 8 projects one click away)
 │
 ├─ About (overlay)   ── /about
 ├─ Contact (copy-email pill; no page)
 ├─ Projects ⇄ Catalog (view switcher)   ── /archive  (106 works by type, as a node tree or grid)
 └─ (no nav link) Think With Your Eyes   ── /incubator  (reached from About / case-study links)
```

**Navigation model.** It's flat and spatial. There's no footer menu, no breadcrumb, and no "next project" link at the end of a case study. Instead the **dock** at top centre always shows all eight projects, so moving between them is a dock click. The Projects/Catalog switcher sits at the top right. The sound toggle sits at the far right.

**Mobile (≤900px).** The header collapses to a hamburger, the centred lockup, and a "projects" icon that opens the dock as a tray (see `case-archiv-mobile.png`). The home becomes a normal scrolling column of posters with no hover video.

## Page by page

### Home `/` (`home-desktop.png`, `home-mobile.png`)

- **What's on screen:** the header, plus two corner captions: "Brand & software design" at bottom left and "Made in New York" at bottom right.
- **The tray:** a single vertical column of eight floating cut-out artefacts, hand-placed and sized in the CMS. They are a scooter, a phone, a Tolan card, a chrome knot, the Groth wordmark, a black Americana card, a ring and the Evara device.
- **No visible text:** the cards carry no project names or captions. Names appear only as `aria-label`s and in the dock.
- **Effect:** it works like an object gallery or shop window, with the curiosity of "what is that?" as the hook. Hover plays a short loop.

### Case study `/work/<slug>` (`case-tolan-desktop.png`, `transition-3-case-open.jpg`)

The structure, from the Sanity block types:

1. An `h1` with the project name. It's in the DOM, but visually the hero media leads.
2. A hero: a full-width rounded image, video or interactive embed.
3. A short intro, 2–3 paragraphs at 15/22 in a narrow column (~530px).
4. Credits, where relevant ("Original character design by Eran Hilleli and in-house creative by Lucas Zanotto").
5. Alternating sections:
   - full images or videos;
   - media pairs or triples;
   - text columns;
   - "canvas" collages;
   - a footer canvas.
6. A footer: Twitter, LinkedIn, and an "Email" copy button; then the lockup, "Made in …" and "© 2015-2026 Studio DMCG Inc".

**Writing pattern.** Each section explains *one design decision* and its rationale. For example, on Tolan: "What would happen if the Tolan logo was dropped into their world? Suddenly it's a physical object." The disciplines (Brand / Web / Software / Prototyping) are listed in metadata rather than on screen.

**Credit hygiene.** Case studies say what DMCG did *not* do ("The founders had developed the original logo…") and credit collaborators by name. That is good practice and builds trust.

### About `/about` (`about-desktop.png`)

- **Layout:** an overlay panel of plain paragraphs over a soft radial glow.
- **Sections:**
  - intro positioning;
  - **Approach**;
  - **Technology** ("uses AI and builds its own tools…");
  - a video;
  - **Working Together**, with three disciplines and **published starting fees** ($40k / $30k / $45k) plus the flat-fee model;
  - a long bio of David McGillivray.
- **Headings:** the section labels are bold text, not heading elements.

### Catalog `/archive` (`catalog-desktop.png`)

- **Layout:** a left-to-right tree. "Catalog 106" branches to Logo 24, Digital 60 and Physical 22. The selected branch fans out with hairline curves to a scatter of thumbnail cards for every logo or piece.
- **Toggle:** a grid/tree switch sits at bottom centre.
- **What it shows:** breadth (24 brands), at a glance, without a case study for each one.

### Incubator `/incubator` (`incubator-desktop.png`)

- **Header:** the hand-lettered "THINK WITH YOUR EYES" wordmark, then a one-sentence intro.
- **Rail:** a horizontal row of four cards: Corners, Archiv, Hedroom and Soba. Each has an image, a type, a green status dot with status text ("Open Since 2023", "Beta on Testflight", "Public Beta") and a link ("More Information ↗", "View Casestudy ↗", "Download ↗").

## Copy tone

- **Register.** First-person-plural is avoided. The studio is "The Design Office". The voice is calm, British and understated, with phrasing like "a relatively organic way of working", "less time spent on process and more time spent designing" and "before anyone moves a pixel".
- **No marketing superlatives** and no client logos wall. There are no testimonials and no awards strip.
- **Microcopy** is terse: "Copy", "Copied", "Sounds on", "Drag to resize · double-click to reset".
- **Descriptor:** the studio's own one-liner is "Brand & software design" (corner caption). The positioning line is "building coherent worlds for people inventing new things".

## Calls to action and conversion funnel

| Step | Mechanism | Evidence |
|---|---|---|
| Discover | Search, social, **design galleries**, **AI assistants** (tracked as separate referrer buckets) | analytics regexes in [02](02-tech-stack.md) |
| Browse | Hover loops (tracked after 1s dwell as `hover:<slug>`), open a case study (`open:landing/link/back`) | |
| Read | Scroll depth `read:10…100` on case studies and About | |
| Qualify | About page fees and flat-fee model filter out low-budget leads before contact | |
| Contact | **Copy email** (`office@dmcg.co`) from the header pill or a case-study footer. It's tracked as `email:<location>` and falls back to `window.location.href = mailto:` only if the clipboard write fails. There's no form and no booking link. | `aria-label="Contact: copy office@dmcg.co"`; `copy:async()=>{if((0,s.track)(\`email:${i}\`),!await u(e)){window.location.href=\`mailto:${e}\`…` |

**[inferred] Assessment.**

- The funnel is deliberately low-volume and high-intent. Published prices and an email-only contact suit a solo senior practice that wants a few large engagements.
- The weak point is the **copy-to-clipboard contact**. It's elegant, and it's measured. But on mobile, and for visitors who expect a link to open their mail app, an explicit "open in mail" option next to "Copy" would remove a step.
- There is no CTA at the end of a case study beyond the footer's email button.
