from pydantic import BaseModel, Field
from uuid import UUID

class ProductBase(BaseModel):
    name: str
    category: str
    price: float
    stock_quantity: int
    is_active: bool

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    price: float | None = None
    stock_quantity: int | None = None
    is_active: bool | None = None

class ProductResponse(ProductBase):
    id: UUID

    class Config:
        orm_mode = True