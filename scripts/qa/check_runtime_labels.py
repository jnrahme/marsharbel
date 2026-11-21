"""Runtime-label completeness gate for locale pages in the composition pipeline.

Regression coverage for the 2026-10-08 install-dict incident: 109 generated
locale pages shipped without the sc-runtime-labels dictionary (English Install
App button / footer labels), and 13 of them additionally shipped without the
translate.js tag at all (no install control):
  ar/miracles/index.html, ar/miracles/nohad-el-shami.html,
  ar/miracles/raymond-nader.html, ar/miracles/dafne-gutierrez.html,
  ar/rosary.html, fr/chapelet.html, es/fiesta.html, es/rosario.html,
  pt/festa.html, pt/rosario.html, it/rosario.html, de/rosenkranz.html,
  pl/rozaniec.html
Every pipeline page (contains same-page-switcher.js or sc-runtime-labels) in a
non-default locale must embed exactly one dictionary and load translate.js
exactly once, and re-applying ensure_runtime_labels to served bytes must be a
no-op (composition is idempotent).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from i18n.catalog import read_json
from i18n.runtime_labels import ensure_runtime_labels

FORMERLY_MISSING = [
    'ar/miracles/index.html', 'ar/miracles/nohad-el-shami.html',
    'ar/miracles/raymond-nader.html', 'ar/miracles/dafne-gutierrez.html',
    'ar/rosary.html', 'fr/chapelet.html', 'es/fiesta.html', 'es/rosario.html',
    'pt/festa.html', 'pt/rosario.html', 'it/rosario.html',
    'de/rosenkranz.html', 'pl/rozaniec.html',
]


def main():
    registry = read_json(ROOT / 'locales/registry.json')
    locales = [c for c in registry['locales'] if c != registry['defaultLocale']]
    failures = []
    checked = 0
    for code in locales:
        for path in sorted((ROOT / code).rglob('*.html')):
            text = path.read_text()
            if 'same-page-switcher.js' not in text and 'sc-runtime-labels' not in text:
                continue
            checked += 1
            rel = path.relative_to(ROOT)
            labels = text.count('id="sc-runtime-labels"')
            translate = text.count('/translate.js?')
            if labels != 1:
                failures.append(f'{rel}: sc-runtime-labels count {labels}')
            if translate != 1:
                failures.append(f'{rel}: translate.js count {translate}')
            lang = re.search(r'<html[^>]*lang=["\']([^"\']+)', text)
            if not lang or lang.group(1) != code:
                failures.append(f'{rel}: html lang mismatch')
                continue
            if ensure_runtime_labels(text, ROOT, code, registry) != text:
                failures.append(f'{rel}: ensure_runtime_labels is not idempotent on served bytes')
    # The install control is created by same-page-switcher.js; its pill styling
    # (44px design-bar touch target, EN-scoped-out, any-length containment)
    # must live in same-page-switcher.css, the one stylesheet every control
    # page loads last. Assert on the rule block itself, not loose substrings.
    switcher_css = (ROOT / 'same-page-switcher.css').read_text()
    block = re.search(r'html:not\(\[lang="en"\]\) \.sc-install-app-btn\{([^}]*)\}', switcher_css)
    if not block:
        failures.append('same-page-switcher.css: locale-scoped .sc-install-app-btn pill rule missing')
    else:
        for needle in ('min-height:44px', 'max-width:100%', 'min-width:0'):
            if needle not in block.group(1):
                failures.append(f'same-page-switcher.css: install pill rule missing {needle}')
    label = re.search(r'\.sc-install-app-btn-label\{([^}]*)\}', switcher_css)
    if not label:
        failures.append('same-page-switcher.css: .sc-install-app-btn-label ellipsis rule missing')
    else:
        for needle in ('min-width:0', 'overflow:hidden', 'text-overflow:ellipsis', 'white-space:nowrap'):
            if needle not in label.group(1):
                failures.append(f'same-page-switcher.css: label ellipsis rule missing {needle}')
    # Compact trim takes back nav padding and row gap only. Link/nav-parent
    # min-height must stay at the site-standard 24px: 22px fails the WCAG 2.2
    # target-size floor (axe, #656 shard 2).
    if 'padding-block:.2rem' not in switcher_css:
        failures.append('same-page-switcher.css: locale compact-header trim missing')
    if 'min-height:22px' in switcher_css:
        failures.append('same-page-switcher.css: compact link min-height below the 24px target-size floor')
    switcher_js = (ROOT / 'same-page-switcher.js').read_text()
    if "installLabel.className='sc-install-app-btn-label'" not in switcher_js:
        failures.append('same-page-switcher.js: install button does not wrap its label in .sc-install-app-btn-label (ellipsis cannot render without it)')
    for rel in FORMERLY_MISSING:
        text = (ROOT / rel).read_text()
        if text.count('/translate.js?') != 1:
            failures.append(f'{rel}: formerly missing page does not load translate.js exactly once')
    if failures:
        print('runtime-label gate failures:', file=sys.stderr)
        for f in failures:
            print(f'  {f}', file=sys.stderr)
        return 1
    print(f'runtime labels: {checked} pipeline pages complete and idempotent across {len(locales)} locales; 13 formerly missing pages pinned')
    return 0


if __name__ == '__main__':
    sys.exit(main())
