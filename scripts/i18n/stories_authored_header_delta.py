"""Raw href-only inverse for the independently enumerated authored15 fixture set."""
import hashlib
import json
import subprocess
from i18n.stories_header_twin_delta import intended_anchor

BASE = '194b3cb965173162e0890833013760ed6b4f0573'
FILES = frozenset({code+'/travel.html' for code in ('ar','fr','es','pt','it','pl')} | {
    'ar/qadisha-valley.html','fr/vallee-qadisha.html','es/valle-qadisha.html',
    'ar/qannoubine-monastery.html','fr/monastere-qannoubine.html','es/monasterio-qannoubine.html',
    'ar/qozhaya-monastery.html','fr/monastere-qozhaya.html','es/monasterio-qozhaya.html'})


def inverse(root, file, text, expected_sha):
    if file not in FILES:
        return text
    original = subprocess.check_output(['git','show',BASE+':'+file],cwd=root).decode()
    if hashlib.sha256(original.encode()).hexdigest() != expected_sha:
        raise ValueError('Authored Stories original fixture drift')
    if text == original:
        return text
    code = file.split('/')[0]
    # Destination must be the accepted rendered Stories body, not config alone.
    raw = (root/'locales/stories-equivalence.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != '1548b0d229445fadd59b725da7d98e6e9e338b23d11dce9cfaaae8112ad02e6a':
        raise ValueError('Authored Stories accepted evidence table edited')
    record = json.loads(raw)
    for path, expected in record['sourceFiles'].items():
        if hashlib.sha256((root/path).read_bytes()).hexdigest() != expected:
            raise ValueError('Authored Stories accepted source drift')
    from i18n.reviewed_history import digest
    if digest((root/(code+'/stories.html')).read_text()) != record['variants'][code]['bodySha256']:
        raise ValueError('Authored Stories destination drift')
    registry = json.loads((root/'locales/registry.json').read_text())
    config = registry.get('pageMirrors',{}).get('stories-master',{})
    if code not in config.get('renderLocales',[]) or config.get('routes',{}).get(code) != '/'+code+'/stories':
        raise ValueError('Authored Stories destination unregistered')
    old_header, old_anchor = intended_anchor(original,'/stories')
    new_header, new_anchor = intended_anchor(text,'/'+code+'/stories')
    expected = old_anchor[0].replace('href="/stories"','href="/'+code+'/stories"',1)
    if new_anchor[0] != expected:
        raise ValueError('Authored Stories anchor label/attribute drift')
    restored_header = new_header[0][:new_anchor.start()] + old_anchor[0] + new_header[0][new_anchor.end():]
    restored = text[:new_header.start()] + restored_header + text[new_header.end():]
    if restored != original:
        raise ValueError('Authored Stories non-href byte drift')
    return restored
