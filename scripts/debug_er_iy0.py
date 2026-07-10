#!/usr/bin/env python3
"""Debug trace for ER+IY0 contraction."""
import sys
sys.path.insert(0, "src/nvdajp-jtalk-dic")
from arpabet_to_kana import _morae_with_stress, arpabet_to_kana

tests = {
    "gallery": ["G", "AE1", "L", "ER0", "IY0"],
    "galleries": ["G", "AE1", "L", "ER0", "IY0", "Z"],
    "galleria": ["G", "AE1", "L", "ER0", "IY1", "AH0"],
}

for word, ph in tests.items():
    morae = _morae_with_stress(ph)
    result_str = "|".join(m for m, _ in morae)
    print(f"{word:20s} morae: {result_str}")
    print(f"{'':20s} kana:  {arpabet_to_kana(ph)}")
    print(f"{'':20s} stress: {[s for _, s in morae]}")
    print()