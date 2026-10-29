from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    isbn = Column(String, unique=True, index=True)
    available = Column(Boolean, default=True)
