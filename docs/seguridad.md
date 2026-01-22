# Documentación de Seguridad - Barber Manager Pro

Guía completa de los aspectos de seguridad implementados en el sistema de gestión de turnos.

---

## Tabla de Contenidos

- [Autenticación](#autenticación)
- [Rate Limiting](#rate-limiting)
- [Gestión de Contraseñas](#gestión-de-contraseñas)
- [Gestión de Sesiones](#gestión-de-sesiones)
- [Validación de Inputs](#validación-de-inputs)
- [Seguridad de Base de Datos](#seguridad-de-base-de-datos)
- [Variables de Entorno](#variables-de-entorno)
- [Mejores Prácticas](#mejores-prácticas)
- [Consideraciones de Deployment](#consideraciones-de-deployment)

---

## Autenticación

### Hash de Contraseñas con bcrypt

El sistema utiliza **bcrypt** para el almacenamiento seguro de contraseñas.

#### Características

- **Algoritmo**: bcrypt (industry standard)
- **Rounds**: 10 (default, ~100ms por hash)
- **Salt**: Generado automáticamente y embebido en hash
- **Output**: 60 caracteres en formato `$2b$10$...`

#### Implementación

```python
# services/auth_service.py
import bcrypt

def hash_password(password: str) -> str:
    """Genera hash bcrypt de contraseña."""
    salt = bcrypt.gensalt()  # Genera salt aleatorio
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verifica contraseña contra hash."""
    return bcrypt.checkpw(
        password.encode('utf-8'),
        hashed.encode('utf-8')
    )
```

#### ¿Por qué bcrypt?

| Característica | bcrypt | SHA-256 | MD5 |
|----------------|--------|---------|-----|
| **Diseñado para passwords** | ✅ Sí | ❌ No | ❌ No |
| **Salt automático** | ✅ Sí | ❌ Manual | ❌ Manual |
| **Costoso computacionalmente** | ✅ Sí (previene brute force) | ❌ Muy rápido | ❌ Muy rápido |
| **Configurable** | ✅ Rounds ajustables | ❌ Fixed | ❌ Fixed |
| **Resistente a rainbow tables** | ✅ Sí | ⚠️ Con salt | ⚠️ Con salt |
| **Recomendado por OWASP** | ✅ Sí | ❌ No para passwords | ❌ NUNCA |

#### Ejemplo de Hash

```python
password = "MiPassword123!"
hashed = hash_password(password)
print(hashed)
# $2b$10$abcdefghijklmnopqrstuvwxyz123456789...

# Breakdown:
# $2b$      - Versión de bcrypt
# 10$       - Cost factor (2^10 rounds = 1024)
# abc...xyz - Salt (22 caracteres)
# 123...    - Hash de password+salt (31 caracteres)
```

---

## Rate Limiting

Protección contra ataques de fuerza bruta en el login.

### Configuración

```python
# services/auth_service.py
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 5
```

### Algoritmo

```mermaid
graph TD
    A[Intento de login] --> B{Usuario existe?}
    B -->|No| C[Retornar 'Credenciales inválidas']
    B -->|Sí| D{locked_until > now?}
    D -->|Sí| E[Retornar 'Cuenta bloqueada. X minutos']
    D -->|No| F{Password correcto?}
    F -->|Sí| G[failed_attempts = 0]
    G --> H[locked_until = NULL]
    H --> I[Retornar user]
    F -->|No| J[failed_attempts += 1]
    J --> K{failed_attempts >= 5?}
    K -->|Sí| L[locked_until = now + 5 min]
    K -->|No| M[Retornar 'Credenciales inválidas. X intentos']
    L --> M
```

### Campos en Base de Datos

```sql
-- users table
failed_attempts INTEGER DEFAULT 0
locked_until DATETIME NULL
```

**`failed_attempts`**:
- Incrementa en cada login fallido
- Resetea a 0 en login exitoso

**`locked_until`**:
- `NULL` si no está bloqueado
- `datetime` futuro si está bloqueado
- Se verifica con `locked_until > datetime.now()`

### Implementación

```python
@classmethod
def authenticate(cls, db: Session, username: str, password: str):
    """Autentica con rate limiting."""
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        return None, "Credenciales inválidas"
    
    # Verificar bloqueo
    if user.locked_until and user.locked_until > datetime.now():
        remaining = (user.locked_until - datetime.now()).seconds // 60 + 1
        return None, f"Cuenta bloqueada. Intente en {remaining} minutos"
    
    # Verificar password
    if verify_password(password, user.password_hash):
        # Éxito - resetear intentos
        user.failed_attempts = 0
        user.locked_until = None
        db.flush()
        return user, None
    else:
        # Falla - incrementar
        user.failed_attempts += 1
        if user.failed_attempts >= MAX_FAILED_ATTEMPTS:
            user.locked_until = datetime.now() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        db.flush()
        
        attempts_left = MAX_FAILED_ATTEMPTS - user.failed_attempts
        if attempts_left > 0:
            return None, f"Credenciales inválidas. {attempts_left} intentos restantes"
        else:
            return None, f"Cuenta bloqueada por {LOCKOUT_DURATION_MINUTES} minutos"
```

### Desbloqueo Manual

Administradores pueden desbloquear usuarios:

```python
@classmethod
def unlock_user(cls, db: Session, username: str) -> bool:
    """Desbloquea usuario manualmente (para admins)."""
    user = db.query(User).filter(User.username == username).first()
    if user:
        user.failed_attempts = 0
        user.locked_until = None
        db.flush()
        return True
    return False
```

**Uso**:
```python
from services.auth_service import AuthService

with get_db() as db:
    AuthService.unlock_user(db, "usuario_bloqueado")
```

---

## Gestión de Contraseñas

### Cambio Obligatorio en Primer Login

Todos los usuarios nuevos deben cambiar su contraseña en el primer login.

#### Campo `must_change_password`

```sql
-- users table
must_change_password BOOLEAN DEFAULT TRUE
```

- Se establece a `TRUE` al crear usuario
- Se verifica después de login exitoso
- Se establece a `FALSE` tras cambiar contraseña

#### Flujo en UI

```mermaid
sequenceDiagram
    participant U as Usuario
    participant L as login_view
    participant A as AuthService
    participant C as change_password_view
    participant M as main.py

    U->>L: Ingresar credenciales
    L->>A: authenticate(username, password)
    A-->>L: (user, None)
    
    alt must_change_password == TRUE
        L->>C: Redirigir a cambio de contraseña
        U->>C: Ingresar nueva contraseña
        C->>A: change_password(user_id, new_password)
        A->>A: must_change_password = FALSE
        A-->>C: (True, None)
        C->>M: Redirigir a agenda
    else must_change_password == FALSE
        L->>M: Redirigir a agenda
    end
```

#### Implementación

```python
# En login_view.py
def on_login_success(user_data):
    if user_data.get("must_change_password", False):
        # Forzar cambio de contraseña
        content_area.content = create_change_password_view(
            page, user_data, on_password_changed
        )
    else:
        # Ir a aplicación normalmente
        content_area.content = create_agenda_view(page)

# En auth_service.py
def change_password(cls, db, user_id, new_password):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False, "Usuario no encontrado"
    
    if len(new_password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres"
    
    user.password_hash = cls.hash_password(new_password)
    user.must_change_password = False  # Marcar como cambiada
    db.flush()
    
    return True, None
```

### Política de Contraseñas

#### Requisitos Actuales

- **Longitud mínima**: 6 caracteres
- **Sin requisitos de complejidad** (por simplicidad)

#### Mejora Recomendada (Futuro)

```python
import re

def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
    """Valida fortaleza de contraseña."""
    if len(password) < 8:
        return False, "Mínimo 8 caracteres"
    
    if not re.search(r'[A-Z]', password):
        return False, "Debe contener al menos una mayúscula"
    
    if not re.search(r'[a-z]', password):
        return False, "Debe contener al menos una minúscula"
    
    if not re.search(r'\d', password):
        return False, "Debe contener al menos un número"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Debe contener al menos un carácter especial"
    
    return True, None
```

---

## Gestión de Sesiones

### Almacenamiento de Sesión

El estado de sesión se almacena en `page.data` (diccionario en memoria).

```python
# Estructura de sesión
page.data = {
    "user_id": int,
    "is_logged_in": bool,
    "barber_id": Optional[int],
    "username": str,
    "role": str  # "admin" o "barber"
}
```

### Verificación de Autenticación

En cada cambio de ruta, se verifica sesión:

```python
# En main.py - route_change()
async def route_change(e: ft.RouteChangeEvent):
    route = page.route
    
    # Verificar autenticación
    is_logged_in = False
    if hasattr(page, 'data') and page.data is not None:
        is_logged_in = page.data.get("is_logged_in", False)
    
    if not is_logged_in:
        # Redirigir a login
        content_area.content = create_login_view(page, on_login_success)
        return
    
    # Usuario autenticado - cargar vista solicitada
    if route == "/":
        content_area.content = create_agenda_view(page)
    # ...
```

### Cierre de Sesión

```python
def on_logout():
    """Callback de logout."""
    # Limpiar datos de sesión
    if hasattr(page, 'data') and page.data is not None:
        page.data.clear()
    
    # Ocultar sidebar
    sidebar_container.visible = False
    
    # Redirigir a login
    content_area.content = create_login_view(page, on_login_success)
    page.update()
```

### Timeout de Sesión (Por Implementar)

Actualmente la sesión persiste mientras la aplicación esté abierta.

**Mejora recomendada**:

```python
import time

# Agregar timestamp a sesión
page.data["last_activity"] = time.time()

# En route_change, verificar timeout
TIMEOUT_SECONDS = 30 * 60  # 30 minutos

if page.data.get("last_activity"):
    if time.time() - page.data["last_activity"] > TIMEOUT_SECONDS:
        # Timeout - forzar logout
        on_logout()
        return

# Actualizar timestamp en cada actividad
page.data["last_activity"] = time.time()
```

---

## Validación de Inputs

### Validadores Implementados

Archivo: `utils/validators.py`

#### `validate_email(email: str)`

```python
import re

def validate_email(email: Optional[str]) -> Tuple[bool, Optional[str]]:
    """Valida formato de email."""
    if not email or not email.strip():
        return False, "Email requerido"
    
    # Regex básico pero robusto
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(pattern, email):
        return False, "Formato de email inválido"
    
    return True, None
```

**Previene**:
- SQL injection (aunque ORM ya protege)
- XSS si email se muestra en UI

---

#### `validate_phone(phone: Optional[str])`

```python
def validate_phone(phone: Optional[str]) -> Tuple[bool, Optional[str]]:
    """Valida formato de teléfono."""
    if not phone or not phone.strip():
        return True, None  # Teléfono es opcional
    
    # Permitir dígitos, espacios, +, -, (, )
    pattern = r'^[\d\s\+\-\(\)]+$'
    if not re.match(pattern, phone):
        return False, "Formato de teléfono inválido"
    
    # Mínimo 7 dígitos
    digits = re.sub(r'\D', '', phone)
    if len(digits) < 7:
        return False, "Teléfono debe tener al menos 7 dígitos"
    
    return True, None
```

---

#### `validate_name(name: str)`

```python
def validate_name(name: str) -> Tuple[bool, Optional[str]]:
    """Valida nombre de persona."""
    if not name or not name.strip():
        return False, "Nombre requerido"
    
    if len(name.strip()) < 2:
        return False, "Nombre debe tener al menos 2 caracteres"
    
    # Solo letras, espacios, acentos, guiones
    pattern = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-]+$'
    if not re.match(pattern, name):
        return False, "Nombre contiene caracteres inválidos"
    
    return True, None
```

**Previene**:
- Inyección de scripts
- Caracteres especiales que rompen UI

---

#### `sanitize_string(text: str)`

```python
def sanitize_string(text: str) -> str:
    """Sanitiza string removiendo caracteres peligrosos."""
    if not text:
        return ""
    
    # Remover caracteres SQL peligrosos
    dangerous = ['%', '_', '\\', ';', '--', '/*', '*/']
    sanitized = text
    for char in dangerous:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()
```

---

### Doble Validación

**UI Validation** (UX):
```python
# En vista
if not email_field.value:
    show_error("Email requerido")
    return
```

**Service Validation** (Seguridad):
```python
# En servicio
is_valid, error = validate_email(email)
if not is_valid:
    return None, error
```

**Razón**: UI puede ser bypasseada (tests, API futura), servicio SIEMPRE valida.

---

## Seguridad de Base de Datos

### Protección contra SQL Injection

**SQLAlchemy ORM** previene SQL injection automáticamente:

```python
# ✅ Seguro: SQLAlchemy parametriza queries
client = db.query(Client).filter(Client.email == user_input).first()

# SQL generado:
# SELECT * FROM clients WHERE email = ?
# Parámetros: ['user_input_value']

# ❌ Inseguro (NO hacer):
# db.execute(f"SELECT * FROM clients WHERE email = '{user_input}'")
```

### Constraints de Base de Datos

#### Unique Constraints

```python
# Previenen duplicados a nivel de BD
username: Mapped[str] = mapped_column(String(50), unique=True)
email: Mapped[str] = mapped_column(String(150), unique=True)
```

#### Foreign Keys

```python
# Previenen referencias inválidas
client_id: Mapped[int] = mapped_column(Integer, ForeignKey("clients.id"))
```

#### NOT NULL

```python
# Previenen datos faltantes
name: Mapped[str] = mapped_column(String(100), nullable=False)
```

### Permisos de Base de Datos

Para SQLite, el archivo `.db` tiene permisos del filesystem.

**Recomendación para deployment**:
```bash
# Linux/Mac: Solo owner puede leer/escribir
chmod 600 barber_manager.db
```

---

## Variables de Entorno

### Archivo `.env`

**NUNCA** commitear `.env` al repositorio (está en `.gitignore`).

```env
# .env (NO commitear)
ADMIN_PASSWORD=ContraseñaSegura123!
DATABASE_URL=sqlite:///barber_manager.db
DEBUG=false
```

### Archivo `.env.example`

Commitear plantilla SIN valores reales:

```env
# .env.example (SÍ commitear)
ADMIN_PASSWORD=CHANGE_THIS_TO_SECURE_PASSWORD
DATABASE_URL=sqlite:///barber_manager.db
DEBUG=false
ECHO_SQL=false
```

### Validación de Variables Críticas

```python
# database.py
import os
from dotenv import load_dotenv

load_dotenv()

admin_password = os.getenv("ADMIN_PASSWORD")
if not admin_password:
    raise ValueError(
        "ADMIN_PASSWORD no está configurada en .env\n"
        "Por seguridad, debes establecer una contraseña segura.\n"
        "Copia .env.example a .env y configura ADMIN_PASSWORD."
    )
```

**La aplicación NO arranca** si falta `ADMIN_PASSWORD`.

---

## Mejores Prácticas

### 1. Principio de Menor Privilegio

Usuarios solo tienen permisos necesarios para su rol:

| Acción | Admin | Barber |
|--------|-------|--------|
| Ver turnos propios | ✅ | ✅ |
| Ver turnos de otros | ✅ | ❌ |
| Crear barberos | ✅ | ❌ |
| Desactivar barberos | ✅ | ❌ |
| Configurar horarios | ✅ | ❌ |
| Desbloquear usuarios | ✅ | ❌ |

**Implementar en futuras versiones**:
```python
def require_admin(func):
    """Decorator para requerir rol admin."""
    def wrapper(page, *args, **kwargs):
        if page.data.get("role") != "admin":
            page.snack_bar = SnackBar(
                content=Text("Acceso denegado"),
                bgcolor=Colors.RED_700
            )
            return
        return func(page, *args, **kwargs)
    return wrapper

@require_admin
def create_barbers_view(page):
    ...
```

### 2. Logging de Eventos de Seguridad

```python
from config import logger

# Login exitoso
logger.info(f"Login exitoso: {username}")

# Login fallido
logger.warning(f"Intento de login fallido: {username}")

# Usuario bloqueado
logger.warning(f"Usuario {username} bloqueado por {LOCKOUT_DURATION_MINUTES} minutos")

# Desbloqueo manual
logger.info(f"Usuario {username} desbloqueado manualmente por admin")
```

### 3. Actualización de Dependencias

Mantener librerías actualizadas:

```bash
# Ver dependencias desactualizadas
pip list --outdated

# Actualizar
pip install --upgrade package_name

# Actualizar requirements.txt
pip freeze > requirements.txt
```

**Dependencias críticas**:
- `bcrypt`: Vulnerabilidades de seguridad
- `sqlalchemy`: SQL injection protections
- `cryptography`: Algoritmos criptográficos

---

## Consideraciones de Deployment

### 1. No Usar SQLite en Producción Multi-Usuario

SQLite es excelente para desarrollo y single-user, pero NO para múltiples usuarios concurrentes.

**Migrar a PostgreSQL**:

```python
# .env
DATABASE_URL=postgresql://user:pass@localhost:5432/barber_db

# Sin cambios en código (SQLAlchemy abstrae todo)
```

---

### 2. HTTPS Obligatorio

Si se expone remotamente (web), usar HTTPS.

**Flet soporta deployment web**:
```bash
flet build web
# Deployar con Nginx + SSL certificate
```

---

### 3. Backup y Recuperación

```bash
#!/bin/bash
# backup_schedule.sh
BACKUP_DIR="/backups"
DB_FILE="/app/barber_manager.db"

# Backup diario
cp $DB_FILE "$BACKUP_DIR/barber_$(date +%Y%m%d).db"

# Mantener solo últimos 30 días
find $BACKUP_DIR -name "barber_*.db" -mtime +30 -delete
```

Automatizar con cron:
```bash
# Diario a las 2 AM
0 2 * * * /path/to/backup_schedule.sh
```

---

### 4. Monitoreo de Intentos de Ataque

Implementar alertas para:
- Múltiples usuarios bloqueados en corto tiempo
- Patrones de ataque (mismo IP, múltiples usernames)

```python
# Futuro: log a sistema de monitoreo
logger.warning(
    f"ALERTA: {failed_count} usuarios bloqueados en última hora",
    extra={"alert": "security", "severity": "high"}
)
```

---

### 5. Política de Retención de Datos

Definir cuánto tiempo mantener:
- Turnos completados: ¿1 año? ¿Indefinido?
- Usuarios inactivos: ¿Desactivar tras 6 meses?
- Logs: ¿30 días?

```python
# Ejemplo: Archivar turnos antiguos
from datetime import datetime, timedelta

def archive_old_appointments(db):
    """Archiva turnos de más de 1 año."""
    cutoff = datetime.now() - timedelta(days=365)
    
    old_appointments = db.query(Appointment).filter(
        Appointment.start_time < cutoff
    ).all()
    
    # Mover a tabla de archivo o exportar a CSV
    ...
```

---

## Conclusión

La seguridad es un proceso continuo. Este sistema implementa:

- ✅ **Autenticación robusta** con bcrypt
- ✅ **Rate limiting** contra brute force
- ✅ **Validación exhaustiva** de inputs
- ✅ **Gestión segura** de sesiones
- ✅ **Protección SQL injection** con ORM
- ✅ **Cambio obligatorio** de contraseña

**Próximos pasos recomendados**:
- Implementar 2FA (Two-Factor Authentication)
- Auditoría de seguridad profesional
- Penetration testing
- Política de contraseñas más estricta
- Monitoreo de seguridad en tiempo real

La seguridad nunca está "completa", siempre hay margen de mejora.

---

**📚 Documentación Relacionada**:
- [API Interna](api_interna.md) - AuthService y validadores
- [Base de Datos](base_de_datos.md) - Constraints y seguridad de datos
- [Guía de Desarrollo](guia_desarrollo.md) - Mejores prácticas
