"""Side-effect-free exact-master text replacement. Never translate a moving DOM."""
import re
from bs4 import Comment


def translatable_nodes(container):
    """Visible-copy candidates only; CSS visibility is not inferred server-side.

    Callers must audit their container for CSS-only hidden content. Explicitly
    hidden/inert and non-content descendants remain untouched, as do comments.
    """
    result = []
    for node in container.find_all(string=True):
        if isinstance(node, Comment) or not node.strip():
            continue
        if any(parent.name in {'script', 'style', 'template', 'noscript'}
               or parent.has_attr('hidden') or parent.has_attr('inert')
               or parent.get('aria-hidden', '').lower() == 'true'
               for parent in node.parents if getattr(parent, 'name', None)):
            continue
        result.append(node)
    return result


def translate_slots(container, slots, label='Mirror'):
    """Replace every visible source string, preserving tags and edge whitespace."""
    nodes = translatable_nodes(container)
    if set(slots) != {str(i) for i in range(len(nodes))}:
        raise ValueError(f'{label} slot count changed')
    replacements = []
    for i, node in enumerate(nodes):
        slot = slots[str(i)]
        if set(slot) != {'source', 'text'}:
            raise ValueError(f'{label} invalid slot {i}')
        if ' '.join(str(node).split()) != slot['source']:
            raise ValueError(f'{label} master changed at slot {i}')
        text = slot['text']
        if not isinstance(text, str) or not text.strip() or re.search(r'[<>]', text):
            raise ValueError(f'Unsafe {label.lower()} slot {i}')
        old = str(node)
        leading = old[:len(old) - len(old.lstrip())]
        trailing = old[len(old.rstrip()):]
        replacements.append((node, leading + text + trailing))
    # Validate every slot before applying any replacement.
    for node, text in replacements:
        node.replace_with(text)
