"""Validate one written shard against its slots and all available writer output."""
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

from common import jsonl, require
from similarity import matches, normalize, transcript


def validate_messages(messages, turns):
    require(isinstance(messages, list) and len(messages) == 2 * turns, f"expected {turns} student/tutor pairs")
    for i, msg in enumerate(messages):
        role = ("student", "tutor")[i % 2]
        require(isinstance(msg, dict) and msg.get("role") == role, f"message {i + 1}: expected {role}")
        content = msg.get("content")
        require(isinstance(content, str) and content.strip(), f"message {i + 1}: empty content")
        require(len(content) <= 4000, f"message {i + 1}: exceeds 4,000 characters")
        require("\t" not in content and len(content.splitlines(keepends=True)) == 1
                and content == content.splitlines()[0], f"message {i + 1}: tab or line break")


def read_written(path, slots, errors, complete):
    messages = {}
    seen = set()
    with path.open(encoding="utf-8") as src:
        for i, line in enumerate(src, 1):
            key = f"{path.name}@{i}"
            try:
                r = json.loads(line)
                require(isinstance(r, dict) and isinstance(r.get("row_id"), str), "expected object with row_id")
                key = r["row_id"]
                require(key not in seen, "duplicate row_id")
                seen.add(key)
                require(key in slots, "unexpected row_id")
                slot = slots[key]
                for field in slot.keys() & r.keys():
                    require(r[field] == slot[field] and type(r[field]) is type(slot[field]),
                            f"changed slot field {field}")
                validate_messages(r.get("messages"), slot["turns"])
                messages[key] = r["messages"]
            except ValueError as exc:
                errors[key].add(str(exc))
    if complete:
        for key in slots.keys() - seen:
            errors[key].add("missing row_id")
    return messages


def check_files(paths, targets, canonical=None):
    errors = defaultdict(set)
    all_messages = {}
    focus = set()
    corpus_openers = defaultdict(list)
    for path in paths:
        target = path in targets
        name = path.name.replace(".written.jsonl", ".slots.jsonl")
        rows = list(jsonl(path.with_name(name)))
        slots = {r["row_id"]: r for r in rows}
        require(len(slots) == len(rows) == 400, f"{name}: expected 400 unique slots")
        shard = int(path.name[6:8])
        require(all(r["shard"] == shard for r in rows), f"{name}: wrong shard")
        require(not all_messages.keys() & slots.keys(), f"{name}: IDs shared by shards")
        if canonical is not None:
            for key, slot in slots.items():
                require(key in canonical and all(slot.get(k) == v for k, v in canonical[key].items()),
                        f"{name}: {key} disagrees with master manifest")
        local_errors = defaultdict(set)
        messages = read_written(path, slots, local_errors, complete=target)
        openers = defaultdict(list)
        for key, msgs in messages.items():
            prefix = tuple(re.findall(r"\w+", normalize(msgs[0]["content"]))[:8])
            openers[prefix].append(key)
            corpus_openers[prefix].append(key)
        if target:
            for key, reasons in local_errors.items():
                errors[key].update(reasons)
            focus.update(slots)
            for group in openers.values():
                if len(group) > 4:
                    for key in group:
                        errors[key].add(f"first eight words repeated {len(group)} times in shard")
        else:
            # In-progress peers may lack rows. Never certify a check with unreadable peers.
            for key, reasons in local_errors.items():
                errors[f"{path.name}/{key}"].update(reasons)
        all_messages.update(messages)
    for group in corpus_openers.values():
        if len(group) > 25:
            for key in focus.intersection(group):
                errors[key].add(f"first eight words repeated {len(group)} times across written rows")
    docs = {k: transcript(v) for k, v in all_messages.items()}
    for a, b, score in matches(docs, lambda a, b: a in focus or b in focus):
        kind = "duplicate" if docs[a] == docs[b] else "near-duplicate"
        for key, peer in ((a, b), (b, a)):
            if key in focus:
                errors[key].add(f"{kind} of {peer} (Jaccard {score:.3f})")
    for key, reasons in sorted(errors.items()):
        print(f"{key}\t{' | '.join(sorted(reasons))}")
    print(f"expected={len(focus)} structurally_valid={len(focus & all_messages.keys())} "
          f"compared={len(all_messages)} rejected_ids_or_lines={len(errors)}")
    return all_messages, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("written", type=Path)
    path = parser.parse_args().written.resolve()
    require(re.fullmatch(r"shard-(0[1-9]|1\d|2[0-5])\.written\.jsonl", path.name) and path.is_file(),
            "expected shard-NN.written.jsonl (01..25)")
    paths = sorted(path.parent.glob("shard-[0-9][0-9].written.jsonl"))
    _, errors = check_files(paths, {path})
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
