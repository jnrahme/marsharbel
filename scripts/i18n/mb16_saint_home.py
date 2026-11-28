"""Compose only the exact existing saint generator span with MB16 discovery.

The generator implementation is fixed, data remains separately reviewed, and
all bytes outside the one marked saint block retain the original MB16 pin.
No general HTML stripping and no replacement of historical master hashes.
"""
import importlib.util
from pathlib import Path
import tempfile

MODULE = 'scripts/i18n/mb16_saint_home.py'
CONTROLS = {'scripts/build_saint_of_day.py': '552f5cc7a316a428508af916f5e3acef196f84c70411fb0409f3eca6c1f52c53', 'scripts/i18n/saint_plate.py': 'a9f084a3acf4a99812a9fe755e762822d7397babdec7714389c141d8dc4b6c39', 'templates/saint-of-day/home.html': 'f48d7a139f9f7d7e73d1a0edb3e24c1b82a9d68f2f59ae8ef3ee8d5871fdc78b', 'templates/saint-of-day/home-nobook.html': '39c9dfad11937845c9e822d2b4960bc4f9c41f37d9c00479c8cd1ee412ed3580', 'templates/saint-of-day/home-nobook-mono.html': '789899899072164c156ead8ea66b64584da5391c69332c1f86452ae7523d3724', 'templates/saint-of-day/home-nobook-image.html': 'ded5b37a94c21f62598a193fc63ffd7830a98c8eb509126070f5fb697c32964d'}
DATA = ('locales/saint-of-day.json', 'locales/en/saint-of-day.json', 'src/pages/index.html')
INPUTS = tuple(CONTROLS) + DATA
START = b'<!-- saint-of-day:start -->'
END = b'<!-- saint-of-day:end -->'


def span(raw):
    if raw.count(START) != 1 or raw.count(END) != 1:
        raise ValueError('MB16 saint: missing or duplicate markers')
    a, z = raw.index(START), raw.index(END) + len(END)
    if a >= z:
        raise ValueError('MB16 saint: reversed markers')
    return a, z


def generated_block(root, revision=None):
    from i18n.mb16_home_continuation import git, sha
    from i18n.seo_continuations import require_regular_inputs
    root = Path(root)
    require_regular_inputs(root, [MODULE, *INPUTS])
    if revision and (root / MODULE).read_bytes() != git(root, 'show', revision + ':' + MODULE):
        raise ValueError('MB16 saint: module differs from native HEAD')
    payload = {p: git(root, 'show', revision + ':' + p) if revision else
               (root / p).read_bytes() for p in INPUTS}
    for p, expected in CONTROLS.items():
        if sha(payload[p]) != expected:
            raise ValueError('MB16 saint: fixed generator/template changed ' + p)
    # Only local fixed implementation executes. Native snapshots supply data,
    # never executable source. Source HTML is inert generator input.
    for p, expected in CONTROLS.items():
        if sha((root / p).read_bytes()) != expected:
            raise ValueError('MB16 saint: disk generator/template changed ' + p)
    spec = importlib.util.spec_from_file_location('mb16_fixed_saint_builder', root / 'scripts/build_saint_of_day.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    with tempfile.TemporaryDirectory(prefix='mb16-saint-inputs-') as tmp:
        target = Path(tmp)
        for p, raw in payload.items():
            file = target / p
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(raw)
        _, output = builder.output(target)
        raw = output.encode()
    a, z = span(raw)
    return raw[a:z]


def restore(root, original, candidate, revision=None):
    """Validate generated candidate, restoring only its one saint span."""
    a, z = span(original)
    ca, cz = span(candidate)
    if candidate[ca:cz] == original[a:z]:
        return candidate
    if candidate[ca:cz] != generated_block(root, revision):
        raise ValueError('MB16 saint: candidate is not exact generated saint block')
    return candidate[:ca] + original[a:z] + candidate[cz:]


def reapply(original, candidate):
    """Keep the independent current home catalog responsible for saint copy."""
    a, z = span(original)
    ca, cz = span(candidate)
    return original[:a] + candidate[ca:cz] + original[z:]
