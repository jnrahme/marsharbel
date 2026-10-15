"""Per-locale source citation targets for strict mirror twins.

A strict twin mirrors the master's words, but a citation link should land on the
reader's own edition: the Thai page cites the Thai bishops' catechesis text, the
Arabic page the Vatican's Arabic PDF. The mapping lives in the family's
pageMirrors entry as sourceLinks: {lang: {master_href: locale_href}} and is
applied after check_pair, like the other post-render passes. The
'localized-source-links' normalizer in mirror_structure reverts exactly these
registered pairs for the policy diff - nothing else gets a free pass.
"""
from bs4 import BeautifulSoup


def apply_localized_source_links(text, mapping):
    """Swap registered master hrefs for the locale's citation target.

    Every registered master href must occur exactly once: a missing or
    duplicated citation anchor is a page bug, not something to skip.
    """
    soup = BeautifulSoup(text, 'html.parser')
    for master_href, locale_href in mapping.items():
        anchors = soup.select(f'a[href="{master_href}"]')
        if len(anchors) != 1:
            raise ValueError(f'localized source link: expected exactly one anchor for {master_href}, found {len(anchors)}')
        anchors[0]['href'] = locale_href
    return str(soup)


def reverse_map(registry):
    """Every registered (locale href -> master href) pair across families."""
    pairs = {}
    for cfg in registry.get('pageMirrors', {}).values():
        for mapping in (cfg.get('sourceLinks') or {}).values():
            for master_href, locale_href in mapping.items():
                pairs[locale_href] = master_href
    return pairs
