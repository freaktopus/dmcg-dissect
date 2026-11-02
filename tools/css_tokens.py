#!/usr/bin/env python3
"""Summarise a CSS file: custom properties, colour frequencies, font
families/sizes, media queries, keyframes, transitions/easings.

Usage: python3 -I tools/css_tokens.py raw/css/file.css
"""
import re
import sys
from collections import Counter


def top(counter, n=40):
    return "\n".join(f"  {v:>4}  {k}" for k, v in counter.most_common(n))


def main():
    css = open(sys.argv[1], encoding="utf-8", errors="replace").read()
    print("bytes:", len(css))
    props = Counter(re.findall(r"(--[a-zA-Z0-9_-]+)\s*:", css))
    print("\n# custom properties defined (count):\n" + top(props, 80))
    root = re.findall(r"(?::root|html)[^{]*\{([^}]*)\}", css)
    print("\n# :root/html blocks:")
    for b in root[:6]:
        print("  ", b[:1500])
    hexes = Counter(h.lower() for h in re.findall(r"#[0-9a-fA-F]{3,8}\b", css))
    print("\n# hex colours:\n" + top(hexes, 50))
    funcs = Counter(re.findall(r"(?:rgba?|hsla?|oklch|color-mix)\([^)]*\)", css))
    print("\n# colour functions:\n" + top(funcs, 40))
    fams = Counter(re.findall(r"font-family:\s*([^;}]+)", css))
    print("\n# font-family:\n" + top(fams, 20))
    faces = re.findall(r"@font-face\s*\{([^}]*)\}", css)
    print("\n# @font-face (%d):" % len(faces))
    for f in faces[:20]:
        fam = re.search(r"font-family:([^;]+)", f)
        w = re.search(r"font-weight:([^;]+)", f)
        src = re.search(r"url\(([^)]+)\)", f)
        print("  ", fam and fam.group(1), w and w.group(1), src and src.group(1)[:90])
    sizes = Counter(re.findall(r"font-size:\s*([^;}]+)", css))
    print("\n# font-size:\n" + top(sizes, 40))
    lh = Counter(re.findall(r"line-height:\s*([^;}]+)", css))
    print("\n# line-height:\n" + top(lh, 15))
    ls = Counter(re.findall(r"letter-spacing:\s*([^;}]+)", css))
    print("\n# letter-spacing:\n" + top(ls, 15))
    fw = Counter(re.findall(r"font-weight:\s*([^;}]+)", css))
    print("\n# font-weight:\n" + top(fw, 10))
    mq = Counter(re.findall(r"@media\s*([^{]+)\{", css))
    print("\n# @media:\n" + top(mq, 40))
    sup = Counter(re.findall(r"@supports\s*([^{]+)\{", css))
    print("\n# @supports:\n" + top(sup, 15))
    kf = re.findall(r"@keyframes\s+([\w-]+)", css)
    print("\n# @keyframes (%d):" % len(kf), ", ".join(kf))
    ease = Counter(re.findall(r"cubic-bezier\([^)]*\)|linear\([^)]{0,60}", css))
    print("\n# easings:\n" + top(ease, 20))
    trans = Counter(re.findall(r"transition:\s*([^;}]+)", css))
    print("\n# transition:\n" + top(trans, 25))
    misc = {k: len(re.findall(k, css)) for k in [
        "backdrop-filter", "mix-blend-mode", "clamp\\(", "svh|dvh|lvh", "container-type",
        "@container", "view-transition", "scroll-snap", "position:\\s*sticky", "grid-template-columns",
        "aspect-ratio", "mask-image", "filter:\\s*blur", "@layer", "env\\(safe-area", ":has\\(", "text-wrap",
        "scroll-timeline|animation-timeline|view-timeline", "@property", "prefers-reduced-motion",
        "prefers-color-scheme", "cursor:", "focus-visible", "will-change"]}
    print("\n# feature counts:", misc)
    radius = Counter(re.findall(r"border-radius:\s*([^;}]+)", css))
    print("\n# border-radius:\n" + top(radius, 15))
    gtc = Counter(re.findall(r"grid-template-columns:\s*([^;}]+)", css))
    print("\n# grid-template-columns:\n" + top(gtc, 15))


if __name__ == "__main__":
    main()
