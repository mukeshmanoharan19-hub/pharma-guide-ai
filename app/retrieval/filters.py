"""Retrieval filtering (Phase 6).

Product documents are stored as the raw JSON record in ``page_content``, so we
can parse structured fields and apply metadata / category / medicine-type
filters after retrieval. A lightweight heuristic extractor infers obvious
filters from the query; callers may also pass explicit filters.
"""

from __future__ import annotations

import json
from typing import List, Optional

from loguru import logger
from pydantic import BaseModel

# Common dosage forms (medicine-type) we can detect in free text.
_DOSAGE_FORMS = [
    "tablet",
    "capsule",
    "syrup",
    "suspension",
    "injection",
    "drops",
    "cream",
    "ointment",
    "gel",
    "powder",
    "spray",
    "lotion",
    "sachet",
    "inhaler",
]


class RetrievalFilters(BaseModel):
    """Structured, optional filters applied to retrieved product documents."""

    dosage_form: Optional[str] = None
    prescription_req: Optional[bool] = None
    subcategory_id: Optional[str] = None
    salt_type: Optional[str] = None

    def is_active(self) -> bool:
        return any(
            v is not None
            for v in (
                self.dosage_form,
                self.prescription_req,
                self.subcategory_id,
                self.salt_type,
            )
        )


def parse_record(doc) -> dict:
    """Best-effort parse of a document's JSON product record."""
    content = getattr(doc, "page_content", "") or ""
    try:
        record = json.loads(content)
        return record if isinstance(record, dict) else {}
    except (ValueError, TypeError):
        return {}


def extract_filters(query: str) -> RetrievalFilters:
    """Infer obvious filters from the query text (conservative heuristics)."""
    q = (query or "").lower()
    filters = RetrievalFilters()

    for form in _DOSAGE_FORMS:
        if form in q:
            filters.dosage_form = form
            break

    if any(p in q for p in ("over the counter", "otc", "without prescription", "no prescription")):
        filters.prescription_req = False
    elif any(p in q for p in ("prescription only", "needs prescription", "with prescription")):
        filters.prescription_req = True

    return filters


def _matches(record: dict, filters: RetrievalFilters) -> bool:
    if not record:
        # Can't verify a non-product document against product filters.
        return False

    if filters.dosage_form is not None:
        value = str(record.get("dosage_form") or "").lower()
        if filters.dosage_form.lower() not in value:
            return False

    if filters.prescription_req is not None:
        if bool(record.get("prescription_req")) != filters.prescription_req:
            return False

    if filters.subcategory_id is not None:
        if str(record.get("subcategory_id") or "") != str(filters.subcategory_id):
            return False

    if filters.salt_type is not None:
        value = str(record.get("salt_type") or "").lower()
        if filters.salt_type.lower() not in value:
            return False

    return True


def apply_filters(documents: List, filters: RetrievalFilters) -> List:
    """Filter documents by ``filters``; never starve the answer to empty.

    If filtering removes everything, the original documents are returned so the
    generator still has context to work with.
    """
    if not filters or not filters.is_active():
        return documents

    filtered = [doc for doc in documents if _matches(parse_record(doc), filters)]

    if not filtered:
        logger.info(
            "Metadata filters {} removed all documents; falling back to unfiltered.",
            filters.model_dump(exclude_none=True),
        )
        return documents

    logger.info(
        "Metadata filters {} kept {}/{} documents.",
        filters.model_dump(exclude_none=True),
        len(filtered),
        len(documents),
    )
    return filtered
