#!/usr/bin/env python3
"""Deterministic surface-realism transforms for conversation turns.

The transforms make template-generated dialogue read like real chat traffic:
student messages get texting abbreviations and occasional typos, assistant
messages get exclamation moderation and canned-phrase variation. All changes
are surface-level: meaning, facts, and safety-relevant content are untouched.

Everything is seeded, so the same (seed, role) always transforms identically.
"""
import random
import re

# word -> chat replacements for student messages (applied whole-word)
_STUDENT_SWAPS = [
    (r"\bthough\b", ["tho", "tho", "tho"]),
    (r"\bbecause\b", ["bc", "cause", "bc"]),
    (r"\bgoing to\b", ["gonna", "gonna", "gonna"]),
    (r"\bwant to\b", ["wanna", "wanna", "wanna"]),
    (r"\bkind of\b", ["kinda", "kinda", "kinda"]),
    (r"\bi don't know\b", ["idk", "idk", "idk"]),
    (r"\bplease\b", ["pls", "plz", "pls"]),
    (r"\bright now\b", ["rn", "rn", "rn"]),
    (r"\babout\b", ["abt", "abt", "abt"]),
    (r"\bnever mind\b", ["nvm", "nvm", "nvm"]),
    (r"\bto be honest\b", ["tbh", "tbh", "tbh"]),
    (r"\bthanks\b", ["thx", "ty", "ty!"]),
    (r"\byeah\b", ["ya", "yea", "yep"]),
    (r"\byes\b", ["ya", "ye", "yep"]),
    (r"\breally\b", ["rly", "actually", "rly"]),
    (r"\byour\b", ["ur", "ur", "your"]),
    (r"\byou\b", ["u", "u", "you"]),
    (r"\bpeople\b", ["ppl", "ppl", "people"]),
]

# assistant canned-phrase variation (applied at message start or anywhere)
_ASSISTANT_SWAPS = [
    (r"\bPerfect!", ["Love that!", "Great plan!", "Nice!", "That's the spirit!"]),
    (r"\bYou're welcome", ["Anytime", "Happy to help", "No problem"]),
    (r"\bAwesome!", ["Nice!", "So cool!", "Love it!"]),
    (r"\bsuper responsible\b", ["really responsible", "so responsible"]),
    (r"\bsuper \b", ["really ", "super "]),
]

_TYPO_MIN_LEN = 5
_SAFE_TYPO_WORDS = {"helmet", "safely", "danger", "unsafe"}


def _typo(word, rng):
    """Return a plausible kid typo of `word` (>= 5 letters)."""
    if len(word) < _TYPO_MIN_LEN or word.lower() in _SAFE_TYPO_WORDS:
        return word
    kind = rng.randrange(3)
    i = rng.randrange(1, len(word) - 1)
    if kind == 0:  # dropped letter
        return word[:i] + word[i + 1:]
    if kind == 1:  # doubled letter
        return word[:i] + word[i] + word[i] + word[i + 1:]
    # swapped adjacent letters
    if i + 1 < len(word) and word[i] != word[i + 1]:
        return word[:i] + word[i + 1] + word[i] + word[i + 2:]
    return word


def _inject_typo(msg, rng):
    words = msg.split(" ")
    idxs = [i for i, w in enumerate(words) if len(w) >= _TYPO_MIN_LEN]
    if not idxs:
        return msg
    i = rng.choice(idxs)
    fixed = _typo(words[i], rng)
    if fixed == words[i]:
        return msg
    words[i] = fixed
    return " ".join(words)


def transform(msg, role, seed):
    """Apply seeded realism transforms to one message."""
    if not msg:
        return msg
    rng = random.Random(seed)
    if role == "student":
        # abbreviation pass on ~45% of student messages
        if rng.random() < 0.45:
            for pat, alts in _STUDENT_SWAPS:
                if rng.random() < 0.55:
                    msg = re.sub(pat, lambda _m, a=alts: rng.choice(a), msg)
        # occasional typo on ~9% of student messages
        if rng.random() < 0.09:
            msg = _inject_typo(msg, rng)
        # double exclamation cleanup
        msg = msg.replace("!!", "!")
        return msg
    # assistant
    if msg.count("!") >= 2:
        # keep the first exclamation, soften the rest
        first = msg.index("!")
        msg = msg[:first + 1] + msg[first + 1:].replace("!", ".")
    for pat, alts in _ASSISTANT_SWAPS:
        if rng.random() < 0.5 and re.search(pat, msg):
            msg = re.sub(pat, lambda _m, a=alts: rng.choice(a), msg, count=1)
    msg = msg.replace("!!", "!")
    return msg
