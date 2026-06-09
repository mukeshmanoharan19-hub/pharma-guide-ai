"""Build the RAG knowledge base.

IMPORTANT: the vector store / BM25 index holds ONLY company policies and FAQs.
The medicine catalog is NOT indexed here — it lives in the database and is
served through the medicine tools (search/details/alternatives). Product data
(``products.json``) is intentionally excluded from RAG ingestion.
"""

from pathlib import Path

from loguru import logger

from app.ingestion.knowledge_loader import load_text_documents
from app.ingestion.pdf_loader import load_pdf
from app.ingestion.text_splitter import split_documents

_SEEDS_DIR = Path(__file__).parent.parent.parent / "data" / "seeds"
# Company policies (PDFs) and FAQs (PDF / markdown / text).
POLICIES_DIR = _SEEDS_DIR / "policies"
FAQS_DIR = _SEEDS_DIR / "faqs"


def process_document() -> list:
    """Load and chunk the policy/FAQ knowledge base."""
    docs = []

    # Company policies (PDF).
    docs.extend(load_pdf(str(POLICIES_DIR)))

    # FAQs — support both PDF and markdown/text formats.
    if FAQS_DIR.exists():
        docs.extend(load_pdf(str(FAQS_DIR)))
        docs.extend(load_text_documents(str(FAQS_DIR)))

    logger.info(f"[ingestion] Loaded {len(docs)} policy/FAQ documents")

    if not docs:
        logger.warning(
            "[ingestion] No policy/FAQ documents found under "
            f"{POLICIES_DIR} or {FAQS_DIR}"
        )
        return []

    chunks = split_documents(docs)
    logger.info(f"[ingestion] Created {len(chunks)} chunks")
    return chunks


# if __name__ == "__main__":
#     chunks = process_document()
#     print(f"Total chunks created: {len(chunks)}")
