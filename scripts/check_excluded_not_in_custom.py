#!/usr/bin/env python3
"""Check which excluded words are actually in custom_dic_maker.py."""
import re
import pathlib

custom = pathlib.Path(
    "src/nvdajp-jtalk-dic/custom_dic_maker.py"
).read_text(encoding="utf-8")

eng = pathlib.Path(
    "src/nvdajp-jtalk-dic/eng_dic_maker.py"
).read_text(encoding="utf-8")
m = re.search(r"EXCLUDED_WORDS = frozenset\(\((.*?)\)\)", eng, re.DOTALL)
excluded = set(w.lower() for w in re.findall(r'"([a-zA-Z]+)"', m.group(1)))

custom_eng = set()
for mm in re.finditer(r'\["([a-zA-Z]+)"', custom):
    custom_eng.add(mm.group(1).lower())

# Words that are excluded from eng-dic but NOT in custom dic
excluded_not_in_custom = sorted(excluded - custom_eng)
print(f"Excluded from eng-dic but NOT in custom dic ({len(excluded_not_in_custom)}):")
for w in excluded_not_in_custom:
    print(f"  {w}")

# These words will be unknown to MeCab (no reading)
# They should either be added to custom dic or removed from EXCLUDED_WORDS