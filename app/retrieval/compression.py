from langchain_classic.retrievers.document_compressors import EmbeddingsFilter
from langchain_openai import OpenAIEmbeddings
from app.core.config import settings
from loguru import logger

# Create embeddings once
embeddings = OpenAIEmbeddings(
    api_key=settings.OPENAI_API_KEY,
    model=settings.EMBEDDING_MODEL
)


def compress_documents(documents, query, top: int = 5, similarity_threshold: int = 0.3):
    """
    Compress and filter documents based on semantic similarity.
    """

    try:
        if not documents:
            logger.warning("No documents received for compression")
            return []

        logger.info(f"Compressing {len(documents)} documents")

        # Lower threshold OR use top-k
        embeddings_filter = EmbeddingsFilter(
            embeddings=embeddings,
            similarity_threshold=similarity_threshold,
            k=top   # Always keep top matches
        )

        compressed_docs = embeddings_filter.compress_documents(
            documents=documents,
            query=query
        )

        logger.info(f"Compressed to {len(compressed_docs)} documents")

        # Fallback if empty
        if not compressed_docs:
            logger.warning(
                "Compression returned empty list. Returning original documents."
            )
            return documents[:top]

        return compressed_docs

    except Exception as e:
        logger.exception(f"Document compression failed: {str(e)}")

        # Safe fallback
        return documents[:top]