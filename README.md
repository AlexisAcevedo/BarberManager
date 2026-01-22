# 🪒 Barber Manager Pro

> Sistema profesional de gestión de turnos para barberías

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flet](https://img.shields.io/badge/Flet-0.80+-00ADD8?style=for-the-badge)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red?style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Barber Manager Pro** es una aplicación de escritorio moderna y completa para la gestión integral de barberías. Construida con **Flet** para una interfaz de usuario elegante y **SQLAlchemy** para un robusto manejo de datos, ofrece todas las herramientas necesarias para administrar turnos, clientes, personal y reportes.

---

## ✨ Características Principales

### 📅 Gestión de Agenda
- **Vista semanal interactiva** con calendario visual
- **Creación rápida de turnos** con detección automática de conflictos
- **Filtrado por barbero** para visualización personalizada
- **Estados de turnos**: pendiente, confirmado, cancelado
- **Slots de 15 minutos** configurables según duración de servicios

### 👥 Gestión de Clientes
- **CRUD completo** (Crear, Leer, Actualizar, Eliminar)
- **Búsqueda inteligente** por nombre o teléfono
- **Historial de turnos** por cliente
- **Notas personalizadas** para cada cliente
- **Validación de datos**: emails, teléfonos

### 💈 Multi-Barbero
- **Gestión de personal** con CRUD de barberos
- **Asignación de colores** para identificación visual
- **Activación/desactivación** de barberos
- **Estadísticas de desempeño** por barbero
- **Validaciones**: no permitir desactivar último barbero activo ni con citas futuras

### 📊 Reportes y Estadísticas
- **Arqueo de caja** diario y por período
- **Estadísticas de servicios** más solicitados
- **Desempeño por barbero**: turnos completados, cancelados
- **Ingresos totales** y proyecciones

### 🔔 Notificaciones
- **Recordatorios por WhatsApp** (genera URL para envío manual)
- Mensaje personalizado con datos del turno

### 🔐 Seguridad Robusta
- **Autenticación con bcrypt** (hashing de contraseñas)
- **Rate Limiting**: bloqueo tras 5 intentos fallidos (5 minutos)
- **Cambio obligatorio de contraseña** en primer login
- **Gestión de sesiones** segura
- **Roles de usuario**: Admin y Barbero
- **Desbloqueo manual** de usuarios por administradores

### ⚙️ Configuración Flexible
- **Horarios de atención** configurables desde la UI
- **Catálogo de servicios** personalizable (nombre, duración, precio)
- **Configuración key-value** en base de datos para flexibilidad

### 🎨 Interfaz Moderna
- **Modo oscuro** elegante
- **Diseño responsivo** y minimalista
- **Sidebar de navegación** intuitiva
- **Componentes reutilizables** (cards, time slots)
- **Feedback visual** con snackbars y diálogos

---

## 🚀 Instalación

### Requisitos Previos

- **Python 3.10 o superior**
- **pip** (gestor de paquetes de Python)
- **Git** (para clonar el repositorio)

### Pasos de Instalación

#### 1. Clonar el Repositorio

```bash
git clone https://github.com/AlexisAcevedo/BarberManager.git
cd BarberManager
```

#### 2. Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

#### 4. Configurar Variables de Entorno

Copia el archivo de ejemplo y configura tus variables:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edita el archivo `.env` y configura **obligatoriamente** la contraseña del administrador:

```env
# REQUERIDO: Contraseña del usuario admin (cambia esto)
ADMIN_PASSWORD=tu_contraseña_segura_aqui

# Opcional: Configuración de base de datos
DATABASE_URL=sqlite:///barber_manager.db

# Opcional: Debugging
DEBUG=false
ECHO_SQL=false
```

> ⚠️ **IMPORTANTE**: `ADMIN_PASSWORD` es obligatoria. La aplicación no arrancará sin ella por seguridad.

#### 5. Ejecutar la Aplicación

```bash
python main.py
```

La aplicación se abrirá en una ventana de escritorio (1280x780 por defecto).

---

## 📖 Uso

### Credenciales por Defecto

- **Usuario**: `admin`
- **Contraseña**: La que configuraste en `ADMIN_PASSWORD` del archivo `.env`

> 🔒 En el primer login se te **pedirá cambiar la contraseña** por seguridad.

### Navegación

La aplicación cuenta con un **sidebar izquierdo** con las siguientes secciones:

| Sección | Descripción |
|---------|-------------|
| 📅 **Agenda** | Vista principal con calendario semanal, filtrado por barbero, lista de turnos del día |
| 👥 **Clientes** | Gestión completa de clientes: agregar, editar, eliminar, buscar |
| 💇 **Barberos** | Administración de personal: CRUD, colores de identificación, activación |
| 📊 **Reportes** | Estadísticas, arqueo de caja, desempeño por barbero |
| 💈 **Servicios** | Catálogo de servicios: gestión de nombre, duración y precio |
| ⚙️ **Configuración** | Horarios de atención, parámetros del sistema |

### Flujo Básico de Trabajo

1. **Configuración inicial**:
   - Ir a **Barberos** y agregar tu personal
   - Ir a **Servicios** y configurar tus servicios (corte, barba, etc.)
   - Ir a **Configuración** y establecer horarios de atención

2. **Agregar clientes**:
   - Desde **Clientes**, hacer clic en "Nuevo Cliente"
   - Completar nombre, email, teléfono (opcional), notas

3. **Crear turnos**:
   - Desde **Agenda**, seleccionar fecha y hacer clic en un slot libre
   - Elegir cliente, servicio y barbero
   - El sistema valida automáticamente conflictos de horario

4. **Gestionar turnos**:
   - Ver turnos del día en la lista
   - Cambiar estado: pendiente → confirmado
   - Cancelar turnos si es necesario
   - Enviar recordatorio por WhatsApp

5. **Revisar estadísticas**:
   - Ir a **Reportes** para ver arqueo de caja
   - Consultar desempeño de barberos
   - Analizar servicios más solicitados

---

## 📁 Estructura del Proyecto

```
barberia/
├── main.py                          # Punto de entrada de la aplicación
├── config.py                        # Configuración centralizada (Business, DB, Logging)
├── database.py                      # Engine SQLAlchemy, sesiones, data seeding
├── .env                             # Variables de entorno (NO commitear)
├── .env.example                     # Plantilla de variables de entorno
├── requirements.txt                 # Dependencias de producción
├── requirements-dev.txt             # Dependencias de desarrollo
├── alembic.ini                      # Configuración de Alembic
│
├── models/                          # Modelos ORM (SQLAlchemy)
│   ├── __init__.py
│   ├── base.py                      # Entities: Barber, User, Client, Service, Appointment, Settings
│   └── serializers.py               # Serialización para transferencia de datos
│
├── repositories/                    # Capa de acceso a datos (Repository Pattern)
│   ├── __init__.py
│   ├── base_repository.py           # Repository genérico con CRUD básico
│   └── appointment_repository.py    # Queries especializadas para appointments
│
├── services/                        # Capa de lógica de negocio (Service Layer)
│   ├── __init__.py
│   ├── appointment_service.py       # Gestión de turnos, disponibilidad, conflict detection
│   ├── auth_service.py              # Autenticación, hashing bcrypt, rate limiting
│   ├── barber_service.py            # CRUD barberos, validaciones, estadísticas
│   ├── client_service.py            # CRUD clientes, búsqueda
│   ├── service_service.py           # CRUD servicios
│   ├── notification_service.py      # Notificaciones WhatsApp
│   └── settings_service.py          # Configuración dinámica de la app
│
├── views/                           # Capa de presentación (UI con Flet)
│   ├── __init__.py
│   ├── agenda_view.py               # Vista principal: calendario semanal
│   ├── new_appointment_view.py      # Formulario crear/editar turno
│   ├── login_view.py                # Pantalla de autenticación
│   ├── change_password_view.py      # Forzar cambio de contraseña
│   ├── clients_view.py              # CRUD clientes
│   ├── barbers_view.py              # CRUD barberos
│   ├── services_view.py             # CRUD servicios
│   ├── reports_view.py              # Estadísticas y reportes
│   ├── settings_view.py             # Configuración del sistema
│   └── components/                  # Componentes UI reutilizables
│       ├── __init__.py
│       ├── sidebar.py               # Barra lateral de navegación
│       ├── appointment_card.py      # Tarjeta de turno
│       └── time_slot.py             # Slot de tiempo en agenda
│
├── utils/                           # Utilidades
│   ├── __init__.py
│   └── validators.py                # Validadores de entrada (email, phone, etc.)
│
├── tests/                           # Test suite (pytest)
│   ├── __init__.py
│   ├── conftest.py                  # Fixtures compartidos
│   ├── test_appointment_service.py  # Tests de servicio de turnos
│   ├── test_appointment_repository.py
│   ├── test_auth_service.py         # Tests de autenticación y rate limiting
│   ├── test_client_service.py
│   ├── test_service_service.py
│   ├── test_base_repository.py
│   ├── test_validators.py
│   ├── test_notification_service.py
│   └── test_settings_service.py
│
├── alembic/                         # Migraciones de base de datos
│   ├── env.py
│   └── versions/                    # Scripts de migración
│       ├── 42b5c52f6d7d_initial_migration.py
│       ├── 137560ca3196_add_must_change_password_field.py
│       ├── 8eae66de00f0_add_rate_limiting_fields_to_user.py
│       └── 93df974c4a69_add_indexes_for_performance.py
│
└── docs/                            # Documentación técnica
    ├── arquitectura.md              # Arquitectura del sistema
    ├── base_de_datos.md             # Esquema de base de datos
    ├── api_interna.md               # API de servicios
    ├── guia_desarrollo.md           # Guía para desarrolladores
    ├── testing.md                   # Estrategia de testing
    └── seguridad.md                 # Aspectos de seguridad
```

---

## 🏗️ Arquitectura

El proyecto implementa una **arquitectura en capas** combinando los patrones **MVC**, **Repository** y **Service Layer**:

### Capas

```
┌─────────────────────────────────────────────────────┐
│  Presentación (views/)                              │
│  - Interfaz de usuario con Flet                     │
│  - Manejo de eventos y navegación                   │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│  Servicios (services/)                              │
│  - Lógica de negocio                                │
│  - Validaciones                                      │
│  - Orquestación de operaciones                      │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│  Repositorios (repositories/)                       │
│  - Abstracción de acceso a datos                    │
│  - Queries especializadas                           │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│  Modelos (models/)                                  │
│  - Entidades ORM (SQLAlchemy)                       │
│  - Relaciones y constraints                         │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│  Base de Datos (SQLite)                             │
└─────────────────────────────────────────────────────┘
```

### Flujo de Datos (Ejemplo: Crear Turno)

1. **Usuario** hace clic en un slot libre en `agenda_view.py`
2. **Vista** llama a `AppointmentService.create_appointment()`
3. **Servicio** valida disponibilidad con `check_slot_availability()`
4. **Repositorio** consulta turnos existentes con `find_overlapping()`
5. **ORM** ejecuta query SQL en la base de datos
6. Si está disponible, se crea el `Appointment` y se persiste
7. **Vista** actualiza la UI con el nuevo turno

> 📚 Para más detalles sobre la arquitectura, ver [docs/arquitectura.md](docs/arquitectura.md)

---

## 🧪 Tests

El proyecto incluye una suite completa de tests unitarios con **pytest**.

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=. --cov-report=html

# Tests específicos
pytest tests/test_appointment_service.py

# Modo verbose
pytest -v
```

### Cobertura Actual

- **Servicios**: 85%+
- **Repositorios**: 90%+
- **Validadores**: 95%+
- **Total**: ~87%

> 📚 Para más información sobre testing, ver [docs/testing.md](docs/testing.md)

---

## ⚙️ Configuración

### Variables de Entorno (`.env`)

| Variable | Tipo | Por Defecto | Descripción |
|----------|------|-------------|-------------|
| `ADMIN_PASSWORD` | **Requerida** | - | Contraseña del usuario admin (primera vez) |
| `DATABASE_URL` | Opcional | `sqlite:///barber_manager.db` | URL de conexión a la base de datos |
| `DEBUG` | Opcional | `false` | Modo debug (más logs) |
| `ECHO_SQL` | Opcional | `false` | Imprimir queries SQL en consola |
| `WINDOW_WIDTH` | Opcional | `1280` | Ancho de ventana en píxeles |
| `WINDOW_HEIGHT` | Opcional | `780` | Alto de ventana en píxeles |
| `LOG_FILE` | Opcional | - | Ruta a archivo de log (si se desea persistir) |

### Configuración de Negocio

Estas configuraciones se manejan **dinámicamente desde la UI** (Configuración):

- **Horario de atención**: Hora de inicio y fin (ej. 12:00 a 20:00)
- **Duración de slots**: Intervalos de tiempo (por defecto 15 minutos)

---

## 🔧 Desarrollo

### Instalar Dependencias de Desarrollo

```bash
pip install -r requirements-dev.txt
```

Incluye: `pytest`, `pytest-cov`, herramientas de linting, etc.

### Crear Nueva Migración

```bash
# Generar migración automática
alembic revision --autogenerate -m "descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Ver estado actual
alembic current

# Historial de migraciones
alembic history
```

### Logging

El sistema usa logging estructurado. Para ver logs detallados:

```env
DEBUG=true
ECHO_SQL=true
```

Los logs se imprimen en consola con formato:
```
2026-01-22 20:15:30 | INFO     | barber_manager.auth | Usuario admin autenticado exitosamente
```

> 📚 Para guía completa de desarrollo, ver [docs/guia_desarrollo.md](docs/guia_desarrollo.md)

---

## 🐛 Troubleshooting

### Problema: "ADMIN_PASSWORD no está configurada"

**Solución**: Crea el archivo `.env` copiando `.env.example` y establece `ADMIN_PASSWORD`.

```bash
cp .env.example .env
# Editar .env y establecer ADMIN_PASSWORD=tu_contraseña
```

### Problema: "Usuario bloqueado por intentos fallidos"

**Solución**: Espera 5 minutos o desbloquea manualmente desde código:

```python
from database import get_db
from services.auth_service import AuthService

with get_db() as db:
    AuthService.unlock_user(db, "admin")
```

### Problema: La base de datos parece corrupta

**Solución** (⚠️ ELIMINA TODOS LOS DATOS):

```bash
# Eliminar archivo de base de datos
rm barber_manager.db  # Linux/Mac
del barber_manager.db  # Windows

# Ejecutar aplicación (recreará la DB)
python main.py
```

### Problema: Tests fallan con "DetachedInstanceError"

**Solución**: Los tests usan una base de datos en memoria. Asegúrate de usar las fixtures de `conftest.py`.

---

## 📋 Dependencias Principales

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| **flet** | 0.80.1 | Framework de UI (Flet es un wrapper de Flutter) |
| **sqlalchemy** | 2.0.25 | ORM para manejo de base de datos |
| **bcrypt** | 4.1.2 | Hashing de contraseñas |
| **alembic** | 1.13.1 | Migraciones de esquema de base de datos |
| **python-dotenv** | 1.0.0+ | Carga de variables de entorno desde `.env` |
| **google-api-python-client** | 2.100.0+ | Google Calendar API (para futura integración) |

### Dependencias de Desarrollo

- **pytest** | **pytest-cov**: Testing y cobertura
- Otras herramientas de linting y análisis

---

## 🗺️ Roadmap

### Funcionalidades Futuras

- [ ] **Sincronización con Google Calendar** (actualmente stub)
- [ ] **API de WhatsApp Business** para envío automático de recordatorios
- [ ] **Reportes avanzados PDF** exportables
- [ ] **Multi-sede**: soporte para múltiples barberías
- [ ] **Sistema de inventario** para productos
- [ ] **Programa de fidelización** de clientes
- [ ] **Modo claro** (además del dark mode)
- [ ] **Soporte multiidioma** (i18n)

### Mejoras Técnicas

- [ ] Migrar a PostgreSQL para entornos de producción multi-usuario
- [ ] Implementar caché para queries frecuentes
- [ ] Añadir más tests de integración y E2E
- [ ] CI/CD pipeline con GitHub Actions

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Para contribuir:

1. **Fork** el proyecto
2. Crea una rama para tu feature:
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```
3. **Commit** tus cambios siguiendo [Conventional Commits](https://www.conventionalcommits.org/):
   ```bash
   git commit -m "feat: agregar exportación de reportes a PDF"
   ```
4. **Push** a tu rama:
   ```bash
   git push origin feature/nueva-funcionalidad
   ```
5. Abre un **Pull Request** describiendo los cambios

### Guías de Contribución

- Mantén la separación de responsabilidades entre capas
- Escribe tests para nuevas funcionalidades
- Documenta cambios significativos en los docs correspondientes
- Sigue el estilo de código existente (PEP 8 para Python)

---

## 📄 Licencia

Este proyecto está licenciado bajo la **Licencia MIT**.

```
MIT License
```

---

## 👨‍💻 Autor

**Alexis Acevedo**

- GitHub: [@AlexisAcevedo](https://github.com/AlexisAcevedo)
- Email: [contacto](acevedoalexisg1992@gmail.com)

---

## 🙏 Agradecimientos

- **Flet Team**: Por crear un framework tan potente para Python
- **SQLAlchemy Team**: Por el mejor ORM de Python
- Comunidad open source por las librerías utilizadas

---

<div align="center">

**⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub ⭐**

[Reportar Bug](https://github.com/AlexisAcevedo/BarberManager/issues) · [Solicitar Feature](https://github.com/AlexisAcevedo/BarberManager/issues) · [Documentación](docs/)

</div>
