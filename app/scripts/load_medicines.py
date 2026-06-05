import json
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

from app.db.database import SessionLocal, engine
from app.models.medicine import Medicine

# This script loads medicines from a JSON file into the database.
# Usage: 
# docker exec -it pharma-guide-api bash
# python -m app.scripts.load_medicines

SEEDS_DIR = Path(__file__).resolve().parents[2] / "data" / "seeds"


def parse_iso_datetime(value: str | None):
    if not value:
        return None
    if value.endswith("Z"):
        value = value[:-1]
    return datetime.fromisoformat(value)

def main():

    db: Session = SessionLocal()

    # Ensure the medicines table exists before inserting data.
    Medicine.__table__.create(bind=engine, checkfirst=True)

    with open(SEEDS_DIR / "products.json", "r", encoding="utf-8") as f:
        medicines = json.load(f)
    
    print(f"Loading {len(medicines)} medicines into the database...")
    
    batch = []

    for item in medicines:
        batch.append(
            Medicine(
                title=item.get("title"),
                description=item.get("description"),
                compositions=item.get("compositions"),
                search_suggestion_keywords=item.get("searchSuggestionKeywords"),
                tags=item.get("tags"),
                sku=item.get("sku"),
                seo=item.get("seo"),
                unit_price=item.get("unitPrice"),
                maximum_retail_price=item.get("maximumRetailPrice"),
                discount=item.get("discount"),
                final_price=item.get("finalPrice"),
                thumbnail=item.get("thumbnail"),
                subcategory_id=item.get("subCategoryId", {}).get("$oid"),
                is_active=item.get("isActive", True),
                about_product=item.get("aboutProduct"),
                taxes=item.get("taxes"),
                created_at=parse_iso_datetime(item.get("createdAt")),
                updated_at=parse_iso_datetime(item.get("updatedAt")),
                discount_type=item.get("discountType"),
                max_order_quantity=item.get("maxOrderQuantity"),
                min_order_quantity=item.get("minOrderQuantity"),
                brand_tags=item.get("brandTags"),
                hsn_number=item.get("hsnNumber"),
                scheduled_drug=item.get("scheduledDrug"),
                salt_type=item.get("saltType"),
                prescription_req=item.get("prescriptionReq"),
                packing_type=item.get("packingType"),
                clinical_product_key=item.get("clinicalProductKey"),
                composition_key=item.get("compositionKey"),
                dosage_form=item.get("dosageForm"),
                release_type=item.get("releaseType"),
                route=item.get("route"),
            )
        )

    db.bulk_save_objects(batch)
    db.commit()

    print(f"Loaded {len(batch)} medicines")


if __name__ == "__main__":
    main()