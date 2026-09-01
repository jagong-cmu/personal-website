'use strict';

// Publish and unpublish.
//
// Publishing writes the post's page, moves its source out of `drafts/`, and rewrites
// `blog.html` and `sitemap.xml` — four or five paths in a SINGLE commit, as PRD section 6
// requires. That part of the spec was not changed by the 2026-09-01 overrides, and the
// reason it matters is unchanged too: a half-applied publish would leave a page listed but
// missing, or present but unlisted, in the window between commits.

const { hasValidSession } = require('./_lib/session');
const { send, fail, readJsonBody, isTrustedOrigin } = require('./_lib/http');
const { ContentError, publish, unpublish } = require('./_lib/content');

module.exports = async function handler(req, res) {
  if (!hasValidSession(req)) return fail(res, 401, 'Not signed in.');

  if (req.method !== 'POST') return fail(res, 405, 'Method not allowed.');
  if (!isTrustedOrigin(req.headers.origin, req.headers.host)) {
    return fail(res, 403, 'Request rejected.');
  }

  let body;
  try {
    body = await readJsonBody(req);
  } catch (_) {
    return fail(res, 400, 'Bad request.');
  }

  try {
    if (body && body.action === 'unpublish') {
      return send(res, 200, await unpublish(String(body.slug || '').trim()));
    }
    return send(res, 200, await publish(body));
  } catch (error) {
    if (error instanceof ContentError) return fail(res, error.status, error.message);
    console.error('publish: %s', error && error.stack ? error.stack : error);
    return fail(res, 500, 'Something went wrong. Try again.');
  }
};
