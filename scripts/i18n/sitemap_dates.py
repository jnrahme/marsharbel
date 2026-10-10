"""Preserve carried sitemap dates; initialize only from clean committed sources."""
import re
from sitemap_lastmod import source_for,git


def generated_lastmod(root,url,carried):
    if url in carried:return carried[url]
    source=source_for(root,url);relative=source.relative_to(root).as_posix()
    if git(root,'status','--porcelain','--',relative):
        raise ValueError('Cannot date uncommitted sitemap source: '+relative)
    if git(root,'ls-files','--',relative)!=relative:
        raise ValueError('Cannot date untracked sitemap source: '+relative)
    changed=git(root,'log','-1','--format=%as','--',relative)
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',changed):
        raise ValueError('Missing committed sitemap author date: '+relative)
    return changed
