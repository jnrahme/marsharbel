#!/usr/bin/env python3
"""DOM-normalized comparison of two HTML files.

Ignores: doctype case, comments, whitespace between tags, collapsed whitespace in text,
attribute order, quote style, self-closing slash. Reports every other difference.
Usage: dom_equiv.py A.html B.html   (exit 0 = equivalent, 1 = differences printed)
"""
import sys, re, difflib, json
from html.parser import HTMLParser

VOID = {'meta', 'link', 'img', 'br', 'hr', 'input', 'source', 'area', 'base', 'col', 'embed', 'track', 'wbr'}

class Norm(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.stack = [], []
    def handle_starttag(self, tag, attrs):
        if tag == 'meta':  # charset values are case-insensitive (utf-8 == UTF-8)
            attrs = [(k, v.lower() if k == 'charset' and v else v) for k, v in attrs]
        a = ' '.join(f'{k}={("" if v is None else v)!r}' for k, v in sorted(attrs))
        self.out.append(f'{"  " * len(self.stack)}<{tag} {a}>')
        if tag not in VOID: self.stack.append(tag)
    def handle_startendtag(self, tag, attrs):
        if tag == 'meta':  # charset values are case-insensitive (utf-8 == UTF-8)
            attrs = [(k, v.lower() if k == 'charset' and v else v) for k, v in attrs]
        a = ' '.join(f'{k}={("" if v is None else v)!r}' for k, v in sorted(attrs))
        self.out.append(f'{"  " * len(self.stack)}<{tag} {a}>')
    def handle_endtag(self, tag):
        if tag in self.stack:
            while self.stack and self.stack.pop() != tag: pass
    def handle_data(self, data):
        if self.stack and self.stack[-1] == 'script' and self.out and 'application/ld+json' in self.out[-1]:
            try: data = json.dumps(json.loads(data), sort_keys=True, ensure_ascii=False)
            except ValueError: pass
        t = re.sub(r'\s+', ' ', data).strip()
        if t: self.out.append(f'{"  " * len(self.stack)}"{t}"')

def norm(path):
    p = Norm(); p.feed(open(path, encoding='utf-8').read()); return p.out

if __name__ == '__main__':
    a, b = norm(sys.argv[1]), norm(sys.argv[2])
    if a == b: print('equivalent'); sys.exit(0)
    for l in difflib.unified_diff(a, b, 'before', 'after', n=0, lineterm=''):
        if not l.startswith(('---', '+++', '@@')): print(l[:300])
    sys.exit(1)
