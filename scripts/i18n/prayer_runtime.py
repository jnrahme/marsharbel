"""Approved head-runtime addition, separate from frozen prayer body/catalogs."""
import json,re
from bs4 import BeautifulSoup
from i18n.catalog import read_json


def share_head(text,root,lang,hub=False):
    soup=BeautifulSoup(text,'html.parser')
    labels={k:v for k,v in read_json(root/f'locales/{lang}/share.json').items()if k.startswith('share.')}
    english=read_json(root/'locales/en/share.json')
    if set(labels)!=set(english):raise ValueError('Prayer share key mismatch '+lang)
    for key,value in labels.items():
        if not isinstance(value,str)or not value.strip():raise ValueError('Prayer share empty label '+lang)
        if set(re.findall(r'\{([a-z]+)\}',value))!=set(re.findall(r'\{([a-z]+)\}',english[key])):raise ValueError('Prayer share placeholders '+lang+' '+key)
    head_end=text.index('</head>');head=text[:head_end]
    head=re.sub(r'<script\b[^>]*id=["\']sc-share-labels["\'][^>]*>[\s\S]*?</script>\s*','',head)
    config='<script type="application/json" id="sc-share-labels">'+json.dumps(labels,ensure_ascii=False).replace('<','\\u003c')+'</script>\n'
    if hub:
        head=re.sub(r'<script\b[^>]*src=["\'][^"\']*share\.js[^"\']*["\'][^>]*></script>\s*','',head)
        config+='<script defer src="/share.js?v=20261002-share-2"></script>\n'
    return head+config+text[head_end:]
