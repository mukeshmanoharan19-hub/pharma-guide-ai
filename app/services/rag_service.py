import json

from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.retrieval.hybrid_search import HybridRetriever
from app.retrieval.reranker import rerank
from app.core.prompts import RAG_PROMPT, CHAT_RAG_PROMPT
from app.retrieval.compression import compress_documents
from app.retrieval.query_rewriter import rewrite_query
from app.retrieval.filters import apply_filters, extract_filters
from app.retrieval.context import build_grounded_context, dedupe_documents
from app.retrieval.verification import check_grounding, validate_retrieval
from app.observability.langsmith import runnable_config
from loguru import logger

GROUNDING_CAVEAT = (
    "\n\n_(Some details above could not be fully verified against our product "
    "information — please confirm with a pharmacist before relying on them.)_"
)

NO_CONTEXT_MESSAGE = (
    "Sorry, I couldn't find relevant information to answer your question."
)

llm = ChatOpenAI(
    api_key=settings.OPENAI_API_KEY,
    model=settings.MODEL_NAME,
    temperature=0
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

    def _prepare_context(
        self, query: str, history_text=None, summary_text=None
    ) -> tuple[str, list]:
        """Agentic retrieval pipeline (Phase 6).

        rewrite -> hybrid retrieval (multi-query) -> dedup -> metadata filter
        -> rerank -> compress -> dynamic, source-grounded context build.
        """
        # Step 1 — Conversation-aware query rewriting
        search_query = rewrite_query(query, history_text, summary_text)

        # Step 2 — Hybrid retrieval (internal multi-query expansion + RRF)
        logger.info("Starting hybrid retrieval")
        retrieved_docs = self.retriever.search(search_query)
        logger.info(f"Retrieved {len(retrieved_docs)} documents")

        # Step 3 — Duplicate removal
        deduped_docs = dedupe_documents(retrieved_docs)
        logger.info(f"After dedup: {len(deduped_docs)} documents")

        # Step 4 — Metadata filtering (off by default: RAG holds only
        # policies/FAQs; product/category/medicine-type filtering is handled in
        # the DB-backed medicine tools, not here).
        if settings.ENABLE_METADATA_FILTERS:
            filters = extract_filters(query)
            if filters.is_active():
                deduped_docs = apply_filters(deduped_docs, filters)

        # Step 5 — Reranking
        logger.info("Starting reranking")
        reranked_docs = rerank(search_query, deduped_docs)
        logger.info(f"Reranked {len(reranked_docs)} documents")

        # Step 6 — Compression
        logger.info("Starting context compression")
        compressed_docs = compress_documents(reranked_docs, search_query)
        logger.info(f"Compressed {len(compressed_docs)} documents")

        # Step 7 — Dynamic, source-grounded context build (token budget)
        context, sources = build_grounded_context(compressed_docs)
        logger.info(
            f"Built context ({len(context)} chars) from sources: {sources}"
        )

        return context, compressed_docs

    def _build_prompt(self, query, context, history_text=None, summary_text=None):
        """Use the conversation-aware prompt when history/summary is present."""
        if history_text or summary_text:
            return CHAT_RAG_PROMPT.format(
                summary=summary_text or "None.",
                history=history_text or "None.",
                context=context,
                question=query,
            )
        return RAG_PROMPT.format(context=context, question=query)

    def ask(self, query, history_text=None, summary_text=None):

        logger.info(
            f"Received user query: {query}"
        )

        try:

            context, compressed_docs = self._prepare_context(
                query, history_text, summary_text
            )

            # Retrieval validation — bail out cleanly when there is no grounding.
            if not validate_retrieval(compressed_docs) or not context.strip():
                return {
                    "answer": NO_CONTEXT_MESSAGE,
                    "grounded": False,
                    # "productsSuggestions": [],
                }


            # Step 5 — Create Prompt
            logger.info(
                "Creating RAG prompt"
            )

            prompt = self._build_prompt(
                query, context, history_text, summary_text
            )

            logger.info(
                f"Prompt created successfully. "
                f"Prompt length: "
                f"{len(prompt)} characters"
            )

            # Step 6 — Generate Response (plain text)
            logger.info(
                "Invoking LLM"
            )

            response = llm.invoke(
                prompt,
                config=runnable_config(
                    run_name="rag.generate_answer",
                    tags=["rag", "llm"],
                    metadata={"component": "RAGService", "mode": "sync"},
                ),
            )

            logger.success(
                "LLM response generated "
                "successfully"
            )

            answer = response.content if isinstance(response.content, str) else str(response.content)

            # Step 7 — Hallucination / grounding check
            grounding = check_grounding(answer, context)
            if not grounding.is_grounded:
                answer = f"{answer}{GROUNDING_CAVEAT}"

            result = {
                "answer": answer,
                "grounded": grounding.is_grounded,
                # "productsSuggestions": response.productsSuggestions
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

    def ask_stream(self, query, history_text=None, summary_text=None):
        """Stream the RAG response token by token."""
        logger.info(f"Received streaming user query: {query}")

        try:
            context, compressed_docs = self._prepare_context(
                query, history_text, summary_text
            )

            if not validate_retrieval(compressed_docs) or not context.strip():
                yield json.dumps({
                    "answer": NO_CONTEXT_MESSAGE,
                    # "productsSuggestions": [],
                })
                return

            # Step 5 — Create Prompt
            logger.info("Creating RAG prompt")
            prompt = self._build_prompt(
                query, context, history_text, summary_text
            )
            logger.info(f"Prompt created. Length: {len(prompt)} characters")

            # Step 6 — Stream Response (plain text tokens).
            # Each SSE payload carries the cumulative plain-text answer in an
            # {"answer": ...} envelope so newlines stay JSON-escaped (SSE-safe)
            # and the client can read a clean string.
            logger.info("Invoking LLM with streaming")

            accumulated = ""
            for chunk in llm.stream(
                prompt,
                config=runnable_config(
                    run_name="rag.generate_answer_stream",
                    tags=["phase10", "rag", "llm", "stream"],
                    metadata={"component": "RAGService", "mode": "stream"},
                ),
            ):
                token = getattr(chunk, "content", "") or ""
                if not isinstance(token, str):
                    token = str(token)
                if token:
                    accumulated += token
                    yield json.dumps({"answer": accumulated})

            logger.success("Streaming RAG pipeline completed successfully")

        except Exception as e:
            logger.exception(f"Error during streaming RAG pipeline: {str(e)}")
            raise


_default_rag_service: "RAGService | None" = None


def get_rag_service() -> "RAGService":
    """Return a lazily-created, process-wide RAGService.

    Sharing a single instance avoids loading the hybrid retriever / vector
    store more than once (it is reused by both the chat route and the agent
    graph).
    """
    global _default_rag_service
    if _default_rag_service is None:
        _default_rag_service = RAGService()
    return _default_rag_service