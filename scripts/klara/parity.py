"""Compare two native PyTorch logits with TEI and/or a Transformers.js fixture probe."""

import argparse
import json
import subprocess
from pathlib import Path

import torch
from backends import request_json
from common import read_tsv, require
from training import transcript
from transformers import AutoModelForSequenceClassification, AutoTokenizer


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--hf", type=Path, required=True)
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--endpoint")
    p.add_argument("--browser", type=Path, help="local transformers.js model folder")
    p.add_argument(
        "--tolerance", type=float, default=0.08, help="absolute per-logit tolerance"
    )
    p.add_argument("--browser-tolerance", type=float, default=0.35)
    a = p.parse_args()
    require(a.endpoint or a.browser, "specify a serving path")
    texts = []
    lengths = set()
    for row in read_tsv(a.data):
        if row["turns"] not in lengths:
            texts.append(transcript(row))
            lengths.add(row["turns"])
    require(texts, "no fixture rows")
    t = AutoTokenizer.from_pretrained(a.hf)
    model = AutoModelForSequenceClassification.from_pretrained(
        a.hf, dtype=torch.float32, attn_implementation="eager"
    ).eval()
    with torch.no_grad():
        ref = [
            model(**t(text, return_tensors="pt")).logits[0].tolist() for text in texts
        ]

    def compare(name, actual, tolerance):
        measured, expected = torch.tensor(actual), torch.tensor(ref)
        require(measured.shape == expected.shape, f"{name}: shape mismatch")
        error = (measured - expected).abs().max().item()
        print(
            json.dumps(
                {
                    "backend": name,
                    "count": len(ref),
                    "max_abs_error": error,
                    "example_reference": ref[0],
                    "example_served": actual[0],
                }
            ),
            flush=True,
        )
        require(error <= tolerance, f"{name}: logit tolerance exceeded")

    if a.endpoint:
        require(
            request_json(a.endpoint + "/info", 30)["model_id"] == str(a.hf.resolve()),
            "wrong TEI checkpoint",
        )
        actual = []
        for text in texts:
            response = request_json(
                a.endpoint + "/predict",
                60,
                {"inputs": text, "raw_scores": True, "truncate": False},
            )
            scores = {r["label"]: r["score"] for r in response}
            actual.append(
                [
                    scores[model.config.id2label[i]]
                    for i in range(model.config.num_labels)
                ]
            )
        compare("tei", actual, a.tolerance)
    if a.browser:
        result = subprocess.run(
            [
                "node",
                str(Path(__file__).with_name("browser_logits.cjs")),
                str(a.browser),
            ],
            input=json.dumps(texts),
            text=True,
            capture_output=True,
            check=False,
        )
        require(result.returncode == 0, result.stderr)
        compare("transformers.js", json.loads(result.stdout), a.browser_tolerance)


if __name__ == "__main__":
    main()
