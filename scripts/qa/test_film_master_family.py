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
  self.r={'site':'https://marsharbel.com','defaultLocale':'en','locales':{c:{'direction':'rtl' if c=='ar' else 'ltr'} for c in self.codes},'pageMirrors':{m.FAMILY:self.cfg}}
  self.write('locales/registry.json',self.r)
  template='<article id="'+m.ID+'"><h3><a class="card-cover" href="/news">${premiere.title}</a></h3><p>${premiere.body} <a href="https://example.invalid/source">Source</a></p><h4>Video</h4><iframe src="https://example.invalid/video"></iframe></article>'
  self.write('templates/news-desk/cards.html',template);english={'premiere.title':'Title','premiere.body':'Body'};self.write('locales/en/news-desk.json',english)
  source=template.replace('${premiere.title}','Title').replace('${premiere.body}','Body');self.write('news.html',source)
  article=str(m.adapted(BeautifulSoup(source,'html.parser').article))
  links=''.join('<link rel="alternate" hreflang="'+c+'" href="https://marsharbel.com'+p+'"/>' for c,p in {**self.routes,'x-default':self.routes['en']}.items())
  switcher='<nav class="film-locale-switcher">'+''.join('<a hreflang="'+c+'" href="'+p+'">'+c+'</a>' for c,p in self.routes.items())+'</nav>'
  self.pages={}
  for c,route in self.routes.items():
   text='<html lang="'+c+'" dir="'+self.r['locales'][c]['direction']+'"><head><link rel="canonical" href="https://marsharbel.com'+route+'"/>'+links+'<style>'+m.RULE+'</style></head><body><header>Header</header><main>'+article+'</main>'+switcher+'<footer>Footer</footer></body></html>'
   file=m.SLUG+'.html' if c=='en' else c+'/'+m.SLUG+'.html';self.write(file,text);self.pages[c]=(file,text)
   self.write('locales/'+c+'/'+m.FAMILY+'-copy.json',{'body':'Body'})
  master=self.pages['en'][1];self.write('locales/en/'+m.FAMILY+'-bindings.json',{'master':m.SLUG+'.html','masterSha256':m.digest(master),'bindings':[{'key':'body','selector':'article p','kind':'text','nodeIndex':0,'source':'Body'}]})
  raw=BeautifulSoup(template,'html.parser').article
  self.contract={'family':m.FAMILY,'templateSha256':m.digest(str(raw)),'englishCatalogSha256':m.digest(json.dumps(english,ensure_ascii=False,sort_keys=True)),'sourceFeatureSha256':m.digest(str(BeautifulSoup(source,'html.parser').article)),'shellSha256':{c:m.shell_digest(t,self.routes[c]) for c,(f,t) in self.pages.items()}}
  self.write('config/film-master-family.json',self.contract)
 def fail(self,message):
  with self.assertRaisesRegex(ValueError,message):m.validate_family(self.root)
 def change_page(self,code,old,new):
  file,text=self.pages[code];self.write(file,text.replace(old,new))
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
 def test_source_news_drift_refuse(self):self.write('news.html','<article id="'+m.ID+'">Wrong</article>');self.fail('served news source differs')
 def test_changed_article_links_media_refuse(self):
  for old,new in [('Body','Other'),('example.invalid/source','example.invalid/wrong'),('example.invalid/video','example.invalid/other')]:
   self.change_page('ar',old,new);self.fail('article differs from keyed output ar')
 def test_altered_shell_refuse(self):self.change_page('ar','Header','Changed header');self.fail('independent final shell drift ar')
 def test_missing_duplicate_wrong_underline_refuse(self):
  for replacement in ('',('<style>'+m.RULE+'</style>')*2,'<style>'+m.RULE.replace('underline','none')+'</style>'):
   self.change_page('ar','<style>'+m.RULE+'</style>',replacement);self.fail('exactly one exact underline rule required ar')
 def test_missing_wrong_xdefault_and_nonreciprocal_refuse(self):
  old='<link rel="alternate" hreflang="x-default" href="https://marsharbel.com/'+m.SLUG+'"/>'
  for replacement in ('',old.replace('/'+m.SLUG,'/other')):
   self.change_page('ar',old,replacement);self.fail('reciprocal cluster/x-default mismatch ar')
  self.change_page('ar','hreflang="fr"','hreflang="xx"');self.fail('reciprocal cluster/x-default mismatch ar')
 def test_js_only_switcher_refuse(self):
  file,text=self.pages['ar'];text=text.replace('<a hreflang="fr" href="/fr/'+m.SLUG+'">','<a hreflang="fr" data-href="/fr/'+m.SLUG+'">');self.write(file,text)
  self.contract['shellSha256']['ar']=m.shell_digest(text,self.routes['ar']);self.write('config/film-master-family.json',self.contract);self.fail('crawlable 12-locale switcher required ar')
if __name__=='__main__':unittest.main()
