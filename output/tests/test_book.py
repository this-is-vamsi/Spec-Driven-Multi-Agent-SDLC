from conftest import Book

# Inline service functions

def create_book(db, title, author, isbn, available=True):
    book = Book(title=title, author=author, isbn=isbn, available=available)
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

def get_books(db):
    return db.query(Book).all()

def get_book_by_id(db, book_id):
    return db.query(Book).filter(Book.id == book_id).first()

def update_book(db, book_id, title=None, author=None, isbn=None, available=None):
    book = get_book_by_id(db, book_id)
    if book:
        if title is not None:
            book.title = title
        if author is not None:
            book.author = author
        if isbn is not None:
            book.isbn = isbn
        if available is not None:
            book.available = available
        db.commit()
        db.refresh(book)
    return book

def delete_book(db, book_id):
    book = get_book_by_id(db, book_id)
    if book:
        db.delete(book)
        db.commit()

# Tests

def test_create_book(db):
    book = create_book(db, '1984', 'George Orwell', '1234567890')
    assert book.id is not None
    assert book.title == '1984'
    assert book.author == 'George Orwell'
    assert book.isbn == '1234567890'
    assert book.available is True

def test_get_books(db):
    create_book(db, 'Brave New World', 'Aldous Huxley', '0987654321')
    books = get_books(db)
    assert len(books) == 2

def test_get_book_by_id(db):
    book = create_book(db, 'Fahrenheit 451', 'Ray Bradbury', '1122334455')
    fetched_book = get_book_by_id(db, book.id)
    assert fetched_book.id == book.id
    assert fetched_book.title == 'Fahrenheit 451'

def test_update_book(db):
    book = create_book(db, 'The Great Gatsby', 'F. Scott Fitzgerald', '6677889900')
    updated_book = update_book(db, book.id, title='The Great Gatsby Updated')
    assert updated_book.title == 'The Great Gatsby Updated'

def test_delete_book(db):
    book = create_book(db, 'To Kill a Mockingbird', 'Harper Lee', '5544332211')
    delete_book(db, book.id)
    assert get_book_by_id(db, book.id) is None
