from typing import List, Optional, Dict, Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from src.schemas.users import UserRead, UserCreate, UserUpdate

class UserRepository:

    def __init__(self, db: AsyncIOMotorDatabase) -> None:

        self._collection: AsyncIOMotorCollection = db["users"]

    @staticmethod
    def _to_object_id(user_id: str) -> ObjectId:

        if not ObjectId.is_valid(user_id):
            raise ValueError(f"ID de libro inválido: {user_id}")
        return ObjectId(user_id)
    
    @staticmethod
    def _document_to_user_read(doc: Dict[str, Any]) -> UserRead:

        return UserRead(
            id=str(doc["_id"]),
            first_name=doc["first_name"],
            last_name=doc["last_name"],
            email=doc["email"],
            role=doc["role"],
        )
    
    async def create_user(self, user_in: UserCreate) -> UserRead:

        user_dict = user_in.model_dump()
        result = await self._collection.insert_one(user_dict)

        created = await self._collection.find_one({"_id": result.inserted_id})
        if created is None:
            raise RuntimeError("Error al recuperar el libro recién creado")

        return self._document_to_user_read(created)