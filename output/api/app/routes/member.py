from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.member import MemberCreate, MemberResponse
from app.services.member import get_members, create_member
from app.dependencies import get_db

router = APIRouter()

@router.get("/", response_model=list[MemberResponse])
async def list_members(db: Session = Depends(get_db)):
    return get_members(db)

@router.post("/", response_model=MemberResponse)
async def register_member(member: MemberCreate, db: Session = Depends(get_db)):
    return create_member(db, member)
