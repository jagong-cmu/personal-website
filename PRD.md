# Jonathan Gong — Personal Website PRD

- **Project:** `jagong-cmu/personal-website` (public)
- **Owner:** Jonathan Gong
- **Status:** Visual direction approved (§9, decisions 27–29). The approved static preview
  is landed at the repository root and deploys on Vercel for review; the Next.js build in
  §7 has not started. `README.md` covers the preview.
- **Date:** 2026-08-18, last revised 2026-08-19
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
- **No admin editing of work, projects, or awards.** Those are file edits. Only blog and Journey — the content that grows without bound — earn a management interface.
- **No auto-sync of projects from GitHub.** Curation beats completeness; the public repos include scratch work that would weaken the page.
- **No showcase-tier motion.** No parallax, no custom cursor, no animated hero.
- **No contact form, analytics dashboard, or other admin operations in v1.** Each is a separate future project.

## 4. Information architecture

**The front door is a tabbed shell, not a long scroll.** One persistent header — name,
one line, links — with a row of plain text tabs beneath it. Clicking a tab swaps the
content area in place. Each tab is a real route so it can be linked and bookmarked.

```
/                 Front door shell. Opens on About.
  /about          About — a short paragraph
  /work           Work experience
  /projects       Projects
  /awards         Awards
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
Company, role, date range, and two to three lines written as outcomes with concrete numbers wherever they exist. Terse listings undersell; metrics are what make this section work.

### 5.2 Projects — file-edited, hand-curated
Name, one-line summary, longer description, tech, links (repo, live). The set is now curated and settled — the five projects carried by the root static preview (§11.2) — which supersedes the earlier guess at which public repositories would be featured.

### 5.3 Awards — file-edited
Own section, one tab. Each entry: name, granting body, year.

**Exactly ONE award is confirmed** — 1st Place, Y Combinator × Moss Conversational AI
Hackathon (June 2026, 200+ competitors, sponsored by Unsiloed AI). The owner believed there
were three or four; all three résumé versions were read in full on 2026-08-18 and contain
only this one. The earlier "three to four entries" figure recorded that belief and was
wrong; it is corrected here rather than left as a requirement the site cannot meet.

The section is built to hold three or four gracefully and renders one deliberately — no
padding, no placeholder, no "more coming". If the owner supplies more they drop in with no
layout change (open item, §11.2).

### 5.4 Blog — admin-managed
Frontmatter: title, slug, date, summary, draft flag, optional cover image. Body is MDX. Ships with **one real post** at launch — an empty blog reads as abandoned, a single genuine post reads as a beginning.

### 5.5 Journey — admin-managed
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
Not yet purchased. `jonathangong.com` was available at $11.25/yr as of 2026-08-18; `.dev` $9.99, `.me` $13.99, `.net` $13.50. `jongong.com` and `jgong.dev` are already taken. Nothing in the build depends on this; it is wired up at the end.

## 8. Privacy and safety

- **The Journey is excluded from search engines**, so it will not surface in a search for the owner's name.
- **Accepted risk, decided knowingly:** `noindex` does not restrict anyone holding the URL, and scrapers routinely ignore it. There is **no per-entry private switch** in v1 — every uploaded photo is effectively public to anyone who has ever been sent the link. Adding per-entry visibility later is a retrofit; the option was offered and declined.
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
- **No decoration.** No cards, no shadows, no gradients, no borders-as-styling, no
  coloured panels, no badges, no signature motif.
  - **Exception, owner's instruction 2026-08-19:** social links are monochrome inline-SVG
    icons rather than the words "GitHub"/"LinkedIn"/"Email". Icons only for these three.
  - **Exception, owner's instruction 2026-08-19:** the headshot is a circular crop, framed
    on the head, and noticeably larger than a thumbnail. This is the one shaped element
    on the site.
- **Colour is black text on white**, plus grey for metadata. At most one restrained accent,
  used for links only. No accent backgrounds.
  - **Exception, owner's instruction 2026-08-19:** the three social icons are near-black
    (`#111111`), not accent-coloured. The accent itself is untouched — body links stay
    visibly link-coloured. Do not "unify" the two: links that read as plain text are a
    usability regression, not a simplification.
- **Motion is near-zero.** A plain instant tab switch is the default. Nothing animates in on
  scroll. This supersedes decision 24.
- **No theme toggle.** The site is white. Dark mode is dropped for now; this supersedes
  decisions 13 and 26 and is trivially re-addable if the owner asks.

The headshot appears in the front-door header as a **circle, cropped to the head**, at a
size that reads as a portrait rather than an avatar. No border, no shadow, no filter.

## 10. Delivery plan

**Single deployment.** The site does not go to a public URL until the public pages and the admin both work.

| Stage | Output | Gate |
|---|---|---|
| 1 | Three visual directions — front door + one Journey screen, side by side | Owner picks one |
| 2 | Public site built: front door, /projects, /journey, /blog | Visual review |
| 3 | Admin built: GitHub auth, editor, image pipeline, commit layer | Working end to end |
| 4 | Real content in, one blog post written, domain connected | Launch |

Stage 1 closed on 2026-08-19: the owner approved the plain/white/empty direction after
four review rounds, and §9 is the result. The approved static preview now deploys on
Vercel as a **review** URL so that design can be checked on a real screen. That does not
loosen the rule above — the launch is still stages 2–4 shipping together.

**Assumption carried forward, flagged for overrule:** "live as soon as possible" is satisfied by seeing mockups within a day or two, *not* by an early deployment. Under this reading nothing is lost but an early URL that would not have been shared anyway. If a deployed public site is wanted before the admin exists, this reverts to two drops and stages 2 and 3 ship separately.

## 11. Open items

### 11.1 Journey shape — deliberately open
The precise structure and visual treatment of the Journey is unsettled **on purpose**. It is the part of the site the owner cares most about, and prose is the wrong medium for deciding it. It will be built with defaults — era chapters, date ranges, work entries visually distinguished — and settled by reacting to a real screen. Expect revision here; it is planned for, not a risk.

### 11.2 Content required from owner
Supplied 2026-08-19 and now living in the root static preview: work experience, the
curated projects, awards, the three social accounts (GitHub, LinkedIn, email), and
`headshot.jpg`. It is real content, not placeholder copy, and it is what the Next.js
build ports into MDX.

Still open: further awards, if the owner has any beyond the one confirmed in §5.3. The
awards section holds three or four without redesign, so any the owner supplies drop in
with no layout change.

### 11.3 Domain
Deferred by owner. See §7.5.

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
| 3 | Blog real but occasional; one post at launch | Zero posts reads as abandoned |
| 4 | Admin UI for content | Owner override of a files-only recommendation |
| 5 | Name: Jonathan Gong; domain deferred | — |
| 6 | True clean slate; old `portfolio` repo ignored entirely | Owner's decision |
| 7 | Git-backed content, no database | ~6 posts/year does not justify permanent database operation; git gives history, backup, rollback, portability free |
| 8 | Admin scope: content only | Work/projects/awards change rarely; a CRUD interface for five fields costs more than editing a file |
| 9 | Journey grouped by era | Owner's choice over flat stream and expandable spine |
| 10 | Journey noindexed; no per-entry privacy | Owner's choice; consequence accepted in §8 |
| 11 | Substantive work entries (2–3 lines, metrics) | Terse listings tell a recruiter nothing |
| 12 | Projects hand-curated | Public repos include scratch work; auto-sync weakens the page |
| 13 | Editorial-warm visual direction | Photographs need editorial minimalism, not utilitarian minimalism |
| 14 | Images in repo | Blob exhausted; removes every external quota and dependency |
| 15 | Next.js App Router + MDX + Tailwind | Admin is a real app; existing familiarity; one deployment |
| 16 | GitHub OAuth, single account | Same identity that owns the repo; no stored credential |
| 17 | *(open — Journey shape, §11.1)* | Settled visually, not in prose |
| 18 | Awards → own section; no PDF; headshot yes; GPS stripped always | Owner's decisions except GPS, which is non-negotiable. The original "3–4 awards" figure was the owner's recollection; the résumés contain exactly one, so §5.3 now records one confirmed and the section holds more without redesign |
| 19 | Ship fast, full structure | See §10 assumption |
| 20 | Single deployment including admin | Owner override of a two-drop recommendation |
| 21 | Real content, projects seeded from repos | Owner's choice over placeholders |
| 22 | Three visual directions | Taste is comparative |
| 23 | Journey and blog in nav from day one | Structure visible; blog seeded with one real post |
| 24 | Considered motion | Near-static undersells a photo timeline; showcase-tier reads as a template |
| 25 | `/projects` own page; About on front door | Owner's decision; About would compete with the Journey |
| 26 | ~~Light default, dark opt-in~~ **SUPERSEDED by 27** | Owner's decision, 2026-08-19. A portfolio should look the way its author intended on first load; dark stays available as an opt-in |
| 27 | **Plain / white / empty, tabbed front door.** Supersedes 2, 13, 24, 25, 26 | Owner reviewed three directions on 2026-08-19 and rejected all three as too cluttered and too fancy. Requested a simplistic layout, plain typography, heavy negative space, pure white, and one section per tab instead of a stacked scroll. The reference is davidchung.io, not juliannth.com |
| 28 | Social links as icons; headshot large and circular, head-framed | Owner's instruction 2026-08-19, reviewing plain-v1. Narrow, explicit exceptions to decision 27's no-icons / no-photo-treatment rules; everything else in 27 stands |
| 29 | Social icons near-black (`#111111`); link accent unchanged | Owner's instruction 2026-08-19, reviewing plain-v2: "the social icon should be black." Scoped to the icons — body links stay accent-coloured and underlined, because links that look like text are a usability regression |
