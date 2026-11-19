"""Offline probes for the fixture, grouped selection, verdict loss and serving checks."""

import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from calibrate import apply
from export_chat import preserve_tokenizer_metadata
from make_tuning_fixture import write_fixture
from metrics import metrics
from training import fingerprint, missed_ids, partition
from verify_chat import compare_verdict, reference_key


class GuardTuningChecks(unittest.TestCase):
    def test_dataset_pin_checks_source_and_projected_bytes(self):
        from tier_data import digest, prepare, verify

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "full.tsv"
            source.write_bytes(b"row_id\tsplit\tx\nK1\ttrain\tA\nK2\ttest\t\xff\nK3\tvalidation\tB\n")
            expected = digest(source)
            out = root / "log"
            prepare(out, source, expected)
            verify(out, source, expected)
            dev = out / "development.tsv"
            self.assertEqual(dev.read_bytes(), b"row_id\tsplit\tx\nK1\ttrain\tA\nK3\tvalidation\tB\n")
            dev.write_bytes(dev.read_bytes() + b"x")
            with self.assertRaisesRegex(ValueError, "projection"):
                verify(out, source, expected)
            source.write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "full dataset"):
                verify(out, source, expected)

    def test_deployed_k_quant_grids_reconstruct_gguf_codes(self):
        try:
            import gguf
            import numpy as np
            from flash_precision import grid
        except ImportError:
            self.skipTest("tuning environment required")
        rng = np.random.default_rng(5)
        for kind in (gguf.GGMLQuantizationType.Q5_K, gguf.GGMLQuantizationType.Q6_K):
            packed = rng.integers(0, 256, (3, gguf.GGML_QUANT_SIZES[kind][1]), dtype=np.uint8)
            if kind == gguf.GGMLQuantizationType.Q5_K:
                packed[:, :4] = np.array([.0625, .125], dtype=np.float16).view(np.uint8)
            else:
                packed[:, -2:] = np.array([.0625], dtype=np.float16).view(np.uint8)
            scales, offsets, lo, hi = grid(SimpleNamespace(tensor_type=kind, data=packed))
            decoded = gguf.dequantize(packed, kind).reshape(scales.size, -1)
            scale, offset = scales.reshape(-1, 1), offsets.reshape(-1, 1)
            codes = np.rint((decoded - offset) / np.where(scale == 0, 1, scale)).clip(lo, hi)
            np.testing.assert_allclose(codes * scale + offset, decoded)

    def test_interrupted_benchmark_preserves_first_attempts(self):
        import csv
        import contextlib
        import sys
        from unittest.mock import patch
        import benchmark

        rows = [dict(row_id=str(i), split="validation", turns="1", trigger="none",
                     rule_id="", clarity="clear", is_unsafe="0", turn1_request="hi",
                     turn1_response="hello") for i in range(4)]
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            data = root / "development.tsv"
            with data.open("w") as f:
                writer = csv.DictWriter(f, rows[0], delimiter="\t")
                writer.writeheader()
                writer.writerows(rows)
            (root / "dataset.json").write_text("{}")
            output = root / "scores.tsv"
            args = ["benchmark.py", "--backend", "ollama", "--model", "fixture", "--tier", "flash",
                    "--data", str(data), "--split", "validation", "--output", str(output)]
            reply = ({"unsafe_probability": 0.1, "label": "safe"}, "", "", None)
            with patch("benchmark.Backend") as backend, patch("tier_data.verify_input"), \
                    patch.object(sys, "argv", args), contextlib.redirect_stdout(io.StringIO()):
                scorer = backend.return_value
                scorer.name, scorer.model = "ollama", "fixture"
                scorer.threshold, scorer.calibration_hash = 0.5, ""
                scorer.prompt_hash, scorer.raw_probability = "test", 0.1
                scorer.score.side_effect = [reply, KeyboardInterrupt(), reply, reply]
                with self.assertRaises(KeyboardInterrupt):
                    benchmark.main()
                args.append("--resume-interrupted")
                benchmark.main()
            with output.open() as f:
                saved = list(csv.DictReader(f, delimiter="\t"))
            self.assertEqual([r["correct"] for r in saved], ["1", "0", "1", "1"])
            self.assertEqual(scorer.score.call_count, 4)
            self.assertEqual(saved[1]["error"], "interrupted before durable verdict")

    def test_native_multitoken_verdict_and_missing_alternative(self):
        from ollama_native import native_verdict

        forms = {"Safe": " Safe", "Unsafe": " Unsafe", "Controversial": " Cont"}
        first = dict(token=" Cont", logprob=-1, top_logprobs=[
            dict(token=" Safe", logprob=-2), dict(token=" Unsafe", logprob=-3)])
        reply = dict(response=" Controversial", logprobs=[first], done=True)
        p, label = native_verdict(reply, forms)
        self.assertEqual(label, "Controversial")
        self.assertAlmostEqual(p, 0.7552715289)
        first["top_logprobs"].pop()
        with self.assertRaisesRegex(ValueError, "alternative"):
            native_verdict(reply, forms)

    def test_mezzo_native_tei_keeps_independent_sigmoids(self):
        from math import exp
        from backends import mezzo_score

        logits = [
            {"label": k, "score": 2}
            for k in ("sexual", "violence", "self-harm", "hate-speech", "toxic")
        ]
        p, raw = mezzo_score(logits)
        self.assertAlmostEqual(p, 1 / (1 + exp(-2)))
        self.assertEqual(json.loads(raw), logits)
        with self.assertRaises(ValueError):
            mezzo_score(logits[:-1])

    def test_browser_check_uses_the_calibrated_operating_point(self):
        from browser_compare import differences

        spec = dict(slope=1, intercept=1, threshold=0.7)
        rows = [
            dict(
                row_id="one",
                raw_probability=".5",
                unsafe_probability=str(apply(0.5, spec)),
                label="unsafe",
                error="",
            ),
            dict(
                row_id="two",
                raw_probability="",
                unsafe_probability="",
                label="",
                error="malformed",
            ),
        ]
        measured = differences(rows, [[0, 0], [1, 0]], spec)
        self.assertEqual(measured[0]["label_flip"], 0)
        self.assertAlmostEqual(measured[0]["abs_calibrated"], 0)
        self.assertEqual(measured[1]["label_flip"], "")
        with self.assertRaises(ValueError):
            differences(rows, [[0, 0]], spec)

    def test_oof_missed_positive_repeats_its_safe_lookalike(self):
        from training import resample_groups

        rows = [
            dict(row_id="risk", is_unsafe="1", rule_id="A1", look_alike_of=""),
            dict(row_id="near", is_unsafe="0", rule_id="", look_alike_of="risk"),
            dict(row_id="other", is_unsafe="0", rule_id="", look_alike_of=""),
        ]
        weak, pairs, repeat = resample_groups(rows, {"risk", "outside-fit"}, 18, True)
        self.assertEqual(weak, ["A1"])
        self.assertTrue(pairs)
        self.assertEqual(repeat, {"risk", "near"})

    def test_packed_browser_matrices_match_gguf_blocks(self):
        try:
            import gguf
            import numpy as np
            from onnx import helper, numpy_helper, TensorProto
            from onnx.reference import ReferenceEvaluator
            from export_smol_browser import pack_matrices
        except ImportError:
            self.skipTest("requires tuning environment")
        rng = np.random.default_rng(11)
        embed = rng.normal(size=(8, 32)).astype("float32")
        weight = rng.normal(size=(32, 2)).astype("float32")
        x = helper.make_tensor_value_info("ids", TensorProto.INT64, [None])
        y = helper.make_tensor_value_info("logits", TensorProto.FLOAT, [None, 2])
        graph = helper.make_graph(
            [
                helper.make_node("Gather", ["embed", "ids"], ["x"]),
                helper.make_node("MatMul", ["x", "w"], ["logits"]),
            ],
            "q8",
            [x],
            [y],
            [
                numpy_helper.from_array(embed, "embed"),
                numpy_helper.from_array(weight, "w"),
            ],
        )
        self.assertEqual(pack_matrices(graph), 2)
        model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 18)])
        ids = np.array([1, 7])
        result = ReferenceEvaluator(model).run(None, {"ids": ids})[0]
        typ = gguf.GGMLQuantizationType.Q8_0

        def q8(matrix):
            return gguf.dequantize(
                gguf.quantize(np.ascontiguousarray(matrix), typ), typ
            )

        np.testing.assert_allclose(
            result, q8(embed)[ids] @ q8(weight.T).T, atol=1e-6, rtol=1e-6
        )

    def test_q8_aware_matches_converter_and_trains_lora(self):
        try:
            import torch
            import gguf
            from peft import get_peft_model, LoraConfig
            from transformers import LlamaConfig, LlamaForCausalLM
            from train_chat import enable_smol_q8, q8_weights
        except ImportError:
            self.skipTest("requires tuning environment")
        torch.manual_seed(7)
        values = torch.randn(3, 32)
        values[0] = 0
        typ = gguf.GGMLQuantizationType.Q8_0
        reference = gguf.dequantize(gguf.quantize(values.numpy(), typ), typ)
        torch.testing.assert_close(
            q8_weights(values), torch.from_numpy(reference), rtol=0, atol=0
        )
        tiny = LlamaForCausalLM(
            LlamaConfig(
                hidden_size=32,
                intermediate_size=64,
                num_hidden_layers=1,
                num_attention_heads=2,
                num_key_value_heads=2,
                vocab_size=64,
                tie_word_embeddings=True,
            )
        )
        model = get_peft_model(
            tiny, LoraConfig(r=2, lora_alpha=4, target_modules=["q_proj", "v_proj"])
        )
        enable_smol_q8(model)
        model(torch.tensor([[1, 2, 3]])).logits.mean().backward()
        self.assertTrue(
            any(
                "lora_B" in k and p.grad is not None and p.grad.abs().sum() > 0
                for k, p in model.named_parameters()
            )
        )

    def test_fixture_reproduces_measured_rows(self):
        output = io.StringIO(newline="")
        write_fixture(output)
        digest = hashlib.sha256(output.getvalue().encode("utf-8")).hexdigest()
        self.assertEqual(
            digest, "1638d9b98b51dbe6defe7c0cb0f80a0ffd021c2865e8ef3d7041d3a4b9aab577"
        )

    def test_saved_reference_binds_inputs_and_both_adapters(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            for name in ("adapter", "round-one"):
                path = run / name
                path.mkdir()
                (path / "adapter_config.json").write_text("{}")
                (path / "adapter_model.safetensors").write_bytes(b"fixture")
            recipe = {"init_adapter": str(run / "round-one"), "ids": [1, 2]}
            samples = {"1": "one", "2": "two"}
            key = reference_key(recipe, samples, run)
            self.assertEqual(
                key, reference_key(recipe, dict(reversed(samples.items())), run)
            )
            self.assertNotEqual(key, reference_key(recipe, {"1": "different"}, run))
            self.assertNotEqual(
                key, reference_key({**recipe, "ids": [2, 1]}, samples, run)
            )
            for directory in ("adapter", "round-one"):
                weights = run / directory / "adapter_model.safetensors"
                weights.write_bytes(b"different")
                self.assertNotEqual(key, reference_key(recipe, samples, run))
                weights.write_bytes(b"fixture")

    def test_first_token_probe_detects_missing_alternative_wrong_length_and_margin(
        self,
    ):
        ref = {"ids": [7, 9], "margin": -1.5}
        tokens = [" safe", " unsafe"]
        alternative = {"token": " unsafe", "logprob": -1.8}
        first = {"token": " safe", "logprob": -0.3, "top_logprobs": [alternative]}
        reply = {
            "message": {"content": " safe"},
            "done": True,
            "logprobs": [first],
            "prompt_eval_count": 2,
        }
        self.assertEqual(compare_verdict(ref, tokens, reply, 0.01)["delta"], 0)
        with self.assertRaisesRegex(ValueError, "token count"):
            compare_verdict(ref, tokens, {**reply, "prompt_eval_count": 1}, 0.01)
        with self.assertRaisesRegex(ValueError, "margin"):
            compare_verdict({**ref, "margin": 2}, tokens, reply, 0.01)
        first["top_logprobs"] = []
        with self.assertRaisesRegex(ValueError, "unavailable for unsafe"):
            compare_verdict(ref, tokens, reply, 0.01)

    def test_staged_phi_keeps_bpe_class_and_special_token_flags(self):
        with tempfile.TemporaryDirectory() as temp:
            original, staged = [Path(temp) / name for name in ("original", "staged")]
            original.write_text(
                json.dumps(
                    {
                        "tokenizer_class": "GPT2Tokenizer",
                        "add_bos_token": False,
                        "add_eos_token": False,
                        "chat_template": "native",
                    }
                )
            )
            staged.write_text(
                json.dumps(
                    {"tokenizer_class": "TokenizersBackend", "pad_token": "<pad>"}
                )
            )
            preserve_tokenizer_metadata(original, staged)
            self.assertEqual(
                json.loads(staged.read_text()),
                {
                    "tokenizer_class": "GPT2Tokenizer",
                    "add_bos_token": False,
                    "add_eos_token": False,
                    "pad_token": "<pad>",
                },
            )

    def test_verdict_loss_matches_full_vocabulary_targets_and_gradients(self):
        try:
            import torch
        except ImportError:
            self.skipTest("tuning environment supplies PyTorch")
        from training import verdict_loss

        x = torch.tensor(
            [[0.0, 1.0, 2.0, -1.0], [3.0, -4.0, 2.0, 1.0]], requires_grad=True
        )
        labels, ids = torch.tensor([0, 1]), torch.tensor([3, 1])
        for smoothing in (0.0, 0.05):
            target = torch.zeros_like(x)
            target[torch.arange(2), ids[labels]] = 1.0 - smoothing
            target[torch.arange(2), ids[1 - labels]] = smoothing
            expected = -(target * x.log_softmax(-1)).sum(-1)
            measured = verdict_loss(x, labels, ids, smoothing)
            torch.testing.assert_close(measured, expected)
            torch.testing.assert_close(
                torch.autograd.grad(measured.sum(), x)[0],
                torch.autograd.grad(expected.sum(), x)[0],
            )

    def test_tied_pr_auc_brier_and_missing_output(self):
        rows = [
            {
                "is_unsafe": y,
                "unsafe_probability": p,
                "label": label,
                "error": error,
                "latency_ms": 1,
            }
            for y, p, label, error in [
                (1, 0.8, "unsafe", ""),
                (0, 0.8, "unsafe", ""),
                (1, 0.3, "safe", ""),
                (0, 0.1, "safe", ""),
                (1, "", "", "missing"),
            ]
        ]
        report = metrics(rows)
        self.assertEqual(report["PR-AUC (AP)"], "0.5833")
        self.assertEqual(report["Brier"], "0.2950")
        self.assertEqual(report["missed/unsafe"], "2/3")
        self.assertAlmostEqual(apply(0.25, {"slope": 1, "intercept": 0}), 0.25)

    def test_grouped_oof_rejects_leakage_and_incomplete_coverage(self):
        rows = [
            {
                "scenario_id": f"s{i}",
                "scenario_kind": ("ordinary", "risk")[i % 2],
                "grade_band": "middle",
                "row_id": f"r{i}-{j}",
                "split": "train",
                "is_unsafe": str(int(i % 2 and j == 0)),
            }
            for i in range(20)
            for j in range(2)
        ]
        a = SimpleNamespace(seed=42, folds=2, fold=None, source=Path("/fixture"))
        _, _, _, folds = partition(rows, a)
        paths = []
        with tempfile.TemporaryDirectory() as tmp:
            for i in range(2):
                a.fold = i
                train, dev, held, _ = partition(rows, a)
                fit_ids = {r["scenario_id"] for r in train + dev}
                self.assertTrue(fit_ids.isdisjoint(r["scenario_id"] for r in held))
                self.assertEqual(
                    {r["scenario_kind"] for r in held}, {"ordinary", "risk"}
                )
                self.assertFalse(
                    {r["scenario_id"] for r in train} & {r["scenario_id"] for r in dev}
                )
                doc = {
                    "source": str(a.source),
                    "train_sha256": fingerprint(rows),
                    "seed": a.seed,
                    "folds": 2,
                    "fold": i,
                    "predictions": {r["row_id"]: 0 for r in held},
                    "fit_scenarios": sorted(fit_ids),
                }
                path = Path(tmp) / f"{i}.json"
                path.write_text(json.dumps(doc))
                paths.append(path)
            a.fold = None
            self.assertEqual(
                missed_ids(paths, rows, folds, a),
                {r["row_id"] for r in rows if r["is_unsafe"] == "1"},
            )
            with self.assertRaisesRegex(ValueError, "incomplete"):
                missed_ids(paths[:1], rows, folds, a)
            doc["fit_scenarios"].append(held[0]["scenario_id"])
            path.write_text(json.dumps(doc))
            with self.assertRaisesRegex(ValueError, "leakage"):
                missed_ids(paths, rows, folds, a)


if __name__ == "__main__":
    unittest.main()
