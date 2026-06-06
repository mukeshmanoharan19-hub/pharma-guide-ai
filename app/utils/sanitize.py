import json
from pathlib import Path

# Input and output file paths
INPUT_FILE = "data/seeds/products-old.json"
OUTPUT_FILE = "data/seeds/products-new.json"

# Fields to remove
FIELDS_TO_REMOVE = {
    "selectedSections",
    "translations",
    "collections",
    "consumption",
    "composition",
    "image",
    "images",
    "associatedProducts",
    "hasVariation",
    "variation",
}


def remove_fields(data):
    """
    Recursively remove unwanted fields from JSON data and append product metadata
    into aboutProduct when available.
    """

    if isinstance(data, dict):
        cleaned = {
            key: remove_fields(value)
            for key, value in data.items()
            if key not in FIELDS_TO_REMOVE
        }

        if "aboutProduct" in cleaned and isinstance(cleaned["aboutProduct"], dict):
            for field in ("title", "compositions", "sku", "finalPrice", "thumbnail", "brandTags"):
                if field in cleaned:
                    cleaned["aboutProduct"][field] = cleaned[field]

        return cleaned["aboutProduct"] if "aboutProduct" in cleaned else cleaned

    elif isinstance(data, list):
        return [remove_fields(item) for item in data]

    return data


def sanitize_json():
    input_path = Path(INPUT_FILE)
    output_path = Path(OUTPUT_FILE)
    count = 50
    
    # Read JSON file
    with open(input_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Remove unwanted fields
    sanitized_data = remove_fields(data)

    # Write sanitized JSON
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            sanitized_data[:count],  # Limit to first 50 products for testing
            file,
            ensure_ascii=False,
            indent=2
        )

    print(f"Sanitized JSON saved to: {output_path}")


if __name__ == "__main__":
    sanitize_json()