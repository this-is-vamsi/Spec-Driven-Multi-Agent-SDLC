from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse
from app.services.orders import create_order, get_order, update_order
from app.dependencies import get_db

router = APIRouter()

@router.post("/", response_model=OrderResponse)
def create_new_order(order: OrderCreate, db: Session = Depends(get_db)):
    return create_order(db, order)

@router.get("/{order_id}", response_model=OrderResponse)
def read_order(order_id: str, db: Session = Depends(get_db)):
    db_order = get_order(db, order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@router.patch("/{order_id}", response_model=OrderResponse)
def update_existing_order(order_id: str, order: OrderUpdate, db: Session = Depends(get_db)):
    return update_order(db, order_id, order)