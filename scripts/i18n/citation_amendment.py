"""Citation-source-correction amendment proof module.

PROPOSED-data proof only: this module authenticates NOTHING and marks nothing accepted.
Authority is external exact-head review of the real head carrying the sidecar. Every
owning guard calls these functions; a covered family is usable only while the FULL proof
passes in the current process (historical leg + finite delta, memoized only against a
root-bound full input key: root, base, sidecar/table bytes, and this tooling's bytes).
"""
import hashlib, json, re, subprocess, sys, tempfile, shutil,os
from pathlib import Path

SIDECAR='locales/citation-amendment-2026-11.json'
_MEMO={}
_TOOL_FILES=('scripts/i18n/citation_amendment.py','scripts/i18n/reviewed_history.py',
    'scripts/i18n/reviewed_prayers.py','scripts/i18n/reviewed_travel.py',
    'scripts/i18n/travel_variant_evidence.py','scripts/i18n/ar2_equivalence.py',
    'scripts/i18n/keyed_master.py','scripts/i18n/reviewed_travel.py')
_RECORD_FILES=('locales/history-equivalence.json','locales/prayer-equivalence.json',
    'locales/travel-equivalence.json','locales/ar2-pairing-evidence.json')

def _sh(root,*a,binary=False):
    r=subprocess.check_output(['git','-C',str(root)]+list(a),stderr=subprocess.DEVNULL)
    return r if binary else r.decode().strip()
def _blob(root,rev,rel):
    try:return _sh(root,'show',f'{rev}:{rel}',binary=True)
    except subprocess.CalledProcessError:return None

def _git_mode(root):
    """True: working git tree (.git file or dir, rev-parse works) - full object proof.
    False: genuine export (no .git entry at all) - degraded file-identity mode.
    A PRESENT but unreadable .git (corrupt gitfile, broken dir, stripped metadata) is
    corruption: fail closed. Never silently fall from git mode into export mode."""
    # lstat-level presence: a DANGLING .git symlink is a present-but-broken marker,
    # not an absent one - Path.exists() would follow the link and silently degrade.
    if not os.path.lexists(str(Path(root)/'.git')):return False
    try:_sh(root,'rev-parse','--git-dir');return True
    except subprocess.CalledProcessError:
        raise ValueError('citation: .git present but unreadable; refusing degraded export mode')

def load(root):
    """Sidecar dict or None. Structural validation only; proof is prove()."""
    p=Path(root)/SIDECAR
    if not p.exists():return None
    s=json.loads(p.read_text())
    if s.get('kind')!='citation-source-correction':raise ValueError('citation amendment: wrong kind')
    if 'accepted' in json.dumps(s).lower():raise ValueError('citation amendment: acceptance vocabulary is not data')
    for k in ('base','candidate','table','derivedPins','families','addendumText'):
        if k not in s:raise ValueError('citation amendment: missing '+k)
    return s

def match(root,family,code):
    s=load(root)
    if not s:return None
    fam=s['families'].get(family)
    if not fam:return None
    return fam.get('variants',{}).get(code)

def match_ar2(root,slug,code):
    s=load(root)
    if not s:return None
    pages=s['families'].get('ar2',{}).get('pages',{})
    row=pages.get(slug)
    return row.get(code) if row else None

def addendum(root,family,code,current_digest):
    """Nested proof sibling. Historical scope quoted verbatim; new scope is the fixed note."""
    e=match(root,family,code)
    if not e:return None
    prove(root)
    s=load(root)
    out={'type':'citation-source-correction','sourceC':s['candidate']['commit'],
         'candidateBlobSha1':e.get('candidateBlobSha1AtC'),'newBodySha256':e['newBodySha256'],
         'historicalBodySha256':e['oldBodySha256'],'tableSha256':s['table']['sha256'],
         'scope':s['addendumText']}
    if e.get('inheritedScope'):out['inheritedScope']=e['inheritedScope']
    if e.get('historicalCandidateFileSha256'):out['historicalCandidateFileSha256']=e['historicalCandidateFileSha256']
    if e.get('historicalPreparedRevision'):out['historicalPreparedRevision']=e['historicalPreparedRevision']
    if current_digest!=e['newBodySha256']:raise ValueError('citation amendment: digest mismatch '+family+' '+code)
    return out

def effective_body(root,family,code,old_sha):
    e=match(root,family,code)
    if not e:return old_sha
    if old_sha!=e['oldBodySha256']:
        raise ValueError('citation amendment: guard-passed historical pin != sidecar historical pin '+family+' '+code)
    prove(root)
    return e['newBodySha256']

def effective_catalog(root,family,code,old_sha):
    e=match(root,family,code)
    if not e:return old_sha
    cat=e.get('catalog')
    if not cat:return old_sha
    prove(root)
    if cat['sha256Unchanged']!=old_sha or not cat['verifiedEqual']:raise ValueError('citation amendment: catalog contract violated '+family+' '+code)
    return old_sha

def current_candidate_bytes(root,family,code):
    e=match(root,family,code)
    if not e:return None
    prove(root)
    b=_blob(root,load(root)['candidate']['commit'],e['file'])
    if b is None or _sh(root,'rev-parse',f"{load(root)['candidate']['commit']}:{e['file']}")!=e['candidateBlobSha1AtC']:
        raise ValueError('citation amendment: candidate blob unavailable/mismatch')
    return b

def ar2_addendum(root,slug,code,current_digest,current_candidate_sha):
    row=match_ar2(root,slug,code)
    if not row:return None
    prove(root)
    if current_digest!=row['newDigest'] or current_candidate_sha!=row['newCandidateFileSha256']:
        raise ValueError('citation amendment: ar2 digest mismatch '+slug+' '+code)
    s=load(root)
    pg=s['families']['ar2']['pages'][slug]
    return {'type':'citation-source-correction','sourceC':s['candidate']['commit'],
            'candidateBlobSha1':row['candidateBlobSha1AtC'],'newBodySha256':row['newDigest'],
            'historicalBodySha256':row['historicalDigest'],'tableSha256':s['table']['sha256'],
            'scope':s['addendumText'],
            'inheritedScope':pg['inheritedScope'],'inheritedSourceRevision':pg['inheritedSourceRevision']}

# ---------- full proof ----------
def _hash_files(root,rels):
    h=hashlib.sha256()
    for rel in rels:
        h.update(rel.encode());h.update(b'\0');h.update((Path(root)/rel).read_bytes());h.update(b'\0')
    return h.hexdigest()

def _input_paths(s):
    """Every disk path whose bytes feed the proof: records, catalogs, covered content."""
    rels=list(_RECORD_FILES)
    for fam,d in s['families'].items():
        if fam=='ar2':continue
        for e in d.get('variants',{}).values():
            rels.append(e['file'])
            if e.get('catalog'):rels.append(e['catalog']['path'])
    for pg in s['families'].get('ar2',{}).get('pages',{}).values():
        for code,row in pg.items():
            if isinstance(row,dict) and 'file' in row:rels.append(row['file'])
    # Derived-pin contracts AND their masters: the degraded closure checks these bytes,
    # so they are proof inputs and must key the memo (warm-memo tamper control C30b).
    for e in s.get('derivedPins',[]):
        rels.append(e['file']);rels.append(e['master'])
    return sorted(set(rels))

def prove(root):
    root=str(Path(root).resolve())
    s=load(root)
    # Full current-input identity on EVERY call: root, actual HEAD, sidecar/table bytes,
    # tooling bytes, and the current bytes of every record/catalog/covered-content file.
    # A cached receipt is reused only when ALL of these are unchanged.
    git=_git_mode(root)
    key=(root,_sh(root,'rev-parse','HEAD') if git else '<no-git>',
         hashlib.sha256((Path(root)/SIDECAR).read_bytes()).hexdigest(),
         hashlib.sha256((Path(root)/s['table']['path']).read_bytes()).hexdigest(),
         _hash_files(root,_TOOL_FILES),
         _hash_files(root,_input_paths(s)))
    if key in _MEMO:return _MEMO[key]
    receipts=_prove_fresh(root,s) if git else _prove_degraded(root,s)
    _MEMO[key]=receipts
    return receipts

EXPORT_CONTRACT_HEAD='deterministic export BUILD support only - not an acceptance guard. '
EXPORT_CONTRACT=EXPORT_CONTRACT_HEAD+(
    'This receipt establishes NO historical/reviewed/accepted/equivalent status: every '
    'anchor it checks (sidecar, table, records, content, derived pins) is editable in an '
    'export, so self-consistency here is not authenticity. Historical qualification '
    'requires the git-native full proof (ancestry, reconstruction, derived pins, HEAD/W0 '
    'binding, isolated clean-B chain), which remains mandatory wherever git exists.')

def proof_mode(root):
    """'git' when the full object proof binds this tree, else 'degraded-no-git'.
    Runs the proof first: a tampered tree raises here instead of returning a mode."""
    if _git_mode(root):prove(root);return 'git'
    return prove(root)['mode']

def export_variant(path,eff,source_sha):
    """The ONLY variant shape an editable export may emit for citation-covered content:
    deterministic build data with NO verified/reviewed/approved/equivalent claim, so no
    consumer (same-page-resolver verified()) can resolve it as reviewed."""
    return {'path':path,'aliases':[],'status':'unverified-export','contentSha256':eff,
            'sourceSha256':source_sha,'proof':{'type':'unverified-export','exportContract':EXPORT_CONTRACT}}

def _prove_degraded(root,s):
    """Exported/synthetic tree without .git: the object-level legs (ancestry, blob
    reconstruction, derived pins, historical chain, HEAD/worktree binding) cannot run
    there. What remains enforced is exact file identity: table sha, the structural table
    guards, the memo key over every proof input's current bytes, and the calling guards'
    digest equality of each covered file against the sidecar's recorded new shas.
    Authoritative builds and every wired QA gate run in real clones and pay the full
    proof; this mode exists so an exported or synthetic tree builds deterministically
    instead of crashing inside a subprocess, and it never runs where git exists."""
    table_raw=(Path(root)/s['table']['path']).read_bytes()
    if hashlib.sha256(table_raw).hexdigest()!=s['table']['sha256']:raise ValueError('citation: table sha mismatch')
    table=json.loads(table_raw)
    for e in table:
        p=e['path']
        if p.startswith('/') or '..' in p.split('/') or not re.fullmatch(r'[A-Za-z0-9._\-/]+',p) or not p.endswith('.html'):
            raise ValueError('citation: unsafe table path '+p)
        if not e['find'] or not e['replace'] or e['find']==e['replace'] or e['occurrences']<1:
            raise ValueError('citation: bad table entry '+p)
    # Content/catalog identity for ALL families - the SAME digest semantics the calling
    # guards use (bs4-normalized main for bodies; raw-bytes sha256 for ar2 candidate
    # files and catalogs). A mutated sidecar, record, or covered file breaks this
    # closure even with no git objects present. Deferred import: the guard modules
    # import this module at their own top level.
    from i18n.reviewed_history import digest as _guard_digest
    for fam,d in s['families'].items():
        if fam=='ar2':continue
        for code,e in d.get('variants',{}).items():
            if _guard_digest((Path(root)/e['file']).read_text())!=e['newBodySha256']:
                raise ValueError('citation: degraded content digest mismatch '+fam+' '+code)
            cat=e.get('catalog')
            if cat:
                if not cat.get('verifiedEqual') or hashlib.sha256((Path(root)/cat['path']).read_bytes()).hexdigest()!=cat['sha256Unchanged']:
                    raise ValueError('citation: degraded catalog mismatch '+fam+' '+code)
    for slug,pg in s['families'].get('ar2',{}).get('pages',{}).items():
        for code,row in pg.items():
            if not (isinstance(row,dict) and 'file' in row):continue
            raw=(Path(root)/row['file']).read_bytes()
            if hashlib.sha256(raw).hexdigest()!=row['newCandidateFileSha256']:
                raise ValueError('citation: degraded ar2 candidate mismatch '+slug+' '+code)
            if _guard_digest((Path(root)/row['file']).read_text())!=row['newDigest']:
                raise ValueError('citation: degraded ar2 digest mismatch '+slug+' '+code)
    # Derived-pin closure over current bytes: same owning formulas as R3, current tree.
    sys.path.insert(0,str(Path(root)/'scripts'))
    from i18n.keyed_master import strip_static_fallback
    by_file={}
    for e in s['derivedPins']:by_file.setdefault(e['file'],[]).append(e)
    for rel,entries in by_file.items():
        cc=json.loads((Path(root)/rel).read_bytes())
        for e in entries:
            m=e['master']
            if rel.endswith('-bindings.json') or rel.endswith('-exact.json'):
                if e['newSha256']!=hashlib.sha256(strip_static_fallback((Path(root)/m).read_bytes())).hexdigest():raise ValueError('citation: degraded new pin != owning formula '+rel)
                if cc[e['field']]!=e['newSha256']:raise ValueError('citation: degraded pin field mismatch '+rel)
            else:
                def msha(x):return hashlib.sha256(re.search(rb'<main\b[\s\S]*?</main>',x)[0]).hexdigest()
                if e['newSha256']!=msha((Path(root)/m).read_bytes()):raise ValueError('citation: degraded contract new pin mismatch '+m)
                if cc['files'][m][e['field']]!=e['newSha256']:raise ValueError('citation: degraded contract field mismatch '+rel)
    return {'mode':'degraded-no-git','base':s['base'],'commands':[],
            'contract':EXPORT_CONTRACT}

def _prove_fresh(root,s):
    B=s['base'];C=s['candidate']['commit']
    table_path=s['table']['path'];table_raw=(Path(root)/table_path).read_bytes()
    if hashlib.sha256(table_raw).hexdigest()!=s['table']['sha256']:raise ValueError('citation: table sha mismatch')
    table=json.loads(table_raw)
    # T1 guards
    for e in table:
        p=e['path']
        if p.startswith('/') or '..' in p.split('/') or not re.fullmatch(r'[A-Za-z0-9._\-/]+',p) or not p.endswith('.html'):
            raise ValueError('citation: unsafe table path '+p)
        if not e['find'] or not e['replace'] or e['find']==e['replace'] or e['occurrences']<1:
            raise ValueError('citation: bad table entry '+p)
    # G: objects/ancestry
    def _cat(rev):
        try:return _sh(root,'cat-file','-t',rev)
        except subprocess.CalledProcessError:return None
    if _cat(B)!='commit' or _cat(C)!='commit':raise ValueError('citation: missing objects')
    if _sh(root,'rev-parse',C+'^')!=_sh(root,'rev-parse',B):raise ValueError('citation: C parent != B')
    if _sh(root,'rev-parse',C+'^{tree}')!=s['candidate']['tree']:raise ValueError('citation: C tree mismatch')
    # W0 worktree fidelity: every proof input's disk bytes must equal its HEAD blob
    head=_sh(root,'rev-parse','HEAD')
    for rel in [SIDECAR,table_path]+list(_TOOL_FILES)+_input_paths(s):
        disk=(Path(root)/rel).read_bytes()
        if _blob(root,head,rel)!=disk:raise ValueError('citation: worktree proof input diverges from head '+rel)
    # finite changed set
    tpaths={e['path'] for e in table}
    dfiles=sorted({e['file'] for e in s['derivedPins']})
    changed=_sh(root,'diff','--name-only',B,C).split('\n')
    if set(changed)!=tpaths|set(dfiles):raise ValueError('citation: changed set outside finite table+derived')
    # R2 byte-exact reconstruction + raw-span href scan
    for f in tpaths:
        b=_blob(root,B,f);c=_blob(root,C,f)
        if b is None or c is None:raise ValueError('citation: missing blob '+f)
        _scan_href_spans(b,f,[e for e in table if e['path']==f])
        recon=b
        for e in [e for e in table if e['path']==f]:
            if recon.count(e['find'].encode())!=e['occurrences']:raise ValueError('citation: occurrence drift '+f)
            recon=recon.replace(e['find'].encode(),e['replace'].encode())
        if recon!=c:raise ValueError('citation: reconstruction != committed candidate '+f)
    # R3 derived pins: owning formulas + base-pin match + literal swap
    sys.path.insert(0,str(Path(root)/'scripts'))
    from i18n.keyed_master import strip_static_fallback
    by_file={}
    for e in s['derivedPins']:by_file.setdefault(e['file'],[]).append(e)
    for rel,entries in by_file.items():
        bb=_blob(root,B,rel);cc=_blob(root,C,rel)
        cB=json.loads(bb);cC=json.loads(cc);recon=bb
        for e in entries:
            m=e['master']
            if rel.endswith('-bindings.json') or rel.endswith('-exact.json'):
                if e['oldSha256']!=hashlib.sha256(strip_static_fallback(_blob(root,B,m))).hexdigest():raise ValueError('citation: base-pin mismatch (drift absorb rejected) '+rel)
                if e['newSha256']!=hashlib.sha256(strip_static_fallback(_blob(root,C,m))).hexdigest():raise ValueError('citation: new pin != owning formula '+rel)
                if cB[e['field']]!=e['oldSha256'] or cC[e['field']]!=e['newSha256']:raise ValueError('citation: pin field mismatch '+rel)
            else:
                def msha(x):return hashlib.sha256(re.search(rb'<main\b[\s\S]*?</main>',x)[0]).hexdigest()
                if e['oldSha256']!=msha(_blob(root,B,m)):raise ValueError('citation: contract base-pin mismatch '+m)
                if e['newSha256']!=msha(_blob(root,C,m)):raise ValueError('citation: contract new pin mismatch '+m)
                if cB['files'][m][e['field']]!=e['oldSha256'] or cC['files'][m][e['field']]!=e['newSha256']:raise ValueError('citation: contract field mismatch '+m)
            if recon.count(e['oldSha256'].encode())!=1:raise ValueError('citation: pin token not unique in base bytes '+rel)
            recon=recon.replace(e['oldSha256'].encode(),e['newSha256'].encode(),1)
        if recon!=cc:raise ValueError('citation: non-literal derived-pin delta '+rel)
    # E1 historical evidence records immutable: identical at B, C AND the current final head.
    for rel in _RECORD_FILES:
        rb=_blob(root,B,rel)
        if rb is None:raise ValueError('citation: historical record missing at base '+rel)
        if _blob(root,C,rel)!=rb:raise ValueError('citation: evidence record mutated at candidate '+rel)
        if _blob(root,head,rel)!=rb:raise ValueError('citation: evidence record mutated at current head '+rel)
    # E2 sidecar historical bindings must match the actual historical records (no self-declared history)
    hist=json.loads(_blob(root,B,'locales/history-equivalence.json'))
    for code,e in s['families'].get('history-master',{}).get('variants',{}).items():
        v=hist['variants'][code]
        if v['file']!=e['file'] or v['bodySha256']!=e['oldBodySha256']:raise ValueError('citation: sidecar rewrites history record '+code)
        if e.get('catalog') and (v['catalogSha256']!=e['catalog']['sha256Unchanged']):raise ValueError('citation: sidecar rewrites history catalog '+code)
    pray=json.loads(_blob(root,B,'locales/prayer-equivalence.json'))
    for code,e in s['families'].get('saint-charbel-prayers-master',{}).get('variants',{}).items():
        v=pray['groups']['saint-charbel-prayers-master']['variants'][code]
        if v['file']!=e['file'] or v['bodySha256']!=e['oldBodySha256']:raise ValueError('citation: sidecar rewrites prayer record '+code)
        if e.get('catalog') and (v['catalogSha256']!=e['catalog']['sha256Unchanged']):raise ValueError('citation: sidecar rewrites prayer catalog '+code)
    trav=json.loads(_blob(root,B,'locales/travel-equivalence.json'))
    for code,e in s['families'].get('saint-charbel-places-lebanon-travel-master',{}).get('variants',{}).items():
        v=trav['groups']['saint-charbel-places-lebanon-travel-master']['variants'][code]
        ev=v.get('reviewEvidence',{})
        if v['file']!=e['file'] or v['bodySha256']!=e['oldBodySha256']:raise ValueError('citation: sidecar rewrites travel record '+code)
        if v.get('candidateFileSha256')!=e['historicalCandidateFileSha256']:raise ValueError('citation: sidecar rewrites travel candidate pin '+code)
        if ev.get('preparedRevision')!=e['historicalPreparedRevision']:raise ValueError('citation: sidecar rewrites travel prepared revision '+code)
        if ev.get('scope')!=e['inheritedScope']:raise ValueError('citation: sidecar rewrites travel scope '+code)
        if e.get('catalog') and (v['catalogSha256']!=e['catalog']['sha256Unchanged']):raise ValueError('citation: sidecar rewrites travel catalog '+code)
    ar2=json.loads(_blob(root,B,'locales/ar2-pairing-evidence.json'))
    for slug,pg in s['families'].get('ar2',{}).get('pages',{}).items():
        row=ar2['pages'][slug]
        if row['scope']!=pg['inheritedScope'] or row['nativeReviewStatus']!=pg['nativeReviewStatus']:raise ValueError('citation: sidecar rewrites ar2 record '+slug)
        if ar2.get('sourceRevision')!=pg['inheritedSourceRevision']:raise ValueError('citation: sidecar rewrites ar2 source revision '+slug)
        if row.get('evidenceRef')!=pg.get('inheritedEvidenceRef'):raise ValueError('citation: sidecar rewrites ar2 evidence ref '+slug)
        if row['en']!=pg['en']['route'] or row['ar']!=pg['ar']['route']:raise ValueError('citation: sidecar rewrites ar2 routes '+slug)
    # H2 historical pins (travel covered family)
    for code,v in trav['groups']['saint-charbel-places-lebanon-travel-master']['variants'].items():
        ev=v.get('reviewEvidence',{});b=_blob(root,ev.get('preparedRevision',''),v['file'])
        if b is None or hashlib.sha256(b).hexdigest()!=v['candidateFileSha256']:raise ValueError('citation: historical leg broken '+code)
    # per-variant digest + blob-id spot-verification against committed B/C objects
    from i18n.reviewed_history import digest
    for fam in ('history-master','saint-charbel-prayers-master','saint-charbel-places-lebanon-travel-master'):
        for code,e in s['families'][fam]['variants'].items():
            if _sh(root,'rev-parse',f"{C}:{e['file']}")!=e['candidateBlobSha1AtC']:raise ValueError('citation: nested amendment blob id mismatch '+fam+' '+code)
            if digest(_blob(root,C,e['file']).decode())!=e['newBodySha256']:raise ValueError('citation: sidecar digest not actual C bytes '+fam+' '+code)
            if digest(_blob(root,B,e['file']).decode())!=e['oldBodySha256']:raise ValueError('citation: sidecar old digest not actual B bytes '+fam+' '+code)
    for slug,pg in s['families'].get('ar2',{}).get('pages',{}).items():
        for code,row in pg.items():
            if code in ('inheritedScope','inheritedSourceRevision','nativeReviewStatus','inheritedEvidenceRef'):continue
            if not isinstance(row,dict) or 'file' not in row:continue
            if _sh(root,'rev-parse',f"{C}:{row['file']}")!=row['candidateBlobSha1AtC']:raise ValueError('citation: ar2 nested blob id mismatch '+slug+' '+code)
            cb=_blob(root,C,row['file'])
            if hashlib.sha256(cb).hexdigest()!=row['newCandidateFileSha256']:raise ValueError('citation: ar2 candidate sha not actual C bytes '+slug+' '+code)
            if digest(cb.decode())!=row['newDigest']:raise ValueError('citation: ar2 digest not actual C bytes '+slug+' '+code)
            bb=_blob(root,B,row['file'])
            if digest(bb.decode())!=row['historicalDigest']:raise ValueError('citation: ar2 historical digest not actual B bytes '+slug+' '+code)
    # historical chain execution, isolated clean B, this process once
    hist=_historical_leg(root,B)
    return {'base':B,'candidate':C,'head':head,'tableSha256':s['table']['sha256'],'historicalLeg':hist,
            'note':'TECHNICAL CANDIDATE PROOF ONLY - not acceptance'}

# Raw-text elements and comments are masked before tag attribution; occurrences must be
# the EXACT full value of an href attribute on a real start tag - not text, not script
# strings, not comments, not data-href, not a substring of a longer value.
_RAWTEXT=re.compile(rb'<(script|style|title|textarea)\b[^>]*>[\s\S]*?</\1\s*>',re.I)
_COMMENT=re.compile(rb'<!--[\s\S]*?-->')
_ATTR=re.compile(rb'([A-Za-z_:][\w:.-]*)\s*=\s*(?:"([^"]*)"|\'([^\']*)\')')

def _scan_href_spans(blob,f,entries):
    masked=[m.span() for m in _COMMENT.finditer(blob)]+[m.span() for m in _RAWTEXT.finditer(blob)]
    def is_masked(s,e):return any(s<me and e>ms for ms,me in masked)
    for e in entries:
        needle=e['find'].encode()
        for m in re.finditer(re.escape(needle),blob):
            s,en=m.span()
            if is_masked(s,en):raise ValueError('citation: occurrence inside comment/raw-text element '+f)
            lt=blob.rfind(b'<',0,s);gt=blob.find(b'>',en)
            if lt<0 or gt<0:raise ValueError('citation: occurrence outside any tag '+f)
            if b'>' in blob[lt+1:s] or b'<' in blob[en:gt]:raise ValueError('citation: occurrence in text node '+f)
            tag=blob[lt:gt+1]
            if tag.startswith((b'</',b'<!',b'<?')):raise ValueError('citation: occurrence in non-start tag '+f)
            ok=False
            for am in _ATTR.finditer(tag):
                name=am.group(1).lower()
                gi=2 if am.group(2) is not None else 3
                vs,ve=am.start(gi),am.end(gi)
                if lt+vs<=s and en<=lt+ve:
                    if name!=b'href':raise ValueError('citation: occurrence in non-href attribute '+f)
                    if tag[vs:ve]!=needle or lt+vs!=s or lt+ve!=en:raise ValueError('citation: occurrence is a substring of the href value '+f)
                    ok=True
            if not ok:raise ValueError('citation: occurrence not an exact quoted href value '+f)

def _historical_leg(root,B):
    """Execute clean-B validator chain once per process: isolated full-history checkout,
    locked deps, B's own tooling. Fails closed on any missing object/dep/validator."""
    tmp=tempfile.mkdtemp(prefix='citation-histB-')
    try:
        subprocess.run(['git','clone','--no-hardlinks','--quiet',f'file://{root}',tmp],check=True)
        subprocess.run(['git','-C',tmp,'checkout','--quiet','--detach',B],check=True)
        if _sh(tmp,'rev-parse','HEAD')!=_sh(root,'rev-parse',B):raise ValueError('citation: historical leg HEAD != B')
        if _sh(tmp,'status','--porcelain')!='':raise ValueError('citation: historical leg dirty')
        if _sh(tmp,'cat-file','-t','19845304893719bcdee5864fb31fd3c3e043e386')!='commit':raise ValueError('citation: historical ancestor missing')
        npm=subprocess.run(['npm','ci','--ignore-scripts','--no-audit','--no-fund'],cwd=tmp,capture_output=True)
        if npm.returncode:raise ValueError('citation: historical leg deps: '+npm.stderr.decode()[-300:])
        receipts={'commands':[],'base':B}
        for cmd in (['python3','scripts/qa/check_i18n_policy.py'],['python3','scripts/qa/probe_partial_build.py']):
            r=subprocess.run(cmd,cwd=tmp,capture_output=True)
            receipts['commands'].append({'cmd':cmd,'exit':r.returncode,'toolSha1':_sh(tmp,'rev-parse',f'HEAD:{cmd[1]}'),
                'lockSha256':hashlib.sha256((Path(tmp)/'package-lock.json').read_bytes()).hexdigest()})
            if r.returncode:raise ValueError('citation: historical leg validator failed: '+' '.join(cmd)+'\n'+r.stdout.decode()[-400:]+r.stderr.decode()[-400:])
        return receipts
    finally:
        shutil.rmtree(tmp,ignore_errors=True)
