"""Every locale page is accounted for; rebuilt routes must pass strict mirror QA."""
import json
from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.mirror_structure import check_pair, NORMALIZERS

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

    def test_extracted_features_have_bounded_provenance_and_shell(self):
        from i18n.feature_mirror import check_feature, FEATURES
        for path, entry in self.policy['pages'].items():
            if entry['status'] != 'extracted-feature':
                continue
            self.assertNotIn(path,self.policy['exceptions'])
            self.assertIn(entry['family'],FEATURES)
            self.assertEqual(path,FEATURES[entry['family']]['target'])
            contract_path='config/feature-mirrors/'+entry['family']+'.json'
            contract=json.loads((ROOT/contract_path).read_text())
            self.assertEqual(check_feature(ROOT,entry,contract),[])

    def test_strict_pages_have_no_unregistered_structure_changes(self):
        for path,entry in self.policy['pages'].items():
            if entry['status']!='strict': continue
            # No exception masking is implemented. A bounded exception needs a
            # specific tested normalizer and verified evidence, never a wildcard.
            self.assertNotIn(path,self.policy['exceptions'],'No whole-page bypasses permitted')
            normalizers=entry.get('normalizers',[])
            for name in normalizers:
                self.assertIn(name,NORMALIZERS,f'{path}: unregistered normalizer {name}')
            differences=check_pair((ROOT/entry['master']).read_text(),(ROOT/path).read_text(),entry['masterRoute'],entry['route'],normalizers)
            self.assertEqual(differences,[],f'{path}: divergence from {entry["master"]}')

if __name__=='__main__':unittest.main()
