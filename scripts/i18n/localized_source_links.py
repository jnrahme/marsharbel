"""Per-locale source citation targets for strict mirror twins.

A strict twin mirrors the master's words, but a citation link should land on the
reader's own edition: the Thai page cites the Thai bishops' catechesis text, the
Arabic page the Vatican's Arabic PDF. The mapping lives in the family's
pageMirrors entry as sourceLinks: {lang: {master_href: locale_href}} and is
applied after check_pair, like the other post-render passes.

The 'localized-source-links' normalizer in mirror_structure is the strict
inverse for the policy diff: it reverts exactly the pairs registered for the
page's own family+locale - never a registry-wide reversal - and fails on a
missing, duplicated, wrong-locale, or unregistered citation anchor instead of
passing silently. The structural signature records no hrefs, so citation
correctness is asserted explicitly in the locale mirror policy test as well.
"""
from bs4 import BeautifulSoup


def _require_one_to_one(mapping):
    locale_hrefs = list(mapping.values())
    if len(set(locale_hrefs)) != len(locale_hrefs):
        raise ValueError('localized source link: mapping is not one-to-one (shared locale target)')


def apply_localized_source_links(text, mapping):
    """Swap registered master hrefs for the locale's citation target.

    Every registered master href must occur exactly once: a missing or
    duplicated citation anchor is a page bug, not something to skip. The mapping
    itself must be one-to-one so the inverse cannot be ambiguous.
    """
    _require_one_to_one(mapping)
    soup = BeautifulSoup(text, 'html.parser')
    for master_href, locale_href in mapping.items():
        anchors = soup.select(f'a[href="{master_href}"]')
        if len(anchors) != 1:
            raise ValueError(f'localized source link: expected exactly one anchor for {master_href}, found {len(anchors)}')
        anchors[0]['href'] = locale_href
    return str(soup)


def resolve_family(registry, master, route, lang):
    """The single pageMirrors family that owns this exact rendered page."""
    matches = [name for name, cfg in registry.get('pageMirrors', {}).items()
               if cfg.get('master') == master and (cfg.get('routes') or {}).get(lang) == route]
    if len(matches) != 1:
        raise ValueError(f'localized source link: expected one family for {master} {route} {lang}, found {len(matches)}')
    return matches[0]


def scoped_mapping(registry, family, lang):
    """The registered swap set for one family+locale; absence is a config bug."""
    cfg = registry.get('pageMirrors', {}).get(family, {})
    mapping = (cfg.get('sourceLinks') or {}).get(lang)
    if not mapping:
        raise ValueError(f'localized source link: no sourceLinks mapping registered for {family} {lang}')
    _require_one_to_one(mapping)
    return mapping


def registered_targets(registry, skip_family=None, skip_lang=None):
    """Every locale href registered anywhere, minus one (family, lang) scope."""
    targets = {}
    for name, cfg in registry.get('pageMirrors', {}).items():
        for code, mapping in (cfg.get('sourceLinks') or {}).items():
            if name == skip_family and code == skip_lang:
                continue
            for locale_href in mapping.values():
                targets.setdefault(locale_href, []).append(f'{name}:{code}')
    return targets


def strip_localized_source_links(soup, registry, family, lang):
    """Revert this page's registered citation swaps, and only those.

    Strict inverse of apply_localized_source_links scoped to the page's own
    (family, lang):
    - each registered locale target must occur exactly once on the twin - a
      missing or duplicated citation anchor fails, never passes silently;
    - an anchor carrying another locale's or another family's registered
      target is a wrong-locale/unregistered swap and fails;
    - unregistered anchors are never touched (no registry-wide reversal).
    """
    mapping = scoped_mapping(registry, family, lang)
    own_targets = set(mapping.values())
    for master_href, locale_href in mapping.items():
        anchors = soup.select(f'a[href="{locale_href}"]')
        if len(anchors) != 1:
            raise ValueError(f'localized source link: expected exactly one {family}:{lang} citation anchor for {locale_href}, found {len(anchors)}')
        anchors[0]['href'] = master_href
    foreign = {href: owners for href, owners in registered_targets(registry, skip_family=family, skip_lang=lang).items()
               if href not in own_targets}
    for anchor in soup.select('a[href]'):
        owners = foreign.get(anchor['href'])
        if owners:
            raise ValueError(f'localized source link: {family}:{lang} page carries a citation target registered to {owners}: {anchor["href"]}')
    return soup
