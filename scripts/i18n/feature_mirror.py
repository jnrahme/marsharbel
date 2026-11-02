"""Bounded extracted-feature validation; no whole-page mirror exceptions."""
import hashlib
import html
import json
import re
from bs4 import BeautifulSoup


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()

def one(soup, selector):
    nodes = soup.select(selector)
    if len(nodes) != 1:
        raise ValueError('Expected exactly one feature: ' + selector)
    return nodes[0]

def adapted(block):
    """The only permitted source-to-standalone changes, tested individually."""
    block = BeautifulSoup(str(block), 'html.parser').article
    heading = block.find('h3', recursive=False)
    if heading is None or len(heading.select('a.card-cover')) != 1:
        raise ValueError('Unexpected source heading')
    heading.name = 'h1'
    heading.a.unwrap()
    subheads = block.find_all('h4')
    if len(subheads) != 1:
        raise ValueError('Expected one video heading')
    subheads[0].name = 'h2'
    block['class'] = ['film-news-article']
    return block

def shell_digest(text, route):
    soup = BeautifulSoup(text, 'html.parser')
    feature = one(soup, 'main > article.film-news-article')
    feature.decompose()
    # Independent final-shell pin includes every attribute, label, metadata value,
    # full URL/query, runtime dictionary and control. Only feature is excluded.
    return digest(str(soup))
