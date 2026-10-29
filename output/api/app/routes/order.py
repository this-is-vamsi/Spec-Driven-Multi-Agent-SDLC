from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate
from app.services.order import (
    place_order,
    get_orders,
    get_order_by_id,
    update_order_status
)
from app.dependencies import get_db

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    new_order = place_order(db, order)
    return {"success": True, "message": "Order placed successfully", "data": new_order, "meta": {}}

@router.get("/", response_model=list[OrderResponse])
def list_orders(status: str | None = None, customer_id: UUID | None = None, db: Session = Depends(get_db)):
    orders = get_orders(db, status=status, customer_id=customer_id)
    return {"success": True, "message": "Operation completed successfully", "data": orders, "meta": {}}

@router.get("/{id}", response_model=OrderResponse)
def get_order(id: UUID, db: Session = Depends(get_db)):
    order = get_order_by_id(db, id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"success": True, "message": "Operation completed successfully", "data": order, "meta": {}}

@router.patch("/{id}/status", response_model=OrderResponse)
def update_order_status_route(id: UUID, order_update: OrderUpdate, db: Session = Depends(get_db)):
    updated_order = update_order_status(db, id, order_update)
    return {"success": True, "message": "Order status updated successfully", "data": updated_order, "meta": {}}