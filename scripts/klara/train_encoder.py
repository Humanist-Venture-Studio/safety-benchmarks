"""Fit a full binary encoder or a frozen-backbone probe; export for TEI."""

import json
from pathlib import Path

import torch
from torch.nn import functional as F
from training import fit, options, prepare
from transformers import AutoConfig, AutoModelForSequenceClassification, AutoTokenizer


def main():
    p = options(__doc__)
    p.add_argument(
        "--precision",
        choices=("fp32", "fp16"),
        default="fp32",
        help="forward precision with FP32 optimizer weights",
    )
    p.add_argument("--probe", action="store_true")
    p.add_argument(
        "--init-checkpoint", type=Path, help="first-round binary head and backbone"
    )
    a = p.parse_args()
    rows = prepare(a)
    tokenizer = AutoTokenizer.from_pretrained(a.source, local_files_only=True)
    weights = a.init_checkpoint or a.source
    config = AutoConfig.from_pretrained(weights)
    config.id2label = {0: "safe", 1: "unsafe"}
    config.label2id = {"safe": 0, "unsafe": 1}
    config.problem_type = "single_label_classification"
    model = AutoModelForSequenceClassification.from_pretrained(
        weights,
        config=config,
        ignore_mismatched_sizes=True,
        dtype=torch.float32,
        attn_implementation="eager",
    )
    if a.probe:
        model.requires_grad_(False)
        model.classifier.requires_grad_(True)
    model.to(a.device)

    def forward(x, y):
        with torch.autocast(
            a.device, dtype=torch.float16, enabled=a.precision == "fp16"
        ):
            logits = model(**x).logits
        return logits, F.cross_entropy(logits.float(), y, reduction="none")

    fit(model, tokenizer, lambda text: tokenizer(text)["input_ids"], forward, rows, a)
    dest = a.out / "hf"
    model.eval().to(device="cpu", dtype=torch.float16).save_pretrained(dest)
    tokenizer.save_pretrained(dest)
    path = dest / "config.json"
    cfg = json.loads(path.read_text())
    cfg["num_labels"] = 2
    if cfg["model_type"] == "modernbert":
        for scope, layer in (
            ("global", "full_attention"),
            ("local", "sliding_attention"),
        ):
            cfg[f"{scope}_rope_theta"] = model.config.rope_parameters[layer][
                "rope_theta"
            ]
    path.write_text(json.dumps(cfg, indent=2))


if __name__ == "__main__":
    main()
