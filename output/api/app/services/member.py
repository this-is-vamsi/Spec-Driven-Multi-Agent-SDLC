from sqlalchemy.orm import Session
from app.models.member import Member
from app.schemas.member import MemberCreate

def get_members(db: Session):
    return db.query(Member).all()

def create_member(db: Session, member: MemberCreate):
    db_member = Member(**member.dict())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member
