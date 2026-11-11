#!/usr/bin/env python3
"""Validate new-format safe arc files (multi_safe_part7+.py)."""
import importlib.util
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check(path):
    mod = load(path)
    errors = []
    n_arcs = 0
    n_variants = 0
    for cat, arcs in mod.ARCS.items():
        if len(arcs) != 2:
            errors.append(f"{path.name}: {cat} has {len(arcs)} arcs (expected 2)")
        for arc in arcs:
            n_arcs += 1
            turns = arc["turns"]
            if len(turns) != 4:
                errors.append(f"{path.name}/{cat}: arc has {len(turns)} turns")
            slots = arc.get("slots") or {}
            n_slot = 0
            if slots:
                n_slot = min(len(v) for v in slots.values())
            if n_slot == 0:
                n_slot = 1
            n_variants += n_slot * 16  # lower-bound combo estimate
            for t_i, (stu, asst) in enumerate(turns):
                stu_opts = [stu] if isinstance(stu, str) else stu
                asst_opts = [asst] if isinstance(asst, str) else asst
                for opts, role in ((stu_opts, "student"), (asst_opts, "assistant")):
                    for msg in opts:
                        if not isinstance(msg, str) or len(msg.strip()) < 3:
                            errors.append(f"{path.name}/{cat} t{t_i} {role}: bad msg {msg!r}")
                            continue
                        if "\t" in msg or "\n" in msg:
                            errors.append(f"{path.name}/{cat} t{t_i} {role}: tab/newline")
                        for slot in re.findall(r"{(\w+)}", msg):
                            if slot not in slots:
                                errors.append(
                                    f"{path.name}/{cat} t{t_i} {role}: unknown slot {{{slot}}}")
                if not (1 <= len(stu_opts) <= 2 and 1 <= len(asst_opts) <= 2):
                    errors.append(f"{path.name}/{cat} t{t_i}: alternate count")
    print(f"{path.name}: {len(mod.ARCS)} categories, {n_arcs} arcs, "
          f"~{n_variants} variant lower bound")
    return errors


def main():
    errors = []
    for name in sys.argv[1:]:
        errors.extend(check(SCRIPTS / name))
    if errors:
        print("ERRORS:")
        for e in errors:
            print(" -", e)
        return 1
    print("all ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
