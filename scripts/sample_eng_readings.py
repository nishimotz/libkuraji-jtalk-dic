#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sample eng-dic entries whose katakana reading does NOT appear in NAIST-JDIC.

This surfaces English words whose reading cannot be validated against the native
Japanese dictionary, making them good candidates for human pronunciation review.

Usage:
    python scripts/sample_eng_readings.py -o review/sample_200.tsv
"""
from __future__ import annotations

import argparse
import csv
import random
import re
import sys
from pathlib import Path

NAIST_JDIC = Path(__file__).parent.parent / "src" / "nvdajp-jtalk-dic" / "naist-jdic-source" / "naist-jdic.csv"
ENG_DIC = Path(__file__).parent.parent / "src" / "nvdajp-jtalk-dic" / "naist-jdic-source" / "nvdajp-eng-dic.csv"


def _is_fullwidth_ascii(s: str) -> bool:
    return bool(re.fullmatch(r"[\uff21-\uff3a\uff41-\uff5a]+", s))


def _is_katakana(s: str) -> bool:
    return bool(re.fullmatch(r"[\u30a1-\u30ff]+", s))


def load_eng_dic_entries(path: Path):
    """Return list of (surface_ascii, reading, accent) for ASCII-surface entries."""
    entries = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            cols = line.strip().split(",")
            if len(cols) < 15:
                continue
            surface = cols[0]
            reading = cols[12]
            accent = cols[13] if len(cols) > 13 else ""
            if _is_fullwidth_ascii(surface) and _is_katakana(reading):
                entries.append((surface, reading, accent))
    return entries


def load_naist_katakana_forms(path: Path):
    """Return set of katakana forms used as surface or reading in NAIST-JDIC."""
    forms = set()
    with path.open("r", encoding="euc-jp") as f:
        for line in f:
            cols = line.strip().split(",")
            if len(cols) < 15:
                continue
            surface = cols[0]
            reading = cols[12] if len(cols) > 12 else ""
            for form in (surface, reading):
                if _is_katakana(form):
                    forms.add(form)
    return forms


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sample eng-dic entries whose reading is absent from NAIST-JDIC"
    )
    parser.add_argument("-n", "--count", type=int, default=200, help="number of samples (default: 200)")
    parser.add_argument("-s", "--seed", type=int, default=42, help="random seed (default: 42)")
    parser.add_argument("-o", "--output", type=Path, default=None, help="output TSV path (default: stdout)")
    args = parser.parse_args()

    if not ENG_DIC.exists():
        print(f"eng-dic not found: {ENG_DIC}", file=sys.stderr)
        return 1
    if not NAIST_JDIC.exists():
        print(f"naist-jdic not found: {NAIST_JDIC}", file=sys.stderr)
        return 1

    eng_entries = load_eng_dic_entries(ENG_DIC)
    naist_forms = load_naist_katakana_forms(NAIST_JDIC)

    # Entries whose reading is NOT found as surface or reading in NAIST-JDIC
    unmatched = [(s, r, a) for s, r, a in eng_entries if r not in naist_forms]

    random.seed(args.seed)
    sample = random.sample(unmatched, min(args.count, len(unmatched)))

    out = args.output.open("w", encoding="utf-8", newline="") if args.output else sys.stdout
    writer = csv.writer(out, delimiter="\t", lineterminator="\n")
    writer.writerow(["eng_surface", "eng_reading", "eng_accent", "judgment", "notes"])
    for surface, reading, accent in sample:
        writer.writerow([surface, reading, accent, "", ""])

    if args.output:
        out.close()
        print(f"wrote {len(sample)} rows to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
