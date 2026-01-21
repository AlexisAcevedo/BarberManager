# Esquema de Base de Datos

## Visión General

Barber Manager Pro utiliza **SQLite** como base de datos con **SQLAlchemy ORM** para el mapeo objeto-relacional.

## Tablas

### barbers
Almacena información de los barberos/empleados.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Identificador único |
| `name` | VARCHAR(100) | NOT NULL | Nombre del barbero |
| `color` | VARCHAR(20) | DEFAULT '#2196F3' | Color de identificación en UI |
| `is_active` | BOOLEAN | DEFAULT TRUE | Estado activo/inactivo |
| `created_at` | DATETIME | NOT NULL | Fecha de creación |

---

### users
Usuarios del sistema para autenticación.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Identificador único |
| `username` | VARCHAR(50) | UNIQUE, NOT NULL | Nombre de usuario |
| `password_hash` | VARCHAR(255) | NOT NULL | Hash bcrypt de contraseña |
| `role` | VARCHAR(20) | DEFAULT 'barber' | Rol: admin, barber |
| `barber_id` | INTEGER | FK → barbers.id | Barbero asociado |
| `is_active` | BOOLEAN | DEFAULT TRUE | Estado activo/inactivo |

---

### clients
Clientes de la barbería.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Identificador único |
| `name` | VARCHAR(100) | NOT NULL | Nombre del cliente |
| `email` | VARCHAR(150) | NOT NULL | Email (para invitaciones) |
| `phone` | VARCHAR(20) | NULLABLE | Teléfono (para WhatsApp) |
| `notes` | TEXT | NULLABLE | Notas adicionales |
| `created_at` | DATETIME | NOT NULL | Fecha de registro |

---

### services
Servicios ofrecidos por la barbería.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Identificador único |
| `name` | VARCHAR(100) | UNIQUE, NOT NULL | Nombre del servicio |
| `duration` | INTEGER | NOT NULL | Duración en minutos |
| `price` | FLOAT | DEFAULT 0.0 | Precio del servicio |
| `is_active` | BOOLEAN | DEFAULT TRUE | Servicio disponible |

---

### appointments
Turnos agendados.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Identificador único |
| `client_id` | INTEGER | FK → clients.id, NOT NULL | Cliente |
| `service_id` | INTEGER | FK → services.id, NOT NULL | Servicio |
| `barber_id` | INTEGER | FK → barbers.id, NOT NULL | Barbero asignado |
| `start_time` | DATETIME | NOT NULL | Hora de inicio |
| `end_time` | DATETIME | NOT NULL | Hora de fin |
| `status` | VARCHAR(20) | DEFAULT 'pending' | Estado del turno |
| `google_event_id` | VARCHAR(255) | UNIQUE, NULLABLE | ID evento Google |
| `created_at` | DATETIME | NOT NULL | Fecha de creación |

**Estados válidos (`status`):**
- `pending`: Turno pendiente/agendado
- `confirmed`: Turno completado/confirmado
- `cancelled`: Turno cancelado

---

### settings
Configuración clave-valor de la aplicación.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Identificador único |
| `key` | VARCHAR(50) | UNIQUE, NOT NULL | Clave de configuración |
| `value` | VARCHAR(255) | NOT NULL | Valor |

**Claves predefinidas:**
- `business_hours_start`: Hora de apertura (defecto: 12)
- `business_hours_end`: Hora de cierre (defecto: 20)
- `slot_duration`: Duración de slots en minutos (defecto: 15)

---

## Diagrama ER

```
┌─────────────┐       ┌─────────────┐
│   barbers   │       │    users    │
├─────────────┤       ├─────────────┤
│ id (PK)     │←──────│ barber_id   │
│ name        │       │ username    │
│ color       │       │ role        │
│ is_active   │       └─────────────┘
└──────┬──────┘
       │
       │ 1:N
       ↓
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│appointments │       │   clients   │       │  services   │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │       │ id (PK)     │
│ barber_id   │←──────│ name        │       │ name        │
│ client_id   │───────│ email       │       │ duration    │
│ service_id  │───────│ phone       │───────│ price       │
│ start_time  │       └─────────────┘       └─────────────┘
│ end_time    │
│ status      │
└─────────────┘

┌─────────────┐
│  settings   │
├─────────────┤
│ id (PK)     │
│ key         │
│ value       │
└─────────────┘
```

## Índices

Los siguientes índices se crean automáticamente:
- PK en todas las tablas (id)
- UNIQUE en `users.username`
- UNIQUE en `services.name`
- UNIQUE en `settings.key`
- UNIQUE en `appointments.google_event_id`
- FK índices automáticos de SQLAlchemy

## Migraciones

El proyecto usa **Alembic** para migraciones de esquema:

```bash
# Crear nueva migración
alembic revision --autogenerate -m "descripcion"

# Aplicar migraciones
alembic upgrade head

# Ver estado
alembic current
```

## Datos Semilla

Al inicializar la base de datos se crean automáticamente:

**Servicios:**
- Corte (30 min)
- Barba (15 min)
- Combo Corte+Barba (40 min)

**Usuario:**
- admin / admin (rol: admin)

**Barbero:**
- Barbero Principal (color: #7E57C2)
