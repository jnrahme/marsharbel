"""Validate the corrected English Qadisha paragraphs against plain-text slots."""
from html import escape, unescape
import json
from pathlib import Path
import re

from i18n.catalog import ROOT, leaves, read_json

CATALOG = 'locales/en/qadisha-corrections.json'
PAGE = 'qadisha-valley.html'


def paragraphs(root=ROOT):
    text = read_json(root / CATALOG)
    expected = {'beforeBirthplace', 'birthplaceLink', 'betweenLinks', 'hermitageLink',
                'afterHermitage', 'faqBeforeTrail', 'trailLink', 'faqAfterTrail'}
    if set(text) != expected:
        raise ValueError(f'Qadisha correction keys: expected {sorted(expected)}')
    leaves(text)
    def slot(key):
        return escape(text[key], quote=True)
    body = ('<p>' + slot('beforeBirthplace') + '<a href="./bekaa-kafra">' +
            slot('birthplaceLink') + '</a>' + slot('betweenLinks') +
            '<a href="./saint-charbel-hermitage">' + slot('hermitageLink') +
            '</a>' + slot('afterHermitage') + '</p>')
    faq = ('<p>' + slot('faqBeforeTrail') + '<a href="./saint-charbel-trail">' +
           slot('trailLink') + '</a>' + slot('faqAfterTrail') + '</p>')
    return body, faq


def validate(root=ROOT):
    """Ensure the master, keyed correction, and visible FAQ all agree."""
    page = (root / PAGE).read_text(encoding='utf-8')
    copy = read_json(root / CATALOG)
    catalog = read_json(root / 'locales/en/mirrors/qadisha.json')
    if [catalog[key] for key in ('charbel.text1', 'charbel.link1', 'charbel.text2',
                                  'charbel.link2', 'charbel.text3')] != [copy[key] for key in
                                  ('beforeBirthplace', 'birthplaceLink', 'betweenLinks',
                                   'hermitageLink', 'afterHermitage')]:
        raise ValueError('English Qadisha master differs from correction catalog')
    if [catalog[key] for key in ('faq.text5', 'faq.link1', 'faq.text6')] != [copy[key] for key in
                                  ('faqBeforeTrail', 'trailLink', 'faqAfterTrail')]:
        raise ValueError('English Qadisha FAQ differs from correction catalog')
    pattern = r'(<h2>Saint Charbel and the Qadisha</h2>\s*<div class="card story">\s*)(<p>.*?</p>)'
    match = re.search(pattern, page, re.S)
    q_pattern = r'(<h3>What is Saint Charbel.s connection to the Qadisha Valley\?</h3>\s*)(<p>.*?</p>)'
    question = re.search(q_pattern, page, re.S)
    def visible(fragment):
        return unescape(re.sub(r'<[^>]*>', '', fragment))
    expected_body = ''.join(copy[key] for key in ('beforeBirthplace', 'birthplaceLink',
                                                   'betweenLinks', 'hermitageLink', 'afterHermitage'))
    expected_faq = ''.join(copy[key] for key in ('faqBeforeTrail', 'trailLink', 'faqAfterTrail'))
    if not match or not question or visible(match[2]) != expected_body or visible(question[2]) != expected_faq:
        raise ValueError('English Qadisha correction differs from visible copy')
    faq_blocks = [json.loads(block) for block in re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', page, re.S)]
    matching = [item['acceptedAnswer']['text'] for block in faq_blocks
                if block.get('@type') == 'FAQPage' for item in block['mainEntity']
                if item['name'] == catalog['faq.question5']]
    if matching != [expected_faq]:
        raise ValueError('Qadisha FAQ schema differs from keyed visible answer')
    unesco_pattern = r'(<h2>UNESCO World Heritage Status</h2>\s*<div class="card story">\s*<p>.*?</p>\s*)(<p>.*?</p>)'
    unesco = re.search(unesco_pattern, page, re.S)
    expected_unesco = ''.join(catalog[key] for key in ('unesco.text2', 'unesco.link1', 'unesco.text3'))
    if not unesco or visible(unesco[2]) != expected_unesco or 'not a third property in the UNESCO inscription' not in expected_unesco:
        raise ValueError('Qadisha UNESCO distinction differs from keyed catalog')
    return page


if __name__ == '__main__':
    validate()
    print('English Qadisha correction matches keyed catalog.')
