"""
Schemas Pydantic para Enrollments (Inscripciones)
Validación y serialización de datos de inscripciones a cursos
"""

from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Optional, List, TypeVar, Generic
from datetime import datetime
from beanie import PydanticObjectId
from app.models.enums import EnrollmentStatus


class EnrollmentCreateSchema(BaseModel):
    """
    Schema para crear enrollment (solo admin).
    El admin inscribe manualmente al estudiante.
    """
    user_id: PydanticObjectId = Field(..., description="ID del estudiante a inscribir")
    course_id: PydanticObjectId = Field(..., description="ID del curso")
    notes: Optional[str] = Field(None, max_length=500, description="Notas administrativas")


class EnrollmentProgressUpdateSchema(BaseModel):
    """
    Schema para actualizar progreso de video.
    Enviado por frontend cada 10-30 segundos.
    """
    lesson_id: PydanticObjectId = Field(..., description="ID de la lección actual")
    video_position_seconds: int = Field(..., ge=0, description="Posición del video en segundos")


class EnrollmentExtendSchema(BaseModel):
    """Schema para extender expiración (admin)"""
    additional_days: int = Field(..., ge=1, le=3650, description="Días adicionales (máx 10 años)")


class CourseEmbeddedSchema(BaseModel):
    """
    Schema simplificado de curso para embedder en enrollments.
    Solo incluye campos esenciales para navegación y UI.
    """
    id: PydanticObjectId
    title: str
    slug: str
    cover_image_url: Optional[HttpUrl] = None
    price: float
    currency: str = "USD"
    
    model_config = ConfigDict(from_attributes=True)



class EnrollmentResponseSchema(BaseModel):
    """
    Schema de respuesta de enrollment.
    Usado en GET /enrollments
    """
    id: PydanticObjectId
    user_id: PydanticObjectId
    course_id: PydanticObjectId
    course: Optional[CourseEmbeddedSchema] = Field(None, description="Datos del curso (populated en servicio)")
    
    # Estado
    status: EnrollmentStatus
    enrolled_at: datetime
    expires_at: datetime
    
    # Progreso
    last_accessed_lesson_id: Optional[PydanticObjectId] = None
    last_video_position_seconds: Optional[int] = None
    last_accessed_at: Optional[datetime] = None
    
    # Completado
    completed_at: Optional[datetime] = None
    certificate_url: Optional[HttpUrl] = None
    
    # Metadata
    notes: Optional[str] = None
    
    # Campos de auditoría
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "course_id": "507f1f77bcf86cd799439013",
                "status": "ACTIVE",
                "enrolled_at": "2026-01-20T10:00:00Z",
                "expires_at": "2027-01-20T10:00:00Z",
                "last_accessed_lesson_id": "507f1f77bcf86cd799439014",
                "last_video_position_seconds": 332,
                "last_accessed_at": "2026-01-25T15:30:00Z",
                "completed_at": None,
                "certificate_url": None,
                "created_at": "2026-01-20T10:00:00Z",
                "updated_at": "2026-01-25T15:30:00Z"
            }
        }
    )

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Schema genérico de respuesta paginada"""
    total: int          # Total de registros encontrados
    page: int           # Página actual
    per_page: int       # Registros por página
    total_pages: int    # Total de páginas
    data: List[T]       # Lista de objetos


class EnrollmentListResponse(PaginatedResponse[EnrollmentResponseSchema]):
    """Respuesta paginada de enrollments"""
    pass
