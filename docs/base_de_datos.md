# Esquema de Base de Datos - Barber Manager Pro

Documentación completa del esquema de base de datos, relaciones, índices, constraints y migraciones del sistema de gestión de turnos.

---

## Tabla de Contenidos

- [Visión General](#visión-general)
- [Tablas del Sistema](#tablas-del-sistema)
- [Relaciones](#relaciones)
- [Índices y Optimización](#índices-y-optimización)
- [Constraints](#constraints)
- [Migraciones con Alembic](#migraciones-con-alembic)
- [Data Seeding](#data-seeding)
- [Queries Comunes](#queries-comunes)

---

## Visión General

Barber Manager Pro utiliza **SQLite** como base de datos embedded con **SQLAlchemy 2.0** como ORM (Object-Relational Mapping).

### Características de la Base de Datos

- **Motor**: SQLite 3
- **ORM**: SQLAlchemy 2.0+ con Mapped types
- **Migraciones**: Alembic 1.13+
- **Ubicación**: `barber_manager.db` (configurable vía `.env`)
- **Transacciones**: ACID compliant
- **Thread-safety**: Configurado con `check_same_thread=False`

### Estadísticas del Schema

| Métrica | Valor |
|---------|-------|
| Tablas | 6 |
| Relaciones | 5 Foreign Keys |
| Índices | 8 (3 automáticos + 5 custom) |
| Constraints | 10+ |

---

## Tablas del Sistema

### 1. `barbers` - Barberos/Personal

Almacena información de los barberos que trabajan en la barbería.

#### Estructura

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Identificador único |
| `name` | VARCHAR(100) | NOT NULL | Nombre completo del barbero |
| `color` | VARCHAR(20) | DEFAULT '#2196F3' | Color de identificación en UI (formato hex) |
| `is_active` | BOOLEAN | DEFAULT TRUE | Estado activo/inactivo |
| `created_at` | DATETIME | NOT NULL, DEFAULT now() | Fecha de creación del registro |

#### Relaciones

- **1:1** con `users` - Un barbero puede tener una cuenta de usuario
- **1:N** con `appointments` - Un barbero puede tener muchos turnos

#### Validaciones de Negocio

- No permitir desactivar si es el **último barbero activo**
- No permitir desactivar si tiene **citas futuras**
- Nombre debe ser único (validado en servicio)
- Color debe ser formato hexadecimal válido

#### Ejemplo de Registro

```sql
INSERT INTO barbers (id, name, color, is_active, created_at)
VALUES (1, 'Barbero Principal', '#7E57C2', TRUE, '2026-01-20 10:00:00');
```

---

### 2. `users` - Usuarios del Sistema

Usuarios para autenticación y control de acceso.

#### Estructura

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Identificador único |
| `username` | VARCHAR(50) | UNIQUE, NOT NULL | Nombre de usuario (login) |
| `password_hash` | VARCHAR(255) | NOT NULL | Hash bcrypt de la contraseña |
| `role` | VARCHAR(20) | DEFAULT 'barber' | Rol: 'admin' o 'barber' |
| `barber_id` | INTEGER | FK → barbers.id, NULLABLE | Barbero asociado (NULL si es admin puro) |
| `is_active` | BOOLEAN | DEFAULT TRUE | Usuario activo/inactivo |
| `failed_attempts` | INTEGER | DEFAULT 0 | Contador de intentos fallidos de login |
| `locked_until` | DATETIME | NULLABLE | Fecha hasta la cual está bloqueado |
| `must_change_password` | BOOLEAN | DEFAULT TRUE | Forzar cambio de password en primer login |

#### Relaciones

- **N:1** con `barbers` - Un usuario pertenece a un barbero (opcional)

#### Campos de Seguridad

##### Rate Limiting

- **`failed_attempts`**: Incrementa en cada login fallido, resetea en éxito
- **`locked_until`**: Se establece a `now() + 5 minutos` tras 5 intentos fallidos
- **Algoritmo**: Ver [seguridad.md](seguridad.md)

##### Cambio Forzado de Contraseña

- **`must_change_password`**: Se establece a `TRUE` al crear usuario
- Al hacer login, si es `TRUE`, redirige a `change_password_view`
- Se establece a `FALSE` tras cambiar contraseña

#### Valores del Enum `role`

| Rol | Permisos |
|-----|----------|
| `admin` | Acceso completo: gestión de usuarios, barberos, configuración |
| `barber` | Acceso limitado: solo turnos propios, clientes, servicios |

#### Ejemplo de Registro

```sql
INSERT INTO users (username, password_hash, role, barber_id, must_change_password)
VALUES (
    'admin',
    '$2b$10$abcdefghijklmnopqrstuvwxyz1234567890',  -- Hash bcrypt
    'admin',
    1,
    TRUE
);
```

---

### 3. `clients` - Clientes

Base de datos de clientes de la barbería.

#### Estructura

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Identificador único |
| `name` | VARCHAR(100) | NOT NULL | Nombre completo del cliente |
| `email` | VARCHAR(150) | NOT NULL | Email (debe ser válido y único) |
| `phone` | VARCHAR(20) | NULLABLE | Teléfono para WhatsApp (opcional) |
| `notes` | TEXT | NULLABLE | Notas personalizadas (preferencias, alergias, etc.) |
| `created_at` | DATETIME | NOT NULL, DEFAULT now() | Fecha de registro |

#### Relaciones

- **1:N** con `appointments` - Un cliente puede tener muchos turnos
- **CASCADE DELETE**: Al eliminar cliente, se eliminan sus turnos (configurado en ORM)

#### Índices

```sql
CREATE INDEX idx_client_name ON clients(name);
CREATE INDEX idx_client_phone ON clients(phone);
```

**Justificación**: La búsqueda por nombre y teléfono es muy frecuente en la UI.

#### Validaciones

- **Email**: Formato válido, único en la base de datos
- **Teléfono**: Formato válido si se proporciona (validado en servicio)
- **Nombre**: Mínimo 2 caracteres

#### Ejemplo de Registro

```sql
INSERT INTO clients (name, email, phone, notes, created_at)
VALUES (
    'Juan Pérez',
    'juan.perez@example.com',
    '+54 9 11 1234-5678',
    'Prefiere corte bajo, alérgico a ciertos productos',
    '2026-01-15 09:30:00'
);
```

---

### 4. `services` - Servicios Ofrecidos

Catálogo de servicios que ofrece la barbería.

#### Estructura

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Identificador único |
| `name` | VARCHAR(100) | UNIQUE, NOT NULL | Nombre del servicio |
| `duration` | INTEGER | NOT NULL | Duración en minutos (debe ser > 0) |
| `price` | FLOAT | DEFAULT 0.0 | Precio del servicio |
| `is_active` | BOOLEAN | DEFAULT TRUE | Servicio disponible/no disponible |

#### Relaciones

- **1:N** con `appointments` - Un servicio puede estar en muchos turnos

#### Validaciones

- **Nombre**: Único (no puede haber dos servicios con el mismo nombre)
- **Duración**: Mayor a 0
- **Precio**: Mayor o igual a 0

#### Servicios por Defecto

Al inicializar la BD, se crean automáticamente:

| Nombre | Duración | Precio |
|--------|----------|--------|
| Corte | 30 min | 0.0 |
| Barba | 15 min | 0.0 |
| Combo Corte+Barba | 40 min | 0.0 |

> 💡 El precio 0.0 permite no mostrar precios en UI si no se desea

#### Ejemplo de Registro

```sql
INSERT INTO services (name, duration, price, is_active)
VALUES ('Corte Premium', 45, 2500.0, TRUE);
```

---

### 5. `appointments` - Turnos Agendados

Tabla principal que vincula clientes con servicios, barberos y horarios.

#### Estructura

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Identificador único |
| `client_id` | INTEGER | FK → clients.id, NOT NULL | Cliente del turno |
| `service_id` | INTEGER | FK → services.id, NOT NULL | Servicio solicitado |
| `barber_id` | INTEGER | FK → barbers.id, NOT NULL | Barbero asignado |
| `start_time` | DATETIME | NOT NULL | Hora de inicio del turno |
| `end_time` | DATETIME | NOT NULL | Hora de fin del turno |
| `status` | VARCHAR(20) | DEFAULT 'pending', NOT NULL | Estado del turno |
| `google_event_id` | VARCHAR(255) | UNIQUE, NULLABLE | ID del evento en Google Calendar (futuro) |
| `created_at` | DATETIME | NOT NULL, DEFAULT now() | Fecha de creación del turno |

#### Relaciones

- **N:1** con `clients` - Muchos turnos pertenecen a un cliente
- **N:1** con `services` - Muchos turnos usan un servicio
- **N:1** con `barbers` - Muchos turnos son atendidos por un barbero

#### Estados Válidos (`status`)

| Estado | Descripción | Color UI |
|--------|-------------|----------|
| `pending` | Turno agendado, pendiente de confirmación | Amarillo |
| `confirmed` | Turno completado/confirmado | Verde |
| `cancelled` | Turno cancelado | Rojo |

#### Índices

```sql
CREATE INDEX idx_appointment_start_time ON appointments(start_time);
CREATE INDEX idx_appointment_barber_date ON appointments(barber_id, start_time);
CREATE INDEX idx_appointment_status ON appointments(status);
```

**Justificación**:
- **start_time**: Queries por fecha son constantes (agenda diaria/semanal)
- **barber_id + start_time**: Filtrado por barbero y fecha (muy frecuente)
- **status**: Reportes filtran por estado

#### Validaciones de Negocio

1. **No overlap**: Un barbero no puede tener dos turnos al mismo tiempo
   ```python
   # Algoritmo de detección de conflictos:
   existing.start_time < new.end_time AND
   existing.end_time > new.start_time
   ```

2. **Horario de negocio**: `start_time` debe estar dentro de horarios de atención

3. **Duración**: `end_time - start_time` debe coincidir con `service.duration`

#### Ejemplo de Registro

```sql
INSERT INTO appointments (client_id, service_id, barber_id, start_time, end_time, status, created_at)
VALUES (
    1,                              -- client_id
    2,                              -- service_id (Barba, 15 min)
    1,                              -- barber_id
    '2026-01-25 14:00:00',          -- start_time
    '2026-01-25 14:15:00',          -- end_time
    'pending',                      -- status
    '2026-01-20 10:30:00'           -- created_at
);
```

---

### 6. `settings` - Configuración del Sistema

Tabla key-value para configuración dinámica.

#### Estructura

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Identificador único |
| `key` | VARCHAR(50) | UNIQUE, NOT NULL | Clave de configuración |
| `value` | VARCHAR(255) | NOT NULL | Valor de configuración |

#### Claves Predefinidas

| Key | Default | Descripción |
|-----|---------|-------------|
| `business_hours_start` | `"12"` | Hora de apertura (0-23) |
| `business_hours_end` | `"20"` | Hora de cierre (0-23) |
| `slot_duration` | `"15"` | Duración de slots en minutos (futuro) |

#### Ventajas del Modelo Key-Value

- ✅ Configuración sin cambiar código
- ✅ Fácil añadir nuevas configuraciones
- ✅ Valores editables desde UI
- ✅ No requiere migraciones para nuevas configs

#### Acceso desde Código

```python
from services.settings_service import SettingsService

# Obtener horarios de negocio
start_hour, end_hour = SettingsService.get_business_hours(db)

# Establecer nuevo horario
SettingsService.set_business_hours(db, start_hour=9, end_hour=21)
```

#### Ejemplo de Registros

```sql
INSERT INTO settings (key, value) VALUES ('business_hours_start', '12');
INSERT INTO settings (key, value) VALUES ('business_hours_end', '20');
```

---

## Relaciones

### Diagrama Entidad-Relación

```mermaid
erDiagram
    BARBER ||--o| USER : "has optional login"
    BARBER ||--o{ APPOINTMENT : "performs many"
    CLIENT ||--o{ APPOINTMENT : "books many"
    SERVICE ||--o{ APPOINTMENT : "used in many"
    
    BARBER {
        int id PK
        string name
        string color
        boolean is_active
        datetime created_at
    }
    
    USER {
        int id PK
        string username UK
        string password_hash
        string role
        int barber_id FK
        boolean is_active
        int failed_attempts
        datetime locked_until
        boolean must_change_password
    }
    
    CLIENT {
        int id PK
        string name
        string email
        string phone
        text notes
        datetime created_at
    }
    
    SERVICE {
        int id PK
        string name UK
        int duration
        float price
        boolean is_active
    }
    
    APPOINTMENT {
        int id PK
        int client_id FK
        int service_id FK
        int barber_id FK
        datetime start_time
        datetime end_time
        string status
        string google_event_id UK
        datetime created_at
    }
    
    SETTINGS {
        int id PK
        string key UK
        string value
    }
```

### Tipos de Relaciones

#### 1. Barber → User (One-to-Optional-One)

```python
# ORM Definition
class Barber(Base):
    user: Mapped[Optional["User"]] = relationship("User", back_populates="barber", uselist=False)

class User(Base):
    barber: Mapped[Optional["Barber"]] = relationship("Barber", back_populates="user")
```

**Características**:
- Un barbero **puede** tener un usuario (no obligatorio)
- Un usuario **puede** pertenecer a un barbero (NULL si es admin puro)
- `uselist=False` en `Barber` indica relación 1:1

---

#### 2. Barber → Appointments (One-to-Many)

```python
class Barber(Base):
    appointments: Mapped[List["Appointment"]] = relationship("Appointment", back_populates="barber")

class Appointment(Base):
    barber: Mapped["Barber"] = relationship("Barber", back_populates="appointments")
```

**Características**:
- Un barbero tiene **muchos** turnos
- Un turno pertenece a **un solo** barbero

---

#### 3. Client → Appointments (One-to-Many con Cascade)

```python
class Client(Base):
    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment", 
        back_populates="client", 
        cascade="all, delete-orphan"
    )
```

**Características**:
- Un cliente tiene **muchos** turnos
- **CASCADE DELETE**: Al eliminar cliente, se eliminan sus turnos automáticamente
- `delete-orphan`: Si un appointment pierde su client, se elimina

---

#### 4. Service → Appointments (One-to-Many)

```python
class Service(Base):
    appointments: Mapped[List["Appointment"]] = relationship("Appointment", back_populates="service")
```

**Características**:
- Un servicio puede estar en **muchos** turnos
- No hay cascade delete (preservar historial de turnos)

---

## Índices y Optimización

### Índices Implementados

#### 1. Búsqueda de Clientes

```python
# En models/base.py - Client
__table_args__ = (
    Index('idx_client_name', 'name'),
    Index('idx_client_phone', 'phone'),
)
```

**Query optimizada**:
```sql
-- Sin índice: Full table scan
-- Con índice: Index scan
SELECT * FROM clients WHERE name LIKE 'Juan%';  -- Usa idx_client_name
SELECT * FROM clients WHERE phone = '+54123';  -- Usa idx_client_phone
```

---

#### 2. Agenda de Turnos

```python
# En models/base.py - Appointment
__table_args__ = (
    Index('idx_appointment_start_time', 'start_time'),
    Index('idx_appointment_barber_date', 'barber_id', 'start_time'),
    Index('idx_appointment_status', 'status'),
)
```

**Queries optimizadas**:
```sql
-- Turnos de una fecha (vista agenda)
SELECT * FROM appointments 
WHERE start_time BETWEEN '2026-01-25 00:00:00' AND '2026-01-25 23:59:59';
-- Usa: idx_appointment_start_time

-- Turnos de un barbero en una fecha (filtro por barbero)
SELECT * FROM appointments 
WHERE barber_id = 1 AND start_time >= '2026-01-25 00:00:00';
-- Usa: idx_appointment_barber_date (composite index)

-- Reportes por estado
SELECT COUNT(*) FROM appointments WHERE status = 'confirmed';
-- Usa: idx_appointment_status
```

---

### Análisis de Performance

| Query | Sin Índice | Con Índice | Mejora |
|-------|------------|------------|--------|
| Búsqueda cliente por nombre | O(n) scan | O(log n) | 10-100x |
| Turnos de fecha | O(n) scan | O(log n) | 10-50x |
| Turnos de barbero + fecha | O(n) scan | O(log n) | 20-100x |

---

## Constraints

### Constraints de Integridad

#### Primary Keys

Todas las tablas tienen PK autoincremental:
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
```

---

#### Foreign Keys

```sql
-- users.barber_id → barbers.id
FOREIGN KEY (barber_id) REFERENCES barbers(id)

-- appointments.client_id → clients.id
FOREIGN KEY (client_id) REFERENCES clients(id)

-- appointments.service_id → services.id  
FOREIGN KEY (service_id) REFERENCES services(id)

-- appointments.barber_id → barbers.id
FOREIGN KEY (barber_id) REFERENCES barbers(id)
```

**Validación**: SQLite valida que los IDs referenciados existan.

---

#### Unique Constraints

```sql
-- users.username debe ser único
username VARCHAR(50) UNIQUE NOT NULL

-- services.name debe ser único
name VARCHAR(100) UNIQUE NOT NULL

-- settings.key debe ser único
key VARCHAR(50) UNIQUE NOT NULL

-- appointments.google_event_id debe ser único (si no es NULL)
google_event_id VARCHAR(255) UNIQUE NULLABLE
```

---

#### NOT NULL Constraints

Campos obligatorios en todas las tablas:
```sql
-- Ejemplos
barbers.name VARCHAR(100) NOT NULL
users.username VARCHAR(50) NOT NULL
clients.email VARCHAR(150) NOT NULL
appointments.start_time DATETIME NOT NULL
```

---

#### Default Values

```sql
-- Defaults comunes
is_active BOOLEAN DEFAULT TRUE
status VARCHAR(20) DEFAULT 'pending'
created_at DATETIME DEFAULT (datetime('now'))
price FLOAT DEFAULT 0.0
failed_attempts INTEGER DEFAULT 0
must_change_password BOOLEAN DEFAULT TRUE
```

---

## Migraciones con Alembic

Alembic gestiona el versionado del esquema de base de datos.

### Configuración

Archivo: `alembic.ini`

```ini
[alembic]
script_location = alembic
sqlalchemy.url = sqlite:///barber_manager.db
```

---

### Historial de Migraciones

| Versión | Fecha | Descripción |
|---------|-------|-------------|
| `42b5c52f6d7d` | 2026-01-10 | Initial migration - Creación de todas las tablas |
| `137560ca3196` | 2026-01-12 | Add must_change_password field to User |
| `8eae66de00f0` | 2026-01-13 | Add rate limiting fields (failed_attempts, locked_until) |
| `93df974c4a69` | 2026-01-14 | Add indexes for performance optimization |

---

### Comandos

#### Ver Estado Actual

```bash
alembic current
# Output: 93df974c4a69 (head), add indexes for performance
```

#### Ver Historial

```bash
alembic history --verbose
```

#### Crear Nueva Migración

```bash
# Automática (detecta cambios en models/)
alembic revision --autogenerate -m "add new field"

# Manual
alembic revision -m "add custom index"
```

#### Aplicar Migraciones

```bash
# Aplicar todas pendientes
alembic upgrade head

# Aplicar una específica
alembic upgrade 42b5c52f6d7d

# Rollback
alembic downgrade -1  # Retroceder 1
alembic downgrade base  # Volver al inicio
```

---

### Ejemplo de Migración

**Archivo**: `alembic/versions/137560ca3196_add_must_change_password_field.py`

```python
def upgrade():
    op.add_column('users', sa.Column('must_change_password', sa.Boolean(), nullable=False, server_default='1'))

def downgrade():
    op.drop_column('users', 'must_change_password')
```

---

## Data Seeding

La función `init_db()` en `database.py` puebla datos iniciales.

### Servicios por Defecto

```python
def _seed_services():
    default_services = [
        Service(name="Corte", duration=30, price=0.0, is_active=True),
        Service(name="Barba", duration=15, price=0.0, is_active=True),
        Service(name="Combo Corte+Barba", duration=40, price=0.0, is_active=True),
    ]
    for service in default_services:
        db.add(service)
```

---

### Usuario Admin y Barbero Principal

```python
def _seed_auth():
    # Requiere ADMIN_PASSWORD en .env
    admin_password = os.getenv("ADMIN_PASSWORD")
    
    # Crear barbero por defecto
    default_barber = Barber(id=1, name="Barbero Principal", color="#7E57C2")
    db.add(default_barber)
    
    # Crear usuario admin
    AuthService.create_user(
        db, 
        username="admin", 
        password=admin_password, 
        role="admin",
        barber_id=1
    )
```

---

## Queries Comunes

### 1. Obtener Turnos de un Día

```python
# SQLAlchemy
from datetime import date, datetime, timedelta

target_date = date(2026, 1, 25)
start = datetime.combine(target_date, datetime.min.time())
end = start + timedelta(days=1)

appointments = db.query(Appointment).filter(
    Appointment.start_time >= start,
    Appointment.start_time < end
).all()
```

```sql
-- SQL directo
SELECT * FROM appointments 
WHERE start_time >= '2026-01-25 00:00:00' 
  AND start_time < '2026-01-26 00:00:00'
ORDER BY start_time;
```

---

### 2. Detectar Conflictos de Horario

```python
# Buscar turnos del barbero que se solapan
conflicting = db.query(Appointment).filter(
    Appointment.barber_id == barber_id,
    Appointment.start_time < proposed_end_time,
    Appointment.end_time > proposed_start_time,
    Appointment.status != 'cancelled'
).all()
```

```sql
-- SQL directo
SELECT * FROM appointments
WHERE barber_id = 1
  AND start_time < '2026-01-25 15:00:00'  -- Fin propuesto
  AND end_time > '2026-01-25 14:30:00'    -- Inicio propuesto
  AND status != 'cancelled';
```

---

### 3. Buscar Clientes

```python
# Por nombre (case-insensitive)
clients = db.query(Client).filter(
    Client.name.ilike(f'%{search_term}%')
).limit(10).all()

# Por teléfono exacto
client = db.query(Client).filter(
    Client.phone == phone_number
).first()
```

```sql
-- SQL directo
SELECT * FROM clients 
WHERE name LIKE '%Juan%' 
ORDER BY name 
LIMIT 10;

-- Usa índice idx_client_name
```

---

### 4. Estadísticas de Barbero

```python
# Turnos completados del mes
from sqlalchemy import func

month_start = datetime(2026, 1, 1)
month_end = datetime(2026, 2, 1)

stats = db.query(
    func.count(Appointment.id).label('total'),
    func.sum(case([(Appointment.status == 'confirmed', 1)], else_=0)).label('completed'),
    func.sum(case([(Appointment.status == 'cancelled', 1)], else_=0)).label('cancelled')
).filter(
    Appointment.barber_id == barber_id,
    Appointment.start_time >= month_start,
    Appointment.start_time < month_end
).first()
```

```sql
-- SQL directo
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled
FROM appointments
WHERE barber_id = 1
  AND start_time >= '2026-01-01 00:00:00'
  AND start_time < '2026-02-01 00:00:00';
```

---

### 5. Clientes con Más Turnos

```python
# Top 10 clientes
top_clients = db.query(
    Client,
    func.count(Appointment.id).label('appointment_count')
).join(Appointment).group_by(Client.id).order_by(
    desc('appointment_count')
).limit(10).all()
```

```sql
-- SQL directo
SELECT 
    c.id, c.name, c.email,
    COUNT(a.id) as appointment_count
FROM clients c
JOIN appointments a ON c.id = a.client_id
GROUP BY c.id
ORDER BY appointment_count DESC
LIMIT 10;
```

---

## Consideraciones de Performance

### Para SQLite

#### ✅ Buenas Prácticas

1. **Usar transacciones**: Agruparcambios en una transacción
   ```python
   with get_db() as db:
       # Todas las operaciones en una transacción
       db.add(appointment1)
       db.add(appointment2)
       # Commit automático al salir del context
   ```

2. **Índices apropiados**: Ya implementados para queries frecuentes

3. **VACUUM periódico**: Optimiza el archivo DB
   ```bash
   sqlite3 barber_manager.db "VACUUM;"
   ```

4. **ANALYZE**: Actualiza estadísticas para el query planner
   ```bash
   sqlite3 barber_manager.db "ANALYZE;"
   ```

#### ❌ Limitaciones de SQLite

- **Escrituras concurrentes**: Solo una a la vez
- **Locks**: Base de datos completa (no por tabla)
- **Escala**: No recomendado para >100k filas con alta concurrencia

#### 🔄 Migración a PostgreSQL

Para entornos de producción multi-usuario, migrar a PostgreSQL:

```python
# Cambiar DATABASE_URL en .env
DATABASE_URL=postgresql://user:pass@localhost/barber_db

# SQLAlchemy maneja el resto automáticamente
# (los modelos ORM no cambian)
```

---

## Backup y Recuperación

### Backup de SQLite

```bash
# Backup simple (copiar archivo)
cp barber_manager.db barber_manager_backup_$(date +%Y%m%d).db

# Backup con VACUUM (optimizado)
sqlite3 barber_manager.db ".backup barber_backup.db"
```

### Restauración

```bash
# Restaurar desde backup
cp barber_backup.db barber_manager.db
```

### Backup Automático (Script)

```bash
#!/bin/bash
# backup_db.sh
BACKUP_DIR="./backups"
DB_FILE="barber_manager.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
sqlite3 $DB_FILE ".backup $BACKUP_DIR/barber_$TIMESTAMP.db"
echo "Backup created: $BACKUP_DIR/barber_$TIMESTAMP.db"
```

---

## Conclusión

El esquema de base de datos de Barber Manager Pro está diseñado para:

- ✅ **Normalización**: Evitar redundancia y mantener integridad
- ✅ **Performance**: Índices estratégicos para queries frecuentes
- ✅ **Escalabilidad**: Preparado para migrar a PostgreSQL
- ✅ **Mantenibilidad**: Migraciones versionadas con Alembic
- ✅ **Flexibilidad**: Configuración key-value para parámetros dinámicos

La estructura actual soporta perfectamente las necesidades de una barbería individual o pequeña cadena, con camino claro de migración para escalar.

---

**📚 Documentación Relacionada**:
- [Arquitectura](arquitectura.md) - Arquitectura del sistema
- [API Interna](api_interna.md) - Servicios y repositorios
- [Guía de Desarrollo](guia_desarrollo.md) - Añadir nuevas tablas/migraciones
