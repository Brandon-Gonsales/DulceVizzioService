from beanie import Indexed
from pydantic import EmailStr, Field
from typing import Optional
from datetime import datetime
from .base import BaseDocument
from .enums import Role

class User(BaseDocument):
    """
    Modelo de Usuario
    
    Roles:
    - SUPERADMIN: Propietario, acceso total.
    - ADMIN: Administrador del sistema.
    - MODERATOR: Moderadora de comunidad (VIP).
    - USER: Estudiante.
    """
    
    email: Indexed(EmailStr, unique=True)  # Email único e indexado
    username: Indexed(str, unique=True) = None
    full_name: str
    password_hash: str  # Contraseña hasheada con bcrypt

    
    role: Role = Role.USER  # Ahora usa el Enum
    is_active: bool = True

    avatar_url: Optional[str] = None
    phone_number: Optional[str] = None
    birth_date: Optional[datetime] = None
    
    # created_at y updated_at ahora vienen de BaseDocument
    
    class Settings:
        name = "users"  # Nombre de la colección en MongoDB
        indexes = [
            "email",
            "username",
            "role",
            "is_active",
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@dulcevicio.com",
                "username": "admin",
                "full_name": "Admin DulceVicio",
                "role": "ADMIN",
                "is_active": True
            }
        }
    
    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
    
    def __str__(self):
        return self.email
