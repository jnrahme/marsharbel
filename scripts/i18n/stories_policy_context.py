"""Supply pinned source-derived context to the existing Stories normalizer."""
import hashlib
from i18n.stories_shelf_copy import MASTER_SHA256
from i18n.localized_source_links import resolve_family


def trusted_context(root, registry, entry):
    code = entry['locale']
    if code not in ('ar','fr','es','pt','it','de','pl','ru','hi','th','zh-Hans'):
        raise ValueError('Stories policy locale differs')
    family = resolve_family(registry,entry['master'],entry['route'],code)
    cfg = registry['pageMirrors'][family]
    if (family,entry.get('family'),entry['master'],entry['masterRoute'],entry['route'],cfg.get('english')) != (
        'stories-master','stories-master','templates/masters/stories.html','/stories','/'+code+'/stories','/stories'):
        raise ValueError('Stories policy exact family/master/route differs')
    if code not in cfg.get('renderLocales',[]):
        raise ValueError('Stories policy locale not rendered')
    actual = hashlib.sha256((root/entry['master']).read_bytes()).hexdigest()
    if actual != MASTER_SHA256:
        raise ValueError('Stories policy frozen source hash differs')
    return {'family':family,'lang':code,'masterSha256':actual}
