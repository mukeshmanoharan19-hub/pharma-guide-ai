from loguru import logger

from app.ingestion.document_processor import process_document
from app.retrieval.bm25_store import BM25Store
from app.retrieval.vector_store import (
    create_or_update_vector_store,
    reset_vector_store,
)


class IngestionService:

    @staticmethod
    def ingest():
        """Rebuild the policy/FAQ knowledge base from scratch.

        Existing vector + BM25 indexes are cleared first so stale content (e.g.
        previously-indexed product data) is removed, then the fresh policy/FAQ
        chunks are indexed.
        """
        try:
            # 1. Clear existing indexes so we start from a clean slate.
            logger.info("Clearing existing vector and BM25 stores")
            reset_vector_store()
            BM25Store.clear()

            # 2. Load + chunk the policy/FAQ knowledge base (no product data).
            chunks = process_document()

            if not chunks:
                logger.warning("No documents to ingest; stores left empty.")
                return {"status": "success", "chunks": 0}

            logger.info(
                f"Document processed successfully. Total chunks: {len(chunks)}"
            )

            # 3. Build a fresh vector store.
            logger.info("Building vector store")
            create_or_update_vector_store(chunks)
            logger.info("Vector store built successfully")

            # 4. Build a fresh BM25 store.
            logger.info("Building BM25 store")
            bm25_store = BM25Store()
            bm25_store.add_documents(chunks)
            bm25_store.save()
            logger.info("BM25 store built and saved")

            logger.success("Ingestion completed successfully")

            return {"status": "success", "chunks": len(chunks)}

        except Exception as e:
            logger.exception(f"Error occurred during ingestion: {str(e)}")
            return {"status": "failed", "error": str(e)}
