from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.services.customers import create_customer, get_customer, update_customer
from app.dependencies import get_db

router = APIRouter()

@router.post("/", response_model=CustomerResponse)
def create_new_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    return create_customer(db, customer)

@router.get("/{customer_id}", response_model=CustomerResponse)
def read_customer(customer_id: str, db: Session = Depends(get_db)):
    db_customer = get_customer(db, customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@router.patch("/{customer_id}", response_model=CustomerResponse)
def update_existing_customer(customer_id: str, customer: CustomerUpdate, db: Session = Depends(get_db)):
    return update_customer(db, customer_id, customer)