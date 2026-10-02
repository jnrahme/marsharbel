import json
from html.parser import HTMLParser
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from i18n.catalog import read_json
from i18n.tour_nav import tour_nav
from i18n.same_page_injection import inject_control
from i18n.metadata import published_locales
from i18n.eucharistic_mirror import render_eucharistic,SLUGS

ROOT=Path(__file__).resolve().parents[2]

class Shape(HTMLParser):
    def __init__(self,body):
        super().__init__();self.tags=[];self.images=[];self.headings=[];self.scripts=[];self.in_script=False;self.script='';self.feed(body)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ('section','figure','button','h1','h2','h3'):self.tags.append(tag)
        if tag=='img':self.images.append(a.get('src'))
        if tag=='script' and a.get('type')=='application/ld+json':self.in_script=True
    def handle_endtag(self,tag):
        if tag=='script' and self.in_script:self.scripts.append(json.loads(self.script));self.in_script=False;self.script=''
    def handle_data(self,data):
        if self.in_script:self.script+=data

class EucharisticLocaleTests(unittest.TestCase):
    def test_catalog_shape_and_exact_rendering(self):
        outputs=render_eucharistic(ROOT)
        languages = [code for code in published_locales(read_json(ROOT/'locales/registry.json'), 'eucharistic') if code != 'en']
        self.assertEqual(len(outputs), len(languages) * (len(SLUGS) + 1))
        english=read_json(ROOT/'locales/en/eucharistic-miracles.json')
        for lang in [code for code in published_locales(read_json(ROOT/'locales/registry.json'), 'eucharistic') if code != 'en']:
            catalog=read_json(ROOT/f'locales/{lang}/eucharistic-miracles.json')
            self.assertEqual(set(catalog['hub']),set(english['hub']))
            for slug in ('index',*SLUGS):
                route=ROOT/lang/'miracles/eucharistic'/f'{slug}.html'
                translated=outputs[route]
                self.assertEqual(route.read_text(),inject_control(tour_nav(translated,ROOT,lang),ROOT,read_json(ROOT/"locales/same-page-manifest.pending.json"),read_json(ROOT/"locales/same-page-copy.json")),route)
                source=(ROOT/'miracles/eucharistic'/f'{slug}.html').read_text()
                a,b=Shape(source),Shape(translated)
                self.assertEqual(a.tags,b.tags,(lang,slug))
                self.assertEqual([x.replace('../../','/') for x in a.images],b.images,(lang,slug))
                self.assertEqual(len(a.scripts),len(b.scripts))
                for x,y in zip(a.scripts,b.scripts):
                    self.assertEqual(x['@type'],y['@type'])
                    self.assertEqual(x['image'],y['image'])
                    self.assertEqual(y['inLanguage'],lang)
                    self.assertEqual(y['url'],'https://marsharbel.com/'+lang+'/miracles/eucharistic/'+('' if slug=='index' else slug))
                self.assertEqual(translated.count('hreflang='),len(languages)+2)
                if slug!='index':
                    self.assertEqual(len(catalog['stories'][slug]['sections']),3)
                    for field in ('image','credit','licenseurl','photo','source','source2'):
                        if field in english['stories'][slug]:
                            self.assertEqual(catalog['stories'][slug][field],english['stories'][slug][field])
    def test_corrected_bolsena_photo_in_every_language(self):
        for lang in [code for code in published_locales(read_json(ROOT/'locales/registry.json'), 'eucharistic') if code != 'en']:
            c=read_json(ROOT/f'locales/{lang}/eucharistic-miracles.json')['stories']['bolsena-orvieto']
            self.assertEqual(c['credit'],'Abxbay')
            self.assertEqual(c['license'],'CC0 1.0')
            self.assertIn('Duomo_orvieto_-_reliquario_del_corporale',c['photo'])
            self.assertNotIn('Corporal_of_Bolsena.JPG',str(c))

if __name__=='__main__': unittest.main()
