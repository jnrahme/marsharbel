"""Saint of the Day null-book plate: monogram derivation + localized short dates.

Derives the single-letter monogram for the solo-card plate from the saint's
display name in the page's locale (titles stripped per locale, Arabic article
and tashkeel stripped), plus the localized short date without year used under
the initial. A reviewed per-locale 'monogram' override in the saint copy pack
always wins. When nothing is derivable the caller falls back to the plain halo
plate. Pure functions; no I/O.
"""
import re,unicodedata
from datetime import date as _date

TITLES = {
    'en': ['Servant of God', 'Venerable', 'Ven.', 'Blessed', 'Bl.', 'Saint', 'St.', 'Pope'],
    'ar': ['القديسة', 'القديس', 'الطوباوية', 'الطوباوي', 'البابا', 'الأب'],
    'de': ['Heiliger', 'Heilige', 'Seliger', 'Selige'],
    'fr': ['Sainte', 'Saint', 'Bienheureuse', 'Bienheureux'],
    'es': ['Santa', 'San', 'Beata', 'Beato'],
    'it': ['Santa', 'San', 'Beata', 'Beato'],
    'pt': ['São', 'Santa', 'Santo', 'Beata', 'Beato'],
    'pl': ['Święta', 'Święty', 'Błogosławiona', 'Błogosławiony'],
    'ru': ['Святая', 'Святой', 'Блаженная', 'Блаженный'],
    'hi': ['संत', 'धन्य'],
    'th': ['นักบุญ'],
}

MONTHS_SHORT = {
    'en': ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
    'ar': ['كانون الثاني','شباط','آذار','نيسان','أيار','حزيران','تموز','آب','أيلول','تشرين الأول','تشرين الثاني','كانون الأول'],
    'fr': ['janv.','févr.','mars','avr.','mai','juin','juil.','août','sept.','oct.','nov.','déc.'],
    'es': ['ene','feb','mar','abr','may','jun','jul','ago','sept','oct','nov','dic'],
    'pt': ['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'],
    'it': ['gen','feb','mar','apr','mag','giu','lug','ago','set','ott','nov','dic'],
    'de': ['Jan.','Feb.','März','Apr.','Mai','Juni','Juli','Aug.','Sept.','Okt.','Nov.','Dez.'],
    'pl': ['sty','lut','mar','kwi','maj','cze','lip','sie','wrz','paź','lis','gru'],
    'ru': ['янв.','февр.','мар.','апр.','мая','июн.','июл.','авг.','сент.','окт.','нояб.','дек.'],
    'hi': ['जन.','फ़र.','मार्च','अप्रै.','मई','जून','जुल.','अग.','सित.','अक्टू.','नव.','दिस.'],
    'th': ['ม.ค.','ก.พ.','มี.ค.','เม.ย.','พ.ค.','มิ.ย.','ก.ค.','ส.ค.','ก.ย.','ต.ค.','พ.ย.','ธ.ค.'],
}

_TASHKEEL = dict.fromkeys(range(0x064B, 0x0653), None) | {0x0670: None, 0x0640: None}

def _strip_titles(name, lang):
    titles = sorted(TITLES.get(lang, ()), key=len, reverse=True)
    out = name.strip()
    changed = True
    while changed:
        changed = False
        for t in titles:
            # Thai script runs words together, so its titles match without a space boundary.
            boundary = r'(?=.)' if lang == 'th' else r'(?=\s|$)'
            m = re.match(r'^\s*' + re.escape(t) + boundary, out, flags=re.IGNORECASE)
            if m:
                out = out[m.end():].strip()
                changed = True
    return out

def _first_letter(text):
    for ch in text:
        if ch.isalpha():
            return ch
    return None

def derive_monogram(name, lang, override=None):
    """Single-letter monogram, or None when nothing is derivable."""
    if override and override.strip():
        return override.strip()
    rest = _strip_titles(name or '', lang)
    if lang == 'ar':
        rest = rest.translate(_TASHKEEL).strip()
        while rest.startswith('ال') and len(rest) > 2:
            rest = rest[2:].lstrip()
    letter = _first_letter(rest)
    if lang == 'th':
        # Thai preposed vowels (เ แ โ ใ ไ) render before their consonant; the monogram is the consonant.
        while letter is not None and letter in 'เแโใไ':
            rest = rest[rest.index(letter) + 1:]
            letter = _first_letter(rest)
    if letter is None:
        return None
    up = letter.upper()
    # Uppercasing must stay a single glyph (Latin/Cyrillic); other scripts are unchanged.
    return up if len(up) == 1 else letter

def date_short(iso_date, lang):
    """Localized short date without year, e.g. en '15 Oct', ar '15 تشرين الأول'."""
    d = _date.fromisoformat(iso_date)
    months = MONTHS_SHORT.get(lang) or MONTHS_SHORT['en']
    mon = months[d.month - 1]
    if lang == 'de':
        return f'{d.day}. {mon}'
    return f'{d.day} {mon}'

def plate_fields(name, lang, iso_date, override=None):
    """{'monogram','dateShort'} for the mono plate, or None for the halo fallback."""
    mono = derive_monogram(name, lang, override)
    if mono is None:
        return None
    return {'monogram': mono, 'dateShort': date_short(iso_date, lang)}


# --- saintImage production gate (design-director hard rule, 2026-10-15) ---
# The photo plate is only ever a REAL photograph or approved portrait of THAT
# saint, backed by an explicit per-saint source record. Storybook illustration
# paths are never eligible; no keyword-picking, no generated imagery.
# Production photo contract: portrait or face-visible crop only; set
# object-position per image (template default 50% 15%); never crop a face.
BOOK_ART_MARKERS = ('storybook', '/books/')

def saint_image_rejection(entry):
    """Return None when entry's saintImage may render, else the refusal reason.

    The caller falls back to the monogram plate on any non-None result.
    """
    img = (entry or {}).get('saintImage')
    if not img:
        return 'no saintImage'
    low = img.lower()
    for marker in BOOK_ART_MARKERS:
        if marker in low:
            return f'saintImage points at book/storybook art: {img}'
    src = (entry or {}).get('saintImageSource')
    if not isinstance(src, dict):
        return 'saintImage without a saintImageSource record'
    for field in ('url', 'licence', 'credit'):
        if not (src.get(field) or '').strip():
            return f'saintImageSource missing {field}'
    return None
