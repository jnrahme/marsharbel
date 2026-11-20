"""Exact MB16 Chinese premiere home-shell continuation, no shell-pin refresh."""
import json
from pathlib import Path
import subprocess
from i18n import mb16_home_continuation as home
MODULE='scripts/i18n/mb16_film_home.py'
RECORD='locales/mb16-film-home.json'
PATH='zh-Hans/charbel-film-premiere.html'
EDITS=(
    ('"item": "https://marsharbel.com/"','"item": "https://marsharbel.com/zh-Hans/"'),
    ('<a class="brand" href="/">圣夏尔贝勒</a>','<a class="brand" href="/zh-Hans/">圣夏尔贝勒</a>'),
    ('<a class="back" href="/">首页 （英语）</a>','<a class="back" href="/zh-Hans/">首页</a>'),
)

def derive(original):
    for before,after in EDITS:
        if original.count(before.encode())!=1:
            raise ValueError('MB16 film: exact shell occurrence drift')
        original=original.replace(before.encode(),after.encode())
    return original

def verify_delta(original,candidate):
    if candidate!=original and candidate!=derive(original):
        raise ValueError('MB16 film: bytes outside exact shell-home delta')
    return original

def preimage(root,path,current):
    if path!=PATH:return current
    root=Path(root)
    if not (root/RECORD).exists() and not (root/RECORD).is_symlink():return current
    from i18n.seo_continuations import require_regular_inputs
    inputs=[MODULE,RECORD,home.MODULE,home.RECORD,'locales/registry.json',
            'scripts/build-international.py','scripts/i18n/same_page_injection.py',PATH]
    require_regular_inputs(root,inputs)
    record=json.loads((root/RECORD).read_bytes())
    if set(record)!={'base','path','originalSha256'} or record['base']!=home.BASE or record['path']!=PATH:
        raise ValueError('MB16 film: record scope drift')
    try:
        head=home.git(root,'rev-parse','HEAD').decode().strip()
        subprocess.run(['git','-C',str(root),'merge-base','--is-ancestor',home.BASE,head],
                       check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        for rel in inputs:
            if (root/rel).read_bytes()!=home.git(root,'show',head+':'+rel):
                raise ValueError('MB16 film: raw native HEAD fidelity differs '+rel)
        if current!=(root/PATH).read_bytes():raise ValueError('MB16 film: caller differs from native candidate')
        home.preimage(root,'index.html',(root/'index.html').read_bytes())
        original=home.git(root,'show',home.BASE+':'+PATH)
        if home.sha(original)!=record['originalSha256']:raise ValueError('MB16 film: original fixed-base hash differs')
        return verify_delta(original,current)
    except (OSError,subprocess.CalledProcessError) as error:
        raise ValueError('MB16 film: native proof unavailable, export rejected') from error
