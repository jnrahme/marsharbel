"""Fail-closed C-0016 per-variant evidence; never native certification."""
import hashlib
import json
import re
import subprocess
from pathlib import Path
from bs4 import BeautifulSoup
from i18n.reviewed_history import digest

STAGE = '6701907d05aedc47b7942ada6a14cfc6470c31ce'
REVIEW_REFS_SHA256 = 'fd6d60cf162bbb66041dafc7378fcf7dc619f5658102bbd190b778276b8e4a14'
SLUGS = {'travel','annaya-tour','bekaa-kafra','bkerke-maronite-patriarchate',
         'cedars-of-god-lebanon','our-lady-of-lebanon-harissa','qadisha-valley',
         'qannoubine-monastery','qozhaya-monastery','saint-charbel-hermitage',
         'saint-charbel-places-lebanon','saint-charbel-trail'}
SCOPED = 'chrome-label delta only (Media group values), body main hash unchanged from the pinned stage commit.'


def blob(root, ref, file):
    if not re.fullmatch(r'[a-f0-9]{40}', ref) or Path(file).is_absolute() or '..' in Path(file).parts:
        raise ValueError('Unsafe evidence provenance')
    try:
        subprocess.run(['git','merge-base','--is-ancestor',ref,'HEAD'],cwd=root,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        return subprocess.check_output(['git','show',ref+':'+file],cwd=root,stderr=subprocess.DEVNULL).decode()
    except subprocess.CalledProcessError as exc:
        raise ValueError('Missing/nonancestor evidence provenance') from exc


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def without_ru(text, slug):
    soup = BeautifulSoup(text,'html.parser')
    nodes = soup.select('head link[hreflang="ru"]')
    if len(nodes)>1 or any(n.get('href')!='https://marsharbel.com/ru/'+slug or n.get('rel')!=['alternate'] for n in nodes):
        raise ValueError('Wrong RU hreflang')
    pattern = re.compile(r'<link\b[^>]*\bhreflang="ru"[^>]*?/>(?:\n)?')
    matches = pattern.findall(text)
    if len(matches)!=len(nodes):raise ValueError('Non-isolated RU hreflang')
    isolated=re.compile(r'^[ \t]*<link\b[^>]*\bhreflang="ru"[^>]*?/>[ \t]*\n',re.M)
    return pattern.sub('',isolated.sub('',text))


def label_delta(before, after, code, slug):
    if digest(before)!=digest(after):raise ValueError('DE/HI main drift')
    before,after = without_ru(before,slug),without_ru(after,slug)
    def mask(text, target):
        soup=BeautifulSoup(text,'html.parser')
        groups=soup.select('header > div > nav > div:nth-of-type(6)')
        if len(groups)!=1 or len(groups[0].select('a'))!=4:raise ValueError('Media group shape changed')
        expected = ('Media','Music','Video','Galerie' if slug=='qadisha-valley' else 'Gallery')
        if target:expected=('Media','Music','Video','Galerie') if code=='de' else ('मीडिया','संगीत','वीडियो','चित्र संग्रह')
        if code=='hi' and not target:expected=('Media','Music','Video','Gallery')
        # Locate exact existing header fragment in the raw serializer. No generic
        # reserialization: only those four direct anchor text scalars are masked.
        header=re.search(r'<header\b[^>]*>.*?</header>',text,re.S)
        if not header:raise ValueError('Missing header')
        raw=header[0]
        for anchor,label in zip(groups[0].select('a'),expected):
            if anchor.get_text(strip=True)!=label:raise ValueError('Wrong Media label')
            token='>'+label+'<'
            if raw.count(token)!=1:raise ValueError('Ambiguous Media label scalar')
            raw=raw.replace(token,'>C0016_LABEL<',1)
        return text[:header.start()]+raw+text[header.end():]
    if mask(before,False)!=mask(after,True):raise ValueError('Non-label/hreflang byte delta')


def validate_group(family, group):
    slug=family.removesuffix('-travel-master')
    if slug not in SLUGS or group.get('evidenceSchema')!='scoped-variants-v1':
        raise ValueError('New-family evidence schema missing')
    if any(k in group for k in ('renderedReviewStatus','catalogReview','renderedReview')):
        raise ValueError('Group-level review laundering')
    expected={'en','de','ru','hi'} if slug=='travel' else {'en','de','ru'}
    if set(group['variants'])!=expected:raise ValueError('Scoped Travel membership mismatch')


def isolated_en_ru(text, slug):
    clean=without_ru(text,slug)
    if 'hreflang="ru"' in text:
        found=re.findall(r'^[ \t]*<link\b[^>]*\bhreflang="ru"[^>]*?/>[ \t]*\n',text,re.M)
        if len(found)!=1:raise ValueError('EN RU hreflang must be isolated line')
    return clean


def validate_variant(root, family, code, variant, text, final=True):
    slug=family.removesuffix('-travel-master')
    if slug not in SLUGS or code not in ({'en','de','ru','hi'} if slug=='travel' else {'en','de','ru'}):
        raise ValueError('Wrong keyed variant membership')
    file=(slug+'.html') if code=='en' else code+'/'+slug+'.html'
    if variant['file']!=file or variant['path']!='/'+file.removesuffix('.html'):
        raise ValueError('Wrong variant route')
    evidence=variant.get('reviewEvidence',{})
    if evidence.get('stageRevision')!=STAGE:raise ValueError('Wrong pinned stage')
    candidate=blob(root,evidence.get('preparedRevision',''),file)
    if sha(candidate)!=evidence.get('candidateFileSha256') or variant.get('candidateFileSha256')!=sha(candidate):
        raise ValueError('Candidate hash not actual prepared bytes')
    if final and without_ru(candidate,slug)!=without_ru(text,slug):raise ValueError('Post-review candidate drift')
    if digest(candidate)!=variant['bodySha256'] or digest(text)!=variant['bodySha256']:
        raise ValueError('Candidate/current main drift')
    if code=='en':
        if evidence.get('state')!='carried' or evidence.get('scope')!='stage bytes carried; no new review':raise ValueError('EN must be carried')
        if isolated_en_ru(blob(root,STAGE,file),slug)!=isolated_en_ru(candidate,slug):raise ValueError('Carried stage drift')
        if final:isolated_en_ru(text,slug)
        if any(k in evidence for k in ('renderedReview','catalogReview')):raise ValueError('Carried cannot claim new review')
    else:
        refs_raw=(root/'locales/travel-c0016-review-refs.json').read_bytes()
        if hashlib.sha256(refs_raw).hexdigest()!=REVIEW_REFS_SHA256:
            raise ValueError('Reviewer reference table edited')
        refs=json.loads(refs_raw)
        record=refs.get(file)
        if not record or evidence.get('state')!='approved':raise ValueError('Missing approved review record')
        for key in ('candidateFileSha256','scope','renderedReview','catalogReview'):
            if evidence.get(key)!=record[key]:raise ValueError('Unknown scoped reviewer evidence')
        if code in ('de','hi'):
            if evidence['scope']!=SCOPED:raise ValueError('Wrong chrome review scope')
            label_delta(blob(root,STAGE,file),candidate,code,slug)
    if evidence.get('nativeReviewStatus')!='not-certified':raise ValueError('False native certification')
    return {'type':'scoped-travel-variant','state':evidence['state'],
            'scope':evidence['scope'],'candidateFileSha256':sha(candidate),
            'reviewedContentSha256':variant['bodySha256'],'nativeReviewStatus':'not-certified',
            'evidenceRef':evidence.get('renderedReview','stage-'+STAGE)}


def validate_final_outputs(root, texts):
    """Final injection boundary: full-file continuity plus actual final main pins."""
    record=root/'locales/travel-equivalence.json'
    if not record.exists():return
    for family,group in json.loads(record.read_text())['groups'].items():
        if group.get('evidenceSchema')!='scoped-variants-v1':continue
        validate_group(family,group)
        for code,variant in group['variants'].items():
            file=root/variant['file']
            text=texts[file] if file in texts else file.read_text()
            validate_variant(root,family,code,variant,text,final=True)
