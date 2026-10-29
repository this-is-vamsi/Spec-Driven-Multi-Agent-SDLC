from sqlalchemy.orm import Session
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderUpdate
from uuid import uuid4
from fastapi import HTTPException


def create_order(db: Session, order: OrderCreate):
    db_order = Order(id=uuid4(), **order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def get_order(db: Session, order_id: str):
    return db.query(Order).filter(Order.id == order_id).first()


def update_order(db: Session, order_id: str, order: OrderUpdate):
    db_order = get_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    for key, value in order.dict(exclude_unset=True).items():
        setattr(db_order, key, value)
    db.commit()
    db.refresh(db_order)
    return db_order