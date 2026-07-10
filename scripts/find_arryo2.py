#!/usr/bin/env python3
"""Search for arryo/arryo in CMUdict and eng-dic."""
import pathlib

# Search in CMUdict
p = pathlib.Path("src/nvdajp-jtalk-dic/eng-dic-source/cmudict-subset.dict")
for line in p.read_text(encoding="utf-8").splitlines():
    word = line.split()[0] if line.split() else ""
    if word.lower().startswith("arr") and len(word) <= 6:
        print(f"CMUdict: {repr(word)} (len={len(word)})")

print()

# Search in eng-dic CSV
p2 = pathlib.Path("src/nvdajp-jtalk-dic/naist-jdic-source/nvdajp-eng-dic.csv")
target = "\uff41\uff52\uff52\uff4f\uff59\uff4f"  # ａｒｒｏｙｏ = arryo
target2 = "\uff41\uff52\uff52\uff59\uff4f"  # ａｒｒｙｏ = arryo
print(f"Looking for {repr(target)} ({len(target)} chars)")
print(f"Also looking for {repr(target2)} ({len(target2)} chars)")
for line in p2.read_text(encoding="utf-8").splitlines():
    if line.startswith(target) or line.startswith(target2):
        print(f"eng-dic: {repr(line[:20])}")