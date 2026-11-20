"""Exact Jaccard search over normalized character five-grams."""
import unicodedata
from collections import Counter, defaultdict

NGRAM = 5
# Integer arithmetic keeps pairs at exactly 85% in the result.
PERCENT = 85


def normalize(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def transcript(messages):
    return "\n".join(normalize(m["content"]) for m in messages)


def matches(documents, eligible):
    """Yield qualifying pairs satisfying eligible(a, b). Prefix filtering is lossless."""
    vocab = {}
    sets = {}
    frequency = Counter()
    for key, doc in documents.items():
        terms = {doc[i:i + NGRAM] for i in range(max(1, len(doc) - NGRAM + 1))}
        ids = {vocab.setdefault(term, len(vocab)) for term in terms}
        frequency.update(ids)
        sets[key] = ids
    postings = defaultdict(list)
    for key, ids in sets.items():
        # A qualifying pair must share a term in both prefixes under one global order.
        length = len(ids)
        prefix_size = length - (PERCENT * length + 99) // 100 + 1
        ordered = sorted(ids, key=lambda term: (frequency[term], term))
        prefix = ordered[:prefix_size]
        candidates = {prev for term in prefix for prev in postings[term]}
        for prev in sorted(candidates):
            if not eligible(prev, key):
                continue
            other = sets[prev]
            if 100 * min(length, len(other)) < PERCENT * max(length, len(other)):
                continue
            shared = len(ids & other)
            union = length + len(other) - shared
            if 100 * shared >= PERCENT * union:
                yield prev, key, shared / union
        for term in prefix:
            postings[term].append(key)
