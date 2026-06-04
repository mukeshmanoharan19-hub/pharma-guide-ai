import json
from pathlib import Path

# Input and output file paths
INPUT_FILE = "data/seeds/products.json"
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
    Recursively remove unwanted fields from JSON data.
    """

    if isinstance(data, dict):
        return {
            key: remove_fields(value)
            for key, value in data.items()
            if key not in FIELDS_TO_REMOVE
        }

    elif isinstance(data, list):
        return [remove_fields(item) for item in data]

    return data


def sanitize_json():
    input_path = Path(INPUT_FILE)
    output_path = Path(OUTPUT_FILE)

    # Read JSON file
    with open(input_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Remove unwanted fields
    sanitized_data = remove_fields(data)

    # Write sanitized JSON
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            sanitized_data,
            file,
            ensure_ascii=False,
            indent=2
        )

    print(f"Sanitized JSON saved to: {output_path}")


if __name__ == "__main__":
    sanitize_json()