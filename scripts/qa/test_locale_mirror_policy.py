"""Every locale page is accounted for; rebuilt routes must pass strict mirror QA."""
import json
from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.mirror_structure import check_pair, NORMALIZERS, CONTEXT_NORMALIZERS

class LocaleMirrorPolicy(unittest.TestCase):
    def setUp(self):
        self.registry=json.loads((ROOT/'locales/registry.json').read_text())
        self.policy=json.loads((ROOT/'config/locale-mirror-policy.json').read_text())

    def test_registered_english_escape_for_non_equivalent_miracles_hub(self):
        from i18n.same_page_injection import with_english_sources, _english_source_cache
        _english_source_cache.clear()
        manifest=json.loads((ROOT/'locales/same-page-manifest.pending.json').read_text())
        enriched=with_english_sources(ROOT,manifest)
        self.assertEqual(enriched['englishSources']['/ar/miracles'],'/miracles/')
        # An English escape route must not promote the Arabic hub to verified.
        for family in enriched['pages'].values():
            for code,variant in family['variants'].items():
                if variant['path'].rstrip('/')=='/ar/miracles':
                    self.assertNotEqual(variant['status'],'verified')

    def test_every_locale_page_has_explicit_master_and_status(self):
        files={p.relative_to(ROOT).as_posix() for lang in self.registry['locales'] if lang!='en' for p in (ROOT/lang).rglob('*.html')}
        self.assertEqual(files,set(self.policy['pages']),'Every new or removed locale route must update mirror coverage')
        for path,entry in self.policy['pages'].items():
            self.assertIn(entry['status'],('strict','migration-debt','extracted-feature'),path)
            self.assertTrue((ROOT/entry['master']).is_file(),path)
            self.assertFalse(Path(entry['master']).is_absolute(),path)
            self.assertNotIn('..',Path(entry['master']).parts,path)
            self.assertTrue(entry['route'].startswith('/'+entry['locale']+'/'),path)

    def test_activated_home_routes_cannot_stay_migration_debt(self):
        for lang in self.registry.get('homepageMirrors',{}).get('renderLocales',[]):
            self.assertEqual(self.policy['pages'][lang+'/index.html']['status'],'strict',lang)

    def test_registered_film_master_family(self):
        from i18n.film_master_family import registered, validate_family
        if registered(ROOT):
            self.assertEqual(validate_family(ROOT),[])

    def test_extracted_features_have_bounded_provenance_and_shell(self):
        from i18n.film_master_family import FAMILY, registered, validate_family
        for path, entry in self.policy['pages'].items():
            if entry['status'] != 'extracted-feature':
                continue
            self.assertNotIn(path,self.policy['exceptions'])
            self.assertEqual(entry['family'],FAMILY,path+': only the strict film family may be an extracted feature')
            self.assertEqual(path,entry['locale']+'/charbel-film-premiere.html')
            self.assertEqual((entry['route'],entry['master'],entry['masterRoute']),('/'+entry['locale']+'/charbel-film-premiere','charbel-film-premiere.html','/charbel-film-premiere'),path)
            self.assertTrue(registered(ROOT),path+': extracted-feature family must be registered in locales/registry.json')
            self.assertFalse(entry.get('normalizers'),path)
            self.assertEqual(validate_family(ROOT),[],path)

    def test_strict_pages_have_no_unregistered_structure_changes(self):
        for path,entry in self.policy['pages'].items():
            if entry['status']!='strict': continue
            # No exception masking is implemented. A bounded exception needs a
            # specific tested normalizer and verified evidence, never a wildcard.
            self.assertNotIn(path,self.policy['exceptions'],'No whole-page bypasses permitted')
            normalizers=entry.get('normalizers',[])
            for name in normalizers:
                self.assertIn(name,tuple(NORMALIZERS)+tuple(CONTEXT_NORMALIZERS),f'{path}: unregistered normalizer {name}')
            context=None
            if any(name in CONTEXT_NORMALIZERS for name in normalizers):
                from i18n.localized_source_links import resolve_family
                context={'family':resolve_family(self.registry,entry['master'],entry['route'],entry['locale']),
                         'lang':entry['locale']}
                if 'stories-keyed-data-copy' in normalizers:
                    from i18n.stories_policy_context import trusted_context
                    context=trusted_context(ROOT,self.registry,entry)
            differences=check_pair((ROOT/entry['master']).read_text(),(ROOT/path).read_text(),entry['masterRoute'],entry['route'],normalizers,context)
            self.assertEqual(differences,[],f'{path}: divergence from {entry["master"]}')

    def test_citation_targets_match_registration(self):
        # The structural signature records no hrefs, so citation correctness is
        # asserted explicitly: every rendered twin of a sourceLinks family
        # carries exactly one anchor per registered target (or the master target
        # when the locale registers no swap) and no anchor registered to another
        # locale or family.
        from bs4 import BeautifulSoup
        from i18n.localized_source_links import registered_targets
        for name,cfg in self.registry.get('pageMirrors',{}).items():
            source_links=cfg.get('sourceLinks') or {}
            if not source_links: continue
            master_hrefs=list({master for mapping in source_links.values() for master in mapping})
            self.assertTrue(master_hrefs,name+': sourceLinks without master hrefs')
            for lang,route in (cfg.get('routes') or {}).items():
                page=ROOT/(route.lstrip('/')+'.html')
                self.assertTrue(page.is_file(),f'{name}:{lang} rendered twin missing: {page}')
                soup=BeautifulSoup(page.read_text(),'html.parser')
                mapping=source_links.get(lang) or {}
                own_targets=set(mapping.values())
                for master_href in master_hrefs:
                    expected=mapping.get(master_href,master_href)
                    found=len(soup.select(f'a[href="{expected}"]'))
                    self.assertEqual(found,1,f'{name}:{lang} citation target {expected} occurs {found} times')
                foreign={h:o for h,o in registered_targets(self.registry,skip_family=name,skip_lang=lang).items() if h not in own_targets}
                for anchor in soup.select('a[href]'):
                    self.assertNotIn(anchor['href'],foreign,f'{name}:{lang} carries citation target registered to {foreign.get(anchor["href"])}: {anchor["href"]}')

if __name__=='__main__':unittest.main()
