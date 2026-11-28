"""Shared header chrome labels for authored mirrors, always from reviewed locale catalogs."""
from i18n.catalog import read_json

COMMON_NAV = {'Media': 'navigation.media', 'Music': 'navigation.music', 'Video': 'navigation.video', 'Gallery': 'navigation.gallery'}
HOME_HEADER = ('home.header.our-lady-of-lebanon-at-harissa', 'home.header.the-cedars-of-god', 'home.header.bkerke-and-the-maronite-patriarchate')


def shared_header_chrome(root, lang):
    """Map English header labels to the locale's reviewed text; never new text."""
    common = read_json(root / f'locales/{lang}/common.json')
    chrome = {english: common[key] for english, key in COMMON_NAV.items()}
    en_home = read_json(root / 'locales/en/home-copy.json')
    local_home = read_json(root / f'locales/{lang}/home-copy.json')
    chrome.update({en_home[key]: local_home[key] for key in HOME_HEADER})
    return chrome
