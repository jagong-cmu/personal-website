# drafts

Unpublished blog posts, one Markdown file per post, written and managed from `/admin`.
Nothing here is served.

A post's state is its location:

| Where | State |
|---|---|
| `drafts/<slug>.md` | Written, not published |
| `blog/<slug>.md` | Published — the source |
| `blog/<slug>.html` | Published — the page a reader gets |

Publishing moves the source from here to `blog/`, generates the page, and updates
`blog.html` and `sitemap.xml`, all in one commit. Unpublishing moves it back.

**Everything in this directory is withheld from the deployment by `.vercelignore`'s `*.md`
pattern, and that is the whole mechanism by which a draft is unreachable rather than merely
unlinked.** It matches on the extension and nothing else, so a single file here that is not
Markdown would be served publicly at its own URL to anyone who guessed it. CI's
`drafts-not-servable` rule (`.github/scripts/check-design-rules.py`) fails the build on one
rather than leaving it to be noticed. Do not narrow the `*.md` pattern, and do not put a
non-Markdown file here.

This file is itself Markdown, so requesting `/drafts/README.md` on any deployment is a
direct check that the exclusion is live — it should 404.

Editing a file here by hand works, but `/admin` is the intended path: it writes the
frontmatter this repository expects and keeps the published index consistent. See
`AGENTS.md` for the admin's design notes and `PRD.md` §6 for the specification.
