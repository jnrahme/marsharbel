#!/usr/bin/env python3
"""Reject new hardcoded text outside catalogs; grandfather existing legacy wording."""
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from i18n.catalog import read_json, page_url


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ignored = 0
        self.values = []

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.ignored += 1
        for name, value in attrs:
            if name in ('alt', 'title', 'aria-label', 'placeholder') and value:
                self.values.append(value)
            if tag == 'meta' and name == 'content':
                attributes = dict(attrs)
                if attributes.get('name') == 'description' or attributes.get('property') in ('og:title', 'og:description'):
                    self.values.append(value)

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.ignored = max(0, self.ignored - 1)

    def handle_data(self, data):
        if not self.ignored and data.strip():
            self.values.append(' '.join(data.split()))


def extract_html(text):
    # These generated blocks are separately verified by the reproducible build.
    text = re.sub(r'<!-- i18n-[\w-]+:start -->.*?<!-- i18n-[\w-]+:end -->', '', text, flags=re.S)
    parser = VisibleText()
    parser.feed(text)
    return Counter(parser.values)


def snapshot(root=ROOT):
    registry = read_json(root / 'locales/registry.json')
    generated = {f'{code}.html' for code in registry['locales'] if code != registry['defaultLocale']}
    generated.update(page_url(registry, code, topic).lstrip('/') + '.html'
                     for code in registry['locales'] for topic in registry['topics'])
    result = {}
    for path in sorted([*root.glob('*.html'), *root.glob('mysteries/*.html')]):
        relative = path.relative_to(root).as_posix()
        if relative not in generated:
            result[relative] = dict(extract_html(path.read_text()))
    for path in sorted(root.glob('*.js')):
        if path.name == 'locale-routes.js':
            continue
        values = json.loads(subprocess.check_output(['node', str(root/'scripts/i18n/extract-js-text.mjs'), str(path)],text=True))
        result[path.name] = dict(Counter(values))
    return result


def check(root=ROOT):
    baseline = read_json(root/'locales/legacy-text-baseline.json')
    errors = []
    for file, values in snapshot(root).items():
        additions = Counter(values) - Counter(baseline.get(file, {}))
        if additions:
            errors.append(f'{file}: new hardcoded wording; move it to locales/: {list(additions)[:3]}')
    for path in (root/'templates/international').glob('*.html'):
        for value in extract_html(path.read_text()):
            if re.sub(r'\$[A-Za-z][A-Za-z0-9_]*', '', value).strip():
                errors.append(f'{path.name}: literal display text belongs in common.json: {value}')
    return errors


if __name__ == '__main__':
    errors = check()
    if errors:
        raise SystemExit('\n'.join(errors))
    print('Localization policy passed: no new legacy wording or template literals.')
