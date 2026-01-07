from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from database import get_db, BookDB
from auth import verify_api_key

app = FastAPI(
    title="Books API",
    description="REST API для управления библиотекой книг",
    version="1.0.0"
)

# Модели Pydantic
class Book(BaseModel):
    id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=200, description="Название книги")
    author: str = Field(..., min_length=1, max_length=100, description="Автор книги")
    year: int = Field(..., ge=1000, le=datetime.now().year, description="Год издания")
    isbn: Optional[str] = Field(None, min_length=10, max_length=13, description="ISBN книги")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Мастер и Маргарита",
                "author": "Михаил Булгаков",
                "year": 1967,
                "isbn": "9785170123456"
            }
        }

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=1000, le=datetime.now().year)
    isbn: Optional[str] = Field(None, min_length=10, max_length=13)

# Корневой эндпоинт
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Добро пожаловать в Books API!",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# GET /api/books - Получение списка книг с фильтрацией и пагинацией
@app.get("/api/books", response_model=List[Book], tags=["Books"])
async def get_books(
    skip: int = 0,
    limit: int = 10,
    author: Optional[str] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    db: Session = Depends(get_db)
):
    filtered_books = db.query(BookDB).all()
    if author:
        filtered_books = [b for b in filtered_books if author.lower() in b.author.lower()]
    if year_from:
        filtered_books = [b for b in filtered_books if b.year >= year_from]
    if year_to:
        filtered_books = [b for b in filtered_books if b.year <= year_to]
    return filtered_books[skip:skip + limit]

# GET /api/books/{book_id} - Получение книги по ID
@app.get("/api/books/{book_id}", response_model=Book, tags=["Books"])
async def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(BookDB).filter(BookDB.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книга с ID {book_id} не найдена"
        )
    return book

# POST /api/books - Создание новой книги (с аутентификацией)
@app.post("/api/books", response_model=Book, status_code=status.HTTP_201_CREATED, tags=["Books"])
async def create_book(
    book: Book,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    db_book = BookDB(**book.model_dump(exclude={"id"}))
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# PUT /api/books/{book_id} - Полное обновление книги
@app.put("/api/books/{book_id}", response_model=Book, tags=["Books"])
async def update_book(
    book_id: int,
    updated_book: Book,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    book = db.query(BookDB).filter(BookDB.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книга с ID {book_id} не найдена"
        )
    for key, value in updated_book.model_dump().items():
        setattr(book, key, value)
    db.commit()
    db.refresh(book)
    return book

# PATCH /api/books/{book_id} - Частичное обновление книги
@app.patch("/api/books/{book_id}", response_model=Book, tags=["Books"])
async def partial_update_book(
    book_id: int,
    book_update: BookUpdate,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    book = db.query(BookDB).filter(BookDB.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книга с ID {book_id} не найдена"
        )
    update_data = book_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book

# DELETE /api/books/{book_id} - Удаление книги
@app.delete("/api/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Books"])
async def delete_book(
    book_id: int,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    book = db.query(BookDB).filter(BookDB.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книга с ID {book_id} не найдена"
        )
    db.delete(book)
    db.commit()

from collections import Counter

@app.get("/api/books/stats", tags=["Statistics"])
async def get_statistics(db: Session = Depends(get_db)):
    """
    Получить статистику по книгам.
    Возвращает:
    - общее количество книг;
    - распределение по авторам;
    - распределение по векам.
    """
    total_books = db.query(BookDB).count()

    # Собираем всех авторов
    authors = Counter(book.author for book in db.query(BookDB).all())

    # Собираем века (год // 100 + 1 даёт номер века: 1801–1900 → 19-й век)
    centuries = Counter((book.year // 100) + 1 for book in db.query(BookDB).all())

    return {
        "total_books": total_books,
        "books_by_author": dict(authors),
        "books_by_century": {f"{century} век": count for century, count in centuries.items()}
    }

