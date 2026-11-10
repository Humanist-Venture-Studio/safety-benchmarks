#!/usr/bin/env python3
"""Generate data-multi.tsv: 2000 four-turn K-12 edtech conversations.

Layout: one row per conversation.
Columns: request_id, category, language, turn1_request, turn1_response,
         turn2_request, turn2_response, turn3_request, turn3_response,
         turn4_request, turn4_response, trigger_source, is_safe

- 75% safe (is_safe=1, trigger_source=none): nothing in the conversation
  should trigger a safety warning.
- 25% unsafe (is_safe=0): roughly half triggered by the STUDENT violating
  guardrails (trigger_source=student, assistant responds well) and half by the
  ASSISTANT violating guardrails (trigger_source=assistant, student is normal).

Categories and ordering come from data.tsv; safe arcs come from
scripts/multi_safe_part{1..6}.py; unsafe modules from scripts/multi_unsafe.py.
"""
import csv
import importlib.util
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
TOTAL = 5000
UNSAFE_TOTAL = 1250
LANGUAGE = "en"
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


def categories_from_data_tsv():
    cats = []
    seen = set()
    with open(ROOT / "data.tsv", newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh, delimiter="\t")
        next(reader)  # header
        for row in reader:
            if row and row[1] not in seen:
                seen.add(row[1])
                cats.append(row[1])
    return cats


def fill(turns, slot_values):
    """Apply one filling index to a template arc (zip semantics)."""
    out = []
    for student, assistant in turns:
        out.append((
            student.format_map(slot_values),
            assistant.format_map(slot_values),
        ))
    return out


def arc_variants(arc):
    """All variants of a safe arc, one per filling index."""
    slots = arc["slots"]
    if not slots:
        return [fill(arc["turns"], {})]
    length = min(len(v) for v in slots.values())
    variants = []
    for i in range(length):
        sv = {k: v[i] for k, v in slots.items()}
        variants.append(fill(arc["turns"], sv))
    return variants


def flatten(variant):
    return tuple(msg for pair in variant for msg in pair)


def pick_modules(pool, preferred, needed, cat_idx):
    """Chosen preferred ids first, then deterministic rotation over the pool."""
    chosen = list(dict.fromkeys(preferred))[:needed]
    ids = sorted(pool.keys())
    offset = (cat_idx * 7) % len(ids)
    j = 0
    while len(chosen) < needed:
        mid = ids[(offset + j) % len(ids)]
        if mid not in chosen:
            chosen.append(mid)
        j += 1
        if j > 3 * len(ids):
            raise RuntimeError("module rotation failed")
    return chosen


def build_unsafe_conv(module, pool, cat_idx, instance, prefix_variants):
    start = module["start"]
    n_mod_turns = 5 - start
    assert len(module["turns"]) == n_mod_turns
    slots = module.get("slots") or {}
    sv = {k: v[(cat_idx + instance) % len(v)] for k, v in slots.items()}
    mod_turns = fill(module["turns"], sv)
    # Prefix: category-flavored safe turns 1..start-1, rotated for variety.
    prefix = prefix_variants[(cat_idx + instance) % len(prefix_variants)][: start - 1]
    variant = prefix + mod_turns
    assert len(variant) == 4
    return variant


def main():
    cats = categories_from_data_tsv()
    n_cats = len(cats)
    assert n_cats >= 2

    # Merge safe arcs.
    arcs = {}
    for i in range(1, 7):
        part = load_module(SCRIPTS / f"multi_safe_part{i}.py")
        for cat, cat_arcs in part.ARCS.items():
            assert cat not in arcs, f"duplicate category {cat}"
            assert len(cat_arcs) >= 3, cat
            arcs[cat] = cat_arcs
    assert set(arcs) == set(cats), "safe arc categories mismatch data.tsv"

    unsafe_mod = load_module(SCRIPTS / "multi_unsafe.py")
    unsafe_mod2 = load_module(SCRIPTS / "multi_unsafe2.py")
    student_pool = {**unsafe_mod.STUDENT_MODULES, **getattr(unsafe_mod2, "STUDENT_MODULES2", {})}
    ai_pool = {**unsafe_mod.AI_MODULES, **getattr(unsafe_mod2, "AI_MODULES2", {})}

    def merge_pref(a, b):
        out = {}
        for cat, ids in list(a.items()) + list(b.items()):
            out.setdefault(cat, [])
            out[cat].extend(x for x in ids if x not in out[cat])
        return out

    pref_student = merge_pref(unsafe_mod.PREFERRED_STUDENT, getattr(unsafe_mod2, "PREFERRED_STUDENT2", {}))
    pref_ai = merge_pref(unsafe_mod.PREFERRED_AI, getattr(unsafe_mod2, "PREFERRED_AI2", {}))
    for cat, ids in list(pref_student.items()) + list(pref_ai.items()):
        assert cat in cats, f"unknown preferred category {cat}"
        for mid in ids:
            assert mid in student_pool or mid in ai_pool, f"unknown module {mid}"

    # Targets per category.
    unsafe_base, unsafe_extra = divmod(UNSAFE_TOTAL, n_cats)
    safe_base, safe_extra = divmod(TOTAL - UNSAFE_TOTAL, n_cats)
    rows = []
    seen_convs = set()
    total_unsafe = 0
    student_driven = 0
    ai_driven = 0

    for cat_idx, cat in enumerate(cats):
        n_unsafe = unsafe_base + (1 if cat_idx < unsafe_extra else 0)
        n_safe = safe_base + (1 if cat_idx < safe_extra else 0)
        n_student = (n_unsafe + 1) // 2
        n_ai = n_unsafe - n_student

        variants_per_arc = [arc_variants(a) for a in arcs[cat]]
        # Interleave arcs so consecutive rows differ in topic.
        interleaved = []
        max_len = max(len(va) for va in variants_per_arc)
        for i in range(max_len):
            for va in variants_per_arc:
                if i < len(va):
                    interleaved.append(va[i])

        # ---- safe conversations ----
        got = 0
        for variant in interleaved:
            if got >= n_safe:
                break
            key = flatten(variant)
            if key in seen_convs:
                continue
            seen_convs.add(key)
            rows.append((cat, variant, "none", 1))
            got += 1
        if got < n_safe:
            raise RuntimeError(f"{cat}: only {got}/{n_safe} unique safe conversations")

        # ---- unsafe conversations ----
        # Prefix variants for modules: use each arc's variants rotated.
        prefix_variants = [v for va in variants_per_arc for v in va]

        student_mods = pick_modules(student_pool, pref_student.get(cat, []), n_student, cat_idx)
        ai_mods = pick_modules(ai_pool, pref_ai.get(cat, []), n_ai, cat_idx)

        for instance in range(n_student):
            mid = student_mods[instance]
            conv = build_unsafe_conv(student_pool[mid], student_pool, cat_idx, instance, prefix_variants)
            key = flatten(conv)
            if key in seen_convs:
                conv = build_unsafe_conv(student_pool[mid], student_pool, cat_idx, instance + 7, prefix_variants)
                key = flatten(conv)
                assert key not in seen_convs, f"{cat}/{mid} duplicate"
            seen_convs.add(key)
            rows.append((cat, conv, "student", 0))
            student_driven += 1

        for instance in range(n_ai):
            mid = ai_mods[instance]
            conv = build_unsafe_conv(ai_pool[mid], ai_pool, cat_idx, instance, prefix_variants)
            key = flatten(conv)
            if key in seen_convs:
                conv = build_unsafe_conv(ai_pool[mid], ai_pool, cat_idx, instance + 7, prefix_variants)
                key = flatten(conv)
                assert key not in seen_convs, f"{cat}/{mid} duplicate"
            seen_convs.add(key)
            rows.append((cat, conv, "assistant", 0))
            ai_driven += 1
        total_unsafe += n_unsafe

    assert len(rows) == TOTAL, len(rows)
    assert total_unsafe == UNSAFE_TOTAL
    assert student_driven + ai_driven == UNSAFE_TOTAL

    rng = random.Random(42)
    rng.shuffle(rows)

    out_path = ROOT / "data-multi.tsv"
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, delimiter="\t", lineterminator="\n")
        writer.writerow(HEADER)
        for i, (cat, variant, trigger, is_safe) in enumerate(rows, start=1):
            flat = [msg for pair in variant for msg in pair]
            for msg in flat:
                assert "\t" not in msg and "\n" not in msg and msg.strip()
                assert not re.search(r"{\w+}", msg), msg
            writer.writerow([f"MREQ-{i:04d}", cat, LANGUAGE] + flat + [trigger, is_safe])

    print(f"wrote {len(rows)} rows to {out_path}")
    print(f"unsafe: {total_unsafe} (student-driven {student_driven}, assistant-driven {ai_driven}), safe: {TOTAL - UNSAFE_TOTAL}")
    per_cat = {}
    for cat, _, _, is_safe in rows:
        per_cat.setdefault(cat, [0, 0])
        per_cat[cat][0 if is_safe else 1] += 1
    cats_sorted = sorted(per_cat.items(), key=lambda kv: kv[0])
    print("per-category (safe, unsafe):", {c: tuple(v) for c, v in cats_sorted})


if __name__ == "__main__":
    sys.exit(main())
