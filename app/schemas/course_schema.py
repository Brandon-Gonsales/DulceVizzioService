"""
Schemas Pydantic para Curso
Validación y serialización de datos de cursos
"""

from pydantic import BaseModel, Field, HttpUrl, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from beanie import PydanticObjectId
from app.models.enums import CourseStatus, CourseDifficulty

class CourseBase(BaseModel):
    """Schema base para Curso"""
    title: str = Field(..., min_length=5, max_length=100, description="Título del curso")
    description: str = Field(..., min_length=20, description="Descripción completa")
    category: str = Field(..., min_length=2, max_length=50)
    subcategory: Optional[str] = Field(None, min_length=2, max_length=50)
    difficulty: CourseDifficulty = CourseDifficulty.INTERMEDIATE
    tags: List[str] = Field(default_factory=list)
    price: float = Field(..., ge=0, description="Precio del curso")
    currency: str = Field(default="USD", min_length=3, max_length=3)
    whatsapp_group_url: Optional[HttpUrl] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        return v.strip()


class CourseCreateSchema(CourseBase):
    """Schema para crear curso"""
    pass


class CourseUpdateSchema(BaseModel):
    """Schema para actualizar curso (PATCH partial)"""
    title: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = Field(None, min_length=20)
    category: Optional[str] = Field(None, min_length=2, max_length=50)
    subcategory: Optional[str] = Field(None, min_length=2, max_length=50)
    difficulty: Optional[CourseDifficulty] = None
    tags: Optional[List[str]] = None
    price: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    whatsapp_group_url: Optional[HttpUrl] = None
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return v.strip()


class CourseStatusUpdateSchema(BaseModel):
    """Schema para cambiar estado del curso"""
    status: CourseStatus


from .lesson_schema import LessonResponseSchema

class CourseResponseSchema(CourseBase):
    """Schema de respuesta de curso"""
    id: PydanticObjectId
    slug: str
    cover_image_url: Optional[HttpUrl] = None
    status: CourseStatus
    rating_average: Optional[float] = None
    enrollment_count: int
    is_enrolled: bool = Field(default=False, description="Si el usuario actual está inscrito")
    
    # Campos calculados (requieren consulta async - se setean en el servicio)
    lessons_count: int = Field(default=0)
    total_duration_hours: float = Field(default=0.0)
    
    # Campos de auditoría
    created_at: datetime
    published_at: Optional[datetime] = None
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "title": "Macarons Perfectos",
                "slug": "macarons-perfectos",
                "description": "Aprende a hacer macarons franceses perfectos desde cero...",
                "category": "Repostería",
                "subcategory": "Macarons",
                "difficulty": "INTERMEDIATE",
                "price": 29.99,
                "currency": "USD",
                "status": "PUBLISHED",
                "rating_average": 4.8,
                "enrollment_count": 127,
                "is_enrolled": False,
                "lessons_count": 10,
                "total_duration_hours": 2.5,
                "created_at": "2026-01-20T10:00:00Z",
                "published_at": "2026-01-22T10:00:00Z",
                "updated_at": "2026-01-22T10:00:00Z"
            }
        }
    )


class CourseDetailResponseSchema(CourseResponseSchema):
    """Schema detallado con lecciones para vista individual"""
    lessons: List[LessonResponseSchema] = []

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "title": "Macarons Perfectos",
                # ... campos heredados ...
                "lessons": [
                    {
                        "id": "507f1f77bcf86cd799439012",
                        "course_id": "507f1f77bcf86cd799439011",
                        "title": "Introducción",
                        "video_url": "https://video.bunnycdn.com/play/...",
                        "is_preview": True,
                        "order": 1,
                        "materials": [],
                        "created_at": "2026-01-20T10:00:00Z",
                        "updated_at": "2026-01-20T10:00:00Z",
                    }
                ]
            }
        }
    )
