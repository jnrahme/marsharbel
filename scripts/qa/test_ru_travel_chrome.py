"""Synthetic exact-byte scope coverage for the RU generator href amendment."""
import importlib.util
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('ru_travel_chrome',ROOT/'scripts/i18n/ru_travel_chrome.py')
m = importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class RuTravelChromeTests(unittest.TestCase):
    def registry(self, route='/ru/travel'):
        return {'pageMirrors':{'travel':{'english':'/travel','routes':{'ru':route},'renderLocales':['ru']}}}

    def raw(self):
        return '<head><script>{"item":"https://site/travel"}</script></head><header><a href="/travel">Путешествия</a><a href="/bekaa-kafra">Бекаа</a><a href="/travel?x=1">Query</a></header><main><nav class="travel-breadcrumb"><a href="/travel">Путешествия</a></nav><p><a href="/travel">Body</a></p></main>'

    def test_every_existing_family_only_two_exact_chrome_hrefs(self):
        raw=self.raw();expected=raw.replace('href="/travel">Путешествия','href="/ru/travel">Путешествия')
        for family in m.FAMILIES:
            with self.subTest(family=family):
                self.assertEqual(m.localize_travel_chrome(raw,self.registry(),'ru',family),expected)
                self.assertEqual(m.localize_travel_chrome(expected,self.registry(),'ru',family),expected)

    def test_other_locales_families_and_missing_hub_byte_identical(self):
        raw=self.raw()
        for code,family,registry in [('de','home',self.registry()),('ru','travel-travel-master',self.registry()),
                                      ('ru','home',{}),('ru','home',{'pageMirrors':{'travel':{'english':'/travel','routes':{'ru':'/ru/travel'},'renderLocales':[]}}})]:
            self.assertEqual(m.localize_travel_chrome(raw,registry,code,family),raw)

    def test_data_href_not_an_anchor_target(self):
        raw='<header><a data-href="/travel" href="/other">Same</a></header>'
        self.assertEqual(m.localize_travel_chrome(raw,self.registry(),'ru','home'),raw)

    def test_registry_route_not_hardcoded(self):
        out=m.localize_travel_chrome(self.raw(),self.registry('/ru/journey'),'ru','home')
        self.assertEqual(out.count('href="/ru/journey"'),2)
        self.assertNotIn('/ru/travel',out)

    def test_ambiguous_or_unsafe_hub_refused(self):
        reg=self.registry();reg['pageMirrors']['other']={'english':'/travel','routes':{'ru':'/ru/other'},'renderLocales':['ru']}
        with self.assertRaises(ValueError):m.localize_travel_chrome(self.raw(),reg,'ru','home')
        with self.assertRaises(ValueError):m.localize_travel_chrome(self.raw(),self.registry('https://outside'),'ru','home')


if __name__ == '__main__':unittest.main()
