import sys,json,shutil,tempfile,importlib.util
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'))
from i18n.catalog import read_json,load_catalog,PRAYER_FAMILIES
from i18n.make_bindings import build
# Build in isolated copy so all production inputs/outputs remain untouched.
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
 out=b.outputs(T);zz=[p for p in out if p.relative_to(T).parts[0]=='zz' and p.suffix=='.html'];assert len(zz)==18,zz;assert T/'zz/index.html' not in out;assert 'zz' not in json.loads(out[T/'locale-routes.js'].split(' = ')[1].rstrip(';\n'))['homes'];print('PARTIAL FULL OUTPUT PASS',len(out),len(zz));assert not any('/eucharistic' in str(p) for p in zz);assert {T/('zz'+v[0]+'.html') for v in PRAYER_FAMILIES.values()} <= set(zz)
except Exception as e:print(type(e).__name__,str(e));raise
