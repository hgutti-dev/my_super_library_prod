from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from book import BookSummary


# ======================================================
# ================  BASE MODELS  =======================
# ======================================================

class LoanBase(BaseModel):
    user_id: str = Field(..., description="ID del usuario que realiza el préstamo")
    book_id: str = Field(..., description="ID del libro prestado")
    borrowed_at: datetime = Field(default_factory=datetime.utcnow, description="Fecha y hora del préstamo")
    due_date: Optional[date] = Field(
        None,
        description="Fecha límite de devolución del libro"
    )
    returned_at: Optional[datetime] = Field(
        default=None,
        description="Fecha y hora de devolución (si ya fue devuelto)"
    )
    status: str = Field(
        default="borrowed",
        description="Estado del préstamo: borrowed, returned, lost, etc."
    )


# ======================================================
# =================  CREATE MODEL  =====================
# ======================================================

class LoanCreate(LoanBase):
    """Modelo para crear un préstamo nuevo."""
    pass


# ======================================================
# =================  UPDATE MODEL  =====================
# ======================================================

class LoanUpdate(BaseModel):
    due_date: Optional[date] = None
    returned_at: Optional[datetime] = None
    status: Optional[str] = None


# ======================================================
# ===================  READ MODEL  =====================
# ======================================================

class LoanRead(LoanBase):
    id: str = Field(..., description="ID único del préstamo en MongoDB")
    model_config = ConfigDict(from_attributes=True)


# ======================================================
# ==========  READ MODEL FOR LOANS TO USERS  ===========
# ======================================================

class LoanWithBook(LoanRead):
    book: BookSummary