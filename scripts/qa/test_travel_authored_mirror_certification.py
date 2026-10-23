"""Travel authored-mirror certification stays closed until final QA and rejects drift."""
import json, shutil, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / 'scripts'))
from i18n.reviewed_travel_authored_mirror import travel_authored_mirror_manifest, LOCALES, RECORD

FAMILY = 'travel-travel-master-equivalence'

def _record():
    return json.loads((ROOT / RECORD).read_text())

def _seed_family():
    return {'sourcePath': 'travel.html', 'sourceRevision': '19845304893719bcdee5864fb31fd3c3e043e386',
            'sourceSha256': '0' * 64, 'anchorIDs': {},
            'variants': {'en': {'path': '/travel', 'aliases': [], 'status': 'verified'}}}

def _scratch(record):
    temp = tempfile.TemporaryDirectory(); root = Path(temp.name)
    files = {v['file'] for v in record['groups']['travel-authored-mirror']['variants'].values()}
    files |= {v['catalog'] for v in record['groups']['travel-authored-mirror']['variants'].values()}
    for file in files:
        dst = root / file; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(ROOT / file, dst)
    (root / RECORD).parent.mkdir(parents=True, exist_ok=True)
    (root / RECORD).write_text(json.dumps(record))
    return temp, root

class TravelAuthoredMirrorCertification(unittest.TestCase):
    def test_pending_gate_is_noop(self):
        record = _record(); record['gateStatus'] = 'pending-final-qa'
        marker = {'pages': {'keep': {}}}
        temp, root = _scratch(record)
        with temp:
            self.assertIs(travel_authored_mirror_manifest(root, {}, marker), marker)

    def test_merge_supersede_and_drift(self):
        record = _record(); record['gateStatus'] = 'approved'
        temp, root = _scratch(record)
        with temp:
            seed = {'pages': {FAMILY: _seed_family()}}
            for code in LOCALES:
                seed['pages']['page-stale-' + code] = {'anchorIDs': {}, 'sourceSha256': 'old',
                    'variants': {code: {'path': record['groups']['travel-authored-mirror']['variants'][code]['path'], 'status': 'pending'}}}
            m = travel_authored_mirror_manifest(root, {}, seed)
            self.assertFalse([k for k in m['pages'] if k.startswith('page-stale-')])
            variants = m['pages'][FAMILY]['variants']
            self.assertEqual(set(variants), {'en', *LOCALES})
            for code in LOCALES:
                self.assertEqual(variants[code]['status'], 'verified')
                self.assertEqual(variants[code]['proof']['nativeReviewStatus'], 'not-certified')
                self.assertIn('owner waiver 2026-10-22 16:23 EDT', variants[code]['proof']['scope'])
            # Body drift is refused.
            bad = _record(); bad['gateStatus'] = 'approved'
            code0 = LOCALES[0]
            bad['groups']['travel-authored-mirror']['variants'][code0]['bodySha256'] = 'f' * 64
            temp2, root2 = _scratch(bad)
            with temp2:
                with self.assertRaisesRegex(ValueError, 'body drift'):
                    travel_authored_mirror_manifest(root2, {}, {'pages': {FAMILY: _seed_family()}})
            # A multi-variant row on a target route is never superseded.
            guard = {'pages': {FAMILY: _seed_family(),
                     'page-multi': {'anchorIDs': {}, 'sourceSha256': 'old',
                        'variants': {'es': {'path': '/es/travel', 'status': 'pending'},
                                     'fr': {'path': '/x', 'status': 'pending'}}}}}
            with self.assertRaisesRegex(ValueError, 'would replace'):
                travel_authored_mirror_manifest(root, {}, guard)

    def test_rendered_structural_parity(self):
        """Scripted parity audit backing the evidence: main/footer/assets identical
        to the EN master; the only header delta is launch-availability nav shaping
        (enc-nav-item marking plus omitted items for pages the locale lacks)."""
        import sys
        from bs4 import BeautifulSoup
        sys.path.insert(0, str(ROOT / 'scripts'))
        from i18n.mirror_structure import signature, tree
        record = _record()
        master_text = (ROOT / 'travel.html').read_text()
        master = signature(master_text, '/travel')
        for code in LOCALES:
            variant = record['groups']['travel-authored-mirror']['variants'][code]
            text = (ROOT / variant['file']).read_text()
            twin = signature(text, variant['path'])
            for key in ('main', 'footer', 'styles', 'scripts', 'images', 'video'):
                self.assertEqual(master[key], twin[key], code + ' ' + key)
            # Header: unwrap the reviewed English-destination marking, strip
            # qualifier spans; remaining tree may only DROP nav anchors whose
            # targets have no locale page.
            def headsrc(raw):
                soup = BeautifulSoup(raw, 'html.parser')
                for div in soup.select('div.enc-nav-item'):
                    div.unwrap()
                for span in soup.select('span.enc-language'):
                    span.decompose()
                return soup
            en_soup = headsrc(master_text)
            twin_soup = headsrc(text)
            from collections import Counter
            def norm(href):
                return '/' + href.lstrip('./') if href else href
            en_links = Counter(norm(a.get('href')) for a in en_soup.header.select('nav.links a'))
            twin_links = Counter(norm(a.get('href')) for a in twin_soup.header.select('nav.links a'))
            missing = en_links - twin_links
            extra = twin_links - en_links
            for href, _ in extra.items():
                # locale-prefixed twins of EN routes are fine
                self.assertTrue(href.startswith('/' + code + '/'), code + ' unexpected header link ' + href)
            for href, _ in missing.items():
                target = href.lstrip('.').lstrip('/')
                if not (ROOT / code / (target + '.html')).is_file():
                    continue  # launch-availability omission: locale page does not exist
                locale_route = '/' + code + '/' + target
                self.assertIn(locale_route, twin_links,
                              code + ' omits nav link to existing locale page: ' + href)
            self.assertEqual(tree(en_soup.header)[0], tree(twin_soup.header)[0], code + ' header tag')

if __name__ == '__main__':
    unittest.main()
