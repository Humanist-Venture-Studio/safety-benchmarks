"""Export a tuned ModernBERT binary head for Transformers.js with dynamic axes."""

import argparse
import tempfile
from pathlib import Path

import onnx
import torch
from common import require
from onnxruntime.quantization import QuantType, quantize_dynamic
from onnxruntime.transformers.float16 import convert_float_to_float16
from training import MODELS
from transformers import AutoModelForSequenceClassification, AutoTokenizer


class BrowserEncoder(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, input_ids, attention_mask):
        # ONNX supports broadcast arithmetic directly; HF's generic vmap mask builder is not traceable.
        m = self.model
        pos = torch.arange(input_ids.shape[1])
        valid = attention_mask[:, None, None, :].bool()
        local = (pos[:, None] - pos[None, :]).abs() <= m.config.sliding_window
        masks = {
            k: torch.where(v, 0.0, torch.finfo(torch.float32).min)
            for k, v in (
                ("full_attention", valid),
                ("sliding_attention", valid & local),
            )
        }
        hidden = m.model(input_ids=input_ids, attention_mask=masks).last_hidden_state
        pooled = (hidden * attention_mask.unsqueeze(-1)).sum(1) / attention_mask.sum(
            1, keepdim=True
        )
        return m.classifier(m.head(pooled))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--hf", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--dtype", choices=("q8", "fp16"), default="q8")
    a = p.parse_args()
    require(
        a.out.resolve().is_relative_to(MODELS.resolve()), "use the task model directory"
    )
    model = AutoModelForSequenceClassification.from_pretrained(
        a.hf, dtype=torch.float32, attn_implementation="eager"
    ).eval()
    require(
        model.config.model_type == "modernbert"
        and model.config.classifier_pooling == "mean",
        "expected mean-pooled ModernBERT",
    )
    tok = AutoTokenizer.from_pretrained(a.hf)
    a.out.mkdir(exist_ok=False, parents=True)
    dest = a.out / "onnx"
    dest.mkdir()
    model.config.save_pretrained(a.out)
    tok.save_pretrained(a.out)
    x = tok("Fixture text used to trace dynamic input dimensions.", return_tensors="pt")
    wrapper = BrowserEncoder(model).eval()
    with torch.no_grad(), tempfile.TemporaryDirectory(dir=a.out) as tmp:
        torch.testing.assert_close(
            wrapper(x.input_ids, x.attention_mask), model(**x).logits
        )
        graph = str(Path(tmp) / "model.onnx")
        torch.onnx.export(
            wrapper,
            (x.input_ids, x.attention_mask),
            graph,
            dynamo=False,
            opset_version=18,
            input_names=["input_ids", "attention_mask"],
            output_names=["logits"],
            dynamic_axes={
                "input_ids": {0: "batch", 1: "sequence"},
                "attention_mask": {0: "batch", 1: "sequence"},
                "logits": {0: "batch"},
            },
        )
        if a.dtype == "q8":
            quantize_dynamic(
                graph,
                str(dest / "model_quantized.onnx"),
                per_channel=True,
                weight_type=QuantType.QInt8,
            )
        else:
            graph16 = convert_float_to_float16(onnx.load(graph), keep_io_types=True)
            onnx.save(graph16, dest / "model_fp16.onnx")
    size = sum(path.stat().st_size for path in a.out.rglob("*") if path.is_file())
    require(size <= 250_000_000, f"browser artifact exceeds spark tier: {size} bytes")
    print(f"browser package {size} bytes")


if __name__ == "__main__":
    main()
