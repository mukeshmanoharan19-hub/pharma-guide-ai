from langchain_community.document_loaders import JSONLoader


# Custom function to extract metadata fields for each document
def metadata_func(record: dict, metadata: dict) -> dict:
    metadata["sku"] = record.get("sku")
    return metadata

def load_json(file_path):
    loader = JSONLoader(
        file_path=file_path, 
        text_content=False, 
        jq_schema=".[]", 
        metadata_func=metadata_func
    )
    documents = loader.load()
    return documents