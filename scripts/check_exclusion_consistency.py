#!/usr/bin/env python3
"""Check custom dic English entries not in EXCLUDED_WORDS and verify
they don't appear in eng-dic CSV (which would be duplicates).

Usage:
  python scripts/check_exclusion_consistency.py            # report
  python scripts/check_exclusion_consistency.py --update    # update eng_dic_maker.py
"""
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENG_MAKER = ROOT / "src" / "nvdajp-jtalk-dic" / "eng_dic_maker.py"
CUSTOM_MAKER = ROOT / "src" / "nvdajp-jtalk-dic" / "custom_dic_maker.py"
ENG_CSV = ROOT / "src" / "nvdajp-jtalk-dic" / "naist-jdic-source" / "nvdajp-eng-dic.csv"


def _load_excluded(text):
    m = re.search(r"EXCLUDED_WORDS = frozenset\(\((.*?)\)\)", text, re.DOTALL)
    return set(w.lower() for w in re.findall(r'"([a-zA-Z]+)"', m.group(1)))


def _load_custom_eng(text):
    return {mm.group(1).lower() for mm in re.finditer(r'\["([a-zA-Z]+)"', text)}


def _fullwidth(s):
    _H2Z = {}
    for c in "abcdefghijklmnopqrstuvwxyz":
        _H2Z[c] = chr(ord(c) - ord("a") + ord("ａ"))
    for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        _H2Z[c] = chr(ord(c) - ord("A") + ord("ａ"))
    return s.translate(str.maketrans(_H2Z))


def main():
    import sys

    update_mode = "--update" in sys.argv

    eng_text = ENG_MAKER.read_text(encoding="utf-8")
    excluded = _load_excluded(eng_text)
    custom_text = CUSTOM_MAKER.read_text(encoding="utf-8")
    custom_eng = _load_custom_eng(custom_text)
    missing = custom_eng - excluded

    eng_csv = ENG_CSV.read_text(encoding="utf-8")
    duplicates = []
    not_in_csv = []
    for w in sorted(missing):
        fw = _fullwidth(w)
        found = any(line.startswith(fw + ",") for line in eng_csv.splitlines())
        if found:
            duplicates.append(w)
        else:
            not_in_csv.append(w)

    print(f"Custom dic English entries not in EXCLUDED_WORDS: {len(missing)}")
    print(f"  DUPLICATES (in eng-dic CSV): {len(duplicates)}")
    print(f"  Not in eng-dic CSV (safe): {len(not_in_csv)}")

    if duplicates:
        print("\nDuplicates to add to EXCLUDED_WORDS:")
        for w in duplicates:
            print(f'    "{w}",')
    if not_in_csv:
        print("\nNot in eng-dic CSV (no action needed):")
        for w in not_in_csv:
            print(f"    {w}")

    if update_mode and duplicates:
        # Insert duplicates into EXCLUDED_WORDS, before the closing ))
        # Find the insertion point: just before the closing `))`
        m = re.search(r"EXCLUDED_WORDS = frozenset\(\((.*?)\)\)", eng_text, re.DOTALL)
        if m:
            block = m.group(1)
            # Find existing entries to avoid re-adding
            existing = set(re.findall(r'"([a-zA-Z]+)"', block))
            new_words = [w for w in duplicates if w not in existing]
            if new_words:
                # Add a comment and the new words before the closing ))
                # Find the last closing paren of frozenset
                insert_before = m.end() - 2  # position of `))`
                # Build the new entries text
                new_lines = "\n    # Pre-existing custom dic entries that were also in eng-dic\n"
                for w in new_words:
                    new_lines += f'    "{w}",\n'
                new_text = eng_text[:insert_before] + new_lines + eng_text[insert_before:]
                ENG_MAKER.write_text(new_text, encoding="utf-8")
                print(f"\nUpdated {ENG_MAKER.name} with {len(new_words)} new excluded words.")


if __name__ == "__main__":
    main()