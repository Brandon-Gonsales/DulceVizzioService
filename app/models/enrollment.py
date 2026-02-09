"""
Modelo de Enrollment (Inscripciones a cursos)
Sistema de pago individual por curso con expiración
"""

from beanie import PydanticObjectId
from pydantic import Field, HttpUrl
from typing import Optional
from datetime import datetime, timedelta
from .enums import EnrollmentStatus
from .base import BaseDocument


class Enrollment(BaseDocument):
    """
    Inscripción de un estudiante a un curso individual.
    
    El usuario paga por acceso temporal (1 año) a un curso específico.
    Preparado para convivir con sistema de Membership futuro.
    """
    
    # Relación Many-to-Many (User ↔ Course)
    user_id: PydanticObjectId = Field(..., description="ID del estudiante")
    course_id: PydanticObjectId = Field(..., description="ID del curso")
    
    # Estado y fechas
    status: EnrollmentStatus = Field(default=EnrollmentStatus.ACTIVE, description="Estado de la inscripción")
    enrolled_at: datetime = Field(default_factory=datetime.utcnow, description="Fecha de inscripción")
    expires_at: datetime = Field(..., description="Fecha de expiración (1 año desde inscripción)")
    
    # Tracking de progreso de video
    last_accessed_lesson_id: Optional[PydanticObjectId] = Field(None, description="Última lección vista")
    last_video_position_seconds: Optional[int] = Field(None, ge=0, description="Posición del video en segundos")
    last_accessed_at: Optional[datetime] = Field(None, description="Última vez que accedió al curso")
    
    # Certificado (opcional - si completa el curso)
    completed_at: Optional[datetime] = Field(None, description="Fecha de completado del curso")
    certificate_url: Optional[HttpUrl] = Field(None, description="URL del certificado (si completó)")
    
    # Metadata administrativa
    notes: Optional[str] = Field(None, max_length=500, description="Notas internas (admin)")
    
    class Settings:
        name = "enrollments"
        indexes = [
            "user_id",
            "course_id",
            "status",
            ("user_id", "course_id"),  # Índice compuesto único
            "expires_at",
            "enrolled_at"
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "course_id": "507f1f77bcf86cd799439012",
                "status": "ACTIVE",
                "enrolled_at": "2026-01-20T10:00:00Z",
                "expires_at": "2027-01-20T10:00:00Z",
                "last_accessed_lesson_id": "507f1f77bcf86cd799439013",
                "last_video_position_seconds": 332,
                "last_accessed_at": "2026-01-25T15:30:00Z"
            }
        }
    
    @classmethod
    def create_with_expiration(
        cls,
        user_id: PydanticObjectId,
        course_id: PydanticObjectId,
        **kwargs
    ) -> "Enrollment":
        """
        Crea una inscripción con expiración automática de 1 año.
        
        Args:
            user_id: ID del estudiante
            course_id: ID del curso
            **kwargs: Campos adicionales opcionales
        
        Returns:
            Enrollment: Inscripción con expires_at calculado
        """
        enrolled_at = datetime.utcnow()
        expires_at = enrolled_at + timedelta(days=365)  # 1 año
        
        return cls(
            user_id=user_id,
            course_id=course_id,
            enrolled_at=enrolled_at,
            expires_at=expires_at,
            **kwargs
        )
    
    async def is_active_now(self) -> bool:
        """
        Verifica si la inscripción está activa en este momento.
        Si está activa pero la fecha expiró, actualiza el estado a EXPIRED.
        
        Returns:
            bool: True si está activa y no expirada
        """
        if self.status != EnrollmentStatus.ACTIVE:
            return False
        
        # Verificar fecha
        if datetime.utcnow() >= self.expires_at:
            # Expiró: Actualizar estado (Lazy Update)
            self.status = EnrollmentStatus.EXPIRED
            await self.save()
            return False
        
        return True
    
    def remaining_days(self) -> int:
        """
        Calcula días restantes de acceso.
        
        Returns:
            int: Días restantes (0 si expiró, negativo si ya expiró hace X días)
        """
        delta = self.expires_at - datetime.utcnow()
        return delta.days
