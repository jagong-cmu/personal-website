'use strict';

// The session cookie.
//
// PRD section 6 originally specified GitHub OAuth and stated that no password exists in
// this system. The owner replaced that with a password gate on 2026-09-01 (decision 59),
// so this file is the whole of the site's authentication. What it must never become is a
// bearer of the secret itself: the cookie carries a signed statement of *when* a session
// was opened and when it expires, and nothing else. `ADMIN_PASSWORD`, `SESSION_SECRET`,
// and `GITHUB_TOKEN` stay in the environment and never reach the browser.

const crypto = require('crypto');

const COOKIE_NAME = 'jg_admin';
const SESSION_SECONDS = 12 * 60 * 60;

function requiredEnv(name) {
  const value = process.env[name];
  if (!value) {
    // The message names the variable because it is read only in server logs. It never
    // reaches a response body — callers turn this into a bare 500.
    throw new Error(`${name} is not set`);
  }
  return value;
}

function base64url(buffer) {
  return Buffer.from(buffer).toString('base64')
    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function fromBase64url(text) {
  return Buffer.from(text.replace(/-/g, '+').replace(/_/g, '/'), 'base64');
}

function sign(payload) {
  return base64url(crypto.createHmac('sha256', requiredEnv('SESSION_SECRET')).update(payload).digest());
}

// Constant-time for equal-length inputs; `timingSafeEqual` throws on a length mismatch,
// so the lengths are compared first and a mismatch is simply false.
function equalsConstantTime(a, b) {
  const left = Buffer.from(String(a), 'utf8');
  const right = Buffer.from(String(b), 'utf8');
  if (left.length !== right.length) return false;
  return crypto.timingSafeEqual(left, right);
}

// The password comparison. Both sides are hashed first so that the length of the
// submitted password is not itself leaked by the length check above.
function passwordMatches(submitted) {
  const expected = requiredEnv('ADMIN_PASSWORD');
  if (typeof submitted !== 'string') return false;
  const a = crypto.createHash('sha256').update(submitted, 'utf8').digest();
  const b = crypto.createHash('sha256').update(expected, 'utf8').digest();
  return crypto.timingSafeEqual(a, b);
}

function issue(now = Date.now()) {
  const issued = Math.floor(now / 1000);
  const payload = base64url(JSON.stringify({ v: 1, iat: issued, exp: issued + SESSION_SECONDS }));
  return `${payload}.${sign(payload)}`;
}

function verifyToken(token, now = Date.now()) {
  if (typeof token !== 'string' || token.length > 512) return false;
  const parts = token.split('.');
  if (parts.length !== 2) return false;
  const [payload, signature] = parts;
  if (!equalsConstantTime(signature, sign(payload))) return false;
  let claims;
  try {
    claims = JSON.parse(fromBase64url(payload).toString('utf8'));
  } catch (_) {
    return false;
  }
  if (!claims || claims.v !== 1) return false;
  if (typeof claims.exp !== 'number') return false;
  return Math.floor(now / 1000) < claims.exp;
}

function parseCookies(header) {
  const jar = {};
  if (!header) return jar;
  for (const pair of String(header).split(';')) {
    const index = pair.indexOf('=');
    if (index < 0) continue;
    const name = pair.slice(0, index).trim();
    if (!name || Object.prototype.hasOwnProperty.call(jar, name)) continue;
    jar[name] = decodeURIComponent(pair.slice(index + 1).trim());
  }
  return jar;
}

// `Secure` is unconditional. Browsers treat http://localhost as a secure context, so the
// cookie is still stored during local testing and the deployed behaviour is never weaker
// than what was exercised here.
function cookieHeader(token, maxAge) {
  return [
    `${COOKIE_NAME}=${token}`,
    'HttpOnly',
    'Secure',
    'SameSite=Strict',
    'Path=/',
    `Max-Age=${maxAge}`,
  ].join('; ');
}

function issuedCookie(now = Date.now()) {
  return cookieHeader(issue(now), SESSION_SECONDS);
}

function clearedCookie() {
  return cookieHeader('', 0);
}

// The single gate every content endpoint calls first. It reads only the signed cookie and
// nothing else the browser sends about who it is.
//
// It fails closed and never throws. `verifyToken` needs `SESSION_SECRET`, so an
// unconfigured deployment would otherwise throw here — before any handler's try/catch — and
// the difference between "misconfigured" and "signed out" is not one a caller should be
// able to see anyway. The misconfiguration is logged, and `api/login.js` is where it
// surfaces as a 500.
function hasValidSession(req, now = Date.now()) {
  try {
    const jar = (req.cookies && typeof req.cookies === 'object')
      ? req.cookies
      : parseCookies(req.headers && req.headers.cookie);
    return verifyToken(jar[COOKIE_NAME], now);
  } catch (error) {
    console.error('session: %s', error.message);
    return false;
  }
}

module.exports = {
  COOKIE_NAME,
  SESSION_SECONDS,
  requiredEnv,
  passwordMatches,
  issue,
  verifyToken,
  parseCookies,
  issuedCookie,
  clearedCookie,
  hasValidSession,
};
