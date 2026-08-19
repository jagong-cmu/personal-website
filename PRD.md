# Jonathan Gong — Personal Website PRD

- **Project:** `jagong-cmu/personal-website` (public, empty at time of writing)
- **Owner:** Jonathan Gong
- **Status:** Awaiting sign-off. No code written yet.
- **Date:** 2026-08-18
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

```
/                 Front door — headshot, name, one-line bio, About,
                  Work Experience, featured Projects, Awards, social links
/projects         Full curated project list
/journey          Era-chaptered photographic timeline  [noindexed]
/blog             Post index
/blog/[slug]      Individual post
/admin            Authenticated content management  [noindexed, nofollow]
```

**About** lives as a section on the front door rather than its own page — a separate About page would compete with the Journey for the same job, and the Journey does it better. It is a real paragraph with a voice, not a bio line.

**Featured projects** appear on the front door (3 items) linking through to the full `/projects` page. The front door must remain scannable; the complete list does not belong on it.

## 5. Content model

All content is MDX or structured data files committed to the repository. There is no database anywhere in this system.

### 5.1 Work experience — file-edited
Company, role, date range, and two to three lines written as outcomes with concrete numbers wherever they exist. Terse listings undersell; metrics are what make this section work.

### 5.2 Projects — file-edited, hand-curated
Name, one-line summary, longer description, tech, links (repo, live). Seeded from real repositories: `patientscopeai`, `transcript-analyzer`, `corgihackathon`, `icu-insights-hub`, `ai-job-search`, plus any not represented publicly.

### 5.3 Awards — file-edited
Own section on the front door. Three to four entries: name, granting body, year.

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

**Libraries, each with a reason:** Tailwind for the system; shadcn/ui for admin inputs and dialogs where hand-rolling is wasted effort; Motion for §9 animation; sharp for the image pipeline; MDX for content; a deliberate typeface pairing rather than system defaults. Nothing is included for its own sake — a site that looks visibly assembled from components is the outcome being avoided.

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

**Editorial and warm** — the Julian Ng-Thow-Hing end of the reference spectrum rather than the David Chung end. Generous whitespace, typographic restraint, prose that reads like a magazine column. The reasoning is functional, not stylistic: this site carries a photographic Journey, and stark utilitarian minimalism fights photographs while editorial minimalism is built to hold them.

- **Headshot on the front door.** Owner's decision.
- **Dark/light toggle**, as a quiet corner control. Not a feature. No warmth slider.
- **Motion: considered.** Scroll-triggered reveals as Journey eras enter the viewport, smooth page transitions, images that settle rather than pop. The standard: a visitor should feel the motion and never notice it.

**Three distinct directions** will be built as mockups for side-by-side comparison before any production code is written. Taste is comparative — more is learned from rejecting two directions than from approving one in isolation.

## 10. Delivery plan

**Single deployment.** The site does not go to a public URL until the public pages and the admin both work.

| Stage | Output | Gate |
|---|---|---|
| 1 | Three visual directions — front door + one Journey screen, side by side | Owner picks one |
| 2 | Public site built: front door, /projects, /journey, /blog | Visual review |
| 3 | Admin built: GitHub auth, editor, image pipeline, commit layer | Working end to end |
| 4 | Real content in, one blog post written, domain connected | Launch |

**Assumption carried forward, flagged for overrule:** "live as soon as possible" is satisfied by seeing mockups within a day or two, *not* by an early deployment. Under this reading nothing is lost but an early URL that would not have been shared anyway. If a deployed public site is wanted before the admin exists, this reverts to two drops and stages 2 and 3 ship separately.

## 11. Open items

### 11.1 Journey shape — deliberately open
The precise structure and visual treatment of the Journey is unsettled **on purpose**. It is the part of the site the owner cares most about, and prose is the wrong medium for deciding it. It will be built with defaults — era chapters, date ranges, work entries visually distinguished — and settled by reacting to a real screen. Expect revision here; it is planned for, not a risk.

### 11.2 Content required from owner
Blocks the real build, not the mockups.

- Work experience: company, title, dates, one line each, numbers where they exist
- The three to four awards: name, granting body, year
- Which projects to feature, including any not public on GitHub
- Which social accounts (assumed: GitHub, LinkedIn, email)
- A headshot image file

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
| 18 | 3–4 awards → own section; no PDF; headshot yes; GPS stripped always | Owner's decisions except GPS, which is non-negotiable |
| 19 | Ship fast, full structure | See §10 assumption |
| 20 | Single deployment including admin | Owner override of a two-drop recommendation |
| 21 | Real content, projects seeded from repos | Owner's choice over placeholders |
| 22 | Three visual directions | Taste is comparative |
| 23 | Journey and blog in nav from day one | Structure visible; blog seeded with one real post |
| 24 | Considered motion | Near-static undersells a photo timeline; showcase-tier reads as a template |
| 25 | `/projects` own page; About on front door | Owner's decision; About would compete with the Journey |
