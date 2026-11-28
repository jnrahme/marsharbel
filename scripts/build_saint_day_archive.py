#!/usr/bin/env python3
"""Build the dated Saint of the Day archive list from reviewed data, never guess dates.

Renders one archive row per manifest entry into src/pages/saint-of-the-day.html
between the i18n-saint-day-archive markers, from persistent reviewed history, independent of the rolling homepage window. --check fails when the block is stale."""
import argparse,html,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from datetime import date

def merge_daily_history(root=ROOT,check=False):
    """Admit the exact reviewed daily pack before rendering, without deleting history."""
    path=root/'locales/saint-day-archive.json'
    history=json.loads(path.read_text());items=history['entries'];dates=[x['date'] for x in items]
    if len(dates)!=len(set(dates)):raise ValueError('Duplicate archive date')
    by_date={x['date']:x for x in items};manifest=json.loads((root/'locales/saint-of-day.json').read_text())
    langs=json.loads((root/'locales/registry.json').read_text())['homePublicationLocales']
    for d,entry in manifest['entries'].items():
        packs={lang:json.loads((root/f'locales/{lang}/saint-of-day.json').read_text())[d] for lang in langs}
        if d in by_date:
            existing=by_date[d]
            if 'copy' in existing and (existing['entry']!=entry or existing['copy']!=packs):raise ValueError('Daily/archive conflict at '+d)
            continue
        if check:raise ValueError('Daily date not archived: '+d)
        items.append({'date':d,'entry':entry,'copy':packs,'sourceRecovery':'Exact daily-card inputs, automatically retained by build_saint_of_day.py'})
    history['entries']=sorted(items,key=lambda x:x['date'])
    text=json.dumps(history,ensure_ascii=False,indent=2)+'\n'
    if not check and path.read_text()!=text:path.write_text(text)
    return history

def render_block(root=ROOT):
    history=json.loads((root/'locales/saint-day-archive.json').read_text())
    entries=history['entries'];dates=[e['date'] for e in entries]
    if len(dates)!=len(set(dates)):raise ValueError('Duplicate archive date')
    rows=[]
    for item in sorted(entries,key=lambda e:e['date']):
        d=item['date'];date.fromisoformat(d)
        if 'reviewedHtml' in item:
            import hashlib
            if hashlib.sha256(item['reviewedHtml'].encode()).hexdigest()!=item['htmlSha256']:raise ValueError('Historical archive bytes changed')
            rows.append(item['reviewedHtml']);continue
        entry=item['entry'];pack=item['copy']['en'];label=date.fromisoformat(d).strftime('%d.%m.%Y');esc=html.escape
        rows.append(f'''          <li>
            <article class="news-row update reveal" id="saint-day-{d}">
              <p class="news-lead-kicker"><time datetime="{d}">{label}</time> <span class="news-meta">{esc(pack["calendar"])}</span></p>
              <h3 class="news-lead-title"><a href="{esc(entry["infoUrl"])}">{esc(pack["name"])}</a></h3>
              <p class="news-lead-summary">{esc(pack["story"])}</p>
              <p class="news-meta">{esc(pack["provenance"])}</p>
              <a class="news-lead-cta" href="{esc(entry["infoUrl"])}">{esc(pack["infoCta"])}</a>
            </article>
          </li>''')
    return ('<!-- i18n-saint-day-archive:start -->\n        <ul class="news-list">\n'
            + '\n'.join(rows)
            + '\n        </ul>\n<!-- i18n-saint-day-archive:end -->')

def output(root=ROOT):
    path=root/'src/pages/saint-of-the-day.html'
    source=path.read_text()
    pattern=r'(<!-- i18n-saint-day-archive:start -->).*?(<!-- i18n-saint-day-archive:end -->)'
    rendered,n=re.subn(pattern,lambda m: render_block(root),source,flags=re.S)
    if n!=1: raise ValueError('Expected one saint archive marker pair')
    return path,rendered

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
    merge_daily_history(ROOT,check=a.check)
    path,text=output()
    if a.check:
        if path.read_text()!=text: raise SystemExit('Saint of the Day archive output stale')
    else: path.write_text(text)
    print('Saint of the Day archive source checked' if a.check else 'Saint of the Day archive source built')
