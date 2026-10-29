from pydantic import BaseModel, EmailStr
from uuid import UUID

class CustomerBase(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None

class CustomerResponse(CustomerBase):
    id: UUID

    class Config:
        orm_mode = True