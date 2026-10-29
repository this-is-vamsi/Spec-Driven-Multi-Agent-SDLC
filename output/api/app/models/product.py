from sqlalchemy import Column, String, Integer, Boolean, DECIMAL, TIMESTAMP
from sqlalchemy.dialects.sqlite import UUID
from sqlalchemy.sql import func
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(DECIMAL, nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())