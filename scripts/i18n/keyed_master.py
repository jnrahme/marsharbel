"""Validate keyed copy against an immutable master before applying any edits."""
import hashlib
import re
from bs4 import BeautifulSoup, NavigableString
from i18n.catalog import read_json


def apply_keyed_master(root, family, lang, catalog=None):
    contract = read_json(root / f'locales/en/{family}-bindings.json')
    raw = (root / contract['master']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != contract['masterSha256']:
        raise ValueError(f'{family} master changed: update bindings and reviewed locale catalogs')
    english = read_json(root / f'locales/en/{family}-copy.json')
    copy = catalog if catalog is not None else read_json(root / f'locales/{lang}/{family}-copy.json')
    if set(copy) != set(english):
        raise ValueError(f'{family} {lang}: missing/extra message keys: {sorted(set(english) ^ set(copy))}')
    for key, value in copy.items():
        if not isinstance(value, str) or not value.strip() or re.search(r'<\s*/?\s*[A-Za-z!]', value):
            raise ValueError(f'{family} {lang}: unsafe or empty message {key}')
        if set(re.findall(r'\{([A-Za-z]+)\}', value)) != set(re.findall(r'\{([A-Za-z]+)\}', english[key])):
            raise ValueError(f'{family} {lang}: placeholders differ for {key}')
    soup = BeautifulSoup(raw, 'html.parser')
    pending=[]
    for binding in contract['bindings']:
        nodes=soup.select(binding['selector'])
        if len(nodes)!=1:raise ValueError(f'{family}: ambiguous binding {binding["key"]}')
        node=nodes[0]
        if binding['kind']=='attribute':
            if node.get(binding['attribute'])!=binding['source']:raise ValueError(f'{family}: changed attribute {binding["key"]}')
            pending.append((node,binding, None))
        else:
            text=node.contents[binding['nodeIndex']]
            if not isinstance(text,NavigableString) or ' '.join(str(text).split())!=binding['source']:raise ValueError(f'{family}: changed text {binding["key"]}')
            pending.append((node,binding,text))
    # Validate all bindings before replacing any node, including repeated keys.
    for node,binding,text in pending:
        value=copy[binding['key']]
        if text is None:node[binding['attribute']]=value
        else:
            old=str(text)
            text.replace_with(old[:len(old)-len(old.lstrip())]+value+old[len(old.rstrip()):])
    return raw,soup,copy
