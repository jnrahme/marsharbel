"""Registry-driven RU hub href repair in seven existing keyed renderers.
Preserve all bytes except exact Travel hrefs in header/breadcrumb chrome.
"""
import re

FAMILIES = {'home', 'annaya-master', 'twenty-second-master', 'pilgrimage-master',
            'history-master', 'saint-charbel-prayers-master', 'saint-charbel-novena-master'}


def localize_travel_chrome(text, registry, lang, family):
    if lang != 'ru' or family not in FAMILIES:
        return text
    hubs = [cfg['routes'][lang] for cfg in registry.get('pageMirrors', {}).values()
            if cfg.get('english') == '/travel' and lang in cfg.get('renderLocales', [])
            and lang in cfg.get('routes', {})]
    if not hubs:
        return text
    if len(set(hubs)) != 1:
        raise ValueError('Ambiguous registered RU Travel hub')
    hub = hubs[0]
    if not re.fullmatch(r'/[a-zA-Z0-9/_-]+', hub):
        raise ValueError('Unsafe registered Travel hub route')
    # The generated keyed serializers emit quoted attributes. Restrict matches
    # to exact local /travel anchors, not submenu destinations or global URLs.
    def replace_block(match):
        return re.sub(r'(<a\b[^>]*\s+href=)(["\'])/travel\2',
                      lambda anchor: anchor[1] + anchor[2] + hub + anchor[2],
                      match[0])
    text = re.sub(r'<header\b[^>]*>.*?</header>', replace_block, text, flags=re.S)
    return re.sub(r'<nav\b(?=[^>]*\bclass=["\'][^"\']*\btravel-breadcrumb\b)[^>]*>.*?</nav>',
                  replace_block, text, flags=re.S)
