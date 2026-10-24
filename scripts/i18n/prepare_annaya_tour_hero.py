"""Prepare only Annaya hero bindings/copy. Never writes source or review pins."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
FAMILIES={'annaya-tour-travel-master':('en','de','ru'),'annaya-tour-zh-travel-master':('en','zh-Hans')}
ALT={'en':'Saint Maron monastery and the church bell tower at Annaya in winter','de':'Kloster des heiligen Maron und der Kirchturm in Annaya im Winter','ru':'Монастырь святого Марона и церковная колокольня в Аннайе зимой','zh-Hans':'冬季安纳亚的圣马龙修道院与教堂钟楼'}
PREFIX='#main-content > section:nth-of-type(1) > '
KEY='annaya.hero.imageAlt'
def prepare(root):
    updates={}
    for family,codes in FAMILIES.items():
        file=root/f'locales/en/{family}-bindings.json';contract=json.loads(file.read_text())
        prepared = any(b['key']==KEY for b in contract['bindings'])
        for b in contract['bindings']:
            if not prepared and b['selector'].startswith(PREFIX):
                b['selector']=b['selector'].replace(PREFIX,PREFIX+'div.annaya-tour-summary > ',1)
        # Secondary destinations move to a quiet row without changing their copy.
        for b in contract['bindings']:
            if b['selector'].startswith(PREFIX+'div.annaya-tour-summary > div:nth-of-type(1) > a:nth-of-type('):
                if b['selector'].endswith('(3)'):b['selector']=b['selector'].replace('div:nth-of-type(1) > a:nth-of-type(3)','div:nth-of-type(2) > a:nth-of-type(1)')
                if b['selector'].endswith('(4)'):b['selector']=b['selector'].replace('div:nth-of-type(1) > a:nth-of-type(4)','div:nth-of-type(2) > a:nth-of-type(2)')
        records=[{'key':KEY,'selector':'.annaya-tour-lead img','source':ALT['en'],'kind':'attribute','attribute':'alt'}]
        # Credit is the exact existing Travel string, not a new source claim.
        for key,selector,source,index in [
            ('annaya.hero.creditAuthor','.annaya-tour-lead figcaption','Paul Saad /',0),
            ('annaya.hero.creditCommons','.annaya-tour-lead figcaption a:nth-of-type(1)','Wikimedia Commons',0),
            ('annaya.hero.creditSeparator','.annaya-tour-lead figcaption','/',2),
            ('annaya.hero.creditLicense','.annaya-tour-lead figcaption a:nth-of-type(2)','CC BY-SA 4.0',0)]:
            records.append({'key':key,'selector':selector,'source':source,'kind':'text','nodeIndex':index})
        if prepared:
            if [b for b in contract['bindings'] if b['key'].startswith('annaya.hero.')] != records:
                raise ValueError('Prepared hero bindings drift')
        else:
            contract['bindings'].extend(records)
        contract['messages'].update({b['key']:b['source'] for b in records})
        updates[file]=contract
        for code in codes:
            file=root/f'locales/{code}/{family}-copy.json';copy=json.loads(file.read_text())
            for b in records:copy[b['key']]=ALT[code] if b['key']==KEY else b['source']
            updates[file]=copy
    return updates
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);mode=parser.add_mutually_exclusive_group();mode.add_argument('--write',action='store_true');mode.add_argument('--check',action='store_true');args=parser.parse_args()
    updates=prepare(ROOT)
    print(json.dumps({'files':[str(p.relative_to(ROOT)) for p in updates],'pinWrites':0,'locales':['de','ru','zh-Hans'],'nativeCertified':False},indent=2))
    if args.check:
        if any(json.loads(p.read_text()) != data for p,data in updates.items()):raise SystemExit('Annaya hero preparation not applied')
    if args.write:
        for p,data in updates.items():p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
