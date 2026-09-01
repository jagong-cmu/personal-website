'use strict';

// The post model, and the one place a slug is validated.
//
// State is location, not a flag:
//
//   drafts/<slug>.md      an unpublished post — source only
//   blog/<slug>.md        a published post's source
//   blog/<slug>.html      a published post's page
//
// Both `.md` trees are withheld from the deployment by `.vercelignore`'s `*.md`, so no
// post source is ever publicly reachable whatever its state. Keeping the published source
// beside its page is what makes "edit again after publishing" a normal edit rather than an
// attempt to parse HTML back into Markdown.

const { readFile, listDirectory } = require('./github');

const DRAFTS_DIR = 'drafts';
const BLOG_DIR = 'blog';

// PRD section 4's slug shape. Every write path in this system is built from a slug, so an
// unvalidated one is a path-traversal hole: `..`, a slash, a leading dot, and a percent
// escape are all rejected by construction rather than by a blocklist.
const SLUG = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const MAX_SLUG_LENGTH = 80;

function isValidSlug(slug) {
  return typeof slug === 'string' && slug.length > 0
    && slug.length <= MAX_SLUG_LENGTH && SLUG.test(slug);
}

const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;

function isValidDate(date) {
  if (typeof date !== 'string' || !ISO_DATE.test(date)) return false;
  const parsed = new Date(`${date}T00:00:00Z`);
  return !Number.isNaN(parsed.getTime()) && parsed.toISOString().slice(0, 10) === date;
}

const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'];

// `2026-09-01` -> `September 1, 2026`, matching the Month-Year voice of `.entry-meta`
// elsewhere on the site with the day a post needs added.
function displayDate(date) {
  if (!isValidDate(date)) return date;
  const [year, month, day] = date.split('-');
  return `${MONTHS[Number(month) - 1]} ${Number(day)}, ${year}`;
}

// --- frontmatter -------------------------------------------------------------------------
// A tiny fixed-key format, not YAML. Four known scalar keys, one per line, values stored
// as JSON strings so a colon, a quote, or a newline in a title needs no escaping rules of
// its own.

const FIELDS = ['title', 'date', 'summary'];

function serialize(post) {
  const head = FIELDS.map((key) => `${key}: ${JSON.stringify(post[key] == null ? '' : String(post[key]))}`);
  return `---\n${head.join('\n')}\n---\n\n${String(post.markdown == null ? '' : post.markdown).replace(/\r\n?/g, '\n').trimEnd()}\n`;
}

function parse(text) {
  const source = String(text == null ? '' : text).replace(/\r\n?/g, '\n');
  const match = source.match(/^---\n([\s\S]*?)\n---\n?/);
  const post = { title: '', date: '', summary: '', markdown: source };
  if (!match) return post;
  for (const line of match[1].split('\n')) {
    const at = line.indexOf(':');
    if (at < 0) continue;
    const key = line.slice(0, at).trim();
    if (!FIELDS.includes(key)) continue;
    const raw = line.slice(at + 1).trim();
    try {
      post[key] = String(JSON.parse(raw));
    } catch (_) {
      post[key] = raw;
    }
  }
  post.markdown = source.slice(match[0].length).replace(/^\n+/, '');
  return post;
}

// --- repository access ---------------------------------------------------------------------

function draftPath(slug) { return `${DRAFTS_DIR}/${slug}.md`; }
function sourcePath(slug) { return `${BLOG_DIR}/${slug}.md`; }
function pagePath(slug) { return `${BLOG_DIR}/${slug}.html`; }
function publicUrl(slug) { return `https://jonathangong.com/${BLOG_DIR}/${slug}.html`; }

/** Read one post wherever it lives, or null. Never touches a caller-supplied path. */
async function load(slug) {
  if (!isValidSlug(slug)) return null;
  const published = await readFile(sourcePath(slug));
  if (published !== null) return { slug, published: true, ...parse(published) };
  const draft = await readFile(draftPath(slug));
  if (draft !== null) return { slug, published: false, ...parse(draft) };
  return null;
}

/**
 * Which of a slug's files are really there: `{ draft, published }`.
 *
 * `load` answers "which post is this" and stops at the first file it finds. A write needs
 * the other question — which paths exist — because a delete staged for a path that is not
 * in the tree is rejected by the Git Data API, and because a slug nothing occupies is not
 * the same as one whose draft happens to be missing.
 */
async function locate(slug) {
  if (!isValidSlug(slug)) return { draft: false, published: false };
  const [source, draft] = await Promise.all([
    readFile(sourcePath(slug)),
    readFile(draftPath(slug)),
  ]);
  return { draft: draft !== null, published: source !== null };
}

function slugsIn(names) {
  return names
    .filter((name) => name.endsWith('.md'))
    .map((name) => name.slice(0, -3))
    .filter(isValidSlug);
}

/** Every post, newest first. Ties break on slug so the order is stable. */
async function list() {
  const [draftNames, blogNames] = await Promise.all([
    listDirectory(DRAFTS_DIR),
    listDirectory(BLOG_DIR),
  ]);
  const wanted = [
    ...slugsIn(draftNames).map((slug) => ({ slug, published: false })),
    ...slugsIn(blogNames).map((slug) => ({ slug, published: true })),
  ];
  const posts = await Promise.all(wanted.map(async ({ slug, published }) => {
    const text = await readFile(published ? sourcePath(slug) : draftPath(slug));
    if (text === null) return null;
    const { title, date, summary } = parse(text);
    return { slug, published, title, date, summary };
  }));
  return posts.filter(Boolean).sort(compare);
}

function compare(a, b) {
  if (a.date !== b.date) return a.date < b.date ? 1 : -1;
  return a.slug < b.slug ? 1 : -1;
}

module.exports = {
  DRAFTS_DIR,
  BLOG_DIR,
  MAX_SLUG_LENGTH,
  isValidSlug,
  isValidDate,
  displayDate,
  serialize,
  parse,
  draftPath,
  sourcePath,
  pagePath,
  publicUrl,
  load,
  locate,
  list,
  compare,
};
