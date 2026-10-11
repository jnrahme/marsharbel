"""AUTHOR ONLY: unreviewed render preparation, not build/QA or review pins.
Writes labeled snapshots outside repo; NEVER imported by production or CI.
Executor must compare pre-boundary bytes to owning build before committing pages.
"""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.page_mirror import render_page
from i18n.travel_metadata import compose_travel_clusters
from i18n.runtime_labels import ensure_runtime_labels
from i18n.same_page_injection import inject_control
FAMILIES={'de':'annaya-tour-travel-master','ru':'annaya-tour-travel-master','zh-Hans':'annaya-tour-zh-travel-master'}
def snapshot(root,destination):
    destination=destination.resolve()
    if destination==root.resolve() or root.resolve() in destination.parents:raise ValueError('Snapshots must be outside gated repository')
    destination.mkdir(parents=True,exist_ok=True)
    registry=json.loads((root/'locales/registry.json').read_text())
    manifest=json.loads((root/'locales/same-page-manifest.pending.json').read_text())
    copy=json.loads((root/'locales/same-page-copy.json').read_text())
    report={'status':'UNREVIEWED','qaPass':False,'warning':'Preparation only. Frozen pending manifest, not approved release overlay. Diff pre-boundary against owning producer before committing any candidate bytes. Never use these files as review pins.','snapshots':[]}
    english=(root/'annaya-tour.html').read_text()
    (destination/'UNREVIEWED-en-PREBOUNDARY-annaya-tour.html').write_text('<!-- UNREVIEWED AUTHOR SNAPSHOT - NOT QA OR APPROVED CANDIDATE -->\n'+english)
    report['snapshots'].append({'file':'UNREVIEWED-en-PREBOUNDARY-annaya-tour.html','family':'annaya-tour-travel-master','boundary':'PREBOUNDARY'})
    for code,family in FAMILIES.items():
        route=registry['pageMirrors'][family]['routes'][code]
        text=render_page(root,registry,code,family,route)
        # Strict keyed pages skip travel_frame in the owning builder.
        path=root/(route.lstrip('/')+'.html')
        text=compose_travel_clusters(root,registry,{path:text})[path]
        text=ensure_runtime_labels(text,root,code,registry)
        for boundary,value in [('PREBOUNDARY',text),('CONTROL-PREVIEW',inject_control(text,root,manifest,copy))]:
            # Labeled comments deliberately prevent these files matching a pin.
            name=f'UNREVIEWED-{code}-{boundary}-annaya-tour.html'
            (destination/name).write_text('<!-- UNREVIEWED AUTHOR SNAPSHOT - NOT QA OR APPROVED CANDIDATE -->\n'+value)
            report['snapshots'].append({'file':name,'family':family,'boundary':boundary})
    (destination/'UNREVIEWED-annaya-snapshot-report.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output-dir',required=True);args=parser.parse_args()
    print(json.dumps(snapshot(ROOT,Path(args.output_dir)),indent=2))
