#!/usr/bin/env python3
"""Build the English error page from keyed copy; no runtime JS required."""
import argparse
import html
import json
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[2]


def render(root=ROOT):
    copy = json.loads((root / 'locales/en/error-404.json').read_text())
    assert set(copy) == {'title', 'brand', 'heading', 'explanation', 'homeLink'}
    return Template((root / 'templates/errors/404.html').read_text()).substitute(
        {key: html.escape(value, quote=True) for key, value in copy.items()})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    rendered = render()
    output = ROOT / '404.html'
    if args.check:
        if not output.exists() or output.read_text() != rendered:
            raise SystemExit('404.html differs from keyed English error catalog/template')
        print('404 catalog freshness passed')
    else:
        output.write_text(rendered)
