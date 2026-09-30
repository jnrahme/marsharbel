#!/usr/bin/env python3
"""Keep the explicit QA bootstrap before every config; run after locale generation."""
import argparse,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def bootstrap(text):
    text=re.sub(r"gtag\(['\"]config['\"],\s*['\"]G-CJX1M0VFKP['\"]\s*\)", "gtag('config', 'G-CJX1M0VFKP', window.SC_QA_ANALYTICS || {})", text)
    if text.count('<script src="/analytics-qa.js"></script>') == 1 and text.index('<script src="/analytics-qa.js"></script>') < text.index("gtag("):
        return text
    clean=re.sub(r'\s*<script src="/analytics-qa.js"></script>', '',text)
    clean=re.sub(r'([ \t]*)(<!-- Google tag \(gtag.js\) -->)',r'\1<script src="/analytics-qa.js"></script>\n\1\2',clean,count=1)
    if '<script src="/analytics-qa.js"></script>' not in clean:
        clean=re.sub(r'(<script\b[^>]*>\s*(?:window\.)?dataLayer)',r'<script src="/analytics-qa.js"></script>\n\1',clean,count=1)
    if '<script src="/analytics-qa.js"></script>' not in clean:raise ValueError(f'Cannot place bootstrap in document')
    return clean

def sync(check=False):
    stale=[]
    for p in ROOT.rglob('*.html'):
        if any(x in p.parts for x in ('node_modules','.git','playwright-report','test-results')):continue
        text=p.read_text()
        if not re.search(r"gtag\(['\"]config['\"]",text):continue
        clean=bootstrap(text)
        if clean!=text:
            stale.append(str(p.relative_to(ROOT)))
            if not check:p.write_text(clean)
    if check and stale:raise SystemExit('Stale analytics bootstrap: '+', '.join(stale))
    return stale
if __name__=='__main__':
    args=argparse.ArgumentParser();args.add_argument('--check',action='store_true');ns=args.parse_args();print('Analytics bootstrap changed:',len(sync(ns.check)))
