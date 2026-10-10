"""Bounded Annaya hero amendment. Independent reviewer activates exact pins."""
import hashlib,json,re
from bs4 import BeautifulSoup
from i18n.reviewed_history import digest
FAMILIES={'annaya-tour-travel-master':{'en','de','ru'},'annaya-tour-zh-travel-master':{'en','zh-Hans'}}
SCHEMA='annaya-hero-v1'
SCOPE='hero-alt-credit-scrim'
# Deliberately unset. Only the independent reviewer can activate a reviewed table.
REVIEW_TABLE_SHA256='fcc33fcd5d8a117c34f1828fe43f1687d0e53157c178f187090a5784650ed253'
TABLE='locales/annaya-hero-review-refs.json'
def sha(text):return hashlib.sha256(text.encode()).hexdigest()
def validate_group(family,group):
    if family not in FAMILIES or group.get('evidenceSchema')!=SCHEMA or set(group.get('variants',{}))!=FAMILIES[family]:
        raise ValueError('Annaya amendment family/schema/membership mismatch')
    if any(k in group for k in ('renderedReviewStatus','catalogReview','renderedReview')):raise ValueError('Annaya group-level review refused')
def remainder(text):
    soup=BeautifulSoup(text,'html.parser');main=soup.select('main')
    if len(main)!=1:raise ValueError('Annaya unique main required')
    hero=main[0].select(':scope > section')
    if not hero or not set(hero[0].get('class',[])) & {'hero','annaya-tour-hero'}:raise ValueError('Annaya exact lead hero required')
    hero[0].decompose()
    return str(main[0])
def validate_variant(root,family,code,variant,text,final=True):
    from i18n.travel_variant_evidence import blob
    if family not in FAMILIES or code not in FAMILIES[family]:raise ValueError('Annaya extra locale/family')
    if REVIEW_TABLE_SHA256 is None:raise ValueError('Annaya review table unset')
    raw=(root/TABLE).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=REVIEW_TABLE_SHA256:raise ValueError('Annaya reviewer table edited')
    table=json.loads(raw)
    if table.get('schema')!=SCHEMA or set(table.get('groups',{}))!=set(FAMILIES):raise ValueError('Annaya review table membership')
    file='annaya-tour.html' if code=='en' else code+'/annaya-tour.html'
    if any(set(table['groups'][f])!=codes for f,codes in FAMILIES.items()):raise ValueError('Annaya per-family review membership')
    record=table['groups'][family][code]
    if variant.get('file')!=file or variant.get('path')!='/'+file.removesuffix('.html'):raise ValueError('Annaya route mismatch')
    ev=variant.get('reviewEvidence',{})
    if ev.get('amendmentSchema')!=SCHEMA:raise ValueError('Annaya evidence schema missing')
    if ev!=record:raise ValueError('Annaya unapproved evidence')
    if ev.get('state')!='approved' or ev.get('scope')!=SCOPE or ev.get('nativeReviewStatus')!='not-certified':raise ValueError('Annaya review state/scope/native mismatch')
    if not ev.get('renderedReview') or not ev.get('catalogReview'):raise ValueError('Annaya independent review refs required')
    prepared=ev.get('preparedRevision','');base=ev.get('baseRevision','')
    # Squash-safe: preparedRevision records review provenance, not an object
    # dependency. Released disk bytes are checked against the approved digests.
    if not re.fullmatch(r'[a-f0-9]{40}',prepared):raise ValueError('Annaya prepared revision invalid')
    candidate=(root/file).read_text();before=blob(root,base,file)
    if sha(candidate)!=ev.get('candidateFileSha256') or sha(candidate)!=variant.get('candidateFileSha256'):raise ValueError('Annaya prepared candidate digest mismatch')
    if digest(candidate)!=ev.get('bodySha256') or digest(candidate)!=variant.get('bodySha256') or digest(text)!=digest(candidate):raise ValueError('Annaya candidate/current main drift')
    if remainder(before)!=remainder(candidate):raise ValueError('Annaya non-hero main changed')
    master=(root/'annaya-tour.html').read_text()
    if sha(master)!=ev.get('masterSha256'):raise ValueError('Annaya master drift')
    if final and sha(text)!=sha(candidate):raise ValueError('Annaya post-review full-file drift')
    catalogs={f'locales/en/{family}-bindings.json',f'locales/{code}/{family}-copy.json'}
    # The shared EN row binds both families; each locale row binds its owner.
    if code=='en':catalogs={f'locales/en/{f}-{suffix}.json' for f in FAMILIES for suffix in ('bindings','copy')}
    if set(ev.get('catalogDigests',{}))!=catalogs:raise ValueError('Annaya catalog inventory mismatch')
    for path,value in ev['catalogDigests'].items():
        if hashlib.sha256((root/path).read_bytes()).hexdigest()!=value:raise ValueError('Annaya catalog digest drift')
    # Runtime proof shape stays scoped-travel-variant so the language resolver verifies the twins.
    return {'type':'scoped-travel-variant','state':'approved','scope':SCOPE,'candidateFileSha256':sha(candidate),'reviewedContentSha256':digest(candidate),'nativeReviewStatus':'not-certified','evidenceRef':ev['renderedReview']}
