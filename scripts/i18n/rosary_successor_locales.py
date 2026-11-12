"""Assemble the all8 draft outside runtime. No activation or review receipt writes."""
import copy
import hashlib
import json
from pathlib import Path
from i18n.rosary_successor_adapter import (build_successor, public_metadata,
    public_illustration_notes, PASSION_SLUGS, MASTER_SHA256)
from i18n.reviewed_rosary_books import SLUGS, LOCALES

PUBLIC_COMMON_FIELDS = frozenset(('adult_notes_heading', 'sources_heading',
    'retelling_disclosure', 'reading_faq_question', 'reading_faq_answer'))


def project_locale(packet, original, plan, canonical, current, notes):
    slug = original['slug']
    candidate = next(b for b in packet['books'] if b['slug'] == slug)
    if candidate['english_source'] != original:
        raise ValueError('Frozen English embedding drift: ' + slug)
    translated = candidate['translation']
    metadata = candidate.get('metadata_translation', translated.get('metadata', {}))
    titles = metadata.get('page_titles', translated.get('page_titles', {}))
    if set(titles) != {p['id'] for p in plan['reader_pages']}:
        raise ValueError('Localized page-title coverage drift: ' + slug)
    if not all(isinstance(x, str) and x.strip() for x in titles.values()):
        raise ValueError('Empty localized title: ' + slug)
    if len(translated.get('prayers', [])) != 3:
        raise ValueError('Localized prayer membership drift: ' + slug)
    common = packet.get('common_translation', translated.get('common', {}))
    result = copy.deepcopy(current)
    result.update(review='text-reviewed-pending-render-rights-release',
        title=metadata['reader_title'], summary=metadata['summary'])
    result['coverAlt'] = (notes['locales'][packet['locale']]['neutral_plate_alt']
        if slug in PASSION_SLUGS else metadata.get('cover_alt', translated.get('cover_alt')))
    if not result['coverAlt']:
        raise ValueError('Missing localized cover alt: ' + slug)
    pages = []
    prayer_index = 0
    story_indices = []
    for page in plan['reader_pages']:
        instruction = ''
        if page['role'] == 'prayer':
            prayer = translated['prayers'][prayer_index]
            source_prayer = original['prayers'][prayer_index]
            if prayer.get('text_en_unchanged', source_prayer['text']) != source_prayer['text']:
                raise ValueError('Prayer English source drift: ' + slug)
            paragraphs = [prayer['text']]
            instruction = prayer['instruction']
            prayer_index += 1
        elif 'source_pointer' in page:
            index = int(page['source_pointer'].split('/')[-2])
            paragraphs = translated['pages'][index]['text']
            if len(paragraphs) != len(original['pages'][index]['text']):
                raise ValueError('Localized page paragraph count drift: ' + slug)
        elif page['role'] == 'reflection':
            paragraphs = translated['reflection']
            if len(paragraphs) != len(original['reflection']):
                raise ValueError('Localized reflection count drift: ' + slug)
        else:
            indices = page['source_paragraphs_1based']
            story_indices.extend(indices)
            if len(translated['narrative']) != len(original['narrative']):
                raise ValueError('Localized story count drift: ' + slug)
            paragraphs = [translated['narrative'][i-1] for i in indices]
        if not all(isinstance(t, str) and t.strip() for t in paragraphs):
            raise ValueError('Empty localized paragraph: ' + slug)
        pages.append({'id': page['id'], 'title': titles[page['id']],
            'body': '\n\n'.join(paragraphs), 'prayer': instruction,
            'heart': '', 'alt': result['coverAlt']})
    if 'narrative' in original and story_indices != list(range(1, len(original['narrative'])+1)):
        raise ValueError('Localized narrative mapping drift: ' + slug)
    result['pages'] = pages
    if [p['id'] for p in pages] != [p['id'] for p in canonical['pages']]:
        raise ValueError('Canonical locale pairing drift: ' + slug)
    # Sources are deliberately separate from public text until source/rights review.
    public_notes = {'grownUpNotes': translated.get('adult_notes', []),
        'metadata': public_metadata(metadata),
        'common': {k: common[k] for k in PUBLIC_COMMON_FIELDS if k in common},
        'publicIllustrationNotes': public_illustration_notes(notes, packet['locale'], slug)}
    return result, public_notes


def build_all_locales(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    if output == root or output.is_relative_to(root):
        raise ValueError('All8 output must be outside runtime checkout')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Refusing to overwrite existing all8 assembly')
    base = root/'docs/rosary-successor'
    manifest = json.loads((base/'locale-candidates.json').read_text())
    if manifest['activationStatus'] != 'unpublished' or manifest['releaseRightsStatus'] != 'held':
        raise ValueError('All8 assembly cannot authorize release')
    if set(manifest['locales']) != set(LOCALES)-{'en'}:
        raise ValueError('All8 locale coverage drift')
    packets = {}
    for code, record in manifest['locales'].items():
        data = (root/record['path']).read_bytes()
        if hashlib.sha256(data).hexdigest() != record['sha256']:
            raise ValueError('Locale candidate bytes drift: '+code)
        packet = json.loads(data)
        if packet['locale'] != code or packet['master_sha256'] != MASTER_SHA256:
            raise ValueError('Locale source identity drift: '+code)
        if len(packet['books']) != 20 or {b['slug'] for b in packet['books']} != set(SLUGS):
            raise ValueError('Locale book coverage drift: '+code)
        packets[code] = packet
    spec = json.loads((base/'integration-spec-v1.json').read_text())
    master_data = (base/'twenty-en-candidates-v3.json').read_bytes()
    originals = {b['slug']:b for b in json.loads(master_data)['books']}
    plans = {b['slug']:b for b in spec['books']}
    notes = json.loads((base/'illustration-notes-all8.json').read_text())
    # Fully validate localized projections before creating output.
    staged = {}
    for slug in SLUGS:
        canonical = {'pages': plans[slug]['reader_pages']}
        for code, packet in packets.items():
            current = json.loads((root/f'content/books/{slug}/{code}.json').read_text())
            text, public_notes = project_locale(packet, originals[slug], plans[slug], canonical, current, notes)
            staged[f'content/books/{slug}/{code}.json'] = text
            staged[f'notes/{code}/{slug}.json'] = public_notes
    build_successor(root, spec, master_data, output)
    for path, value in staged.items():
        target = output/path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(value, ensure_ascii=False, indent=1)+'\n')
    return {'books':20, 'locales':8, 'editions':160,
        'pageStates':sum(len(p['reader_pages']) for p in plans.values())*8,
        'activationStatus':'unpublished', 'releaseRightsStatus':'held'}


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', required=True, type=Path)
    args = p.parse_args()
    print(json.dumps(build_all_locales(Path(__file__).resolve().parents[2], args.output)))
