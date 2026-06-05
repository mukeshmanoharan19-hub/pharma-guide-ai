import cohere

from app.core.config import settings

co = cohere.Client(
    settings.COHERE_API_KEY
)

def rerank(query, documents):

    texts = [
        doc.page_content
        for doc in documents
    ]

    response = co.rerank(
        model="rerank-v3.5",
        query=query,
        documents=texts,
        top_n=5
    )

    return [
        documents[result.index]
        for result in response.results
    ]