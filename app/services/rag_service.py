import json

from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.models.chat import ChatResponse
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

    def _prepare_context(self, query: str) -> tuple[str, list]:
        """Prepare context and retrieve documents."""
        # Step 1 — Hybrid Retrieval
        logger.info("Starting hybrid retrieval")
        retrieved_docs = self.retriever.search(query)
        logger.info(f"Retrieved {len(retrieved_docs)} documents")

        # Step 2 — Reranking
        logger.info("Starting reranking")
        reranked_docs = rerank(query, retrieved_docs)
        logger.info(f"Reranked {len(reranked_docs)} documents")

        # Step 3 — Compression
        logger.info("Starting context compression")
        compressed_docs = compress_documents(reranked_docs, query)
        logger.info(f"Compressed {len(compressed_docs)} documents")

        # Step 4 — Build Context
        context = "\n\n".join([doc.page_content for doc in compressed_docs])
        logger.info(f"Final context length: {len(context)} characters")

        return context, compressed_docs

    def ask(self, query):

        logger.info(
            f"Received user query: {query}"
        )

        try:

            context, compressed_docs = self._prepare_context(query)

            if not context.strip():
                return {
                    "answer": "Sorry, I couldn't find relevant information to answer your question."
                }


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
                prompt,
                response_format=ChatResponse
            )

            logger.success(
                "LLM response generated "
                "successfully"
            )

            result = {
                "answer": response.content,
                "productsSuggestions": response.productsSuggestions
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

    def ask_stream(self, query):
        """Stream the RAG response token by token."""
        logger.info(f"Received streaming user query: {query}")

        try:
            context, compressed_docs = self._prepare_context(query)

            if not context.strip():
                return {
                    "answer": "Sorry, I couldn't find relevant information to answer your question."
                }

            # Step 5 — Create Prompt
            logger.info("Creating RAG prompt")
            prompt = RAG_PROMPT.format(context=context, question=query)
            logger.info(f"Prompt created. Length: {len(prompt)} characters")

            # Step 6 — Stream Response
            logger.info("Invoking LLM with streaming")
            
            # 1. Bind the response format to the LLM first
            structured_llm = llm.with_structured_output(ChatResponse)

            # 2. Stream from the structured LLM
            stream = structured_llm.stream(prompt)

            for chunk in stream:
                # With structured streaming, chunks are often partial Pydantic objects 
                # or the final validated object depending on your provider.
                if chunk:
                    # Use model_dump(mode="json") to safely convert Pydantic to a JSON-serializable dict
                    yield json.dumps(chunk.model_dump(mode="json"))
                        
            logger.success("Streaming RAG pipeline completed successfully")

        except Exception as e:
            logger.exception(f"Error during streaming RAG pipeline: {str(e)}")
            raise