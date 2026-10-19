#!/usr/bin/env python
"""Image-integrity pre-screen for the manuscript figures (reviewer-panel step 5).

Mechanical screen only: perceptual hashing of every figure, all-pairs Hamming
distance, and a rotation/flip pass to catch duplication that has been disguised
by reorientation. It produces LEADS for a human or an image-integrity reviewer,
not verdicts.

This project's figures are all generated from declared source CSVs by scripts in
this repository, so the a-priori expectation is that no pair is similar beyond
the shared styling. The screen exists to test that expectation rather than
assume it: an accidental re-use of one figure's data in another would show up
here as an unexpectedly small Hamming distance.

Implemented with Pillow only (no imagehash dependency): dHash and pHash are
computed directly, so the screen cannot be skipped for want of a package.

Run: python scripts/image_integrity_screen.py
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
FIGS = ROOT / "outputs" / "figures"
OUT = ROOT / "outputs" / "review" / "image_integrity_prescreen.json"


def _bits_to_int(bits: list[int]) -> int:
    v = 0
    for b in bits:
        v = (v << 1) | (1 if b else 0)
    return v


def dhash(img: Image.Image, size: int = 8) -> int:
    g = img.convert("L").resize((size + 1, size), Image.LANCZOS)
    px = list(g.getdata())
    bits = []
    for r in range(size):
        for c in range(size):
            bits.append(px[r * (size + 1) + c] < px[r * (size + 1) + c + 1])
    return _bits_to_int(bits)


def phash(img: Image.Image, size: int = 8, factor: int = 4) -> int:
    g = img.convert("L").resize((size * factor, size * factor), Image.LANCZOS)
    px = list(g.getdata())
    n = size * factor
    # 2-D DCT-II, separable, on the small grid (32x32) -- cheap and dependency-free
    import math
    cos = [[math.cos(math.pi * (2 * x + 1) * u / (2 * n))
            for x in range(n)] for u in range(n)]
    rows = [[sum(px[y * n + x] * cos[u][x] for x in range(n))
             for u in range(n)] for y in range(n)]
    dct = [[sum(rows[y][v] * cos[u][y] for y in range(n))
            for v in range(n)] for u in range(n)]
    vals = [dct[u][v] for u in range(size) for v in range(size)]
    med = sorted(vals)[len(vals) // 2]
    return _bits_to_int([v > med for v in vals])


def hamming(a: int, b: int, bits: int = 64) -> int:
    return bin((a ^ b) & ((1 << bits) - 1)).count("1")


def main() -> int:
    files = sorted(FIGS.glob("figure*.png"))
    if not files:
        print("no figure PNGs found")
        return 1
    hashes = {}
    for f in files:
        with Image.open(f) as im:
            im.load()
            base = im.copy()
        variants = {"orig": base, "r90": base.rotate(90, expand=True),
                    "r180": base.rotate(180, expand=True),
                    "r270": base.rotate(270, expand=True),
                    "flip": base.transpose(Image.FLIP_LEFT_RIGHT)}
        hashes[f.stem] = {k: (dhash(v), phash(v)) for k, v in variants.items()}

    pairs = []
    names = sorted(hashes)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            best = None
            for ka, (da, pa) in hashes[a].items():
                for kb, (db, pb) in hashes[b].items():
                    dd, dp = hamming(da, db), hamming(pa, pb)
                    score = min(dd, dp)
                    if best is None or score < best[0]:
                        best = (score, ka, kb, dd, dp)
            pairs.append({"a": a, "b": b, "min_distance": best[0],
                          "variant_a": best[1], "variant_b": best[2],
                          "dhash_distance": best[3], "phash_distance": best[4]})
    pairs.sort(key=lambda p: p["min_distance"])
    flagged = [p for p in pairs if p["min_distance"] <= 10]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "figures_screened": names,
        "n_pairs": len(pairs),
        "threshold": 10,
        "note": ("dHash and pHash computed with Pillow only; each pair compared "
                 "across original, 90/180/270-degree rotations and a horizontal "
                 "flip, so reorientation cannot hide a duplicate. Results are "
                 "LEADS for human review, not verdicts."),
        "flagged_pairs": flagged,
        "closest_pairs": pairs[:6],
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"figures screened : {len(names)}")
    print(f"pairs compared   : {len(pairs)} (x5 orientations each)")
    print(f"flagged (<=10)   : {len(flagged)}")
    print("\nclosest pairs:")
    for p in pairs[:6]:
        print(f"  {p['min_distance']:>3}  {p['a']} <-> {p['b']}  "
              f"(dHash {p['dhash_distance']}, pHash {p['phash_distance']})")
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
