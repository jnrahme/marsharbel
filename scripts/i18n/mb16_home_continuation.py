"""Finite MB16 generated footer and index-only home-alternate preimages.

No memo, no editable-export qualification, no pin refresh, no generic stripping.
This is BUILD-ONLY reconstruction, not native evidence qualification. It permits
an exact generated candidate before commit. Citation prove independently requires
raw native HEAD == disk for every proof input before it can qualify evidence.
Callers still compare the reconstructed bytes to their original owning pin.
"""
import hashlib
import json
from pathlib import Path
import subprocess

BASE = '607e3a679e8bcf61bb60153686baafb87835e44c'
RECORD = 'locales/mb16-home-continuation.json'
MODULE = 'scripts/i18n/mb16_home_continuation.py'
PATHS = frozenset({'index.html','history.html','visit-annaya.html','22nd-of-the-month.html',
                   'rosary-intro.html','saint-charbel-novena.html','saint-charbel-prayers.html'})
# Literal ordered identity, not a registry-selected publication grant.
HOMES = (
 ('en','/','English','ltr'),('ar','/ar/','العربية','rtl'),('fr','/fr/','Français','ltr'),
 ('es','/es/','Español','ltr'),('pt','/pt/','Português','ltr'),('it','/it/','Italiano','ltr'),
 ('de','/de/','Deutsch','ltr'),('pl','/pl/','Polski','ltr'),('ru','/ru/','Русский','ltr'),
 ('hi','/hi/','हिन्दी','ltr'),('th','/th/','ไทย','ltr'))
CHINESE = ('zh-Hans','/zh-Hans/','简体中文','ltr')

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def footer(homes, sorted_attrs=True):
    if sorted_attrs:
        nav='<nav aria-label="Languages" class="footer-locales">'
        links=[f'<a dir="{direction}" href="{href}" hreflang="{code}" lang="{code}">{name}</a>' for code,href,name,direction in homes]
    else:
        nav='<nav class="footer-locales" aria-label="Languages">'
        links=[f'<a href="{href}" hreflang="{code}" lang="{code}" dir="{direction}">{name}</a>' for code,href,name,direction in homes]
    return ('<!-- i18n-navigation:start -->\n'+nav+' <span aria-hidden="true">-</span> '.join(links)+'</nav>\n<!-- i18n-navigation:end -->').encode()

def alternates(homes):
    lines=[f'<link rel="alternate" hreflang="{code}" href="https://marsharbel.com{href}" />' for code,href,_,_ in homes]
    lines.append('<link rel="alternate" hreflang="x-default" href="https://marsharbel.com/" />')
    return ('<!-- i18n-alternates:start -->\n'+'\n'.join(lines)+'\n<!-- i18n-alternates:end -->').encode()

def span(raw, marker, section):
    start=b'<!-- '+marker+b':start -->';end=b'<!-- '+marker+b':end -->'
    if raw.count(start)!=1 or raw.count(end)!=1:
        raise ValueError('MB16: missing or duplicate '+marker.decode())
    a=raw.index(start);z=raw.index(end)+len(end)
    if a>=z or not(raw.rfind(b'<'+section,0,a)>=0 and raw.find(b'</'+section,a)>=z):
        raise ValueError('MB16: moved '+marker.decode())
    return a,z

def derive(path, original, footer_form=None, add_alternate=False):
    if path not in PATHS:raise ValueError('MB16: path outside finite set')
    a,z=span(original,b'i18n-navigation',b'footer')
    if original[a:z]!=footer(HOMES):raise ValueError('MB16: old footer differs from explicit serializer')
    edits=[]
    if footer_form is not None:
        if footer_form not in ('sorted','generator'):raise ValueError('MB16: unknown serializer')
        edits.append((a,z,footer(HOMES+(CHINESE,),footer_form=='sorted')))
    if add_alternate:
        if path!='index.html':raise ValueError('MB16: alternates are index-only')
        a,z=span(original,b'i18n-alternates',b'head')
        if original[a:z]!=alternates(HOMES):raise ValueError('MB16: old alternates differ')
        edits.append((a,z,alternates(HOMES+(CHINESE,))))
    for a,z,value in sorted(edits,reverse=True):original=original[:a]+value+original[z:]
    return original

def verify_delta(path, original, current):
    # Candidate equality to fixed reconstructions compares ALL outside-span bytes.
    for form in (None,'sorted','generator'):
        for alternate in ((False,True) if path=='index.html' else (False,)):
            if current==derive(path,original,form,alternate):return original
    raise ValueError('MB16: candidate differs outside exact generated home blocks')

def old_home_blocks(path, raw):
    a,z=span(raw,b'i18n-navigation',b'footer')
    if raw[a:z]!=footer(HOMES):return False
    if path=='index.html':
        a,z=span(raw,b'i18n-alternates',b'head')
        if raw[a:z]!=alternates(HOMES):return False
    return True

def git(root,*args):
    return subprocess.check_output(['git','-C',str(root),*args],stderr=subprocess.DEVNULL)

def reconstruct(path, current):
    """Invert only the finite footer and index-alternate delta.

    This is not a native proof. A git-less export still cannot approve any
    other byte; verify_delta rejects everything outside those spans.
    """
    if path not in PATHS:
        return current
    if old_home_blocks(path, current):
        return current
    a, z = span(current, b'i18n-navigation', b'footer')
    block = current[a:z]
    restored = None
    for form in ('sorted', 'generator'):
        if block == footer(HOMES + (CHINESE,), form == 'sorted'):
            restored = current[:a] + footer(HOMES) + current[z:]
            break
    if restored is None:
        raise ValueError('MB16: candidate differs outside exact generated home blocks')
    if path == 'index.html':
        a, z = span(restored, b'i18n-alternates', b'head')
        alt = restored[a:z]
        if alt == alternates(HOMES + (CHINESE,)):
            restored = restored[:a] + alternates(HOMES) + restored[z:]
        elif alt != alternates(HOMES):
            raise ValueError('MB16: candidate differs outside exact generated home blocks')
    if verify_delta(path, restored, current) != restored:
        raise ValueError('MB16: candidate differs outside exact generated home blocks')
    return restored

def continue_published_footer(path, raw):
    """Reapply the finite Chinese language-list edit after a preimage render.

    The English serializer is byte-exact. A translated footer keeps its own
    language name on the nav and only gains the missing 简体中文 link.
    """
    if path not in PATHS or not isinstance(raw, (bytes, bytearray)):
        return raw
    try:
        a, z = span(raw, b'i18n-navigation', b'footer')
    except ValueError:
        a = z = None
    if a is not None and raw[a:z] == footer(HOMES):
        return raw[:a] + footer(HOMES + (CHINESE,), True) + raw[z:]
    start = raw.find(b'class="footer-locales"')
    if start < 0:
        return raw
    end = raw.find(b'</nav>', start)
    if end < 0 or b'href="/zh-Hans/"' in raw[start:end]:
        return raw
    link = ' <span aria-hidden="true">-</span> <a dir="ltr" href="/zh-Hans/" hreflang="zh-Hans" lang="zh-Hans">简体中文</a>'.encode()
    return raw[:end] + link + raw[end:]

def build_preimage(root, path, current):
    """Native proof when git can bind HEAD; exact reconstruction otherwise."""
    try:
        return preimage(root, path, current)
    except ValueError as error:
        message = str(error)
        # A locale-catalog fixture copies masters but not this proof module.
        # A missing module is not a symlink attack; only the exact footer
        # delta may be rebuilt. preimage() itself still rejects symlinks.
        if 'native proof unavailable' not in message and not message.startswith('continuation: nonregular proof input '):
            raise
        return reconstruct(path, current)

def preimage(root,path,current):
    if path not in PATHS:return current
    root=Path(root)
    # Existing unrelated trees and old test fixtures do not acquire a new grant.
    if not (root/RECORD).exists() and not (root/RECORD).is_symlink():return current
    from i18n.seo_continuations import require_regular_inputs
    inputs=[RECORD,MODULE,'locales/registry.json','scripts/build-international.py','scripts/i18n/same_page_injection.py',path]
    require_regular_inputs(root,inputs)
    record=json.loads((root/RECORD).read_bytes())
    if set(record)!={'base','homes','paths','registrySha256','generatorSha256','controlSha256'}:
        raise ValueError('MB16: record fields differ')
    if record.get('base')!=BASE or set(record.get('paths',{}))!=PATHS or record.get('homes')!=[list(x)for x in HOMES]:
        raise ValueError('MB16: record scope drift')
    try:
        head=git(root,'rev-parse','HEAD').decode().strip()
        subprocess.run(['git','-C',str(root),'merge-base','--is-ancestor',BASE,head],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        for rel in inputs[:-1]:
            if (root/rel).read_bytes()!=git(root,'show',head+':'+rel):raise ValueError('MB16: proof input differs from native HEAD '+rel)
        for rel,key in [('locales/registry.json','registrySha256'),('scripts/build-international.py','generatorSha256'),('scripts/i18n/same_page_injection.py','controlSha256')]:
            bound=(root/rel).read_bytes()
            if rel=='locales/registry.json':
                from i18n.secret_prayers_registry_continuation import registry_preimage
                bound=registry_preimage(root,bound)
            if rel=='scripts/i18n/same_page_injection.py':
                from i18n.secret_prayers_registry_continuation import control_preimage
                bound=control_preimage(root,bound)
            if sha(bound)!=record.get(key):raise ValueError('MB16: generator/registry binding differs '+rel)
        registry=json.loads((root/'locales/registry.json').read_bytes())
        expected=list(HOMES)+( [CHINESE] )
        observed=[(c,registry['locales'][c]['home'],registry['locales'][c]['nativeName'],registry['locales'][c]['direction'])for c in registry['homePublicationLocales']]
        if observed!=expected:raise ValueError('MB16: registry home identities drift')
        original=git(root,'show',BASE+':'+path)
        if sha(original)!=record['paths'][path]:raise ValueError('MB16: original fixed-base hash drift')
        committed=git(root,'show',head+':'+path)
        disk=(root/path).read_bytes()
        # No MB16 change is not a proof grant. Leave every byte intact for the
        # owning pin / independently activated continuation to judge. This does
        # not normalize away FAQ, schema, prayer, metadata or content edits.
        if all(old_home_blocks(path,raw) for raw in (committed,disk,current)):
            return current
        # Once ANY home block changes, the complete fixed-base delta must hold
        # independently for HEAD, disk and caller. Mixed continuations fail.
        if path == 'index.html':
            from i18n.mb16_saint_home import restore, reapply
            verify_delta(path, original, restore(root, original, committed, head))
            verify_delta(path, original, restore(root, original, disk))
            verify_delta(path, original, restore(root, original, current))
            return reapply(original, current)
        verify_delta(path,original,committed)
        verify_delta(path,original,disk)
        return verify_delta(path,original,current)
    except (subprocess.CalledProcessError,OSError) as error:
        raise ValueError('MB16: native proof unavailable; exports cannot qualify continued bytes') from error
