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

## Stack

Next.js (App Router) · MDX · Tailwind · deployed on Vercel.

Content lives in this repository as MDX. There is no database. The admin writes posts
and timeline entries back to the repo as commits, so all content carries free version
history, backups, and rollback.

Images are stored in-repo and pre-optimized at build time with `sharp`, which keeps the
site off metered runtime image optimization entirely.

## Development

```sh
npm install
npm run dev
```

## License

Content and images © Jonathan Gong. Code is available for reference.
