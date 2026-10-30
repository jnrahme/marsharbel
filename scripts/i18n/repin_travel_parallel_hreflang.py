"""Thirteen ZH/TH source-master pins, isolated correct RU hreflang only.
Independent executor: check first, review raw table, then write. No copy/review edits.
"""
import argparse
import importlib.util
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('ru_repin',ROOT/'scripts/i18n/repin_ru_travel_release.py')
tools=importlib.util.module_from_spec(spec);spec.loader.exec_module(tools)
FAMILIES={slug+'-zh-travel-master':slug for slug in tools.SLUGS}
FAMILIES['travel-th-travel-master']='travel'


def prepare(root,base):
    if not re.fullmatch(r"[0-9a-f]{40}",base):raise ValueError("Full committed base SHA required")
    updates,rows={},[]
    for family,slug in sorted(FAMILIES.items()):
        file='locales/en/'+family+'-bindings.json'
        raw=tools.blob(root,base,file);prior=json.loads(raw)
        text=(root/file).read_text();current=json.loads(text)
        master=slug+'.html'
        before=tools.blob(root,base,master);after=(root/master).read_bytes()
        tools.hreflang_delta(before,after,'https://marsharbel.com/ru/'+slug)
        old,new=tools.sha(before),tools.sha(after)
        if prior['master']!=master or prior['masterSha256']!=old or current['masterSha256'] not in (old,new):
            raise ValueError('Unknown source pin provenance')
        clean=dict(current);clean['masterSha256']=prior['masterSha256']
        if clean!=prior or tools.pin_text(text,'masterSha256',current['masterSha256'],old).encode()!=raw:
            raise ValueError('Non-pin binding/provenance edit')
        updates[root/file]=tools.pin_text(text,'masterSha256',current['masterSha256'],new)
        rows.append({'file':file,'master':master,'old':old,'new':new,'bodyBefore':tools.main_hash(before),'bodyAfter':tools.main_hash(after)})
        code='th' if family=='travel-th-travel-master' else 'zh-Hans'
        catalog='locales/'+code+'/'+family+'-copy.json'
        if tools.blob(root,base,catalog)!=(root/catalog).read_bytes():raise ValueError('Parallel copy changed')
        for frozen in ('locales/en/'+family+'-copy.json','locales/'+code+'/'+family+'-schema-bindings.json'):
            tracked=__import__('subprocess').check_output(['git','ls-tree','--name-only',base,'--',frozen],cwd=root).strip()
            if tracked and (not (root/frozen).exists() or tools.blob(root,base,frozen)!=(root/frozen).read_bytes()):
                raise ValueError('Parallel source/schema catalog changed')
            if not tracked and (root/frozen).exists():raise ValueError('New parallel source/schema catalog')
    # All preexisting provenance/review/release records are frozen; no arbitrary
    # recursive hash replacement and no addition of parallel exact group records.
    for file in ('locales/travel-equivalence.json','locales/history-equivalence.json','locales/prayer-equivalence.json'):
        if tools.blob(root,base,file)!=(root/file).read_bytes():raise ValueError('Equivalence record changed')
    release=root/'locales/travel-release.json'
    if release.exists() and tools.blob(root,base,'locales/travel-release.json')!=release.read_bytes():raise ValueError('Release record changed')
    return updates,rows


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',required=True);p.add_argument('--write',action='store_true');a=p.parse_args()
    updates,rows=prepare(ROOT,a.base)
    print(json.dumps({'mode':'write' if a.write else 'check','parallelSourcePins':rows,'scope':'13 masterSha256 fields only'},indent=2))
    if a.write:
        for file,text in updates.items():
            if file.read_text()!=text:file.write_text(text)
if __name__=='__main__':main()
