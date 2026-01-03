from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field, EmailStr, ConfigDict, computed_field, field_validator
""" from loans import LoanWithBook """


# ======================================================
# ================  BASE MODELS  =======================
# ======================================================

class UserBase(BaseModel):
    first_name: str = Field(..., description="Nombre del usuario")
    last_name: str = Field(..., description="Apellido del usuario")
    email: EmailStr = Field(..., description="Correo electrónico único del usuario")
    role: str = Field(..., description="Rol del usuario dentro del sistema. Ej: admin, staff, customer")
    registered_date: date = Field(default_factory=datetime.today)

    @computed_field(return_type=str)
    @property
    def full_name(self) -> str:
        """Devuelve el nombre completo del usuario."""
        return f"{self.first_name} {self.last_name}"

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        roles_validos = {"admin", "manager", "user", "viewer"}
        if v not in roles_validos:
            raise ValueError(f"El rol '{v}' no es válido. Roles permitidos: {roles_validos}")
        return v


# ======================================================
# =================  CREATE MODEL  =====================
# ======================================================

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Contraseña del usuario")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return v


# ======================================================
# =================  UPDATE MODEL  =====================
# ======================================================

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v is None:
            return v
        roles_validos = {"admin", "manager", "user", "viewer"}
        if v not in roles_validos:
            raise ValueError(f"El rol '{v}' no es válido. Roles permitidos: {roles_validos}")
        return v


# ======================================================
# ===================  READ MODEL  =====================
# ======================================================

class UserRead(UserBase):
    id: str = Field(..., description="ID único en MongoDB")
    model_config = ConfigDict(from_attributes=True)

# ======================================================
# ===========  READ MODEL FOR USER'S LOANS  ============
# ======================================================

""" class UserReadWithLoans(UserRead):
    loans: List[LoanWithBook] = Field(
        default_factory=list,
        description="Listado de préstamos actuales e históricos del usuario"
    ) """