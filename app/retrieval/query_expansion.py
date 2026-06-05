from langchain_openai import ChatOpenAI

from app.core.config import settings

llm = ChatOpenAI(
    api_key=settings.OPENAI_API_KEY,
    model=settings.MODEL_NAME,
    temperature=0
)

def generate_queries(query: str, limit: int = 1):
    if limit == 1:
        return [query]
    
    prompt = f"""
    You are a query expansion assistant.

    Generate {limit} different search queries
    related to the user's question.

    Rules:
    1. Keep meaning same
    2. Use synonyms
    3. Use technical variations
    4. Keep queries concise
    5. Return one query per line

    User Query:
    {query}
    """

    response = llm.invoke(prompt)

    queries = response.content.split("\n")

    cleaned_queries = [
        q.strip("- ").strip()
        for q in queries
        if q.strip()
    ]

    # Add original query
    cleaned_queries.insert(0, query)

    return list(set(cleaned_queries))[:limit]