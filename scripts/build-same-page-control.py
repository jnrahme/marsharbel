"""Final site-wide language-control composition after page and locale builders."""
import sys,json,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from i18n.same_page_injection import control_outputs
from bs4 import BeautifulSoup
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
manifest=json.loads((root/'locales/same-page-manifest.pending.json').read_text());copy=json.loads((root/'locales/same-page-copy.json').read_text())
texts={}
# Canonical actual page coverage, rather than stale manifest/sourcePath assumptions.
for file in root.rglob('*.html'):
 if any(part in {'node_modules','.git','src','templates','docs','test-results','playwright-report'} for part in file.relative_to(root).parts):continue
 text=file.read_text();soup=BeautifulSoup(text,'html.parser');canonical=soup.select_one('link[rel=canonical]');robots=soup.select_one('meta[name=robots]')
 if not canonical or not soup.main or (robots and 'noindex' in robots.get('content','')):continue
 if not canonical.get('href','').startswith('https://marsharbel.com/'):continue
 if soup.html.get('lang','en') not in copy:continue
 texts[file]=text
stale=[]
for path,text in control_outputs(root,texts,manifest,copy).items():
 if not path.exists() or path.read_text()!=text:
  stale.append(str(path.relative_to(root)))
  if not args.check:path.write_text(text)
print('Same-page control:',len(texts),'canonical pages;',len(stale),'stale' if args.check else 'written')
if args.check and stale:raise SystemExit(', '.join(stale))
