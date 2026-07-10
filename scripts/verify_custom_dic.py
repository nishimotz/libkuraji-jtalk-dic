#!/usr/bin/env python3
"""Verify that previously duplicated words are now read from custom dic
(not eng-dic) after adding them to EXCLUDED_WORDS."""
import fugashi

tagger = fugashi.GenericTagger(
    "-d f:/nvda/gh/libkuraji-jtalk-dic/src/nvdajp-jtalk-dic/build/dic"
    " -r f:/nvda/gh/libkuraji-jtalk-dic/src/nvdajp-jtalk-dic/build/dic/dicrc"
)

# Custom dic entries cost=1000, eng-dic cost=3000.
# Previously these words existed in both; now they should only be in custom.
# Check that the reading matches the custom dic version.
words = [
    "accent", "button", "help", "version", "youtube", "radio",
    "oasis", "variety", "hurry", "gallery", "diary", "luxury",
    "firearm", "hierarchy", "arroyo", "matsui", "tetsuo", "ceo",
    "sos", "aoki", "diaries", "fiery", "worry", "scouring",
    "pizzeria", "maria", "burrowing", "radioactive", "radioactivity",
    "matsui", "tetsuo", "tsui", "oishi", "aoi", "aida", "iona", "iota",
    "iain", "yeo", "ios", "galleria", "fabrizio", "koreatown",
    "darius", "mariah", "zachariah", "pariah", "gonorrhea", "diarrhea",
    "diarrhoea", "psoriasis", "aorta", "aortic", "notoriety",
    "radio", "oasis",
]

# Expected readings from custom_dic_maker.py
expected = {
    "accent": "アクセント",
    "button": "ボタン",
    "help": "ヘルプ",
    "version": "バージョン",
    "youtube": "ユーチューブ",
    "variety": "バライアティー",
    "firearm": "ファイアアーム",
    "hierarchy": "ハイアラーキー",
    "arroyo": "アロヨ",
    "radioactive": "レイディオアクティブ",
    "radioactivity": "レイディオアクティビティー",
    "burrowing": "バロウイング",
    "pizzeria": "ピッツェリア",
    "maria": "マリア",
    # Newly added
    "matsui": "マツイ",
    "tetsuo": "テツオ",
    "tsui": "ツイ",
    "oishi": "オイシ",
    "aoki": "アオキ",
    "aoi": "アオイ",
    "aida": "アイダ",
    "iona": "イオナ",
    "iota": "イオタ",
    "iain": "イアン",
    "yeo": "イェオ",
    "ios": "アイオス",
    "galleria": "ガレリア",
    "fabrizio": "ファブリツィオ",
    "koreatown": "コリアタウン",
    "darius": "ダライウス",
    "mariah": "マライア",
    "zachariah": "ザカライア",
    "pariah": "パライア",
    "gonorrhea": "ゴノレア",
    "diarrhea": "ダイヤリア",
    "diarrhoea": "ダイヤリア",
    "psoriasis": "ソライシス",
    "aorta": "アオルタ",
    "aortic": "アオルティック",
    "notoriety": "ノウトライアティー",
    "radio": "ラジオ",
    "oasis": "オアシス",
}

_H2Z = {}
for c in "abcdefghijklmnopqrstuvwxyz":
    _H2Z[c] = chr(ord(c) - ord("a") + ord("ａ"))
for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    _H2Z[c] = chr(ord(c) - ord("A") + ord("ａ"))
tr = str.maketrans(_H2Z)

passed = 0
failed = 0
for w in words:
    fw = w.translate(tr)
    result = tagger(fw)
    for word in result:
        fs = word.feature
        # GenericTagger feature is a tuple; reading is field index 7
        # But the actual field layout depends on the dictionary.
        # Let's just print the raw feature.
        if len(fs) > 7:
            reading = fs[7]
        elif len(fs) > 0:
            reading = "(no reading)"
        else:
            reading = "(empty)"
        pos = fs[0] if fs else "?"
        exp = expected.get(w, None)
        if exp:
            ok = reading == exp
            status = "OK" if ok else f"MISMATCH (expected {exp})"
            if ok:
                passed += 1
            else:
                failed += 1
        else:
            status = "(no expected value)"
        print(f"{w:12s} surface={word.surface} reading={reading} pos={pos} {status}")