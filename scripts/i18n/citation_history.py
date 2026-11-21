"""Reviewed citation-history hydration: offline, hash-bound import of the C2 graph.

The amendment candidate commit C2 (REVIEWED_C below) is a reviewed local-preparation
object that no remote ref advertises. Fresh native checkouts - and every file:// clone
made from them, including the proof checker's tamper fixtures - therefore lack it, and
the citation proof's object legs fail closed with 'missing objects'. This module
hydrates EXACTLY that reviewed graph from a committed, hash-pinned, offline artifact
(locales/citation-maintenance/candidate-C2.bundle.b64) into the local git object store
only, before any proof leg looks the objects up.

Contract:
- Offline and deterministic: no network, no credentials, no remote interaction, and no
  ref, index, worktree or config writes (git bundle unbundle imports objects only).
- Fail closed: artifact absence, non-regular-file, non-canonical base64 framing, any
  hash/size mismatch, an unreadable git repository, a missing reviewed base, or any
  divergence of the bundle's heads/prerequisite/imported identity from the reviewed
  constants below raises ValueError. There is no fallback and no degraded path.
- Never import arbitrary sidecar-named refs, paths or URLs: hydration runs only when
  the sidecar's base/candidate binding equals the fixed reviewed identifiers. A sidecar
  naming anything else is left entirely to the proof's own named rejection branches
  (this preserves, for example, the candidate-drift control's reconstruction branch).
- The artifact is re-validated on EVERY call, even when C2 is already present, so a
  tampered artifact can never hide behind a warm object store. Combined with the
  artifact's membership in the proof's memo key and W0 worktree-fidelity set, an
  artifact mutation is always caught.
"""
import base64, hashlib, os, shutil, stat, subprocess, tempfile
from pathlib import Path

ARTIFACT='locales/citation-maintenance/candidate-C2.bundle.b64'
REVIEWED_B='7961151d3d8663e5e97e6f9f2f4aa73215b95468'
REVIEWED_C='69a74a3d4d011b7893467bcf4f051b6f52076724'
REVIEWED_TREE='0b21be27e66279a3ad557377cc83ac0e8c6a6f9e'
REVIEWED_REF='refs/heads/review-citC2'
BUNDLE_BYTES=122224
BUNDLE_SHA256='ec68b80694e1bbd4760414063ba62dac249e70fb7f12c6e1614bf8ed0c8b9ccc'
ARTIFACT_SHA256='2d86baa2ef532dee0c820e2a596ecc97f491b01afba894757152eb53e3d3915d'

def _git(root,*a):
    return subprocess.check_output(['git','-C',str(root)]+list(a),stderr=subprocess.DEVNULL).decode().strip()

def _cat(root,rev):
    try:return _git(root,'cat-file','-t',rev)
    except subprocess.CalledProcessError:return None

def _load_artifact(root):
    """Read and fully validate the committed artifact; return the decoded bundle bytes."""
    e='citation history artifact: '
    p=Path(root)/ARTIFACT
    if not os.path.lexists(str(p)):raise ValueError(e+'missing '+ARTIFACT)
    if not stat.S_ISREG(os.lstat(str(p)).st_mode):raise ValueError(e+'not a regular file '+ARTIFACT)
    raw=p.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=ARTIFACT_SHA256:raise ValueError(e+'text sha256 mismatch')
    try:decoded=base64.b64decode(raw.replace(b'\n',b''),validate=True)
    except Exception:raise ValueError(e+'non-canonical base64')
    if base64.encodebytes(decoded)!=raw:raise ValueError(e+'non-canonical base64 framing')
    if len(decoded)!=BUNDLE_BYTES:raise ValueError(e+'decoded size mismatch')
    if hashlib.sha256(decoded).hexdigest()!=BUNDLE_SHA256:raise ValueError(e+'decoded bundle sha256 mismatch')
    return decoded

def _assert_identity(root):
    if _cat(root,REVIEWED_C)!='commit':raise ValueError('citation history: missing objects (reviewed C2 absent after import)')
    if _git(root,'rev-parse',REVIEWED_C+'^')!=REVIEWED_B:raise ValueError('citation history: C2 parent != reviewed base')
    if _git(root,'rev-parse',REVIEWED_C+'^{tree}')!=REVIEWED_TREE:raise ValueError('citation history: C2 tree != reviewed tree')

def ensure_history(root,s):
    """Validate the reviewed artifact (always) and, when the sidecar binds the reviewed
    base/candidate and C2 is absent from root's object store, import the reviewed graph.

    Returns True when the reviewed graph is present afterwards, False when the sidecar
    names a different binding (nothing imported; the proof's own branches judge it).
    """
    decoded=_load_artifact(root)
    cand=s.get('candidate',{}) if isinstance(s,dict) else {}
    if not (s.get('base')==REVIEWED_B and cand.get('commit')==REVIEWED_C and cand.get('tree')==REVIEWED_TREE):
        return False
    if _cat(root,REVIEWED_C)=='commit':
        _assert_identity(root)
        return True
    try:_git(root,'rev-parse','--git-dir')
    except subprocess.CalledProcessError:
        raise ValueError('citation history: git repository unreadable; refusing to hydrate')
    if _cat(root,REVIEWED_B)!='commit':
        raise ValueError('citation history: missing objects (reviewed base absent)')
    tmp=tempfile.mkdtemp(prefix='cithist-')
    os.chmod(tmp,0o700)
    try:
        bp=Path(tmp)/'reviewed-C2.bundle'
        with os.fdopen(os.open(str(bp),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb') as f:
            f.write(decoded)
        heads=_git(root,'bundle','list-heads',str(bp))
        if heads!=REVIEWED_C+' '+REVIEWED_REF:
            raise ValueError('citation history: bundle heads != reviewed ref :: '+heads)
        verify=_git(root,'bundle','verify',str(bp))
        if 'requires' not in verify or REVIEWED_B not in verify:
            raise ValueError('citation history: bundle prerequisite != reviewed base')
        _git(root,'bundle','unbundle',str(bp))
    finally:
        shutil.rmtree(tmp,ignore_errors=True)
    _assert_identity(root)
    return True
