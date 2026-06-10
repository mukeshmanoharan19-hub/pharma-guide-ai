from __future__ import annotations

from loguru import logger

from app.evaluation.datasets import RagCase
from app.evaluation.metrics import citation_coverage, jaccard, theme_coverage
from app.evaluation.ragas_adapter import compute_ragas_metrics


def _answer_live(query: str) -> str:
    from app.services.rag_service import get_rag_service

    result = get_rag_service().ask(query)
    return result.get("answer", "") if isinstance(result, dict) else str(result)


def _answer_offline(case: RagCase) -> str:
    # Deterministic synthetic answer for CI/no-key mode.
    themes = ", ".join(case.expected_themes)
    cites = " ".join(f"[{c}]" for c in case.required_citations)
    return f"Policy summary: {themes}. References: {cites}"


def evaluate_rag(cases: list[RagCase], *, live: bool = False) -> dict:
    rows = []
    for case in cases:
        try:
            answer = _answer_live(case.query) if live else _answer_offline(case)
        except Exception as exc:  # fail-open per case
            logger.warning(f"RAG eval failed for {case.id}: {exc}")
            answer = ""

        expected_refs = set(x.lower() for x in case.required_citations)
        found_refs = {
            ref.lower()
            for ref in case.required_citations
            if ref.lower() in answer.lower()
        }
        row = {
            "id": case.id,
            "query": case.query,
            "answer": answer,
            "faithfulness": citation_coverage(answer, case.required_citations),
            "answer_relevancy": theme_coverage(answer, case.expected_themes),
            "context_precision": jaccard(found_refs, expected_refs),
            "context_recall": 1.0 if expected_refs.issubset(found_refs) else 0.0,
        }
        rows.append(row)

    n = max(len(rows), 1)
    custom = {
        "count": len(rows),
        "faithfulness": sum(r["faithfulness"] for r in rows) / n,
        "answer_relevancy": sum(r["answer_relevancy"] for r in rows) / n,
        "context_precision": sum(r["context_precision"] for r in rows) / n,
        "context_recall": sum(r["context_recall"] for r in rows) / n,
        "cases": rows,
    }
    custom["ragas"] = compute_ragas_metrics(samples=rows)
    return custom

