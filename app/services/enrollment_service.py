"""
Servicio para lógica de negocio de Enrollments
Gestión de inscripciones a cursos individuales
"""

from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from datetime import datetime
from app.models.enrollment import Enrollment
from app.models.course import Course
from app.models.user import User
from app.models.enums import EnrollmentStatus, Role
from app.schemas.enrollment_schema import (
    EnrollmentCreateSchema,
    EnrollmentProgressUpdateSchema,
    EnrollmentExtendSchema
)


class EnrollmentService:
    
    @staticmethod
    async def create_enrollment(data: EnrollmentCreateSchema, admin: User) -> Enrollment:
        """
        Crear enrollment (solo admin).
        El admin inscribe manualmente al estudiante.
        """
        # Verificar que el curso existe
        course = await Course.get(data.course_id)
        if not course or course.is_deleted:
            raise HTTPException(status_code=404, detail="Curso no encontrado")
        
        # Verificar que el usuario existe
        user = await User.get(data.user_id)
        if not user or user.is_deleted:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Verificar si ya está inscrito
        existing = await Enrollment.find_one(
            Enrollment.user_id == data.user_id,
            Enrollment.course_id == data.course_id,
            Enrollment.status == EnrollmentStatus.ACTIVE
        )
        
        if existing and await existing.is_active_now():
            raise HTTPException(
                status_code=400,
                detail="El usuario ya tiene una inscripción activa en este curso"
            )
        
        # Crear enrollment con expiración de 1 año
        enrollment = Enrollment.create_with_expiration(
            user_id=data.user_id,
            course_id=data.course_id,
            notes=data.notes,
            created_by=str(admin.id)
        )
        
        await enrollment.save()
        
        return enrollment
    
    @staticmethod
    async def get_user_enrollments(
        user_id: str,
        search: Optional[str] = None,
        status: Optional[EnrollmentStatus] = None,
        page: int = 1,
        size: int = 10
    ) -> Dict[str, Any]:
        """Obtener enrollments de un usuario con paginación y búsqueda"""
        from bson import ObjectId
        
        # Convertir user_id string a ObjectId
        try:
            user_oid = ObjectId(user_id)
        except Exception:
            # Si el ID es inválido, retornar vacío
            return {
                "total": 0,
                "page": page,
                "per_page": size,
                "total_pages": 0,
                "data": []
            }
        
        # Usar filtros de diccionario para mayor compatibilidad
        query_filters = [{"user_id": user_oid}]
        
        if status:
            query_filters.append({"status": status})
        
        # Si hay búsqueda, necesitamos filtrar por título de curso
        if search:
            # Buscar cursos que coincidan
            matching_courses = await Course.find(
                {"title": {"$regex": search, "$options": "i"}}
            ).to_list()
            
            if matching_courses:
                course_ids = [c.id for c in matching_courses]
                query_filters.append({"course_id": {"$in": course_ids}})
            else:
                # Si no hay cursos que coincidan, retornar vacío
                return {
                    "total": 0,
                    "page": page,
                    "per_page": size,
                    "total_pages": 0,
                    "data": []
                }
        
        total = await Enrollment.find(*query_filters).count()
        
        # Calcular paginación
        total_pages = (total + size - 1) // size
        
        # Obtener items
        items = await Enrollment.find(*query_filters)\
            .sort("-enrolled_at")\
            .skip((page - 1) * size)\
            .limit(size)\
            .to_list()
        
        # Obtener IDs de cursos únicos
        course_ids = list(set([e.course_id for e in items]))
        
        # Fetch cursos en una sola query
        courses = await Course.find({"_id": {"$in": course_ids}}).to_list()
        courses_dict = {c.id: c for c in courses}
        
        # Convertir enrollments a dicts e incluir curso
        enrollments_data = []
        for enrollment in items:
            enrollment_dict = enrollment.model_dump(mode='json')
            
            # Agregar datos del curso si existe
            course = courses_dict.get(enrollment.course_id)
            if course:
                enrollment_dict["course"] = {
                    "id": str(course.id),
                    "title": course.title,
                    "slug": course.slug,
                    "cover_image_url": str(course.cover_image_url) if course.cover_image_url else None,
                    "price": course.price,
                    "currency": course.currency
                }
            
            enrollments_data.append(enrollment_dict)
        
        return {
            "total": total,
            "page": page,
            "per_page": size,
            "total_pages": total_pages,
            "data": enrollments_data
        }

    @staticmethod
    async def get_all_enrollments(
        search: Optional[str] = None,
        page: int = 1,
        size: int = 10,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Obtener todos los enrollments (Admin) con filtros, búsqueda y paginación"""
        query_filters = []
        
        if filters:
            if filters.get("user_id"):
                query_filters.append(Enrollment.user_id == filters["user_id"])
            if filters.get("course_id"):
                query_filters.append(Enrollment.course_id == filters["course_id"])
            if filters.get("status"):
                query_filters.append(Enrollment.status == filters["status"])
        
        # Si hay búsqueda, buscar en usuarios Y cursos
        if search:
            matching_user_ids = []
            matching_course_ids = []
            
            # Buscar usuarios por username o full_name
            matching_users = await User.find(
                {"$or": [
                    {"username": {"$regex": search, "$options": "i"}},
                    {"full_name": {"$regex": search, "$options": "i"}}
                ]}
            ).to_list()
            matching_user_ids = [u.id for u in matching_users]
            
            # Buscar cursos por título
            matching_courses = await Course.find(
                {"title": {"$regex": search, "$options": "i"}}
            ).to_list()
            matching_course_ids = [c.id for c in matching_courses]
            
            # Filtrar enrollments que coincidan con usuarios O cursos
            if matching_user_ids or matching_course_ids:
                or_conditions = []
                if matching_user_ids:
                    or_conditions.append({"user_id": {"$in": matching_user_ids}})
                if matching_course_ids:
                    or_conditions.append({"course_id": {"$in": matching_course_ids}})
                
                query_filters.append({"$or": or_conditions})
            else:
                # Si no hay coincidencias, retornar vacío
                return {
                    "total": 0,
                    "page": page,
                    "per_page": size,
                    "total_pages": 0,
                    "data": []
                }
            
        # Ejecutar query
        query = Enrollment.find(*query_filters)
        total = await query.count()
        
        total_pages = (total + size - 1) // size
        
        items = await query.sort("-enrolled_at")\
            .skip((page - 1) * size)\
            .limit(size)\
            .to_list()
        
        # Obtener IDs de cursos únicos
        course_ids = list(set([e.course_id for e in items]))
        
        # Fetch cursos en una sola query
        courses = await Course.find({"_id": {"$in": course_ids}}).to_list()
        courses_dict = {c.id: c for c in courses}
        
        # Convertir enrollments a dicts e incluir curso
        enrollments_data = []
        for enrollment in items:
            enrollment_dict = enrollment.model_dump(mode='json')
            
            # Agregar datos del curso si existe
            course = courses_dict.get(enrollment.course_id)
            if course:
                enrollment_dict["course"] = {
                    "id": str(course.id),
                    "title": course.title,
                    "slug": course.slug,
                    "cover_image_url": str(course.cover_image_url) if course.cover_image_url else None,
                    "price": course.price,
                    "currency": course.currency
                }
            
            enrollments_data.append(enrollment_dict)
            
        return {
            "total": total,
            "page": page,
            "per_page": size,
            "total_pages": total_pages,
            "data": enrollments_data
        }
    
    @staticmethod
    async def get_enrollment_by_id(enrollment_id: str, user: User) -> Enrollment:
        """Obtener enrollment por ID"""
        enrollment = await Enrollment.get(enrollment_id)
        
        if not enrollment:
            raise HTTPException(status_code=404, detail="Inscripción no encontrada")
        
        # Verificar permisos
        is_admin = user.role in [Role.ADMIN, Role.SUPERADMIN]
        is_owner = str(enrollment.user_id) == str(user.id)
        
        if not is_admin and not is_owner:
            raise HTTPException(status_code=403, detail="No tienes permiso para ver esta inscripción")
        
        return enrollment
    
    @staticmethod
    async def update_progress(
        enrollment_id: str,
        data: EnrollmentProgressUpdateSchema,
        user: User
    ) -> Dict[str, str]:
        """
        Actualizar progreso de video.
        Llamado por frontend cada 10-30 segundos.
        """
        enrollment = await Enrollment.get(enrollment_id)
        
        if not enrollment:
            raise HTTPException(status_code=404, detail="Inscripción no encontrada")
        
        # Solo el dueño puede actualizar su progreso
        if str(enrollment.user_id) != str(user.id):
            raise HTTPException(status_code=403, detail="No puedes actualizar esta inscripción")
        
        # Verificar que no haya expirado
        if not enrollment.is_active_now():
            raise HTTPException(status_code=403, detail="Tu inscripción ha expirado")
        
        # Actualizar progreso
        enrollment.last_accessed_lesson_id = data.lesson_id
        enrollment.last_video_position_seconds = data.video_position_seconds
        enrollment.last_accessed_at = datetime.utcnow()
        enrollment.updated_by = str(user.id)
        
        await enrollment.save()
        
        return {"message": "Progreso guardado correctamente"}
    
    @staticmethod
    async def extend_enrollment(
        enrollment_id: str,
        data: EnrollmentExtendSchema,
        admin: User
    ) -> Enrollment:
        """Extender expiración de enrollment (admin)"""
        enrollment = await Enrollment.get(enrollment_id)
        
        if not enrollment:
            raise HTTPException(status_code=404, detail="Inscripción no encontrada")
        
        # Extender fecha
        from datetime import timedelta
        enrollment.expires_at = enrollment.expires_at + timedelta(days=data.additional_days)
        enrollment.updated_by = str(admin.id)
        
        # Si estaba expirado y se extiende, reactivar
        if enrollment.status == EnrollmentStatus.EXPIRED:
            enrollment.status = EnrollmentStatus.ACTIVE
        
        await enrollment.save()
        
        return enrollment
    
    @staticmethod
    async def cancel_enrollment(enrollment_id: str, admin: User) -> Dict[str, str]:
        """Cancelar enrollment (admin)"""
        enrollment = await Enrollment.get(enrollment_id)
        
        if not enrollment:
            raise HTTPException(status_code=404, detail="Inscripción no encontrada")
        
        enrollment.status = EnrollmentStatus.CANCELLED
        enrollment.updated_by = str(admin.id)
        
        await enrollment.save()
        
        return {"message": "Inscripción cancelada correctamente"}
