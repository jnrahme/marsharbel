import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from i18n.encyclopedia_nav import strip_legacy_partial_nav_marks, route_nav_hrefs, mark_english_nav_hrefs

ROOT = Path(__file__).resolve().parents[2]

PARTIAL = '<html lang="de"><body><header class="topbar"><nav class="links">' \
    '<a href="/history" hreflang="en" aria-label="Ganze Geschichte (Englisch)">Ganze Geschichte</a>' \
    '<a hreflang="en" aria-label="Vermächtnis (Englisch)" href="/saint-charbel-encyclopedia">Vermächtnis <span class="enc-language">(Englisch)</span></a>' \
    '<a href="/de/biografie">Leben</a>' \
    '</nav></header></body></html>'


class StripLegacyPartialNavMarksTests(unittest.TestCase):
    def test_partial_attrs_removed(self):
        out = strip_legacy_partial_nav_marks(PARTIAL, ROOT, 'de')
        first = re.search(r'<a href="/history"[^>]*>', out)[0]
        self.assertNotIn('hreflang', first)
        self.assertNotIn('aria-label', first)

    def test_fully_marked_anchor_untouched(self):
        out = strip_legacy_partial_nav_marks(PARTIAL, ROOT, 'de')
        self.assertIn('Vermächtnis <span class="enc-language">(Englisch)</span>', out)
        marked = re.search(r'<a hreflang="en"[^>]*Vermächtnis[\s\S]*?</a>', out)[0]
        self.assertIn('aria-label="Vermächtnis (Englisch)"', marked)

    def test_locale_internal_link_untouched(self):
        out = strip_legacy_partial_nav_marks(PARTIAL, ROOT, 'de')
        self.assertIn('<a href="/de/biografie">Leben</a>', out)

    def test_english_noop(self):
        self.assertEqual(strip_legacy_partial_nav_marks(PARTIAL, ROOT, 'en'), PARTIAL)

    def test_non_marking_locale_noop(self):
        self.assertEqual(strip_legacy_partial_nav_marks(PARTIAL, ROOT, 'zh-Hans'), PARTIAL)

    def test_idempotent(self):
        once = strip_legacy_partial_nav_marks(PARTIAL, ROOT, 'de')
        self.assertEqual(strip_legacy_partial_nav_marks(once, ROOT, 'de'), once)

    def test_end_to_end_strip_route_mark(self):
        # After stripping, routing sends /history to the de twin and marking
        # fully discloses the twin-less encyclopedia link.
        out = mark_english_nav_hrefs(route_nav_hrefs(strip_legacy_partial_nav_marks(PARTIAL, ROOT, 'de'), ROOT, 'de'), ROOT, 'de')
        self.assertIn('href="/de/biografie">Ganze Geschichte</a>', out)
        enc = re.search(r'<a [^>]*saint-charbel-encyclopedia[\s\S]*?</a>', out)[0]
        self.assertIn('hreflang="en"', enc)
        self.assertIn('<span class="enc-language">(Englisch)</span>', enc)
        self.assertIn('aria-label="Vermächtnis (Englisch)"', enc)


PARTIAL_STRAY = '<html lang="fr"><body><header class="topbar"><nav class="links">' \
    '<div class="enc-nav-item"><a href="/saint-charbel-encyclopedia" hreflang="en" aria-label="Encyclop\\u00e9die (en anglais)">Encyclop\\u00e9die</a> <span class="enc-language">(en anglais)</span></div>' \
    '<div class="enc-nav-item"><a href="/history" hreflang="en" aria-label="Biographie compl\\u00e8te (en anglais)">Biographie compl\\u00e8te</a> <span class="enc-language">(en anglais)</span></div>' \
    '</nav></header><main><span class="enc-language">(en anglais)</span></main></body></html>'


class StripLegacyStraySpanTests(unittest.TestCase):
    """Legacy partial form B: visible qualifier span emitted AFTER </a>."""

    def test_stray_span_after_anchor_removed(self):
        out = strip_legacy_partial_nav_marks(PARTIAL_STRAY, ROOT, 'fr')
        header = re.search(r'<header[\s\S]*?</header>', out)[0]
        self.assertNotIn('enc-language', header)

    def test_stray_span_outside_header_untouched(self):
        out = strip_legacy_partial_nav_marks(PARTIAL_STRAY, ROOT, 'fr')
        main = re.search(r'<main>[\s\S]*?</main>', out)[0]
        self.assertIn('<span class="enc-language">(en anglais)</span>', main)

    def test_stray_idempotent(self):
        once = strip_legacy_partial_nav_marks(PARTIAL_STRAY, ROOT, 'fr')
        self.assertEqual(strip_legacy_partial_nav_marks(once, ROOT, 'fr'), once)

    def test_end_to_end_no_twin_labeled_english(self):
        # The fr/biographie twin must route and must NOT keep the English
        # qualifier; the twin-less encyclopedia link must be fully marked
        # exactly once (no duplicate qualifier inside or after the anchor).
        out = mark_english_nav_hrefs(route_nav_hrefs(strip_legacy_partial_nav_marks(PARTIAL_STRAY, ROOT, 'fr'), ROOT, 'fr'), ROOT, 'fr')
        twin = re.search(r'<a href="/fr/biographie">[\s\S]*?</a>', out)[0]
        self.assertNotIn('enc-language', twin)
        self.assertNotIn('hreflang', twin)
        enc = re.search(r'<a [^>]*saint-charbel-encyclopedia[\s\S]*?</a>', out)[0]
        self.assertEqual(enc.count('enc-language'), 1)
        self.assertIn('hreflang="en"', enc)
        header = re.search(r'<header[\s\S]*?</header>', out)[0]
        self.assertEqual(header.count('enc-language'), 1)


if __name__ == '__main__':
    unittest.main()
