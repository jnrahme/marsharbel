"""Build the Follow-Along catalog admission from the homepage block and keyed pack."""
import argparse,json
from collections import Counter
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
def output(root=ROOT):
    soup=BeautifulSoup((root/'index.html').read_text(),'html.parser')
    section=soup.select_one('#follow-us')
    if section is None:raise ValueError('Follow-Along block absent from index.html')
    strings=[section.select_one('h2').get_text(strip=True)]
    sub=section.select_one('.section-sub')
    if sub:strings.append(sub.get_text(strip=True))
    cards=section.select('a.follow-card')
    if len(cards)!=3:raise ValueError('Follow-Along card count != 3')
    for card in cards:
        strings.append(card.select_one('.follow-txt strong').get_text(strip=True))
        strings.append(card.select_one('.follow-handle').get_text(strip=True))
        strings.append(card.select_one('.follow-line').get_text(strip=True))
    keyed=json.loads((root/'locales/en/home-copy.json').read_text())
    keyed_values={keyed['home.follow-us.'+k] for k in ('title','sub','instagram','facebook','youtube')}
    if not keyed_values<=set(strings):raise ValueError('Keyed follow-us copy missing from page: '+str(keyed_values-set(strings)))
    return {'values':{'index.html':dict(Counter(strings))}}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
    path=ROOT/'locales/en/home-follow-copy.json'
    text=json.dumps(output(),ensure_ascii=False,indent=2)+'\n'
    if a.check:
        if path.read_text()!=text:raise SystemExit('Follow-Along catalog stale')
    else:path.write_text(text)
    print('Follow-Along catalog checked' if a.check else 'Follow-Along catalog built')
