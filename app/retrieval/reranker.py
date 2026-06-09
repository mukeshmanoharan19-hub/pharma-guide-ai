import cohere

from app.core.config import settings

co = cohere.Client(
    settings.COHERE_API_KEY
)

def rerank(query, documents, top_n=None):

    if not documents:
        return []

    if top_n is None:
        top_n = settings.RERANK_TOP_N

    texts = [
        doc.page_content
        for doc in documents
    ]

    response = co.rerank(
        model="rerank-v3.5",
        query=query,
        documents=texts,
        top_n=min(top_n, len(texts))
    )

    return [
        documents[result.index]
        for result in response.results
    ]