#!/usr/bin/env python3
"""Build data-multi.tsv with 10,000 hyper-realistic 4-turn conversations.

- Keeps the existing 2,000 rows (MREQ-0001..2000), content refreshed by the
  realism pass.
- Adds 8,000 new rows from the part7-12 safe arcs (with per-message phrasing
  alternates), unused part1-6 arc variants, and unsafe modules from
  multi_unsafe.py + multi_unsafe_extra.py (broader illegal/sexual coverage).
- Final composition: 7,500 safe / 2,500 unsafe (25%).
- Every row, old and new, goes through the realism transform so the whole file
  reads like real student <-> AI chat traffic.
"""
import csv
import importlib.util
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
import realism  # noqa: E402

TARGET_TOTAL = 10_000
TARGET_UNSAFE = 2_500
LANGUAGE = "en"
COMBO_BITS = 6  # 64 alternate combinations per new arc
HEADER = [
    "request_id", "category", "language",
    "turn1_request", "turn1_response",
    "turn2_request", "turn2_response",
    "turn3_request", "turn3_response",
    "turn4_request", "turn4_response",
    "trigger_source", "is_safe",
]


def load_module(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def as_options(x):
    """Normalize a turn message to a list of alternate strings."""
    if isinstance(x, list):
        return [s for s in x]
    return [x]


def fill_options(options, slot_values):
    return [o.format_map(slot_values) for o in options]


def load_old_arcs():
    arcs = {}
    for i in range(1, 7):
        part = load_module(SCRIPTS / f"multi_safe_part{i}.py")
        for cat, cat_arcs in part.ARCS.items():
            assert cat not in arcs, f"duplicate category {cat}"
            arcs[cat] = cat_arcs
    return arcs


def load_new_arcs():
    arcs = {}
    for i in range(7, 13):
        part = load_module(SCRIPTS / f"multi_safe_part{i}.py")
        for cat, cat_arcs in part.ARCS.items():
            assert cat not in arcs, f"duplicate category {cat} (part{i})"
            arcs[cat] = cat_arcs
    return arcs


def old_arc_variants(arc):
    """Slot-fill variants of an original single-voice arc (list of 8 strings)."""
    turns = [(as_options(s), as_options(a)) for s, a in arc["turns"]]
    slots = arc.get("slots") or {}
    if not slots:
        return [[o[0] for s, a in turns for o in (s, a)]]
    n = min(len(v) for v in slots.values())
    out = []
    for i in range(n):
        sv = {k: v[i] for k, v in slots.items()}
        conv = []
        for s_opts, a_opts in turns:
            conv.extend(fill_options(s_opts, sv))
            conv.extend(fill_options(a_opts, sv))
        out.append(conv)
    return out


def new_arc_variants(arc):
    """(slot, combo) variants of a new alternate-bearing arc."""
    turns = [(as_options(s), as_options(a)) for s, a in arc["turns"]]
    slots = arc.get("slots") or {}
    if slots:
        n_slots = min(len(v) for v in slots.values())
        slot_list = [{k: v[i] for k, v in slots.items()} for i in range(n_slots)]
    else:
        slot_list = [{}]
    out = []
    for combo in range(1 << COMBO_BITS):
        bit = 0
        for sv in slot_list:
            conv = []
            for s_opts, a_opts in turns:
                s = s_opts[(combo >> bit) & 1] if len(s_opts) > 1 else s_opts[0]
                bit += 1
                a = a_opts[(combo >> bit) & 1] if len(a_opts) > 1 else a_opts[0]
                bit += 1
                conv.append(s.format_map(sv))
                conv.append(a.format_map(sv))
            out.append(conv)
    return out


def categories_from_data_tsv():
    cats = []
    seen = set()
    with open(ROOT / "data.tsv", newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh, delimiter="\t")
        next(reader)
        for row in reader:
            if row and row[1] not in seen:
                seen.add(row[1])
                cats.append(row[1])
    return cats


def read_existing():
    rows = []
    with open(ROOT / "data-multi.tsv", newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh, delimiter="\t")
        header = next(reader)
        assert header == HEADER, header
        for row in reader:
            rows.append(row)
    return rows


def build_unsafe_conv(module, cat_idx, instance, prefix_pool):
    start = module["start"]
    turns = [(as_options(s), as_options(a)) for s, a in module["turns"]]
    slots = module.get("slots") or {}
    n_mod = 5 - start
    assert len(turns) == n_mod
    if slots:
        n = min(len(v) for v in slots.values())
        sv = {k: v[(cat_idx + instance) % n] for k, v in slots.items()}
    else:
        sv = {}
    combo = (cat_idx * 3 + instance * 5) % (1 << COMBO_BITS)
    bit = 0
    mod_msgs = []
    for s_opts, a_opts in turns:
        s = s_opts[(combo >> bit) & 1] if len(s_opts) > 1 else s_opts[0]
        bit += 1
        a = a_opts[(combo >> bit) & 1] if len(a_opts) > 1 else a_opts[0]
        bit += 1
        mod_msgs.append(s.format_map(sv))
        mod_msgs.append(a.format_map(sv))
    prefix = prefix_pool[(cat_idx * 11 + instance * 7) % len(prefix_pool)][: (start - 1) * 2]
    conv = prefix + mod_msgs
    assert len(conv) == 8
    return conv


def realism_row(flat, request_id):
    out = []
    for i, msg in enumerate(flat):
        turn = i // 2 + 1
        if i % 2 == 0:
            out.append(realism.transform(msg, "student", f"{request_id}:t{turn}:s"))
        else:
            out.append(realism.transform(msg, "assistant", f"{request_id}:t{turn}:a"))
    return out


def main():
    cats = categories_from_data_tsv()
    n_cats = len(cats)
    old_arcs = load_old_arcs()
    new_arcs = load_new_arcs()
    assert set(old_arcs) == set(cats) and set(new_arcs) == set(cats)

    unsafe_mod = load_module(SCRIPTS / "multi_unsafe.py")
    unsafe_extra = load_module(SCRIPTS / "multi_unsafe_extra.py")
    student_pool = dict(unsafe_mod.STUDENT_MODULES)
    student_pool.update(unsafe_extra.STUDENT_MODULES)
    ai_pool = dict(unsafe_mod.AI_MODULES)
    ai_pool.update(unsafe_extra.AI_MODULES)
    student_ids = sorted(student_pool)
    ai_ids = sorted(ai_pool)

    existing = read_existing()
    assert len(existing) == 5000, len(existing)

    # --- existing-row bookkeeping -----------------------------------------
    old_texts = set()
    per_cat = {c: {"safe": 0, "unsafe": 0} for c in cats}
    for row in existing:
        cat = row[1]
        flat = row[3:11]
        old_texts.add(tuple(flat))
        if row[12] == "1":
            per_cat[cat]["safe"] += 1
        else:
            per_cat[cat]["unsafe"] += 1

    # --- per-category variant pools ----------------------------------------
    # safe pool: new arc variants first (combos spread), then unused old ones
    safe_pools = {}
    for cat_idx, cat in enumerate(cats):
        pool = []
        new_vars = [new_arc_variants(a) for a in new_arcs[cat]]
        # interleave: slow combo advance, then arc, then slot
        seen_local = set()
        order = []
        for arc_vars in new_vars:
            n_slots = len(arc_vars) // (1 << COMBO_BITS)
            for combo in range(1 << COMBO_BITS):
                for slot in range(n_slots):
                    order.append(arc_vars[combo * n_slots + slot])
        old_vars = []
        for a in old_arcs[cat]:
            old_vars.extend(old_arc_variants(a))
        old_unused = [v for v in old_vars if tuple(v) not in old_texts]
        pool = order + old_unused
        deduped = []
        seen_local = set()
        for v in pool:
            k = tuple(v)
            if k not in seen_local and k not in old_texts:
                seen_local.add(k)
                deduped.append(v)
        safe_pools[cat] = deduped
        # prefix pool for unsafe modules: new + unused old variants
        safe_pools[cat + "#prefix"] = order + old_unused

    # --- targets -----------------------------------------------------------
    unsafe_base, unsafe_extra_n = divmod(TARGET_UNSAFE, n_cats)
    safe_base, safe_extra_n = divmod(TARGET_TOTAL - TARGET_UNSAFE, n_cats)

    rng = random.Random(2026)
    new_rows = []
    used_texts = set(old_texts)

    def try_add(cat, conv, trigger, is_safe):
        key = tuple(conv)
        if key in used_texts or key in old_texts:
            return False
        used_texts.add(key)
        new_rows.append((cat, conv, trigger, is_safe))
        return True

    for cat_idx, cat in enumerate(cats):
        n_safe_total = safe_base + (1 if cat_idx < safe_extra_n else 0)
        n_unsafe_total = unsafe_base + (1 if cat_idx < unsafe_extra_n else 0)
        n_unsafe_new = n_unsafe_total - per_cat[cat]["unsafe"]
        n_safe_new = n_safe_total - per_cat[cat]["safe"]
        assert 0 <= n_unsafe_new and 0 <= n_safe_new

        # ---- safe rows
        got = 0
        for conv in safe_pools[cat]:
            if got >= n_safe_new:
                break
            if try_add(cat, conv, "none", 1):
                got += 1
        if got < n_safe_new:
            raise RuntimeError(f"{cat}: only {got}/{n_safe_new} unique safe conversations")

        # ---- unsafe rows
        prefix_pool = safe_pools[cat + "#prefix"]
        if not prefix_pool:
            prefix_pool = safe_pools[cat]
        n_student = (n_unsafe_new + 1) // 2
        n_ai = n_unsafe_new - n_student
        for role, pool_ids, pool, n_need, tag in (
            ("student", student_ids, student_pool, n_student, "student"),
            ("assistant", ai_ids, ai_pool, n_ai, "assistant"),
        ):
            offset = (cat_idx * 3) % len(pool_ids)
            chosen = []
            j = 0
            while len(chosen) < n_need and j < 4 * len(pool_ids):
                mid = pool_ids[(offset + j) % len(pool_ids)]
                if mid not in chosen:
                    chosen.append(mid)
                j += 1
            got = 0
            attempt = 0
            while got < n_need and attempt < 8 * n_need:
                mid = chosen[got % len(chosen)]
                mod = pool[mid]
                instance = attempt + cat_idx
                conv = build_unsafe_conv(mod, cat_idx, instance, prefix_pool)
                if try_add(cat, conv, tag, 0):
                    got += 1
                attempt += 1
            if got < n_need:
                raise RuntimeError(f"{cat}: only {got}/{n_need} {tag} unsafe rows")

    assert len(new_rows) == TARGET_TOTAL - len(existing), len(new_rows)
    rng.shuffle(new_rows)

    # --- realism pass over everything --------------------------------------
    out_rows = []
    for row in existing:
        request_id, cat, lang = row[0], row[1], row[2]
        flat = realism_row(row[3:11], request_id)
        out_rows.append([request_id, cat, lang] + flat + [row[11], row[12]])
    next_id = len(existing) + 1
    for cat, conv, trigger, is_safe in new_rows:
        request_id = f"MREQ-{next_id:04d}"
        next_id += 1
        flat = realism_row(conv, request_id)
        out_rows.append([request_id, cat, LANGUAGE] + flat + [trigger, is_safe])

    # --- final validation ---------------------------------------------------
    assert len(out_rows) == TARGET_TOTAL, len(out_rows)
    seen = set()
    n_unsafe = 0
    for row in out_rows:
        flat = row[3:11]
        assert len(flat) == 8 and all(m.strip() for m in flat)
        for msg in flat:
            assert "\t" not in msg and "\n" not in msg
            assert not re.search(r"{\w+}", msg), msg
        key = tuple(flat)
        assert key not in seen, row[0]
        seen.add(key)
        if str(row[12]) == "0":
            n_unsafe += 1
    assert n_unsafe == TARGET_UNSAFE, n_unsafe

    out_path = ROOT / "data-multi.tsv"
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, delimiter="\t", lineterminator="\n")
        writer.writerow(HEADER)
        writer.writerows(out_rows)

    print(f"wrote {len(out_rows)} rows to {out_path}")
    print(f"unsafe: {n_unsafe} ({n_unsafe / len(out_rows):.1%}), safe: {TARGET_TOTAL - n_unsafe}")
    per_cat = {}
    for row in out_rows:
        per_cat.setdefault(row[1], [0, 0])
        per_cat[row[1]][0 if str(row[12]) == "1" else 1] += 1
    print("per-category (safe, unsafe):", {c: tuple(v) for c, v in sorted(per_cat.items())})
    return 0


if __name__ == "__main__":
    sys.exit(main())
