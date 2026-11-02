"""Targeted controls for scripts/i18n/citation_history.py (reviewed C2 hydration).

Fixture strategy: a bare repo carrying ONLY the candidate head's reachable history -
the reviewed base B is present, the unadvertised candidate commit C2 is absent, exactly
like a fresh native checkout (audit: clean native-only git misses C2 before hydration).
Cloning the working repo would be contaminated by local-only branches that carry C2.
The bare is fetched INTO (not pushed to) so a shallow candidate checkout also works.

Full-proof integration on a native-only checkout is covered by the existing C1 control
(scripts/qa/check_citation_amendment.py) wherever the checkout genuinely lacks C2;
these controls pin the loader's own contract: identity, integrity, no-mutation,
no-arbitrary-import, and independent rehydration across clone generations.

Clone budget: object-mutating clones use --no-hardlinks and one clone is reused across
the artifact-tamper cases with a byte-exact restore between cases (the artifact content
is hash-pinned, so a restored file is provably the committed one).
"""
import hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from i18n import citation_amendment as ca
from i18n import citation_history as ch

RESULTS=[]
def record(name,ok,detail=''):
    RESULTS.append((name,ok,detail))
    print(('PASS' if ok else 'FAIL')+' '+name+(' :: '+detail if detail else ''),flush=True)

def expect_reject(name,branch,fn):
    try:
        fn();record(name,False,'tampered state was ACCEPTED')
    except ValueError as e:
        if branch in str(e):record(name,True,str(e)[:120])
        else:record(name,False,'rejected on WRONG branch: '+str(e)[:140])
    except Exception as e:
        record(name,False,'wrong exception type '+type(e).__name__+': '+str(e)[:120])

ROOT=str(Path(__file__).resolve().parents[2])
BARE=None

def _git(d,*a):
    return subprocess.run(['git','-C',d]+list(a),capture_output=True,text=True).stdout.strip()

def has_obj(d,rev):
    return subprocess.run(['git','-C',d,'cat-file','-t',rev],capture_output=True).returncode==0

def native_only():
    """Fresh clone of the reviewed head lineage: B present, C2 absent (pre-state asserted)."""
    tmp=tempfile.mkdtemp(prefix='cithist-')
    subprocess.run(['git','clone','--no-hardlinks','--quiet','file://'+BARE,tmp],check=True)
    if not has_obj(tmp,ch.REVIEWED_B):raise RuntimeError('fixture broken: reviewed base B absent from native-only clone')
    if has_obj(tmp,ch.REVIEWED_C):raise RuntimeError('fixture broken: C2 already present in native-only clone')
    return tmp

def restore(d):
    """Byte-exact restore of proof-input files a case may have mutated/removed/linked."""
    subprocess.run(['git','-C',d,'checkout','--',ch.ARTIFACT,ca.SIDECAR],check=True)
    ok=hashlib.sha256((Path(d)/ch.ARTIFACT).read_bytes()).hexdigest()==ch.ARTIFACT_SHA256
    if not ok:raise RuntimeError('restore failed: artifact hash != pin')

def setup_bare():
    global BARE
    d=tempfile.mkdtemp(prefix='cithist-bare-');BARE=os.path.join(d,'r.git')
    subprocess.run(['git','init','--bare','--quiet','-b','main',BARE],check=True)
    r=subprocess.run(['git','--git-dir',BARE,'fetch','--quiet',ROOT,'HEAD:refs/heads/main'],capture_output=True,text=True)
    if r.returncode!=0:raise RuntimeError('fixture setup fetch failed: '+r.stderr[:200])
    head=subprocess.check_output(['git','-C',ROOT,'rev-parse','HEAD']).decode().strip()
    bare_head=subprocess.check_output(['git','--git-dir',BARE,'rev-parse','HEAD']).decode().strip()
    if head!=bare_head:raise RuntimeError('fixture broken: bare head != candidate head')
    if subprocess.run(['git','--git-dir',BARE,'cat-file','-t',ch.REVIEWED_C],capture_output=True).returncode==0:
        raise RuntimeError('fixture broken: C2 reachable from candidate head')

def run(record,expect_reject):
    """Execute the hydration controls, reporting into the caller's recorders.

    Called standalone by main() and natively by check_citation_amendment.py, so the
    citation step executes these controls under the SAME inventory command: no new
    slot, no displacement, and the step's measured duration honestly covers both
    suites. Fixture discipline is identical on both paths."""
    setup_bare()
    s=ca.load(ROOT)
    if not s:
        record('N0 sidecar present at root',False,'no sidecar; nothing to control')
        return

    # One cold clone carries the artifact-tamper cases first (C2 still absent), then the
    # positive hydration, then the warm-store tamper case.
    d=native_only()
    try:
        def tampered(name,branch,mutate):
            p=Path(d)/ch.ARTIFACT;raw=p.read_bytes();mutate(p,raw)
            expect_reject(name,branch,lambda:ch.ensure_history(d,ca.load(d)))
            record(name+' :: no import on failure',not has_obj(d,ch.REVIEWED_C))
            restore(d)
        tampered('N2 mutated artifact text rejected','text sha256 mismatch',
                 lambda p,raw:p.write_bytes(raw[:200]+(b'A' if raw[200:201]!=b'A' else b'B')+raw[201:]))
        tampered('N3 missing artifact rejected','artifact: missing',lambda p,raw:p.unlink())
        tampered('N4 truncated artifact rejected','citation history artifact:',lambda p,raw:p.write_bytes(raw[:-77]))
        tampered('N5 non-base64 artifact rejected','citation history artifact:',
                 lambda p,raw:p.write_bytes(raw[:100]+b'!'+raw[101:]))
        def to_symlink(p,raw):
            p.unlink();os.symlink('/etc/hostname',str(p))
        tampered('N6 symlink artifact rejected','not a regular file',to_symlink)

        # N1 positive: hydration imports EXACTLY the reviewed graph.
        sd=ca.load(d)
        ok=ch.ensure_history(d,sd) is True
        ok=ok and _git(d,'rev-parse',ch.REVIEWED_C+'^')==ch.REVIEWED_B
        ok=ok and _git(d,'rev-parse',ch.REVIEWED_C+'^{tree}')==ch.REVIEWED_TREE
        tab=json.loads((Path(d)/sd['table']['path']).read_bytes())
        finite=sorted({e['path'] for e in tab}|{e['file'] for e in sd['derivedPins']})
        changed=sorted(_git(d,'diff','--name-only',ch.REVIEWED_B,ch.REVIEWED_C).split('\n'))
        ok=ok and changed==finite and len(changed)==44
        ok=ok and all(_git(d,'rev-parse',ch.REVIEWED_C+':'+f)==_git(d,'rev-parse','HEAD:'+f) for f in finite)
        record('N1 native-only hydration yields exact reviewed C2 graph',ok,'changed files: '+str(len(changed)))

        # N11 warm object store never masks artifact tampering (hydrated above).
        p=Path(d)/ch.ARTIFACT;raw=p.read_bytes()
        p.write_bytes(raw[:200]+(b'A' if raw[200:201]!=b'A' else b'B')+raw[201:])
        expect_reject('N11 warm odb + tampered artifact still rejected','text sha256 mismatch',lambda:ch.ensure_history(d,ca.load(d)))
        restore(d)
    finally:shutil.rmtree(d,ignore_errors=True)

    # N7 non-reviewed sidecar binding: NO import, NO error; the proof's own branch judges.
    d=native_only()
    try:
        sd=ca.load(d);sd['candidate']={'commit':'0'*40,'tree':'0'*40}
        r=ch.ensure_history(d,sd)
        record('N7 non-reviewed binding imports nothing',r is False and not has_obj(d,ch.REVIEWED_C))
        sp=Path(d)/ca.SIDECAR;sp.write_text(json.dumps(sd,indent=1,ensure_ascii=False))
        expect_reject('N7b non-reviewed binding judged by proof itself','missing objects',lambda:ca.prove(d))
    finally:shutil.rmtree(d,ignore_errors=True)

    # N8 stripped object store (base also absent) fails closed on the missing-objects branch.
    d=native_only()
    try:
        objdir=Path(d)/'.git'/'objects'
        for child in objdir.iterdir():
            if child.is_dir():shutil.rmtree(child)
            else:child.unlink()
        expect_reject('N8 stripped objects fail closed','missing objects',lambda:ch.ensure_history(d,ca.load(d)))
    finally:shutil.rmtree(d,ignore_errors=True)

    # N9 the import path mutates NOTHING but the object store (cold clone).
    d=native_only()
    try:
        snap=lambda:(_git(d,'for-each-ref'),_git(d,'rev-parse','HEAD'),
                     _git(d,'status','--porcelain'),
                     hashlib.sha256((Path(d)/'.git'/'index').read_bytes()).hexdigest(),
                     _git(d,'remote','-v'),(Path(d)/'.git'/'FETCH_HEAD').exists(),
                     hashlib.sha256((Path(d)/ca.SIDECAR).read_bytes()).hexdigest(),
                     hashlib.sha256((Path(d)/ch.ARTIFACT).read_bytes()).hexdigest())
        before=snap();ch.ensure_history(d,ca.load(d));after=snap()
        record('N9 hydration touches no refs/index/worktree/remote/input bytes',before==after and has_obj(d,ch.REVIEWED_C))
    except Exception as e:
        record('N9 hydration touches no refs/index/worktree/remote/input bytes',False,type(e).__name__+': '+str(e)[:160])
    finally:shutil.rmtree(d,ignore_errors=True)

    # N10 clone-of-clone: imported C2 is unreachable, so a second-generation clone again
    # lacks it and rehydrates independently from the committed artifact alone.
    d1=native_only()
    try:
        ch.ensure_history(d1,ca.load(d1))
        d2=tempfile.mkdtemp(prefix='cithist-gen2-')
        try:
            subprocess.run(['git','clone','--no-hardlinks','--quiet','file://'+d1,d2],check=True)
            gen2_clean=not has_obj(d2,ch.REVIEWED_C)
            ok=ch.ensure_history(d2,ca.load(d2)) is True and _git(d2,'rev-parse',ch.REVIEWED_C+'^{tree}')==ch.REVIEWED_TREE
            record('N10 second-generation clone rehydrates independently',gen2_clean and ok)
        finally:shutil.rmtree(d2,ignore_errors=True)
    except Exception as e:
        record('N10 second-generation clone rehydrates independently',False,type(e).__name__+': '+str(e)[:160])
    finally:shutil.rmtree(d1,ignore_errors=True)

    shutil.rmtree(os.path.dirname(BARE),ignore_errors=True)

def main():
    run(record,expect_reject)
    print()
    fails=[n for n,ok,_ in RESULTS if not ok]
    print(f'{len(RESULTS)-len(fails)}/{len(RESULTS)} controls pass'+('' if not fails else ' — FAILURES: '+','.join(fails)))
    return 1 if fails else 0

if __name__=='__main__':sys.exit(main())
