#!/usr/bin/env python3
"""Render the independently researched English Eucharistic collection from its locale catalog.
Other locale mirrors are built by the international lane using equivalent catalogs.
"""
from pathlib import Path
from html import escape as e
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
from i18n.metadata import published_locales
REGISTRY = json.loads((ROOT / 'locales/registry.json').read_text())
C = json.loads((ROOT / 'locales/en/eucharistic-miracles.json').read_text())
H, STORIES = C['hub'], C['stories']
DEST = ROOT / 'miracles/eucharistic'
DEST.mkdir(parents=True, exist_ok=True)
SOURCE = (ROOT/'miracles/index.html').read_text()
NAV = (ROOT/'partials/primary-navigation.html').read_text().strip().replace('href="./', 'href="../../')
# The hub and its stories remain children of Miracles in the shared navigation.
NAV = NAV.replace('class="nav-parent" href="../../miracles/"', 'class="active nav-parent" href="../../miracles/"')
HEADER = SOURCE[SOURCE.index('  <header class="topbar">'):SOURCE.index('  </header>') + len('  </header>')]
import re
HEADER = HEADER.replace('href="../', 'href="../../')
HEADER = re.sub(r'<nav\b[^>]*class="links"[^>]*>[\s\S]*?</nav>', lambda _: NAV, HEADER)
FOOTER = '<footer class="footer"><div class="site-shell">'+e(H['note'])+'</div></footer>'


def head(title, desc, url, image, bread):
    schema = {'@context':'https://schema.org','@type':'Article' if len(bread)>3 else 'CollectionPage',
              'headline': title,'description':desc,'url':url,'image':image,
              'author':{'@type':'Organization','name':'marsharbel.com','url':'https://marsharbel.com/'},
              'datePublished':'2026-09-29' if url.endswith(('/legnica', '/amsterdam', '/ivorra', '/faverney')) else '2026-09-28','dateModified':'2026-09-29',
              'breadcrumb':{'@type':'BreadcrumbList','itemListElement':[
                  {'@type':'ListItem','position':i+1,'name':name,'item':link}
                  for i,(name,link) in enumerate(bread)]}}
    data=json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')
    alternates = ''.join(f'<link rel="alternate" hreflang="{lang}" href="https://marsharbel.com{("/"+lang) if lang != "en" else ""}/miracles/eucharistic/{url.split("/miracles/eucharistic/",1)[1]}">' for lang in published_locales(REGISTRY, 'eucharistic'))
    alternates += f'<link rel="alternate" hreflang="x-default" href="{url}">'
    return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><!-- Google tag (gtag.js) -->
<script defer src="/analytics-init.js"></script><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} | Saint Charbel</title><meta name="description" content="{e(desc,quote=True)}">
<meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="{e(url,quote=True)}">{alternates}
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

cards='\n'.join(f'''<a class="euch-card" href="./{key}"><span class="euch-card-photo">{img(s)}</span><span class="euch-card-copy"><small>{e(s['place'])} · {e(s['era'])}</small><strong>{e(s['title'])}</strong><span>{e(s['lead'])}</span><em>{e(H['browse'])} &rarr;</em></span></a>''' for key,s in STORIES.items())
filters=''.join(f'<a href="#story-{e(k)}">{e(s["place"])}</a>' for k,s in STORIES.items())
card_rows=''.join(f'<div id="story-{e(k)}" data-country="{e(s["place"].split(", ")[-1],quote=True)}">'+card+'</div>' for (k,s),card in zip(STORIES.items(),cards.split('\n')))
hub=f'''{head(H['title'],H['intro'],BASE,'https://marsharbel.com/media/eucharistic-miracles/lanciano.webp', BREAD+[(H['title'],BASE)])}<a class="skip-link" href="#main-content">Skip to main content</a>{HEADER}
<main id="main-content" class="euch-shell" tabindex="-1">
<section class="euch-hero"><div class="euch-hero-art" aria-hidden="true"></div><div class="euch-hero-content"><p class="euch-eyebrow">{e(H['eyebrow'])}</p><h1>{e(H['title'])}</h1><p class="euch-lead">{e(H['intro'])}</p><a class="euch-action" href="#journey">{e(H['atlasTitle'])} <span aria-hidden="true">↓</span></a></div><span class="euch-hero-caption">{e(STORIES['lanciano']['alt'])} · <a href="{e(STORIES['lanciano']['photo'],quote=True)}">{e(STORIES['lanciano']['credit'])}</a>, <a href="{e(STORIES['lanciano']['licenseurl'],quote=True)}">{e(STORIES['lanciano']['license'])}</a></span></section>
<section class="euch-intro"><div><p class="euch-eyebrow">{e(H['eyebrow'])}</p><h2>{e(H['carloTitle'])}</h2></div><p>{e(H['carloText'])} <a href="https://www.carloacutis.com/en/association/mostra-miracoli-eucaristici">{e(H['carloSource'])}</a> · <a href="https://press.vatican.va/content/salastampa/en/bollettino/pubblico/2025/09/07/250907a.html">{e(H['canonizationSource'])}</a></p></section>
<section id="journey" class="euch-journey"><div class="euch-heading"><p class="euch-eyebrow">01 / {len(STORIES):02d}</p><h2>{e(H['atlasTitle'])}</h2></div><div class="euch-filter" role="group" aria-label="{e(H['filterLabel'],quote=True)}"><button type="button" data-filter="all" aria-pressed="true">{e(H['filterAll'])}</button><button type="button" data-filter="Italy" aria-pressed="false">{e(H['filterItaly'])}</button><button type="button" data-filter="Portugal" aria-pressed="false">{e(H['filterPortugal'])}</button><button type="button" data-filter="Poland" aria-pressed="false">{e(H['filterPoland'])}</button><button type="button" data-filter="Croatia" aria-pressed="false">{e(H['filterCroatia'])}</button><button type="button" data-filter="Netherlands" aria-pressed="false">{e(H['filterNetherlands'])}</button><button type="button" data-filter="Spain" aria-pressed="false">{e(H['filterSpain'])}</button><button type="button" data-filter="France" aria-pressed="false">{e(H['filterFrance'])}</button></div><nav class="euch-places" aria-label="{e(H['atlasTitle'],quote=True)}">{filters}</nav><p class="euch-empty" hidden>{e(H['noFilterResults'])}</p><div class="euch-grid">{card_rows}</div></section>
<section class="euch-method"><p class="euch-eyebrow">{e(H['updated'])}</p><h2>{e(H['methodTitle'])}</h2><p>{e(H['methodText'])}</p><p class="euch-fine">{e(H['note'])}</p></section>
</main>{FOOTER}{scripts()}</body></html>'''
outputs = {DEST/'index.html': hub}

for key,s in STORIES.items():
    title=s['title'];url=BASE+key;image='https://marsharbel.com/media/eucharistic-miracles/'+s['image']
    further_source = f'<p><a href="{e(s["source2"],quote=True)}">{e(s["source2Label"])}</a></p>' if s.get('source2') else ''
    sections=''.join(f'<section class="euch-chapter"><p class="euch-eyebrow">0{i}</p><h2>{e(t)}</h2><p>{e(text)}</p></section>' for i,(t,text) in enumerate(s['sections'],1))
    story=f'''{head(title,s.get('description') or s['lead'],url,image,BREAD+[(H['title'],BASE),(title,url)])}<a class="skip-link" href="#main-content">Skip to main content</a>{HEADER}
<main id="main-content" class="euch-shell euch-story" tabindex="-1"><a href="./" class="euch-back">← {e(H['back'])}</a><header class="euch-story-head"><p class="euch-eyebrow">{e(s['label'])} · {e(s['place'])} · {e(s['era'])}</p><h1>{e(title)}</h1><p class="euch-lead">{e(s['lead'])}</p></header>
<figure class="euch-feature-photo">{img(s,True)}<figcaption>{e(s['alt'])}. {e(H['photo'])}: {e(s['credit'])}, <a href="{e(s['licenseurl'],quote=True)}">{e(s['license'])}</a>; resized to WebP for this site. <a href="{e(s['photo'],quote=True)}">{e(H['originalPhoto'])}</a>.</figcaption></figure>
<div class="euch-story-body">{sections}<aside class="euch-reflection"><h2>{e(H['reflection'])}</h2><p>{e(s['reflection'])}</p></aside><section class="euch-sources"><h2>{e(H['sources'])}</h2><p><a href="{e(s['source'],quote=True)}">{e(s['sourceLabel'])}</a></p>{further_source}<p>{e(H['updated'])}. {e(H['note'])}</p></section><a href="./" class="euch-back">← {e(H['back'])}</a></div></main>{FOOTER}{scripts()}</body></html>'''
    outputs[DEST/(key+'.html')] = story
from i18n.same_page_injection import control_outputs
outputs.update(control_outputs(ROOT,outputs,json.loads((ROOT/'locales/same-page-manifest.pending.json').read_text()),json.loads((ROOT/'locales/same-page-copy.json').read_text())))
if '--check' in sys.argv:
    stale=[str(path.relative_to(ROOT)) for path, rendered in outputs.items() if not path.exists() or path.read_text()!=rendered]
    if stale: raise SystemExit('Stale Eucharistic pages: '+', '.join(stale))
    print('Eucharistic English collection current: all pages match catalog.')
else:
    for path, rendered in outputs.items(): path.write_text(rendered)
    print(f'Rendered English Eucharistic hub and {len(STORIES)} stories')
