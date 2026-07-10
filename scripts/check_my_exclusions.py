#!/usr/bin/env python3
"""Check that the custom dic entries added in this session are all
in EXCLUDED_WORDS in eng_dic_maker.py."""
import re
import pathlib

eng = pathlib.Path("src/nvdajp-jtalk-dic/eng_dic_maker.py").read_text(
    encoding="utf-8"
)
m = re.search(r"EXCLUDED_WORDS = frozenset\(\((.*?)\)\)", eng, re.DOTALL)
excluded = set(
    w.lower() for w in re.findall(r'"([a-zA-Z]+)"', m.group(1))
)

# Entries added in this session
my_entries = [
    "variety", "varieties", "various", "parietal", "pizzeria", "maria",
    "firearm", "firearms", "hierarchy", "burrowing", "arroyo",
    "radioactive", "radioactivity",
    "electromagnetism", "extraterrestrial", "extraterrestrials",
    "indistinguishable", "institutionalized", "triangulation",
    "unsubstantiated",
]

print("My custom dic entries added this session:")
all_ok = True
for w in my_entries:
    in_excluded = w.lower() in excluded
    status = "OK" if in_excluded else "MISSING!"
    if not in_excluded:
        all_ok = False
    print(f"  {w:25s} excluded={in_excluded}  {status}")

print(f"\n{'All OK!' if all_ok else 'SOME MISSING!'}")