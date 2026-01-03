from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.db.db import get_db
from src.repositories.user_repostory import UserRepository
from src.schemas.users import UserCreate, UserRead, UserUpdate
from src.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

# -------------------- Dependencies --------------------

def get_user_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> UserService:
    repo = UserRepository(db)
    return UserService(repo)



@router.get("", status_code=status.HTTP_200_OK)
async def list_all_users():
    return {"message": "Get All - Users"}

@router.post("",response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_book(payload: UserCreate, service: UserService = Depends(get_user_service)) -> UserRead:
    return await service.create_user(payload)
