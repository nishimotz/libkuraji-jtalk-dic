# libkuraji-jtalk-dic

JTalk 拡張辞書（NAIST-JDIC + nvdajp 独自拡張）のビルドレシピ。

この辞書は Open JTalk 系の日本語形態素解析辞書 [NAIST-JDIC](http://naist-jdic.sourceforge.jp/) をベースに、NVDA 日本語版（nvdajp）が読み・アクセント推定の改善と点訳表記フィールドのために追加した拡張エントリ（`nvdajp-custom-dic`、`nvdajp-tankan-dic`、`nvdajp-eng-dic`）を加えたものです。

**この辞書は単一のプロジェクトの所有物ではなく、共有資産です:**
- **JTalk**（[nvdajp](https://github.com/nvdajp/nvdajp) の音声合成エンジン）が読み・アクセント推定に使用します。
- **[libkuraji](https://github.com/nishimotz/libkuraji)**（日本語点訳エンジン）が形態素解析器を介して分かち書きに使用します。拡張フィールド（点訳表記）はこの辞書に由来します。

## リポジトリの中身

- `src/nvdajp-jtalk-dic/`: 辞書ビルドスクリプト（`make_jdic.py` ほか）と NAIST-JDIC ソース・nvdajp 拡張データ（`naist-jdic-source/`）
- ビルド済みの `sys.dic` バイナリ自体はこのリポジトリには含まない（GitHub Releases での配布を予定、未実装）

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

## ライセンス

BSD 3-Clause License. 詳細は [LICENSE](LICENSE) を参照。NAIST-JDIC・MeCab のライセンス表記も同ファイルに含む。

## nvdajp との関係

このリポジトリは nvdajp の `miscDepsJp/jptools/jtalk/` 配下から辞書ビルドレシピを抽出したものです。nvdajp 自身のビルド（`scons jtalkSync`）は現時点ではこのリポジトリに依存せず、従来どおり内部のコピーでビルドします（今後、このリポジトリの成果物に一本化する可能性があります）。
