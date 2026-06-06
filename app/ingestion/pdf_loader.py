from langchain_community.document_loaders import PyMuPDFLoader
from pathlib import Path

def load_pdf(data_dir: str) -> list[dict]:
    # Use project root data folder
    data_path = Path(data_dir).resolve()
    documents = []

    # PDF files
    pdf_files = list(data_path.glob('**/*.pdf'))
    # print(f"[DEBUG] Found {len(pdf_files)} PDF files: {[str(f) for f in pdf_files]}")
    for pdf_file in pdf_files:
        # print(f"[DEBUG] Loading PDF: {pdf_file}")
        try:
            loader = PyMuPDFLoader(str(pdf_file))
            loaded = loader.load()
            # print(f"[DEBUG] Loaded {len(loaded)} PDF docs from {pdf_file}")
            documents.extend(loaded)
        except Exception as e:
            print(f"[ERROR] Failed to load PDF {pdf_file}: {e}")
    
    return documents

# if __name__ == "__main__":
#     # Example usage
#     data_directory = Path(__file__).parent.parent.parent / "data" / "seeds" / "policies"
#     loaded_docs = load_pdf(str(data_directory))
#     print(f"Total PDF documents loaded: {len(loaded_docs)}")