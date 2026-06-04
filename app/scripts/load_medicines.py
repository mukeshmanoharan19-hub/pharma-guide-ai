import json

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.medicine import Medicine


def main():

    db: Session = SessionLocal()

    with open("data/products.json", "r", encoding="utf-8") as f:
        medicines = json.load(f)

    batch = []

    for item in medicines:
        batch.append(
            Medicine(
                name=item.get("name"),
                generic_name=item.get("generic_name"),
                category=item.get("category"),
                symptoms=item.get("symptoms", []),
                side_effects=item.get("side_effects", []),
                dosage=item.get("dosage"),
                stock=item.get("stock", 0),
            )
        )

    db.bulk_save_objects(batch)
    db.commit()

    print(f"Loaded {len(batch)} medicines")


if __name__ == "__main__":
    main()