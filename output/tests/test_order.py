from conftest import Order, Customer
from sqlalchemy.exc import IntegrityError
import pytest

# Inline service function (extracted from API code)
def create_order(db, customer_id, total_price, status):
    order = Order(customer_id=customer_id, total_price=total_price, status=status)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

def test_create_order_valid(db):
    customer = Customer(name="Eve", email="eve@example.com")
    db.add(customer)
    db.commit()
    order = create_order(db, customer.id, 199.99, "pending")
    assert order.id is not None
    assert order.customer_id == customer.id
    assert order.total_price == 199.99
    assert order.status == "pending"


def test_create_order_missing_customer(db):
    with pytest.raises(IntegrityError):
        create_order(db, None, 199.99, "pending")


def test_update_order_status(db):
    customer = Customer(name="Frank", email="frank@example.com")
    db.add(customer)
    db.commit()
    order = create_order(db, customer.id, 299.99, "pending")
    order.status = "completed"
    db.commit()
    db.refresh(order)
    assert order.status == "completed"


def test_delete_order(db):
    customer = Customer(name="Grace", email="grace@example.com")
    db.add(customer)
    db.commit()
    order = create_order(db, customer.id, 399.99, "shipped")
    db.delete(order)
    db.commit()
    assert db.query(Order).filter(Order.id == order.id).first() is None
