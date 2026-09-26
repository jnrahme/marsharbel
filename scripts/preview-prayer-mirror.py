#!/usr/bin/env python3
"""Build an external review copy of the English/Arabic prayer mirror.

Never writes to the site's public HTML paths, sitemap or route map.
"""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from i18n.mirror import render_pair


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path, help='Preview output directory outside the repository')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    out = args.out.resolve()
    if out == root or root in out.parents:
        parser.error('Preview output must be outside the repository')
    pages = render_pair(root)
    for source, html in pages.items():
        path = out / source.relative_to(root)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding='utf-8')
        print(path)


if __name__ == '__main__':
    main()
