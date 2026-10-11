"""Positive and destructive controls for bounded extracted-feature policy."""
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.feature_mirror import FEATURES, adapted, check_feature, digest, shell_digest

class FeatureMirror(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.root=Path(temp.name)
        self.spec=FEATURES['film-premiere-v1']
        raw='<article class="card update reveal" id="charbel-premiere-release-2026-10"><h3><a class="card-cover" href="./saint-charbel-movie">${premiere.title}</a></h3><p>${premiere.body} <a href="https://example.org/source?q=1">${premiere.link}</a></p><h4>${premiere.videoTitle}</h4><iframe src="https://www.youtube-nocookie.com/embed/WYOPngWLTh0" title="${premiere.videoTitle}" allowfullscreen></iframe></article>'
        en={'premiere.title':'Feature','premiere.body':'Full text','premiere.link':'Source','premiere.videoTitle':'Trailer'}
        ar={k:'ترجمة '+str(i)for i,k in enumerate(en)}
        render=lambda j:re.sub(r'\$\{([^}]+)\}',lambda m:j[m[1]],raw)
        source=render(en)
        target='<!doctype html><html lang="ar" dir="rtl"><head><link rel="canonical" href="https://marsharbel.com/ar/charbel-film-premiere"><link rel="stylesheet" href="/international.css"><script src="/translate.js"></script></head><body><header><nav><select id="sc-language-select"></select></nav></header><main>'+str(adapted(BeautifulSoup(render(ar),'html.parser').article))+'</main><footer><p>Footer</p></footer></body></html>'
        for name,value in [(self.spec['template'],raw),(self.spec['catalog'],json.dumps(en)),(self.spec['localeCatalog'],json.dumps(ar)),(self.spec['source'],source),(self.spec['target'],target)]:
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value)
        self.entry={'family':'film-premiere-v1','master':'news.html','route':self.spec['route'],'locale':'ar','status':'extracted-feature'}
        self.contract={'version':1,'family':'film-premiere-v1','textKeys':sorted(en),'templateSha256':digest(str(BeautifulSoup(raw,'html.parser').article)),'englishCatalogSha256':digest(json.dumps(en,ensure_ascii=False,sort_keys=True)),'sourceFeatureSha256':digest(str(BeautifulSoup(source,'html.parser').article)),'shellSha256':shell_digest(target,self.spec['route'])}
    def check(self):return check_feature(self.root,self.entry,self.contract)
    def edit(self,path,old,new):
        p=self.root/path;p.write_text(p.read_text().replace(old,new))
    def test_complete_feature_passes(self):self.assertEqual(self.check(),[])
    def test_source_provenance_and_coverage_mutations_fail(self):
        for field in ['templateSha256','englishCatalogSha256','sourceFeatureSha256','shellSha256']:
            with self.subTest(field=field):
                original=self.contract[field];self.contract[field]='0'*64
                with self.assertRaises(ValueError):self.check()
                self.contract[field]=original
        self.contract['textKeys'].pop()
        with self.assertRaises(ValueError):self.check()
    def test_stale_served_source_fails(self):
        self.edit('news.html','Full text','Stale text')
        with self.assertRaises(ValueError):self.check()
    def test_extra_missing_or_empty_locale_key_fails(self):
        p=self.root/self.spec['localeCatalog'];original=json.loads(p.read_text())
        for change in ['extra','missing','empty','markup']:
            j=dict(original)
            if change=='extra':j['opening.body']='foreign'
            elif change=='missing':del j['premiere.body']
            elif change=='empty':j['premiere.body']=' '
            else:j['premiere.body']='<b>markup</b>'
            p.write_text(json.dumps(j))
            with self.subTest(change=change),self.assertRaises(ValueError):self.check()
    def test_target_media_links_prose_structure_and_controls_fail(self):
        p=self.root/self.spec['target'];original=p.read_text()
        for old,new in [('q=1','q=2'),('WYOPngWLTh0','another'),('allowfullscreen=""',''),('ترجمة 1','wrong copy'),('<p>','<p hidden>'),('</main>','<aside>Extra</aside></main>'),('/translate.js','/translate.js?v=changed'),('<nav>','<nav data-mode="changed">'),('Footer','Altered footer'),('id="sc-language-select"','id="other-select"'),('dir="rtl"','dir="ltr"'),('/ar/charbel-film-premiere','/ar/wrong')]:
            p.write_text(original.replace(old,new));self.assertNotEqual(original,p.read_text())
            with self.subTest(old=old),self.assertRaises(ValueError):self.check()
    def test_no_wildcard_or_self_master_escape(self):
        for key,value in [('family','*'),('master','ar/charbel-film-premiere.html'),('normalizers',['ignore-main']),('exceptions',['*'])]:
            saved=dict(self.entry);self.entry[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.check()
            self.entry=saved
    def test_duplicate_or_foreign_source_feature_fails(self):
        p=self.root/self.spec['template'];original=p.read_text()
        for text in [original*2,original.replace('${premiere.body}','${opening.body}')]:
            p.write_text(text)
            with self.assertRaises(ValueError):self.check()
if __name__=='__main__':unittest.main()
