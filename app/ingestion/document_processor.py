from app.ingestion.json_loader import load_json
from app.ingestion.pdf_loader import load_pdf
from app.ingestion.text_splitter import split_documents
from pathlib import Path

products_file_path = Path(__file__).parent.parent.parent / "data" / "seeds" / "products.json"
policy_files_path = Path(__file__).parent.parent.parent / "data" / "seeds" / "policies"

def process_document() -> list[dict]:
    docs = []
    
    product_docs = load_json(products_file_path)
    docs.extend(product_docs)
    
    pdf_docs = load_pdf(str(policy_files_path))
    docs.extend(pdf_docs)

    print(f"[DEBUG] Total documents loaded: {len(docs)}")    

    chunks = split_documents(docs)

    return chunks

if __name__ == "__main__":
    chunks = process_document()
    print(f"Total chunks created: {len(chunks)}")