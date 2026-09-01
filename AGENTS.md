# Project agent memory

This file is the project's committed home for project-intrinsic agent knowledge: build, test, release, architecture, and sharp-edge notes that should travel with the code.

- Add durable project-specific notes here as they are discovered through real work.

## The stack: hand-written static HTML plus `api/` functions

`index.html`, `journey.html`, `blog.html`, `headshot.jpg`, `journey/`, `logos/`, `projects/`,
the root icons, and `robots.txt` / `sitemap.xml` at the repo root are the site, **live in
production on `jonathangong.com`** via Vercel zero-config. They are intentionally
hand-written, self-contained (inline `<style>`, inline `<script>`, inline SVG), and have
**no build step, no framework, no package.json, and no dependencies**. Do not add any —
a `package.json` in particular risks Vercel re-detecting the project as a framework build.

**This file and `README.md` used to call these pages a temporary preview that would be
deleted and replaced by a Next.js app. The owner rejected that on 2026-09-01** (`PRD.md`
decisions 58 and 59, which rewrote §6, §7.1 and §7.4 around it). There is no replacement
pending, and "it would be easier in a framework" is the exact argument that was overruled.

Each page duplicates the whole stylesheet and masthead, so any header or style change is an
N-way edit across every hand-written page. CI's `stylesheets-identical` rule fails if they
drift apart. A generated post page under `blog/` is in that set too but is never edited by
hand: `api/_lib/render.js` lifts the stylesheet and masthead out of `blog.html` at publish
time rather than keeping a copy, so a post is identical by construction — after a CSS change,
re-save each published post from `/admin` to regenerate it.
The mastheads legitimately differ — `index.html` does not wrap its own name in a self-link —
so they are not checked. The per-page `<head>` blocks differ on purpose too: every
description is distinct, and `journey.html` deliberately carries no canonical, Open Graph,
or structured data (`PRD.md` decision 38). Do not make the three heads uniform.

## The blog admin (`/admin`, `api/`)

Built 2026-09-01 on the static stack. `README.md` has the file map; `PRD.md` §6 and §7.1 have
the specification and decisions 58–62 the reasoning. The things that are not obvious from
reading the code:

**Three secrets, environment-only.** `ADMIN_PASSWORD`, `SESSION_SECRET`, `GITHUB_TOKEN` are
set in Vercel and must never appear in a committed file, in client-side JavaScript, or in a
response body. Never add a fallback default for one: a gate that works without its password
is worse than one that fails.

**All content I/O goes through the GitHub API, never the deployed filesystem** — `*.md` is
withheld from the deployment upload, and a just-committed file is not in the running
deployment anyway. `fs` has no place in `api/`.

**A post's state is its location**: `drafts/<slug>.md` unpublished, `blog/<slug>.md` +
`blog/<slug>.html` published. `.vercelignore`'s `*.md` is the *entire* reason a draft is
unreachable rather than merely unlinked, and it keys on the extension alone — a single
non-`.md` file in `drafts/` would be publicly served. CI's `drafts-not-servable` rule guards
that; do not narrow the pattern.

**Every write is one commit** via the Git Data API (`api/_lib/github.js`), because a
half-applied publish leaves a page listed with nothing behind it. The Contents API cannot do
this — it commits per file.

**The slug is the only untrusted input that reaches a path.** It is validated once, in
`api/_lib/posts.js`; every write path is built from it there. Nothing accepts a path from the
browser.

**Markdown is escaped, never passed through** (`api/_lib/markdown.js`). The public pages
carry no author-supplied scripts and CI enforces it; the editor must not become the hole in
that. It is deliberately narrow — do not grow it into a general Markdown engine.

**`admin/` is exempt from the public design rules**, by name in `check-design-rules.py`'s
`EXEMPT_DIRS` and pinned by its tests — `PRD.md` §7.1 grants it. Post pages under `blog/`
are *not* exempt; they are public and fully checked. The one half that does not bind them is
the outbound-link allowlist (decision 61).

**`/admin` is kept out of search by its `noindex` tag alone.** It is named in neither
`robots.txt` nor `sitemap.xml`, and nothing links to it — a `Disallow` would suppress the
fetch that reads the tag while publishing the path in a file every crawler reads. That is the
same reasoning `robots.txt` already gives for `journey.html`.

## Binding visual constraints

`PRD.md` §9 is a list of prohibitions, not preferences, and the owner has rejected several
designs for unrequested "improvement". Before changing anything visual, read §9. The short
form: pure `#FFFFFF` background, system font stack only (no Google Fonts), at most three
type sizes, no shadows/gradients/coloured panels/animation/dark mode. The exceptions §9
grants to those are the inline-SVG social icons — near-black `#111111`, deliberately *not*
the link colour — the circular headshot (one of only two elements permitted a non-zero `border-radius`), and the
**full-colour company logos in the Work panel** (`logos/`, `.entry-logo`, decision 41).
That last one is an owner override of "no badges" and of the palette limit, chosen over a
monochrome treatment firstmate recommended: do not desaturate it back, and do not read brand
colour in Work as licence anywhere else. Nothing may be drawn around a mark, and a company
whose logo source the owner has not confirmed carries none — no placeholder, initial, or
generic glyph stands in for it, and the slot simply stays empty (decision 30 covers logo
sources as it covers links). All four current entries happen to carry a mark, so the rule has
no live example on the page; it still binds the next entry added. The marks sit in a shared
fixed-width column — 40px on the owner's instruction of 2026-08-24, decision 44 — so all four
company names keep one left edge and an unmarked entry would hold the same indent; a ragged
left edge is a defect, not the look of an absent mark (decision 42). At 40px a mark no longer
fits the title's line box, so a Work entry is a two-column grid rather than an inline image.
That grid is scoped to `[data-panel="work"]`: the Projects panel shares `.entry` and
`.entry-title` and must not gain a column.

§9 grants one further exception of the same kind, and it is the **Projects panel: rounded
image cards with a hover reveal** (decisions 45, 48–52 and 53, owner's instruction 2026-08-25).
At rest a card is the screenshot from `projects/` and nothing else, filling it edge to edge
inside a `1px` hairline (`--rule`) and a `border-radius` that clips it. The title, meta,
one-sentence description, and any links row live in an overlay revealed on hover over a flat
`rgba(255,255,255,0.94)` scrim — white and near-opaque so contrast does not depend on which
screenshot the text lands over. All of it is an explicit override of §9's "no cards, no
borders-as-styling", escalated by firstmate before anything was built and confirmed by the
owner, so it is not an oversight to correct back. It grants the border, the radius, the image,
and that flat scrim, and nothing more: no shadow, no gradient (CI rejects one, including as a
scrim), no tinted panel, and **no motion** — the reveal is an instant opacity switch, §9's
motion rule and CI's `transition` ban were not relaxed for it (decision 52), and easing it is
an owner decision to reopen, not a gap to close.

The radius means **the headshot is no longer the only rounded element on the site**.
`check-design-rules.py` now names exactly two selectors in `RADIUS_EXEMPT_SELECTORS` and
matches the whole selector, not a substring, so a radius on anything else — including
`[data-panel="projects"] .entry-title`, which merely shares a prefix — still fails.
`test-design-rules.py` pins both halves; extend it, don't loosen it.

**The Projects panel is the one part of this site with a live interactive state, so its hidden
text is live markup, not leftovers — do not read it as dead and delete it.** The title and
description sit in the DOM at all times and are hidden only by `opacity`, never `display:
none`, `visibility: hidden`, `aria-hidden`, CSS `content`, or script, so a screen reader reads
all three with no interaction. `:focus-within` opens the overlay for a keyboard user. And the
overlay is not the default state at all: **the permanent layout is the default and the overlay
is a capability-gated enhancement** (decision 53). `.entry-reveal` is static, opaque and
unscrimmed in the base rules, and only inside
`@media (hover: hover) and (pointer: fine) and (min-width: 768px)` does it become the absolute,
scrimmed, `opacity: 0` overlay. Gating on width alone was the bug: an iPad reports a wide
viewport and no hover, so it got neither the overlay nor the text, and a hovering window in the
561-660px band clipped the title off the top of a card whose height is locked to the image's
12:5 ratio. The 768px floor is measured — PatientScope has the tallest overlay and only clears
its own 28px top padding from 720px up — so re-measure PatientScope before lowering it. Those
three paths are load-bearing; a change that leaves the description reachable only by mouse is a
regression.

A linked card is the click target through an empty `::after` stretched from the title's `<a>`,
so the visible link stays on the title text. Chalk has no confirmed destination, so it carries
no anchor and nothing in it implies a click — that absence is decision 47, not a gap to fill —
and its `tabindex="0"` exists solely so a keyboard user can open its reveal. Descriptions are
one sentence each (decision 50); ManuAI's 1st-place hackathon line was kept through that cut on
purpose; the About paragraph no longer mentions it, so that entry is the award's only
home in the front-door panels, and `journey.html` narrates the same win separately in
its Summer 2026 era (decision 56). Cards are one per row (decision 51): three across
was measured at about 234x97 per image and rejected as unreadable. All three images
share one ratio and one pixel size on purpose — re-crop, never letterbox or stretch, if a
fourth is added. Each `projects/` `<img>` carries `loading="lazy"` alongside its intrinsic
`width`/`height` (decision 54): the three PNGs are 762KB together and `display: none` on the
inactive panel does not stop a browser fetching them, so a fourth screenshot gets the attribute
too. Every card rule is scoped to `[data-panel="projects"]` the way the Work grid
is scoped to `[data-panel="work"]`, and for the same reason: verify both panels after touching
either.

Three further prohibitions bind this preview as owner decisions rather than §9 text, so do not
expect to find them there: **zero external requests** (no web fonts, no CDN, no external
CSS/JS — a `<link>` is permitted only for a same-origin canonical or icon, decision 37),
no phone number anywhere, and **no committed image may carry embedded
metadata** — GPS and EXIF are stripped before an image lands, non-optionally, because this
repository is public and an unstripped commit publishes the owner's locations permanently into
git history (`PRD.md` §7.3, §8, decision 33).
CI's `no-image-metadata` rule fails the build on anything that still carries it, and for the
static preview the strip is a manual step, done with exactly this command:
`magick <in> -auto-orient -strip -resize '1600x1600>' -quality 82 <out>`.
`-auto-orient` must come before `-strip`, because stripping removes the EXIF orientation tag
and a plain `-strip` therefore leaves a phone photo rotated on the page.
That invocation produced the seven `journey/` photographs, so it is recorded history rather
than a suggestion: do not substitute another tool, add flags, or reorder it.
It is the preview-era procedure only, and `PRD.md` §7.3 owns the eventual build-time `sharp`
pipeline that subsumes it once the Next.js application lands.
The root icons are the one image pair it does not describe — `favicon.ico` (16/32/48) and
`apple-touch-icon.png` (180x180) are cropped from `headshot.jpg` tighter than the on-page
circle, because a head-and-shoulders photo is unreadable at 16px. They were produced with
`magick headshot.jpg -auto-orient -strip -crop 440x440+115+55 +repage` into a working file,
then resized; the `-auto-orient` before `-strip` ordering is the same and non-negotiable.
Regenerate them only if the headshot itself changes.
The `projects/` screenshots follow the same rule with the display size as the resize geometry:
`magick <in> -auto-orient -crop <geom> +repage -strip -resize 1080x450 -quality 82 <out>`, the
crop being what brings each source to the shared 12:5 ratio the three cards need (decision 45).
The three sources live outside this repository and only the stripped results are committed. The
**Chalk source was a full-desktop capture and its crop is a privacy crop, not a composition
choice**: the discarded region held browser chrome, the macOS dock, and a video-call overlay
showing two identifiable bystanders. Do not widen that crop, re-derive `projects/chalk.png`
from a fuller frame, or restore the removed area — the in-app "Nico" tutor avatar that remains
is product UI and is the only face the file may carry.
The patient names visible in `projects/patientscope-ai.png` are **owner-confirmed synthetic
placeholders** (decision 55), confirmed before the file shipped because git history is public
and permanent. That file ships exactly as committed — do not re-crop, blur, or re-export it, and
do not re-open the question. It is a confirmation, not a licence: the next screenshot showing
anything that reads as personal data needs its own, on the same terms.

The `logos/` company marks are the other exception, and they split by file type. The two rasters
(`996-ventures.png`, `scottylabs.png`) take the strip command with the same flag order
(`magick <in> -auto-orient -strip ... -quality 82 <out>`), but the resize geometry is the display
size, not `1600x1600>`. The two SVGs (`corgi.svg`, `scurry.svg`) are text files, so `magick` is
the wrong tool for them and `no-image-metadata` does not reach them either — the checker's
`IMAGE_SUFFIXES` is `.jpg`/`.jpeg`/`.png` only, so nothing in CI polices an SVG. Clear a committed
SVG by reading it: no `<metadata>` block, no generator comment, and no external `href`, which
zero external requests would forbid anyway. Two marks carried a file-level defect that had to be
corrected before they were usable, and the corrections are recorded in decision 41 rather than
repeated here. Do not recolour, crop, or restyle a mark: using it as published is what keeps
nominative use of an employer's logo straightforward.
Make the change asked for and nothing else.

Most of these are enforced in CI by `.github/scripts/check-design-rules.py`, which runs on
every push and pull request. Run it locally before pushing a visual change; a failure names
the rule and where it fired. It is a guard, not the specification — `PRD.md` §9 is.
`.github/scripts/test-design-rules.py` runs beside it in the same job and pins the parts of
the checker that are easy to loosen by accident — which `<link>` elements
`zero-external-requests` permits (`PRD.md` decision 37), which selectors may carry a
`border-radius` (decision 49), and, since the checker started *discovering* public pages
rather than listing three, that post pages fall inside the walk and `admin/` falls outside
it. Run both.

Outbound links are allowlisted by destination in that script (`ALLOWED_LINK_PREFIXES`), so
any new absolute `href` on a hand-written page fails CI until it is added. The gate is
deliberate: a destination goes on the list only once the owner has confirmed it, and the
confirmation is recorded in the `PRD.md` decision log. Never add a guessed URL to clear the
check — leaving the text unlinked is the correct outcome for an unconfirmed destination.
The allowlist does **not** apply to a post under `blog/` (decision 61): a post's links are
typed by the owner in the editor, so they are confirmed by construction and the list would be
a false gate. Every other part of `zero-external-requests` binds a post page exactly as it
binds the front door — do not read the one exemption as a general one.

Post prose adds two live trade-offs that look like oversights and are not (decision 62).
`<code>` and `<pre>` declare a size from the site's own three and **no `font-family`**: §9
says "One family" and the checker fails a second declaration, so the face is left to the
browser's default for those elements. A blockquote is set off by **indent alone**, deeper
than a list, because §9 forbids borders-as-styling and a second text colour. Both are the
owner's to revisit; neither is yours to "fix".

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
