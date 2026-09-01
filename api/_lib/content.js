'use strict';

// The four content operations, each landing as exactly ONE commit (PRD section 6).
//
// Every one of them recomputes the whole published set and rewrites `blog.html` and
// `sitemap.xml` from it, rather than patching a line in or out. That is why publishing,
// unpublishing, editing, and deleting all converge on the same file contents instead of
// each leaving its own residue, and why deleting the last post restores `blog.html`'s
// original placeholder byte for byte.
//
// The set of paths a request can ever touch is fixed here and derived from a validated
// slug: `drafts/<slug>.md`, `blog/<slug>.md`, `blog/<slug>.html`, `blog.html`, and
// `sitemap.xml`. Nothing accepts a path from the browser.

const { readFile, commitChanges } = require('./github');
const posts = require('./posts');
const render = require('./render');

const INDEX_PAGE = 'blog.html';
const SITEMAP = 'sitemap.xml';

class ContentError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

function validate(input) {
  const slug = String(input && input.slug || '').trim();
  if (!posts.isValidSlug(slug)) {
    throw new ContentError(400, 'Slug must be lower-case words separated by single hyphens.');
  }
  const title = String(input.title == null ? '' : input.title).trim();
  if (!title) throw new ContentError(400, 'A title is required.');
  if (title.length > 200) throw new ContentError(400, 'Title is too long.');

  const date = String(input.date == null ? '' : input.date).trim();
  if (!posts.isValidDate(date)) throw new ContentError(400, 'Date must be a real YYYY-MM-DD date.');

  const summary = String(input.summary == null ? '' : input.summary).trim();
  if (!summary) throw new ContentError(400, 'A one-line summary is required; it is the post’s description.');
  if (summary.length > 400) throw new ContentError(400, 'Summary is too long.');

  const markdown = String(input.markdown == null ? '' : input.markdown);
  if (markdown.length > 200000) throw new ContentError(400, 'Post is too long.');

  return { slug, title, date, summary, markdown };
}

const SLUG_TAKEN = 'A post already exists at that slug. Choose a different title or slug.';

/**
 * Where the slug's files are, having first refused to write a NEW post over an existing one.
 *
 * The editor derives a slug from the title and only freezes it once the post has been
 * saved, so two posts whose titles slugify alike would otherwise land on each other and the
 * first would survive only in git history. The server cannot tell a second post from a
 * re-save of the first by looking at the repository — both are a slug with a file behind it
 * — so the caller says which it is doing, and an edit is left exactly as it was.
 */
async function claimSlug(input, slug) {
  const where = await posts.locate(slug);
  const creating = !!(input && input.create === true);
  if (creating && (where.draft || where.published)) throw new ContentError(409, SLUG_TAKEN);
  return where;
}

/**
 * Rewrite the two index files for a given published set, and add them to `changes`.
 * `blogHtml` is the page as it stands; its stylesheet and masthead are what every post
 * page is built from, so it is read once and reused.
 */
async function reindex(changes, published, blogHtml) {
  const currentSitemap = await readFile(SITEMAP);
  if (currentSitemap === null) throw new ContentError(500, 'Site index is unavailable.');

  const ordered = published.slice().sort(posts.compare);
  changes[INDEX_PAGE] = render.blogIndex(blogHtml, ordered);
  changes[SITEMAP] = render.sitemap(currentSitemap, ordered);
}

async function loadIndexPage() {
  const blogHtml = await readFile(INDEX_PAGE);
  if (blogHtml === null) throw new ContentError(500, 'Site index is unavailable.');
  return blogHtml;
}

// The published set after an in-memory change: `next` replaces or removes the entry for
// its own slug, and nothing else moves.
async function publishedAfter(slug, next) {
  const all = await posts.list();
  const kept = all.filter((post) => post.published && post.slug !== slug);
  return next ? kept.concat([next]) : kept;
}

/**
 * Save a post's source.
 *
 * A draft is written to `drafts/` and touches nothing else. A post that is already
 * published is re-rendered in the same commit, because a published page must never be
 * stale relative to the source it came from. A post being created for the first time is
 * refused if its slug is already occupied; see `claimSlug`.
 */
async function save(input) {
  const post = validate(input);
  const where = await claimSlug(input, post.slug);
  const changes = {};

  if (where.published) {
    const blogHtml = await loadIndexPage();
    changes[posts.sourcePath(post.slug)] = posts.serialize(post);
    changes[posts.pagePath(post.slug)] = render.postPage(post, blogHtml);
    await reindex(changes, await publishedAfter(post.slug, { ...post, published: true }), blogHtml);
    return { commit: await commitChanges(changes, `content: update ${post.slug}`), post: { ...post, published: true } };
  }

  changes[posts.draftPath(post.slug)] = posts.serialize(post);
  return { commit: await commitChanges(changes, `content: save draft ${post.slug}`), post: { ...post, published: false } };
}

/** Move a draft to `blog/`, render its page, and relist it. One commit. */
async function publish(input) {
  const post = validate(input);
  const where = await claimSlug(input, post.slug);
  const blogHtml = await loadIndexPage();
  const changes = {};

  // The draft is staged for deletion only when there is one. A tree entry with a null sha
  // is rejected for a path that is not in the base tree, so the ordinary first publish —
  // written and published without ever pressing Save draft — would fail on a file that was
  // never created, and so would every republish after the first moved the draft out.
  if (where.draft) changes[posts.draftPath(post.slug)] = null;
  changes[posts.sourcePath(post.slug)] = posts.serialize(post);
  changes[posts.pagePath(post.slug)] = render.postPage(post, blogHtml);
  await reindex(changes, await publishedAfter(post.slug, { ...post, published: true }), blogHtml);

  return { commit: await commitChanges(changes, `content: publish ${post.slug}`), post: { ...post, published: true } };
}

/** Return a published post to draft: the page goes, the source moves back. One commit. */
async function unpublish(slug) {
  if (!posts.isValidSlug(slug)) throw new ContentError(400, 'Unknown post.');
  const existing = await posts.load(slug);
  if (!existing) throw new ContentError(404, 'Unknown post.');
  if (!existing.published) return { commit: null, post: existing };

  const blogHtml = await loadIndexPage();
  const changes = {};
  changes[posts.pagePath(slug)] = null;
  changes[posts.sourcePath(slug)] = null;
  changes[posts.draftPath(slug)] = posts.serialize(existing);
  await reindex(changes, await publishedAfter(slug, null), blogHtml);

  return { commit: await commitChanges(changes, `content: unpublish ${slug}`), post: { ...existing, published: false } };
}

/** Delete a post outright, in whichever state it is in. One commit. */
async function remove(slug) {
  if (!posts.isValidSlug(slug)) throw new ContentError(400, 'Unknown post.');
  const existing = await posts.load(slug);
  if (!existing) throw new ContentError(404, 'Unknown post.');

  const changes = {};
  if (existing.published) {
    const blogHtml = await loadIndexPage();
    changes[posts.pagePath(slug)] = null;
    changes[posts.sourcePath(slug)] = null;
    await reindex(changes, await publishedAfter(slug, null), blogHtml);
  } else {
    changes[posts.draftPath(slug)] = null;
  }

  return { commit: await commitChanges(changes, `content: delete ${slug}`), slug };
}

module.exports = { ContentError, validate, save, publish, unpublish, remove };
