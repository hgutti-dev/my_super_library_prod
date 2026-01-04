# src/services/user_service.py

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status

from src.repositories.user_repostory import UserRepository
from src.schemas.users import UserRead, UserCreate, UserUpdate


class UserService:
    """
    Capa de negocio para Users.
    - Valida reglas (duplicados, existencia)
    - Traduce errores del repositorio a HTTPException
    - Define comportamientos (update vacío, límites, etc.)
    """

    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    # ======================================================
    # =====================  HELPERS  ======================
    # ======================================================

    @staticmethod
    def _normalize_str(value: str) -> str:
        return value.strip().lower()

    async def _ensure_not_duplicated_on_create(self, user_in: UserCreate) -> None:
        """
        Regla de negocio:
        - Evitar duplicar usuarios por email.
        """
        email = self._normalize_str(user_in.email)

        # tu repo tiene método directo por email: úsalo (más eficiente que list_users)
        existing = await self._repo.get_user_by_email(email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un usuario con ese email.",
            )

    async def _ensure_user_exists(self, user_id: str) -> UserRead:
        """
        Obtiene el usuario o lanza 404.
        También traduce ValueError del ObjectId inválido.
        """
        try:
            user = await self._repo.get_user_by_id(user_id)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e),
            )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado.",
            )
        return user

    async def _ensure_not_duplicated_on_update(
        self,
        user_id: str,
        user_in: UserUpdate,
    ) -> None:
        """
        Regla de negocio:
        - Si se actualiza el email, no debe chocar con otro usuario.
        """
        update_data = user_in.model_dump(exclude_unset=True)

        if "email" not in update_data:
            return

        new_email = self._normalize_str(update_data["email"])
        existing = await self._repo.get_user_by_email(new_email)

        # Si existe y NO es el mismo usuario, conflicto
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El email ya está en uso por otro usuario.",
            )

    # ======================================================
    # ======================  CREATE  ======================
    # ======================================================

    async def create_user(self, user_in: UserCreate) -> UserRead:
        # Normaliza email (si tu schema permite mutación podrías setearlo;
        # si no, crea un dict y reconstruye el modelo).
        # Aquí asumimos que UserCreate es mutable o que no te molesta dejarlo tal cual.
        normalized_email = self._normalize_str(user_in.email)
        if normalized_email != user_in.email:
            # intentamos mutar si se puede (pydantic v2 depende de config)
            try:
                user_in.email = normalized_email  # type: ignore[attr-defined]
            except Exception:
                pass

        await self._ensure_not_duplicated_on_create(user_in)

        try:
            return await self._repo.create_user(user_in)
        except RuntimeError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

    # ======================================================
    # =======================  READ  =======================
    # ======================================================

    async def get_user_by_id(self, user_id: str) -> UserRead:
        return await self._ensure_user_exists(user_id)

    async def get_user_by_email(self, email: str) -> UserRead:
        normalized = self._normalize_str(email)
        user = await self._repo.get_user_by_email(normalized)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado.",
            )
        return user

    async def list_users(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[UserRead]:
        if limit > 200:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El parámetro 'limit' no puede ser mayor a 200.",
            )

        # Opcional: normalizar filtro email si viene
        if filters and "email" in filters and isinstance(filters["email"], str):
            filters = dict(filters)
            filters["email"] = self._normalize_str(filters["email"])

        return await self._repo.list_users(skip=skip, limit=limit, filters=filters)

    # ======================================================
    # ======================  UPDATE  ======================
    # ======================================================

    async def update_user(self, user_id: str, user_in: UserUpdate) -> UserRead:
        # 1) validar existencia + formato id
        _ = await self._ensure_user_exists(user_id)

        # 2) si no trae cambios, devolvemos el doc actual
        update_data = user_in.model_dump(exclude_unset=True)
        if not update_data:
            return await self._ensure_user_exists(user_id)

        # 3) normalizar email si viene
        if "email" in update_data and isinstance(update_data["email"], str):
            normalized_email = self._normalize_str(update_data["email"])
            if normalized_email != update_data["email"]:
                try:
                    user_in.email = normalized_email  # type: ignore[attr-defined]
                except Exception:
                    pass

        # 4) regla: email no duplicado si se cambia
        await self._ensure_not_duplicated_on_update(user_id, user_in)

        try:
            updated = await self._repo.update_user(user_id, user_in)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e),
            )

        if updated is None:
            # raro, ya validamos existencia, pero por consistencia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado.",
            )

        return updated

    # ======================================================
    # ======================  DELETE  ======================
    # ======================================================

    async def delete_user(self, user_id: str) -> None:
        await self._ensure_user_exists(user_id)

        try:
            deleted = await self._repo.delete_user(user_id)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e),
            )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado.",
            )
