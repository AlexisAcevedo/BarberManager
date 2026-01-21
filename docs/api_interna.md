# API Interna - Servicios

Documentación de los métodos principales de la capa de servicios.

## AppointmentService

Gestión de turnos y disponibilidad.

### Métodos

#### `get_appointments_for_date(db, target_date, barber_id=None)`
Obtiene todos los turnos para una fecha específica.

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `db` | Session | Sesión de base de datos |
| `target_date` | date | Fecha a consultar |
| `barber_id` | int (opcional) | Filtrar por barbero |

**Retorna:** `List[Appointment]`

---

#### `get_available_slots(db, target_date, service_duration, barber_id)`
Obtiene slots disponibles para agendar.

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `db` | Session | Sesión de base de datos |
| `target_date` | date | Fecha objetivo |
| `service_duration` | int | Duración del servicio (min) |
| `barber_id` | int | ID del barbero |

**Retorna:** `List[Tuple[hour, minute, is_available]]`

---

#### `create_appointment(db, client_id, service_id, barber_id, start_time)`
Crea un nuevo turno verificando disponibilidad.

**Retorna:** `Tuple[Optional[Appointment], Optional[str]]`

---

#### `update_appointment_status(db, appointment_id, new_status)`
Actualiza el estado de un turno.

| Estados válidos |
|-----------------|
| `pending` |
| `confirmed` |
| `cancelled` |

**Retorna:** `Tuple[Optional[Appointment], Optional[str]]`

---

## ClientService

CRUD de clientes.

### Métodos

#### `get_all_clients(db)`
Retorna todos los clientes ordenados por nombre.

---

#### `search_clients(db, search_term)`
Busca clientes por nombre o teléfono.

**Retorna:** `List[Client]` (máximo 10 resultados)

---

#### `create_client(db, name, email, phone=None, notes=None)`
Crea un nuevo cliente con validación.

**Validaciones:**
- Email único y formato válido
- Nombre mínimo 2 caracteres
- Teléfono formato válido (opcional)

**Retorna:** `Tuple[Optional[Client], Optional[str]]`

---

#### `update_client(db, client_id, **kwargs)`
Actualiza campos de un cliente existente.

---

#### `delete_client(db, client_id)`
Elimina un cliente (solo si no tiene turnos asociados).

**Retorna:** `Tuple[bool, Optional[str]]`

---

## ServiceService

Gestión de servicios de barbería.

### Métodos

#### `get_all_services(db, active_only=True)`
Retorna servicios, opcionalmente solo activos.

---

#### `create_service(db, name, duration, price=0.0)`
Crea un nuevo servicio.

**Validaciones:**
- Nombre único
- Duración > 0
- Precio >= 0

---

#### `update_service(db, service_id, **kwargs)`
Actualiza un servicio existente.

---

## AuthService

Autenticación, gestión de usuarios y seguridad.

### Rate Limiting
- **Máximo intentos fallidos:** 5
- **Duración del bloqueo:** 5 minutos

### Métodos

#### `hash_password(password) -> str`
Genera hash bcrypt de una contraseña.

---

#### `verify_password(password, hashed) -> bool`
Verifica contraseña contra hash.

---

#### `authenticate(db, username, password) -> Tuple[Optional[User], Optional[str]]`
Autentica usuario con protección de rate limiting.

**Retorna:**
- `(User, None)` si éxito
- `(None, "mensaje de error")` si falla

---

#### `create_user(db, username, password, role, barber_id=None)`
Crea nuevo usuario con contraseña hasheada.

---

#### `change_password(db, user_id, new_password) -> Tuple[bool, Optional[str]]`
Cambia la contraseña de un usuario y marca `must_change_password=False`.

---

#### `unlock_user(db, username) -> bool`
Desbloquea manualmente un usuario (para admins).

---

## NotificationService

Envío de notificaciones.

### Métodos

#### `send_whatsapp_reminder(appointment) -> str`
Genera URL de WhatsApp para enviar recordatorio manual.

**Formato del mensaje:**
```
Hola {nombre}! Te recordamos tu turno en Barbería Pro 
para el día {fecha} a las {hora} ({servicio}). ¡Te esperamos!
```

---

## SettingsService

Configuración de la aplicación.

### Métodos

#### `get_setting(db, key) -> Optional[str]`
Obtiene valor de configuración.

---

#### `set_setting(db, key, value)`
Establece valor de configuración.

---

#### `get_business_hours(db) -> Tuple[int, int]`
Retorna horario de atención (hora_inicio, hora_fin).

---

#### `set_business_hours(db, start_hour, end_hour)`
Establece horario de atención.

---

## BarberService

Gestión de barberos.

### Métodos

#### `get_all_barbers(db) -> List[Barber]`
Retorna todos los barberos activos.

---

#### `get_barber_by_id(db, barber_id) -> Optional[Barber]`
Obtiene barbero por ID.

---

#### `create_barber(db, name, color="#2196F3") -> Barber`
Crea nuevo barbero.
