"""Untouched safety-head baselines using each producer's native verdict format."""

import json

import torch
from backends import POLICY
from common import require
from transformers import (
    AutoModelForCausalLM,
    AutoModelForSequenceClassification,
    AutoTokenizer,
)


class NativeGuard:
    def __init__(self, source, kind):
        require(
            kind in ("mezzo", "granite", "qwen-guard"),
            "choose --native mezzo, granite or qwen-guard",
        )
        self.kind = kind
        self.tok = AutoTokenizer.from_pretrained(source, local_files_only=True)
        cls = (
            AutoModelForSequenceClassification
            if kind == "mezzo"
            else AutoModelForCausalLM
        )
        self.model = (
            cls.from_pretrained(source, dtype=torch.bfloat16, local_files_only=True)
            .to("mps")
            .eval()
        )
        self.recipe = {
            "mezzo": "Mezzo: max of five independent sigmoid labels on transcript",
            "granite": "Granite: native Yes/No custom risk on transcript: " + POLICY,
            "qwen-guard": "Qwen3Guard: maximum per-turn native Unsafe + Controversial mass",
        }[kind]

    def decision(self, prefix, forms, closing_tag=""):
        tok = self.tok
        ids = tok.encode(prefix, add_special_tokens=False)
        first = []
        for surface, _ in forms:
            combined = tok.encode(prefix + surface, add_special_tokens=False)
            require(
                combined[: len(ids)] == ids and len(combined) > len(ids),
                "unstable native verdict boundary",
            )
            first.append(combined[len(ids)])
        require(len(set(first)) == len(first), "native verdict tokens overlap")
        x = torch.tensor([ids], device=self.model.device)
        response = self.model.generate(
            input_ids=x,
            attention_mask=torch.ones_like(x),
            do_sample=False,
            max_new_tokens=8,
            return_dict_in_generate=True,
            output_scores=True,
            pad_token_id=self.tok.eos_token_id,
        )
        word = (
            tok.decode(response.sequences[0, len(ids) :], skip_special_tokens=True)
            .strip()
            .splitlines()
        )
        label = word[0].strip() if word else ""
        if closing_tag:
            label = label.partition(closing_tag)[0].strip()
        require(
            label in [surface.strip() for surface, _ in forms],
            "malformed native verdict",
        )
        probs = response.scores[0][0, first].float().softmax(0).tolist()
        return sum(p for p, (_, flag) in zip(probs, forms) if flag), label

    @torch.inference_mode()
    def score(self, messages):
        text = json.dumps(messages, ensure_ascii=False, separators=(",", ":"))
        if self.kind == "mezzo":
            x = self.tok(text, return_tensors="pt").to(self.model.device)
            scores = self.model(**x).logits[0].float().sigmoid().tolist()
            require(len(scores) == 5, "expected native five-label Mezzo head")
            return max(scores), json.dumps(
                {self.model.config.id2label[i]: value for i, value in enumerate(scores)}
            )
        if self.kind == "granite":
            tagged = "custom_criteria" in self.tok.chat_template
            config = (
                {"custom_criteria": POLICY}
                if tagged
                else {"risk_name": "klara", "risk_definition": POLICY}
            )
            prefix = self.tok.apply_chat_template(
                [{"role": "user", "content": text}],
                tokenize=False,
                add_generation_prompt=True,
                guardian_config=config,
                think=False,
            )
            if tagged:
                return self.decision(
                    prefix + "<score>", [("no", False), ("yes", True)], "</score>"
                )
            return self.decision(prefix, [("No", False), ("Yes", True)])
        native, scores, words = [], [], []
        for message in messages:
            native.append(
                {
                    "role": "user" if message["role"] == "student" else "assistant",
                    "content": message["content"],
                }
            )
            prefix = self.tok.apply_chat_template(native, tokenize=False) + "Safety:"
            p, word = self.decision(
                prefix, [(" Safe", False), (" Unsafe", True), (" Controversial", True)]
            )
            scores.append(p)
            words.append(word)
        return max(scores), json.dumps(words)
