"""Create a local reversible whole-site preview, never overwrite live source."""
import sys,json,shutil,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from i18n.same_page_injection import control_outputs
root=Path(__file__).resolve().parents[1];target=Path(os.environ.get('SAME_PAGE_PREVIEW_DIR','/tmp/marsharbel-same-page-preview'))
manifest=json.loads((root/'locales/same-page-manifest.pending.json').read_text());copy=json.loads((root/'locales/same-page-copy.draft.json').read_text())
if target.exists():shutil.rmtree(target)
shutil.copytree(root,target,ignore=shutil.ignore_patterns('.git','node_modules','media','playwright-report','test-results'))
if (root/'media').exists():(target/'media').symlink_to(root/'media',target_is_directory=True)
texts={root/item['sourcePath']:(root/item['sourcePath']).read_text() for item in manifest['pages'].values()}
for path,text in control_outputs(root,texts,manifest,copy).items():
 out=target/path.relative_to(root);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(text)
print('Local pending preview only:',target,len(texts),'page identities; all unreviewed targets unavailable')
