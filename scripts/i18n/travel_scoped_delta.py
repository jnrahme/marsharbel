"""Parsed, raw-byte scoped DE/HI chrome + RU-head delta gate.
Label pairs derive only from stage and the hash-pinned reviewer candidate.
"""
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from bs4 import BeautifulSoup

class Tokens(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=False);self.text=text;self.tokens=[]
        self.lines=[0]
        for i,c in enumerate(text):
            if c=='\n':self.lines.append(i+1)
        self.feed(text)
    def source_position(self):
        line,col=self.getpos();return self.lines[line-1]+col
    def handle_starttag(self,tag,attrs):
        start=self.source_position();self.tokens.append(('tag',start,start+len(self.get_starttag_text()),tag,attrs))
    handle_startendtag=handle_starttag
    def handle_data(self,data):
        start=self.source_position();self.tokens.append(('data',start,start+len(data),data,None))

def parsed_without_ru(text,slug,required=False):
    soup=BeautifulSoup(text,'html.parser');nodes=soup.select('link[hreflang="ru"]')
    if len(nodes)>1 or (required and len(nodes)!=1):raise ValueError('Missing/duplicate RU line')
    if not nodes:return text
    node=nodes[0]
    if not node.find_parent('head') or dict(node.attrs)!={'rel':['alternate'],'hreflang':'ru','href':'https://marsharbel.com/ru/'+slug}:
        raise ValueError('Wrong RU head attributes')
    starts=[t for t in Tokens(text).tokens if t[0]=='tag' and t[3]=='link' and dict(t[4]).get('hreflang')=='ru']
    if len(starts)!=1:raise ValueError('Ambiguous RU source tag')
    _,start,end,_,_=starts[0]
    if '\n' in text[start:end] or '\r' in text[start:end]:raise ValueError('RU tag must occupy one source line')
    left=text.rfind('\n',0,start)+1;right=text.find('\n',end)
    if right>=0 and not text[left:start].strip() and not text[end:right].strip():start,end=left,right+1
    elif text[end:end+1]=='\n':end+=1
    return text[:start]+text[end:]

def scalars(text):
    soup=BeautifulSoup(text,'html.parser');groups=soup.select('header > div > nav > div:nth-of-type(6)')
    if len(groups)!=1 or len(groups[0].select('a'))!=4:raise ValueError('Media anchor group shape')
    tokens=Tokens(text).tokens;lines=Tokens(text).lines;out=[]
    for a in groups[0].select('a'):
        start=lines[a.sourceline-1]+a.sourcepos
        tag=next((t for t in tokens if t[0]=='tag' and t[1]==start),None)
        if not tag or tag[3]!='a':raise ValueError('Anchor source location')
        # Only the existing first direct text scalar. Qualifier spans and all
        # following text/markup stay raw and are never masked.
        data=next((t for t in tokens if t[1]==tag[2] and t[0]=='data'),None)
        if not data or not data[3].strip():raise ValueError('Missing direct Media label')
        out.append((data[1],data[2],data[3]))
    return out

def classified_delta(before,after,slug,pairs):
    before=parsed_without_ru(before,slug);after=parsed_without_ru(after,slug,required=True)
    b,a=scalars(before),scalars(after)
    if len(pairs)!=4:raise ValueError('Pinned label table shape')
    for old,new,pair in zip(b,a,pairs):
        if (old[2],new[2]) not in (tuple(pair),(pair[1],pair[1])):raise ValueError('Off-table Media label')
    def masked(text,items):
        for start,end,value in reversed(items):text=text[:start]+'C0016_LABEL'+text[end:]
        return text
    if masked(before,b)!=masked(after,a):raise ValueError('Non-label/head byte change')

def scoped_delta(root,before,after,code,slug,variant):
    from i18n.travel_variant_evidence import REVIEW_REFS_SHA256,STAGE,SCOPED,blob
    raw=(root/'locales/travel-c0016-review-refs.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=REVIEW_REFS_SHA256:raise ValueError('Reviewer table edited')
    file=code+'/'+slug+'.html';record=json.loads(raw).get(file);evidence=variant['reviewEvidence']
    if code not in ('de','hi') or not record or record['scope']!=SCOPED:raise ValueError('Unreviewed label scope')
    candidate=blob(root,evidence['preparedRevision'],file)
    if hashlib.sha256(candidate.encode()).hexdigest()!=record['candidateFileSha256'] or evidence['candidateFileSha256']!=record['candidateFileSha256']:
        raise ValueError('Label table source not pinned reviewer candidate')
    stage=blob(root,STAGE,file)
    pairs=[(x[2],y[2]) for x,y in zip(scalars(stage),scalars(candidate))]
    classified_delta(before.decode(),after.decode(),slug,pairs)
