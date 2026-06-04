from sqlalchemy import Column, Integer, String, JSON

from app.db.database import Base


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True)

    name = Column(String)

    generic_name = Column(String)

    category = Column(String)

    symptoms = Column(JSON)

    side_effects = Column(JSON)

    dosage = Column(String)

    stock = Column(Integer)