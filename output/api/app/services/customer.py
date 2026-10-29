from sqlalchemy.orm import Session
from uuid import UUID
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate

# Service functions

def get_customers(db: Session):
    return db.query(Customer).all()

def get_customer_by_id(db: Session, customer_id: UUID):
    return db.query(Customer).filter(Customer.id == customer_id).first()

def create_customer(db: Session, customer: CustomerCreate):
    db_customer = Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def update_customer(db: Session, customer_id: UUID, customer_update: CustomerUpdate):
    customer = get_customer_by_id(db, customer_id)
    if customer:
        for key, value in customer_update.dict().items():
            setattr(customer, key, value)
        db.commit()
        db.refresh(customer)
    return customer