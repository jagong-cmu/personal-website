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
| `/blog.html` | Writing — lists published posts, newest first |
| `/blog/<slug>.html` | A published post. Generated at publish time, not hand-written |
| `/admin` | Blog admin: write, save drafts, publish, edit, delete. Password-gated |

See [`PRD.md`](./PRD.md) for the full product requirements and the reasoning behind
every decision.

## Current state

`index.html`, `journey.html` and `blog.html` at the repository root, together with
`headshot.jpg`, the `journey/` photographs, the `logos/` company marks, the `projects/`
screenshots, the root icons, and `robots.txt` / `sitemap.xml`, are the live site at
<https://jonathangong.com>, deployed on Vercel zero-config. They are hand-written HTML with
an inline `<style>` block and no build step, no framework, and no dependencies —
deliberately.

**These files used to be described here as a temporary preview that "will be deleted" and
replaced by a Next.js application. That is no longer true.** The owner rejected the stack
change on 2026-09-01 (`PRD.md` decision 58), and the admin was built on these pages rather
than on a framework. There is no replacement pending. Extending the static files is now the
normal way to work on this site.

What that costs is worth knowing before you edit anything: each page carries its own copy
of the whole stylesheet, so **a style change is an N-way edit**, and CI fails the build if
the copies drift. A generated post page does not carry a copy of its own — it lifts the
stylesheet and masthead out of `blog.html` when it is published, which is why a post can
never drift from the site's style.

## Stack

Hand-written static HTML · Node serverless functions in `api/` · deployed on Vercel
zero-config. No framework, no bundler, no `package.json`, no dependencies.

```
index.html, journey.html, blog.html   the hand-written pages
blog/<slug>.html                      a published post — generated
blog/<slug>.md                        its Markdown source — never served
drafts/<slug>.md                      an unpublished post — never served
admin/index.html                      the editor: one page, no dependencies
api/login.js                          password gate, signed session cookie
api/posts.js                          list, read, save draft, preview, delete
api/publish.js                        publish and unpublish
api/_lib/                             shared modules (a leading `_` keeps them off the routes)
```

Content lives in this repository as Markdown, so the site inherits free version history,
backups, and rollback. There is no database. **All content reads and writes go through the
GitHub API, never the deployed filesystem** — `.vercelignore` withholds `*.md` from the
deployment upload, and a just-committed file is not in the currently-running deployment
either. `.vercelignore` is also what keeps drafts unreachable; do not narrow it.

Images are stored in-repo and stripped of GPS and EXIF before they land — non-optionally,
because this repository is public (`PRD.md` §7.3 and §8). The exact command is in
[`AGENTS.md`](./AGENTS.md).

## Configuration

The admin needs three environment variables, set in Vercel and **nowhere in this
repository**:

| Variable | Purpose |
|---|---|
| `ADMIN_PASSWORD` | The gate. Its strength is the real defence — see `PRD.md` decision 59 |
| `SESSION_SECRET` | Signs the session cookie. Any long random string |
| `GITHUB_TOKEN` | Contents read/write on this repository. Server-side only |

`GITHUB_REPO` and `GITHUB_BRANCH` are optional overrides and default to
`jagong-cmu/personal-website` and `main`.

## Development

Open `index.html` in a browser; there is nothing to install. The `api/` functions need a
runtime, so exercise them with `vercel dev` or on a preview deployment.

Before pushing any visual change, run the checkers — CI runs the same three on every push:

```sh
python3 .github/scripts/check-design-rules.py
python3 .github/scripts/test-design-rules.py
node .github/scripts/test-api.js
```

The third exercises the content operations against a stub GitHub API, so a publish that
would be rejected upstream fails here first rather than on a live post.

## License

Content and images © Jonathan Gong. Code is available for reference.
