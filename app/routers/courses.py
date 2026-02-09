"""
Router para endpoints de Cursos
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from typing import List, Optional
from app.models.user import User
from app.models.course import Course
from app.models.enums import Role, CourseStatus
from app.schemas.course_schema import (
    CourseCreateSchema, 
    CourseUpdateSchema, 
    CourseResponseSchema, 
    CourseStatusUpdateSchema,
    CourseDetailResponseSchema
)
from app.services.course_service import CourseService
from app.utils.dependencies import get_current_user, get_current_admin, get_current_superadmin, get_current_user_optional

router = APIRouter(
    prefix="/api/courses",
    tags=["Courses"]
)



# --- Endpoints Públicos ---

@router.get("", response_model=dict)
async def get_courses(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user_optional) # Opcional para acceso público
):
    """
    Listar cursos paginados.
    - Usuario logeado o usuario sin logear: Solo ve cursos PUBLISHED (y no eliminados).
    - Admin: Puede filtrar por cualquier status.
    """
    return await CourseService.get_courses(
        page=page, 
        limit=limit, 
        category=category, 
        difficulty=difficulty, 
        status=status,
        search=search,
        current_user=current_user
    )

@router.get("/{slug}", response_model=CourseDetailResponseSchema)
async def get_course(
    slug: str,
    current_user: Optional[User] = Depends(get_current_user_optional) # Opcional para acceso público
):
    """
    Obtener detalle de un curso por slug (o ID).
    - usuario no logueado o usuario no inscrito: Solo ve metadatos y lecciones preview
    - usuario inscrito o admin o superadmin: Ve todo el contenido
    """
    return await CourseService.get_course_by_slug(slug, current_user=current_user)

# --- Endpoints Administrativos ---

@router.post("", response_model=CourseResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreateSchema,
    current_user: User = Depends(get_current_admin)
):
    """
    Crear nuevo curso (Admin).
    Inicialmente en estado DRAFT.
    """
    return await CourseService.create_course(course_data, current_user)

@router.put("/{course_id}", response_model=CourseResponseSchema)
async def update_course(
    course_id: str,
    course_data: CourseUpdateSchema,
    current_user: User = Depends(get_current_admin)
):
    """
    Actualizar curso existente (Admin).
    """
    return await CourseService.update_course(course_id, course_data, current_user)

@router.patch("/{course_id}/status", response_model=CourseResponseSchema)
async def update_course_status(
    course_id: str,
    status_data: CourseStatusUpdateSchema,
    current_user: User = Depends(get_current_admin)
):
    """
    Cambiar estado del curso (Admin).
    Ej: PUBLICAR, ARCHIVAR.
    """
    return await CourseService.update_status(course_id, status_data.status, current_user)

@router.delete("/{course_id}")
async def delete_course(
    course_id: str,
    current_user: User = Depends(get_current_user) # Verificamos rol dentro
):
    """
    Eliminar curso.
    - ADMIN: Borrado lógico (soft delete).
    - SUPERADMIN: Borrado físico (hard delete).
    """
    if current_user.role not in [Role.ADMIN, Role.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="No tienes permisos")
        
    return await CourseService.delete_course(course_id, current_user)

# --- Endpoint FormData ---

@router.patch("/{course_id}/cover", response_model=CourseResponseSchema)
async def upload_course_cover(
    course_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin)
):
    """
    Subir imagen de portada del curso (Admin).
    Usa Multipart/Form-Data.
    """
    return await CourseService.upload_cover_image(course_id, file, current_user)
