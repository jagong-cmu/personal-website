'use strict';

// Every content read and write goes through the GitHub API, never the deployed
// filesystem. Two independent reasons: `.vercelignore` withholds `*.md` from the build
// upload, so a draft does not exist in the deployment at all; and a file committed a
// second ago is not in the currently-running deployment either. The repository is the
// only place that is always current.
//
// Writes use the Git Data API rather than the Contents API because a publish touches four
// files and PRD section 6 requires a single batched commit. The Contents API commits one
// file per call.

const { requiredEnv } = require('./session');

const API_BASE = process.env.GITHUB_API_BASE || 'https://api.github.com';
const REPO = process.env.GITHUB_REPO || 'jagong-cmu/personal-website';
const BRANCH = process.env.GITHUB_BRANCH || 'main';
const USER_AGENT = 'jonathangong.com-admin';

function repoUrl(suffix) {
  return `${API_BASE}/repos/${REPO}${suffix}`;
}

async function call(method, suffix, body) {
  const response = await fetch(repoUrl(suffix), {
    method,
    headers: {
      Authorization: `Bearer ${requiredEnv('GITHUB_TOKEN')}`,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': USER_AGENT,
      // GitHub serves content responses through a cache; a publish immediately followed by
      // a read must not see the pre-publish tree.
      'Cache-Control': 'no-cache',
      ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
    },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  if (response.status === 404) return null;
  if (!response.ok) {
    const detail = await response.text().catch(() => '');
    // Logged server-side only. Callers surface a generic failure; an upstream message can
    // name a token scope or a private path and has no business in a response body.
    const error = new Error(`GitHub ${method} ${suffix} -> ${response.status} ${detail.slice(0, 400)}`);
    error.status = response.status;
    throw error;
  }
  if (response.status === 204) return null;
  return response.json();
}

// --- reads -----------------------------------------------------------------------------

// A file's UTF-8 text, or null when it does not exist.
async function readFile(path) {
  const data = await call('GET', `/contents/${encodeURI(path)}?ref=${encodeURIComponent(BRANCH)}`);
  if (!data || Array.isArray(data) || typeof data.content !== 'string') return null;
  return Buffer.from(data.content, data.encoding === 'base64' ? 'base64' : 'utf8').toString('utf8');
}

// File names directly inside a directory, or [] when the directory does not exist.
async function listDirectory(path) {
  const data = await call('GET', `/contents/${encodeURI(path)}?ref=${encodeURIComponent(BRANCH)}`);
  if (!Array.isArray(data)) return [];
  return data.filter((item) => item.type === 'file').map((item) => item.name);
}

// --- writes ----------------------------------------------------------------------------

async function headCommit() {
  const ref = await call('GET', `/git/ref/heads/${encodeURIComponent(BRANCH)}`);
  if (!ref) throw new Error(`branch ${BRANCH} not found`);
  const commit = await call('GET', `/git/commits/${ref.object.sha}`);
  return { sha: ref.object.sha, tree: commit.tree.sha };
}

/**
 * Commit a set of changes as ONE commit.
 *
 * `changes` is a map of repository path -> string content, or `null` to delete the path.
 * Callers pass paths they built themselves from a validated slug; nothing here accepts a
 * path straight from the browser.
 */
async function commitChanges(changes, message) {
  const paths = Object.keys(changes);
  if (paths.length === 0) return null;

  const base = await headCommit();

  const tree = [];
  for (const path of paths) {
    const content = changes[path];
    if (content === null) {
      tree.push({ path, mode: '100644', type: 'blob', sha: null });
      continue;
    }
    const blob = await call('POST', '/git/blobs', { content, encoding: 'utf-8' });
    tree.push({ path, mode: '100644', type: 'blob', sha: blob.sha });
  }

  const created = await call('POST', '/git/trees', { base_tree: base.tree, tree });
  if (created.sha === base.tree) return null; // Nothing actually changed.

  const commit = await call('POST', '/git/commits', {
    message,
    tree: created.sha,
    parents: [base.sha],
  });
  await call('PATCH', `/git/refs/heads/${encodeURIComponent(BRANCH)}`, { sha: commit.sha });
  return commit.sha;
}

module.exports = { API_BASE, REPO, BRANCH, readFile, listDirectory, commitChanges };
