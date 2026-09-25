#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

FAILURES=0

echo "[dead-code] Checking for unreferenced JS files..."

# Collect all JS files in root (exclude node_modules, tmp, .venv, .git)
while IFS= read -r jsfile; do
  basename=$(basename "$jsfile")
  # Check if any HTML file references this JS file
  if ! grep -rql "$basename" --include="*.html" . --exclude-dir=node_modules --exclude-dir=tmp --exclude-dir=.venv --exclude-dir=.git >/dev/null 2>&1; then
    # Also check if any JS file references it
    if ! grep -rql "$basename" --include="*.js" . --exclude-dir=node_modules --exclude-dir=tmp --exclude-dir=.venv --exclude-dir=.git --exclude="$basename" >/dev/null 2>&1; then
      echo "  DEAD JS: $jsfile (not referenced by any HTML or JS file)"
      FAILURES=$((FAILURES + 1))
    fi
  fi
done < <(find . -maxdepth 1 -name "*.js" -not -name "service-worker.js" | sort)

echo "[dead-code] Checking for old versioned JS backups..."

# Find versioned JS files and check if they're the latest version
for base in global-audio-player mystery-meditation; do
  latest=""
  for vfile in $(ls ${base}.v*.js 2>/dev/null | sort -V); do
    latest="$vfile"
  done
  if [ -n "$latest" ]; then
    for vfile in $(ls ${base}.v*.js 2>/dev/null | sort -V); do
      if [ "$vfile" != "$latest" ]; then
        # Verify the old version isn't referenced
        vbase=$(basename "$vfile")
        if ! grep -rql "$vbase" --include="*.html" . --exclude-dir=node_modules --exclude-dir=tmp --exclude-dir=.venv --exclude-dir=.git >/dev/null 2>&1; then
          echo "  DEAD VERSION: $vfile (superseded by $latest)"
          FAILURES=$((FAILURES + 1))
        fi
      fi
    done
  fi
done

echo "[dead-code] Checking for unreferenced images..."

# Check gallery images
for img in gallery/*.jpg gallery/*.jpeg gallery/*.png; do
  [ -f "$img" ] || continue
  imgbase=$(basename "$img")
  if ! grep -rql "$imgbase" --include="*.html" --include="*.js" . --exclude-dir=node_modules --exclude-dir=tmp --exclude-dir=.venv --exclude-dir=.git >/dev/null 2>&1; then
    echo "  DEAD IMAGE: $img (not referenced in HTML or JS)"
    FAILURES=$((FAILURES + 1))
  fi
done

# Check mockup-products images
for img in mockup-products/*.jpg mockup-products/*.jpeg mockup-products/*.png; do
  [ -f "$img" ] || continue
  imgbase=$(basename "$img")
  if ! grep -rql "$imgbase" --include="*.html" --include="*.js" . --exclude-dir=node_modules --exclude-dir=tmp --exclude-dir=.venv --exclude-dir=.git >/dev/null 2>&1; then
    echo "  DEAD IMAGE: $img (not referenced in HTML or JS)"
    FAILURES=$((FAILURES + 1))
  fi
done

# Check storybook images for .bak files
for img in media/storybook/images/*.bak.png; do
  [ -f "$img" ] || continue
  echo "  DEAD IMAGE: $img (backup file)"
  FAILURES=$((FAILURES + 1))
done

echo "[dead-code] Checking for orphan HTML pages..."

has_clean_inbound_link() {
  python3 - "$1" <<'PY'
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
import sys

target = '/' + Path(sys.argv[1]).stem

class Links(HTMLParser):
    found = False

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        href = dict(attrs).get('href', '')
        url = urlsplit(urljoin(self.base, href))
        if url.netloc == 'marsharbel.com' and url.path.rstrip('/') == target:
            self.found = True

for path in [*Path('.').glob('*.html'), *Path('mysteries').glob('*.html'), *Path('miracles').glob('*.html')]:
    if path.name == sys.argv[1]:
        continue
    parser = Links()
    parser.base = 'https://marsharbel.com/' + path.as_posix()
    parser.feed(path.read_text())
    if parser.found:
        sys.exit(0)
sys.exit(1)
PY
}

# Check each root HTML page has at least one inbound link from another HTML page
for htmlfile in *.html; do
  [ -f "$htmlfile" ] || continue
  # Skip special files and known intentional orphans
  # mystery-meditation.html = alternate entry point for rosary meditation
  # souvenirs.html = store paused 2026-09-24 (nav links removed site-wide); page intentionally kept, reachable by direct URL for relaunch
  # rosary-source-text.html = SEO redirect (has meta refresh + noindex)
  # testimony-review.html = admin/moderation page (noindex)
  # voice-lab.html = internal dev/testing tool
  case "$htmlfile" in
    google*.html|index.html) continue ;;
    mystery-meditation.html|rosary-source-text.html|testimony-review.html|voice-lab.html|souvenirs.html) continue ;;
  esac
  # Check if any OTHER html file links to this page
  if ! grep -rql "$htmlfile" --include="*.html" . --exclude-dir=node_modules --exclude-dir=tmp --exclude-dir=.venv --exclude-dir=.git --exclude="$htmlfile" >/dev/null 2>&1; then
    # Also check JS files (some pages are navigated to via JS); match both the
    # .html filename and the clean-URL stem (links migrated to extensionless URLs)
    stem="${htmlfile%.html}"
    if ! grep -rql "$htmlfile" --include="*.js" . --exclude-dir=node_modules --exclude-dir=tmp --exclude-dir=.venv --exclude-dir=.git >/dev/null 2>&1 \
      && ! grep -rql "/$stem[\"'/?#]" --include="*.js" . --exclude-dir=node_modules --exclude-dir=tmp --exclude-dir=.venv --exclude-dir=.git >/dev/null 2>&1; then
      if has_clean_inbound_link "$htmlfile"; then
        continue
      fi
      echo "  ORPHAN HTML: $htmlfile (no inbound links from other pages)"
      FAILURES=$((FAILURES + 1))
    fi
  fi
done

echo ""
if [ "$FAILURES" -gt 0 ]; then
  echo "[dead-code] Found $FAILURES dead code issue(s)."
  exit 1
else
  echo "[dead-code] No dead code found."
  exit 0
fi
