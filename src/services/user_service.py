from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status

from src.repositories.user_repostory import UserRepository
from src.schemas.users import UserRead, UserCreate, UserUpdate

class UserService:

    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    @staticmethod
    def _normalize_str(value: str) -> str:
        
        return value.strip().lower()
    
    async def _ensure_not_duplicated_on_create(self, user_in: UserCreate) -> None:
        filters: Dict[str, Any] = {
            "email": user_in.email,
            
        }

        return ""
    
    async def create_user(self, user_in: UserCreate) -> UserRead:

        try:
            return await self._repo.create_user(user_in)
        except RuntimeError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )