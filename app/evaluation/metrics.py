from __future__ import annotations

from typing import Iterable


def _safe_div(a: float, b: float) -> float:
    if b == 0:
        return 0.0
    return a / b


def recall_at_k(expected: set[str], predicted: list[str], k: int) -> float:
    top = set(predicted[:k])
    return _safe_div(len(expected.intersection(top)), len(expected))


def precision_at_k(expected: set[str], predicted: list[str], k: int) -> float:
    top = set(predicted[:k])
    return _safe_div(len(expected.intersection(top)), len(top))


def hit_rate(expected: set[str], predicted: list[str], k: int) -> float:
    top = set(predicted[:k])
    return 1.0 if expected.intersection(top) else 0.0


def theme_coverage(answer: str, themes: Iterable[str]) -> float:
    text = (answer or "").lower()
    t = [x.lower() for x in themes]
    if not t:
        return 1.0
    found = sum(1 for theme in t if theme in text)
    return found / len(t)


def citation_coverage(answer: str, required_citations: Iterable[str]) -> float:
    text = (answer or "").lower()
    refs = [x.lower() for x in required_citations]
    if not refs:
        return 1.0
    found = sum(1 for ref in refs if ref in text)
    return found / len(refs)


def jaccard(a: set[str], b: set[str]) -> float:
    union = a.union(b)
    if not union:
        return 1.0
    return len(a.intersection(b)) / len(union)

