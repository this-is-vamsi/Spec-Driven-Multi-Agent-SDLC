from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.product import (
    get_products,
    get_product_by_id,
    create_product,
    update_product_stock,
    deactivate_product
)
from app.dependencies import get_db

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=list[ProductResponse])
def list_products(category: str | None = None, db: Session = Depends(get_db)):
    products = get_products(db, category=category)
    return {"success": True, "message": "Operation completed successfully", "data": products, "meta": {}}

@router.get("/{id}", response_model=ProductResponse)
def get_product(id: UUID, db: Session = Depends(get_db)):
    product = get_product_by_id(db, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"success": True, "message": "Operation completed successfully", "data": product, "meta": {}}

@router.post("/", response_model=ProductResponse)
def create_new_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = create_product(db, product)
    return {"success": True, "message": "Product created successfully", "data": new_product, "meta": {}}

@router.patch("/{id}/stock", response_model=ProductResponse)
def update_stock(id: UUID, stock_update: ProductUpdate, db: Session = Depends(get_db)):
    updated_product = update_product_stock(db, id, stock_update)
    return {"success": True, "message": "Stock quantity updated successfully", "data": updated_product, "meta": {}}

@router.patch("/{id}/deactivate", response_model=ProductResponse)
def deactivate_product_route(id: UUID, db: Session = Depends(get_db)):
    deactivated_product = deactivate_product(db, id)
    return {"success": True, "message": "Product deactivated successfully", "data": deactivated_product, "meta": {}}