# 01 - Contexto y Arquitectura Backend (Reference for AI & Frontend)

## Introducción
Este documento define el **contexto arquitectónico y las convenciones globales** de la API de DulceVizzio.  
**Objetivo:** Servir como "Fuente de Verdad" inicial para que una IA entienda cómo interactuar con el backend antes de conocer los endpoints específicos.

---

## 🛠 Tech Stack Resumen
*   **Framework:** FastAPI (Python 3.10+)
*   **Database:** MongoDB Atlas (Driver: Motor / ODM: Beanie)
*   **Auth:** JWT (JSON Web Tokens) con algoritmo HS256
*   **Media Storage:**
    *   Imágenes/Documentos: Cloudinary
    *   Videos: Bunny.net Stream
*   **Protocolo:** HTTP/1.1 RESTful JSON

---

## 🌐 Base URLs & Entornos
El frontend debe configurar estas URLs base según el entorno de despliegue.

| Entorno | Base URL | Comentarios |
| :--- | :--- | :--- |
| **Development** | `http://localhost:8000` | Entorno local default |
| **Staging** | `https://api-staging.dulcevizzio.com` | (Si aplica) |
| **Production** | `https://api.dulcevizzio.com` | Servidor final en Render/AWS |

> **Nota:** Todos los endpoints relativos listados en la documentación asumen un prefijo `/api` si no se indica lo contrario dentro de la ruta (ej. `/api/auth/login`).

---

## 🔐 Convenciones de Autenticación
El sistema utiliza autenticación basada en **Headers** con tokens JWT.

### 1. Obtención del Token
El token se obtiene vía `POST /api/auth/login`. La respuesta incluye el token y el esquema de usuario.

### 2. Header Requerido
Para cualquier endpoint protegido, el frontend **DEBE** enviar el siguiente header:
```http
Authorization: Bearer <tu_access_token>
```

### 3. Expiración y Renovación
*   **Access Token Time:** Configurable (default: 30 minutos a 24 horas según env).
*   **Manejo de 401 Unauthorized:** Si la API devuelve `401`, el frontend debe redirigir al Login o intentar un flujo de refresh token (si estuviera implementado).
*   **Roles:** El payload del token (y el objeto user) contiene el campo `role` (`USER`, `MODERATOR`, `ADMIN`, `SUPERADMIN`) que determina el acceso.

---

## 🔒 Control de Acceso por Rol

### Jerarquía de Roles
```
SUPERADMIN  →  ADMIN  →  MODERATOR  →  USER
(Máximo)                             (Mínimo)
```

### Matriz de Permisos por Endpoint

| Endpoint | Método | USER | MODERATOR | ADMIN | SUPERADMIN | Notas |
|:---------|:-------|:-----|:----------|:------|:-----------|:------|
| **Autenticación** |
| `/api/auth/login` | POST | 🌐 | 🌐 | 🌐 | 🌐 | Público |
| `/api/auth/me` | GET | ✅ | ✅ | ✅ | ✅ | Usuario autenticado |
| `/api/auth/me/avatar` | PATCH | ✅ | ✅ | ✅ | ✅ | Subir propio avatar |
| `/api/auth/me/change-password` | PATCH | ✅ | ✅ | ✅ | ✅ | Solo propio password |
| **Cursos** |
| `/api/courses` | GET | ✅¹ | ✅¹ | ✅² | ✅² | ¹Ve PUBLISHED ²Ve todos |
| `/api/courses/{slug}` | GET | ✅¹ | ✅¹ | ✅² | ✅² | ¹Solo PUBLISHED ²Todos |
| `/api/courses` | POST | ❌ | ❌ | ✅ | ✅ | |
| `/api/courses/{id}` | PUT | ❌ | ❌ | ✅ | ✅ | |
| `/api/courses/{id}/status` | PATCH | ❌ | ❌ | ✅ | ✅ | Cambiar estado |
| `/api/courses/{id}/cover` | PATCH | ❌ | ❌ | ✅ | ✅ | Subir portada |
| `/api/courses/{id}` | DELETE | ❌ | ❌ | ✅³ | ✅⁴ | ³Soft / ⁴Hard delete |
| **Lecciones** |
| `/api/courses/{id}/lessons` | GET | ✅ | ✅ | ✅ | ✅ | Metadata básica |
| `/api/lessons/{id}` | GET | ✅⁵ | ✅⁵ | ✅ | ✅ | ⁵Verifica enrollment |
| `/api/courses/{id}/lessons` | POST | ❌ | ❌ | ✅ | ✅ | |
| `/api/lessons/{id}` | PUT | ❌ | ❌ | ✅ | ✅ | |
| `/api/lessons/{id}/order` | PATCH | ❌ | ❌ | ✅ | ✅ | Reordenar |
| `/api/lessons/{id}` | DELETE | ❌ | ❌ | ✅ | ✅ | |
| **Materiales** |
| `/api/lessons/{id}/materials` | POST | ❌ | ❌ | ✅ | ✅ | Subir material |
| `/api/lessons/{id}/materials` | DELETE | ❌ | ❌ | ✅ | ✅ | Eliminar todos |
| **Enrollments** |
| `/api/enrollments/me` | GET | ✅ | ✅ | ✅ | ✅ | Mis cursos |
| `/api/enrollments/{id}` | GET | ✅⁶ | ✅⁶ | ✅ | ✅ | ⁶Solo si es dueño |
| `/api/enrollments/{id}/progress` | PATCH | ✅⁶ | ✅⁶ | ❌ | ❌ | ⁶Solo dueño |
| `/api/enrollments` | GET | ❌ | ❌ | ✅ | ✅ | Listar todos |
| `/api/enrollments` | POST | ❌ | ❌ | ✅ | ✅ | Inscribir estudiante |
| `/api/enrollments/{id}/extend` | PATCH | ❌ | ❌ | ✅ | ✅ | Extender expiración |
| `/api/enrollments/{id}` | DELETE | ❌ | ❌ | ✅ | ✅ | Cancelar |
| **Usuarios** |
| `/api/users` | GET | ❌ | ❌ | ✅ | ✅ | Listar usuarios |
| `/api/users/{id}` | GET | ❌ | ❌ | ✅ | ✅ | Ver usuario |
| `/api/users` | POST | ❌ | ❌ | ✅⁷ | ✅⁸ | ⁷Solo MOD/USER ⁸+ADMIN |
| `/api/users/{id}` | PATCH | ❌ | ❌ | ✅⁹ | ✅ | ⁹No edita Admins |
| `/api/users/{id}/avatar` | PATCH | ❌ | ❌ | ✅⁹ | ✅ | |
| `/api/users/{id}/toggle-active` | PATCH | ❌ | ❌ | ✅⁹ | ✅ | |
| `/api/users/{id}/change-role` | PATCH | ❌ | ❌ | ✅⁹ | ✅ | |
| `/api/users/{id}` | DELETE | ❌ | ❌ | ✅¹⁰ | ✅¹¹ | ¹⁰Soft / ¹¹Hard |

**Leyenda:**
- 🌐 = Público (sin autenticación)
- ✅ = Permitido (requiere autenticación)
- ❌ = Prohibido (403 Forbidden)

**Notas Importantes**:
- **¹** USER/MODERATOR autenticados solo ven cursos `PUBLISHED`
- **²** ADMIN/SUPERADMIN ven cursos en cualquier estado (DRAFT, REVIEW, etc.)
- **⁵** Acceso a lección requiere enrollment activo o ser admin
- **⁶** Usuario solo puede ver/actualizar sus propios enrollments

**Reglas de Jerarquía:**
- **ADMIN** solo puede crear/editar usuarios con roles **MODERATOR** o **USER**
- **ADMIN** no puede modificar a otros **ADMIN** ni **SUPERADMIN**
- **SUPERADMIN** puede editar cualquier usuario excepto crear nuevos **SUPERADMIN**
- Solo **SUPERADMIN** puede hacer **hard delete** (eliminación física)

---

## 📦 Estándares de Respuesta (JSON Envelopes)
La API sigue una estructura predecible para todas las respuestas.

### Respuesta Exitosa (Resource/Object)
Para obtener un solo objeto (ej. `GET /courses/slug-123`):
```json
{
  "id": "507f1f77bcf86cd799439011",
  "title": "Curso Ejemplo",
  "created_at": "2023-01-01T12:00:00Z"
  // ... resto de campos
}
```

### Respuesta Exitosa (List/Collection + Pagination)
Para listados (ej. `GET /courses`), siempre se envuelve en un objeto de paginación estándar:
```json
{
  "data": [
    { "id": "1", "title": "Curso A" },
    { "id": "2", "title": "Curso B" }
  ],
  "total": 45,        // Total de items en la BD que coinciden con el filtro
  "page": 1,          // Página actual
  "limit": 10,        // Items por página
  "pages": 5          // Total de páginas disponibles
}
```

> **Regla para Frontend:** Si el endpoint devuelve una lista, espera siempre la estructura `data`, `total`, `page`, `limit`.

---

## ⚠️ Manejo de Errores Estándar
Los errores siempre devuelven un JSON con la clave `detail`.

### Estructura de Error Simple
```json
{
  "detail": "Credenciales incorrectas"
}
```

### Estructura de Error de Validación (Pydantic / 422)
Cuando los datos enviados no cumplen el schema esperado:
```json
{
  "detail": [
    {
      "loc": ["body", "price"],
      "msg": "Input should be greater than 0",
      "type": "greater_than"
    }
  ]
}
```
> **Regla para IA/Frontend:** Mapear `loc` (location) al campo del formulario correspondiente para mostrar el error al usuario.

### Códigos HTTP Clave
*   `200 OK`: Éxito síncrono.
*   `201 Created`: Recurso creado exitosamente.
*   `400 Bad Request`: Error de lógica de negocio (ej. "El curso ya está publicado").
*   `401 Unauthorized`: Falta token o token inválido.
*   `403 Forbidden`: Token válido pero rol insuficiente (ej. Student intentando borrar curso).
*   `404 Not Found`: Recurso no existe.
*   `422 Unprocessable Entity`: Error de validación de campos (types incorrectos, faltantes).
*   `500 Internal Error`: Bug del servidor.

---

## 🔍 Convenciones de Query Parameters (Filtrado)
Los endpoints de listado (`GET`) soportan parámetros estándar:
*   `?page=1`: Número de página
*   `?limit=10`: Tamaño de página (Max: 100)
*   `?search=texto`: Búsqueda parcial case-insensitive (generalmente por título/nombre).
*   `?sort=-created_at`: (Opcional si soportado) Ordenamiento, `-` indica descendente.

---

## 📅 Formato de Fechas
Todas las fechas (`created_at`, `updated_at`, etc.) se devuelven en formato **ISO 8601 UTC**:
`YYYY-MM-DDTHH:MM:SS.mmmmmm`
Ejemplo: `2026-01-27T10:30:00.123456`

> **Recomendación Frontend:** Parsear siempre como UTC y mostrar en la zona horaria local del usuario.

## 📄 Tipos de Datos Especiales
*   **ObjectIDs:** Se devuelven siempre como `string` (ej. "507f1f77bcf86cd799439011").
*   **Enums:** Se devuelven como string en MAYÚSCULAS (ej. `PUBLISHED`, `STUDENT`).
