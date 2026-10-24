"""Every locale, both comparison sides, one mutation at a time."""
import json,sys,tempfile,shutil,unittest,os
from pathlib import Path
from unittest.mock import patch
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.keyed_master import apply_keyed_master
from i18n.mirror_structure import check_pair,signature
from i18n import stories_shelf_copy as normalizer
ALL_CODES=('ar','fr','es','pt','it','de','pl','ru','hi','th','zh-Hans')
CODES=tuple(x for x in ALL_CODES if x==os.environ.get('STORIES_TEST_LOCALE')) if os.environ.get('STORIES_TEST_LOCALE') else ALL_CODES

class StoriesDataCopy(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        fixtures=ROOT/'scripts/tests/fixtures/stories-keyed-data'
        (self.root/'templates/masters').mkdir(parents=True);(self.root/'locales/en').mkdir(parents=True)
        shutil.copyfile(fixtures/'master.html',self.root/'templates/masters/stories.html')
        shutil.copyfile(fixtures/'bindings.json',self.root/'locales/en/stories-master-bindings.json')
        shutil.copyfile(fixtures/'en.json',self.root/'locales/en/stories-master-copy.json')
        for lang in CODES:
            (self.root/f'locales/{lang}').mkdir(exist_ok=True)
            shutil.copyfile(fixtures/f'{lang}.json',self.root/f'locales/{lang}/stories-master-copy.json')
        self.mock=patch.object(normalizer,'__file__',str(self.root/'scripts/i18n/stories_shelf_copy.py'));self.mock.start()
    def tearDown(self):self.mock.stop();self.tmp.cleanup()
    def texts(self,lang):
        raw,soup,_=apply_keyed_master(self.root,'stories-master',lang)
        return raw.decode(),str(soup)
    def compare(self,en,local,code,**change):
        context={'family':'stories-master','lang':code,'masterSha256':normalizer.MASTER_SHA256};context.update(change)
        return check_pair(en,local,'/stories','/stories',('stories-keyed-data-copy',),context)
    def assert_rejected(self,en,local,lang):
        try:self.assertTrue(self.compare(en,local,lang))
        except (ValueError,KeyError):pass
    def test_real_baseline_23_attributes_and_all_locale_positive(self):
        binds=json.loads((self.root/'locales/en/stories-master-bindings.json').read_text())['bindings']
        data=[b for b in binds if b.get('attribute') in normalizer.DATA_COPY]
        self.assertEqual(len(data),23)
        for lang in CODES:
            with self.subTest(lang=lang):
                en,local=self.texts(lang);a,b=BeautifulSoup(en,'html.parser'),BeautifulSoup(local,'html.parser')
                self.assertEqual(sum(a.select_one(x['selector'])[x['attribute']]!=b.select_one(x['selector'])[x['attribute']] for x in data),23)
                self.assertEqual(check_pair(en,local,'/stories','/stories'),['main'])
                self.assertEqual(self.compare(en,local,lang),[])
    def test_each_keyed_attribute_tamper_on_each_side_each_locale(self):
        binds=json.loads((self.root/'locales/en/stories-master-bindings.json').read_text())['bindings']
        for lang in CODES:
            en,local=self.texts(lang)
            for b in [x for x in binds if x.get('attribute') in normalizer.DATA_COPY]:
                for side in ('en','locale'):
                    with self.subTest(lang=lang,key=b['key'],side=side):
                        s=BeautifulSoup(en if side=='en' else local,'html.parser');s.select_one(b['selector'])[b['attribute']]='unreviewed value'
                        self.assert_rejected(str(s) if side=='en' else en,str(s) if side=='locale' else local,lang)
    def test_structure_and_other_data_still_fail_each_side_each_locale(self):
        mutations=(lambda s:s.select_one('#shelf-q').__setitem__('type','password'),lambda s:s.select_one('#shelf-q').__setitem__('required',''),lambda s:s.main.__setitem__('data-unreviewed','x'),lambda s:s.select_one('[data-total]').__setitem__('data-total','999'),lambda s:s.select_one('main img').__setitem__('src','/wrong.webp'),lambda s:s.select('.promo-card')[-1].decompose(),lambda s:s.select_one('#shelf-q').__setitem__('tabindex','-1'))
        for lang in CODES:
            en,local=self.texts(lang)
            for i,mutate in enumerate(mutations):
                for side in ('en','locale'):
                    with self.subTest(lang=lang,mutation=i,side=side):
                        s=BeautifulSoup(en if side=='en' else local,'html.parser');mutate(s)
                        self.assert_rejected(str(s) if side=='en' else en,str(s) if side=='locale' else local,lang)
    def test_context_and_catalog_fail_closed_every_locale(self):
        for lang in CODES:
            en,local=self.texts(lang)
            for changed in ({'family':'unrelated-master'},{'lang':'en'},{'masterSha256':'0'*64}):
                with self.subTest(lang=lang,context=changed),self.assertRaises(ValueError):self.compare(en,local,lang,**changed)
            path=self.root/f'locales/{lang}/stories-master-copy.json';original=path.read_text();d=json.loads(original);d['unexpected.key']='unreviewed';path.write_text(json.dumps(d))
            with self.subTest(lang=lang,extra_key=True),self.assertRaises(ValueError):self.compare(en,local,lang)
            path.write_text(original)
            for target in (self.root/'templates/masters/stories.html',self.root/'locales/en/stories-master-bindings.json',self.root/'locales/en/stories-master-copy.json'):
                old=target.read_bytes();target.write_bytes(old+b' ')
                with self.subTest(lang=lang,changed_file=str(target)),self.assertRaises(ValueError):self.compare(en,local,lang)
                target.write_bytes(old)

    def test_raw_duplicate_attributes_every_binding_side_order_locale(self):
        from i18n.mirror_structure import INVARIANT
        bindings=json.loads((self.root/'locales/en/stories-master-bindings.json').read_text())['bindings']
        for lang in CODES:
            en,local=self.texts(lang)
            for side in ('en','locale'):
                original=en if side=='en' else local
                soup=BeautifulSoup(original,'html.parser')
                cases=[(soup.select_one(b['selector']),b['attribute']) for b in bindings if b.get('attribute') in normalizer.DATA_COPY]
                # Every other invariant, including attributes not present in the
                # fixture, must be rejected as raw duplicates too.
                cases += [(soup.main,attr) for attr in sorted(INVARIANT | {'href','src','data-src-mp4','data-unreviewed'})]
                for node,attr in cases:
                    clean=str(node)
                    tag=clean.split('>',1)[0]+'>'
                    if not node.has_attr(attr):
                        node[attr]='original';clean=str(node);tag=clean.split('>',1)[0]+'>'
                    for order in ('before','after'):
                        with self.subTest(lang=lang,side=side,attr=attr,order=order):
                            bad=(tag.replace('<'+node.name,'<'+node.name+' '+attr.upper()+'="ATTACK"',1) if order=='before' else tag[:-1]+' '+attr+'="ATTACK">')
                            mutated=str(soup).replace(tag,bad,1)
                            self.assertNotEqual(mutated,str(soup))
                            self.assert_rejected(mutated if side=='en' else en,mutated if side=='locale' else local,lang)

    def test_missing_context_keys_and_wrong_valid_language(self):
        for lang in CODES:
            en,local=self.texts(lang)
            with self.subTest(lang=lang,missing_context=True),self.assertRaises(ValueError):
                check_pair(en,local,'/stories','/stories',('stories-keyed-data-copy',))
            wrong='fr' if lang!='fr' else 'ar'
            with self.subTest(lang=lang,wrong_valid_language=wrong):
                try:self.assertTrue(self.compare(en,local,wrong))
                except (ValueError,KeyError,FileNotFoundError):pass
            path=self.root/f'locales/{lang}/stories-master-copy.json';original=path.read_text();catalog=json.loads(original)
            key=next(iter(catalog))
            for variant in ('missing','empty'):
                bad=dict(catalog)
                if variant=='missing':bad.pop(key)
                else:bad[key]=''
                path.write_text(json.dumps(bad))
                with self.subTest(lang=lang,key_case=variant):self.assert_rejected(en,local,lang)
                path.write_text(original)

    def test_binding_node_and_protected_destination_hostile_controls(self):
        import copy
        def duplicate(s):s.select_one('.promo-card').insert_after(copy.copy(s.select_one('.promo-card')))
        def move(s):s.header.append(s.select_one('.promo-card').extract())
        def swap(s):
            a,b=s.select('.promo-card')[:2];holder=BeautifulSoup('<i></i>','html.parser').i;a.replace_with(holder);b.replace_with(a);holder.replace_with(b)
        def wrongtag(s):s.select_one('.promo-card').name='div'
        def extra(s):s.main['data-keywords']='unexpected'
        def href(s):s.select_one('main a[href]')['href']='/ATTACK'
        def script(s):s.select_one('script[src]')['src']='/ATTACK.js'
        def inline_script(s):
            node=s.new_tag('script');node.string='ATTACK()';s.body.append(node)
        mutations=(duplicate,move,swap,wrongtag,extra,href,script,inline_script,
                   lambda s:s.select_one('.promo-card').__setitem__('class',['ATTACK']),
                   lambda s:s.select_one('.promo-card').__setitem__('id','ATTACK'),
                   lambda s:s.main.__setitem__('data-src-mp4','/ATTACK.mp4'))
        for lang in CODES:
            en,local=self.texts(lang)
            for mutate in mutations:
                for side in ('en','locale'):
                    with self.subTest(lang=lang,side=side,mutation=mutate.__name__):
                        soup=BeautifulSoup(en if side=='en' else local,'html.parser');mutate(soup)
                        self.assert_rejected(str(soup) if side=='en' else en,str(soup) if side=='locale' else local,lang)

    def test_hostile_contract_binding_variants_fail_pinned_trust(self):
        path=self.root/'locales/en/stories-master-bindings.json';original=path.read_text()
        contract=json.loads(original)
        def duplicate(c):c['bindings'].append(dict(c['bindings'][0]))
        def moved(c):c['bindings'][0]['selector']='footer'
        def swapped(c):c['bindings'][0]['key'],c['bindings'][1]['key']=c['bindings'][1]['key'],c['bindings'][0]['key']
        def missing(c):c['bindings'][0].pop('key')
        def empty(c):c['bindings'][0]['key']=''
        for lang in CODES:
            en,local=self.texts(lang)
            for mutate in (duplicate,moved,swapped,missing,empty):
                import copy
                bad=copy.deepcopy(contract);mutate(bad);path.write_text(json.dumps(bad))
                with self.subTest(lang=lang,binding=mutate.__name__):self.assert_rejected(en,local,lang)
                path.write_text(original)

if __name__=='__main__':unittest.main()
