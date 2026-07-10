#!/usr/bin/env python3
"""Debug trace for 4 problematic words."""
import sys
sys.path.insert(0, "src/nvdajp-jtalk-dic")
from arpabet_to_kana import arpabet_to_kana, _morae_with_stress

tests = {
    "monument": ["M", "AA1", "N", "Y", "AH0", "M", "AH0", "N", "T"],
    "separation": ["S", "EH1", "P", "AH0", "R", "EY2", "SH", "AH0", "N"],
    "communicates": ["K", "AH0", "M", "Y", "UW1", "N", "AH0", "K", "EY2", "T", "S"],
    "herald": ["HH", "EH1", "R", "AH0", "L", "D"],
}

for word, ph in tests.items():
    kana = arpabet_to_kana(ph)
    morae = _morae_with_stress(ph)
    print(f"{word:20s} {kana}")
    print(f"{'':20s} morae: {[(m, s) for m, s in morae]}")
    print(f"{'':20s} phonemes: {ph}")
    print()