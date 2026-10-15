#!/usr/bin/env python3
"""Build the dated homepage saint units from reviewed data, never guess today's feast.

Emits one inert <template data-saint-date> per manifest entry (the window:
today + next N, N<=7 in America/New_York). saint-of-day.js mounts exactly the
unit matching the New York date and fails closed when none matches. --prune
rewrites the manifest dropping entries expired before the New York today; the
pack lane runs it when adding a sourced unit."""
import argparse,html,json,re,sys
from datetime import date,datetime
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.saint_plate import plate_fields
REQUIRED=('saint','calendar','infoUrl','sources','translationStatus')
def load(root):
    manifest=json.loads((root/'locales/saint-of-day.json').read_text())
    entries=manifest['entries']
    for d in entries: date.fromisoformat(d)
    if len(entries)>8: raise ValueError('saint window larger than today + next 7')
    dates=sorted(date.fromisoformat(d) for d in entries)
    if dates and (dates[-1]-dates[0]).days>7: raise ValueError('saint window spans more than 7 days')
    copy=json.loads((root/'locales/en/saint-of-day.json').read_text())
    for d,entry in entries.items():
        missing=[k for k in REQUIRED if not entry.get(k)]
        if missing: raise ValueError(f'saint unit {d} missing sourced fields: {missing}')
        has_url,has_img=bool(entry.get('bookUrl')),bool(entry.get('bookImage'))
        explicit_none='book' in entry and entry['book'] is None
        if has_url!=has_img: raise ValueError(f'saint unit {d} carries only one of bookUrl/bookImage; a book is both or neither')
        if has_url and explicit_none: raise ValueError(f'saint unit {d} contradicts itself: "book": null with bookUrl/bookImage set')
        if not has_url and not explicit_none: raise ValueError(f'saint unit {d} has no book and no explicit "book": null; a missing book is never silent')
        if entry.get('saintImage'):
            if has_url: raise ValueError(f'saint unit {d} carries both a book and saintImage; the photo plate is a solo-card variant')
            if not copy.get(d,{}).get('imageAlt'): raise ValueError(f'saint unit {d} has saintImage but no reviewed English imageAlt')
        if d not in copy: raise ValueError(f'saint unit {d} has no English copy')
    return manifest,copy
def output(root=ROOT):
    manifest,copy=load(root)
    pair=(root/'templates/saint-of-day/home.html').read_text()
    solo=(root/'templates/saint-of-day/home-nobook.html').read_text()
    mono=(root/'templates/saint-of-day/home-nobook-mono.html').read_text()
    image=(root/'templates/saint-of-day/home-nobook-image.html').read_text()
    units=[]
    for d in sorted(manifest['entries']):
        entry=manifest['entries'][d]
        values={**entry,**copy[d],'date':d,'dateLabel':date.fromisoformat(d).strftime('%d.%m.%Y'),'calendarUrl':entry['sources'][0]}
        if entry.get('bookUrl'):
            template=pair
        elif entry.get('saintImage'):
            template=image
        else:
            fields=plate_fields(copy[d].get('name',''),'en',d,override=copy[d].get('monogram'))
            if fields: values.update(fields);template=mono
            else: template=solo
        units.append(re.sub(r'\$\{([^}]+)\}',lambda m:html.escape(values[m[1]],quote=True),template))
    path=root/'src/pages/index.html'; source=path.read_text()
    pattern=r'(<!-- saint-of-day:start -->).*?(<!-- saint-of-day:end -->)'
    rendered,n=re.subn(pattern,lambda m:m[1]+'\n'+'\n'.join(units)+m[2],source,flags=re.S)
    if n!=1:raise ValueError('Expected one saint marker')
    return path,rendered
def prune(root=ROOT):
    path=root/'locales/saint-of-day.json'; manifest=json.loads(path.read_text())
    today=datetime.now(ZoneInfo(manifest['timezone'])).date()
    kept={d:e for d,e in manifest['entries'].items() if date.fromisoformat(d)>=today}
    dropped=sorted(set(manifest['entries'])-set(kept))
    manifest['entries']=kept
    path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    return dropped
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--prune',action='store_true');a=p.parse_args()
    if a.prune:
        print('Pruned expired saint units:',prune() or 'none');raise SystemExit
    path,text=output()
    if a.check:
        if path.read_text()!=text:raise SystemExit('Saint of the Day output stale')
    else:path.write_text(text)
    print('Saint of the Day source checked' if a.check else 'Saint of the Day source built')
