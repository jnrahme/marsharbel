#!/usr/bin/env python3
"""Build the dated homepage saint unit from reviewed data, never guess today's feast."""
import argparse,html,json,re
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def output(root=ROOT):
    manifest=json.loads((root/'locales/saint-of-day.json').read_text())
    selected=manifest['activeDate']; date.fromisoformat(selected)
    entry=manifest['entries'][selected]
    copy=json.loads((root/'locales/en/saint-of-day.json').read_text())
    values={**entry,**copy,'date':selected,'calendarUrl':entry['sources'][0]}
    template=(root/'templates/saint-of-day/home.html').read_text()
    card=re.sub(r'\$\{([^}]+)\}',lambda m:html.escape(values[m[1]],quote=True),template)
    path=root/'src/pages/index.html'; source=path.read_text()
    pattern=r'(<!-- saint-of-day:start -->).*?(<!-- saint-of-day:end -->)'
    rendered,n=re.subn(pattern,lambda m:m[1]+'\n'+card+m[2],source,flags=re.S)
    if n!=1:raise ValueError('Expected one saint marker')
    return path,rendered
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
    path,text=output()
    if a.check:
        if path.read_text()!=text:raise SystemExit('Saint of the Day output stale')
    else:path.write_text(text)
    print('Saint of the Day source checked' if a.check else 'Saint of the Day source built')
