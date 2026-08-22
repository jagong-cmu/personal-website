#!/usr/bin/env python3
"""Enforce the site's design rules.

The site is plain, white, and self-contained on purpose. Those constraints are easy to
erode one well-meaning edit at a time, so they are asserted here instead of being left to
memory. Most rules below are recorded in PRD.md section 9; the two that are not are named
where they are defined — no-image-metadata comes from PRD.md sections 7.3 and 8 (decision
33), and stylesheets-identical from AGENTS.md.

Standard library only. Run it from the repository root:

    python3 .github/scripts/check-design-rules.py
"""

import hashlib
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

# A prefix above names a whole destination, so it matches only at a boundary: the URL is
# either exactly the prefix or continues with one of these. `996ventures.community` and
# `996ventures.com.co` are therefore different destinations from `996ventures.com`, and
# stay unapproved until the owner confirms them by name.
LINK_BOUNDARY = "/?#"

# The site's own origin. Canonical URLs point at the apex, never at `www`, because apex and
# `www` both serve 200 and a search engine that sees two hostnames sees two sites (§7.5).
SITE_ORIGIN = "https://jonathangong.com"

# `rel` values a <link> element may carry. `canonical` starts no fetch at all; `icon` and
# `apple-touch-icon` name files committed to this repository, which the browser would
# request from the root convention paths with or without the tag. Everything else — and
# `stylesheet` above all — is a fetch this page does not make. See PRD decision 37.
ALLOWED_LINK_RELS = frozenset({"canonical", "icon", "apple-touch-icon"})


def attribute_of(tag, name):
    """An attribute's value from a tag's source text, or "" when it is absent."""
    m = re.search(rf"""\b{name}\s*=\s*["']([^"']*)["']""", tag, re.I)
    return m.group(1).strip() if m else ""


def is_same_origin(url):
    """True for a relative path, or an absolute URL on the site's own origin.

    A scheme this function does not recognise as the site's own — `data:`, another host,
    protocol-relative `//` — is off-site, because whatever it names is not in this
    repository."""
    if url.startswith(("http://", "https://", "//")):
        if not url.startswith(SITE_ORIGIN):
            return False
        rest = url[len(SITE_ORIGIN):]
        return rest == "" or rest[0] in LINK_BOUNDARY
    if re.match(r"^[a-z][a-z0-9+.-]*:", url, re.I):
        return False
    return True


def is_allowed_link(url):
    for prefix in ALLOWED_LINK_PREFIXES:
        if prefix.endswith(":"):  # A bare scheme such as mailto: has no host to bound.
            if url.startswith(prefix):
                return True
            continue
        prefix = prefix.rstrip("/")  # An entry reads the same with or without a trailing slash.
        if url == prefix:
            return True
        if url.startswith(prefix) and url[len(prefix)] in LINK_BOUNDARY:
            return True
    return False


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
def check_link_element(path, n, tag):
    """A single <link>. The rule is about fetches, so it turns on what the tag makes the
    browser do: a stylesheet or an off-site href is a fetch and fails; a same-origin
    canonical, icon, or apple-touch-icon is not and passes."""
    rels = set(attribute_of(tag, "rel").lower().split())
    href = attribute_of(tag, "href")

    if "stylesheet" in rels:
        fail("zero-external-requests", path, n,
             f"<link rel=\"stylesheet\"> found. The CSS is inline on purpose; the page loads "
             f"no stylesheet, its own included.\n    {tag.strip()}")
        return

    if href and not is_same_origin(href):
        fail("zero-external-requests", path, n,
             f"<link> href points off-site: {href}\n"
             f"    A <link> may only name this repository's own files or {SITE_ORIGIN}.\n"
             f"    {tag.strip()}")
        return

    if not rels or not rels <= ALLOWED_LINK_RELS:
        described = ", ".join(sorted(rels)) or "(none)"
        fail("zero-external-requests", path, n,
             f"<link rel=\"{described}\"> is not one the page is permitted to carry.\n"
             f"    Allowed rel values: {', '.join(sorted(ALLOWED_LINK_RELS))} — these start no "
             f"fetch off this site. Anything else does.\n    {tag.strip()}")


def check_external_requests(path, text):
    for n, line in lines_of(text):
        for m in re.finditer(r"<link\b[^>]*>", line, re.I):
            check_link_element(path, n, m.group(0))
        # <link> hrefs are judged above, on what the browser does with them. The scans
        # below are about other attributes, so the tags come out of the line first.
        line = re.sub(r"<link\b[^>]*>", " ", line, flags=re.I)

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
                if not is_allowed_link(url):
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


# --------------------------------------------------------------------------------------
# Rule 9 — committed images carry no embedded metadata
# --------------------------------------------------------------------------------------
# PRD section 7.3 requires GPS and EXIF stripping "always, non-optional", and section 8
# states it cannot be disabled. This repository is public, so an unstripped commit
# publishes the owner's coordinates permanently into git history — two photos in the first
# Journey batch arrived carrying GPS that resolved to real locations. The rule makes that
# guarantee structural instead of dependent on whoever adds the next photo.
#
# Parsed at the segment/chunk level rather than searched for as text: byte sequences such
# as `Exif` and `GPS` occur naturally inside entropy-coded scan data, so a substring search
# reports photographs that are in fact clean.
#
# The rule fails closed. A file is parsed by what its bytes are, not by what its name claims,
# and a file whose metadata cannot be read to the end is a failure rather than a pass: an
# image this rule cannot account for is one nobody has shown to be stripped.

IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png")

# APP0 (0xE0) is the JFIF container header and is expected. APP1–APP15 carry EXIF, XMP,
# ICC-embedded metadata, Photoshop resources, and the rest; COM is a free-text comment.
JPEG_METADATA_MARKERS = {0xFE: "COM"}
for _n in range(1, 16):
    JPEG_METADATA_MARKERS[0xE0 + _n] = f"APP{_n}"

# Segments with no payload length, plus SOI. Scanning stops at SOS, where entropy-coded
# image data begins and marker parsing no longer applies, or at EOI.
JPEG_STANDALONE = {0xD8} | set(range(0xD0, 0xD8))

JPEG_SIGNATURE = b"\xff\xd8"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

PNG_METADATA_CHUNKS = {b"tEXt", b"iTXt", b"zTXt", b"eXIf"}
PNG_CHUNK_TYPE = re.compile(rb"[A-Za-z]{4}")


def jpeg_metadata_segments(data):
    """(names, error) for a JPEG: metadata-bearing segments in file order, and why the
    scan stopped. `error` is None only when the marker sequence ran cleanly to the start of
    scan or the end of image; anything else means the segments could not all be read, so
    the names found so far do not amount to a clean bill."""
    found = []
    i = 2
    while i + 1 < len(data):
        if data[i] != 0xFF:
            return found, f"expected a marker at byte {i}, found 0x{data[i]:02X}"
        marker = data[i + 1]
        if marker == 0xFF:  # Fill byte; markers may be padded with them.
            i += 1
            continue
        if marker == 0xDA:  # Start of scan — compressed pixel data follows.
            return found, None
        if marker == 0xD9:  # End of image, reached without a scan.
            return found, None
        if marker in JPEG_STANDALONE:
            i += 2
            continue
        if i + 3 >= len(data):
            return found, f"the segment header at byte {i} is cut off by the end of the file"
        length = int.from_bytes(data[i + 2:i + 4], "big")
        if length < 2:
            return found, f"the segment at byte {i} declares an impossible length of {length}"
        i += 2 + length
        if i > len(data):
            return found, f"the segment at byte {i - 2 - length} runs past the end of the file"
        if marker in JPEG_METADATA_MARKERS:
            found.append(JPEG_METADATA_MARKERS[marker])
    return found, "the marker sequence ran off the end of the file without a start-of-scan marker"


def png_metadata_chunks(data):
    """(names, error) for a PNG, on the same terms as jpeg_metadata_segments: `error` is
    None only when the chunk sequence ran cleanly to IEND."""
    found = []
    i = 8
    while i + 8 <= len(data):
        length = int.from_bytes(data[i:i + 4], "big")
        kind = data[i + 4:i + 8]
        if not PNG_CHUNK_TYPE.fullmatch(kind):
            return found, f"the chunk type at byte {i + 4} is not four letters: {kind!r}"
        if kind in PNG_METADATA_CHUNKS:
            found.append(kind.decode("ascii"))
        if kind == b"IEND":
            return found, None
        i += 12 + length  # length + type + data + CRC
        if i > len(data):
            return found, f"the {kind.decode('ascii')} chunk declares a length that runs past the end of the file"
    return found, "the chunk sequence ran off the end of the file without an IEND chunk"


def check_image_metadata(root):
    """Check every committed raster image. Returns how many were inspected."""
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in sorted(filenames):
            if not name.lower().endswith(IMAGE_SUFFIXES):
                continue
            count += 1
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root)
            with open(full, "rb") as handle:
                data = handle.read()
            if data.startswith(JPEG_SIGNATURE):
                kind, (found, error) = "JPEG", jpeg_metadata_segments(data)
            elif data.startswith(PNG_SIGNATURE):
                kind, (found, error) = "PNG", png_metadata_chunks(data)
            else:
                fail("no-image-metadata", rel, None,
                     f"Bytes are neither a JPEG nor a PNG: the file opens with "
                     f"{data[:8].hex(' ').upper() or '(nothing)'}, matching neither FF D8 nor "
                     f"89 50 4E 47 0D 0A 1A 0A. A `.png` straight off a phone is often a JPEG.\n"
                     f"    Its metadata cannot be read, so it cannot be shown to be stripped, "
                     f"and this rule never resolves unreadable to clean (PRD sections 7.3 "
                     f"and 8).")
                continue
            if error:
                fail("no-image-metadata", rel, None,
                     f"This {kind} could not be read to the end of its metadata: {error}.\n"
                     f"    A file that does not parse cannot be shown to be stripped of GPS "
                     f"and EXIF, so it fails the rule rather than passing it by default "
                     f"(PRD sections 7.3 and 8).")
            if found:
                fail("no-image-metadata", rel, None,
                     f"Embedded metadata found: {', '.join(found)}.\n"
                     f"    Every committed image is stripped of GPS and EXIF before it lands "
                     f"(PRD sections 7.3 and 8); the stripping cannot be disabled.\n"
                     f"    This repository is public, so an unstripped commit publishes the "
                     f"location permanently in git history.")
    return count


# --------------------------------------------------------------------------------------
# Rule 10 — the three inline stylesheets are byte-identical
# --------------------------------------------------------------------------------------
# Each page carries its own copy of the whole sheet, which AGENTS.md accepts for the static
# preview. Nothing detected drift: the rules above validate each page independently, so all
# three could diverge and still pass. A style change is a three-way edit; this says so.
def check_stylesheets_identical(pages):
    sheets = {}
    for path, text in pages.items():
        blocks = re.findall(r"<style[^>]*>(.*?)</style>", text, re.S)
        sheets[path] = "".join(blocks)

    if len(set(sheets.values())) <= 1:
        return

    # No page is the reference: the one that was edited is as likely to be the outlier as
    # the majority. Report the drift once, naming every participant and grouping the pages
    # that still agree, so the odd sheet out is the odd group out.
    groups = {}
    for path in sorted(sheets):
        groups.setdefault(sheets[path], []).append(path)
    described = "\n    ".join(
        f"{', '.join(paths)}: {len(css)} bytes, sha256 {hashlib.sha256(css.encode()).hexdigest()[:12]}"
        for css, paths in sorted(groups.items(), key=lambda item: item[1]))

    fail("stylesheets-identical", ", ".join(sorted(sheets)), None,
         f"The inline stylesheets have drifted into {len(groups)} versions:\n"
         f"    {described}\n"
         "    Every page carries a byte-identical copy of the whole sheet, so a CSS change "
         "is a three-way edit. Whichever version was edited last, all three must end up "
         "the same.")


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
    check_stylesheets_identical(pages)
    images = check_image_metadata(root)

    if failures:
        print(f"Design rules: {len(failures)} violation(s).\n")
        for item in failures:
            print(item)
        print("\nThese rules are recorded in PRD.md — section 9 for the visual ones, "
              "sections 7.3 and 8\n(decision 33) for no-image-metadata — and in AGENTS.md "
              "for stylesheets-identical.\nThey are prohibitions, not preferences. If a rule "
              "genuinely needs to change, change it\nthere first.")
        return 1

    print(f"Design rules: all checks passed across {len(pages)} pages "
          f"and {images} image(s); the three inline stylesheets are identical.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
