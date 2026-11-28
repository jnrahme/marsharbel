"""Finite EN-only publication policy for the four reviewed Secret Prayers pages."""
import hashlib,json,re
from pathlib import Path
RECORD='locales/secret-prayers-en-release.json'
RECORD_SHA256='21379b19582f3816dec199e38ee1ab584b8221175fa7d103f436b3fa9a1a3d1d'
SLUGS=('powerful-secret-prayers','mary-who-goes-ahead-prayer','lebanese-mountain-prayers','terco-da-batalha')
def load(root):
 from secret_prayers_ar_fr_policy import load as continuation
 d=continuation(root)
 if d is not None:return d
 p=Path(root)/RECORD
 if not p.exists():return None
 if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=RECORD_SHA256:raise ValueError('Secret EN release policy drift')
 d=json.loads(p.read_bytes())
 if d['releaseLocales']!=['en'] or set(d['pages'])!={s+'.html'for s in SLUGS}:raise ValueError('Secret EN release scope drift')
 return d

def errors(root):
 from secret_prayers_ar_fr_policy import load as continuation, errors as continuation_errors
 if continuation(root) is not None:return continuation_errors(root)
 root=Path(root);d=load(root)
 if d is None:return []
 out=[]
 for code in d['heldLocales']:
  for slug in SLUGS:
   if (root/code/(slug+'.html')).exists():out.append('Held foreign secret page present: '+code+'/'+slug)
 pattern=re.compile(r'https://marsharbel\.com/(?:'+('|'.join(re.escape(x)for x in d['heldLocales']))+')/(?:'+('|'.join(SLUGS))+r')(?:["<>/?#\s]|$)')
 for p in root.glob('sitemap*.xml'):
  if pattern.search(p.read_text()):out.append('Held foreign Secret URL in '+p.name)
 for p in root.rglob('*.html'):
  if any(x in p.relative_to(root).parts for x in ['node_modules','.git','output','test-results']):continue
  text=p.read_text()
  for tag in re.findall(r'<link\b[^>]*>',text):
   if 'hreflang' in tag and pattern.search(tag):out.append('Held foreign Secret hreflang in '+str(p.relative_to(root)))
 return out
