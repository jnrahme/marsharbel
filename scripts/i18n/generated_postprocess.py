"""One final runtime/control pass for generated international outputs."""
import re
from i18n.catalog import read_json

def postprocess_outputs(root, registry, catalogs, result):
    from i18n.same_page_injection import control_outputs
    manifest=read_json(root/'locales/same-page-manifest.pending.json')
    control_copy=read_json(root/'locales/same-page-copy.json')
    # Generated locale pages need the runtime dictionary translate.js reads
    # (install/footer labels); page_mirror families already embed it. This runs
    # before control_outputs so the same-page manifest sees the final bytes.
    from i18n.runtime_labels import ensure_runtime_labels
    for path, text in list(result.items()):
        if path.suffix != '.html':
            continue
        lang = re.search(r'<html[^>]*lang=["\']([^"\']+)', text)
        if lang and lang.group(1) in registry['locales'] and lang.group(1) != registry['defaultLocale']:
            code = lang.group(1)
            if 'runtime' not in catalogs.get(code, {}):
                # Explicit synthetic-locale path: only reachable when load_catalog
                # is replaced (the foundation gate's zh-Hans). Real loads always
                # carry 'runtime' - load_catalog raises otherwise.
                continue
            result[path] = ensure_runtime_labels(text, root, code, registry)
    result.update(control_outputs(root,{path:text for path,text in result.items() if path.suffix=='.html'},manifest,control_copy))
    return result
