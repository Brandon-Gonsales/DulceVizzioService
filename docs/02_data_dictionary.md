# 02 - Diccionario de Datos y Modelos (Frontend Reference)

## Introducción
Este documento define los **Modelos de Datos** y **Enums** exactos que la API expone, incluyendo **TODOS** los campos heredados del modelo base.
**Objetivo:** Permitir al equipo frontend (y su IA) generar interfaces TypeScript precisas y completas.

---

## 📝 Campos de Auditoría (Heredados de BaseDocument)

**TODOS** los modelos de entidad (User, Course, Lesson, Enrollment, etc.) heredan estos campos automáticamente:

| Campo | Tipo | Obligatorio | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | string | ✅ | ID único (ObjectId MongoDB). |
| `created_at` | string | ✅ | Timestamp de creación (ISO 8601 UTC). |
| `updated_at` | string | ✅ | Timestamp de última modificación (autocalculado). |
| `created_by` | string | ❌ | ID del usuario que creó el registro. |
| `updated_by` | string | ❌ | ID del usuario que modificó por última vez. |
| `revision_id` | string | ❌ | UUID de versión (cambia en cada actualización). |
| `is_deleted` | boolean | ✅ | Soft delete (default: false). |
| `deleted_at` | string | ❌ | Timestamp de eliminación lógica. |

> **Nota para Frontend:** Estos campos **siempre** están presentes en las respuestas de API pero raramente se envían en requests de creación (el backend los gestiona automáticamente).

---

## 🔠 Enums (Valores Constantes)

### `UserRole`
Roles de usuario para control de acceso.
```typescript
enum UserRole {
  USER = "USER",           // Estudiante regular (default)
  MODERATOR = "MODERATOR", // Moderador VIP
  ADMIN = "ADMIN",         // Administrador de contenido
  SUPERADMIN = "SUPERADMIN" // Propietario del sistema
}
```

### `CourseStatus`
Estado del ciclo de vida de un curso.
```typescript
enum CourseStatus {
  DRAFT = "DRAFT",         // Borrador
  REVIEW = "REVIEW",       // En revisión
  PUBLISHED = "PUBLISHED", // Público
  ARCHIVED = "ARCHIVED",   // Archivado (accesible para alumnos actuales)
  RETIRED = "RETIRED"      // Retirado completamente
}
```

### `CourseDifficulty`
Nivel de dificultad.
```typescript
enum CourseDifficulty {
  BEGINNER = "BEGINNER",
  INTERMEDIATE = "INTERMEDIATE",
  ADVANCED = "ADVANCED",
  EXPERT = "EXPERT"
}
```

### `EnrollmentStatus`
Estado de la inscripción.
```typescript
enum EnrollmentStatus {
  ACTIVE = "ACTIVE",       // Vigente
  EXPIRED = "EXPIRED",     // Periodo finalizado
  CANCELLED = "CANCELLED"  // Cancelada por admin
}
```

---

## 📦 Modelos de Entidad

### 1. `User` (Usuario)

Hereda de: **BaseDocument**

#### Campos Propios

| Campo | Tipo | Obligatorio | Validación | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `email` | string | ✅ | Email válido, único | Email de acceso. |
| `username` | string | ❌ | Único | Nombre de usuario (slug). |
| `full_name` | string | ✅ | - | Nombre completo. |
| `password_hash` | string | ✅ | - | Hash bcrypt (nunca expuesto en API). |
| `role` | `UserRole` | ✅ | Enum | Rol (default: USER). |
| `is_active` | boolean | ✅ | - | Estado de cuenta (default: true). |
| `avatar_url` | string | ❌ | URL | Foto de perfil (Cloudinary). |
| `phone_number` | string | ❌ | - | Teléfono de contacto. |
| `birth_date` | string | ❌ | ISO 8601 | Fecha de nacimiento. |

#### Ejemplo JSON Real
```json
{
  "id": "695cc40748b8077a89cb103e",
  "email": "bgonsalescoronado@gmail.com",
  "username": "Super_Administrador_Backend",
  "full_name": "Brandon Gonsales Coronado",
  "role": "SUPERADMIN",
  "is_active": true,
  "avatar_url": "https://res.cloudinary.com/dmxooones/image/upload/v1767696698/dulcevicio/avatars/jallfzycvrpz5uum6fyj.png",
  "phone_number": "+59160984296",
  "birth_date": "2002-03-20T00:00:00",
  "created_at": "2026-01-06T08:12:55",
  "updated_at": "2026-01-06T10:55:46.561000",
  "revision_id": null,
  "created_by": null,
  "updated_by": "695cc40748b8077a89cb103e",
  "is_deleted": false,
  "deleted_at": null
}
```

---

### 2. `Course` (Curso)

Hereda de: **BaseDocument**

#### Campos Propios

| Campo | Tipo | Obligatorio | Validación | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `title` | string | ✅ | Indexado | Título del curso. |
| `slug` | string | ✅ | Único, indexado | URL-friendly ID. |
| `description` | string | ✅ | - | Descripción completa (Markdown). |
| `category` | string | ✅ | Indexado | Categoría principal. |
| `subcategory` | string | ❌ | - | Subcategoría. |
| `tags` | string[] | ✅ | - | Lista de etiquetas (default: []). |
| `difficulty` | `CourseDifficulty` | ✅ | Enum | Nivel (default: INTERMEDIATE). |
| `cover_image_url` | string | ❌ | HttpUrl | Imagen de portada (Cloudinary). |
| `price` | number | ✅ | ≥ 0 | Precio. |
| `currency` | string | ✅ | 3 chars | Moneda (default: "USD"). |
| `whatsapp_group_url` | string | ❌ | HttpUrl | Link a comunidad WhatsApp. |
| `status` | `CourseStatus` | ✅ | Enum | Estado (default: DRAFT). |
| `published_at` | string | ❌ | ISO 8601 | Fecha de publicación. |
| `rating_average` | number | ❌ | 0-5 | Promedio de estrellas. |
| `enrollment_count` | number | ✅ | - | Total inscritos (default: 0). |
| `lessons_count` | number | ✅ | - | Total lecciones (autocalculado). |
| `total_duration_hours` | number | ✅ | - | Horas totales (autocalculado). |

#### Ejemplo JSON Real
```json
{
  "id": "6977fd2eb1241ae2597096eb",
  "title": "curso 1",
  "slug": "curso-1",
  "description": "stringstringstringst",
  "category": "string",
  "subcategory": "string",
  "tags": ["string"],
  "difficulty": "INTERMEDIATE",
  "cover_image_url": null,
  "price": 10.0,
  "currency": "USD",
  "whatsapp_group_url": "https://example.com/",
  "status": "DRAFT",
  "published_at": null,
  "rating_average": null,
  "enrollment_count": 0,
  "lessons_count": 3,
  "total_duration_hours": 0.0,
  "created_at": "2026-01-26T23:47:58.408000",
  "updated_at": "2026-01-26T23:52:36.794000",
  "created_by": "695cc40748b8077a89cb103e",
  "updated_by": null,
  "is_deleted": false,
  "deleted_at": null,
  "revision_id": null
}
```

---

### 3. `Lesson` (Lección)

Hereda de: **BaseDocument**

#### Campos Propios

| Campo | Tipo | Obligatorio | Validación | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `course_id` | string | ✅ | ObjectId | ID del curso padre. |
| `title` | string | ✅ | - | Título de la lección. |
| `summary` | string | ❌ | - | Resumen/descripción. |
| `duration_seconds` | number | ❌ | ≥ 0 | Duración del video (segundos). |
| `order` | number | ✅ | - | Posición secuencial (1, 2, 3...). |
| `is_preview` | boolean | ✅ | - | Si es gratis/vista previa (default: false). |
| `video_url` | string | ❌ | HttpUrl | URL streaming (Bunny.net). |
| `video_id` | string | ❌ | - | ID del video en Bunny. |
| `materials` | `LessonMaterial[]` | ✅ | - | Archivos adjuntos embebidos (default: []). |

#### Sub-modelo: `LessonMaterial` (Embebido)

**NO** hereda de BaseDocument (es un objeto anidado, no tiene colección propia).

| Campo | Tipo | Obligatorio | Descripción |
| :--- | :--- | :--- | :--- |
| `title` | string | ✅ | Nombre descriptivo. |
| `resource_url` | string | ✅ | URL de descarga (Cloudinary). |
| `file_format` | string | ❌ | Extensión (pdf, jpg, zip). |
| `is_downloadable` | boolean | ✅ | Permite descarga (default: true). |
| `order` | number | ✅ | Orden (default: 1). |
| `created_at` | string | ✅ | Timestamp de subida. |
| `created_by` | string | ❌ | ID del uploader. |

#### Ejemplo JSON Real
```json
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
  "created_at": "2026-01-26T23:52:22.865000",
  "updated_at": "2026-01-26T23:56:46.618000",
  "created_by": "695cc40748b8077a89cb103e",
  "updated_by": "695cc40748b8077a89cb103e",
  "is_deleted": false,
  "deleted_at": null,
  "revision_id": null
}
```

---

### 4. `Enrollment` (Inscripción)

Hereda de: **BaseDocument**

#### Campos Propios

| Campo | Tipo | Obligatorio | Validación | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `user_id` | string | ✅ | ObjectId | ID del estudiante. |
| `course_id` | string | ✅ | ObjectId | ID del curso. |
| `status` | `EnrollmentStatus` | ✅ | Enum | Estado (default: ACTIVE). |
| `enrolled_at` | string | ✅ | ISO 8601 | Fecha de inscripción. |
| `expires_at` | string | ✅ | ISO 8601 | Fecha fin (1 año después). |
| `last_accessed_lesson_id` | string | ❌ | ObjectId | Última lección vista. |
| `last_video_position_seconds` | number | ❌ | ≥ 0 | Segundo del video (resume). |
| `last_accessed_at` | string | ❌ | ISO 8601 | Último acceso al curso. |
| `completed_at` | string | ❌ | ISO 8601 | Fecha de finalización. |
| `certificate_url` | string | ❌ | HttpUrl | Link al certificado. |
| `notes` | string | ❌ | Max 500 chars | Notas administrativas. |

#### Ejemplo JSON Real
```json
{
  "id": "6979392db66a9eb3ebedab17",
  "user_id": "695cecf6d3c63cf174c7f068",
  "course_id": "6977fd2eb1241ae2597096eb",
  "status": "ACTIVE",
  "enrolled_at": "2026-01-27T22:16:13.280000",
  "expires_at": "2027-01-27T22:16:13.280000",
  "last_accessed_lesson_id": null,
  "last_video_position_seconds": null,
  "last_accessed_at": null,
  "completed_at": null,
  "certificate_url": null,
  "notes": null,
  "created_at": "2026-01-27T22:16:13.280000",
  "updated_at": "2026-01-27T22:16:13.280000",
  "created_by": "695cc40748b8077a89cb103e",
  "updated_by": null,
  "is_deleted": false,
  "deleted_at": null,
  "revision_id": null
}
```

---

## 📌 Notas para Implementación TypeScript

### Interfaces Base Recomendadas

```typescript
// Campos de auditoría heredados por todas las entidades
interface BaseDocument {
  id: string;
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
  revision_id?: string;
  is_deleted: boolean;
  deleted_at?: string;
}

// Ejemplo de uso
interface User extends BaseDocument {
  email: string;
  username?: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  avatar_url?: string;
  phone_number?: string;
  birth_date?: string;
}

interface Course extends BaseDocument {
  title: string;
  slug: string;
  description: string;
  category: string;
  subcategory?: string;
  tags: string[];
  difficulty: CourseDifficulty;
  cover_image_url?: string;
  price: number;
  currency: string;
  whatsapp_group_url?: string;
  status: CourseStatus;
  published_at?: string;
  rating_average?: number;
  enrollment_count: number;
  lessons_count: number;
  total_duration_hours: number;
}

interface Lesson extends BaseDocument {
  course_id: string;
  title: string;
  summary?: string;
  duration_seconds?: number;
  order: number;
  is_preview: boolean;
  video_url?: string;
  video_id?: string;
  materials: LessonMaterial[];
}

interface LessonMaterial {
  title: string;
  resource_url: string;
  file_format?: string;
  is_downloadable: boolean;
  order: number;
  created_at: string;
  created_by?: string;
}

interface Enrollment extends BaseDocument {
  user_id: string;
  course_id: string;
  status: EnrollmentStatus;
  enrolled_at: string;
  expires_at: string;
  last_accessed_lesson_id?: string;
  last_video_position_seconds?: number;
  last_accessed_at?: string;
  completed_at?: string;
  certificate_url?: string;
  notes?: string;
}
```

---

**Fin del diccionario de datos**
