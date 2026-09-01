'use strict';

// Markdown to HTML for blog posts. Deliberately narrow: headings, paragraphs, bold,
// italic, links, lists, blockquotes, inline code, and fenced code blocks. Nothing else.
// This is not a general Markdown engine and should not grow into one.
//
// The security property that matters: raw HTML in the source is ESCAPED, never passed
// through. The public pages carry no author-supplied scripts by design and
// `check-design-rules.py` enforces that; the editor must not become the hole in it. Every
// character of post text reaches the output through `escapeHtml` first, and the only tags
// in the result are the ones this file writes itself.

// Placeholder marker for lifted-out code spans. NUL cannot survive `escapeHtml` from user
// input because it is stripped from the source first, so a post cannot forge one.
const SENTINEL = '\u0000';

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// A link destination is safe when it is relative, a fragment, or one of three schemes a
// reader can follow. `javascript:`, `data:`, and anything else become plain text rather
// than a link — the label is kept, the destination is dropped.
function safeHref(rawUrl) {
  const url = String(rawUrl).trim();
  if (!url || /[\u0000-\u0020]/.test(url)) return null;
  if (/^[a-z][a-z0-9+.-]*:/i.test(url)) {
    return /^(?:https?|mailto):/i.test(url) ? url : null;
  }
  return url;
}

// Inline markup, applied to text that has ALREADY been escaped. Code spans are lifted out
// first so that a `*` or `[` inside them is not read as markup.
function renderInline(rawText) {
  const escaped = escapeHtml(String(rawText).replace(/\u0000/g, ''));

  const codeSpans = [];
  let text = escaped.replace(/`([^`]+)`/g, (_match, code) => {
    codeSpans.push(code);
    return `${SENTINEL}c${codeSpans.length - 1}${SENTINEL}`;
  });

  text = text.replace(/\[([^\]]*)\]\(([^)\s]+)\)/g, (match, label, target) => {
    // The target passed through escapeHtml above, so `&` is `&amp;` and a quote cannot
    // break out of the attribute. It is decoded only to judge the scheme.
    const decoded = target.replace(/&amp;/g, '&').replace(/&#39;/g, "'").replace(/&quot;/g, '"');
    if (!safeHref(decoded)) return label || match;
    return `<a href="${target}">${label}</a>`;
  });

  text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  text = text.replace(/__([^_]+)__/g, '<strong>$1</strong>');
  text = text.replace(/(^|[^*\w])\*([^*\n]+)\*(?![*\w])/g, '$1<em>$2</em>');
  text = text.replace(/(^|[^_\w])_([^_\n]+)_(?![_\w])/g, '$1<em>$2</em>');

  return text.replace(
    new RegExp(`${SENTINEL}c(\\d+)${SENTINEL}`, 'g'),
    (_match, index) => `<code>${codeSpans[Number(index)]}</code>`,
  );
}

const FENCE = /^\s*```/;
const HEADING = /^(#{1,6})\s+(.*)$/;
const QUOTE = /^>\s?(.*)$/;
const BULLET = /^\s*[-*+]\s+(.*)$/;
const NUMBER = /^\s*\d+[.)]\s+(.*)$/;

function startsBlock(line) {
  return FENCE.test(line) || HEADING.test(line) || QUOTE.test(line)
    || BULLET.test(line) || NUMBER.test(line) || line.trim() === '';
}

function renderList(lines, index, pattern, tag, out) {
  const items = [];
  let i = index;
  while (i < lines.length) {
    const match = lines[i].match(pattern);
    if (!match) break;
    const parts = [match[1]];
    i += 1;
    // A wrapped item continues on the next line; a blank line or a new block ends it.
    while (i < lines.length && !startsBlock(lines[i])) {
      parts.push(lines[i].trim());
      i += 1;
    }
    items.push(parts.join(' ').trim());
  }
  out.push(`<${tag}>`);
  for (const item of items) out.push(`<li>${renderInline(item)}</li>`);
  out.push(`</${tag}>`);
  return i;
}

/**
 * Convert Markdown to the HTML that goes inside a post page's `.post-body`.
 *
 * Heading depth collapses to the two levels the site has type for: `#` and `##` become
 * `<h2>`, anything deeper becomes `<h3>`. The page's own `<h1>` is the post title, so a
 * body heading never competes with it.
 */
function renderMarkdown(source) {
  const lines = String(source == null ? '' : source).replace(/\r\n?/g, '\n').split('\n');
  const out = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    if (line.trim() === '') { i += 1; continue; }

    if (FENCE.test(line)) {
      i += 1;
      const code = [];
      while (i < lines.length && !FENCE.test(lines[i])) { code.push(lines[i]); i += 1; }
      i += 1; // The closing fence, or the end of the source.
      out.push(`<pre><code>${escapeHtml(code.join('\n'))}</code></pre>`);
      continue;
    }

    const heading = line.match(HEADING);
    if (heading) {
      const tag = heading[1].length <= 2 ? 'h2' : 'h3';
      out.push(`<${tag}>${renderInline(heading[2].trim())}</${tag}>`);
      i += 1;
      continue;
    }

    if (QUOTE.test(line)) {
      const quoted = [];
      while (i < lines.length && QUOTE.test(lines[i])) {
        quoted.push(lines[i].match(QUOTE)[1]);
        i += 1;
      }
      out.push(`<blockquote>\n${renderMarkdown(quoted.join('\n'))}\n</blockquote>`);
      continue;
    }

    if (BULLET.test(line)) { i = renderList(lines, i, BULLET, 'ul', out); continue; }
    if (NUMBER.test(line)) { i = renderList(lines, i, NUMBER, 'ol', out); continue; }

    const paragraph = [line.trim()];
    i += 1;
    while (i < lines.length && !startsBlock(lines[i])) { paragraph.push(lines[i].trim()); i += 1; }
    out.push(`<p>${renderInline(paragraph.join('\n'))}</p>`);
  }

  return out.join('\n');
}

module.exports = { escapeHtml, safeHref, renderInline, renderMarkdown };
