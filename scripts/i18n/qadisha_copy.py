"""Validate the corrected English Qadisha paragraphs against plain-text slots."""
from html import escape
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
    page = (root / PAGE).read_text(encoding='utf-8')
    body, faq = paragraphs(root)
    pattern = r'(<h2>Saint Charbel and the Qadisha</h2>\s*<div class="card story">\s*)(<p>.*?</p>)'
    match = re.search(pattern, page, re.S)
    q_pattern = r'(<h3>What is Saint Charbel.s connection to the Qadisha Valley\?</h3>\s*)(<p>.*?</p>)'
    question = re.search(q_pattern, page, re.S)
    if not match or not question or match[2] != body or question[2] != faq:
        raise ValueError('English Qadisha correction differs from keyed catalog')
    expected_faq = read_json(root / CATALOG)['faqBeforeTrail'] + read_json(root / CATALOG)['trailLink'] + read_json(root / CATALOG)['faqAfterTrail']
    faq_blocks = [json.loads(block) for block in re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', page, re.S)]
    matching = [item['acceptedAnswer']['text'] for block in faq_blocks
                if block.get('@type') == 'FAQPage' for item in block['mainEntity']
                if item['name'] == 'What is Saint Charbel\'s connection to the Qadisha Valley?']
    if matching != [expected_faq]:
        raise ValueError('Qadisha FAQ schema differs from keyed visible answer')
    return page


if __name__ == '__main__':
    validate()
    print('English Qadisha correction matches keyed catalog.')
