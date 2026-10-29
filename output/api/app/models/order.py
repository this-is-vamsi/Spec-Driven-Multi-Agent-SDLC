from sqlalchemy import Column, String, Integer, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.sqlite import UUID
from sqlalchemy.sql import func
from app.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID, primary_key=True, index=True)
    customer_id = Column(UUID, ForeignKey("customers.id"), nullable=False)
    total_price = Column(DECIMAL, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())