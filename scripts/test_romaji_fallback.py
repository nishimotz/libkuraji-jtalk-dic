#!/usr/bin/env python3
"""Check how words are read with the current eng-dic included MeCab dictionary."""
import fugashi

tagger = fugashi.GenericTagger(
    "-d f:/nvda/gh/libkuraji-jtalk-dic/src/nvdajp-jtalk-dic/build/dic"
    " -r f:/nvda/gh/libkuraji-jtalk-dic/src/nvdajp-jtalk-dic/build/dic/dicrc"
)

test_words = [
    # Japanese names that should be romaji-read
    "matsui", "tetsuo", "tsui", "oishi", "aoki",
    # Common words where romaji reading is established
    "radio", "oasis", "iona", "iota", "iain", "yeo", "sos", "baa",
    # ER0+IY0 pattern words
    "diary", "hurry", "gallery", "luxury", "prior", "variety",
    # Other C1 words
    "notoriety", "pizzeria", "scouring", "worrying", "lowering",
    "firearm", "browning", "pariah", "mariah", "darius",
    "fabrizio", "koreatown", "zachariah",
    "ceo", "cia", "aol", "iou",
    "aida", "aorta", "aortic", "aoi",
]

for w in test_words:
    result = tagger(w)
    parts = []
    for word in result:
        fs = word.feature
        reading = fs[7] if len(fs) > 7 else "?"
        pos = fs[0] if fs else "?"
        parts.append(f"{word.surface}({reading}/{pos})")
    print(f"{w:12s} {' '.join(parts)}")