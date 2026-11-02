#!/usr/bin/env python3
"""Inventory a saved HTML file: meta/OG tags, JSON-LD, scripts, stylesheets,
preloads, images/videos, headings, links and alt-text coverage.

Usage: python3 -I tools/html_inventory.py raw/html/home.html [--json out.json]

Reads the file as data only (stdlib HTMLParser); nothing in it is executed.
"""
import json
import sys
from collections import Counter
from html.parser import HTMLParser


class Inv(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta, self.scripts, self.styles, self.links = [], [], [], []
        self.imgs, self.videos, self.headings, self.anchors = [], [], [], []
        self.jsonld, self.inline_script_sizes = [], []
        self.title = ""
        self._in = None
        self._buf = []
        self._script_type = None
        self.tags = Counter()
        self.classes = Counter()
        self.aria = Counter()
        self.html_attrs = {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags[tag] += 1
        for c in (a.get("class") or "").split():
            self.classes[c] += 1
        for k in a:
            if k.startswith("aria-") or k == "role":
                self.aria[k] += 1
        if tag == "html":
            self.html_attrs = a
        elif tag == "meta":
            self.meta.append(a)
        elif tag == "link":
            self.links.append(a)
        elif tag == "script":
            if a.get("src"):
                self.scripts.append(a)
            self._in, self._buf, self._script_type = "script", [], a.get("type")
        elif tag == "style":
            self._in, self._buf = "style", []
        elif tag == "title":
            self._in, self._buf = "title", []
        elif tag == "img":
            self.imgs.append(a)
        elif tag in ("video", "source") and (a.get("src") or a.get("data-src")):
            self.videos.append({"tag": tag, **a})
        elif tag == "video":
            self.videos.append({"tag": tag, **a})
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._in, self._buf, self._htag = "h", [], tag
        elif tag == "a":
            self.anchors.append(a)

    def handle_data(self, data):
        if self._in:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if self._in == "script" and tag == "script":
            body = "".join(self._buf)
            if self._script_type == "application/ld+json":
                self.jsonld.append(body)
            elif body.strip():
                self.inline_script_sizes.append(len(body))
            self._in = None
        elif self._in == "style" and tag == "style":
            self.styles.append(len("".join(self._buf)))
            self._in = None
        elif self._in == "title" and tag == "title":
            self.title = "".join(self._buf).strip()
            self._in = None
        elif self._in == "h" and tag == getattr(self, "_htag", None):
            self.headings.append((self._htag, " ".join("".join(self._buf).split())[:120]))
            self._in = None


def main():
    path = sys.argv[1]
    with open(path, encoding="utf-8", errors="replace") as fh:
        html = fh.read()
    p = Inv()
    p.feed(html)
    out = {
        "bytes": len(html.encode()),
        "html_attrs": p.html_attrs,
        "title": p.title,
        "meta": p.meta,
        "jsonld": p.jsonld,
        "links": p.links,
        "scripts": p.scripts,
        "inline_scripts": {"count": len(p.inline_script_sizes), "total_chars": sum(p.inline_script_sizes)},
        "inline_styles": p.styles,
        "imgs": {"count": len(p.imgs), "missing_alt": sum(1 for i in p.imgs if "alt" not in i),
                 "empty_alt": sum(1 for i in p.imgs if i.get("alt") == ""),
                 "lazy": sum(1 for i in p.imgs if i.get("loading") == "lazy"),
                 "sample": p.imgs[:8]},
        "videos": p.videos[:20],
        "video_count": sum(1 for v in p.videos if v["tag"] == "video"),
        "headings": p.headings,
        "anchors": sorted({a.get("href", "") for a in p.anchors}),
        "tag_counts": p.tags.most_common(25),
        "aria": dict(p.aria),
        "top_classes": p.classes.most_common(40),
    }
    if "--json" in sys.argv:
        with open(sys.argv[sys.argv.index("--json") + 1], "w") as fh:
            json.dump(out, fh, indent=1)
    else:
        print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
