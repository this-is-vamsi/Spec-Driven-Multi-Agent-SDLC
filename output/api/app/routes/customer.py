from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from app.services.customer import (
    get_customers,
    get_customer_by_id,
    create_customer,
    update_customer
)
from app.dependencies import get_db

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.get("/", response_model=list[CustomerResponse])
def list_customers(db: Session = Depends(get_db)):
    customers = get_customers(db)
    return {"success": True, "message": "Operation completed successfully", "data": customers, "meta": {}}

@router.get("/{id}", response_model=CustomerResponse)
def get_customer(id: UUID, db: Session = Depends(get_db)):
    customer = get_customer_by_id(db, id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"success": True, "message": "Operation completed successfully", "data": customer, "meta": {}}

@router.post("/", response_model=CustomerResponse)
def create_new_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    new_customer = create_customer(db, customer)
    return {"success": True, "message": "Customer created successfully", "data": new_customer, "meta": {}}

@router.patch("/{id}", response_model=CustomerResponse)
def update_customer_info(id: UUID, customer_update: CustomerUpdate, db: Session = Depends(get_db)):
    updated_customer = update_customer(db, id, customer_update)
    return {"success": True, "message": "Customer info updated successfully", "data": updated_customer, "meta": {}}