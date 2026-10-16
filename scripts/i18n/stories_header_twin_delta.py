"""Exact inverse for the 25 independently scoped Stories header destination deltas."""
import json
import re
from i18n.reviewed_history import digest

SLUGS = ('annaya-tour','bekaa-kafra','bkerke-maronite-patriarchate',
         'cedars-of-god-lebanon','our-lady-of-lebanon-harissa','qadisha-valley',
         'qannoubine-monastery','qozhaya-monastery','saint-charbel-hermitage',
         'saint-charbel-places-lebanon','saint-charbel-trail','travel')
PAIRS = {(slug+'-travel-master',code) for slug in SLUGS for code in ('de','ru')} | {('travel-travel-master','hi')}
HEADER = re.compile(r'<header\b[\s\S]*?</header>')
ANCHOR = re.compile(r'<a\b[^>]*>[\s\S]*?</a>')
HI_QUALIFIER = '<span class="launch-english-qualifier"> (अंग्रेज़ी में)</span>'


def intended_anchor(text, href):
    headers = list(HEADER.finditer(text))
    if len(headers) != 1:
        raise ValueError('Stories amendment needs one header')
    matches = [m for m in ANCHOR.finditer(headers[0][0])
               if re.search(r'\bhref="'+re.escape(href)+r'"',m[0])]
    if len(matches) != 1:
        raise ValueError('Stories amendment needs one exact header destination')
    return headers[0], matches[0]


def inverse(root, family, code, text, candidate):
    """Both arguments already passed the existing strict DE marking inverse.

    Return only the exact former candidate representation. The caller still
    performs its original complete-file equality comparison with original pins.
    """
    if text == candidate:
        return text
    if (family,code) not in PAIRS:
        return text
    registry = json.loads((root/'locales/registry.json').read_text())
    family_config = registry.get('pageMirrors',{}).get('stories-master',{})
    if code not in family_config.get('renderLocales',[]):
        return text
    target = '/'+code+'/stories'
    if family_config.get('routes',{}).get(code) != target:
        raise ValueError('Stories amendment destination differs')
    record = json.loads((root/'locales/stories-equivalence.json').read_text())
    if record.get('reviewStatus') != 'isolated-review-pass':
        raise ValueError('Stories amendment destination unreviewed')
    destination = root/(code+'/stories.html')
    # Full build supplies generated destinations before writing output files.
    generated = _outputs.get(destination)
    if generated is None and destination.is_file():
        generated = destination.read_text()
    if generated is None or digest(generated) != record['variants'][code]['bodySha256']:
        raise ValueError('Stories amendment destination not rendered and reviewed')
    original_header, old = intended_anchor(candidate,'/stories')
    final_header, new = intended_anchor(text,target)
    expected = old[0].replace('href="/stories"','href="'+target+'"',1)
    if code == 'hi':
        if expected.count(HI_QUALIFIER) != 1:
            raise ValueError('Stories Hindi exact original qualifier missing')
        expected = expected.replace(HI_QUALIFIER,'',1)
    if new[0] != expected:
        raise ValueError('Stories amendment changed label or attributes')
    restored = final_header[0][:new.start()] + old[0] + final_header[0][new.end():]
    return text[:final_header.start()] + restored + text[final_header.end():]


# Explicit per-build context, reset at the final-output boundary.
_outputs = {}
def set_outputs(texts):
    global _outputs
    _outputs = texts
