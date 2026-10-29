from conftest import Customer
from sqlalchemy.exc import IntegrityError
import pytest

# Inline service function (extracted from API code)
def create_customer(db, name, email, phone=None):
    customer = Customer(name=name, email=email, phone=phone)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

def test_create_customer_valid(db):
    customer = create_customer(db, "John Doe", "john@example.com", "1234567890")
    assert customer.id is not None
    assert customer.name == "John Doe"
    assert customer.email == "john@example.com"
    assert customer.phone == "1234567890"


def test_create_customer_missing_email(db):
    with pytest.raises(IntegrityError):
        create_customer(db, "Jane Doe", None)


def test_create_customer_duplicate_email(db):
    create_customer(db, "Alice", "alice@example.com")
    with pytest.raises(IntegrityError):
        create_customer(db, "Bob", "alice@example.com")


def test_update_customer_phone(db):
    customer = create_customer(db, "Charlie", "charlie@example.com")
    customer.phone = "0987654321"
    db.commit()
    db.refresh(customer)
    assert customer.phone == "0987654321"


def test_delete_customer(db):
    customer = create_customer(db, "Dave", "dave@example.com")
    db.delete(customer)
    db.commit()
    assert db.query(Customer).filter(Customer.id == customer.id).first() is None
