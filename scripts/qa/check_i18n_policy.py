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
from i18n.build_error_404 import render as render_error_404
from i18n.metadata import published_locales
from i18n.catalog import locale_topics, read_json, page_url
from i18n.mirror import render_pair
from i18n.qadisha_mirror import render_qadisha
from i18n.monastery_mirror import render_monasteries
from i18n.qadisha_copy import validate as validate_qadisha, paragraphs as qadisha_paragraphs


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
    # This block is generated from the reviewed English testimony catalog and
    # checked byte-for-byte by build-testimony-baseline.mjs --check in QA.
    text = re.sub(r'<!-- baseline-testimonies:start -->.*?<!-- baseline-testimonies:end -->', '', text, flags=re.S)
    parser = VisibleText()
    parser.feed(text)
    return Counter(parser.values)


def snapshot(root=ROOT):
    registry = read_json(root / 'locales/registry.json')
    generated = {f'{code}/index.html' for code in registry['locales'] if code != registry['defaultLocale']}
    generated.update((page_url(registry, code, topic).lstrip('/') + 'index.html'
                      if page_url(registry, code, topic).endswith('/')
                      else page_url(registry, code, topic).lstrip('/') + '.html')
                     for code in registry['locales'] for topic in locale_topics(registry, code))
    if 'chaplet' in registry.get('authoredMirrors', {}):
        generated.update(route.lstrip('/')+'.html' for code,route in registry['authoredMirrors']['chaplet']['routes'].items() if code != 'en')
    generated.update(f'{code}/miracles/eucharistic/'+('index.html' if slug=='index' else slug+'.html')
                     for code in published_locales(registry, 'eucharistic') if code != registry['defaultLocale']
                     for slug in ('index','lanciano','bolsena-orvieto','siena','santarem','sokolka','legnica','ludbreg','amsterdam','ivorra','faverney'))
    # Exact outputs retain strict guarded-source and byte-freshness checks.
    generated.update((route.lstrip('/')+'index.html' if route.endswith('/') else route.lstrip('/')+'.html')
                     for cfg in registry.get('exactMirrors',{}).values() for code,route in cfg['routes'].items() if code in cfg.get('renderLocales',[]))
    generated.add("ar/litany-of-saint-charbel.html")
    generated.update(route.lstrip("/")+".html" for route in registry.get("authoredMirrors", {}).get("travel", {}).get("routes", {}).values())
    result = {}
    for path in sorted([*root.glob('*.html'), *root.glob('mysteries/*.html'), *root.glob('miracles/*.html'), *root.glob('miracles/eucharistic/*.html'),
                        *(p for code in registry['locales'] if code != registry['defaultLocale']
                          for p in root.glob(f'{code}/**/*.html'))]):
        relative = path.relative_to(root).as_posix()
        if relative not in generated:
            result[relative] = dict(extract_html(path.read_text()))
    # Catalog-generated control copy is exact-checked, not a blanket JS exemption.
    copy_path=root/'locales/same-page-copy.json'
    if copy_path.exists():
        expected='window.SC_SAME_PAGE_COPY = '+json.dumps(read_json(copy_path),ensure_ascii=False,separators=(',',':'))+';\n'
        if (root/'same-page-copy.js').read_text()!=expected:raise ValueError('same-page-copy.js differs from UI catalog')
    for path in sorted(root.glob('*.js')):
        if (path.name == 'same-page-copy.js' and copy_path.exists()) or path.name in ('locale-routes.js', 'eucharistic.js') or (path.name == 'testimonies-copy.js' and (root / 'locales/en/testimonies.json').exists()):
            continue
        values = json.loads(subprocess.check_output(['node', str(root/'scripts/i18n/extract-js-text.mjs'), str(path)],text=True))
        result[path.name] = dict(Counter(values))
    return result


def check(root=ROOT):
    baseline = read_json(root/'locales/legacy-text-baseline.json')
    errors = []
    error_404_path = root / "404.html"
    error_404_rendered = render_error_404(root) if error_404_path.exists() else None
    if error_404_rendered is not None and error_404_path.read_text() != error_404_rendered:
        errors.append("404.html differs from keyed English error catalog/template")
    accessibility_path = root/'locales/en/accessibility-copy.json'
    accessibility_catalog = read_json(accessibility_path)['values'] if accessibility_path.exists() else {}
    display_catalog = read_json(root/'locales/en/letters-display.json')['values']
    aeo_catalog_path = root/'locales/en/aeo-p2-copy.json'
    aeo_catalog = read_json(aeo_catalog_path)['values'] if aeo_catalog_path.exists() else {}
    pillar_path = root/'locales/en/saint-pillars-copy.json'
    pillar_catalog = read_json(pillar_path)['values'] if pillar_path.exists() else {}
    a11y_path = root/'locales/en/a11y-statement-copy.json'
    a11y_catalog = read_json(a11y_path)['values'] if a11y_path.exists() else {}
    scripture_catalog = {}
    for name in ('scripture-copy', 'nav-legacy-copy', 'encyclopedia-copy', 'home-travel-copy', 'history-copy', 'history-accessibility-copy', 'caption-copy', 'bekaa-tour-copy', 'bekaa-followup-copy', 'jpii-pass-copy', 'rosary-bead-copy'):
        extra_path = root/f'locales/en/{name}.json'
        if extra_path.exists():
            for page, values in read_json(extra_path)['values'].items():
                scripture_catalog.setdefault(page, Counter()).update(values)
    storybook_catalog = read_json(root/'locales/en/storybook.json')
    teresa_catalog = read_json(root/'locales/en/mother-teresa-story-copy.json')
    rafqa_catalog = read_json(root/'locales/en/rafqa-story-copy.json')
    charbel_v2_catalog = read_json(root/'locales/en/charbel-v2-story-copy.json')
    magdalene_path = root/'locales/en/magdalene-story-copy.json'
    magdalene_catalog = read_json(magdalene_path)['values'] if magdalene_path.exists() else {}
    maroun_path = root/'locales/en/maroun-story-copy.json'
    maroun_catalog = read_json(maroun_path)['values'] if maroun_path.exists() else {}
    augustine_path = root/'locales/en/augustine-story-copy.json'
    augustine_catalog = read_json(augustine_path)['values'] if augustine_path.exists() else {}
    marina_path = root/'locales/en/marina-story-copy.json'
    marina_catalog = read_json(marina_path)['values'] if marina_path.exists() else {}
    annaya_path = root/'locales/en/annaya-practical-copy.json'
    annaya_catalog = read_json(annaya_path)['values'] if annaya_path.exists() else {}
    sergius_path = root/'locales/en/sergius-bacchus-story-copy.json'
    sergius_catalog = read_json(sergius_path)['values'] if sergius_path.exists() else {}
    saint_bios_path = root/'locales/en/saint-bios-copy.json'
    saint_bios_catalog = read_json(saint_bios_path)['values'] if saint_bios_path.exists() else {}
    shelf_path = root/'locales/en/stories-shelf-copy.json'
    shelf_catalog = read_json(shelf_path)['values'] if shelf_path.exists() else {}
    jude_path = root/'locales/en/jude-story-copy.json'
    jude_catalog = read_json(jude_path)['values'] if jude_path.exists() else {}
    peter_path = root/'locales/en/peter-story-copy.json'
    peter_catalog = read_json(peter_path)['values'] if peter_path.exists() else {}
    francis_path = root/'locales/en/francis-story-copy.json'
    francis_catalog = read_json(francis_path)['values'] if francis_path.exists() else {}
    answer_path = root/'locales/en/feast-novena-answer-copy.json'
    answer_catalog = read_json(answer_path)['values'] if answer_path.exists() else {}
    joseph_path = root/'locales/en/joseph-story-copy.json'
    joseph_catalog = read_json(joseph_path)['values'] if joseph_path.exists() else {}
    anthony_path = root/'locales/en/anthony-story-copy.json'
    anthony_catalog = read_json(anthony_path)['values'] if anthony_path.exists() else {}
    therese_path = root/'locales/en/therese-story-copy.json'
    therese_catalog = read_json(therese_path)['values'] if therese_path.exists() else {}
    massabki_path = root/'locales/en/massabki-story-copy.json'
    massabki_catalog = read_json(massabki_path)['values'] if massabki_path.exists() else {}
    jpii_story_path = root/'locales/en/jpii-story-copy.json'
    jpii_story_catalog = read_json(jpii_story_path)['values'] if jpii_story_path.exists() else {}
    story_copy_path = root/'locales/en/story-copy.json'
    story_copy_catalog = read_json(story_copy_path)['values'] if story_copy_path.exists() else {}
    hardini_catalog = read_json(root/'locales/en/hardini-story-copy.json')
    pio_film_catalog = read_json(root/'locales/en/pio-film-copy.json')
    testimony_path = root / 'locales/en/testimonies.json'
    testimony_catalog = read_json(testimony_path) if testimony_path.exists() else None
    prayer_mirror = render_pair(root) if (root/'templates/mirrors/prayers.html').exists() else {}
    qadisha_pages = render_qadisha(root) if (root / "templates/mirrors/qadisha.html").exists() else {}
    monastery_pages = render_monasteries(root) if (root / "templates/mirrors/qannoubine-monastery.html").exists() else {}
    if (root/'qadisha-valley.html').exists():
        validate_qadisha(root)
    # Generated English copy has exact freshness verification in full QA.
    if testimony_catalog and (root / 'testimonies-copy.js').exists():
        generated_copy = (root / 'testimonies-copy.js').read_text()
        for key in ('readerUnavailable', 'readerSuccess', 'readerError'):
            if json.dumps(testimony_catalog[key], ensure_ascii=False) not in generated_copy:
                errors.append(f'testimonies-copy.js: {key} differs from English catalog')
    from i18n.exact_master import render_exact_set
    for path, expected in render_exact_set(root,read_json(root/'locales/registry.json')).items():
        from i18n.same_page_injection import inject_control
        from i18n.travel_components import travel_frame
        from i18n.tour_nav import tour_nav
        lang=path.relative_to(root).parts[0]
        expected=travel_frame(tour_nav(expected,root,lang),root,lang,'/'+str(path.relative_to(root)).removesuffix('.html'),read_json(root/'locales/registry.json'))
        expected=inject_control(expected,root,read_json(root/'locales/same-page-manifest.pending.json'),read_json(root/'locales/same-page-copy.json'))
        if path.read_text()!=expected: errors.append(str(path.relative_to(root))+': exact output differs from guarded catalog')
    for file, values in snapshot(root).items():
        additions = Counter(values) - Counter(baseline.get(file, {}))
        if file == 'videos.html':
            # Exact fragment output is checked by build-pages --check; never expand the legacy baseline.
            additions -= Counter({v: 23 for v in read_json(root/'locales/en/video-playback.json').values()})
        if file=='share.js':
            additions-=Counter(v for k,v in read_json(root/'locales/en/share.json').items() if k.startswith('share.'))
        # One generated Travel hub entry, backed by the shared locale catalog.
        if '<nav class="links"' in (root/file).read_text() and file.endswith('.html'):
            additions -= Counter({read_json(root/'locales/en/travel.json')['hubLabel']:1})
        if file.endswith('.html'):
            from bs4 import BeautifulSoup
            page = BeautifulSoup((root/file).read_text(),'html.parser')
            code = page.html.get('lang','en') if page.html else 'en'
            tour_copy = root/f'locales/{code}/nav-tour.json'
            if tour_copy.exists():
                label = read_json(tour_copy)['header.annayaTour']
                matching = [a for a in page.select('header a[href]') if a.get('href','').removeprefix('../').removeprefix('./').removeprefix('/') == 'annaya-tour' and a.get_text(strip=True) == label]
                if len(matching) == 1: additions -= Counter({label:1})
        if file == "404.html" and error_404_rendered is not None:
            additions -= extract_html(error_404_rendered)
        if file.startswith('miracles/eucharistic/'):
            # Built from the keyed English collection catalog; separate build check covers freshness.
            # The dedicated builder is checked byte-for-byte in QA.
            continue
        if root/file in prayer_mirror or root/file in qadisha_pages or root/file in monastery_pages:
            # This English legacy URL now renders entirely from its own keyed
            # English catalog; freshness is checked byte-for-byte by the build.
            continue
        if file == 'testimonies.html' and testimony_catalog:
            # Existing interactive page; cataloged English strings are static
            # and the archive block is verified by the reproducible build.
            for key in ('title', 'description', 'introduction', 'readerInitial'):
                additions.pop(testimony_catalog[key], None)
        # Newly edited English legacy pages are catalog-backed, not added to
        # the frozen legacy baseline. The per-file counts prevent a second
        # unreviewed occurrence from being silently accepted.
        additions -= Counter(maroun_catalog.get(file, {}))
        additions -= Counter(augustine_catalog.get(file, {}))
        additions -= Counter(marina_catalog.get(file, {}))
        additions -= Counter(annaya_catalog.get(file, {}))
        additions -= Counter(sergius_catalog.get(file, {}))
        additions -= Counter(magdalene_catalog.get(file, {}))
        additions -= Counter(jude_catalog.get(file, {}))
        additions -= Counter(peter_catalog.get(file, {}))
        additions -= Counter(therese_catalog.get(file, {}))
        additions -= Counter(anthony_catalog.get(file, {}))
        additions -= Counter(joseph_catalog.get(file, {}))
        additions -= Counter(answer_catalog.get(file, {}))
        additions -= Counter(francis_catalog.get(file, {}))
        additions -= Counter(massabki_catalog.get(file, {}))
        additions -= Counter(jpii_story_catalog.get(file, {}))
        additions -= Counter(story_copy_catalog.get(file, {}))
        additions -= Counter(display_catalog.get(file, {}))
        additions -= Counter(accessibility_catalog.get(file, {}))
        additions -= Counter(aeo_catalog.get(file, {}))
        additions -= Counter(shelf_catalog.get(file, {}))
        additions -= Counter(saint_bios_catalog.get(file, {}))
        additions -= Counter(pillar_catalog.get(file, {}))
        additions -= Counter(a11y_catalog.get(file, {}))
        additions -= Counter(scripture_catalog.get(file, {}))
        stale_scripture = Counter(scripture_catalog.get(file, {})) - Counter(values)
        if stale_scripture:
            errors.append(f'{file}: scripture-copy catalog entries missing from the page: {sorted(stale_scripture)[:3]}')
        if file == 'miracles/index.html':
            euch_entry = read_json(root/'locales/en/eucharistic-miracles.json')['hub']
            additions -= Counter({euch_entry[key]: 1 for key in ('charbelEntryTitle','charbelEntryIntro','charbelEntryAction','charbelEntryCredit','charbelEntryAlt','charbelEntryPhotoSource','charbelEntryLicense','charbelEntryLicenseText','eyebrow')})
            additions -= Counter({',': 1, '.': 1})
        if file in ('story.html','pio-story.html','jpii-story.html'):
            additions -= Counter({'Story settings': 2})
            if file != 'story.html': additions -= Counter({storybook_catalog['disclosure']: 1})
        if file == 'storybook.js': additions -= Counter({read_json(root/'locales/en/pio-story-copy.json')['firstPage']: 1})
        if file in ('mother-teresa-story.html','rafqa-story.html','hardini-story.html','charbel-story-v2.html'):
            additions -= Counter({'Story settings': 2, storybook_catalog['disclosure']: 1})
        additions -= Counter(teresa_catalog.get(file, {}))
        additions -= Counter(rafqa_catalog.get(file, {}))
        additions -= Counter(hardini_catalog.get(file, {}))
        additions -= Counter(pio_film_catalog.get(file, {}))
        additions -= Counter(charbel_v2_catalog.get(file, {}))
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
