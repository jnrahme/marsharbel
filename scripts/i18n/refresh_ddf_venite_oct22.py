"""Rebind the news-master contract after adding the DDF 'Venite ad Me' row (October 22, 2026).

Row insertion shifts li:nth-of-type selectors for every following row, so selectors are
regenerated from the rebuilt master with scripts/i18n/make_bindings.build, but keys are
remapped to the established key for any unchanged (source, kind) pair: same-node text
updates keep their keys, and only genuinely new texts receive fresh slug keys. Executor
only; run after build-pages and build_news_desk:
python3 scripts/i18n/refresh_ddf_venite_oct22.py [--check]
"""
import argparse, hashlib, json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from i18n.make_bindings import build
from i18n.keyed_master import strip_static_fallback

ROOT = Path(__file__).resolve().parents[2]
STRIPPED = ROOT / 'news.master-stripped.html'

NEW_AR = {
    # Vatican Doctrinal Dicastery Publishes 'Venite ad Me' on Handing On the Faith
    'news.latest-news.vatican-doctrinal-dicastery-publishes-venite-ad-me-on-handin':
        "إصدار «تعالوا إليّ»: الديكاستري للعقيدة والإيمان ينشر وثيقة عن نقل الإيمان",
    # The Dicastery for the Doctrine of the Faith published ...
    'news.latest-news.the-dicastery-for-the-doctrine-of-the-faith-published-venite':
        "نشر الديكاستري لعقيدة الإيمان في 22 تشرين الأول وثيقة «تعالوا إليّ: تأملات في نقل الإيمان في تغيّر تاريخي شامل». ويقدّمها الديكاستري بوصفها مجموعة تأملات لا ملاحظة عقائدية، داعيًا إلى تجديد إعلان الإنجيل وإلى مسارات جديدة لتبشير البالغين إلى جانب تعليم الأطفال الإيمان. وبحسب فاتيكان نيوز، وافق البابا لاوون الرابع عشر على الوثيقة في 21 آب 2026.",
    # Dicastery for the Doctrine of the Faith: 'Venite ad Me' publication announcement (October 22, 2026)
    'news.latest-news.dicastery-for-the-doctrine-of-the-faith-venite-ad-me-publica':
        "الديكاستري لعقيدة الإيمان: إعلان نشر وثيقة «تعالوا إليّ» (22 تشرين الأول 2026)",
    # Vatican News: Doctrine of the Faith - returning to the kerygma amid crisis in passing on faith (October 22, 2026)
    'news.latest-news.vatican-news-doctrine-of-the-faith-returning-to-the-kerygma':
        "فاتيكان نيوز: الديكاستري لعقيدة الإيمان - العودة إلى الكيريغما وسط أزمة نقل الإيمان (22 تشرين الأول 2026)",
}

def outputs(root=ROOT):
    old_contract = json.loads((root / 'locales/en/news-master-bindings.json').read_text())
    old_copy = json.loads((root / 'locales/en/news-master-copy.json').read_text())
    ar_copy = json.loads((root / 'locales/ar/news-master-copy.json').read_text())
    # The control-build noscript fallback is never part of a master or its pins:
    # bind and hash the stripped master bytes, exactly as keyed_master does.
    stripped = strip_static_fallback((ROOT / 'news.html').read_bytes())
    STRIPPED.write_bytes(stripped)
    try:
        fresh, fresh_messages = build(STRIPPED.name, 'news-master', 'news')
    finally:
        STRIPPED.unlink()
    fresh['master'] = 'news.html'

    # Map unchanged nodes back to their established key: exact selector match first
    # (stable for head/meta nodes), else a unique (source, kind, attribute) match.
    by_selector = {}
    by_content = {}
    for b in old_contract['bindings']:
        sig = (b['source'], b['kind'], b.get('attribute'))
        by_selector[(b['selector'],) + sig] = b['key']
        if sig in by_content and by_content[sig] != b['key']:
            by_content[sig] = None  # ambiguous without its selector
        else:
            by_content.setdefault(sig, b['key'])

    bindings, used = [], set()
    for b in fresh['bindings']:
        sig = (b['source'], b['kind'], b.get('attribute'))
        key = by_selector.get((b['selector'],) + sig) or by_content.get(sig) or b['key']
        nb = dict(b); nb['key'] = key
        bindings.append(nb); used.add(key)

    dead = set(old_copy) - used
    copy = {k: old_copy[k] for k in old_copy if k in used}
    for k, v in fresh_messages.items():
        if k in used and k not in copy:
            copy[k] = v
    missing_ar = [k for k in copy if k not in ar_copy]
    for k in missing_ar:
        if k not in NEW_AR:
            raise ValueError('new key needs an Arabic translation: ' + k)
        ar_copy[k] = NEW_AR[k]
    for k in list(ar_copy):
        if k not in copy:
            del ar_copy[k]
    if set(ar_copy) != set(copy):
        raise ValueError('Arabic news keys differ from English')

    contract = dict(fresh)
    contract['bindings'] = bindings
    contract['messages'] = copy
    contract['masterSha256'] = hashlib.sha256(stripped).hexdigest()
    return {root / 'locales/en/news-master-bindings.json': contract,
            root / 'locales/en/news-master-copy.json': copy,
            root / 'locales/ar/news-master-copy.json': ar_copy}

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--check', action='store_true')
    a = p.parse_args()
    for path, data in outputs().items():
        text = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
        if a.check:
            if path.read_text() != text:
                raise SystemExit('DDF Venite ad Me bindings stale: ' + str(path))
        else:
            path.write_text(text)
    print('DDF Venite ad Me bindings checked' if a.check else 'DDF Venite ad Me bindings refreshed')
