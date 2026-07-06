# libkuraji-jtalk-dic

JTalk 拡張辞書（NAIST-JDIC + nvdajp 独自拡張）のビルドレシピ。

この辞書は Open JTalk 系の日本語形態素解析辞書 [NAIST-JDIC](http://naist-jdic.sourceforge.jp/) をベースに、NVDA 日本語版（nvdajp）が読み・アクセント推定の改善と点訳表記フィールドのために追加した拡張エントリ（`nvdajp-custom-dic`、`nvdajp-tankan-dic`、`nvdajp-eng-dic`）を加えたものです。

**この辞書は単一のプロジェクトの所有物ではなく、共有資産です:**
- **JTalk**（[nvdajp](https://github.com/nvdajp/nvdajp) の音声合成エンジン）が読み・アクセント推定に使用します。
- **[libkuraji](https://github.com/nishimotz/libkuraji)**（日本語点訳エンジン）が形態素解析器を介して分かち書きに使用します。拡張フィールド（点訳表記）はこの辞書に由来します。

## リポジトリの中身

- `src/nvdajp-jtalk-dic/`: 辞書ビルドスクリプト（`make_jdic.py` ほか）と NAIST-JDIC ソース・nvdajp 拡張データ（`naist-jdic-source/`）
- ビルド済みの辞書バイナリ一式（`sys.dic`、`matrix.bin`、`char.bin`、`unk.dic`、`dicrc`、`DIC_VERSION` — 6 ファイルすべてが揃って初めて MeCab が読み込める）はこのリポジトリには含まない（GitHub Releases での配布を予定、未実装。配布時は 1 ファイルではなくディレクトリ／アーカイブ単位で扱う）

## ビルド方法

辞書のコンパイルには MeCab の `mecab-dict-index` 実行ファイルが必要です。このリポジトリには含まれていません（ビルドは別途 MeCab ソースから、または nvdajp チェックアウトで `scons jtalkSync` を実行して用意してください）。

```console
python src/nvdajp-jtalk-dic/make_jdic.py --mecab-dict-index /path/to/mecab-dict-index.exe --outdir build/dic
```

生成される `build/dic/` に `sys.dic`、`matrix.bin`、`char.bin`、`unk.dic`、`dicrc`、`DIC_VERSION` が出力されます。動作確認済み（nvdajp の `translator2` に読み込ませて分かち書き・点訳できることを確認済み）。

`mecab-dict-index` を用意できない場合でも、CSV ソース（nvdajp 拡張エントリの品詞 ID 解決など）だけを検証できます。CI はこのモードを実行しています。

```console
python src/nvdajp-jtalk-dic/make_jdic.py --validate-only
```

## ユーザー辞書（独自語彙の追加）

固有名詞や専門用語など、ベース辞書に無い語を追加して読み・分かち書きを正しくするためのユーザー辞書を、ビルド済みの `sys.dic` に対してコンパイルできます。libkuraji・JTalk のどちらの利用者にも共通して使える機能です。

```console
python src/nvdajp-jtalk-dic/build_userdic.py \
  --mecab-dict-index /path/to/mecab-dict-index.exe \
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

このリポジトリは nvdajp の `miscDepsJp/jptools/jtalk/` 配下から辞書ビルドレシピを抽出したものです。nvdajp 自身のビルド（`scons jtalkSync`）は現時点ではこのリポジトリに依存せず、従来どおり内部のコピーでビルドします（今後、このリポジトリの成果物に一本化する可能性があります）。
