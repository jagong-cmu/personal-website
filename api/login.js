'use strict';

// The password gate.
//
// PRD decision 59 replaced GitHub OAuth with this on the owner's instruction. What that
// gives up is stated there and not softened here: a password can be leaked, guessed, or
// reused in a way an OAuth identity cannot, and this endpoint is the only thing between
// the open internet and a commit to a live site under the owner's real name.
//
// So the defences, honestly labelled:
//
//   * the comparison is timing-safe (`crypto.timingSafeEqual` over SHA-256 digests, so
//     neither the value nor the length of the submitted password is leaked by timing);
//   * a failed attempt costs a fixed delay;
//   * repeated failures from one address are throttled — BEST EFFORT ONLY. Serverless
//     instances are stateless and independent, so the counter below lives in one warm
//     instance's memory and a distributed or patient attacker simply lands elsewhere. It
//     raises the cost of a naive script and nothing more.
//
// The real defence is the strength of `ADMIN_PASSWORD`. Nothing in this file substitutes
// for it.

const { hasValidSession, passwordMatches, issuedCookie, clearedCookie } = require('./_lib/session');
const { send, fail, readJsonBody, isTrustedOrigin } = require('./_lib/http');

const WINDOW_MS = 15 * 60 * 1000;
const MAX_FAILURES = 8;
const FAILURE_DELAY_MS = 700;

const failures = new Map();

function clientKey(req) {
  const forwarded = req.headers['x-forwarded-for'];
  const first = typeof forwarded === 'string' ? forwarded.split(',')[0].trim() : '';
  return first || req.headers['x-real-ip'] || (req.socket && req.socket.remoteAddress) || 'unknown';
}

function throttled(key, now) {
  const record = failures.get(key);
  if (!record || now - record.first > WINDOW_MS) return false;
  return record.count >= MAX_FAILURES;
}

function recordFailure(key, now) {
  const record = failures.get(key);
  if (!record || now - record.first > WINDOW_MS) {
    failures.set(key, { first: now, count: 1 });
  } else {
    record.count += 1;
  }
  // Unbounded growth is the other way a stateless throttle goes wrong. One warm instance
  // never needs more than a handful of entries.
  if (failures.size > 512) {
    for (const [entry, value] of failures) {
      if (now - value.first > WINDOW_MS) failures.delete(entry);
    }
  }
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

module.exports = async function handler(req, res) {
  // Whether a session is open. Costs nothing and reveals nothing; the admin page calls it
  // on load to decide which of its two views to show.
  if (req.method === 'GET') {
    return send(res, 200, { authenticated: hasValidSession(req) });
  }

  if (req.method === 'DELETE') {
    return send(res, 200, { authenticated: false }, { 'Set-Cookie': clearedCookie() });
  }

  if (req.method !== 'POST') {
    return fail(res, 405, 'Method not allowed.');
  }

  if (!isTrustedOrigin(req.headers.origin, req.headers.host)) {
    return fail(res, 403, 'Request rejected.');
  }

  const now = Date.now();
  const key = clientKey(req);
  if (throttled(key, now)) {
    await sleep(FAILURE_DELAY_MS);
    // Same body as a wrong password. A caller learns nothing about which of the two it hit.
    return fail(res, 401, 'Incorrect password.');
  }

  let body;
  try {
    body = await readJsonBody(req);
  } catch (_) {
    return fail(res, 400, 'Bad request.');
  }

  let cookie;
  try {
    if (!passwordMatches(body && body.password)) {
      recordFailure(key, now);
      await sleep(FAILURE_DELAY_MS);
      return fail(res, 401, 'Incorrect password.');
    }
    // Signing the session needs `SESSION_SECRET`, so it sits under the same guard as the
    // comparison that needs `ADMIN_PASSWORD`. Outside it, a deployment with one variable
    // set and the other missing would accept the password and then throw past this
    // handler, and the log line below — the only account anyone gets of it — never runs.
    cookie = issuedCookie(now);
  } catch (error) {
    // `ADMIN_PASSWORD` or `SESSION_SECRET` is not configured. Logged, never described to
    // the caller — an unconfigured gate must not advertise itself as one.
    console.error('login: %s', error.message);
    return fail(res, 500, 'Server error.');
  }

  failures.delete(key);
  return send(res, 200, { authenticated: true }, { 'Set-Cookie': cookie });
};
