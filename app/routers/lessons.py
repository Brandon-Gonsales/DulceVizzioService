"""
Router para endpoints de Lecciones (Clases)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile, File, Form
from typing import List, Optional
from app.models.user import User
from app.schemas.lesson_schema import (
    LessonCreateSchema, 
    LessonUpdateSchema, 
    LessonResponseSchema, 
    LessonOrderUpdateSchema
)
from app.services.lesson_service import LessonService
from app.services.cloudinary_service import CloudinaryService
from app.utils.dependencies import get_current_user, get_current_admin
# from app.routers.courses import get_current_admin # YA NO NECESARIO

router = APIRouter(
    
    prefix="/api",
    tags=["Lessons"]
)

# --- Endpoints Públicos ---

@router.get("/courses/{course_id}/lessons", response_model=List[LessonResponseSchema])
async def get_course_lessons(
    course_id: str,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Listar lecciones de un curso.
    - Público: Metadata básica
    - Estudiante inscrito: Acceso completo
    """
    return await LessonService.get_lessons_by_course(course_id, current_user)

@router.get("/lessons/{lesson_id}", response_model=LessonResponseSchema)
async def get_lesson(
    lesson_id: str,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Obtener detalle de una lección.
    Verifica permisos si no es preview.
    """
    return await LessonService.get_lesson_by_id(lesson_id, current_user)

# --- Endpoints Administrativos ---

@router.post("/courses/{course_id}/lessons", response_model=LessonResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    course_id: str,
    lesson_data: LessonCreateSchema,
    current_user: User = Depends(get_current_admin)
):
    """
    Crear nueva lección en un curso (Admin).
    
    Los campos de video (video_url, video_id) son opcionales.
    Puedes crear la lección sin video y subirlo después con PATCH.
    """
    return await LessonService.create_lesson(course_id, lesson_data, current_user)


@router.put("/lessons/{lesson_id}", response_model=LessonResponseSchema)
async def update_lesson(
    lesson_id: str,
    lesson_data: LessonUpdateSchema,
    current_user: User = Depends(get_current_admin)
):
    """
    Actualizar lección (Admin).
    """
    return await LessonService.update_lesson(lesson_id, lesson_data, current_user)

@router.patch("/lessons/{lesson_id}/order", response_model=List[LessonResponseSchema])
async def reorder_lesson(
    lesson_id: str,
    order_data: LessonOrderUpdateSchema,
    current_user: User = Depends(get_current_admin)
):
    """
    Cambiar orden de una lección (Admin).
    Reordena automáticamente las demás. Retorna la lista actualizada.
    """
    return await LessonService.reorder_lesson(lesson_id, order_data.order, current_user)

@router.delete("/lessons/{lesson_id}")
async def delete_lesson(
    lesson_id: str,
    current_user: User = Depends(get_current_admin)
):
    """
    Eliminar lección (Admin).
    Se elimina del curso y de la base de datos.
    """
    return await LessonService.delete_lesson(lesson_id, current_user)
