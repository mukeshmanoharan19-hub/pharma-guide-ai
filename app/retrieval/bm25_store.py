import pickle
import os
from loguru import logger

from rank_bm25 import BM25Okapi

BM25_PATH = "data/bm25"


class BM25Store:

    def __init__(self):

        self.documents = []
        self.tokenized_docs = []
        self.bm25 = None

    @staticmethod
    def clear():
        """Delete the persisted BM25 index so the next build starts clean."""
        pkl_path = f"{BM25_PATH}/bm25.pkl"
        if os.path.exists(pkl_path):
            os.remove(pkl_path)
            logger.info(f"Cleared BM25 store at {pkl_path}")

    @staticmethod
    def load():

        store = BM25Store()

        try:

            with open(
                f"{BM25_PATH}/bm25.pkl",
                "rb"
            ) as f:

                store.documents = pickle.load(f)

            print("Loaded documents:", len(store.documents))
            
            logger.info(f"Loaded Documents: {len(store.documents)}")

            store.tokenized_docs = [
                doc.page_content.split()
                for doc in store.documents
            ]

            logger.info(f"Tokenized docs: {len(store.tokenized_docs)}")
            

            if store.tokenized_docs:

                store.bm25 = BM25Okapi(
                    store.tokenized_docs
                )

            return store

        except Exception as e:

            print("Load error:", e)

            return store
    
    def add_documents(self, chunks):

        self.documents.extend(chunks)

        self.tokenized_docs = [
            doc.page_content.split()
            for doc in self.documents
        ]

        self.bm25 = BM25Okapi(
            self.tokenized_docs
        )

    def save(self):

        os.makedirs(
            BM25_PATH,
            exist_ok=True
        )

        with open(
            f"{BM25_PATH}/bm25.pkl",
            "wb"
        ) as f:

            # Save only documents
            pickle.dump(
                self.documents,
                f
            )

    def search(
        self,
        query,
        top_k=10
    ):

        if not self.bm25:
            raise ValueError(
                "BM25 index is not initialized"
            )

        tokenized_query = query.split()

        scores = self.bm25.get_scores(
            tokenized_query
        )

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:top_k]

        return [
            self.documents[i]
            for i in ranked_indices
        ]