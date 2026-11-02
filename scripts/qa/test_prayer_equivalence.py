"""Prayer promotion stays closed until final QA and rejects content drift."""
import json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from i18n import citation_amendment
from i18n.reviewed_prayers import prayer_manifest
class PrayerEquivalence(unittest.TestCase):
 def test_pending_gate_is_noop(self):
  marker={'pages':{}}
  from unittest.mock import patch
  record=json.loads((ROOT/'locales/prayer-equivalence.json').read_text());record['gateStatus']='pending-final-qa'
  original=json.loads
  with patch('i18n.reviewed_prayers.json.loads',side_effect=lambda text:record if 'gateStatus' in text else original(text)):
   self.assertIs(prayer_manifest(ROOT,{},marker),marker)
 def test_review_and_body_and_catalog_checks(self):
  record=json.loads((ROOT/'locales/prayer-equivalence.json').read_text())
  sidecar=citation_amendment.load(ROOT)
  with tempfile.TemporaryDirectory()as temp:
   root=Path(temp)
   for file in ('locales/prayer-review-record.json',*[v['catalog']for g in record['groups'].values()for v in g['variants'].values()if 'catalog'in v]):
    dst=root/file;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/file,dst)
   for group,g in record['groups'].items():
    for lang,v in g['variants'].items():
     dst=root/v['file'];dst.parent.mkdir(parents=True,exist_ok=True)
     entry=sidecar['families'].get(group,{}).get('variants',{}).get(lang) if sidecar else None
     if entry and entry['oldBodySha256']==v['bodySha256']:
      # The synthetic root carries no sidecar, so the guard compares bodies against the
      # historical pins: seed citation-amended files with their sidecar-bound historical
      # base bytes. Current bytes carry the amendment and drift against the unchanged pins.
      dst.write_bytes(subprocess.check_output(['git','-C',str(ROOT),'show',sidecar['base']+':'+v['file']]))
     else:shutil.copyfile(ROOT/v['file'],dst)
   record['gateStatus']='approved';(root/'locales/prayer-equivalence.json').write_text(json.dumps(record))
   m=prayer_manifest(root,{}, {'pages':{}})
   self.assertEqual(len(m['pages']),2)
   for page in m['pages'].values():self.assertEqual(set(page['variants']),{'en','ar','de','fr','ru','pt','it','pl','es'})
   first=record['groups']['saint-charbel-prayers-master']['variants']['ar']
   with self.assertRaisesRegex(ValueError,'body drift'):prayer_manifest(root,{root/first['file']:(root/first['file']).read_text().replace('<main','<main data-drift="yes"',1)}, {'pages':{}})
   (root/first['catalog']).write_text('{}')
   with self.assertRaisesRegex(ValueError,'catalog drift'):prayer_manifest(root,{}, {'pages':{}})
if __name__=='__main__':unittest.main()
