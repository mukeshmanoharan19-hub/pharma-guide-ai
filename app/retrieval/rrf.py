from collections import defaultdict
from loguru import logger

def reciprocal_rank_fusion(results, k=60):

    scores = defaultdict(float)

    documents = {}
    
    for result_list in results:

        for rank, doc in enumerate(result_list): # Rank here is index number

            # It removes duplicate incase of same document page content
            doc_id = hash(
                doc.page_content
            )

            documents[doc_id] = doc

            scores[doc_id] += (
                1 / (k + rank + 1)
            )

    reranked = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return [
        documents[doc_id]
        for doc_id, _ in reranked
    ]