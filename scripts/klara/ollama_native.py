"""Score every speaker under an untouched guard's published policy in Ollama."""

import json
import math
import time

from backends import request_json
from common import require


def native_verdict(reply, forms):
    require(reply["done"], "incomplete native verdict")
    lines = reply["response"].strip().splitlines()
    require(lines and lines[0].strip() in forms, "malformed native verdict")
    first = reply["logprobs"][0]
    scores = {r["token"]: r["logprob"] for r in first["top_logprobs"]}
    scores[first["token"]] = first["logprob"]
    verdict = lines[0].strip()
    require(first["token"] == forms[verdict], "native first token differs from verdict")
    values = [scores.get(token) for token in forms.values()]
    require(all(type(x) in (float, int) and math.isfinite(x) for x in values),
            "missing native verdict alternative")
    exp = [math.exp(x - max(values)) for x in values]
    return sum(exp[1:]) / sum(exp), verdict


class OllamaNative:
    def __init__(self, kind, source):
        from transformers import AutoTokenizer

        self.kind = kind
        self.tok = AutoTokenizer.from_pretrained(source, local_files_only=True)
        self.recipe = json.dumps([kind, "native per-speaker maximum v1", self.tok.chat_template],
                                 ensure_ascii=False)
        sample = self.prefix([{"role": "user", "content": "Hello"}])
        prefix = self.tok.encode(sample, add_special_tokens=False)
        words = ("No", "Yes") if kind == "granite" else (" Safe", " Unsafe", " Controversial")
        self.forms = {}
        for word in words:
            combined = self.tok.encode(sample + word, add_special_tokens=False)
            require(combined[:len(prefix)] == prefix and len(combined) > len(prefix),
                    "unstable native verdict boundary")
            self.forms[word.strip()] = self.tok.decode(combined[len(prefix):len(prefix)+1])
        require(len(set(self.forms.values())) == len(words), "native verdicts share a token")

    def prefix(self, messages):
        if self.kind == "granite":
            return self.tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True,
                                                guardian_config={"risk_name": "harm"})
        return self.tok.apply_chat_template(messages, tokenize=False) + "Safety:"

    def score(self, messages, base, model, timeout):
        history, traces, scores = [], [], []
        end = time.monotonic() + timeout
        for message in messages:
            history.append({"role": "user" if message["role"] == "student" else "assistant",
                            "content": message["content"]})
            remaining = end - time.monotonic()
            require(remaining > 0, "native row deadline expired")
            reply = request_json(base + "/api/generate", remaining, {
                "model": model, "prompt": self.prefix(history), "raw": True, "stream": False,
                "logprobs": True, "top_logprobs": 20,
                "options": {"temperature": 0, "num_predict": 8, "stop": ["\n"]}})
            p, label = native_verdict(reply, self.forms)
            scores.append(p)
            traces.append([label, p])
        return max(scores), json.dumps(traces, separators=(",", ":"))
