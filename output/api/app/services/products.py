from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from uuid import uuid4
from fastapi import HTTPException


def create_product(db: Session, product: ProductCreate):
    db_product = Product(id=uuid4(), **product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_product(db: Session, product_id: str):
    return db.query(Product).filter(Product.id == product_id).first()


def update_product(db: Session, product_id: str, product: ProductUpdate):
    db_product = get_product(db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.dict(exclude_unset=True).items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product