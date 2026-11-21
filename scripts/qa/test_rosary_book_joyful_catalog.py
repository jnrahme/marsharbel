#!/usr/bin/env python3
"""Mutation proof for the rosary-book-joyful copy catalog in check_i18n_policy."""
import json, shutil, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/qa'))
sys.path.insert(0, str(ROOT / 'scripts'))
from i18n.catalog import read_json
import check_i18n_policy as policy

PAGE = 'rosary-book-joyful.html'
CATALOG = 'locales/en/rosary-book-joyful-copy.json'

class RosaryBookJoyfulCatalogTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        shutil.copytree(ROOT / 'locales', self.root / 'locales')
        # Minimal policy fixture: tests unrelated hardcoded strings, not full mirror rendering.
        registry = json.loads((self.root / 'locales/registry.json').read_text())
        registry['exactMirrors'] = {}
        # The film family has its own strict gate (test_film_master_family); keep it out of this string-policy fixture.
        registry.get('pageMirrors', {}).pop('film-premiere-master', None)
        (self.root / 'locales/registry.json').write_text(json.dumps(registry))
        shutil.copyfile(ROOT / 'same-page-copy.js', self.root / 'same-page-copy.js')
        # Mirror capability validation needs real source masters in this fixture.
        for cfg in registry.get('pageMirrors', {}).values():
            master = cfg['master']
            if not (self.root / master).exists():
                (self.root / master).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / master, self.root / master)
        shutil.copyfile(ROOT / PAGE, self.root / PAGE)

    def page_errors(self):
        return [e for e in policy.check(self.root) if PAGE in e]

    def edit_catalog(self, update):
        path = self.root / CATALOG
        data = read_json(path)
        update(data)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

    def test_baseline_catalog_covers_page(self):
        self.assertEqual(self.page_errors(), [])

    def test_remove_one_page_string_turns_stale_check_red(self):
        # Drop a cataloged string from the page; the catalog entry goes stale.
        page = self.root / PAGE
        text = page.read_text()
        assert '&#9654; Listen' in text
        page.write_text(text.replace('&#9654; Listen', '', 1))
        errors = self.page_errors()
        self.assertTrue(any('catalog entries missing from the page' in e for e in errors), errors)

    def test_add_unlisted_literal_stays_red(self):
        page = self.root / PAGE
        page.write_text(page.read_text().replace('</body>', '<p>unlisted probe literal</p></body>'))
        errors = self.page_errors()
        self.assertTrue(any('new hardcoded wording' in e for e in errors), errors)

if __name__ == '__main__':
    unittest.main()
