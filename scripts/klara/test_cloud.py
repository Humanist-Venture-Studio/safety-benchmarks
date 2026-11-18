"""Offline regression cases for Klara's Decisions scorer and per-row evidence."""
import argparse
import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import backends
import benchmark
import score
from common import read_tsv
from make_tuning_fixture import write_fixture
from results import validate_run


def noul(p):
    return {"type": "noul", "noul": p}


def reply(answers, cost=0.000015876):
    return {"answers": answers, "usage": {"cost": cost}, "model": "typesafe/jev-1.14-20261014"}


class CloudTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.key = "synthetic-fixture-value"
        key_path = self.root / "stub-key"
        key_path.write_text(self.key, encoding="utf-8")
        environment = patch.dict(os.environ, {"KLARA_OPENROUTER_KEY_FILE": str(key_path)})
        environment.start()
        self.addCleanup(environment.stop)
        self.messages = [{"role": "student", "content": "How many sides?"},
                         {"role": "tutor", "content": "A triangle has three."}]

    def backend(self, *flags):
        p = argparse.ArgumentParser()
        backends.backend_args(p)
        return backends.Backend(p.parse_args(["--tier", "cloud", *flags]))

    def test_score_entry_point_default_spec(self):
        path = self.root / "conversation.json"
        path.write_text(json.dumps(self.messages), encoding="utf-8")
        argv = ["score.py", "--tier", "cloud", "--input", str(path), "--threshold", "0.6"]
        with patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()) as out:
            with patch.object(backends, "request_json", return_value=reply({"unsafe": noul(.57)})) as send:
                score.main()
        self.assertEqual(json.loads(out.getvalue()), {"unsafe_probability": .57, "label": "safe"})
        spec = json.loads(backends.CLOUD_SPEC.read_bytes())
        send.assert_called_once_with("https://openrouter.ai/api/alpha/decisions", 120, {
            "model": "typesafe/jev-1.14",
            "state": spec["state_prefix"] + "\n\nstudent: How many sides?\ntutor: A triangle has three.",
            "questions": spec["questions"],
        }, self.key)

    def test_selectors_and_json_transcript(self):
        questions = {"a": {"type": "noul", "instructions": "First signal?"},
                     "b": {"type": "noul", "instructions": "Second signal?"},
                     "risk": {"type": "choice", "instructions": "Classify.",
                              "criteria": {"safe": "Ordinary.", "unsafe": "Needs action."}}}
        answers = {"a": noul(.25), "b": noul(.6),
                   "risk": {"type": "choice", "choice": "safe", "probabilities": {"safe": .8, "unsafe": .2}}}
        for selector, expected in (({"from": "risk", "choice": "unsafe"}, .2),
                                   ({"max": ["a", "b"]}, .6), ({"noisy_or": ["a", "b"]}, .7)):
            with self.subTest(selector=selector):
                spec = {"questions": questions, "transcript": "json", "unsafe_probability": selector}
                path = self.root / "variant.json"
                content = json.dumps(spec, indent=2).replace("\n", "\r\n").encode()
                path.write_bytes(content)
                backend = self.backend("--prompt-file", str(path), "--threshold", ".6")
                with patch.object(backends, "request_json", return_value=reply(answers)) as send:
                    contract, raw, error, cost = backend.score(self.messages)
                self.assertEqual(backend.prompt_hash, hashlib.sha256(content).hexdigest())
                payload = send.call_args.args[2]
                self.assertEqual(payload["state"], json.dumps(self.messages, separators=(",", ":")))
                self.assertEqual(payload["questions"], questions)
                self.assertEqual(error, "")
                self.assertEqual(cost, .000015876)
                self.assertEqual(json.loads(raw), answers)
                self.assertAlmostEqual(contract["unsafe_probability"], expected)
                self.assertEqual(contract["label"], "unsafe" if expected >= .6 else "safe")

    def test_missing_malformed_and_echoed_answers(self):
        backend = self.backend()
        bad = [{}, {"unsafe": {"type": "refusal"}}, {"unsafe": {"type": "noul"}},
               {"unsafe": noul(.5), "extra": self.key}]
        bad.extend({"unsafe": noul(p)} for p in (-.1, 1.1, True, "0.5", None, float("inf"), float("nan")))
        for answers in bad:
            with self.subTest(answers=answers):
                with patch.object(backends, "request_json", return_value=reply(answers)) as send:
                    contract, raw, error, cost = backend.score(self.messages)
                send.assert_called_once()
                self.assertIsNone(contract)
                self.assertTrue(error)
                self.assertEqual(cost, .000015876)
                self.assertNotIn(self.key, raw + error)

    def test_transport_failure_one_attempt(self):
        for failure in ("status", "timeout"):
            with self.subTest(failure=failure), patch.object(backends.http.client, "HTTPSConnection") as connect:
                conn = connect.return_value
                response = conn.getresponse.return_value
                response.status = 400
                response.read.return_value = self.key.encode()
                if failure == "timeout":
                    conn.getresponse.side_effect = TimeoutError(self.key)
                contract, raw, error, cost = self.backend().score(self.messages)
                self.assertIsNone(contract)
                self.assertIsNone(cost)
                self.assertEqual(raw, "")
                self.assertEqual(error, "TimeoutError" if failure == "timeout" else "ValueError")
                conn.request.assert_called_once()
                conn.close.assert_called_once()

    def test_auxiliary_answers_and_noisy_or_endpoints(self):
        questions = {"a": {"type": "noul", "instructions": "First?"},
                     "b": {"type": "noul", "instructions": "Second?"},
                     "level": {"type": "score", "instructions": "Level?", "criteria": ["Low", "High"]},
                     "bounds": {"type": "box", "instructions": "Where?"}}
        spec = backends.parse_cloud_spec(json.dumps({
            "transcript": "lines", "questions": questions, "unsafe_probability": {"noisy_or": ["a", "b"]}}))
        answers = {"level": {"type": "score", "score": .75, "probabilities": {"0": .25, "1": .75}},
                   "bounds": {"type": "box", "box": {"top": 0, "bottom": 1, "left": 0, "right": .5}}}
        for a, b, expected in ((0, 0, 0), (1, .6, 1), (0, 1e-20, 1e-20)):
            answers.update(a=noul(a), b=noul(b))
            self.assertEqual(backends.cloud_score(answers, spec), expected)
        answers["level"]["score"] = 2
        with self.assertRaises(ValueError):
            backends.cloud_score(answers, spec)

    def test_invalid_selectors_and_missing_auxiliary_answers(self):
        spec = {"transcript": "lines", "questions": {"a": {"type": "noul", "instructions": "Signal?"},
                "b": {"type": "choice", "instructions": "Select.", "criteria": {"unsafe": "Needs action."}}}}
        for rule in ({"max": []}, {"noisy_or": ["a", "a"]}, {"from": "missing"},
                     {"max": ["b"]}, {"from": "b"}, {"from": "b", "choice": "unknown"}):
            with self.subTest(rule=rule), self.assertRaises(ValueError):
                backends.parse_cloud_spec(json.dumps({**spec, "unsafe_probability": rule}))
        spec["unsafe_probability"] = {"from": "a"}
        with self.assertRaises(KeyError):
            backends.cloud_score({"a": noul(0)}, spec)
        spec["unsafe_probability"] = {"from": "b", "choice": "unsafe"}
        with self.assertRaises(KeyError):
            backends.cloud_score({"a": noul(0), "b": {"type": "choice", "probabilities": {"safe": 1}}}, spec)

    def test_budget_and_benchmark_evidence(self):
        fixture = self.root / "synthetic.tsv"
        with fixture.open("w", encoding="utf-8", newline="") as out:
            write_fixture(out)
        output = self.root / "full.tsv"
        argv = ["benchmark.py", "--tier", "cloud", "--data", str(fixture), "--split", "validation",
                "--limit", "20", "--output", str(output), "--max-cost", ".3"]
        responses = [reply({"unsafe": noul(.5)}, .1), reply({}, .2)]
        with patch.object(sys, "argv", argv), patch.object(backends, "request_json", side_effect=responses) as send:
            with self.assertRaisesRegex(SystemExit, "cost limit reached"):
                benchmark.main()
        self.assertEqual(send.call_count, 2)
        self.assertFalse(output.exists())
        partial = output.with_suffix(".tsv.partial")
        rows = list(read_tsv(partial))
        validate_run(rows)
        self.assertEqual([r["raw"] for r in rows], ['{"unsafe":{"type":"noul","noul":0.5}}', '{}'])
        self.assertEqual([r["cost_usd"] for r in rows], ["0.1", "0.2"])
        self.assertEqual((rows[0]["label"], rows[0]["raw_probability"]), ("unsafe", "0.5"))
        self.assertEqual((rows[1]["label"], rows[1]["correct"], rows[1]["error"]), ("", "0", "KeyError"))
        self.assertNotIn(self.key, partial.read_text())
        self.assertEqual(rows[0]["prompt_sha256"], hashlib.sha256(backends.CLOUD_SPEC.read_bytes()).hexdigest())

        # Same seed and input select the same first rows even when the earlier run hit its cap.
        argv[argv.index(str(output))] = str(self.root / "sample.tsv")
        with patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()) as summary:
            with patch.object(backends, "request_json", return_value=reply({"unsafe": noul(.5)})) as send:
                benchmark.main()
        complete = list(read_tsv(self.root / "sample.tsv"))
        validate_run(complete)
        self.assertEqual(send.call_count, 20)
        self.assertEqual(len(complete), 20)
        self.assertEqual([r["row_id"] for r in complete[:2]], [r["row_id"] for r in rows])
        self.assertIn("20/20 rows priced", summary.getvalue())

    def test_zero_cap_and_invalid_cost(self):
        self.assertEqual(self.backend().max_cost, Decimal("5"))
        with patch.object(backends, "request_json") as send, self.assertRaises(SystemExit):
            self.backend("--max-cost", "0").score(self.messages)
        send.assert_not_called()
        for cost in (-1, None, float("inf"), True):
            with self.subTest(cost=cost), patch.object(backends, "request_json", return_value=reply({"unsafe": noul(0)}, cost)):
                result = self.backend().score(self.messages)
                self.assertIsNone(result[0])
                self.assertEqual(json.loads(result[1]), {"unsafe": noul(0)})
                self.assertTrue(result[2])
                self.assertIsNone(result[3])


if __name__ == "__main__":
    unittest.main()
