from conftest import Product
from sqlalchemy.exc import IntegrityError
import pytest

# Inline service function (extracted from API code)
def create_product(db, name, category, price, stock_quantity=0, is_active=True):
    product = Product(name=name, category=category, price=price,
                      stock_quantity=stock_quantity, is_active=is_active)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def test_create_product_valid(db):
    product = create_product(db, "Widget", "Tools", 29.99, 10)
    assert product.id is not None
    assert product.name == "Widget"
    assert product.category == "Tools"
    assert product.price == 29.99
    assert product.stock_quantity == 10
    assert product.is_active is True


def test_create_product_missing_name(db):
    with pytest.raises(IntegrityError):
        create_product(db, None, "Tools", 29.99, 10)


def test_create_product_duplicate_name(db):
    create_product(db, "Gadget", "Tools", 19.99, 5)
    with pytest.raises(IntegrityError):
        create_product(db, "Gadget", "Tools", 19.99, 5)


def test_update_product_stock(db):
    product = create_product(db, "Device", "Electronics", 99.99, 15)
    product.stock_quantity = 20
    db.commit()
    db.refresh(product)
    assert product.stock_quantity == 20


def test_delete_product(db):
    product = create_product(db, "Appliance", "Home", 49.99, 8)
    db.delete(product)
    db.commit()
    assert db.query(Product).filter(Product.id == product.id).first() is None
