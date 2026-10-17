"""Negative controls for the PR new-page full-catalog gate."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from check_new_page_locales import check, required_locales, public_page

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))


class NewPageLocales(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.registry = {'locales': {c: {} for c in ['en','ar','fr','es','pt','it','de','pl']},
                         'pageMirrors': {'fixture': {'master': 'new-page.html'}}}
        self.write('locales/registry.json', self.registry)
        master = '<html><head><title>Title</title></head><body><main><h1>Hello</h1></main></body></html>'
        (self.root/'new-page.html').write_text(master)
        self.contract = {'master': 'new-page.html', 'masterSha256': hashlib.sha256(master.encode()).hexdigest(),
                         'bindings': [
                             {'key':'page.title','selector':'title','kind':'text','nodeIndex':0,'source':'Title'},
                             {'key':'page.heading','selector':'h1','kind':'text','nodeIndex':0,'source':'Hello'}]}
        self.write('locales/en/fixture-bindings.json', self.contract)
        for code in self.registry['locales']:
            self.write(f'locales/{code}/fixture-copy.json', {'page.title':'Title','page.heading':'Hello'})

    def write(self, path, data):
        file = self.root/path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(json.dumps(data))

    def errors(self, added=None, base=None):
        return check(self.root, added or ['new-page.html'], base or self.registry)[1]

    def test_complete_catalogs_pass(self):
        self.assertEqual(self.errors(), [])

    def test_english_only_new_page_fails(self):
        for code in self.registry['locales']:
            if code != 'en': (self.root/f'locales/{code}/fixture-copy.json').unlink()
        self.assertEqual(len(self.errors()), 7)

    def test_unregistered_page_fails(self):
        self.registry['pageMirrors'] = {}
        self.write('locales/registry.json', self.registry)
        self.assertIn('register exactly one', self.errors()[0])

    def test_missing_key_fails(self):
        self.write('locales/fr/fixture-copy.json', {'page.title':'Titre'})
        self.assertIn('missing/extra message keys', self.errors()[0])

    def test_empty_key_fails(self):
        self.write('locales/de/fixture-copy.json', {'page.title':'Titel','page.heading':''})
        self.assertIn('unsafe or empty', self.errors()[0])

    def test_placeholders_must_match(self):
        self.write('locales/es/fixture-copy.json', {'page.title':'Título {name}','page.heading':'Hola'})
        self.assertIn('placeholders differ', self.errors()[0])

    def test_ui_only_keys_cannot_hide_unkeyed_body(self):
        self.contract['bindings'].pop()
        self.write('locales/en/fixture-bindings.json', self.contract)
        self.write('locales/en/fixture-copy.json', {'page.title':'Title'})
        self.assertTrue(any('unkeyed master text: Hello' in e for e in self.errors()))

    def test_unrelated_bindings_master_fails(self):
        self.contract['master'] = 'unrelated.html'
        self.write('locales/en/fixture-bindings.json', self.contract)
        self.assertIn('not unrelated text', self.errors()[0])

    def test_fake_locale_registry_cannot_hide_english_page(self):
        self.registry['locales']['fake'] = {}
        self.write('locales/registry.json',self.registry)
        (self.root/'fake').mkdir()
        (self.root/'fake/new.html').write_text('<html lang=en></html>')
        self.assertIn('register exactly one', self.errors(['fake/new.html'])[0])

    def test_unkeyed_metadata_attribute_fails(self):
        file=self.root/'new-page.html'
        file.write_text(file.read_text().replace('</head>','<meta name="description" content="Unkeyed"></head>'))
        self.contract['masterSha256']=hashlib.sha256(file.read_bytes()).hexdigest()
        self.write('locales/en/fixture-bindings.json', self.contract)
        self.assertTrue(any('unkeyed content attribute' in e for e in self.errors()))

    def test_root_page_mislabeled_as_locale_does_not_bypass(self):
        (self.root/'unregistered.html').write_text('<html lang=fr></html>')
        self.assertIn('register exactly one', self.errors(['unregistered.html'])[0])

    def test_stale_master_pin_fails(self):
        self.contract['masterSha256'] = '0'*64
        self.write('locales/en/fixture-bindings.json', self.contract)
        self.assertIn('master changed', self.errors()[0])

    def test_hi_th_activate_when_in_base_not_candidate_only(self):
        self.assertNotIn('hi', required_locales(self.registry))
        base = {'locales': {'hi':{},'th':{},'zh-Hans':{}}}
        self.assertEqual(len(self.errors(base=base)), 3)
        for code in ['hi','th','zh-Hans']:
            self.write(f'locales/{code}/fixture-copy.json', {'page.title':'Title','page.heading':'Hello'})
        self.assertEqual(self.errors(base=base), [])

    def test_adding_source_without_public_output_is_not_a_new_url(self):
        self.assertEqual(self.errors(['src/pages/new-page.html']), [])
        self.assertFalse(public_page('templates/fixture.html'))

    def test_added_locale_page_does_not_create_new_english_requirement(self):
        (self.root/'ar').mkdir()
        (self.root/'ar/new-page.html').write_text('<html lang=ar></html>')
        self.assertEqual(self.errors(['ar/new-page.html']), [])

    def test_unregistered_utility_page_is_not_exempt(self):
        (self.root/'utility.html').write_text('<html lang=en></html>')
        self.assertIn('register exactly one', self.errors(['utility.html'])[0])

    def test_git_diff_rename_is_seen_as_added_public_page(self):
        subprocess.run(['git','init','-q',str(self.root)],check=True)
        def git(*args):
            return subprocess.check_output(['git','-C',str(self.root),*args],text=True).strip()
        git('add','.')
        git('-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','base')
        base=git('rev-parse','HEAD')
        git('mv','new-page.html','renamed.html')
        git('-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','rename')
        added=git('diff','--no-renames','--diff-filter=A','--name-only',base,'HEAD').splitlines()
        self.assertEqual(added,['renamed.html'])
        self.assertIn('register exactly one', self.errors(added)[0])


class FilmExactShellCoverage(unittest.TestCase):
    def setUp(self):
        import copy
        from collections import Counter
        from bs4 import BeautifulSoup
        from check_new_page_locales import film_shell_coverage
        self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.page='charbel-film-premiere.html';self.family='film-premiere-master'
        self.contract=json.loads((ROOT/'locales/en/film-premiere-master-bindings.json').read_text())
        (self.root/self.page).write_bytes((ROOT/self.page).read_bytes())
        self.soup=BeautifulSoup((ROOT/self.page).read_text(),'html.parser')
        for file in ('locales/registry.json','locales/en/film-premiere-shell-copy.json','locales/en/nav-legacy-copy.json','locales/en/travel.json'):
            path=self.root/file;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((ROOT/file).read_bytes())
        # Independent fixture counter is collected from real uncovered DOM nodes.
        from bs4 import Comment,NavigableString,Doctype,Declaration
        covered=set()
        for b in self.contract['bindings']:
            node=self.soup.select(b['selector'])[0]
            covered.add(('text',id(node.contents[b['nodeIndex']]))) if b['kind']=='text' else covered.add(('attr',id(node),b['attribute']))
        self.uncovered=Counter()
        for node in self.soup.descendants:
            if isinstance(node,NavigableString) and not isinstance(node,(Comment,Doctype,Declaration)) and node.parent.name not in ('script','style') and str(node).strip() and ('text',id(node)) not in covered:self.uncovered[' '.join(str(node).split())]+=1
            if getattr(node,'attrs',None):
                attrs=['alt','title','aria-label','placeholder']
                if node.name=='meta' and (node.get('name')=='description' or node.get('property') in ('og:title','og:description','twitter:title','twitter:description')):attrs.append('content')
                for attr in attrs:
                    if node.get(attr) and ('attr',id(node),attr) not in covered:self.uncovered[node[attr]]+=1
        self.validate=film_shell_coverage
    def call(self):return self.validate(self.root,self.page,self.family,self.contract,self.soup,self.uncovered)
    def test_exact_real_counter_passes(self):self.assertTrue(self.call())
    def test_extra_uncovered_and_each_catalog_occurrence_refuse(self):
        original=self.uncovered.copy()
        for value in ['Uncataloged injected text',*json.loads((self.root/'locales/en/film-premiere-shell-copy.json').read_text())[self.page]]:
            self.uncovered=original.copy();self.uncovered[value]+=1
            with self.assertRaisesRegex(ValueError,'exact uncovered/catalog counter mismatch'):self.call()
    def test_missing_nav_legacy_phrase_refuse(self):
        nav=json.loads((self.root/'locales/en/nav-legacy-copy.json').read_text())['values'][self.page]
        for value in nav:
            original=self.uncovered.copy();self.uncovered[value]-=1
            with self.assertRaisesRegex(ValueError,'exact uncovered/catalog counter mismatch'):self.call()
            self.uncovered=original
    def test_non_film_page_same_strings_not_covered(self):
        self.page='other.html';self.assertFalse(self.call())
    def test_unregistered_family_not_covered(self):
        file=self.root/'locales/registry.json';r=json.loads(file.read_text());r['pageMirrors'].pop(self.family);file.write_text(json.dumps(r));self.assertFalse(self.call())
    def test_hub_allowance_absent_without_nav_condition(self):
        file=self.root/self.page;file.write_text(file.read_text().replace('<nav class="links"','<nav class="other"'))
        with self.assertRaisesRegex(ValueError,'exact uncovered/catalog counter mismatch'):self.call()
        value=json.loads((self.root/'locales/en/travel.json').read_text())['hubLabel'];self.uncovered[value]-=1
        self.assertTrue(self.call())
    def test_extra_travel_occurrence_refuse(self):
        value=json.loads((self.root/'locales/en/travel.json').read_text())['hubLabel'];self.uncovered[value]+=1
        with self.assertRaisesRegex(ValueError,'exact uncovered/catalog counter mismatch'):self.call()
    def test_caption_pair_mapping_exactly_once(self):
        caption=next(b['source'] for b in self.contract['bindings'] if b['key']=='premiere.videoCaption')
        file=self.root/'locales/en/film-premiere-shell-copy.json';d=json.loads(file.read_text());d[self.page][caption]=2;file.write_text(json.dumps(d))
        with self.assertRaisesRegex(ValueError,'exactly one occurrence'):self.call()
        d[self.page][caption]=1;file.write_text(json.dumps(d));self.contract['bindings']=[b for b in self.contract['bindings'] if not(b['key']=='premiere.videoCaption' and b['kind']=='attribute')]
        with self.assertRaisesRegex(ValueError,'exact caption pair'):self.call()

if __name__ == '__main__':
    unittest.main()
