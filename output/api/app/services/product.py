from sqlalchemy.orm import Session
from uuid import UUID
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

# Service functions

def get_products(db: Session, category: str | None = None):
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    return query.all()

def get_product_by_id(db: Session, product_id: UUID):
    return db.query(Product).filter(Product.id == product_id).first()

def create_product(db: Session, product: ProductCreate):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product_stock(db: Session, product_id: UUID, stock_update: ProductUpdate):
    product = get_product_by_id(db, product_id)
    if product:
        product.stock_quantity = stock_update.stock_quantity
        db.commit()
        db.refresh(product)
    return product

def deactivate_product(db: Session, product_id: UUID):
    product = get_product_by_id(db, product_id)
    if product:
        product.is_active = False
        db.commit()
        db.refresh(product)
    return product