#!/usr/bin/env python3
"""Check feature raw output for a few words."""
import fugashi

tagger = fugashi.GenericTagger(
    "-d f:/nvda/gh/libkuraji-jtalk-dic/src/nvdajp-jtalk-dic/build/dic"
    " -r f:/nvda/gh/libkuraji-jtalk-dic/src/nvdajp-jtalk-dic/build/dic/dicrc"
)

for w in ["matsui", "radio", "diary", "hello"]:
    result = tagger(w)
    for word in result:
        print(f"{w}: surface={word.surface} feature={word.feature}")