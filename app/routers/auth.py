"""
Router de Autenticación
Endpoints para login, registro y gestión de cuenta
"""

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Request
from typing import Optional

from app.schemas.user_schema import (
    UserLogin,
    TokenResponse,
    UserResponse,
    ChangePasswordSchema
)
from app.services.auth_service import auth_service
from app.services.cloudinary_service import cloudinary_service
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])





@router.post("/login", response_model=TokenResponse)
async def login(request: Request, credentials: UserLogin):
    """
    Iniciar sesión
    
    - **email**: Email del usuario
    - **password**: Contraseña
    
    Retorna un token JWT para autenticación en endpoints protegidos
    
    **Rate Limit:** 5 intentos por 15 minutos por IP
    """
    from app.main import limiter
    
    # Aplicar rate limit específico
    limiter.limit("5/15minute")(login)
    
    return await auth_service.login(credentials)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Obtener información del usuario autenticado
    
    Requiere token JWT en el header: Authorization: Bearer <token>
    """
    return await auth_service.get_current_user_info(current_user)


@router.patch("/me/avatar", response_model=UserResponse)
async def update_my_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Actualizar mi foto de perfil
    
    Permite al usuario subir una nueva imagen de perfil.
    """
    # Subir imagen usando el servicio
    avatar_url = await cloudinary_service.upload_image(file, folder="avatars")
    
    current_user.avatar_url = avatar_url
    current_user.updated_by = str(current_user.id)
    await current_user.save()
    
    return current_user





@router.patch("/change-password")
async def change_password(
    request: Request,
    password_data: ChangePasswordSchema,
    current_user: User = Depends(get_current_user)
):
    """
    Cambiar contraseña del usuario autenticado
    
    - **current_password**: Contraseña actual
    - **new_password**: Nueva contraseña (mínimo 8 caracteres)
    - **confirm_password**: Confirmación de nueva contraseña
    
    **Rate Limit:** 3 intentos por hora por usuario
    """
    from app.main import limiter
    
    # Aplicar rate limit específico por usuario
    limiter.limit("3/hour")(change_password)
    
    return await auth_service.change_password(
        user=current_user,
        current_password=password_data.current_password,
        new_password=password_data.new_password
    )
