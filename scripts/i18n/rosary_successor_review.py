"""Integrity checks for a new Rosary review packet; never an activation grant.

Not wired into the live manifest. A future integration must explicitly consume
this check after independent review and all release gates. Existing pairing
history remains unchanged. Hash integrity does not authenticate a reviewer or
establish owner permission.
"""
import hashlib
import re
from i18n.reviewed_rosary_books import LOCALES, SLUGS

SCHEMA = 'rosary-story-successor-review-v1'
SCOPE = 'story-text-and-translation-only'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha(value, label):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{64}', value):
        raise ValueError('Invalid SHA256: ' + label)


def _file(root, relative):
    # Receipts cannot pin unrelated private files or escape the checkout.
    path = root / relative
    if not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('Missing or unsafe artifact: ' + relative)
    return path


def validate_successor_review(root, record):
    """Validate exact 20x8 text review coverage, without changing activation.

    Each locale receipt is bound to both its new text and its EN source. Public
    page/reader/API hashes belong to the later technical pairing receipt, not
    this editorial receipt. Art, audio, native certification and deployment are
    deliberately not certified by this function.
    """
    if record.get('schema') != SCHEMA or record.get('scope') != SCOPE:
        raise ValueError('Wrong successor review schema or scope')
    if record.get('nativeReviewStatus') != 'not-certified':
        raise ValueError('Native certification is outside this contract')
    if record.get('activationStatus') != 'unpublished':
        raise ValueError('Editorial receipt cannot activate a release')
    _sha(record.get('previousPairingSha256'), 'previous pairing')
    previous = _file(root, 'locales/rosary-books-pairing.json')
    if sha256(previous) != record['previousPairingSha256']:
        raise ValueError('Previous pairing history drift')
    if set(record.get('reviews', {})) != set(LOCALES):
        raise ValueError('Successor locale membership drift')
    english = record['reviews']['en'].get('books', {})
    for locale in LOCALES:
        review = record['reviews'][locale]
        if (review.get('status') != 'agent-reviewed'
                or not review.get('producer') or not review.get('reviewer')
                or review['producer'] == review['reviewer']
                or not review.get('evidenceRef')):
            raise ValueError('Independent review incomplete: ' + locale)
        if set(review.get('books', {})) != set(SLUGS):
            raise ValueError('Successor book membership drift: ' + locale)
        for slug in SLUGS:
            receipt = review['books'][slug]
            text_path = f'content/books/{slug}/{locale}.json'
            source_path = f'content/books/{slug}/en.json'
            catalog_path = f'locales/{locale}/{slug}-master-copy.json'
            expected = {text_path, catalog_path, f'content/books/{slug}/book.json'}
            if set(receipt.get('artifacts', {})) != expected:
                raise ValueError('Unexpected text artifact coverage: ' + slug + ' ' + locale)
            for relative, pin in receipt['artifacts'].items():
                _sha(pin, relative)
                if sha256(_file(root, relative)) != pin:
                    raise ValueError('Reviewed text artifact drift: ' + relative)
            _sha(receipt.get('englishSourceSha256'), source_path)
            if sha256(_file(root, source_path)) != receipt['englishSourceSha256']:
                raise ValueError('English review source drift: ' + slug + ' ' + locale)
            en_pin = english.get(slug, {}).get('artifacts', {}).get(source_path)
            if en_pin != receipt['englishSourceSha256']:
                raise ValueError('Translation review source mismatch: ' + slug + ' ' + locale)
    return {'books': len(SLUGS), 'locales': len(LOCALES),
            'reviewedEditions': len(SLUGS) * len(LOCALES),
            'activationStatus': 'unpublished'}
