import sys,json,shutil,tempfile,importlib.util,copy,re,difflib
from collections import Counter
from unittest.mock import patch
from bs4 import BeautifulSoup
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'))
from i18n.catalog import read_json,load_catalog,PRAYER_FAMILIES
from i18n.make_bindings import build
# Production proof runs first on the real git-backed root. No fixture patches.
spec=importlib.util.spec_from_file_location('production_probe_builder',R/'scripts/build-international.py')
production_builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(production_builder)
production=production_builder.outputs(R)
for file,text in production.items():
 assert file.is_file(),'Missing production output: '+str(file.relative_to(R))
 assert file.read_text()==text,'Production build drift: '+str(file.relative_to(R))
original_registry=read_json(R/'locales/registry.json')
print('PRODUCTION LEG real validators + committed-byte equality',len(production))
# Build synthetic capability world in isolated copy, never production writes.
temp=tempfile.TemporaryDirectory();T=Path(temp.name);shutil.copytree(R,T,dirs_exist_ok=True,ignore=shutil.ignore_patterns('.git','node_modules'))
r=read_json(T/'locales/registry.json');r['locales']['zz']={'nativeName':'Test','direction':'ltr','ogLocale':'zz_ZZ','selectorAliases':[],'slugs':{},'capabilities':{'home':False,'topicGuides':[],'mirrorTabs':['travel'],'runtime':True,'selectorCopy':True}};r['ogLocaleOrder'].append('zz');(T/'locales/zz').mkdir()
for f in ['common','runtime','encyclopedia-trail','travel','share']:
 source=T/f'locales/de/{f}.json';shutil.copyfile(source,T/f'locales/zz/{f}.json')
(T/'locales/zz/pages.json').write_text('{}\n')
cp=read_json(T/'locales/same-page-copy.json');cp['zz']=dict(cp['de'])
for v in cp.values():v['names']={**v['names'],'zz':'Test'}
(T/'locales/same-page-copy.json').write_text(json.dumps(cp,ensure_ascii=False))
for path in ['/travel',*read_json(T/'locales/travel-routes.json')['destinations']]:
 page=path[1:];family='test-'+page;# actual source binding generated using fixture-local module ROOT
 import i18n.make_bindings as mb;mb.ROOT=T
 contract,copy=mb.build(page+'.html',family,'test')
 # Renderer's schema/home interface requires a stable alias.
 copy['test.header.home']='Home';contract['messages']=copy
 for lang,kind,data in [('en','bindings',contract),('en','copy',copy),('zz','copy',copy)]:
  (T/f'locales/{lang}/{family}-{kind}.json').write_text(json.dumps(data,ensure_ascii=False))
 r['pageMirrors'][family]={'master':page+'.html','english':path,'routes':{'zz':'/zz/'+page},'renderLocales':['zz']}
# Add only the three explicitly permitted keyed Prayer families. English values
# are synthetic fixture copy, never production translation or review evidence.
r['locales']['zz']['capabilities']['mirrorTabs'].append('prayers')
for family,(english,pinned) in PRAYER_FAMILIES.items():
 cfg=r['pageMirrors'][family];cfg['routes']['zz']='/zz'+english;cfg['renderLocales'].append('zz')
 shutil.copyfile(T/f'locales/en/{family}-copy.json',T/f'locales/zz/{family}-copy.json')
r['locales']['zz']['capabilities']['mirrorTabs'].append('history')
r['pageMirrors']['history-master']['routes']['zz']='/zz/history'
r['pageMirrors']['history-master']['renderLocales'].append('zz')
shutil.copyfile(T/'locales/en/history-master-copy.json',T/'locales/zz/history-master-copy.json')
(T/'locales/registry.json').write_text(json.dumps(r,ensure_ascii=False))
m=read_json(T/'locales/same-page-manifest.pending.json');m['languages'].append('zz');m['aliases']['zz']='zz';(T/'locales/same-page-manifest.pending.json').write_text(json.dumps(m))
spec=importlib.util.spec_from_file_location('partial_fixture_builder',T/'scripts/build-international.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)

SCOPED_KEYS=frozenset({
 'annaya-tour-travel-master-equivalence','bekaa-kafra-travel-master-equivalence',
 'bkerke-maronite-patriarchate-travel-master-equivalence','cedars-of-god-lebanon-travel-master-equivalence',
 'our-lady-of-lebanon-harissa-travel-master-equivalence','qadisha-valley-travel-master-equivalence',
 'qannoubine-monastery-travel-master-equivalence','qozhaya-monastery-travel-master-equivalence',
 'saint-charbel-hermitage-travel-master-equivalence','saint-charbel-places-lebanon-travel-master-equivalence',
 'saint-charbel-trail-travel-master-equivalence','travel-travel-master-equivalence',
})
PENDING_KEYS={
 'page-0c3101330827fc67':'/annaya-tour','page-e9cfbe50da9de9f7':'/bekaa-kafra',
 'page-62d85c73a9bdfa99':'/bkerke-maronite-patriarchate','page-a7734b0c52abce0b':'/cedars-of-god-lebanon',
 'page-0e8499e9e2421b0d':'/de/travel','page-840507ec030f0af8':'/our-lady-of-lebanon-harissa',
 'page-3d48199e3f92943a':'/qadisha-valley','page-81558ec897fdcbbb':'/qannoubine-monastery',
 'page-957e0d01739ef65e':'/qozhaya-monastery','page-b0c56b3ffb9333da':'/saint-charbel-hermitage',
 'page-8b59e8d442e73c8a':'/saint-charbel-places-lebanon','page-4cb67ba7bdb9d9e3':'/saint-charbel-trail',
 'page-d858dcfecbd57093':'/travel',
}
from i18n import travel_metadata as tm,reviewed_travel as rt,travel_variant_evidence as ve
from i18n.travel_scoped_delta import Tokens
real_compose=tm.compose_travel_clusters;real_travel=rt.travel_manifest;real_final=ve.validate_final_outputs
final_calls=[]
hits=Counter();composition={'negative':False,'synthetic_heads':set(),'production':set(),'roundtrip':0,'roundtrip-pretty':0,'roundtrip-minified':0}

def head_map(text):
 return {n['hreflang']:n['href'] for n in BeautifulSoup(text.split('</head>')[0],'html.parser').select('link[hreflang]')}

def prepare_fixture_heads(root,registry,texts):
 clusters=tm.travel_clusters(root,registry);owners={route:c for c in clusters.values() for route in c.values()}
 for file,text in list(texts.items()):
  if file.suffix!='.html':continue
  soup=BeautifulSoup(text.split('</head>')[0],'html.parser');canonical=soup.select_one('link[rel=canonical]')
  if not canonical:continue
  route=canonical['href'].removeprefix(registry['site']);cluster=owners.get(route)
  if cluster is None:continue
  expected={c:registry['site']+v for c,v in cluster.items()}
  actual=head_map(text)
  if file.relative_to(root).parts[0]=='zz':
   # Real synthetic renderer emits only its explicit family routes initially.
   assert all(expected.get(c)==v for c,v in actual.items()),file
   end=text.index('</head>');head=re.sub(r'<link\b[^>]*\bhreflang=["\'][^>]*>\s*','',text[:end])
   block='\n'.join('<link rel="alternate" hreflang="'+c+'" href="'+v+'" />' for c,v in expected.items())
   texts[file]=head+block+'\n'+text[end:]
   composition['synthetic_heads'].add(file.relative_to(root).as_posix())
  elif set(expected)-set(actual)=={'zz'}:
   if not composition['negative']:
    try:real_compose(root,registry,{file:text});raise AssertionError('Strict composer accepted missing zz')
    except ValueError as exc:assert 'discovery gap' in str(exc),exc
    composition['negative']=True;print('NEGATIVE strict composer rejects missing fixture head',file.relative_to(root))
   token=next(t for t in Tokens(text[:text.index('</head>')]).tokens if t[0]=='tag' and t[3]=='link' and dict(t[4]).get('hreflang')=='x-default')
   raw=text[token[1]:token[2]]
   # Exact raw self-anchor serialization, only two bound scalar substitutions.
   new=raw.replace('hreflang="x-default"','hreflang="zz"').replace('href="'+expected['x-default']+'"','href="'+expected['zz']+'"')
   assert new!=raw and head_map('<head>'+new+'</head>')=={'zz':expected['zz']}
   # Line-whole insertion: the x-default anchor keeps its committed bytes and
   # the prepared head is the original plus exactly one zz line.
   line_start=text.rfind('\n',0,token[1])+1
   indent=text[line_start:token[1]]
   if indent.strip()=='':
    # Pretty-printed head: one indented zz line before the x-default line.
    inserted=indent+new+'\n'
    prepared=text[:line_start]+inserted+text[line_start:]
    assert prepared[:line_start]+prepared[line_start+len(inserted):]==text,(file,'prepared-minus-zz-line != original head')
    composition['roundtrip-pretty']+=1
   else:
    # Minified head: anchors share one line; the exact tag plus its own
    # trailing separator goes at the tag boundary, other bytes untouched.
    inserted=new+'\n'
    prepared=text[:token[1]]+inserted+text[token[1]:]
    assert prepared[:token[1]]+prepared[token[1]+len(inserted):]==text,(file,'prepared-minus-zz-line != original head')
    composition['roundtrip-minified']+=1
   texts[file]=prepared
   composition['production'].add(file.relative_to(root).as_posix())
   composition['roundtrip']+=1
 # This is the real strict composer, on fully prepared fixture-owned inputs.
 return real_compose(root,registry,texts)

def synthetic_travel(root,texts,manifest):
 # Remove no evidence checks for legacy groups. Only scoped release overlay is
 # absent from this counterfactual locale world, without generating null proofs.
 out=real_travel(root,texts,manifest)
 for key,route in PENDING_KEYS.items():
  row=out['pages'].pop(key)
  assert {v['path'] for v in row['variants'].values()}=={route},key
 assert len(PENDING_KEYS)==13
 print('SYNTHETIC omitted pending routes',json.dumps(PENDING_KEYS,sort_keys=True))
 assert not SCOPED_KEYS & set(out['pages'])
 return out

def observed_final(root,texts):
 count=sum(group.get('evidenceSchema')=='scoped-variants-v1' for group in read_json(root/'locales/travel-equivalence.json')['groups'].values())
 final_calls.append(count);print('REAL FINAL VALIDATOR called; scoped records',count)
 return real_final(root,texts)

def fail_diff(file,expected,actual):
 if expected!=actual:
  print(''.join(difflib.unified_diff(expected.splitlines(True),actual.splitlines(True),fromfile='production/'+file,tofile='synthetic-normalized/'+file))[:16000])
  raise AssertionError('Unexpected synthetic production diff: '+file)

def strip_html_zz(text):
 # Exact parsed node positions, never regex spanning neighbouring nodes.
 head_end=text.index('</head>');tokens=Tokens(text[:head_end]).tokens;edits=[]
 for kind,start,end,tag,attrs in tokens:
  if kind!='tag':continue
  attrs=dict(attrs);raw=text[start:end];category=None
  if tag=='link' and attrs.get('hreflang')=='zz':
   assert attrs.get('rel')=='alternate' and attrs.get('href','').startswith('https://marsharbel.com/zz/'),raw
   allowed=['<link rel="alternate" hreflang="zz" href="'+attrs['href']+'" />','<link href="'+attrs['href']+'" hreflang="zz" rel="alternate"/>']
   assert raw in allowed,raw;category='alternate'
  if tag=='meta' and attrs.get('property')=='og:locale:alternate' and attrs.get('content')=='zz_ZZ':
   assert raw in ['<meta property="og:locale:alternate" content="zz_ZZ" />','<meta content="zz_ZZ" property="og:locale:alternate"/>'],raw;category='og'
  if category:
   # Remove the whole zz line: the line's own leading whitespace, the exact
   # tag, and its trailing separator. Neighbour lines keep their exact bytes.
   line_start=text.rfind('\n',0,start)+1
   if text[line_start:start].strip()=='':start=line_start
   if text[end:end+1]=='\n':end+=1
   edits.append((start,end,''));hits[category]+=1
 for start,end,replacement in reversed(edits):text=text[:start]+replacement+text[end:]
 # Dictionary key location is parsed and checked before its exact raw scalar removal.
 soup=BeautifulSoup(text,'html.parser')
 for script in soup.select('script#sc-runtime-labels'):
  payload=str(script.string);data=json.loads(payload)
  assert data['nativeNames'].get('zz')=='Test'
  token=', "zz": "Test"';assert payload.count(token)==1
  replacement=payload.replace(token,'',1);parsed=json.loads(replacement)
  del data['nativeNames']['zz'];assert parsed==data
  assert text.count(payload)==1;text=text.replace(payload,replacement,1);hits['runtime']+=1
 return text

def json_assignment(text):
 prefix,body=text.split(' = ',1);return prefix,json.loads(body.rstrip().removesuffix(';'))

def compare_json(file,old,new):
 prefix,a=json_assignment(old);other,b=json_assignment(new);assert prefix==other
 if file=='same-page-manifest.js':
  assert len(a['pages'])==255 and len(SCOPED_KEYS)==12
  assert SCOPED_KEYS<=set(a['pages']);assert not SCOPED_KEYS&set(b['pages'])
  for key in SCOPED_KEYS:del a['pages'][key]
  assert len(a['pages'])==len(b['pages'])==243
  assert b['aliases'].pop('zz')=='zz';assert b['languages'].pop()=='zz'
  extra={k:b['englishSources'].pop(k) for k in list(b['englishSources']) if k.startswith('/zz/')}
  assert len(extra)==18 and all(k=='/zz'+v.rstrip('/') for k,v in extra.items()),extra
  hits['manifest-routes']+=18
  # Same proof-class exclusion as the 12 page keys: the scoped masters' self-route
  # identity entries come from the omitted overlay rows. Assert identity in the
  # real manifest AND absence in the synthetic one before removing.
  scoped_routes={'/'+key.removesuffix('-travel-master-equivalence') for key in SCOPED_KEYS}
  assert len(scoped_routes)==12
  for route in scoped_routes:
   assert a['englishSources'].get(route)==route,(route,'real englishSources self-route not identity')
   assert route not in b['englishSources'],(route,'synthetic englishSources carries scoped self-route')
  for route in scoped_routes:del a['englishSources'][route]
  # /de/travel is pending-omitted yet its englishSources entry resolves to /travel and survives on both sides.
  assert a['englishSources'].get('/de/travel')=='/travel'==b['englishSources'].get('/de/travel'),'de/travel must survive resolving to /travel'
  hits['manifest-sources']+=12;print('MANIFEST proof excluded in synthetic only 12; legacy overlays real; compared 243')
  print('MANIFEST englishSources scoped self-routes excluded',len(scoped_routes),json.dumps(sorted(scoped_routes)))
  print('EXCLUDED TOTAL 12 page keys + 12 englishSources + 13 pending + 18 zz =',12+12+13+18)
 elif file=='same-page-copy.js':
  zz=b.pop('zz');expected=copy.deepcopy(b['de']);assert zz==expected
  for row in b.values():assert row['names'].pop('zz')=='Test';hits['copy-names']+=1
 elif file=='locale-routes.js':
  assert b['aliases'].pop('zz')=='zz';count=0
  for english,row in b['topics'].items():
   if 'zz' in row:assert row.pop('zz')=='/zz'+english;count+=1
  assert count==18;hits['routing']+=count
 else:raise AssertionError('Unbound generated JS diff: '+file)
 assert a==b,(file,'Non-zz JSON difference')

# The synthetic locale cannot claim the twelve full-file scoped release grants.
# Filter only that exact class from the copied evidence input; keep legacy records.
record=read_json(T/'locales/travel-equivalence.json')
removed={key for key,value in record['groups'].items() if value.get('evidenceSchema')=='scoped-variants-v1'}
assert {key+'-equivalence' for key in removed}==SCOPED_KEYS and len(removed)==12
for key in removed:del record['groups'][key]
(T/'locales/travel-equivalence.json').write_text(json.dumps(record))
print('BOUNDARY full original production build; synthetic scoped overlay absent; legacy checks ON')
print('CLUSTERS original',json.dumps(tm.travel_clusters(R,original_registry),sort_keys=True))
print('CLUSTERS synthetic',json.dumps(tm.travel_clusters(T,r),sort_keys=True))
try:
 original=read_json(T/'locales/registry.json')
 # Strict malformed/collision/catalog probes before expensive full rendering.
 for label,mutate in [('unlisted-tab',lambda x:x['locales']['zz']['capabilities']['mirrorTabs'].append('media')),('unlisted-prayer-master',lambda x:x['pageMirrors'].update(extra={'english':'/history-extra','master':'history.html','routes':{'zz':'/zz/history-extra'},'renderLocales':['zz']})),('nontravel-collision',lambda x:x['pageMirrors'].update(extra={'english':'/history','master':'history.html','routes':{'zz':'/zz/travel'},'renderLocales':['zz']})),('empty-capability',lambda x:x['locales']['zz']['capabilities'].update(mirrorTabs=[])),('collision',lambda x:x['pageMirrors']['test-annaya-tour']['routes'].update(zz='/zz/travel')),('home',lambda x:x['locales']['zz'].update(home='/zz/')),('zh-tw',lambda x:x['locales']['zz'].update(selectorAliases=['zh-TW']))]:
  if label=='zh-tw':continue  # Direct zh-Hans guard covered in unit fixture.
  import copy as cpmod
  bad=cpmod.deepcopy(original);mutate(bad);(T/'locales/registry.json').write_text(json.dumps(bad))
  try:load_catalog(T);raise AssertionError('accepted '+label)
  except ValueError:pass
 (T/'locales/registry.json').write_text(json.dumps(original))
 selectors=read_json(T/'locales/same-page-copy.json');badnames=json.loads(json.dumps(selectors));badnames['fr']['names'].pop('zz');(T/'locales/same-page-copy.json').write_text(json.dumps(badnames))
 try:load_catalog(T);raise AssertionError('accepted incomplete French names')
 except ValueError:pass
 (T/'locales/same-page-copy.json').write_text(json.dumps(selectors))
 for filename,key in [('runtime.json','install.label'),('common.json','navigation.home')]:
  file=T/'locales/zz'/filename;data=read_json(file);old=dict(data);data.pop(key);file.write_text(json.dumps(data))
  try:load_catalog(T);raise AssertionError('accepted missing '+key)
  except ValueError:pass
  file.write_text(json.dumps(old))
 with patch.object(tm,'compose_travel_clusters',side_effect=prepare_fixture_heads),patch.object(rt,'travel_manifest',side_effect=synthetic_travel),patch.object(ve,'validate_final_outputs',side_effect=observed_final):
  out=b.outputs(T)
 zz=[p for p in out if p.relative_to(T).parts[0]=='zz' and p.suffix=='.html'];assert len(zz)==18,zz;assert T/'zz/index.html' not in out;assert 'zz' not in json.loads(out[T/'locale-routes.js'].split(' = ')[1].rstrip(';\n'))['homes'];print('PARTIAL FULL OUTPUT PASS',len(out),len(zz));assert not any('/eucharistic' in str(p) for p in zz);assert {T/('zz'+v[0]+'.html') for v in PRAYER_FAMILIES.values()} <= set(zz)

 assert final_calls==[0],final_calls
 assert composition['negative'] and len(composition['synthetic_heads'])==14
 expected_production=set()
 original_clusters=tm.travel_clusters(R,original_registry)
 owned={route for cluster in original_clusters.values() for route in cluster.values()}
 for file,text in production.items():
  if file.suffix!='.html':continue
  canonical=BeautifulSoup(text.split('</head>')[0],'html.parser').select_one('link[rel=canonical]')
  if canonical and canonical['href'].removeprefix(original_registry['site']) in owned:
   expected_production.add(file.relative_to(R).as_posix())
 authored=set(tm.PARTIAL_AUTHORED_FILES)
 assert len(authored)==19 and authored<=expected_production
 composed=expected_production-authored
 assert not composition['production']&authored
 assert composition['production']==composed,(len(composition['production']),len(composed),composition['production']^composed)
 assert expected_production-composition['production']==authored
 synthetic_clusters=tm.travel_clusters(T,r)
 original_owners={route:cluster for cluster in original_clusters.values() for route in cluster.values()}
 synthetic_owners={route:cluster for cluster in synthetic_clusters.values() for route in cluster.values()}
 en_external={'travel.html','qadisha-valley.html','qannoubine-monastery.html','qozhaya-monastery.html'}
 assert len(en_external)==4 and en_external<=authored
 locale_runtime=authored-en_external
 assert len(locale_runtime)==15 and not en_external&locale_runtime
 print('AUTHORED EXTERNAL RUNTIME class4',json.dumps(sorted(en_external)))
 print('AUTHORED EMBEDDED RUNTIME class15',json.dumps(sorted(locale_runtime)))
 _,synthetic_copy=json_assignment(out[T/'same-page-copy.js'])
 assert synthetic_copy['en']['names']['zz']=='Test' and synthetic_copy['zz']['names']['zz']=='Test'
 print('EN external same-page-copy ZZ name positively checked')
 for file in sorted(authored):
  text=out[T/file];raw_head=text.split('</head>')[0]
  soup=BeautifulSoup(raw_head,'html.parser');canonical=soup.select_one('link[rel=canonical]')
  links=soup.select('link[hreflang]');codes=[link['hreflang'] for link in links]
  route=canonical['href'].removeprefix(r['site']) if canonical else ''
  actual={link['hreflang']:link['href'] for link in links}
  expected={code:r['site']+path for code,path in original_owners.get(route,{}).items()}
  complete={code:r['site']+path for code,path in synthetic_owners.get(route,{}).items()}
  fixture_routes={cfg['english']:cfg['routes']['zz'] for cfg in r['pageMirrors'].values() if 'zz' in cfg.get('routes',{})}
  english=next((source for source,cluster in original_clusters.items() if route in cluster.values()),None)
  fixture_zz=r['site']+fixture_routes[english]
  assert complete=={**expected,'zz':fixture_zz}
  zz_links=[link for link in links if link.get('hreflang')=='zz']
  zz_meta=soup.select('meta[property="og:locale:alternate"][content="zz_ZZ"]')
  runtime=soup.select('script#sc-runtime-labels')
  runtime_hits=sum(json.loads(str(script.string)).get('nativeNames',{}).get('zz')=='Test' for script in runtime)
  if file in en_external:
   assert not runtime and not BeautifulSoup(production[R/file],'html.parser').select('script#sc-runtime-labels'),file
   expected_runtime=0
  else:
   assert len(runtime)==1 and len(BeautifulSoup(production[R/file],'html.parser').select('script#sc-runtime-labels'))==1,file
   expected_runtime=1
  counts={'alternate':len(zz_links),'og':len(zz_meta),'runtime':runtime_hits}
  print('AUTHORED ZZ CLASSES',file,json.dumps(counts,sort_keys=True))
  if file=='ar/qadisha-valley.html':
   print('DISTINCT alternate link:',str(zz_links[0]) if zz_links else '<absent>')
   print('DISTINCT OG alternate meta:',str(zz_meta[0]) if zz_meta else '<absent>')
   print('DISTINCT runtime nativeNames JSON key:', '"zz": "Test"' if runtime_hits else '<absent>')
  if counts!={'alternate':1,'og':1,'runtime':expected_runtime} or len(codes)!=len(set(codes)) or actual!=complete or actual.get('zz')!=fixture_zz or any(link.get('rel')!=['alternate'] for link in links):
   print('AUTHORED RAW HEAD FAILURE',file,raw_head)
   raise AssertionError('Unbound authored synthetic head: '+file)
 assert composition['roundtrip']==len(composition['production']),(composition['roundtrip'],len(composition['production']))
 print('PREPARED ROUND TRIP',composition['roundtrip'],'=',composition['roundtrip-pretty'],'pretty +',composition['roundtrip-minified'],'minified; prepared-minus-zz-line == original head on every prepared page')
 print('PRODUCTION TRAVEL OWNERS',len(expected_production),'=',len(composition['production']),'+',len(authored),'authored actual-head complement checked; injected masks NOT renderer proof')
 print('SYNTHETIC VALIDATORS real renderer/structural catalog capability collision; legacy Travel History Prayer body+catalog; real final validator sees zero scoped records')
 assert all(Path(f).parts[0]=='zz' for f in composition['synthetic_heads'])
 assert len(zz)==18 and not any(p.relative_to(T).parts[0]!='zz' for p in zz)
 for file in zz:
  text=out[file];soup=BeautifulSoup(text,'html.parser');assert len(soup.select('main'))==1
  route='/'+file.relative_to(T).as_posix().removesuffix('.html')
  assert soup.select_one('link[rel=canonical]')['href']==r['site']+route
 print('SYNTHETIC explicit pages checked 18; production in zz set 0; Travel heads checked 14')
 sitemap=out[T/'sitemap.xml'];zzrows=re.findall(r'<url><loc>(https://marsharbel.com/zz/[^<]+)</loc></url>',sitemap)
 assert len(zzrows)==18 and len(set(zzrows))==18 and 'https://marsharbel.com/zz/history' in zzrows
 assert not (T/'zz/history.html').exists()
 # Negative real source_for control: restoring that crash is observable.
 from i18n import sitemap_dates
 with patch.object(sitemap_dates,'source_for',side_effect=ValueError('no source file for https://marsharbel.com/zz/history: expected zz/history.html')):
  assert sitemap_dates.generated_lastmod(T,'https://marsharbel.com/zz/history',{})==''
 with patch.object(sitemap_dates,'source_for',side_effect=ValueError('unexpected source failure')):
  try:sitemap_dates.generated_lastmod(T,'https://marsharbel.com/zz/history',{});raise AssertionError('swallowed source crash')
  except ValueError:pass
 for prod_file,old in production.items():
  file=prod_file.relative_to(R).as_posix();candidate=out[T/file]
  if file.endswith('.html'):
   normalized=strip_html_zz(candidate);fail_diff(file,old,normalized)
   if file=='travel.html':
    corrupted=candidate.replace('</main>','X</main>',1);assert corrupted!=candidate
    try:fail_diff(file,old,strip_html_zz(corrupted));raise AssertionError('accepted real candidate corruption')
    except AssertionError as exc:assert 'Unexpected synthetic production diff' in str(exc)
    print('NEGATIVE real travel candidate stray-byte refused')
  elif file in ('same-page-manifest.js','same-page-copy.js','locale-routes.js'):compare_json(file,old,candidate)
  elif file=='sitemap.xml':
   normalized=candidate
   for url in zzrows:
    line='  <url><loc>'+url+'</loc></url>\n';assert normalized.count(line)==1;normalized=normalized.replace(line,'',1)
   fail_diff(file,old,normalized);hits['sitemap']+=18
  else:fail_diff(file,old,candidate)
 assert hits['alternate']>0 and hits['og']>0 and hits['runtime']>0 and hits['copy-names']==12
 # Unexpected production prose always fails the identical-byte comparison.
 try:fail_diff('negative-control','<main>Original</main>','<main>Unexpected</main>');raise AssertionError('accepted unexpected content')
 except AssertionError as exc:assert 'Unexpected synthetic production diff' in str(exc)
 print('MASK COUNTS',json.dumps(hits,sort_keys=True));print('SPLIT PARTIAL PROBE PASS')
except Exception as e:print(type(e).__name__,str(e));raise
