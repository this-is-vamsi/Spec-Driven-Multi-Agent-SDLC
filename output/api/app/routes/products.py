from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.products import create_product, get_product, update_product
from app.dependencies import get_db

router = APIRouter()

@router.post("/", response_model=ProductResponse)
def create_new_product(product: ProductCreate, db: Session = Depends(get_db)):
    return create_product(db, product)

@router.get("/{product_id}", response_model=ProductResponse)
def read_product(product_id: str, db: Session = Depends(get_db)):
    db_product = get_product(db, product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.patch("/{product_id}", response_model=ProductResponse)
def update_existing_product(product_id: str, product: ProductUpdate, db: Session = Depends(get_db)):
    return update_product(db, product_id, product)