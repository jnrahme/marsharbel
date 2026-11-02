"""Exact inverse of mark_english_nav_hrefs, for review-pinned pages.

Pinned pages are frozen to reviewed candidate bytes. English-destination
marking (hreflang="en", aria-label "<label> <qualifier>", trailing
span.enc-language) is the only post-review header delta allowed. The final
full-file gate strips that delta, strictly, and compares the remainder with the
reviewed candidate. Anything else (changed text, extra attributes, a qualifier
that is not the locale's reviewed one, body bytes) survives the strip and fails
the equality check. Pages without marking pass through unchanged.
"""
import re
from html import escape, unescape

HEADER = re.compile(r'<header\b[\s\S]*?</header>')


def strip_marking(text, qualifier):
    header = HEADER.search(text)
    if not header or not qualifier:
        return text
    q_attr = re.escape(escape(qualifier, quote=True))
    q_text = re.escape(escape(qualifier))
    pattern = re.compile(
        r'<a\b((?:(?!<a\b)[^>])*?) hreflang="en" aria-label="([^"]*)"((?: [^>]*)?)>'
        r'([\s\S]*?) <span class="enc-language">' + q_text + r'</span></a>')

    def replace(m):
        before, label, after, body = m.groups()
        visible = unescape(re.sub(r'<span\b[\s\S]*?</span>', '', body).strip())
        if unescape(label) != visible + ' ' + qualifier:
            raise ValueError('Marking aria-label does not match visible label and qualifier')
        return '<a' + before + after + '>' + body + '</a>'

    block = pattern.sub(replace, header[0])
    return text[:header.start()] + block + text[header.end():]


def strip_for_locale(root, code, text):
    """Strip using the locale's reviewed qualifier; no-op for non-marking locales."""
    from i18n.encyclopedia_nav import MARKING_LOCALES
    from i18n.encyclopedia_trail import load_trail
    if code not in MARKING_LOCALES:
        return text
    return strip_marking(text, load_trail(root, code)['englishQualifier'])
