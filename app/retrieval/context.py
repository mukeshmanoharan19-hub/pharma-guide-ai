"""Context optimization (Phase 6): duplicate removal + dynamic, grounded build.

- ``dedupe_documents`` removes near/exact duplicates (same SKU or identical
  content) while preserving rank order.
- ``build_grounded_context`` assembles a context string sized to a token
  budget, tagging each chunk with its source so the generator (and the
  grounding check) can attribute facts.
"""

from __future__ import annotations

from typing import List, Tuple

from app.core.config import settings
from app.memory.tokens import estimate_tokens
from app.retrieval.filters import parse_record


def _doc_key(doc) -> str:
    """Stable identity for de-duplication: prefer SKU, else content hash."""
    sku = (getattr(doc, "metadata", None) or {}).get("sku")
    if sku:
        return f"sku:{sku}"
    record = parse_record(doc)
    if record.get("sku"):
        return f"sku:{record['sku']}"
    content = (getattr(doc, "page_content", "") or "").strip()
    return f"hash:{hash(content)}"


def dedupe_documents(documents: List) -> List:
    """Remove duplicate documents, keeping the first (highest-ranked) instance."""
    seen = set()
    unique = []
    for doc in documents:
        key = _doc_key(doc)
        if key in seen:
            continue
        seen.add(key)
        unique.append(doc)
    return unique


def _source_label(doc) -> str:
    meta = getattr(doc, "metadata", None) or {}
    sku = meta.get("sku") or parse_record(doc).get("sku")
    if sku:
        return f"sku={sku}"
    source = meta.get("source")
    return f"source={source}" if source else "source=catalog"


def build_grounded_context(
    documents: List,
    token_budget: int | None = None,
) -> Tuple[str, List[str]]:
    """Build a source-tagged context string within a token budget.

    Returns ``(context, sources)`` where ``sources`` lists the labels actually
    included (useful for grounding/citation).
    """
    budget = token_budget or settings.RAG_CONTEXT_TOKEN_BUDGET
    parts: List[str] = []
    sources: List[str] = []
    running = 0

    for doc in documents:
        content = (getattr(doc, "page_content", "") or "").strip()
        if not content:
            continue
        label = _source_label(doc)
        block = f"[{label}]\n{content}"
        cost = estimate_tokens(block)

        # Always include at least one block even if it alone exceeds budget.
        if parts and running + cost > budget:
            break

        parts.append(block)
        sources.append(label)
        running += cost

    return "\n\n".join(parts), sources
