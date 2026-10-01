#!/usr/bin/env python3
"""Render the daily news blocks from keyed English copy; --check fails on drift."""
import argparse
import html
import json
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[1]

def outputs(root=ROOT):
    copy = json.loads((root / 'locales/en/news-desk.json').read_text())
    result = {}
    for file, template, marker in [('news.html', 'cards.html', 'news-desk'), ('index.html', 'home.html', 'news-home')]:
        text = (root / file).read_text()
        content = (root / 'templates/news-desk' / template).read_text()
        content = re.sub(r'\$\{([^}]+)\}', lambda m: html.escape(copy[m[1]], quote=True), content)
        pattern = rf'(<!-- i18n-{marker}:start -->).*?(<!-- i18n-{marker}:end -->)'
        text, n = re.subn(pattern, lambda m: m[1] + '\n' + content + '\n' + m[2], text, flags=re.S)
        if n != 1:
            raise ValueError(f'{file}: expected exactly one {marker} block')
        text = re.sub(r'(<!-- news-copy:([^:]+):start -->).*?(<!-- news-copy:\2:end -->)',
                      lambda m: m[1] + html.escape(copy[m[2]], quote=True) + m[3], text, flags=re.S)
        result[root / file] = text
    return result

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    for path, content in outputs().items():
        if args.check:
            if path.read_text() != content:
                raise SystemExit(f'News desk output stale: {path.name}')
        else:
            path.write_text(content)
    print('News desk catalog output checked.' if args.check else 'News desk catalog output built.')

if __name__ == '__main__':
    main()
