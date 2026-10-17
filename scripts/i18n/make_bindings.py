"""Generate keyed-master bindings + English copy for a page family from its English master HTML.

Usage: python3 scripts/i18n/make_bindings.py <master.html> <family> <prefix>
Writes locales/en/<family>-bindings.json and locales/en/<family>-copy.json.
Format matches scripts/i18n/keyed_master.py (selector, source, kind, nodeIndex | attribute).
"""
import hashlib, json, re, subprocess, sys
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Comment

ROOT = Path(__file__).resolve().parents[2]
ATTRS = ('alt', 'aria-label', 'title', 'placeholder')
META = ('description', 'og:title', 'og:description', 'twitter:title', 'twitter:description')


def slug(text, n=60):
    s = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    return s[:n].strip('-') or 'text'


def selector(node):
    parts = []
    while node is not None and node.name != '[document]':
        if node.get('id'):
            parts.append('#' + node['id'])
            break
        siblings = [s for s in node.parent.find_all(node.name, recursive=False)] if node.parent else [node]
        parts.append(f'{node.name}:nth-of-type({next(i for i, s in enumerate(siblings) if s is node) + 1})')
        node = node.parent
    return ' > '.join(reversed(parts))


def area(node, current):
    for p in node.parents:
        if p.name in ('header', 'footer'):
            return p.name
        if p.name == 'head':
            return 'metadata'
    return current


def build(master, family, prefix):
    raw = (ROOT / master).read_bytes()
    soup = BeautifulSoup(raw, 'html.parser')
    bindings, messages, taken = [], {}, {}

    def key_for(source, kind_area, base):
        k = f'{prefix}.{kind_area}.{slug(base or source)}'
        if k in messages and messages[k] != source:
            i = 2
            while f'{k}-{i}' in messages and messages[f'{k}-{i}'] != source: i += 1
            k = f'{k}-{i}'
        messages[k] = source
        return k

    # head: title, meta
    if soup.title and soup.title.string:
        src = ' '.join(soup.title.string.split())
        bindings.append(dict(key=key_for(src, 'metadata', 'title ' + src), selector=selector(soup.title), source=src, kind='text', nodeIndex=0))
    for m in soup.select('meta[name],meta[property]'):
        name = m.get('name') or m.get('property')
        if name in META and m.get('content'):
            bindings.append(dict(key=key_for(m['content'], 'metadata', name + ' ' + m['content']), selector=selector(m), source=m['content'], kind='attribute', attribute='content'))
    current = 'body'
    for el in soup.body.descendants:
        if getattr(el, 'name', None) in ('h1', 'h2'):
            current = slug(el.get_text(' ', strip=True), 24)
        if getattr(el, 'attrs', None):
            for a in ATTRS:
                if el.get(a) and isinstance(el[a], str) and re.search(r'[A-Za-z]{2}', el[a]):
                    area_ = 'accessibility' if a in ('aria-label', 'alt') else area(el, current)
                    bindings.append(dict(key=key_for(' '.join(el[a].split()), area_, el[a]), selector=selector(el), source=' '.join(el[a].split()), kind='attribute', attribute=a))
        if isinstance(el, NavigableString) and not isinstance(el, Comment):
            if el.parent.name in ('script', 'style') or not el.strip():
                continue
            src = ' '.join(str(el).split())
            node = el.parent
            idx = next(i for i, c in enumerate(node.contents) if c is el)
            a_ = area(node, current)
            bindings.append(dict(key=key_for(src, a_, src), selector=selector(node), source=src, kind='text', nodeIndex=idx))
    # drop dupes of same key+selector
    out = {'version': 1, 'master': master, 'masterSha256': hashlib.sha256(raw).hexdigest(),
           'sourceRevision': subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
           'bindings': bindings, 'messages': messages}
    return out, messages


if __name__ == '__main__':
    master, family, prefix = sys.argv[1:4]
    contract, messages = build(master, family, prefix)
    (ROOT / f'locales/en/{family}-bindings.json').write_text(json.dumps(contract, ensure_ascii=False, indent=2) + '\n')
    (ROOT / f'locales/en/{family}-copy.json').write_text(json.dumps(messages, ensure_ascii=False, indent=2) + '\n')
    print(family, len(contract['bindings']), 'bindings', len(messages), 'messages')
