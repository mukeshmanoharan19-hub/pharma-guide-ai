from app.ingestion.json_loader import load_json
from app.ingestion.text_splitter import split_documents

def process_document(file_path):

    docs = load_json(file_path)

    print(f"Loaded {len(docs)} documents from {file_path}")

    chunks = split_documents(docs)

    return chunks