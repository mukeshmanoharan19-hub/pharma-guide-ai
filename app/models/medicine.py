from sqlalchemy import Boolean, Column, DateTime, Float, Integer, JSON, String, Text

from app.db.database import Base


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    compositions = Column(Text, nullable=True)
    search_suggestion_keywords = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    sku = Column(String, nullable=True, index=True)
    seo = Column(JSON, nullable=True)
    unit_price = Column(Float, nullable=True)
    maximum_retail_price = Column(Float, nullable=True)
    discount = Column(Float, nullable=True)
    final_price = Column(Float, nullable=True)
    thumbnail = Column(String, nullable=True)
    subcategory_id = Column(String, nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=True)
    about_product = Column(JSON, nullable=True)
    taxes = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    discount_type = Column(String, nullable=True)
    max_order_quantity = Column(Integer, nullable=True)
    min_order_quantity = Column(Integer, nullable=True)
    brand_tags = Column(JSON, nullable=True)
    hsn_number = Column(String, nullable=True)
    scheduled_drug = Column(String, nullable=True)
    salt_type = Column(String, nullable=True)
    prescription_req = Column(Boolean, nullable=True)
    packing_type = Column(String, nullable=True)
    clinical_product_key = Column(String, nullable=True)
    composition_key = Column(String, nullable=True)
    dosage_form = Column(String, nullable=True)
    release_type = Column(String, nullable=True)
    route = Column(String, nullable=True)
    # Inventory (Phase 2). Null is treated as "in stock" for mock/seed data.
    stock_quantity = Column(Integer, nullable=True)