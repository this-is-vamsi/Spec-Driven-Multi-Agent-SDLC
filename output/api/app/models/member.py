from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.sql import func
from app.database import Base

class Member(Base):
    __tablename__ = 'members'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    joined_date = Column(Date, server_default=func.now())
