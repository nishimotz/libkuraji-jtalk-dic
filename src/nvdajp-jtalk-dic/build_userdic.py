# coding: utf-8
# build_userdic.py
# Copyright (C) 2026 Takuya Nishimoto
# License: BSD 3-Clause. See LICENSE.
#
# Compile a MeCab user dictionary (e.g. jtusr.dic) from a CSV of custom
# vocabulary, against an already-built base dictionary (see make_jdic.py).
# This lets any libkuraji/JTalk user add domain-specific words (proper
# nouns, technical terms) without rebuilding the base dictionary, so that
# word separation and braille/reading output are correct for their text.
#
# The compiled user dictionary must be loaded together with the sys.dic
# it was built against (MeCab's Dictionary::isCompatible checks version,
# charset and the left/right context table sizes), so it should be
# rebuilt whenever the base dictionary changes.
#
# CSV entry convention: nvdajp's own custom entries (see
# ../nvdajp-jtalk-dic/naist-jdic-source/nvdajp-custom-dic.csv) use "0,0"
# (BOS/EOS context IDs) plus a hand-tuned cost, since automatic ID
# assignment requires a CRF model file that naist-jdic does not provide.
# Migrating to per-POS context IDs is tracked as nvdajp roadmap task 2.8;
# the same convention applies to user dictionaries built with this tool.

import argparse
import subprocess
from pathlib import Path


def build_user_dic(mecab_dict_index: Path, dic_dir: Path, csv_path: Path, out_path: Path) -> Path:
	"""Compile csv_path into a MeCab user dictionary at out_path.

	Raises RuntimeError if mecab-dict-index fails or does not report success.
	"""
	mecab_dict_index = mecab_dict_index.resolve()
	dic_dir = dic_dir.resolve()
	csv_path = csv_path.resolve()
	out_path = out_path.resolve()
	out_path.parent.mkdir(parents=True, exist_ok=True)
	result = subprocess.run(
		[
			str(mecab_dict_index),
			"-d",
			str(dic_dir),
			"-u",
			str(out_path),
			"-f",
			"utf-8",
			"-t",
			"utf-8",
			str(csv_path),
		],
		capture_output=True,
		text=True,
		encoding="utf-8",
		errors="replace",
	)
	output = (result.stdout or "") + (result.stderr or "")
	# mecab-dict-index may not exit nonzero on CHECK_DIE failures (the Open
	# JTalk build disables exit in die()), so also require the success marker.
	if result.returncode != 0 or "done!" not in output or not out_path.exists():
		raise RuntimeError(
			f"mecab-dict-index failed to build {out_path} (exit {result.returncode}):\n{output}"
		)
	return out_path


def _parse_args():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--mecab-dict-index", required=True, type=Path)
	parser.add_argument("--dic-dir", required=True, type=Path, help="base dictionary directory (sys.dic etc.)")
	parser.add_argument("--csv", required=True, type=Path)
	parser.add_argument("--outfile", required=True, type=Path)
	return parser.parse_args()


def _main():
	args = _parse_args()
	path = build_user_dic(args.mecab_dict_index, args.dic_dir, args.csv, args.outfile)
	print(f"built {path}")


if __name__ == "__main__":
	_main()
