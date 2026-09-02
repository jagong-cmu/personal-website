'use strict';

// Tests for the two things in `api/` that a browser can reach with hostile or merely
// unlucky input, and that nothing else in CI would notice.
//
// The renderer writes one `<script>` on a public post page — the JSON-LD block — and it is
// the only place a post's own words reach the output without passing through `escapeHtml`.
// Valid JSON is not the same as safe-inside-a-script-element, so both are asserted.
//
// The content operations are exercised against a GitHub stub that refuses a tree entry with
// a null sha for a path that is not in the base tree, which is what the real create-tree
// endpoint does. A stub that quietly accepted one hid a failure on the ordinary first
// publish: `publish()` staged `drafts/<slug>.md` for deletion whether or not a draft had
// ever been saved.
//
// Standard library only, no package.json, no dependencies (PRD decision 58). Run it from
// the repository root:
//
//     node .github/scripts/test-api.js

const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const path = require('node:path');

const API_BASE = 'https://api.github.test';
process.env.GITHUB_TOKEN = 'test-token';
process.env.GITHUB_API_BASE = API_BASE;
process.env.GITHUB_REPO = 'owner/repo';
process.env.GITHUB_BRANCH = 'main';

const LIB = path.join(__dirname, '..', '..', 'api', '_lib');
const render = require(path.join(LIB, 'render'));
const content = require(path.join(LIB, 'content'));

// --- the GitHub stub --------------------------------------------------------------------
// A repository as a path -> text map, reached only through the endpoints `api/_lib/github.js`
// actually calls. Blobs, trees, commits, and the ref are all real objects here, so "one
// commit per operation" is something the tests can count rather than assume.

const BLOG_HTML = `<!DOCTYPE html>
<html lang="en">
<head>
<meta name="description" content="Writing about the tools I build and the people who have to use them. No posts yet; the first is being written.">
<style>
body { background: #FFFFFF; font-family: system-ui, sans-serif; }
</style>
</head>
<body>
<div class="page">

  <header>
    <div class="masthead"><img src="headshot.jpg" alt="Jonathan Gong"></div>
  </header>

  <main>
    <p>No posts yet. The first one is being written.</p>
    <p class="note" style="margin-top:24px">Notes on what I&rsquo;m building.</p>

  </main>

</div>
</body>
</html>
`;

const SITEMAP_XML = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://jonathangong.com/blog.html</loc>
  </url>
</urlset>
`;

const repo = {
  files: new Map(),
  blobs: new Map(),
  trees: new Map(),
  commits: new Map(),
  head: null,
  commitCount: 0,
  rejectedDeletes: [],
};

function digest(value) {
  return crypto.createHash('sha1').update(value).digest('hex');
}

function snapshotTree(files) {
  const entries = [...files.entries()].sort(([a], [b]) => (a < b ? -1 : 1));
  const sha = digest(JSON.stringify(entries));
  repo.trees.set(sha, new Map(entries));
  return sha;
}

function seedRepository() {
  repo.files = new Map([['blog.html', BLOG_HTML], ['sitemap.xml', SITEMAP_XML]]);
  repo.blobs = new Map();
  repo.trees = new Map();
  repo.commits = new Map();
  repo.rejectedDeletes = [];
  repo.commitCount = 1;
  const tree = snapshotTree(repo.files);
  const commit = digest(`commit:${tree}`);
  repo.commits.set(commit, { tree });
  repo.head = commit;
}

function reply(status, body) {
  return {
    status,
    ok: status >= 200 && status < 300,
    async json() { return body; },
    async text() { return JSON.stringify(body); },
  };
}

function contentsResponse(target) {
  if (repo.files.has(target)) {
    return reply(200, {
      content: Buffer.from(repo.files.get(target), 'utf8').toString('base64'),
      encoding: 'base64',
    });
  }
  const prefix = `${target}/`;
  const children = [...repo.files.keys()].filter((name) => name.startsWith(prefix));
  if (children.length === 0) return reply(404, { message: 'Not Found' });
  return reply(200, children.map((name) => ({ type: 'file', name: name.slice(prefix.length) })));
}

function createTree(body) {
  const base = repo.trees.get(body.base_tree);
  if (!base) return reply(422, { message: 'base_tree not found' });
  const next = new Map(base);
  for (const entry of body.tree) {
    if (entry.sha === null) {
      // What the real endpoint does, and the reason this stub exists: a null sha names a
      // path to delete, and a path that is not in the base tree cannot be deleted.
      if (!next.has(entry.path)) {
        repo.rejectedDeletes.push(entry.path);
        return reply(422, { message: `path ${entry.path} does not exist in the base tree` });
      }
      next.delete(entry.path);
      continue;
    }
    if (!repo.blobs.has(entry.sha)) return reply(422, { message: 'blob not found' });
    next.set(entry.path, repo.blobs.get(entry.sha));
  }
  return reply(201, { sha: snapshotTree(next) });
}

globalThis.fetch = async (url, init = {}) => {
  const request = new URL(url);
  const suffix = request.pathname.replace('/repos/owner/repo', '');
  const method = init.method || 'GET';
  const body = init.body ? JSON.parse(init.body) : null;

  if (method === 'GET' && suffix.startsWith('/contents/')) {
    return contentsResponse(decodeURIComponent(suffix.slice('/contents/'.length)));
  }
  if (method === 'GET' && suffix === '/git/ref/heads/main') {
    return reply(200, { object: { sha: repo.head } });
  }
  if (method === 'GET' && suffix.startsWith('/git/commits/')) {
    const commit = repo.commits.get(suffix.slice('/git/commits/'.length));
    return commit ? reply(200, { tree: { sha: commit.tree } }) : reply(404, {});
  }
  if (method === 'POST' && suffix === '/git/blobs') {
    const sha = digest(`blob:${body.content}`);
    repo.blobs.set(sha, body.content);
    return reply(201, { sha });
  }
  if (method === 'POST' && suffix === '/git/trees') {
    return createTree(body);
  }
  if (method === 'POST' && suffix === '/git/commits') {
    const sha = digest(`commit:${body.tree}:${body.message}:${repo.commitCount}`);
    repo.commits.set(sha, { tree: body.tree });
    return reply(201, { sha });
  }
  if (method === 'PATCH' && suffix === '/git/refs/heads/main') {
    repo.head = body.sha;
    repo.files = new Map(repo.trees.get(repo.commits.get(body.sha).tree));
    repo.commitCount += 1;
    return reply(200, {});
  }
  throw new Error(`the stub has no route for ${method} ${suffix}`);
};

// --- the runner -------------------------------------------------------------------------
// Plain and stdlib-only, for the same reason the site has no build step: nothing here needs
// a framework, and one that came with a version floor would be one more thing to keep true.

const cases = [];
function test(name, run) { cases.push({ name, run }); }

async function refused(promise) {
  try {
    await promise;
  } catch (error) {
    return error;
  }
  return assert.fail('expected the call to be refused, but it resolved');
}

const post = (extra) => ({
  slug: 'a-post',
  title: 'A post',
  date: '2026-09-01',
  summary: 'One line about the post.',
  markdown: 'Hello.',
  ...extra,
});

// --- the JSON-LD block ------------------------------------------------------------------

function jsonLdOf(page) {
  const opened = page.indexOf('<script type="application/ld+json">');
  assert.notEqual(opened, -1, 'the post page carries no JSON-LD block');
  const start = opened + '<script type="application/ld+json">'.length;
  const end = page.indexOf('</script>', start);
  return { text: page.slice(start, end), rest: page.slice(end) };
}

test('a title containing </script> stays inside the JSON-LD block', () => {
  const title = 'Escaping </script><img src=x onerror=alert(1)>';
  const page = render.postPage(post({ title }), BLOG_HTML);

  assert.equal(page.includes('<img src=x onerror=alert(1)>'), false,
    'author text broke out of the script element and reached the page as live markup');
  const { text, rest } = jsonLdOf(page);
  assert.equal(JSON.parse(text).headline, title);
  assert.equal(rest.startsWith('</script>'), true);
});

test('a summary containing </script> stays inside the JSON-LD block', () => {
  const summary = 'Closing with </SCRIPT > and carrying on.';
  const page = render.postPage(post({ summary }), BLOG_HTML);
  assert.equal(JSON.parse(jsonLdOf(page).text).description, summary);
});

test('the line separators JSON allows raw are escaped', () => {
  const title = 'Line\u2028separator\u2029here';
  const page = render.postPage(post({ title }), BLOG_HTML);
  const { text } = jsonLdOf(page);
  assert.equal(/[\u2028\u2029]/.test(text), false, 'U+2028 or U+2029 survived raw');
  assert.equal(JSON.parse(text).headline, title);
});

test('ordinary metadata still round-trips through the block', () => {
  const page = render.postPage(post(), BLOG_HTML);
  const data = JSON.parse(jsonLdOf(page).text);
  assert.equal(data.headline, 'A post');
  assert.equal(data.datePublished, '2026-09-01');
  assert.equal(data.url, 'https://jonathangong.com/blog/a-post.html');
});

// --- publishing -------------------------------------------------------------------------

test('a post published without ever being saved as a draft lands in one commit', async () => {
  seedRepository();
  const before = repo.commitCount;
  const result = await content.publish(post({ create: true }));

  assert.equal(repo.rejectedDeletes.length, 0,
    `staged a delete for a path that was never written: ${repo.rejectedDeletes.join(', ')}`);
  assert.equal(repo.commitCount, before + 1, 'a publish is exactly one commit');
  assert.equal(typeof result.commit, 'string');
  assert.equal(repo.files.has('blog/a-post.html'), true);
  assert.equal(repo.files.has('blog/a-post.md'), true);
  assert.equal(repo.files.has('drafts/a-post.md'), false);
  assert.equal(repo.files.get('blog.html').includes('href="blog/a-post.html"'), true);
  assert.equal(repo.files.get('sitemap.xml').includes('/blog/a-post.html'), true);
});

test('publishing a saved draft moves it out in one commit', async () => {
  seedRepository();
  await content.save(post({ create: true }));
  assert.equal(repo.files.has('drafts/a-post.md'), true);

  const before = repo.commitCount;
  await content.publish(post());
  assert.equal(repo.commitCount, before + 1);
  assert.equal(repo.files.has('drafts/a-post.md'), false);
  assert.equal(repo.files.has('blog/a-post.html'), true);
});

test('republishing an already published post succeeds', async () => {
  seedRepository();
  await content.publish(post({ create: true }));
  const before = repo.commitCount;

  await content.publish(post({ title: 'A post, revised' }));
  assert.equal(repo.rejectedDeletes.length, 0);
  assert.equal(repo.commitCount, before + 1);
  assert.equal(repo.files.get('blog/a-post.html').includes('A post, revised'), true);
});

test('unpublishing and republishing round-trips', async () => {
  seedRepository();
  await content.publish(post({ create: true }));
  await content.unpublish('a-post');
  assert.equal(repo.files.has('drafts/a-post.md'), true);
  assert.equal(repo.files.has('blog/a-post.html'), false);

  await content.publish(post());
  assert.equal(repo.rejectedDeletes.length, 0);
  assert.equal(repo.files.has('drafts/a-post.md'), false);
  assert.equal(repo.files.has('blog/a-post.html'), true);
});

// --- the slug is not taken twice ----------------------------------------------------------

test('a new post may not be written over an existing draft', async () => {
  seedRepository();
  await content.save(post({ create: true }));
  const before = repo.commitCount;

  const error = await refused(content.save(post({ create: true, title: 'A different post' })));
  assert.equal(error instanceof content.ContentError, true);
  assert.equal(error.status, 409);
  assert.match(error.message, /already exists/i);
  assert.equal(repo.commitCount, before, 'the refused save must commit nothing');
  assert.equal(repo.files.get('drafts/a-post.md').includes('A post'), true);
});

test('a new post may not be written over a published one', async () => {
  seedRepository();
  await content.publish(post({ create: true }));
  const before = repo.commitCount;

  const error = await refused(content.save(post({ create: true, title: 'A different post' })));
  assert.equal(error.status, 409);
  assert.equal(repo.commitCount, before);
  assert.equal(repo.files.get('blog/a-post.md').includes('A post'), true);
});

test('a new post may not be published over an existing one', async () => {
  seedRepository();
  await content.save(post({ create: true }));
  const before = repo.commitCount;

  const error = await refused(content.publish(post({ create: true, title: 'A different post' })));
  assert.equal(error.status, 409);
  assert.equal(repo.commitCount, before);
});

test('editing a post the editor has already saved still overwrites it', async () => {
  seedRepository();
  await content.save(post({ create: true }));

  await content.save(post({ title: 'A post, revised' }));
  assert.equal(repo.files.get('drafts/a-post.md').includes('A post, revised'), true);
});

test('the first save of a new post is not refused by its own absence', async () => {
  seedRepository();
  const result = await content.save(post({ create: true }));
  assert.equal(typeof result.commit, 'string');
  assert.equal(repo.files.has('drafts/a-post.md'), true);
});

// --- deleting -----------------------------------------------------------------------------

test('deleting the last published post restores blog.html and sitemap.xml', async () => {
  seedRepository();
  await content.publish(post({ create: true }));
  await content.remove('a-post');

  assert.equal(repo.rejectedDeletes.length, 0);
  assert.equal(repo.files.has('blog/a-post.html'), false);
  assert.equal(repo.files.has('blog/a-post.md'), false);
  assert.equal(repo.files.get('blog.html'), BLOG_HTML);
  assert.equal(repo.files.get('sitemap.xml'), SITEMAP_XML);
});

(async function main() {
  let failed = 0;
  for (const item of cases) {
    try {
      await item.run();
      console.log(`ok   ${item.name}`);
    } catch (error) {
      failed += 1;
      console.log(`FAIL ${item.name}\n     ${error && error.message}`);
    }
  }
  console.log(`\n${cases.length - failed} passed, ${failed} failed.`);
  process.exit(failed ? 1 : 0);
}());
