from typing import Optional
from datetime import date
from pydantic import BaseModel, Field, ConfigDict, computed_field, field_validator


# ======================================================
# ================  BASE MODELS  =======================
# ======================================================

class BookBase(BaseModel):
    title: str = Field(..., description="Título del libro")
    author: str = Field(..., description="Autor del libro")
    published_year: date = Field(..., description="Fecha de publicación")
    genre: str = Field(..., description="Género literario")
    total_copies: int = Field(..., ge=0, description="Total de copias disponibles en biblioteca")

    @computed_field(return_type=int)
    @property
    def age_since_publication(self) -> int:
        """Devuelve cuántos años han pasado desde la publicación."""
        today = date.today()
        return today.year - self.published_year.year

    @field_validator("total_copies")
    @classmethod
    def validate_total_copies(cls, v):
        if v < 0:
            raise ValueError("El número de copias no puede ser negativo")
        return v


# ======================================================
# =================  CREATE MODEL  =====================
# ======================================================

class BookCreate(BookBase):
    """Modelo para crear un libro nuevo."""
    pass


# ======================================================
# =================  UPDATE MODEL  =====================
# ======================================================

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    published_year: Optional[date] = None
    genre: Optional[str] = None
    total_copies: Optional[int] = Field(None, ge=0)

    @field_validator("total_copies")
    @classmethod
    def validate_total_copies(cls, v):
        if v is not None and v < 0:
            raise ValueError("El número de copias no puede ser negativo")
        return v


# ======================================================
# ===================  READ MODEL  =====================
# ======================================================

class BookRead(BookBase):
    id: str = Field(..., description="ID único del libro en MongoDB")
    model_config = ConfigDict(from_attributes=True)


# ======================================================
# ============  READ MODEL PARA PRESTAMOS  =============
# ======================================================

class BookSummary(BaseModel):
    id: str = Field(..., description="ID único del libro en MongoDB")
    title: str
    author: str
    genre: str


