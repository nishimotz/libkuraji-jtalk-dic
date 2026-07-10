# arpabet_to_kana.py
# Copyright (C) 2010-2026 Takuya Nishimoto
# License: BSD 3-Clause. See LICENSE.
#
# Rule-based conversion from CMUdict's ARPAbet phoneme transcriptions to
# katakana, following common English-loanword adaptation conventions.
# Used by eng_dic_maker.py to generate nvdajp-eng-dic.csv from
# eng-dic-source/cmudict-subset.dict, replacing the GPL-licensed
# bep-eng.dic that nvdajp itself uses (see eng-dic-source/README.md).
#
# This is a coarse approximation, not a full English-to-Japanese
# transliteration engine: it gets common IT vocabulary (e.g. "alt",
# "windows", "point") right, but historically-lexicalized loanwords
# whose conventional katakana does not track modern General American
# pronunciation (e.g. "character" -> traditionally "kyarakutaa", not
# derived from the CMUdict pronunciation) will differ from the
# established spelling. Such cases are handled as individual overrides
# in custom_dic_maker.py, not by further generalizing this module.

VOWELS = {
    "AA": "ア", "AE": "ア", "AH": "ア", "AO": "オ",
    "EH": "エ", "IH": "イ", "IY": "イー", "UH": "ウ", "UW": "ウー",
    "ER": "アー",
    # diphthongs
    "AW": "アウ", "AY": "アイ", "EY": "エイ", "OW": "オウ", "OY": "オイ",
}

# Diphthong -> (vowel-key for combining with a preceding consonant, trailing mora).
# e.g. "shout" (SH AW1 T) -> consonant SH + "a" -> "シャ", then trailing "ウ" -> "シャウト".
DIPHTHONG_PARTS = {
    "AW": ("a", "ウ"), "AY": ("a", "イ"), "EY": ("e", "イ"),
    "OW": ("o", "ウ"), "OY": ("o", "イ"),
}

# consonant -> {a,i,u,e,o: combined kana, coda: kana when no following vowel}
CONSONANTS = {
    "P": {"a": "パ", "i": "ピ", "u": "プ", "e": "ペ", "o": "ポ", "coda": "プ"},
    "B": {"a": "バ", "i": "ビ", "u": "ブ", "e": "ベ", "o": "ボ", "coda": "ブ"},
    "T": {"a": "タ", "i": "ティ", "u": "トゥ", "e": "テ", "o": "ト", "coda": "ト"},
    "D": {"a": "ダ", "i": "ディ", "u": "ドゥ", "e": "デ", "o": "ド", "coda": "ド"},
    "K": {"a": "カ", "i": "キ", "u": "ク", "e": "ケ", "o": "コ", "coda": "ク"},
    "G": {"a": "ガ", "i": "ギ", "u": "グ", "e": "ゲ", "o": "ゴ", "coda": "グ"},
    "CH": {"a": "チャ", "i": "チ", "u": "チュ", "e": "チェ", "o": "チョ", "coda": "チ"},
    "JH": {"a": "ジャ", "i": "ジ", "u": "ジュ", "e": "ジェ", "o": "ジョ", "coda": "ジ"},
    "F": {"a": "ファ", "i": "フィ", "u": "フ", "e": "フェ", "o": "フォ", "coda": "フ"},
    "V": {"a": "ヴァ", "i": "ヴィ", "u": "ヴ", "e": "ヴェ", "o": "ヴォ", "coda": "ヴ"},
    "TH": {"a": "サ", "i": "シ", "u": "ス", "e": "セ", "o": "ソ", "coda": "ス"},
    "DH": {"a": "ザ", "i": "ジ", "u": "ズ", "e": "ゼ", "o": "ゾ", "coda": "ズ"},
    "S": {"a": "サ", "i": "シ", "u": "ス", "e": "セ", "o": "ソ", "coda": "ス"},
    "Z": {"a": "ザ", "i": "ジ", "u": "ズ", "e": "ゼ", "o": "ゾ", "coda": "ズ"},
    "SH": {"a": "シャ", "i": "シ", "u": "シュ", "e": "シェ", "o": "ショ", "coda": "シュ"},
    "ZH": {"a": "ジャ", "i": "ジ", "u": "ジュ", "e": "ジェ", "o": "ジョ", "coda": "ジュ"},
    "HH": {"a": "ハ", "i": "ヒ", "u": "フ", "e": "ヘ", "o": "ホ", "coda": "フ"},
    "M": {"a": "マ", "i": "ミ", "u": "ム", "e": "メ", "o": "モ", "coda": "ム"},
    "N": {"a": "ナ", "i": "ニ", "u": "ヌ", "e": "ネ", "o": "ノ", "coda": "ン"},
    "NG": {"a": "ンガ", "i": "ンギ", "u": "ング", "e": "ンゲ", "o": "ンゴ", "coda": "ング"},
    "L": {"a": "ラ", "i": "リ", "u": "ル", "e": "レ", "o": "ロ", "coda": "ル"},
    "R": {"a": "ラ", "i": "リ", "u": "ル", "e": "レ", "o": "ロ", "coda": ""},  # coda R: see below
    "W": {"a": "ワ", "i": "ウィ", "u": "ウ", "e": "ウェ", "o": "ウォ", "coda": "ウ"},
    "Y": {"a": "ヤ", "i": "イ", "u": "ユー", "e": "イェ", "o": "ヨ", "coda": "イ"},
}

_VOWEL_KEYS = {"AA": "a", "AE": "a", "AH": "a", "AO": "o", "EH": "e", "IH": "i", "IY": "i", "UH": "u", "UW": "u"}


def _strip_stress(phoneme):
    if phoneme and phoneme[-1].isdigit():
        return phoneme[:-1], phoneme[-1]
    return phoneme, None


_SMALL_KANA = set("ゃゅょぁぃぅぇぉャュョァィゥェォ")


def _split_morae(s):
    """Split a kana string into mora units, attaching small kana to the
    preceding character (standard Japanese mora-counting convention)."""
    morae = []
    for ch in s:
        if ch in _SMALL_KANA and morae:
            morae[-1] += ch
        else:
            morae.append(ch)
    return morae


def _morae_with_stress(phonemes):
    """Return a list of (mora_str, stress_or_None) pairs.

    stress is the ARPAbet stress digit ('0'/'1'/'2') of the vowel that
    produced the mora, assigned to the first mora of a multi-mora
    segment (long vowel, diphthong, or nasal-initial combo like NG).
    """
    stressed = [_strip_stress(p) for p in phonemes]
    bases = [b for b, _ in stressed]
    stresses = [s for _, s in stressed]
    result = []
    i = 0
    n = len(bases)
    while i < n:
        ph = bases[i]
        if ph == "ER" and result and result[-1][0][-1] in "アイウエオー":
            # rhotic schwa directly after a vowel-ending mora (no
            # intervening consonant) is a lengthening, not a new
            # "ア" mora (e.g. "power" P-AW-ER: after the "ウ" from AW,
            # ER just lengthens to "パウー" instead of "パウアー").
            result.append(("ー", stresses[i]))
            i += 1
            continue
        if ph in VOWELS:
            kana = VOWELS[ph]
            morae = _split_morae(kana)
            for j, m in enumerate(morae):
                result.append((m, stresses[i] if j == 0 else None))
            i += 1
            continue
        if ph in CONSONANTS:
            nxt = bases[i + 1] if i + 1 < n else None
            # consonant + ER ("er/ar" rhotic vowel): combine as
            # consonant+a, then lengthen (e.g. "current" K-ER -> "カー",
            # not "ク" + bare "アー").
            if nxt == "ER" and ph != "R":
                result.append((CONSONANTS[ph]["a"], stresses[i + 1]))
                result.append(("ー", None))
                i += 2
                continue
            # T/D immediately followed by S/Z (adjacent, no vowel between)
            # is the English "-ts"/"-dz" affricate ending (lights, results,
            # insights, words...): a single "ツ"/"ズ" mora, not two separate
            # codas (avoids "insights" -> インサイトス instead of インサイツ).
            if ph == "T" and nxt == "S":
                result.append(("ツ", None))
                i += 2
                continue
            if ph == "D" and nxt == "Z":
                result.append(("ズ", None))
                i += 2
                continue
            # Velar nasal NG immediately followed by K is realized as "ンク"
            # (not "ング" + "ク") when K begins a new syllable marker, e.g.
            # "functions" -> ファンクションズ.  When K is followed by a vowel
            # (ING endings), it forms the syllable onset instead: "thinking"
            # /ˈθɪŋkɪŋ/ -> シンキング, "banking" /ˈbæŋkɪŋ/ -> バンキング.
            if ph == "NG" and nxt == "K":
                if i + 2 < n and bases[i + 2] in _VOWEL_KEYS:
                    result.append(("ン", None))
                    vowel = bases[i + 2]
                    kana = CONSONANTS["K"][_VOWEL_KEYS[vowel]]
                    morae = _split_morae(kana)
                    for j, m in enumerate(morae):
                        result.append((m, stresses[i + 2] if j == len(morae) - 1 else None))
                    # K + IY/UW are long vowels; lengthen the combined mora.
                    if vowel in ("IY", "UW"):
                        result.append(("ー", None))
                    i += 3
                    continue
                result.append(("ンク", None))
                i += 2
                continue
            # consonant + IY/UW: these are inherently long vowels (unlike
            # IH/UH, which share the same combining key "i"/"u"), so the
            # combined mora must also lengthen (e.g. "reader" R-IY-D-ER ->
            # "リーダー", not "リダー").
            if nxt in ("IY", "UW"):
                result.append((CONSONANTS[ph][_VOWEL_KEYS[nxt]], stresses[i + 1]))
                result.append(("ー", None))
                i += 2
                continue
            if (
                ph == "R"
                and result
                and nxt not in _VOWEL_KEYS
                and nxt not in DIPHTHONG_PARTS
            ):
                # true coda /r/ (nothing vowel-like follows): lengthen.
                result.append(("ー", None))
                i += 1
                continue
            if nxt in DIPHTHONG_PARTS:
                vowel_key, trailing = DIPHTHONG_PARTS[nxt]
                combo = _split_morae(CONSONANTS[ph][vowel_key])
                for j, m in enumerate(combo):
                    result.append((m, None))
                result.append((trailing, stresses[i + 1]))
                i += 2
                continue
            # consonant + unstressed AH + L (schwa + dark L) maps to the
            # consonant's e-row kana + "ル" for a few frequent sonorants,
            # matching established loanword spellings:
            #   cancel /ˈkænsəl/ -> キャンセル
            #   camel  /ˈkæməl/  -> キャメル
            #   channel /ˈtʃænəl/ -> チャンネル
            # This must run before the generic syllabic-sonorant rule below.
            if (
                nxt == "AH"
                and i + 1 < n
                and stresses[i + 1] == "0"
                and i + 2 < n
                and bases[i + 2] == "L"
                and ph in ("S", "M", "N")
                and (i + 3 == n or bases[i + 3] not in _VOWEL_KEYS)
            ):
                e_row = {"S": "セ", "M": "メ", "N": "ネ"}[ph]
                result.append((e_row, None))
                result.append(("ル", None))
                i += 3
                continue
            # unstressed schwa immediately before a word-final (or
            # pre-consonant) sonorant is realized in English as a
            # syllabic consonant (e.g. "open" /oʊpn̩/): drop the schwa
            # mora and let the consonant surface on its own, instead of
            # combining consonant+schwa into a spurious extra mora
            # (avoids "open" -> オウパン, produces オウプン instead).
            #
            # Exception: when the current consonant and the following
            # sonorant are the same (N+AH+N, M+AH+M), dropping the schwa
            # produces consecutive ンン which is unnatural in Japanese
            # (e.g. "cannon" -> カンン instead of カナン).  In that case
            # let the normal consonant+vowel combination apply.
            if (
                nxt == "AH"
                and i + 1 < n
                and stresses[i + 1] == "0"
                and i + 2 < n
                and bases[i + 2] in ("N", "M", "L")
                and (i + 3 == n or bases[i + 3] not in _VOWEL_KEYS)
                and not (ph in ("N", "M") and bases[i + 2] == ph)
            ):
                result.append((CONSONANTS[ph]["coda"], None))
                i += 2  # skip this consonant and the schwa; sonorant handled next loop
                continue
            if nxt in _VOWEL_KEYS:
                kana = CONSONANTS[ph][_VOWEL_KEYS[nxt]]
                morae = _split_morae(kana)
                # the vowel's stress belongs to the last mora of the combo
                # (e.g. NG "ン" + "ガ": stress belongs to "ガ")
                for j, m in enumerate(morae):
                    result.append((m, stresses[i + 1] if j == len(morae) - 1 else None))
                i += 2
                continue
            # a short vowel (not the long IY/UW, ER, or a diphthong -
            # those are handled above and don't geminate the same way)
            # directly followed by a word-final/pre-consonant voiceless
            # stop is realized with a geminate (small tsu): "input" IH-N-
            # P-UH-T -> ...プ + ッ + ト ("インプット"), not "...プト".
            if ph in ("P", "T", "K", "CH") and i > 0 and bases[i - 1] in _VOWEL_KEYS:
                result.append(("ッ", None))
            result.append((CONSONANTS[ph]["coda"], None))
            i += 1
            continue
        result.append(("？", None))
        i += 1
    return result


def arpabet_to_kana(phonemes):
    """Convert a list of ARPAbet phonemes (e.g. ['P', 'AW1', 'ER0']) to katakana.

    First-pass approximation only: does not model gemination (soku-on)
    for consonant clusters, nor does it distinguish rhotic vs
    non-rhotic vowel-R sequences beyond the simple "coda R lengthens
    the previous vowel" rule.
    """
    raw = "".join(m for m, _ in _morae_with_stress(phonemes))
    # Collapse consecutive long-vowel morae into one.  The ARPAbet rules
    # can produce sequences like "フェーー" for "fairer" (EH + coda R + ER)
    # because both the coda R and the following rhotic schwa add a "ー".
    # Japanese loanwords never write two long-vowel marks in a row.
    while "ーー" in raw:
        raw = raw.replace("ーー", "ー")
    return raw


# nvdajp's existing custom dic entries (e.g. custom_dic_maker.py's
# "vaiorin"/"vitamin" entries) keep "ヴ"-series kana in the braille
# transcription but substitute the "バ"-series (voiced bilabial stop)
# for speech: Open JTalk's phoneme table does define a genuine /v/
# for "ヴ" (see jpcommon_rule_utf_8.h), but the shipped HTS voice
# models were trained on native Japanese phoneme inventories and
# render /v/ poorly, so nvdajp has historically avoided it in speech.
_V_TO_B = {"ヴァ": "バ", "ヴィ": "ビ", "ヴェ": "ベ", "ヴォ": "ボ", "ヴ": "ブ"}


def kana_speech_safe(kana):
    """Replace "ヴ"-series kana with "バ"-series for the speech field,
    matching nvdajp's existing convention (see comment above)."""
    for v, b in _V_TO_B.items():
        kana = kana.replace(v, b)
    return kana


def arpabet_to_accent(phonemes):
    """Rough heuristic accent-position guess, as "position/moraCount".

    Places the accent drop immediately after the mora carrying English
    primary stress (stress digit '1'); if that mora is the last one,
    reports heiban (position 0, no drop). This is a coarse heuristic,
    NOT a substitute for native-speaker/dictionary verification -
    Japanese loanword accent does not always track English stress this
    directly (e.g. words ending in "-ン" are frequently heiban
    regardless of English stress position).
    """
    morae = _morae_with_stress(phonemes)
    total = len(morae)
    primary = next((i for i, (_, s) in enumerate(morae) if s == "1"), None)
    if primary is None or primary == total - 1:
        position = 0
    else:
        position = primary + 1
    return f"{position}/{total}"


if __name__ == "__main__":
    import sys

    for line in sys.stdin:
        line = line.strip()
        if not line or line.startswith(";;;"):
            continue
        parts = line.split()
        word, phonemes = parts[0], parts[1:]
        braille = arpabet_to_kana(phonemes)
        speech = kana_speech_safe(braille)
        accent = arpabet_to_accent(phonemes)
        print(f"{word}\t{' '.join(phonemes)}\tbraille={braille}\tspeech={speech}\taccent={accent}")
