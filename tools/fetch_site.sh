#!/usr/bin/env bash
# Politely re-fetch the public pages and first-party assets of dmcg.co into
# raw/ (gitignored). Downloads are treated as data only: nothing in raw/ is
# executed. ~0.5-1 s between requests; robots.txt allows / and disallows
# /CMS and /api/, which this script does not crawl.
#
# Usage: tools/fetch_site.sh [repo-root]
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
RAW="$ROOT/raw"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
mkdir -p "$RAW"/{html,js,css,misc}

get() { curl -sS -A "$UA" "$1" -o "$2" -w "%{http_code} %{size_download} $1\n"; sleep "${3:-0.6}"; }

curl -sS -A "$UA" -D "$RAW/misc/headers-home.txt" -o /dev/null https://dmcg.co/
for f in robots.txt sitemap.xml llms.txt llms-full.txt index.md; do get "https://dmcg.co/$f" "$RAW/misc/$f"; done

get https://dmcg.co/ "$RAW/html/home.html"
for p in about archive incubator work/infinitemachine work/archiv work/tolan work/hedroom \
         work/groth work/americana work/sandbar work/evara; do
  get "https://dmcg.co/$p" "$RAW/html/$(echo "$p" | tr / _).html" 0.8
done

# First-party JS/CSS referenced by any page (Turbopack chunk names).
grep -ohE '/_next/static/[^"?\\ ]+\.(js|css)' "$RAW"/html/*.html | sort -u | while read -r p; do
  f=$(basename "$p"); case "$f" in *.css) d=css;; *) d=js;; esac
  [ -f "$RAW/$d/$f" ] || get "https://dmcg.co$p" "$RAW/$d/$f" 0.4
done
