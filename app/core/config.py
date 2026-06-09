from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str
    BACKEND_URL: str
    CLIENT_URL: str
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    OPENAI_API_KEY: str
    COHERE_API_KEY: str
    MODEL_NAME: str
    EMBEDDING_MODEL: str

    # --- Phase 0: Foundation additions ---

    # Redis (session memory, used from Phase 1 onwards)
    REDIS_URL: str = "redis://localhost:6379/0"

    # LangSmith tracing (wired in Phase 10; safe defaults so it stays off)
    LANGCHAIN_TRACING_V2: bool = False
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: str = "pharma-guide-ai"

    # Token budgets for context window management (Phase 1)
    MAX_CONTEXT_TOKENS: int = 8000
    SUMMARY_THRESHOLD_TOKENS: int = 6000
    RECENT_MESSAGE_WINDOW: int = 10

    # Rate limiting (enforced in Phase 12; value available early for wiring)
    RATE_LIMIT_PER_MINUTE: int = 30

    # --- Phase 3: LangGraph agent foundation ---
    # Connection pool size for the Postgres checkpoint saver.
    CHECKPOINT_POOL_SIZE: int = 5

    # --- Phase 4: Supervisor agent ---
    # Below this primary-intent confidence the supervisor falls back to the
    # general conversation route instead of a specialist agent.
    INTENT_CONFIDENCE_THRESHOLD: float = 0.45

    # --- Phase 6: Agentic RAG ---
    # Conversation-aware query rewriting before retrieval.
    ENABLE_QUERY_REWRITE: bool = True
    # Number of search queries to generate per turn (1 disables expansion).
    MULTI_QUERY_COUNT: int = 3
    # Product metadata/category/medicine-type filtering. Off for the RAG path:
    # RAG indexes only policies/FAQs, so product filtering lives in the
    # DB-backed medicine tools (medicine_service.search_medicines), not here.
    ENABLE_METADATA_FILTERS: bool = False
    # Post-generation faithfulness / hallucination check.
    ENABLE_HALLUCINATION_CHECK: bool = True
    # Minimum retrieved documents for the answer to be considered grounded.
    RETRIEVAL_MIN_RESULTS: int = 1
    # Token budget for the assembled RAG context (dynamic context building).
    RAG_CONTEXT_TOKEN_BUDGET: int = 3000
    # Documents kept after reranking.
    RERANK_TOP_N: int = 5

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
