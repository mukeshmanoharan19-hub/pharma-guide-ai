from loguru import logger

from app.core.config import settings

from app.retrieval.vector_store import (
    load_vector_store
)

from app.retrieval.bm25_store import (
    BM25Store
)

from app.retrieval.rrf import (
    reciprocal_rank_fusion
)

from app.retrieval.query_expansion import (
    generate_queries
)

class HybridRetriever:

    def __init__(self):

        logger.info(
            "Initializing HybridRetriever"
        )

        try:
            logger.info(
                "Loading vector store"
            )

            self.vector_store = (
                load_vector_store()
            )

            logger.success(
                "Vector store loaded successfully"
            )

        except Exception as e:

            logger.exception(
                f"Failed to load vector store: {str(e)}"
            )

            raise

        try:
            logger.info(
                "Loading BM25 store"
            )

            self.bm25_store = (
                BM25Store.load()
            )

            logger.success(
                "BM25 store loaded successfully"
            )

        except Exception as e:

            logger.exception(
                f"Failed to load BM25 store: {str(e)}"
            )

            raise

    def search(self, query):

        logger.info(
            f"Starting hybrid search "
            f"for query: {query}"
        )

        try:

            # Query Expansion
            logger.info(
                "Generating expanded queries"
            )

            expanded_queries = generate_queries(
                query,
                limit=settings.MULTI_QUERY_COUNT,
            )

            logger.info(
                f"Generated "
                f"{len(expanded_queries)} "
                f"expanded queries"
            )

            all_vector_results = []

            all_bm25_results = []

            # Retrieval loop
            for expanded_query in expanded_queries:

                logger.info(
                    f"Searching for expanded query: "
                    f"{expanded_query}"
                )

                # Vector Search
                logger.info(
                    "Running vector similarity search"
                )

                vector_results = (
                    self.vector_store.similarity_search(
                        expanded_query,
                        k=5
                    )
                )

                logger.info(
                    f"Vector search returned "
                    f"{len(vector_results)} results"
                )

                # BM25 Search
                logger.info(
                    "Running BM25 search"
                )

                bm25_results = (
                    self.bm25_store.search(
                        expanded_query,
                        top_k=5
                    )
                )

                logger.info(
                    f"BM25 search returned "
                    f"{len(bm25_results)} results"
                )

                all_vector_results.append(
                    vector_results
                )

                all_bm25_results.append(
                    bm25_results
                )

            # Reciprocal Rank Fusion
            logger.info(
                "Performing reciprocal rank fusion"
            )

            fused_results = reciprocal_rank_fusion(
                all_vector_results +
                all_bm25_results
            )

            logger.success(
                f"Hybrid retrieval completed "
                f"successfully. "
                f"Final fused results count: "
                f"{len(fused_results)}"
            )

            return fused_results

        except Exception as e:

            logger.exception(
                f"Error during hybrid retrieval: "
                f"{str(e)}"
            )

            raise