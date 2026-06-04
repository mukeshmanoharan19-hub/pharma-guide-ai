from sqlalchemy import Column, Integer, String
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    email = Column(String, unique=True)

    password = Column(String)

    full_name = Column(String)