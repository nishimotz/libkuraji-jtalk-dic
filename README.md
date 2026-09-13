# libkuraji-jtalk-dic

JTalk 拡張辞書（NAIST-JDIC + nvdajp 独自拡張）のビルドレシピ。

この辞書は Open JTalk 系の日本語形態素解析辞書 [NAIST-JDIC](http://naist-jdic.sourceforge.jp/) をベースに、NVDA 日本語版（nvdajp）が読み・アクセント推定の改善と点訳表記フィールドのために追加した拡張エントリ（`nvdajp-custom-dic`、`nvdajp-tankan-dic`）を加えたものです。

**英単語辞書について**: 本リポジトリは点訳エンジン [libkuraji](https://github.com/nishimotz/libkuraji) 向けの軽量形態素辞書（BSD 3-Clause）であり、一般的な英単語の読み辞書（`nvdajp-eng-dic`）は同梱していません（点訳処理では英単語はアルファベット綴りで表記されるため、カタカナ読み辞書を必要としません）。NVDA 日本語版（nvdajp）の JTalk 音声合成で `bep-eng.dic` を含む完全な英単語発音辞書を利用する場合は、[nvdajp/nvdajp-jtalk-dic](https://github.com/nvdajp/nvdajp-jtalk-dic)（GPL-2.0）を利用してください。

**この辞書は単一のプロジェクトの所有物ではなく、共有資産です:**
- **JTalk**（[nvdajp](https://github.com/nvdajp/nvdajp) の音声合成エンジン）が読み・アクセント推定に使用します。
- **[libkuraji](https://github.com/nishimotz/libkuraji)**（日本語点訳エンジン）が形態素解析器を介して分かち書きに使用します。拡張フィールド（点訳表記）はこの辞書に由来します。

## リポジトリの中身

- `src/nvdajp-jtalk-dic/`: 辞書ビルドスクリプト（`make_jdic.py` ほか）と NAIST-JDIC ソース・nvdajp 拡張データ（`naist-jdic-source/`）
- `src/mecab-src/`: 辞書コンパイラ `mecab-dict-index` をビルドするための MeCab ソース（Open JTalk のフォーク）。Windows/MSVC 専用（`Makefile.mak`, nmake ビルド）。
- ビルド済みの辞書バイナリ一式（`sys.dic`、`matrix.bin`、`char.bin`、`unk.dic`、`dicrc`、`DIC_VERSION` — 6 ファイルすべてが揃って初めて MeCab が読み込める）はこのリポジトリのソースには含まない。`v*` タグを push すると `.github/workflows/release-dic.yml` が CI でビルドし、6 ファイルを zip にまとめて GitHub Releases に添付する（zip とその SHA256 チェックサムファイルの 2 点セット）。

## ビルド方法

### 1. mecab-dict-index のビルド（Windows + MSVC が必要）

```console
cd src/mecab-src/src
nmake /f Makefile.mak MACHINE=x64 mecab.lib mecab-dict-index.exe
```

`libmecab.dll`（DLL ターゲット）は不要なのでビルドしない。CI（`.github/workflows/build-dic.yml`）は `ilammy/msvc-dev-cmd` で MSVC 環境を用意し、Windows ランナー上でこのコマンドを実行して検証している。

**注意**: このソースは Open JTalk 由来のフォークで、`nishimotz/libopenjtalk` リポジトリのソースとは系統が異なる（試したところ、後者は現行 MSVC でのビルドに問題があった）。`nvdajp` 本体が実際に使っているのと同じソース（`miscDepsJp/include/python-jtalk/libopenjtalk/mecab`）をここに同梱している。

### 2. 辞書のビルド

```console
python src/nvdajp-jtalk-dic/make_jdic.py --mecab-dict-index src/mecab-src/src/mecab-dict-index.exe --outdir build/dic
```

生成される `build/dic/` に `sys.dic`、`matrix.bin`、`char.bin`、`unk.dic`、`dicrc`、`DIC_VERSION` が出力されます。動作確認済み（nvdajp の `translator2` に読み込ませて分かち書き・点訳できることを確認済み）。

`mecab-dict-index` を用意できない場合でも、CSV ソース（nvdajp 拡張エントリの品詞 ID 解決など）だけを検証できます。

```console
python src/nvdajp-jtalk-dic/make_jdic.py --validate-only
```

## ユーザー辞書（独自語彙の追加）

固有名詞や専門用語など、ベース辞書に無い語を追加して読み・分かち書きを正しくするためのユーザー辞書を、ビルド済みの `sys.dic` に対してコンパイルできます。libkuraji・JTalk のどちらの利用者にも共通して使える機能です。

```console
python src/nvdajp-jtalk-dic/build_userdic.py \
  --mecab-dict-index src/mecab-src/src/mecab-dict-index.exe \
  --dic-dir build/dic \
  --csv examples/userdic/sample.csv \
  --outfile build/jtusr.dic
```

CSV の書式は `examples/userdic/sample.csv` を参照。品詞 ID は自動採番ではなく `0,0`（文頭/文末）＋人手調整コストで指定する（naist-jdic は自動採番に必要な CRF モデルを含まないため）。品詞別 ID への移行は今後の課題（nvdajp roadmap タスク 2.8 として追跡）。

生成された `jtusr.dic` は `--dic-dir` に指定したのと同じベース辞書と組み合わせて読み込む必要がある（MeCab はバージョン・文字コード・連接コスト表サイズの一致を検査するため）。ベース辞書を再ビルドしたら、ユーザー辞書も再ビルドすること。

動作確認済み: 生成した `jtusr.dic` を nvdajp の `translator2` に読み込ませ、サンプルエントリの読みが優先されることを確認済み。

## ライセンス

BSD 3-Clause License. 詳細は [LICENSE](LICENSE) を参照。NAIST-JDIC・MeCab のライセンス表記も同ファイルに含む。

## nvdajp との関係

このリポジトリは nvdajp の `miscDepsJp/jptools/jtalk/`（レシピ）と `miscDepsJp/include/python-jtalk/libopenjtalk/mecab/`（MeCab ソース）から抽出したものです。点訳エンジン [libkuraji](https://github.com/nishimotz/libkuraji) の形態素解析・分かち書きに必要な最小限の拡張辞書（BSD 3-Clause）を提供します。

NVDA 日本語版（nvdajp）の音声合成辞書としては、`bep-eng.dic` を同梱した [nvdajp/nvdajp-jtalk-dic](https://github.com/nvdajp/nvdajp-jtalk-dic)（GPL-2.0）が正本として利用されます。

## CI

- `.github/workflows/validate.yml`: MeCab 不要の CSV 検証のみを Ubuntu で実行（push / PR ごと）。
- `.github/workflows/build-dic.yml`: Windows ランナー上で mecab-dict-index のビルド → 辞書ビルド → ユーザー辞書ビルドまで一気通貫で検証（push / PR ごと。Releases には公開しない）。
- `.github/workflows/release-dic.yml`: `v*` タグを push したときのみ実行。上記と同じ手順でビルドし、`build/dic/` を zip 化して GitHub Releases に公開する。タグ名がそのままファイル名（`jtalk-dic-<tag>.zip`）とリリースに使われる。あわせて `mecab-dict-index-<tag>.exe`（辞書コンパイラ本体）もチェックサム付きで公開する。

### リリースの作り方

```console
git tag v0.1.0
git push origin v0.1.0
```

これをトリガーに CI が以下を GitHub Release に自動添付する:

- `jtalk-dic-v0.1.0.zip` と `.sha256`: 辞書一式（`sys.dic` 等 6 ファイル）
- `mecab-dict-index-v0.1.0.exe` と `.sha256`: 辞書コンパイラ本体。ユーザー辞書（`jtusr.dic`）を自前でビルドしたい利用者向け。**署名なしの実行ファイル**なので、利用前に必ずチェックサムを検証すること。
