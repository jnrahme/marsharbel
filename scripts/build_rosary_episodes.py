#!/usr/bin/env python3
"""Build src/pages/rosary-episodes.html from content/rosary/episodes.json.

First build-time reader of the content layer (architecture plan PR 1B): the
content/ record is the single source for the daily-rosary video index, and the
served page template is regenerated from it deterministically. The page is a
registered private preview (locales/private-preview-pages.json): noindex, not
in any sitemap, and no inbound links, so merging changes no public surface.
Promotion to public is a later PR (delete the registry entry, ship the keyed
locale mirrors, add nav/sitemap/VideoObject) per the architecture plan.

Usage:
  python3 scripts/build_rosary_episodes.py          # write src/pages/rosary-episodes.html
  python3 scripts/build_rosary_episodes.py --check  # fail if the template is stale
"""
import argparse
import calendar
import json
import re
import sys
from datetime import date
from html import escape as _html_escape


def esc(text):
    # Match build-pages.mjs: escape & < > and double quotes only.
    return _html_escape(text, quote=True).replace('&#x27;', "'")
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EPISODES = ROOT / 'content' / 'rosary' / 'episodes.json'
OUT = ROOT / 'src' / 'pages' / 'rosary-episodes.html'

YOUTUBE_ID = re.compile(r'[A-Za-z0-9_-]{11}')
DATE = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}')
LANGUAGE = re.compile(r'[a-z]{2}(-[A-Za-z]{2,5})?')
MYSTERIES = {'joyful', 'sorrowful', 'glorious', 'luminous'}
LANGUAGE_NAMES = {'en': 'English', 'ar': 'Arabic'}
REQUIRED = ('date', 'mystery', 'language', 'youtubeId', 'title')
ALLOWED = set(REQUIRED) | {'description', 'saint', 'transcriptExcerpt'}

HEAD = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Daily rosary videos | Saint Charbel</title>
  <meta name="description" content="Internal preview of the daily rosary video index generated from the content layer. Not published, not linked, not indexed." />
  <meta name="robots" content="noindex, nofollow" />
  <link rel="icon" href="./favicon.ico" />
  {{> head-font-preloads}}
  <link rel="stylesheet" href="./styles.css?v=20260922-1" />
</head>
<body>
  {{> skip-link}}
  {{> header-open-8}}{{> primary-nav}}{{> header-close-1}}

  <main id="main-content" class="site-shell" tabindex="-1">
    <section class="section" id="daily-rosary-videos">
      <span class="kicker">Internal preview - not published</span>
      <h1>Daily rosary videos</h1>
      <p class="section-sub">Every guided daily rosary episode, newest first. This page is generated from <code>content/rosary/episodes.json</code> by <code>scripts/build_rosary_episodes.py</code>; edit the data, not this file. Embeds use youtube-nocookie.com - no YouTube cookies are set unless you press play.</p>
'''

FOOT = '''    </section>
  </main>

  {{> footer-credit-a "Built for marsharbel.com."}}

  <script defer src="./app.js"></script>
  <script defer src="./global-audio-player.js"></script>
  <script defer src="/locale-routes.js"></script>
  <script defer src="./translate.js?v=20260922-1"></script>
  <script src="./nav.js?v=20260922-1" defer></script>
</body>
</html>
'''

EMPTY_CARD = '''      <div class="grid-2">
        <article class="card update">
          <p>No episodes are registered yet. Each published daily rosary video lands here as one entry in <code>content/rosary/episodes.json</code>.</p>
        </article>
      </div>
'''


def load_episodes(path):
    """Read and fail-closed validate the registry; returns the episode list."""
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('schema') != 1:
        raise ValueError('episodes registry must be an object with "schema": 1')
    episodes = data.get('episodes')
    if not isinstance(episodes, list):
        raise ValueError('episodes registry must carry an "episodes" list')
    for i, ep in enumerate(episodes):
        where = 'episodes[%d]' % i
        if not isinstance(ep, dict):
            raise ValueError(where + ': not an object')
        unknown = set(ep) - ALLOWED
        if unknown:
            raise ValueError(where + ': unknown fields ' + ','.join(sorted(unknown)))
        for field in REQUIRED:
            if not isinstance(ep.get(field), str) or not ep[field].strip():
                raise ValueError(where + ': missing or empty ' + field)
        if not DATE.fullmatch(ep['date']):
            raise ValueError(where + ': bad date ' + ep['date'])
        date.fromisoformat(ep['date'])  # rejects impossible dates
        if ep['mystery'] not in MYSTERIES:
            raise ValueError(where + ': bad mystery ' + ep['mystery'])
        if not LANGUAGE.fullmatch(ep['language']):
            raise ValueError(where + ': bad language ' + ep['language'])
        if not YOUTUBE_ID.fullmatch(ep['youtubeId']):
            raise ValueError(where + ': bad youtubeId ' + ep['youtubeId'])
    return episodes


def sort_key(ep):
    # Newest first; language and id break ties so the output is deterministic.
    return (-int(ep['date'].replace('-', '')), ep['language'], ep['youtubeId'])


def long_date(iso):
    d = date.fromisoformat(iso)
    return '%s %d, %d' % (calendar.month_name[d.month], d.day, d.year)


def card(ep):
    vid = ep['youtubeId']
    title = esc(ep['title'])
    mystery = ep['mystery'].capitalize() + ' Mysteries'
    language = LANGUAGE_NAMES.get(ep['language'], ep['language'])
    meta = '%s · %s · %s' % (mystery, language, long_date(ep['date']))
    lines = [
        '        <article class="card update">',
        '          <div class="video-wrap"><iframe src="https://www.youtube-nocookie.com/embed/%s" title="%s" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe></div>' % (vid, title),
        '          <p><strong>%s</strong></p>' % esc(meta),
    ]
    if ep.get('saint'):
        lines.append('          <p>Feast focus: %s.</p>' % esc(ep['saint']))
    lines.append(
        '          <p>%s. <a href="https://www.youtube.com/watch?v=%s" target="_blank" rel="noopener">Watch on YouTube</a>.</p>' % (title, vid))
    lines.append('        </article>')
    return '\n'.join(lines) + '\n'


def render(episodes):
    out = [HEAD]
    if episodes:
        out.append('      <div class="grid-2">\n')
        out.extend(card(ep) for ep in sorted(episodes, key=sort_key))
        out.append('      </div>\n')
    else:
        out.append(EMPTY_CARD)
    out.append(FOOT)
    return ''.join(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    episodes = load_episodes(EPISODES)
    rendered = render(episodes)
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding='utf-8') != rendered:
            print('rosary-episodes.html is stale: run scripts/build_rosary_episodes.py', file=sys.stderr)
            return 1
        print('rosary-episodes.html matches content/rosary/episodes.json')
        return 0
    OUT.write_text(rendered, encoding='utf-8')
    print('wrote %s (%d episodes)' % (OUT.relative_to(ROOT), len(episodes)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
