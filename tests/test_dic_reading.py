"""Regression tests for dictionary readings.

These tests exercise the built dictionary directly through MeCab and verify that
the returned katakana reading matches the expected value. They are intentionally
NOT end-to-end tests for NVDA/JTalk/libkuraji final output; their only purpose is
to catch regressions in the dictionary source (nvdajp-eng-dic.csv, etc.).

Run after `make_jdic.py` has produced build/dic/:
    python tests/test_dic_reading.py

On CI the script exits with a non-zero status if any expectation is not met.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).parent
ROOT_DIR = TESTS_DIR.parent
DIC_DIR = ROOT_DIR / "src" / "nvdajp-jtalk-dic" / "build" / "dic"


def _load_harness():
    path = TESTS_DIR / "jtalk_reading_harness.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _make_analyzer(dic_dir: Path):
    try:
        import fugashi  # type: ignore[import]
    except ImportError as exc:
        raise RuntimeError(
            "fugashi is required to run dictionary reading tests. "
            "Install with: pip install fugashi"
        ) from exc

    if not dic_dir.exists():
        raise RuntimeError(
            f"Dictionary directory not found: {dic_dir}. "
            "Build the dictionary first with: python src/nvdajp-jtalk-dic/make_jdic.py"
        )

    # fugashi wraps arguments with shlex.split and mangles backslashes on Windows,
    # so always pass forward-slash paths.
    arg = f"-r {dic_dir.as_posix()}/dicrc -d {dic_dir.as_posix()}"
    return fugashi.GenericTagger(arg)


def _reading_from_feature(feature_raw: str) -> str:
    fields = feature_raw.split(",")
    # JTalk/MeCab CSV feature layout (surface prefix omitted by fugashi):
    #   0: pos1, 1: pos2, 2: pos3, 3: pos4, 4: pos5, 5: conj1, 6: conj2,
    #   6: base_form, 7: reading, 8: pronunciation, 9: accent, 10: C0/C1, 11: braille, ...
    # Prefer pronunciation (index 8) when present, fall back to reading (index 7).
    if len(fields) > 8:
        return fields[8]
    if len(fields) > 7:
        return fields[7]
    return ""


def main() -> int:
    harness = _load_harness()
    analyzer = _make_analyzer(DIC_DIR)

    failures = []
    for entry in harness:
        if not isinstance(entry, dict) or "surface" not in entry:
            continue
        surface = entry["surface"]
        expected = entry["reading"]

        # The JTalk dictionary's unknown-word classes are defined for fullwidth
        # ASCII, so we normalize the input the same way libkuraji does.
        from libkuraji.jtalk_dic import _to_mecab_text
        result = analyzer(_to_mecab_text(surface))
        if not result:
            failures.append((surface, expected, "(no parse result)"))
            continue

        actual = "".join(_reading_from_feature(node.feature_raw) for node in result)
        if actual != expected:
            failures.append((surface, expected, actual))

    if failures:
        print("Dictionary reading regressions detected:", file=sys.stderr)
        for surface, expected, actual in failures:
            print(
                f"  {surface}: expected {expected!r}, got {actual!r}",
                file=sys.stderr,
            )
        return 1

    print(f"All {len([e for e in harness if isinstance(e, dict) and 'surface' in e])} dictionary reading checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
