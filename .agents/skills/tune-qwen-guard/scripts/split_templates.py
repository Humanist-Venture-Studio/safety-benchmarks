#!/usr/bin/env python3
"""Reproduce generator provenance and make a deterministic template hold-out.

Standard library only. Reads sibling data.tsv for the original category order.
Never calls a model. Generator writes are intercepted in memory; bytecode is off.
Template IDs identify source file, dictionary/category, and zero-based arc index.
Near-copy groups use slot-normalized wording, all message alternatives, and
transitive union (see template_groups). Output is a NEW file, never overwritten.
"""
import argparse
import builtins
from collections import Counter, defaultdict
from contextlib import redirect_stdout
import csv
import hashlib
import importlib.util
import io
import math
import json
from pathlib import Path
import random
import re
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
TURNS = tuple(f'turn{i}_{role}' for i in range(1, 5) for role in ('request', 'response'))
SEED = 20261111


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Variant(list):
    def __init__(self, values, arc_id='', module_id=''):
        super().__init__(values)
        self.arc_id, self.module_id = arc_id, module_id


def replay(data, scripts):
    """Run the real generation algorithms; attach provenance without changing text."""
    catalog, object_ids, captured = {}, {}, []
    # Keep references so object IDs cannot be recycled between module loads.
    modules = []

    def source_loader(path):
        mod = load(path)
        modules.append(mod)
        for category, arcs in getattr(mod, 'ARCS', {}).items():
            for index, arc in enumerate(arcs):
                key = f'{path.name}:ARCS:{category}:{index}'
                object_ids[id(arc)] = key
                catalog[key] = dict(kind='arc', source=path.name, category=category, index=index, template=arc)
        for attr in ('STUDENT_MODULES', 'STUDENT_MODULES2', 'AI_MODULES', 'AI_MODULES2'):
            for name, module in getattr(mod, attr, {}).items():
                key = f'{path.name}:{attr}:{name}'
                object_ids[id(module)] = key
                catalog[key] = dict(kind='module', source=path.name, category='', index=name, template=module)
        return mod

    class CaptureRandom(random.Random):
        def shuffle(self, rows):
            super().shuffle(rows)
            captured[:] = rows

    def blocked_open(path, mode='r', *args, **kwargs):
        if any(c in mode for c in 'wax+'):
            if Path(path).name != 'data-multi.tsv':
                raise RuntimeError(f'unexpected generator write: {path}')
            return io.StringIO()
        return builtins.open(path, mode, *args, **kwargs)

    def setup(g):
        g.ROOT, g.SCRIPTS = data.parent, scripts
        g.load_module = source_loader
        g.random = SimpleNamespace(Random=CaptureRandom)
        g.open = blocked_open

    first = load(scripts / 'gen_multi.py')
    setup(first)
    original_variants = first.arc_variants
    first.arc_variants = lambda arc: [Variant(v, object_ids[id(arc)]) for v in original_variants(arc)]
    original_unsafe = first.build_unsafe_conv

    def unsafe1(module, pool, cat_idx, instance, prefixes):
        result = original_unsafe(module, pool, cat_idx, instance, prefixes)
        arc = prefixes[(cat_idx + instance) % len(prefixes)].arc_id if module['start'] > 1 else ''
        return Variant(result, arc, object_ids[id(module)])

    first.build_unsafe_conv = unsafe1
    with redirect_stdout(io.StringIO()):
        first.main()
    old = list(captured)
    existing, metadata = [], {}
    for i, (cat, conv, trigger, safe) in enumerate(old, 1):
        rid = f'MREQ-{i:04d}'
        flat = [m for pair in conv for m in pair]
        existing.append([rid, cat, 'en', *flat, trigger, str(safe)])
        metadata[rid] = dict(arc_id=conv.arc_id, module_id=conv.module_id, raw=flat)

    # gen_multi_v2 imports realism by name, so select only the requested directory.
    sys.path.insert(0, str(scripts))
    sys.modules['realism'] = load(scripts / 'realism.py')
    second = load(scripts / 'gen_multi_v2.py')
    setup(second)
    second.read_existing = lambda: existing
    for name in ('old_arc_variants', 'new_arc_variants'):
        original = getattr(second, name)
        setattr(second, name, lambda arc, fn=original: [Variant(v, object_ids[id(arc)]) for v in fn(arc)])
    original_unsafe2 = second.build_unsafe_conv

    def unsafe2(module, cat_idx, instance, prefixes):
        result = original_unsafe2(module, cat_idx, instance, prefixes)
        arc = prefixes[(cat_idx * 11 + instance * 7) % len(prefixes)].arc_id if module['start'] > 1 else ''
        return Variant(result, arc, object_ids[id(module)])

    second.build_unsafe_conv = unsafe2
    with redirect_stdout(io.StringIO()):
        second.main()
    generated = list(existing)
    for i, (cat, conv, trigger, safe) in enumerate(captured, len(existing) + 1):
        rid = f'MREQ-{i:04d}'
        flat = list(conv)
        generated.append([rid, cat, 'en', *flat, trigger, str(safe)])
        metadata[rid] = dict(arc_id=conv.arc_id, module_id=conv.module_id, raw=flat)
    generated = {r[0]: [*r[:3], *second.realism_row(r[3:11], r[0]), *r[11:]] for r in generated}
    with data.open(encoding='utf-8', newline='') as f:
        actual = list(csv.DictReader(f, delimiter='\t'))
    if len({r['request_id'] for r in actual}) != len(actual):
        raise ValueError('duplicate request_id')
    for row in actual:
        rid = row['request_id']
        expected = generated.get(rid)
        text_ok = expected is not None and expected[3:11] == [row[t] for t in TURNS]
        meta_ok = expected is not None and (expected[1], expected[11], expected[12]) == (row['category'], row['trigger_source'], row['is_safe'])
        info = metadata.setdefault(rid, dict(arc_id='', module_id='', raw=[]))
        info['exact'] = text_ok
        info['verified'] = text_ok and meta_ok
        # Fail closed on any input drift. This dataset needs no approximate fallback.
        # An unverified row's proposed IDs are removed rather than treated as evidence.
        if not info['verified']:
            info['arc_id'] = info['module_id'] = ''
    return actual, metadata, catalog


def normalise(text):
    return ' '.join(re.sub(r'[^a-z0-9]+', ' ', text.lower()).split())


def shingles(text):
    words = normalise(re.sub(r'\{[^}]+\}', ' SLOT ', text)).split()
    return {' '.join(words[i:i + 3]) for i in range(max(1, len(words) - 2))}


def template_groups(catalog):
    """Group textual near copies, including copies across safe/module kinds.

    All alternative phrasings participate. Slot names/values do not count as
    distinct wording. Union if trigram Jaccard >= .50, or shorter-text containment
    >= .80 with size ratio >= .50, or >= 75% of shorter template messages match
    alternatives at Jaccard >= .80 (at least 4 messages). Position independent to
    catch modules duplicating an arc's suffix. These lexical thresholds do not
    claim to detect every semantic paraphrase.
    """
    ids = sorted(catalog)
    parent = {k: k for k in ids}
    def root(k):
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k
    features, messages = {}, {}
    for k in ids:
        msgs = []
        for pair in catalog[k]['template']['turns']:
            for msg in pair:
                options = msg if isinstance(msg, list) else [msg]
                msgs.append([shingles(o) for o in options])
        messages[k] = msgs
        features[k] = set().union(*(s for m in msgs for s in m))
    # Inverted candidate index avoids comparing template pairs with no trigrams.
    index = defaultdict(list)
    pairs = set()
    for k in ids:
        for gram in sorted(features[k]):
            pairs.update((old, k) for old in index[gram])
            index[gram].append(k)
    edges = []
    for a, b in sorted(pairs):
        fa, fb = features[a], features[b]
        shared = len(fa & fb)
        j = shared / len(fa | fb)
        containment = shared / min(len(fa), len(fb))
        ratio = min(len(fa), len(fb)) / max(len(fa), len(fb))
        reason = 'jaccard' if j >= .5 else 'containment' if containment >= .8 and ratio >= .5 else ''
        matches = 0
        if not reason and shared >= 8:
            left, right = sorted((messages[a], messages[b]), key=len)
            if len(left) >= 4:
                # Maximum bipartite matching: repeated short closers count once.
                adj = [[i for i, mb in enumerate(right) if any(len(x & y) / len(x | y) >= .8 for x in ma for y in mb)] for ma in left]
                assigned = {}
                def augment(i, seen):
                    for other in adj[i]:
                        if other in seen:
                            continue
                        seen.add(other)
                        if other not in assigned or augment(assigned[other], seen):
                            assigned[other] = i
                            return True
                    return False
                matches = sum(augment(i, set()) for i in range(len(left)))
                if matches >= 4 and matches / len(left) >= .75:
                    reason = 'message_matches'
        if reason:
            ra, rb = root(a), root(b)
            parent[max(ra, rb)] = min(ra, rb)
            edges.append(dict(a=a, b=b, jaccard=j, containment=containment, matching_messages=matches, reason=reason))
    groups = {k: root(k) for k in ids}
    return groups, edges


def choose_split(rows, metadata, groups):
    """Fixed-seed, text/provenance-only partition with template-count quotas.

    In each stratum (old/new arcs and student/assistant modules), reserve 25%
    of active template groups for test and 10% for validation. Swaps preserve
    these quotas, preventing exclusion minimization from assigning practically
    all modules to train. Minimize excluded rows plus eight times absolute row
    deviation from test=2500, validation=1000. Trigger-source row targets are 25%/10% of the source's 1260 student and
    1240 assistant module rows (315/126 and 310/124). This is stratification;
    no consensus ratings enter that objective.
    Four seeded restarts, each 40000 swaps, at a fixed cooling schedule.
    Only the required class/trigger presence is checked using labels.
    """
    row_keys = {}
    weighted = Counter()
    for row in rows:
        m = metadata[row['request_id']]
        keys = tuple(sorted({groups[m[k]] for k in ('arc_id', 'module_id') if m[k]})) if m['verified'] else ()
        row_keys[row['request_id']] = keys
        if keys:
            weighted[(keys, row["trigger_source"])] += 1
    nodes = sorted({k for keys, _ in weighted for k in keys})
    indices = {k: i for i, k in enumerate(nodes)}
    edges = [(tuple(indices[k] for k in keys), count, {"none":0,"student":4,"assistant":8}[role]) for (keys, role), count in sorted(weighted.items())]
    adjacent = [set() for _ in nodes]
    for e, (keys, _, _) in enumerate(edges):
        for k in keys:
            adjacent[k].add(e)
    def stratum(key):
        members = [k for k, g in groups.items() if g == key]
        kinds = set()
        for m in members:
            if ':ARCS:' in m:
                part = int(re.search(r'part(\d+)', m)[1])
                kinds.add('arc:old' if part <= 6 else 'arc:new')
            else:
                kinds.add('module:student' if ':STUDENT_' in m else 'module:assistant')
        return '+'.join(sorted(kinds))
    strata = defaultdict(list)
    for k in nodes:
        strata[stratum(k)].append(indices[k])
    strata = dict(sorted(strata.items()))
    def state(keys, labels):
        s = labels[keys[0]]
        return s if all(labels[k] == s for k in keys[1:]) else 3
    def cost(counts):
        return counts[3] + 8 * (abs(counts[1] - 1000) + abs(counts[2] - 2500) + sum(abs(counts[offset+s] - target) for offset,s,target in ((4,1,126),(4,2,315),(8,1,124),(8,2,310))))
    best, candidates = None, []
    quota = {}
    for restart in range(4):
        rng = random.Random(SEED + restart)
        labels = [0] * len(nodes)
        for name, values in strata.items():
            values = list(values)
            rng.shuffle(values)
            nt, nv = round(len(values) * .25), round(len(values) * .10)
            for k in values[:nt]:
                labels[k] = 2
            for k in values[nt:nt+nv]:
                labels[k] = 1
            quota[name] = dict(train=len(values)-nt-nv, validation=nv, test=nt)
        counts = [0, 0, 0, sum(not row_keys[r['request_id']] for r in rows)] + [0] * 8
        for keys, n, offset in edges:
            st = state(keys, labels)
            counts[st] += n
            if offset:
                counts[offset+st] += n
        score = cost(counts)
        local_best = (score, counts[3], tuple(labels), tuple(counts))
        pools = [v for v in strata.values() if len(v) >= 2]
        for step in range(40000):
            pool = pools[rng.randrange(len(pools))]
            a, b = rng.sample(pool, 2)
            if labels[a] == labels[b]:
                continue
            changed = adjacent[a] | adjacent[b]
            delta = [0] * 12
            for e in changed:
                keys, n, offset = edges[e]
                st = state(keys, labels)
                delta[st] -= n
                if offset:
                    delta[offset+st] -= n
            labels[a], labels[b] = labels[b], labels[a]
            for e in changed:
                keys, n, offset = edges[e]
                st = state(keys, labels)
                delta[st] += n
                if offset:
                    delta[offset+st] += n
            next_counts = [c + d for c, d in zip(counts, delta)]
            next_score = cost(next_counts)
            temperature = 16 * (0.02 ** (step / 40000))
            if next_score <= score or rng.random() < math.exp((score-next_score)/temperature):
                counts, score = next_counts, next_score
                rank = (score, counts[3], tuple(labels), tuple(counts))
                if rank < local_best:
                    local_best = rank
            else:
                labels[a], labels[b] = labels[b], labels[a]
        candidates.append(local_best)
    names = ('train', 'validation', 'test', 'excluded')
    for candidate in sorted(candidates):
        labels = candidate[2]
        assignment = {rid: names[state(tuple(indices[k] for k in keys), labels)] if keys else 'excluded' for rid, keys in row_keys.items()}
        presence = {s: set() for s in names}
        triggers = {s: set() for s in names}
        for row in rows:
            s = assignment[row['request_id']]
            presence[s].add(row['consensus_rating'])
            triggers[s].add(row['trigger_source'])
        if all(presence[s] == {'SAFE', 'FLAGGED', 'UNSAFE'} and {'student', 'assistant'} <= triggers[s] for s in names[:3]):
            best = candidate
            break
    if best is None:
        raise ValueError('No partition meets class/trigger presence; no output written')
    # Verify actual template groups are disjoint across all three retained splits.
    owners = {}
    for row in rows:
        rid = row['request_id']
        s = assignment[rid]
        if s == 'excluded':
            continue
        for k in row_keys[rid]:
            if owners.setdefault(k, s) != s:
                raise AssertionError(f'template group crosses split: {k}')
    info = dict(seed=SEED, objective=best[0], counts=dict(zip(names,best[3])),
                template_group_quotas=quota, template_group_assignment={k:names[best[2][i]] for i,k in enumerate(nodes)},
                restarts=4, swap_steps_per_restart=40000,
                row_targets=dict(test=2500,validation=1000,test_student=315,test_assistant=310,validation_student=126,validation_assistant=124),
                labels_used_only_for='trigger-source stratification; SAFE/FLAGGED/UNSAFE presence in retained splits')
    return assignment, info


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, default=Path('data-multi.tsv'))
    p.add_argument('--scripts', type=Path, default=Path('scripts'))
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--details', type=Path, help='optional NEW JSON with provenance, groups and selection metadata')
    args = p.parse_args()
    rows, metadata, catalog = replay(args.data.resolve(), args.scripts.resolve())
    print(f'Reproduced {sum(m["exact"] for m in metadata.values())}/{len(rows)} rows exactly', flush=True)
    groups, edges = template_groups(catalog)
    print(f'{len(catalog)} templates; {len(set(groups.values()))} groups; {len(edges)} near-copy edges', flush=True)
    assignments, selection = choose_split(rows, metadata, groups)
    if args.details:
        with args.details.open('x') as f:
            json.dump(dict(metadata=metadata, catalog=catalog, groups=groups, edges=edges, selection=selection), f, sort_keys=True)
    with args.output.open('x', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(('request_id', 'split', 'arc_id', 'module_id'))
        for row in rows:
            rid = row['request_id']
            m = metadata[rid]
            w.writerow((rid, assignments.get(rid, 'excluded'), m['arc_id'], m['module_id']))


if __name__ == '__main__':
    main()
