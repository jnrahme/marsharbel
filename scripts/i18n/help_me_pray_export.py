"""Build the Help Me Pray public browser payload (positive allowlist only).

Reads the 12 runtime catalogs (already stripped of private fields at projection)
and emits assets/help-me-pray-data.json. Contract: pendingNotice survives,
beginEnabled stays false, no prayer body text, no review/private tokens.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCALES = ['en', 'ar', 'fr', 'es', 'pt', 'it', 'de', 'pl', 'ru', 'hi', 'th', 'zh-Hans']
CARD_COPY_FIELDS = ['question', 'practicalAnswer', 'why', 'source.publisher', 'source.section',
                    'source.label', 'practiceType', 'boundaryNote', 'prayerTarget.heading', 'prayerTarget.type']

# The desk's catalogs carry English need labels (identical in all 12 locales).
# Map them to the canonical need keys; raw card.need is preserved alongside.
NEED_KEY_MAP = {
    'beginning/restarting prayer': 'restart',
    'family': 'family',
    'illness': 'illness',
    'gratitude': 'gratitude',
    'discouragement in prayer': 'discouragement',
    'understanding Maronite practice': 'maronite',
}


def main():
    payload = {}
    for lang in LOCALES:
        cat = json.loads((ROOT / 'locales' / lang / 'help-me-pray-catalog.json').read_text())
        cards = {}
        for cid, card in cat['cards'].items():
            if card['need'] not in NEED_KEY_MAP:
                raise SystemExit(f'{lang}/{cid}: unmapped need {card["need"]!r}')
            proj = {
                'need': card['need'],
                'needKey': NEED_KEY_MAP[card['need']],
                'copy': {f: card['copy'][f] for f in CARD_COPY_FIELDS},
                'sourceURL': card['sourceURL'],
                'prayerTargetURL': card['prayerTargetURL'],
                'additionalSourceURLs': card['additionalSourceURLs'],
                'beginEnabled': False,
            }
            if 'sourceAuthor' in card:
                proj['sourceAuthor'] = card['sourceAuthor']
            cards[cid] = proj
        payload[lang] = {
            'direction': cat['direction'],
            'page': cat['page'],  # reviewNotice was stripped at projection; pendingNotice must be present
            'needs': cat['needs'],
            'ui': cat['ui'],
            'cards': cards,
        }
        assert 'pendingNotice' in cat['page'], f'{lang}: pendingNotice missing'
        assert 'reviewNotice' not in cat['page'], f'{lang}: reviewNotice survived projection'
    out = ROOT / 'assets/help-me-pray-data.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n')
    print(f'wrote {out} ({out.stat().st_size} bytes, {len(payload)} locales)')


if __name__ == '__main__':
    main()
