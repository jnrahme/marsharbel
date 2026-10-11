"""Reciprocal prayer discovery heads, separate from reviewed content bindings."""
import re, json, hashlib

def compose_prayer_clusters(root, registry, texts, source_inputs=False):
    for family in ('saint-charbel-prayers-master','saint-charbel-novena-master'):
        cfg=registry.get('pageMirrors',{}).get(family)
        if not cfg:continue
        links='\n'.join('<link rel="alternate" hreflang="'+lang+'" href="'+registry['site']+route+'" />' for lang,route in cfg['discoveryRoutes'].items())
        for route in set(cfg['discoveryRoutes'].values()):
            file=root/(route.lstrip('/')+'.html')
            if source_inputs and file not in texts: continue
            # English master and untouched locale outputs come from released
            # bytes, not older prayer-template writers.
            original=file.read_text()
            text=texts.get(file,original) if source_inputs or route in cfg['routes'].values() else original
            end=text.index('</head>');head=re.sub(r'<link\b[^>]*\bhreflang=["\'][^>]*>\s*','',text[:end])
            if family=='saint-charbel-prayers-master' and (route==cfg['english'] or route in cfg['routes'].values()):
                head=re.sub(r'<meta\b(?=[^>]*name=["\']robots["\'])(?=[^>]*content=["\']noindex["\'])[^>]*>\s*','',head)
            # Locale identity belongs to the registry, including preserved English heads.
            # Keep existing alternate membership, but refresh each locale's regional tag.
            for locale in registry['locales'].values():
                value=locale['ogLocale']
                prefix=value.split('_',1)[0]+'_'
                head=re.sub(r'(<meta\b(?=[^>]*property=[\"\']og:locale(?::alternate)?[\"\'])[^>]*content=[\"\'])'+re.escape(prefix)+r'[^\"\']+([\"\'])',lambda m:m.group(1)+value+m.group(2),head)
            from i18n.prayer_runtime import share_head
            text=head+links+'\n'+text[end:]
            if route==cfg['english'] or route in cfg['routes'].values():
                lang=next(c for c,r in cfg['discoveryRoutes'].items()if r==route and c!='x-default')
                text=share_head(text,root,lang,family=='saint-charbel-prayers-master')
            texts[file]=text
        if family=='saint-charbel-prayers-master' and (not source_inputs or root/'en/prayers.html' in texts):
            file=root/'en/prayers.html';text=texts.get(file,file.read_text());end=text.index('</head>');head=re.sub(r'<link\b[^>]*\bhreflang=["\'][^>]*>\s*','',text[:end]);texts[file]=head+'<link rel="alternate" hreflang="en" href="'+registry['site']+'/en/prayers" />\n<link rel="alternate" hreflang="x-default" href="'+registry['site']+'/en/prayers" />\n'+text[end:]
    contract=root/'locales/prayer-metadata-contract.json'
    if contract.exists():
        for file,proof in json.loads(contract.read_text())['files'].items():
            if source_inputs and root/file not in texts: continue
            text=texts.get(root/file,(root/file).read_text())
            body=re.search(r'<main\b[\s\S]*?</main>',text)[0]
            if hashlib.sha256(body.encode()).hexdigest()!=proof['mainSha256']:
                raise ValueError('Prayer metadata refresh changed frozen body: '+file)
    return texts
