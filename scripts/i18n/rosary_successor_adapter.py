"""Map the frozen Rosary manuscripts to staged canonical book data.

This is an offline adapter, not a publisher. It refuses the checkout as output
and leaves existing runtime content, pairing and routes untouched.
"""
import copy
import hashlib
import json
from pathlib import Path
import re

from i18n.reviewed_rosary_books import SLUGS

PASSION_SLUGS = {'sorrowful-scourging', 'sorrowful-crowning-thorns', 'sorrowful-crucifixion'}

MASTER_SHA256 = '2ad25dd88b617e6fa374d36d56784caac44b5d73b6ac39617fa9eab9f7737421'


def build_successor(root, spec, master_bytes, output):
    root, output = root.resolve(), output.resolve()
    if output == root or output.is_relative_to(root):
        raise ValueError('Successor output must be outside the runtime checkout')
    if hashlib.sha256(master_bytes).hexdigest() != MASTER_SHA256:
        raise ValueError('Frozen manuscript bytes changed')
    master = json.loads(master_bytes)
    if spec.get('frozen_approved_master', {}).get('sha256') != MASTER_SHA256:
        raise ValueError('Spec source hash mismatch')
    books = {b['slug']: b for b in spec['books']}
    originals = {b['slug']: b for b in master['books']}
    if len(spec['books']) != 20 or set(books) != set(SLUGS):
        raise ValueError('Successor book membership drift')
    # v2 explicitly supersedes the old speech/public-domain production claims.
    metadata_packet = json.loads((root / 'docs/rosary-successor/locale-metadata-field-packet-v2.json').read_text())
    if metadata_packet.get('version') != 'v2-corrected-disclosures' or metadata_packet.get('master_sha256') != MASTER_SHA256:
        raise ValueError('Metadata successor version/source mismatch')
    metadata = {b['slug']: b['metadata_source'] for b in metadata_packet['books']}
    if set(metadata) != set(SLUGS):
        raise ValueError('Metadata successor membership drift')
    illustration_notes = json.loads((root / 'docs/rosary-successor/illustration-notes-all8.json').read_text())
    if set(illustration_notes['locales']) != set(('en','ar','de','es','fr','it','pl','pt')):
        raise ValueError('Illustration note locale coverage drift')
    staged = {}
    for slug in SLUGS:
        plan, original = copy.deepcopy(books[slug]), originals[slug]
        plan['metadata'] = metadata[slug]
        current = json.loads((root / f'content/books/{slug}/book.json').read_text())
        current_en = json.loads((root / f'content/books/{slug}/en.json').read_text())
        pages = plan['reader_pages']
        if len(pages) != plan['page_count']:
            raise ValueError('Page count mismatch: ' + slug)
        ids = [p['id'] for p in pages]
        if len(set(ids)) != len(ids) or any(not re.fullmatch('bk-' + re.escape(slug) + r'-flow-[a-z0-9-]+', i) for i in ids):
            raise ValueError('Semantic page ID mismatch: ' + slug)
        roles = [p['role'] for p in pages]
        if (roles.count('reflection') != 1 or roles[-3:] != ['prayer'] * 3
                or roles[-4] != 'reflection' or any(r != 'story' for r in roles[:-4])):
            raise ValueError('Story/reflection/prayer order drift: ' + slug)
        painting = plan['painting']['asset_record']
        if painting not in current['assets'] or painting['id'] != current['cover']:
            raise ValueError('Retained painting metadata drift: ' + slug)
        image_path = root / painting['path']
        if (image_path.stat().st_size != painting['bytes']
                or hashlib.sha256(image_path.read_bytes()).hexdigest() != painting['sha256']):
            raise ValueError('Retained painting bytes drift: ' + slug)
        story, reflection, prayers = [], [], []
        for i, page in enumerate(pages, 1):
            if page['index'] != i or page['audio'] or page['image'] != current['cover']:
                raise ValueError('Page structure drift: ' + slug)
            if page['role'] == 'story':
                story.extend(page['paragraphs'])
            elif page['role'] == 'reflection':
                reflection.extend(page['paragraphs'])
            elif page['role'] == 'prayer':
                prayers.append(page)
            else:
                raise ValueError('Unknown semantic role: ' + slug)
        if 'narrative' in original:
            expected_story, expected_reflection = original['narrative'], original['reflection']
        else:
            expected_story = [t for p in original['pages'][:-1] for t in p['text']]
            expected_reflection = original['pages'][-1]['text']
        if story != expected_story or reflection != expected_reflection:
            raise ValueError('Missing, duplicated or changed movement: ' + slug)
        if len(prayers) != 3:
            raise ValueError('Prayer membership drift: ' + slug)
        for page, prayer in zip(prayers, original['prayers']):
            if (page['paragraphs'] != [prayer['text']]
                    or page['instruction'] != prayer['instruction']
                    or page['title'] != prayer['title']):
                raise ValueError('Prayer text/instruction drift: ' + slug)
        # Validate every book before writing any output.
        book = copy.deepcopy(current)
        book['status'] = 'draft'
        if slug in PASSION_SLUGS:
            plate = root / 'docs/rosary-successor/neutral-prayer-plate.svg'
            safe_id = 'bk-' + slug + '-img-prayer-ornament'
            book['cover'] = safe_id
            # Omit original art from automatic API/assets entirely while rights are open.
            book['assets'] = [{'id': safe_id, 'kind': 'image',
                'path': 'media/mysteries/neutral-prayer-plate.svg',
                'mime': 'image/svg+xml', 'bytes': plate.stat().st_size,
                'sha256': hashlib.sha256(plate.read_bytes()).hexdigest(),
                'access': 'public', 'width': 960, 'height': 1200}]
            for page in pages:
                page['image'] = safe_id

        book['pages'] = [{'id': p['id'], 'index': p['index'],
            # Existing reader supports story/reflection, not a prayer enum.
            'kind': 'reflection' if p['role'] == 'reflection' else 'story',
            'scene': p['role'], 'access': 'public', 'image': p['image'],
            'audio': {}, 'evidence': []} for p in pages]
        en = copy.deepcopy(current_en)
        en.update(review='pending-metadata-layout-review',
                  title=plan['metadata']['reader_title'], summary=plan['metadata']['summary'])
        alt = current_en['coverAlt']
        if slug in PASSION_SLUGS:
            # Proposed new wording requires independent copy + locale review.
            alt = illustration_notes['locales']['en']['neutral_plate_alt']
            en['coverAlt'] = alt
        en['pages'] = [{'id': p['id'], 'title': p['title'],
            'body': '\n\n'.join(p['paragraphs']),
            'prayer': p.get('instruction', ''), 'heart': '',
            'alt': alt} for p in pages]
        staged[f'content/books/{slug}/book.json'] = book
        staged[f'content/books/{slug}/en.json'] = en
        staged[f'notes/{slug}.json'] = {
            'status': 'unpublished-layout-and-metadata-review-required',
            'grownUpNotes': plan['grown_up_notes'], 'metadata': plan['metadata'],
            'evidenceStatus': 'source-and-localized-claims-not-yet-mapped'}
    if output.exists() and any(output.iterdir()):
        raise ValueError('Refusing to overwrite an existing successor staging directory')
    for relative, value in staged.items():
        dest = output / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(value, ensure_ascii=False, indent=1) + '\n')
    plate_dest = output / 'media/mysteries/neutral-prayer-plate.svg'
    plate_dest.parent.mkdir(parents=True, exist_ok=True)
    plate_dest.write_bytes((root / 'docs/rosary-successor/neutral-prayer-plate.svg').read_bytes())
    return {'books': len(books), 'pages': sum(b['page_count'] for b in books.values()),
            'activationStatus': 'unpublished', 'files': len(staged) + 1}


if __name__ == '__main__':
    import argparse
    import sys
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', required=True, type=Path)
    parser.add_argument('--master', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build_successor(Path(__file__).resolve().parents[2],
        json.loads(args.spec.read_text()), args.master.read_bytes(), args.output)))
