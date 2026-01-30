"""
DulceVicio API - FastAPI Application
Plataforma de cursos de repostería con MongoDB Atlas
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events: startup y shutdown"""
    # Startup
    logger.info("🚀 Iniciando DulceVicio API...")
    await connect_to_mongo()
    logger.info("✅ Aplicación lista!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Cerrando aplicación...")
    await close_mongo_connection()
    logger.info("👋 Aplicación cerrada")


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API REST para gestión de cursos de repostería con MongoDB Atlas y Cloudinary",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar Rate Limiting
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Configurar CORS (permite todos los orígenes en DEBUG, específicos en producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "message": "🎂 DulceVicio API - Plataforma de Cursos de Repostería",
        "version": settings.APP_VERSION,
        "status": "healthy"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint de salud"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# Registrar routers
from app.routers import auth, users, courses, lessons, materials, enrollments

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(lessons.router)
app.include_router(materials.router)
app.include_router(enrollments.router) # Prefijo explícito para consistencia

# TODO: Registrar más routers aquí
# from app.routers import enrollments, memberships, comments
# app.include_router(enrollments.router)
# app.include_router(memberships.router)
# app.include_router(comments.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
