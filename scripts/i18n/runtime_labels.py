"""Runtime label injection for generated locale pages.

page_mirror-owned families embed the sc-runtime-labels dictionary themselves.
The generated families (rosary, feast, miracles, monasteries, qadisha, litany,
chaplet, travel, Eucharistic) were built without it, so translate.js fell back
to English - most visibly the Install App header button, and the footer privacy/
terms/accessibility labels. A few of those pages also never loaded translate.js
at all, which removed the install control entirely. One idempotent pass closes
both gaps for every generated locale page.
"""
import json
from i18n.catalog import read_json

TRANSLATE_SRC = '/translate.js?v=20260922-1'


def ensure_runtime_labels(text, root, lang, registry):
    if lang == registry['defaultLocale']:
        return text
    if 'id="sc-runtime-labels"' not in text:
        # load_catalog fails closed when a published locale lacks runtime.json;
        # synthetic test locales never reach this helper (outputs() skips them).
        runtime = read_json(root / f'locales/{lang}/runtime.json')
        runtime['language.choose'] = read_json(root / f'locales/{lang}/common.json')['navigation.chooseLanguage']
        runtime['nativeNames'] = {code: cfg['nativeName'] for code, cfg in registry['locales'].items()}
        payload = json.dumps(runtime, ensure_ascii=False).replace('<', '\\u003c')
        node = f'<script id="sc-runtime-labels" type="application/json">{payload}</script>'
        text = text.replace('</head>', node + '\n</head>', 1)
    if 'translate.js' not in text:
        tag = f'<script defer src="{TRANSLATE_SRC}"></script>\n'
        if '<script defer src="/same-page-switcher.js">' in text:
            text = text.replace('<script defer src="/same-page-switcher.js">', tag + '<script defer src="/same-page-switcher.js">', 1)
        elif text.count('</body>') == 1:
            # control_outputs appends the same-page script block at </body>
            # after this pass; anchoring here keeps translate.js ahead of it,
            # matching pages whose generators emit the tag themselves.
            text = text.replace('</body>', tag + '</body>', 1)
    return text
