#!/usr/bin/env python3
"""Project reviewed, keyed Nader context into existing legacy pages only."""
import argparse,json,re
from pathlib import Path
from html import escape
ROOT=Path(__file__).resolve().parents[1]
TARGETS={
 'en':{'miracles/index.html':'Latest Recorded and Reported Miracles','templates/masters/miracles-exact.html':'Latest Recorded and Reported Miracles','miracles/raymond-nader.html':'How the Church Treated It'},
 'ar':{'ar/miracles/index.html':'أحدث العجائب المسجَّلة والمبلَّغ عنها','ar/miracles/raymond-nader.html':'كيف تعاملت الكنيسة مع الحالة'},
}
def project(source,heading,copy):
 snippet='<!-- nader-reported-context:begin -->\n<p data-nader-reported-context>'+escape(copy['text'])+'</p>\n<p><a href="'+escape(copy['href'],quote=True)+'" rel="noopener" target="_blank">'+escape(copy['link_text'])+'</a></p>\n<!-- nader-reported-context:end -->'
 marker=r'<!-- nader-reported-context:begin -->.*?<!-- nader-reported-context:end -->'
 if re.search(marker,source,re.S):
  if len(re.findall(marker,source,re.S))!=1:raise ValueError('Duplicate Nader context')
  return re.sub(marker,lambda _:snippet,source,flags=re.S)
 pattern=r'(<h2[^>]*>'+re.escape(heading)+r'</h2>.*?)</p>'
 result,count=re.subn(pattern,lambda m:m.group(0)+'\n'+snippet,source,count=1,flags=re.S)
 if count!=1:raise ValueError('Missing reviewed insertion heading '+heading)
 return result

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args();changed=[]
 for lang,pages in TARGETS.items():
  copy=json.loads((ROOT/f'locales/{lang}/nader-context-copy.json').read_text())['copy']
  for rel,heading in pages.items():
   path=ROOT/rel;before=path.read_text();after=project(before,heading,copy)
   if before!=after:
    changed.append(rel)
    if not args.check:path.write_text(after)
 if args.check and changed:raise SystemExit('Nader context stale: '+', '.join(changed))
 print('Nader context '+('check' if args.check else 'build')+': '+str(len(changed))+' changed')
if __name__=='__main__':main()
