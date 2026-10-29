from pydantic import BaseModel, EmailStr
from datetime import date

class MemberBase(BaseModel):
    name: str
    email: EmailStr

class MemberCreate(MemberBase):
    pass

class MemberResponse(MemberBase):
    id: int
    joined_date: date

    class Config:
        orm_mode = True
