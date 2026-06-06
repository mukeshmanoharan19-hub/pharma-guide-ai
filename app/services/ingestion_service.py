from loguru import logger
from app.ingestion.document_processor import process_document
from app.retrieval.vector_store import create_or_update_vector_store
from app.retrieval.bm25_store import BM25Store

class IngestionService:

    @staticmethod
    def ingest():

        try:

            chunks = process_document()

            logger.info(
                f"Document processed successfully. "
                f"Total chunks: {len(chunks)}"
            )

            # Vector store update
            logger.info("Updating vector store")

            create_or_update_vector_store(chunks)

            logger.info("Vector store updated successfully")

            # BM25 Store
            try:
                logger.info("Loading BM25 store")

                bm25_store = BM25Store.load()

                logger.info("BM25 store loaded successfully")

            except Exception as e:
                logger.warning(
                    f"Failed to load BM25 store. "
                    f"Creating new store. Error: {str(e)}"
                )

            bm25_store = BM25Store()

            # Add documents to BM25
            logger.info("Adding documents to BM25 store")

            bm25_store.add_documents(chunks)

            bm25_store.save()

            logger.info("BM25 store updated and saved")


            logger.success(
                f"Ingestion completed successfully "
            )

            return {
                "status": "success",
                "chunks": len(chunks)
            }

        except Exception as e:
            logger.exception(
                f"Error occurred during ingestion: {str(e)}"
            )

            return {
                "status": "failed",
                "error": str(e)
            }

        finally:
            logger.info("Database session closed")