"""
Schemas Pydantic para Lecciones (Clases)
Validación y serialización de datos de lecciones
"""

from pydantic import BaseModel, Field, HttpUrl, ConfigDict, field_validator
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from beanie import PydanticObjectId

if TYPE_CHECKING:
    from app.models.lesson import LessonMaterial

class LessonBase(BaseModel):
    """Schema base para Lección"""
    title: str = Field(..., min_length=3, max_length=100, description="Título de la lección")
    summary: Optional[str] = Field(None, min_length=10, max_length=500, description="Resumen corto")
    duration_seconds: Optional[int] = Field(None, ge=0, description="Duración en segundos")
    is_preview: bool = Field(default=False, description="Vista previa gratuita")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        return v.strip()


class LessonCreateSchema(LessonBase):
    """
    Schema para crear lección
    Nota: course_id se pasa por parámetro de ruta, no en el body
    """
    video_url: Optional[HttpUrl] = Field(None, description="URL del video (Bunny.net)")
    video_id: Optional[str] = Field(None, min_length=1, description="ID del video en Bunny.net")

class LessonUpdateSchema(BaseModel):
    """Schema para actualizar lección"""
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    summary: Optional[str] = Field(None, min_length=10, max_length=500)
    duration_seconds: Optional[int] = Field(None, ge=0)
    is_preview: Optional[bool] = None
    video_url: Optional[HttpUrl] = None
    video_id: Optional[str] = None
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return v.strip()


class LessonOrderUpdateSchema(BaseModel):
    """Schema para reordenar lección"""
    order: int = Field(..., ge=1, description="Nuevo número de orden")


class LessonResponseSchema(LessonBase):
    """
    Schema de respuesta de lección.
    Incluye materials embebidos (lista cargada desde lesson.materials)
    """
    id: PydanticObjectId
    course_id: PydanticObjectId
    video_url: Optional[HttpUrl] = None
    video_id: Optional[str] = None
    order: int
    materials: List = Field(default_factory=list, description="Materiales embebidos")
    
    # Campos de auditoría (igual que Course y User)
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "course_id": "507f1f77bcf86cd799439012",
                "title": "Introducción a Macarons",
                "summary": "Fundamentos básicos y herramientas necesarias",
                "duration_seconds": 1200,
                "is_preview": True,
                "video_url": "https://video.bunnycdn.com/play/123/abc",
                "video_id": "abc-123",
                "order": 1,
                "materials": [],
                "created_at": "2026-01-20T10:00:00Z",
                "updated_at": "2026-01-22T12:30:00Z",
                "created_by": "507f1f77bcf86cd799439013",
                "updated_by": "507f1f77bcf86cd799439013"
            }
        }
    )
