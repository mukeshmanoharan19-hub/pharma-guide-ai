import os
from langchain_community.vectorstores import FAISS
from app.ingestion.embeddings import get_embedding_model

VECTOR_DB_PATH = "data/vector_store"

def create_or_update_vector_store(chunks):

    embeddings = get_embedding_model()

    if os.path.exists(VECTOR_DB_PATH):

        vector_store = FAISS.load_local(
            VECTOR_DB_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )

        vector_store.add_documents(chunks)

    else:

        vector_store = FAISS.from_documents(
            chunks,
            embeddings
        )

    vector_store.save_local(VECTOR_DB_PATH)

def load_vector_store():

    try:

        embeddings = get_embedding_model()

        return FAISS.load_local(
            VECTOR_DB_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
    
    except Exception as e:
        print(f'Error while load vector store', e)