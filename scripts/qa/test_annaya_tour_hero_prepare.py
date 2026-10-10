import importlib.util,json,sys,tempfile,unittest,shutil
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('prepare_hero',ROOT/'scripts/i18n/prepare_annaya_tour_hero.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class AnnayaHeroPreparation(unittest.TestCase):
    def test_bounded_preparation_preserves_pins_copy_and_existing_sources(self):
        updates=mod.prepare(ROOT)
        self.assertEqual(len(updates),7)
        master=BeautifulSoup((ROOT/'annaya-tour.html').read_text(),'html.parser')
        for family,codes in mod.FAMILIES.items():
            path=ROOT/f'locales/en/{family}-bindings.json';old=json.loads(path.read_text());new=updates[path]
            for field in ('masterSha256','sourceRevision','master'):self.assertEqual(new[field],old[field])
            self.assertEqual(new['bindings'][:len(old['bindings'])][0]['key'],old['bindings'][0]['key'])
            for before,after in zip(old['bindings'],new['bindings']):
                self.assertEqual({k:v for k,v in before.items() if k!='selector'},{k:v for k,v in after.items() if k!='selector'})
                node=master.select(after['selector']);self.assertEqual(len(node),1)
                value=node[0].get(after['attribute']) if after['kind']=='attribute' else str(node[0].contents[after['nodeIndex']])
                self.assertEqual(' '.join(value.split()),after['source'])
            for code in codes:
                path=ROOT/f'locales/{code}/{family}-copy.json';copy=json.loads(path.read_text())
                self.assertEqual({k:updates[path][k] for k in copy},copy)
                self.assertEqual(updates[path][mod.KEY],mod.ALT[code])
    def test_prepared_input_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);shutil.copytree(ROOT/'locales',root/'locales')
            updates=mod.prepare(root)
            for p,data in updates.items():p.write_text(json.dumps(data))
            self.assertEqual(mod.prepare(root),updates)
if __name__=='__main__':unittest.main()
