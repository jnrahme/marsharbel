#!/usr/bin/env python3
"""Re-pin the frozen authored full-file hashes after a header-marking PR, with proof.

For every file in the fixture: render the current tree, strip ONLY the English-destination
header marking (scripts/i18n/header_marking_delta.py, strict inverse), and require the
stripped bytes to hash to the CURRENT fixture value. Only then write the new rendered
hash. Any other drift aborts with no write. Updates the sha pin constant in the test.
Allowed delta per file: route_nav_hrefs(frozen stage bytes) with or without the stripped marking.
Usage: python3 scripts/qa/repin_authored_final_hashes.py [--write]
"""
import hashlib,json,re,sys,importlib.util,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
try:
    from i18n.header_marking_delta import strip_for_locale  # merged with the pinned-page marking PR (#782)
except ImportError:
    def strip_for_locale(root,code,text):return text  # no marking strip available: only routing deltas pass
from i18n.encyclopedia_nav import route_nav_hrefs, strip_legacy_partial_nav_marks
FIX=ROOT/'scripts/qa/fixtures/travel-authored-heads-f6e0d947.json';TEST=ROOT/'scripts/qa/test_travel_authored_final_hashes.py'
sha=lambda t:hashlib.sha256(t.encode()).hexdigest()
spec=importlib.util.spec_from_file_location('b',ROOT/'scripts/build-international.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
final=b.outputs();raw=FIX.read_bytes();data=json.loads(raw)
changed=[];bad=[]
for file,row in data['files'].items():
    code=file.split('/')[0] if '/' in file else 'en'
    new=final[ROOT/file]
    if sha(new)==row['fileSha256']:continue
    # Frozen bytes cannot be recovered from git by hash, so re-derive the expected bytes:
    # the frozen file is the stage render; allowed delta = real twin routing (route_nav_hrefs)
    # plus exact English-destination marking (stripped). Both touch <header> anchors only.
    old=subprocess.run(['git','show','origin/stage:'+file],capture_output=True,cwd=ROOT).stdout.decode()
    if sha(old)!=row['fileSha256']:bad.append(file+' (origin/stage bytes != frozen hash)');continue
    # Legacy partial marks (hreflang+aria-label without the visible span, plus
    # stray spans after </a>) block twin routing, so the allowed delta starts
    # from the same strip the pipeline applies (check_i18n_policy.py chain):
    # strip partials -> real twin routing -> exact English-destination marking
    # (stripped). All three touch <header> anchors only.
    expected=route_nav_hrefs(strip_legacy_partial_nav_marks(old,ROOT,code),ROOT,code)
    if sha(strip_for_locale(ROOT,code,new))==sha(expected):changed.append((file,row['fileSha256'],sha(new)))
    else:bad.append(file)
for f,o,n in changed:print('ROUTING-OR-MARKING-ONLY',f,o[:12],'->',n[:12])
for f in bad:print('REJECTED (non-marking drift)',f)
if bad:sys.exit(1)
if '--write' in sys.argv and changed:
    text=raw.decode()
    for f,o,n in changed:
        assert text.count(o)==1;text=text.replace(o,n)
    FIX.write_text(text)
    t=TEST.read_text();old=hashlib.sha256(raw).hexdigest();assert t.count(old)==1
    TEST.write_text(t.replace(old,hashlib.sha256(text.encode()).hexdigest()))
    print('written',len(changed))
