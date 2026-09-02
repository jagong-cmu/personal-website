'use strict';

// List, read, save as draft, preview, and delete.
//
// The session check is the first thing every branch does, including the read-only ones.
// A missing or invalid session returns 401 and the handler does nothing else: it does not
// reach GitHub, does not report whether a slug exists, and does not distinguish an expired
// session from an absent one.

const { hasValidSession } = require('./_lib/session');
const { send, fail, readJsonBody, query, isTrustedOrigin } = require('./_lib/http');
const { ContentError, save, remove } = require('./_lib/content');
const { renderMarkdown } = require('./_lib/markdown');
const posts = require('./_lib/posts');

function reportServerError(res, error, where) {
  if (error instanceof ContentError) return fail(res, error.status, error.message);
  // An upstream message can name a token scope or a repository path. It goes to the
  // function log; the browser gets nothing it did not already know.
  console.error('%s: %s', where, error && error.stack ? error.stack : error);
  return fail(res, 500, 'Something went wrong. Try again.');
}

module.exports = async function handler(req, res) {
  if (!hasValidSession(req)) return fail(res, 401, 'Not signed in.');

  try {
    if (req.method === 'GET') {
      const slug = String(query(req).slug || '').trim();
      if (!slug) return send(res, 200, { posts: await posts.list() });
      if (!posts.isValidSlug(slug)) return fail(res, 400, 'Unknown post.');
      const post = await posts.load(slug);
      if (!post) return fail(res, 404, 'Unknown post.');
      return send(res, 200, { post });
    }

    if (req.method === 'POST' || req.method === 'DELETE') {
      if (!isTrustedOrigin(req.headers.origin, req.headers.host)) {
        return fail(res, 403, 'Request rejected.');
      }
      let body;
      try {
        body = await readJsonBody(req);
      } catch (_) {
        return fail(res, 400, 'Bad request.');
      }

      if (req.method === 'DELETE') {
        const result = await remove(String(body && body.slug || '').trim());
        return send(res, 200, result);
      }

      // Preview runs the same converter the published page is built with, so what the
      // editor shows is what the post will say — not a second, drifting renderer.
      if (body && body.action === 'preview') {
        return send(res, 200, { html: renderMarkdown(body.markdown) });
      }

      return send(res, 200, await save(body));
    }

    return fail(res, 405, 'Method not allowed.');
  } catch (error) {
    return reportServerError(res, error, 'posts');
  }
};
