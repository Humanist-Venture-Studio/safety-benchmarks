"""Pin the full input and the undecoded split projection used by a real tier run."""

import hashlib
import json
from pathlib import Path

from common import WORK, atomic_text, require

FINAL_SHA256 = "0ff32b946a2e83760e90ce0974c73cedff23a6b8cbd9bd766cef155744caf294"


def digest(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def prepare(directory, source=None, expected=FINAL_SHA256):
    source = source or WORK / "data/data-klara.tsv"
    require(digest(source) == expected, "full dataset SHA-256 mismatch")
    directory.mkdir(parents=True, exist_ok=True)
    projection = directory / "development.tsv"
    stream_hash = hashlib.sha256()
    with source.open("rb") as rows, atomic_text(projection, replace=False) as out:
        header = next(rows)
        stream_hash.update(header)
        out.write(header.decode())
        for line in rows:
            stream_hash.update(line)
            if line.startswith((b"train\t", b"validation\t"), line.index(b"\t") + 1):
                out.write(line.decode())
        require(stream_hash.hexdigest() == expected, "dataset changed during projection")
    with atomic_text(directory / "dataset.json", replace=False) as out:
        json.dump(dict(source_sha256=expected, development_sha256=digest(projection)), out)
        out.write("\n")


def verify(directory, source=None, expected=FINAL_SHA256):
    source = source or WORK / "data/data-klara.tsv"
    record = json.loads((directory / "dataset.json").read_bytes())
    require(digest(source) == record["source_sha256"] == expected, "full dataset SHA-256 mismatch")
    require(digest(directory / "development.tsv") == record["development_sha256"],
            "development projection SHA-256 mismatch")
    return record


def verify_input(path):
    if path.name == "development.tsv" and (path.parent / "dataset.json").is_file():
        verify(path.parent)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "verify"])
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    (prepare if args.action == "prepare" else verify)(args.directory)
