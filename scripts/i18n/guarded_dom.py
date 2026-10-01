"""Side-effect-free exact-master text replacement. Never translate a moving DOM."""
import re
from bs4 import Comment


def translate_slots(container, slots, label='Mirror'):
    """Replace every visible source string, preserving tags and edge whitespace."""
    nodes = [n for n in container.find_all(string=True) if n.strip() and not isinstance(n, Comment)]
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
