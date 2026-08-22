# Project agent memory

This file is the project's committed home for project-intrinsic agent knowledge: build, test, release, architecture, and sharp-edge notes that should travel with the code.

- Add durable project-specific notes here as they are discovered through real work.

## Current stage: static preview at the repo root

`index.html`, `journey.html`, `blog.html`, `headshot.jpg`, `journey/`, `logos/`, the root
icons, and `robots.txt` / `sitemap.xml` at the repo root are an owner-approved static
preview, **live in production on `jonathangong.com`** via Vercel zero-config. They are
intentionally hand-written, self-contained (inline `<style>`, inline `<script>`, inline
SVG), and have **no build step, no framework, no package.json, and no dependencies**. Do
not add any. They will be deleted and replaced by the Next.js app in `PRD.md`, which is
the source of truth for the eventual architecture — never infer the stack from these files.

Each page duplicates the whole stylesheet and masthead, so any header or style change is a
three-way edit. That duplication is accepted for the preview and goes away in the Next.js
build; CI's `stylesheets-identical` rule fails if the three inline stylesheets drift apart.
The mastheads legitimately differ — `index.html` does not wrap its own name in a self-link —
so they are not checked. The per-page `<head>` blocks differ on purpose too: every
description is distinct, and `journey.html` deliberately carries no canonical, Open Graph,
or structured data (`PRD.md` decision 38). Do not make the three heads uniform.

## Binding visual constraints

`PRD.md` §9 is a list of prohibitions, not preferences, and the owner has rejected several
designs for unrequested "improvement". Before changing anything visual, read §9. The short
form: pure `#FFFFFF` background, system font stack only (no Google Fonts), at most three
type sizes, no shadows/gradients/coloured panels/animation/dark mode. The exceptions §9
grants to those are the inline-SVG social icons — near-black `#111111`, deliberately *not*
the link colour — the circular headshot (the site's only non-zero `border-radius`), and the
**full-colour company logos in the Work panel** (`logos/`, `.entry-logo`, decision 41).
That last one is an owner override of "no badges" and of the palette limit, chosen over a
monochrome treatment firstmate recommended: do not desaturate it back, and do not read brand
colour in Work as licence anywhere else. Nothing may be drawn around a mark, and a company
whose logo source the owner has not confirmed carries none — Bizybear's empty slot is
correct (decision 30 covers logo sources as it covers links).

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
the checker that are easy to loosen by accident — chiefly which `<link>` elements
`zero-external-requests` permits (`PRD.md` decision 37). Run both.

Outbound links are allowlisted by destination in that script (`ALLOWED_LINK_PREFIXES`), so
any new absolute `href` fails CI until it is added. The gate is deliberate: a destination
goes on the list only once the owner has confirmed it, and the confirmation is recorded in
the `PRD.md` decision log. Never add a guessed URL to clear the check — leaving the text
unlinked is the correct outcome for an unconfirmed destination.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
