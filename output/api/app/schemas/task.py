from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.models.task import TaskStatus

class TaskCreate(BaseModel):
    title: str
    description: str
    due_date: datetime

class TaskUpdate(BaseModel):
    status: TaskStatus

class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: str
    due_date: datetime
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True