# eng_dic_maker.py
# Copyright (C) 2010-2026 Takuya Nishimoto
# License: BSD 3-Clause. See LICENSE.
#
# Build nvdajp-eng-dic.csv (English word readings for JTalk speech and
# libkuraji braille) from eng-dic-source/cmudict-subset.dict, using
# arpabet_to_kana.py. See eng-dic-source/README.md for provenance and why
# this replaces nvdajp's bep-eng.dic-derived dictionary (GPL, incompatible
# with this repository's BSD 3-Clause license).
#
# Entries here are bulk-generated and approximate (see arpabet_to_kana.py's
# module docstring); a higher cost than custom_dic_maker.py's default
# (1000) is used so that hand-curated overrides in custom_dic_maker.py -
# added for words where this generator's output is clearly wrong, or
# whose established katakana spelling doesn't derive from pronunciation
# rules at all - win the cost comparison when both dictionaries define the
# same surface form.

import sys
from pathlib import Path

from arpabet_to_kana import arpabet_to_accent, arpabet_to_kana, kana_speech_safe
from custom_dic_maker import _to_mecab_surface

OUT_FILE = "nvdajp-eng-dic.csv"
SOURCE_FILE = "cmudict-subset.dict"
COST = 3000
POS = "名詞,一般,*,*,*,*"

# Words excluded from the CMUdict-derived bulk dictionary.
# These fall into two groups:
# 1. Words with established katakana spellings that the ARPAbet-to-kana
#    rules generate incorrectly.  Provided as hand-curated overrides in
#    custom_dic_maker.py instead.
# 2. Japanese-origin proper names and short acronyms/initialisms whose
#    conventional reading is simply the romaji reading (e.g. "matsui" ->
#    マツイ, "ceo" -> C.E.O. = シーイーオー).  The ARPAbet pronunciation
#    produces unnatural vowel-heavy katakana for these, so excluding them
#    lets MeCab's unknown-word handler produce the romaji reading instead.
EXCLUDED_WORDS = frozenset((
    # Established katakana overrides (custom_dic_maker.py)
    "amazon",
    "com",
    "director",
    "directors",
    # Japanese-origin proper names: romaji reading is correct
    "matsui",
    "tetsuo",
    "tsui",
    "oishi",
    "aoki",
    "aoi",
    "aida",
    # Acronyms/initialisms: spell out each letter
    "ceo",
    "cia",
    "aol",
    "iou",
    "sos",
    "baa",
    # Short proper names better read as romaji
    "iona",
    "iota",
    "iain",
    "yeo",
    # Foreign-origin proper names where romaji reading is closer
    "galleria",
    "fabrizio",
    "koreatown",
    "darius",
    "mariah",
    "zachariah",
    "ios",
    "pariah",
    "gonorrhea",
    "diarrhea",
    "diarrhoea",
    "aorta",
    "aortic",
    "arroyo",
    "psoriasis",
    "oasis",
    "notoriety",
    "radio",
    "radioactive",
    "radioactivity",
    # Custom dic overrides for complex ER/vowel patterns
    "variety",
    "varieties",
    "various",
    "parietal",
    "pizzeria",
    "maria",
    "firearm",
    "firearms",
    "hierarchy",
    "burrowing",
    "arroyo",
    "electromagnetism",
    "extraterrestrial",
    "extraterrestrials",
    "indistinguishable",
    "institutionalized",
    "triangulation",
    "unsubstantiated",
))


def _load_source(source_path: Path):
    entries = []
    for line in source_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        word, phonemes = parts[0], parts[1:]
        entries.append((word, phonemes))
    return entries


def make_dic(CODE, THISDIR):
    THISDIR = Path(THISDIR)
    source_path = THISDIR.parent / "eng-dic-source" / SOURCE_FILE
    entries = _load_source(source_path)
    with open(THISDIR / OUT_FILE, "w", encoding=CODE) as file:
        for word, phonemes in entries:
            if word.lower() in EXCLUDED_WORDS:
                continue
            k1 = _to_mecab_surface(word)
            braille = arpabet_to_kana(phonemes)
            speech = kana_speech_safe(braille)
            accent = arpabet_to_accent(phonemes)
            # 表層形,左文脈ID,右文脈ID,コスト,品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用形,活用型,原形,読み,発音,アクセント,C0,braille
            s = "%s,0,0,%d,%s,%s,%s,%s,%s,C0,%s\n" % (
                k1, COST, POS, k1, speech, speech, accent, braille,
            )
            file.write(s)


if __name__ == "__main__":
    make_dic("utf-8", Path(__file__).resolve().parent)
    print(f"wrote {OUT_FILE}", file=sys.stderr)
