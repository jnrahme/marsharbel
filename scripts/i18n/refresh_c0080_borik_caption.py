"""C-0080 non-author executor re-pin after Borik caption value change (203->203, one source value)."""
import hashlib,json,subprocess
from pathlib import Path
from bs4 import BeautifulSoup,NavigableString
ROOT=Path(__file__).resolve().parents[2]
KEY='home.latest-news.historic-saint-charbel-portrait-public-domain-not-a-photograph'
NEW_EN='Traditional portrait of Saint Charbel; not a photograph of Dr. Borik.'
def outputs(root=ROOT):
 contract=json.loads((root/'locales/en/home-bindings.json').read_text());raw=(root/'index.html').read_bytes();soup=BeautifulSoup(raw,'html.parser')
 if len(contract['bindings'])!=203:raise ValueError('Expected 203 bindings')
 bindings=[];changed=0
 for old in contract['bindings']:
  b=dict(old)
  nodes=soup.select(b['selector'])
  if len(nodes)!=1:raise ValueError('Selector drift '+b['key'])
  n=nodes[0];v=n.get(b['attribute'])if b['kind']=='attribute'else ' '.join(str(n.contents[b['nodeIndex']]).split())
  if b['key']==KEY:
   if v!=NEW_EN:raise ValueError('Built caption mismatch: '+repr(v))
   if b['source']==NEW_EN:raise ValueError('Already re-pinned')
   b['source']=NEW_EN;changed+=1
  else:
   if v!=b['source']:raise ValueError('Other source drift '+b['key'])
  bindings.append(b)
 if changed!=1:raise ValueError('Unexpected delta '+str(changed))
 messages=json.loads((root/'locales/en/home-copy.json').read_text())
 if messages[KEY]!=NEW_EN:raise ValueError('Catalog mismatch')
 contract.update(bindings=bindings,messages=messages,masterSha256=hashlib.sha256(raw).hexdigest(),sourceRevision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip())
 return {root/'locales/en/home-bindings.json':json.dumps(contract,ensure_ascii=False,indent=2)+'\n'}
if __name__=='__main__':
 for p,t in outputs().items():p.write_text(t)
 print('C-0080 re-pin: 203 bindings, 1 source value updated, pins refreshed')
