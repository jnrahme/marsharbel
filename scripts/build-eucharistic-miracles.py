#!/usr/bin/env python3
"""Render the independently researched English Eucharistic collection from its locale catalog.
Other locale mirrors are built by the international lane using equivalent catalogs.
"""
from pathlib import Path
from html import escape as e
import json

ROOT = Path(__file__).resolve().parents[1]
C = json.loads((ROOT / 'locales/en/eucharistic-miracles.json').read_text())
H, STORIES = C['hub'], C['stories']
DEST = ROOT / 'miracles/eucharistic'
DEST.mkdir(parents=True, exist_ok=True)
SOURCE = (ROOT/'miracles/index.html').read_text()
HEADER = SOURCE[SOURCE.index('  <header class="topbar">'):SOURCE.index('  </header>') + len('  </header>')].replace('href="../', 'href="../../')
# The nav sync tool owns the nav markup after render. Preserve other shared controls.
FOOTER = SOURCE[SOURCE.index('  <footer class="footer">'):SOURCE.index('  </footer>') + len('  </footer>')].replace('href="../', 'href="../../')


def head(title, desc, url, image, bread):
    schema = {'@context':'https://schema.org','@type':'Article' if len(bread)>2 else 'CollectionPage',
              'headline': title,'description':desc,'url':url,'image':image,
              'author':{'@type':'Organization','name':'marsharbel.com','url':'https://marsharbel.com/'},
              'datePublished':'2026-09-28','dateModified':'2026-09-28',
              'breadcrumb':{'@type':'BreadcrumbList','itemListElement':[
                  {'@type':'ListItem','position':i+1,'name':name,'item':link}
                  for i,(name,link) in enumerate(bread)]}}
    data=json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')
    return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} | Saint Charbel</title><meta name="description" content="{e(desc,quote=True)}">
<meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="{e(url,quote=True)}">
<meta property="og:type" content="article"><meta property="og:site_name" content="Saint Charbel"><meta property="og:title" content="{e(title,quote=True)}"><meta property="og:description" content="{e(desc,quote=True)}"><meta property="og:url" content="{e(url,quote=True)}"><meta property="og:image" content="{e(image,quote=True)}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title,quote=True)}"><meta name="twitter:description" content="{e(desc,quote=True)}"><meta name="twitter:image" content="{e(image,quote=True)}">
<script type="application/ld+json">{data}</script>
<link rel="stylesheet" href="../../styles.css?v=20260922-1"><link rel="stylesheet" href="../../eucharistic.css?v=20260928-1">
</head><body class="eucharistic-world">
'''

BASE='https://marsharbel.com/miracles/eucharistic/'
BREAD=[('Home','https://marsharbel.com/'),('Miracles','https://marsharbel.com/miracles/')]

def img(s, eager=False):
    src='../../media/eucharistic-miracles/'+s['image']
    return f'<img src="{e(src,quote=True)}" alt="{e(s["alt"],quote=True)}" loading="{"eager" if eager else "lazy"}" decoding="async" width="1200" height="800">'

def scripts():
    return '''<script defer src="../../app.js"></script><script defer src="../../global-audio-player.js"></script><script defer src="/locale-routes.js"></script><script defer src="../../translate.js?v=20260922-1"></script><script src="../../nav.js?v=20260922-1" defer></script><script defer src="../../eucharistic.js?v=20260928-1"></script>'''

cards='\n'.join(f'''<a class="euch-card" href="./eucharistic/{key}"><span class="euch-card-photo">{img(s)}</span><span class="euch-card-copy"><small>{e(s['place'])} · {e(s['era'])}</small><strong>{e(s['title'])}</strong><span>{e(s['lead'])}</span><em>{e(H['browse'])} &rarr;</em></span></a>''' for key,s in STORIES.items())
# We serve the index file at /miracles/eucharistic/; from that directory its story links are ./slug, not ./eucharistic/slug.
cards=cards.replace('href="./eucharistic/','href="./')
filters=''.join(f'<a href="#story-{e(k)}">{e(s["place"])}</a>' for k,s in STORIES.items())
card_rows=''.join(f'<div id="story-{e(k)}">'+card+'</div>' for (k,s),card in zip(STORIES.items(),cards.split('\n')))
hub=f'''{head(H['title'],H['intro'],BASE,'https://marsharbel.com/media/eucharistic-miracles/lanciano.webp', BREAD+[(H['title'],BASE)])}{HEADER}
<main id="main-content" class="euch-shell">
<section class="euch-hero"><div class="euch-hero-art" aria-hidden="true"></div><div class="euch-hero-content"><p class="euch-eyebrow">{e(H['eyebrow'])}</p><h1>{e(H['title'])}</h1><p class="euch-lead">{e(H['intro'])}</p><a class="euch-action" href="#journey">{e(H['atlasTitle'])} <span aria-hidden="true">↓</span></a></div><span class="euch-hero-caption">{e(STORIES['lanciano']['alt'])} · <a href="{e(STORIES['lanciano']['photo'],quote=True)}">{e(STORIES['lanciano']['credit'])}</a>, <a href="{e(STORIES['lanciano']['licenseurl'],quote=True)}">{e(STORIES['lanciano']['license'])}</a></span></section>
<section class="euch-intro"><div><p class="euch-eyebrow">{e(H['eyebrow'])}</p><h2>{e(H['carloTitle'])}</h2></div><p>{e(H['carloText'])} <a href="https://www.carloacutis.com/en/association/mostra-miracoli-eucaristici">{e(H['source'])}</a></p></section>
<section id="journey" class="euch-journey"><div class="euch-heading"><p class="euch-eyebrow">01 / 05</p><h2>{e(H['atlasTitle'])}</h2></div><nav class="euch-places" aria-label="{e(H['atlasTitle'],quote=True)}">{filters}</nav><div class="euch-grid">{card_rows}</div></section>
<section class="euch-method"><p class="euch-eyebrow">{e(H['updated'])}</p><h2>{e(H['methodTitle'])}</h2><p>{e(H['methodText'])}</p><p class="euch-fine">{e(H['note'])}</p></section>
</main>{FOOTER}{scripts()}</body></html>'''
(DEST/'index.html').write_text(hub)

for key,s in STORIES.items():
    title=s['title'];url=BASE+key;image='https://marsharbel.com/media/eucharistic-miracles/'+s['image']
    sections=''.join(f'<section class="euch-chapter"><p class="euch-eyebrow">0{i}</p><h2>{e(t)}</h2><p>{e(text)}</p></section>' for i,(t,text) in enumerate(s['sections'],1))
    story=f'''{head(title,s['lead'],url,image,BREAD+[(H['title'],BASE),(title,url)])}{HEADER}
<main id="main-content" class="euch-shell euch-story"><a href="./" class="euch-back">← {e(H['back'])}</a><header class="euch-story-head"><p class="euch-eyebrow">{e(s['label'])} · {e(s['place'])} · {e(s['era'])}</p><h1>{e(title)}</h1><p class="euch-lead">{e(s['lead'])}</p></header>
<figure class="euch-feature-photo">{img(s,True)}<figcaption>{e(s['alt'])}. {e(H['photo'])}: {e(s['credit'])}, <a href="{e(s['licenseurl'],quote=True)}">{e(s['license'])}</a>. <a href="{e(s['photo'],quote=True)}">{e(s['photo'])}</a>.</figcaption></figure>
<div class="euch-story-body">{sections}<aside class="euch-reflection"><h2>{e(H['reflection'])}</h2><p>{e(s['reflection'])}</p></aside><section class="euch-sources"><h2>{e(H['sources'])}</h2><p><a href="{e(s['source'],quote=True)}">{e(s['sourceLabel'])}</a></p><p>{e(H['updated'])}. {e(H['note'])}</p></section><a href="./" class="euch-back">← {e(H['back'])}</a></div></main>{FOOTER}{scripts()}</body></html>'''
    (DEST/(key+'.html')).write_text(story)
print('Rendered English Eucharistic hub and five stories')
