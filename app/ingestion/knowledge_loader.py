"""Loader for plain-text / markdown knowledge-base files (FAQs, policies).

The RAG knowledge base holds ONLY company policies and FAQs (the medicine
catalog lives in the database and is reached via tools). PDFs are handled by
``pdf_loader``; this module covers ``.md`` / ``.txt`` / ``.markdown`` files so
FAQs can simply be dropped into the seeds folder.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from langchain_core.documents import Document
from loguru import logger

_TEXT_EXTENSIONS = ("*.md", "*.markdown", "*.txt")


def load_text_documents(data_dir: str) -> List[Document]:
    """Load markdown/text files under ``data_dir`` as LangChain Documents."""
    base = Path(data_dir).resolve()
    documents: List[Document] = []

    if not base.exists():
        return documents

    for pattern in _TEXT_EXTENSIONS:
        for file_path in base.glob(f"**/{pattern}"):
            try:
                text = file_path.read_text(encoding="utf-8").strip()
            except Exception as exc:
                logger.warning(f"Failed to read knowledge file {file_path}: {exc}")
                continue
            if not text:
                continue
            documents.append(
                Document(
                    page_content=text,
                    metadata={"source": str(file_path), "doc_type": "faq"},
                )
            )

    return documents
