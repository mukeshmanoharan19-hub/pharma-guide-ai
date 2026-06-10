from __future__ import annotations

from pathlib import Path
from typing import Any

from loguru import logger

from app.evaluation.datasets import RetrievalCase
from app.evaluation.metrics import hit_rate, precision_at_k, recall_at_k
from app.retrieval.bm25_store import BM25Store


def _extract_doc_id(doc: Any) -> str:
    metadata = getattr(doc, "metadata", {}) or {}
    source = str(metadata.get("source") or metadata.get("file_path") or "").lower()
    if source:
        # Keep semantic-ish source id (filename stem).
        stem = Path(source).stem
        if stem:
            return stem
    text = (getattr(doc, "page_content", "") or "").lower()
    # Fallback: first few words hashed-ish surrogate.
    return "-".join(text.split()[:3]) if text else "unknown"


def _search_live(query: str):
    from app.retrieval.hybrid_search import HybridRetriever

    retriever = HybridRetriever()
    return retriever.search(query)


def _search_offline(query: str):
    bm25 = BM25Store.load()
    if not bm25.documents:
        logger.warning("BM25 store empty; offline retrieval eval returns no docs.")
        return []
    return bm25.search(query, top_k=5)


def evaluate_retrieval(
    cases: list[RetrievalCase],
    *,
    k: int = 5,
    live: bool = False,
) -> dict:
    rows = []
    for case in cases:
        docs = _search_live(case.query) if live else _search_offline(case.query)
        predicted = [_extract_doc_id(doc) for doc in docs]
        expected = set(x.lower() for x in case.relevant_ids)
        predicted_norm = [x.lower() for x in predicted]
        row = {
            "id": case.id,
            "query": case.query,
            "category": case.category,
            "expected": list(expected),
            "predicted": predicted_norm[:k],
            "recall_at_k": recall_at_k(expected, predicted_norm, k),
            "precision_at_k": precision_at_k(expected, predicted_norm, k),
            "hit_rate": hit_rate(expected, predicted_norm, k),
        }
        rows.append(row)

    n = max(len(rows), 1)
    return {
        "count": len(rows),
        "recall_at_k": sum(r["recall_at_k"] for r in rows) / n,
        "precision_at_k": sum(r["precision_at_k"] for r in rows) / n,
        "hit_rate": sum(r["hit_rate"] for r in rows) / n,
        "cases": rows,
    }

