"""Create a local reversible whole-site preview, never overwrite live source."""
import sys,json,shutil,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from i18n.same_page_injection import control_outputs
root=Path(__file__).resolve().parents[1];target=Path(os.environ.get('SAME_PAGE_PREVIEW_DIR','/tmp/marsharbel-same-page-preview'))
manifest=json.loads((root/'locales/same-page-manifest.pending.json').read_text());copy=json.loads((root/'locales/same-page-copy.json').read_text())
if target.exists():shutil.rmtree(target)
target.mkdir(parents=True)
# Link untouched assets and scripts. Never copy the media-heavy source tree.
for source in root.iterdir():
    if source.name in {'.git','node_modules','playwright-report','test-results'}:continue
    if source.is_dir():
        # HTML output directories need writable skeletons; all other files are links.
        for item in source.rglob('*'):
            if item.is_dir():continue
            dest=target/item.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True)
            dest.symlink_to(item)
    else:(target/source.name).symlink_to(source)
texts={root/item['sourcePath']:(root/item['sourcePath']).read_text() for item in manifest['pages'].values()}
for path,text in control_outputs(root,texts,manifest,copy).items():
 out=target/path.relative_to(root);out.parent.mkdir(parents=True,exist_ok=True)
 if out.is_symlink():out.unlink()
 out.write_text(text)
print('Local pending preview only:',target,len(texts),'page identities; all unreviewed targets unavailable')
