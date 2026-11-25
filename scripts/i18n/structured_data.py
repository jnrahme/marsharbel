"""Public FAQ schema policy, applied after localized metadata composition.

Visible Q&A and existing schema retain their original bytes. Minimal Articles
use only the page's existing metadata through the reviewed fixed transform.
"""
from i18n.seo_continuations import derive


def normalize(path, text):
    without_faq = derive(path, text.encode(), ['faq-remove'])
    if without_faq == text.encode():
        return text
    return derive(path, without_faq, ['article-add']).decode()


def normalize_outputs(root, texts):
    return {file: normalize(file.relative_to(root).as_posix(), text)
            if file.suffix == '.html' else text for file, text in texts.items()}
