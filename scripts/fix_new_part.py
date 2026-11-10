#!/usr/bin/env python3
"""Repeatedly apply structural fixes to new-format arc files until they parse.

Usage: python3 fix_new_part.py multi_safe_part11.py
"""
import importlib.util
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def load_ok(path):
    try:
        spec = importlib.util.spec_from_file_location(path.stem, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod, None
    except Exception as e:  # noqa: BLE001
        return None, e


def fix_once(src):
    changed = []
    def sub(pat, rep, flags=0, name=""):
        nonlocal src
        new = re.sub(pat, rep, src, flags=flags)
        if new != src:
            changed.append(name or pat)
            src = new

    # join "unterminated text\n<spaces>" + ".replace(chr(10), "")" junctions
    sub(r'\n\s*(?="\.replace\(chr\(10\),\s*""\))', '', name="join-replace")
    # drop redundant .replace(chr(10), "") method calls on closed strings
    sub(r'""\.replace\(chr\(10\),\s*""\),\],', '"],', name="drop-replace-tail")
    sub(r'""\.replace\(chr\(10\),\s*""\),', '",', name="drop-replace")
    sub(r'"",\],', '"],', name="repair-double-quote")
    # assistant list closes but turn tuple does not: "X"],\n([  ->  "X"]),\n([
    sub(r'("(?:[^"\\]|\\.)*")\],(\n\s*)\(\["', r'\1]),\2(["', name="open-turn-close")
    # ["X"][0] -> "X" ; ["X"[0]] -> "X"] ; "X"[0], -> "X",
    sub(r'\[("(?:[^"\\]|\\.)*")\]\[0\]', r'\1', name="list-indexed")
    sub(r'\[("(?:[^"\\]|\\.)*")\[0\]\]', r'\1]', name="str-indexed-list")
    # (( -> ( at turn starts ; ])) -> ])
    sub(r'^(\s*)\(\(', r'\1(', flags=re.M, name="double-open")
    sub(r'\]\)\),', ']),', name="double-close")
    # nested single-string list as a line: ["X"]), / ["X"]], / ["X"],
    sub(r'^(\s*)\[\s*("(?:[^"\\]|\\.)*")\s*\]\s*(\)?)\s*,\s*$', r'\1\2\3,', flags=re.M, name="nested-single")
    # bare final alternate ending "X"), -> "X"]),
    sub(r'^(\s*)("(?:[^"\\]|\\.)*")\),\s*$', r'\1\2]),', flags=re.M, name="bare-turn-close")
    # stray extra bracket at line end: "X"]]), / "X"])), / "X")),
    sub(r'^(\s*)("(?:[^"\\]|\\.)*")\]\],\s*$', r'\1\2],', flags=re.M, name="extra-bracket0")
    sub(r'^(\s*)("(?:[^"\\]|\\.)*")\]\]\),\s*$', r'\1\2]),', flags=re.M, name="extra-bracket3")
    sub(r'^(\s*)("(?:[^"\\]|\\.)*")\]\),\s*$', r'\1\2]),', flags=re.M, name="extra-bracket")
    sub(r'^(\s*)("(?:[^"\\]|\\.)*")\]\)\),\s*$', r'\1\2]),', flags=re.M, name="extra-bracket2")
    sub(r'^(\s*)("(?:[^"\\]|\\.)*")\)\),\s*$', r'\1\2),', flags=re.M, name="extra-paren")
    return src, changed


def main(name):
    path = SCRIPTS / name
    src = path.read_text()
    for round_no in range(1, 12):
        mod, err = load_ok(path)
        if mod is not None:
            print(f"parses after {round_no - 1} fix rounds")
            return 0
        new_src, changed = fix_once(src)
        if not changed:
            print(f"stuck after {round_no - 1} rounds; last error: {err}")
            return 1
        src = new_src
        path.write_text(src)
    mod, err = load_ok(path)
    if mod is not None:
        print("parses after 10+ rounds")
        return 0
    print(f"still failing: {err}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
