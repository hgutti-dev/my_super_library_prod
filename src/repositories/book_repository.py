# src/repositories/book_repository.py

from typing import List, Optional, Dict, Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from src.schemas.book import BookCreate, BookUpdate, BookRead


class BookRepository:
    """
    Repositorio de acceso a datos para la colección 'books'.
    SOLO maneja operaciones contra MongoDB (sin lógica de negocio).
    """

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        # Aquí asumimos que tu colección se llama "books"
        self._collection: AsyncIOMotorCollection = db["books"]

    # ======================================================
    # ====================  HELPERS  =======================
    # ======================================================

    @staticmethod
    def _to_object_id(book_id: str) -> ObjectId:
        """
        Convierte un string a ObjectId.
        Lanza ValueError si el formato no es válido (la capa de servicio decide qué hacer).
        """
        if not ObjectId.is_valid(book_id):
            raise ValueError(f"ID de libro inválido: {book_id}")
        return ObjectId(book_id)

    @staticmethod
    def _document_to_book_read(doc: Dict[str, Any]) -> BookRead:
        """
        Convierte un documento de MongoDB en un modelo BookRead.
        """
        return BookRead(
            id=str(doc["_id"]),
            title=doc["title"],
            author=doc["author"],
            genre=doc["genre"],
            total_copies=doc["total_copies"],
        )

    # ======================================================
    # ====================  CREATE  ========================
    # ======================================================

    async def create_book(self, book_in: BookCreate) -> BookRead:
        """
        Inserta un nuevo libro en la colección y devuelve el modelo BookRead.
        """
        book_dict = book_in.model_dump()
        result = await self._collection.insert_one(book_dict)

        created = await self._collection.find_one({"_id": result.inserted_id})
        if created is None:
            # En teoría no debería ocurrir; la capa de servicio puede manejar este caso.
            raise RuntimeError("Error al recuperar el libro recién creado")

        return self._document_to_book_read(created)

    # ======================================================
    # ======================  READ  ========================
    # ======================================================

    async def get_book_by_id(self, book_id: str) -> Optional[BookRead]:
        """
        Devuelve un libro por su ID o None si no existe.
        """
        oid = self._to_object_id(book_id)
        doc = await self._collection.find_one({"_id": oid})
        if doc is None:
            return None
        return self._document_to_book_read(doc)

    async def list_books(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[BookRead]:
        """
        Lista libros con paginación y filtros opcionales.
        - filters puede ser algo como {"author": "Nombre", "genre": "Ficción"}
        """
        query: Dict[str, Any] = filters or {}

        cursor = (
            self._collection
            .find(query)
            .skip(skip)
            .limit(limit)
        )

        books: List[BookRead] = []
        async for doc in cursor:
            books.append(self._document_to_book_read(doc))

        return books

    # ======================================================
    # =====================  UPDATE  =======================
    # ======================================================

    async def update_book(
        self,
        book_id: str,
        book_in: BookUpdate,
    ) -> Optional[BookRead]:
        """
        Actualiza un libro por su ID.
        Devuelve el BookRead actualizado o None si no existe.
        """
        oid = self._to_object_id(book_id)
        update_data = book_in.model_dump(exclude_unset=True)

        if not update_data:
            # Nada que actualizar; la capa de servicio decide qué hacer con esto.
            doc = await self._collection.find_one({"_id": oid})
            return self._document_to_book_read(doc) if doc else None

        result = await self._collection.update_one(
            {"_id": oid},
            {"$set": update_data},
        )

        if result.matched_count == 0:
            return None

        updated = await self._collection.find_one({"_id": oid})
        if updated is None:
            return None

        return self._document_to_book_read(updated)

    # ======================================================
    # =====================  DELETE  =======================
    # ======================================================

    async def delete_book(self, book_id: str) -> bool:
        """
        Elimina un libro por ID.
        Devuelve True si se eliminó algún documento, False en caso contrario.
        """
        oid = self._to_object_id(book_id)
        result = await self._collection.delete_one({"_id": oid})
        return result.deleted_count == 1
