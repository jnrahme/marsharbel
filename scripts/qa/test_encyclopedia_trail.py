import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from bs4 import BeautifulSoup
from i18n.encyclopedia_trail import render_trail
class TrailRendering(unittest.TestCase):
 def test_contextual_adjacency_and_qualifier(self):
  rows=[("Fait partie de l'","Encyclopédie de saint Charbel",". Lisez ","le récit complet de sa vie"," ou parcourez tous les sujets.",". Découvrez tous les sujets, de son tombeau à sa neuvaine.","(en anglais)"),("Parte dell'","Enciclopedia di san Charbel",". Leggi ","la storia completa della sua vita"," oppure esplora tutti gli argomenti.",". Esplora tutti gli argomenti, dalla sua tomba alla sua novena.","(in inglese)"),("Część ","Encyklopedii świętego Szarbela",". Przeczytaj ","pełną historię jego życia"," lub przejrzyj wszystkie tematy.",". Poznaj wszystkie tematy, od jego grobu po nowennę.","(po angielsku)")]
  keys=['before','encyclopedia','middle','history','after','historyAfter','englishQualifier']
  for values in rows:
   c=dict(zip(keys,values))
   for variant in [False,True]:
    s=BeautifulSoup(render_trail(c,'/history',variant),'html.parser');a=s.a
    self.assertEqual(a['hreflang'],'en');self.assertFalse(a.has_attr('lang'));self.assertEqual(a['aria-label'],c['encyclopedia']+' '+c['englishQualifier'])
    self.assertEqual(a.find_next_sibling('span').get_text(),c['englishQualifier'])
    expected=c['before']+c['encyclopedia']+' '+c['englishQualifier']+(c['historyAfter'] if variant else c['middle']+c['history']+' '+c['englishQualifier']+c['after'])
    self.assertEqual(s.p.get_text(),expected)
 def test_missing_reviewed_qualifier_fails(self):
  with self.assertRaisesRegex(ValueError,'key mismatch'):render_trail({})

class NavDisclosure(unittest.TestCase):
 def test_header_only_and_nominative(self):
  from i18n.encyclopedia_nav import disclose_nav
  from i18n.catalog import ROOT
  original='<header><a class="nav-parent" href="/saint-charbel-encyclopedia">Dziedzictwo duchowe<span class="nav-chev" aria-hidden="true"></span></a><a href="/saint-charbel-encyclopedia">Encyklopedia świętego Szarbela</a><a href="/pl/biografia">Pełna historia</a></header><main><p>Unchanged &amp; exact.</p></main>'
  output=disclose_nav(original,ROOT,'pl')
  self.assertEqual(output.split('<main>')[1],original.split('<main>')[1])
  soup=BeautifulSoup(output,'html.parser');a=soup.header.select('a')[1]
  self.assertEqual(a['aria-label'],'Encyklopedia świętego Szarbela (po angielsku)')
  self.assertFalse(a.has_attr('lang'));self.assertEqual(a['hreflang'],'en')
  self.assertEqual(a.find_next_sibling('span').get_text(),'(po angielsku)')

if __name__=='__main__':unittest.main()
