from pydantic import BaseModel
from uuid import UUID

class OrderBase(BaseModel):
    customer_id: UUID
    total_price: float
    status: str

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    total_price: float | None = None
    status: str | None = None

class OrderResponse(OrderBase):
    id: UUID

    class Config:
        orm_mode = True