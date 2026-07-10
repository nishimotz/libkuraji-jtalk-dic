#!/usr/bin/env python3
"""Search for arryo in eng-dic CSV."""
path = "src/nvdajp-jtalk-dic/naist-jdic-source/nvdajp-eng-dic.csv"
target = "\uff41\uff52\uff52\uff59\uff4f"  # ａｒｒｙｏ
with open(path, "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith(target):
            print(repr(line.strip()))