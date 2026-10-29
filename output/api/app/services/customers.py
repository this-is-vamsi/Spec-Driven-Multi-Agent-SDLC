from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
from uuid import uuid4
from fastapi import HTTPException


def create_customer(db: Session, customer: CustomerCreate):
    db_customer = Customer(id=uuid4(), **customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def get_customer(db: Session, customer_id: str):
    return db.query(Customer).filter(Customer.id == customer_id).first()


def update_customer(db: Session, customer_id: str, customer: CustomerUpdate):
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    for key, value in customer.dict(exclude_unset=True).items():
        setattr(db_customer, key, value)
    db.commit()
    db.refresh(db_customer)
    return db_customer