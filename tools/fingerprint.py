#!/usr/bin/env python3
"""Grep downloaded JS/CSS bundles for known library signatures and print
short context excerpts as evidence.

Usage: python3 -I tools/fingerprint.py raw/js [raw/css ...]
Files are read as text only; nothing is executed.
"""
import os
import re
import sys

SIGS = {
    "Next.js version": r'"(?:next|NEXT)[^"]{0,20}"\s*[,:]\s*"1[3-9]\.\d+\.\d+[^"]*"|window\.next\s*=\s*\{version:"[^"]+"|version:"1[4-9]\.\d+\.\d+[^"]*"',
    "React version": r'"1[89]\.\d+\.\d+(?:-[a-z0-9.-]+)?"',
    "GSAP": r"gsap|GreenSock|ScrollTrigger",
    "Lenis": r"lenis|Lenis",
    "Locomotive": r"locomotive",
    "Framer Motion / motion": r"framer-motion|motion\.dev|useMotionValue|AnimatePresence|animateMini|MotionConfig",
    "Three.js": r"THREE\.|WebGLRenderer|three\.module",
    "OGL / WebGL raw": r"getContext\(\"webgl2?\"|WEBGL_|gl_FragColor|precision (?:highp|mediump) float",
    "Canvas 2D": r"getContext\(\"2d\"\)",
    "Swiper/Embla/Keen": r"swiper|embla|keen-slider",
    "Barba/Swup": r"barba|swup",
    "View Transitions API": r"startViewTransition|view-transition",
    "Sanity": r"sanity|cdn\.sanity\.io|@sanity",
    "Vercel Analytics": r"va\.vercel-scripts|/_vercel/insights|vercel-analytics|@vercel/analytics",
    "Vercel Speed Insights": r"speed-insights|/_vercel/speed-insights",
    "Google Analytics/GTM": r"googletagmanager|gtag\(|google-analytics",
    "Plausible/Fathom/Posthog": r"plausible|usefathom|posthog",
    "Meta pixel / others": r"fbq\(|connect\.facebook|hotjar|clarity\.ms|segment\.com",
    "Mux/HLS": r"mux\.com|hls\.js|Hls\.|m3u8",
    "IntersectionObserver": r"IntersectionObserver",
    "requestAnimationFrame": r"requestAnimationFrame",
    "matchMedia reduced motion": r"prefers-reduced-motion",
    "Web Animations API": r"\.animate\(\[|\.animate\(\{",
    "Zustand/Jotai": r"zustand|jotai",
    "Spring physics": r"stiffness|damping",
}


def main():
    files = []
    for root in sys.argv[1:]:
        for dp, _, fns in os.walk(root):
            for fn in sorted(fns):
                if fn.endswith((".js", ".css")):
                    files.append(os.path.join(dp, fn))
    for name, pat in SIGS.items():
        rx = re.compile(pat)
        hits = []
        for f in files:
            with open(f, encoding="utf-8", errors="replace") as fh:
                txt = fh.read()
            ms = list(rx.finditer(txt))
            if ms:
                m = ms[0]
                ctx = txt[max(0, m.start() - 60): m.end() + 60].replace("\n", " ")
                hits.append((os.path.basename(f), len(ms), ctx))
        print(f"## {name}: {'NONE' if not hits else ''}")
        for fn, n, ctx in hits[:6]:
            print(f"  {fn} x{n}: ...{ctx}...")


if __name__ == "__main__":
    main()
