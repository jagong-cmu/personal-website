# Project agent memory

This file is the project's committed home for project-intrinsic agent knowledge: build, test, release, architecture, and sharp-edge notes that should travel with the code.

- Add durable project-specific notes here as they are discovered through real work.

## Current stage: static preview at the repo root

`index.html`, `journey.html`, `blog.html`, and `headshot.jpg` at the repo root are an
owner-approved static preview deployed on Vercel zero-config. They are intentionally
hand-written, self-contained (inline `<style>`, inline `<script>`, inline SVG), and have
**no build step, no framework, no package.json, and no dependencies**. Do not add any.
They will be deleted and replaced by the Next.js app in `PRD.md`, which is the source of
truth for the eventual architecture — never infer the stack from these files.

Each page duplicates the whole stylesheet and masthead, so any header or style change is a
three-way edit. That duplication is accepted for the preview and goes away in the Next.js
build.

## Binding visual constraints

`PRD.md` §9 is a list of prohibitions, not preferences, and the owner has rejected several
designs for unrequested "improvement". Before changing anything visual, read §9. The short
form: pure `#FFFFFF` background, system font stack only (no Google Fonts), at most three
type sizes, no shadows/gradients/coloured panels/animation/dark mode. The exceptions §9
grants are the inline-SVG social icons — near-black `#111111`, deliberately *not* the link
colour — and the circular headshot (the site's only non-zero `border-radius`).

Two further prohibitions bind this preview as owner decisions rather than §9 text, so do not
expect to find them there: **zero external requests** (no web fonts, no CDN, no `<link>`, no
external CSS/JS) and no phone number anywhere. Make the change asked for and nothing else.

Most of these are enforced in CI by `.github/scripts/check-design-rules.py`, which runs on
every push and pull request. Run it locally before pushing a visual change; a failure names
the rule and the offending line. It is a guard, not the specification — `PRD.md` §9 is.

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
