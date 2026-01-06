"""
Schemas Pydantic para Usuario
Validación y serialización de datos de usuarios
"""

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, TypeVar, Generic, List
from datetime import datetime, date
import re
from beanie import PydanticObjectId
from app.models.enums import Role

# Generic type for pagination
T = TypeVar('T')


class UserBase(BaseModel):
    """Schema base para Usuario"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    username: str = Field(None, min_length=3, max_length=50)
    phone_number: Optional[str] = Field(None, pattern=r'^\+\d{5,15}$')
    birth_date: Optional[datetime] = None

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('El username solo puede contener letras, números, guiones (-) y guiones bajos (_)')
        return v
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        return v.strip()


class PasswordValidationMixin(BaseModel):
    """Mixin para validación de contraseñas """
    password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v


class UserSelfRegister(UserBase, PasswordValidationMixin):
    """
    Schema para auto-registro público (solo USER)
    Hereda validación de password del Mixin
    """
    pass


class UserCreate(UserBase, PasswordValidationMixin):
    """
    Schema para crear usuario (uso administrativo)
    Hereda validación de password del Mixin
    """
    role: Role = Role.USER


class UserUpdate(BaseModel):
    """Schema para actualizar usuario (Datos textuales)"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    phone_number: Optional[str] = Field(None, pattern=r'^\+\d{5,15}$')
    birth_date: Optional[datetime] = None
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('El username solo puede contener letras, números, guiones (-) y guiones bajos (_)')
        return v
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return v.strip()


class UserResponse(UserBase):
    """Schema de respuesta de usuario (sin contraseña)"""
    id: PydanticObjectId
    # email, full_name, username heredados de UserBase
    role: Role
    is_active: bool
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = None
    birth_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None 
    updated_by: Optional[str] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "email": "estudiante@example.com",
                "full_name": "María García",
                "username": "mariagarcia",
                "role": "USER",
                "is_active": True,
                "avatar_url": None,
                "created_at": "2025-12-19T14:00:00Z",
                "updated_at": "2025-12-19T14:00:00Z",
                "created_by": "admin_id_123",
                "updated_at": "2025-12-19T14:00:00Z",
                "created_by": "admin_id_123",
                "updated_by": "admin_id_123",
                "phone_number": "+59170012345",
                "birth_date": "1990-01-01"
            }
        }
    )


class UserLogin(BaseModel):
    """Schema para login"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema de respuesta de token JWT"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ChangePasswordSchema(BaseModel):
    """Schema para cambiar contraseña"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Las contraseñas no coinciden')
        return v


class PaginatedResponse(BaseModel, Generic[T]):
    """Schema genérico de respuesta paginada"""
    total: int          # Total de registros encontrados
    page: int           # Página actual
    per_page: int       # Registros por página
    total_pages: int    # Total de páginas
    data: List[T]       # Lista de objetos
