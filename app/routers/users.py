"""
Router de Gestión de Usuarios
Endpoints administrativos para crear y gestionar usuarios
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body, File, UploadFile, Query
from typing import Optional

from app.schemas.user_schema import UserResponse, UserUpdate, UserCreate, PasswordValidationMixin, PaginatedResponse
from app.models.user import User
from app.models.enums import Role
from app.utils.dependencies import require_admin, require_superadmin
from app.services.auth_service import auth_service
from app.services.cloudinary_service import cloudinary_service
from app.schemas.user_schema import UserUpdate, UserCreate, PasswordValidationMixin
from app.utils.security import hash_password

router = APIRouter(prefix="/api/users", tags=["User Management"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, current_user: User = Depends(require_admin)):
    """
    Crear usuario (ADMIN o SUPERADMIN)
    
    **Permisos:**
    - ✅ **SUPERADMIN**: Puede crear ADMIN, MODERATOR, USER
    - ✅ **ADMIN**: Puede crear MODERATOR, USER
    - ❌ **MODERATOR/USER**: Sin acceso
    
    **Roles disponibles:**
    - `ADMIN` - Solo SUPERADMIN puede crear
    - `MODERATOR` - ADMIN o SUPERADMIN pueden crear
    - `USER` - ADMIN o SUPERADMIN pueden crear
    
    **Campos requeridos:**
    - **email**: Email único del usuario
    - **password**: Contraseña (mínimo 8 caracteres)
    - **full_name**: Nombre completo
    - **role**: Rol del usuario (ADMIN, MODERATOR, USER)
    - **username**: Username opcional (único)
    """
    
    # ✅ Validar permisos según el rol que se intenta crear
    if user_data.role == Role.ADMIN:
        # Solo SUPERADMIN puede crear ADMIN
        if current_user.role != Role.SUPERADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo SUPERADMIN puede crear administradores"
            )
    
    elif user_data.role == Role.SUPERADMIN:
        # No se pueden crear nuevos SUPERADMIN
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pueden crear nuevos SUPERADMIN"
        )

    user = await auth_service.register_user(user_data, created_by=str(current_user.id))
    
    return user


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    q: Optional[str] = None,
    role: Optional[Role] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(require_admin)
):
    """
    Listar usuarios con paginación y filtros (ADMIN o SUPERADMIN)
    
    **Paginación:**
    - **page**: Número de página (mínimo 1)
    - **per_page**: Registros por página (entre 1 y 100, por defecto 10)
    
    **Filtros opcionales:**
    - **q**: Búsqueda general en email, username, full_name, phone_number
    - **role**: Filtrar por rol (ADMIN, MODERATOR, USER)
    - **is_active**: Filtrar por estado activo/inactivo
    """
    from beanie.operators import Or
    import math
    
    # Query base: excluir usuarios eliminados lógicamente
    query = User.find(User.is_deleted == False)
    
    # Filtro de búsqueda general (búsqueda insensible a mayúsculas)
    if q:
        regex = {"$regex": q, "$options": "i"}
        query = query.find(Or(
            User.email == regex,
            User.username == regex,
            User.full_name == regex,
            User.phone_number == regex
        ))
    
    # Filtro por rol
    if role:
        query = query.find(User.role == role)
    
    # Filtro por estado
    if is_active is not None:
        query = query.find(User.is_active == is_active)
    
    # Obtener total de registros (CRÍTICO para calcular páginas)
    total_count = await query.count()
    
    # Aplicar paginación (Skip & Limit)
    skip = (page - 1) * per_page
    users = await query.skip(skip).limit(per_page).to_list()
    
    # Calcular total de páginas
    total_pages = math.ceil(total_count / per_page) if per_page > 0 else 0
    
    return {
        "total": total_count,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "data": users
    }



@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_admin)
):
    """
    Obtener información de un usuario específico (ADMIN o SUPERADMIN)
    """
    from bson import ObjectId
    
    try:
        user = await User.get(ObjectId(user_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    if not user or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    update_data: UserUpdate,
    current_user: User = Depends(require_admin)
):
    """
    Actualizar datos del usuario (Datos textuales)
    
    Permite actualizar: username, full_name, phone_number, birth_date.
    
    **Permisos:**
    - SUPERADMIN puede editar a cualquiera.
    - ADMIN puede editar a MODERATOR y USER.
    """
    from bson import ObjectId
    
    try:
        user = await User.get(ObjectId(user_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    if not user or user.is_deleted:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    # Validar jerarquía
    if current_user.role == Role.ADMIN and user.role in [Role.SUPERADMIN, Role.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para editar a este usuario"
        )
        
    # Verificar unicidad de username si cambia
    if update_data.username and update_data.username != user.username:
        existing = await User.find_one(User.username == update_data.username)
        if existing:
            raise HTTPException(status_code=400, detail="El username ya está en uso")

    # Verificar unicidad de email si cambia
    if update_data.email and update_data.email != user.email:
        existing_email = await User.find_one(User.email == update_data.email)
        if existing_email:
            raise HTTPException(status_code=400, detail="El email ya está en uso")
            
    # Actualizar campos
    if update_data.email:
        user.email = update_data.email
    if update_data.full_name:
        user.full_name = update_data.full_name
    if update_data.username:
        user.username = update_data.username
    if update_data.phone_number is not None:
        user.phone_number = update_data.phone_number
    if update_data.birth_date is not None:
        user.birth_date = update_data.birth_date
        
    await user.save()
    return user




@router.patch("/{user_id}/avatar", response_model=UserResponse)
async def update_user_avatar(
    user_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin)
):
    """
    Actualizar avatar de usuario (ADMIN o SUPERADMIN)
    
    Sube una nueva imagen de perfil para el usuario especificado.
    La imagen se sube a Cloudinary y se guarda la URL.
    """
    from bson import ObjectId
    
    try:
        user = await User.get(ObjectId(user_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    if not user or user.is_deleted:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    # Validar jerarquía
    if current_user.role == Role.ADMIN and user.role in [Role.SUPERADMIN, Role.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para cambiar el avatar de este usuario"
        )
        
    # Subir imagen usando el servicio
    avatar_url = await cloudinary_service.upload_image(file, folder="avatars")
    
    user.avatar_url = avatar_url
    user.updated_by = str(current_user.id)
    await user.save()
    
    return user


@router.patch("/{user_id}/password", status_code=status.HTTP_204_NO_CONTENT)
async def admin_reset_password(
    user_id: str,
    password_data: PasswordValidationMixin = Body(...),
    current_user: User = Depends(require_admin)
):
    """
    Restablecer contraseña de usuario (ADMIN o SUPERADMIN)
    
    Permite a un administrador forzar el cambio de contraseña de un usuario.
    útil si el usuario perdió su acceso.
    """
    from bson import ObjectId
    
    try:
        user = await User.get(ObjectId(user_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    if not user or user.is_deleted:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Validar jerarquía estricta
    # ADMIN -> Solo puede cambiar a MODERATOR y USER
    if current_user.role == Role.ADMIN:
        if user.role in [Role.SUPERADMIN, Role.ADMIN]:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para cambiar la contraseña de este usuario"
            )
    
    # Hashear nueva contraseña
    user.password_hash = hash_password(password_data.password)
    await user.save()
    
    return None


@router.patch("/{user_id}/toggle-active", response_model=UserResponse)
async def toggle_user_active(
    user_id: str,
    current_user: User = Depends(require_admin)
):
    """
    Activar/Desactivar usuario (ADMIN o SUPERADMIN)
    
    Alterna el estado is_active del usuario
    """
    from bson import ObjectId
    
    try:
        user = await User.get(ObjectId(user_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # No se puede desactivar a sí mismo
    if str(user.id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propia cuenta"
        )
    
    # Validar jerarquía de roles
    # ADMIN solo puede desactivar a MODERATOR y USER
    if current_user.role == Role.ADMIN:
        if user.role in [Role.SUPERADMIN, Role.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para desactivar a este usuario"
            )
            
    # Alternar estado
    user.is_active = not user.is_active
    await user.save()
    
    return user


@router.patch("/{user_id}/role", response_model=UserResponse)
async def change_user_role(
    user_id: str,
    new_role: Role = Body(..., embed=True),
    current_user: User = Depends(require_superadmin)
):
    """
    Cambiar rol de usuario (SOLO SUPERADMIN)
    
    **Solo SUPERADMIN puede cambiar roles**
    
    No se puede cambiar a SUPERADMIN
    """
    from bson import ObjectId
    
    if new_role == Role.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede asignar el rol SUPERADMIN"
        )
    
    try:
        user = await User.get(ObjectId(user_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # No se puede cambiar el rol del SUPERADMIN
    if user.role == Role.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede cambiar el rol del SUPERADMIN"
        )
    
    # Cambiar rol
    user.role = new_role
    await user.save()
    
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_admin) # ADMIN o SUPERADMIN
):
    """
    Eliminar usuario (Híbrido)
    
    - **SUPERADMIN**: Borrado Físico (Elimina de la BD).
    - **ADMIN**: Borrado Lógico (Marca is_deleted=True).
    """
    from bson import ObjectId
    from datetime import datetime
    
    try:
        user = await User.get(ObjectId(user_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    if not user or user.is_deleted:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Prevenir auto-borrado
    if str(user.id) == str(current_user.id):
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propia cuenta")

    # Validar jerarquía (ADMIN no puede borrar a SUPERADMIN ni a otro ADMIN)
    if current_user.role == Role.ADMIN:
        if user.role in [Role.SUPERADMIN, Role.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para eliminar a este usuario"
            )
        # Borrado Lógico para ADMIN
        user.is_deleted = True
        user.deleted_at = datetime.utcnow()
        await user.save()
        
    elif current_user.role == Role.SUPERADMIN:
        if user.role == Role.SUPERADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para eliminar a este usuario"
            )
        # Borrado Físico REAL para SUPERADMIN
        await user.delete()
    
    return None
