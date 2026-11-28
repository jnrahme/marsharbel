"""Finite publication and registry continuation negative controls."""
import copy
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'scripts/qa')]
from secret_prayers_ar_fr_policy import load, errors, RECORD, HELD, SLUGS
from i18n.secret_prayers_registry_continuation import registry_preimage, ORIGINAL_SHA256


class SecretARFR(unittest.TestCase):
    def fixture(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        for name in [RECORD, 'locales/secret-prayers-en-release.json', 'locales/registry.json']:
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, root / name)
        for code in ('ar', 'fr'):
            for slug in SLUGS:
                path = root / ('locales/' + code + '/' + slug + '-master-copy.json')
                path.parent.mkdir(exist_ok=True)
                shutil.copyfile(ROOT / path.relative_to(root), path)
        return root

    def test_policy_and_inverse(self):
        root = self.fixture()
        self.assertEqual(errors(root), [])
        self.assertEqual(hashlib.sha256(registry_preimage(root, (root / 'locales/registry.json').read_bytes())).hexdigest(), ORIGINAL_SHA256)

    def test_record_tamper(self):
        root = self.fixture()
        path = root / RECORD
        path.write_bytes(path.read_bytes() + b' ')
        with self.assertRaises(ValueError):
            load(root)

    def test_predecessor_tamper(self):
        root = self.fixture()
        path = root / 'locales/secret-prayers-en-release.json'
        path.write_bytes(path.read_bytes() + b' ')
        with self.assertRaises(ValueError):
            load(root)

    def test_missing_required_catalog(self):
        for code in ('ar', 'fr'):
            for slug in SLUGS:
                root = self.fixture()
                (root / ('locales/' + code + '/' + slug + '-master-copy.json')).unlink()
                self.assertTrue(errors(root))

    def test_every_held_url_file_and_hreflang(self):
        for code in HELD:
            for slug in SLUGS:
                root = self.fixture()
                (root / 'sitemap.xml').write_text('<loc>http://www.marsharbel.com/' + code + '/' + slug + '</loc>')
                self.assertTrue(errors(root))
                (root / 'sitemap.xml').unlink()
                path = root / code / slug / 'index.html'
                path.parent.mkdir(parents=True)
                path.write_text('held')
                self.assertTrue(errors(root))
                path.unlink()
                (root / 'index.html').write_text('<link hreflang="' + code + '" href="/' + code + '/' + slug + '">')
                self.assertTrue(errors(root))

    def test_fourth_locale_or_foreign_registry_delta_rejected(self):
        root = self.fixture()
        original = json.loads((root / 'locales/registry.json').read_bytes())
        for mutate in ('fourth', 'other'):
            data = copy.deepcopy(original)
            if mutate == 'fourth':
                cfg = data['pageMirrors']['terco-da-batalha-master']
                cfg['routes']['de'] = '/de/terco-da-batalha'
                cfg['renderLocales'].append('de')
            else:
                data['locales']['fr']['nativeName'] = 'changed'
            raw = (json.dumps(data, ensure_ascii=False, indent=1) + '\n').encode()
            with self.assertRaises(ValueError):
                registry_preimage(root, raw)

    def test_registry_serializer_and_missing_family_rejected(self):
        root = self.fixture()
        data = json.loads((root / 'locales/registry.json').read_bytes())
        with self.assertRaises(ValueError):
            registry_preimage(root, json.dumps(data).encode())
        del data['pageMirrors']['terco-da-batalha-master']
        with self.assertRaises(ValueError):
            registry_preimage(root, (json.dumps(data, ensure_ascii=False, indent=1) + '\n').encode())

    def test_registry_reordered_keys_rejected(self):
        root=self.fixture()
        data=json.loads((root/'locales/registry.json').read_bytes())
        data=dict(reversed(list(data.items())))
        with self.assertRaises(ValueError):
            registry_preimage(root,(json.dumps(data,ensure_ascii=False,indent=1)+'\n').encode())

    def test_nested_sitemap_and_generated_artifacts_rejected(self):
        for rel in ('sitemaps/2026/prayers.xml','locale-routes.js','locales/same-page-manifest.json','generated/deep/routes.json'):
            root=self.fixture();p=root/rel;p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text('"/de/powerful-secret-prayers"')
            self.assertTrue(errors(root),rel)

    def test_fifth_page_not_exempt(self):
        from check_new_page_locales import check
        root=self.fixture()
        page='fifth-secret-page.html';family='fifth-secret-master'
        source='mary-who-goes-ahead-prayer-master'
        shutil.copyfile(ROOT/'mary-who-goes-ahead-prayer.html',root/page)
        registry=json.loads((root/'locales/registry.json').read_bytes())
        registry['pageMirrors'][family]={'master':page,'english':'/fifth-secret-page','routes':{'ar':'/ar/fifth-secret-page','fr':'/fr/fifth-secret-page'},'renderLocales':['ar','fr']}
        (root/'locales/registry.json').write_text(json.dumps(registry))
        (root/'locales/en').mkdir(exist_ok=True)
        contract=json.loads((ROOT/('locales/en/'+source+'-bindings.json')).read_bytes())
        contract['master']=page
        (root/('locales/en/'+family+'-bindings.json')).write_text(json.dumps(contract))
        shutil.copyfile(ROOT/('locales/en/'+source+'-copy.json'),root/('locales/en/'+family+'-copy.json'))
        checked,failures=check(root,[page],registry)
        self.assertEqual(checked,[page])
        self.assertTrue(any('fifth-secret' in x and 'ar' in x for x in failures),failures)
        self.assertTrue(any('fifth-secret' in x and 'fr' in x for x in failures),failures)

    def test_all_eight_direct_render_structures(self):
        from i18n.catalog import load_catalog
        from i18n.page_mirror import render_page
        from bs4 import BeautifulSoup
        registry, _ = load_catalog(ROOT)
        for code in ('ar', 'fr'):
            for slug in SLUGS:
                text=render_page(ROOT, registry, code, slug+'-master', '/'+code+'/'+slug)
                soup=BeautifulSoup(text,'html.parser')
                self.assertEqual(soup.html['lang'],code)
                self.assertEqual({x['hreflang'] for x in soup.select('head link[hreflang]')},{'en','ar','fr','x-default'})
                if slug=='terco-da-batalha':
                    from i18n.catalog import home_url
                    home=soup.select_one('header nav a[href="'+home_url(registry,code)+'"]')
                    schemas=[json.loads(x.string)for x in soup.select('script[type="application/ld+json"]')]
                    breadcrumb=next(x['breadcrumb']for x in schemas if 'breadcrumb'in x)
                    self.assertEqual(breadcrumb['itemListElement'][0]['name'],home.get_text(' ',strip=True))
                    self.assertNotEqual(home.get_text(' ',strip=True),soup.select_one('header > div > a').get_text(' ',strip=True))
                    self.assertEqual(len(soup.select('article.prayer-card')),3)
                    self.assertNotIn('Salve Rainha',text)

    def test_original_portuguese_slots_match_source_exact_english(self):
        english=json.loads((ROOT/'locales/en/terco-da-batalha-master-copy.json').read_bytes())
        for code in ('ar','fr'):
            copy=json.loads((ROOT/('locales/'+code+'/terco-da-batalha-master-copy.json')).read_bytes())
            for n in (77,80,83,86,91,95,99):
                key='terco.source-exact.'+str(n)
                self.assertEqual(copy[key],english[key])

    def test_all_eight_keyed_catalogs(self):
        from i18n.keyed_master import apply_keyed_master
        for code in ('ar', 'fr'):
            for slug in SLUGS:
                apply_keyed_master(ROOT, slug + '-master', code)


if __name__ == '__main__':
    unittest.main()
