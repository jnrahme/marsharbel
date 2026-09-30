#!/usr/bin/env python3
"""Assemble <slug>-story-data.js from page-manifest.json + titles.json (final-bundle step)."""
import json, sys
from pathlib import Path
root = Path(__file__).parent
slug = root.name
upper = slug.upper().replace('-', '_')
titles = json.loads((root/'titles.json').read_text())
evid = json.loads((root/'evidence-keys.json').read_text())
rows = json.loads((root/'page-manifest.json').read_text())
out = []
for r in rows:
    refl = r.get('kind') == 'reflection'
    out.append({
        "illustration": f"./media/storybook-{slug}/images/page-{r['page']:02}.webp",
        "title": "Points of reflection" if refl else titles[str(r['page'])],
        "body": r['text'],
        "prayer": "",
        "heart": "",
        "scene": "birth",
        "audio": f"page-{r['page']:02}.mp3",
        "reflection": refl,
        "evidence": [{
            "type": "pastoral" if refl else "documented",
            "claim": ("This page offers pastoral guidance for children, drawn from the documented life and teaching of the saint."
                      if refl else
                      "An original retelling of documented events; imaginative composites and reported interior experiences are named in the story."),
            "sources": evid['reflection' if refl else 'narrative'],
        }],
    })
js = "window.%s_STORY_EN = %s\n" % (upper, json.dumps(out, indent=2, ensure_ascii=False))
(root.parent.parent / f"{slug}-story-data.js").write_text(js)
print(f"wrote {slug}-story-data.js", len(out), "pages")
