#!/usr/bin/env python3
"""Enforce the site's design rules.

The site is plain, white, and self-contained on purpose. Those constraints are easy to
erode one well-meaning edit at a time, so they are asserted here instead of being left to
memory. Every rule below is recorded in PRD.md section 9.

Standard library only. Run it from the repository root:

    python3 .github/scripts/check-design-rules.py
"""

import os
import re
import sys

PAGES = ["index.html", "journey.html", "blog.html"]

# Absolute URLs a page is allowed to LINK to. These are navigation targets the visitor
# chooses to follow, not resources the page fetches while loading.
ALLOWED_LINK_PREFIXES = (
    "https://github.com/jagong-cmu",
    "https://linkedin.com/in/gong-jonathan",
    # Companies the owner has confirmed by name (PRD decision 30). Only confirmed ones are
    # listed: an unlinked company name is correct, a guessed domain is not.
    "https://scottylabs.org",
    "https://996ventures.com",
    "mailto:",
)

failures = []


def fail(rule, path, line, message):
    """Record a violation. `line` may be None when the rule is about an absent thing."""
    where = f"{path}:{line}" if line else path
    failures.append(f"[{rule}] {where}\n    {message}")


def lines_of(text):
    return list(enumerate(text.splitlines(), start=1))


def line_of(text, index):
    """1-based line number for a character offset."""
    return text.count("\n", 0, index) + 1


def strip_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def styles_of(text):
    """Every <style> block's contents, comments stripped."""
    return [strip_comments(m.group(1)) for m in re.finditer(r"<style[^>]*>(.*?)</style>", text, re.S)]


def css_blocks(css):
    """(selector, body) for each top-level rule. Good enough for a hand-written sheet."""
    return [(m.group(1).strip(), m.group(2)) for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css)]


# --------------------------------------------------------------------------------------
# Rule 1 — zero external requests
# --------------------------------------------------------------------------------------
def check_external_requests(path, text):
    for n, line in lines_of(text):
        # No stylesheet links at all: the CSS is inline on purpose.
        for m in re.finditer(r"<link\b[^>]*>", line, re.I):
            fail("zero-external-requests", path, n,
                 f"<link> tag found. The stylesheet is inline; the page must fetch nothing.\n"
                 f"    {m.group(0).strip()}")

        # Anything the browser fetches automatically must be a relative path.
        for m in re.finditer(r"""\bsrc\s*=\s*["']([^"']+)["']""", line, re.I):
            url = m.group(1).strip()
            if re.match(r"^(?:[a-z][a-z0-9+.-]*:)?//|^[a-z][a-z0-9+.-]*:", url, re.I) and not url.startswith("data:"):
                fail("zero-external-requests", path, n,
                     f"src points off-site: {url}\n"
                     f"    Assets must be committed to this repository and referenced relatively.")

        # CSS-initiated fetches.
        for m in re.finditer(r"url\(\s*['\"]?([^)'\"]+)", line, re.I):
            url = m.group(1).strip()
            if url.startswith(("http://", "https://", "//")):
                fail("zero-external-requests", path, n, f"CSS url() fetches a remote resource: {url}")
        if re.search(r"@import\b", line, re.I):
            fail("zero-external-requests", path, n, "@import pulls in an external stylesheet.")

        # Links the visitor follows: allowed, but only to the owner's own destinations.
        for m in re.finditer(r"""\bhref\s*=\s*["']([^"']+)["']""", line, re.I):
            url = m.group(1).strip()
            if url.startswith(("http://", "https://", "//", "mailto:")):
                if not url.startswith(ALLOWED_LINK_PREFIXES):
                    fail("zero-external-requests", path, n,
                         f"Absolute link to an unapproved destination: {url}\n"
                         f"    Allowed: {', '.join(ALLOWED_LINK_PREFIXES)}")


# --------------------------------------------------------------------------------------
# Rule 2 — pure white, no dark mode
# --------------------------------------------------------------------------------------
def check_white_background(path, text):
    css = "\n".join(styles_of(text))
    if not re.search(r"background(?:-color)?\s*:\s*#FFFFFF\b", css, re.I):
        fail("pure-white", path, None,
             "No `background: #FFFFFF` declaration found. The page background is pure white, "
             "not cream, sand, off-white, or grey.")

    for n, line in lines_of(text):
        if re.search(r"prefers-color-scheme", line, re.I):
            fail("pure-white", path, n,
                 "prefers-color-scheme block found. The site is white; there is no dark mode.")


# --------------------------------------------------------------------------------------
# Rule 3 — one system font family
# --------------------------------------------------------------------------------------
def check_font_family(path, text):
    for n, line in lines_of(text):
        if re.search(r"@font-face", line, re.I):
            fail("system-font-only", path, n, "@font-face loads a custom font. The stack is system fonts only.")
        if re.search(r"fonts\.googleapis\.com|fonts\.gstatic\.com|use\.typekit|fonts\.bunny\.net", line, re.I):
            fail("system-font-only", path, n, "Web-font host referenced. No font may be downloaded.")

    css = "\n".join(styles_of(text))
    families = {m.group(1).strip() for m in re.finditer(r"font-family\s*:\s*([^;}]+)", css, re.I)}
    if len(families) > 1:
        fail("system-font-only", path, None,
             "More than one font-family declared; the site uses exactly one stack:\n    "
             + "\n    ".join(sorted(families)))
    for family in families:
        if not re.match(r"^\s*system-ui\b", family):
            fail("system-font-only", path, None,
                 f"font-family must start with system-ui. Found: {family}")


# --------------------------------------------------------------------------------------
# Rule 4 — at most three distinct font sizes
# --------------------------------------------------------------------------------------
def check_font_sizes(path, text):
    css = "\n".join(styles_of(text))
    tokens = {m.group(1): m.group(2).strip() for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;}]+)", css)}

    sizes = set()
    for m in re.finditer(r"font-size\s*:\s*([^;}]+)", css, re.I):
        value = m.group(1).strip()
        var = re.match(r"var\(\s*(--[\w-]+)", value)
        if var:
            value = tokens.get(var.group(1), value)
        sizes.add(value.strip())

    if len(sizes) > 3:
        fail("three-type-sizes", path, None,
             f"{len(sizes)} distinct font sizes: {', '.join(sorted(sizes))}\n"
             f"    At most three are permitted across the site.")


# --------------------------------------------------------------------------------------
# Rule 5 — no decoration
# --------------------------------------------------------------------------------------
def check_no_decoration(path, text):
    for n, line in lines_of(text):
        stripped = strip_comments(line)
        if re.search(r"box-shadow\s*:\s*(?!none)", stripped, re.I):
            fail("no-decoration", path, n, "box-shadow is not permitted.")
        if re.search(r"text-shadow\s*:\s*(?!none)", stripped, re.I):
            fail("no-decoration", path, n, "text-shadow is not permitted.")
        if re.search(r"(linear|radial|conic)-gradient", stripped, re.I):
            fail("no-decoration", path, n, "Gradients are not permitted; backgrounds are flat.")
        if re.search(r"@keyframes", stripped, re.I):
            fail("no-decoration", path, n, "@keyframes animation is not permitted; motion is near-zero.")
        if re.search(r"\btransition\s*:", stripped, re.I):
            fail("no-decoration", path, n,
                 "transition is not permitted. Tab switching is instant and nothing eases in.")
        if re.search(r"\banimation\s*:\s*(?!none)", stripped, re.I):
            fail("no-decoration", path, n, "animation is not permitted.")

    # border-radius: the circular headshot is the single granted exception.
    for css in styles_of(text):
        for selector, body in css_blocks(css):
            for m in re.finditer(r"border-radius\s*:\s*([^;}]+)", body, re.I):
                value = m.group(1).strip()
                if re.fullmatch(r"0(?:px|%|em|rem)?", value):
                    continue
                if ".masthead img" not in selector:
                    fail("no-decoration", path, None,
                         f"border-radius: {value} on `{selector}`.\n"
                         f"    The headshot (.masthead img) is the only element permitted a "
                         f"non-zero border-radius.")


# --------------------------------------------------------------------------------------
# Rule 6 — the timeline is excluded from search engines, the other pages are not
# --------------------------------------------------------------------------------------
def check_robots(pages):
    for path, text in pages.items():
        has_noindex = bool(re.search(
            r"""<meta[^>]*name\s*=\s*["']robots["'][^>]*content\s*=\s*["'][^"']*noindex""",
            text, re.I))
        if path == "journey.html" and not has_noindex:
            fail("robots", path, None,
                 'Missing <meta name="robots" content="noindex, nofollow">. The timeline is '
                 'excluded from search engines so it does not surface in a search for the '
                 "owner's name (PRD section 8).")
        if path != "journey.html" and has_noindex:
            line = line_of(text, re.search(r"<meta[^>]*robots", text, re.I).start())
            fail("robots", path, line,
                 "This page carries a robots noindex tag. Only journey.html is excluded from "
                 "search engines; this page is meant to be found.")


# --------------------------------------------------------------------------------------
# Rule 7 — no phone number
# --------------------------------------------------------------------------------------
# Matched by shape rather than by value: writing the actual number into a public
# repository would publish the very thing this rule keeps off the site.
PHONE = re.compile(r"""
    (?<![\d/-])
    (?:\+?1[\s.-]?)?
    (?:\(\d{3}\)|\d{3})
    [\s.-]
    \d{3}
    [\s.-]
    \d{4}
    (?![\d/-])
""", re.X)


def check_no_phone(path, text):
    for n, line in lines_of(text):
        m = PHONE.search(line)
        if m:
            fail("no-phone-number", path, n,
                 "A phone number appears on the page. Contact is by email only; the number "
                 "is deliberately absent from the site.")


# --------------------------------------------------------------------------------------
# Rule 8 — internal links resolve
# --------------------------------------------------------------------------------------
def check_internal_links(path, text, root):
    for n, line in lines_of(text):
        for attr in ("href", "src"):
            for m in re.finditer(rf"""\b{attr}\s*=\s*["']([^"']+)["']""", line, re.I):
                url = m.group(1).strip()
                if url.startswith(("http://", "https://", "//", "mailto:", "data:", "#")):
                    continue
                target = url.split("#", 1)[0].split("?", 1)[0]
                if not target:
                    continue
                if not os.path.isfile(os.path.join(root, target)):
                    fail("internal-links-resolve", path, n,
                         f"{attr}=\"{url}\" points at {target}, which does not exist in the repository.")


def main():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    pages = {}
    for name in PAGES:
        full = os.path.join(root, name)
        if not os.path.isfile(full):
            fail("pages-present", name, None, "Expected page is missing from the repository root.")
            continue
        with open(full, encoding="utf-8") as handle:
            pages[name] = handle.read()

    for path, text in pages.items():
        check_external_requests(path, text)
        check_white_background(path, text)
        check_font_family(path, text)
        check_font_sizes(path, text)
        check_no_decoration(path, text)
        check_no_phone(path, text)
        check_internal_links(path, text, root)

    check_robots(pages)

    if failures:
        print(f"Design rules: {len(failures)} violation(s).\n")
        for item in failures:
            print(item)
        print("\nThese rules are recorded in PRD.md section 9. They are prohibitions, not "
              "preferences.\nIf a rule genuinely needs to change, change it there first.")
        return 1

    print(f"Design rules: all checks passed across {len(pages)} pages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
