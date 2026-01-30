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
    CourseStatusUpdateSchema
)
from app.services.course_service import CourseService
from app.utils.dependencies import get_current_user, get_current_admin, get_current_superadmin

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
    current_user: Optional[User] = Depends(get_current_user) # Opcional para ver si es admin
):
    """
    Listar cursos paginados.
    - Público: Solo ve cursos PUBLISHED (y no eliminados).
    - Admin: Puede filtrar por cualquier status.
    """
    is_admin = current_user and current_user.role in [Role.ADMIN, Role.SUPERADMIN]
    
    # Si no es admin, forzar vista pública
    public_view = not is_admin
    
    # Si es admin pero no especificó status, mostrar todos (o filtrar si especificó)
    # Si es público, el servicio filtrará solo PUBLISHED
    
    return await CourseService.get_courses(
        page=page, 
        limit=limit, 
        category=category, 
        difficulty=difficulty, 
        status=status,
        search=search,
        public_view=public_view
    )

@router.get("/{slug}", response_model=CourseResponseSchema)
async def get_course(
    slug: str,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Obtener detalle de un curso por slug (o ID).
    """
    is_admin = current_user and current_user.role in [Role.ADMIN, Role.SUPERADMIN]
    return await CourseService.get_course_by_slug(slug, public_view=not is_admin)

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
