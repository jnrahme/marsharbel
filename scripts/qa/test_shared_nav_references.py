import hashlib,json,sys,tempfile,unittest,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.keyed_master import apply_keyed_master
class SharedNavReferences(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
        raw='<html><header><nav><a href="/music">Media</a></nav></header><main></main></html>'
        self.contract={'master':'master.html','masterSha256':hashlib.sha256(raw.encode()).hexdigest(),'bindings':[{'key':'header.media','kind':'text','selector':'header nav a','nodeIndex':0,'source':'Media'}]}
        self.write('master.html',raw);self.write('locales/en/demo-copy.json',{'header.media':'Media'});self.write('locales/ar/demo-copy.json',{'header.media':'family unchanged'})
        self.write('locales/en/common.json',{'navigation.media':'Media'});self.write('locales/ar/common.json',{'navigation.media':'وسائط'})
        self.save()
    def write(self,name,value):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value)if not isinstance(value,str)else value)
    def save(self):self.write('locales/en/demo-bindings.json',self.contract)
    def render(self):return apply_keyed_master(self.root,'demo','ar')[1].select_one('header a').get_text()
    def activate(self):
        self.contract['bindings'][0]['sharedMessage']='navigation.media';self.save()
        self.write('locales/en/demo-copy.json',{});self.write('locales/ar/demo-copy.json',{})
    def test_undeclared_family_unaffected_even_without_shared_catalog(self):
        (self.root/'locales/ar/common.json').unlink();self.assertEqual(self.render(),'family unchanged')
    def test_explicit_reference_uses_shared_message(self):self.activate();self.assertEqual(self.render(),'وسائط')
    def test_shared_bound_key_absent_from_family_catalog_builds(self):
        self.activate();self.assertEqual(self.render(),'وسائط')
    def test_duplicate_family_shared_key_rejected(self):
        self.activate()
        self.write('locales/en/demo-copy.json',{'header.media':'Media'})
        self.write('locales/ar/demo-copy.json',{'header.media':'family duplicate'})
        with self.assertRaisesRegex(ValueError,'duplicate family/shared message'):self.render()
    def test_missing_shared_key_fails(self):
        self.activate();self.write('locales/ar/common.json',{})
        with self.assertRaises(ValueError):self.render()
    def test_missing_english_source_fails(self):
        self.activate();self.write('locales/en/common.json',{})
        with self.assertRaises(ValueError):self.render()
    def test_wildcard_foreign_reference_and_source_drift_fail(self):
        for reference in ['*','navigation.other','navigation.media']:
            self.activate();self.contract['bindings'][0]['sharedMessage']=reference;self.save()
            if reference=='navigation.media':self.write('locales/en/common.json',{'navigation.media':'Source drift'})
            with self.subTest(reference=reference),self.assertRaises(ValueError):self.render()
    def test_empty_markup_or_placeholder_value_fails(self):
        self.activate()
        for value in ['', '<b>Media</b>', 'Media {count}']:
            self.write('locales/ar/common.json',{'navigation.media':value})
            with self.subTest(value=value),self.assertRaises(ValueError):self.render()
class SharedNavPageIntegration(unittest.TestCase):
    def test_real_page_renderer_without_family_shared_key(self):
        from i18n.page_mirror import render_page
        from bs4 import BeautifulSoup
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);shutil.copytree(ROOT/'locales',root/'locales')
            family='bekaa-kafra-travel-master'
            file=root/f'locales/en/{family}-bindings.json'
            contract=json.loads(file.read_text())
            shutil.copyfile(ROOT/contract['master'],root/contract['master'])
            binding=next(b for b in contract['bindings'] if b['source']=='Media')
            binding['sharedMessage']='navigation.media'
            key=binding['key'];contract['messages'].pop(key,None)
            file.write_text(json.dumps(contract))
            for lang in ('en','de'):
                file=root/f'locales/{lang}/{family}-copy.json'
                catalog=json.loads(file.read_text());catalog.pop(key)
                file.write_text(json.dumps(catalog))
            registry=json.loads((root/'locales/registry.json').read_text())
            route=registry['pageMirrors'][family]['routes']['de']
            result=render_page(root,registry,'de',family,route)
            soup=BeautifulSoup(result,'html.parser')
            expected=json.loads((root/'locales/de/common.json').read_text())['navigation.media']
            self.assertEqual(soup.select_one(binding['selector']).get_text(strip=True),expected)
            raw,keyed,_=apply_keyed_master(root,family,'de')
            self.assertEqual(keyed.select_one(binding['selector']).get_text(strip=True),expected)
            self.assertEqual(soup.select_one('link[rel=canonical]')['href'],registry['site']+route)
            for lang in ('en','de'):
                file=root/f'locales/{lang}/{family}-copy.json'
                catalog=json.loads(file.read_text());catalog[key]='Media'
                file.write_text(json.dumps(catalog))
            with self.assertRaisesRegex(ValueError,'duplicate family/shared message'):
                render_page(root,registry,'de',family,route)
            with self.assertRaisesRegex(ValueError,'duplicate family/shared message'):
                apply_keyed_master(root,family,'de')
if __name__=='__main__':unittest.main()
