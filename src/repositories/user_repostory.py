# src/repositories/user_repository.py

from typing import List, Optional, Dict, Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from src.schemas.users import UserRead, UserCreate, UserUpdate


class UserRepository:
    """
    Repositorio de acceso a datos para la colección 'users'.
    SOLO maneja operaciones contra MongoDB (sin lógica de negocio).
    """

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection: AsyncIOMotorCollection = db["users"]

    # ======================================================
    # ====================  HELPERS  =======================
    # ======================================================

    @staticmethod
    def _to_object_id(user_id: str) -> ObjectId:
        """
        Convierte un string a ObjectId.
        Lanza ValueError si el formato no es válido (la capa de servicio decide qué hacer).
        """
        if not ObjectId.is_valid(user_id):
            # (Tu mensaje decía "ID de libro", lo ajusto a "usuario")
            raise ValueError(f"ID de usuario inválido: {user_id}")
        return ObjectId(user_id)

    @staticmethod
    def _document_to_user_read(doc: Dict[str, Any]) -> UserRead:
        """
        Convierte un documento de MongoDB en un modelo UserRead.
        """
        return UserRead(
            id=str(doc["_id"]),
            first_name=doc["first_name"],
            last_name=doc["last_name"],
            email=doc["email"],
            role=doc["role"],
        )

    # ======================================================
    # ====================  CREATE  ========================
    # ======================================================

    async def create_user(self, user_in: UserCreate) -> UserRead:
        """
        Inserta un nuevo usuario en la colección y devuelve el modelo UserRead.
        """
        user_dict = user_in.model_dump()
        result = await self._collection.insert_one(user_dict)

        created = await self._collection.find_one({"_id": result.inserted_id})
        if created is None:
            raise RuntimeError("Error al recuperar el usuario recién creado")

        return self._document_to_user_read(created)

    # ======================================================
    # ======================  READ  ========================
    # ======================================================

    async def get_user_by_id(self, user_id: str) -> Optional[UserRead]:
        """
        Devuelve un usuario por su ID o None si no existe.
        """
        oid = self._to_object_id(user_id)
        doc = await self._collection.find_one({"_id": oid})
        if doc is None:
            return None
        return self._document_to_user_read(doc)

    async def get_user_by_email(self, email: str) -> Optional[UserRead]:
        """
        Devuelve un usuario por email o None si no existe.
        """
        doc = await self._collection.find_one({"email": email})
        if doc is None:
            return None
        return self._document_to_user_read(doc)

    async def list_users(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[UserRead]:
     
        query: Dict[str, Any] = filters or {}

        cursor = (
            self._collection
            .find(query)
            .skip(skip)
            .limit(limit)
        )

        users: List[UserRead] = []
        async for doc in cursor:
            users.append(self._document_to_user_read(doc))

        return users

    # ======================================================
    # =====================  UPDATE  =======================
    # ======================================================

    async def update_user(
        self,
        user_id: str,
        user_in: UserUpdate,
    ) -> Optional[UserRead]:

        oid = self._to_object_id(user_id)
        update_data = user_in.model_dump(exclude_unset=True)

        if not update_data:
            # Nada que actualizar; devolvemos el doc actual si existe
            doc = await self._collection.find_one({"_id": oid})
            return self._document_to_user_read(doc) if doc else None

        result = await self._collection.update_one(
            {"_id": oid},
            {"$set": update_data},
        )

        if result.matched_count == 0:
            return None

        updated = await self._collection.find_one({"_id": oid})
        if updated is None:
            return None

        return self._document_to_user_read(updated)

    # ======================================================
    # =====================  DELETE  =======================
    # ======================================================

    async def delete_user(self, user_id: str) -> bool:

        oid = self._to_object_id(user_id)
        result = await self._collection.delete_one({"_id": oid})
        return result.deleted_count == 1
