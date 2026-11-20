"""Export a merged Spark chat candidate as a two-verdict Q8_0 ONNX graph."""

import argparse
import json
import tempfile
import time
from pathlib import Path

import gguf
import numpy as np
import onnx
import torch
from onnx import TensorProto, helper, numpy_helper
from peft import PeftModel
from transformers import AutoTokenizer
from backends import chat_prompt
from common import require
from train_chat import load_base
from training import MODELS


class VerdictHead(torch.nn.Module):
    def __init__(self, merged, ids):
        super().__init__()
        self.backbone = merged.model
        self.register_buffer(
            "verdict_weight",
            merged.get_output_embeddings().weight[ids].detach().clone(),
        )

    def forward(self, input_ids, attention_mask):
        positions = torch.arange(input_ids.shape[1])
        visible = (positions[:, None] >= positions[None, :]) & attention_mask[
            :, None, None, :
        ].bool()
        mask = torch.where(visible, 0.0, torch.finfo(torch.float32).min)
        last = self.backbone(
            input_ids=input_ids,
            attention_mask=mask,
            position_ids=positions[None],
            use_cache=False,
        ).last_hidden_state[:, -1]
        return torch.nn.functional.linear(last, self.verdict_weight)


def pack_matrices(graph):
    # Store the same signed blocks as GGUF. Standard ONNX ops unpack constant weights
    # when the inference session is optimized, without a custom JS kernel.
    consumers = {}
    for node in graph.node:
        for i, name in enumerate(node.input):
            consumers.setdefault(name, set()).add((node.op_type, i))
    ops = []
    count = 0
    for tensor in list(graph.initializer):
        if tensor.data_type != TensorProto.FLOAT or len(tensor.dims) != 2:
            continue
        name = tensor.name
        uses = consumers[name]
        matrix = numpy_helper.to_array(tensor)
        transposed = uses == {("MatMul", 1)}
        if not transposed and uses != {("Gather", 0)}:
            require(matrix.size < 4096, f"unexpected matrix consumer {uses}")
            continue
        weights = np.ascontiguousarray(matrix.T if transposed else matrix)
        blocks = gguf.quantize(weights, gguf.GGMLQuantizationType.Q8_0).reshape(-1, 34)
        scales = blocks[:, :2].copy().view(np.float16)
        codes = blocks[:, 2:].copy().view(np.int8)
        prefix = name + "/q8/"
        arrays = {
            "codes": codes,
            "scale": scales,
            "shape": np.array(weights.shape, dtype=np.int64),
        }
        del_index = list(graph.initializer).index(tensor)
        del graph.initializer[del_index]
        for key, array in arrays.items():
            graph.initializer.append(numpy_helper.from_array(array, prefix + key))
        for key in ("codes", "scale"):
            ops.append(
                helper.make_node(
                    "Cast", [prefix + key], [prefix + key + "f"], to=TensorProto.FLOAT
                )
            )
        ops.append(
            helper.make_node(
                "Mul", [prefix + "codesf", prefix + "scalef"], [prefix + "values"]
            )
        )
        ops.append(
            helper.make_node(
                "Reshape",
                [prefix + "values", prefix + "shape"],
                [prefix + "weight" if transposed else name],
            )
        )
        if transposed:
            ops.append(
                helper.make_node("Transpose", [prefix + "weight"], [name], perm=[1, 0])
            )
        count += 1
    original = list(graph.node)
    del graph.node[:]
    graph.node.extend(ops + original)
    return count


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    require(
        a.out.resolve().is_relative_to(MODELS.resolve()), "expected task model folder"
    )
    t = time.monotonic()
    recipe = json.loads((a.run / "chat.json").read_bytes())
    model = load_base(recipe["source"])
    if recipe["init_adapter"]:
        model = PeftModel.from_pretrained(
            model, recipe["init_adapter"]
        ).merge_and_unload()
    model = (
        PeftModel.from_pretrained(model, a.run / "adapter")
        .merge_and_unload(safe_merge=True)
        .float()
        .eval()
    )
    model.set_attn_implementation("eager")
    tok = AutoTokenizer.from_pretrained(recipe["source"])
    a.out.mkdir(parents=True, exist_ok=False)
    model.config.klara_verdict_ids = recipe["ids"]
    model.config.save_pretrained(a.out)
    tok.save_pretrained(a.out)
    graph_dir = a.out / "onnx"
    graph_dir.mkdir(exist_ok=False)
    encoded = tok(chat_prompt("[]"), return_tensors="pt")
    wrapper = VerdictHead(model, recipe["ids"]).eval()
    with torch.no_grad(), tempfile.TemporaryDirectory(dir=a.out) as scratch:
        inp = (encoded.input_ids, encoded.attention_mask)
        torch.testing.assert_close(
            wrapper(*inp), model(**encoded).logits[:, -1, recipe["ids"]]
        )
        path = Path(scratch) / "original.onnx"
        torch.onnx.export(
            wrapper,
            inp,
            str(path),
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
        doc = onnx.load(path)
        require(
            pack_matrices(doc.graph) > 100,
            "expected the language model's projection matrices",
        )
        onnx.checker.check_model(doc)
        onnx.save(doc, graph_dir / "model_quantized.onnx")
    total = sum(f.stat().st_size for f in a.out.rglob("*") if f.is_file())
    require(total <= 250_000_000, "Spark browser package exceeds size limit")
    print(json.dumps({"bytes": total, "seconds": time.monotonic() - t}))


if __name__ == "__main__":
    main()
