from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db

router = APIRouter()

@router.get("/")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    # Placeholder for dashboard metrics logic
    return {"message": "Dashboard metrics"}