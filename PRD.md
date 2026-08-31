# Jonathan Gong — Personal Website PRD

- **Project:** `jagong-cmu/personal-website` (public)
- **Owner:** Jonathan Gong
- **Status:** Visual direction approved (§9, decisions 27–30). The approved static preview
  is landed at the repository root and is **live in production on `jonathangong.com`**; the
  Next.js build in §7 has not started. `README.md` covers the preview.
- **Date:** 2026-08-18, last revised 2026-08-25
- **Source:** Derived from a four-round requirements interview. Every decision below traces to the log in §13.

---

## 1. Purpose

A personal site that does two jobs at once, in a deliberate order.

1. **Convince a recruiter in thirty seconds.** A hiring manager or recruiter lands, sees who Jonathan is, where he's worked, what he's built, and what he's won, and comes away willing to make contact.
2. **Show the person behind the résumé.** Anyone who stays longer gets a photographic, chronological account of his life that no résumé can carry.

The structural principle that resolves the tension between those two jobs: **front door and deep room.** The homepage is a tight, professional, scannable front door that could sit beside any strong CMU portfolio without apology. The personal material lives in rooms a visitor walks into on purpose. The two never compete for the same screen.

## 2. Audience

| Priority | Audience | What they need |
|---|---|---|
| 1 | Recruiters, hiring managers | Credibility fast: roles, outcomes, proof of ability, a way to make contact |
| 2 | Interviewers preparing for a conversation | Depth on specific projects, something human to open with |
| 3 | Peers, friends, future self | The Journey; the writing |

## 3. Non-goals

Explicitly out of scope. Each was considered and declined.

- **No downloadable résumé PDF.** Owner's decision. Accepted consequence: application flows that require a file upload get nothing from this site.
- **No CMS, no database.** All content is files in the repository.
- **No admin editing of work or projects.** Those are file edits. Only blog and Journey — the content that grows without bound — earn a management interface.
- **No auto-sync of projects from GitHub.** Curation beats completeness; the public repos include scratch work that would weaken the page.
- **No showcase-tier motion.** No parallax, no custom cursor, no animated hero.
- **No contact form, analytics dashboard, or other admin operations in v1.** Each is a separate future project.

## 4. Information architecture

**The front door is a tabbed shell, not a long scroll.** One persistent header — name,
one line, links — with a row of plain text tabs beneath it. Clicking a tab swaps the
content area in place. Each tab is a real route so it can be linked and bookmarked.

```
/                 Front door shell. Opens on About.
  /about          About — four short paragraphs
  /work           Work experience
  /projects       Projects
/journey          Era-chaptered photographic timeline  [noindexed]
/blog             Post index → /blog/[slug]
/admin            Authenticated content management  [noindexed, nofollow]
```

Only ONE section is on screen at a time. Nothing stacks. A visitor who wants work
experience clicks Work and sees work experience on an otherwise empty page.

Journey and Blog sit in the same tab row but are full destinations rather than panels,
because they are long-form and scroll on their own.

## 5. Content model

All content is MDX or structured data files committed to the repository. There is no database anywhere in this system.

### 5.1 Work experience — file-edited
Company, role, date range, and one to two sentences of prose describing the work. No bullet
lists and no required metrics: the entry is a short qualitative description, and an entry with
little to say is allowed to be short rather than padded. This rewrites the earlier "two to three
lines written as outcomes with concrete numbers" rule on the owner's explicit instruction of
2026-08-20 (decision 35), which also removed the numbers already on the page.

An entry may also carry the **company's own logo** beside the company name, in full colour
(§9's 2026-08-21 exception, decision 41). It is optional by construction: a company whose
logo URL the owner has not confirmed carries none, and decision 30's no-guessed-URLs rule
applies to a logo source exactly as it does to a link. The mark sits in a fixed-width column
reserved on the entry, so every company name shares one left edge and an entry with no mark
holds the same indent with its slot simply empty (decision 42). That empty slot is the correct
outcome and is never filled with a placeholder, an initial, or a generic glyph. The column is
40px wide on the owner's instruction of 2026-08-24 (decision 44), which is why the entry is a
two-column grid rather than an image inline in the title.

### 5.2 Projects — file-edited, hand-curated
Name, one-line summary, description, tech, links (repo, live). The description is prose with no
bullet lists and no required metrics (decision 35), condensed to **one sentence** on 2026-08-25
so it reads as a hover caption (decision 50) — that is where Projects now departs from §5.1's
one-to-two-sentence form, and only in length.
The set is curated and settled at **three** projects — ManuAI, PatientScope AI, and Chalk — after
the owner removed Poker Bot and the C0 Virtual Machine on 2026-08-25 (decision 46). That supersedes
both the earlier guess at which public repositories would be featured and the five-project set the
root static preview shipped with. An entry carries its own award mention where one applies, which is
where the confirmed award now lives (decision 39).

A Projects entry is a **rounded image card** (§9's 2026-08-25 exception, decisions 45, 48–52
and 53). At rest the card is the screenshot and nothing else: the image fills it edge to edge
and the card's `border-radius` clips it, with a hairline border around the whole thing and
nothing else drawn — no shadow, no gradient, no fill, no motion. The title, meta, description,
and any `.entry-links` row live in an **overlay revealed on hover**, over a flat translucent
white scrim.

The reveal is not hover-only, because a visitor who cannot hover must still learn what all
three projects are:

- **Keyboard.** `:focus-within` opens the overlay, so tabbing to a card reveals its
  description. A card with no focusable descendant — one with no confirmed link — carries
  `tabindex="0"` so it still takes a tab stop.
- **Touch.** The permanent layout is the **default** and the overlay is the enhancement. A
  card only withholds its text where `@media (hover: hover) and (pointer: fine) and
  (min-width: 768px)` matches; on every touch device at any width, and in any hovering
  window below the floor, the title, meta, description, and links sit permanently beneath
  the image, unscrimmed. Nothing is tap-to-reveal. The gate is capability-first because
  width alone answered the wrong question — an iPad reports a wide viewport and no hover —
  and the 768px floor is measured, not chosen for tidiness (decision 53).
- **Screen readers.** The title and description are real markup in the DOM at all times,
  hidden only visually (`opacity`), never `display: none`, `visibility: hidden`,
  `aria-hidden`, CSS `content`, or script. A screen reader reads all three with no
  interaction.

That hidden text is therefore live markup with a live interactive state behind it, not
leftovers — do not read it as dead and delete it.

Each description is **one sentence**, tight enough to read as a hover caption; the
`.entry-meta` date-and-stack line is already short and sits in the overlay with the title.
Condensing means cutting, never embellishing: no capability, metric, or claim is added that
the longer prose did not already carry, and ManuAI's 1st-place hackathon result survives the
cut because it is the strongest credential on the page (decision 50).

The cards lay out **one per row at full measure**, stacked with the panel's 24px rhythm.
Three across was measured and rejected: each image rendered about 234x97 and was unreadable,
which defeats the point of showing an image at all (decision 51).

The image convention:

- The screenshot lives in `projects/` at the repository root, committed and referenced
  relatively. Zero external requests is not relaxed for it: a project's own site is never
  hotlinked and no thumbnail is fetched from a third party. A YouTube destination is a plain
  `<a href>` and never an embedded player or an iframe.
- It is **stripped of embedded metadata like every other committed image** (§7.3, §8,
  decision 33) and carries explicit `width`/`height` attributes so the cards do not reflow
  as the images load.
- All the images share **one aspect ratio and one pixel size** so the cards read as the same
  kind of object down the column. Nothing is letterboxed or distorted to reach it: an image
  that does not fit the ratio is re-cropped, never stretched.
- Each `<img>` carries **`loading="lazy"`**. The three screenshots total 762KB and the
  Projects panel is `display: none` until its tab is opened, which does not by itself stop
  an `<img src>` from being fetched; lazy-loading defers them until the panel is shown, so a
  visitor who never opens Projects never pays for them (decision 54).
- Each `<img>` carries a **real `alt`** describing what the screenshot shows. This is the
  opposite of the Work logos, which carry `alt=""` because the company name repeats them as
  adjacent text; here the image says something the prose does not.
- The **whole card is the click target** for a project with a confirmed destination, but the
  visible link stays on the title text (decision 29) — the title's `<a>` stretches an empty
  `::after` over the card rather than the prose being wrapped in an anchor. A project with no
  confirmed destination has no anchor at all, so nothing in its card takes a pointer cursor or
  implies a click; its overlay still opens on hover and focus like the others. Decision 30's
  no-guessed-URLs rule governs which is which.

### 5.3 Blog — admin-managed
Frontmatter: title, slug, date, summary, draft flag, optional cover image. Body is MDX. **Ships empty.** Posts are occasional and go up when one is written; there is no post required at launch (decision 34).

### 5.4 Journey — admin-managed
Grouped into **eras** — chapters such as childhood, high school, each CMU year. Each entry carries:

- a **date range**, not a single date, so a season and a moment are both expressible
- a title and short narrative
- a **photo cluster** (the entry's reason for existing)
- an **entry type**, distinguishing personal moments from work/professional milestones

**Work experience also appears on the Journey**, styled as a visually distinct entry type. This is the central argument of the section: the internships and the hackathons and the family photographs are one life on one line. Work is still presented seriously and separately on the front door.

> **Open branch.** The precise visual and structural treatment of the Journey is deliberately unsettled — see §11.1.

## 6. Admin

Scope is content only: **blog posts and Journey entries.**

- Sign in with GitHub, restricted to the `jagong-cmu` account. No password exists anywhere in this system to be leaked, guessed, or reused.
- Create, edit, delete, and save drafts for both content types.
- Image upload with an automatic pipeline (§7.3).
- Publishing writes MDX and images back to the repository as a **single batched commit** via the GitHub API, then triggers a rebuild. A post is live roughly forty seconds after publish.

The consequence worth stating plainly: because content is committed to git, the site inherits free version history, free backups, free rollback, and content that stays readable and portable long after any framework decision made here has expired.

## 7. Technical architecture

### 7.1 Stack
Next.js (App Router) + MDX + Tailwind, deployed on Vercel. Chosen over Astro because the admin is a genuine application with authentication, uploads, and an editor, and splitting it into a second deployment would double maintenance for an imperceptible gain. Next on Vercel is also the owner's existing, familiar path.

**Libraries, each with a reason:** Tailwind for the system; sharp for the build-time image
pipeline; MDX for content. That is the whole list for the public site.

**No animation library.** §9 forbids motion, so nothing like Motion/Framer is included.

**No web fonts and no typeface pairing.** §9 mandates a plain system font stack. This
supersedes the earlier "deliberate typeface pairing" line, which belonged to the voided
editorial direction.

**shadcn/ui is permitted in the ADMIN ONLY** — `/admin` is private and authenticated, and
§9 governs the public site's appearance, not a tool only the owner ever sees. It must not
leak into any public route.

Nothing is included for its own sake.

### 7.2 Storage
**Images live in the repository.** Vercel Blob is unavailable — the account is at its ceiling. Storing images in git collapses the system to one login, one store, one backup, one location, and removes every third-party free tier that could be revoked or exhausted.

Sizing: a web-optimized 1600px photo is roughly 200KB, so 300 photos is about 60MB and 1,000 is about 200MB. Comfortable well past the expected volume. **Watch item:** if the library grows past roughly 500 photos, revisit — build times climb with repository size, and Cloudflare R2 (10GB free, no egress charges) is the migration target.

### 7.3 Image pipeline
Runs at upload/build time, never per-request:

1. **Strip GPS and EXIF metadata — always, non-optional.** Phone photos embed exact coordinates; a public timeline of geotagged images published under a real name discloses where the owner lives and studies.
2. Generate fixed-width AVIF/WebP variants with sharp.
3. Serve as static files via plain `srcset`.

**Vercel's runtime image optimizer is never invoked.** It is metered on the Hobby plan, the account already carries eight projects, and a photo-heavy Journey is precisely the workload that would exhaust it. Pre-generating variants makes the quota structurally irrelevant.

### 7.4 Rendering
Static generation for all public routes. The admin is dynamic and authenticated.

### 7.5 Domain
`jonathangong.com` is registered and connected. Apex and `www` both resolve, and the static
preview (§11.1, `README.md`) serves from it through Vercel. Verified live 2026-08-20.

### 7.6 Discoverability metadata
Generated per route from the content, never hand-copied between pages:

1. **Per-page `description`, `author`, Open Graph, and Twitter card.** One description reused
   across the site is not acceptable — every public route describes itself. Next's route
   `metadata` export covers this natively, and `metadataBase` makes the `og:image` and
   `og:url` values absolute without repeating the domain.
2. **A per-page canonical URL on the apex.** Apex and `www` both serve 200 (§7.5), so without
   one, search engines may treat the two as duplicates of each other.
3. **`Person` structured data**, inline in the document so it costs no request: name, url,
   image, description, `alumniOf`, and `sameAs` listing **only destinations the owner has
   confirmed**. Decision 30's no-guessed-URLs rule governs structured data exactly as it
   governs links.
4. **`robots.txt` and `sitemap.xml`**, generated from the route list (`app/robots.ts`,
   `app/sitemap.ts`) rather than maintained by hand, so a new route cannot be silently
   omitted.
5. **Icons at the root convention paths** — `/favicon.ico` and `/apple-touch-icon.png`.
   Browsers and iOS request both with no markup at all, so the icon survives any change to
   the `<head>`. Next's `app/favicon.ico` convention covers the first; the second must sit in
   `public/`, because `app/apple-icon.*` is served as `/apple-icon` and would miss the path
   iOS actually asks for.

**The Journey is excluded from all of it and must stay crawlable.** It gets no canonical, no
Open Graph, no structured data, and no sitemap entry (§8). It is deliberately **not**
`Disallow`ed in `robots.txt`, and that is not an oversight to correct: a disallowed page is
never fetched, so its `noindex` is never read, and the bare URL can still be indexed from
inbound links. Blocking the crawler would make the exclusion weaker, not stronger.

## 8. Privacy and safety

- **The Journey is excluded from search engines**, so it will not surface in a search for the owner's name. It carries `noindex` and is left out of `sitemap.xml`; it is deliberately **not** `Disallow`ed in `robots.txt`, because a page that is never crawled never has its `noindex` read (§7.6, decision 38).
- **Accepted risk, and now a live condition rather than a future one.** The Journey is publicly reachable today at `jonathangong.com/journey.html`, carrying real photographs of the owner. `noindex` does not restrict anyone holding the URL, and scrapers routinely ignore it. There is **no per-entry private switch** in v1 — every uploaded photo is effectively public to anyone who has ever been sent the link. Adding per-entry visibility later is a retrofit; the option was offered and declined, and that decision stands.
- **GPS stripping is automatic and cannot be disabled.**
- The admin route is `noindex, nofollow` and gated on a single GitHub identity.

## 9. Visual direction

**Plain. White. Empty.** This section was rewritten on 2026-08-19 after the owner reviewed
three directions and rejected all three as "too cluttered, too fancy." The earlier
"editorial and warm" specification was wrong and is void. The nearest reference is
davidchung.io — the utilitarian one — not juliannth.com.

Hard rules, stated as prohibitions because that is how this direction fails:

- **Background is pure white** (`#FFFFFF`). Not cream, not sand, not off-white, not grey.
- **Typography is a plain system font stack.** No Google Fonts. No display face, no serif,
  no variable-width tricks, no letterspaced small caps. One family, two or three sizes.
- **Negative space is the design.** Generous margins and large gaps are the point; if a
  screen looks sparse, it is correct. Do not fill space.
  - **Exception, owner's instruction 2026-08-20:** the measure is `880px`, widened from
    `720px`, capped at `900px` because the About paragraph is the readability constraint.
    "Do not fill space" is set aside for the single `--measure` token and nothing else
    (decision 36). Do not narrow it back as a correction.
- **No decoration.** No cards, no shadows, no gradients, no borders-as-styling, no
  coloured panels, no badges, no signature motif.
  - **Exception, owner's instruction 2026-08-19:** social links are monochrome inline-SVG
    icons rather than the words "GitHub"/"LinkedIn"/"Email". Icons only for these three.
  - **Exception, owner's instruction 2026-08-19:** the headshot is a circular crop, framed
    on the head, and noticeably larger than a thumbnail. ~~This is the one shaped element
    on the site.~~ **Amended 2026-08-25, decision 49:** it is one of two, the other being
    the rounded Projects card below. That is a two-item list, not a loosening — every other
    element on the site is square, and `check-design-rules.py` permits those two selectors
    by name and nothing else.
  - **Exception, owner's instruction 2026-08-21:** a Work entry may carry the company's
    own logo beside the company name, in **full colour**. This sets aside "no badges" for
    those marks only. Firstmate escalated the conflict with this section and offered a
    monochrome treatment matching the `#111111` social icons; the owner reviewed it and
    chose full colour anyway, so brand colour in the Work panel is the instruction, not an
    oversight. Do not desaturate it, do not add a greyscale hover, and do not read it as
    licence to loosen this section anywhere else — the mark itself is the exception, and
    nothing may be drawn around it: no card, border, shadow, panel, or background. See
    decision 41. The marks sit in a shared fixed-width column so the company names keep one
    left edge; a ragged left edge is a defect, not the look of an absent mark (decision 42).
    **Exception extended, owner's instruction 2026-08-24:** that column is `40px`, roughly
    double the original 20px band, so the marks read at a deliberate size rather than as
    title ornament (decision 44). Nothing else about the exception moves — still full colour,
    still nothing drawn around the mark.
  - **Exception, owner's instruction 2026-08-25:** a **Projects** entry is a rounded image
    card. At rest it shows the project's screenshot and nothing else; the title, meta, and
    a one-sentence description sit in an overlay revealed on hover. This sets aside "no
    cards" and "no borders-as-styling" for the Projects panel only. Firstmate escalated the
    conflict with this section before anything was built and the owner chose cards anyway,
    then redirected the treatment to image-first with a hover reveal, so it is the
    instruction, not an oversight to correct back. What it grants is exactly a `1px` border
    in a light neutral (`--rule`, `#dcdcdc`), a `border-radius` on that card, a committed
    screenshot filling it edge to edge, and a **flat** translucent white scrim behind the
    revealed text. What it does not grant, inside the card or anywhere else: no shadow, no
    gradient — the scrim is flat by rule, and CI rejects a gradient one — no coloured or
    tinted panel, and **no motion**: the reveal is an instant opacity switch with no
    transition, no fade, and no transform, and the near-zero motion rule below was not
    relaxed for it. The radius makes the headshot no longer the only shaped element on the
    site, and `check-design-rules.py` now permits exactly those two selectors by name and
    nothing else. The panel carries a real interactive state, so its hidden text is live
    markup, not dead: the title and description are in the DOM at all times and only
    visually hidden, `:focus-within` opens the overlay for a keyboard user, and the overlay
    itself is offered only where the device proves it can hover on a card wide enough to
    hold it — `@media (hover: hover) and (pointer: fine) and (min-width: 768px)`. Everywhere
    else the same text is laid out permanently under the image, because a device that cannot
    hover cannot reach a reveal (decision 53). Work is
    untouched: it shares `.entry` and `.entry-title` with Projects, and every card rule is
    scoped to `[data-panel="projects"]` the way the Work logo column is scoped to
    `[data-panel="work"]`. See decisions 45, 48–52 and 53.
- **Colour is black text on white**, plus grey for metadata. At most one restrained accent,
  used for links only. No accent backgrounds.
  - **Exception, owner's instruction 2026-08-19:** the three social icons are near-black
    (`#111111`), not accent-coloured. The accent itself is untouched — body links stay
    visibly link-coloured. Do not "unify" the two: links that read as plain text are a
    usability regression, not a simplification.
  - **Exception, owner's instruction 2026-08-21:** company logos in the Work panel carry
    their own brand colours, which are therefore the only colours on the site outside black
    text, grey metadata, and the link accent. The exception is scoped to those marks: it
    grants no accent background, no new text colour, and nothing to any other element. See
    decision 41.
- **Motion is near-zero.** A plain instant tab switch is the default. Nothing animates in on
  scroll. This supersedes decision 24.
- **No theme toggle.** The site is white. Dark mode is dropped for now; this supersedes
  decisions 13 and 26 and is trivially re-addable if the owner asks.

The headshot appears in the front-door header as a **circle, cropped to the head**, at a
size that reads as a portrait rather than an avatar. No border, no shadow, no filter.

## 10. Delivery plan

**Two drops.** The public site is live and ships continuously from here; the admin is a
separate later drop. This supersedes the original single-deployment rule — captain's
instruction 2026-08-20, exercising the overrule the earlier plan explicitly held open
(decision 32).

| Stage | Output | State |
|---|---|---|
| 1 | Three visual directions — front door + one Journey screen, side by side | **Closed 2026-08-19.** Owner approved plain/white/empty; §9 is the result |
| 2 | Public site built: front door, /projects, /journey, /blog | **Deployed as the static preview**, on `jonathangong.com`, and shipping continuously. The Next.js build has not started |
| 3 | Admin built: GitHub auth, editor, image pipeline, commit layer | **Not started.** Now its own drop, with no gate on the public site |
| 4 | Real content in, domain connected | Domain connected 2026-08-20. Real front-door and Journey content is in; the blog ships empty by choice (decision 34) |

Stage 2's row is the one to read carefully: what is live is the hand-written static preview,
not the architecture in §7. Public-site work continues to ship straight to production; the
Next.js replacement lands the same way when it is ready.

## 11. Open items

### 11.1 Journey shape — deliberately open
The precise structure and visual treatment of the Journey is unsettled **on purpose**. It is the part of the site the owner cares most about, and prose is the wrong medium for deciding it. It was built with defaults — era chapters, date ranges, work entries visually distinguished — and is settled by reacting to a real screen. Expect revision here; it is planned for, not a risk.

**The placeholders are gone.** The owner's real photographs and captions landed on
2026-08-20, replacing every grey box, along with the page-top note that described the
chapters as provisional. The shape is therefore no longer *blocked on content* — it can now
be judged on a real screen with real pictures in it, which is exactly the reaction this
section was waiting for. It remains open: what changes next is a reaction to what is there,
not a guess at what might be.

Three owner-scoped edits already made to the preview are waiting on that reaction, and none is an oversight to correct: the Bizybear entry was removed from the Journey and, later, from the Work tab too (decision 43); the CMU Sophomore era was removed entirely, which drops 996 Ventures from the Journey while keeping it on the Work tab (decision 31, the same pattern as Bizybear); and the Summer 2026 era was merged from three entries into one, which necessarily costs that era the work/personal type distinction — an entry cannot be both.

### 11.2 Content required from owner
Supplied 2026-08-19 and now living in the root static preview: work experience, the
curated projects, the three social accounts (GitHub, LinkedIn, email), and
`headshot.jpg`. It is real content, not placeholder copy, and it is what the Next.js
build ports into MDX. The company logos in `logos/` (decision 41) and the three project
screenshots in `projects/` (decision 45) are owner-supplied on the same terms: each one
comes from a source the owner confirmed, and an entry whose source has not been confirmed
carries no mark and no screenshot rather than a substitute. Where a screenshot shows what
could be read as personal data, the owner confirms its provenance before it ships, because
a public repository cannot unpublish a file from its own history: the patient names in
`projects/patientscope-ai.png` are confirmed synthetic (decision 55).

**Closed 2026-08-21 by decision 39.** The awards open item is retired with the section
that held it: the one confirmed award is a sentence inside the ManuAI project entry, and
there is no longer a section standing empty-handed waiting for a second. A further award
is an owner decision about where it goes, not a slot already cut for it.

### 11.3 Domain
**Closed 2026-08-20.** `jonathangong.com` is registered, connected, and serving the site.
See §7.5.

## 12. Success criteria

1. A recruiter can state Jonathan's background, best work, and how to contact him within thirty seconds of landing.
2. He can publish a blog post from a browser without opening an editor or touching git.
3. He can add a Journey entry with twenty photos in a single sitting.
4. Adding a year of content requires no infrastructure decision, no bill, and no migration.
5. The site does not look like a template.

## 13. Decision log

| # | Decision | Rationale |
|---|---|---|
| 1 | Recruiter-first, personal depth as differentiator | Competing in the CMU pipeline; the human layer is the edge |
| 2 | Front door / deep room structure | Journey-led buries the professional material; co-equal nav flattens emphasis |
| 3 | ~~Blog real but occasional; one post at launch~~ **SUPERSEDED by 34** | Zero posts reads as abandoned. That reasoning is overruled, not reinterpreted: the site is live with an empty blog and the owner accepts how it reads. The blog stays real and occasional under 34; only the at-launch post is retired |
| 4 | Admin UI for content | Owner override of a files-only recommendation |
| 5 | Name: Jonathan Gong; domain deferred | Deferral closed 2026-08-20: `jonathangong.com` is registered and serving the site (§7.5, decision 32) |
| 6 | True clean slate; old `portfolio` repo ignored entirely | Owner's decision |
| 7 | Git-backed content, no database | ~6 posts/year does not justify permanent database operation; git gives history, backup, rollback, portability free |
| 8 | Admin scope: content only | Work/projects/awards change rarely; a CRUD interface for five fields costs more than editing a file |
| 9 | Journey grouped by era | Owner's choice over flat stream and expandable spine |
| 10 | Journey noindexed; no per-entry privacy | Owner's choice; consequence accepted in §8 |
| 11 | ~~Substantive work entries (2–3 lines, metrics)~~ **SUPERSEDED by 35** | Terse listings tell a recruiter nothing. That reasoning is overruled, not reinterpreted: both the bullet structure and the numbers are gone |
| 12 | Projects hand-curated | Public repos include scratch work; auto-sync weakens the page |
| 13 | Editorial-warm visual direction | Photographs need editorial minimalism, not utilitarian minimalism |
| 14 | Images in repo | Blob exhausted; removes every external quota and dependency |
| 15 | Next.js App Router + MDX + Tailwind | Admin is a real app; existing familiarity; one deployment |
| 16 | GitHub OAuth, single account | Same identity that owns the repo; no stored credential |
| 17 | *(open — Journey shape, §11.1)* | Settled visually, not in prose |
| 18 | ~~Awards → own section~~ **SUPERSEDED by 39**; no PDF; headshot yes; GPS stripped always | Owner's decisions except GPS, which is non-negotiable. The original "3–4 awards" figure was the owner's recollection; the résumés contain exactly one, and the section built to hold more is gone under 39 — the award now sits in the project it was won with. The rest of the row stands |
| 19 | Ship fast, full structure | See §10, now two drops (decision 32) |
| 20 | ~~Single deployment including admin~~ **SUPERSEDED by 32** | Owner override of a two-drop recommendation. Overtaken by events: the public site went live on its own domain before the admin existed, which §10 had already flagged as the condition for reverting to two drops |
| 21 | Real content, projects seeded from repos | Owner's choice over placeholders |
| 22 | Three visual directions | Taste is comparative |
| 23 | Journey and blog in nav from day one | Structure visible; the blog ships empty (decision 34) |
| 24 | Considered motion | Near-static undersells a photo timeline; showcase-tier reads as a template |
| 25 | `/projects` own page; About on front door | Owner's decision; About would compete with the Journey |
| 26 | ~~Light default, dark opt-in~~ **SUPERSEDED by 27** | Owner's decision, 2026-08-19. A portfolio should look the way its author intended on first load; dark stays available as an opt-in |
| 27 | **Plain / white / empty, tabbed front door.** Supersedes 2, 13, 24, 25, 26 | Owner reviewed three directions on 2026-08-19 and rejected all three as too cluttered and too fancy. Requested a simplistic layout, plain typography, heavy negative space, pure white, and one section per tab instead of a stacked scroll. The reference is davidchung.io, not juliannth.com |
| 28 | Social links as icons; headshot large and circular, head-framed | Owner's instruction 2026-08-19, reviewing plain-v1. Narrow, explicit exceptions to decision 27's no-icons / no-photo-treatment rules; everything else in 27 stands |
| 29 | Social icons near-black (`#111111`); link accent unchanged | Owner's instruction 2026-08-19, reviewing plain-v2: "the social icon should be black." Scoped to the icons — body links stay accent-coloured and underlined, because links that look like text are a usability regression |
| 30 | Work entries may link the company name, for confirmed companies only | Owner's instruction 2026-08-19. ScottyLabs and 996 Ventures are confirmed and linked; the remaining companies stay plain text until the owner confirms a URL, because a guessed domain is worse than no link. Styled as an ordinary body link — no icon, no external-link marker, no new colour |
| 31 | CMU Sophomore era removed from the Journey | Owner's instruction 2026-08-20. Drops 996 Ventures and "Back on campus" from the timeline; 996 Ventures stays on the front door's Work tab, the same pattern as the earlier removal of Bizybear from the Journey (§11.1; Bizybear later left the Work tab as well, decision 43). The Journey is a curated set of chapters, not a complete record |
| 32 | **Public site live before the admin exists.** Supersedes 20 | Captain's instruction 2026-08-20. `jonathangong.com` is registered, connected, and serving the static preview in production. §10 had carried the single-deployment rule as an assumption flagged for overrule; this is that overrule, so §10 is now two drops and the admin (stage 3) ships separately |
| 33 | Committed images must carry no embedded metadata, enforced in CI | Two photos in the first real Journey batch arrived carrying GPS that resolved to real locations, and this repository is public — an unstripped commit publishes them permanently in git history. §7.3 and §8 already required stripping; `check-design-rules.py` now makes it structural rather than dependent on whoever adds the next photo. Parsed at the JPEG-segment / PNG-chunk level, because the bytes `Exif` and `GPS` occur naturally inside compressed scan data and a substring search flags clean files |
| 34 | **Blog ships empty; posts are occasional, added when written.** Supersedes 3 | Captain's instruction 2026-08-20, retiring the requirement that the site launch with one real post. Decision 3's "zero posts reads as abandoned" rationale is overruled outright: the public site is live at `jonathangong.com` with no posts and that is the accepted state. §5.3 and stage 4 of §10 follow; row 23's "blog seeded with one real post" clause is retired with it |
| 35 | **Work and project entries are brief prose with no metrics.** Supersedes 11 | Owner's explicit instruction 2026-08-20, against firstmate's recommendation to keep the figures. Every three-bullet `entry-body` list in Work and Projects became one to two sentences, and the numeric performance figures were removed outright — signup counts, ambassador and user counts, bug and turnaround reductions, launch and iteration counts, analytics and simulation counts, and the "200+ competitors" figure inside the ManuAI project entry. Nothing was invented to replace them and short entries stay short. Scoped to Work and Projects: ~~the Awards panel keeps "1st Place" and "200+ competitors"~~ **SUPERSEDED by 39**, and `entry-meta` lines are unaffected. §5.1 and §5.2 are rewritten to match |
| 36 | **The measure widens from 720px to 880px.** Narrowly overrides §9 for this token only | Owner's instruction 2026-08-20: "a little bit more, not too much". 720px gave roughly 70 characters at 17px and left the front door feeling narrow; 880px is about 88 characters and still leaves roughly 280px of margin each side at 1440px. Hard cap 900px — the About paragraph is the readability constraint, and past it the line grows harder to track back. A single `--measure` token, not a second prose-vs-entry measure. §9's "Do not fill space" is set aside for this one token and nothing else: the negative-space principle otherwise stands in full |
| 37 | **`zero-external-requests` narrows from "no `<link>` at all" to "no `<link>` that fetches off-site".** Amends decision 33's checker, one day on | The rule shipped 2026-08-20 rejecting every `<link>` element with "the page must fetch nothing", which overshot its own intent: the same function already permitted same-origin `src` and only failed off-site ones, and `<link rel="canonical">` starts no fetch whatsoever. Blanket rejection would have blocked a canonical tag and a favicon link — both of which fetch nothing the browser would not already request from the root convention paths. The rule now turns on what the tag makes the browser do: any stylesheet link and any off-site href still fail; same-origin `canonical`, `icon`, and `apple-touch-icon` pass, and every other `rel` (`preconnect`, `preload`, `prefetch`, a bare `<link>` with no `rel`) still fails. This is a deliberate narrowing to the rule's stated purpose, not the constraint eroding: zero external requests is unchanged and still enforced, and `.github/scripts/test-design-rules.py` pins both halves — what must still fail and what must now pass — so a future permissive edit fails CI instead of shipping |
| 38 | The site carries a favicon, per-page metadata, `robots.txt`, and `sitemap.xml` | Owner's instruction 2026-08-21. The live site returned 404 for `/favicon.ico`, `/robots.txt`, and `/sitemap.xml`, and its `<head>` held only charset, viewport, and title, so search results and social previews had nothing to work with. The icons are derived from `headshot.jpg`, cropped tighter to the face because a head-and-shoulders photo turns to mush at 16px, and land at the root convention paths so they work with or without a `<link>` tag. Descriptions are per page and distinct. `journey.html` is excluded from the promotion — it keeps its `noindex`, gets no canonical, no Open Graph, and no structured data, and is left out of the sitemap (§8). It is deliberately **not** `Disallow`ed in `robots.txt`: a disallowed page is never crawled, so its `noindex` is never read and the bare URL can still be indexed from inbound links, which would make the exclusion weaker rather than stronger. Canonical URLs name the apex because apex and `www` both serve 200 (§7.5). `sameAs` lists only the GitHub and LinkedIn URLs already confirmed in `ALLOWED_LINK_PREFIXES`; decision 30's no-guessed-URLs rule applies to structured data too. No visible pixel changes except the browser tab icon. §7.6 carries this contract forward as a requirement of the Next.js build |
| 39 | **Awards section removed; the one award lives in the ManuAI project entry.** Supersedes 18 | Owner's instruction 2026-08-21. The award is only legible next to the thing that won it, and a tab holding a single entry advertised its own thinness. The ManuAI entry already carried the sentence, so this was a deletion, not a migration: the `#awards` tab, its panel, and its entry in the front door's `TABS` array are gone from `index.html`, and the dangling `Awards` link is gone from the `journey.html` and `blog.html` mastheads. "200+ competitors" dies with the Awards panel and is not relocated — decision 35 had already removed the other numeric claims there. The About paragraph keeps its own narrative phrasing of the same result, deliberately: decision 35 never scoped About. §3, §4, §5.2, the removed Awards section (Blog and Journey renumbered to §5.3/§5.4) and §11.2 follow; a stale `#awards` bookmark falls back to About, which is the routing that was already there |
| 40 | Corgi and Scurry confirmed as linkable companies | Owner's confirmation 2026-08-21, logged as decision 30 requires. `https://www.corgi.insure/` and `https://scurryconsulting.com/`, both reachable at the time of confirmation and added to `ALLOWED_LINK_PREFIXES` exactly as given — Corgi's host carries `www.` and Scurry's does not, and neither was normalised into the other's shape. The company name is linked, not the role, matching 996 Ventures and ScottyLabs. Bizybear stayed plain text while it was on the page: no URL was ever confirmed for it, and decision 30 makes an unlinked name the correct outcome rather than a gap to fill. The entry itself was removed by decision 43 |
| 41 | **Work-entry company logos are full colour, overriding §9's "no badges" and palette limit for those marks only** | Owner's instruction 2026-08-21. Firstmate escalated the conflict with §9 and recommended monochrome marks matching the `#111111` social icons; the owner reviewed that conflict and chose full colour, so this row records the override the same way decision 36 records the measure's. Four of the five entries then on the page carry a mark — 996 Ventures, Corgi, ScottyLabs, and Scurry, each from a source the owner confirmed and each committed to `logos/` and referenced relatively, because zero external requests is not relaxed and a company's asset is never hotlinked. **Bizybear carried none**: no logo URL was ever confirmed for it, decision 30 forbids guessing one, and the owner approved the empty slot — no placeholder, initial, or generic glyph stands in for it. That entry was removed by decision 43, so the empty slot is no longer on the page, but the rule it demonstrated still binds the next unconfirmed mark. The marks are used unaltered, which is what keeps nominative use of an employer's logo on a personal CV site straightforward; the only file-level changes are removing empty transparent canvas from the 996 Ventures wordmark (a 637x364 mark centred in a 1024x1024 file, which a plain resize would have rendered as 7px glyphs) and correcting Scurry's SVG root `width`/`height` from a square `64x64` to its own `13:10` viewBox ratio, so it stops rendering letterboxed. Neither touches the drawing. The `.entry-logo` rule fitted every mark to a 20px band inside the title's 27.19px line box, so the vertical rhythm and the 880px measure were unchanged — **superseded by 44**, which doubles the band to 40px and moves the mark out of the line box into a real grid column; and ~~width runs free to 36px so no mark is distorted~~ **CORRECTED by 42**, which replaces the free width with the shared fixed-width slot and keeps each mark undistorted inside it with `object-fit: contain`. Each mark carries `alt=""`: the company name sits in the title as text immediately after it, so a described logo would make a screen reader announce every company twice. The mark sits **outside** the `<a>` on the four linked names, keeping the click target on the text. `check-design-rules.py` needed no change — no rule fired on the logos, so none was narrowed |
| 42 | Work-entry logos sit in a shared fixed-width slot, so all the company names keep one left edge | Firstmate's visual review of the preview, 2026-08-21. Decision 41 shipped with `width: auto` on the mark, so each logo set its own width and pushed its company name to a different x — 387/372/372/378 across the four marked entries, with Bizybear falling back to the panel edge at 344. A 43px ragged edge in a five-item list (the panel held five entries until decision 43), on a page whose stated design is negative space and restraint, read as broken rather than deliberate. The layout the owner approved showed the names sharing one left edge with Bizybear's slot simply empty: a gap where a logo would be, not a line starting further left than every other line. The slot is reserved on the Work `.entry-title` as `padding-left: 43px` — the widest mark (996 Ventures at 35px) plus the existing 8px gap, so nothing narrowed — and the mark is pulled back into that gutter with a matching negative margin. `object-fit: contain` with `object-position: left center` keeps each mark's own aspect ratio inside the slot, left-aligned; no logo is stretched, cropped, or letterboxed, and no image file changed. Scoped to `[data-panel="work"]` because the Projects panel shares `.entry-title` and must not gain a gutter (verified: Projects titles keep `padding-left: 0` at x=344). This corrects decision 41's implementation; it does not reopen any of its decisions — full colour, the four-of-five coverage, and Bizybear's empty slot all stood at the time, and full colour still does. The slot mechanism itself is unchanged by decision 44, which only widens it from 43px to 40px-plus-gap and reserves it on a grid column instead of the title's padding |
| 43 | **Bizybear removed from the Work panel.** The company no longer appears anywhere on the site | Owner's instruction 2026-08-24. The Journey dropped the entry earlier (§11.1); this removes the remaining one, on the front door's Work tab, so the four entries left are 996 Ventures, Corgi, ScottyLabs, and Scurry. Not an oversight to correct back: the Work tab is a curated list, the same way the Journey is a curated set of chapters. The prose the removal falsified was corrected in the same pass rather than left standing — decision 40's "Bizybear stays plain text", decision 41's four-of-five coverage and empty slot, decision 42's "five company names", §11.1's account of which tab kept the entry, and `AGENTS.md`'s use of Bizybear as the worked example of an unconfirmed logo source. The **rule** that example carried is untouched and still binds: a company whose logo source the owner has not confirmed carries no mark, and no placeholder, initial, or generic glyph stands in for it (decision 30). So is decision 42's shared-slot contract — every remaining entry happens to carry a mark, but the reserved column stays, because an unmarked entry must still hold the same indent |
| 44 | **Work-entry logos enlarged to a 40px band, superseding the 20px sizing in decisions 41 and 42** | Owner's instruction 2026-08-24. The marks read as title ornament at 20px; the owner asked for them noticeably larger, and 40px is roughly double. Every mark is fitted to a 40px square with `object-fit: contain`, so each keeps its own aspect ratio and its **long edge** lands at 40px — the three square-ish marks double, and the 996 Ventures wordmark, already width-constrained at 35px, grows to 40x23. A wide wordmark reading smaller than a square mark at the same long edge is the honest cost of not distorting it, not a defect. At 40px a mark no longer fits the title's 27.19px line box, so decision 41's inline image with a `vertical-align` nudge is replaced by a two-column grid on `[data-panel="work"] .entry` — a fixed `40px` column, a `16px` gap, and the mark spanning the title and meta rows, vertically centred against that block. The `<img>` therefore moves out of `.entry-title` and becomes a direct child of the entry; it stays outside the `<a>`, keeps `alt=""`, and its intrinsic `width`/`height` attributes are unchanged. The grid stays scoped to `[data-panel="work"]` so the Projects panel, which shares `.entry` and `.entry-title`, gains no column (verified: Projects titles hold x=264, the panel edge). **Nothing else about decision 41 moves** — the marks are still full colour, still unaltered, and still have nothing drawn around them: no card, border, shadow, panel, or background. Decision 42's shared-left-edge contract is met by the grid column instead of the title's `padding-left`. No image file changed: 996 Ventures at 70px and ScottyLabs at 37px still cover a 40px display box at ~1.75x and ~0.93x, close enough that no re-export was warranted, and ScottyLabs has no confirmed source on hand to re-export from anyway — decision 30's no-guessing rule covers logo sources, so re-fetching one from the web was not an option. Checked at 1280px and at the 560px breakpoint: 40px plus a 16px gap leaves the title uncrowded at 375px, so the breakpoint needed no override. Decision 36's 880px `--measure` token is unchanged — it was set for the About paragraph's readability, which the Work body was never the constraint on — but the 40px column and its 16px gap sit inside that measure, so the Work panel's effective body measure is 824px, and the entry's title, meta, and body now share one left edge rather than the body starting flush at the panel edge. Firstmate raised that indent as a side effect on 2026-08-24 and the owner reviewed it the same day and kept it, so it is the intended layout, not a consequence to undo. The Projects panel is untouched at 880px |
| 45 | **Projects entries become image cards, overriding §9's "no cards" and "no borders-as-styling" for that panel only** | Owner's instruction 2026-08-25. Firstmate raised the conflict with §9 explicitly before anything was built — the section prohibits cards and borders-as-styling in the same breath — and the owner chose cards anyway, so this row records the override the way decision 41 records the full-colour logos' and decision 36 the measure's. It is not an oversight to correct back. **What it grants:** a `1px` hairline border in a light neutral (`--rule`, `#dcdcdc`) around a Projects entry, and one committed screenshot filling that card. **What it does not grant:** anything to any other panel, and inside the card no shadow, no gradient, no coloured or tinted panel. The three images are committed to `projects/`, referenced relatively, and stripped of embedded metadata like every other image (decision 33); they share one aspect ratio and one pixel size (1080x450, 12:5) so the cards read as the same kind of object, and each was cropped to that ratio rather than letterboxed or stretched. Each `<img>` carries a real `alt` and explicit `width`/`height`, the opposite of the Work logos' `alt=""` (decision 41) because here the image says something the prose does not. A linked card is the click target through an empty `::after` stretched from the title's `<a>`, which keeps the visible link on the title text (decision 29) instead of flattening the prose into link colour; `.entry-links` is positioned above that overlay so PatientScope's `Repository` link stays independently clickable. Every rule is scoped to `[data-panel="projects"]`, the mirror of decision 44's scoping — verified after the change that the Work panel renders pixel-for-pixel identically, and that Work entries still carry no border, no positioning, and their 40px logo column. **Amended the same day by the owner's redirect, decisions 48–52:** ~~the title, meta, and body sit beneath the image on the resting card~~ they are revealed on hover instead (48); ~~no `border-radius`, the headshot is still the only shaped element~~ the card is rounded and is now the second (49); ~~a responsive grid, three across at the 880px measure~~ one card per row (51). Two clauses of this row survive that redirect unchanged and are restated by decision 52: **no motion** — no transition, no hover animation, no transform — and nothing else drawn inside the card |
| 46 | **Poker Bot and the C0 Virtual Machine removed from Projects.** The panel is three entries | Owner's instruction 2026-08-25. Projects is a curated list, the same way the Work tab is (decision 43) and the Journey is a curated set of chapters (decision 31): the removal is the decision, not a gap to fill, and neither entry returns because a later session notices the repository still exists. ManuAI, PatientScope AI, and Chalk remain, in that order. §5.2 follows — the "five projects carried by the root static preview" set is retired with them |
| 47 | ManuAI and PatientScope AI linked to confirmed destinations; **Chalk deliberately left unlinked** | Owner's confirmation 2026-08-25, logged as decision 30 requires. `https://www.youtube.com/watch?v=9Mp3-vZTWuM` for ManuAI and `https://devpost.com/software/patientscope-ai` for PatientScope AI, both verified reachable (HTTP 200, no redirect) at the time of confirmation and added to `ALLOWED_LINK_PREFIXES` exactly as given — the YouTube host carries `www.` and the Devpost host does not, and neither was normalised into the other's shape, the same care decision 40 took with Corgi and Scurry. PatientScope AI keeps its existing `Repository` link in `.entry-links`; the card link is in addition to it, not a replacement. **The owner declined to link Chalk.** No URL was confirmed for it, so it carries none: decision 30 makes an unlinked entry the correct outcome, and a future session should read the missing link as the decision it is rather than infer one from the project's screenshot or find one on the web. Its card carries no anchor at all, so nothing in it takes a pointer cursor or implies a click. **Amended by decision 48:** it is not otherwise inert — ~~no hover state~~ its overlay opens on hover and focus exactly like the other two, because a project the visitor cannot click is still a project they must be able to read. Having no focusable descendant, it takes `tabindex="0"` so a keyboard user reaches it; that attribute exists for the reveal, not to imply a destination |
| 48 | **A Projects card shows the image alone; the title and description are revealed on hover, on focus, and shown permanently on small screens** | Owner's redirect 2026-08-25, superseding decision 45's resting layout: "can we instead have it so all the cards just show the image and they're rounded and more aesthetic? When you hover over the card you see the description." So the card *is* the screenshot at rest, and the title, `entry-meta` line, one-sentence description, and any `.entry-links` row sit in an overlay over a **flat** translucent white scrim — flat because §9 and CI both reject a gradient, and white because it keeps the site's own colour language (near-black text, grey meta, the link accent) rather than introducing white-on-dark. The scrim is `rgba(255, 255, 255, 0.94)`, chosen so the composite is effectively white under *any* screenshot: the images run from ManuAI's dark camera feed to PatientScope's white dashboard, and at that alpha the worst case a black pixel can produce is `rgb(240, 240, 240)`, which holds the body text at 16.6:1, the grey meta at 4.7:1, and the link accent above 8:1. Contrast therefore does not depend on which image the text lands over, which is the failure mode a lighter scrim would have had. **Three access paths are part of the decision, not polish on top of it**, because hover-only content is unreachable for most of the ways people use a site: `:focus-within` opens the overlay for a keyboard user (Chalk, having no link and so no focusable descendant, takes `tabindex="0"` to earn a tab stop); ~~at the 560px breakpoint and below the overlay stops being an overlay and lays out permanently beneath the image, unscrimmed, with no tap-to-reveal hack, because phones do not hover~~ **SUPERSEDED by 53**, which keeps the permanent unscrimmed layout and the no-tap-to-reveal rule exactly as written but gates it on hover and pointer *capability* plus a measured `min-width` floor rather than on the 560px breakpoint — the width test left an iPad with neither the overlay nor the permanent text, and left a 561-660px hovering window clipping the title off the top of the card; and the text is real markup in the DOM at all times, hidden only by `opacity` — never `display: none`, `visibility: hidden`, `aria-hidden`, CSS `content`, or script — so a screen reader reads all three descriptions with no interaction at all. That makes the Projects panel the first part of this site to carry a genuine interactive state: **its visually hidden text is live markup, not leftovers, and a future session must not read it as dead and delete it.** Verified at 1280px that all three overlays open and stay legible over their own screenshot, that every tab stop opens its card and shows a focus ring, and at 560px and 375px that nothing depends on hover |
| 49 | **Projects cards are rounded, overriding §9's single-radius rule; the CI gate widens from one selector to two** | Owner's redirect 2026-08-25 ("rounded and more aesthetic"). The headshot had been the only element on the site permitted a non-zero `border-radius` since decision 28, and decision 45 had explicitly kept it that way a few hours earlier; this overrides that. The card takes `border-radius: 10px` plus `overflow: hidden`, which is what makes the radius clip the screenshot so no square image corner pokes out past it. **The headshot is no longer the only rounded element on the site, and that is now a two-item list rather than a principle** — it grants nothing to any other component, and a radius anywhere else is still a defect. `check-design-rules.py`'s `no-decoration` rule was widened the narrow way, by selector: a `RADIUS_EXEMPT_SELECTORS` set naming `.masthead img` and `[data-panel="projects"] .entry` and nothing else. The check also tightened while it moved — it now matches the whole selector, comma part by comma part, where it used to test for `.masthead img` as a substring, because `[data-panel="projects"] .entry-title` shares a prefix with the card and must not inherit the permission, and `.masthead img, .anything-else` must not launder a radius onto the second half. Nothing else in that rule moved: the `transition`, `@keyframes`, `animation`, gradient, and shadow branches are untouched. `.github/scripts/test-design-rules.py` gained twelve cases pinning both halves of the new boundary — both exempt selectors pass, a zero radius passes anywhere, and `.entry`, `[data-panel="work"] .entry`, the shared-prefix selectors, and a mixed comma group all still fail — for the same reason decision 37 pinned the `<link>` rule: a widening that quietly permitted a radius everywhere would still pass CI, and that test file exists to catch exactly that |
| 50 | **Projects descriptions condensed to one sentence each** | Owner's redirect 2026-08-25 — "if any of them are longer than a couple of sentences, then squish them down into just one sentence" — applied to all three, which were each two sentences of 30 to 40 words and too long for any overlay to carry. Condensing was cutting, not rewriting: no capability, metric, or claim appears that the longer prose did not already carry. What was deliberately kept through the cut: **ManuAI's 1st place at the Y Combinator × Moss Conversational AI Hackathon**, which is the strongest credential on the page and which the About paragraph already refers to, so dropping it would have left that reference dangling (decision 39 put the award in this entry for the same reason); PatientScope AI as ICU clinical decision support built on MIMIC-IV; and Chalk as an AI voice tutor that draws synced whiteboard animations. What went: ManuAI's hackathon sponsor, PatientScope's CTE and split-hosting sentence, and Chalk's JSON-format and renderer sentence. The `.entry-meta` date-and-stack line is unchanged — it was already short — and moves into the overlay with the title. Decision 35's "short entries stay short and nothing is invented to replace them" governs this the same way it governed the original cut |
| 51 | **Projects cards lay out one per row at full measure**, closing the grid-width question | Owner's decision 2026-08-25, settling a question firstmate had raised and paused on. Three across put each image at about **234x97**, which is unreadable and defeats the point of having images at all; one per row gives roughly **752x313**. The panel's 24px rhythm between cards is unchanged, and the grid is now a single `1fr` column at every width rather than an `auto-fit` track — which also retires the two-column middle range decision 45 shipped. The 560px breakpoint no longer needs a column override, because one column is the layout everywhere; ~~what it overrides now is the reveal (decision 48)~~ **SUPERSEDED by 53** — the reveal moved off that breakpoint onto a capability query, so the 560px block now carries nothing about Projects at all. Checked for horizontal overflow at 1280px, 560px, and 375px: none |
| 52 | **Motion stayed at zero through the hover redirect; §9's motion rule and CI's `transition` ban were not relaxed** | Recorded because the opposite is the obvious thing for a future session to assume. A hover reveal is the classic reason to reach for an ease, and both §9 ("motion is near-zero") and `check-design-rules.py`'s `no-decoration` rule (which rejects any `transition:` outright) were left exactly as they were. The reveal is an `opacity` switch with no transition, no fade, no transform, and no `@keyframes` — measured in the browser as `transition-duration: 0s` on the overlay. This is deliberate and is not a thing to improve: if the design is ever judged to fail without easing, that is an owner decision to reopen, not an implementation gap to close. `test-design-rules.py` now pins it directly, asserting that a `transition` and a gradient scrim on the overlay's own selector both still fail |
| 53 | **The Projects reveal is gated on hover and pointer capability plus a measured width floor, not on the viewport breakpoint.** Supersedes the small-screen clause of 48 | Owner's decision 2026-08-25, after firstmate escalated two findings that the width-based rule could not close. **First**, a touch device wider than 560px had neither hover nor the permanent layout: an iPad at 768px portrait or 1024px landscape rendered the panel as three unlabelled screenshots, and a tap on ManuAI or PatientScope left the site with nothing on screen naming the destination, while Chalk — `tabindex="0"` and not a link — behaved differently again depending on Safari's hover emulation. **Second**, and separately, a *hovering* window in the 561-660px band clipped the overlay's title off the top: the card's height is locked to the image's 12:5 ratio while the overlay's text grows as the card narrows, so `justify-content: flex-end` pushed the excess past the top edge, where `overflow: hidden` cut it away. Decision 48's verification pass at 1280px, 560px and 375px had bracketed that band without entering it. Measured title-top offsets against the card's top edge, negative meaning clipped away entirely (ManuAI / PatientScope / Chalk): **561px** -53 / -85 / -49; **600px** -36 / -69 / -9; **640px** +8 / -28 / +35; **700px** +33 / +24 / +60; **720px** +41 / +32 / +68; **768px** +88 / +52 / +88. PatientScope's overlay is the tallest — longest description plus the Repository row — and only clears the overlay's own 28px top padding from 720px up. The fix inverts the structure so that **the accessible layout is the default and the overlay is the capability-gated enhancement**: `.entry-reveal` is static, opaque, unscrimmed and padded by default, and only inside `@media (hover: hover) and (pointer: fine) and (min-width: 768px)` does it become the absolute, scrimmed, `opacity: 0` overlay with its `:hover` and `:focus-within` rules. 768px is the first round value above the 720px measured floor and also keeps an iPad-width window on the permanent layout; **do not lower it without re-measuring PatientScope**. The now-redundant `max-width: 560px` override is deleted, because the permanent layout is the default at every width. Nothing else moved: the 12:5 ratio, the 1080x450 files, one card per row, the 24px gap, the radius, the border and the `rgba(255, 255, 255, 0.94)` scrim are unchanged, **motion is still zero** (decision 52 — no transition, transform or animation was added and CI's ban was not relaxed), no JavaScript was introduced, the hidden text is still hidden by `opacity` alone, Chalk keeps its `tabindex="0"`, and every rule stays scoped to `[data-panel="projects"]`. Re-verified: the capability gate evaluates false and the text is permanently visible on emulated iPad 768x1024 and 1024x768 touch profiles and on a 375x812 phone; no title or body clips at 560, 600, 640 or 767px on a hovering pointer, nor at any width from 768px up (worst case is PatientScope at +52 against 28px of padding at the floor itself); hover opens all three overlays at 1280px with `transition-duration: 0s`; the four keyboard tab stops still each open their card's reveal with a focus ring; whole-card hit-testing still resolves ManuAI and PatientScope to their URLs at top, middle and bottom with `cursor: pointer` while Chalk returns `cursor: auto`, and PatientScope's Repository link stays independently clickable. The Work and About panels, `journey.html` and `blog.html` were pixel-diffed against the pre-fix commit at 1280, 768, 560 and 375px: identical. §5.2's Touch bullet, §9's Projects exception and `AGENTS.md` all now state the capability rule |
| 54 | **The three Projects screenshots carry `loading="lazy"`** | Firstmate's finding, owner's decision 2026-08-25. The images total 762KB — `manuai.png` 369KB, `chalk.png` 257KB, `patientscope-ai.png` 136KB — against a previous whole-page weight of a headshot at 36KB, and every one of them was fetched on **every** load of `/` even though About is the default panel and Projects is `display: none` until its tab is opened: `display: none` does not stop an `<img src>` from loading. An element with no box never intersects the viewport, so `loading="lazy"` defers all three until the panel is actually shown, and a visitor who never opens Projects never pays for them. Verified: zero `projects/` requests on load of `/`, all three requested on opening the tab. **Re-exporting or re-encoding the images was considered and rejected** — the owner is explicit that the stripped-and-cropped PNGs ship byte-for-byte as committed (decisions 45 and 48), so converting them to JPEG, or re-exporting at the 1504x627 that would match the display size at 2x, was not done. The existing `width`/`height` attributes are kept so nothing reflows as a deferred image arrives |
| 55 | **The patient names in `projects/patientscope-ai.png` are owner-confirmed synthetic placeholders** | Owner's confirmation 2026-08-25, logged the way decision 30 requires an owner confirmation to be logged, and obtained **before** the file shipped rather than after — a public repository cannot unpublish an image from its own git history, which is why the question was asked up front. Firstmate flagged that the screenshot puts patient-level rows on a live public site: full names ("Christopher White", "Charles Hernandez", "Matthew Garcia") beside lab values and timestamps. The owner confirms they are **app-generated surrogates, not real people**, which is consistent with the underlying data — MIMIC-IV carries no patient names at all, and the far-future dates in the frame (11/17/2201, 5/23/2187, 10/27/2181) are MIMIC-IV's date-shifting signature. The file therefore ships exactly as committed: it is **not** to be re-cropped, blurred, re-exported, or replaced, and a future session must not read those names as a privacy defect to correct. This row records a positive confirmation, not an unreviewed oversight, and it **loosens nothing**: §7.3, §8 and decision 33's rule against publishing identifying data into this repository stand unchanged, and the next screenshot carrying anything that looks like personal data needs its own confirmation on the same terms |
| 56 | **The About paragraph is replaced by four short paragraphs of the owner's own copy, and no longer narrates the hackathon result** | Owner's instruction 2026-08-31, supplying the replacement text himself. The single About paragraph — which opened "Hi, I'm Jonathan" and closed "my inbox is open" — is gone, along with the `.note` education line beneath it ("Carnegie Mellon University — B.S. Information Systems, double major in Artificial Intelligence. August 2025 – May 2029."); the `.note` CSS rule stays, because `blog.html` still uses it and the three inline stylesheets are required to stay byte-identical. The new copy is the owner's words about himself and is not to be rewritten, expanded, or condensed by a future session. **This narrows two standing rows.** Decision 39 says "The About paragraph keeps its own narrative phrasing of the same result, deliberately" and decision 50 says the ManuAI award was kept through the one-sentence cut partly because "the About paragraph already refers to" it — both are now false as to About, and a reader following either row will look for a sentence that is gone. **The award's home is the ManuAI project entry alone**, on the owner's instruction, and that entry keeps it: the credential did not leave the site, and this was accepted rather than overlooked. Neither earlier row is rewritten in place; they are superseded here, the way this log supersedes elsewhere. **One deliberate departure from the supplied text:** the owner wrote "inquires" and it ships as "inquiries" — a spelling correction to an obvious typo on a professional portfolio page, made knowingly and reported to the owner, recorded so it is not later read as drift and reverted. Everything else is verbatim, including the fragment "A little bit about me.", the unhyphenated "go to market", and the closing exclamation mark. "reach out" in the last paragraph is a `mailto:jagong@andrew.cmu.edu` link — the same address the masthead email icon already uses, so no new destination and no `ALLOWED_LINK_PREFIXES` change — carrying no class, inline style, `target`, or `rel`, so it inherits the page's existing link styling. **No `<head>` metadata changed:** the `description`, Open Graph, Twitter, and JSON-LD strings on `index.html` and `blog.html` still say "Information Systems and Artificial Intelligence student at Carnegie Mellon" and the JSON-LD keeps its `alumniOf` entry — the AI double major is still true, merely no longer in the prose, and the owner asked for a copy rewrite rather than a claims audit. The masthead one-liner is untouched on all three pages. No CSS, markup pattern, or JavaScript changed; decision 36's 880px `--measure` still governs the panel, and no horizontal overflow or layout change was found at 1280, 768, 560 or 375px |
| 57 | **About's four paragraphs are separated by 24px, a scoped exception to the panel's 56px rhythm** | Firstmate's finding on decision 56, owner's decision 2026-08-31 taken after reviewing 56px, 24px and 16px rendered. `.panel > * + *` was sized as the **between-entry** rhythm — it separates whole Work entries, and before decision 56 it separated the single About paragraph from the grey `.note` line — and four one-line prose paragraphs inherited it, so the bio read as four disconnected blocks rather than one continuous introduction on the site's default landing view: **the paragraphs spanned 331px, 168px of it empty**. 16px was rejected in the other direction, because the gap between paragraphs would fall below the paragraph's own roughly 27px line spacing and a paragraph break would read as weaker than a line break inside one. The whole change is one rule, `[data-panel="about"] > p + p { margin-top: 24px; }`, **scoped to About so no other panel moves**: `.panel > * + * { margin-top: 56px; }` is unchanged and still governs Work, Projects and every other panel child (verified: Work, Projects, `journey.html` and `blog.html` render identically). 24px is already on the page — it is the Projects card gap (decision 51) and the masthead's column gap — so no new token, type size, or colour was introduced, and §9 binds in full otherwise: no shadow, gradient, transition, animation, or radius. The identical line goes into all three inline stylesheets at the identical position, because `stylesheets-identical` requires them byte-identical even though only `index.html` has an About panel. The copy, the `mailto:` anchor, the markup, the `<head>` metadata and the JavaScript are untouched. **This narrows decision 56's closing "No CSS, markup pattern, or JavaScript changed"** — that was true of the copy rewrite itself; this row is the spacing that followed from it, and neither row is rewritten in place. Recorded here so the two are not later read as unrelated: the same finding round also corrected `AGENTS.md`, whose Projects paragraph still said ManuAI's 1st-place hackathon line "was kept through that cut on purpose and the About paragraph depends on it" — a dependency decision 56 had made false, and the load-bearing rationale a future session would use to justify keeping the credential. That clause now states that the About paragraph no longer mentions it and that the ManuAI entry is the award's only home on the site |
