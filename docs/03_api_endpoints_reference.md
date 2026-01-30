# 03 - Referencia de Endpoints API

## Introducción
Este documento lista **todos los endpoints** disponibles en la API de DulceVizzio organizados por dominio.
Cada endpoint incluye: método HTTP, headers requeridos, body esperado, respuestas exitosas y errores comunes.

---

## 🔐 Autenticación

### POST `/api/auth/login`
Autenticar usuario y obtener token JWT.

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "bgonsalescoronado@gmail.com",
  "password": "tu_contraseña_segura"
}
```

**Response 200 OK:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "695cc40748b8077a89cb103e",
    "email": "bgonsalescoronado@gmail.com",
    "full_name": "Brandon Gonsales Coronado",
    "username": "Super_Administrador_Backend",
    "role": "SUPERADMIN",
    "is_active": true,
    "avatar_url": "https://res.cloudinary.com/...",
    "created_at": "2026-01-06T08:12:55"
  }
}
```

**Errores:**
- `401` - Credenciales incorrectas
- `422` - Error de validación (email mal formado)

### GET `/api/auth/me`
Obtener perfil del usuario autenticado.

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200 OK:** Objeto `User` (ver Diccionario de Datos).

---

## 📚 Cursos

### GET `/api/courses`
Listar todos los cursos publicados (con paginación).

**Query Parameters:**
- `page` (int, default: 1)
- `limit` (int, default: 10, max: 100)
- `category` (string, opcional)
- `difficulty` (enum: BEGINNER | INTERMEDIATE | ADVANCED | EXPERT, opcional)
- `status` (enum: DRAFT | REVIEW | PUBLISHED | ARCHIVED | RETIRED, opcional - solo visible para Admins)
- `search` (string, opcional) - Búsqueda por título

**Response 200 OK:**
```json
{
  "data": [
    {
      "id": "6977fd2eb1241ae2597096eb",
      "title": "curso 1",
      "slug": "curso-1",
      "description": "stringstringstringst",
      "category": "string",
      "subcategory": "string",
      "tags": ["string"],
      "difficulty": "INTERMEDIATE",
      "price": 10.0,
      "currency": "USD",
      "cover_image_url": null,
      "status": "DRAFT",
      "rating_average": null,
      "enrollment_count": 0,
      "lessons_count": 3,
      "total_duration_hours": 0.0,
      "created_at": "2026-01-26T23:47:58.408000"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10,
  "pages": 1
}
```

### GET `/api/courses/{slug}`
Obtener un curso por su slug.

**Path Params:** `slug` (string)

**Response 200 OK:** Objeto `Course` individual.

**Errores:**
- `404` - Curso no encontrado

### POST `/api/courses`
Crear nuevo curso (Admin).

**Headers:**
```
Authorization: Bearer {admin_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Curso de Macarons Avanzado",
  "description": "Aprende técnicas avanzadas de merengue francés y macaronage perfecto con al menos 20 caracteres",
  "price": 49.99,
  "currency": "USD",
  "difficulty": "ADVANCED",
  "category": "Repostería",
  "subcategory": "Macarons",
  "tags": ["macarons", "francés", "repostería"],
  "whatsapp_group_url": "https://chat.whatsapp.com/invite123"
}
```

**Response 201 Created:** Objeto `Course` con `status: "DRAFT"` y `slug` autogenerado.

**Errores:**
- `401` - No autenticado
- `403` - Rol insuficiente (no Admin)
- `422` - Validación fallida (título muy corto, precio negativo, etc.)

### PUT `/api/courses/{id}`
Actualizar curso existente (Admin).

**Headers:**
```
Authorization: Bearer {admin_token}
Content-Type: application/json
```

**Request Body:** (Todos los campos opcionales)
```json
{
  "description": "Nueva descripción más detallada con al menos 20 caracteres",
  "price": 59.99
}
```

**Response 200 OK:** Objeto `Course` actualizado.

### PATCH `/api/courses/{id}/status`
Cambiar estado del curso (Admin).

**Request Body:**
```json
{
  "status": "PUBLISHED"
}
```

**Valores permitidos:** `DRAFT`, `REVIEW`, `PUBLISHED`, `ARCHIVED`, `RETIRED`

**Response 200 OK:** Curso con nuevo estado.

### PATCH `/api/courses/{id}/cover`
Subir imagen de portada (Admin).

**Headers:**
```
Authorization: Bearer {admin_token}
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: Imagen (JPG, PNG, WebP, max 5MB)

**Response 200 OK:** Curso con `cover_image_url` actualizado (Cloudinary).

### DELETE `/api/courses/{id}`
Eliminar curso (Admin: soft delete | Superadmin: hard delete).

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response 200 OK:**
```json
{
  "message": "Curso eliminado correctamente"
}
```

---

## 🎓 Lecciones

### GET `/api/courses/{course_id}/lessons`
Listar lecciones de un curso (ordenadas por `order`).

**Response 200 OK:** Array de objetos `Lesson`.

```json
[
  {
    "id": "6977fe36b1241ae2597096ee",
    "course_id": "6977fd2eb1241ae2597096eb",
    "title": "leccion primera",
    "summary": "stringstri",
    "duration_seconds": 0,
    "order": 1,
    "is_preview": false,
    "video_url": "https://example.com/",
    "video_id": "string",
    "materials": [],
    "created_at": "2026-01-26T23:52:22.865000"
  }
]
```

### GET `/api/lessons/{lesson_id}`
Obtener lección por ID.

**Response 200 OK:** Objeto `Lesson`.

### POST `/api/courses/{course_id}/lessons`
Crear lección (Admin).

**Headers:**
```
Authorization: Bearer {admin_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Lección 2: Técnica del Macaronage",
  "summary": "Aprende a doblar la masa sin romper las burbujas de aire formadas",
  "video_url": "https://video.bunnycdn.com/play/12345/abcdef",
  "video_id": "abcdef-12345",
  "duration_seconds": 1800,
  "is_preview": false
}
```

> **Nota:** El campo `order` se calcula automáticamente (última posición + 1).

**Response 201 Created:** Objeto `Lesson`.

**Efecto secundario:** Actualiza `lessons_count` y `total_duration_hours` del curso padre.

### PUT `/api/lessons/{lesson_id}`
Actualizar lección (Admin).

**Request Body:** (Campos opcionales)
```json
{
  "summary": "Resumen actualizado más descriptivo",
  "duration_seconds": 2000
}
```

**Response 200 OK:** Objeto `Lesson` actualizado.

### PATCH `/api/lessons/{lesson_id}/order`
Reordenar lección dentro del curso (Admin).

**Request Body:**
```json
{
  "order": 3
}
```

**Response 200 OK:** Array con todas las lecciones del curso reordenadas.

### DELETE `/api/lessons/{lesson_id}`
Eliminar lección (Admin).

**Response 200 OK:**
```json
{
  "message": "Lección eliminada correctamente"
}
```

**Efecto secundario:** Recalcula estadísticas del curso y reordena lecciones restantes.

---

## 📎 Materiales

> **Nota:** Los materiales son embebidos en Lecciones. Se consultan junto con `GET /lessons/{id}`.

### POST `/api/lessons/{lesson_id}/materials`
Subir material adjunto (Admin).

**Headers:**
```
Authorization: Bearer {admin_token}
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: Archivo (PDF, DOCX, JPG, PNG, ZIP - max 10MB)
- `title`: Nombre descriptivo
- `is_downloadable`: Boolean (default: true)

**Response 201 Created:**
```json
{
  "title": "Receta de Macarons",
  "resource_url": "https://res.cloudinary.com/dulcevicio/materials/abc123.pdf",
  "file_format": "pdf",
  "is_downloadable": true,
  "order": 1,
  "created_at": "2026-01-27T12:00:00Z"
}
```

### DELETE `/api/lessons/{lesson_id}/materials`
Eliminar **TODOS** los materiales de una lección (Admin).

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response 200 OK:**
```json
{
  "message": "Se eliminaron 3 materiales correctamente"
}
```

---

## 📝 Inscripciones (Enrollments)

### Endpoints de Usuario

#### GET `/api/enrollments/me`
Listar MIS cursos inscritos (Usuario autenticado).

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters:**
- `status` (ACTIVE | EXPIRED | CANCELLED, opcional)
- `page` (int, default: 1)
- `size` (int, default: 10, max: 100)

**Response 200 OK:**
```json
{
  "total": 3,
  "page": 1,
  "per_page": 10,
  "total_pages": 1,
  "data": [
    {
      "id": "6979392db66a9eb3ebedab17",
      "user_id": "695cecf6d3c63cf174c7f068",
      "course_id": "6977fd2eb1241ae2597096eb",
      "status": "ACTIVE",
      "enrolled_at": "2026-01-27T22:16:13.280000",
      "expires_at": "2027-01-27T22:16:13.280000",
      "last_accessed_lesson_id": null,
      "last_video_position_seconds": null
    }
  ]
}
```

#### GET `/api/enrollments/{enrollment_id}`
Obtener detalle de un enrollment.

**Headers:**
```
Authorization: Bearer {token}
```

**Permisos:**
- El dueño del enrollment puede verlo
- Admins pueden ver cualquiera

**Response 200 OK:** Objeto `Enrollment` completo.

**Errores:**
- `404` - Enrollment no encontrado
- `403` - Sin permisos para ver este enrollment

#### PATCH `/api/enrollments/{enrollment_id}/progress`
Actualizar progreso de video (Usuario).

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "lesson_id": "6977fe36b1241ae2597096ee",
  "video_position_seconds": 345
}
```

**Response 200 OK:**
```json
{
  "message": "Progreso guardado correctamente"
}
```

**Errores:**
- `403` - Solo el dueño puede actualizar su progreso
- `403` - Inscripción expirada

---

### Endpoints Administrativos

#### POST `/api/enrollments`
Inscribir estudiante a un curso (Admin).

**Headers:**
```
Authorization: Bearer {admin_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_id": "695cecf6d3c63cf174c7f068",
  "course_id": "6977fd2eb1241ae2597096eb",
  "notes": "Pago verificado - Transferencia bancaria"
}
```

**Response 201 Created:** Objeto `Enrollment` con `expires_at` automático (1 año).

```json
{
  "id": "6979392db66a9eb3ebedab17",
  "user_id": "695cecf6d3c63cf174c7f068",
  "course_id": "6977fd2eb1241ae2597096eb",
  "status": "ACTIVE",
  "enrolled_at": "2026-01-27T22:16:13.280000",
  "expires_at": "2027-01-27T22:16:13.280000",
  "notes": "Pago verificado - Transferencia bancaria"
}
```

**Errores:**
- `400` - Usuario ya inscrito activamente
- `404` - Curso o usuario no encontrado

#### GET `/api/enrollments`
Listar TODOS los enrollments con filtros (Admin).

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Query Parameters:**
- `user_id` (string, opcional) - Filtrar por estudiante
- `course_id` (string, opcional) - Filtrar por curso
- `status` (ACTIVE | EXPIRED | CANCELLED, opcional)
- `page`, `size` (paginación)

**Response 200 OK:** Mismo formato que `/enrollments/me`.

#### PATCH `/api/enrollments/{enrollment_id}/extend`
Extender fecha de expiración (Admin).

**Headers:**
```
Authorization: Bearer {admin_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "additional_days": 90
}
```

**Response 200 OK:** Enrollment con `expires_at` extendido.

> **Nota:** Si el enrollment estaba EXPIRED, se reactiva automáticamente a ACTIVE.

#### DELETE `/api/enrollments/{enrollment_id}`
Cancelar enrollment (Admin).

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response 200 OK:**
```json
{
  "message": "Inscripción cancelada correctamente"
}
```

> **Nota:** Cambia `status` a CANCELLED. No elimina el registro.

---

## 👥 Usuarios (Gestión Administrativa)

### POST `/api/users`
Crear usuario (Admin/Superadmin).

**Headers:**
```
Authorization: Bearer {admin_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "nuevo@dulcevicio.com",
  "password": "Password123!",
  "full_name": "María González",
  "username": "maria_gonzalez",
  "role": "USER",
  "phone_number": "+59170123456",
  "birth_date": "1995-05-15T00:00:00"
}
```

**Permisos:**
- **SUPERADMIN** puede crear: ADMIN, MODERATOR, USER
- **ADMIN** puede crear: MODERATOR, USER

**Response 201 Created:** Objeto `User`.

**Errores:**
- `403` - Intentando crear un rol superior a tu jerarquía
- `400` - Email o username ya existe
- `422` - Validación fallida (contraseña débil, email inválido)

### GET `/api/users`
Listar usuarios con paginación y filtros (Admin).

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Query Parameters:**
- `page` (int, default: 1)
- `per_page` (int, default: 10, max: 100)
- `q` (string, opcional) - Búsqueda en email/username/full_name/phone
- `role` (enum: USER | MODERATOR | ADMIN, opcional)
- `is_active` (boolean, opcional)

**Response 200 OK:**
```json
{
  "total": 15,
  "page": 1,
  "per_page": 10,
  "total_pages": 2,
  "data": [
    {
      "id": "695cc40748b8077a89cb103e",
      "email": "user@example.com",
      "username": "user_example",
      "full_name": "Usuario Ejemplo",
      "role": "USER",
      "is_active": true,
      "avatar_url": "https://res.cloudinary.com/...",
      "created_at": "2026-01-06T08:12:55"
    }
  ]
}
```

### GET `/api/users/{user_id}`
Obtener usuario por ID (Admin).

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response 200 OK:** Objeto `User`.

**Errores:**
- `404` - Usuario no encontrado

### PATCH `/api/users/{user_id}`
Actualizar datos del usuario (Admin).

**Headers:**
```
Authorization: Bearer {admin_token}
Content-Type: application/json
```

**Request Body:** (Campos opcionales)
```json
{
  "email": "nuevo_email@example.com",
  "full_name": "Nombre Actualizado",
  "username": "nuevo_username",
  "phone_number": "+59170987654",
  "birth_date": "1995-05-15T00:00:00"
}
```

**Jerarquía:**
- **SUPERADMIN** puede editar a cualquiera
- **ADMIN** puede editar a MODERATOR y USER (no a otros Admins)

**Response 200 OK:** Objeto `User` actualizado.

**Errores:**
- `403` - Jerarquía insuficiente
- `400` - Email o username duplicado

### PATCH `/api/users/{user_id}/avatar`
Subir avatar de usuario (Admin).

**Headers:**
```
Authorization: Bearer {admin_token}
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: Imagen (JPG, PNG, max 5MB)

**Response 200 OK:** Usuario con `avatar_url` actualizado (Cloudinary).

---

**Fin de la referencia de endpoints**

