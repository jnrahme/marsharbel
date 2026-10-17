import re, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from i18n.encyclopedia_nav import MARKING_LOCALES, route_and_mark_nav  # noqa: E402

LOCALE = re.compile(r'^/(ar|de|es|fr|hi|it|pl|pt|ru|th|zh-Hans)(/|$)')
# th pages built through page_mirror/home_mirror (route_and_mark_nav). Excluded:
# help-me-pray (no header), the strict film family (header outside the marking system
# on every locale).
MARKED = ['index', 'history', 'music', 'travel']


def unmarked(header):
    bad = []
    for m in re.finditer(r'<a\b([^>]*?)href="([^"]*)"([^>]*)>', header):
        pre, href, post = m.groups()
        if href.startswith(('#', 'mailto:', 'tel:', 'http')) or not href.startswith('/') or LOCALE.match(href):
            continue
        if 'hreflang="en"' not in pre + post:
            bad.append(href)
    return bad


class ThaiHeaderMarking(unittest.TestCase):
    def test_th_is_a_marking_locale(self):
        self.assertIn('th', MARKING_LOCALES)

    def test_pages_have_no_unmarked_english_header_link(self):
        for name in MARKED:
            text = (ROOT / 'th' / f'{name}.html').read_text(encoding='utf8')
            self.assertEqual(unmarked(re.search(r'<header\b[\s\S]*?</header>', text)[0]), [], name)

    def test_negative_control_unmarked_english_link_is_caught_and_marked(self):
        header = '<header><nav class="links"><a href="/some-english-only-page">Page</a></nav></header>'
        self.assertEqual(unmarked(header), ['/some-english-only-page'])
        marked = route_and_mark_nav(header, ROOT, 'th')
        self.assertEqual(unmarked(marked), [])
        self.assertIn('hreflang="en"', marked)
        self.assertIn('(ภาษาอังกฤษ)', marked)

    def test_launch_qualifier_header_annotation_is_upgraded_not_doubled(self):
        header = ('<header><nav class="links"><a href="/saints">Saints'
                  '<span class="launch-english-qualifier"> (ภาษาอังกฤษ)</span></a></nav></header>')
        marked = route_and_mark_nav(header, ROOT, 'th')
        self.assertEqual(marked.count('launch-english-qualifier'), 0)
        self.assertEqual(marked.count('enc-language'), 1)
        # The upgraded mark carries the qualifier twice: aria-label plus visible span.
        self.assertEqual(marked.count('(ภาษาอังกฤษ)'), 2)
        self.assertIn('aria-label="Saints (ภาษาอังกฤษ)"', marked)
        self.assertEqual(unmarked(marked), [])


if __name__ == '__main__':
    unittest.main()
