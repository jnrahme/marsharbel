"""Registry-owned locale identity and explicit publication sets."""
from i18n.catalog import ROOT, read_json


def og_locales(registry=None):
    registry = registry or read_json(ROOT / 'locales/registry.json')
    order = registry['ogLocaleOrder']
    return {code: registry['locales'][code]['ogLocale'] for code in order}


def published_locales(registry, name):
    registry = registry or read_json(ROOT / 'locales/registry.json')
    return registry['publicationSets'][name]


def selector_aliases(registry):
    return {alias.lower(): code for code, config in registry['locales'].items()
            for alias in [code, *config.get('selectorAliases', [])]}
