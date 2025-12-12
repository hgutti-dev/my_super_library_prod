# src/services/book_service.py

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status

from src.repositories.book_repository import BookRepository
from src.schemas.book import BookCreate, BookUpdate, BookRead


class BookService:
    """
    Capa de negocio para Books.
    - Valida reglas (duplicados, existencia)
    - Traduce errores del repositorio a HTTPException
    - Decide comportamientos (update vacío, etc.)
    """

    def __init__(self, repo: BookRepository) -> None:
        self._repo = repo

    # ======================================================
    # =====================  HELPERS  ======================
    # ======================================================

    @staticmethod
    def _normalize_str(value: str) -> str:
        # Normalización básica para comparaciones.
        # (Puedes mejorar con unidecode si quieres ignorar tildes)
        return value.strip().lower()

    async def _ensure_not_duplicate_on_create(self, book_in: BookCreate) -> None:
        """
        Regla de negocio:
        Evitar duplicados. Aquí asumimos duplicado si coincide:
        - title
        - author
        - published_year  (si existe en tu schema)
        Ajusta según tu modelo real.
        """
        # Nota: tu BookRepository actual no incluye published_year en BookRead,
        # pero tu schema inicial sí lo tenía. Si tu BookCreate tiene published_year,
        # úsalo. Si no, elimina esa parte.
        filters: Dict[str, Any] = {
            "title": book_in.title,
            "author": book_in.author,
        }

        existing = await self._repo.list_books(skip=0, limit=1, filters=filters)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un libro con los mismos datos (posible duplicado).",
            )

    async def _ensure_book_exists(self, book_id: str) -> BookRead:
        """
        Obtiene el libro o lanza 404.
        También traduce ValueError del ObjectId inválido.
        """
        try:
            book = await self._repo.get_book_by_id(book_id)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e),
            )

        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Libro no encontrado.",
            )
        return book

    # ======================================================
    # ======================  CREATE  ======================
    # ======================================================

    async def create_book(self, book_in: BookCreate) -> BookRead:
        # (Opcional) normalizar strings de entrada
        # book_in.title = book_in.title.strip()  # si tu modelo permite mutación
        # Mejor: crea dict normalizado si quieres

        await self._ensure_not_duplicate_on_create(book_in)

        try:
            return await self._repo.create_book(book_in)
        except RuntimeError as e:
            # Error inesperado al recuperar lo insertado, etc.
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

    # ======================================================
    # =======================  READ  =======================
    # ======================================================

    async def get_book_by_id(self, book_id: str) -> BookRead:
        return await self._ensure_book_exists(book_id)

    async def list_books(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[BookRead]:
        # Regla simple: límites razonables (evitar que pidan 100000)
        if limit > 200:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El parámetro 'limit' no puede ser mayor a 200.",
            )

        # (Opcional) normalizar filtros de texto para búsquedas case-insensitive
        # Esto depende de cómo guardas datos e índices.
        return await self._repo.list_books(skip=skip, limit=limit, filters=filters)

    # ======================================================
    # ======================  UPDATE  ======================
    # ======================================================

    async def update_book(self, book_id: str, book_in: BookUpdate) -> BookRead:
        # 1) Asegurar que existe (y validar ObjectId)
        _ = await self._ensure_book_exists(book_id)

        # 2) Si no trae cambios, para mí es regla de negocio:
        #    devolver el libro actual (o lanzar 422 si prefieres)
        update_data = book_in.model_dump(exclude_unset=True)
        if not update_data:
            # Devuelve el actual
            return await self._ensure_book_exists(book_id)

        # 3) (Opcional) regla de duplicado en update:
        #    si cambian title/author/published_year, verificar que no choque
        #    con otro documento. Requiere método repo adicional para buscar
        #    excluyendo el _id actual, por eso aquí lo dejo como comentario.

        try:
            updated = await self._repo.update_book(book_id, book_in)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e),
            )

        if updated is None:
            # raro porque ya validamos existencia, pero por consistencia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Libro no encontrado.",
            )

        return updated

    # ======================================================
    # ======================  DELETE  ======================
    # ======================================================

    async def delete_book(self, book_id: str) -> None:
        # validar existence + id format
        await self._ensure_book_exists(book_id)

        try:
            deleted = await self._repo.delete_book(book_id)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e),
            )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Libro no encontrado.",
            )
