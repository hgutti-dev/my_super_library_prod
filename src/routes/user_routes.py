# src/routers/user_router.py

from typing import List, Optional, Dict, Any

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


# ======================================================
# =======================  READ  =======================
# ======================================================

@router.get("", response_model=List[UserRead], status_code=status.HTTP_200_OK)
async def list_all_users(
    service: UserService = Depends(get_user_service),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    email: Optional[str] = Query(None, description="Filtro opcional por email exacto"),
) -> List[UserRead]:
    filters: Optional[Dict[str, Any]] = {"email": email} if email else None
    return await service.list_users(skip=skip, limit=limit, filters=filters)


@router.get("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_user_by_id(
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    return await service.get_user_by_id(user_id)


# (Opcional, pero útil) buscar por email sin meter lógica al list:
@router.get("/by-email/{email}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_user_by_email(
    email: str,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    return await service.get_user_by_email(email)


# ======================================================
# ======================  CREATE  ======================
# ======================================================

@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    return await service.create_user(payload)


# ======================================================
# ======================  UPDATE  ======================
# ======================================================

@router.patch("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: str,
    payload: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    return await service.update_user(user_id, payload)


# ======================================================
# ======================  DELETE  ======================
# ======================================================

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> None:
    await service.delete_user(user_id)
    return None

