"""Finite SEO continuation proofs. These prove deltas, never owner approval.

Historical C2 records, bundle and pins are not changed. Callers must first run
that historical proof, then compare the returned preimage with their ORIGINAL
pin. This module is not a replacement for those guards and is not wired into
any guard by this foundation change. A content PR must explicitly integrate
and independently review each owning guard before activating a receipt.
"""
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urljoin, urlsplit, urlunsplit

RECEIPT = 'locales/seo-continuations.json'
MODULE = 'scripts/i18n/seo_continuations.py'
CLASSES = ('prayers-href', 'prayers-robots', 'faq-remove', 'article-add')
WINNER = '/saint-charbel-prayers'
ROBOT_VALUE = 'index,follow,max-image-preview:large'
# Literal finite membership, independently reviewed with this module.
ALLOWED_PATHS = frozenset((
    'ar/biography.html',
    'ar/feast-day.html',
    'ar/prayers.html',
    'ar/saint-charbel-chaplet.html',
    'de/biografie.html',
    'de/gebete.html',
    'de/gedenktag.html',
    'de/saint-charbel-places-lebanon.html',
    'en/prayers.html',
    'es/biografia.html',
    'es/oraciones.html',
    'fr/biographie.html',
    'fr/prieres.html',
    'hi/history.html',
    'history.html',
    'it/biografia.html',
    'it/preghiere.html',
    'pl/biografia.html',
    'pl/modlitwy.html',
    'pt/biografia.html',
    'pt/oracoes.html',
    'ru/biography.html',
    'ru/molitvy.html',
    'ru/saint-charbel-places-lebanon.html',
    'saint-charbel-chaplet.html',
    'saint-charbel-feast-day.html',
    'saint-charbel-places-lebanon.html',
    'saint-charbel-prayers.html',
    'src/pages/history.html',
    'src/pages/saint-charbel-chaplet.html',
    'src/pages/saint-charbel-feast-day.html',
    'src/pages/saint-charbel-places-lebanon.html',
    'templates/masters/history-exact.html',
    'templates/masters/saint-charbel-prayers.html',
    'templates/mirrors/prayers.html',
    'th/history.html',
    'zh-Hans/saint-charbel-places-lebanon.html',
))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def safe_path(path):
    if (not isinstance(path, str) or not re.fullmatch(r'[A-Za-z0-9._/-]+', path)
            or path.startswith('/') or any(x in ('', '.', '..') for x in path.split('/'))
            or not path.endswith('.html')):
        raise ValueError('continuation: unsafe HTML path')
    return path


class Spans(HTMLParser):
    """Locate real tags without rewriting their bytes or scanning raw text."""
    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.text = text
        self.lines = [0]
        self.lines.extend(m.end() for m in re.finditer('\n', text))
        self.inert = [m.span(2) for m in re.finditer(
            r'<(script|style|textarea|title)\b[^>]*>([\s\S]*?)</\1\s*>', text, re.I)]
        self.tags = []
        self.scripts = []
        self.script_start = None
        self.feed(text)
        self.close()
        if self.script_start is not None:
            raise ValueError('continuation: unclosed script')

    def source_offset(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        start = self.source_offset()
        if any(a <= start < b for a, b in self.inert):
            return
        raw = self.get_starttag_text()
        row = (tag, start, start + len(raw), attrs)
        self.tags.append(row)
        if tag == 'script':
            if self.script_start is not None:
                raise ValueError('continuation: nested script')
            self.script_start = row

    def handle_startendtag(self, tag, attrs):
        if tag == 'script':
            raise ValueError('continuation: self-closing script rejected')
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag == 'script' and self.script_start is not None:
            _, start, body_start, attrs = self.script_start
            end = self.text.find('>', self.source_offset())
            if end < 0:
                raise ValueError('continuation: malformed script close')
            self.scripts.append((start, end + 1, body_start, self.source_offset(), attrs))
            self.script_start = None


def replace_spans(text, edits):
    previous = len(text) + 1
    for start, end, replacement in sorted(edits, reverse=True):
        if not (0 <= start <= end < previous):
            raise ValueError('continuation: overlapping edits')
        text = text[:start] + replacement + text[end:]
        previous = start
    return text


def attrs_dict(attrs):
    keys = [k for k, _ in attrs]
    if len(keys) != len(set(keys)):
        raise ValueError('continuation: duplicate attribute')
    return dict(attrs)


def prayers_href(path, text):
    edits = []
    for tag, start, end, attrs in Spans(text).tags:
        if tag != 'a':
            continue
        attr = attrs_dict(attrs)
        href = attr.get('href')
        if not href:
            continue
        url = urlsplit(urljoin('https://marsharbel.com/' + path, href))
        if url.scheme not in ('http', 'https') or url.netloc != 'marsharbel.com':
            continue
        if url.path not in ('/en/prayers', '/en/prayers.html', '/en/prayers/'):
            continue
        target = urlunsplit(('', '', WINNER, url.query, url.fragment))
        raw = text[start:end]
        # Exact href attribute only. Never data-href, prose, comments or scripts.
        values = list(re.finditer(r'''(?<![\w:-])href\s*=\s*(["'])(.*?)\1''', raw, re.I | re.S))
        if len(values) != 1 or html.unescape(values[0][2]) != href:
            raise ValueError('continuation: unquoted or ambiguous href')
        match = values[0]
        edits.append((start + match.start(2), start + match.end(2), html.escape(target, quote=True)))
    return replace_spans(text, edits)


def prayers_robots(path, text):
    if path != 'saint-charbel-prayers.html':
        raise ValueError('continuation: robots only on prayer winner')
    parsed = Spans(text)
    heads = [(s, e) for tag, s, e, _ in parsed.tags if tag == 'head']
    if len(heads) != 1 or text.count('</head>') != 1:
        raise ValueError('continuation: winner head missing or ambiguous')
    close = text.index('</head>')
    edits = []
    for tag, start, end, attrs in parsed.tags:
        attr = attrs_dict(attrs)
        if tag == 'meta' and attr.get('name', '').lower() == 'robots':
            if not heads[0][1] <= start < close:
                raise ValueError('continuation: robots outside head')
            edits.append((start, end, '<meta name="robots" content="' + ROBOT_VALUE + '" />'))
    if len(edits) > 1:
        raise ValueError('continuation: duplicate robots')
    if not edits:
        edits = [(heads[0][1], heads[0][1], '\n<meta name="robots" content="' + ROBOT_VALUE + '" />')]
    return replace_spans(text, edits)


def require_plain_faq(data):
    """Only the observed plain FAQ vocabulary is deletable, never nested nodes."""
    allowed = {'@context', '@type', 'mainEntity', 'inLanguage', 'description', 'url'}
    if (set(data) - allowed or not {'@type', 'mainEntity'} <= set(data)
            or data['@type'] != 'FAQPage'
            or any(not isinstance(value, str) for key, value in data.items() if key != 'mainEntity')
            or not isinstance(data['mainEntity'], list)):
        raise ValueError('continuation: mixed FAQ graph or unsupported root shape')
    for question in data['mainEntity']:
        if (not isinstance(question, dict) or set(question) != {'@type', 'name', 'acceptedAnswer'}
                or question['@type'] != 'Question' or not isinstance(question['name'], str)):
            raise ValueError('continuation: mixed FAQ graph or unsupported Question shape')
        answer = question['acceptedAnswer']
        if (not isinstance(answer, dict) or set(answer) != {'@type', 'text'}
                or answer['@type'] != 'Answer' or not isinstance(answer['text'], str)):
            raise ValueError('continuation: mixed FAQ graph or unsupported Answer shape')


def faq_remove(path, text):
    edits = []
    for start, end, body_start, body_end, attrs in Spans(text).scripts:
        if attrs_dict(attrs).get('type', '').lower() != 'application/ld+json':
            continue
        try:
            data = json.loads(text[body_start:body_end])
        except ValueError as error:
            raise ValueError('continuation: malformed JSON-LD') from error
        # This first operation supports ONLY standalone FAQPage blocks. Mixed
        # graphs fail closed until separately designed and reviewed, never drop
        # a graph containing Article, breadcrumbs or other structured data.
        if isinstance(data, dict) and data.get('@type') == 'FAQPage' and '@graph' not in data:
            require_plain_faq(data)
            edits.append((start, end, ''))
        elif 'FAQPage' in json.dumps(data, ensure_ascii=False):
            raise ValueError('continuation: mixed FAQ graph not supported')
    return replace_spans(text, edits)



def article_add(path, text):
    """Minimal Article from existing page metadata, no invented dates or author."""
    parsed = Spans(text)
    types = set()
    for _, _, body_start, body_end, attrs in parsed.scripts:
        if attrs_dict(attrs).get('type', '').lower() != 'application/ld+json':
            continue
        try:
            data = json.loads(text[body_start:body_end])
        except ValueError as error:
            raise ValueError('continuation: malformed JSON-LD') from error
        def visit(node):
            if isinstance(node, dict):
                kind = node.get('@type', [])
                types.update([kind] if isinstance(kind, str) else kind)
                for value in node.values():
                    visit(value)
            elif isinstance(node, list):
                for value in node:
                    visit(value)
        visit(data)
    if 'Article' in types:
        return text
    canonicals, titles, descriptions, languages, images, heads = [], [], [], [], [], []
    for tag, start, end, attrs in parsed.tags:
        a = attrs_dict(attrs)
        if tag == 'head':
            heads.append(start)
        if tag == 'html' and a.get('lang'):
            languages.append(a['lang'])
        if tag == 'link' and 'canonical' in a.get('rel', '').split():
            canonicals.append(a.get('href'))
        if tag == 'meta':
            if a.get('property') == 'og:title':
                titles.append(a.get('content'))
            if a.get('name') == 'description':
                descriptions.append(a.get('content'))
            if a.get('property') == 'og:image':
                images.append(a.get('content'))
    if (any(len(items) != 1 or not items[0] for items in (canonicals, titles, descriptions, languages, heads))
            or len(images) > 1 or text.count('</head>') != 1):
        raise ValueError('continuation: missing or ambiguous Article metadata')
    canonical = urlsplit(canonicals[0])
    if canonical.scheme != 'https' or canonical.netloc != 'marsharbel.com' or canonical.query or canonical.fragment:
        raise ValueError('continuation: invalid Article canonical')
    data = {'@context': 'https://schema.org', '@type': 'Article',
            '@id': canonicals[0] + '#article', 'mainEntityOfPage': canonicals[0],
            'headline': titles[0], 'description': descriptions[0], 'inLanguage': languages[0]}
    if images:
        data['image'] = images[0]
    # Metadata is data, even inside a script. Escape closing-tag characters.
    payload = json.dumps(data, ensure_ascii=False, indent=2).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    close = text.index('</head>')
    return text[:close] + '<script type="application/ld+json">\n' + payload + '\n</script>\n' + text[close:]


def derive(path, before, operations):
    safe_path(path)
    if (not isinstance(operations, list) or not operations
            or not all(isinstance(op, str) for op in operations)
            or len(operations) != len(set(operations))
            or any(op not in CLASSES for op in operations)
            or operations != [op for op in CLASSES if op in operations]):
        raise ValueError('continuation: unknown, duplicate or unordered operation')
    text = before.decode('utf-8')
    for op in operations:
        text = {'prayers-href': prayers_href, 'prayers-robots': prayers_robots,
                'faq-remove': faq_remove, 'article-add': article_add}[op](path, text)
    return text.encode('utf-8')


def verify_delta(path, before, after, row):
    if not isinstance(row, dict) or set(row) != {'beforeSha256', 'afterSha256', 'operations'}:
        raise ValueError('continuation: unexpected receipt row fields')
    if not all(isinstance(row[k], str) and re.fullmatch('[0-9a-f]{64}', row[k])
               for k in ('beforeSha256', 'afterSha256')):
        raise ValueError('continuation: malformed digest')
    if sha(before) != row['beforeSha256'] or sha(after) != row['afterSha256']:
        raise ValueError('continuation: receipt digest mismatch')
    expected = derive(path, before, row['operations'])
    if expected == before:
        raise ValueError('continuation: no-op receipt rejected')
    if expected != after:
        raise ValueError('continuation: bytes outside fixed operation')
    return before


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.DEVNULL)



def require_regular_inputs(root, paths):
    """Recheck path identity on EVERY proof call, including warm-memo hits."""
    root = Path(root)
    for path in paths:
        file = root / path
        if not file.is_file() or file.is_symlink():
            raise ValueError('continuation: nonregular proof input ' + path)
        for parent in file.parents:
            if parent.is_symlink():
                raise ValueError('continuation: symlink proof parent ' + path)
            if parent == root:
                break
        if not file.resolve().is_relative_to(root.resolve()):
            raise ValueError('continuation: escaped proof input ' + path)


def verify_receipt(root):
    """Full current native tree binding. No editable-export or stale-memo pass."""
    root = Path(root)
    receipt = root / RECEIPT
    if not receipt.exists() and not receipt.is_symlink():
        return {}
    require_regular_inputs(root, [RECEIPT, MODULE])
    data = json.loads((root / RECEIPT).read_bytes())
    if not isinstance(data, dict) or set(data) != {'version', 'baseCommit', 'files'} or data['version'] != 1:
        raise ValueError('continuation: bad receipt schema')
    if not isinstance(data['files'], dict) or not data['files']:
        raise ValueError('continuation: empty or malformed file map')
    if any(path not in ALLOWED_PATHS for path in data['files']):
        raise ValueError('continuation: path outside fixed membership')
    base = data['baseCommit']
    if not isinstance(base, str) or not re.fullmatch('[0-9a-f]{40}', base):
        raise ValueError('continuation: base must be exact commit')
    if not isinstance(data['files'], dict) or not data['files']:
        raise ValueError('continuation: empty receipt')
    try:
        head = git(root, 'rev-parse', 'HEAD').decode().strip()
        if git(root, 'cat-file', '-t', base).strip() != b'commit':
            raise ValueError('continuation: base is not commit')
        subprocess.run(['git', '-C', str(root), 'merge-base', '--is-ancestor', base, head],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for path in [RECEIPT, MODULE, *data['files']]:
            if path not in (RECEIPT, MODULE):
                safe_path(path)
            file = root / path
            if (file.is_symlink() or not file.is_file()
                    or any(parent.is_symlink() for parent in file.parents if parent != root.parent)
                    or not file.resolve().is_relative_to(root.resolve())):
                raise ValueError('continuation: nonregular proof input')
            if (root / path).read_bytes() != git(root, 'show', head + ':' + path):
                raise ValueError('continuation: worktree differs from HEAD')
        # Hydration validates the fixed reviewed artifact independently. A
        # receipt cannot launder a different preimage merely by naming a newer
        # ancestor. The owner guards still run the complete B-to-C2 proof.
        from i18n import citation_history, citation_amendment
        citation_history.ensure_history(root, citation_amendment.load(root))
        preimages = {}
        for path, row in data['files'].items():
            before = git(root, 'show', base + ':' + path)
            if before != git(root, 'show', citation_history.REVIEWED_C + ':' + path):
                raise ValueError('continuation: preimage is not reviewed C2 bytes')
            after = (root / path).read_bytes()
            preimages[path] = verify_delta(path, before, after, row)
        return preimages
    except (subprocess.CalledProcessError, OSError) as error:
        raise ValueError('continuation: native proof unavailable') from error


def pinned_preimage(root, path, current):
    """Caller MUST compare result to its old pin; this proves no approval."""
    rows = verify_receipt(root)
    if path not in rows:
        return current
    if current != (Path(root) / path).read_bytes():
        raise ValueError('continuation: caller bytes differ from verified candidate')
    return rows[path]


def continue_outputs(root, texts):
    """Reapply fixed operations AFTER locale metadata is composed.

    Master renderers use original pinned preimages, not continued English schema.
    This prevents an English Article headline leaking into translated output.
    Final owning guards and stale-output checks still validate the result.
    """
    verified = verify_receipt(root)
    if not verified:
        return texts
    rows = json.loads((Path(root) / RECEIPT).read_bytes())['files']
    out = dict(texts)
    for file, text in texts.items():
        rel = Path(file).relative_to(root).as_posix()
        if rel in verified:
            out[file] = derive(rel, text.encode(), rows[rel]['operations']).decode()
    return out
