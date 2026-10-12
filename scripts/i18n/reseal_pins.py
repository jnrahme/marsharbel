"""Deterministic review-pin reseal after registering a new Arabic twin family.

Registering a pageMirrors family rewrites that route's href in the shared nav
chrome of the twin's locale pages (e.g. href="/gallery" -> href="/ar/gallery"
on ar pages), which legitimately drifts reviewed-body pins. This script
performs the reseal as a machine-checked step, never a hand edit:

  1. Render the full build in memory with the pin gates temporarily inert
     (in-process monkeypatch only; no gate file is modified on disk).
  2. For each pinned variant whose rendered body drifted, prove scope with a
     byte-exact revert: replacing every rendered href="<twin route>" with
     href="<english route>" for that variant's locale must reproduce the
     origin/stage bytes exactly. Any other byte change aborts the reseal.
  3. Only then rewrite the variant's bodySha256 to the new rendered digest.

Rerunnable after rebase (always compares against current origin/stage).
Non-author review still verifies the reseal per the merge-train rule; this
script is the deterministic mechanism, not the approval.

Usage: python3 scripts/i18n/reseal_pins.py          # report only
       python3 scripts/i18n/reseal_pins.py --write  # rewrite accepted pins
"""
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))

from bs4 import BeautifulSoup
import i18n.reviewed_history as rh
import i18n.reviewed_travel as rt

PIN_FILES = ['locales/history-equivalence.json', 'locales/travel-equivalence.json']


def digest_main(text):
    return hashlib.sha256(str(BeautifulSoup(text, 'html.parser').main).encode()).hexdigest()


def stage_bytes(rel):
    r = subprocess.run(['git', 'show', f'origin/stage:{rel}'], capture_output=True, cwd=ROOT)
    return r.stdout.decode() if r.returncode == 0 else None


def twin_rewrites():
    """(locale, twin route, english route) triples this change adds.

    Only pageMirrors entries (or renderLocales within an entry) that are NEW
    versus origin/stage legitimately drift pins; twins already registered on
    stage are part of the reviewed bytes and reverting them would corrupt the
    scope proof. Rebase-safe: always diffs against current origin/stage.
    """
    current = json.loads((ROOT / 'locales/registry.json').read_text()).get('pageMirrors', {})
    r = subprocess.run(['git', 'show', 'origin/stage:locales/registry.json'],
                       capture_output=True, cwd=ROOT)
    base = json.loads(r.stdout.decode()).get('pageMirrors', {}) if r.returncode == 0 else {}
    out = []
    for name, cfg in current.items():
        base_cfg = base.get(name, {})
        base_locales = set(base_cfg.get('renderLocales', []))
        english = cfg.get('english')
        for code in cfg.get('renderLocales', []):
            if code in base_locales:
                continue
            route = cfg.get('routes', {}).get(code)
            if english and route:
                out.append((code, route, english))
    return out


def rendered_texts():
    rh.history_manifest = lambda root, texts, manifest: manifest
    rt.travel_manifest = lambda root, texts, manifest: manifest
    import importlib
    build = importlib.import_module('build-international')
    return build.outputs()


def main():
    write = '--write' in sys.argv
    texts = rendered_texts()
    rewrites = twin_rewrites()
    accepted, rejected = [], []
    for pin_rel in PIN_FILES:
        pin_path = ROOT / pin_rel
        if not pin_path.exists():
            continue
        data = json.loads(pin_path.read_text())
        swaps = []
        for code, v in data.get('variants', {}).items():
            f = ROOT / v['file']
            new = texts.get(f)
            if new is None:
                new = f.read_text() if f.exists() else None
            if new is None or digest_main(new) == v['bodySha256']:
                continue
            base = stage_bytes(v['file'])
            reverted = new
            for loc, twin, english in rewrites:
                if loc == code:
                    reverted = reverted.replace(f'href="{twin}"', f'href="{english}"')
            if base is None or reverted != base:
                rejected.append(f"{pin_rel}:{code} ({v['file']})")
                continue
            accepted.append((pin_rel, code, v['file'], v['bodySha256'], digest_main(new)))
            if write:
                swaps.append((v['bodySha256'], digest_main(new)))
        if write and swaps:
            text = pin_path.read_text()
            for old_sha, new_sha in swaps:
                assert text.count(old_sha) == 1, f'pin sha not unique in {pin_rel}'
                text = text.replace(old_sha, new_sha)
            pin_path.write_text(text)
    for pin_rel, code, file, old, new in accepted:
        print(f'RESEAL-OK {pin_rel} {code} {file} {old[:12]}->{new[:12]}')
    for r in rejected:
        print(f'RESEAL-REJECTED {r}')
    if rejected:
        sys.exit(1)
    print(f'{len(accepted)} variant pins resealed' if write else f'{len(accepted)} variant pins eligible (report only)')


if __name__ == '__main__':
    main()
