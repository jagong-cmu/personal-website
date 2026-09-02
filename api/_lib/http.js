'use strict';

// Request/response plumbing shared by every endpoint. Vercel hands a Node
// ServerResponse with Express-flavoured helpers bolted on; nothing here uses those
// helpers, so the same handlers run unchanged under the plain Node server used for
// local testing.

const MAX_BODY_BYTES = 512 * 1024;

// The site's own origin, plus the deploy URLs Vercel generates for it. A state-changing
// request that names an Origin outside this set is rejected: SameSite=Strict already
// keeps the session cookie off cross-site requests, and this is the second, independent
// check that does not depend on the browser honouring it.
function isTrustedOrigin(origin, host) {
  if (!origin) return true; // Same-origin fetch may omit it; SameSite is the guard there.
  let parsed;
  try {
    parsed = new URL(origin);
  } catch (_) {
    return false;
  }
  if (parsed.protocol !== 'https:' && parsed.protocol !== 'http:') return false;
  return parsed.host === host;
}

function send(res, status, body, headers) {
  res.statusCode = status;
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Referrer-Policy', 'no-referrer');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Robots-Tag', 'noindex, nofollow');
  for (const [name, value] of Object.entries(headers || {})) res.setHeader(name, value);
  if (body === undefined || body === null) {
    res.end();
    return;
  }
  const text = JSON.stringify(body);
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.end(text);
}

// Failures carry no detail. A caller who is not signed in learns only that; a caller who
// asked for something impossible learns only that. Nothing echoes a path, a token, an
// environment variable, or an upstream GitHub message back to the browser.
function fail(res, status, message) {
  send(res, status, { error: message });
}

async function readJsonBody(req) {
  if (req.body !== undefined && req.body !== null) {
    if (typeof req.body === 'string') {
      if (req.body === '') return {};
      return JSON.parse(req.body);
    }
    if (Buffer.isBuffer(req.body)) return JSON.parse(req.body.toString('utf8') || '{}');
    if (typeof req.body === 'object') return req.body;
  }
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > MAX_BODY_BYTES) throw new Error('body too large');
    chunks.push(chunk);
  }
  const text = Buffer.concat(chunks).toString('utf8');
  if (!text.trim()) return {};
  return JSON.parse(text);
}

function query(req) {
  if (req.query && typeof req.query === 'object') return req.query;
  const url = new URL(req.url, 'http://localhost');
  return Object.fromEntries(url.searchParams.entries());
}

function pathnameOf(req) {
  return new URL(req.url, 'http://localhost').pathname;
}

module.exports = { MAX_BODY_BYTES, isTrustedOrigin, send, fail, readJsonBody, query, pathnameOf };
