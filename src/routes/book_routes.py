from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.db.db import get_db
from src.repositories.book_repository import BookRepository
from src.schemas.book import BookCreate, BookRead, BookUpdate
from src.services.book_service import BookService

router = APIRouter(prefix="/books", tags=["Books"])


# -------------------- Dependencies --------------------

def get_book_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> BookService:
    repo = BookRepository(db)
    return BookService(repo)


# -------------------- Routes --------------------

@router.post(
    "",
    response_model=BookRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_book(
    payload: BookCreate,
    service: BookService = Depends(get_book_service),
) -> BookRead:
    return await service.create_book(payload)


@router.get(
    "",
    response_model=List[BookRead],
)
async def list_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    title: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    service: BookService = Depends(get_book_service),
) -> List[BookRead]:
    filters: Dict[str, Any] = {}
    if title:
        filters["title"] = title
    if author:
        filters["author"] = author
    if genre:
        filters["genre"] = genre

    return await service.list_books(skip=skip, limit=limit, filters=filters or None)


@router.get(
    "/{book_id}",
    response_model=BookRead,
)
async def get_book_by_id(
    book_id: str,
    service: BookService = Depends(get_book_service),
) -> BookRead:
    return await service.get_book_by_id(book_id)


@router.patch(
    "/{book_id}",
    response_model=BookRead,
)
async def update_book(
    book_id: str,
    payload: BookUpdate,
    service: BookService = Depends(get_book_service),
) -> BookRead:
    return await service.update_book(book_id, payload)


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_book(
    book_id: str,
    service: BookService = Depends(get_book_service),
) -> None:
    await service.delete_book(book_id)
    return None
