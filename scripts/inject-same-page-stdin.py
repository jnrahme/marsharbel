import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from i18n.same_page_injection import inject_control
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'locales/same-page-manifest.pending.json').read_text())
copy=json.loads((root/'locales/same-page-copy.json').read_text())
text=sys.stdin.read()
import re
from urllib.parse import urlsplit
from i18n.prayer_metadata import compose_prayer_clusters
canonical=re.search(r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)',text)
if canonical:
 route=urlsplit(canonical[1]).path
 registry=json.loads((root/'locales/registry.json').read_text())
 prayer_routes={'/en/prayers'}
 for family in ('saint-charbel-prayers-master','saint-charbel-novena-master'):
  prayer_routes.update(registry.get('pageMirrors',{}).get(family,{}).get('discoveryRoutes',{}).values())
 if route in prayer_routes:
  text=inject_control(text,root,manifest,copy)
  file=root/(route.lstrip('/')+'.html')
  text=compose_prayer_clusters(root,registry,{file:text},source_inputs=True).get(file,text)
sys.stdout.write(inject_control(text,root,manifest,copy))
