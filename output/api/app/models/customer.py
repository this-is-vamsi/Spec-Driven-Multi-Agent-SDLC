from sqlalchemy import Column, String, TIMESTAMP
from sqlalchemy.dialects.sqlite import UUID
from sqlalchemy.sql import func
from app.database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())