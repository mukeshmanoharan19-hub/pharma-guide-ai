from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.retrieval.hybrid_search import HybridRetriever
from app.retrieval.reranker import rerank
from app.core.prompts import RAG_PROMPT
from app.retrieval.compression import compress_documents
from loguru import logger

# Initialize LLM
logger.info(
    f"Initializing LLM model: "
    f"{settings.MODEL_NAME}"
)

llm = ChatOpenAI(
    api_key=settings.OPENAI_API_KEY,
    model=settings.MODEL_NAME,
    temperature=0
)

logger.success(
    "LLM initialized successfully"
)


class RAGService:

    def __init__(self):

        logger.info(
            "Initializing RAGService"
        )

        try:

            self.retriever = (
                HybridRetriever()
            )

            logger.success(
                "HybridRetriever initialized "
                "successfully"
            )

        except Exception as e:

            logger.exception(
                f"Failed to initialize "
                f"HybridRetriever: {str(e)}"
            )

            raise

    def ask(self, query):

        logger.info(
            f"Received user query: {query}"
        )

        try:

            # Step 1 — Hybrid Retrieval
            logger.info(
                "Starting hybrid retrieval"
            )

            retrieved_docs = (
                self.retriever.search(query)
            )

            logger.info(
                f"Hybrid retrieval completed. "
                f"Retrieved "
                f"{len(retrieved_docs)} documents"
            )

            # Step 2 — Reranking
            logger.info(
                "Starting reranking"
            )

            reranked_docs = rerank(
                query,
                retrieved_docs
            )

            logger.info(
                f"Reranking completed. "
                f"Reranked "
                f"{len(reranked_docs)} documents"
            )

            # Step 3 — Compression
            logger.info(
                "Starting context compression"
            )

            compressed_docs = compress_documents(reranked_docs, query)
            
            logger.info(
                f"Compression completed. "
                f"Compressed documents count: "
                f"{len(compressed_docs)}"
            )

            # Step 4 — Build Context
            logger.info(
                "Building final context"
            )

            context = "\n\n".join([
                doc.page_content
                for doc in compressed_docs
            ])

            logger.info(
                f"Final context length: "
                f"{len(context)} characters"
            )

            # Step 5 — Create Prompt
            logger.info(
                "Creating RAG prompt"
            )

            prompt = RAG_PROMPT.format(
                context=context,
                question=query
            )

            logger.info(
                f"Prompt created successfully. "
                f"Prompt length: "
                f"{len(prompt)} characters"
            )

            # Step 6 — Generate Response
            logger.info(
                "Invoking LLM"
            )

            response = llm.invoke(
                prompt
            )

            logger.success(
                "LLM response generated "
                "successfully"
            )

            result = {
                "answer": response.content,
                # "sources": [
                #     {
                #         "page":
                #         doc.metadata.get("page"),

                #         "source":
                #         doc.metadata.get("source")
                #     }
                #     for doc in compressed_docs
                # ]
            }

            logger.success(
                "RAG pipeline completed "
                "successfully"
            )

            return result

        except Exception as e:

            logger.exception(
                f"Error during RAG pipeline "
                f"execution: {str(e)}"
            )

            raise