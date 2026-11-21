import copy,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from i18n import film_master_family as m
from bs4 import BeautifulSoup
class FilmMasterFamily(unittest.TestCase):
 def write(self,path,value):
  p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,ensure_ascii=False) if not isinstance(value,str) else value)
 def setUp(self):
  temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.root=Path(temp.name)
  self.codes=('en','ar','fr','es','pt','it','de','pl','ru','hi','th','zh-Hans')
  self.routes={c:('/'+m.SLUG if c=='en' else '/'+c+'/'+m.SLUG) for c in self.codes}
  self.cfg={'master':m.SLUG+'.html','english':self.routes['en'],'routes':{c:p for c,p in self.routes.items() if c!='en'},'renderLocales':list(self.codes[1:])}
  self.r={'site':'https://marsharbel.com','defaultLocale':'en','locales':{c:{'direction':'rtl' if c=='ar' else 'ltr','home':None if c=='zh-Hans' else ('/' if c=='en' else '/'+c+'/')} for c in self.codes},'pageMirrors':{m.FAMILY:self.cfg}}
  self.write('locales/registry.json',self.r)
  template='<article id="'+m.ID+'"><h3><a class="card-cover" href="/'+m.SLUG+'">${premiere.title}</a></h3><p>${premiere.body} <a href="https://example.invalid/source">Source</a></p><h4>Video</h4><iframe src="https://example.invalid/video"></iframe></article>'
  self.write('templates/news-desk/premiere-feature.html',template);english={'premiere.title':'Title','premiere.body':'Body'};self.write('locales/en/news-desk.json',english)
  source=template.replace('${premiere.title}','Title').replace('${premiere.body}','Body')
  row='<article id="'+m.ID+'" class="news-row update"><h3><a class="card-cover news-row-link" href="/'+m.SLUG+'">Title</a></h3></article>';self.write('news.html',row)
  article=str(m.adapted(BeautifulSoup(source,'html.parser').article))
  links=''.join('<link rel="alternate" hreflang="'+c+'" href="https://marsharbel.com'+p+'"/>' for c,p in {**self.routes,'x-default':self.routes['en']}.items())
  switcher='<nav class="film-locale-switcher">'+''.join('<a hreflang="'+c+'" href="'+p+'">'+c+'</a>' for c,p in self.routes.items())+'</nav>'
  self.pages={}
  for c,route in self.routes.items():
   text='<html lang="'+c+'" dir="'+self.r['locales'][c]['direction']+'"><head><link rel="canonical" href="https://marsharbel.com'+route+'"/>'+links+'<style>'+m.style_for(c)+'</style></head><body><header>Header</header><main>'+article+'</main>'+switcher+'<footer>Footer</footer></body></html>'
   file=m.SLUG+'.html' if c=='en' else c+'/'+m.SLUG+'.html';self.write(file,text);self.pages[c]=(file,text)
   self.write('locales/'+c+'/'+m.FAMILY+'-copy.json',{'body':'Body'})
  master=self.pages['en'][1];self.write('locales/en/'+m.FAMILY+'-bindings.json',{'master':m.SLUG+'.html','masterSha256':m.digest(master),'bindings':[{'key':'body','selector':'article p','kind':'text','nodeIndex':0,'source':'Body'}]})
  raw=BeautifulSoup(template,'html.parser').article
  self.contract={'family':m.FAMILY,'templateSha256':m.digest(str(raw)),'englishCatalogSha256':m.digest(json.dumps(english,ensure_ascii=False,sort_keys=True)),'sourceFeatureSha256':m.digest(str(BeautifulSoup(source,'html.parser').article)),'shellSha256':{c:m.shell_digest(t,self.routes[c]) for c,(f,t) in self.pages.items()}}
  self.write('config/film-master-family.json',self.contract)
  self.sitemap='<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>https://marsharbel.com'+p+'</loc><lastmod>2026-10-10</lastmod></url>' for p in self.routes.values())+'</urlset>'
  self.write('sitemap.xml',self.sitemap)
  for c,cfg in self.r['locales'].items():
   if cfg['home']:
    f='index.html' if c=='en' else c+'/index.html'
    self.write(f,'<a class="home-news-lead home-news-lead--film" href="'+self.routes[c]+'">Film</a>')
 def fail(self,message):
  with self.assertRaisesRegex(ValueError,message):m.validate_family(self.root)
 def change_page(self,code,old,new):
  file,text=self.pages[code];self.write(file,text.replace(old,new))
 def test_missing_registry_not_registered(self):
  (self.root/'locales/registry.json').unlink()
  self.assertFalse(m.registered(self.root))
 def test_complete_twelve_pass(self):self.assertEqual(m.validate_family(self.root),[])
 def test_unregistered_unaffected(self):self.r['pageMirrors']={};self.write('locales/registry.json',self.r);self.assertEqual(m.validate_family(self.root),[])
 def test_11_13_active_sets_refuse(self):
  for extra in (False,True):
   r=copy.deepcopy(self.r)
   if extra:r['locales']['xx']={'direction':'ltr'}
   else:r['locales'].pop('th')
   self.write('locales/registry.json',r);self.fail('active locale set must contain exactly 12')
 def test_missing_extra_duplicate_render_locale_refuse(self):
  for codes in (list(self.codes[1:-1]),list(self.codes[1:])+['xx'],list(self.codes[1:])+['ar']):
   r=copy.deepcopy(self.r);r['pageMirrors'][m.FAMILY]['renderLocales']=codes;self.write('locales/registry.json',r);self.fail('locale membership/routes')
 def test_stale_three_source_digests_refuse(self):
  for key in ('templateSha256','englishCatalogSha256','sourceFeatureSha256'):
   c=copy.deepcopy(self.contract);c[key]='0'*64;self.write('config/film-master-family.json',c);self.fail('stale source provenance '+key)
 def test_news_row_without_card_cover_refuse(self):
  row='<article id="'+m.ID+'" class="news-row update"><h3><a class="news-row-link" href="/'+m.SLUG+'">Title</a></h3></article>'
  self.write('news.html',row);self.fail('news row must keep the card-cover link')
 def test_changed_article_links_media_refuse(self):
  for old,new in [('Body','Other'),('example.invalid/source','example.invalid/wrong'),('example.invalid/video','example.invalid/other')]:
   self.change_page('ar',old,new);self.fail('article differs from keyed output ar')
 def test_altered_shell_refuse(self):self.change_page('ar','Header','Changed header');self.fail('independent final shell drift ar')
 def test_missing_duplicate_wrong_underline_refuse(self):
  for replacement in ('',('<style>'+m.style_for('ar')+'</style>')*2,'<style>'+m.style_for('ar').replace('underline','none')+'</style>','<style>'+m.RULE+'</style>'):
   self.change_page('ar','<style>'+m.style_for('ar')+'</style>',replacement);self.fail('exactly one exact underline rule required ar')
 def test_missing_wrong_xdefault_and_nonreciprocal_refuse(self):
  old='<link rel="alternate" hreflang="x-default" href="https://marsharbel.com/'+m.SLUG+'"/>'
  for replacement in ('',old.replace('/'+m.SLUG,'/other')):
   self.change_page('ar',old,replacement);self.fail('reciprocal cluster/x-default mismatch ar')
  self.change_page('ar','hreflang="fr"','hreflang="xx"');self.fail('reciprocal cluster/x-default mismatch ar')
 def test_js_only_switcher_refuse(self):
  file,text=self.pages['ar'];text=text.replace('<a hreflang="fr" href="/fr/'+m.SLUG+'">','<a hreflang="fr" data-href="/fr/'+m.SLUG+'">');self.write(file,text)
  self.contract['shellSha256']['ar']=m.shell_digest(text,self.routes['ar']);self.write('config/film-master-family.json',self.contract);self.fail('crawlable 12-locale switcher required ar')
 def test_missing_duplicate_sitemap_url_refuse(self):
  entry='<url><loc>https://marsharbel.com'+self.routes['ar']+'</loc><lastmod>2026-10-10</lastmod></url>'
  for replacement in ('',entry*2):
   self.write('sitemap.xml',self.sitemap.replace(entry,replacement));self.fail('sitemap URL must occur exactly once ar')
 def test_lastmod_required_for_each_of_twelve(self):
  for code,route in self.routes.items():
   old='<loc>https://marsharbel.com'+route+'</loc><lastmod>2026-10-10</lastmod>'
   self.write('sitemap.xml',self.sitemap.replace(old,'<loc>https://marsharbel.com'+route+'</loc>'))
   self.fail('valid sitemap lastmod required '+code)
 def test_missing_invalid_lastmod_refuse(self):
  for replacement in ('','<lastmod>2026-02-30</lastmod>','<lastmod>tomorrow</lastmod>'):
   self.write('sitemap.xml',self.sitemap.replace('<lastmod>2026-10-10</lastmod>',replacement));self.fail('valid sitemap lastmod required')
 def test_wrong_js_only_home_lead_refuse(self):
  for link in ('<a class="home-news-lead--film" href="/charbel-film-premiere">Film</a>','<a class="home-news-lead--film" data-href="/ar/charbel-film-premiere">Film</a>','<a class="home-news-lead--film" href="/ar/charbel-film-premiere" rel="nofollow">Film</a>'):
   self.write('ar/index.html',link);self.fail('home lead must reach own locale article ar')
 def test_news_card_wrong_target_refuse(self):
  source=(self.root/'news.html').read_text().replace('href="/'+m.SLUG+'"','href="/saint-charbel-movie"')
  self.write('news.html',source)
  # Discovery is separately tested so source-contract drift cannot mask it.
  with self.assertRaisesRegex(ValueError,'news card must reach EN article'):m.validate_discovery(self.root,self.r,self.routes)
class FilmShellWording(unittest.TestCase):
 def test_exact_file_only_and_count_limits(self):
  import importlib.util
  spec=importlib.util.spec_from_file_location('film_wording_policy',ROOT/'scripts/qa/check_i18n_policy.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);path=root/'locales/en/film-premiere-shell-copy.json';path.parent.mkdir(parents=True)
   self.assertEqual(policy.film_shell_wording(root,'charbel-film-premiere.html'),{})
   path.write_text(json.dumps({'charbel-film-premiere.html':{'Title':2,'Description':2,'Skip':1}}))
   self.assertEqual(policy.film_shell_wording(root,'other.html'),{})
   allowed=policy.film_shell_wording(root,'charbel-film-premiere.html')
   from collections import Counter
   self.assertEqual(Counter({'Title':3,'Unexpected':1})-allowed,{'Title':1,'Unexpected':1})
   path.write_text(json.dumps({'other.html':{'Title':2}}))
   with self.assertRaisesRegex(ValueError,'exact EN film file'):policy.film_shell_wording(root,'charbel-film-premiere.html')
   for bad in (0,-1,True,'2'):
    path.write_text(json.dumps({'charbel-film-premiere.html':{'Title':bad}}))
    with self.assertRaisesRegex(ValueError,'positive exact counts'):policy.film_shell_wording(root,'charbel-film-premiere.html')
if __name__=='__main__':unittest.main()
