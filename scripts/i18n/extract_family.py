"""Extract keyed-master bindings + English copy from an EN master page.

Usage: python3 scripts/i18n/extract_family.py <master.html> <family> <key-prefix>
Writes locales/en/<family>-bindings.json and locales/en/<family>-copy.json.
Covers: <title>, meta description/og:title/og:description, text nodes in
header/main/footer (excluding script/style/noscript), img[alt] in main.
"""
import hashlib, json, re, sys
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

ROOT = Path(__file__).resolve().parents[2]

def slug(text, used):
    words = re.findall(r"[a-z0-9]+", text.lower())[:6]
    base = '-'.join(words) or 'text'
    s, i = base, 2
    while s in used:
        s = f'{base}-{i}'; i += 1
    used.add(s)
    return s

def selector_for(node):
    chain = []
    cur = node
    while cur is not None and getattr(cur, 'name', None):
        if cur.get('id'):
            chain.append(f'#{cur["id"]}')
            break
        sibs = [s for s in cur.parent.find_all(cur.name, recursive=False)] if cur.parent else [cur]
        idx = sibs.index(cur) + 1
        chain.append(f'{cur.name}:nth-of-type({idx})')
        cur = cur.parent
    return ' > '.join(reversed(chain))

def main():
    master, family, prefix = sys.argv[1], sys.argv[2], sys.argv[3]
    raw = (ROOT / master).read_bytes()
    soup = BeautifulSoup(raw, 'html.parser')
    bindings, messages, used = [], {}, set()

    def add(sel, source, kind, key_hint, node_index=None, attribute=None):
        nodes = soup.select(sel)
        if len(nodes) != 1:
            return  # ambiguous or missing: skip, never bind
        key = f'{prefix}.{key_hint}'
        b = {'key': key, 'selector': sel, 'source': source, 'kind': kind}
        if kind == 'text':
            b['nodeIndex'] = node_index
        else:
            b['attribute'] = attribute
        bindings.append(b)
        messages[key] = source

    t = soup.select_one('title')
    if t and t.string and t.string.strip():
        add(selector_for(t), ' '.join(t.string.split()), 'text', 'title', node_index=0)
    for name, hint in (('description', 'meta-description'),):
        m = soup.select_one(f'meta[name="{name}"]')
        if m and m.get('content'):
            add(selector_for(m), m['content'], 'attribute', hint, attribute='content')
    for prop, hint in (('og:title', 'meta-og-title'), ('og:description', 'meta-og-description')):
        m = soup.select_one(f'meta[property="{prop}"]')
        if m and m.get('content'):
            add(selector_for(m), m['content'], 'attribute', hint, attribute='content')

    for region in ('header', 'main', 'footer'):
        root_el = soup.select_one(region)
        if not root_el:
            continue
        for el in root_el.find_all(string=True):
            if not isinstance(el, NavigableString):
                continue
            if el.parent.name in ('script', 'style', 'noscript'):
                continue
            txt = ' '.join(str(el).split())
            if not txt or len(txt) < 2:
                continue
            parent = el.parent
            idx = next(i for i, c in enumerate(parent.contents) if c is el)
            sel = selector_for(parent)
            sec = parent.find_parent(id=True)
            sec_id = sec['id'] if sec else parent.name
            hint = f'{region}-{sec_id}-{slug(txt, used)}'
            add(sel, txt, 'text', hint, node_index=idx)
        if region == 'main':
            for img in root_el.find_all('img'):
                if img.get('alt'):
                    add(selector_for(img), img['alt'], 'attribute', f'main-img-alt-{slug(img["alt"], used)}', attribute='alt')

    contract = {
        'version': 1,
        'master': master,
        'masterSha256': hashlib.sha256(raw).hexdigest(),
        'sourceRevision': sys.argv[4] if len(sys.argv) > 4 else 'unknown',
        'bindings': bindings,
        'messages': messages,
    }
    (ROOT / f'locales/en/{family}-bindings.json').write_text(json.dumps(contract, indent=1, ensure_ascii=False) + '\n')
    (ROOT / f'locales/en/{family}-copy.json').write_text(json.dumps(messages, indent=1, ensure_ascii=False) + '\n')
    print(f'{family}: {len(bindings)} bindings extracted')

if __name__ == '__main__':
    main()
