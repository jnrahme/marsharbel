"""Negative/positive controls for the citation-source-correction amendment mechanism.
Every control must actually fail closed on its NAMED branch: tamper fixtures are COMMITTED
in independent clones so the worktree-fidelity gate passes and the tamper reaches the exact
check it targets; a generic rejection is not accepted as coverage. Heavy: the positive
control runs the full proof incl. the isolated clean-B historical chain (~minutes).
"""
import hashlib, json, os, re, subprocess, sys, tempfile, shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from i18n import citation_amendment as ca

RESULTS=[]
def record(name,ok,detail=''):
    RESULTS.append((name,ok,detail))
    print(('PASS' if ok else 'FAIL')+' '+name+(' :: '+detail if detail else ''))

def expect_reject(name,branch,fn):
    """Reject ONLY via the named branch (substring of the error message)."""
    try:
        fn();record(name,False,'tampered state was ACCEPTED')
    except ValueError as e:
        if branch in str(e):record(name,True,str(e)[:120])
        else:record(name,False,'rejected on WRONG branch: '+str(e)[:140])
    except Exception as e:
        record(name,False,'wrong exception type '+type(e).__name__+': '+str(e)[:120])

def fresh_clone(src):
    tmp=tempfile.mkdtemp(prefix='citqa-')
    subprocess.run(['git','clone','--no-hardlinks','--quiet',f'file://{src}',tmp],check=True)
    return tmp

def commit_all(d,msg):
    subprocess.run(['git','-C',d,'add','-A'],check=True)
    subprocess.run(['git','-C',d,'-c','user.email=qa@local','-c','user.name=qa','commit','--quiet','-m',msg],check=True)
    return subprocess.check_output(['git','-C',d,'rev-parse','HEAD']).decode().strip()

def main():
    root=str(Path(__file__).resolve().parents[2])
    s=ca.load(root)
    if not s:print('FAIL no sidecar at root; nothing to control');return 1
    B=s['base'];C=s['candidate']['commit']

    # C1 positive: full proof on the real root (delta + historical leg, memoized).
    try:
        r=ca.prove(root);record('C1 positive full proof (delta + isolated clean-B chain)',True,'historical commands: '+','.join(c['cmd'][1] for c in r['historicalLeg']['commands']))
    except Exception as e:
        record('C1 positive full proof (delta + isolated clean-B chain)',False,str(e)[:300]);print('aborting fixtures without a passing positive control');return 1

    # C2 pristine-B non-amended regression: no sidecar, passthrough semantics.
    bdir=fresh_clone(root)
    try:
        subprocess.run(['git','-C',bdir,'checkout','--quiet','--detach',B],check=True)
        record('C2 pristine-B load() is None',ca.load(bdir) is None)
        record('C2b pristine-B effective passthrough',ca.effective_body(bdir,'history-master','en','x')=='x' and ca.current_candidate_bytes(bdir,'history-master','en') is None)
    finally:shutil.rmtree(bdir,ignore_errors=True)

    # Committed-mutation fixtures: one independent clone per case so every tamper is
    # committed (W0 fidelity passes) and reaches its NAMED branch.
    def fixture(mutate):
        d=fresh_clone(root)
        sp=Path(d)/ca.SIDECAR;tp=Path(d)/s['table']['path']
        side=json.loads(sp.read_text());tab=json.loads(tp.read_text())
        mutate(d,side,tab)
        sp.write_text(json.dumps(side,indent=1,ensure_ascii=False))
        tp.write_text(json.dumps(tab,indent=1,ensure_ascii=False))
        commit_all(d,'tamper fixture')
        return d,side

    cases=[
      ('C3 sidecar digest not actual candidate bytes','sidecar digest not actual C bytes',
       lambda d,side,tab:side['families']['history-master']['variants']['en'].__setitem__('newBodySha256','0'*64)),
      ('C4 acceptance vocabulary in sidecar','acceptance vocabulary',
       lambda d,side,tab:side.__setitem__('accepted',True)),
      ('C5 derived-pin base-pin mismatch (drift absorb)','base-pin mismatch',
       lambda d,side,tab:side['derivedPins'][0].__setitem__('oldSha256','0'*64)),
      ('C6 table sha mismatch','table sha mismatch',
       lambda d,side,tab:side['table'].__setitem__('sha256','0'*64)),
      ('C7 occurrence-count drift','occurrence drift',
       lambda d,side,tab:(tab[0].__setitem__('occurrences',tab[0]['occurrences']+1),side['table'].__setitem__('sha256',hashlib.sha256(json.dumps(tab,indent=1,ensure_ascii=False).encode()).hexdigest()))),
      ('C8 non-byte-exact replacement','reconstruction != committed candidate',
       lambda d,side,tab:(tab[0].__setitem__('replace',tab[0]['replace']+'X'),side['table'].__setitem__('sha256',hashlib.sha256(json.dumps(tab,indent=1,ensure_ascii=False).encode()).hexdigest()))),
      ('C9 altered nested amendment blob id','nested amendment blob id mismatch',
       lambda d,side,tab:side['families']['history-master']['variants']['en'].__setitem__('candidateBlobSha1AtC','0'*40)),
      ('C10 historical (old) digest inconsistency','sidecar rewrites history record',
       lambda d,side,tab:side['families']['history-master']['variants']['en'].__setitem__('oldBodySha256','0'*64)),
      ('C16 committed history-record mutation at head','evidence record mutated at current head',
       lambda d,side,tab:(Path(d)/'locales/history-equivalence.json').write_bytes((Path(d)/'locales/history-equivalence.json').read_bytes()+b' ')),
    ]
    for name,branch,mut in cases:
        d,side=fixture(mut)
        try:expect_reject(name,branch,lambda d=d:ca.prove(d))
        finally:shutil.rmtree(d,ignore_errors=True)

    # C11 candidate commit with extra content drift. D1 = base + the EXACT finite 44
    # C2 paths + drift inside one changed HTML file (no sidecar/table/tooling in D1, so
    # the finite changed-set gate passes). D2 checks back out the ACTUAL current head tree
    # (retaining D1) and modifies ONLY the sidecar candidate binding, so W0 fidelity and
    # every proof input hold; the tamper must then reach the reconstruction branch.
    d=fresh_clone(root)
    try:
        head0=subprocess.check_output(['git','-C',d,'rev-parse','HEAD']).decode().strip()
        table_now=json.loads((Path(d)/s['table']['path']).read_text())
        finite=sorted({e['path'] for e in table_now}|{e['file'] for e in s['derivedPins']})
        victim=sorted({e['path'] for e in table_now})[0]
        subprocess.run(['git','-C',d,'checkout','--quiet','-b','driftctl',B],check=True)
        subprocess.run(['git','-C',d,'checkout','--quiet',C,'--']+finite,check=True)
        Path(d,victim).write_bytes(Path(d,victim).read_bytes()+b'<!--drift-->')
        commit_all(d,'drift control D1')
        D1=subprocess.check_output(['git','-C',d,'rev-parse','HEAD']).decode().strip()
        tree=subprocess.check_output(['git','-C',d,'rev-parse','HEAD^{tree}']).decode().strip()
        subprocess.run(['git','-C',d,'checkout','--quiet',head0,'--','.'],check=True)
        sp=Path(d)/ca.SIDECAR;side=json.loads(sp.read_text())
        side['candidate']={'commit':D1,'tree':tree}
        sp.write_text(json.dumps(side,indent=1,ensure_ascii=False))
        commit_all(d,'sidecar drift binding D2')
        expect_reject('C11 candidate content drift beyond table','reconstruction != committed candidate',lambda:ca.prove(d))
    finally:shutil.rmtree(d,ignore_errors=True)

    # C12 stateful raw-span scanner unit controls (exact independent fixtures)
    ok=b'<html><head><link href="https://a.example/x?b=1&amp;c=2"/></head><body></body></html>'
    ent=[{'path':'f.html','find':'https://a.example/x?b=1&amp;c=2','replace':'https://n.example/','occurrences':1}]
    try:ca._scan_href_spans(ok,'f.html',ent);record('C12a legitimate href span accepted',True)
    except ValueError as e:record('C12a legitimate href span accepted',False,str(e))
    for label,bad in (('script pseudoanchor',b'<script>const x=\'<a href="https://a.example/x?b=1&amp;c=2">\';</script>'),
                      ('comment pseudoanchor',b'<!-- <a href="https://a.example/x?b=1&amp;c=2"> -->'),
                      ('data-href attribute',b'<a data-href="https://a.example/x?b=1&amp;c=2">x</a>'),
                      ('href value substring',b'<a href="prefixhttps://a.example/x?b=1&amp;c=2suffix">x</a>'),
                      ('unquoted href',b'<a href=https://a.example/x?b=1&amp;c=2>x</a>'),
                      ('text node',b'<p>see https://a.example/x?b=1&amp;c=2 here</p>'),
                      ('JSON-LD',b'<script type="application/ld+json">{"url":"https://a.example/x?b=1&amp;c=2"}</script>')):
        try:ca._scan_href_spans(bad,'f.html',ent);record('C12 '+label+' rejected',False,'ACCEPTED')
        except ValueError:record('C12 '+label+' rejected',True)

    # C14 cross-root memo NC: identical base+sidecar on a DIFFERENT root with a tampered
    # (committed) table must re-validate and reject on the named branch.
    d,side=fixture(lambda d,side,tab:tab[0].__setitem__('occurrences',tab[0]['occurrences']+1))
    try:expect_reject('C14 different-root tampered table (memo cannot cross roots)','table sha mismatch',lambda:ca.prove(d))
    finally:shutil.rmtree(d,ignore_errors=True)

    # C15 same-root worktree history-record mutation: memo must not serve the cached
    # receipt; re-validation must hit the W0 fidelity branch. Mutate + restore.
    rec_path=Path(root)/'locales/history-equivalence.json'
    raw=rec_path.read_bytes()
    try:
        rec_path.write_bytes(raw+b' ')
        expect_reject('C15 same-root worktree history-record mutation','worktree proof input diverges from head',lambda:ca.prove(root))
    finally:
        rec_path.write_bytes(raw)
    try:
        ca.prove(root);record('C15b restored state returns to proof',True)
    except Exception as e:record('C15b restored state returns to proof',False,str(e)[:200])

    # C13 manifest-policy exact equality on the committed manifest (amendment participates in recompute)
    mtext=(Path(root)/'same-page-manifest.js').read_text()
    try:
        from i18n.manifest_policy import scoped_provenance
        scoped_provenance(Path(root),mtext);record('C13 manifest_policy exact equality with amendment',True)
    except Exception as e:record('C13 manifest_policy exact equality with amendment',False,str(e)[:300])

    # ---- T7 boundary controls: degraded export mode + manifest identity (Scrum round 5) ----
    # C26 genuine export (no .git entry): degraded mode works, claims nothing beyond file identity.
    ex=fresh_clone(root);shutil.rmtree(str(Path(ex)/'.git'))
    try:
        r=ca.prove(ex)
        record('C26 genuine export: degraded mode, no ancestry/historical claims',r.get('mode')=='degraded-no-git' and r.get('commands')==[] and 'contract' in r,json.dumps(r)[:120])
    except Exception as e:
        record('C26 genuine export: degraded mode, no ancestry/historical claims',False,type(e).__name__+': '+str(e)[:200])
    finally:shutil.rmtree(ex,ignore_errors=True)
    # C27 export + mutated table
    ex=fresh_clone(root);shutil.rmtree(str(Path(ex)/'.git'))
    try:
        tp=Path(ex)/s['table']['path'];b=tp.read_bytes();tp.write_bytes(b[:-2]+b'xx')
        expect_reject('C27 export+mutated table rejected','table sha mismatch',lambda:ca.prove(ex))
    finally:shutil.rmtree(ex,ignore_errors=True)
    # C28 export + mutated covered content
    ex=fresh_clone(root);shutil.rmtree(str(Path(ex)/'.git'))
    try:
        f=Path(ex)/'history.html';f.write_text(f.read_text().replace('<main','<main data-tamper="1"',1))
        expect_reject('C28 export+mutated content rejected','degraded content digest mismatch',lambda:ca.prove(ex))
    finally:shutil.rmtree(ex,ignore_errors=True)
    # C29 export + mutated sidecar digest
    ex=fresh_clone(root);shutil.rmtree(str(Path(ex)/'.git'))
    try:
        sp=Path(ex)/ca.SIDECAR;sd=json.loads(sp.read_text());e=sd['families']['history-master']['variants']['en']
        e['newBodySha256']=('0' if e['newBodySha256'][0]!='0' else '1')+e['newBodySha256'][1:]
        sp.write_text(json.dumps(sd,indent=2,ensure_ascii=False)+'\n')
        expect_reject('C29 export+mutated sidecar digest rejected','degraded content digest mismatch',lambda:ca.prove(ex))
    finally:shutil.rmtree(ex,ignore_errors=True)
    # C30 export + mutated derived pin
    ex=fresh_clone(root);shutil.rmtree(str(Path(ex)/'.git'))
    try:
        e0=s['derivedPins'][0];rel=e0['file'];fp=Path(ex)/rel;data=json.loads(fp.read_bytes())
        if rel.endswith('-bindings.json') or rel.endswith('-exact.json'):
            data[e0['field']]='0'*64;branch='degraded pin field mismatch'
        else:
            data['files'][e0['master']][e0['field']]='0'*64;branch='degraded contract field mismatch'
        fp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
        expect_reject('C30 export+mutated derived pin rejected',branch,lambda:ca.prove(ex))
    finally:shutil.rmtree(ex,ignore_errors=True)
    # C30b warm-memo derived-pin tamper: the memo key must cover every checked input's
    # bytes - a cached receipt must NOT survive mutation of a derived-pin contract.
    ex=fresh_clone(root);shutil.rmtree(str(Path(ex)/'.git'))
    try:
        ca.prove(ex)  # warm the memo on the pristine export
        e0=next(e for e in s['derivedPins'] if e['file'].endswith('-exact.json'))
        fp=Path(ex)/e0['file'];data=json.loads(fp.read_text())
        data[e0['field']]='0'*64
        fp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
        expect_reject('C30b warm-memo derived-pin tamper rejected','degraded pin field mismatch',lambda:ca.prove(ex))
    finally:shutil.rmtree(ex,ignore_errors=True)
    # C31a broken .git FILE (corrupt gitfile): never falls into export mode
    d=fresh_clone(root)
    try:
        shutil.rmtree(str(Path(d)/'.git'));Path(d,'.git').write_text('gitdir: /nonexistent-citqa\n')
        expect_reject('C31 broken .git gitfile never degrades','refusing degraded export mode',lambda:ca.prove(d))
    finally:shutil.rmtree(d,ignore_errors=True)
    # C31b .git present but objects stripped: git mode, fail closed on missing objects
    d=fresh_clone(root)
    try:
        # Keep .git/objects PRESENT but strip its contents: git still accepts the repo
        # (moving the whole dir away makes git itself call the repo invalid, which
        # lands on the _git_mode unreadable branch instead of the object-proof branch).
        _objdir=Path(d)/'.git'/'objects'
        for _child in _objdir.iterdir():
            if _child.is_dir():shutil.rmtree(_child)
            else:_child.unlink()
        expect_reject('C31b stripped .git objects fail closed','missing objects',lambda:ca.prove(d))
    finally:shutil.rmtree(d,ignore_errors=True)
    # C31c dangling .git SYMLINK: present-but-broken marker, never an absent one
    d=fresh_clone(root)
    try:
        shutil.rmtree(str(Path(d)/'.git'));os.symlink('/nonexistent-citqa-target',str(Path(d)/'.git'))
        expect_reject('C31c dangling .git symlink never degrades','refusing degraded export mode',lambda:ca.prove(d))
    finally:shutil.rmtree(d,ignore_errors=True)
    # C32 valid worktree .git FILE selects full git mode (never degraded)
    d=fresh_clone(root);wt=tempfile.mkdtemp(prefix='citqa-wt-')
    try:
        subprocess.run(['git','-C',d,'worktree','add','--detach','--quiet',wt,'HEAD'],check=True)
        record('C32 worktree .git file selects full git mode',ca._git_mode(wt) is True)
    finally:
        subprocess.run(['git','-C',d,'worktree','remove','--force',wt],capture_output=True)
        shutil.rmtree(d,ignore_errors=True);shutil.rmtree(wt,ignore_errors=True)
    # C33 manifest provenance identity (balanced missing/duplicate/foreign/mutated)
    import copy as _copy
    from i18n.manifest_policy import citation_provenance
    man=json.loads(mtext[len('window.SC_SAME_PAGE_MANIFEST = '):-2])
    try:
        sc=citation_provenance(Path(root),man);record('C33 manifest addenda identity positive',sum(sc.values())>0,'scoped prose tokens: '+str(sum(sc.values())))
    except Exception as e:
        record('C33 manifest addenda identity positive',False,type(e).__name__+': '+str(e)[:200])
    man2=_copy.deepcopy(man)
    done=False
    for key,page in man2['pages'].items():
        for code,v in page['variants'].items():
            if v.get('proof',{}).pop('citationAmendment',None) is not None:done=True;break
        if done:break
    expect_reject('C33b manifest missing amendment rejected','set differs from sidecar',lambda:citation_provenance(Path(root),man2))
    man3=_copy.deepcopy(man)
    dup=_copy.deepcopy(man3['pages']['history-master-equivalence'])
    dup['variants']={'en':dup['variants']['en']}
    man3['pages']['history-master-equivalence-DUP']=dup
    expect_reject('C33c manifest duplicated amendment rejected','unexpected page key',lambda:citation_provenance(Path(root),man3))
    man6=_copy.deepcopy(man)
    man6['pages']['history-master-equivalence-RENAMED']=man6['pages'].pop('history-master-equivalence')
    expect_reject('C33f renamed page key rejected','unexpected page key',lambda:citation_provenance(Path(root),man6))
    man4=_copy.deepcopy(man)
    k0=next(k for k,pg in man4['pages'].items() if not any('citationAmendment' in v.get('proof',{}) for v in pg['variants'].values()))
    next(iter(man4['pages'][k0]['variants'].values())).setdefault('proof',{})['citationAmendment']={'type':'citation-source-correction','scope':'x'}
    expect_reject('C33d foreign manifest amendment rejected','unexpected page key',lambda:citation_provenance(Path(root),man4))
    man5=_copy.deepcopy(man)
    man5['pages']['history-master-equivalence']['variants']['en']['proof']['citationAmendment']['scope']='tampered scope'
    expect_reject('C33e mutated manifest addendum rejected','differs from validated sidecar',lambda:citation_provenance(Path(root),man5))

    # C34 coherent multi-anchor attack (content+table+sidecar mutated consistently).
    # Scrum's trust-anchor boundary: in an export every anchor is editable, so a coherent
    # attack CAN pass degraded self-consistency - the control pins the contract that the
    # export build then claims NOTHING historical, while the git-native proof rejects the
    # same bytes on the reconstruction branch. Trust anchor is git mode, never self-consistency.
    _masters={e['master'] for e in s['derivedPins']}
    _table=json.loads((Path(root)/s['table']['path']).read_text())
    _victim=None
    for _fam,_d0 in s['families'].items():
        if _fam=='ar2':continue
        for _code,_e in _d0.get('variants',{}).items():
            if _e['file'] not in _masters and any(t['path']==_e['file'] for t in _table):
                _victim=(_fam,_code,_e);break
        if _victim:break
    if not _victim:raise ValueError('control setup: no table-covered non-master victim found')
    def coherent_attack(x):
        _fam,_code,_e=_victim
        tv=[t for t in _table if t['path']==_e['file']][0]
        evil='https://evil.example/citation-attack'
        f=Path(x)/_e['file'];t=f.read_text()
        if tv['replace'] not in t:raise ValueError('control setup: replace string absent from victim')
        f.write_text(t.replace(tv['replace'],evil))
        tpath=Path(x)/s['table']['path'];tt=json.loads(tpath.read_text())
        for row in tt:
            if row['path']==_e['file'] and row['replace']==tv['replace']:row['replace']=evil
        tpath.write_text(json.dumps(tt,indent=2,ensure_ascii=False)+'\n')
        sp=Path(x)/ca.SIDECAR;sd=json.loads(sp.read_text())
        from i18n.reviewed_history import digest as _gd
        sd['families'][_fam]['variants'][_code]['newBodySha256']=_gd(f.read_text())
        sd['table']['sha256']=hashlib.sha256(tpath.read_bytes()).hexdigest()
        sp.write_text(json.dumps(sd,indent=2,ensure_ascii=False)+'\n')
    ex=fresh_clone(root);shutil.rmtree(str(Path(ex)/'.git'))
    coherent_attack(ex)
    try:
        r=ca.prove(ex)
        ok=r.get('mode')=='degraded-no-git' and r.get('commands')==[] and 'contract' in r
        # Caller boundary: the REAL caller must withhold verified/reviewed vocabulary
        from i18n.reviewed_history import history_manifest
        out=history_manifest(Path(ex),{},{'pages':{}})
        v=out['pages']['history-master-equivalence']['variants']['ar']
        blob=json.dumps(v)
        clean=(v.get('status')!='verified' and v.get('proof',{}).get('type')=='unverified-export'
               and 'approved' not in blob and 'reviewed-history-master' not in blob)
        # Consumer boundary: the REAL resolver must not resolve the attacked route
        mf=Path(ex)/'manifest-check.json'
        mf.write_text(json.dumps({'version':1,'pages':out['pages']}))
        js=("const R=require(%s),M=require(%s);"
            "const f=R.locate(M,'/ar/biography');"
            "process.stdout.write(JSON.stringify({found:!!f,verified:f?!!R.verified(f.page,f.variant):null}));"
            %(json.dumps(str(Path(root)/'same-page-resolver.js')),json.dumps(str(mf))))
        nr=subprocess.run(['node','-e',js],capture_output=True,text=True,timeout=60)
        res=json.loads(nr.stdout)
        record('C34a coherent attack: export caller+consumer claim NOTHING',ok and clean and res.get('found')==True and res.get('verified')==False,
               'mode=%s status=%s resolverVerified=%s'%(r.get('mode'),v.get('status'),res.get('verified')))
    except Exception as e:
        record('C34a coherent attack: export caller+consumer claim NOTHING',False,type(e).__name__+': '+str(e)[:200])
    finally:shutil.rmtree(ex,ignore_errors=True)
    d=fresh_clone(root);coherent_attack(d);commit_all(d,'coherent citation attack fixture')
    expect_reject('C34b coherent attack rejected by git-native proof','reconstruction != committed candidate',lambda:ca.prove(d))
    shutil.rmtree(d,ignore_errors=True)
    # C35 resolver positive: the committed git-mode manifest MUST still resolve verified
    # (guards against over-blocking by the export segregation).
    real=json.loads(mtext[len('window.SC_SAME_PAGE_MANIFEST = '):-2])
    mf2=Path(tempfile.mkdtemp(prefix='citqa-res-'))/'m.json'
    mf2.write_text(json.dumps({'version':1,'pages':real['pages']}))
    js=("const R=require(%s),M=require(%s);"
        "const a=R.locate(M,'/ar/biography');const b=R.locate(M,'/ar/gallery');"
        "process.stdout.write(JSON.stringify({bio:a?!!R.verified(a.page,a.variant):null,gal:b?!!R.verified(b.page,b.variant):null}));"
        %(json.dumps(str(Path(root)/'same-page-resolver.js')),json.dumps(str(mf2))))
    nr=subprocess.run(['node','-e',js],capture_output=True,text=True,timeout=60)
    try:res=json.loads(nr.stdout)
    except Exception:res={}
    record('C35 resolver resolves committed git-mode manifest verified',res.get('bio')==True and res.get('gal')==True,nr.stdout[:90]+nr.stderr[:60])
    shutil.rmtree(mf2.parent,ignore_errors=True)
    # C36 every export caller withholds verified/reviewed claims for citation-covered
    # content (pristine export; a builder that cannot run in an export emits nothing,
    # which cannot leak a claim - noted in detail, not failed).
    ex=fresh_clone(root);shutil.rmtree(str(Path(ex)/'.git'))
    try:
        bad=[];ran=[]
        from i18n.reviewed_history import history_manifest
        from i18n.reviewed_prayers import prayer_manifest
        from i18n.reviewed_travel import travel_manifest
        from i18n.ar2_equivalence import ar2_manifest
        covered={fam+'-equivalence' for fam in s['families'] if fam!='ar2'}|{'ar2-'+slug+'-equivalence' for slug in s['families']['ar2']['pages']}
        m={'pages':{}}
        for builder in (history_manifest,prayer_manifest,travel_manifest,ar2_manifest):
            try:m=builder(Path(ex),{},m);ran.append(builder.__name__)
            except Exception as e:ran.append(builder.__name__+'(raised:'+type(e).__name__+')')
        for key in covered:
            for code,v in m['pages'].get(key,{}).get('variants',{}).items():
                blob=json.dumps(v)
                if v.get('status')=='verified' or 'approved' in blob or v.get('proof',{}).get('type')!='unverified-export':
                    bad.append(key+'/'+code+':'+str(v.get('status'))+','+str(v.get('proof',{}).get('type')))
        record('C36 every export caller withholds verified/reviewed claims',not bad,('; '.join(bad[:3])) if bad else 'builders: '+','.join(ran))
    finally:shutil.rmtree(ex,ignore_errors=True)

    fails=[n for n,ok,_ in RESULTS if not ok]
    print(f'\n{len(RESULTS)-len(fails)}/{len(RESULTS)} controls pass'+('' if not fails else ' — FAILURES: '+','.join(fails)))
    return 1 if fails else 0

if __name__=='__main__':sys.exit(main())
