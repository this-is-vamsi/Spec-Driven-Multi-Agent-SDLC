from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.book import BookCreate, BookUpdate, BookResponse
from app.services.book import get_books, create_book, get_book_by_id, update_book, delete_book
from app.dependencies import get_db

router = APIRouter()

@router.get("/", response_model=list[BookResponse])
async def list_books(db: Session = Depends(get_db)):
    return get_books(db)

@router.post("/", response_model=BookResponse)
async def add_book(book: BookCreate, db: Session = Depends(get_db)):
    return create_book(db, book)

@router.get("/{id}", response_model=BookResponse)
async def get_book(id: int, db: Session = Depends(get_db)):
    book = get_book_by_id(db, id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.put("/{id}", response_model=BookResponse)
async def update_book_details(id: int, book: BookUpdate, db: Session = Depends(get_db)):
    return update_book(db, id, book)

@router.delete("/{id}", status_code=204)
async def remove_book(id: int, db: Session = Depends(get_db)):
    delete_book(db, id)
    return
