import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from i18n.same_page_injection import inject_control
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'locales/same-page-manifest.pending.json').read_text())
copy=json.loads((root/'locales/same-page-copy.json').read_text())
sys.stdout.write(inject_control(sys.stdin.read(),root,manifest,copy))
