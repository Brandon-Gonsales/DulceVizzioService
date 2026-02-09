"""
Servicio para lógica de negocio de Cursos
REFACTORIZADO: Trabaja con relaciones Course-Lesson
"""

from typing import List, Optional, Dict, Any
from fastapi import UploadFile, HTTPException
from beanie.operators import In
from app.models.course import Course
from app.models.lesson import Lesson
from app.models.user import User
from app.models.enums import CourseStatus, Role
from app.schemas.course_schema import CourseCreateSchema, CourseUpdateSchema
from app.utils.slug import generate_slug, ensure_unique_slug_course
from app.services.cloudinary_service import CloudinaryService
from datetime import datetime

class CourseService:
    
    @staticmethod
    async def update_course_stats(course_id: str):
        """
        Recalcula y guarda estadísticas del curso en DB.
        Debe llamarse cuando se agregan/eliminan/editan lecciones.
        """
        from bson import ObjectId
        # Asegurar que sea ObjectId si viene como str
        if isinstance(course_id, str):
            try:
                course_id = ObjectId(course_id)
            except:
                return

        course = await Course.get(course_id)
        if not course:
            return
        
        # Calcular estadísticas reales
        lessons = await Lesson.find({"course_id": course.id}).to_list()
        
        course.lessons_count = len(lessons)
        total_seconds = sum(l.duration_seconds or 0 for l in lessons)
        course.total_duration_hours = round(total_seconds / 3600, 2)
        
        # Guardar cambios
        await course.save()

    @staticmethod
    async def get_courses(
        page: int = 1, 
        limit: int = 10,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        current_user: Optional[User] = None
    ) -> Dict[str, Any]:
        """
        Obtener lista paginada de cursos con filtros.
        Calcula is_enrolled para cada curso según el usuario actual.
        """
        query_filters = [Course.is_deleted == False]
        # Calcular vista pública basada en el usuario
        is_admin = current_user and current_user.role in [Role.ADMIN, Role.SUPERADMIN]
        public_view = not is_admin #si no es admin, entonces se activa la vista publica  

        if public_view:
            query_filters.append(Course.status == CourseStatus.PUBLISHED)
        elif status:
            try:
                query_filters.append(Course.status == CourseStatus(status))
            except ValueError:
                pass
            
        if category:
            query_filters.append(Course.category == category)
            
        if difficulty:
            query_filters.append(Course.difficulty == difficulty)
            
        if search:
            query_filters.append({"title": {"$regex": search, "$options": "i"}})

        query = Course.find(*query_filters)
        total = await query.count()
        
        skip = (page - 1) * limit
        courses = await query.sort("-created_at").skip(skip).limit(limit).to_list()
        
        # Calcular is_enrolled para cada curso
        if current_user:
            from app.models.enrollment import Enrollment
            
            # Verificar si es admin (acceso total)
            if current_user.role in [Role.ADMIN, Role.SUPERADMIN]:
                # Admin tiene acceso a todo
                for course in courses:
                    course.is_enrolled = True
            else:
                # Usuario regular: obtener enrollments activos en UNA sola query
                enrollments = await Enrollment.find({
                    "user_id": current_user.id,
                    "status": "ACTIVE"
                }).to_list()
                
                # Crear set de course_ids para búsqueda O(1)
                enrolled_course_ids = set()
                for e in enrollments:
                    if await e.is_active_now():
                        enrolled_course_ids.add(e.course_id)
                
                # Marcar cursos inscritos
                for course in courses:
                    course.is_enrolled = course.id in enrolled_course_ids

        # Convertir cursos a dicts e incluir is_enrolled manualmente
        courses_data = []
        for course in courses:
            course_dict = course.model_dump(mode='json')
            course_dict["is_enrolled"] = course.is_enrolled
            courses_data.append(course_dict)
        
        return {
            "data": courses_data,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }

    @staticmethod
    async def get_course_by_slug(slug: str, current_user: Optional[User] = None) -> Dict[str, Any]:
        """Obtener curso por slug con control de acceso híbrido"""
        # Calcular vista pública basada en el usuario
        is_admin = current_user and current_user.role in [Role.ADMIN, Role.SUPERADMIN]
        public_view = not is_admin

        # Usar filtros por diccionario para evitar problemas con Beanie Indexed fields
        query_filters = [{"slug": slug}, {"is_deleted": False}]
        
        if public_view:
            query_filters.append({"status": CourseStatus.PUBLISHED})
            
        course = await Course.find_one(*query_filters)

        if not course:
            raise HTTPException(status_code=404, detail="Curso no encontrado")
        
        # Verificar inscripción y setear is_enrolled
        if current_user:
            from app.models.enrollment import Enrollment
            # Verificar si es admin (acceso total)
            if current_user.role in [Role.ADMIN, Role.SUPERADMIN]:
                course.is_enrolled = True
            else:
                # Verificar si tiene inscripción activa
                enrollment = await Enrollment.find_one({
                    "user_id": current_user.id,
                    "course_id": course.id,
                    "status": "ACTIVE"
                })
                if enrollment and await enrollment.is_active_now():
                    course.is_enrolled = True
        
        # --- NUEVO: Obtener y filtar Lecciones ---
        from app.models.lesson import Lesson
        
        # 1. Obtener todas las lecciones del curso ordenadas
        lessons = await Lesson.find({"course_id": course.id}).sort("order").to_list()
        
        # 2. Filtrar contenido sensible si NO está inscrito
        if not course.is_enrolled:
            for lesson in lessons:
                # Si NO es preview, ocultar video y materiales
                if not lesson.is_preview:
                    lesson.video_url = None
                    lesson.video_id = None
                    lesson.materials = []
        
        # 3. Convertir curso a dict y agregar lecciones
        course_dict = course.model_dump(mode='json')
        course_dict["is_enrolled"] = course.is_enrolled  # Incluir manualmente (exclude=True en modelo)
        course_dict["lessons"] = [lesson.model_dump(mode='json') for lesson in lessons]

        return course_dict

    @staticmethod
    async def create_course(data: CourseCreateSchema, user: User) -> Course:
        """Crear nuevo curso"""
        slug_base = generate_slug(data.title)
        slug = await ensure_unique_slug_course(slug_base)
        
        course_data = data.model_dump()
        course = Course(
            **course_data,
            slug=slug,
            status=CourseStatus.DRAFT,
            created_by=str(user.id)
        )
        
        await course.save()
        return course

    @staticmethod
    async def update_course(course_id: str, data: CourseUpdateSchema, user: User) -> Course:
        """Actualizar curso"""
        course = await Course.get(course_id)
        if not course or course.is_deleted:
            raise HTTPException(status_code=404, detail="Curso no encontrado")
            
        update_data = data.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(course, key, value)
            
        course.updated_by = str(user.id)
        await course.save()
        return course

    @staticmethod
    async def update_status(course_id: str, status: CourseStatus, user: User) -> Course:
        """Cambiar estado del curso"""
        course = await Course.get(course_id)
        if not course or course.is_deleted:
            raise HTTPException(status_code=404, detail="Curso no encontrado")
            
        if course.status != status:
            course.status = status
            
            if status == CourseStatus.PUBLISHED and not course.published_at:
                course.published_at = datetime.utcnow()
                
            course.updated_by = str(user.id)
            await course.save()
        
        return course

    @staticmethod
    async def upload_cover_image(course_id: str, file: UploadFile, user: User) -> Course:
        """Subir imagen de portada"""
        course = await Course.get(course_id)
        if not course or course.is_deleted:
            raise HTTPException(status_code=404, detail="Curso no encontrado")
            
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
            
        try:
            url = await CloudinaryService.upload_image(file, folder="courses/covers")
            
            course.cover_image_url = url
            course.updated_by = str(user.id)
            await course.save()
            
            return course
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al subir imagen: {str(e)}")

    @staticmethod
    async def delete_course(course_id: str, user: User) -> Dict[str, str]:
        """
        Eliminar curso
        - ADMIN: Soft delete
        - SUPERADMIN: Hard delete (físico) + eliminar lessons relacionadas
        """
        course = await Course.get(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Curso no encontrado")
            
        if user.role == Role.SUPERADMIN:
            # Borrado FÍSICO: eliminar lessons asociadas también
            await Lesson.find({"course_id": course.id}).delete()
            await course.delete()
            return {"message": "Curso eliminado permanentemente"}
        elif user.role == Role.ADMIN:
            # Borrado LÓGICO
            course.is_deleted = True
            course.deleted_at = datetime.utcnow()
            course.updated_by = str(user.id)
            await course.save()
            return {"message": "Curso enviado a papelera"}
        else:
             raise HTTPException(status_code=403, detail="No tienes permisos para eliminar cursos")
