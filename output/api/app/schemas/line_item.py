from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class LineItemCreate(BaseModel):
    product_id: UUID
    quantity: int

class LineItemResponse(BaseModel):
    id: UUID
    order_id: UUID
    product_id: UUID
    quantity: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    deleted_at: datetime | None

    class Config:
        orm_mode = True