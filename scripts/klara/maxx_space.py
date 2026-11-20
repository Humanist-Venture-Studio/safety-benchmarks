"""Reserve space before each large Maxx allocation and retire refetchable source shards."""

import json
import shutil
import subprocess

from common import WORK, require

PINS = {
    "phi4": ("microsoft/Phi-4-mini-instruct", "cfbefacb99257ffa30c83adab238a50856ac3083"),
    "qguard8": ("Qwen/Qwen3Guard-Gen-8B", "4505cb1a6f1864f21f8b27f7daf1b9a1aab6edbb"),
    "q35-4": ("Qwen/Qwen3.5-4B", "851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a"),
}
CANDIDATES = ("phi4", "qguard8")
LIMIT = 50_000_000_000


def source_weights(src):
    root = WORK / "models/tier-proof"
    require(src == root / src.parent.name / "source" and src == src.resolve(), "unexpected source path")
    pin = PINS[src.parent.name]
    saved = json.loads((src.parent / "source.json").read_bytes())
    require((saved["id"], saved["rev"]) == pin, "upstream revision mismatch")
    return sorted(src.glob("*.safetensors"), key=lambda p: -p.stat().st_size)


def reserve(amount, phase, evict=None):
    """evict is passed only after the converter has finished consuming upstream weights."""
    spare = 250_000_000
    purgeable = source_weights(evict) if evict else []
    while True:
        used = int(subprocess.check_output(["du", "-sk", WORK]).split()[0]) * 1024
        free = shutil.disk_usage(WORK).free
        ok = used + amount + spare <= LIMIT and free >= amount + spare
        row = dict(phase=phase, allocated=used, free=free, reserve=amount)
        if not ok and purgeable:
            path = purgeable.pop(0)
            require(path.is_file() and path == path.resolve(), "expected a pinned source shard")
            row["evicted_source"] = str(path.relative_to(WORK))
            path.unlink()
        with (WORK / "logs/maxx/space.jsonl").open("a") as f:
            print(json.dumps(row), file=f)
        if ok:
            return
        require("evicted_source" in row, f"insufficient space during {phase}: {row}")
