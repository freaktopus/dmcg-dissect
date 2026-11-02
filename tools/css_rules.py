#!/usr/bin/env python3
"""Print CSS rules (including @media/@keyframes blocks) whose text contains a
keyword. Brace-matching, no external deps.

Usage: python3 -I tools/css_rules.py raw/css/file.css KEYWORD [MAXCHARS]
"""
import sys


def blocks(css):
    """Yield top-level blocks as strings."""
    depth, start = 0, 0
    for i, ch in enumerate(css):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                yield css[start:i + 1].strip()
                start = i + 1


def main():
    css = open(sys.argv[1], encoding="utf-8", errors="replace").read()
    kw = sys.argv[2]
    cap = int(sys.argv[3]) if len(sys.argv) > 3 else 400
    for b in blocks(css):
        if kw in b:
            if b.startswith("@media") or b.startswith("@supports"):
                # print only the inner rules that match
                inner = b[b.index("{") + 1:-1]
                head = b[:b.index("{")]
                for r in blocks(inner):
                    if kw in r:
                        print(f"[{head.strip()}] {r[:cap]}")
            else:
                print(b[:cap])


if __name__ == "__main__":
    main()
