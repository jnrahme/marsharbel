"""Synthetic seven-page chrome scope/refusal coverage; no repo mutation."""
import importlib.util
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('nav_repin', ROOT/'scripts/i18n/repin_ru_nav_alignment.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


class RuNavAlignmentRepinTests(unittest.TestCase):
    def before(self):
        return '<html><head><title>Same</title></head><body><header><nav><a class="nav-parent" href="/travel">Паломничество<span></span></a><a href="/bekaa-kafra">Бекаа-Кафра</a></nav></header><main><nav class="travel-breadcrumb"><a href="/travel">Паломничество</a></nav><p>Body</p></main></body></html>'.encode()

    def after(self):
        return self.before().decode().replace('/travel', '/ru/travel').replace('Паломничество', 'Путешествия').encode()

    def test_only_travel_header_and_breadcrumb(self):
        old, new = m.nav_delta(self.before(), self.after())
        self.assertNotEqual(old, new)
        self.assertEqual(m.nav_delta(self.after(), self.after()), (new, new))

    def test_body_head_submenu_and_wrong_label_refused(self):
        for before, after in [(b'Body', b'Other'), (b'Same', b'Other'),
                              (b'/bekaa-kafra', b'/ru/bekaa-kafra'),
                              ('Путешествия'.encode(), 'Другое'.encode())]:
            with self.subTest(before=before), self.assertRaises(ValueError):
                m.nav_delta(self.before(), self.after().replace(before, after))

    def test_non_chrome_travel_link_refused(self):
        old = self.before().replace(b'</main>', '<a href="/travel">Паломничество</a></main>'.encode())
        new = old.decode().replace('/travel', '/ru/travel').replace('Паломничество', 'Путешествия').encode()
        with self.assertRaises(ValueError):
            m.nav_delta(old, new)

    def test_catalog_values_and_only_named_keys(self):
        m.catalog_delta('{"annaya.header.travel":"Паломничество","other":"same"}', '{"annaya.header.travel":"Путешествия","other":"same"}')
        for target in ['{"annaya.header.travel":"Путешествия","other":"changed"}',
                       '{"annaya.header.travel":"Other","other":"same"}',
                       '{"annaya.header.travel":"Путешествия"}']:
            with self.assertRaises(ValueError):
                m.catalog_delta('{"annaya.header.travel":"Паломничество","other":"same"}', target)

    def schema(self):
        import json
        data = {'@type':'WebPage','breadcrumb':{'@type':'BreadcrumbList','itemListElement':[
            {'position':1,'name':'Главная','item':'https://marsharbel.com/ru/'},
            {'position':2,'name':'Паломничество','item':'https://marsharbel.com/travel'}]}}
        return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False)+'</script>'

    def schema_before_after(self):
        old=self.before().decode().replace('</head>',self.schema()+'</head>')
        new=old.replace('/travel">','/ru/travel">').replace('Паломничество','Путешествия')
        return old.encode(),new.encode()

    def test_bounded_schema_name_delta(self):
        old,new=self.schema_before_after()
        for file in m.SCHEMA_PAGES:m.nav_delta(old,new,file)

    def test_schema_url_position_page_and_wrong_name_refused(self):
        old,new=self.schema_before_after()
        for file,after in [('ru/annaya.html',new.replace(b'https://marsharbel.com/travel',b'https://marsharbel.com/ru/travel')),
                           ('ru/annaya.html',new.replace('Главная'.encode(),'Другая'.encode())),
                           ('ru/novena.html',new),
                           ('ru/annaya.html',new.replace('Путешествия'.encode(),'Иное'.encode()))]:
            with self.subTest(file=file),self.assertRaises(ValueError):m.nav_delta(old,after,file)

    def test_other_schema_bytes_refused(self):
        old,new=self.schema_before_after()
        with self.assertRaises(ValueError):m.nav_delta(old,new.replace(b'"position": 1',b'"position" : 1'),'ru/annaya.html')


if __name__ == '__main__':
    unittest.main()
