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
