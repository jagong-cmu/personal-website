#!/usr/bin/env python3
"""Tests for the design rules that are easy to get subtly wrong.

`zero-external-requests` used to reject every <link> element outright. It now turns on what
the tag actually makes the browser do (PRD decision 37), and that distinction is exactly the
kind that erodes: a permissive bug here is invisible until an external request has shipped.
So both halves are pinned — what must still fail, and what must now pass.

`no-decoration`'s border-radius branch is the same shape of rule and the same hazard. It named
one selector until 2026-08-25, when the rounded Projects card was granted a second (decision
49). A widening that quietly permitted a radius anywhere would still pass CI, so both halves
are pinned here too: the two exempt selectors pass, and everything else — including selectors
that merely share a prefix with them, or sit in the same comma-separated list — still fails.

The 2026-09-01 admin work added a third hazard of the same kind, and the largest one. The
checker no longer works from a hardcoded list of three pages: it DISCOVERS public pages, so
what it covers is now a consequence of a walk and two directory sets rather than something
anybody reads off a line. Two opposite mistakes are then invisible — a generated post page
quietly falling outside the walk, and `admin/` quietly falling inside it — and a third,
`curated_links`, hands post pages an exemption from the destination allowlist that must not
leak back onto the hand-written pages or widen past that one half of the rule. All three are
pinned below, along with the rules that keep a draft from ever being served.

The same work narrowed the declaration scans to actual CSS — <style> contents and inline
`style=` attributes — because a post's body is prose and rendered code blocks, and a post
that merely writes about `transition:` was failing a rule it does not break, after the
publish commit had already landed. That narrowing is the easiest of all of these to widen
back by accident or to over-narrow into uselessness, so both halves are pinned too.

Standard library only, same as the checker. Run it from the repository root:

    python3 .github/scripts/test-design-rules.py
"""

import importlib.util
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "check_design_rules", os.path.join(HERE, "check-design-rules.py"))
rules = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rules)


class LinkElementTest(unittest.TestCase):
    """Every case is one <link> in a page's head, checked in isolation."""

    def failures_for(self, tag):
        rules.failures.clear()
        rules.check_external_requests("test.html", f"<head>\n{tag}\n</head>\n")
        return list(rules.failures)

    def assertBlocked(self, tag):
        found = self.failures_for(tag)
        self.assertTrue(found, f"expected {tag} to be rejected, but it passed")
        for item in found:
            self.assertIn("zero-external-requests", item)

    def assertPermitted(self, tag):
        found = self.failures_for(tag)
        self.assertEqual([], found, f"expected {tag} to pass, but it was rejected:\n" + "\n".join(found))

    # ---- still blocked ----------------------------------------------------------------

    def test_external_stylesheet_is_blocked(self):
        self.assertBlocked('<link rel="stylesheet" href="https://cdn.example.com/reset.css">')

    def test_same_origin_stylesheet_is_blocked(self):
        # The narrowing is about fetches, and a local stylesheet is still a fetch. The CSS
        # is inline; there is no site.css to link.
        self.assertBlocked('<link rel="stylesheet" href="site.css">')

    def test_external_icon_is_blocked(self):
        self.assertBlocked('<link rel="icon" href="https://example.com/favicon.ico">')

    def test_external_canonical_is_blocked(self):
        self.assertBlocked('<link rel="canonical" href="https://example.com/">')

    def test_protocol_relative_href_is_blocked(self):
        self.assertBlocked('<link rel="icon" href="//example.com/favicon.ico">')

    def test_lookalike_origin_is_blocked(self):
        # `jonathangong.com.example.net` is a different host; the boundary check is what
        # keeps a prefix match from becoming a substring match.
        self.assertBlocked('<link rel="canonical" href="https://jonathangong.com.example.net/">')

    def test_preconnect_is_blocked(self):
        # A rel the list does not name, even pointing at our own origin: preconnect exists
        # to open a connection, which is the thing this rule forbids.
        self.assertBlocked('<link rel="preconnect" href="https://jonathangong.com">')

    def test_preload_of_a_local_font_is_blocked(self):
        self.assertBlocked('<link rel="preload" as="font" href="inter.woff2">')

    def test_link_without_rel_is_blocked(self):
        self.assertBlocked('<link href="favicon.ico">')

    # ---- newly permitted --------------------------------------------------------------

    def test_apex_canonical_is_permitted(self):
        self.assertPermitted('<link rel="canonical" href="https://jonathangong.com/">')

    def test_canonical_to_a_page_is_permitted(self):
        self.assertPermitted('<link rel="canonical" href="https://jonathangong.com/blog.html">')

    def test_relative_icon_is_permitted(self):
        self.assertPermitted('<link rel="icon" href="favicon.ico">')

    def test_relative_apple_touch_icon_is_permitted(self):
        self.assertPermitted('<link rel="apple-touch-icon" href="apple-touch-icon.png">')

    def test_icon_with_type_and_sizes_is_permitted(self):
        self.assertPermitted(
            '<link rel="icon" type="image/png" sizes="180x180" href="apple-touch-icon.png">')

    # ---- the surrounding scans still see the rest of the line -------------------------

    def test_off_site_script_src_is_still_blocked(self):
        rules.failures.clear()
        rules.check_external_requests("test.html", '<script src="https://cdn.example.com/a.js"></script>\n')
        self.assertTrue(rules.failures)

    def test_unapproved_navigation_link_is_still_blocked(self):
        rules.failures.clear()
        rules.check_external_requests("test.html", '<a href="https://example.com/">x</a>\n')
        self.assertTrue(rules.failures)

    def test_approved_navigation_link_still_passes(self):
        rules.failures.clear()
        rules.check_external_requests("test.html", '<a href="https://github.com/jagong-cmu">x</a>\n')
        self.assertEqual([], rules.failures)


class BorderRadiusTest(unittest.TestCase):
    """The site is square except for two elements granted a radius by name in PRD section 9:
    the circular headshot (2026-08-19) and the Projects image card (2026-08-25, decision 49).
    Each case is one CSS rule in a page's inline stylesheet."""

    def failures_for(self, css):
        rules.failures.clear()
        rules.check_no_decoration("test.html", f"<style>\n{css}\n</style>\n")
        return list(rules.failures)

    def assertBlocked(self, css):
        found = self.failures_for(css)
        self.assertTrue(found, f"expected {css!r} to be rejected, but it passed")
        for item in found:
            self.assertIn("no-decoration", item)

    def assertPermitted(self, css):
        found = self.failures_for(css)
        self.assertEqual([], found, f"expected {css!r} to pass, but it was rejected:\n"
                                    + "\n".join(found))

    # ---- the two granted exceptions ---------------------------------------------------

    def test_headshot_radius_is_permitted(self):
        self.assertPermitted(".masthead img { border-radius: 50%; }")

    def test_projects_card_radius_is_permitted(self):
        self.assertPermitted('[data-panel="projects"] .entry { border-radius: 10px; }')

    def test_zero_radius_anywhere_is_permitted(self):
        for css in (".anything { border-radius: 0; }",
                    ".anything { border-radius: 0px; }",
                    ".anything { border-radius: 0%; }"):
            self.assertPermitted(css)

    # ---- everything else still fails --------------------------------------------------

    def test_unrelated_selector_is_still_blocked(self):
        self.assertBlocked(".entry-logo { border-radius: 4px; }")

    def test_work_entry_is_still_blocked(self):
        # Work shares `.entry` with Projects; the exception is scoped to the Projects panel.
        self.assertBlocked('[data-panel="work"] .entry { border-radius: 10px; }')

    def test_bare_entry_is_still_blocked(self):
        # The exemption names the panel-scoped selector, not `.entry` on its own, which
        # would carry the radius into Work as well.
        self.assertBlocked(".entry { border-radius: 10px; }")

    def test_prefix_of_an_exempt_selector_is_still_blocked(self):
        # `[data-panel="projects"] .entry-title` starts with the exempt selector. A
        # substring test would let it through; the whole selector has to match.
        self.assertBlocked('[data-panel="projects"] .entry-title { border-radius: 6px; }')
        self.assertBlocked('[data-panel="projects"] .entry-reveal { border-radius: 6px; }')

    def test_exempt_selector_cannot_launder_a_group(self):
        # Naming an exempt selector alongside an unrelated one must not grant the radius to
        # the unrelated one; every comma part has to be exempt.
        self.assertBlocked(".masthead img, .tabs a { border-radius: 50%; }")
        self.assertBlocked('[data-panel="projects"] .entry, .note { border-radius: 10px; }')

    def test_a_group_of_only_exempt_selectors_is_permitted(self):
        self.assertPermitted(
            '.masthead img,\n[data-panel="projects"] .entry { border-radius: 10px; }')

    # ---- the branches beside it are untouched -----------------------------------------

    def test_transition_is_still_blocked(self):
        # The hover reveal is instant on purpose (decision 52). Nothing eases in.
        self.assertBlocked('[data-panel="projects"] .entry-reveal { transition: opacity .2s; }')

    def test_gradient_scrim_is_still_blocked(self):
        self.assertBlocked(
            '[data-panel="projects"] .entry-reveal '
            '{ background: linear-gradient(rgba(0,0,0,0), rgba(0,0,0,.6)); }')

    def test_shadow_on_the_card_is_still_blocked(self):
        self.assertBlocked('[data-panel="projects"] .entry { box-shadow: 0 2px 8px #0002; }')


class CuratedLinksTest(unittest.TestCase):
    """The destination allowlist (PRD decision 30) binds the hand-written pages, where an
    absolute URL is only ever present because the owner confirmed it by name. A blog post's
    links are typed by the owner in the editor, so `blog/` opts out of that half — and ONLY
    that half. The fetch half is what "zero external requests" actually protects and it must
    still bind a post page exactly as it binds the front door."""

    def failures_for(self, markup, curated):
        rules.failures.clear()
        rules.check_external_requests("blog/post.html", markup, curated_links=curated)
        return list(rules.failures)

    def test_unapproved_link_blocked_on_a_hand_written_page(self):
        self.assertTrue(self.failures_for('<a href="https://example.com/">x</a>\n', True))

    def test_unapproved_link_permitted_in_a_post(self):
        self.assertEqual([], self.failures_for('<a href="https://example.com/">x</a>\n', False))

    def test_a_post_may_not_load_an_external_stylesheet(self):
        self.assertTrue(self.failures_for(
            '<link rel="stylesheet" href="https://cdn.example.com/a.css">\n', False))

    def test_a_post_may_not_load_an_off_site_script(self):
        self.assertTrue(self.failures_for('<script src="https://cdn.example.com/a.js"></script>\n', False))

    def test_a_post_may_not_fetch_a_remote_image(self):
        self.assertTrue(self.failures_for('<img src="https://example.com/a.png">\n', False))

    def test_a_post_may_not_import_a_stylesheet(self):
        self.assertTrue(self.failures_for('<style>@import url(x.css);</style>\n', False))

    def test_javascript_href_blocked_in_both_modes(self):
        for curated in (True, False):
            self.assertTrue(self.failures_for('<a href="javascript:alert(1)">x</a>\n', curated), curated)

    def test_data_href_blocked_in_both_modes(self):
        for curated in (True, False):
            self.assertTrue(self.failures_for('<a href="data:text/html,x">x</a>\n', curated), curated)


class CssOnlyScanTest(unittest.TestCase):
    """The declaration scans read CSS, not the page.

    A post's body is the owner's prose and its rendered code blocks, so a post that writes
    ABOUT `transition:` — or shows a `box-shadow` in a fenced example — must pass. It would
    otherwise go red after the publish commit had landed and deployed, on a page that
    violates nothing. The other half matters just as much: the same declaration inside a
    <style> block or an inline `style=` attribute is real CSS on any page and still fails."""

    def failures_for(self, markup):
        rules.failures.clear()
        rules.check_white_background("blog/a-post.html", "<style>body { background: #FFFFFF; }</style>\n" + markup)
        rules.check_font_family("blog/a-post.html", markup)
        rules.check_no_decoration("blog/a-post.html", markup)
        return list(rules.failures)

    def assertProsePasses(self, body):
        found = self.failures_for(body)
        self.assertEqual([], found, f"expected {body!r} to pass, but it was rejected:\n"
                                    + "\n".join(found))

    def assertCssFails(self, declaration):
        for markup in (f"<style>\n.x {{ {declaration} }}\n</style>\n",
                       f'<p style="{declaration}">x</p>\n'):
            found = self.failures_for(markup)
            self.assertTrue(found, f"expected {markup!r} to be rejected, but it passed")

    # ---- a post that writes about CSS is not a post that uses it ----------------------

    def test_a_paragraph_about_a_declaration_passes(self):
        self.assertProsePasses("<p>The reveal has no <code>transition: opacity .2s</code> on it.</p>\n")

    def test_a_code_block_showing_declarations_passes(self):
        self.assertProsePasses(
            "<pre><code>.card {\n  box-shadow: 0 2px 8px #0002;\n"
            "  transition: opacity 120ms;\n  background: linear-gradient(#fff, #eee);\n"
            "}\n@keyframes pulse { to { opacity: 1; } }\n</code></pre>\n")

    def test_prose_naming_a_font_host_passes(self):
        self.assertProsePasses("<p>The site loads nothing from fonts.googleapis.com.</p>\n")

    def test_prose_naming_a_media_query_passes(self):
        self.assertProsePasses("<p>There is no prefers-color-scheme block anywhere.</p>\n")

    def test_a_code_block_showing_font_face_passes(self):
        self.assertProsePasses("<pre><code>@font-face { src: url(x.woff2); }</code></pre>\n")

    # ---- the same declarations in real CSS still fail ---------------------------------

    def test_box_shadow_in_css_still_fails(self):
        self.assertCssFails("box-shadow: 0 2px 8px #0002;")

    def test_text_shadow_in_css_still_fails(self):
        self.assertCssFails("text-shadow: 0 1px 0 #000;")

    def test_transition_in_css_still_fails(self):
        self.assertCssFails("transition: opacity .2s;")

    def test_animation_in_css_still_fails(self):
        self.assertCssFails("animation: pulse 1s infinite;")

    def test_gradient_in_css_still_fails(self):
        self.assertCssFails("background: linear-gradient(#fff, #eee);")

    def test_keyframes_in_a_style_block_still_fails(self):
        found = self.failures_for("<style>@keyframes pulse { to { opacity: 1; } }</style>\n")
        self.assertTrue(found)

    def test_font_face_in_a_style_block_still_fails(self):
        found = self.failures_for("<style>@font-face { src: url(x.woff2); }</style>\n")
        self.assertTrue(found)

    def test_a_font_host_in_a_style_block_still_fails(self):
        found = self.failures_for(
            "<style>body { font-family: url(https://fonts.googleapis.com/x); }</style>\n")
        self.assertTrue(found)

    def test_dark_mode_in_a_style_block_still_fails(self):
        found = self.failures_for(
            "<style>@media (prefers-color-scheme: dark) { body { background: #000; } }</style>\n")
        self.assertTrue(found)

    # ---- the line number still points at the source line ------------------------------

    def test_the_reported_line_is_the_declaration_s_own(self):
        rules.failures.clear()
        rules.check_no_decoration(
            "index.html", "<html>\n<head>\n<style>\nbody { color: #111; }\n"
                          ".x { transition: opacity .2s; }\n</style>\n</html>\n")
        self.assertEqual(1, len(rules.failures))
        self.assertIn("index.html:5", rules.failures[0])


class SiteFixture(unittest.TestCase):
    """A throwaway repository root, for the rules that read the filesystem."""

    PAGE = ('<html><head><style>body { background: #FFFFFF; '
            'font-family: system-ui, sans-serif; }</style></head><body>{body}</body></html>\n')

    def setUp(self):
        rules.failures.clear()
        self.root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.root, True)

    def write(self, rel, text):
        full = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(text)
        return full

    def page(self, body=""):
        return self.PAGE.replace("{body}", body)


class DiscoveryTest(SiteFixture):
    """What the checker covers is now the result of a walk, not a list. Both directions of
    that are pinned: a post page published next year must be picked up with nobody
    remembering to add it, and `admin/` must stay out — excluded by name in EXEMPT_DIRS
    because PRD section 7.1 grants it, not merely unnoticed."""

    def test_root_pages_and_posts_are_discovered(self):
        for name in rules.REQUIRED_PAGES:
            self.write(name, self.page())
        self.write("blog/a-post.html", self.page())
        self.write("blog/another-post.html", self.page())
        found = rules.discover_pages(self.root)
        self.assertIn("blog/a-post.html", found)
        self.assertIn("blog/another-post.html", found)
        for name in rules.REQUIRED_PAGES:
            self.assertIn(name, found)

    def test_admin_is_excluded(self):
        self.write("index.html", self.page())
        self.write("admin/index.html", self.page())
        self.assertNotIn("admin/index.html", rules.discover_pages(self.root))

    def test_admin_is_excluded_by_name_not_by_accident(self):
        # If the exemption is ever removed, this fails and names the reason.
        self.assertIn("admin", rules.EXEMPT_DIRS)

    def test_function_sources_and_drafts_are_excluded(self):
        self.write("api/index.html", self.page())
        self.write("drafts/index.html", self.page())
        self.assertEqual([], rules.discover_pages(self.root))

    def test_the_checkers_own_directory_is_skipped(self):
        self.write(".github/scripts/fixture.html", self.page())
        self.assertEqual([], rules.discover_pages(self.root))


class PostPagePathsTest(SiteFixture):
    """A post sits one directory down and reaches shared assets with `../`. A rule that
    resolved every relative URL against the repository root would call the correct link
    broken and the broken one fine."""

    def test_parent_relative_asset_resolves(self):
        self.write("headshot.jpg", "x")
        self.write("blog/a-post.html", "")
        rules.check_internal_links("blog/a-post.html", '<img src="../headshot.jpg">\n', self.root)
        self.assertEqual([], rules.failures)

    def test_root_relative_asset_from_a_post_is_broken(self):
        self.write("headshot.jpg", "x")
        rules.check_internal_links("blog/a-post.html", '<img src="headshot.jpg">\n', self.root)
        self.assertTrue(rules.failures)

    def test_a_missing_target_still_fails(self):
        rules.check_internal_links("blog/a-post.html", '<a href="../nowhere.html">x</a>\n', self.root)
        self.assertTrue(rules.failures)


class StylesheetsIdenticalTest(unittest.TestCase):
    """The rule that keeps a generated page looking hand-written. `api/_lib/render.js`
    lifts the sheet out of `blog.html` rather than carrying its own copy, and this is what
    proves the lift still happens."""

    def test_a_drifting_post_page_fails(self):
        rules.failures.clear()
        rules.check_stylesheets_identical({
            "blog.html": "<style>a { color: red; }</style>",
            "blog/a-post.html": "<style>a { color: blue; }</style>",
        })
        self.assertTrue(rules.failures)
        self.assertIn("stylesheets-identical", rules.failures[0])

    def test_a_matching_post_page_passes(self):
        rules.failures.clear()
        rules.check_stylesheets_identical({
            "blog.html": "<style>a { color: red; }</style>",
            "blog/a-post.html": "<style>a { color: red; }</style>",
        })
        self.assertEqual([], rules.failures)


class AdminExclusionTest(SiteFixture):
    """`admin/` is exempt from the design rules, so what remains of its obligations is
    asserted instead: it is kept out of search by a `noindex` tag on a page that stays
    crawlable, exactly as `journey.html` is and for the reason `robots.txt` gives."""

    def test_missing_noindex_fails(self):
        self.write("admin/index.html", "<html><head></head><body>x</body></html>")
        rules.check_admin(self.root, {})
        self.assertTrue(rules.failures)

    def test_noindex_nofollow_passes(self):
        self.write("admin/index.html",
                   '<html><head><meta name="robots" content="noindex, nofollow"></head></html>')
        rules.check_admin(self.root, {})
        self.assertEqual([], rules.failures)

    def test_noindex_without_nofollow_fails(self):
        self.write("admin/index.html",
                   '<html><head><meta name="robots" content="noindex"></head></html>')
        rules.check_admin(self.root, {})
        self.assertTrue(rules.failures)

    def test_a_sitemap_entry_for_the_admin_fails(self):
        self.write("admin/index.html",
                   '<html><head><meta name="robots" content="noindex, nofollow"></head></html>')
        self.write("sitemap.xml",
                   "<urlset><url><loc>https://jonathangong.com/admin</loc></url></urlset>")
        rules.check_admin(self.root, {})
        self.assertTrue(rules.failures)

    def test_a_comment_mentioning_the_admin_does_not_fail(self):
        # The rule is about what is LISTED. `sitemap.xml`'s own comments describe how the
        # post block is maintained, and a substring search on the word would trip on them.
        self.write("admin/index.html",
                   '<html><head><meta name="robots" content="noindex, nofollow"></head></html>')
        self.write("sitemap.xml", "<urlset><!-- maintained from the admin --></urlset>")
        rules.check_admin(self.root, {})
        self.assertEqual([], rules.failures)

    def test_a_public_page_linking_to_the_admin_fails(self):
        self.write("admin/index.html",
                   '<html><head><meta name="robots" content="noindex, nofollow"></head></html>')
        rules.check_admin(self.root, {"index.html": '<a href="/admin">admin</a>\n'})
        self.assertTrue(rules.failures)

    def test_no_admin_directory_is_not_a_failure(self):
        rules.check_admin(self.root, {})
        self.assertEqual([], rules.failures)


class DraftsTest(SiteFixture):
    """Drafts are kept off the deployment by `.vercelignore`'s `*.md`, which keys on the
    extension and nothing else. A single non-Markdown file in `drafts/` would therefore be
    served to anyone who guessed the URL — the worst outcome the admin can produce — so the
    invariant that exclusion rests on is asserted rather than assumed."""

    def test_markdown_drafts_pass(self):
        self.write("drafts/a-post.md", "---\ntitle: \"x\"\n---\n")
        rules.check_drafts(self.root)
        self.assertEqual([], rules.failures)

    def test_an_html_draft_fails(self):
        self.write("drafts/a-post.html", "<html></html>")
        rules.check_drafts(self.root)
        self.assertTrue(rules.failures)
        self.assertIn("drafts-not-servable", rules.failures[0])

    def test_a_stray_image_in_drafts_fails(self):
        self.write("drafts/screenshot.png", "x")
        rules.check_drafts(self.root)
        self.assertTrue(rules.failures)


class PostsListedTest(SiteFixture):
    """Publishing writes the post page, `blog.html`, and `sitemap.xml` in one commit so
    the three can never disagree (PRD section 6). This is the assertion that says so."""

    SITEMAP = ("<urlset><url><loc>https://jonathangong.com/blog/a-post.html</loc></url>"
               "</urlset>")

    def test_a_fully_published_post_passes(self):
        self.write("blog/a-post.html", self.page())
        self.write("sitemap.xml", self.SITEMAP)
        rules.check_posts_listed(self.root, {"blog.html": '<a href="blog/a-post.html">x</a>'})
        self.assertEqual([], rules.failures)

    def test_a_post_missing_from_the_index_fails(self):
        self.write("blog/a-post.html", self.page())
        self.write("sitemap.xml", self.SITEMAP)
        rules.check_posts_listed(self.root, {"blog.html": "<main></main>"})
        self.assertTrue(rules.failures)

    def test_a_post_missing_from_the_sitemap_fails(self):
        self.write("blog/a-post.html", self.page())
        self.write("sitemap.xml", "<urlset></urlset>")
        rules.check_posts_listed(self.root, {"blog.html": '<a href="blog/a-post.html">x</a>'})
        self.assertTrue(rules.failures)

    def test_a_sitemap_entry_with_no_page_behind_it_fails(self):
        os.makedirs(os.path.join(self.root, "blog"), exist_ok=True)
        self.write("sitemap.xml", self.SITEMAP)
        rules.check_posts_listed(self.root, {"blog.html": ""})
        self.assertTrue(rules.failures)


class SameOriginTest(unittest.TestCase):
    def test_relative_paths_are_same_origin(self):
        for url in ("favicon.ico", "journey/one.jpg", "index.html#about", "?x=1"):
            self.assertTrue(rules.is_same_origin(url), url)

    def test_other_schemes_are_not_same_origin(self):
        for url in ("data:image/png;base64,AAAA", "mailto:x@example.com", "https://example.com/"):
            self.assertFalse(rules.is_same_origin(url), url)

    def test_www_is_not_the_apex(self):
        # Canonical URLs name the apex. `www` resolving too is the reason the tag exists.
        self.assertFalse(rules.is_same_origin("https://www.jonathangong.com/"))


if __name__ == "__main__":
    sys.exit(0 if unittest.main(exit=False, verbosity=2).result.wasSuccessful() else 1)
