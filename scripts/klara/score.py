"""Score one JSON conversation on stdin (or --input)."""
import argparse
import json
import sys
from pathlib import Path

from backends import Backend, backend_args
from check_shard import validate_messages
from common import require


def main():
    p = argparse.ArgumentParser(description=__doc__)
    backend_args(p)
    p.add_argument("--input", type=Path)
    args = p.parse_args()
    require(args.tier, "specify --tier")
    obj = json.loads(args.input.read_text(encoding="utf-8")) if args.input else json.load(sys.stdin)
    messages = obj.get("messages") if isinstance(obj, dict) else obj
    require(isinstance(messages, list) and 2 <= len(messages) <= 10, "expected 1..5 student/tutor pairs")
    validate_messages(messages, len(messages) // 2)
    contract, _, error, _ = Backend(args).score(messages)
    if error:
        raise SystemExit(f"scoring failed: {error}")
    print(json.dumps(contract, allow_nan=False))


if __name__ == "__main__":
    main()
