"""Preserve carried sitemap dates; initialize only from clean committed sources."""
import re
from sitemap_lastmod import source_for,git


def generated_lastmod(root,url,carried):
    if url in carried:return carried[url]
    try:source=source_for(root,url)
    except ValueError as exc:
        if str(exc).startswith('no source file for '+url+': expected '):return ''
        raise
    relative=source.relative_to(root).as_posix()
    if git(root,'status','--porcelain','--',relative):
        return ''
    if git(root,'ls-files','--',relative)!=relative:
        return ''
    changed=git(root,'log','-1','--format=%as','--',relative)
    if not changed:return ''
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',changed):
        raise ValueError('Missing committed sitemap author date: '+relative)
    return changed
