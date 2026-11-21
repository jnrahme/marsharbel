#!/usr/bin/env python3
"""Build the dated Saint of the Day archive list from reviewed data, never guess dates.

Renders one archive row per manifest entry into src/pages/saint-of-the-day.html
between the i18n-saint-day-archive markers, from the same manifest and English
pack that build_saint_of_day.py uses. --check fails when the block is stale."""
import argparse,html,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from datetime import date

def render_block(root=ROOT):
    manifest=json.loads((root/'locales/saint-of-day.json').read_text())
    copy=json.loads((root/'locales/en/saint-of-day.json').read_text())
    dates=sorted(manifest['entries'])
    if set(copy)!=set(dates): raise ValueError('English saint copy dates differ from manifest')
    rows=[]
    for d in dates:
        entry=manifest['entries'][d]; pack=copy[d]
        label=date.fromisoformat(d).strftime('%d.%m.%Y')
        esc=html.escape
        rows.append(f'''          <li>
            <article class="news-row update reveal" id="saint-day-{d}">
              <p class="news-lead-kicker"><time datetime="{d}">{label}</time> <span class="news-meta">{esc(pack["calendar"])}</span></p>
              <h3 class="news-lead-title"><a href="{esc(entry["infoUrl"])}">{esc(pack["name"])}</a></h3>
              <p class="news-lead-summary">{esc(pack["story"])}</p>
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
    path,text=output()
    if a.check:
        if path.read_text()!=text: raise SystemExit('Saint of the Day archive output stale')
    else: path.write_text(text)
    print('Saint of the Day archive source checked' if a.check else 'Saint of the Day archive source built')
