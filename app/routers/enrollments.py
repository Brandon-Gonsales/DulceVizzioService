"""
Router para endpoints de Enrollments (Inscripciones)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from app.models.user import User
from app.models.enums import EnrollmentStatus
from app.schemas.enrollment_schema import (
    EnrollmentCreateSchema,
    EnrollmentListResponse,
    EnrollmentResponseSchema,
    EnrollmentProgressUpdateSchema,
    EnrollmentExtendSchema
)
from app.services.enrollment_service import EnrollmentService
from app.utils.dependencies import get_current_user, get_current_admin

router = APIRouter(
    prefix="/api/enrollments",
    tags=["Enrollments"]
)

# --- Endpoints de Usuario ---

@router.get("/me", response_model=EnrollmentListResponse)
async def get_my_enrollments(
    status: Optional[EnrollmentStatus] = Query(None, description="Filtrar por estado"),
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Items por página"),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener mis enrollments (cursos a los que estoy inscrito).
    
    Query params:
    - status: ACTIVE | EXPIRED | CANCELLED (opcional)
    - page: Página actual (default 1)
    - size: Items por página (default 10)
    """
    return await EnrollmentService.get_user_enrollments(
        user_id=str(current_user.id),
        status=status,
        page=page,
        size=size
    )


@router.get("", response_model=EnrollmentListResponse)
async def get_all_enrollments(
    user_id: Optional[str] = Query(None, description="Filtrar por ID de estudiante"),
    course_id: Optional[str] = Query(None, description="Filtrar por ID de curso"),
    status: Optional[EnrollmentStatus] = Query(None, description="Filtrar por estado"),
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Items por página"),
    current_user: User = Depends(get_current_admin)
):
    """
    Listar inscripciones (Admin).
    
    Permite filtrar por usuario, curso y estado.
    """
    filters = {
        "user_id": user_id,
        "course_id": course_id,
        "status": status
    }
    # Eliminar claves con valor None
    filters = {k: v for k, v in filters.items() if v is not None}
    
    return await EnrollmentService.get_all_enrollments(
        page=page, 
        size=size, 
        filters=filters
    )

@router.get("/{enrollment_id}", response_model=EnrollmentResponseSchema)
async def get_enrollment(
    enrollment_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Obtener detalle de un enrollment.
    Solo el dueño o admin puede verlo.
    """
    return await EnrollmentService.get_enrollment_by_id(enrollment_id, current_user)

@router.patch("/{enrollment_id}/progress")
async def update_progress(
    enrollment_id: str,
    data: EnrollmentProgressUpdateSchema,
    current_user: User = Depends(get_current_user)
):
    """
    Guardar progreso de video.
    
    Frontend debe llamar esto cada 10-30 segundos mientras ve el video.
    Guarda la posición actual para "continuar viendo".
    """
    return await EnrollmentService.update_progress(enrollment_id, data, current_user)

# --- Endpoints Admin ---

@router.post("", response_model=EnrollmentResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_enrollment(
    data: EnrollmentCreateSchema,
    current_user: User = Depends(get_current_admin)
):
    """
    Inscribir estudiante a un curso (Admin).
    
    Crea un enrollment con:
    - expires_at = enrolled_at + 1 año
    - status = ACTIVE
    """
    return await EnrollmentService.create_enrollment(data, current_user)

@router.patch("/{enrollment_id}/extend", response_model=EnrollmentResponseSchema)
async def extend_enrollment(
    enrollment_id: str,
    data: EnrollmentExtendSchema,
    current_user: User = Depends(get_current_admin)
):
    """
    Extender expiración de un enrollment (Admin).
    
    Agrega días adicionales a expires_at.
    """
    return await EnrollmentService.extend_enrollment(enrollment_id, data, current_user)

@router.delete("/{enrollment_id}")
async def cancel_enrollment(
    enrollment_id: str,
    current_user: User = Depends(get_current_admin)
):
    """
    Cancelar enrollment (Admin).
    
    Cambia status a CANCELLED.
    """
    return await EnrollmentService.cancel_enrollment(enrollment_id, current_user)
