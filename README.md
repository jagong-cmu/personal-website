# personal-website

Personal site for Jonathan Gong — portfolio, writing, and a photographic timeline.

Live at: _(not yet deployed)_

## What this is

A recruiter-facing front door with personal depth behind it:

| Route | Purpose |
|---|---|
| `/` | Front door — about, work experience, featured projects, awards, links |
| `/projects` | Full curated project list |
| `/journey` | Era-chaptered photographic timeline (excluded from search engines) |
| `/blog` | Writing |
| `/admin` | Authenticated content management |

See [`PRD.md`](./PRD.md) for the full product requirements and the reasoning behind
every decision.

## Current state: static preview (temporary)

The `index.html`, `journey.html`, `blog.html`, and `headshot.jpg` files at the repository
root are the **captain-approved static preview**, deployed on Vercel zero-config so the
design can be reviewed on a real URL. They are hand-written HTML with an inline `<style>`
block and no build step, no framework, and no dependencies — deliberately.

**They are not the intended architecture and will be deleted.** They will be REPLACED by
the Next.js application described in [`PRD.md`](./PRD.md), which remains the source of
truth for the eventual build. Do not extend the static files, and do not read them as a
statement about the stack — the "Stack" section below is what this repository is going to
become.

## Stack

Next.js (App Router) · MDX · Tailwind · deployed on Vercel.

Content lives in this repository as MDX. There is no database. The admin writes posts
and timeline entries back to the repo as commits, so all content carries free version
history, backups, and rollback.

Images are stored in-repo and pre-optimized at build time with `sharp`, which keeps the
site off metered runtime image optimization entirely.

## Development

The static preview needs no tooling — open `index.html` in a browser. The commands below
apply once the Next.js application replaces it.

```sh
npm install
npm run dev
```

## License

Content and images © Jonathan Gong. Code is available for reference.
