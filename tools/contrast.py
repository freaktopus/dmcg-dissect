#!/usr/bin/env python3
"""WCAG 2.x contrast ratios for colour pairs.

Usage: python3 -I tools/contrast.py FG:BG [FG:BG ...]   (hex, alpha ignored)
"""
import sys


def lum(h):
    h = h.lstrip("#")
    if len(h) in (3, 4):
        h = "".join(c * 2 for c in h[:3])
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


for pair in sys.argv[1:]:
    fg, bg = pair.split(":")
    r = ratio(fg, bg)
    verdict = "AAA" if r >= 7 else "AA" if r >= 4.5 else "AA-large only" if r >= 3 else "FAIL"
    print(f"{fg} on {bg}: {r:.2f}:1  {verdict}")
