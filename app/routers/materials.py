"""
Router para endpoints de Materiales de Lección
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from typing import List, Optional
from app.models.user import User
from app.schemas.material_schema import MaterialResponseSchema
from app.services.material_service import MaterialService
from app.utils.dependencies import get_current_user, get_current_admin

router = APIRouter(
    prefix="/api",
    tags=["Materials"]
)

# --- Endpoints Administrativos ---
# Nota: Materials se obtienen con GET /lessons/{id} (embebidos en lesson)
# Aquí solo están las operaciones de modificación

@router.post("/lessons/{lesson_id}/materials", response_model=MaterialResponseSchema, status_code=status.HTTP_201_CREATED)
async def upload_material(
    lesson_id: str,
    file: UploadFile = File(...),
    title: str = Form(...),
    is_downloadable: bool = Form(True),
    current_user: User = Depends(get_current_admin)
):
    """
    Subir un material a una lección (Admin).
    Usa Multipart/Form-Data.
    Soporta PDF, DOCX, Imágenes, etc.
    """
    return await MaterialService.upload_material(
        lesson_id, 
        file, 
        title, 
        is_downloadable, 
        current_user
    )

@router.delete("/lessons/{lesson_id}/materials")
async def delete_all_materials(
    lesson_id: str,
    current_user: User = Depends(get_current_admin)
):
    """
    Eliminar TODOS los materiales de una lección (Admin).
    Operación masiva: Limpia la lista de materiales embebidos.
    """
    return await MaterialService.delete_all_materials(lesson_id, current_user)
