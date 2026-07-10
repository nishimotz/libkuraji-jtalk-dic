#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Flag suspicious katakana readings in nvdajp-eng-dic.csv.

Scans the full dictionary output and groups entries by the type of
pronunciation/orthography anomaly, so rule-based fixes can be prioritized
by impact.  Output is a TSV summary (one row per entry+rule hit) plus
per-pattern counts to stderr.
"""
from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENG_DIC = ROOT / "src" / "nvdajp-jtalk-dic" / "naist-jdic-source" / "nvdajp-eng-dic.csv"

# Halfwidth katakana map used in ASCII surface generation.
_H2Z = {chr(0x61 + i): chr(0xFF41 + i) for i in range(26)}
_H2Z.update({chr(0x41 + i): chr(0xFF21 + i) for i in range(26)})


def _to_fullwidth_ascii(s: str) -> str:
    return "".join(_H2Z.get(ch, ch) for ch in s)


def _is_fullwidth_ascii(s: str) -> bool:
    return bool(re.fullmatch(r"[\uff21-\uff3a\uff41-\uff5a]+", s))


def _is_katakana(s: str) -> bool:
    return bool(re.fullmatch(r"[\u30a1-\u30ff]+", s))


def load_entries(path: Path):
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


def load_sample_tsv(path: Path):
    """Load surface,reading,accent rows from a sample TSV."""
    entries = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if len(row) < 3 or row[0] == "surface":
                continue
            surface, reading, accent = row[0], row[1], row[2]
            if _is_fullwidth_ascii(surface) and _is_katakana(reading):
                entries.append((surface, reading, accent))
    return entries


def _mora_split(reading: str) -> list[str]:
    """Split katakana into morae (small kana attached to preceding)."""
    small = set("ャュョァィゥェォッー")
    morae = []
    for ch in reading:
        if ch in small and morae:
            morae[-1] += ch
        else:
            morae.append(ch)
    return morae


def _mora_count(reading: str) -> int:
    return len(_mora_split(reading))


def _accent_mora(accent: str) -> int:
    try:
        return int(accent.split("/")[1])
    except Exception:
        return 0


def flag_entries(entries: list[tuple[str, str, str]]):
    hits: list[tuple[str, str, str, str]] = []
    counts: Counter[str] = Counter()

    for surface, reading, accent in entries:
        morae = _mora_split(reading)
        rules_hit: set[str] = set()

        # A. Obvious glyph-level anomalies
        if "ーー" in reading:
            rules_hit.add("A1: consecutive chouon")
        if "ッッ" in reading:
            rules_hit.add("A2: consecutive sokuon")
        # same mora repeated three+ times (e.g. アアア or カカカ)
        if re.search(r"(.)\1{2,}", reading):
            rules_hit.add("A3: same kana tripled")

        # B. Consonant-level Japanese phonotactic anomalies
        # True geminate ン is not a normal Japanese mora sequence; it usually
        # comes from adjacent English /n/ + /n/ being over-segmented
        # (e.g. cannon -> カンネン instead of キャノン/カノン).
        if "ンン" in reading:
            rules_hit.add("B1: consecutive ンン")
        # True geminate ッ is normal for sokuon, but two in a row is not.
        if "ッッ" in reading:
            rules_hit.add("B2: consecutive ッッ")
        # Small vowel kana that is not part of a standard combo (ティ/ディ/ファ etc.)
        # and is not followed by small yoon: these are hard to pronounce in Japanese.
        if re.search(r"(^|ー)([ィゥェォ])", reading):
            rules_hit.add("B3: isolated small vowel at start or after chouon")

        # C. Vowel-level anomalies
        # Four or more consecutive vowel-only morae is rare in Japanese loanwords.
        if re.search(r"[アイウエオー]{4,}", reading):
            rules_hit.add("C1: four+ vowel morae in a row")
        # A standalone vowel mora immediately after ン at word end often means
        # an English syllabic nasal or final schwa was left bare.
        if re.search(r"ン[アイウエオー]$", reading):
            rules_hit.add("C2: ン + standalone vowel at end")

        # D. Stress/mora imbalance
        total = _mora_count(reading)
        if total >= 12:
            rules_hit.add("D1: 12+ morae")
        accent_mora = _accent_mora(accent)
        if accent_mora > 0 and total > accent_mora * 5:
            rules_hit.add("D2: mora count much larger than accent position")

        for rule in rules_hit:
            hits.append((rule, surface, reading, accent))
            counts[rule] += 1

    return hits, counts


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-i", "--input", type=Path, default=ENG_DIC, help="input CSV/TSV path (default: full eng-dic)")
    parser.add_argument("-o", "--output", type=Path, default=None, help="output TSV path (default: stdout)")
    parser.add_argument("--sample-tsv", action="store_true", help="input is a sample TSV with surface,reading,accent columns")
    args = parser.parse_args()

    if args.input == ENG_DIC and not ENG_DIC.exists():
        print(f"eng-dic not found: {ENG_DIC}", file=sys.stderr)
        return 1

    if args.sample_tsv:
        entries = load_sample_tsv(args.input)
    else:
        entries = load_entries(args.input)
    hits, counts = flag_entries(entries)

    print(f"Scanned {len(entries)} ASCII-surface eng-dic entries.", file=sys.stderr)
    print(f"Flagged {len(hits)} rule hits total.", file=sys.stderr)
    print("Counts by rule:", file=sys.stderr)
    for rule, count in counts.most_common():
        print(f"  {count:6d}  {rule}", file=sys.stderr)

    out = args.output.open("w", encoding="utf-8", newline="") if args.output else sys.stdout
    writer = csv.writer(out, delimiter="\t", lineterminator="\n")
    writer.writerow(["rule", "surface", "reading", "accent"])
    for rule, surface, reading, accent in hits:
        writer.writerow([rule, surface, reading, accent])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
