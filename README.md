# personal-website

Personal site for Jonathan Gong — portfolio, writing, and a photographic timeline.

Live at: <https://jonathangong.com>

## What this is

A recruiter-facing front door with personal depth behind it:

| Route | Purpose |
|---|---|
| `/` | Front door shell — opens on About |
| `/#about` | About |
| `/#work` | Work experience |
| `/#projects` | Projects |
| `/journey.html` | Photographic timeline (excluded from search engines) |
| `/blog.html` | Writing |
| `/admin` | Authenticated content management (not built yet) |

This table describes the **live static preview**. Section 4 of [`PRD.md`](./PRD.md) owns the
eventual route shape (`/journey`, `/blog`, `/blog/[slug]`), which the Next.js build will move to.

See [`PRD.md`](./PRD.md) for the full product requirements and the reasoning behind
every decision.

## Current state: static preview (temporary)

The `index.html`, `journey.html`, `blog.html`, and `headshot.jpg` files at the repository
root, together with the `journey/` photographs, the `logos/` company marks, the
`favicon.ico` and `apple-touch-icon.png` icons, and `robots.txt` / `sitemap.xml`, are the
**owner-approved static preview**, and they are what is live in production today at
<https://jonathangong.com>, deployed on Vercel zero-config. This is the public site at the
owner's own domain, not a review link. They are hand-written HTML with an inline `<style>`
block and no build step, no framework, and no dependencies — deliberately.

**Being live does not make them permanent.** They are not the intended architecture and
will be deleted. They will be REPLACED by the Next.js application described in
[`PRD.md`](./PRD.md), which remains the source of truth for the eventual build. Do not
extend the static files, and do not read them as a statement about the stack — the "Stack"
section below is what this repository is going to become.

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
