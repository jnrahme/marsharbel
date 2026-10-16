"""Scoped Stories shelf data-copy validation; never ignore arbitrary data attributes."""
from pathlib import Path
from collections import Counter
import hashlib,json,re
from bs4 import BeautifulSoup
from i18n.catalog import read_json

FAMILY = 'stories-master'
MASTER_SHA256 = 'd8f15f97cd12c8f79d546a9e1d9b903de46635ec3e4277b67d9110394ebd1c13'
CONTRACT_SHA256 = 'b9780fd3fc43028b403ad74e8fb624b694a20196f17e75c1c138a8af1bcdcb6d'
ENGLISH_COPY_SHA256 = '8a778a00de2b5411ccc110513dad8e852796abaa7336342cf14e61426e658cd0'
DATA_COPY = {'data-keywords','data-one','data-many','data-match','data-none'}

def normalize_stories_data(soup, context):
    if context.get('family') != FAMILY or context.get('lang') not in ('ar','fr','es','pt','it','de','pl','ru','hi','th','zh-Hans') or context.get('side') not in ('en','locale') or context.get('masterSha256') != MASTER_SHA256:
        raise ValueError('Stories copy normalizer requires exact family, language, master and side context')
    root = Path(__file__).resolve().parents[2]
    contract_path = root / 'locales/en/stories-master-bindings.json'
    english_path = root / 'locales/en/stories-master-copy.json'
    if hashlib.sha256(contract_path.read_bytes()).hexdigest() != CONTRACT_SHA256 or hashlib.sha256(english_path.read_bytes()).hexdigest() != ENGLISH_COPY_SHA256:
        raise ValueError('Stories trusted contract or English copy changed')
    contract = read_json(contract_path)
    raw = (root / contract['master']).read_bytes()
    if contract['master'] != 'templates/masters/stories.html' or contract['masterSha256'] != MASTER_SHA256 or hashlib.sha256(raw).hexdigest() != MASTER_SHA256:
        raise ValueError('Stories trusted master changed')
    english = read_json(english_path)
    copy = english if context['side'] == 'en' else read_json(root / f'locales/{context["lang"]}/stories-master-copy.json')
    if set(copy) != set(english) or len(copy) != 194:
        raise ValueError('Stories copy key set changed')
    for key,value in copy.items():
        if not isinstance(value,str) or not value.strip() or re.search(r'<\s*/?\s*[A-Za-z!]',value) or set(re.findall(r'\{([A-Za-z]+)\}',value)) != set(re.findall(r'\{([A-Za-z]+)\}',english[key])):
            raise ValueError('Unsafe or placeholder-drifted Stories copy')
    source = BeautifulSoup(raw, 'html.parser')
    bindings = [b for b in contract['bindings'] if b['kind'] == 'attribute' and b['attribute'] in DATA_COPY]
    if Counter(b['attribute'] for b in bindings) != Counter({'data-keywords':19,'data-one':1,'data-many':1,'data-match':1,'data-none':1}):
        raise ValueError('Stories exact data-copy set changed')
    pending=[]; seen=set()
    for binding in bindings:
        selector,attr = binding['selector'],binding['attribute']
        nodes,originals = soup.select(selector),source.select(selector)
        if len(nodes)!=1 or len(originals)!=1 or not nodes[0].find_parent('main'):
            raise ValueError('Missing, duplicate or misplaced Stories copy target')
        node,original = nodes[0],originals[0]
        if attr=='data-keywords' and (node.name!='article' or 'promo-card' not in node.get('class',[])) or attr!='data-keywords' and not node.has_attr('data-shelf-tools'):
            raise ValueError('Wrong Stories data-copy target kind')
        identity=(id(node),attr)
        if identity in seen or original.get(attr)!=binding['source'] or node.get(attr)!=copy[binding['key']]:
            raise ValueError('Stories source/catalog/target data-copy mismatch')
        seen.add(identity);pending.append((node,attr,binding['source']))
    for node,attr,value in pending:node[attr]=value
    return soup
