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

Standard library only, same as the checker. Run it from the repository root:

    python3 .github/scripts/test-design-rules.py
"""

import importlib.util
import os
import sys
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
