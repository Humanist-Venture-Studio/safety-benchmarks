"""Restore only missing files from the pinned preflight checkpoint, without a second cache."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
import subprocess
import time
import urllib.request

from common import WORK, require
from maxx_space import PINS, reserve, source_weights

TOKENIZER_FILES = {"config.json", "tokenizer_config.json", "tokenizer.json", "merges.txt",
                   "vocab.json", "special_tokens_map.json", "added_tokens.json",
                   "preprocessor_config.json", "generation_config.json", "processor_config.json",
                   "tokenizer.model", "chat_template.json", "LICENSE", "README.md"}


def fetch(model):
    name, rev = PINS[model]
    folder = WORK / "models/tier-proof" / model / "source"
    source_weights(folder)  # Check the preflight receipt before using or modifying this path.
    folder.mkdir(exist_ok=True)
    url = f"https://huggingface.co/api/models/{name}/revision/{rev}?blobs=true"
    with urllib.request.urlopen(url, timeout=60) as response:
        meta = json.load(response)
    require(meta["sha"] == rev, "pinned revision missing")
    for item in meta["siblings"]:
        filename = item["rfilename"]
        if "/" in filename or not (filename in TOKENIZER_FILES or
                filename.endswith((".safetensors", ".safetensors.index.json", ".jinja"))):
            continue
        path = folder / filename
        size = item["size"]
        if path.exists():
            require(path.stat().st_size == size, "cached source file size mismatch")
            continue
        part = path.with_suffix(path.suffix + ".part")
        part.unlink(missing_ok=True)
        reserve(size, "fetch " + filename)
        url = f"https://huggingface.co/{name}/resolve/{rev}/{filename}"
        print("fetch", model, rev, filename, size, flush=True)
        chunk = 32 * 1024**2
        if size < chunk:
            subprocess.run(["curl", "-fsSL", "--retry", "3", "--max-time", "240", "-o", part, url], check=True)
        else:
            with part.open("wb") as out:
                def download(start):
                    end = min(size, start + chunk) - 1
                    for attempt in range(4):
                        req = urllib.request.Request(url + f"?download=true&klara_chunk={start}",
                                                    headers={"Range": f"bytes={start}-{end}"})
                        try:
                            with urllib.request.urlopen(req, timeout=90) as src:
                                require(src.status == 206 and src.headers["Content-Range"] ==
                                        f"bytes {start}-{end}/{size}", "incorrect source range")
                                data = src.read(end - start + 2)
                            require(len(data) == end - start + 1, "truncated source range")
                            require(os.pwrite(out.fileno(), data, start) == len(data), "short write")
                            return
                        except OSError:
                            if attempt == 3:
                                raise
                            time.sleep(attempt + 1)
                with ThreadPoolExecutor(max_workers=16) as pool:
                    list(pool.map(download, range(0, size, chunk)))
        require(part.stat().st_size == size, "source size mismatch")
        if item.get("lfs"):
            with part.open("rb") as f:
                require(hashlib.file_digest(f, "sha256").hexdigest() == item["lfs"]["sha256"],
                        "upstream LFS checksum mismatch")
        part.rename(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", choices=PINS)
    fetch(parser.parse_args().model)
