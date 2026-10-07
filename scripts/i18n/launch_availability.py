"""Reviewed home/history-only launch disclosure, not a publication grant."""
import json
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from i18n.catalog import read_json


def apply_launch_availability(text, root, registry, lang, home=False):
    if lang not in registry.get('limitedLaunchLocales', []):
        return text
    copy = read_json(root / f'locales/{lang}/launch-availability.json')
    if set(copy) != {'availability.heading', 'availability.note', 'availability.englishQualifier'}:
        raise ValueError('Incomplete launch availability catalog: ' + lang)
    soup = BeautifulSoup(text, 'html.parser')
    # These are explicit source destinations, not guessed same-page twins.
    localized = {registry['locales'][lang]['home'], registry['pageMirrors']['history-master']['routes'][lang]}
    qualifier = copy['availability.englishQualifier']
    for a in soup.select('header a[href], main a[href]'):
        path = urlsplit(a['href'])
        if path.scheme or not path.path or path.path in localized or a.has_attr('hreflang'):
            continue
        if not a.get_text(strip=True) or path.path.startswith('/' + lang + '/'):
            continue
        # Bound the exception to links to actual English HTML pages.
        file = root / path.path.strip('/')
        file = file / 'index.html' if path.path.endswith('/') else file.with_suffix('.html')
        if not file.is_file():
            continue
        if qualifier not in a.get_text():
            hint = soup.new_tag('span', attrs={'class': 'launch-english-qualifier'})
            hint.string = ' ' + qualifier
            a.append(hint)
    if home:
        note = soup.new_tag('aside', attrs={'class': 'section launch-availability', 'aria-labelledby': 'launch-availability-heading'})
        heading = soup.new_tag('h2', id='launch-availability-heading')
        heading.string = copy['availability.heading']
        paragraph = soup.new_tag('p')
        paragraph.string = copy['availability.note']
        note.extend([heading, paragraph])
        soup.main.insert(0, note)
    return str(soup)
