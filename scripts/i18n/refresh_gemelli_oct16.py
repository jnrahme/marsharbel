"""Bind the reviewed October 16 Gemelli copy without adding locale routes."""
import argparse
import hashlib
import json
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
NEWS_KEYS = {
    'popeGemelli.title': 'news.latest-news.pope-leo-has-a-good-second-night-at-gemelli',
    'popeGemelli.summary': 'news.latest-news.the-holy-see-press-office-says-pope-leo-xiv-had-a-good-secon',
    'popeGemelli.admissionSource': 'news.latest-news.vatican-news-second-night-recovery-update-october-15-2026',
    'popeGemelli.date': 'news.latest-news.october-15-2026',
}
HOME_KEYS = {
    'popeGemelli.homeTitle': 'home.latest-news.pope-leo-has-a-good-second-night-at-gemelli',
    'popeGemelli.homeCredit': 'home.latest-news.the-holy-see-says-pope-leo-had-a-good-second-hospital-night',
    'popeGemelli.date': 'home.latest-news.october-15-2026',
}


def read_json(path):
    return json.loads(path.read_text())


def outputs(root=ROOT):
    translations = read_json(root / 'locales/gemelli-oct16-translations.json')
    english = read_json(root / 'locales/en/news-desk.json')
    registry = read_json(root / 'locales/registry.json')
    if len(translations) != 11 or any(len(values) != 6 for values in translations.values()):
        raise ValueError('Expected the reviewed 11-locale, six-value packet')
    result = {}
    families = [
        ('news-master', 'news.html', NEWS_KEYS, registry['pageMirrors']['news-master']['renderLocales']),
        ('home', 'index.html', HOME_KEYS, registry['homepageMirrors']['renderLocales']),
    ]
    for name, master, mapping, languages in families:
        raw = (root / master).read_bytes()
        soup = BeautifulSoup(raw, 'html.parser')
        binding_path = root / f'locales/en/{name}-bindings.json'
        copy_path = root / f'locales/en/{name}-copy.json'
        contract = read_json(binding_path)
        copy = read_json(copy_path)
        updates = {key: english[field] for field, key in mapping.items()}
        seen = set()
        for binding in contract['bindings']:
            key = binding['key']
            if key not in updates:
                continue
            nodes = soup.select(binding['selector'])
            if len(nodes) != 1:
                raise ValueError(f'{name}: ambiguous binding {key}')
            node = nodes[0]
            if binding['kind'] == 'attribute':
                value = node.get(binding['attribute'])
            else:
                value = ' '.join(str(node.contents[binding['nodeIndex']]).split())
            if value != updates[key]:
                raise ValueError(f'{name}: source mismatch {key}; build news first')
            binding['source'] = value
            seen.add(key)
        if seen != set(updates):
            raise ValueError(f'{name}: missing bindings {set(updates) - seen}')
        copy.update(updates)
        contract.update(messages=copy, masterSha256=hashlib.sha256(raw).hexdigest())
        result[copy_path] = copy
        result[binding_path] = contract
        for language in languages:
            path = root / f'locales/{language}/{name}-copy.json'
            local = read_json(path)
            local.update({key: translations[language][field] for field, key in mapping.items()})
            if set(local) != set(copy):
                raise ValueError(f'{name}: {language} key-set mismatch')
            result[path] = local
    return {path: json.dumps(value, ensure_ascii=False, indent=2) + '\n'
            for path, value in result.items()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path, text in outputs().items():
        if args.check:
            if path.read_text() != text:
                raise SystemExit(f'Gemelli bindings stale: {path}')
        else:
            path.write_text(text)
    print('Gemelli October 16 bindings ' + ('checked' if args.check else 'refreshed'))
