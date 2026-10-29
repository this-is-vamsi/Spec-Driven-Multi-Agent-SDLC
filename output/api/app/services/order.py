from sqlalchemy.orm import Session
from uuid import UUID
from app.models.order import Order
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderUpdate

# Service functions

def place_order(db: Session, order: OrderCreate):
    product = db.query(Product).filter(Product.id == order.product_id).first()
    if not product or product.stock_quantity < order.quantity:
        raise ValueError("Insufficient stock")
    total_price = product.price * order.quantity
    db_order = Order(customer_id=order.customer_id, total_price=total_price, status="pending")
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_orders(db: Session, status: str | None = None, customer_id: UUID | None = None):
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    if customer_id:
        query = query.filter(Order.customer_id == customer_id)
    return query.all()

def get_order_by_id(db: Session, order_id: UUID):
    return db.query(Order).filter(Order.id == order_id).first()

def update_order_status(db: Session, order_id: UUID, order_update: OrderUpdate):
    order = get_order_by_id(db, order_id)
    if order:
        order.status = order_update.status
        db.commit()
        db.refresh(order)
    return order