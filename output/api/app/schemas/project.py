from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str
    description: str

class ProjectUpdate(BaseModel):
    name: str
    description: str

class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True