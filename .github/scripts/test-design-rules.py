#!/usr/bin/env python3
"""Tests for the design rules that are easy to get subtly wrong.

`zero-external-requests` used to reject every <link> element outright. It now turns on what
the tag actually makes the browser do (PRD decision 37), and that distinction is exactly the
kind that erodes: a permissive bug here is invisible until an external request has shipped.
So both halves are pinned — what must still fail, and what must now pass.

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
