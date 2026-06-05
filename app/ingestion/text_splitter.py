from langchain_experimental.text_splitter import SemanticChunker

from langchain_openai import OpenAIEmbeddings

from app.core.config import settings

def split_documents(documents):
    embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY ,model=settings.EMBEDDING_MODEL)
    splitter = SemanticChunker(embeddings)
    return splitter.split_documents(documents)