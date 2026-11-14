"""Synthetic refusal tests; never writes or repins catalogs."""
import importlib.util
import copy
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('history_repin', ROOT / 'scripts/i18n/repin_history_nav_placeholders.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


class HistoryNavRepinTests(unittest.TestCase):
    def binding_fixture(self):
        raw = b'<html><header><nav><div class="nav-group"><a class="nav-parent" href="./music">Media<span></span></a><div class="nav-sub"><a href="./music">Music</a><a href="./videos">Video</a><a href="./gallery">Gallery</a></div></div></nav></header><main>Body<h2 id="visit">Visiting</h2><div id="status" aria-label="Status"></div><div id="facts" aria-label="Facts"></div><div id="cause" aria-label="Cause"></div></main></html>'
        old = dict(master='history.html', masterSha256=m.sha(raw), messages={'existing': 'old'}, bindings=[], sourceRevision='frozen')
        legacy_nodes = {'history.visit.heading': ('#visit', 'Visiting', 'text'),
                        'history.table.status.scroll-label': ('#status', 'Status', 'attribute'),
                        'history.table.facts.scroll-label': ('#facts', 'Facts', 'attribute'),
                        'history.table.cause.scroll-label': ('#cause', 'Cause', 'attribute')}
        for key, (selector, source, kind) in legacy_nodes.items():
            b = dict(key=key, selector=selector, source=source, kind=kind)
            b.update({'attribute': 'aria-label'} if kind == 'attribute' else {'nodeIndex': 0})
            old['bindings'].append(b)
        new = copy.deepcopy(old); new['messages'].update(m.ADDED)
        new['messages'].update({k: v[1] for k, v in legacy_nodes.items()})
        selectors = ['header nav a.nav-parent', 'header nav .nav-sub a:nth-of-type(1)', 'header nav .nav-sub a:nth-of-type(2)', 'header nav .nav-sub a:nth-of-type(3)']
        new['bindings'] += [dict(key=k, selector=s, source=v, kind='text', nodeIndex=0) for (k, v), s in zip(m.ADDED.items(), selectors)]
        return raw, old, new

    def test_binding_positive(self):
        raw, old, new = self.binding_fixture()
        m.validate_bindings(old, new, raw, raw)

    def test_binding_refusals(self):
        raw, old, good = self.binding_fixture()
        mutations = []
        for field, value in [('masterSha256', '0'*64), ('sourceRevision', 'invented')]:
            bad = copy.deepcopy(good); bad[field] = value; mutations.append(bad)
        bad = copy.deepcopy(good); bad['bindings'][-4]['selector'] = 'main'; mutations.append(bad)
        bad = copy.deepcopy(good); bad['messages']['history.visit.heading'] = 'Different'; mutations.append(bad)
        bad = copy.deepcopy(good); bad['messages'].pop('history.visit.heading'); mutations.append(bad)
        bad = copy.deepcopy(good); bad['bindings'].append(dict(key='unrelated', selector='main')); mutations.append(bad)
        for bad in mutations:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                m.validate_bindings(old, bad, raw, raw)
        for changed in [raw.replace(b'Body', b'Other'), raw.replace(b'</main>', b'</main><!-- added -->'), raw.replace(b'./videos', b'./other')]:
            target = copy.deepcopy(good); target['masterSha256'] = m.sha(changed)
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                m.validate_bindings(old, target, raw, changed)

    def test_shipped_locale_scope(self):
        self.assertEqual(m.CODES, {'en', 'ar', 'fr', 'es', 'pt', 'it', 'de', 'pl', 'ru', 'hi', 'th'})

    def test_exact_placeholder_class(self):
        m.placeholders({'existing': 'old'}, {'existing': 'old', **m.ADDED})

    def test_catalog_refusals(self):
        good = {'existing': 'old', **m.ADDED}
        bad_cases = [dict(good, existing='changed'), dict(good, extra='extra'),
                     {k: v for k, v in good.items() if k != 'existing'},
                     dict(good, **{'history.header.media': 'translated'}),
                     {k: v for k, v in good.items() if k != 'history.header.music'}]
        for bad in bad_cases:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                m.placeholders({'existing': 'old'}, bad)

    def test_body_and_non_header_detection(self):
        before = b'<html><head><title>Same</title></head><header><nav>Old</nav></header><main>Body</main></html>'
        nav = before.replace(b'Old', b'New')
        self.assertEqual(m.body(before), m.body(nav))
        self.assertEqual(m.outside_header(before), m.outside_header(nav))
        self.assertNotEqual(m.body(before), m.body(before.replace(b'Body', b'Other')))
        self.assertNotEqual(m.outside_header(before), m.outside_header(before.replace(b'Same', b'Other')))

    def test_pin_preserves_other_bytes_and_is_idempotent(self):
        text = '{ "masterSha256" : "' + 'a'*64 + '", "review":"unchanged" }\n'
        updated = m.pin_text(text, 'masterSha256', 'a'*64, 'b'*64)
        self.assertEqual(updated, text.replace('a'*64, 'b'*64))
        self.assertEqual(updated, m.pin_text(updated, 'masterSha256', 'b'*64, 'b'*64))

    def test_path_scoped_pin_preserves_frozen_provenance(self):
        text = '{"variants":{"ru":{"catalogSha256":"' + 'a'*64 + '"}},"ruPrayerRoutingUnion":{"acceptedStagePins":{"catalogSha256":"' + 'a'*64 + '"},"priorPrayerBranchPins":{"catalogSha256":"' + 'a'*64 + '"}}}'
        updated = m.pin_text(text, ('variants', 'ru', 'catalogSha256'), 'a'*64, 'b'*64)
        self.assertEqual(updated, text.replace('a'*64, 'b'*64, 1))
        self.assertEqual(updated.count('a'*64), 2)
        self.assertEqual(updated, m.pin_text(updated, ('variants', 'ru', 'catalogSha256'), 'b'*64, 'b'*64))
        with self.assertRaises(ValueError):
            m.pin_text(text, ('variants', 'de', 'catalogSha256'), 'a'*64, 'b'*64)
        duplicate = '{"masterSha256":"' + 'a'*64 + '","masterSha256":"' + 'a'*64 + '"}'
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            m.pin_text(duplicate, 'masterSha256', 'a'*64, 'b'*64)

    def test_ambiguous_and_unknown_pin_refused(self):
        text = json.dumps({'masterSha256': 'a'*64})
        for candidate, old in [(text+text, 'a'*64), (text, 'b'*64)]:
            with self.assertRaises(ValueError):
                m.pin_text(candidate, 'masterSha256', old, 'c'*64)


if __name__ == '__main__':
    unittest.main()
