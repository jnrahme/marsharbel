import re, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from i18n.encyclopedia_nav import MARKING_LOCALES, route_and_mark_nav  # noqa: E402

LOCALE = re.compile(r'^/(ar|de|es|fr|hi|it|pl|pt|ru|th|zh-Hans)(/|$)')
# pt pages built through page_mirror/home_mirror (route_and_mark_nav). The finish_nav
# pages (Eucharistic, travel family) get routing only until the finish_nav marking PR.
MARKED = ['o-dia-22-do-mes', 'annaya', 'biografia', 'index', 'music', 'novena', 'oracoes', 'peregrinacao', 'todos-os-santos']


def unmarked(header):
    bad = []
    for m in re.finditer(r'<a\b([^>]*?)href="([^"]*)"([^>]*)>', header):
        pre, href, post = m.groups()
        if href.startswith(('#', 'mailto:', 'tel:', 'http')) or not href.startswith('/') or LOCALE.match(href):
            continue
        if 'hreflang="en"' not in pre + post:
            bad.append(href)
    return bad


class PortugueseHeaderMarking(unittest.TestCase):
    def test_pt_is_a_marking_locale(self):
        self.assertIn('pt', MARKING_LOCALES)

    def test_pages_have_no_unmarked_english_header_link(self):
        for name in MARKED:
            text = (ROOT / 'pt' / f'{name}.html').read_text(encoding='utf8')
            self.assertEqual(unmarked(re.search(r'<header\b[\s\S]*?</header>', text)[0]), [], name)

    def test_negative_control_unmarked_english_link_is_caught_and_marked(self):
        header = '<header><nav class="links"><a href="/some-english-only-page">Page</a></nav></header>'
        self.assertEqual(unmarked(header), ['/some-english-only-page'])
        marked = route_and_mark_nav(header, ROOT, 'pt')
        self.assertEqual(unmarked(marked), [])
        self.assertIn('hreflang="en"', marked)
        self.assertIn('(em inglês)', marked)


if __name__ == '__main__':
    unittest.main()
