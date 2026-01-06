"""
Configuración de la aplicación
Variables de entorno y configuraciones globales
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración de la aplicación usando variables de entorno"""
    
    # App
    APP_NAME: str = "DulceVicio API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # MongoDB Atlas
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "dulcevicio_db"
    
    # JWT Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES_DEBUG: int = 1440  # 1 día para desarrollo
    ACCESS_TOKEN_EXPIRE_MINUTES_PROD: int = 180    # 3 horas para producción
    
    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        """
        Retorna el tiempo de expiración del token según el modo DEBUG
        - DEBUG=True: 1 día (1440 minutos)
        - DEBUG=False: 3 horas (180 minutos)
        """
        if self.DEBUG:
            return self.ACCESS_TOKEN_EXPIRE_MINUTES_DEBUG
        return self.ACCESS_TOKEN_EXPIRE_MINUTES_PROD
    
    
    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def cors_origins(self) -> list[str]:
        """Convierte el string de origins a lista"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def cors_origins_list(self) -> list[str]:
        """
        Retorna los orígenes permitidos según el modo DEBUG
        - DEBUG=True: Permite todos los orígenes (*)
        - DEBUG=False: Solo orígenes específicos
        """
        if self.DEBUG:
            return ["*"]
        return self.cors_origins


# Instancia global de configuración
settings = Settings()
