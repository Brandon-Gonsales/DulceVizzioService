"""
Modelos de Curso y componentes relacionados
"""

from beanie import Indexed, PydanticObjectId
from pydantic import Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from .base import BaseDocument
from .enums import CourseStatus, CourseDifficulty

from .lesson import Lesson # Import for type hinting


class CourseReview(BaseDocument):
    """
    Calificación y opinión de un curso
    """
    course_id: str = Field(..., description="ID del curso")
    user_id: str = Field(..., description="ID de la alumna")
    user_name: str = Field(..., description="Nombre de la alumna (desnormalizado)")
    user_avatar_url: Optional[HttpUrl] = Field(None, description="Avatar de la alumna")
    rating: int = Field(..., ge=1, le=5, description="Calificación de 1 a 5 estrellas")
    review: Optional[str] = Field(None, max_length=1000, description="Opinión escrita (opcional)")
    is_approved: bool = Field(default=True, description="Si la reseña está aprobada")
    
    class Settings:
        name = "course_reviews"
        indexes = [
            "course_id",
            "user_id",
            "rating",
            "created_at",
            "is_approved"
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "course_id": "course_123",
                "user_id": "user_456",
                "user_name": "María García",
                "rating": 5,
                "review": "El mejor curso de macarons que he tomado. Muy detallado y fácil de seguir."
            }
        }


class Course(BaseDocument):
    """
    Modelo Principal de Curso
    Incluye título, descripción, calificación, nivel, cantidad de clases y horas de contenido
    """
    
    # Información básica
    title: Indexed(str) = Field(..., description="Título del curso")
    slug: Indexed(str, unique=True) = Field(..., description="Slug único para URL")
    description: str = Field(..., description="Descripción completa del curso")
    # Categorización
    category: Indexed(str) = Field(..., description="Categoría principal")
    subcategory: Optional[str] = Field(None, description="Subcategoría")
    tags: List[str] = Field(default_factory=list, description="Etiquetas")
    # Nivel
    difficulty: CourseDifficulty = Field(default=CourseDifficulty.INTERMEDIATE, description="Nivel de dificultad")
    # Imagen de portada
    cover_image_url: Optional[HttpUrl] = Field(None, description="URL de la imagen de portada")
    # Precio
    price: float = Field(..., ge=0, description="Precio del curso")
    currency: str = Field(default="USD", description="Moneda")
    # Comunicación
    whatsapp_group_url: Optional[HttpUrl] = Field(None, description="URL del grupo de WhatsApp")
    # Estado
    status: CourseStatus = Field(default=CourseStatus.DRAFT, description="Estado del curso")
    published_at: Optional[datetime] = Field(None, description="Fecha de publicación")
    # Calificación
    rating_average: Optional[float] = Field(None, ge=0, le=5, description="Calificación promedio (0-5 estrellas)")
    # Estadísticas (Cacheadas o calculadas al vuelo)
    enrollment_count: int = Field(default=0, description="Estudiantes inscritos")
    lessons_count: int = Field(default=0, description="Cantidad total de lecciones")
    total_duration_hours: float = Field(default=0.0, description="Horas totales de contenido")
    
    # Campo virtual (no se guarda en BD, se calcula en el servicio)
    is_enrolled: bool = Field(default=False, exclude=True, description="Si el usuario actual está inscrito")
    
    # Propiedades calculadas eliminadas para permitir asignación directa desde el servicio
    async def get_lessons(self) -> List:
        """Obtiene las lecciones del curso ordenadas"""
        from app.models.lesson import Lesson
        return await Lesson.find({"course_id": self.id}).sort("+order").to_list()
    
    class Settings:
        name = "courses"
        indexes = [
            "slug",
            "title",
            "category",
            "subcategory",
            "tags",
            "status",
            "difficulty",
            "price",
            "rating_average",
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Macarons Perfectos",
                "slug": "macarons-perfectos",
                "description": "Aprende a hacer macarons franceses perfectos desde cero",
                "category": "Repostería",
                "subcategory": "Macarons",
                "tags": ["macarons", "repostería francesa", "postres"],
                "difficulty": "INTERMEDIATE",
                "lessons_count": 3,
                "total_duration_hours": 2.5,
                "price": 29.99,
                "currency": "USD",
                "rating_average": 4.8,
                "whatsapp_group_url": "https://chat.whatsapp.com/abc123",
                "status": "PUBLISHED"
            }
        }
    
    def __repr__(self):
        return f"<Course {self.title} ({self.status})>"
    
    def __str__(self):
        return self.title
